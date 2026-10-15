# Markdown adapter v2 (opt-in)

`SkillEntrypoint(sources=SourceConfig.extended())` turns on:
- discovery of `AGENTS.md`, `SOUL.md`, `USER.md`, `IDENTITY.md`, `TOOLS.md`, `HEARTBEAT.md`, `CLAUDE.md` in addition to `MEMORY.md`/`memory.md` (add more with `SourceConfig.extended({"NOTES.md"})`, or fully custom `SourceConfig(markdown_names=..., markdown_v2=True)`). `SourceConfig.extended(..., recognize_dated_markdown=True)` also recognizes basenames that are exactly `YYYY-MM-DD.md`. That switch is off by default;
- the v2 parser: leading YAML-subset frontmatter is metadata (not observations; `name`/`type`/`description` ride along as `doc_meta`); each item gets its heading path (`section`) and first ISO date (`date`); fenced code, HTML comments and rules are skipped; numbered lists and checkboxes are unwrapped.

Default `SourceConfig()` is unchanged (v1 adapter, original four names), so existing behavior and tests are untouched. v1 treats frontmatter lines as observations; flipping the default is a separate decision. Item digests cover text only; duplicate lines in different sections stay distinct occurrences. Redaction (docs/REDACTION.md) is off by default and, when opted in, runs after parsing.
