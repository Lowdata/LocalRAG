import httpx
import time
import asyncio
import numpy as np
import os
from typing import List

API_URL = "http://127.0.0.1:8000/api/v1/query"
INGEST_URL = "http://127.0.0.1:8000/api/v1/ingest"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"
EVAL_FILE = "eval_corpus.md"

# 1. Create a dummy corpus that is heavily structured so we can predictably map queries to chunks.
CORPUS_CONTENT = """# The Great RAG Guide
## Section 1: Architecture
The architecture of this local RAG backend utilizes FastAPI for routing, LanceDB as the embedded vector database, SentenceTransformers for semantic search, and Ollama for the LLM generation.
## Section 2: Embeddings
We use the BAAI/bge-small-en-v1.5 embedding model. It runs completely locally via PyTorch and outputs vectors of 384 dimensions.
## Section 3: Cost and Latency
Retrieval latency is generally under 20ms using LanceDB. However, generation latency using Ollama takes upwards of 2 seconds. Because of this, generation is the bottleneck. The cost of running this stack is under $15 per month on a micro EC2 instance, saving hundreds of dollars compared to Pinecone.
## Section 4: Docker vs Native
When running natively, set OLLAMA_BASE_URL to localhost:11434. When running via Docker Compose, the internal network bridges to the host machine, requiring OLLAMA_BASE_URL to be host.docker.internal.
"""

# 2. A dataset of questions with ground-truth chunk mappings.
# Assuming a chunk size that roughly captures 1-2 sections per chunk.
# By forcing specific chunk_ids, we can compute strict IR metrics.
from typing import Any
DATASET: list[dict[str, Any]] = [
    {
        "question": "What components make up the architecture of the RAG backend?",
        "relevant_chunk_ids": [
            "eval_corpus.md_page1_chunk0",
            "eval_corpus.md_page1_chunk1",
        ],
    },
    {
        "question": "Which embedding model is utilized and what is its dimensionality?",
        "relevant_chunk_ids": [
            "eval_corpus.md_page1_chunk1",
            "eval_corpus.md_page1_chunk2",
        ],
    },
    {
        "question": "What is the primary bottleneck in the system?",
        "relevant_chunk_ids": [
            "eval_corpus.md_page1_chunk2",
            "eval_corpus.md_page1_chunk3",
        ],
    },
    {
        "question": "How much does it cost to run the system compared to Pinecone?",
        "relevant_chunk_ids": ["eval_corpus.md_page1_chunk3"],
    },
    {
        "question": "What is the correct OLLAMA_BASE_URL for Docker?",
        "relevant_chunk_ids": ["eval_corpus.md_page1_chunk4"],
    },
]


async def llm_judge(prompt: str) -> str:
    """Uses Ollama to grade a response."""
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
    return "UNKNOWN"


async def evaluate_faithfulness(question: str, answer: str, context: str) -> int:
    """Evaluates if the answer is completely grounded in the context."""
    prompt = f"""Given the following CONTEXT, evaluate if the ANSWER is completely faithful and grounded in the CONTEXT. If the answer hallucinates or contains information not present in the context, return 0. If it is faithful, return 1. Respond ONLY with the number 1 or 0.\nCONTEXT:\n{context}\nANSWER:\n{answer}"""
    result = await llm_judge(prompt)
    return 1 if "1" in result else 0


async def evaluate_relevance(question: str, answer: str) -> int:
    """Evaluates if the answer directly addresses the question."""
    prompt = f"""Given the following QUESTION and ANSWER, evaluate if the ANSWER is relevant and directly addresses the QUESTION. Return 1 if it is relevant, and 0 if it is not relevant or dodges the question. Respond ONLY with the number 1 or 0.\nQUESTION:\n{question}\nANSWER:\n{answer}"""
    result = await llm_judge(prompt)
    return 1 if "1" in result else 0


def calculate_mrr(retrieved_ids: List[str], relevant_ids: List[str]) -> float:
    for i, cid in enumerate(retrieved_ids):
        if cid in relevant_ids:
            return 1.0 / (i + 1)
    return 0.0


def calculate_recall(
    retrieved_ids: List[str], relevant_ids: List[str], k: int
) -> float:
    retrieved_k = retrieved_ids[:k]
    hits = sum(1 for cid in relevant_ids if cid in retrieved_k)
    return hits / len(relevant_ids) if relevant_ids else 0.0


def calculate_precision(
    retrieved_ids: List[str], relevant_ids: List[str], k: int
) -> float:
    retrieved_k = retrieved_ids[:k]
    if not retrieved_k:
        return 0.0
    hits = sum(1 for cid in retrieved_k if cid in relevant_ids)
    return hits / len(retrieved_k)


def calculate_ndcg(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
    dcg = 0.0
    for i, cid in enumerate(retrieved_ids[:k]):
        if cid in relevant_ids:
            dcg += 1.0 / np.log2(i + 2)

    idcg = 0.0
    for i in range(min(k, len(relevant_ids))):
        idcg += 1.0 / np.log2(i + 2)

    return dcg / idcg if idcg > 0 else 0.0


async def run_evaluation() -> None:
    # 1. Setup: Write the corpus to disk and ingest it
    print(f"Setting up test corpus: {EVAL_FILE}")
    with open(EVAL_FILE, "w") as f:
        f.write(CORPUS_CONTENT)

    async with httpx.AsyncClient(timeout=60.0) as client:
        with open(EVAL_FILE, "rb") as f:
            print("Ingesting corpus to ensure deterministic chunk mappings...")
            try:
                await client.post(
                    INGEST_URL, files={"file": (EVAL_FILE, f, "text/markdown")}
                )
            except Exception as e:
                print(f"Failed to ingest: {e}. Ensure API is running.")
                return

    # 2. Run Evaluation
    print(f"\nStarting strict IR evaluation on {len(DATASET)} questions...")
    latencies, total_mrr, total_recall, total_precision, total_ndcg = (
        [],
        0.0,
        0.0,
        0.0,
        0.0,
    )
    total_faithfulness, total_relevance = 0, 0
    successful_queries = 0

    async with httpx.AsyncClient(timeout=60.0) as client:
        for idx, item in enumerate(DATASET):
            q = item["question"]
            relevant_ids = item["relevant_chunk_ids"]

            print(f"\n[{idx+1}/{len(DATASET)}] Q: {q}")
            start_time = time.time()
            try:
                response = await client.post(
                    API_URL, json={"query": q, "top_k": 3, "document_path": EVAL_FILE}
                )
                latency = time.time() - start_time

                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "")
                    sources = data.get("sources", [])

                    retrieved_ids = [s.get("chunk_id", "") for s in sources]
                    combined_context = "\n".join([s.get("text", "") for s in sources])

                    # 1. Strict IR Metrics (@3)
                    mrr = calculate_mrr(retrieved_ids, relevant_ids)
                    recall = calculate_recall(retrieved_ids, relevant_ids, 3)
                    precision = calculate_precision(retrieved_ids, relevant_ids, 3)
                    ndcg = calculate_ndcg(retrieved_ids, relevant_ids, 3)

                    # 2. LLM Judge Metrics
                    faithfulness = await evaluate_faithfulness(
                        q, answer, combined_context
                    )
                    relevance = await evaluate_relevance(q, answer)

                    print(
                        f"  Latency: {latency:.2f}s | MRR: {mrr:.2f} | Recall@3: {recall:.2f} | nDCG@3: {ndcg:.2f} | Prec@3: {precision:.2f}"
                    )

                    latencies.append(latency)
                    total_mrr += mrr
                    total_recall += recall
                    total_precision += precision
                    total_ndcg += ndcg
                    total_faithfulness += faithfulness
                    total_relevance += relevance
                    successful_queries += 1
                else:
                    print(f"  Error: HTTP {response.status_code}")
            except Exception as e:
                print(f"  Request failed: {str(e)}")

    if successful_queries > 0:
        print("\n" + "=" * 50)
        print("EVALUATION RESULTS (STRICT IR METRICS)")
        print("=" * 50)
        print(f"Retrieval - Recall@3:           {total_recall/successful_queries:.2%}")
        print(
            f"Retrieval - Context Precision:  {total_precision/successful_queries:.2%}"
        )
        print(f"Retrieval - MRR:                {total_mrr/successful_queries:.2f}")
        print(f"Retrieval - nDCG@3:             {total_ndcg/successful_queries:.2f}")
        print(
            f"Answer    - Faithfulness:       {total_faithfulness/successful_queries:.2%}"
        )
        print(
            f"Answer    - Relevance:          {total_relevance/successful_queries:.2%}"
        )
        print(f"Latency   - p50:                {np.percentile(latencies, 50):.2f}s")
        print(f"Latency   - p95:                {np.percentile(latencies, 95):.2f}s")
        print("=" * 50)

    # Cleanup
    if os.path.exists(EVAL_FILE):
        os.remove(EVAL_FILE)


if __name__ == "__main__":
    asyncio.run(run_evaluation())
