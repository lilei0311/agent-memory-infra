# Stage 3 persistence evidence

Code under test: `3c89826202611695ffd22f5be8cc9924182961fe`

This file records execution only. It does not change the harness, V0.1 scripts, Phase G attention configuration, or Phase H seeds.

## Changed files in the implementation commit

- `src/memory_infra/store.py`
- `src/memory_infra/__init__.py`
- `tests/test_stage3_persistence.py`
- `docs/STAGE3_PERSISTENCE_SEAM.md`

No V0.2 transition code changed. Locked Phase H seeds, budget, and policy were not changed.

## Commands

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

Executed at HEAD `3c89826202611695ffd22f5be8cc9924182961fe`.

## pytest output

```
..............................................                           [100%]
46 passed in 0.09s
```

## experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`.

Replay match true. Seed 7 digests:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

Historical Phase H trace sha256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

## Stage 3 authenticity repair

Code under test: `fd3cdfbd9006ffebcef891929e1c554b3bb8fa03`

This append records execution only. It does not change the harness, V0.1 scripts, Phase G attention configuration, or Phase H seeds.

## Changed files in the implementation commit

- `src/memory_infra/store.py`
- `tests/test_stage3_persistence.py`
- `docs/STAGE3_PERSISTENCE_SEAM.md`

No V0.2 transition code changed. Locked Phase H seeds, budget, and policy were not changed.

## Commands

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

Executed at HEAD `fd3cdfbd9006ffebcef891929e1c554b3bb8fa03`.

## pytest output

```
...............................................                          [100%]
47 passed in 0.10s
```

## experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`.

Replay match true. Seed 7 digests:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

Historical Phase H trace sha256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

Caller-rewritten snapshots that recompute the public SHA-256 checksum are rejected by the mechanism HMAC seal.

## Stage 3 instance-seal repair

Code under test: `e078951655aa23f178f30647698a27b3a1924de5`

This append records execution only. It does not change the harness, V0.1 scripts, Phase G attention configuration, or Phase H seeds.

## Changed files in the implementation commit

- `src/memory_infra/store.py`
- `tests/test_stage3_persistence.py`
- `docs/STAGE3_PERSISTENCE_SEAM.md`

No V0.2 transition code changed. Locked Phase H seeds, budget, and policy were not changed. The source-embedded `_MECHANISM_SEAL_KEY` constant was removed. Authenticity is an instance HMAC, not a source-public secret. Public SHA-256 remains a checksum only.

## Commands

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

Executed at HEAD `e078951655aa23f178f30647698a27b3a1924de5`.

## pytest output

```
................................................                         [100%]
48 passed in 0.11s
```

## experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`.

Replay match true. Seed 7 digests:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

Historical Phase H trace sha256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

Caller-rewritten snapshots that recompute the public SHA-256 checksum are rejected. The seal key is not in the snapshot and not in source.

## Stage 3 public-boundary seal repair

Code under test: `6e46f3d1debfc11baf26adb5cfc24e8d97c8a534`

This append records execution only. It does not change the harness, V0.1 scripts, Phase G attention configuration, or Phase H seeds.

## Changed files in the implementation commit

- `src/memory_infra/store.py`
- `tests/test_stage3_persistence.py`
- `docs/STAGE3_PERSISTENCE_SEAM.md`

No V0.2 transition code changed. Locked Phase H seeds, budget, and policy were not changed.

Threat model: public SHA-256 is checksum/integrity only. The instance HMAC key is not in source, not in the snapshot, and not an attribute of `MemoryService`, `InMemoryDurableStore`, or `GraphMemory`. The documented public API does not return it. Process-memory or private-table inspection is outside this boundary.

## Commands

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

Executed at HEAD `6e46f3d1debfc11baf26adb5cfc24e8d97c8a534`.

## pytest output

```
................................................                         [100%]
48 passed in 0.07s
```

## experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`.

Replay match true. Seed 7 digests:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

Historical Phase H trace sha256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

## Exact-HEAD execution at 9e3a3cb

Code under test: `9e3a3cb1e258123433eb1e6263dea18a7a4f0c03`

This append records execution only. It does not change the harness, V0.1 scripts, Phase G attention configuration, or Phase H seeds.

## Changed-file scope

This execution did not change implementation files. The HEAD under test already contains:

- `src/memory_infra/store.py`
- `tests/test_stage3_persistence.py`
- `docs/STAGE3_PERSISTENCE_SEAM.md`
- prior evidence in `experiments/results/stage3_persistence.md`

No V0.2 transition code changed. Locked Phase H seeds, budget, and policy were not changed.

## Commands

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

Executed at HEAD `9e3a3cb1e258123433eb1e6263dea18a7a4f0c03`.

## pytest output

```
................................................                         [100%]
48 passed in 0.07s
```

## experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`.

Replay match true. Seed 7 digests:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

Historical Phase H trace sha256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.
