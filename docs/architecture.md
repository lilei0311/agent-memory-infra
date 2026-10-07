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

## Attention Dynamics: focus and divergent modes

The next architectural addition is an explicit Attention State above Memory Dynamics and below the Agent interface.

The mechanism, not the LLM, owns attention-state transitions. The model may provide evidence/signals, but it does not directly decide the durable context state.

### Focus Mode
When interaction remains on one topic/thread:
- increase activation of the current Event Thread and its nearby Memory Graph neighborhood;
- progressively reduce competing thread activation;
- keep unrelated memories available but out of the active context;
- let the current thread occupy an increasing share of the working context;
- on topic return, restore the prior thread rather than rebuilding it from scratch.

This is intended to reduce context contamination and make the Agent's active context cleaner.

### Divergent / Brainstorm Mode
When the conversation intentionally jumps among topics without a stable dominant thread:
- avoid forcing a single-thread lock;
- maintain several active threads;
- retrieve related memories from multiple neighborhoods;
- permit cross-thread associations and novel combinations;
- keep a higher exploration/diversity budget.

The purpose is not maximal retrieval. It is controlled cross-thread collision: enough diversity to produce useful associations without flooding the context.

### Automatic state detection
No user command and no special LLM behavior should be required.

The control loop is:
conversation stream → topic/thread evidence → Attention State update → active-thread weights → memory retrieval budget → context assembly → Agent response

Candidate observable signals:
- topic continuity;
- semantic distance between successive turns;
- references to prior thread nodes;
- unresolved goal continuity;
- number of active threads;
- rapid topic switching;
- explicit brainstorming/question-generation cues;
- return-to-thread frequency.

Attention should be represented as a distribution over active threads rather than a single scalar:

A = {thread_1: 0.72, thread_2: 0.16, thread_3: 0.07, ...}

The exact thresholds are not frozen yet.

### Important separation
Memory state answers: What exists in memory, and what is its current dynamic condition?
Attention state answers: What should occupy the Agent's active cognitive/context budget right now?
Retrieval policy answers: Given the current attention state, which memory evidence should be brought into context?

This gives:
Memory Graph → Memory Dynamics → Attention State → Retrieval Policy → Context

rather than allowing the LLM to improvise context management.

The design is inspired by event segmentation, memory search, retrieval/reconsolidation and memory-linking research, but it is an engineering hypothesis rather than a claim that an Agent literally reproduces biological attention.