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

## Exact-current-HEAD rerun

Executed at HEAD `b89fbafccd39b0a885de0c5e421dff061e5d2240` as required by Issue #34 comment 6066175900. This evidence commit only records that run. It is not the executed HEAD. Stage 14 is not marked PASS.

Changed-file scope of this evidence commit:

- `experiments/results/stage14_visual_explorer.md`

No implementation files were changed. Seeds, budget, and policy were not changed. V0.1 scripts and historical Phase H / Phase G artifacts were not edited. No V0.2 transition semantic change.

Independent checks at the executed tree:

- pytest exit code 0, 109 passed.
- locked Phase H exit code 0; `deterministic_replay.match` is true; seeds `7,11,19`, budget `4`, policy `none`.
- historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.
- `src/memory_infra/explorer.py` does not import `memory_infra.store`.
- fixture `experiments/results/stage14_explorer_fixture.html` has no duplicate HTML ids; anchors `n-event_3a_ev-7-2` and `n-state_3a_ev-7-2` are both present; contradiction label and read-only status remain.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

### pytest output

```
........................................................................ [ 66%]
.....................................                                    [100%]
109 passed in 0.58s
```

Exit code 0.

### experiment output

Exit code 0. First line:

```
locked {'seeds': [7, 11, 19], 'budget': 4, 'policy': 'none', 'conditions': ('event_identity', 'thread_lifecycle', 'memory_lifecycle', 'evidence_integrity', 'deterministic_replay')}
```

Last line:

```
trace_artifact /tmp/agent-memory-infra/experiments/results/phase_h_trace.json 5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c
```

`deterministic_replay.match` is true for seeds 7, 11, and 19.
