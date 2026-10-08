# Stage 14 read-only Visual Memory Explorer

Presentation layer over the Stage 13 `read_graph` projection. It is not a second owner of identity, lifecycle, relations, provenance, or persistence.

## Contract

Public renderer: `memory_infra.explorer.render_explorer`. Input is the projection returned by Skill API `read_graph`. The renderer does not import `memory_infra.store` and does not write.

Layout:

- status bar states the view is read-only;
- left navigation filters Threads, Events, and Contradictions without durable state;
- center SVG is the memory graph;
- right inspector lists kind, mechanism-owned id, relation metadata, and evidence/provenance.

Node kinds stay distinguishable by shape and text, not color alone: point circle, event rectangle, thread rounded rectangle, state diamond. Relation types are labeled. `evidential.contradicts` is labeled and drawn dashed while both endpoints remain. Repeated Events stay separate nodes.

Ordering follows Stage 13: nodes by kind then id, edges by relation type then relation id. Identical projection input yields identical HTML.

Presentation identity is kind-qualified. DOM anchors and positions use `(kind, id)`. Displayed `data-id` remains the mechanism-owned id. Same-id event and state nodes stay separately positioned and inspectable. Stage 13 graph identity is unchanged.

## Non-claims

This is not a production UI, Hub, Memory Policy, or graph store. Stage 14 is not marked PASS by this document.
