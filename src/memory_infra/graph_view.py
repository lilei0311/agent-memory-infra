"""Read-only Memory Graph projection. Not a second state owner.

The projection is derived from mechanism-owned objects already held by
GraphMemory. It does not allocate ids, persist edges, or rewrite evidence.
"""

from __future__ import annotations

from memory_infra.graph import GraphMemory

NODE_KINDS = ("event", "point", "state", "thread")
EDGE_KINDS = (
    "contextual.changed_context",
    "causal.caused",
    "causal.caused_by",
    "causal.enabled",
    "causal.prevented",
    "evidential.contradicts",
    "referential.revisits",
    "referential.same_thread",
    "temporal.before",
)


def project_graph(graph: GraphMemory) -> dict:
    """Deterministic view. Ordering is kind then mechanism id."""

    nodes = []
    for point in graph.points.values():
        nodes.append(
            {
                "kind": "point",
                "id": point.point_id,
                "evidence_ref": point.evidence_ref,
                "source": point.source,
                "content": point.content,
                "candidate_status": point.candidate_status.value,
            }
        )
    for event in graph.events.values():
        nodes.append(
            {
                "kind": "event",
                "id": event.event_id,
                "evidence_ref": event.evidence_ref,
                "source": event.source,
                "observation": event.observation,
                "thread_id": event.thread_id,
            }
        )
    for thread in graph.threads.values():
        nodes.append(
            {
                "kind": "thread",
                "id": thread.thread_id,
                "member_event_ids": list(thread.member_event_ids),
                "status": thread.status,
                "parent_thread_id": thread.parent_thread_id,
            }
        )
    for state in graph.states.values():
        nodes.append(
            {
                "kind": "state",
                "id": state.target_id,
                "lifecycle_state": state.lifecycle_state.value,
                "contradiction_history": list(state.contradiction_history),
            }
        )
    edges = [
        {
            "relation_id": rel.relation_id,
            "source_id": rel.source_id,
            "target_id": rel.target_id,
            "relation_type": rel.relation_type,
            "evidence_ref": rel.evidence_ref,
            "inferred": rel.inferred,
            "created_at": rel.created_at,
        }
        for rel in graph.relations.values()
    ]
    nodes.sort(key=lambda row: (row["kind"], row["id"]))
    edges.sort(key=lambda row: (row["relation_type"], row["relation_id"]))
    return {
        "read_only": True,
        "owner": "mechanism",
        "ordering": "kind,id",
        "node_kinds": list(NODE_KINDS),
        "edge_kinds": list(EDGE_KINDS),
        "nodes": nodes,
        "edges": edges,
    }
