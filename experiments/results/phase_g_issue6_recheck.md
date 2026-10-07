# Issue 6 recheck on implementation commit

Command:

```text
PYTHONPATH=src python -m pytest -q tests
```

Result: 1 failed, 21 passed.

Phase G tests in `tests/test_graph_dynamics.py` passed, including reopen and causal relation.

V0.1 regression:

- `tests/test_stage1_feedback.py` passed
- `tests/test_memory_policy.py::test_learner_nudges_alpha_only_when_policy_beats_baseline` failed
- assertion: `policy.alpha == 0.85` vs actual `0.8500000000000001`
- expectation was not changed
- failure is in V0.1 `FeedbackLearner` float addition (`0.8 + 0.05`); Phase G graph code does not set alpha
- V0.1 experiment scripts, seeds, and result files were not rerun or edited
