# Biological Memory Research Map

## Purpose
This document maps established biological/cognitive findings to candidate computational mechanisms for Agent Memory. It is explicitly a design translation, not a claim of biological equivalence.

## 1. Event segmentation
Human experience is continuous, but memory is organized into discrete events. Event segmentation research emphasizes event boundaries: changes in external conditions, goals, affective state or motivational state can signal a boundary and update the current event model.

Computational implication:
- do not create one memory object per message;
- detect candidate event boundaries;
- preserve the event context around a boundary;
- allow later evidence to revise the event/thread association.

Candidate variables:
- prediction/context change;
- goal change;
- participant change;
- topic change;
- action/outcome transition;
- temporal gap;
- internal-state proxy when available.

Important caveat: event-boundary detection is not a solved formula. V0.2 should treat it as a measurable hypothesis and compare alternative segmentation rules.

## 2. Episodic structure and causal connectivity
Event cognition research supports rich internal event structure and links among events. The Event Horizon Model emphasizes segmentation into event models and the importance of causal connectivity in long-term organization.

Computational implication:
- an Event should preserve context, action/observation, outcome and evidence;
- Event Threads should preserve multiple occurrences rather than overwrite them;
- causal relations should be first-class when supported by evidence;
- semantic similarity alone should not create causal edges.

## 3. Consolidation
After acquisition, memories undergo processes that contribute to longer-term stabilization. For engineering purposes, the useful abstraction is not a literal brain-state simulation but a transition from a newly encoded, more labile representation toward a more stable representation.

Computational hypothesis:
FORMING → LABILE/NEW → STABLE

Potential measurable variables:
- elapsed time;
- successful retrievals;
- reinforcement/confirmation count;
- contextual diversity;
- contradiction count;
- later task usefulness.

Do not equate these variables one-to-one with biological consolidation mechanisms.

## 4. Retrieval and reconsolidation
Retrieval is not necessarily a read-only operation. Research on reconsolidation proposes that reactivated memories can, under some conditions, become labile and then undergo restabilization or updating.

Computational implication:
retrieval → REACTIVATED → RECONSOLIDATING

During reconsolidation, new evidence can:
- confirm the old memory;
- revise it;
- contradict it;
- leave it unchanged.

This supports storing RetrievalEvent as part of the history rather than treating retrieval as a pure database read.

## 5. Forgetting and accessibility
Forgetting should not be modeled as immediate deletion. A memory may become less accessible while evidence of its existence remains in the history.

Computational distinction:
- existence/evidence;
- accessibility;
- confidence/applicability;
- task usefulness.

Candidate transitions:
STABLE → DORMANT
DORMANT → REACTIVATED
WEAKENED → INACCESSIBLE

Retrieval practice research also shows that successful retrieval can improve later retention, supporting the hypothesis that retrieval itself can alter future accessibility.

## 6. Prediction error and salience
Research on prediction error, novelty and reconsolidation suggests that unexpected outcomes can be important for memory modification. This is particularly relevant to our earlier observation that strong negative outcomes can create strong learning signals.

Computational implication:
learning impact should not equal outcome sign.

Instead consider separate dimensions:
- outcome sign;
- outcome magnitude;
- prediction error;
- salience/importance;
- later confirmation;
- later contradiction.

A severe failure can therefore create a strong memory without being a positive experience.

## 7. What this means for our architecture
The biological review supports the following decomposition:

Experience Stream
→ Event Segmentation
→ Event Instance
→ Event Thread / Relations
→ Initial Encoding
→ Consolidation
→ Retrieval / Reactivation
→ Reconsolidation / Update
→ Accessibility Dynamics
→ Future Retrieval

Policy is intentionally above this mechanism layer:
Memory Dynamics → Memory Policy → Agent behavior.

## 8. What should NOT be hard-coded yet
Do not hard-code:
- one universal forgetting curve;
- a single memory-strength scalar;
- a fixed biological time constant;
- prediction error as the sole explanation for salience;
- literal neural states;
- the assumption that every retrieval causes reconsolidation;
- the assumption that every repeated mention should strengthen a memory.

These should become controlled experimental hypotheses.

## 9. First computational model to test
The first V0.2 model should remain structurally simple:

1. Event objects preserve occurrence evidence.
2. Threads link repeated or related events.
3. Relations preserve temporal, causal, referential, evidential and contextual structure.
4. Dynamic state stores accessibility, confidence, evidence history, context fit and reinforcement/contradiction history separately.
5. Retrieval creates an explicit RetrievalEvent.
6. State transitions are explicit and inspectable.
7. A later retrieval policy derives a score from the state rather than replacing the state with one scalar.

Only after this passes controlled simulation should we introduce more detailed decay, salience, prediction-error or reconsolidation equations.

## References
- Zacks, J. M. (2020), Event Perception and Memory: https://www.annualreviews.org/content/journals/10.1146/annurev-psych-010419-051101
- DuBrow, S. (2024), Events and Boundaries: https://academic.oup.com/edited-volume/57928/chapter-abstract/475474913
- Radvansky & Zacks (2017), Event Boundaries in Memory and Cognition: https://pmc.ncbi.nlm.nih.gov/articles/PMC5734104/
- Nader & Hardt (2009), A single standard for memory: the case for reconsolidation: https://www.nature.com/articles/nrn2590
- McDermott (2021), Practicing Retrieval Facilitates Learning: https://www.annualreviews.org/content/journals/10.1146/annurev-psych-010419-051019
- Review on prediction error, novelty and reconsolidation (2026): https://www.sciencedirect.com/science/article/pii/S0306452225011972