import time
import httpx
import asyncio
from typing import Optional
from app.core.config import settings
from app.schemas.judge import JudgeCase, JudgeVerdict, JudgeCaseResult, JudgeMetadata
from app.judge.prompt_builder import prompt_builder
from app.judge.parser import judge_parser
from app.judge.logger import judge_logger


class JudgeService:
    @staticmethod
    async def evaluate_case(case: JudgeCase, generated_answer: str) -> JudgeCaseResult:
        # Build prompt
        prompt = prompt_builder.build_judge_prompt(
            version=settings.judge_prompt,
            question=case.input,
            expected=case.expected_output,
            generated=generated_answer,
        )

        start_time = time.time()
        raw_response = ""
        verdict = None
        success = False

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                res = await client.post(
                    f"{settings.ollama_base_url}/api/generate",
                    json={
                        "model": settings.judge_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.0
                        },  # We want strict deterministic grading
                    },
                )
                if res.status_code == 200:
                    data = res.json()
                    raw_response = data.get("response", "")
                    verdict = judge_parser.parse_verdict(raw_response)
                    success = True
            except Exception as e:
                raw_response = f"Failed to generate or parse response: {str(e)}"

        latency_ms = int((time.time() - start_time) * 1000)

        # We don't have token tracking easily from standard Ollama API unless we use the advanced endpoints,
        # so we will use a simple proxy for now.
        tokens_prompt = len(prompt) // 4
        tokens_completion = len(raw_response) // 4

        metadata = JudgeMetadata(
            judge_model=settings.judge_model,
            generator_model=settings.generator_model,
            tokens_prompt=tokens_prompt,
            tokens_completion=tokens_completion,
            estimated_cost="0.00 (Local Inference)",
            latency_ms=latency_ms,
            success=success,
        )

        # Log it
        judge_logger.log_evaluation(
            case_id=case.id,
            prompt=prompt,
            raw_response=raw_response,
            parsed_json=verdict.model_dump() if verdict else None,
            metadata=metadata.model_dump(),
        )

        return JudgeCaseResult(case_id=case.id, verdict=verdict, metadata=metadata)


judge_service = JudgeService()
