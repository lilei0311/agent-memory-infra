# Product Architecture: Agent Memory Skill and Memory Hub

## Purpose

The project has two related but independently installable product directions:

1. **Agent Memory Skill** — a memory-management capability installed inside a single Agent/Harness.
2. **Agent Memory Hub** — a standalone application that discovers and aggregates memories from multiple Agents/Harnesses.

They share a common memory model and public integration boundary, but they are not required to be installed together.

The first product is the current priority. The second is a later product track.

---

## Product A — Agent Memory Skill

### Goal

Help one Agent manage its own memory safely and intelligently.

```text
Agent / Harness
      |
      v
+----------------------+
| Agent Memory Skill   |
+----------+-----------+
           |
           +--> Discovery
           +--> Historical Memory Structuring
           +--> Event / Thread / Relation / Evidence
           +--> Memory Graph
           +--> Memory Policy
                 +--> Write
                 +--> Retrieve
                 +--> Retain
                 +--> Forget
                 +--> Abstract
           +--> Outcome / Feedback
                       |
                       v
                 Policy Learning
```

### Historical-memory upgrade

Discovery is not itself migration.

```text
Existing Agent Memory
        |
        v
Discovery
        |
        v
Explicit / controlled import or structuring
        |
        v
New Memory Structure
        |
        +--> Event Instance
        +--> Event Thread
        +--> Relations
        +--> Evidence
        +--> Context
        +--> Dynamic State
        |
        v
Memory Graph
```

Existing memory remains caller-owned unless an explicit integration/import operation is invoked. Discovery must not silently rewrite or migrate user memory.

### Memory Graph

The graph is a representation of the project's memory semantics, not a requirement to adopt a particular graph database.

Core graph objects include:
- Event Instance
- Event Thread
- Relation
- Evidence
- Context
- Dynamic State
- Abstracted Knowledge

Initial relation families include:
- Temporal
- Causal
- Referential
- Evidential
- Contextual

The graph should preserve links from abstractions back to the events and evidence that support them.

### Visual Memory Explorer

A future Skill-facing UI may provide:

```text
Memory Graph
   |
   +--> Graph view
   +--> Timeline view
   +--> Relation expansion
   +--> Evidence/source trace
   +--> Memory state
   +--> Retrieval/use history
```

Visualization is an inspection and management surface. It is not the policy itself.

---

## Product B — Agent Memory Hub

### Goal

Provide a standalone application for users who have multiple Agents/Harnesses.

The Hub is not installed inside every Agent. It operates as an application-level discovery and aggregation layer.

```text
                    +----------------------+
                    |    Agent Memory Hub  |
                    |----------------------|
                    | Agent Discovery      |
                    | Memory Discovery     |
                    | Aggregation          |
                    | Unified Search       |
                    | Graph / Visualization|
                    +----------+-----------+
                               |
             +-----------------+-----------------+
             |                 |                 |
             v                 v                 v
         Harness A         Harness B         Harness C
             |                 |                 |
          Memory A          Memory B          Memory C
```

### Initial Hub responsibilities

1. Discover Agents/Harnesses in the user's environment.
2. Discover their available memory sources.
3. Identify which sources already expose the Agent Memory Skill/public memory boundary.
4. Aggregate metadata and, where explicitly permitted, structured memory views.
5. Provide a unified search and visual view across multiple memory sources.
6. Preserve provenance: which Agent/source produced each memory object.
7. Detect relationships and overlaps without silently rewriting the source memories.

### Hub does not initially require every Agent to install the Skill

```text
Hub
 |
 +--> Agent A ---- Memory Skill ---- Structured Memory
 |
 +--> Agent B ---- Legacy Memory
 |
 +--> Agent C ---- Other Memory System
```

The Hub should be able to discover and represent heterogeneous sources before requiring uniform adoption.

---

## Product relationship

The two products are complementary, but independently useful.

### Single-Agent-only user

```text
Agent A
  |
  +--> Agent Memory Skill
          |
          +--> own memory
          +--> own graph
          +--> own policy
```

No Hub is necessary.

### Multi-Agent user

```text
              Agent Memory Hub
                     |
          +----------+----------+
          |          |          |
          v          v          v
       Agent A    Agent B    Agent C
          |
    Memory Skill
```

The user may install the Skill first and add the Hub later.

The Hub can recognize and interoperate with an already-installed Skill through the shared public boundary.

---

## Aggregation before bridging

The multi-Agent product should not begin as a shared-memory system.

```text
Agent Discovery
      |
      v
Memory Discovery
      |
      v
Memory Aggregation
      |
      v
Unified Search / Unified Graph
      |
      v
Cross-Agent Relationship Discovery
      |
      v
Memory Bridge
      |
      v
Controlled Cross-Agent Sharing
```

**Aggregation** means the Hub can inspect and organize multiple memory sources while preserving provenance and ownership.

**Bridging** means one Agent can intentionally use or receive memory from another Agent under explicit policy and access rules.

Therefore Memory Bridge is a later capability, not a prerequisite for the first Hub release.

---

## Shared foundation

Both products should rely on a common, agent-agnostic memory model and public boundary.

```text
              Common Memory Contract
                       |
       +---------------+---------------+
       |                               |
       v                               v
Agent Memory Skill              Agent Memory Hub
       |                               |
 Single-Agent                    Multi-Agent
 memory management              discovery/aggregation
       |                               |
       +---------------+---------------+
                       |
                       v
        Event / Thread / Relation
        Evidence / Context / State
```

The common foundation must remain storage-agnostic. A source may be Markdown, JSON, SQL, vector storage, a graph database, or an Agent-specific memory system.

The common foundation does not imply that all products must use the same storage implementation.

---

## Product boundaries

### Agent Memory Skill owns

- Single-Agent memory semantics
- Memory structure
- Memory lifecycle
- Memory policy
- Trace/evidence needed for policy evaluation
- Agent-local memory graph
- Agent-local visualization interfaces

### Agent Memory Hub owns

- Agent/Harness discovery
- Memory-source discovery
- Cross-source aggregation
- Unified visualization
- Cross-Agent search
- Provenance across sources
- Later: controlled Memory Bridge

### Neither product should initially own

- A mandatory universal database
- Silent memory migration
- Uncontrolled cross-Agent memory sharing
- A specific Agent/Harness implementation
- A mandatory graph database technology

---

## Development priority

The current repository remains focused on **Product A — Agent Memory Skill**.

The immediate sequence is:

```text
Stage 10
Discovery of existing memory
        |
        v
Stage 11
Minimal discoverable Skill entrypoint
        |
        v
Future
Explicit historical-memory structuring
        |
        v
Future
Memory Graph + visual inspection
        |
        v
Future
Memory Policy + feedback learning
        |
        v
Product A complete enough for real Agent use
```

The **Agent Memory Hub** is a later product track:

```text
Product A maturity
        |
        v
Shared public memory boundary
        |
        v
Product B
Agent Discovery
        |
        v
Memory Aggregation
        |
        v
Unified Graph / Search
        |
        v
Memory Bridge
```

The Hub should not be pulled into the current Stage 11 implementation.

---

## Design principle

The product boundary can be summarized as:

> **Agent Memory Skill makes one Agent's memory better.**
>
> **Agent Memory Hub makes many Agents' memories visible and connectable.**

The two products can be installed independently, while the common memory contract allows them to interoperate when both are present.