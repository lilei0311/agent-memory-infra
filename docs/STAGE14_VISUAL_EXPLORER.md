# Stage 14 read-only Visual Memory Explorer

Presentation layer over the Stage 13 `read_graph` projection. It is not a second owner of identity, lifecycle, relations, provenance, or persistence.

## Contract

Public renderer: `memory_infra.explorer.render_explorer`. Input is the projection returned by Skill API `read_graph`. The renderer does not import `memory_infra.store` and does not write.

Layout:

- status bar states the view is read-only;
- left navigation filters All, Threads, Events, and Contradictions, and search filters by visible id or text; both are client-side display toggles and do not write durable state; a relation inspector article is visible if and only if its relation edge is visible, and edge labels follow that same edge visibility;
- center SVG is the memory graph;
- right inspector lists kind, mechanism-owned id, relation metadata, and evidence/provenance.

Node kinds stay distinguishable by shape and text, not color alone: point circle, event rectangle, thread rounded rectangle, state diamond. Relation types are labeled. `evidential.contradicts` is labeled and drawn dashed while both endpoints remain. Repeated Events stay separate nodes.

Ordering follows Stage 13: nodes by kind then id, edges by relation type then relation id. Identical projection input yields identical HTML.

Presentation identity is kind-qualified. DOM anchors and positions use `(kind, id)`. Displayed `data-id` remains the mechanism-owned id. Same-id event and state nodes stay separately positioned and inspectable. Stage 13 graph identity is unchanged.

Edge geometry and contradiction membership use the same kind-qualified identity. Stage 13 edges carry mechanism ids only, so the projection schema does not name endpoint kinds. The explorer does not guess by first id match. Absent explicit `source_kind`/`target_kind`, it applies the mechanism creation contract: `evidential.contradicts`, causal, and `temporal.before` bind event nodes; `referential.same_thread` and `contextual.changed_context` bind thread nodes (`GraphMemory.merge` relates thread ids); `referential.revisits` binds a thread to an event, or to that thread when no event node has the target id. Contradiction marking and reveal use `(kind, id)`. A state or point that only shares an endpoint id is not marked or revealed.

## Non-claims

This is not a production UI, Hub, Memory Policy, or graph store. Stage 14 is not marked PASS by this document.

## Acceptance provenance

Code-under-test SHA is the exact implementation tree whose source and tests were executed. A later evidence-only commit may record that run, must say it is evidence-only, and must not by itself require another locked rerun solely because HEAD advanced. An evidence-only commit changes only result or provenance documentation, not source, tests, experiment parameters, or frozen artifacts. If that commit also changes implementation, it is a new code-under-test SHA and must be executed before acceptance. Stage 14 is not marked PASS by this rule.
