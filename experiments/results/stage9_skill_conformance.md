# Stage 9 Skill/API conformance evidence

Executed at implementation HEAD `90ccf394f70c06ef2191de53707ee4c2cabd8348`. This evidence commit only records that run. It is not the executed HEAD. Do not treat this evidence commit as exact-current-HEAD acceptance. Stage 9 is not marked PASS.

Changed-file scope of the implementation commit:

- `docs/STAGE9_SKILL_CONFORMANCE.md`
- `tests/skill_conformance.py`
- `tests/test_stage9_conformance.py`

This evidence commit adds only `experiments/results/stage9_skill_conformance.md`.

No public-boundary code change was required. Conformance tests import `SkillApi` from `memory_infra.skill` and the reusable adapter in `tests/skill_conformance.py`. They do not import `memory_infra.store`. Both `SkillApi.open_memory()` and `SkillApi.open_file()` are exercised. Caller notes are not restored. A caller-supplied `point_id` does not become the mechanism identifier. `assign_ids`, impersonation, other-caller scope, and unsupported operations are rejected. Trace assertions require `ok`, `op == inspect_trace`, `target_id`, `kind`, `reason`, and non-empty `evidence_refs`.

Seeds, budget, and policy were not changed. V0.1 scripts and historical Phase H / Phase G artifacts were not edited. No V0.2 transition semantic change.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

## pytest output

```
........................................................................ [100%]
72 passed in 0.45s
```

Exit code 0. Baseline before this commit was 70 passed. The two added tests are the Stage 9 conformance checks.

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
