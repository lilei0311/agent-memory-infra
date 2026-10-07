# Attention Dynamics

## Purpose

Attention is the runtime control layer that decides which existing memory neighborhoods receive the active context budget.

It is distinct from memory existence and memory lifecycle.

```
Memory Graph
    ↓
Memory Dynamics
    ↓
Attention State
    ↓
Retrieval Policy
    ↓
Context Assembly
    ↓
Agent
    ↓
new experience
```

## 1. Core separation

- **Memory State:** what exists and its dynamic condition.
- **Attention State:** what should be active now.
- **Retrieval Policy:** which evidence to retrieve under that attention allocation.
- **Context:** the concrete bounded set delivered to the Agent.

The LLM can supply signals, but the mechanism layer owns the resulting state.

## 2. Attention State

Represent attention as a distribution over active Threads/Blocks:

`A = {thread_1: 0.72, thread_2: 0.16, thread_3: 0.07, ...}`

Also record:
- current anchor;
- mode;
- active set;
- budget allocation;
- transition reason;
- timestamp;
- source signals.

No exact threshold or equation is frozen in V0.2.

## 3. Focus Mode

Enter or remain in Focus Mode when recent turns show coherent continuity.

Signals:
- low semantic distance between adjacent turns;
- references to the current Thread;
- unresolved goal continuity;
- repeated work on the same Event/Thread;
- low topic-switch rate.

Effects:
1. increase current-thread activation;
2. increase nearby graph-neighborhood budget;
3. reduce competing-thread budget;
4. retain unrelated memories outside active context;
5. restore prior activation when returning to a thread.

The reduction is an attention decision, not deletion or memory weakening.

## 4. Divergent / Brainstorm Mode

Use Divergent Mode when the interaction contains multiple active topics or explicit idea-generation signals.

Signals:
- rapid topic switching;
- multiple unresolved goals;
- explicit question generation/brainstorm cues;
- several semantically related but distinct active Threads.

Effects:
1. preserve multiple active anchors;
2. retrieve from several graph neighborhoods;
3. increase diversity budget;
4. allow controlled cross-thread associations;
5. prevent one thread from monopolizing context.

The target is controlled collision, not maximal retrieval.

## 5. Automatic transitions

Initial transition model:

```
UNFOCUSED
   ├─ continuity ↑ → FOCUS
   ├─ divergence ↑ → DIVERGENT
   └─ weak signal → UNFOCUSED

FOCUS
   ├─ continuity persists → FOCUS
   ├─ strong divergence → DIVERGENT
   └─ topic changes → re-anchor

DIVERGENT
   ├─ one thread becomes dominant → FOCUS
   ├─ divergence persists → DIVERGENT
   └─ weak signal → UNFOCUSED
```

These transitions are deterministic policy hypotheses for the simulator, not final learned equations.

## 6. Thread switching

When the conversation returns to a prior Thread:
1. detect reference/semantic continuity;
2. reactivate that Thread's prior attention state;
3. preserve relevant neighboring context;
4. do not reconstruct the Thread from scratch;
5. record the switch as an attention event.

A thread can be active without being the dominant anchor.

## 7. Controlled cross-thread collision

Divergence should not mean retrieving everything.

The simulator should enforce:
- maximum active-thread count;
- per-thread minimum/maximum budget;
- diversity floor;
- relevance floor;
- provenance for every retrieved item.

These are experimental controls; values should be locked before each experiment rather than tuned after seeing results.

## 8. Context pollution test

A key experiment should compare:
- no attention control;
- focus-only;
- divergent-only;
- combined automatic attention.

Measure:
- target-thread retrieval precision;
- irrelevant-context ratio;
- cross-thread contamination;
- task success;
- recovery after topic switch;
- diversity/novelty in brainstorming;
- context budget utilization.

Use identical event streams and candidate pools across variants.

## 9. Human-inspired interpretation

The design is inspired by selective attention, event segmentation, memory search, retrieval effects and memory-linking research.

It does not claim that an Agent implements a biological attention system.

The engineering hypothesis is narrower:

> A mechanism-controlled allocation of memory activation can improve context quality by suppressing irrelevant neighborhoods during focused work while preserving controlled cross-thread access during divergent reasoning.
