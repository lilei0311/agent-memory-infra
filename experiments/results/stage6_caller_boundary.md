# Stage 6 caller isolation evidence

Executed in a worktree based on `73d3de13bcd8708400a39a3d3446d602c69d08e9` with the Stage 6 contract, service seam, and tests present. Seeds, budget, and policy were not changed. V0.1 scripts and historical Phase H results were not edited. Stage 6 is not marked PASS.

Changed-file scope of this commit:

- `docs/STAGE6_CALLER_BOUNDARY.md`
- `src/memory_infra/store.py`
- `tests/test_stage6_caller_isolation.py`
- `experiments/results/stage6_caller_boundary.md`

No V0.2 transition semantic change. Caller notes are service request metadata and are not snapshot fields. Phase H config was not retuned.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

## pytest output

```
..................................................................       [100%]
66 passed in 0.40s
```

Exit code 0. Baseline before this commit was 64 passed. The two added tests are the Stage 6 caller-isolation checks.

## experiment output

Exit code 0. Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`. Replay match true. Seed 7 digests unchanged:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

trace_artifact experiments/results/phase_h_trace.json `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`

Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

The recorded commands ran against parent `73d3de13bcd8708400a39a3d3446d602c69d08e9` plus this uncommitted Stage 6 diff. This file does not claim that a later evidence-only commit was itself executed.
