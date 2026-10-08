# Stage 12 explicit historical-memory import evidence

Executed at implementation HEAD `aca72fc4e58659e0a900445665a0ed04e2d9c2e6`. This evidence commit only records that run. It is not the executed HEAD. Do not treat this evidence commit as exact-current-HEAD acceptance. Stage 12 is not marked PASS.

Changed-file scope of the implementation commit:

- `docs/STAGE12_IMPORT_SEAM.md`
- `src/memory_infra/SKILL.md`
- `src/memory_infra/entrypoint.py`
- `src/memory_infra/importer.py`
- `tests/test_stage12_import.py`

This evidence commit adds only `experiments/results/stage12_import_seam.md`.

Issue #31 required a public explicit import after discovery. `handle.start` remains read-only. `handle.import_selected` structures selected recognized `MEMORY.md` / `memory.md` / `memories.json` / `memory.json` material through the public Skill API. Mechanism code assigns point, event, and evidence ids. Provenance is `import:<path>`. Duplicate policy is `idempotent_by_source_digest`. Unknown and unreadable selections are rejected. Source files are not rewritten.

Seeds, budget, and policy were not changed. V0.1 scripts and historical Phase H / Phase G artifacts were not edited. No V0.2 transition semantic change.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

## pytest output

```
........................................................................ [ 74%]
.........................                                                [100%]
97 passed in 0.37s
```

Exit code 0. Baseline before this commit was 91 passed. The added tests cover discovery without import, explicit import, provenance, idempotent repeat, unknown/unreadable rejection, caller isolation, and unchanged source files.

## experiment output

Exit code 0. Literal locked line:

```
locked {'seeds': [7, 11, 19], 'budget': 4, 'policy': 'none', 'conditions': ('event_identity', 'thread_lifecycle', 'memory_lifecycle', 'evidence_integrity', 'deterministic_replay')}
```

Replay match true. Seed 7 digests unchanged:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

trace_artifact experiments/results/phase_h_trace.json `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`

Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`. Working tree after the run did not modify `experiments/results/phase_h_trace.json`.

## Stage 12 duplicate-policy repair

Executed at implementation HEAD `f55b5da022be18a7a9544e3b040b5377585b1b38`. This evidence commit only records that run. It is not the executed HEAD. Do not treat this evidence commit as exact-current-HEAD acceptance. Stage 12 is not marked PASS. Issue #31 remains open.

Changed-file scope of the implementation commit:

- `docs/STAGE12_IMPORT_SEAM.md`
- `src/memory_infra/entrypoint.py`
- `src/memory_infra/importer.py`
- `tests/test_stage12_import.py`

This evidence commit adds only the repair section in `experiments/results/stage12_import_seam.md`.

Issue #31 comment required the duplicate policy to match the documented source-level digest. The ledger key is now path plus SHA-256 of the selected source snapshot bytes. A repeated identical snapshot reuses recorded point and event ids. A changed snapshot digest is a new import. Distinct parsed occurrences in one snapshot are not collapsed. Provenance remains `import:<path>`. Source files are not rewritten.

Seeds, budget, and policy were not changed. V0.1 scripts and historical Phase H / Phase G artifacts were not edited. No V0.2 transition semantic change.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

## pytest output

```
........................................................................ [ 72%]
...........................                                              [100%]
99 passed in 0.33s
```

Exit code 0. Baseline before this repair was 97 passed. Added tests cover identical repeated source import, changed source digest as a new import, uncollapsed identical occurrences, provenance, and unchanged source bytes.

## experiment output

Exit code 0. Literal locked line:

```
locked {'seeds': [7, 11, 19], 'budget': 4, 'policy': 'none', 'conditions': ('event_identity', 'thread_lifecycle', 'memory_lifecycle', 'evidence_integrity', 'deterministic_replay')}
```

Replay match true. Seed 7 digests unchanged:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

trace_artifact experiments/results/phase_h_trace.json `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`

Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`. Working tree after the run did not modify `experiments/results/phase_h_trace.json`.
