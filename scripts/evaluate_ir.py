import httpx
import time
import asyncio
import numpy as np
import json
from typing import List, Dict

API_URL = "http://127.0.0.1:8000/api/v1/query"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"

# A dataset of 15 questions, assuming the user has ingested README.md or their Resume.
# Since we don't have exact "gold chunks", we will do unsupervised evaluation using the LLM-as-a-judge
# and standard string matching for simple IR metrics.
DATASET = [
    {"question": "What is the architecture of this local RAG backend?", "expected_keywords": ["fastapi", "lancedb", "sentencetransformers", "ollama"]},
    {"question": "Which vector database does this project use?", "expected_keywords": ["lancedb"]},
    {"question": "Which embedding model is used?", "expected_keywords": ["bge-small-en"]},
    {"question": "How do you run the backend natively?", "expected_keywords": ["uvicorn", "reload"]},
    {"question": "How do you run the backend via Docker?", "expected_keywords": ["docker compose up"]},
    {"question": "What endpoints are available?", "expected_keywords": ["/health", "/api/v1/ingest", "/api/v1/query"]},
    {"question": "What AI model does the project default to?", "expected_keywords": ["qwen2.5:1.5b"]},
    {"question": "What script is used to evaluate latency?", "expected_keywords": ["evaluate.py"]},
    {"question": "How do you completely kill Ollama if the port is in use?", "expected_keywords": ["pkill", "-f"]},
    {"question": "What should OLLAMA_BASE_URL be set to for native execution?", "expected_keywords": ["localhost:11434"]},
    {"question": "What should OLLAMA_BASE_URL be set to for Docker execution?", "expected_keywords": ["host.docker.internal"]},
    {"question": "How do you ingest a file?", "expected_keywords": ["/api/v1/ingest", "post"]},
    {"question": "How do you delete a document?", "expected_keywords": ["delete", "/api/v1/documents/"]},
    {"question": "What are the supported file types for ingestion?", "expected_keywords": [".pdf", ".md", ".html"]},
    {"question": "Why would you get an 'address already in use' error for Ollama?", "expected_keywords": ["menu bar", "background"]},
]

async def llm_judge(prompt: str) -> str:
    """Uses Ollama to grade a response."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            res = await client.post(OLLAMA_URL, json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            })
            if res.status_code == 200:
                return res.json().get("response", "").strip()
        except Exception:
            pass
    return "UNKNOWN"

async def evaluate_faithfulness(question: str, answer: str, context: str) -> int:
    """Evaluates if the answer is grounded in the retrieved context."""
    prompt = f"""
Given the following CONTEXT, evaluate if the ANSWER is completely faithful and grounded in the CONTEXT.
If the answer hallucinates or contains information not present in the context, return 0. If it is faithful, return 1.
Respond ONLY with the number 1 or 0.

CONTEXT:
{context}

ANSWER:
{answer}
"""
    result = await llm_judge(prompt)
    return 1 if "1" in result else 0

async def evaluate_relevance(question: str, answer: str) -> int:
    """Evaluates if the answer directly addresses the question."""
    prompt = f"""
Given the following QUESTION and ANSWER, evaluate if the ANSWER is relevant and directly addresses the QUESTION.
Return 1 if it is relevant, and 0 if it is not relevant or dodges the question.
Respond ONLY with the number 1 or 0.

QUESTION:
{question}

ANSWER:
{answer}
"""
    result = await llm_judge(prompt)
    return 1 if "1" in result else 0

def calculate_mrr(retrieved_texts: List[str], expected_keywords: List[str]) -> float:
    """Calculates Mean Reciprocal Rank (MRR) based on keyword matching."""
    for i, text in enumerate(retrieved_texts):
        text_lower = text.lower()
        if any(kw.lower() in text_lower for kw in expected_keywords):
            return 1.0 / (i + 1)
    return 0.0

async def run_evaluation():
    print(f"Starting rigorous IR evaluation on {len(DATASET)} questions...")
    
    latencies = []
    total_hit_rate = 0
    total_mrr = 0.0
    total_faithfulness = 0
    total_relevance = 0
    successful_queries = 0
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for idx, item in enumerate(DATASET):
            q = item["question"]
            expected = item["expected_keywords"]
            
            print(f"\n[{idx+1}/{len(DATASET)}] Q: {q}")
            start_time = time.time()
            try:
                response = await client.post(API_URL, json={"query": q, "top_k": 3})
                latency = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "")
                    sources = data.get("sources", [])
                    
                    retrieved_texts = [s.get("text", "") for s in sources]
                    combined_context = "\n".join(retrieved_texts)
                    
                    # 1. Retrieval Metrics
                    mrr = calculate_mrr(retrieved_texts, expected)
                    hit = 1 if mrr > 0 else 0
                    
                    # 2. Answer Metrics (LLM as Judge)
                    faithfulness = await evaluate_faithfulness(q, answer, combined_context)
                    relevance = await evaluate_relevance(q, answer)
                    
                    print(f"  Latency: {latency:.2f}s | Hit: {hit} | MRR: {mrr:.2f} | Faithful: {faithfulness} | Relevant: {relevance}")
                    
                    latencies.append(latency)
                    total_hit_rate += hit
                    total_mrr += mrr
                    total_faithfulness += faithfulness
                    total_relevance += relevance
                    successful_queries += 1
                else:
                    print(f"  Error: HTTP {response.status_code}")
            except Exception as e:
                print(f"  Request failed: {str(e)}")

    if successful_queries == 0:
        print("No successful queries. Ensure the API is running and documents are ingested (e.g. ingest README.md).")
        return

    # Aggregate Metrics
    p50_latency = np.percentile(latencies, 50)
    p95_latency = np.percentile(latencies, 95)
    
    hit_rate = total_hit_rate / successful_queries
    mean_rr = total_mrr / successful_queries
    faithfulness_score = total_faithfulness / successful_queries
    relevance_score = total_relevance / successful_queries

    print("\n" + "="*50)
    print("EVALUATION RESULTS (N=15)")
    print("="*50)
    print(f"Retrieval - Hit Rate (@3):      {hit_rate:.2%}")
    print(f"Retrieval - MRR (@3):           {mean_rr:.2f}")
    print(f"Answer    - Faithfulness:       {faithfulness_score:.2%}")
    print(f"Answer    - Relevance:          {relevance_score:.2%}")
    print(f"Latency   - p50:                {p50_latency:.2f}s")
    print(f"Latency   - p95:                {p95_latency:.2f}s")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(run_evaluation())
