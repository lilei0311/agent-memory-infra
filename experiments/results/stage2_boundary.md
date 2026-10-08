# Stage 2 boundary evidence

Code under test: `61b65c713f89afc40ac87483bbd63f1d9bf6b91d`

This file records execution only. It does not change the harness, V0.1 scripts, Phase G attention configuration, or Phase H seeds.

## Changed files in the implementation commit

- `src/memory_infra/adapter.py`
- `src/memory_infra/__init__.py`
- `tests/test_stage2_boundary.py`
- `docs/STAGE2_INTEGRATION_BOUNDARY.md`

No mechanism code changed. Locked Phase H seeds, budget, and policy were not changed.

## Commands

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

Executed at HEAD `61b65c713f89afc40ac87483bbd63f1d9bf6b91d`.

## pytest output

```
.........................................                                [100%]
41 passed in 0.08s
```

## experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`.

Replay match true. Seed 7 digests unchanged from the Phase H record:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

Trace artifact sha256 remained `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

V0.1 scripts and historical results were not edited.

## Exact-HEAD re-execution

Repository HEAD under review: `36e02913b31cf863f7c79c317b37fe22d02b5a78`

This section records commands run at that exact HEAD. Implementation semantics, seeds, budget, and policy were not changed. No V0.1 A/B/C/D/E artifact, Phase G locked artifact, or V0.2 mechanism file was edited.

### Changed-file scope

Evidence-only append to `experiments/results/stage2_boundary.md`. No source, test, harness, or historical result file was modified in this commit.

### Commands

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

Executed at HEAD `36e02913b31cf863f7c79c317b37fe22d02b5a78`.

### pytest output

```
.........................................                                [100%]
41 passed in 0.17s
```

### experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`.

Deterministic replay match true. Seed 7 digests:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

Trace artifact sha256 remained `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

V0.1 scripts and historical results were not edited.
