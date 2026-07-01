from typing import List

class JudgeValidator:
    @staticmethod
    def calculate_cohens_kappa(judge_scores: List[int], human_scores: List[int], threshold: int = 7) -> float:
        """
        Calculates a simplified agreement metric.
        If both score >= threshold, it's a pass. Otherwise fail.
        """
        if len(judge_scores) != len(human_scores) or len(judge_scores) == 0:
            return 0.0

        agree = sum(1 for j, h in zip(judge_scores, human_scores) if (j >= threshold) == (h >= threshold))
        return agree / len(judge_scores)

    @staticmethod
    def calculate_flip_rate(runs: List[List[bool]]) -> float:
        """
        Takes multiple runs of the same cases.
        runs[0] = [True, False, True] (Run 1 passes/fails)
        runs[1] = [True, True, True]  (Run 2 passes/fails)
        Calculates how often a case flips its verdict.
        """
        if not runs or len(runs) < 2:
            return 0.0

        num_cases = len(runs[0])
        flips = 0
        for i in range(num_cases):
            verdicts = [run[i] for run in runs]
            if len(set(verdicts)) > 1:
                flips += 1
                
        return flips / num_cases

judge_validator = JudgeValidator()
