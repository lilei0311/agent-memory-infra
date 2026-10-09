# Stage 14 read-only Visual Memory Explorer evidence

## Issue #39 exact-HEAD check at 559e1ddd

Executed at current HEAD `559e1ddd0d63bcbcfc033eef57d8368306b25750`. This evidence commit is not the executed HEAD. Stage 14 is not marked PASS. Issue #39 remains open. No next-stage issue was opened.

Ancestry before this evidence commit:

```
git rev-parse HEAD
559e1ddd0d63bcbcfc033eef57d8368306b25750

git diff --name-only 670e4d2a0457823d2206cdd57a873e383c01ccd9..559e1ddd0d63bcbcfc033eef57d8368306b25750
experiments/results/stage14_issue39_670e4d2_check.md
experiments/results/stage14_visual_explorer.md

git diff --name-only 670e4d2a0457823d2206cdd57a873e383c01ccd9^..670e4d2a0457823d2206cdd57a873e383c01ccd9
docs/STAGE14_VISUAL_EXPLORER.md
src/memory_infra/explorer.py
tests/test_stage14_explorer.py
```

`559e1ddd` is evidence-only relative to implementation SHA `670e4d2a0457823d2206cdd57a873e383c01ccd9`. It changes two evidence records, not implementation files.

Commands at `git rev-parse HEAD` = `559e1ddd0d63bcbcfc033eef57d8368306b25750`:

```bash
git rev-parse HEAD
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

### pytest

Exit code 0.

```
........................................................................ [ 63%]
.........................................                                [100%]
113 passed in 0.64s
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

### Chromium input/change dispatch

Existing `/usr/bin/chromium` headless `--no-sandbox --disable-gpu --dump-dom` loaded generated explorer HTML and dispatched `change` on view radios and `input` on the search field. No new dependency. Fixture nodes: threads `th-1`/`th-2`, same-id event `th-1`, events `e1`/`e2`, same-id state and point `e1`, edges `referential.same_thread` (`rel-merge`, evidence `same-goal`) and `evidential.contradicts` (`rel-con`, evidence `both-seen`).

Observed after event dispatch:

- All: nodes `thread:th-1`, `thread:th-2`, `event:th-1`, `event:e1`, `event:e2`, `state:e1`, `point:e1` visible; edges, labels, and inspectors `rel-merge` and `rel-con` visible.
- Threads: nodes `thread:th-1`, `thread:th-2` visible; same-id event `th-1` hidden; edge, label, and inspector `rel-merge` visible together; `rel-con` hidden.
- Events: event nodes visible, including same-id event `th-1`; state/point/thread nodes hidden; edge, label, and inspector `rel-con` visible together; `rel-merge` hidden.
- Contradictions: event endpoints `e1`/`e2` visible; same-id state and point `e1` hidden; edge, label, and inspector `rel-con` visible together; `rel-merge` hidden.
- Contradiction search `both-seen`, `e1`, and `left claim`: both contradiction endpoints, edge, label, and inspector `rel-con` stayed visible; same-id state/point stayed hidden.
- All search `same-goal`: endpoints, edge, label, and inspector all hidden. No orphan inspector.
- All search `thread alpha`: only node `thread:th-1` visible; edge, label, and inspector empty.
- Clear search restored both edges and inspectors. Return to Threads restored `rel-merge` edge, label, and inspector together. No stale hidden state.

No new concrete defect recorded in this run. Stage 14 remains not PASS. Issue #39 remains open.

## Prior evidence

# Stage 14 read-only Visual Memory Explorer evidence

## Issue #42 relation inspector visibility fix at 670e4d2

Executed at implementation SHA `670e4d2a0457823d2206cdd57a873e383c01ccd9`. Repository HEAD before the implementation commit was `bc4e3ff10bfbf6d6d8e0f298a9d396e648afcd50`. This evidence commit only records the run. It is not the executed HEAD. Stage 14 is not marked PASS. Issue #39 and Issue #42 are left open. No next-stage issue was opened.

Implementation commit changed:

```
docs/STAGE14_VISUAL_EXPLORER.md
src/memory_infra/explorer.py
tests/test_stage14_explorer.py
```

Visibility contract: a relation inspector article is visible if and only if its relation edge is visible. Edge labels use that same edge visibility. `apply()` recomputes from the current view and search controls, so transitions do not keep stale visibility. Stage 13 identity, V0.2 transitions, Phase H seeds/budget/policy, and V0.1 artifacts were not changed.

Commands at `git rev-parse HEAD` = `670e4d2a0457823d2206cdd57a873e383c01ccd9`:

```bash
git rev-parse HEAD
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

### pytest

Exit code 0.

```
........................................................................ [ 63%]
.........................................                                [100%]
113 passed in 0.65s
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

### Chromium input/change dispatch

Existing `/usr/bin/chromium` headless `--no-sandbox --dump-dom` loaded generated explorer HTML and dispatched `change` on view radios and `input` on the search field. No new dependency. Fixture nodes: threads `th-1`/`th-2`, same-id event `th-1`, events `e1`/`e2`, same-id state and point `e1`, edges `referential.same_thread` (`rel-merge`, evidence `same-goal`) and `evidential.contradicts` (`rel-con`, evidence `both-seen`).

Observed after event dispatch:

- All: nodes `event:e1,event:e2,event:th-1,point:e1,state:e1,thread:th-1,thread:th-2`; edges and labels `rel-con,rel-merge`; relation inspectors `rel-con,rel-merge`.
- Threads: nodes `thread:th-1,thread:th-2`; edge and label `rel-merge`; relation inspector `rel-merge`. Same-id event `th-1` hidden. Inspector tracks the visible edge.
- Events: nodes `event:e1,event:e2,event:th-1`; edge and label `rel-con`; relation inspector `rel-con`. Inspector tracks the visible edge.
- Contradictions: nodes `event:e1,event:e2`; edge, label, and inspector `rel-con`; `rel-merge` hidden. Same-id state and point `e1` hidden.
- Contradiction search `both-seen` and `e1`: both contradiction endpoints, edge, label, and inspector `rel-con` stayed visible; same-id state/point stayed hidden.
- All search `thread alpha`: only node `thread:th-1`; edge, label, and relation inspector empty.
- All search `same-goal`: nodes, edges, labels, and relation inspectors empty. No orphan `rel-merge` inspector.
- Return to Threads with empty search: nodes `thread:th-1,thread:th-2`; edge, label, and inspector `rel-merge` restored. No stale hidden state.

Stage 14 remains not PASS. Issue #39 remains open.

## Prior evidence

# Stage 14 read-only Visual Memory Explorer evidence

## Issue #39 click-dispatch check of implementation d669e86

Executed at implementation SHA `d669e86e27f75390c12ed5226772992626efee60`. Repository HEAD before this evidence commit was `34a72925cbdaea277d7a7103fc9ac2d0a33ef356`. This evidence commit only records the independent run. It is not the executed HEAD. Stage 14 is not marked PASS. Issue #39 is left open. No next-stage issue was opened.

Ancestry at the evidence HEAD before this commit:

```
git diff --name-only d669e86e27f75390c12ed5226772992626efee60..34a72925cbdaea277d7a7103fc9ac2d0a33ef356
experiments/results/stage14_visual_explorer.md

git diff --name-only d669e86e27f75390c12ed5226772992626efee60^..d669e86e27f75390c12ed5226772992626efee60
docs/STAGE14_VISUAL_EXPLORER.md
src/memory_infra/explorer.py
tests/test_stage14_explorer.py
```

`34a72925cbdaea277d7a7103fc9ac2d0a33ef356` is evidence-only relative to implementation SHA `d669e86e27f75390c12ed5226772992626efee60`.

Commands after `git checkout d669e86e27f75390c12ed5226772992626efee60` and `git rev-parse HEAD` equaled that SHA:

```bash
git rev-parse HEAD
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

`git rev-parse HEAD` printed `d669e86e27f75390c12ed5226772992626efee60`.

### pytest

Exit code 0.

```
........................................................................ [ 64%]
........................................                                 [100%]
112 passed in 0.59s
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

Working tree after the commands had no tracked artifact diff. Seeds, budget, and policy were not changed. V0.1 and Phase G artifacts were not edited. `src/memory_infra/explorer.py` does not import `memory_infra.store`.

### Chromium input/change dispatch

Existing `/usr/bin/chromium` headless loaded generated explorer HTML and dispatched `change` on view radios and `input` on the search field. No new dependency. This was not a dump-dom-only probe. Fixture nodes: threads `th-1`/`th-2`, same-id event `th-1`, events `e1`/`e2`, same-id state and point `e1`, edges `referential.same_thread` (`rel-merge`, evidence `same-goal`) and `evidential.contradicts` (`rel-con`, evidence `both-seen`).

Observed after event dispatch:

- All: every node, both edges, both labels, and both inspector articles visible. `rel-merge` source/target kinds were thread/thread.
- Threads: only thread nodes visible. `rel-merge` edge and label visible. Same-id event `th-1` hidden. Inspector article `rel-merge` hidden while its edge stayed visible.
- Events: event nodes visible, including same-id event `th-1`; state/point/thread nodes hidden. `rel-con` edge and label visible. Inspector article `rel-con` hidden while its edge stayed visible.
- Contradictions: event endpoints `e1`/`e2` visible; same-id state and point `e1` hidden; `rel-con` edge, label, and inspector visible; `rel-merge` hidden.
- Contradiction search `both-seen` and `e1`: both contradiction endpoints, the contradiction edge, label, and inspector stayed visible; same-id state/point stayed hidden.
- All search `thread alpha`: only thread `th-1` visible; its `rel-merge` edge hidden because `th-2` did not match.
- All search `same-goal`: both endpoints and the `rel-merge` edge/label hidden, while inspector article `rel-merge` stayed visible.

Concrete display defect: relation inspector visibility does not track edge visibility. Thread/event views hide the matching relation inspector while the edge remains visible. All-view evidence search can show the relation inspector while hiding both endpoints and the edge. Not fixed in this run. Stage 14 remains not PASS.

## Prior evidence

# Stage 14 read-only Visual Memory Explorer evidence

## Issue #39 independent check of implementation d669e86

Executed at implementation SHA `d669e86e27f75390c12ed5226772992626efee60`. Repository HEAD before this evidence commit was `0437fa22df91b9d78d6b17724ee52fb121a9ecd5`. This evidence commit only records the independent run. It is not the executed HEAD. Stage 14 is not marked PASS. Issue #39 is left open. No next-stage issue was opened.

Ancestry:

```
git rev-parse HEAD
0437fa22df91b9d78d6b17724ee52fb121a9ecd5

git diff --name-only d669e86e27f75390c12ed5226772992626efee60..0437fa22df91b9d78d6b17724ee52fb121a9ecd5
experiments/results/stage14_visual_explorer.md

git diff --name-only d669e86e27f75390c12ed5226772992626efee60^..d669e86e27f75390c12ed5226772992626efee60
docs/STAGE14_VISUAL_EXPLORER.md
src/memory_infra/explorer.py
tests/test_stage14_explorer.py

git diff --name-only 199d34103c48b3b52b05efb9ea5a587ce3852728..d669e86e27f75390c12ed5226772992626efee60
docs/STAGE14_VISUAL_EXPLORER.md
src/memory_infra/explorer.py
tests/test_stage14_explorer.py
```

`0437fa22df91b9d78d6b17724ee52fb121a9ecd5` is evidence-only relative to implementation SHA `d669e86e27f75390c12ed5226772992626efee60`.

Commands after `git checkout d669e86e27f75390c12ed5226772992626efee60` and `git rev-parse HEAD` equaled that SHA:

```bash
git rev-parse HEAD
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

`git rev-parse HEAD` printed `d669e86e27f75390c12ed5226772992626efee60`.

### pytest

Exit code 0.

```
........................................................................ [ 64%]
........................................                                 [100%]
112 passed in 0.48s
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

Working tree after the commands had no tracked artifact diff. Seeds, budget, and policy were not changed. V0.1 and Phase G artifacts were not edited. Implementation diff vs `199d341` is limited to the explorer, its tests, and Stage 14 docs.

Static checks at the implementation SHA: `src/memory_infra/explorer.py` imports only `html` and `typing`; it does not import `memory_infra.store`. Fallback `referential.same_thread` is `("thread", "thread")`, matching `GraphMemory.merge`. Fixture `experiments/results/stage14_explorer_fixture.html` has 9 unique HTML ids; anchors `n-event_3a_ev-7-2` and `n-state_3a_ev-7-2` are both present. Filter script is present in rendered HTML.

Chromium headless (`/usr/bin/chromium`, already installed; no new dependency) `--dump-dom` loaded generated explorer HTML with two thread nodes `th-1`/`th-2`, same-id event nodes, and one `referential.same_thread` edge `rel-merge`. Dumped line:

```
<line class="edge" x1="480" y1="70" x2="480" y2="160" data-relation-id="rel-merge" data-relation-type="referential.same_thread" data-source-id="th-1" data-target-id="th-2" data-source-kind="thread" data-target-kind="thread" data-contradiction="false"></line>
```

Inspector article `inspect-n-edge_3a_rel-merge` had `data-source-kind="thread"` and `data-target-kind="thread"`. Anchors `n-thread_3a_th-1` and `n-event_3a_th-1` were both present. This was a headless DOM dump, not a click-dispatch session.

No concrete defect was found in this run. This execution record does not mark Stage 14 PASS.

## Prior evidence

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


## Independent check at implementation SHA 85b188d — 2026-10-09

Verdict: **CONDITIONAL / not PASS**. Issue #39 remains open. No next-stage issue opened.

Executed tree: `85b188d02d8ba6a0c7cc30a0a3a28fbaf539563a` after `git checkout --detach` and `git rev-parse HEAD`. This evidence commit is not that tree.

Ancestry:

```
git diff --name-only 85b188d02d8ba6a0c7cc30a0a3a28fbaf539563a..7139b5850cadf6d14f2b315519be5907dacaca39
experiments/results/stage14_visual_explorer.md

git diff --name-only 85b188d02d8ba6a0c7cc30a0a3a28fbaf539563a..b7199eb94f295d054b98ea3325455ff9342d0d94
experiments/results/stage14_visual_explorer.md

git diff --name-only 85b188d02d8ba6a0c7cc30a0a3a28fbaf539563a^..85b188d02d8ba6a0c7cc30a0a3a28fbaf539563a
docs/STAGE14_VISUAL_EXPLORER.md
src/memory_infra/explorer.py
tests/test_stage14_explorer.py
```

`7139b585` and `b7199eb` are evidence-only relative to implementation SHA `85b188d`.

### pytest

```
PYTHONPATH=src python -m pytest -q tests
```

```
........................................................................ [ 64%]
.......................................                                  [100%]
111 passed in 0.60s
```

Exit code 0.

### locked Phase H

```
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

Exit code 0. First line:

```
locked {'seeds': [7, 11, 19], 'budget': 4, 'policy': 'none', 'conditions': ('event_identity', 'thread_lifecycle', 'memory_lifecycle', 'evidence_integrity', 'deterministic_replay')}
```

Last line:

```
trace_artifact /tmp/agent-memory-infra/experiments/results/phase_h_trace.json 5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c
```

`deterministic_replay.match` is true. Historical trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`. Seeds, budget, and policy were not changed. Working tree did not modify `experiments/results/phase_h_trace.json`. V0.1 and Phase G artifacts were not edited. Explorer does not import `memory_infra.store`. Fixture HTML has 9 unique `id` attributes. Kind-qualified anchors remain.

### Browser probe

Existing Chromium plus the session browser loaded a generated explorer page (not a new dependency). Contradiction view kept event endpoints `e1`/`e2` and contradiction edge `rel-c` visible, and hid same-id state `e1` and point `e2`. Search `both-observed` and `e1` kept both event endpoints and the contradiction edge visible.

### Concrete defect, not fixed in this run

`GraphMemory.merge` creates `referential.same_thread` between thread ids (`graph.py` `_rel(left_id, right_id, "referential.same_thread", signal)`). Explorer `_ENDPOINT_KIND` maps that type to `("event", "event")` when `source_kind`/`target_kind` are absent. A projection with thread endpoints `th-1`/`th-2` and a same-id event `th-1` rendered the inspector article as `data-source-kind="event"` `data-target-kind="event"`, and the SVG contained no `line` for that relation (`mergeLine` absent). Stage 14 is not marked PASS. Repair is a separate issue. No Stage 13 identity or V0.2 transition change was made.

## Issue #41 same_thread endpoint mapping

Implementation SHA under test: `d669e86e27f75390c12ed5226772992626efee60`.

Parent HEAD before the implementation commit was `199d34103c48b3b52b05efb9ea5a587ce3852728` (evidence-only relative to `85b188d02d8ba6a0c7cc30a0a3a28fbaf539563a`). This section is an evidence record. The evidence commit that adds it is not the executed HEAD. Stage 14 is not marked PASS. Issue #39 remains open.

Changed files in the implementation commit:

```
docs/STAGE14_VISUAL_EXPLORER.md
src/memory_infra/explorer.py
tests/test_stage14_explorer.py
```

`referential.same_thread` fallback endpoint kinds are now `("thread", "thread")`, matching `GraphMemory.merge` (`_rel(left_id, right_id, "referential.same_thread", signal)`). Stage 13 identity and relation creation were not changed. V0.1 and Phase G artifacts were not edited. Phase H seeds, budget, and policy were not changed.

Commands at `git rev-parse HEAD` = `d669e86e27f75390c12ed5226772992626efee60`:

```bash
git rev-parse HEAD
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

### pytest

Exit code 0.

```
........................................................................ [ 64%]
........................................                                 [100%]
112 passed in 0.27s
```

### locked Phase H

Exit code 0. First line:

```
locked {'seeds': [7, 11, 19], 'budget': 4, 'policy': 'none', 'conditions': ('event_identity', 'thread_lifecycle', 'memory_lifecycle', 'evidence_integrity', 'deterministic_replay')}
```

Last line:

```
trace_artifact /tmp/agent-memory-infra/experiments/results/phase_h_trace.json 5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c
```

`deterministic_replay.match` is true. Historical trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`. Working tree did not modify `experiments/results/phase_h_trace.json`.

### Browser probe

Existing `/usr/bin/chromium` headless `--no-sandbox --dump-dom` loaded a generated explorer page (no new dependency). Fixture: two thread nodes `th-1`/`th-2`, same-id event nodes `th-1`/`th-2`, one `referential.same_thread` edge `rel-merge`. Dumped line:

```
class="edge" x1="480" y1="70" x2="480" y2="160" data-relation-id="rel-merge" data-relation-type="referential.same_thread" data-source-id="th-1" data-target-id="th-2" data-source-kind="thread" data-target-kind="thread" data-contradiction="false"
```

Inspector article `inspect-n-edge_3a_rel-merge` had `data-source-kind="thread"` and `data-target-kind="thread"`. Thread and event anchors `n-thread_3a_th-1` and `n-event_3a_th-1` were both present. Same-id events did not take the edge.


## Issue #43 rerun at 670e4d2

Evidence-only record: `experiments/results/stage14_issue43_rerun_670e4d2.md`. Code-under-test `670e4d2a0457823d2206cdd57a873e383c01ccd9`. Pytest 113 passed, exit 0. Locked Phase H exit 0, seeds 7,11,19, budget 4, policy none, deterministic replay true, trace SHA-256 `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`. Chromium input/change probe recorded. This section was not the executed HEAD. Stage 14 is not marked PASS.
