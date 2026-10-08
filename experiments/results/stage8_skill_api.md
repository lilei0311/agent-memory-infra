# Stage 8 Skill/API packaging evidence

Executed at exact HEAD `d2cd9f628defc5ebf81a1c575ff9764433bfa605`. Seeds, budget, and policy were not changed. V0.1 scripts and historical Phase H results were not edited. Stage 8 is not marked PASS.

Changed-file scope of the implementation commit:

- `docs/STAGE8_SKILL_API.md`
- `src/memory_infra/skill.py`
- `src/memory_infra/__init__.py`
- `tests/test_stage8_skill_api.py`

This evidence commit adds only `experiments/results/stage8_skill_api.md`.

No V0.2 transition semantic change. `SkillApi` binds `caller_id` and forwards the existing request contract. It does not own ids, lifecycle, thread membership, relations, trace, attention, or durable transitions. Phase H config was not retuned.

```bash
PYTHONPATH=src python -m pytest -q tests
PYTHONPATH=src python experiments/phase_h_dynamics.py
```

## pytest output

```
......................................................................   [100%]
70 passed in 0.31s
```

Exit code 0. Baseline before this commit was 68 passed. The two added tests are the Stage 8 Skill/API black-box checks.

## experiment output

Exit code 0. Locked config unchanged: seeds `7, 11, 19`, budget `4`, policy `none`. Replay match true. Seed 7 digests unchanged:

- event_identity `3347ef522ed602969c1362508ee066ee4238f0a21d8d8eaf848c4a5db879ffe1`
- thread_lifecycle `8e5dc455d858df20ae28c26afc8a352eae19a97ad8b2dc25b7dfdf22e9c72405`
- memory_lifecycle `3e34c972193a74938c246be0b275316da08d4b15d5e2148a5d93c00fd69913e9`
- evidence_integrity `e988e7ba855a07c9c155f92a1f665c253b02c5719a5f509ebdc57f2119b112a2`

trace_artifact experiments/results/phase_h_trace.json `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`

Historical Phase H trace SHA-256 remains `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`. Working tree after the run did not modify `experiments/results/phase_h_trace.json`.
