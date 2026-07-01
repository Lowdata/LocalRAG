import httpx
import time
import asyncio
import argparse
from typing import List, Dict

API_URL = "http://127.0.0.1:8000/api/v1/query"

# A sample dataset for evaluation
EVAL_DATASET = [
    "What is RAG?",
    "How does LanceDB work?",
    "What is the role of an embedding model?",
    "Explain how overlapping chunking helps in retrieval."
]

async def run_evaluation(url: str, questions: List[str]) -> Dict[str, float]:
    print(f"Starting evaluation on {len(questions)} questions against {url}...")
    
    total_latency = 0.0
    successful_queries = 0
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        for q in questions:
            print(f"\nQ: {q}")
            start_time = time.time()
            try:
                response = await client.post(url, json={"query": q, "top_k": 3})
                latency = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "")
                    sources = data.get("sources", [])
                    print(f"Latency: {latency:.2f}s | Sources retrieved: {len(sources)}")
                    print(f"A: {answer[:150]}...")
                    
                    total_latency += latency
                    successful_queries += 1
                else:
                    print(f"Error: HTTP {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Request failed: {str(e)}")

    avg_latency = (total_latency / successful_queries) if successful_queries > 0 else 0
    
    print("\n" + "="*40)
    print("EVALUATION SUMMARY")
    print("="*40)
    print(f"Total Questions: {len(questions)}")
    print(f"Successful Queries: {successful_queries}")
    print(f"Average Latency: {avg_latency:.2f} seconds per query")
    
    return {
        "average_latency": avg_latency,
        "success_rate": successful_queries / len(questions) if len(questions) > 0 else 0
    }

def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate RAG Pipeline Latency and Responses")
    parser.add_argument("--url", default=API_URL, help="URL of the query API endpoint")
    args = parser.parse_args()
    
    asyncio.run(run_evaluation(args.url, EVAL_DATASET))

if __name__ == "__main__":
    main()
