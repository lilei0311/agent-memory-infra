# Stage 4 file store evidence

Code under test: `02f088164a832e7a2cd0957f024a35cf00c97cb5`

This file records execution only. It does not change the harness, V0.1 scripts, Phase G attention configuration, or Phase H seeds.

## Changed files in the implementation commit

- `src/memory_infra/store.py`
- `src/memory_infra/__init__.py`
- `tests/test_stage4_file_store.py`
- `docs/STAGE4_FILE_STORE.md`

No V0.2 transition code changed. Locked Phase H seeds, budget, and policy were not changed.

## Commands

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

Executed at HEAD `02f088164a832e7a2cd0957f024a35cf00c97cb5`.

## pytest output

```
............................................................             [100%]
60 passed in 0.35s
```

## experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`.

Replay match true. Seed 7 digests:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

Historical Phase H trace sha256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

## Exact-HEAD re-execution

Code under test: `8138d706a58c01daa988ff95807d361c309de7e2`

Evidence-only parent. Commands re-executed at this HEAD. No mechanism, test, V0.1, Phase G, or Phase H config change.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

## pytest output

```
............................................................             [100%]
60 passed in 0.27s
```

## experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`. Replay match true. Historical Phase H trace sha256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.
