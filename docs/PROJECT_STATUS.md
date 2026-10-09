# Project Status — Agent Memory Infra

Observation date: 2026-10-10. This is a coordination map, not a substitute for issue-level acceptance evidence.

## Immutable product goal
The core hypothesis in README is that historical task feedback should improve what an agent remembers, retrieves, retains, or forgets beyond relevance-only retrieval. Product priority remains Agent Memory Skill for a single agent. Agent Memory Hub, Memory Bridge, telemetry, and external usage learning remain deferred. Storage remains outside this project.

V0.1 A/B/C/D/E, Phase G assets/config/results, V0.2 semantics, and Phase H configuration/results are frozen.

## Stage terminology
The research roadmap stages in `docs/ROADMAP.md` are not the numbered implementation stages. Research Stage 1 is the frozen controlled-policy experiment; research Stage 2 is Skill packaging; research Stage 3 is real-world learning and has not started. Numbered Stages 12–14 are the Skill path: explicit import seam, Memory Graph projection, and read-only visual explorer.

## Current implementation and evidence
- Latest observed default-branch HEAD: `d3faa9c677d96352bbeaf5bf571ebd8e9e42fbd5` (evidence-only record).
- Stage 14 implementation under review: `e6b97ffb47b3d33fa5f36d18cf01234052741e5e`.
- Exact-SHA evidence: `experiments/results/stage14_issue43_e6b97ff.md`.
- The evidence record reports `PYTHONPATH=src python3 -m pytest -q tests` → 114 passed, exit 0; locked Phase H exit 0, seeds 7/11/19, budget 4, policy none, deterministic replay true, trace SHA-256 `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`; and Chromium input/change checks for views and relation/evidence search.
- Diff from prior implementation `0d02872` to `e6b97ff` includes the Stage 14 source/test fix plus historical evidence/status documents. The recorded run says no V0.1, Phase G, or Phase H configuration/trace artifact changed.

## Stage 14 verdict
**CONDITIONAL — not yet accepted.**

Source and evidence review supports the search fix, kind-qualified endpoint handling, same-thread thread endpoints, synchronized edge/label/inspector visibility, deterministic rendering, read-only projection boundary, and frozen Phase H result.

One acceptance evidence gap remains: `experiments/results/stage14_issue43_e6b97ff.md` describes the Chromium cases but does not provide the complete reproducible probe-generation/dispatch command or script and an explicit Chromium exit code. Until this is supplied or the exact probe is rerun and recorded, the interactive-browser criterion is not fully auditable. Do not repeat pytest or Phase H solely because documentation HEAD advanced.

## Canonical open work
- Issue #43: Stage 14 acceptance gate. Next action is only to complete the missing reproducible Chromium evidence at implementation SHA `e6b97ffb47b3d33fa5f36d18cf01234052741e5`, or explain precisely why the existing record is sufficient with the actual command/script and exit code.
- Issue #44: relation/evidence search fix; implementation landed, acceptance remains tied to #43.
- Issues #39–#42: predecessor defect/acceptance chain; close individually only when #43's evidence is accepted and each issue's own criteria are demonstrably resolved.
- Do not create a duplicate Stage 14 issue or make another generic status-only commit.

## Next-stage boundary
Do not start an undefined Stage 15 or expand into Hub/Memory Bridge/telemetry. After Stage 14 is accepted, define the next bounded Agent Memory Skill work unit from `docs/ROADMAP.md` and `docs/PRODUCT_ARCHITECTURE.md`, with an explicit objective, non-goals, and acceptance criteria before implementation begins.
