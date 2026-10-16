"""Query-aware Skill retrieve. Synthetic text only."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from memory_infra.entrypoint import SkillEntrypoint
from memory_infra.graph import GraphMemory, Signals
from memory_infra.skill import SkillApi

ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location(
    "synthetic_usecase_eval", ROOT / "experiments" / "synthetic_usecase_eval.py"
)
assert _SPEC is not None and _SPEC.loader is not None
usecase = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(usecase)

PREFERENCE = "The workspace prefers explicit confirmation before import."
QUERY = "confirmation preference before import"
DISTRACTORS = (
    "Standup notes live in the team channel.",
    "Unique markdown fact: fixtures are checked in on purpose.",
    "The workspace calendar is shared on Fridays.",
)


def _import_memory(root: Path, policy: str):
    entry = SkillEntrypoint(
        seed=7,
        context_budget=3,
        policy=policy,
        backend="memory",
        redact=False,
    )
    handle = entry.open("synthetic-eval")
    handle.start(root=root)
    report = handle.import_selected(["MEMORY.md"])
    preference_id = None
    for row in report["created"]:
        event = handle.invoke("read_event", {"event_id": row["event_id"]})["result"]
        if event["observation"] == PREFERENCE:
            preference_id = row["event_id"]
    assert preference_id
    return handle, preference_id


def test_preference_query_includes_a_later_observation(tmp_path: Path):
    root = tmp_path / "synthetic"
    root.mkdir()
    lines = ["# Synthetic fixture. Not a real user memory.", ""]
    lines.extend(f"- {text}" for text in (*DISTRACTORS, PREFERENCE))
    (root / "MEMORY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    handle, preference_id = _import_memory(root, "none")
    empty = handle.invoke("retrieve", {"query": ""})["result"]
    assert empty["query_used_for_ranking"] is False
    assert preference_id not in empty["selected"]
    assert len(empty["selected"]) == 3

    blank = handle.invoke("retrieve", {"query": "   "})["result"]
    assert blank["query_used_for_ranking"] is False
    assert preference_id not in blank["selected"]

    ranked = handle.invoke("retrieve", {"query": QUERY})["result"]
    assert ranked["query_used_for_ranking"] is True
    assert preference_id in ranked["selected"]
    assert ranked["selected"][0] == preference_id

    trace = handle.invoke("inspect_trace")["result"]
    logs = [row for row in trace if row["kind"] == "retrieval.log"]
    assert "query_used_for_ranking" not in logs[-3]["signals"]
    assert "query_used_for_ranking" not in logs[-2]["signals"]
    assert "query_used_for_ranking" in logs[-1]["signals"]

    automatic, automatic_id = _import_memory(root, "automatic")
    auto = automatic.invoke("retrieve", {"query": QUERY})["result"]
    assert auto["query_used_for_ranking"] is True
    assert automatic_id in auto["selected"]
    assert auto["selected"][0] == automatic_id


def test_automatic_adds_query_relevance_to_attention_weight():
    graph = GraphMemory(seed=7, context_budget=1, policy="automatic")
    standup = graph.promote(
        graph.add_point("Standup notes live in the team channel.").point_id,
        "task-relevance",
    )
    focus = graph.open_thread(standup.event_id, "standup")
    preference = graph.promote(graph.add_point(QUERY).point_id, "task-relevance")
    graph.open_thread(preference.event_id, "preference")
    graph.observe(Signals(topic="standup", topic_continuity=True, thread_reference=focus.thread_id))

    legacy = graph.retrieve(QUERY)
    assert legacy.query_used_for_ranking is False
    assert legacy.selected_refs == [standup.event_id]

    ranked = graph.retrieve(QUERY, rank_by_query=True)
    assert ranked.query_used_for_ranking is True
    assert ranked.selected_refs == [preference.event_id]
    assert "query_used_for_ranking" in graph.log[-1].signals


def test_empty_query_on_skill_api_stays_recency():
    api = SkillApi.open_memory(seed=7, context_budget=1, policy="none")
    caller = api.open_caller("synthetic")
    first = caller.invoke("observe", {"content": DISTRACTORS[0]})
    first_id = caller.invoke(
        "signal",
        {"name": "promote", "point_id": first["point_id"], "reason": "fixture"},
    )["result"]["result"]["event_id"]
    second = caller.invoke("observe", {"content": PREFERENCE})
    second_id = caller.invoke(
        "signal",
        {"name": "promote", "point_id": second["point_id"], "reason": "fixture"},
    )["result"]["result"]["event_id"]
    empty = caller.invoke("retrieve", {"query": ""})["result"]
    assert empty["query_used_for_ranking"] is False
    assert empty["selected"] == (first_id,)
    assert second_id not in empty["selected"]


def test_local_aggregate_uses_the_query_for_ranking(tmp_path: Path):
    root = tmp_path / "snapshot"
    root.mkdir()
    (root / "MEMORY.md").write_text(f"- {PREFERENCE}\n", encoding="utf-8")
    output = tmp_path / "aggregates.md"
    summary = usecase.run_local_aggregate(root, output, queries=[QUERY])
    assert summary["selected_counts"] == [
        {"query": QUERY, "selected_count": 1, "query_used_for_ranking": True}
    ]
    body = output.read_text(encoding="utf-8")
    assert "query_used_for_ranking=true" in body
    assert PREFERENCE not in body
    assert "confirmation preference" in body
