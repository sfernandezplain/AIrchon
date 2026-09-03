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
row in [index.md](../../references/harnesses/index.md) says it covers -- a claim you can check
yourself by opening the page, not a claim about harness internals that
needs a VERIFIED/UNCONFIRMED tag. Where this page describes what a
reader "can now explain" after finishing a tier's reading list, that
description is this page's own synthesis of the cited pages' scope,
not a new factual claim about a harness.

**2026-09-03 relocation and extension note.** This page moved from
`references/harnesses/reader-proficiency-tiers.md` to its current path,
`resources/airchon-teacher/reader-proficiency-tiers.md`, the same day
it was extended with two new reading-list clusters. The move corrects a
mis-scoping this page's own opening paragraph above already flags: this
is a meta/rubric page authored by the operator, not a
`references/harnesses/` research page, and it belongs in
`airchon-teacher`'s own tier domain instead -- the same reasoning that
already relocated the session-pacing agenda files (`*-sessions.md`) out
of the wiki-book and into `resources/airchon-teacher/` on 2026-08-17
(see `CHANGELOG.md`). Nothing about the page's own substance changed
because of the move itself; every link on this page was rewritten to
the new relative depth (two directories up to reach
`references/harnesses/`, `references/rag/`, `references/sdlc/`,
`references/models/`, or `references/inference-engines/`, where a bare
filename or a `../rag/`/`../sdlc/` link previously sufficed from inside
`references/harnesses/` itself), and
`references/harnesses/knowledge-path-curriculum.md`,
`references/harnesses/index.md`, and this project's other consumers of
this page were updated to point at the new path. Same day, two more
reference areas that postdate the 2026-08-24 RAG/SDLC revision below --
`references/models/` and `references/inference-engines/` -- were folded
into the Gnostic->Demiurge extension for the same reason RAG and the
SDLC practitioner-mechanics cluster were folded in then: see that
extension subsection below for the full reasoning and reading lists.

This rubric formalizes the same zero-to-hero arc that already drove
two rounds of this book's own gap-analysis work (the 2026-08-17
eight-item list and its "two thinner gaps" follow-on, both tracked in
`HANDOFF-missing-topics.md` before that file was deleted once fully
resolved -- see the [Observability and self-diagnostics](../../references/harnesses/observability-and-self-diagnostics.md)
and [MCP supply-chain trust/vetting](../../references/harnesses/mcp-supply-chain-trust.md) rows
in `index.md` for the two closing entries). Those gap-analysis rounds
asked "what would a reader still be missing on the way from knowing
nothing to being able to build a harness that surpasses the existing
ones" without ever naming the intermediate stages. This page names
them.

```mermaid
stateDiagram-v2
    [*] --> Slumberer
    Slumberer --> Gnostic: agent-topology.md + agent-loop.md
    Gnostic --> Demiurge: 21-page core-mechanics band + RAG/SDLC/Models/Inference-Engines-mechanics extensions
    Demiurge --> Archon: 10-page design-space band + SDLC design-space extension
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
        -verified machinery, incl.
        a real RAG pipeline, the
        SDLC handbook's own
        instrumented-codebase
        mechanics, a model's own
        classification axes, and
        a local inference engine's
        serving mechanics
    end note
    note right of Archon
        can justify what a NEW
        harness should do, incl.
        where none has a settled
        answer yet -- and can
        critique the SDLC
        handbook's own methodology
        band the same way
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
  [agent-topology.md](../../references/harnesses/agent-topology.md)) is not yet a meaningful
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
  [agent-topology.md](../../references/harnesses/agent-topology.md)'s own axes: reactive vs.
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
  [agent-loop.md](../../references/harnesses/agent-loop.md).
- Given a concrete harness feature description (a changelog entry, a
  docs paragraph, a support forum complaint), can say roughly *which
  general category* of loop mechanism it touches -- without yet being
  able to say which specific config key, file path, or documented
  limit governs it in any one real harness. That specific-mechanism
  fluency is the Demiurge threshold, not this one.

**Reading list, Slumberer -> Gnostic:** [agent-topology.md](../../references/harnesses/agent-topology.md)
followed by [agent-loop.md](../../references/harnesses/agent-loop.md) -- in that order, per
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
  ([configuration.md](../../references/harnesses/configuration.md)); what happens at Sonnet 5's
  documented ~967K auto-compact threshold and its thrash guard
  ([context-compression.md](../../references/harnesses/context-compression.md)); how OpenCode's
  source-verified `FiberSet`-based concurrent dispatch joins parallel
  `Task` tool calls ([fan-out.md](../../references/harnesses/fan-out.md)); or the exact
  precedence chain (`CLAUDE_CODE_SUBAGENT_MODEL` > invocation param >
  frontmatter > inherit) that resolves which model a Claude Code
  subagent actually runs on
  ([model-routing-and-selection.md](../../references/harnesses/model-routing-and-selection.md)).
- Can operate a harness at power-user/administrator depth: write
  correct hook configurations and reason about the exit-code-2-only
  -blocks rule ([hooks-lifecycle-extensibility.md](../../references/harnesses/hooks-lifecycle-extensibility.md)),
  author permission rules and explain why a given approval prompt did
  or didn't fire ([permissions-and-sandboxing.md](../../references/harnesses/permissions-and-sandboxing.md)),
  and configure MCP servers with a working model of discovery,
  transport, and precedence ([mcp-integration.md](../../references/harnesses/mcp-integration.md)).
- Can compare the same mechanism across Claude Code, Copilot CLI, and
  OpenCode and state precisely where they diverge or converge on a
  shared underlying idea -- e.g. all three harnesses' independently
  documented retry policies differ in specifics (retry counts,
  circuit breakers, fallback chains) while solving the same
  single-outbound-request failure-recovery problem
  ([retries.md](../../references/harnesses/retries.md)).
- Can build and reason about a real retrieval-augmented-generation
  pipeline at the same config/parameter granularity as the
  core-mechanics band -- e.g. why `RecursiveCharacterTextSplitter`'s
  character-based `chunk_size` silently disagrees with a transformer
  tokenizer's token count and the token-aware fix
  ([Advanced RAG techniques](../../references/rag/advanced-rag-techniques.md)), where
  a semantic cache sits (before retrieval, not before generation) and
  why FIFO eviction against a Euclidean `IndexFlatL2` threshold was
  chosen over an LRU policy
  ([Semantic caching for RAG](../../references/rag/semantic-caching.md)), and how a
  synthetic-QA/critique-agent/LLM-as-judge evaluation pipeline is
  actually built rather than merely described
  ([RAG evaluation](../../references/rag/rag-evaluation.md)) -- treating RAG as a
  technique with its own mechanics, prerequisite to (and distinct from)
  the Archon-tier question of whether any given harness *should* use it.
- Can operate the Agentic SDLC Handbook's instrumented-codebase
  machinery at the same depth: name the seven primitive types and their
  load modes, trace a primitive through the four-phase
  Resolve/Materialize/Bind/Activate lifecycle, and explain the
  window-vs-attention distinction and the U-shaped attention curve as a
  mechanism *distinct from but concordant with* this book's own
  [context-compression.md](../../references/harnesses/context-compression.md)/[memory-management.md](../../references/harnesses/memory-management.md) --
  while keeping straight that this material's authority is a single
  external source (`references/sdlc/`, "the handbook says"), not
  independently cross-verified the way this book's own pages are.
- Is not yet expected to have an opinion on the open design-space
  questions this book's original-survey pages raise, or to have
  attempted a from-scratch synthesis of a mechanism no shipped harness
  implements -- that is the Archon threshold.

**Reading list, Gnostic -> Demiurge (the core-mechanics band, 21
pages):** [Agent loop: Claude Code vs. OpenCode](../../references/harnesses/agent-loop-implementations.md),
[Memory management](../../references/harnesses/memory-management.md),
[MCP integration](../../references/harnesses/mcp-integration.md),
[Instruction context budget](../../references/harnesses/instruction-context-budget.md),
[Built-in tools](../../references/harnesses/built-in-tools.md),
[Context compression](../../references/harnesses/context-compression.md),
[Caching](../../references/harnesses/caching.md),
[Orchestration](../../references/harnesses/orchestration.md),
[Handoff mechanism](../../references/harnesses/handoff-mechanism.md),
[Fan-out (subagent dispatch)](../../references/harnesses/fan-out.md),
[Inter-agent messaging](../../references/harnesses/inter-agent-messaging.md),
[Retries](../../references/harnesses/retries.md),
[Configuration](../../references/harnesses/configuration.md),
[Built-in skills](../../references/harnesses/built-in-skills.md),
[The LLM API contract](../../references/harnesses/llm-api-contract.md),
[Session & transcript persistence](../../references/harnesses/session-persistence.md),
[Permissions & sandboxing architecture](../../references/harnesses/permissions-and-sandboxing.md),
[Hooks and lifecycle extensibility](../../references/harnesses/hooks-lifecycle-extensibility.md),
[Streaming & incremental rendering](../../references/harnesses/streaming-and-incremental-rendering.md),
[Model routing / selection](../../references/harnesses/model-routing-and-selection.md), and
[Auth & usage accounting](../../references/harnesses/auth-and-usage-accounting.md). These are, in
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

### Demiurge tier extensions: RAG, Agentic-SDLC, AI-model-classification, and inference-engine practitioner mechanics

Four reference areas outside this wiki-book -- `references/rag/`,
`references/sdlc/`, `references/models/`, and
`references/inference-engines/` -- were added to this project after the
four-tier rubric above was first written, and this page has been
revisited twice per its own closing instruction (below) to slot each in
rather than leave it unclassified. `references/rag/` and
`references/sdlc/` were folded in on 2026-08-24; `references/models/`
and `references/inference-engines/` were folded in on 2026-09-03, once
both areas existed and needed the same treatment. All four extend the
Demiurge tier's reading list; none displaces or shortens the 21-page
core-mechanics band above, which remains this tier's primary gate.

**Grounding-status caveat, load-bearing for all four extensions.**
`references/rag/` and `references/sdlc/` are sourced from areas with a
*weaker* grounding discipline than this wiki-book's own
VERIFIED/BEST-CURRENT-UNDERSTANDING tagging. `references/rag/` attributes
claims directly to the HuggingFace Cookbook notebooks and Lewis et al.
(2020) -- "the source says," with no independent cross-verification
beyond what the source itself contains. `references/sdlc/` attributes
claims to the Agentic SDLC Handbook (Daniel Meppiel) alone -- "the
handbook says," re-checked only against the handbook's own live chapter
text, never against harness docs or any other independent authority.
`references/models/` and `references/inference-engines/` differ again,
in a way worth holding apart with equal care rather than folding into
either the "weaker" framing above or this wiki-book's own: both areas do
apply a two-tag VERIFIED/BEST-CURRENT-UNDERSTANDING discipline internally
(per each area's own `index.md`), but that tagging is scoped to each
area's own named primary-source corpus -- Hugging Face's Hub/
`transformers`/Optimum documentation and Maxime Labonne's frankenMoE
writeup for `references/models/`, and each engine's own docs site or
repository (llama.cpp's GitHub README and linked docs, `docs.ollama.com`,
`ktransformers.net/docs`) for `references/inference-engines/` -- never
this wiki-book's own `references/harnesses/` corpus of harness docs,
changelogs, and source. A claim tagged VERIFIED on a
`references/models/` or `references/inference-engines/` page means it
was fetched from one of those named sources this session, never that it
was cross-checked against Claude Code's, Copilot CLI's, or OpenCode's
own documentation -- the same AUTHORITY OVERREACH caution
`references/harnesses/` applies between harnesses applies here between
reference areas: an inference engine's own docs are not authoritative
about a harness's behavior, and vice versa. A Demiurge-tier reader who
has internalized all four extension clusters is fluent in
RAG-the-technique, in the handbook's instrumented-codebase discipline, in
the Hub's own model-classification taxonomy, and in named
local-inference-engine mechanics -- not in a claim this wiki-book's own
`references/harnesses/` corpus has independently verified the way it has
verified, say, Claude Code's `settings.json` merge order.

- **RAG cluster (9 pages, `references/rag/`):**
  [RAG foundations](../../references/rag/foundations.md),
  [The basic RAG pipeline](../../references/rag/basic-rag-pipeline.md),
  [Advanced RAG techniques](../../references/rag/advanced-rag-techniques.md),
  [Vector store integrations](../../references/rag/vector-store-integrations.md),
  [Semantic caching for RAG](../../references/rag/semantic-caching.md),
  [Structured generation for RAG](../../references/rag/structured-generation-for-rag.md),
  [RAG evaluation](../../references/rag/rag-evaluation.md),
  [Agentic RAG with LlamaIndex](../../references/rag/agentic-rag-with-llamaindex.md),
  and [RAG over heterogeneous data sources](../../references/rag/heterogeneous-data-sources.md).
  This cluster is assigned here, rather than folded into the Gnostic
  entry pair, because its depth matches the core-mechanics band's own
  granularity -- specific chunk-size/tokenizer mismatches, specific
  reranker models (ColBERTv2 via RAGatouille), specific cache-eviction
  policies, specific vector-store integrations (Milvus, Elasticsearch,
  MongoDB Atlas) -- not the harness-agnostic abstraction the Gnostic tier
  is deliberately scoped to. It is also, concretely, the direct
  prerequisite body of knowledge for the already-existing Archon-tier
  page [Context retrieval / RAG vs. agentic search as a design
  space](../../references/harnesses/context-retrieval-and-agentic-search.md), which presumes a
  reader already knows what a real RAG pipeline's moving parts are
  before it asks whether a harness *should* reach for one as its
  code-discovery strategy.
- **Agentic-SDLC practitioner-mechanics cluster (7 pages,
  `references/sdlc/`):**
  [The Agentic SDLC reference architecture](../../references/sdlc/04-the-reference-architecture.md)
  (Ch. 4), [The agentic runtime machine](../../references/sdlc/11-the-runtime-machine.md)
  (Ch. 11), [The instrumented codebase](../../references/sdlc/12-the-instrumented-codebase.md)
  (Ch. 12), [The load lifecycle](../../references/sdlc/14-the-load-lifecycle.md)
  (Ch. 14), [Attention and context economy](../../references/sdlc/15-attention-and-context-economy.md)
  (Ch. 15), [Primitives as code](../../references/sdlc/21-primitives-as-code.md)
  (Ch. 21), and [Appendix A: the cross-harness
  reference](../../references/sdlc/appendix-a-cross-harness-reference.md). These seven
  pages are this cluster's *mechanics* half: the seven primitive types
  and their five load modes, the four-phase Resolve/Materialize/Bind
  /Activate pipeline, the window-vs-attention distinction and the
  U-shaped attention curve, and the package/lockfile/override model that
  turns a primitive from a file into a versioned dependency -- material
  that sits at the same "trace a real thing through its actual mechanism"
  depth as this tier's core-mechanics band, just sourced single-source
  from the handbook rather than cross-verified against harness docs. The
  handbook's own Appendix A master comparison table (ten primitive
  concepts across five harnesses' concrete file/config conventions) is
  assigned here specifically because it functions as a cross-harness
  ready-reference of exactly the kind a Demiurge-tier reader is expected
  to be able to produce from the core-mechanics band's own pages. The
  remaining, more speculative/methodological half of this source
  (PROSE, multi-agent orchestration patterns, anti-patterns, the
  execution meta-process, the Rosetta Stone pattern catalogue, and the
  case studies) is assigned at Archon tier instead -- see below.
- **AI model classification cluster (5 pages, `references/models/`):**
  [Model terminology: a grounding glossary](../../references/models/model-terminology.md),
  [Task and pipeline classification: what a model is for](../../references/models/task-and-pipeline-classification.md),
  [Parameter count and scale: the second classification axis](../../references/models/parameter-count-and-scale.md),
  [Mixture of Experts and frankenMoE: the architecture axis](../../references/models/mixture-of-experts-and-frankenmerging.md),
  and [Quantization: the deployment-precision axis](../../references/models/quantization.md).
  This cluster is assigned here, for the same reason the RAG cluster
  above is: its depth matches the core-mechanics band's own granularity
  -- the verified VRAM-per-parameter-count rule of thumb and its worked
  examples, `num_local_experts` vs. `num_experts_per_tok` and MergeKit's
  three router-initialization methods, the affine/symmetric int8
  quantization schemes and a concrete worked VRAM comparison across
  bf16/int8/int4 -- not the harness-agnostic abstraction the Gnostic
  tier is deliberately scoped to. Although its own five pages are, by
  `references/models/`'s own framing, ordered "foundational -> advanced"
  within that area itself, that ordering is relative to that area's own
  more advanced pages, not a reason to place it at the harness-agnostic
  Gnostic tier here -- every one of its claims is pinned to a specific
  number, formula, or named config surface, exactly the Demiurge-tier
  bar. It is also, concretely, a load-bearing prerequisite for the
  inference-engines cluster immediately below, which cross-links this
  cluster's quantization and Mixture-of-Experts pages rather than
  re-deriving either concept -- a Demiurge candidate should read this
  cluster before attempting that one.
- **Local/self-hosted inference-engines cluster (14 pages,
  `references/inference-engines/`):** eleven engine-agnostic concept
  pages -- [Model file formats for inference](../../references/inference-engines/model-file-formats.md),
  [Memory-mapped model loading](../../references/inference-engines/memory-mapped-model-loading.md),
  [Quantization as an inference-engine-level concern](../../references/inference-engines/quantization-at-inference-time.md),
  [The KV cache and context-window management during generation](../../references/inference-engines/kv-cache-and-context-window-management.md),
  [Sampling and decoding parameters](../../references/inference-engines/sampling-and-decoding-parameters.md),
  [Batching and continuous batching of concurrent requests](../../references/inference-engines/batching-and-continuous-batching.md),
  [CPU/GPU/heterogeneous offloading, and expert offloading for MoE models](../../references/inference-engines/cpu-gpu-heterogeneous-offloading.md),
  [Multi-GPU inference: pipeline vs. tensor parallelism](../../references/inference-engines/multi-gpu-and-tensor-parallelism.md),
  [Speculative decoding](../../references/inference-engines/speculative-decoding.md),
  [Server/API modes](../../references/inference-engines/server-api-modes.md), and
  [Model management and distribution](../../references/inference-engines/model-management-and-distribution.md) --
  plus three per-engine implementation pages,
  [llama.cpp: the foundational C/C++ inference engine](../../references/inference-engines/llama-cpp.md),
  [Ollama: a model-registry, Modelfile, and REST layer over llama.cpp (and its own engine)](../../references/inference-engines/ollama.md),
  and [KTransformers: heterogeneous CPU/GPU inference for large MoE models](../../references/inference-engines/ktransformers.md).
  This cluster earns the same Demiurge-tier placement on the same
  grounds as the RAG and model-classification clusters above: it is
  pinned to specific, named config surfaces and figures rather than
  harness-agnostic abstraction -- llama.cpp's load-mode/GPU-layer/
  split-mode/KV-cache-quantization flags, Ollama's context-length
  environment variable and VRAM-tiered automatic scheduling,
  KTransformers' arithmetic-intensity-guided offloading figures, and a
  concrete default GGUF quantization-type naming family. It is also,
  structurally, the same kind of "trace a real thing through its actual
  mechanism" exercise the core-mechanics band's own pages are (e.g.
  `caching.md`'s prompt-prefix reuse vs. this cluster's KV-cache-and
  -context-window page; `fan-out.md`'s concurrency caps vs. this
  cluster's continuous-batching page), just sourced from each engine's
  own docs/repo rather than from a shipped agent harness. Read the
  model-classification cluster above first: this cluster's own
  quantization and CPU/GPU-offloading-for-MoE pages explicitly
  cross-link that cluster's quantization and Mixture-of-Experts pages
  rather than re-deriving either concept, so a reader who has not yet
  internalized `references/models/`'s own vocabulary will hit an
  unexplained term partway through this one.

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
  [advanced-planning-and-execution-architectures.md](../../references/harnesses/advanced-planning-and-execution-architectures.md)'s
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
  [Tool schema / interface design](../../references/harnesses/tool-schema-and-interface-design.md)'s
  treatment of the few-powerful-vs-many-narrow tradeoff and deferred
  -schema-loading strategies.
- Can sketch a four-layer testing pyramid (unit-level wire-format
  correctness through end-to-end capability evals) for a harness that
  does not yet exist, per
  [Evals and testing a harness](../../references/harnesses/evals-and-testing-a-harness.md)'s own
  pyramid and OpenCode's fully source-read testing infrastructure as
  a concrete worked example.
- Can reason about multi-agent coordination topology (centralized,
  decentralized, layered, shared-message-pool, blackboard, consensus
  /voting, market-based allocation) as a genuine design choice for a
  system being designed, not only as a classification exercise applied
  after the fact to Claude Code's agent-team mailbox or `/deep-research`'s
  claim-voting, per
  [The multi-agent coordination design space](../../references/harnesses/multi-agent-coordination-design-space.md) --
  including being able to name why market-based/competitive-bidding
  allocation, confirmed absent from all three harnesses examined, might
  still be worth building.
- Can make and defend, as genuine engineering tradeoffs rather than
  received defaults, a packaging/distribution/self-update strategy
  ([Packaging, distribution, and self-update mechanics](../../references/harnesses/packaging-distribution-and-self-update.md)),
  an observability-signal-layering strategy that keeps cost export,
  execution tracing, interactive debugging, and vendor telemetry
  structurally distinct
  ([Observability and self-diagnostics](../../references/harnesses/observability-and-self-diagnostics.md)),
  a TUI rendering-and-component-model architecture
  ([TUI/CLI application architecture](../../references/harnesses/tui-cli-application-architecture.md)),
  a system-prompt-authoring discipline that survives compaction and
  resists prompt injection
  ([System-prompt / agent-instruction design as a craft](../../references/harnesses/system-prompt-design-as-craft.md)),
  a code-discovery strategy positioned deliberately on the RAG-vs
  -agentic-search spectrum rather than by default
  ([Context retrieval / RAG vs. agentic search as a design space](../../references/harnesses/context-retrieval-and-agentic-search.md)),
  and an MCP/plugin supply-chain trust model addressing identity,
  code-safety, and continuity as separable axes
  ([MCP supply-chain trust/vetting](../../references/harnesses/mcp-supply-chain-trust.md)).
- Can critique, from primitives, the Agentic SDLC Handbook's own
  original methodological and design-space material -- for example,
  arguing whether the five-phase AUDIT/PLAN/WAVE/VALIDATE/SHIP execution
  meta-process ([The execution meta-process](../../references/sdlc/18-the-execution-meta-process.md))
  is a genuinely general discipline or an artifact of the specific
  PR #394 case study it was extracted from, or whether the Rosetta
  Stone pattern catalogue's "precise/partial/weak-or-none" classical
  -analogue ratings ([Architectural patterns: a Rosetta
  Stone](../../references/sdlc/19-architectural-patterns-rosetta-stone.md)) hold up
  against this book's own, independently-grounded treatment of the same
  structural problems (e.g. comparing its Composition-layer GoF mapping
  against [Tool schema / interface design](../../references/harnesses/tool-schema-and-interface-design.md)'s
  own few-powerful-vs-many-narrow tradeoff) -- while keeping straight
  that this material carries the weaker "the handbook says" grounding
  status described in the Demiurge-tier extension above, not this
  book's own VERIFIED/BEST-CURRENT-UNDERSTANDING tagging.

**Reading list, Demiurge -> Archon (the design-space / original
-survey / production-completeness band, 10 pages):**
[The multi-agent coordination design space](../../references/harnesses/multi-agent-coordination-design-space.md),
[Tool schema / interface design](../../references/harnesses/tool-schema-and-interface-design.md),
[System-prompt / agent-instruction design as a craft](../../references/harnesses/system-prompt-design-as-craft.md),
[Context retrieval / RAG vs. agentic search as a design space](../../references/harnesses/context-retrieval-and-agentic-search.md),
[Advanced/novel planning and execution architectures](../../references/harnesses/advanced-planning-and-execution-architectures.md),
[Evals and testing a harness](../../references/harnesses/evals-and-testing-a-harness.md),
[MCP supply-chain trust/vetting](../../references/harnesses/mcp-supply-chain-trust.md),
[Observability and self-diagnostics](../../references/harnesses/observability-and-self-diagnostics.md),
[Packaging, distribution, and self-update mechanics](../../references/harnesses/packaging-distribution-and-self-update.md),
and [TUI/CLI application architecture](../../references/harnesses/tui-cli-application-architecture.md).
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

### Archon tier extension: the Agentic-SDLC design-space/methodology cluster

**Reading list extension (10 items, `references/sdlc/`):**
[Part III preface & the practitioner's
mindset](../../references/sdlc/09-10-part-iii-preface-and-practitioners-mindset.md)
(Ch. 9-10), [The PROSE framework](../../references/sdlc/prose-framework.md) (Ch. 13),
[The deterministic/probabilistic
boundary](../../references/sdlc/16-deterministic-probabilistic-boundary.md) (Ch. 16),
[Multi-agent orchestration](../../references/sdlc/17-multi-agent-orchestration.md)
(Ch. 17), [The execution meta-process](../../references/sdlc/18-the-execution-meta-process.md)
(Ch. 18), [Architectural patterns: a Rosetta
Stone](../../references/sdlc/19-architectural-patterns-rosetta-stone.md) (Ch. 19),
[Anti-patterns and failure modes](../../references/sdlc/20-anti-patterns-and-failure-modes.md)
(Ch. 20), [The reference architecture,
earned](../../references/sdlc/22-the-reference-architecture-earned.md) (Ch. 22), the
four Part IV case studies read as one bundled item ([APM auth + logging
overhaul](../../references/sdlc/23-case-study-apm-overhaul.md),
[handbook-writing](../../references/sdlc/24-case-study-handbook-writing.md),
[publishing pipeline](../../references/sdlc/25-case-study-publishing-pipeline.md),
[growth engine](../../references/sdlc/26-case-study-growth-engine.md)), and
[Appendix B: Genesis worked
example](../../references/sdlc/appendix-b-genesis-worked-example.md).

This ten-item extension is assigned at Archon rather than Demiurge tier
for the same reason the ten-page core design-space band above is: each
item is original synthesis or methodology, not a mechanics report, and
each demands the reader argue about tradeoffs rather than trace a
config value. PROSE's five constraints (Progressive Disclosure, Reduced
Scope, Orchestrated Composition, Safety Boundaries, and Explicit
Hierarchy) are a craft discipline for authoring agent-facing artifacts,
directly parallel in kind to this book's own
[System-prompt / agent-instruction design as a
craft](../../references/harnesses/system-prompt-design-as-craft.md); the Rosetta Stone chapter's
four-layer substrate (Foundation/Assembly/Composition/Execution) and its
precise/partial/weak-or-none Gang-of-Four analogue ratings is a
pattern-catalogue exercise of the same shape this book's own
[Advanced/novel planning and execution
architectures](../../references/harnesses/advanced-planning-and-execution-architectures.md) and
[The multi-agent coordination design
space](../../references/harnesses/multi-agent-coordination-design-space.md) perform, just against a
different (single-source, practitioner-methodology) corpus; the
19-anti-pattern taxonomy and the five-phase AUDIT/PLAN/WAVE/VALIDATE/SHIP
execution meta-process are exactly the kind of "no shipped harness (or
in this case, no shipped methodology) has a settled, universally-agreed
answer" terrain this tier's definition names; and the four case studies
plus Appendix B's Genesis worked example are load-bearing because they
let an Archon-tier reader check whether a named methodology actually
survives contact with a real, messy, citation-bearing production
incident (PR #394's 75-file/6-agent/8-plan-iteration/5-wave overhaul;
Genesis's own before/after panel-in-one-thread fix) rather than only
reading well in the abstract. As with the Demiurge-tier extension above,
this material's grounding status is "the handbook says," re-verified
only against the handbook's own live chapter text -- an Archon-tier
reader engaging with it critically (per this tier's own capacities list)
is expected to hold that epistemic status in mind, not to treat a
methodology claim here with the same confidence as a VERIFIED claim
about Claude Code's or OpenCode's actual source.

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
   [Permissions & sandboxing architecture](../../references/harnesses/permissions-and-sandboxing.md))
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
stays a live map of the book rather than a snapshot of it. The same now
holds for `references/sdlc/`, `references/rag/`, `references/models/`,
and `references/inference-engines/`: this page was revisited on
2026-08-24 to fold `references/sdlc/` and `references/rag/` into the
Demiurge- and Archon-tier reading lists, and again on 2026-09-03 to fold
`references/models/` and `references/inference-engines/` into the
Demiurge-tier reading list, as the extension subsections above document
-- and any future page added to any of the four areas should likewise be
slotted into an existing tier band (or flagged as not yet fitting one)
rather than left unclassified. All four extensions carry a
grounding-status caveat this page's original four bands did not need to
state: `references/sdlc/` and `references/rag/` do not use this
wiki-book's own VERIFIED/BEST-CURRENT-UNDERSTANDING tagging at all, while
`references/models/` and `references/inference-engines/` apply a
same-shaped two-tag discipline but scoped to their own, separate
named-source corpus rather than to this wiki-book's own
`references/harnesses/` corpus -- see the "grounding-status caveat"
paragraph under the Demiurge tier's extension subsection for the exact
wording a reader or mentor should carry forward when discussing this
material's evidentiary weight, for either kind of distinction.

**2026-09-03 relocation note.** This page itself now lives at
`resources/airchon-teacher/reader-proficiency-tiers.md`, not
`references/harnesses/reader-proficiency-tiers.md` -- see this page's
own opening section for why, and see
[references/harnesses/index.md](../../references/harnesses/index.md)
for the pointer left in its old location. Every other file that linked
to or quoted this page (`references/harnesses/knowledge-path-curriculum.md`,
[classification-flow.md](classification-flow.md),
[course-delivery-flow.md](course-delivery-flow.md), and
[demiurge-to-archon-sessions.md](demiurge-to-archon-sessions.md)) was
updated the same day to point at, or quote consistently with, this new
location and this revision's content.
