# Stage 3 persistence seam

Stage 3 adds the smallest storage/service seam around the frozen V0.2 mechanism. It does not change transition semantics, Phase H config, Phase G attention, or V0.1 artifacts.

## Ownership

`GraphMemory` remains the only owner of identifier allocation, lifecycle, thread membership/status, relation endpoints/provenance, and trace records. `DurableStorePort` may only `save_snapshot` / `load_snapshot` a versioned mechanism snapshot.

`InMemoryDurableStore` is the reference implementation. It has no database, GraphRAG, vector, Graphiti, or Mem0 dependency.

## Snapshot contract

Version: `1`. Producer: `mechanism`.

Required fields: `version`, `producer`, `config`, `counters`, `points`, `events`, `threads`, `relations`, `states`, `retrievals`, `contexts`, `attention`, `trace`, `integrity`.

`integrity` is the sha256 of the canonical JSON body without the integrity field. Load and save recompute it. A caller-edited lifecycle, thread, relation, id, or trace field fails integrity and is rejected. Unknown fields and explicit ownership fields (`caller_lifecycle`, `rewrite_lifecycle`, `assign_ids`, `overwrite`, `delete`) are rejected. A version other than `1` is rejected.

Restore installs the validated copy. It does not replay transitions and does not allocate new ids.

## Service facade

`MemoryService` wraps `MemoryAdapter` for `save`, `load`, and a narrow `request` boundary (`observe`, `signal`, `retrieve`, `read_lifecycle`, `read_event`, `read_relations`, `inspect_trace`). Requests still cannot set mechanism-owned fields.

## Next boundary, not implemented

A later stage may bind this port to an external durable backend. That work is not started here. It must keep snapshot validation in front of restore and must not become a second owner of lifecycle, thread, or relation semantics.
