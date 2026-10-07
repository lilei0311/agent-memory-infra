# Stage 1 Architecture

## Goal

Stage 1 validates one research question: can historical task outcomes improve memory retrieval over a relevance-only baseline?

The system is storage-agnostic, agent-agnostic, reproducible, and intentionally small.

## System boundary

Task -> Candidate Memories -> Memory Adapter -> Memory Policy -> Top-K Retrieval -> Agent/Simulator -> Outcome -> Trace -> Policy Update -> next task.

The project owns policy, protocol, trace, evaluation, and simulation. It does not own the user's memory store.

## Components

### Memory Protocol
Canonical logical representation of a memory independent of storage technology. Core concepts: memory_id, content_ref, normalized features, metadata, timestamps, and optional reliability/utility state.

### Memory Adapter
Integration boundary between policy and storage. Minimum logical operations: search(task, limit), get(memory_id), write(memory), update(memory_id, patch), archive(memory_id). Stage 1 may use an in-memory adapter.

### Candidate Generation
Separate candidate generation from ranking. Baseline and adaptive policies must receive identical candidates so candidate-generation differences do not contaminate experiments.

### Memory Policy
V0.1 baseline score = relevance. Adaptive score = weighted relevance + historical utility + reliability + context fit. Weights are explicit and inspectable.

### Agent / Simulator
Stage 1 uses a deterministic or seeded simulator. It defines which memories are useful, how useful memories affect success, and how misleading memories create cost or failure.

### Trace
Record identifiers, normalized features, retrieval decisions, outcome signals, and policy version. Raw user conversation is out of scope.

### Policy Update
Use incremental, explainable updates. No neural training or reinforcement-learning framework is required.

### Evaluation
Compare policies on identical task sequences and candidate sets. Primary metrics: task success rate, useful-memory precision, retrieval waste, correction/error rate, cumulative reward, and convergence/stability.

## Invariants

- Baseline and adaptive policies see identical candidates.
- Traces refer to immutable task and memory identifiers.
- Policy versions are recorded in traces.
- Historical traces are never mutated by policy updates.
- Storage can be replaced without changing policy logic.
- Experiments are reproducible from seed and configuration.
- Stage 1 has no dependency on external users or production telemetry.

## Stage 1 non-goals

LLM reasoning, vector database integration, distributed training, production authentication, anonymous telemetry, public Skill packaging, and cross-user learning are deferred until after controlled validation.
