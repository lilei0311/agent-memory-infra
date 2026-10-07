# Development Roadmap

## Stage 1 — Validate the Memory Policy

1. Protocols
2. In-memory adapter
3. Candidate generator
4. Relevance-only baseline
5. Adaptive scoring
6. Trace recorder
7. Online update rule
8. Simulation environment
9. Evaluation runner
10. Reproducible experiments
11. Learning-curve analysis

Exit gate: controlled experiments determine whether historical feedback improves retrieval.

## Stage 2 — Package as a Skill

1. Freeze protocol
2. Define Skill API
3. Build storage adapters
4. Integrate multiple Agents
5. Standardize evaluation signals

Exit gate: at least two heterogeneous Agent/storage combinations work without changing the policy core.

## Stage 3 — Real-World Learning

1. Optional anonymous telemetry
2. User feedback loop
3. Policy versioning
4. Cross-Agent evaluation
5. Continuous improvement

External usage data begins here, not before.

## Current implementation order

- [x] Protocol design
- [x] Architecture design
- [x] Experiment design
- [x] Stage roadmap
- [x] src package skeleton
- [x] protocol types (RetrievalTrace aligned with PROTOCOLS.md; V0.2 object types live in graph.py)
- [x] in-memory adapter (MemoryStore)
- [x] baseline policy
- [x] adaptive policy
- [x] trace recorder
- [x] simulator
- [x] evaluator (metrics recorded in experiment scripts; no separate module yet)
- [x] first experiment (Issue #1 A/B/C, plus later D/E)
- [ ] learning-curve analysis beyond the recorded windows
- [ ] V0.2 graph dynamics review (Issue #5 / #6)
