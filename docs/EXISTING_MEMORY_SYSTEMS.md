# Existing Agent Memory Systems: Reuse Map

## Purpose
Before implementing V0.2, identify what already exists and separate:
1. capabilities we should reuse;
2. architectural ideas we should borrow;
3. mechanisms we should not mistake for memory dynamics;
4. gaps that justify continuing this research.

> Memory Graph / temporal context is no longer an unexplored engineering problem. Memory Dynamics remains the more interesting layer.

## 1. Systems worth studying

| System | Core idea | Graph | Time | Episodic source | Memory update | Retrieval | Main lesson |
|---|---|---:|---:|---:|---:|---:|---|
| Graphiti / Zep | temporal context graph for agents | Yes | Strong | Yes | Incremental | semantic + keyword + graph | Closest existing implementation to our graph/thread direction |
| Mem0 | production memory layer + entity linking | Yes | Yes | Memory-oriented | Add/update/link | semantic + BM25 + entity | Strong practical baseline; graph is mainly retrieval support |
| Letta / MemGPT | stateful agent with explicit memory blocks | Not core | Implicit | Conversation/state | Agent-managed | Agent/tool driven | Excellent for explicit memory control, less like a temporal event graph |
| LangMem | memory management primitives for agents | Optional storage | Some | Conversation-derived | Hot-path + background | Store/search | Useful adapter/policy layer |
| Cognee | ingest → knowledge graph → recall | Yes | Some | Source documents/conversations | Pipeline-based | graph + vector/search | Useful self-hosted graph/memory infrastructure |

### Graphiti / Zep
Graphiti is explicitly designed as a temporally-aware knowledge graph for AI agents. It supports incremental updates, historical relationships, bi-temporal information, and hybrid retrieval. Zep uses Graphiti as its graph/memory layer.
References: https://github.com/getzep/graphiti and https://arxiv.org/abs/2501.13956

Borrow: episodic source records; temporal validity; incremental graph updates; hybrid retrieval; provenance/history; separate raw episodes from derived entities/facts.
Do not simply copy: graph retrieval is not the same thing as memory dynamics. A temporal graph can tell us what was true when, but not necessarily why a memory becomes accessible, dormant, reconsolidated, or strongly reinforced.

### Mem0
Mem0 is a production-oriented memory layer. Its current graph memory extracts entities and connects memories through shared entities. Its newer memory approach emphasizes additive storage, entity linking, multi-signal retrieval, and temporal reasoning.
References: https://github.com/mem0ai/mem0 and https://github.com/mem0ai/mem0/blob/main/docs/platform/features/graph-memory.mdx

Borrow: additive/non-destructive memory; entity linking; multi-signal retrieval; practical memory evaluation; explicit distinction between memory scope and graph entities.
Important limitation: Mem0's native graph is primarily a retrieval structure. It is not yet the richer Event → Thread → Causal/Evidential/Contextual Relation → Dynamic State model we are investigating.

### Letta / MemGPT
Letta treats an agent as a stateful system with explicit memory blocks and mechanisms for managing memory over long contexts.
Reference: https://github.com/letta-ai/letta
Borrow: explicit memory boundaries; persistent agent state; agent-visible memory management; memory management as part of the agent control loop.
Difference: Letta's central abstraction is stateful-agent memory management, not a temporal event graph with human-inspired memory dynamics.

### LangMem
LangMem provides memory-management primitives that can work with different storage systems. It supports active/hot-path memory management and background extraction/consolidation.
Reference: https://github.com/langchain-ai/langmem
Borrow: storage-agnostic memory API; hot-path vs background processing; automatic extraction/consolidation; clean adapter boundary.

### Cognee
Cognee is an open-source AI memory platform centered on turning data into a knowledge graph that agents can recall and connect.
Reference: https://github.com/topoteretes/cognee
Borrow: self-hosted graph memory; ingestion pipeline; graph + vector/search combination; local deployment as an engineering option.
Difference: Cognee is primarily end-to-end memory/knowledge infrastructure. Our research question is narrower and lower-level: what computational dynamics should govern the lifecycle of an experience?

## 2. The architecture gap
Existing systems cover much of this:

conversation/data → extraction → entity/fact/memory → graph → retrieval

Our proposed model adds another dimension:

experience → event → thread → relations → memory state → state transition → future accessibility/use

Existing systems mostly answer: what should I store, what is related, what was true when, what is relevant, how do I update/retrieve?
Our research asks: when does an interaction become memory-worthy; when should events form a thread; what causes stability; what happens after retrieval; how does contradiction update old evidence; how can accessibility fall without deletion; how do consequence, surprise, repetition and confirmation affect future access?

Therefore we should NOT build another Graphiti/Mem0 clone.

## 3. Proposed architecture after the survey
The top-level product remains Agent Memory.

Internal layers:

Agent Memory
├── 1. Experience Layer
│   ├── Interaction / Observation
│   ├── Event Instance
│   └── Event Boundary / Segmentation
├── 2. Memory Graph
│   ├── Memory Point
│   ├── Event Thread
│   ├── Memory Block
│   └── Relations: temporal / causal / referential / evidential / contextual
├── 3. Memory Dynamics
│   ├── encoding
│   ├── consolidation
│   ├── retrieval / reactivation
│   ├── reconsolidation
│   ├── weakening
│   ├── dormancy
│   └── accessibility recovery
├── 4. Memory Policy
│   ├── write / retrieve / retain / revise / abstract / forget
└── 5. Storage Adapter
    ├── Graphiti
    ├── Mem0
    ├── Cognee
    ├── SQL / JSON / Markdown
    └── Vector / graph DB

The crucial decision is that Storage is below Dynamics. Graphiti, Mem0 and Cognee can become backends or experimental baselines; they should not define what a memory is.

## 4. New key concept: Memory Point
The user's '闲聊中的记忆点' should become a first-class research object.

A conversation should not be message → memory.
It should be:
conversation stream → candidate memory points → event/thread formation → memory graph

A Memory Point is a candidate unit of future memory significance. It may start weak and uncertain:

candidate → repeated / connected / consequential / confirmed → memory-worthy → event / thread → stable memory structure

This solves a major problem that a simple conversation summarizer does not: not every sentence is a memory, but an apparently casual sentence can become important later.

Example:
Day 1: 最近感觉经济师这几个概念总混。
Day 3: 昨天你说的需求弹性，我又错了。
Day 10: 我发现我总是把需求量变化和需求变化混在一起。

A naive system stores three isolated facts. Our graph should discover: three conversational observations → same learning thread → repeated failure pattern → emerging memory block.

## 5. Memory Graph is not the same as a Knowledge Graph
Knowledge Graph: entity → relation → entity.
Memory Graph: experience → relation → experience / abstraction.

Entities can exist inside the graph, but they are not necessarily the primary unit.

## 6. Recommended implementation strategy
Do not replace V0.1 immediately.

### Stage F-1 — Survey
Study Graphiti, Mem0, Letta, LangMem, Cognee.
Deliverable: architecture comparison; reusable components; gaps; adapter boundary.

### Stage F-2 — Formalize our object model
Freeze: MemoryPoint, Event, Thread, Relation, MemoryBlock, MemoryState, RetrievalEvent.
Do not yet freeze the mathematical dynamics.

### Stage F-3 — Build a graph-only simulator
Simulate casual conversation, repeated topic, cross-session references, contradiction, successful/failed retrieval, context change and delayed feedback. Measure whether graph structure evolves correctly.

### Stage F-4 — Add dynamics
Only after the graph is stable: encoding → consolidation → retrieval → reconsolidation → weakening/dormancy. Each mechanism should be independently testable.

### Stage F-5 — Backend adapters
Then test Graphiti, Mem0, Cognee, a simple local graph, and a vector-only baseline.
This answers a stronger question: does the memory-dynamics policy improve the same underlying storage system?

## 7. Current research hypothesis
The strongest hypothesis emerging from the survey is:

> The missing layer is not another storage technology. It is a policy/dynamics layer that operates over temporally connected experience graphs.

Memory Graph = what experiences and relationships exist.
Memory Dynamics = how those experiences change over time.
Memory Policy = what the Agent does with that dynamic state.

## 8. Biological evidence already supporting the direction
Human experience is continuously segmented into discrete events; event boundaries are important for episodic memory organization. Event representations have rich internal structure and connections, with causal connectivity important in the Event Horizon Model. Event boundaries can reflect external and internal changes including goals, affect and motivation. Retrieval can be followed by reconsolidation, so an existing memory can become modifiable rather than simply read from immutable storage. Retrieval practice can slow forgetting. Prediction error and salient novelty are being investigated as factors facilitating memory modification.

References:
- https://academic.oup.com/edited-volume/57928/chapter-abstract/475474913
- https://www.annualreviews.org/content/journals/10.1146/annurev-psych-010419-051101
- https://pmc.ncbi.nlm.nih.gov/articles/PMC5734104/
- https://www.nature.com/articles/nrn2590
- https://www.annualreviews.org/content/journals/10.1146/annurev-psych-010419-051019
- https://www.sciencedirect.com/science/article/pii/S0306452225011972

These findings support the research direction, not a claim that our software state machine is biologically equivalent to the brain.

## 9. Decision
Do not build another Mem0, another GraphRAG, or another vector-memory wrapper.

Build/research: Agent Memory Dynamics Engine.

Core model:
Memory Point → Event → Thread → Relation → Dynamic State → Transition

Infrastructure boundary:
Dynamics Engine ↔ Storage / Retrieval Backend

This is now the recommended direction for Phase F.