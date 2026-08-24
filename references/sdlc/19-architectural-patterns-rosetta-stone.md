# Architectural patterns: a Rosetta Stone

Source: **The Agentic SDLC Handbook**, Daniel Meppiel, Part III (For
Practitioners), Ch. 19 --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch19-architectural-patterns-rosetta-stone.html.
See [index.md](index.md) for why this lives here rather than in
`references/harnesses/`.

Thesis: agentic runtimes contain recurring structural problems --
composition, dispatch, isolation, supervision, fan-out, recovery --
with recognisable solutions, many of which map to classical
Gang-of-Four patterns or distributed-systems literature. "Naming
them -- and naming the analogue -- gives architects a vocabulary to
reason at the system level instead of at the file level." Each catalogue
entry is rated for how exact its classical mapping is: **precise**
(the analogy is exact), **partial** (the analogy holds for most of the
structure but a named part does not map), or **weak/none** (no clean
classical analogue -- the closest distributed-systems shape is given
instead).

## The four-layer substrate

The chapter decomposes an agentic runtime into four layers, each
depending on the one below it as substrate:

- **Foundation layer** -- "The model and the harness that hosts it.
  The model is probabilistic; the harness is deterministic. The seam
  between them is non-negotiable (Ch. 16)." Mostly outside an
  architect's control (vendor decisions), but the boundary it offers
  (tool calls, file reads, capability tokens) is what every higher
  layer depends on.
- **Assembly layer** -- "How content reaches the model. The agent
  source code convention (AGENTS.md, SKILL.md, instruction files) and
  the binding modes the harness applies (eager preload, lazy
  on-demand, dispatcher-mediated) determine what arrives in the
  context window before any reasoning starts." This is where the load
  lifecycle (Ch. 14) lives.
- **Composition layer** -- "How content is structured for reuse.
  Primitives, skills, bundles, dependency edges, override mechanisms.
  This is where most of the architectural work happens -- and where
  the GoF catalogue maps cleanest, because composition has been a
  solved problem in software since the 1990s."
- **Execution layer** -- "How work is dispatched, parallelised,
  persisted across boundaries, and re-entered on a trigger. Threading
  topology, plan persistence, client integration." Multi-agent
  orchestration (Ch. 17) lives here, along with the patterns
  architects argue about most in public: Panel, Wave, Scatter-Gather.

**Cost is a cross-cutting property, not a fifth layer**: "Token
economics does not add a layer; it is a property that cuts across
three existing ones. The model selected at the Foundation layer is the
cost function. The prefix laid out at the Assembly layer decides how
much of each turn is cacheable. The dispatch chosen at the Execution
layer governs how many calls happen and on which model class."

## Composition layer

| Agentic name | Classical analogue (rigour) | Intent | When to apply | Consequences |
|---|---|---|---|---|
| **Skill** | Module / Facade -- precise | Bundle a capability under a single named entrypoint, hiding assets, dependencies, and internal structure | Whenever a capability is reusable, dispatchable by description, and ships with content beyond the instruction body | The skill is the stable reuse unit; its description is its API -- rewording it is a breaking change |
| **Bundle** | Composite -- precise | Treat aggregates of primitives uniformly with leaf primitives | When a primitive contains other primitives (a skill depending on a sub-skill, an agent containing skills) | Recursive distribution; the transitive closure becomes the cost unit |
| **Primitive** | Strategy -- partial | Make a unit of behaviour interchangeable -- an agent, a skill, an instruction, a chatmode each implement the same dispatch contract | When the runtime must select among interchangeable units at load or dispatch time | Does not fully map: Strategy is a pure algorithm; primitives carry state and content |
| **Dependency** | Decorator -- partial / Package Reference (Maven, npm) -- precise | Compose capabilities by declaring a directed edge from one module to another, resolved by a package system | When the same content is needed by 3+ consumers, evolves on its own cadence, has a different owner, or is worth pinning | Crosses a distribution boundary: versioning, transitive closure, conflict resolution; does not map to Decorator |
| **Override** | Template Method -- precise | A base module defines an invariant skeleton; a consuming module replaces named slots without rewriting the skeleton | When a downstream user needs to specialise one section of an upstream primitive without forking it | The base module's slot names become a public contract; renaming a slot is a breaking change |

## Assembly layer

| Agentic name | Classical analogue (rigour) | Intent | When to apply | Consequences |
|---|---|---|---|---|
| **Cache-Aware Prefix** | Cache-Aside -- precise / Append-Only Log -- partial | Lay out the context window so stable content (system preamble, tool definitions, scope-loaded rules, agent source) sits at the prefix head and volatile content (the current turn, an in-flight diff, fresh tool results) sits at the suffix tail, making the prefix cacheable across turns at a fraction of full-input cost | Whenever the harness exposes prompt-prefix caching as a billing unit (true of every major foundation model today) and the session runs more than a turn or two against the same primitive set | Anything mutable placed in the head (timestamps, ephemeral IDs, conversation scrollback) is a cache invalidator that re-prices the whole prefix at full input; the layout becomes a load-bearing public contract |

## Dispatch and orchestration layer

| Agentic name | Classical analogue (rigour) | Intent | When to apply | Consequences |
|---|---|---|---|---|
| **Panel** | Mediator -- partial / Scatter-Gather -- precise | Run N specialised lenses in parallel against the same artifact, then synthesise their verdicts into a single decision | When a decision benefits from three or more independent lenses and the lenses do not share state during evaluation | The synthesis step *is* the decision -- without it the user reads N reports instead of one; does not map to Chain of Responsibility |
| **Wave** | Pipes-and-Filters -- precise / Pipeline (CI) | Execute a topologically-sorted DAG of tasks one wave at a time, gating between waves | When the task DAG is non-trivial and drift between waves is expensive enough to want a localisable failure | Each wave's output gates the next wave's assumptions; a failed gate replans from the failed wave, not from the start |
| **Scatter-Gather** | Scatter-Gather -- precise (origin term) | Decompose a task into independent parallel sub-tasks; each runs in its own thread; results merge at a gather step | When sub-tasks are genuinely independent and merge cleanly | Concurrency cost; one writer per sink -- parallel writers plus shared state is almost always a smell |
| **Threading** | Command + Memento -- partial | Dispatch a unit of work as a serialisable invocation (Command) into a fresh context window whose state is captured by a durable plan artifact (Memento) | When a sub-task needs cold context -- an independent attention budget, no inheritance of the parent's reasoning trace | Cold context costs a re-load; serialisation forces the architect to make the hand-off packet explicit; does not map cleanly to either GoF pattern alone |
| **Subagent Spawn** | Active Object -- precise | Each invocation creates an independent thread of control with its own message queue and lifecycle | When the parent must continue while sub-work runs, or the sub-work must be isolated from the parent's context window | Spawn cost; cross-thread state must travel via durable artifacts, not shared memory |
| **Model Router** | Strategy -- partial / Content-Based Router -- precise | Classify a task's complexity in a cheap preliminary turn and dispatch the substantive work to a right-sized model, rather than running every task on one class | When the workload mixes tasks of materially different complexity (deep planning vs. lint vs. classification) and the foundation layer exposes two or more model classes with a 5x+ cost spread | The classification turn is itself a cost and latency tax; routing must be cache-aware (a mid-trajectory model switch is a cache invalidator and pays full input on the prefix next turn); routing rules are a public contract whose drift produces silent regressions |
| **Gradient Workflow** | Tiered Architecture -- partial / Stratified Pipeline -- weak | Compose a workflow whose stages run on differently sized model classes -- a heavy planner, a mid-tier implementer in fan-out, a lightweight reviewer or triage layer -- rather than one class throughout | When the workflow has a small number of consequential decisions (heavy class), many mechanical edits (mid-tier), and high-volume filtering or classification (lightweight), and the foundation layer offers all three | Each tier boundary is a model switch and so a cache invalidator within the trajectory; the topology must place switches at thread or wave boundaries to avoid paying full input on a warm prefix; composes with Panel (mid-tier lenses, heavy synthesiser) and Wave (heavy planner stage, mid-tier execution) |

Two clarifications the chapter is explicit about:

- **Panel is not Chain of Responsibility.** Panel runs handlers in
  parallel and synthesises; its classical reach is Mediator and its
  distributed-systems reach is Scatter-Gather. "A Panel without a
  synthesizer is not a chain -- it is the **Panel-without-synthesis**
  anti-pattern."
- **Model Router and Gradient Workflow are different axes.** Model
  Router decides *per task, at dispatch time* (classifies the work and
  picks a model). Gradient Workflow decides *per stage, at design
  time* (the topology fixes which tier each stage runs on before any
  task arrives). They compose but are not the same decision.
- **Wave adds durability and determinism to Pipes-and-Filters.** Wave
  is Pipes-and-Filters applied to LLM stages, with the addition that
  each filter's output is *durable* (a plan artifact) and each gate is
  a *deterministic* check, not a model call -- that durability is what
  lets a Gradient Workflow switch model classes at a wave boundary
  without paying a cache penalty.

## Boundary layer

| Agentic name | Classical analogue (rigour) | Intent | When to apply | Consequences |
|---|---|---|---|---|
| **Supervised Execution** | Proxy + Guard -- partial / Capability Security -- precise (strong form) | Plan in the model; execute in the substrate; verify with another deterministic check; the model never holds write capability for irreversible effects | When the work names a system of record (repo, database, cluster) and a consequential action against it | The strong form (substrate-enforced) requires a client that exposes capability-based security; the weak form (prose-enforced) is a fallback; the strong form is *not* a Proxy -- the model genuinely cannot externalise, not merely mediated by one |
| **Schema-Checked Transformer** | Adapter -- precise | Convert the model's freeform output into structured form by gating it through a schema check at the boundary | At every model-to-substrate hand-off where the substrate expects typed input | The schema becomes the public contract of the boundary; a schema mismatch at the gate is recoverable -- one past the gate is a runtime fault |
| **Plan-Write-Then-Reload** | Memento -- weak / Snapshot -- closer | Persist the plan as a durable artifact, then deliberately reload it in a fresh context to defeat attention drift on long sessions | When the work is multi-step, multi-file, or spawn-bound, and goal drift is a real risk | The plan artifact becomes the source of truth; the model's in-context recall is treated as untrusted; no clean GoF analogue -- Memento captures state for restore, but here the restore is *forced* on a thread that already has state, specifically to overwrite attention |
| **Bounded-Scope Grounding** | Bounded Context -- precise (DDD origin, not GoF) | Declare what an external corpus is authoritative *for*, and refuse to import its framing into questions it does not own | Whenever an external grounding source (a spec, a vendor catalogue, competitor docs) is loaded into a session | Authority overreach is the failure mode: the corpus's vocabulary contaminates judgement on questions outside its scope; no GoF analogue -- this is a domain-modelling idea, not an OOP structural one |
| **Tool Subset** | Facade -- partial / Interface Segregation -- precise | Expose to the model only the subset of tools the current phase or sub-task actually needs, rather than the full catalogue; a substrate variant consolidates several narrow tools behind a single code-execution surface that composes them inline | When tool-definition tokens grow to dominate the prefix (a common threshold is around 20 tools loaded every turn), or when the same tools load identically across phases that need disjoint subsets | The subset becomes a phase-scoped public contract; a mid-session catalogue mutation is a cache invalidator and must be avoided once the trajectory is warm; the code-execution variant trades per-tool schema rigour for prefix compression -- the Schema-Checked Transformer moves *inside* the tool rather than at the call seam |

## Recovery and observability layer

| Agentic name | Classical analogue (rigour) | Intent | When to apply | Consequences |
|---|---|---|---|---|
| **Agent Stack Trace** | Distributed Tracing -- precise / no GoF analogue | Make the chain of dispatched skills, spawned threads, and tool calls reconstructible after the fact, the way a stack trace reconstructs a synchronous call | Whenever an agent run produces an artifact whose provenance an operator may need to audit or replay | Tracing has a cost: every dispatch and spawn must emit a trace event, paid up front; the alternative is undebuggable after the fact |
| **Lockfile** | Snapshot -- precise / Memento -- partial | Capture the resolved version of every transitive dependency at install time so the runtime closure is reproducible | Whenever a module declares external dependencies whose drift would silently change behaviour | The lockfile is a public artifact; conflicts between consumers' lockfiles surface at install time, not runtime; Memento maps only partially -- the lockfile is a memento of the dependency graph, but the "restore via originator" mechanic doesn't apply |
| **Audit Trail** | Event Sourcing -- precise | Record every consequential decision the agent made and every consequential effect it produced as an immutable, append-only sequence | Whenever the work is consequential enough that an auditor (security, compliance, a manager, a future maintainer) must reconstruct what fired, what ran, and what was written | Storage cost; query infrastructure for the trail; the discipline to keep the trail truly append-only; the trail must sit on a surface the agent cannot rewrite |

These three travel together: "Audit Trail without Agent Stack Trace
can tell *what* happened but not *why*. Lockfile without Audit Trail
can reproduce the dependency closure but not the decisions that
produced the artifact under it."

## Decision matrix

| Layer | When you have... | Reach for | Trade-off you accept | Failure mode if you skip it |
|---|---|---|---|---|
| Composition | Same content needed in 3+ consumers | Dependency | Distribution boundary; versioning; transitive closure | Duplicated leaf; drift between copies |
| Composition | One module needs to specialise one section of another | Override (Template Method) | Slot names become a public contract | Forking the upstream module |
| Composition | Capability ships with assets and a description | Skill (Module + Facade) | Description is the API; rewording is breaking | Asset leakage into the consumer's context |
| Assembly | Session runs more than a turn or two against the same primitives | Cache-Aware Prefix | Prefix layout becomes a public contract; no timestamps or mutable IDs in the head | Every turn pays full input on the entire prefix |
| Dispatch | Decision needs 3+ independent lenses | Panel | Synthesis cost; one extra orchestration thread | Single-lens bias; missed dissent |
| Dispatch | Work decomposes into ordered, gateable stages | Wave | Each stage's output must be durable; gates must be deterministic | Stage collapse (planning and implementing in one turn) |
| Dispatch | Sub-tasks are independent and parallel-safe | Scatter-Gather | One writer per sink; concurrency budget | Shared-state interlock; serialised fan-out |
| Dispatch | Sub-task needs cold context | Threading + Subagent Spawn | Re-load cost; explicit hand-off packet | Attention contamination from the parent |
| Dispatch | Mixed-complexity workload with a 5x+ cost spread across model classes | Model Router | Classification-turn cost; routing rules are a public contract | Single-class cost floor; overspend on trivial work or underpower on hard work |
| Dispatch | Workflow with stratifiable stages (planning / execution / triage) | Gradient Workflow | Tier switches must land at thread or wave boundaries to preserve cache | Flat model assignment; heavy model on cheap work |
| Boundary | Consequential action against a system of record | Supervised Execution (strong form) | Client lock-in; capability-based security wiring | Plan-and-pray; LLM-asserted side effects |
| Boundary | Freeform model output must enter a typed substrate | Schema-Checked Transformer | Schema becomes a public contract | Type errors past the gate; runtime faults |
| Boundary | Long-session goal drift | Plan-Write-Then-Reload | Plan artifact must be re-readable in a fresh thread | Drift compounds invisibly across turns |
| Boundary | External corpus loaded as grounding | Bounded-Scope Grounding | Must declare what the corpus owns | Authority overreach; vocabulary contamination |
| Boundary | Tool catalogue large enough to dominate the prefix, with disjoint per-phase usage | Tool Subset | Subset is a phase-scoped contract; mid-session mutation is a cache invalidator | Tool-definition tax compounds with turn count; prefix crowds out grounding |
| Recovery | Multi-skill, multi-thread runs whose provenance matters | Agent Stack Trace | Tracing emission cost on every dispatch | Undebuggable after the fact |
| Recovery | External dependencies whose drift changes behaviour | Lockfile | Lockfile becomes a public artifact | Non-reproducible runtime closure |
| Recovery | Consequential effects an auditor must reconstruct | Audit Trail | Storage + query infrastructure; append-only discipline | Implicit-trust outer loop; a clandestine bot |

Reviewer guidance stated explicitly: "A design that names a pattern
from column three without naming the trade-off in column four is
structurally incomplete. The trade-off is what makes the choice
deliberate rather than accidental."

## Anti-patterns named explicitly

- **Panel-without-synthesis** -- parallel lenses with nothing to
  arbitrate dissent collapse to whichever lens speaks loudest; not a
  valid Panel.
- **Stage collapse** -- planning and implementing in one turn; the
  characteristic misuse of Wave. In Genesis's own codification this is
  the **A2 PIPELINE** failure ("I will plan as I go"): planning and
  implementation happen in the same turn and the plan ends up post-hoc
  and unfalsifiable.
- **Shared-state interlock** -- the failure mode when Scatter-Gather is
  applied with multiple writers per sink.
- **Authority overreach** -- the failure mode of Bounded-Scope
  Grounding: the corpus's vocabulary contaminates judgement on
  questions outside its scope.
- **Skipping the strong form** -- choosing weak-form (prose-enforced)
  Supervised Execution on a substrate that actually offers the strong
  (substrate-enforced) form: "leaving a substrate guarantee on the
  table."
- **Cache invalidator** -- any mutable content placed in the prefix
  head (a timestamp, an ephemeral ID, a mid-session tool addition, a
  model switch) that re-prices the entire prefix at full input on the
  next turn.
- **A8 ALIGNMENT LOOP -- considered, rejected**: a pattern Genesis's own
  codification deliberately declines when creative work and goal-drift
  risk are both low.

## Vocabulary

- **Cacheable prefix**: "The stable head of the context window --
  system preamble, tool definitions, scope-loaded rules, agent
  source -- that a harness can bill at a fraction of full input on
  repeat turns."
- **Cache invalidator**: "Anything placed in that head which mutates
  per turn -- a timestamp, an ephemeral ID, a mid-session tool
  addition, a model switch -- and so re-prices the entire prefix at
  full input on the next turn."
- **Primitive**: "Make a unit of behaviour interchangeable: an agent,
  a skill, an instruction, a chatmode each implement the same dispatch
  contract."
- **Skill**: "Bundle a capability under a single named entrypoint that
  hides assets, dependencies, and internal structure from callers."
- Pattern-rigour ratings: **precise** (the analogy is exact),
  **partial** (the analogy holds for most structure but a named part
  does not map), **weak/none** (no clean classical analogue; the
  closest shape from distributed systems is given instead).

## Reconciling three layered lenses used across the handbook

The chapter is explicit that it is one of three competing layered
models the handbook uses, each suited to a different decision:

1. **The 5-layer landscape** (Chapter 4, the Agentic SDLC reference
   architecture) -- Platform -> Context & Capabilities -> Governance
   and Distribution -> Agent Harness -> SDLC phases. Decision surface:
   strategic/executive -- where to invest, what to staff, which layer
   is the moat.
2. **The 4-layer substrate** (this chapter) -- Foundation -> Assembly
   -> Composition -> Execution. Decision surface: architectural/
   engineering -- where a pattern lives, what it depends on, its
   trade-offs.
3. **The 7-layer Agentic Computing Stack** -- a finer-grained slicing
   for protocol-level discussion and interoperability. Decision
   surface: specification/interop.

"No lens is load-bearing across all chapters. Each chapter chooses the
lens that makes its own decisions cleanest... When in doubt: if the
question is *who owns this and where do we invest*, use Chapter 4's
5-layer landscape. If the question is *which pattern applies and what
is its substrate*, use this chapter's 4-layer substrate. If the
question is *how do these two systems agree at a boundary*, the
7-layer model is the one to reach for."

## Scope: what this chapter deliberately does not catalogue

1. **Harness-specific patterns** -- shapes that depend on a single
   vendor's runtime (e.g. Claude Code's container-model MCP-gateway
   topology, GitHub Agentic Workflows' `safe-outputs:` schema). These
   belong in per-harness adapter documentation, not the Rosetta Stone;
   the chapter points to Genesis's `runtime-affordances/per-harness/`
   directory as their home.
2. **Patterns with a shorter useful lifetime than the book's** --
   prompt-injection countermeasures of the day (delimiter tricks,
   instruction sandwiches, role-tag hardening), jailbreak-prompt
   taxonomies, vendor-specific tool-use schemas. These move quarter by
   quarter; the chapter cites their *durable* versions instead --
   capability-based security, schema-checked transformers,
   bounded-scope grounding.
3. **Patterns the field has not yet converged on** -- multi-agent
   negotiation protocols beyond Panel/Wave, agent-to-agent message
   formats, cross-organisation agent identity. "There is real work
   happening in each of these areas, but no convergence yet on a name
   and shape worth standing behind."

Inclusion criterion for everything that *did* make the catalogue:
"Every entry pays its rent: a name a reader can use in a design review
next week and still recognise in five years."

## Cited sources

Gang-of-Four (Gamma et al., 1994), *Design Patterns: Elements of
Reusable Object-Oriented Software*; Hohpe & Woolf (2003), *Enterprise
Integration Patterns* (source for Scatter-Gather); Kleppmann (2017),
*Designing Data-Intensive Applications* (Snapshot semantics,
durability); Buschmann et al. (1996), *Pattern-Oriented Software
Architecture Vol. 1* (Active Object); Mark S. Miller, *Robust
Composition* (PhD thesis, 2006 -- the capability-security frame);
Evans (2003), *Domain-Driven Design* (Bounded Context); Robert C.
Martin (2017), *Clean Architecture* (Interface Segregation Principle);
Sigelman et al., *Dapper* (Google technical report, 2010 -- distributed
tracing); Martin Fowler (2005), Event Sourcing.

## How this connects to neighbouring chapters

The chapter references the agentic runtime machine (Ch. 11), the load
lifecycle (Ch. 14), attention and context economy (Ch. 15), the
deterministic/probabilistic boundary (Ch. 16), multi-agent
orchestration (Ch. 17), and the execution meta-process (Ch. 18) as the
material each layer's patterns draw on; it hands off to Chapter 20
(anti-patterns and failure modes) and Chapter 21 (primitives as code,
where composition-layer patterns are detailed further), and states
that Chapter 22 ("The reference architecture, earned") revisits
Chapter 4's landscape once the substrate view has been established.
Genesis's own agent-loadable cost-pattern codification
(`skills/genesis/assets/architectural-patterns.md`) carries the
handbook-side names introduced here for Cache-Aware Prefix, Model
Router, Gradient Workflow, and Tool Subset; a worked Panel
re-architecture example lives in Appendix B.

## Source

Ch. 19, Part III -- For Practitioners, *The Agentic SDLC Handbook* by
Daniel Meppiel --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch19-architectural-patterns-rosetta-stone.html
