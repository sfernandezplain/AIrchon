# Reader proficiency tiers: Slumberer -> Gnostic -> Demiurge -> Archon

## What this page is, and what it is not

Every other page in this wiki-book is a research page: a claim about
how Claude Code, GitHub Copilot CLI, or OpenCode actually behaves,
tagged VERIFIED (fetched this session or a prior one from a named
authoritative source) or BEST CURRENT UNDERSTANDING, UNCONFIRMED, per
this book's own grounding discipline. This page is different in kind.
The four tier names below -- **Slumberer**, **Gnostic**, **Demiurge**,
**Archon** -- and the zero-to-hero arc they sit on are an original
classification framework, authored by the book's operator and
recorded here for the first time this session (17 August 2026). They
are not a researched claim about any harness and must not be read as
one: nothing on this page is, or should be treated as, VERIFIED or
BEST CURRENT UNDERSTANDING in the sense those tags carry everywhere
else in this book. The names themselves are deliberately drawn from
Gnostic cosmology's own hierarchy (the sleeper who has not yet
"awoken" to knowledge; the one who possesses *gnosis*, direct
knowledge; the demiurge, the craftsman-god who actually shapes matter
according to received forms; the archon, a ruling power with
mastery over the created order) -- used here purely as a mnemonic
scaffold for a proficiency ladder, not as a claim about anything
external to this book.

What *is* grounded, in the ordinary sense this book uses that word, is
the mapping from each tier to a concrete reading list. Every page
named as a tier's syllabus below is cited against what that page's own
row in [index.md](index.md) says it covers -- a claim you can check
yourself by opening the page, not a claim about harness internals that
needs a VERIFIED/UNCONFIRMED tag. Where this page describes what a
reader "can now explain" after finishing a tier's reading list, that
description is this page's own synthesis of the cited pages' scope,
not a new factual claim about a harness.

This rubric formalizes the same zero-to-hero arc that already drove
two rounds of this book's own gap-analysis work (the 2026-08-17
eight-item list and its "two thinner gaps" follow-on, both tracked in
`HANDOFF-missing-topics.md` before that file was deleted once fully
resolved -- see the [Observability and self-diagnostics](observability-and-self-diagnostics.md)
and [MCP supply-chain trust/vetting](mcp-supply-chain-trust.md) rows
in `index.md` for the two closing entries). Those gap-analysis rounds
asked "what would a reader still be missing on the way from knowing
nothing to being able to build a harness that surpasses the existing
ones" without ever naming the intermediate stages. This page names
them.

```mermaid
stateDiagram-v2
    [*] --> Slumberer
    Slumberer --> Gnostic: agent-topology.md + agent-loop.md
    Gnostic --> Demiurge: the 21-page core-mechanics band
    Demiurge --> Archon: the 10-page design-space / original-survey band
    Archon --> [*]: primary sources beyond this book
    note right of Slumberer
        vibecoding, no vocabulary,
        harness = "the model", no
        model of the loop
    end note
    note right of Gnostic
        has the loop + topology
        vocabulary, no mechanism
        depth in any one harness
    end note
    note right of Demiurge
        can trace a real request
        through one harness's
        actual documented/source
        -verified machinery
    end note
    note right of Archon
        can justify what a NEW
        harness should do, incl.
        where none has a settled
        answer yet
    end note
```

## Tier 1 -- Slumberer (the zero end)

**Definition.** The Slumberer has used an AI coding agent -- possibly
extensively, possibly for real production work -- but holds no working
model of the harness wrapping the model. This is the "clueless /
vibecoding" end the operator named explicitly: someone who iterates by
trial-and-error prompt tweaking, treats the CLI or IDE extension as an
undifferentiated black box, and cannot say which part of the system a
given surprise came from.

**Proven absence of capacity, not proven incapacity.** A Slumberer
typically:
- Cannot distinguish "the model" from "the harness" -- attributes
  session memory, tool access, or a refusal to the model's own
  intelligence or mood rather than to a specific engineered mechanism
  (an injected instruction file, a permission rule, a context-window
  eviction). This book's own umbrella use of "harness" (borrowed from
  Claude Code's own glossary-defined term, per
  [agent-topology.md](agent-topology.md)) is not yet a meaningful
  distinction to them.
- Has no vocabulary for the request/response cycle underneath a
  single turn -- doesn't know the terms "tool call," "system prompt,"
  "context window," "compaction," or "hook," and so cannot describe a
  failure ("it forgot what I told it five minutes ago," "it ran a
  command I didn't approve") in terms of which lifecycle stage
  produced it.
- Debugs by re-phrasing the prompt rather than by forming a hypothesis
  about which mechanism (memory injection, tool schema, permission
  gate, retry policy) is responsible -- the defining behavior the
  operator's "vibecoding" label points at.
- Cannot yet meaningfully use most of this book: a Slumberer opening
  any of the 33 topic pages other than the two named below will
  encounter terms (ReAct, `stop_reason`, prompt caching, subagent
  fan-out) with no scaffolding to hang them on.

**Reading list to exit this tier.** None assigned by design -- a
Slumberer has, by definition, not yet done the two-page foundational
read that produces Gnostic-tier vocabulary. The exit path *is* the
Gnostic-tier reading list immediately below; there is no intermediate
assignment.

## Tier 2 -- Gnostic

**Definition.** The Gnostic has acquired *gnosis* -- direct conceptual
knowledge of what an agent harness is and how its control loop is
shaped -- without yet having traced that knowledge through any one
harness's real, documented machinery. This is the vocabulary-and-map
tier: a Gnostic can now describe a harness abstractly and correctly,
but has not yet built or operated one.

**Capacities a reader must demonstrate to be classified here:**
- Can state, unprompted, what a "harness" is as an engineering
  artifact distinct from the LLM it wraps, and place a harness on
  [agent-topology.md](agent-topology.md)'s own axes: reactive vs.
  deliberative, single-agent vs. multi-agent, tool-augmented vs. fully
  autonomous, and the "LLM + tools + memory + planning" component
  decomposition -- including knowing that this decomposition is
  narrower than Anthropic's own usage and broader than the Hugging
  Face agents course's and Lilian Weng's, per that page's own
  comparison.
- Can explain the Thought/Action/Observation cycle and the ReAct
  pattern by name, the while-loop framing of an agent's main loop,
  why observations get appended back into the prompt rather than
  handled out-of-band, and the stop-and-parse distinction between
  JSON-, code-, and function-calling-style agents -- all per
  [agent-loop.md](agent-loop.md).
- Given a concrete harness feature description (a changelog entry, a
  docs paragraph, a support forum complaint), can say roughly *which
  general category* of loop mechanism it touches -- without yet being
  able to say which specific config key, file path, or documented
  limit governs it in any one real harness. That specific-mechanism
  fluency is the Demiurge threshold, not this one.

**Reading list, Slumberer -> Gnostic:** [agent-topology.md](agent-topology.md)
followed by [agent-loop.md](agent-loop.md) -- in that order, per
`index.md`'s own explicit reading-order note that agent-topology.md
"is written to precede agent-loop.md." Both are GENERAL-CONCEPTS
pages with no harness-specific sections by design; that is precisely
why they are the entry pair -- a Gnostic's knowledge is meant to be
harness-agnostic vocabulary, not yet tied to Claude Code, Copilot CLI,
or OpenCode specifically.

## Tier 3 -- Demiurge

**Definition.** The Demiurge is the craftsman: someone who takes the
Gnostic's conceptual forms and actually shapes real matter with them --
operating, configuring, and reasoning about one or more real harnesses'
actual documented (or source-verified) machinery, across the full
mechanics surface this book covers. A Demiurge builds working things
from received forms; a Demiurge has not yet questioned whether those
forms are the *right* ones, or reasoned about what should exist where
no shipped harness has an answer at all. That distinction is exactly
what separates this tier from Archon.

**Capacities a reader must demonstrate to be classified here:**
- Can trace a concrete request end-to-end through at least one real
  harness's actual machinery, correctly, at the level of specific
  config keys, file paths, tool names, and named limits -- for
  example: which of Claude Code's four `settings.json` scopes
  (Managed/User/Project/Local) wins a merge conflict and where the
  documented exception to that ordering lives
  ([configuration.md](configuration.md)); what happens at Sonnet 5's
  documented ~967K auto-compact threshold and its thrash guard
  ([context-compression.md](context-compression.md)); how OpenCode's
  source-verified `FiberSet`-based concurrent dispatch joins parallel
  `Task` tool calls ([fan-out.md](fan-out.md)); or the exact
  precedence chain (`CLAUDE_CODE_SUBAGENT_MODEL` > invocation param >
  frontmatter > inherit) that resolves which model a Claude Code
  subagent actually runs on
  ([model-routing-and-selection.md](model-routing-and-selection.md)).
- Can operate a harness at power-user/administrator depth: write
  correct hook configurations and reason about the exit-code-2-only
  -blocks rule ([hooks-lifecycle-extensibility.md](hooks-lifecycle-extensibility.md)),
  author permission rules and explain why a given approval prompt did
  or didn't fire ([permissions-and-sandboxing.md](permissions-and-sandboxing.md)),
  and configure MCP servers with a working model of discovery,
  transport, and precedence ([mcp-integration.md](mcp-integration.md)).
- Can compare the same mechanism across Claude Code, Copilot CLI, and
  OpenCode and state precisely where they diverge or converge on a
  shared underlying idea -- e.g. all three harnesses' independently
  documented retry policies differ in specifics (retry counts,
  circuit breakers, fallback chains) while solving the same
  single-outbound-request failure-recovery problem
  ([retries.md](retries.md)).
- Is not yet expected to have an opinion on the open design-space
  questions this book's original-survey pages raise, or to have
  attempted a from-scratch synthesis of a mechanism no shipped harness
  implements -- that is the Archon threshold.

**Reading list, Gnostic -> Demiurge (the core-mechanics band, 21
pages):** [Agent loop: Claude Code vs. OpenCode](agent-loop-implementations.md),
[Memory management](memory-management.md),
[MCP integration](mcp-integration.md),
[Instruction context budget](instruction-context-budget.md),
[Built-in tools](built-in-tools.md),
[Context compression](context-compression.md),
[Caching](caching.md),
[Orchestration](orchestration.md),
[Handoff mechanism](handoff-mechanism.md),
[Fan-out (subagent dispatch)](fan-out.md),
[Inter-agent messaging](inter-agent-messaging.md),
[Retries](retries.md),
[Configuration](configuration.md),
[Built-in skills](built-in-skills.md),
[The LLM API contract](llm-api-contract.md),
[Session & transcript persistence](session-persistence.md),
[Permissions & sandboxing architecture](permissions-and-sandboxing.md),
[Hooks and lifecycle extensibility](hooks-lifecycle-extensibility.md),
[Streaming & incremental rendering](streaming-and-incremental-rendering.md),
[Model routing / selection](model-routing-and-selection.md), and
[Auth & usage accounting](auth-and-usage-accounting.md). These are, in
this book's own words, the pages that document "how a real request
actually moves" through a shipped harness -- config, memory, tools,
context, coordination, transport, persistence, rendering, and money,
each grounded page by page against docs, changelogs, or source per
that page's own Sources section. No particular order is required
within this band (unlike the Slumberer->Gnostic pair); a Demiurge
candidate should expect to move back and forth across it, since many
pages explicitly cross-reference each other (e.g. context-compression.md
vs. memory-management.md's compaction-survival split, or
fan-out.md vs. handoff-mechanism.md vs. orchestration.md's three-way
split of "who launches, what crosses the boundary, who holds the
plan").

## Tier 4 -- Archon (the HERO end)

**Definition.** The Archon holds a ruling, load-bearing command of the
domain: not just able to explain what existing harnesses do, but able
to justify what a *new* harness should do instead -- including, and
especially, in the areas this book's own original-survey pages found
that no shipped harness has a settled answer for. This is the tier the
operator named as the book's own stated end goal: someone capable of
building a harness that surpasses the existing implementations, not
merely reproducing one.

**Capacities a reader must demonstrate to be classified here:**
- Can read this book's own original design-space-survey pages
  critically rather than as received fact, and argue a position from
  primitives -- for example, engaging with
  [advanced-planning-and-execution-architectures.md](advanced-planning-and-execution-architectures.md)'s
  BEST-CURRENT-UNDERSTANDING account of *why* tree-search/MCTS
  planning, loop-integrated self-critique, per-step model ensembling,
  and speculative tool execution have not shipped in any of the three
  harnesses examined (cost metering, interactive-latency UX
  investment, and a permission architecture built around single
  deterministic decisions), and being able to say whether that
  account holds up or where it's incomplete.
- Can design a tool schema and permission-annotation scheme from the
  MCP specification's own four tool-annotation hints
  (`readOnlyHint`/`destructiveHint`/`idempotentHint`/`openWorldHint`)
  without simply copying an existing harness's choices, per
  [Tool schema / interface design](tool-schema-and-interface-design.md)'s
  treatment of the few-powerful-vs-many-narrow tradeoff and deferred
  -schema-loading strategies.
- Can sketch a four-layer testing pyramid (unit-level wire-format
  correctness through end-to-end capability evals) for a harness that
  does not yet exist, per
  [Evals and testing a harness](evals-and-testing-a-harness.md)'s own
  pyramid and OpenCode's fully source-read testing infrastructure as
  a concrete worked example.
- Can reason about multi-agent coordination topology (centralized,
  decentralized, layered, shared-message-pool, blackboard, consensus
  /voting, market-based allocation) as a genuine design choice for a
  system being designed, not only as a classification exercise applied
  after the fact to Claude Code's agent-team mailbox or `/deep-research`'s
  claim-voting, per
  [The multi-agent coordination design space](multi-agent-coordination-design-space.md) --
  including being able to name why market-based/competitive-bidding
  allocation, confirmed absent from all three harnesses examined, might
  still be worth building.
- Can make and defend, as genuine engineering tradeoffs rather than
  received defaults, a packaging/distribution/self-update strategy
  ([Packaging, distribution, and self-update mechanics](packaging-distribution-and-self-update.md)),
  an observability-signal-layering strategy that keeps cost export,
  execution tracing, interactive debugging, and vendor telemetry
  structurally distinct
  ([Observability and self-diagnostics](observability-and-self-diagnostics.md)),
  a TUI rendering-and-component-model architecture
  ([TUI/CLI application architecture](tui-cli-application-architecture.md)),
  a system-prompt-authoring discipline that survives compaction and
  resists prompt injection
  ([System-prompt / agent-instruction design as a craft](system-prompt-design-as-craft.md)),
  a code-discovery strategy positioned deliberately on the RAG-vs
  -agentic-search spectrum rather than by default
  ([Context retrieval / RAG vs. agentic search as a design space](context-retrieval-and-agentic-search.md)),
  and an MCP/plugin supply-chain trust model addressing identity,
  code-safety, and continuity as separable axes
  ([MCP supply-chain trust/vetting](mcp-supply-chain-trust.md)).

**Reading list, Demiurge -> Archon (the design-space / original
-survey / production-completeness band, 10 pages):**
[The multi-agent coordination design space](multi-agent-coordination-design-space.md),
[Tool schema / interface design](tool-schema-and-interface-design.md),
[System-prompt / agent-instruction design as a craft](system-prompt-design-as-craft.md),
[Context retrieval / RAG vs. agentic search as a design space](context-retrieval-and-agentic-search.md),
[Advanced/novel planning and execution architectures](advanced-planning-and-execution-architectures.md),
[Evals and testing a harness](evals-and-testing-a-harness.md),
[MCP supply-chain trust/vetting](mcp-supply-chain-trust.md),
[Observability and self-diagnostics](observability-and-self-diagnostics.md),
[Packaging, distribution, and self-update mechanics](packaging-distribution-and-self-update.md),
and [TUI/CLI application architecture](tui-cli-application-architecture.md).
Several of these pages describe themselves, in their own `index.md`
rows, as "an ORIGINAL DESIGN-SPACE SURVEY, not a research-and-report
page like every other row" (advanced-planning-and-execution-architectures.md)
or as closing a deliberate gap-analysis pass rather than answering an
already-asked question -- that self-description is exactly why this
band, not the Gnostic->Demiurge band, is the one assigned here: these
pages require the Demiurge-tier mechanics underneath them as a
prerequisite (most cross-reference a core-mechanics page directly,
e.g. tool-schema-and-interface-design.md's explicit companion
relationship to built-in-tools.md) and then go one level further, into
territory where the honest answer is sometimes "no shipped harness has
solved this," which is precisely the terrain an Archon-tier reader
needs to be comfortable reasoning in.

**Ceiling note.** This book is a necessary but explicitly insufficient
input at Archon tier. It is written LAZY, on demand, as real questions
need each topic (per this book's own front-matter in `index.md`) --
it is not, and does not claim to be, an exhaustive treatment of any
harness. True Archon-level command requires primary-source fluency
this book deliberately does not replace: Claude Code's own Agent SDK
docs and changelog, OpenCode's live `dev`-branch source (flagged
throughout this book as not necessarily reflecting a stable release),
Copilot CLI's own docs and changelog, the Model Context Protocol
specification, and the academic literature cited across the
design-space pages (Tree of Thoughts, LATS, Reflexion, Mixture-of
-Agents, the Contract Net Protocol, and the rest). An Archon-tier
reader treats every page's own "Sources" section as a pointer back to
where the *next* question should actually be researched, not as a
closed case.

## How this rubric is meant to be used

This rubric exists as a calibration instrument, not a gatekeeping one.
Two concrete uses:

1. **Calibrating explanation depth.** `airchon-mentor` (or a reader
   assessing themselves) can use a reader's self-reported or
   demonstrated tier to decide how deep an explanation should go
   before it becomes noise rather than signal. A Slumberer asking "why
   did Claude Code run that command without asking me" needs the
   Gnostic-tier vocabulary (what a permission mode is, what the
   auto-mode classifier does in outline) introduced before the
   Demiurge-tier specifics (the classifier's exact decision pipeline,
   trust-scope rules, and consecutive/total fallback thresholds in
   [Permissions & sandboxing architecture](permissions-and-sandboxing.md))
   land as anything but noise. Conversely, an already-Demiurge reader
   asking the same question should be answered at the mechanism level
   directly, not re-walked through what a permission mode is.
2. **Self-assessment before the book's own stated end goal.** This
   book's gap-analysis history (the `HANDOFF-missing-topics.md` rounds
   referenced in `index.md`'s own entries) was explicitly driven by
   the question of what a reader still needs to go from knowing
   nothing to being able to build a harness that surpasses Claude
   Code, Copilot CLI, and OpenCode. A reader can use the four reading
   lists above as a literal, checkable gate before attempting that
   goal: if a reading-list page names a mechanism you cannot yet
   explain unprompted (a specific config precedence, a specific
   failure mode, a specific source-verified data structure), that is
   the concrete, actionable signal that you are not yet at the tier
   the list claims, regardless of how confident the vibe feels --
   which is, not coincidentally, exactly the gap this rubric's zero
   tier is named for.

This page will need revisiting as new topic pages are added to
`references/harnesses/` -- a newly written page should be slotted into
one of the three post-Slumberer reading lists (or flagged as not yet
fitting any of them) rather than left unclassified, so this rubric
stays a live map of the book rather than a snapshot of it.
