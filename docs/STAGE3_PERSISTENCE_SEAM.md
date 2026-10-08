# Stage 3 persistence seam

Stage 3 adds the smallest storage/service seam around the frozen V0.2 mechanism. It does not change transition semantics, Phase H config, Phase G attention, or V0.1 artifacts.

## Ownership

`GraphMemory` remains the only owner of identifier allocation, lifecycle, thread membership/status, relation endpoints/provenance, and trace records. `DurableStorePort` may only `save_snapshot` / `load_snapshot` a versioned mechanism snapshot.

`InMemoryDurableStore` is the reference implementation. It has no database, GraphRAG, vector, Graphiti, or Mem0 dependency.

## Snapshot contract

Version: `1`. Producer: `mechanism`.

Required fields: `version`, `producer`, `config`, `counters`, `points`, `events`, `threads`, `relations`, `states`, `retrievals`, `contexts`, `attention`, `trace`, `integrity`, `authenticity`.

`integrity` is the sha256 of the canonical JSON body without `integrity` and `authenticity`. It is a public checksum. Recomputing it does not prove authorship.

`authenticity` is an HMAC-SHA256 over that same body. The key is created per mechanism instance with `secrets.token_bytes`. It is not written into the snapshot, not embedded in source, and not stored as an attribute of `MemoryService`, `InMemoryDurableStore`, or `GraphMemory`. The documented public API does not return it. A caller who has only the documented service/store methods and a serialized snapshot cannot obtain the key or authorize a rewrite by recomputing `integrity`.

This is not a claim against a caller who inspects process memory or private module tables. Checksum integrity and mechanism authorship are different guarantees. Plain SHA-256 does not provide authorship.

Unknown fields and explicit ownership fields (`caller_lifecycle`, `rewrite_lifecycle`, `assign_ids`, `overwrite`, `delete`) are rejected. A version other than `1` is rejected.

Restore installs the validated copy. It does not replay transitions and does not allocate new ids.

## Service facade

`MemoryService` wraps `MemoryAdapter` for `save`, `load`, and a narrow `request` boundary (`observe`, `signal`, `retrieve`, `read_lifecycle`, `read_event`, `read_relations`, `inspect_trace`). Requests still cannot set mechanism-owned fields.

## Next boundary, not implemented

A later stage may bind this port to an external durable backend. That work is not started here. It must keep snapshot validation in front of restore and must not become a second owner of lifecycle, thread, or relation semantics.
