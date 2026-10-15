# Memory-item deduplication

Stage 12 still treats a repeated import of the same path and the same snapshot bytes as one import (`idempotent_by_source_digest`). That check does not compare items. Identical lines in one file stay separate observations, and a changed file is imported again from the top.

Item dedup is a separate, opt-in policy on `SkillEntrypoint(item_dedup=ItemDedupPolicy(...))` and on `MemoryStore.add_deduped`. The default import path leaves it off, so existing imports keep one observation per parsed line. `MemoryStore.add` is also unchanged: the same text under two ids stays two items. Experiments use `add`.

Synthetic files in `tests/fixtures/synthetic/` (`MEMORY.md`, `memories.json`, `store_items.json`) exercise the policy. They are invented notes, not a person's memory, and they contain no secrets. `examples/dedup_import.py` imports the markdown and JSON fixtures with `skip`.

## Equality

A content key is the SHA-256 of a comparison string.

| `near` | Name | Comparison string |
| --- | --- | --- |
| `True` (default when the policy is on) | `normalized_text` | NFKC, casefold, strip, collapse internal whitespace |
| `False` | `exact_text` | the item text as parsed |

`The  Workspace` matches `the workspace` only when `near` is true. `Hello` does not match `Hello!`. This is not embedding similarity and not an edit distance.

Dedup runs after redaction. Two different addresses that both become `[REDACTED:email]` share a key. Redaction itself stays the phase-1 default: enabled unless the caller passes `RedactionPolicy.disabled()`.

## Modes

The first item for a key is stored. A later item with the same key follows `mode`:

| Mode | `MemoryStore.add_deduped` | Explicit import |
| --- | --- | --- |
| `skip` | Do not store the new item. Return the first id. | Do not observe again. Report `skipped` with the first point and event ids. |
| `merge` | Keep the first id, text, and embedding. Union tags. Sum `success` and `failure`. | Do not observe again. Append `also_seen` (path, occurrence, snapshot digest, whether the raw text was equal) on the first ledger record. The observation text stays the first one. |
| `keep_latest` | If the raw text is equal, skip. Otherwise replace text, embedding, tags, and counters in place and keep the original id. | If the raw text is equal, skip. If it differs, record a new observation and list the previous ids under `superseded`. The previous event is not deleted or rewritten. |

`skip` is the recommended opt-in. Import `keep_latest` can add an observation each time the raw spelling changes, because mechanism observations are immutable. The store can overwrite a mutable item instead. `add_deduped` stores a copy of a new item, so later edits to the caller's object do not change the store. `add` still stores the caller's object.

The index is on the handle for that session. `start` clears it. It is not part of the mechanism snapshot, so a new process does not remember which texts were imported. A byte-identical reimport still hits the Stage 12 snapshot ledger and returns the previously created records as `reused` without running item dedup again.

`preview_import` plans the same actions (`would_create`, `would_skip`, `would_merge`, `would_keep_latest`) and writes nothing.
