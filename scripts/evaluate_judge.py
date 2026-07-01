import asyncio
import json
import httpx
from typing import List
from app.schemas.judge import JudgeCase
from app.judge.judge_service import judge_service
from app.judge.aggregator import judge_aggregator

API_URL = "http://localhost:8000/api/v1/query"

async def run_evaluation_pipeline(suite_path: str = "datasets/judge/suite.json"):
    print(f"Loading suite from {suite_path}...")
    with open(suite_path, "r") as f:
        cases_data = json.load(f)
        
    cases = [JudgeCase(**data) for data in cases_data]
    print(f"Loaded {len(cases)} cases.")

    results = []
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for i, case in enumerate(cases):
            print(f"\n[{i+1}/{len(cases)}] Evaluating Case: {case.id}")
            print(f"  Q: {case.input}")
            
            # 1. Ask the Generator (RAG API)
            try:
                res = await client.post(API_URL, json={"query": case.input, "top_k": 3})
                if res.status_code == 200:
                    generated_answer = res.json().get("answer", "")
                else:
                    generated_answer = f"API Error: {res.status_code}"
            except Exception as e:
                generated_answer = f"Request Failed: {str(e)}"
                
            print(f"  Generated Answer: {generated_answer[:100]}...")

            # 2. Ask the Judge
            print("  Running Judge Evaluation...")
            result = await judge_service.evaluate_case(case, generated_answer)
            results.append(result)
            
            if result.verdict:
                print(f"  Verdict: OVERALL {result.verdict.overall}/10 | PASS: {result.verdict.pass_verdict}")
            else:
                print("  Verdict: FAILED TO PARSE")

    # 3. Aggregate and Report
    print("\nAggregating Suite Results...")
    report = judge_aggregator.aggregate(results)
    
    print("\n==================================================")
    print("EVALUATION FRAMEWORK SUITE REPORT")
    print("==================================================")
    print(f"Total Cases:     {report.total_cases}")
    print(f"Success Cases:   {report.success_cases}")
    print(f"Pass Rate:       {report.pass_rate * 100:.2f}%")
    print(f"Mean Overall:    {report.mean_overall:.2f}/10")
    print(f"Mean Latency:    {report.mean_latency_ms}ms")
    print(f"Total Tokens:    {report.total_tokens}")
    print("==================================================")
    print("Detailed report saved to reports/judge/")

if __name__ == "__main__":
    asyncio.run(run_evaluation_pipeline())
