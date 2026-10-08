# Stage 5 integration evidence

Executed in a worktree based on `99903ce3e0cfde5bbcfe4c6638ffa1d694d1a9b8` with the Stage 5 contract and tests present and uncommitted. Seeds, budget, and policy were not changed. V0.1 scripts and historical Phase H results were not edited.

Changed-file scope of this commit:

- `docs/STAGE5_INTEGRATION_BOUNDARY.md`
- `tests/test_stage5_integration.py`
- `experiments/results/stage5_integration.md`

No V0.2 transition, store, or adapter code change. Phase H config was not retuned.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

## pytest output

```
................................................................         [100%]
64 passed in 0.35s
```

Baseline before this commit was 61 passed. The three added tests are the Stage 5 matrix.

## experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`. Replay match true. Seed 7 digests unchanged:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

trace_artifact experiments/results/phase_h_trace.json `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`

Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

## Stage 5 acceptance repair

Parent HEAD at execution: `0b609c0a6169e02585615a1c555fa9eda4b06ec8`.

The caller-boundary test was repaired in the worktree before these commands. Each forbidden field was sent on an otherwise valid `promote` request that used a point created by `observe`. Service-owned fields must raise `SnapshotError` matching `caller cannot own mechanism fields` and name the field. Signal-owned fields must raise `BoundaryError` matching `caller cannot set mechanism-owned fields` and name the field. Any rejection is no longer accepted.

Changed-file scope of this commit:

- `tests/test_stage5_integration.py`
- `experiments/results/stage5_integration.md`

No V0.2 transition, store, or adapter code change. Phase H config was not retuned. V0.1 scripts and historical Phase H results were not edited.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

### pytest output

```
................................................................         [100%]
64 passed in 0.41s
```

### experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`. Replay match true. Seed 7 digests unchanged:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

trace_artifact experiments/results/phase_h_trace.json `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`

Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.
