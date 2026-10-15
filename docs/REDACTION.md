# Redaction at import

Redaction is **off by default**. For local personal memory, leave it off and import text as written. Turn it on before sharing or exporting, or when writing into a less-trusted store. SQLite and JSONL imports use the same switch.

Opt in with `SkillEntrypoint(redact=True)`, `handle.import_selected(paths, redact=True)`, or `handle.preview_import(paths, redact=True)`. The first-run example accepts the same choice as `--redact`. Narrow categories with `SkillEntrypoint(redaction=RedactionPolicy.only("email", ...))`. `RedactionPolicy.disabled()` is the import default; `redact=False` on a single call forces that call off.

`SkillHandle.preview_import(paths)` is the dry run for either mode: it parses, redacts only when redaction is on, writes nothing, does not enable memory operations, and reports counts only. `redact_text` and `redact_items` stay available and still apply every category when called with no policy.

When redaction is on, matches become `[REDACTED:<category>]`. Reports contain per-category counts, never matched values. With redaction off, counts stay empty and the stored text is unchanged. Item dedup, when opted in, compares that stored text, so placeholders match only when redaction is on (see [DEDUP.md](DEDUP.md)).

Categories used when redaction is opted in: `private_key`, `aws_access_key`, `github_token`, `slack_token`, `api_key` (sk-...), `bearer_token`, `credential_assignment` (key/secret/token/password = value), `email`, `cn_phone`, `home_path` (/Users/<name>, /home/<name>).

Limits: pattern based, so it cannot catch free-text secrets, names or addresses. Treat redaction as a safety net, not a guarantee; review the dry-run report before sharing redacted memory.
