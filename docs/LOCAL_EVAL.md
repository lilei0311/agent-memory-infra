# Local evaluation playbook

**Do not commit real memory.** This page is a checklist for a private dry-run. The public repository may contain the synthetic eval, this playbook, and aggregate numbers. It must not contain real memory files, database files, JSONL transcripts, explorer HTML rendered from a real import, or Mac home paths that point at real content.

Write local output outside the git clone (or under a gitignored name such as `local-eval/`). Before any commit, `git status` must not list those files. A pull request may quote one aggregate line only (`hit@k preference=1 prior-decision=0 stale-note=1`). Never quote observation text.

Redaction stays **off** for personal use (`redact=False`, the default). Do not flip that default. Turn redaction on only when preparing a shareable export. See [REDACTION.md](REDACTION.md).

Trajectory and session-telemetry files are not the memory product. Leave them out of the eval set.

## What you can measure

The synthetic script scores four tasks and writes `experiments/results/usable_c_synthetic_eval.md`:

- preference recall
- prior decision / fix
- duplicate suppression
- stale or contradictory dated bullets

That file uses invented labels only. Adaptive retrieval is reported next to the baseline and is not required to win. Run it before any private copy:

```bash
python3 -m pytest -q tests
python3 experiments/synthetic_usecase_eval.py
```

On a machine that holds a real corpus, the same script can import a **narrow local snapshot** and write counts only:

```bash
python3 experiments/synthetic_usecase_eval.py \
  --local-root "$DEST" \
  --output "$EVAL_PARENT/aggregates.md"
```

`$DEST` and `$EVAL_PARENT` must sit outside this clone. If `--output` or its sibling JSON path resolves inside the repository, the script exits 2 and writes nothing. `--output "$EVAL_PARENT/aggregates.md"` also writes `$EVAL_PARENT/aggregates.json`. Both files have counts, redaction flags, and selected lengths. Neither records observation text or source paths. After the Tier A import, record hand-scored hit@k with `--hits`. Each of `preference`, `prior-decision`, and `stale-note` is 0 or 1:

```bash
python3 experiments/synthetic_usecase_eval.py \
  --local-root "$DEST" \
  --output "$EVAL_PARENT/aggregates.md" \
  --hits preference=1,prior-decision=0,stale-note=1
```

The markdown file ends with one PR-eligible line, `hit@k preference=1 prior-decision=0 stale-note=1`. The JSON file stores the same scores as integers under `hits` and repeats that line as `pr_one_liner`. A pull request may quote that one aggregate line only.

`--preview-only` stops after discovery and `preview_import`. `--dedup` turns on near-duplicate `skip` for that process. The process keeps mechanism state in memory; it does not write a Skill store file. A persistent store, if you want one, belongs under `$EVAL_PARENT` as well.

Exact extra basenames and dated daily notes stay **off** unless you opt in. `--extra-markdown-names` is repeatable and accepts commas. Each value is an exact basename (`side-notes.md`), not a path and not a glob. `--recognize-dated-markdown` also recognizes basenames that are exactly `YYYY-MM-DD.md` (month 01–12, day 01–31, lowercase `.md`). A date inside a longer name does not match. Passing the token `YYYY-MM-DD.md` as an extra name is the same switch as the flag. Both options are forwarded to `SourceConfig.extended` and to the name set that classifies tier A, so a file discovery accepts is not then counted as `excluded_unlisted`.

```bash
python3 experiments/synthetic_usecase_eval.py \
  --local-root "$DEST" \
  --output "$EVAL_PARENT/aggregates.md" \
  --extra-markdown-names side-notes.md \
  --extra-markdown-names "Custom.md,Other.md" \
  --recognize-dated-markdown \
  --hits preference=1,prior-decision=0,stale-note=1
```

Without those flags the recognized set is unchanged: the extended persona names plus `memories.json` and `memory.json`. The aggregate records `recognize_dated_markdown` and `extra_markdown_name_count` (a count, not the names). Pass the flags on the same `--local-root` command as `--hits` when the Tier A notes you will score use an extra basename or a `YYYY-MM-DD.md` name. The README local-sources paragraph points at this playbook.

## Checklist

- [ ] Synthetic pytest and `experiments/synthetic_usecase_eval.py` exit 0.
- [ ] Freeze a Markdown-only snapshot **outside** any git worktree. Do not point the scanner at a live multi-gigabyte agent tree.
- [ ] Skip `node_modules` template copies, trajectory / telemetry trees, and `*.bak` sidecars.
- [ ] Leave `redact=False`. Confirm the aggregate says `redaction_enabled: false`.
- [ ] Preview counts, then import Tier A.
- [ ] After the Tier A import, record hit@k via `--hits` (`preference`, `prior-decision`, `stale-note` as 0 or 1). That writes the aggregate markdown and the sibling JSON.
- [ ] A PR may quote one aggregate line only (the `hit@k` one-liner). Never quote observation text.
- [ ] Optional later: SQLite only from a backup copy, with `--include-stores`, still outside git.
- [ ] `git status` in the clone shows no new memory, database, JSONL, or explorer HTML.

## OpenClaw layout (aggregates)

Live state is the `~/.openclaw` home. It is a hybrid tree: small config stays on the internal disk; `agents` and `workspace` may be symlinks into a larger migrated copy (on the order of 21G). `~/.openclaw/memory/` may hold small SQLite backups on the internal disk. There is no separate frozen eval copy until you make one. The migrated tree is live data. Read it only to build the snapshot below, and do not write to it.

**Tier A — start here.** Curated workspace Markdown: persona files (`MEMORY.md`, `AGENTS.md`, `SOUL.md`, `USER.md`, `IDENTITY.md`, `HEARTBEAT.md`, `TOOLS.md`) at the workspace root and under per-agent folders. About 17 of those files are real curated notes, about 120 KB, once `node_modules` templates are excluded. `workspace/memory/*.md` is about 4 dated notes, about 384 KB (one may be empty). An optional extra folder of dated daily notes can sit outside `~/.openclaw` (about 50 files, ~197 KB, of which a dated subset is about 21 files, ~128 KB). Those filenames are not in the default recognized set. On the local snapshot, pass exact basenames with `--extra-markdown-names`, or pass `--recognize-dated-markdown` for `YYYY-MM-DD.md` files. Both stay off unless you set them.

**Exclude.** Trajectory / telemetry under the agent tree is about 23,441 files and about 6.6G. Session transcript tables (on the order of 19k rows) are telemetry. The local command skips paths that contain `trajectory` or `archive-tier`, and it skips `node_modules`. It does not import `*.sqlite`, `*.sqlite3`, or `*.jsonl` unless you pass `--include-stores`.

**Tier B — optional, after a backup.** Per-agent `openclaw-agent.sqlite` stores indexed chunks in `memory_index_chunks`. The main agent index is on the order of 4672 chunks and 622 sources. A second agent index is on the order of 570 chunks. Empty backups (0 chunks) can be skipped. A live database may keep pages in a WAL sidecar, so the main file alone can be incomplete. Copy with SQLite's backup API, then point the tool at the copy:

```bash
sqlite3 "$SOURCE_DB" ".backup $EVAL_PARENT/openclaw-agent-snapshot.sqlite"
```

`$SOURCE_DB` stays where it is. The snapshot stays under `$EVAL_PARENT`, never inside the clone. The adapter reads a byte snapshot and does not open the live path, which also means it will not see WAL pages you forgot to fold in. Details: [LOCAL_SOURCES.md](LOCAL_SOURCES.md).

A Hermes-style `~/.hermes/state.db` (on the order of 200 MB and 18k messages) is a separate chat corpus. It is not part of this first dry-run.

## Freeze

```bash
STAMP=$(date +%Y%m%d)
EVAL_PARENT="${EVAL_PARENT:-$HOME/agent-memory-infra-eval}"
DEST="$EVAL_PARENT/openclaw-md-copy-${STAMP}"
mkdir -p "$DEST"
# Copy only the curated markdown you intend to score.
# Skip node_modules, trajectories, sqlite, jsonl, and bak files.
# Recognized names are MEMORY.md, AGENTS.md, SOUL.md, USER.md,
# IDENTITY.md, HEARTBEAT.md, TOOLS.md, CLAUDE.md, memories.json, memory.json.
# Add exact basenames with --extra-markdown-names.
# Add YYYY-MM-DD.md files with --recognize-dated-markdown.
echo "Copy at $DEST — keep off GitHub"
```

Layout inside `$DEST` so discovery can see the files (`max_depth` defaults to 4 on the local command; `scan_limit` defaults to 128). A scan that stops early sets `scan_truncated: true` in the aggregate. Raise the limits, or point `--local-root` at a smaller directory. Do not raise them in order to walk the full agent tree.

## After import

Judge three tasks: a preference, a prior decision, and a stale note. `invoke("retrieve")` returns mechanism ids. Resolving those ids to text is a local step. The local command passes each `--queries` string into that call. The defaults are the task labels `preference`, `prior-decision`, and `stale-note`. A re-score can pass a longer preference-like string when the note wording differs from the label. Record the judgment with `--hits` so the markdown aggregate and the sibling JSON both store `preference`, `prior-decision`, and `stale-note` as 0 or 1. Explorer HTML, if you render it, goes under `$EVAL_PARENT` and is named so `.gitignore` (`*.explorer.html`) would ignore it even if it landed in a clone. Do not render it into the repository.

Honest limit: the local command opens with `policy="none"`. A non-empty `--queries` value is the ranking query. Skill `retrieve` scores each candidate with bag-of-words cosine (`query_relevance`, lowercase alphanumeric tokens, existing cosine helper) against observation text and sets `query_used_for_ranking=true` on the retrieve result and the retrieval trace. `policy="none"` orders by `query_relevance`, then recency, then earlier candidates. An empty query stays recency order. `policy="automatic"` uses `attention_weight + query_relevance + 0.01 * recency + 0.01 * contextual_fit` when the query is non-empty, and `attention_weight + 0.01 * recency + 0.01 * contextual_fit` when it is empty. The recorded Tier A line from 2026-10-16 is preference=0 prior-decision=0 stale-note=0; recognized=47 created=4630; that run filled the budget before this ranking existed. Re-score that snapshot on the Mac. This playbook does not supply a new hit number. The cosine-plus-utility comparison stays in the synthetic policy-layer table in `experiments/results/usable_c_synthetic_eval.md`. A local `--hits` line is the human 0/1 judgment. Tier B sqlite stays a later optional backup import.
