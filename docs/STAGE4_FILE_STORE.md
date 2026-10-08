# Stage 4 file-backed durable store

Storage substitution only. `FileDurableStore` implements `DurableStorePort` with the Python standard library. It does not allocate identifiers and does not own lifecycle, thread, relation, or trace transitions.

The persisted file is the Stage 3 snapshot. Validation and the mechanism-owned seal stay in front of restore. The seal key is not a snapshot field and is not returned by `MemoryService`, `FileDurableStore`, or the package export list. There is no public `restart_seal`. An operator who already holds the key out of band may pass it to `FileDurableStore` before `MemoryService` binds a new key. That constructor input is a restart handoff, not an extractor. `_restart_capability` is an internal mechanism/test path and is not part of the documented caller API.

File behavior:

- missing path: `load_snapshot` returns `None`
- empty, truncated, non-UTF-8, or invalid JSON: `SnapshotError`
- incompatible version, producer, integrity, or authenticity: `SnapshotError` from the Stage 3 validator
- save writes a temporary file in the same directory and replaces the target only after a successful validation

`GraphMemory` transitions are unchanged. In-memory and file stores accept the same snapshot contract.
