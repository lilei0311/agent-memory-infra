# Stage 7 heterogeneous agent-facing evidence

Executed in a worktree based on `1f09e65541fd66274e0098f6eb1bc916b777043e` with the Stage 7 contract, two caller wrappers, and tests present. Seeds, budget, and policy were not changed. V0.1 scripts and historical Phase H results were not edited. Stage 7 is not marked PASS.

Changed-file scope of this commit:

- `docs/STAGE7_AGENT_FACING_BOUNDARY.md`
- `src/memory_infra/clients.py`
- `tests/test_stage7_agent_facing.py`
- `experiments/results/stage7_agent_facing.md`

No V0.2 transition semantic change. Caller notes remain service request metadata and are not snapshot fields. Phase H config was not retuned.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

## pytest output

```
....................................................................     [100%]
68 passed in 0.33s
```

Exit code 0. Baseline before this commit was 66 passed. The two added tests are the Stage 7 heterogeneous-client checks.

## experiment output

Exit code 0. Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`. Replay match true. Seed 7 digests unchanged:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

trace_artifact experiments/results/phase_h_trace.json `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`

Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`. Working tree after the run did not modify `experiments/results/phase_h_trace.json`.

Non-contamination: V0.1 scripts, Phase G artifacts, and Phase H locked config were not edited. `MethodCaller` and `EnvelopeCaller` only call `CallerSession.request`.
