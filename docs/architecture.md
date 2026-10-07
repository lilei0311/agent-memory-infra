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


## Phase F architecture decision

The survey of existing systems is recorded in [EXISTING_MEMORY_SYSTEMS.md](EXISTING_MEMORY_SYSTEMS.md).

The top-level abstraction remains **Agent Memory**. Its internal architecture is now:

1. **Experience Layer** — interaction/observation, event boundary, Event Instance.
2. **Memory Graph** — Memory Point, Event Thread, Memory Block, and temporal/causal/referential/evidential/contextual relations.
3. **Memory Dynamics** — encoding, consolidation, retrieval/reactivation, reconsolidation, weakening, dormancy and accessibility recovery.
4. **Memory Policy** — write, retrieve, retain, revise, abstract and forget.
5. **Storage Adapter** — Graphiti, Mem0, Cognee, SQL/JSON/Markdown, vector or graph databases.

The important boundary is:

**Storage is below Dynamics.**

Existing systems already provide substantial graph, temporal context, entity linking and retrieval infrastructure. We should reuse them rather than recreate them. Our research target is the dynamics/policy layer operating over temporally connected experience.

### Memory Point

A conversation does not map directly to a memory.

The proposed path is:

**conversation stream → candidate Memory Points → event/thread formation → Memory Graph → Dynamic State**

A Memory Point is a weak candidate for future memory significance. Repetition, cross-session linkage, consequence, confirmation, contradiction or other evidence may increase or decrease its significance.

This gives us a principled way to handle casual conversation: an isolated remark can remain weak, while later references can reveal that it belongs to an important thread.

### Memory Graph vs Knowledge Graph

A knowledge graph is primarily:

**entity → relation → entity**

A memory graph is primarily:

**experience → relation → experience / abstraction**

Entities may exist inside the memory graph, but experience history is the primary evidence layer.

### Implementation order

Do not replace V0.1 yet.

1. Survey existing systems.
2. Freeze the object model: MemoryPoint, Event, Thread, Relation, MemoryBlock, MemoryState, RetrievalEvent.
3. Build a graph-only simulator.
4. Add dynamics as independently testable mechanisms.
5. Add backend adapters and compare against vector-only and existing graph-memory baselines.

The mathematical transition equations should remain open until the biological literature review is complete.
