# Redaction at import

Explicit import (`SkillHandle.import_selected`) redacts every parsed item before it becomes mechanism memory. `SkillHandle.preview_import(paths)` is the dry run: it parses and redacts, writes nothing, does not enable memory operations, and reports counts only.

Categories (all on by default): `private_key`, `aws_access_key`, `github_token`, `slack_token`, `api_key` (sk-...), `bearer_token`, `credential_assignment` (key/secret/token/password = value), `email`, `cn_phone`, `home_path` (/Users/<name>, /home/<name>).

Matches become `[REDACTED:<category>]`. Reports contain per-category counts, never matched values. Opt out or narrow with `SkillEntrypoint(redaction=RedactionPolicy.only("email", ...))` / `RedactionPolicy.disabled()`. Redaction stays enabled by default. Item dedup, when opted in, compares the text after this step (see [DEDUP.md](DEDUP.md)).

Limits: pattern based, so it cannot catch free-text secrets, names or addresses. Treat redaction as a safety net, not a guarantee; review the dry-run report before importing real memory.
