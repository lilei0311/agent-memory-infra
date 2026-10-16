"""Synthetic use-case eval. No personal memory is read or written."""

from __future__ import annotations

import importlib.util
import inspect
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "experiments" / "synthetic_usecase_eval.py"
RESULTS = ROOT / "experiments" / "results" / "usable_c_synthetic_eval.md"

_SPEC = importlib.util.spec_from_file_location("synthetic_usecase_eval", SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
usecase = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(usecase)

from memory_infra.entrypoint import SkillEntrypoint

FORBIDDEN = ("/Users/", "/Volumes/", "sk-")


def _row(report, task_id):
    return next(row for row in report["deduped_tasks"] if row["task_id"] == task_id)


def _skill(report, scenario, policy):
    return next(row for row in report["skill"] if row["scenario"] == scenario and row["policy"] == policy)


def test_policy_outcomes_are_mixed_and_honest():
    report = usecase.build_report()
    preference = _row(report, "preference_recall")
    decision = _row(report, "prior_decision")
    duplicate = _row(report, "duplicate_suppression")
    stale = _row(report, "stale_contradiction")

    assert preference["baseline_top"][0] == "pref-distractor"
    assert preference["adaptive_top"][0] == "pref-confirm"
    assert preference["adaptive_hit_at_1"] > preference["baseline_hit_at_1"]

    assert decision["baseline_top"][0] == "decision-direct"
    assert decision["adaptive_top"][0] == "decision-backup"
    assert decision["adaptive_hit_at_1"] > decision["baseline_hit_at_1"]

    assert duplicate["baseline_hit_at_1"] == duplicate["adaptive_hit_at_1"] == 0
    assert duplicate["baseline_hit_at_k"] == 1
    assert duplicate["adaptive_hit_at_k"] == 0
    assert report["raw_duplicate"]["baseline_hit_at_k"] == 0
    assert report["raw_duplicate"]["adaptive_hit_at_k"] == 0
    assert report["raw_duplicate"]["baseline_preference_copies"] == 2
    assert report["store_counts"] == {"raw": 8, "deduped": 7}

    assert stale["baseline_top"][0] == stale["adaptive_top"][0] == "theme-stale"
    assert stale["baseline_hit_at_1"] == stale["adaptive_hit_at_1"] == 0
    assert stale["baseline_hit_at_k"] == stale["adaptive_hit_at_k"] == 1

    assert report["hit_at_1_comparison"] == {"adaptive_higher": 2, "baseline_higher": 0, "tie": 2}
    assert report["hit_at_k_comparison"]["baseline_higher"] == 1
    assert report["hit_at_k_comparison"]["adaptive_higher"] == 0


def test_skill_dedup_decay_and_redaction_stay_off():
    report = usecase.build_report()
    plain = _skill(report, "memory-dedup-off", "none")
    automatic = _skill(report, "memory-dedup-off", "automatic")
    deduped = _skill(report, "memory-dedup-on", "none")
    deduped_auto = _skill(report, "memory-dedup-on", "automatic")
    dated = _skill(report, "dated-notes", "none")
    dated_auto = _skill(report, "dated-notes", "automatic")
    decayed = _skill(report, "dated-notes-after-decay", "none")
    decayed_auto = _skill(report, "dated-notes-after-decay", "automatic")

    assert plain["created"] == 6 and plain["skipped"] == 0
    assert plain["hits"]["unique-fact"] == 0
    assert plain["hits"]["pref-confirm"] == 1
    assert plain["selected_labels"][0] == "pref-confirm"
    assert automatic["hits"]["unique-fact"] == 0
    assert automatic["selected_labels"] == plain["selected_labels"]
    assert all(row["query_used_for_ranking"] is True for row in report["skill"])

    assert deduped["created"] == 3 and deduped["skipped"] == 3
    assert deduped["hits"]["unique-fact"] == 1
    assert deduped_auto["selected_labels"] == deduped["selected_labels"]

    assert dated["selected_labels"] == dated_auto["selected_labels"]
    assert dated["hits"]["theme-stale"] == 1
    assert dated["hits"]["theme-current"] == 1
    assert dated["hits"]["decision-backup"] == 0
    assert dated["selected_labels"][0] == "theme-current"
    assert decayed["contradiction_kept_both"] is True
    assert decayed_auto["contradiction_kept_both"] is True
    assert decayed["hits"]["theme-stale"] == 1
    assert decayed["hits"]["theme-current"] == 1
    assert decayed["hits"]["decision-backup"] == 0
    assert decayed_auto["selected_labels"] == decayed["selected_labels"]

    assert all(row["redaction_enabled"] is False for row in report["skill"])
    assert inspect.signature(SkillEntrypoint.__init__).parameters["redact"].default is False


def test_results_markdown_is_synthetic_and_matches_the_run():
    report = usecase.build_report()
    text = usecase.render_report(report)
    assert RESULTS.read_text(encoding="utf-8") == text
    for task_id in ("preference_recall", "prior_decision", "duplicate_suppression", "stale_contradiction"):
        assert task_id in text
    assert "Adaptive does not beat baseline on every task." in text
    for forbidden in FORBIDDEN:
        assert forbidden not in text
    assert "pref-confirm" in text and usecase.PREFERENCE in text


def test_script_exits_zero(tmp_path):
    target = tmp_path / "out.md"
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--output", str(target)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert target.read_text(encoding="utf-8") == RESULTS.read_text(encoding="utf-8")


def test_dated_fixture_matches_eval_labels():
    text = (usecase.FIXTURES / usecase.DATED_NOTES).read_text(encoding="utf-8")
    for line in (usecase.STALE_THEME, usecase.CURRENT_THEME, usecase.STALE_DECISION, usecase.CURRENT_DECISION):
        assert line in text


def test_local_aggregate_writes_counts_outside_the_repo(tmp_path):
    root = tmp_path / "snapshot"
    (root / "agents" / "main" / "trajectory").mkdir(parents=True)
    (root / "node_modules").mkdir()
    (root / "MEMORY.md").write_text("- The workspace prefers explicit confirmation before import.\n", encoding="utf-8")
    (root / "agents" / "main" / "trajectory" / "session.jsonl").write_text(
        '{"text":"TRAJECTORY_MARKER_DO_NOT_LEAK"}\n', encoding="utf-8"
    )
    (root / "session.jsonl").write_text('{"text":"JSONL_MARKER_DO_NOT_LEAK"}\n', encoding="utf-8")
    (root / "node_modules" / "AGENTS.md").write_text("- vendor template should not import\n", encoding="utf-8")

    output = tmp_path / "aggregates.md"
    summary = usecase.run_local_aggregate(root, output, hits="preference=1,prior-decision=0")
    body = output.read_text(encoding="utf-8")
    assert summary["created"] == 1
    assert summary["excluded_trajectory"] == 1
    assert summary["excluded_store"] == 1
    assert summary["excluded_vendor"] == 1
    assert summary["redaction_enabled"] is False
    assert summary["imported_path_count"] == 1
    assert "TRAJECTORY_MARKER_DO_NOT_LEAK" not in body
    assert "JSONL_MARKER_DO_NOT_LEAK" not in body
    assert "The workspace prefers" not in body
    assert "vendor template" not in body
    assert "hit@k preference=1 prior-decision=0" in body

    stores = usecase.run_local_aggregate(
        root, tmp_path / "stores.md", include_stores=True, queries=["preference"]
    )
    store_body = (tmp_path / "stores.md").read_text(encoding="utf-8")
    assert stores["excluded_store"] == 0
    assert stores["created"] > 1
    assert "JSONL_MARKER_DO_NOT_LEAK" not in store_body

    preview = usecase.run_local_aggregate(root, tmp_path / "preview.md", preview_only=True)
    assert preview["created"] == 0
    assert preview["preview_path_count"] == 1
    assert preview["imported_path_count"] == 0


def test_hits_round_trip_into_markdown_and_json(tmp_path):
    raw = "preference=1,prior-decision=0,stale-note=1"
    parsed = usecase.parse_hits(raw)
    assert parsed == [("preference", 1), ("prior-decision", 0), ("stale-note", 1)]
    assert usecase.parse_hits("preference=1, prior-decision=0, stale-note=1") == parsed
    assert usecase.parse_hit_line(usecase.format_hit_line(parsed)) == parsed
    for bad in ("preference=2", "stale-note=no", "preference=1,preference=0", "prior decision=1", "preference="):
        with pytest.raises(usecase.LocalEvalError):
            usecase.parse_hits(bad)

    root = tmp_path / "snapshot"
    root.mkdir()
    observation = "Synthetic preference note for the hit gate."
    (root / "MEMORY.md").write_text(f"- {observation}\n", encoding="utf-8")
    output = tmp_path / "aggregates.md"
    summary = usecase.run_local_aggregate(root, output, hits=raw)
    body = output.read_text(encoding="utf-8")
    json_path = usecase.aggregate_json_path(output)
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert summary["created"] == 1
    assert summary["hits"] == [{"task": label, "hit": value} for label, value in parsed]
    assert summary["pr_one_liner"] == "hit@k preference=1 prior-decision=0 stale-note=1"
    assert usecase.hits_from_aggregate_markdown(body) == parsed
    assert usecase.hits_from_aggregate_json(payload) == parsed
    assert payload["pr_one_liner"] == summary["pr_one_liner"]
    assert payload["pr_one_liner"] in body
    for label, value in parsed:
        assert payload["hits"][parsed.index((label, value))] == {"task": label, "hit": value}
        assert isinstance(payload["hits"][parsed.index((label, value))]["hit"], int)
        assert f"- {label}: {value}" in body
    assert observation not in body
    assert observation not in json_path.read_text(encoding="utf-8")
    assert str(root) not in body
    assert str(root) not in json_path.read_text(encoding="utf-8")

    empty = usecase.run_local_aggregate(root, tmp_path / "empty.md", preview_only=True)
    assert empty["hits"] == []
    assert empty["pr_one_liner"] == ""
    assert usecase.hits_from_aggregate_markdown((tmp_path / "empty.md").read_text(encoding="utf-8")) == []
    assert json.loads((tmp_path / "empty.json").read_text(encoding="utf-8"))["hits"] == []

    cli = tmp_path / "cli-hits.md"
    code = usecase.main(
        ["--local-root", str(root), "--output", str(cli), "--hits", raw]
    )
    assert code == 0
    cli_body = cli.read_text(encoding="utf-8")
    cli_payload = json.loads(usecase.aggregate_json_path(cli).read_text(encoding="utf-8"))
    assert usecase.hits_from_aggregate_markdown(cli_body) == parsed
    assert usecase.hits_from_aggregate_json(cli_payload) == parsed
    assert observation not in cli_body

    rejected = tmp_path / "rejected.md"
    assert usecase.main(
        ["--local-root", str(root), "--output", str(rejected), "--hits", "preference=2"]
    ) == 2
    assert not rejected.exists()
    assert not usecase.aggregate_json_path(rejected).exists()


def test_extra_markdown_names_are_tier_a_and_importable(tmp_path):
    root = tmp_path / "snapshot"
    root.mkdir()
    (root / "MEMORY.md").write_text("- Default synthetic note stays importable.\n", encoding="utf-8")
    (root / "side-notes.md").write_text("- Synthetic extra basename should import.\n", encoding="utf-8")
    (root / "agents").mkdir()
    (root / "agents" / "Custom.md").write_text("- Second synthetic extra.\n", encoding="utf-8")

    assert usecase.classify_local_path("side-notes.md", include_stores=False) == "excluded_unlisted"
    default = usecase.run_local_aggregate(root, tmp_path / "default.md")
    assert default["created"] == 1
    assert default["imported_path_count"] == 1
    assert default["excluded_unlisted"] == 0
    assert default["extra_markdown_name_count"] == 0
    assert default["recognize_dated_markdown"] is False

    sources = usecase.local_source_config({"side-notes.md", "Custom.md"})
    names = usecase._tier_names(sources)
    assert usecase.classify_local_path("agents/main/side-notes.md", include_stores=False, tier_names=names) == "tier_a"
    extra = usecase.run_local_aggregate(
        root, tmp_path / "extra.md", extra_markdown_names={"side-notes.md", "Custom.md"}
    )
    body = (tmp_path / "extra.md").read_text(encoding="utf-8")
    assert extra["created"] == 3
    assert extra["imported_path_count"] == 3
    assert extra["excluded_unlisted"] == 0
    assert extra["extra_markdown_name_count"] == 2
    assert "Synthetic extra basename" not in body
    assert "Default synthetic note" not in body

    cli_out = tmp_path / "cli.md"
    code = usecase.main(
        [
            "--local-root",
            str(root),
            "--output",
            str(cli_out),
            "--preview-only",
            "--extra-markdown-names",
            "side-notes.md,Custom.md",
            "--extra-markdown-names",
            "Absent.md",
        ]
    )
    assert code == 0
    cli_body = cli_out.read_text(encoding="utf-8")
    assert "preview_path_count: 3" in cli_body
    assert "extra_markdown_name_count: 3" in cli_body
    assert "recognize_dated_markdown: false" in cli_body
    assert usecase.main(
        ["--local-root", str(root), "--output", str(tmp_path / "bad.md"), "--extra-markdown-names", "nested/Foo.md"]
    ) == 2
    assert usecase.main(["--extra-markdown-names", "side-notes.md"]) == 2


def test_recognize_dated_markdown_when_enabled(tmp_path):
    root = tmp_path / "snapshot"
    (root / "memory").mkdir(parents=True)
    (root / "memory" / "2026-04-02.md").write_text("- Dated synthetic fact.\n", encoding="utf-8")
    (root / "memory" / "2026-13-01.md").write_text("- Invalid month stays out.\n", encoding="utf-8")
    (root / "notes-2026-04-02.md").write_text("- A date inside a longer name stays out.\n", encoding="utf-8")
    (root / "2026-04-02.txt").write_text("not markdown\n", encoding="utf-8")

    assert usecase.classify_local_path("memory/2026-04-02.md", include_stores=False) == "excluded_unlisted"
    off = usecase.run_local_aggregate(root, tmp_path / "off.md", preview_only=True)
    assert off["preview_path_count"] == 0
    assert off["excluded_unlisted"] == 0
    assert off["recognize_dated_markdown"] is False

    names = usecase._tier_names(usecase.local_source_config(recognize_dated_markdown=True))
    assert usecase.classify_local_path("memory/2026-04-02.md", include_stores=False, tier_names=names) == "tier_a"
    assert usecase.classify_local_path("2026-13-01.md", include_stores=False, tier_names=names) == "excluded_unlisted"
    assert usecase.classify_local_path("2026-4-02.md", include_stores=False, tier_names=names) == "excluded_unlisted"

    on = usecase.run_local_aggregate(root, tmp_path / "on.md", recognize_dated_markdown=True)
    body = (tmp_path / "on.md").read_text(encoding="utf-8")
    assert on["created"] == 1
    assert on["imported_path_count"] == 1
    assert on["excluded_unlisted"] == 0
    assert on["recognize_dated_markdown"] is True
    assert on["extra_markdown_name_count"] == 0
    assert "Dated synthetic fact" not in body
    assert "Invalid month" not in body

    token = usecase.run_local_aggregate(
        root, tmp_path / "token.md", extra_markdown_names={usecase.DATED_MARKDOWN_TOKEN}, preview_only=True
    )
    assert token["preview_path_count"] == 1
    assert token["recognize_dated_markdown"] is True

    cli = tmp_path / "cli-dated.md"
    assert usecase.main(
        ["--local-root", str(root), "--output", str(cli), "--recognize-dated-markdown", "--preview-only"]
    ) == 0
    assert "preview_path_count: 1" in cli.read_text(encoding="utf-8")
    assert "recognize_dated_markdown: true" in cli.read_text(encoding="utf-8")


def test_default_local_eval_without_flags_is_unchanged(tmp_path):
    assert usecase.classify_local_path("AGENTS.md", include_stores=False) == "tier_a"
    assert usecase.classify_local_path("MEMORY.md", include_stores=False) == "tier_a"
    assert usecase.classify_local_path("notes-custom.md", include_stores=False) == "excluded_unlisted"
    assert usecase.classify_local_path("2026-04-02.md", include_stores=False) == "excluded_unlisted"
    assert usecase.DATED_MARKDOWN_TOKEN not in usecase._tier_names()

    root = tmp_path / "snapshot"
    root.mkdir()
    (root / "AGENTS.md").write_text("- Persona synthetic line.\n", encoding="utf-8")
    (root / "2026-04-02.md").write_text("- Dated synthetic fact stays out.\n", encoding="utf-8")
    (root / "side-notes.md").write_text("- Extra basename stays out.\n", encoding="utf-8")
    summary = usecase.run_local_aggregate(root, tmp_path / "default.md")
    body = (tmp_path / "default.md").read_text(encoding="utf-8")
    assert summary["created"] == 1
    assert summary["imported_path_count"] == 1
    assert summary["excluded_unlisted"] == 0
    assert summary["recognize_dated_markdown"] is False
    assert summary["extra_markdown_name_count"] == 0
    assert "Dated synthetic fact" not in body
    assert "Extra basename" not in body
    assert "Persona synthetic" not in body

    target = tmp_path / "synthetic.md"
    assert usecase.main(["--output", str(target)]) == 0
    assert target.read_text(encoding="utf-8") == RESULTS.read_text(encoding="utf-8")


def test_local_output_inside_the_repo_is_refused(tmp_path):
    with pytest.raises(usecase.LocalEvalError):
        usecase.run_local_aggregate(tmp_path, ROOT / "experiments" / "results" / "local-eval" / "nope.md")
    code = usecase.main(
        ["--local-root", str(tmp_path), "--output", "experiments/results/usable_c_synthetic_eval.md"]
    )
    assert code == 2
    assert "Do not commit" in (ROOT / "docs" / "LOCAL_EVAL.md").read_text(encoding="utf-8")
    playbook = (ROOT / "docs" / "LOCAL_EVAL.md").read_text(encoding="utf-8")
    for forbidden in ("/Users/", "/Volumes/"):
        assert forbidden not in playbook
    assert ".backup" in playbook
    assert "redact=False" in playbook
    assert "trajectory" in playbook
