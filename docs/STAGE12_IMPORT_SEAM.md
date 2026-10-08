# Stage 12 explicit historical-memory import

Smallest caller-invoked structuring seam after Stage 10 discovery and the Stage 11 entrypoint.

Discovery remains read-only. `handle.start` never imports. `handle.import_selected(paths)` is the only import operation.

## Operation

Public entry: `SkillEntrypoint` / `SkillHandle.import_selected`.

Recognized names stay `MEMORY.md`, `memory.md`, `memories.json`, and `memory.json`. Markdown imports non-empty, non-heading lines. JSON imports a string, a list of strings, or `memories` / `items` / `text` / `content` fields. Other shapes are rejected.

Each accepted line becomes a mechanism observation and promotion through the public Skill API. Mechanism code assigns point, event, and evidence ids. The observation source is `import:<path>`.

## Duplicate policy

`idempotent_by_source_digest`. A repeated explicit import of the same path and content digest returns the previously recorded point and event ids and does not create another observation. A changed digest is a new import. The ledger stays on the caller handle.

## Rejection

Unknown, unreadable, not-in-discovery, and unparseable selections are reported in `rejected`. They are not ingested. Source files are not rewritten or deleted.

## Non-claims

This is not a Memory Graph, migration framework, or Hub feature. Stage 12 is not marked PASS by this document.
