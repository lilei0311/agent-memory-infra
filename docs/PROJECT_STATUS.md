# Project Status — Agent Memory Infra

Observation date: 2026-10-10. This is a coordination map, not a substitute for issue-level acceptance evidence.

## Immutable product goal
The core hypothesis in README is that historical task feedback should improve what an agent remembers, retrieves, retains, or forgets beyond relevance-only retrieval. Product priority remains Agent Memory Skill for a single agent. Agent Memory Hub, Memory Bridge, telemetry, and external usage learning remain deferred. Storage remains outside this project.

V0.1 A/B/C/D/E, Phase G assets/config/results, V0.2 semantics, and Phase H configuration/results are frozen.

## Stage terminology
The research roadmap stages in `docs/ROADMAP.md` are not the numbered implementation stages. Research Stage 1 is the frozen controlled-policy experiment; research Stage 2 is Skill packaging; research Stage 3 is real-world learning and has not started. Numbered Stages 12–14 are the Skill path: explicit import seam, Memory Graph projection, and read-only visual explorer.

## Current implementation and evidence
- Default-branch HEAD before the Skill API contract commit: `fc443b86feea38fa1216c16f9c34d99c6028067a` (evidence-only Stage 14 Chromium probe record). The contract commit adds `docs/SKILL_API.md`, `tests/test_skill_api_contract.py`, and this map only.
- Stage 14 implementation under review: `e6b97ffb47b3d33fa5f36d18cf01234052741e5e`.
- Exact-SHA evidence: `experiments/results/stage14_issue43_e6b97ff.md`.
- The evidence record reports `PYTHONPATH=src python3 -m pytest -q tests` → 114 passed, exit 0; locked Phase H exit 0, seeds 7/11/19, budget 4, policy none, deterministic replay true, trace SHA-256 `5ba3af8f5376cf9586a7389293b5205d204a49b7b1de986c45031dc826bfa40c`; and Chromium input/change checks for views and relation/evidence search.
- Diff from prior implementation `0d02872` to `e6b97ff` includes the Stage 14 source/test fix plus historical evidence/status documents. The recorded run says no V0.1, Phase G, or Phase H configuration/trace artifact changed.

## Stage 14 verdict
**Owner closed Issue #43 as completed and opened Issue #46.** This map does not re-execute Stage 14 checks and does not replace that closure. Prior recorded verdict was conditional until the Chromium probe script and exit code existed; those files are on `fc443b86`.

Source and evidence review supports the search fix, kind-qualified endpoint handling, same-thread thread endpoints, synchronized edge/label/inspector visibility, deterministic rendering, read-only projection boundary, and frozen Phase H result.

The named browser-evidence gap is closed by `experiments/stage14_issue43_chromium_probe.py` and `experiments/results/stage14_issue43_e6b97ff_chromium.md`. The probe ran at implementation SHA `e6b97ffb47b3d33fa5f36d18cf01234052741e5e`: Chromium exit 0, probe assert exit 0. It covers All/Threads/Events/Contradictions, relation id/type, evidence, endpoint-only, no-match, and edge/label/inspector visibility. Pytest and Phase H were not repeated.

## Canonical open work
- Issue #43 was closed completed by the owner on 2026-10-09. This map does not re-open Stage 14 and does not claim a fresh independent execution in this commit.
- Issue #46 is the active work unit: public Skill API contract in `docs/SKILL_API.md`. Contract revision `skill-api-2026-10-10.3`. Pinning tests: `tests/test_skill_api_contract.py` (ops, envelopes, missing fields, invalid signal, exact multi-key scope/ownership suffixes, read_graph ownership order, signal BoundaryError distinct from SnapshotError ownership). Issue #46 stays open pending independent review.
- Do not create a duplicate Stage 14 issue or a second API-contract issue.

## Next-stage boundary
Issue #46 is design/contract only. Do not implement adapters, packaging, Hub, Memory Bridge, telemetry, UI, server, MCP, GraphRAG, or vector DB under that issue. After the contract is independently accepted, open one implementation issue from the approved contract.
