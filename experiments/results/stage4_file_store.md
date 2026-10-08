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

## Exact-HEAD re-execution at fd5cfff

Code under test: `fd5cfff49cc6e5ffde71da2041835652ae9222aa`

Evidence-only parent. Commands re-executed at this HEAD. No mechanism, test, V0.1, Phase G, or Phase H config change.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

## pytest output

```
............................................................             [100%]
60 passed in 0.36s
```

## experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`. Replay match true. Seed 7 digests unchanged:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

Historical Phase H trace sha256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

## Stage 4 seal-extraction repair at 521d79d

Code under test: `521d79d34b20d245b385b90e1ccc7013fbf2b412`

Public `restart_seal` removed. Seal stays in the private capability table and out of the snapshot. Process restart still takes an out-of-band key. Adversarial regression uses only the package/service/store surface and rejects a rewritten file. No V0.1, Phase G, or Phase H config/result change. V0.2 transitions unchanged.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

## pytest output

```
.............................................................            [100%]
61 passed in 0.24s
```

## experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`. Replay match true. Seed 7 digests unchanged:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

trace_artifact /tmp/agent-memory-infra/experiments/results/phase_h_trace.json 5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c

## Exact-HEAD re-execution at 0c2498c

Code under test: `0c2498c77e9c7e50b9ea77b5eaebdcd142dbc913`

Evidence-only parent. Commands re-executed at this HEAD. Changed-file scope of this evidence commit is `experiments/results/stage4_file_store.md` only. No mechanism, test, V0.1 A/B/C/D/E, Phase G, or V0.2 transition change. Phase H config and historical results were not retuned.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

## pytest output

```
.............................................................            [100%]
61 passed in 0.36s
```

## experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`. Replay match true. Seed 7 digests unchanged:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

trace_artifact experiments/results/phase_h_trace.json `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`

Public seal extraction remains removed. Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

## Exact-HEAD re-execution at 86386fd

Code under test: `86386fd06731e60e38b65da15b4210381067511d`

Evidence-only parent. Commands re-executed at this HEAD. Changed-file scope of this evidence commit is `experiments/results/stage4_file_store.md` only. No mechanism, test, V0.1 A/B/C/D/E, Phase G, or V0.2 transition change. Phase H config and historical results were not retuned.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

## pytest output

```
.............................................................            [100%]
61 passed in 0.40s
```

## experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`. Replay match true. Seed 7 digests unchanged:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

trace_artifact experiments/results/phase_h_trace.json `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`

Public seal extraction remains removed. Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

## Exact-HEAD re-execution at c991fe2

Code under test: `c991fe272168e7990b90afb86764eac62794aa5d`

Evidence-only parent. Commands re-executed at this HEAD. Changed-file scope of this evidence commit is `experiments/results/stage4_file_store.md` only. No mechanism, test, V0.1 A/B/C/D/E, Phase G, or V0.2 transition change. Phase H config and historical results were not retuned. Public restart-seal extraction remains absent.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

## pytest output

```
.............................................................            [100%]
61 passed in 0.26s
```

## experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`. Replay match true. Seed 7 digests unchanged:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

trace_artifact experiments/results/phase_h_trace.json `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`

Public seal extraction remains removed. Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

## Exact-HEAD re-execution at 6896106

Code under test: `68961062239b2d7f0490433e5054e85ffd863c94`

Evidence-only parent. Commands re-executed at this HEAD. Changed-file scope of this evidence commit is `experiments/results/stage4_file_store.md` only. No mechanism, test, V0.1 A/B/C/D/E, Phase G, or V0.2 transition change. Phase H config and historical results were not retuned. Public restart-seal extraction remains absent.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

## pytest output

```
.............................................................            [100%]
61 passed in 0.27s
```

## experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`. Replay match true. Seed 7 digests unchanged:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

trace_artifact experiments/results/phase_h_trace.json `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`

Public seal extraction remains removed. Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

## Exact-HEAD re-execution at 214d882

Code under test: `214d8824b4f6b6d261a11688d124d07813fb4b54`

Evidence-only parent. Commands re-executed at this HEAD. Changed-file scope of this evidence commit is `experiments/results/stage4_file_store.md` only. No mechanism, test, V0.1 A/B/C/D/E, Phase G, or V0.2 transition change. Phase H config and historical results were not retuned. Public restart-seal extraction remains absent.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

## pytest output

```
.............................................................            [100%]
61 passed in 0.34s
```

## experiment output

Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`. Replay match true. Seed 7 digests unchanged:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

trace_artifact experiments/results/phase_h_trace.json `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`

Public seal extraction remains removed. Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.
