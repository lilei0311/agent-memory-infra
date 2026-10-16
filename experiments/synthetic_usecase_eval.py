"""Synthetic use-case eval: hit@k for baseline vs adaptive, plus Skill retrieve.

Tasks use invented fixture text only. The script does not read a home
directory. Adaptive hit@k is reported beside the baseline and is not a
pass criterion.

Two retrieval paths:

* Policy layer (``memory_infra.retrieval.retrieve``): baseline score is
  cosine similarity; adaptive score is similarity + alpha * utility.
* Skill API (``SkillEntrypoint`` → ``invoke("retrieve")``): ``policy="none"``
  ranks by recency. Any other policy ranks by attention weight plus a small
  recency and contextual-fit term. The query string is stored on the
  retrieval event and is not a similarity feature.

Local aggregates (``--local-root``) write counts only, and only outside
this repository. ``--hits`` records hand-scored 0/1 values (``preference``,
``prior-decision``, ``stale-note``) in the markdown aggregate and a sibling
JSON file. See ``docs/LOCAL_EVAL.md``. ``--extra-markdown-names`` adds
exact basenames. ``--recognize-dated-markdown`` also recognizes
``YYYY-MM-DD.md``. Both stay off unless passed, and both feed discovery and
tier classification for that run, including a hit@k run over those notes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from memory_infra.dedup import ItemDedupPolicy  # noqa: E402
from memory_infra.entrypoint import SkillEntrypoint  # noqa: E402
from memory_infra.memory import MemoryItem, MemoryStore  # noqa: E402
from memory_infra.policy import LearnedPolicy  # noqa: E402
from memory_infra.retrieval import retrieve  # noqa: E402
from memory_infra.source_adapter import (  # noqa: E402
    DATED_MARKDOWN_TOKEN,
    SourceConfig,
    matches_recognized_name,
)

FIXTURES = ROOT / "tests" / "fixtures" / "synthetic"
DEFAULT_RESULTS = ROOT / "experiments" / "results" / "usable_c_synthetic_eval.md"
DATED_NOTES = "dated-notes.md"

K = 3
ALPHA = 0.5
SKILL_BUDGET = 3
SKILL_SEED = 7

PREFERENCE = "The workspace prefers explicit confirmation before import."
PREFERENCE_NEAR = "the workspace prefers explicit confirmation before import."
PREFERENCE_NEAR_WS = "The  workspace prefers explicit confirmation before import."
STANDUP = "Standup notes live in the team channel."
UNIQUE = "Unique markdown fact: fixtures are checked in on purpose."
DISTRACTOR = "The workspace prefers posting standup notes in the team channel."
STALE_THEME = "2026-01-02: The workspace prefers a dark editor theme."
CURRENT_THEME = (
    "2026-06-18: The workspace prefers a light editor theme. "
    "The January dark-theme note is stale."
)
STALE_DECISION = "2026-01-04: Decision: open the live database file directly when importing messages."
CURRENT_DECISION = (
    "2026-03-18: Decision: copy a quiescent snapshot with sqlite3 .backup "
    "before a read-only import."
)

LABELS = {
    PREFERENCE: "pref-confirm",
    PREFERENCE_NEAR: "pref-near",
    PREFERENCE_NEAR_WS: "pref-near-ws",
    STANDUP: "standup",
    UNIQUE: "unique-fact",
    DISTRACTOR: "pref-distractor",
    STALE_THEME: "theme-stale",
    CURRENT_THEME: "theme-current",
    STALE_DECISION: "decision-direct",
    CURRENT_DECISION: "decision-backup",
}

PREFERENCE_QUERY = [1.0, 0.0, 0.0, 0.0]
DECISION_QUERY = [0.0, 1.0, 0.0, 0.0]
THEME_QUERY = [0.0, 0.0, 1.0, 0.0]

# One near-copy of the confirmation preference. It exists so the raw store
# can crowd a top-k window; ``add_deduped`` collapses it into pref-confirm.
_ITEMS = (
    MemoryItem("pref-confirm", PREFERENCE, [0.92, 0.04, 0.03, 0.02], success=8, failure=0),
    MemoryItem("pref-distractor", DISTRACTOR, [0.99, 0.01, 0.01, 0.01], success=0, failure=6),
    MemoryItem("decision-backup", CURRENT_DECISION, [0.04, 0.78, 0.04, 0.08], success=5, failure=0),
    MemoryItem("decision-direct", STALE_DECISION, [0.03, 0.98, 0.03, 0.02], success=0, failure=4),
    MemoryItem("theme-stale", STALE_THEME, [0.02, 0.02, 0.99, 0.02], success=0, failure=0),
    MemoryItem("theme-current", CURRENT_THEME, [0.02, 0.02, 0.70, 0.18], success=0, failure=0),
    MemoryItem("unique-fact", UNIQUE, [0.02, 0.02, 0.02, 0.25], success=1, failure=0),
)
_DUP = MemoryItem(
    "pref-confirm-dup",
    PREFERENCE_NEAR,
    [0.90, 0.05, 0.04, 0.03],
    success=2,
    failure=0,
)
_PREFERENCE_IDS = frozenset({"pref-confirm", "pref-confirm-dup"})

_TASKS = (
    {
        "task_id": "preference_recall",
        "query": "confirmation preference before import",
        "embedding": PREFERENCE_QUERY,
        "expected_ids": ("pref-confirm",),
    },
    {
        "task_id": "prior_decision",
        "query": "how to copy a database before a read-only import",
        "embedding": DECISION_QUERY,
        "expected_ids": ("decision-backup",),
    },
    {
        "task_id": "duplicate_suppression",
        "query": "confirmation preference before import",
        "embedding": PREFERENCE_QUERY,
        "expected_ids": ("unique-fact",),
    },
    {
        "task_id": "stale_contradiction",
        "query": "which editor theme is current",
        "embedding": THEME_QUERY,
        "expected_ids": ("theme-current",),
    },
)

_TRAJECTORY_MARKERS = ("trajectory", "archive-tier")
_DEFAULT_LOCAL_QUERIES = ("preference", "prior-decision", "stale-note")
_PR_LINE_PREFIX = "PR-eligible one-liner (numbers only): "


class LocalEvalError(ValueError):
    """Local aggregate output must stay outside the git repository."""


def _store(dedup: bool) -> MemoryStore:
    store = MemoryStore()
    policy = ItemDedupPolicy("skip", near=True)
    for item in (*_ITEMS, _DUP):
        if dedup:
            store.add_deduped(item, policy)
        else:
            store.add(item)
    return store


def _rank(store: MemoryStore, embedding: list[float], policy: LearnedPolicy | None) -> list[str]:
    traces = retrieve(store, embedding, policy, k=K, task_id="synthetic")
    return [trace.memory_id for trace in traces]


def _hit(ids: list[str], expected: tuple[str, ...], k: int) -> int:
    top = ids[:k]
    return int(any(item_id in top for item_id in expected))


def _preference_copies(ids: list[str]) -> int:
    return sum(1 for item_id in ids if item_id in _PREFERENCE_IDS)


def _score_store(store: MemoryStore, policy: LearnedPolicy) -> list[dict]:
    rows = []
    for task in _TASKS:
        baseline_ids = _rank(store, task["embedding"], None)
        adaptive_ids = _rank(store, task["embedding"], policy)
        expected = task["expected_ids"]
        rows.append(
            {
                "task_id": task["task_id"],
                "query": task["query"],
                "expected_ids": list(expected),
                "baseline_top": baseline_ids,
                "adaptive_top": adaptive_ids,
                "baseline_hit_at_1": _hit(baseline_ids, expected, 1),
                "adaptive_hit_at_1": _hit(adaptive_ids, expected, 1),
                "baseline_hit_at_k": _hit(baseline_ids, expected, K),
                "adaptive_hit_at_k": _hit(adaptive_ids, expected, K),
                "baseline_preference_copies": _preference_copies(baseline_ids),
                "adaptive_preference_copies": _preference_copies(adaptive_ids),
            }
        )
    return rows


def _label(text: str) -> str:
    try:
        return LABELS[text]
    except KeyError as exc:
        raise RuntimeError("synthetic observation is not a known label") from exc


def _selected_labels(handle, query: str) -> list[str]:
    result = handle.invoke("retrieve", {"query": query})["result"]
    labels = []
    for event_id in result["selected"]:
        event = handle.invoke("read_event", {"event_id": event_id})["result"]
        labels.append(_label(event["observation"]))
    return labels


def _event_id(handle, report: dict, text: str) -> str:
    for row in report["created"]:
        event = handle.invoke("read_event", {"event_id": row["event_id"]})["result"]
        if event["observation"] == text:
            return row["event_id"]
    raise RuntimeError("synthetic text was not imported")


def _open_skill(root: Path, paths: list[str], *, policy: str, dedup: ItemDedupPolicy | None, sources: SourceConfig):
    entry = SkillEntrypoint(
        seed=SKILL_SEED,
        context_budget=SKILL_BUDGET,
        policy=policy,
        backend="memory",
        redact=False,
        sources=sources,
        item_dedup=dedup,
    )
    handle = entry.open("synthetic-eval")
    handle.start(root=root)
    report = handle.import_selected(paths)
    return handle, report


def _skill_row(
    scenario: str,
    policy: str,
    *,
    dedup: ItemDedupPolicy | None,
    sources: SourceConfig,
    paths: list[str],
    query: str,
    decay_stale: bool,
) -> dict:
    handle, report = _open_skill(FIXTURES, paths, policy=policy, dedup=dedup, sources=sources)
    contradiction_kept_both = None
    if decay_stale:
        stale_id = _event_id(handle, report, STALE_THEME)
        current_id = _event_id(handle, report, CURRENT_THEME)
        handle.invoke(
            "signal",
            {
                "name": "contradict",
                "left_event": stale_id,
                "right_event": current_id,
                "evidence": "synthetic dated theme bullets disagree",
            },
        )
        stale_text = handle.invoke("read_event", {"event_id": stale_id})["result"]["observation"]
        current_text = handle.invoke("read_event", {"event_id": current_id})["result"]["observation"]
        contradiction_kept_both = stale_text == STALE_THEME and current_text == CURRENT_THEME
        handle.invoke("signal", {"name": "decay", "target_id": stale_id})
    labels = _selected_labels(handle, query)
    hit_keys = {
        "pref-confirm": PREFERENCE,
        "unique-fact": UNIQUE,
        "theme-stale": STALE_THEME,
        "theme-current": CURRENT_THEME,
        "decision-direct": STALE_DECISION,
        "decision-backup": CURRENT_DECISION,
    }
    return {
        "scenario": scenario,
        "policy": policy,
        "budget": SKILL_BUDGET,
        "dedup": dedup is not None,
        "created": len(report["created"]),
        "skipped": len(report["skipped"]),
        "redaction_enabled": report["redaction"]["enabled"],
        "selected_labels": labels,
        "hits": {name: int(LABELS[text] in labels) for name, text in hit_keys.items()},
        "contradiction_kept_both": contradiction_kept_both,
        "query_used_for_ranking": False,
    }


def _skill_scenarios() -> list[dict]:
    plain = SourceConfig()
    dated = SourceConfig.extended(frozenset({DATED_NOTES}))
    skip = ItemDedupPolicy("skip", near=True)
    specs = (
        ("memory-dedup-off", "none", None, plain, ["MEMORY.md"], "confirmation preference before import", False),
        ("memory-dedup-off", "automatic", None, plain, ["MEMORY.md"], "confirmation preference before import", False),
        ("memory-dedup-on", "none", skip, plain, ["MEMORY.md"], "confirmation preference before import", False),
        ("memory-dedup-on", "automatic", skip, plain, ["MEMORY.md"], "confirmation preference before import", False),
        ("dated-notes", "none", None, dated, [DATED_NOTES], "which editor theme is current", False),
        ("dated-notes", "automatic", None, dated, [DATED_NOTES], "which editor theme is current", False),
        ("dated-notes-after-decay", "none", None, dated, [DATED_NOTES], "which editor theme is current", True),
        ("dated-notes-after-decay", "automatic", None, dated, [DATED_NOTES], "which editor theme is current", True),
    )
    return [_skill_row(scenario, policy, dedup=dedup, sources=sources, paths=paths, query=query, decay_stale=decay) for scenario, policy, dedup, sources, paths, query, decay in specs]


def _mean(rows: list[dict], key: str) -> float:
    return sum(row[key] for row in rows) / len(rows)


def _compare(baseline: int, adaptive: int) -> str:
    if adaptive > baseline:
        return "adaptive higher"
    if adaptive < baseline:
        return "baseline higher"
    return "tie"


def build_report() -> dict:
    """Score the synthetic corpus. Does not write a file."""

    policy = LearnedPolicy(alpha=ALPHA)
    deduped = _score_store(_store(True), policy)
    raw = _score_store(_store(False), policy)
    raw_by_id = {row["task_id"]: row for row in raw}
    skill = _skill_scenarios()
    hit1 = [_compare(row["baseline_hit_at_1"], row["adaptive_hit_at_1"]) for row in deduped]
    hitk = [_compare(row["baseline_hit_at_k"], row["adaptive_hit_at_k"]) for row in deduped]
    return {
        "k": K,
        "alpha": ALPHA,
        "redact_default": False,
        "corpus": [
            {
                "id": item.id,
                "text": item.text,
                "success": item.success,
                "failure": item.failure,
                "utility": round(item.utility, 3),
            }
            for item in (*_ITEMS, _DUP)
        ],
        "deduped_tasks": deduped,
        "raw_duplicate": raw_by_id["duplicate_suppression"],
        "store_counts": {"raw": len(_store(False).items), "deduped": len(_store(True).items)},
        "skill": skill,
        "hit_at_1_comparison": {
            "adaptive_higher": hit1.count("adaptive higher"),
            "baseline_higher": hit1.count("baseline higher"),
            "tie": hit1.count("tie"),
        },
        "hit_at_k_comparison": {
            "adaptive_higher": hitk.count("adaptive higher"),
            "baseline_higher": hitk.count("baseline higher"),
            "tie": hitk.count("tie"),
        },
        "means": {
            "baseline_hit_at_1": _mean(deduped, "baseline_hit_at_1"),
            "adaptive_hit_at_1": _mean(deduped, "adaptive_hit_at_1"),
            "baseline_hit_at_k": _mean(deduped, "baseline_hit_at_k"),
            "adaptive_hit_at_k": _mean(deduped, "adaptive_hit_at_k"),
        },
    }


def _fmt_ids(ids: list[str]) -> str:
    return ", ".join(ids)


def _fmt_hits(hits: dict) -> str:
    return ", ".join(f"{name}={value}" for name, value in hits.items())


def render_report(report: dict) -> str:
    """Markdown with synthetic labels only."""

    counts = report["store_counts"]
    comparison = report["hit_at_1_comparison"]
    means = report["means"]
    lines = [
        "# Synthetic use-case eval",
        "",
        "Labels in this file are invented fixture text. This run did not read a home directory, a personal database, or a private export.",
        "",
        "Command: `python3 experiments/synthetic_usecase_eval.py`",
        "",
        "Pass condition: the script finishes and writes this file. Adaptive hit@k is not required to exceed baseline.",
        "",
        f"Policy layer: baseline = cosine, adaptive = cosine + {report['alpha']} * utility, k={report['k']}. Alpha is fixed; the online learner is not updated. The scored store is the near-deduped corpus (`skip`, normalized text) unless a row says raw.",
        "",
        "Skill API: every import in this run used `redact=False`. `SkillEntrypoint` still defaults to `redact=False`; this eval does not change that. "
        f"`context_budget={SKILL_BUDGET}`. `policy=\"none\"` is recency order. `policy=\"automatic\"` adds attention weight. "
        "With no threads every attention weight is 0, so tied scores break on event-id text order. That tie break is not a query match. "
        "The query string is not a similarity feature (`query_used_for_ranking` is false).",
        "",
        "## Corpus",
        "",
        "| id | utility | text |",
        "| --- | --- | --- |",
    ]
    for item in report["corpus"]:
        lines.append(f"| {item['id']} | {item['utility']:.3f} | {item['text']} |")
    lines.extend(
        [
            "",
            f"Raw store size {counts['raw']}. Deduped store size {counts['deduped']}. `pref-confirm-dup` is the near-copy that dedup removes.",
            "",
            "## Policy hit@k (deduped store)",
            "",
            "| task | expected | baseline top | adaptive top | baseline hit@1 | adaptive hit@1 | baseline hit@3 | adaptive hit@3 | hit@1 |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report["deduped_tasks"]:
        lines.append(
            "| {task} | {expected} | {base} | {adapt} | {b1} | {a1} | {bk} | {ak} | {rel} |".format(
                task=row["task_id"],
                expected=", ".join(row["expected_ids"]),
                base=_fmt_ids(row["baseline_top"]),
                adapt=_fmt_ids(row["adaptive_top"]),
                b1=row["baseline_hit_at_1"],
                a1=row["adaptive_hit_at_1"],
                bk=row["baseline_hit_at_k"],
                ak=row["adaptive_hit_at_k"],
                rel=_compare(row["baseline_hit_at_1"], row["adaptive_hit_at_1"]),
            )
        )
    lines.extend(
        [
            "",
            (
                f"Mean hit@1 baseline {means['baseline_hit_at_1']:.2f}, adaptive {means['adaptive_hit_at_1']:.2f}. "
                f"Mean hit@3 baseline {means['baseline_hit_at_k']:.2f}, adaptive {means['adaptive_hit_at_k']:.2f}."
            ),
            (
                f"hit@1 counts on the four tasks: adaptive higher {comparison['adaptive_higher']}, "
                f"baseline higher {comparison['baseline_higher']}, tie {comparison['tie']}."
            ),
            (
                "hit@3 counts on the four tasks: adaptive higher {adaptive_higher}, "
                "baseline higher {baseline_higher}, tie {tie}.".format(**report["hit_at_k_comparison"])
            ),
            "",
            "Reading, from this seed and these vectors:",
            "",
            "- Preference recall: the nearer distractor has a failing history. Baseline hit@1 stays on that distractor. Adaptive hit@1 moves to `pref-confirm`.",
            "- Prior decision: baseline hit@1 stays on the older direct-open decision (higher cosine, failing history). Adaptive hit@1 moves to `decision-backup`.",
            "- Duplicate suppression: expected id is `unique-fact` under the preference probe, after near-dup collapse. Baseline hit@3 includes it. Adaptive hit@3 does not, because the backup decision's utility outranks that fact. Adaptive does not win this task.",
            "- Stale/contradiction: both dated theme bullets have utility 0, so the adaptive term does not reorder them. Top-1 is `theme-stale` for both policies, so expected `theme-current` is hit@1 = 0 and hit@3 = 1. Dated text alone does not demote the stale bullet.",
            "",
            "Adaptive does not beat baseline on every task. That is the result.",
            "",
            "## Duplicate counts",
            "",
        ]
    )
    raw = report["raw_duplicate"]
    dedup_row = next(row for row in report["deduped_tasks"] if row["task_id"] == "duplicate_suppression")
    lines.extend(
        [
            f"Raw preference-family ids in the top {K}: baseline {raw['baseline_preference_copies']}, adaptive {raw['adaptive_preference_copies']}.",
            f"Deduped preference-family ids in the top {K}: baseline {dedup_row['baseline_preference_copies']}, adaptive {dedup_row['adaptive_preference_copies']}.",
            f"Raw `unique-fact` hit@3: baseline {raw['baseline_hit_at_k']}, adaptive {raw['adaptive_hit_at_k']}. Both miss while the near-copy occupies a slot.",
            "Item dedup is what removes the extra copy. The adaptive score does not.",
            "",
            "## Skill API retrieve",
            "",
            "Fixtures: `tests/fixtures/synthetic/MEMORY.md` and `dated-notes.md`. Import redaction stayed off on every row.",
            "",
            "| scenario | policy | created | skipped | selected labels | unique-fact | theme-stale | theme-current | decision-backup |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report["skill"]:
        hits = row["hits"]
        lines.append(
            "| {scenario} | {policy} | {created} | {skipped} | {labels} | {unique} | {stale} | {current} | {backup} |".format(
                scenario=row["scenario"],
                policy=row["policy"],
                created=row["created"],
                skipped=row["skipped"],
                labels=", ".join(row["selected_labels"]),
                unique=hits["unique-fact"],
                stale=hits["theme-stale"],
                current=hits["theme-current"],
                backup=hits["decision-backup"],
            )
        )
    lines.extend(
        [
            "",
            "On `memory-dedup-off`, recency order keeps the first three confirmation lines and drops `unique-fact`. `automatic` selects a different trio because tied attention scores sort by event id, which is not chronological once ids pass 9. That is why `automatic` can list `unique-fact` without dedup. It did not match the query.",
            "",
            "On `memory-dedup-on`, near-duplicate confirmation and standup lines collapse (`skip`). Three observations fit in the budget, including `unique-fact`, for both policies.",
            "",
            "On `dated-notes`, both policies keep the first three bullets and drop `decision-backup`. The stale theme stays. After `contradict` (both observations kept) and one `decay` on the stale theme event, both policies drop `theme-stale` and include `decision-backup`. The date string did not do that. The decay signal did. The two policies still agree.",
            "",
            "Skill retrieve does not implement the cosine-plus-utility score. Use the policy-layer table for that comparison.",
            "",
        ]
    )
    return "\n".join(lines)


def write_synthetic(path: Path | None = None) -> dict:
    report = build_report()
    target = path if path is not None else DEFAULT_RESULTS
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_report(report), encoding="utf-8")
    return report


def _repo_contains(path: Path) -> bool:
    resolved = path.resolve()
    repo = ROOT.resolve()
    return resolved == repo or repo in resolved.parents


def parse_extra_markdown_names(values: list[str] | None) -> frozenset[str]:
    """Split repeatable, comma-separated CLI values into exact basenames."""

    collected: list[str] = []
    for raw in values or []:
        if not isinstance(raw, str):
            raise LocalEvalError("extra markdown names must be exact basenames")
        collected.extend(part.strip() for part in raw.split(",") if part.strip())
    return _validate_extra_markdown_names(collected)


def _validate_extra_markdown_names(names: list[str] | frozenset[str] | set[str]) -> frozenset[str]:
    cleaned: set[str] = set()
    for name in names:
        if not isinstance(name, str) or not name or name != name.strip():
            raise LocalEvalError("extra markdown names must be exact basenames")
        if "/" in name or "\\" in name or name != Path(name).name or name in {".", ".."}:
            raise LocalEvalError("extra markdown names must be exact basenames")
        if any(char in name for char in "*?\x00"):
            raise LocalEvalError("extra markdown names must be exact basenames")
        cleaned.add(name)
    return frozenset(cleaned)


def local_source_config(
    extra_markdown_names: frozenset[str] | set[str] | list[str] | None = None,
    *,
    recognize_dated_markdown: bool = False,
) -> SourceConfig:
    """Extended sources for one local run, including optional extras and dated names."""

    extras = _validate_extra_markdown_names(list(extra_markdown_names or ()))
    return SourceConfig.extended(extras, recognize_dated_markdown=recognize_dated_markdown)


def _tier_names(sources: SourceConfig | None = None) -> frozenset[str]:
    config = sources if sources is not None else SourceConfig.extended()
    return config.markdown_names | config.json_names


def classify_local_path(
    path: str,
    *,
    include_stores: bool,
    tier_names: frozenset[str] | set[str] | None = None,
) -> str:
    """Return tier_a, store, or an excluded_* reason. Never returns file text.

    ``tier_names`` is the Markdown and JSON name set for this run. It must be
    the same set discovery used, including extras and ``YYYY-MM-DD.md`` when
    that pattern is enabled. The default is ``SourceConfig.extended()`` with
    no extras and no dated pattern.
    """

    parts = [part.lower() for part in path.split("/")]
    if any(marker in part for part in parts for marker in _TRAJECTORY_MARKERS):
        return "excluded_trajectory"
    if "node_modules" in parts:
        return "excluded_vendor"
    name = Path(path).name
    lower = name.lower()
    if lower.endswith((".sqlite", ".sqlite3", ".jsonl")):
        return "store" if include_stores else "excluded_store"
    names = frozenset(tier_names) if tier_names is not None else _tier_names()
    if matches_recognized_name(name, names):
        return "tier_a"
    return "excluded_unlisted"


def _consume_hit(part: str, seen: set[str]) -> tuple[str, int]:
    if "=" not in part:
        raise LocalEvalError("hit labels must look like task=0 or task=1")
    label, value = part.split("=", 1)
    label = label.strip()
    if not label or any(char.isspace() for char in label) or any(char in label for char in "/\\="):
        raise LocalEvalError("hit labels must be short task names")
    if value.strip() not in {"0", "1"}:
        raise LocalEvalError("hit values must be 0 or 1")
    if label in seen:
        raise LocalEvalError("hit labels must be unique")
    seen.add(label)
    return label, int(value.strip())


def parse_hits(text: str) -> list[tuple[str, int]]:
    """Parse ``task=0,task=1`` hand scores. Each value is 0 or 1."""

    if not str(text).strip():
        return []
    rows: list[tuple[str, int]] = []
    seen: set[str] = set()
    for part in str(text).split(","):
        if not part.strip():
            raise LocalEvalError("hit labels must look like task=0 or task=1")
        rows.append(_consume_hit(part, seen))
    return rows


def parse_hit_line(text: str) -> list[tuple[str, int]]:
    """Parse a ``hit@k task=0 task=1`` aggregate line back into scores."""

    body = text.strip()
    if body.startswith("hit@k "):
        body = body[len("hit@k ") :].strip()
    elif body == "hit@k":
        return []
    if not body:
        return []
    rows: list[tuple[str, int]] = []
    seen: set[str] = set()
    for part in body.split():
        rows.append(_consume_hit(part, seen))
    return rows


def format_hit_line(hits: list[tuple[str, int]]) -> str:
    if not hits:
        return ""
    return "hit@k " + " ".join(f"{label}={value}" for label, value in hits)


def aggregate_json_path(markdown_path: Path) -> Path:
    """Sibling JSON path for a markdown aggregate ``--output``."""

    if markdown_path.suffix.lower() == ".md":
        return markdown_path.with_suffix(".json")
    return markdown_path.with_name(markdown_path.name + ".json")


def hits_from_aggregate_markdown(text: str) -> list[tuple[str, int]]:
    """Read the single PR-eligible hit@k line out of an aggregate markdown file."""

    lines = [line[len(_PR_LINE_PREFIX) :] for line in text.splitlines() if line.startswith(_PR_LINE_PREFIX)]
    if not lines:
        return []
    if len(lines) != 1:
        raise LocalEvalError("aggregate markdown must contain one hit@k line")
    return parse_hit_line(lines[0])


def hits_from_aggregate_json(payload: dict) -> list[tuple[str, int]]:
    """Read ``hits`` out of an aggregate JSON object. Values stay 0 or 1."""

    rows: list[tuple[str, int]] = []
    seen: set[str] = set()
    for row in payload.get("hits") or []:
        if not isinstance(row, dict) or "task" not in row or "hit" not in row:
            raise LocalEvalError("hit labels must look like task=0 or task=1")
        label = row["task"]
        value = row["hit"]
        if not isinstance(label, str) or isinstance(value, bool) or not isinstance(value, int):
            raise LocalEvalError("hit values must be 0 or 1")
        rows.append(_consume_hit(f"{label}={value}", seen))
    return rows


def run_local_aggregate(
    root: Path,
    output: Path,
    queries: list[str] | tuple[str, ...] | None = None,
    *,
    dedup: bool = False,
    include_stores: bool = False,
    preview_only: bool = False,
    hits: str = "",
    scan_limit: int = 128,
    max_depth: int = 4,
    extra_markdown_names: frozenset[str] | set[str] | list[str] | None = None,
    recognize_dated_markdown: bool = False,
) -> dict:
    """Import a local root in memory and write counts. No observation text.

    ``output`` is the markdown aggregate. A sibling JSON file (``.md``
    replaced with ``.json``) is written beside it. Both must resolve outside
    the git repository. ``hits`` is a comma-separated ``task=0`` / ``task=1``
    list; Tier A hand scores use ``preference``, ``prior-decision``, and
    ``stale-note``. The default query list is those task labels, not memory
    quotes. ``extra_markdown_names`` are exact basenames passed to
    ``SourceConfig.extended``. When ``recognize_dated_markdown`` is true,
    ``YYYY-MM-DD.md`` basenames are recognized too. Classification uses that
    same name set.
    """

    output = output.resolve()
    json_path = aggregate_json_path(output)
    if _repo_contains(output) or _repo_contains(json_path):
        raise LocalEvalError("refusing to write local-eval output inside the git repository")
    chosen_queries = list(queries) if queries is not None else list(_DEFAULT_LOCAL_QUERIES)
    if any(not isinstance(query, str) or not query.strip() for query in chosen_queries):
        raise LocalEvalError("local queries must be non-empty task labels")
    judgments = parse_hits(hits)
    root = root.resolve()
    sources = local_source_config(
        extra_markdown_names, recognize_dated_markdown=recognize_dated_markdown
    )
    tier_names = _tier_names(sources)
    item_dedup = ItemDedupPolicy("skip", near=True) if dedup else None
    entry = SkillEntrypoint(
        seed=SKILL_SEED,
        context_budget=SKILL_BUDGET,
        policy="none",
        backend="memory",
        redact=False,
        sources=sources,
        item_dedup=item_dedup,
    )
    handle = entry.open("local-eval")
    discovered = handle.start(root=root, scan_limit=scan_limit, max_depth=max_depth)
    recognized = [item["path"] for item in discovered["sources"] if item.get("status") == "recognized"]
    grouped: dict[str, list[str]] = {}
    for path in recognized:
        grouped.setdefault(
            classify_local_path(path, include_stores=include_stores, tier_names=tier_names), []
        ).append(path)
    selected = grouped.get("tier_a", []) + (grouped.get("store", []) if include_stores else [])
    preview = handle.preview_import(selected) if selected else None
    imported = None
    selected_counts = []
    if selected and not preview_only:
        imported = handle.import_selected(selected)
        for query in chosen_queries:
            result = handle.invoke("retrieve", {"query": query})["result"]
            selected_counts.append({"query": query, "selected_count": len(result["selected"])})
    redaction = (imported or preview or {}).get("redaction") or {"enabled": False, "items_total": 0, "items_redacted": 0, "counts": {}}
    created = len(imported["created"]) if imported else 0
    skipped = len(imported["skipped"]) if imported else 0
    merged = len(imported["merged"]) if imported else 0
    summary = {
        "root_basename": root.name,
        "recognized_count": len(recognized),
        "imported_path_count": len(selected) if imported else 0,
        "preview_path_count": len(selected),
        "excluded_trajectory": len(grouped.get("excluded_trajectory", [])),
        "excluded_vendor": len(grouped.get("excluded_vendor", [])),
        "excluded_store": len(grouped.get("excluded_store", [])),
        "excluded_unlisted": len(grouped.get("excluded_unlisted", [])),
        "created": created,
        "skipped": skipped,
        "merged": merged,
        "rejected": len((imported or {}).get("rejected", [])),
        "redaction_enabled": bool(redaction.get("enabled")),
        "redaction_items_total": redaction.get("items_total", 0),
        "redaction_items_redacted": redaction.get("items_redacted", 0),
        "scan_truncated": "scan truncated at bound" in discovered.get("diagnostics", []),
        "preview_only": preview_only,
        "include_stores": include_stores,
        "dedup": dedup,
        "recognize_dated_markdown": recognize_dated_markdown or DATED_MARKDOWN_TOKEN in sources.markdown_names,
        "extra_markdown_name_count": len(sources.markdown_names - _tier_names() - {DATED_MARKDOWN_TOKEN}),
        "selected_counts": selected_counts,
        "hits": [{"task": label, "hit": value} for label, value in judgments],
        "pr_one_liner": format_hit_line(judgments),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(_render_local(summary), encoding="utf-8")
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def _render_local(summary: dict) -> str:
    lines = [
        "# Local eval aggregates",
        "",
        "Do not commit this file. Counts only. No memory text and no source paths.",
        "",
        f"- root_basename: {summary['root_basename']}",
        f"- recognized_count: {summary['recognized_count']}",
        f"- preview_path_count: {summary['preview_path_count']}",
        f"- imported_path_count: {summary['imported_path_count']}",
        f"- excluded_trajectory: {summary['excluded_trajectory']}",
        f"- excluded_vendor: {summary['excluded_vendor']}",
        f"- excluded_store: {summary['excluded_store']}",
        f"- excluded_unlisted: {summary['excluded_unlisted']}",
        f"- created: {summary['created']}",
        f"- skipped: {summary['skipped']}",
        f"- merged: {summary['merged']}",
        f"- rejected: {summary['rejected']}",
        f"- redaction_enabled: {str(summary['redaction_enabled']).lower()}",
        f"- redaction_items_total: {summary['redaction_items_total']}",
        f"- redaction_items_redacted: {summary['redaction_items_redacted']}",
        f"- scan_truncated: {str(summary['scan_truncated']).lower()}",
        f"- preview_only: {str(summary['preview_only']).lower()}",
        f"- include_stores: {str(summary['include_stores']).lower()}",
        f"- dedup: {str(summary['dedup']).lower()}",
        f"- recognize_dated_markdown: {str(summary['recognize_dated_markdown']).lower()}",
        f"- extra_markdown_name_count: {summary['extra_markdown_name_count']}",
        "",
        "## Selected counts",
        "",
    ]
    if summary["selected_counts"]:
        for row in summary["selected_counts"]:
            lines.append(f"- {row['query']}: {row['selected_count']}")
    else:
        lines.append("- none")
    lines.extend(["", "## Hand-scored hit@k", ""])
    if summary["hits"]:
        for row in summary["hits"]:
            lines.append(f"- {row['task']}: {row['hit']}")
        lines.extend(["", f"{_PR_LINE_PREFIX}{summary['pr_one_liner']}"])
    else:
        lines.append("- none recorded")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synthetic use-case eval, or a local counts-only aggregate.")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--local-root", type=Path, default=None)
    parser.add_argument("--queries", nargs="*", default=None)
    parser.add_argument("--dedup", action="store_true")
    parser.add_argument("--include-stores", action="store_true")
    parser.add_argument("--preview-only", action="store_true")
    parser.add_argument(
        "--hits",
        default="",
        help=(
            "Hand scores as task=0 or task=1, comma-separated. "
            "Tier A tasks: preference, prior-decision, stale-note. "
            "Written into the markdown aggregate and its sibling JSON."
        ),
    )
    parser.add_argument("--scan-limit", type=int, default=128)
    parser.add_argument("--max-depth", type=int, default=4)
    parser.add_argument(
        "--extra-markdown-names",
        action="append",
        default=None,
        metavar="NAME",
        help=(
            "Exact Markdown basename to recognize, besides the extended set. "
            "Repeat the flag or separate names with commas. Requires --local-root."
        ),
    )
    parser.add_argument(
        "--recognize-dated-markdown",
        action="store_true",
        help="Also recognize Markdown basenames that are exactly YYYY-MM-DD.md. Requires --local-root.",
    )
    args = parser.parse_args(argv)
    try:
        extras = parse_extra_markdown_names(args.extra_markdown_names)
        if args.local_root is None and (extras or args.recognize_dated_markdown):
            raise LocalEvalError(
                "--extra-markdown-names and --recognize-dated-markdown require --local-root"
            )
        if args.local_root is not None:
            if args.output is None:
                raise LocalEvalError("--local-root requires --output outside the repository")
            run_local_aggregate(
                args.local_root,
                args.output,
                args.queries,
                dedup=args.dedup,
                include_stores=args.include_stores,
                preview_only=args.preview_only,
                hits=args.hits,
                scan_limit=args.scan_limit,
                max_depth=args.max_depth,
                extra_markdown_names=extras,
                recognize_dated_markdown=args.recognize_dated_markdown,
            )
            return 0
        write_synthetic(args.output)
    except LocalEvalError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
