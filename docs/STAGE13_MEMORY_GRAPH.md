# Stage 13 read-only Memory Graph projection

Smallest public query seam over mechanism-owned V0.2 objects. The graph is a view. It is not a second owner of identity, lifecycle, relations, provenance, or persistence.

## Operation

Public entry: Skill API `read_graph`. Payload must be empty. The seam binds `caller_id` and returns the current projection. It does not write.

Node kinds already evidence-backed in the mechanism: `point`, `event`, `thread`, `state`.

Edge kinds already implemented as `Relation.relation_type`:

- `temporal.before`
- `causal.caused`, `causal.caused_by`, `causal.enabled`, `causal.prevented`
- `referential.same_thread`, `referential.revisits`
- `evidential.contradicts`
- `contextual.changed_context`

Ids are the mechanism-owned ids. Evidence stays on `evidence_ref`. Repeated Events stay separate nodes. Contradictions stay as an `evidential.contradicts` edge plus both event nodes and both evidence refs. Caller notes are not graph fields.

## Ordering

Nodes sort by `kind`, then `id`. Edges sort by `relation_type`, then `relation_id`. The same mechanism state yields the same projection. Membership lists keep mechanism order and are not collapsed.

## Ownership

Callers cannot supply `nodes`, `edges`, `relations`, `relation_id`, `event_id`, `point_id`, `thread_id`, or other mechanism-owned fields on this read. Those requests are rejected. The projection does not allocate ids.

## Non-claims

This is not a visual explorer, Hub, GraphRAG store, or Memory Policy. Stage 13 is not marked PASS by this document.
