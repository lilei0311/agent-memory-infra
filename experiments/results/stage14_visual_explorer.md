# Stage 14 read-only Visual Memory Explorer evidence

Executed at implementation HEAD `0358dfff802b7b50c0febbaa85910a483420b19c`. This evidence commit only records that run. It is not the executed HEAD. Do not treat this evidence commit as exact-current-HEAD acceptance. Stage 14 is not marked PASS.

Changed-file scope of the implementation commit:

- `docs/STAGE14_VISUAL_EXPLORER.md`
- `src/memory_infra/explorer.py`
- `tests/test_stage14_explorer.py`
- `experiments/results/stage14_explorer_fixture.html`

This evidence commit adds only `experiments/results/stage14_visual_explorer.md`.

Issue #34 required a minimal local read-only Visual Memory Explorer over Stage 13 `read_graph`. `render_explorer` consumes that projection and emits deterministic HTML/SVG. It does not import `memory_infra.store`, allocate ids, or persist a second graph. Node kinds are labeled and shaped: point circle, event rectangle, thread rounded rectangle, state diamond. Relation types are labeled. Contradiction edges keep both endpoints and evidence refs. Repeated events stay distinct. Caller notes are not rendered.

Representative fixture: `experiments/results/stage14_explorer_fixture.html`.

Seeds, budget, and policy were not changed. V0.1 scripts and historical Phase H / Phase G artifacts were not edited. No V0.2 transition semantic change.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

## pytest output

```
........................................................................ [ 66%]
....................................                                     [100%]
108 passed in 0.43s
```

Exit code 0. Baseline before this commit was 103 passed.

## experiment output

Exit code 0. Locked config: seeds `7,11,19`, budget `4`, policy `none`. `deterministic_replay.match` is true.

Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.
