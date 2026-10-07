# Agent Memory Infrastructure
> A research infrastructure for building adaptive memory systems for AI agents.
## Overview
Most Agent memory systems focus on **storing** and **retrieving** information.
This project focuses on a different question:
> **Can an Agent learn from its past experience to decide what should be remembered, retrieved, retained, or forgotten?**
The goal is to build a lightweight, agent-agnostic **Memory Policy Layer** that can work across different Agents and different memory storage implementations.
The memory storage does not belong to this project.
The project focuses on the **policy and feedback loop above the storage layer**.
---
## Core Hypothesis
Traditional memory retrieval often looks like:
```text
User Task
   ↓
Semantic Search
   ↓
Top-K Memories
   ↓
Agent

We propose an adaptive approach:

                         ┌───────────────┐
                         │ Historical    │
                         │ Experience    │
                         └───────┬───────┘
                                 ↓
Task → Candidate Memories → Memory Policy
                                 ↓
                              Top-K
                                 ↓
                               Agent
                                 ↓
                              Outcome
                                 ↓
                              Trace
                                 ↓
                         Policy Update
                                 │
                                 └──────────→ next task

The system continuously learns which memories are actually useful.

────────

Design Principles

1. Storage-Agnostic

Agents may store memories as:

* Markdown
* JSON
* SQL
* Vector databases
* Knowledge graphs
* Agent-specific memory systems
* Other custom formats

The Memory Policy Layer should not depend on any particular storage technology.

────────

2. Agent-Agnostic

The same memory policy should be usable by different Agents.

The Agent only needs to provide a minimal adapter interface.

Agent
  ↓
Memory Adapter
  ↓
Memory Policy
  ↓
Memory Store

This allows the system to become a reusable Skill rather than a memory implementation tied to one Agent.

────────

3. Feedback Driven

A memory should not become important simply because it is semantically similar to the current task.

Its historical usefulness should also matter.

For example:

Memory A
similarity = 0.82
historical usefulness = high
Memory B
similarity = 0.90
historical usefulness = low

The policy may decide that Memory A is more valuable.

────────

4. Outcome-Oriented

The system should evaluate memory based on what happened after it was retrieved.

Possible signals include:

* task success
* user feedback
* correction rate
* execution efficiency
* repeated reuse
* whether the Agent ignored the memory
* whether the memory caused an incorrect decision

The goal is not simply to measure whether a memory was retrieved.

The goal is to measure whether the memory helped.

────────

Memory Lifecycle

The long-term goal is to learn four related policies:

                 ┌──────────────┐
                 │ Memory Policy│
                 └──────┬───────┘
                        │
          ┌─────────────┼─────────────┐
          ↓             ↓             ↓
       Write        Retrieve       Retain
          │             │             │
          └─────────────┼────────────┘
                        ↓
                     Forget

Write Policy

Should this information become a memory?

Retrieval Policy

Should this memory be retrieved for the current task?

Retention Policy

Should this memory remain important over time?

Forgetting Policy

Should this memory be downgraded, archived, or removed?

────────

V0.1

The first version deliberately avoids:

* Large Language Models
* Vector databases
* Complex reinforcement learning
* Distributed infrastructure

Instead, V0.1 uses a simple and explainable policy.

The first experiment compares:

Baseline

retrieval_score = semantic_relevance

with:

Adaptive Policy

retrieval_score =
    relevance
    + historical_utility
    + reliability
    + context_fit

The weights are updated using historical task outcomes.

────────

Trace

Every memory interaction should generate a lightweight trace.

Example:

{
  "task_id": "task_001",
  "memory_id": "memory_123",
  "retrieved": true,
  "used": true,
  "task_success": true,
  "user_feedback": 1
}

The trace should describe the interaction and outcome, rather than requiring storage of the user’s raw conversation.

This allows the system to evaluate whether the memory policy is actually improving performance.

────────

Evaluation

The primary research question is:

Does historical feedback improve memory retrieval compared with relevance-only retrieval?

Initial metrics may include:

* Task success rate
* Memory usefulness
* Retrieval precision
* Retrieval waste
* User correction rate
* Repeat usefulness
* Policy convergence

The first experiment should run controlled simulations before connecting to real Agents.

────────

Agent Skill

Once the Memory Policy is validated, it will be packaged as an Agent Skill.

The Skill will provide Agents with a standard method to:

1. Inspect available memory
2. Select relevant memories
3. Record memory usage
4. Report task outcome
5. Update memory utility

Different Agents can therefore use different memory stores while sharing the same policy methodology.

              Memory Policy Skill
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
     Agent A         Agent B        Agent C
        │              │              │
    Store A         Store B        Store C

────────

Privacy

The project should not require users to upload or expose their raw memories.

Where possible, the evaluation layer should operate on:

* memory identifiers
* abstract features
* retrieval events
* outcome signals
* aggregated statistics

The actual memory content should remain inside the user’s Agent environment.

────────

Research Roadmap

Phase 1 — Policy Prototype

* [ ]	Define memory protocol
* [ ]	Define adapter interface
* [ ]	Implement baseline retrieval
* [ ]	Implement adaptive scoring
* [ ]	Implement trace format
* [ ]	Implement online policy update
* [ ]	Build simulation

Phase 2 — Evaluation

* [ ]	Compare baseline vs adaptive policy
* [ ]	Run controlled experiments
* [ ]	Analyze learning curves
* [ ]	Identify useful feedback signals
* [ ]	Test different memory distributions

Phase 3 — Agent Skill

* [ ]	Define Skill specification
* [ ]	Build storage adapters
* [ ]	Package reusable Skill
* [ ]	Test with multiple Agents
* [ ]	Collect anonymous evaluation signals

Phase 4 — Real-World Learning

* [ ]	Real Agent integration
* [ ]	User feedback loop
* [ ]	Policy versioning
* [ ]	Cross-Agent evaluation
* [ ]	Continuous policy improvement

────────

Long-Term Vision

The long-term goal is not to build another vector database or another memory store.

It is to build a learning layer for Agent memory.

                 Agent Memory Infrastructure
                         ┌─────────┐
                         │ Agents  │
                         └────┬────┘
                              ↓
                     ┌─────────────────┐
                     │ Memory Policy  │
                     │     Layer      │
                     └───────┬─────────┘
                             ↓
                  ┌─────────────────────┐
                  │ Memory Adapter API │
                  └─────────┬──────────┘
                            ↓
              ┌─────────────┼─────────────┐
              ↓             ↓             ↓
          Markdown        Vector         SQL
          Memory          Store         Store

The central idea is simple:

Memory should not only store experience.
Memory should learn from experience.

────────

Status

Research / Experimental

This project is currently focused on validating the core hypothesis before building a production-grade implementation.


## Stage 1 Design

The current implementation is deliberately focused on validating the Memory Policy Layer before any public Skill or external-user feedback loop.

- [Architecture](docs/ARCHITECTURE.md)
- [Protocols](docs/PROTOCOLS.md)
- [Experiment Plan](docs/EXPERIMENT_PLAN.md)
- [Roadmap](docs/ROADMAP.md)

Stage 1 uses controlled simulation and reproducible experiments. External adoption and anonymous telemetry begin only after the Stage 1 exit gate is passed.
