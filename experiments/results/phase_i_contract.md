# Phase I contract evidence

Code under test: `34a7c2aff3d5b0c91547486a9954b38d7d9addb6`

This file records execution only. It does not change the harness, V0.1 scripts, or Phase G attention configuration.

## Changed files in the contract commit

- `docs/V02_DYNAMICS_CONTRACT.md`
- `tests/test_v02_contract.py`

No mechanism code changed. Locked Phase H seeds, budget, and policy were not changed.

## Commands

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

Executed at HEAD `34a7c2aff3d5b0c91547486a9954b38d7d9addb6`.

## pytest output

```
...................................                                      [100%]
35 passed in 0.07s
```

## experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`.

Replay match true. Seed 7 digests unchanged from the Phase H record:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

Trace artifact `experiments/results/phase_h_trace.json` sha256 remained `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.


## Re-execution after relation provenance tests

Code under test: `b2d74e5944feaa19f49e4cc07acdce79c806a1c3`

Parent evidence HEAD was `9b4aae833b9c0a40c55e3294b26f228aff87277b`. The only code change since that HEAD is `tests/test_v02_contract.py`, which now asserts:

- split creates `contextual.changed_context` with provenance `new-context`
- merge creates `referential.same_thread` with provenance `same-goal`
- reopen creates `referential.revisits` with provenance `later-reference`

Mechanism code, Phase H harness, seeds, budget, and policy were not changed. V0.1 A/B/C/D/E scripts and historical results were not edited. Phase G locked attention config and results were not edited.

### Commands

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

Executed at HEAD `b2d74e5944feaa19f49e4cc07acdce79c806a1c3`.

### pytest output

```
....................................                                     [100%]
36 passed in 0.07s
```

### experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`.

Replay match true. Seed 7 digests unchanged from the locked Phase H record:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

Trace artifact `experiments/results/phase_h_trace.json` sha256 remained `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.
