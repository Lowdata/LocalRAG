import statistics

class ScoreClusteringBias:
    @staticmethod
    def measure_variance(scores: list) -> float:
        """
        Calculates the variance of a list of scores.
        Small models often cluster around 7 and 8. Higher variance means the model is using the full range (1-10).
        """
        if len(scores) < 2:
            return 0.0
        return statistics.variance(scores)
