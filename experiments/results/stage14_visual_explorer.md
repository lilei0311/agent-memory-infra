# Stage 14 read-only Visual Memory Explorer evidence

Executed at implementation HEAD `1453da99de93fd20a5e24a9d220735fb1c44db24`. This evidence commit only records that run. It is not the executed HEAD. Do not treat this evidence commit as exact-current-HEAD acceptance. Stage 14 is not marked PASS.

Changed-file scope of the implementation commit:

- `docs/STAGE14_VISUAL_EXPLORER.md`
- `src/memory_infra/explorer.py`
- `tests/test_stage14_explorer.py`
- `experiments/results/stage14_explorer_fixture.html`

This evidence commit updates only `experiments/results/stage14_visual_explorer.md`.

Issue #34 P1: presentation identity was keyed only by mechanism id, so event/state/thread nodes that share an id collided in position and HTML id. Repair keys positions and DOM anchors by `(kind, id)` via `presentation_key`. Displayed `data-id` remains the mechanism-owned id. Stage 13 graph identity is unchanged.

Representative fixture: `experiments/results/stage14_explorer_fixture.html`. Same-id event `ev-7-2` and state `ev-7-2` have distinct anchors `n-event_3a_ev-7-2` and `n-state_3a_ev-7-2`.

Seeds, budget, and policy were not changed. V0.1 scripts and historical Phase H / Phase G artifacts were not edited. No V0.2 transition semantic change.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

## pytest output

```
........................................................................ [ 66%]
.....................................                                    [100%]
109 passed in 0.38s
```

Exit code 0. Baseline before this repair was 108 passed.

## experiment output

Exit code 0. Locked config: seeds `7,11,19`, budget `4`, policy `none`. `deterministic_replay.match` is true.

Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.
