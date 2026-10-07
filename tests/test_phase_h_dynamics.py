import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))

from phase_h_dynamics import (  # noqa: E402
    BUDGET,
    POLICY,
    SEEDS,
    run_evidence_integrity,
    run_event_identity,
    run_memory_lifecycle,
    run_replay,
    run_thread_lifecycle,
)
from memory_infra.graph import Lifecycle


def test_locked_config_is_explicit() -> None:
    assert SEEDS == [7, 11, 19]
    assert BUDGET == 4
    assert POLICY == "none"


def test_repeated_events_remain_distinct() -> None:
    row = run_event_identity(7)
    assert row["distinct_events"] and row["distinct_evidence"] and row["event_count"] == 2


def test_thread_create_extend_split_merge_reopen() -> None:
    row = run_thread_lifecycle(7)
    assert row["created"] and row["extended"] and row["split"]
    assert row["reopened"] and row["members_unchanged_on_reopen"]
    assert row["not_topic_return"]
    assert row["child_topic"] == "beta"


def test_memory_lifecycle_confirm_revise_weaken_and_reactivation() -> None:
    row = run_memory_lifecycle(7)
    assert row["confirm"] and row["revise"] and row["weaken"]
    assert row["dormant_before_retrieval"] == Lifecycle.DORMANT.value
    assert row["reactivated"] == Lifecycle.REACTIVATED.value
    assert row["inaccessible"] == Lifecycle.INACCESSIBLE.value
    assert row["evidence_kept"]
    pairs = set(map(tuple, row["pairs"]))
    assert ("FORMING", "LABILE") in pairs
    assert ("LABILE", "STABLE") in pairs
    assert ("STABLE", "REACTIVATED") in pairs
    assert ("REACTIVATED", "RECONSOLIDATING") in pairs
    assert ("RECONSOLIDATING", "STABLE") in pairs
    assert ("RECONSOLIDATING", "UPDATED") in pairs
    assert ("RECONSOLIDATING", "WEAKENED") in pairs
    assert ("STABLE", "DORMANT") in pairs
    assert ("DORMANT", "REACTIVATED") in pairs
    assert ("DORMANT", "INACCESSIBLE") in pairs


def test_evidence_paths_and_relation_provenance() -> None:
    row = run_evidence_integrity(7)
    assert row["both_events_present"] and row["distinct_evidence"] and row["endpoints_unchanged"]
    assert row["contradiction"] == "evidential.contradicts"
    assert row["causal"] == "causal.caused_by"
    types = set(row["relation_types"])
    assert "temporal.before" in types
    assert "evidential.contradicts" in types
    assert "causal.caused_by" in types


def test_replay_is_deterministic_across_locked_seeds() -> None:
    for seed in SEEDS:
        row = run_replay(seed)
        assert row["match"]
        assert len(set(row["digests"])) == 4
