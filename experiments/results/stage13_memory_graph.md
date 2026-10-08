# Stage 13 read-only Memory Graph projection evidence

Executed at implementation HEAD `4a85068c1c6ff8ee06981294d8a23563c2633ae6`. This evidence commit only records that run. It is not the executed HEAD. Do not treat this evidence commit as exact-current-HEAD acceptance. Stage 13 is not marked PASS.

Changed-file scope of the implementation commit:

- `docs/STAGE13_MEMORY_GRAPH.md`
- `docs/STAGE8_SKILL_API.md`
- `src/memory_infra/SKILL.md`
- `src/memory_infra/adapter.py`
- `src/memory_infra/graph_view.py`
- `src/memory_infra/skill.py`
- `src/memory_infra/store.py`
- `tests/test_stage13_graph.py`

This evidence commit adds only `experiments/results/stage13_memory_graph.md`.

Issue #32 required a public read-only Memory Graph projection over existing mechanism state. `read_graph` returns mechanism-owned point, event, thread, and state nodes and already-implemented relation edges. It does not allocate ids, append trace, or persist a second graph. Repeated events stay distinct. Contradiction edges keep both endpoints and evidence refs. Caller notes are not graph fields. Callers cannot supply nodes, edges, or mechanism ids on this read.

Seeds, budget, and policy were not changed. V0.1 scripts and historical Phase H / Phase G artifacts were not edited. No V0.2 transition semantic change.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

## pytest output

```
........................................................................ [ 69%]
...............................                                          [100%]
103 passed in 0.92s
```

Exit code 0. Baseline before this commit was 99 passed. The added tests cover mechanism-owned nodes and edges, repeated events, contradiction evidence, non-mutation, deterministic output, caller isolation, and ownership rejection.

## experiment output

Exit code 0. Literal locked line:

```
locked {'seeds': [7, 11, 19], 'budget': 4, 'policy': 'none', 'conditions': ('event_identity', 'thread_lifecycle', 'memory_lifecycle', 'evidence_integrity', 'deterministic_replay')}
```

Replay match: true.

Historical Phase H trace SHA-256:

```
5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c
```

Literal trace line:

```
trace_artifact /tmp/agent-memory-infra/experiments/results/phase_h_trace.json 5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c
```
