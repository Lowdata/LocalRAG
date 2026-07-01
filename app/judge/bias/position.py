from typing import Any


class PositionBias:
    @staticmethod
    def measure_flip_rate(results_ab: list[Any], results_ba: list[Any]) -> float:
        """
        Measures how often the judge changes its 'winner' when the order of candidates A and B are swapped.
        """
        if len(results_ab) != len(results_ba) or len(results_ab) == 0:
            return 0.0

        flips = 0
        for ab, ba in zip(results_ab, results_ba):
            # If AB says 'A' won, BA should say 'B' won (since they are swapped).
            # If they both say 'A' won, it means the judge just picked the first position both times!
            if ab == ba and ab in ["A", "B"]:
                flips += 1

        return flips / len(results_ab)
