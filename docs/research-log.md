# Research log

## 2026-10-07

仓库单独拆出。第一阶段只验证：历史任务反馈能否让下一次 retrieval 好于纯向量相似度。

合成样例：最近邻居是重复失败，稍远的 item 是重复成功。policy 应选成功项，baseline 选失败项。

## 2026-10-07 (fix/align-code-with-protocols)

对齐代码与 docs/PROTOCOLS.md：

- RetrievalTrace 扩展为单条交互记录：trace_id、task_id、memory_id、retrieved、rank、mode、policy_version，加 used、task_success、user_feedback（缺失信号为 None，不猜测）。
- retrieve() 返回 list[RetrievalTrace]，每个取回项一条记录。
- FeedbackLearner：alpha 只在 policy 选对且不同于 baseline 时推高（成功）或降低（失败）；同选时不变。
- MemoryItem.utility 改为 Laplace 平滑：(success - failure) / (success + failure + 1)，防稀疏反馈打穿。
- policy.py 注释说明 v0.1 是两项式，四权重是文档目标。
- 测试补充：leaner 条件、alpha 不变、失败降低、utility 平滑。
