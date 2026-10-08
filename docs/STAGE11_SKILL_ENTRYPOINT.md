# Stage 11 Skill entrypoint

Minimal distributable entry over the Stage 10 bootstrap seam and the Stage 8/9 Skill API.

## Package

- Python entry: `memory_infra.entrypoint.SkillEntrypoint`
- Packaging marker: project entry point `memory_infra.skill` / `agent_memory`
- Instruction file: `src/memory_infra/SKILL.md`

No MCP, HTTP, authentication, or agent SDK is included.

## Startup sequence

1. `SkillEntrypoint.open(caller_id)` opens a caller-bound Stage 10 `BootstrapSession`.
2. `handle.start(root=..., artifacts=...)` runs the bounded read-only discovery scan.
3. The return value exposes inventory, diagnostics, and sources. `memory_operations_enabled` is false. `imported` is false.
4. `handle.enable_memory()` may run only after that discovery. It opens `SkillApi` and does not ingest discovered files.
5. `handle.invoke(op, payload)` forwards to the public Skill API for that caller only.

Unknown and unreadable sources are recorded and do not abort startup. Repeated `start` on the same handle replaces only that handle's discovery note and does not import memory.

## Non-claims

This entrypoint does not claim compatibility with external harness products beyond the tested in-process sequence. Stage 11 is not marked PASS by this document.
