import pytest
from app.judge.parser import JudgeParser, JSONParserError
from app.judge.validator import JudgeValidator
from app.judge.bias.position import PositionBias
from app.judge.bias.verbosity import VerbosityBias
from app.judge.bias.sycophancy import SycophancyBias
from app.schemas.judge import JudgeVerdict

def test_judge_parser_extracts_json():
    # Test that the parser can extract JSON even with conversational fluff around it
    raw_response = """
    Here is my evaluation:
    ```json
    {
      "correctness": 8,
      "faithfulness": 9,
      "completeness": 7,
      "safety": 10,
      "overall": 8,
      "pass_verdict": true,
      "reasoning": "Good answer."
    }
    ```
    I hope this helps!
    """
    verdict = JudgeParser.parse_verdict(raw_response)
    assert verdict.correctness == 8
    assert verdict.pass_verdict is True

def test_judge_parser_fails_on_bad_json():
    raw_response = "This is just text without any JSON."
    with pytest.raises(JSONParserError):
        JudgeParser.parse_verdict(raw_response)

def test_validator_kappa():
    # Perfect agreement
    assert JudgeValidator.calculate_cohens_kappa([8, 9, 10], [8, 9, 10], threshold=7) == 1.0
    # 50% agreement (pass/fail)
    assert JudgeValidator.calculate_cohens_kappa([10, 2], [10, 10], threshold=7) == 0.5

def test_position_bias():
    # Judge picked 'A', then picked 'A' again when swapped (meaning it just picked position 1)
    flips = PositionBias.measure_flip_rate(['A', 'A'], ['A', 'B'])
    assert flips == 0.5

def test_verbosity_bias():
    diff = VerbosityBias.measure_score_difference([5, 5], [7, 6])
    assert diff == 1.5

def test_sycophancy_bias():
    # Original fails (False), Sycophantic passes (True)
    rate = SycophancyBias.measure_fooled_rate([False, False], [True, False])
    assert rate == 0.5
