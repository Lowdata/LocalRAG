from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel
from app.schemas.judge import JudgeCase, JudgeCaseResult
from app.judge.judge_service import judge_service
from app.judge.compare import compare_service

router = APIRouter()


class JudgeSingleRequest(BaseModel):
    case: JudgeCase
    generated_answer: str


class CompareRequest(BaseModel):
    question: str
    expected: str
    generated: str
    prompt_v1: str = "v1"
    prompt_v2: str = "v2"


@router.post("", response_model=JudgeCaseResult)
@router.post("", response_model=JudgeCaseResult)
async def evaluate_single_case(request: JudgeSingleRequest) -> Any:
    return await judge_service.evaluate_case(request.case, request.generated_answer)


@router.post("/compare")
async def compare_prompts(request: CompareRequest) -> Any:
    return await compare_service.compare_prompts(
        question=request.question,
        expected=request.expected,
        generated=request.generated,
        prompt_v1_name=request.prompt_v1,
        prompt_v2_name=request.prompt_v2,
    )
