from memory_infra.memory import MemoryStore
from memory_infra.policy import LearnedPolicy


class FeedbackLearner:
    """Apply task outcome to the retrieved item, then nudge alpha."""

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
            delta = self.step if success else -self.step
            policy.alpha = min(self.alpha_max, max(self.alpha_min, policy.alpha + delta))
        return policy
