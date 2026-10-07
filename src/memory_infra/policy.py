from dataclasses import dataclass


@dataclass
class LearnedPolicy:
    """V0.1 adaptive scoring.

    score = similarity + alpha * utility

    alpha is the only learned knob. Full four-weight scoring
    (relevance + utility + reliability + context_fit) is the
    documented target; v0.1 starts with the two-term form so the
    feedback loop can be validated before adding weights.
    """

    alpha: float = 0.5

    def score(self, similarity: float, utility: float) -> float:
        return similarity + self.alpha * utility
