from memory_infra.memory import MemoryStore
from memory_infra.policy import LearnedPolicy


class FeedbackLearner:
    """Apply task outcome to the retrieved item, then nudge alpha.

    Alpha is raised only when the policy's top pick beats the baseline's
    top pick on a successful task, and lowered when the policy's pick
    fails. If both policies pick the same item, alpha is unchanged.
    """

    def __init__(self, step: float = 0.05, alpha_min: float = 0.0, alpha_max: float = 2.0) -> None:
        self.step = step
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max

    def observe(
        self,
        store: MemoryStore,
        policy: LearnedPolicy,
        chosen_id: str,
        success: bool,
        baseline_id: str | None = None,
    ) -> LearnedPolicy:
        item = store.get(chosen_id)
        if success:
            item.success += 1
        else:
            item.failure += 1
        if baseline_id is not None and chosen_id != baseline_id:
            if success:
                policy.alpha = min(self.alpha_max, policy.alpha + self.step)
            else:
                policy.alpha = max(self.alpha_min, policy.alpha - self.step)
        return policy
