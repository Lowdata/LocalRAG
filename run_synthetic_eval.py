import os
import json
import httpx
import asyncio
import numpy as np
import time
from collections import Counter
import re

API_URL = "http://localhost:8000/api/v1/query"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"
K = 5


def normalize_text(text: str) -> str:
    return re.sub(r"\W+", " ", text.lower().strip())


def calculate_em(prediction: str, ground_truth: str) -> int:
    return int(normalize_text(prediction) == normalize_text(ground_truth))


def calculate_f1(prediction: str, ground_truth: str) -> float:
    pred_tokens = normalize_text(prediction).split()
    truth_tokens = normalize_text(ground_truth).split()

    if not pred_tokens or not truth_tokens:
        return 1.0 if pred_tokens == truth_tokens else 0.0

    common_tokens = Counter(pred_tokens) & Counter(truth_tokens)
    num_same = sum(common_tokens.values())

    if num_same == 0:
        return 0.0

    precision = 1.0 * num_same / len(pred_tokens)
    recall = 1.0 * num_same / len(truth_tokens)
    return (2 * precision * recall) / (precision + recall)


async def llm_judge(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            res = await client.post(
                OLLAMA_URL,
                json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
            )
            if res.status_code == 200:
                return str(res.json().get("response", "")).strip()
        except Exception:
            pass
    return "0"


async def evaluate_faithfulness(question: str, answer: str, context: str) -> int:
    prompt = f"Given the following CONTEXT, evaluate if the ANSWER is completely faithful and grounded in the CONTEXT. If it hallucinated, return 0. If faithful, return 1. Respond ONLY with 1 or 0.\nCONTEXT:\n{context}\nANSWER:\n{answer}"
    result = await llm_judge(prompt)
    return 1 if "1" in result else 0


async def evaluate_relevance(question: str, answer: str) -> int:
    prompt = f"Given the QUESTION and ANSWER, evaluate if the ANSWER is relevant and directly addresses the QUESTION. Return 1 if relevant, 0 if not. Respond ONLY with 1 or 0.\nQUESTION:\n{question}\nANSWER:\n{answer}"
    result = await llm_judge(prompt)
    return 1 if "1" in result else 0


def calculate_mrr(retrieved_ids: list[str], relevant_ids: list[str]) -> float:
    for i, cid in enumerate(retrieved_ids):
        if cid in relevant_ids:
            return 1.0 / (i + 1)
    return 0.0


def calculate_recall(
    retrieved_ids: list[str], relevant_ids: list[str], k: int
) -> float:
    retrieved_k = retrieved_ids[:k]
    hits = sum(1 for cid in relevant_ids if cid in retrieved_k)
    return hits / len(relevant_ids) if relevant_ids else 0.0


def calculate_precision(
    retrieved_ids: list[str], relevant_ids: list[str], k: int
) -> float:
    retrieved_k = retrieved_ids[:k]
    if not retrieved_k:
        return 0.0
    hits = sum(1 for cid in retrieved_k if cid in relevant_ids)
    return hits / len(retrieved_k)


def calculate_ndcg(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> float:
    dcg = sum(
        1.0 / np.log2(i + 2)
        for i, cid in enumerate(retrieved_ids[:k])
        if cid in relevant_ids
    )
    idcg = sum(1.0 / np.log2(i + 2) for i in range(min(k, len(relevant_ids))))
    return dcg / idcg if idcg > 0 else 0.0


async def run_evaluation():
    with open("eval_dataset.json", "r") as f:
        dataset = json.load(f)

    total_mrr, total_recall, total_precision, total_ndcg = 0.0, 0.0, 0.0, 0.0
    total_faithfulness, total_relevance = 0.0, 0.0
    total_em, total_f1 = 0.0, 0.0
    successful = 0

    print(f"Evaluating {len(dataset)} questions with k={K}...")

    async with httpx.AsyncClient(timeout=120.0) as client:
        for idx, item in enumerate(dataset):
            q = item["question"]
            gold = item["gold_answer"]
            relevant_ids = item["relevant_chunk_ids"]
            doc_path = item["document_path"]

            print(f"[{idx+1}/{len(dataset)}] Q: {q}")
            try:
                # We are now utilizing the metadata filter we built earlier!
                response = await client.post(
                    API_URL,
                    json={
                        "query": q,
                        "top_k": K,
                        "document_path": doc_path,  # <-- THIS IS THE FIX
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "")
                    sources = data.get("sources", [])

                    retrieved_ids = [s.get("chunk_id", "") for s in sources]
                    combined_context = "\n".join([s.get("text", "") for s in sources])

                    total_mrr += calculate_mrr(retrieved_ids, relevant_ids)
                    total_recall += calculate_recall(retrieved_ids, relevant_ids, K)
                    total_precision += calculate_precision(
                        retrieved_ids, relevant_ids, K
                    )
                    total_ndcg += calculate_ndcg(retrieved_ids, relevant_ids, K)

                    total_faithfulness += await evaluate_faithfulness(
                        q, answer, combined_context
                    )
                    total_relevance += await evaluate_relevance(q, answer)

                    total_em += calculate_em(answer, gold)
                    total_f1 += calculate_f1(answer, gold)

                    successful += 1
            except Exception as e:
                print(f"Request failed: {e}")

    if successful > 0:
        print("\n=== RESULTS ===")
        print(f"Recall@{K} / Hit Rate: {total_recall/successful:.4f}")
        print(f"MRR: {total_mrr/successful:.4f}")
        print(f"nDCG@{K}: {total_ndcg/successful:.4f}")
        print(f"Context Precision: {total_precision/successful:.4f}")
        print(f"Faithfulness: {total_faithfulness/successful:.4f}")
        print(f"Answer Relevance: {total_relevance/successful:.4f}")
        print(f"EM: {total_em/successful:.4f}")
        print(f"F1: {total_f1/successful:.4f}")


if __name__ == "__main__":
    asyncio.run(run_evaluation())
