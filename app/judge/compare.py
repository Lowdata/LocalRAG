import httpx
from typing import Dict, Any, Optional
from app.core.config import settings
from app.judge.prompt_builder import prompt_builder
from app.judge.parser import judge_parser

class CompareService:
    @staticmethod
    async def compare_prompts(
        question: str, 
        expected: str, 
        generated: str, 
        prompt_v1_name: str = "v1", 
        prompt_v2_name: str = "v2"
    ) -> Dict[str, Any]:
        """Runs the same case through two different judge prompts and compares the results."""
        
        prompt_v1 = prompt_builder.build_judge_prompt(prompt_v1_name, question, expected, generated)
        prompt_v2 = prompt_builder.build_judge_prompt(prompt_v2_name, question, expected, generated)

        async def run_prompt(p: str) -> Optional[Dict[str, Any]]:
            async with httpx.AsyncClient(timeout=120.0) as client:
                try:
                    res = await client.post(
                        f"{settings.ollama_base_url}/api/generate",
                        json={
                            "model": settings.judge_model,
                            "prompt": p,
                            "stream": False,
                            "options": {"temperature": 0.0}
                        }
                    )
                    if res.status_code == 200:
                        raw = res.json().get("response", "")
                        return judge_parser.parse_verdict(raw).model_dump()
                except Exception:
                    pass
            return None

        import asyncio
        results = await asyncio.gather(
            run_prompt(prompt_v1),
            run_prompt(prompt_v2)
        )

        return {
            "v1": results[0],
            "v2": results[1],
            "winner": "v1" if results[0] and results[1] and results[0].get("overall", 0) > results[1].get("overall", 0) else "v2"
        }

compare_service = CompareService()
