# Architecture

v0 只有一条路：

1. `MemoryStore` 保存 item、embedding、success/failure。
2. `retrieve` 做两种打分：baseline 只用 cosine；policy 用 `similarity + alpha * utility`。
3. `FeedbackLearner` 把任务结果写回 item，并在 policy 选择不同于 baseline 时微调 alpha。
4. `RetrievalTrace` 记下本次取回的 id 和分数，供实验对照。

不接 Agent 运行时，不接总控平台。接入点留到假设被实验支持之后。


## Human-Inspired Memory Dynamics (research direction)

The next design layer is documented in [MEMORY_DYNAMICS.md](MEMORY_DYNAMICS.md). It introduces Event Instance, Event Thread, explicit relations, and a research state machine covering forming, consolidation, retrieval/reactivation, reconsolidation, dormancy, weakening, and inaccessibility/forgetting.

This layer is intentionally above the current V0.1 implementation. V0.1 remains the controlled baseline for experiments; V0.2 should not be implemented as a larger weighted score until the event/state model has been reviewed and its transitions are experimentally specified.
