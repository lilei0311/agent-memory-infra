from dataclasses import dataclass


@dataclass
class LearnedPolicy:
    """Score = similarity + alpha * historical utility.

    alpha is the only learned knob in v0. Positive feedback raises it
    only when the policy pick beats the baseline pick.
    """

    alpha: float = 0.5

    def score(self, similarity: float, utility: float) -> float:
        return similarity + self.alpha * utility
