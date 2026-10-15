"""Pattern redaction for secrets and personal identifiers.

``redact_text`` and ``redact_items`` apply ``DEFAULT_POLICY`` (every category)
when no policy is passed. Import does not. ``SkillEntrypoint`` stores text as
written unless the caller opts in with ``redact=True`` or an explicit enabled
policy. Matches are replaced by ``[REDACTED:<category>]`` placeholders.
Reports carry only category counts (never matched values), so they are safe
to print or log. Redaction is deterministic and has no I/O.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

__all__ = [
    "ALL_CATEGORIES",
    "DEFAULT_POLICY",
    "RedactionPolicy",
    "RedactionReport",
    "redact_items",
    "redact_text",
]

# Order matters: more specific secret shapes run before the generic key=value one.
_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----(?:.*?-----END [A-Z ]*PRIVATE KEY-----)?", re.S)),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    ("api_key", re.compile(r"\bsk-[A-Za-z0-9_-]{16,}")),
    ("bearer_token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{20,}")),
    (
        "credential_assignment",
        re.compile(
            r"(?i)\b(api[_-]?key|secret|token|passwd|password)([\"']?\s*[:=]\s*[\"']?)[A-Za-z0-9/+_.\-]{16,}"
        ),
    ),
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("cn_phone", re.compile(r"(?<![0-9])1[3-9][0-9]{9}(?![0-9])")),
    ("home_path", re.compile(r"(?<![A-Za-z0-9_])/(?:Users|home)/[A-Za-z0-9_.-]+(?=/|\b)")),
)

ALL_CATEGORIES: tuple[str, ...] = tuple(name for name, _ in _RULES)


@dataclass(frozen=True)
class RedactionPolicy:
    """Which categories to redact.

    ``RedactionPolicy()`` enables every category. That object is the opt-in
    policy. Import leaves redaction off unless the caller asks for it.
    """

    categories: frozenset[str] = frozenset(ALL_CATEGORIES)
    enabled: bool = True

    def __post_init__(self) -> None:
        unknown = set(self.categories) - set(ALL_CATEGORIES)
        if unknown:
            raise ValueError(f"unknown redaction categories: {sorted(unknown)}")

    @classmethod
    def only(cls, *categories: str) -> "RedactionPolicy":
        return cls(categories=frozenset(categories))

    @classmethod
    def disabled(cls) -> "RedactionPolicy":
        return cls(categories=frozenset(), enabled=False)


# Full category set used by redact_text/redact_items, and by import when the
# caller opts in with redact=True and no narrower policy. Not the import default.
DEFAULT_POLICY = RedactionPolicy()


@dataclass
class RedactionReport:
    """Aggregate redaction outcome. Contains counts only, never values."""

    items_total: int = 0
    items_redacted: int = 0
    counts: dict[str, int] = field(default_factory=dict)

    def add(self, other_counts: dict[str, int]) -> None:
        self.items_total += 1
        if other_counts:
            self.items_redacted += 1
        for key, value in other_counts.items():
            self.counts[key] = self.counts.get(key, 0) + value

    def as_dict(self) -> dict:
        return {
            "items_total": self.items_total,
            "items_redacted": self.items_redacted,
            "counts": dict(sorted(self.counts.items())),
        }


def redact_text(text: str, policy: RedactionPolicy = DEFAULT_POLICY) -> tuple[str, dict[str, int]]:
    """Return (redacted_text, {category: count}). Deterministic."""

    if not policy.enabled or not text:
        return text, {}
    counts: dict[str, int] = {}
    out = text
    for name, pattern in _RULES:
        if name not in policy.categories:
            continue
        if name == "credential_assignment":
            out, n = pattern.subn(lambda m: f"{m.group(1)}{m.group(2)}[REDACTED:{name}]", out)
        elif name == "home_path":
            out, n = pattern.subn(f"/[REDACTED:{name}]", out)
        else:
            out, n = pattern.subn(f"[REDACTED:{name}]", out)
        if n:
            counts[name] = counts.get(name, 0) + n
    return out, counts


def redact_items(
    items: Iterable[dict], policy: RedactionPolicy = DEFAULT_POLICY
) -> tuple[list[dict], RedactionReport]:
    """Redact the ``text`` of parsed items and recompute their digest.

    Item order and count are preserved. Items that become identical after
    redaction stay distinct occurrences (the caller decides about dedup).
    """

    import hashlib

    report = RedactionReport()
    result: list[dict] = []
    for item in items:
        new_text, counts = redact_text(item["text"], policy)
        report.add(counts)
        copy = dict(item)
        if counts:
            copy["text"] = new_text
            copy["digest"] = hashlib.sha256(new_text.encode("utf-8")).hexdigest()
            copy["redacted"] = True
        result.append(copy)
    return result, report
