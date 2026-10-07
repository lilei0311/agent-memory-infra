# Stage 1 Protocols

## Memory Record

Canonical logical shape:

    {
      "memory_id": "memory_123",
      "content_ref": "opaque-or-local-reference",
      "features": {"relevance": 0.82, "context_fit": 0.70},
      "metadata": {"created_at": "2026-01-01T00:00:00Z", "source": "agent-local"}
    }

content_ref may point to local Markdown, JSON, SQL, a vector store, or another private representation. The policy layer must not require raw content.

## Candidate

    {
      "memory_id": "memory_123",
      "features": {"relevance": 0.82, "context_fit": 0.70}
    }

Candidate generation and policy ranking are separate interfaces.

## Trace

    {
      "trace_id": "trace_001",
      "task_id": "task_001",
      "memory_id": "memory_123",
      "retrieved": true,
      "rank": 1,
      "used": true,
      "task_success": true,
      "user_feedback": 1,
      "policy_version": "adaptive-v0.1"
    }

Rules: one trace describes one memory-task interaction; missing signals are unknown rather than guessed; traces are append-only; raw conversation is not required; policy version is mandatory for experiment attribution.

## Outcome

    {
      "task_success": true,
      "correction_count": 0,
      "execution_cost": 1.0,
      "memory_helpful": true
    }

The evaluator converts these signals into comparable metrics.

## Adapter Contract

search(task_context, limit) -> Candidate[]
get(memory_id) -> Memory
write(memory) -> memory_id
update(memory_id, patch) -> Memory
archive(memory_id) -> success

Adapters translate this contract to any underlying store.

## Policy Contract

rank(task, candidates, state) -> RankedCandidate[]
update(trace_batch, state) -> new_state

The policy consumes normalized features and historical state rather than storage-specific representations.

## Experiment Contract

Every experiment records experiment_id, seed, task distribution, candidate configuration, policy configuration, K, task count, metrics, and policy version. Baseline and adaptive runs must use the same seed, task stream, and candidate sets.
