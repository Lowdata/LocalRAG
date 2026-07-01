import os
import json
from datetime import datetime
from typing import List
from app.schemas.judge import JudgeCaseResult, JudgeSuiteReport

class JudgeAggregator:
    def __init__(self, reports_dir: str = "reports/judge"):
        self.reports_dir = reports_dir
        os.makedirs(self.reports_dir, exist_ok=True)

    def aggregate(self, results: List[JudgeCaseResult]) -> JudgeSuiteReport:
        total = len(results)
        if total == 0:
            return JudgeSuiteReport(
                total_cases=0, success_cases=0, pass_rate=0.0,
                mean_correctness=0.0, mean_faithfulness=0.0,
                mean_completeness=0.0, mean_overall=0.0,
                mean_latency_ms=0.0, total_tokens=0, results=[]
            )

        success_results = [r for r in results if r.metadata.success and r.verdict is not None]
        success_cases = len(success_results)
        
        pass_cases = sum(1 for r in success_results if r.verdict.pass_verdict) # type: ignore
        pass_rate = pass_cases / success_cases if success_cases > 0 else 0.0

        mean_correctness = sum(r.verdict.correctness for r in success_results) / success_cases if success_cases > 0 else 0.0 # type: ignore
        mean_faithfulness = sum(r.verdict.faithfulness for r in success_results) / success_cases if success_cases > 0 else 0.0 # type: ignore
        mean_completeness = sum(r.verdict.completeness for r in success_results) / success_cases if success_cases > 0 else 0.0 # type: ignore
        mean_overall = sum(r.verdict.overall for r in success_results) / success_cases if success_cases > 0 else 0.0 # type: ignore

        mean_latency = sum(r.metadata.latency_ms for r in results) / total
        total_tokens = sum(r.metadata.tokens_prompt + r.metadata.tokens_completion for r in results)

        report = JudgeSuiteReport(
            total_cases=total,
            success_cases=success_cases,
            pass_rate=pass_rate,
            mean_correctness=mean_correctness,
            mean_faithfulness=mean_faithfulness,
            mean_completeness=mean_completeness,
            mean_overall=mean_overall,
            mean_latency_ms=mean_latency,
            total_tokens=total_tokens,
            results=results
        )

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.reports_dir, f"report_{timestamp}.json")
        with open(report_path, "w") as f:
            f.write(report.model_dump_json(indent=2))

        return report

judge_aggregator = JudgeAggregator()
