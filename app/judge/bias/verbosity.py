class VerbosityBias:
    @staticmethod
    def generate_fluffed_answer(answer: str) -> str:
        """Injects verbose, academic-sounding fluff to a generated answer to test if the judge gives it a higher score."""
        fluff = (
            " In conclusion, it is highly imperative to deeply analyze the multidimensional aspects "
            "of this phenomenon. Through careful synthesis of the underlying architectural paradigms, "
            "we can robustly ascertain that the aforementioned methodology leverages optimal synergies. "
            "Furthermore, this extensively corroborates the foundational hypothesis detailed in the primary literature."
        )
        return answer + fluff

    @staticmethod
    def measure_score_difference(original_scores: list, fluffed_scores: list) -> float:
        """Calculates the average point difference given by the judge when fluff is added."""
        if len(original_scores) != len(fluffed_scores) or len(original_scores) == 0:
            return 0.0

        diffs = [f - o for o, f in zip(original_scores, fluffed_scores)]
        return sum(diffs) / len(diffs)
