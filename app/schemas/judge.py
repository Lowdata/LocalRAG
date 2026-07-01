from pydantic import BaseModel, Field
from typing import List, Optional, Any

class JudgeCase(BaseModel):
    id: str
    input: str
    expected_output: str
    criteria: List[str] = ["correctness", "faithfulness", "completeness"]

class JudgeVerdict(BaseModel):
    correctness: int = Field(ge=0, le=10)
    faithfulness: int = Field(ge=0, le=10)
    completeness: int = Field(ge=0, le=10)
    safety: int = Field(ge=0, le=10, default=10)
    overall: int = Field(ge=0, le=10)
    pass_verdict: bool
    reasoning: str

class PairwiseVerdict(BaseModel):
    winner: str = Field(description="'A', 'B', or 'Tie'")
    reasoning: str

class JudgeMetadata(BaseModel):
    judge_model: str
    generator_model: str
    tokens_prompt: int
    tokens_completion: int
    estimated_cost: str
    latency_ms: int
    success: bool

class JudgeCaseResult(BaseModel):
    case_id: str
    verdict: Optional[JudgeVerdict]
    metadata: JudgeMetadata

class JudgeSuiteReport(BaseModel):
    total_cases: int
    success_cases: int
    pass_rate: float
    mean_correctness: float
    mean_faithfulness: float
    mean_completeness: float
    mean_overall: float
    mean_latency_ms: float
    total_tokens: int
    results: List[JudgeCaseResult]
