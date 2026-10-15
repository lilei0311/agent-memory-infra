"""Memory-item deduplication.

Equality is a content key, not an embedding and not an edit distance.

* ``exact_text`` (``near=False``): SHA-256 of the item text as stored.
* ``normalized_text`` (``near=True``): SHA-256 after NFKC, casefold, strip,
  and collapsing internal whitespace. ``"The  Workspace"`` matches
  ``"the workspace"``. Punctuation and word changes do not match.

Modes, applied only when a key is already stored:

* ``skip``: keep the first item. The new one is not stored.
* ``merge``: keep the first item's id and text. On ``MemoryStore``, union
  tags and sum ``success`` / ``failure``. On import, append provenance to
  the first ledger record and do not create another observation.
* ``keep_latest``: identical text is ``skip`` (nothing newer). A near
  duplicate with different raw text replaces mutable ``MemoryStore`` fields
  in place and keeps the original id. Import observations are immutable, so
  import ``keep_latest`` records a new observation and marks the previous
  ledger entry superseded. The previous event stays in the graph.

The default import path does not enable this. Stage 12 source-snapshot
idempotency is unchanged until a caller passes ``ItemDedupPolicy``.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from typing import Mapping

__all__ = [
    "DEDUP_MODES",
    "ItemDecision",
    "ItemDedupPolicy",
    "item_key",
    "normalize_text",
    "plan_items",
]

DEDUP_MODES = ("skip", "merge", "keep_latest")
_WS = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """NFKC, casefold, strip, and collapse whitespace."""

    if not isinstance(text, str):
        raise TypeError("memory text must be a string")
    folded = unicodedata.normalize("NFKC", text).casefold().strip()
    return _WS.sub(" ", folded)


def item_key(text: str, *, near: bool) -> str:
    basis = normalize_text(text) if near else text
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()


def equality_name(near: bool) -> str:
    return "normalized_text" if near else "exact_text"


@dataclass(frozen=True)
class ItemDedupPolicy:
    """How to treat an item whose content key is already stored.

    ``mode="skip"`` and ``near=True`` is the recommended opt-in.
    """

    mode: str = "skip"
    near: bool = True

    def __post_init__(self) -> None:
        if self.mode not in DEDUP_MODES:
            raise ValueError(f"item dedup mode must be one of {', '.join(DEDUP_MODES)}")
        if not isinstance(self.near, bool):
            raise TypeError("item dedup near must be a bool")

    def describe(self) -> dict:
        return {
            "enabled": True,
            "mode": self.mode,
            "near": self.near,
            "equality": equality_name(self.near),
        }


def disabled_dedup() -> dict:
    return {"enabled": False, "mode": None, "near": None, "equality": None}


@dataclass(frozen=True)
class ItemDecision:
    """One planned action. ``key`` is None when dedup is off."""

    index: int
    action: str
    key: str | None


def resolve_action(policy: ItemDedupPolicy, prior_text: str | None, text: str) -> str:
    if prior_text is None:
        return "create"
    if policy.mode == "merge":
        return "merge"
    if policy.mode == "keep_latest" and text != prior_text:
        return "keep_latest"
    return "skip"


def plan_items(
    items: list[dict],
    policy: ItemDedupPolicy | None,
    prior: Mapping[str, str] | None = None,
) -> tuple[list[ItemDecision], dict[str, str]]:
    """Plan create/skip/merge/keep_latest without writing memory.

    ``prior`` maps content key to the active raw text. It is not mutated.
    With ``policy is None`` every item is ``create`` and the index is copied
    through unchanged. Dedup compares ``item["text"]`` (already redacted
    when the caller redacts first).
    """

    index = dict(prior or {})
    decisions: list[ItemDecision] = []
    if policy is None:
        for index_in_batch, _item in enumerate(items):
            decisions.append(ItemDecision(index_in_batch, "create", None))
        return decisions, index
    for index_in_batch, item in enumerate(items):
        text = item["text"]
        if not isinstance(text, str):
            raise TypeError("memory text must be a string")
        key = item_key(text, near=policy.near)
        action = resolve_action(policy, index.get(key), text)
        decisions.append(ItemDecision(index_in_batch, action, key))
        if action in {"create", "keep_latest"}:
            index[key] = text
    return decisions, index
