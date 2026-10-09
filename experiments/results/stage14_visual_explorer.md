# Stage 14 read-only Visual Memory Explorer evidence

## Issue #39 independent check of repaired implementation 85b188d

Executed at implementation SHA `85b188d02d8ba6a0c7cc30a0a3a28fbaf539563a`. Current repository HEAD before this evidence commit was `7139b5850cadf6d14f2b315519be5907dacaca39`. This evidence commit only records the independent run. It is not the executed HEAD. Stage 14 is not marked PASS. Issue #39 is left open. No next-stage issue was opened.

Ancestry:

```
git diff --name-only 85b188d02d8ba6a0c7cc30a0a3a28fbaf539563a..7139b5850cadf6d14f2b315519be5907dacaca39
experiments/results/stage14_visual_explorer.md

git diff --name-only 85b188d02d8ba6a0c7cc30a0a3a28fbaf539563a^..85b188d02d8ba6a0c7cc30a0a3a28fbaf539563a
docs/STAGE14_VISUAL_EXPLORER.md
src/memory_infra/explorer.py
tests/test_stage14_explorer.py
```

`7139b5850cadf6d14f2b315519be5907dacaca39` is evidence-only relative to implementation SHA `85b188d02d8ba6a0c7cc30a0a3a28fbaf539563a`. Parent of the implementation commit is `fec8f8a405d2b83d29e875be46cadc17be5811c2`.

Commands after `git checkout 85b188d02d8ba6a0c7cc30a0a3a28fbaf539563a` and `git rev-parse HEAD` equaled that SHA:

```bash
git rev-parse HEAD
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

`git rev-parse HEAD` printed `85b188d02d8ba6a0c7cc30a0a3a28fbaf539563a`.

### pytest

Exit code 0.

```
........................................................................ [ 64%]
.......................................                                  [100%]
111 passed in 0.59s
```

### locked Phase H

Exit code 0. Locked config unchanged: seeds 7, 11, 19; budget 4; policy none. `deterministic_replay.match` true for seeds 7, 11, and 19. Historical trace SHA-256 unchanged: `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

First line:

```
locked {'seeds': [7, 11, 19], 'budget': 4, 'policy': 'none', 'conditions': ('event_identity', 'thread_lifecycle', 'memory_lifecycle', 'evidence_integrity', 'deterministic_replay')}
```

Last line:

```
trace_artifact /tmp/agent-memory-infra/experiments/results/phase_h_trace.json 5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c
```

Working tree after the commands had no tracked artifact diff. Seeds, budget, and policy were not changed. V0.1 and Phase G artifacts were not edited.

Static checks at the implementation SHA: fixture `experiments/results/stage14_explorer_fixture.html` has 9 unique HTML ids and no duplicates; anchors `n-event_3a_ev-7-2` and `n-state_3a_ev-7-2` are both present. `src/memory_infra/explorer.py` imports only `html` and `typing`; it does not import `memory_infra.store`. Fallback endpoint kinds match Stage 13 creation relations in `graph.py`: contradiction/causal/temporal/same_thread bind events; `contextual.changed_context` binds threads; `referential.revisits` binds thread to event. No unmapped Stage 13 relation type was found. Same-id state/point nodes are not marked contradiction endpoints.

Chromium headless (`/usr/bin/chromium`, already installed; no new dependency) loaded generated explorer HTML and dispatched view/search events. Contradiction view kept event endpoints visible, hid same-id state and point nodes, kept the contradiction edge and label visible, and hid non-contradiction edges. Search `both-seen` and `e1` kept both contradiction endpoints, the contradiction relation, and its inspector article visible, and kept the same-id state node hidden. Thread view showed the thread node and thread edge only. Event view showed event nodes and event-event edges only. All-view search `thread alpha` showed only the thread node. This was a headless DOM probe, not a manual browser session.

No concrete defect was found in this run. This execution record does not mark Stage 14 PASS.

## Prior evidence

# Stage 14 read-only Visual Memory Explorer evidence

## Issue #40 kind-qualified contradiction endpoints

Executed at implementation HEAD `85b188d02d8ba6a0c7cc30a0a3a28fbaf539563a`. This evidence commit only records that run. It is not the executed HEAD. Do not treat this evidence commit as exact-current-HEAD acceptance. Stage 14 is not marked PASS.

Changed-file scope of the implementation commit:

- `src/memory_infra/explorer.py`
- `tests/test_stage14_explorer.py`
- `docs/STAGE14_VISUAL_EXPLORER.md`

Issue #40: contradiction endpoint membership and reveal were keyed by mechanism id alone, and edge geometry used the first id match. The fix binds endpoints by explicit `source_kind`/`target_kind` when present, otherwise by the Stage 13 mechanism creation contract. Same-id state or point nodes are not contradiction endpoints. Stage 13 graph identity, V0.2 transitions, Phase H config, and V0.1 artifacts were not changed.

Commands at `85b188d02d8ba6a0c7cc30a0a3a28fbaf539563a`:

```bash
git rev-parse HEAD
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

`git rev-parse HEAD` printed `85b188d02d8ba6a0c7cc30a0a3a28fbaf539563a`.

### pytest

Exit code 0.

```
........................................................................ [ 64%]
.......................................                                  [100%]
111 passed in 0.56s
```

### locked Phase H

Exit code 0. Locked config unchanged: seeds 7, 11, 19; budget 4; policy none. `deterministic_replay.match` true. Historical trace SHA-256 unchanged: `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.

No browser/DOM runtime was executed. Filter reveal behavior is covered by HTML/script assertions, not a browser interaction run.

Stage 14 remains not PASS. Issue #39 stays open for independent acceptance.

## Prior evidence

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


## Exact-current-HEAD rerun at 9c20ce4

Executed at HEAD `9c20ce45168adfbe6baf9a4d8b4d339cb5ba9cfc` as required by Issue #34 comments 6066237182 and 6066518598. This evidence commit only records that run. It is not the executed HEAD. Stage 14 is not marked PASS. Issue #34 is left open.

Changed-file scope of this evidence commit:

- `experiments/results/stage14_visual_explorer.md`

No implementation files were changed. Seeds, budget, and policy were not changed. V0.1 scripts and historical Phase H / Phase G artifacts were not edited. No V0.2 transition semantic change.

Independent checks at the executed tree:

- `PYTHONPATH=src python -m pytest -q tests` exit code 0, 109 passed in 0.59s.
- `PYTHONPATH=src python experiments/phase_h_dynamics.py` exit code 0; locked config seeds `7,11,19`, budget `4`, policy `none`; `deterministic_replay.match` is true.
- historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.
- `src/memory_infra/explorer.py` does not import `memory_infra.store` and does not write a graph store.
- fixture `experiments/results/stage14_explorer_fixture.html` has 9 unique HTML `id` attributes and no duplicates; anchors `n-event_3a_ev-7-2` and `n-state_3a_ev-7-2` are both present, as are `n-event_3a_ev-7-5` / `n-state_3a_ev-7-5` and `n-thread_3a_th-7-3` / `n-state_3a_th-7-3`. Contradiction label and read-only status remain.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

### pytest output

```
........................................................................ [ 66%]
.....................................                                    [100%]
109 passed in 0.59s
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


## Exact-current-HEAD rerun at 5ade7a8

Executed at HEAD `5ade7a8c064c9047983e2e13388090863b5ba386` as required by Issue #35. `git rev-parse HEAD` before the commands was `5ade7a8c064c9047983e2e13388090863b5ba386`. This evidence commit only records that run. It is not the executed HEAD. Stage 14 is not marked PASS. Issue #34 and Issue #35 are left open.

Changed-file scope of this evidence commit:

- `experiments/results/stage14_visual_explorer.md`

No implementation files were changed. Seeds, budget, and policy were not changed. V0.1 scripts and historical Phase H / Phase G artifacts were not edited. No V0.2 transition semantic change.

Independent checks at the executed tree:

- `PYTHONPATH=src python -m pytest -q tests` exit code 0, 109 passed in 0.45s.
- `PYTHONPATH=src python experiments/phase_h_dynamics.py` exit code 0; locked config seeds `7,11,19`, budget `4`, policy `none`; `deterministic_replay.match` is true for seeds 7, 11, and 19.
- historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`.
- `src/memory_infra/explorer.py` imports only `html` and `typing`; it does not import `memory_infra.store` and does not write a graph store.
- fixture `experiments/results/stage14_explorer_fixture.html` has 9 unique HTML `id` attributes and no duplicates; anchors `n-event_3a_ev-7-2` and `n-state_3a_ev-7-2` are both present, as are `n-event_3a_ev-7-5` / `n-state_3a_ev-7-5` and `n-thread_3a_th-7-3` / `n-state_3a_th-7-3`. Contradiction label and read-only status remain.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

### pytest output

```
........................................................................ [ 66%]
.....................................                                    [100%]
109 passed in 0.45s
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


## Issue #36 provenance and exact-HEAD run at 2481798

Ancestry check at checkout `24817983426b93865afa81686372c2a322324fe4`:

```
git rev-parse HEAD
24817983426b93865afa81686372c2a322324fe4

git diff --name-only 5ade7a8c064c9047983e2e13388090863b5ba386..24817983426b93865afa81686372c2a322324fe4
experiments/results/stage14_visual_explorer.md
```

`24817983426b93865afa81686372c2a322324fe4` changes only `experiments/results/stage14_visual_explorer.md` relative to `5ade7a8c064c9047983e2e13388090863b5ba386` (50 insertions). No source, test, parameter, V0.1, Phase G, or V0.2 transition file changed in that commit.

Commands were then executed at `24817983426b93865afa81686372c2a322324fe4`. This section records that run. The commit that adds this section is evidence-only and was not itself executed. It must not by itself force another locked rerun. Stage 14 is not marked PASS.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

### pytest output

```
........................................................................ [ 66%]
.....................................                                    [100%]
109 passed in 0.62s
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

`deterministic_replay.match` is true for seeds 7, 11, and 19. Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`. Working tree after the commands had no tracked artifact diff. Existing Stage 14 tests still cover kind-qualified same-id anchors, unique fixture HTML ids, contradiction/evidence visibility, and the read-only public boundary. Seeds, budget, and policy were not changed.

## Issue #38 filter/search run at 91ec93f

Code-under-test SHA: `91ec93fa9b1b1c74bce690023c7e9b8f18a2f10f`.

That commit wires client-side display filters and search in `src/memory_infra/explorer.py`, adds `tests/test_stage14_explorer.py` coverage, updates the Stage 14 contract note, and regenerates `experiments/results/stage14_explorer_fixture.html`. It does not change Phase H seeds, budget, or policy. This section records the run executed at that SHA. The commit that adds this section is evidence-only and was not itself executed. Stage 14 is not marked PASS.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

### pytest output

```
........................................................................ [ 65%]
......................................                                   [100%]
110 passed in 0.39s
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

`deterministic_replay.match` is true for seeds 7, 11, and 19. Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`. Working tree after the commands had no tracked artifact diff. Seeds, budget, and policy were not changed.


## Issue #39 independent verification of 91ec93f

Ancestry at default HEAD `015cb95d964c423f4670d8f4e096be16e1fdd7d8`:

```
git diff --name-only 91ec93fa9b1b1c74bce690023c7e9b8f18a2f10f..015cb95d964c423f4670d8f4e096be16e1fdd7d8
experiments/results/stage14_visual_explorer.md
```

`015cb95d964c423f4670d8f4e096be16e1fdd7d8` is evidence-only relative to implementation SHA `91ec93fa9b1b1c74bce690023c7e9b8f18a2f10f`. Implementation parent diff:

```
git diff --name-only 5e7949c65ffc9206f92119a5a2a6a71e91366dac..91ec93fa9b1b1c74bce690023c7e9b8f18a2f10f
docs/STAGE14_VISUAL_EXPLORER.md
experiments/results/stage14_explorer_fixture.html
src/memory_infra/explorer.py
tests/test_stage14_explorer.py
```

Commands were executed after `git checkout 91ec93fa9b1b1c74bce690023c7e9b8f18a2f10f` and `git rev-parse HEAD` equaled that SHA. This section records that run. The commit that adds this section is evidence-only and was not itself executed. Stage 14 is not marked PASS.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

### pytest output

```
........................................................................ [ 65%]
......................................                                   [100%]
110 passed in 0.64s
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

`deterministic_replay.match` is true for seeds 7, 11, and 19. Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`. Seeds, budget, and policy were not changed. V0.1 and Phase G artifacts were not edited.

Static inspection at the implementation SHA: fixture HTML `id` attributes are 9 unique values with no duplicates; kind-qualified anchors `n-event_3a_ev-7-2` and `n-state_3a_ev-7-2` are both present. Explorer imports are `html` and `typing` only. No browser/DOM runtime was available, so interactive filter clicks were not browser-verified. Observation left for review: contradiction endpoint marking and contradiction unhide match on `data-id` alone, so same-id state nodes are also marked `data-contradiction-endpoint=true` and can be shown with event endpoints.
