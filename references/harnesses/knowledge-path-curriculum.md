# Knowledge-path curriculum: a course skeleton for the three tier transitions

## What this page is, and what it is not

This page is a **curriculum scaffold**, not a research page. Every other
page in this wiki-book (plus
[reader-proficiency-tiers.md](../../resources/airchon-teacher/reader-proficiency-tiers.md),
which this page directly expands but which itself relocated out of this
book on 2026-09-03 -- see this page's own revision note below) makes
claims about how Claude Code, GitHub
Copilot CLI, or OpenCode actually behave, each tagged VERIFIED or BEST
CURRENT UNDERSTANDING, UNCONFIRMED per this book's grounding discipline.
This page makes no new claims of that kind. It takes the three named
transitions from `reader-proficiency-tiers.md` -- Slumberer to Gnostic,
Gnostic to Demiurge, Demiurge to Archon -- and turns each tier's flat
reading list into a teachable unit: learning objectives, one module per
source page with key concepts / a comprehension check / an applied
exercise, and a capstone that proves the transition actually happened
rather than merely that the pages were opened.

Two consequences follow from that scope. First, every factual detail
this page cites about what a given source page covers (a config key, a
tool name, a mechanism) is inherited from that source page's own
grounding, not re-verified here -- if a module's "key concepts" line
names `CLAUDE_CODE_MAX_RETRIES` or `PostToolUse`, the authority for that
claim is [retries.md](retries.md) or
[hooks-lifecycle-extensibility.md](hooks-lifecycle-extensibility.md)
itself, cited by reference, not re-fetched for this page. Second, the
comprehension-check questions, exercise prompts, and capstones below are
this page's own original pedagogical design (like the tier names
themselves), not a researched claim about how anyone actually learns --
treat them as a first-draft course skeleton to be iterated on when
actual courses/exercises get built from it, not as a finished syllabus.

**2026-08-24 revision note.** `reader-proficiency-tiers.md` was revisited
this session to fold `references/sdlc/` and `references/rag/` into the
Demiurge and Archon reading lists (see that page's Demiurge- and
Archon-tier extension subsections); this page was revised to match --
Cluster 6 (RAG) and Cluster 7 (Agentic-SDLC practitioner mechanics) were
added to Transition 2, and Cluster 8 (Agentic-SDLC design-space and
methodology) was added to Transition 3, each with the same per-module
key-concepts/comprehension-check/exercise shape as the pre-existing
clusters. Every module in Clusters 6-8 inherits its factual detail from
`references/rag/` or `references/sdlc/` pages, which in turn attribute
their own claims to the HuggingFace Cookbook notebooks and Lewis et al.
(2020), or to the Agentic SDLC Handbook alone -- not to this
wiki-book's own VERIFIED/BEST-CURRENT-UNDERSTANDING grounding. That
distinction is restated inline at each new cluster's overview and is not
optional context to drop when teaching from this page.

**2026-09-03 revision note.** `reader-proficiency-tiers.md` moved out of
this wiki-book that same day, to
`resources/airchon-teacher/reader-proficiency-tiers.md` (a relocation,
not a re-scoping of what it covers -- see that page's own opening
section and `references/harnesses/index.md`'s "Reader proficiency
tiers" section for why), and was revisited again to fold two more
reference areas, `references/models/` and `references/inference-engines/`,
into its Demiurge-tier extension. This page was revised to match:
Cluster 9 (AI model classification, 5 modules from `references/models/`)
and Cluster 10 (Local/self-hosted inference engines, 14 modules from
`references/inference-engines/`) were added to Transition 2, immediately
after Clusters 6-7, using the same per-module key-concepts
/comprehension-check/exercise shape as every prior cluster. Every module
in Clusters 9-10 inherits its factual detail from `references/models/`
or `references/inference-engines/` pages, which in turn attribute their
own claims to Hugging Face's own documentation (Hub task pages, the
`transformers` glossary, the Optimum quantization guide), Maxime
Labonne's frankenMoE writeup, or each named inference engine's own
docs/repo -- not to this wiki-book's own VERIFIED/BEST-CURRENT
-UNDERSTANDING grounding, though both areas do apply that same two-tag
discipline internally, scoped to their own sources. That distinction is
restated inline at each new cluster's overview, the same discipline
Clusters 6-8's own overviews already hold to, and is not optional
context to drop when teaching from this page.

```mermaid
stateDiagram-v2
    [*] --> Slumberer
    Slumberer --> Gnostic: 2 modules, sequential
    Gnostic --> Demiurge: 55 modules, 5 core clusters + Clusters 6-7 (RAG, SDLC mechanics) + Clusters 9-10 (Models, Inference Engines)
    Demiurge --> Archon: 10 modules, design-space band + Cluster 8 (SDLC design-space)
    Archon --> [*]: primary sources beyond this book
    note right of Slumberer
        capstone: none (entry state)
    end note
    note right of Gnostic
        capstone: trace-a-request essay
        (abstract, no real harness yet)
    end note
    note right of Demiurge
        capstone: cross-harness mechanism
        comparison + operator config
        (or Cluster 6/7/9/10 variant)
    end note
    note right of Archon
        capstone: from-scratch harness
        design document
        (or Cluster 8 variant)
    end note
```

---

## Transition 1: Slumberer -> Gnostic

**Overview.** The Slumberer treats the harness as an undifferentiated
black box and debugs by rephrasing prompts; the cognitive shift this
transition asks for is the acquisition of a *vocabulary and a map* --
the learner stops asking "why did the model do that" and starts asking
"which stage of the loop produced that." This is a conceptual-only
transition: per `reader-proficiency-tiers.md`, a Gnostic can describe a
harness abstractly and correctly but has not yet traced that
description through any one harness's real, documented machinery --
that tracing is deferred to the next transition on purpose.

**Learning objectives.** By the end of this band, the learner can:
- State what a "harness" is as an engineering artifact distinct from
  the LLM it wraps, and name at least three things a harness typically
  adds (tool access, memory/instruction injection, permission gating).
- Place any given agent system on agent-topology.md's own axes:
  reactive vs. deliberative, single-agent vs. multi-agent,
  tool-augmented vs. fully autonomous.
- Describe the Thought/Action/Observation cycle and the ReAct pattern
  by name, and explain the while-loop framing of an agent's main loop.
- Explain the stop-and-parse distinction and contrast JSON-mode, code-
  generating, and native function-calling agents as three different
  ways a loop decides "the model wants to call a tool."
- Given a real, unlabeled transcript of an agent session, annotate
  which lines are Thought, which are Action, and which are Observation.

### Session breakdown (agenda only), Slumberer -> Gnostic

A pacing layer chunking this transition's two modules into three
schedulable teaching sessions (5/4/3 items respectively, sized so no
sitting is overloaded or too thin to be worth convening) now lives at
`resources/airchon-teacher/slumberer-to-gnostic-sessions.md`
-- moved there 2026-08-17, out of this page, since session-pacing for
actually running a course is scoped to `airchon-teacher`'s own domain
and is explicitly downstream work that agent doesn't do itself (see
its Constraints & Scope), not general wiki-book research content. This
page's learning objectives, modules, comprehension checks, and
exercises below are still the authoritative source that file's agendas
point back to -- it adds pacing, not new content.

### Module: A topology of agentic systems ([agent-topology.md](agent-topology.md))

**Key concepts:** reactive vs. deliberative agents; single-agent vs.
multi-agent systems as a topology axis (not yet the mechanics -- those
live in orchestration.md/fan-out.md/inter-agent-messaging.md in the next
band); the "LLM + tools + memory + planning" component decomposition,
and how it differs in scope from Anthropic's own narrower usage and
from the Hugging Face agents course's / Lilian Weng's broader ones.

**Comprehension check:** Name the four axes agent-topology.md uses to
classify an agentic system, and state which one distinguishes "a
chatbot with a calculator plugin" from "a fully autonomous coding
agent."

**Exercise:** Pick any AI coding tool you have personally used (an IDE
autocomplete plugin counts). Place it on all four of agent-topology.md's
axes and write two sentences justifying each placement.

### Module: The agent loop ([agent-loop.md](agent-loop.md))

**Key concepts:** the Thought/Action/Observation cycle and the ReAct
pattern; the while-loop framing (observations appended back into the
prompt, loop continues until a stop condition); the stop-and-parse
distinction between "the model emitted plain text" and "the model
emitted a structured tool call," and how JSON-mode, code-generating, and
function-calling agents each resolve that distinction differently.

**Comprehension check:** In the ReAct while-loop framing, what
specifically gets appended to the prompt after a tool executes, and why
does that step have to happen before the loop can produce its next
Thought?

**Exercise:** Take a real multi-step agent transcript (your own session
history, or a shared example) and rewrite it as an explicit
Thought/Action/Observation-labeled trace, one loop iteration per block,
stopping at the first point where the model's next action depended on
an observation from two iterations earlier.

### Capstone: trace-a-request essay (no real harness yet)

Write a 300-500 word abstract description of what happens between a
user typing a coding request and a tool call executing, using only the
vocabulary from these two pages (Thought/Action/Observation, ReAct,
while-loop, stop-and-parse, reactive/deliberative, single/multi-agent).
The essay must not name any concrete harness's actual config keys, file
paths, or tool names -- that concreteness is the next transition's job,
and reaching for it here is the most common way learners short-circuit
this capstone. A grader checks two things: (1) every loop-vocabulary
term is used correctly, and (2) the essay stays at the abstract level
agent-topology.md/agent-loop.md themselves stay at.

---

## Transition 2: Gnostic -> Demiurge

**Overview.** The Gnostic has the map but has never walked the real
terrain: this transition is where abstract loop vocabulary gets
attached to actual config keys, file paths, tool names, and named
limits inside a real harness. The cognitive shift is from "I can
describe a permission system" to "I can say which of Claude Code's six
permission modes a given `settings.json` block selects, and what
Copilot CLI's or OpenCode's equivalent looks like." Per
`reader-proficiency-tiers.md`, a Demiurge can also operate at
power-user/administrator depth (hooks, permission rules, MCP servers)
and compare the same mechanism across all three harnesses -- that
cross-harness comparison is the band's defining exercise shape, not an
optional extra. Per that same page's Demiurge-tier extension
subsections (added 2026-08-24, extended again 2026-09-03), this band
also now includes four further clusters sourced from outside the
wiki-book proper -- a RAG cluster (`references/rag/`), an
Agentic-SDLC practitioner-mechanics cluster (`references/sdlc/`), an
AI-model-classification cluster (`references/models/`), and a
local/self-hosted-inference-engines cluster
(`references/inference-engines/`) -- all four held to the
mechanics-depth bar this transition sets, but grounded "the source
says"/"the handbook says"/"the docs say" rather than this book's own
VERIFIED/BEST-CURRENT-UNDERSTANDING tagging (the model-classification
and inference-engines clusters apply that same two-tag shape
internally, just scoped to their own named sources rather than this
book's own); see `reader-proficiency-tiers.md`'s grounding-status
caveat for the exact wording this distinction should be taught with.

**Learning objectives.** By the end of this band, the learner can:
- For any of the five core clusters below, name the specific config
  key/file path/tool name each of Claude Code, Copilot CLI, and
  OpenCode uses for that mechanism, not just a generic description of
  the mechanism.
- Trace a single concrete request (e.g. "edit this file, hit a context
  limit, and confirm a shell command") through a real harness's actual
  documented machinery end to end, citing the specific limit or gate it
  crosses at each stage.
- Read one harness's real settings/config file and correctly explain
  what each key does and where it sits in that harness's precedence
  hierarchy.
- Distinguish mechanisms that are easy to conflate because they sit
  next to each other in the loop (e.g. context-compression.md's
  mid-run eviction vs. memory-management.md's compaction-survival vs.
  instruction-context-budget.md's eager-load budget) by naming which
  lifecycle stage each one actually operates at.
- Compare the same mechanism (memory, orchestration, permissions,
  retries, auth) across all three harnesses and state, with citations,
  where they genuinely converge and where they genuinely diverge.
- Build a real retrieve-then-generate pipeline and name, at the same
  parameter granularity as the five core clusters, the specific chunking
  strategy, embedding model, vector store, or reranker choice it makes
  and why (Cluster 6).
- Trace a primitive (rule file, skill, or agent persona) through the
  Agentic SDLC Handbook's own four-phase Resolve/Materialize/Bind
  /Activate lifecycle and name which phase a given failure ("the skill
  never activated") actually occurred in (Cluster 7).
- Classify a given model along all four of `references/models/`'s
  classification axes (task/pipeline type, parameter count and scale,
  dense vs. Mixture of Experts, quantization) and state one concrete
  cost or capability consequence of each classification (Cluster 9).
- Configure a named local inference engine's real CLI flags or
  environment variables to change one of its documented runtime
  behaviors (context-window size, GPU/CPU layer placement, batching
  concurrency) and explain, at the config-key level, what the change
  actually does (Cluster 10).

The 21-page core-mechanics band is grouped into five thematic clusters
below to make it navigable as a course, plus four extension clusters (6,
7, 9, and 10) covering the RAG, Agentic-SDLC-mechanics, AI-model
-classification, and local-inference-engine material described above.
The clusters are this page's own organizing device, not a
distinction drawn by the source pages themselves -- several pages
(session-persistence.md, memory-management.md) explicitly
cross-reference each other across cluster boundaries, and a course
built from this skeleton should preserve those cross-references rather
than teach the clusters as hermetically sealed units.

```mermaid
flowchart TB
    subgraph C1["Cluster 1: Memory and Context"]
        MM["memory-management.md"]
        ICB["instruction-context-budget.md"]
        CC["context-compression.md"]
        CACHE["caching.md"]
        SP["session-persistence.md"]
    end
    subgraph C2["Cluster 2: Coordination and Multi-Agent"]
        ORCH["orchestration.md"]
        HM["handoff-mechanism.md"]
        FO["fan-out.md"]
        IAM["inter-agent-messaging.md"]
    end
    subgraph C3["Cluster 3: Transport and API"]
        LLMAPI["llm-api-contract.md"]
        STREAM["streaming-and-incremental-rendering.md"]
        RETRY["retries.md"]
        ROUTE["model-routing-and-selection.md"]
    end
    subgraph C4["Cluster 4: Config and Permissions"]
        CONF["configuration.md"]
        PERM["permissions-and-sandboxing.md"]
        HOOKS["hooks-lifecycle-extensibility.md"]
        AUTH["auth-and-usage-accounting.md"]
    end
    subgraph C5["Cluster 5: Skills and Tools"]
        BT["built-in-tools.md"]
        BS["built-in-skills.md"]
        MCP["mcp-integration.md"]
        ALI["agent-loop-implementations.md"]
    end
    subgraph C6["Cluster 6: RAG (references/rag/)"]
        RF["foundations.md"]
        RB["basic-rag-pipeline.md"]
        RA["advanced-rag-techniques.md"]
        RV["vector-store-integrations.md"]
        RS["semantic-caching.md"]
        RG["structured-generation-for-rag.md"]
        RE["rag-evaluation.md"]
        RL["agentic-rag-with-llamaindex.md"]
        RH["heterogeneous-data-sources.md"]
    end
    subgraph C7["Cluster 7: Agentic SDLC practitioner mechanics (references/sdlc/)"]
        S04["04-the-reference-architecture.md"]
        S11["11-the-runtime-machine.md"]
        S12["12-the-instrumented-codebase.md"]
        S14["14-the-load-lifecycle.md"]
        S15["15-attention-and-context-economy.md"]
        S21["21-primitives-as-code.md"]
        SA["appendix-a-cross-harness-reference.md"]
    end
    subgraph C9["Cluster 9: AI model classification (references/models/)"]
        MT["model-terminology.md"]
        MTP["task-and-pipeline-classification.md"]
        MPS["parameter-count-and-scale.md"]
        MMOE["mixture-of-experts-and-frankenmerging.md"]
        MQ["quantization.md"]
    end
    subgraph C10["Cluster 10: Local/self-hosted inference engines (references/inference-engines/)"]
        IFF["model-file-formats.md"]
        IML["memory-mapped-model-loading.md"]
        IQ["quantization-at-inference-time.md"]
        IKV["kv-cache-and-context-window-management.md"]
        ISD["sampling-and-decoding-parameters.md"]
        IB["batching-and-continuous-batching.md"]
        IOF["cpu-gpu-heterogeneous-offloading.md"]
        IMG["multi-gpu-and-tensor-parallelism.md"]
        ISP["speculative-decoding.md"]
        ISA["server-api-modes.md"]
        IMD["model-management-and-distribution.md"]
        ILC["llama-cpp.md"]
        IOL["ollama.md"]
        IKT["ktransformers.md"]
    end
    C1 --> C2 --> C3 --> C4 --> C5 --> C6 --> C7 --> C9 --> C10
```


### Session breakdown (agenda only), Gnostic -> Demiurge

A pacing layer chunking this transition's 21 modules into 27
schedulable teaching sessions (organized around the five clusters
above: one session per module, plus one per-cluster synthesis session,
plus a final capstone session) now lives at
`resources/airchon-teacher/gnostic-to-demiurge-sessions.md`
-- scoped to `airchon-teacher`'s own domain rather than kept as general
wiki-book content, the same reasoning and the same day's precedent as
Transition 1's session breakdown (see that transition's own pointer
paragraph above and `CHANGELOG.md`). This page's learning objectives,
clusters, modules, comprehension checks, exercises, and capstone below
remain the authoritative source that file's agendas point back to -- it
adds pacing, not new content. **Note (2026-08-24, still current
2026-09-03):** that pacing file's 27-session count was set before
Clusters 6, 7, 9, and 10 below existed and covers only the original
five-cluster/21-module band; a future pacing pass on that file (out of
scope for this page, per `airchon-teacher`'s own domain boundary) is
needed to fold in session agendas for the RAG, Agentic-SDLC-mechanics,
AI-model-classification, and local-inference-engine clusters this page
now documents.

### Cluster 1: Memory & Context

**Cluster overview:** how instructions get loaded eagerly, how a live
run's context gets shrunk when it fills up, how a completed session
survives a process restart, and how a server reuses a previously-sent
prefix instead of resending it -- four operations on the same resource
(the context window) that are easy to conflate and that these five
pages deliberately keep apart.

#### Module: Memory management ([memory-management.md](memory-management.md))

**Key concepts:** instruction-file hierarchies (e.g. `CLAUDE.md` load
order); Claude Code's auto-memory vs. Copilot's server-side Copilot
Memory; injection timing and compaction-survival (what memory content
does or does not survive a compaction event).

**Comprehension check:** What is the practical difference between
memory content that is "eagerly loaded" and memory content that is
"reloaded on edit," and which of the two does this page document as
mid-session-edit-aware?

**Exercise:** Pick one harness's memory-file mechanism documented on
this page. Write a memory file that intentionally tests the load-order
rule the page describes (e.g. a project-level file meant to override a
user-level one) and predict which content wins before checking the
harness's actual behavior.

#### Module: Instruction context budget ([instruction-context-budget.md](instruction-context-budget.md))

**Key concepts:** why `@`-style imports don't reduce eager-load cost;
path-scoped rules (`paths:`) vs. `applyTo:` as two harnesses' answers to
the same scoping problem; skills as the invoke-only (lazy-load) tier
contrasted with the eager-load tier.

**Comprehension check:** Name one lever each harness offers for
trimming what loads eagerly into the budget, and explain why moving
content into a skill changes its loading cost.

**Exercise:** For a harness of your choice, measure (using the
mechanism this page documents for "how to measure what loaded") how
much of your actual context budget a real project's instruction files
consume, then propose one concrete change to reduce it without losing
information.

#### Module: Context compression ([context-compression.md](context-compression.md))

**Key concepts:** mid-run compression as distinct from eager-load
budget and from compaction-survival; Claude Code's evict-then-summarize
two-phase mechanism and its auto-compact default; OpenCode's
source-verified `prune()`/`process()` pipeline.

**Comprehension check:** At what proportion of context capacity does
each harness this page documents trigger its compression mechanism, and
what does "evict-then-summarize" mean as opposed to "summarize
everything"?

**Exercise:** Deliberately drive a real session past a documented
compression trigger point (e.g. by pasting large file contents
repeatedly) and record, turn by turn, what the harness evicted first
versus what it preserved as summary.

#### Module: Caching ([caching.md](caching.md))

**Key concepts:** server-side prefix reuse as distinct from compression
(shrinking) and memory loading; cache scope and TTL-by-auth-path;
subagent/fork cache-inheritance behavior.

**Comprehension check:** Name one action documented on this page that
invalidates a cache and one that preserves it, and explain why editing
an early system-prompt section is more expensive than appending a new
user message.

**Exercise:** For one harness, construct two versions of the same
session -- one that only appends new turns, one that edits an early
turn -- and use the harness's own token/cost accounting to observe the
cache-hit difference this page predicts.

#### Module: Session & transcript persistence ([session-persistence.md](session-persistence.md))

**Key concepts:** single-session durability across process restarts, as
distinct from mid-run compaction-survival and agent-to-agent handoff;
what a `--resume`/`--continue`-style command actually restores vs.
leaves behind; fork/branch semantics vs. an in-place undo mechanism.

**Comprehension check:** For one harness this page documents, name the
literal file path or storage backend a session transcript is written
to, and state one thing a resume command does *not* restore.

**Exercise:** Kill a real harness process mid-session (not gracefully
exit it), then use its documented resume mechanism to recover. Compare
what actually came back against what this page's own documentation
predicted would and wouldn't survive.

### Cluster 2: Coordination & Multi-Agent

**Cluster overview:** once a task needs more than one agent, four
separable questions arise -- who holds the overall plan, how a new
agent gets spawned and what crosses that spawn boundary, how many
agents run concurrently and how that's throttled, and what wire format
agents use to talk to each other once running. Each of these four pages
answers exactly one of those questions.

#### Module: Orchestration ([orchestration.md](orchestration.md))

**Key concepts:** the general orchestrator/manager-agent concept; Claude
Code's turn-by-turn model vs. its script-held Dynamic-workflows plan
(`agent()`/`pipeline()`); Copilot CLI's `/fleet` orchestrator agent;
OpenCode's primary-agent/subagent taxonomy.

**Comprehension check:** What is the difference between a
"turn-by-turn" orchestration model and a "script-held plan" model, and
which harness/feature pair on this page instantiates each?

**Exercise:** Design (on paper, no code required) a script-held plan for
a 3-stage task using the `agent()`/`pipeline()` primitives this page
documents, and identify where in your plan the documented
concurrency/total-agent cap would bind.

#### Module: Handoff mechanism ([handoff-mechanism.md](handoff-mechanism.md))

**Key concepts:** agent-to-agent context transfer specifically (not
compaction survival); Claude Code's fresh-context subagents vs. named
resumeable ones; OpenCode's `Task` tool (`session.create(parentID)`,
`task_id` resume).

**Comprehension check:** When Claude Code spawns a subagent, does that
subagent start with a fresh context or an inherited one, and what
mechanism resumes it later?

**Exercise:** Spawn a real subagent/subtask in one harness this page
documents, deliberately give it a task that requires information from
the parent's context, and observe exactly what did and didn't cross
the handoff boundary.

#### Module: Fan-out (subagent dispatch) ([fan-out.md](fan-out.md))

**Key concepts:** launch mechanics distinct from handoff (what crosses)
and orchestration (who holds the plan); Claude Code's three distinct
fan-out layers with their concurrency/depth caps; OpenCode's
`FiberSet`-based concurrent dispatch.

**Comprehension check:** Name the three distinct fan-out layers this
page documents for Claude Code, and state which one has no documented
hard concurrency cap.

**Exercise:** Trigger a real parallel-subagent dispatch in one harness
and count how many ran concurrently against the documented cap; if the
harness lets you exceed the apparent default, identify which config key
you changed to do it.

#### Module: Inter-agent messaging ([inter-agent-messaging.md](inter-agent-messaging.md))

**Key concepts:** the wire format/transport once agents are already
talking; Claude Code's `SendMessage` tool and file-based mailbox;
OpenCode's finding of no dedicated inter-agent message type at all
(ordinary message rows over the same SSE bus).

**Comprehension check:** Contrast Claude Code's messaging architecture
with OpenCode's on this page: which one has a dedicated addressed
mailbox, and which one treats agent-to-agent communication as
indistinguishable from any other session event?

**Exercise:** For a harness with a documented peer-to-peer channel,
construct a two-agent scenario where one agent must wait on a
structured protocol message (e.g. a shutdown or plan-approval message)
from the other, and trace the message through the mechanism this page
documents.

### Cluster 3: Transport & API

**Cluster overview:** the wire-level layer every other cluster assumes
already works -- how a single outbound model request is framed, how it
streams back, how failure on that single request gets retried, and how
the harness picks which model answers a given step.

#### Module: The LLM API contract ([llm-api-contract.md](llm-api-contract.md))

**Key concepts:** Anthropic's Messages API (`tool_use`/`tool_result`
blocks, the `stop_reason` enumeration, the SSE event sequence); OpenAI's
Responses API (`tool_calls`/`call_id`, `finish_reason`); OpenCode's
source-verified `Protocol`/`Endpoint`/`Auth`/`Framing` route
decomposition unifying both.

**Comprehension check:** Name the SSE event sequence Anthropic's
Messages API emits from `message_start` to `message_stop`, and identify
which event carries an in-progress tool-call argument delta.

**Exercise:** Capture a raw streamed API response from one documented
provider (via a debug/verbose flag if the harness exposes one) and
manually annotate each SSE event against this page's own event
taxonomy.

#### Module: Streaming & incremental rendering ([streaming-and-incremental-rendering.md](streaming-and-incremental-rendering.md))

**Key concepts:** the client/UI-side layer above the wire-level SSE
contract; buffering/reassembly/pacing discipline; Claude Code's
delta-coalescing history as a concrete performance-engineering example.

**Comprehension check:** Why does this page distinguish "reassembly at
the JSON-parsing level" from "buffering and pacing," and does any
harness this book covers attempt to parse a genuinely incomplete
tool-call JSON object mid-stream?

**Exercise:** Force a slow/degraded network condition against a real
harness session and observe how its rendering degrades -- does it
buffer visibly, coalesce deltas, or fail to reassemble -- and map the
observed behavior back to a mechanism this page names.

#### Module: Retries ([retries.md](retries.md))

**Key concepts:** failure recovery on a single outbound request, as
distinct from context-overflow handling and cache-prefix reuse; Claude
Code's `CLAUDE_CODE_MAX_RETRIES`/retry-vs-not category list; OpenCode's
two-layer transport-retry-wrapped-by-whole-turn-retry architecture.

**Comprehension check:** What is the practical difference between
OpenCode's bounded transport retry and its wrapping whole-turn retry
this page documents, and which of the two is described as effectively
uncapped?

**Exercise:** Deliberately induce a retryable failure (e.g. hit a rate
limit or kill network briefly) against a real harness and observe how
many attempts it makes and at what backoff interval, comparing against
the documented default.

#### Module: Model routing / selection ([model-routing-and-selection.md](model-routing-and-selection.md))

**Key concepts:** which underlying model answers a given step; Claude
Code's four-tier session-model precedence stack; Copilot CLI's Auto
model selection two-system router; OpenCode's `defaultModel()`
startup-resolution algorithm.

**Comprehension check:** For one harness this page documents, list its
model-selection precedence order from highest to lowest priority, and
name one config key or flag at each level.

**Exercise:** Override a harness's model selection at two different
precedence levels simultaneously (e.g. an env var and a settings file)
and verify which one actually wins, against this page's documented
precedence order.

### Cluster 4: Config & Permissions

**Cluster overview:** the general settings/config-file system, the
enforcement architecture that turns permission rules into actual
runtime gates, the mechanism for user-side code to sit inside the
loop's control flow, and how identity/spend get tracked and enforced.

#### Module: Configuration ([configuration.md](configuration.md))

**Key concepts:** Claude Code's four-scope `settings.json` hierarchy
(Managed/User/Project/Local); Copilot CLI's `~/.copilot` layout and
precedence chain; OpenCode's `mergeConfigConcatArrays()` eight-source
merge order.

**Comprehension check:** For one harness, name its full config
precedence chain from highest to lowest authority, and identify one
documented exception to strict precedence (e.g. a merge rather than an
override).

**Exercise:** Set the same setting at two different scopes in one
harness's config hierarchy (e.g. a User-scope and a Project-scope
value) and confirm which one wins in practice, then locate the
documented merge exception if the setting is one that merges rather
than overrides.

#### Module: Permissions & sandboxing architecture ([permissions-and-sandboxing.md](permissions-and-sandboxing.md))

**Key concepts:** the enforcement architecture underneath the
permission-rule schema; Claude Code's OS-level sandboxed-Bash
two-layer (filesystem/network) design and its named escape hatches;
OpenCode's finding that it ships no OS-level sandbox at all.

**Comprehension check:** Name Claude Code's two independent sandbox
layers for its Bash tool and one documented escape hatch that
deliberately bypasses one of them.

**Exercise:** Configure the strictest permission mode a harness offers,
then deliberately attempt an action you expect to be denied (a
filesystem write outside an allowed directory, or a network call) and
document the exact denial message and which layer produced it.

#### Module: Hooks and lifecycle extensibility ([hooks-lifecycle-extensibility.md](hooks-lifecycle-extensibility.md))

**Key concepts:** the mechanism for user-side code to sit directly
inside the loop's control flow; Claude Code's ~30-event catalogue and
exit-code-2-only-blocks rule; OpenCode's two-surface plugin model
(generic `event` bus vs. typed `Hooks` interface functions).

**Comprehension check:** In Claude Code's hook model, what specific
exit code from a hook handler blocks the action it's attached to, and
what do other non-zero exit codes do instead?

**Exercise:** Write a real hook (in any one harness this page
documents) that fires on a tool-call lifecycle event and deliberately
blocks one specific tool invocation, then verify the block actually
happens and inspect what payload your hook received.

#### Module: Auth & usage accounting ([auth-and-usage-accounting.md](auth-and-usage-accounting.md))

**Key concepts:** API-key/OAuth handling and precedence; token/cost
tracking surfaces (e.g. `/usage`); the three genuinely distinct
budget-enforcement mechanisms this page documents at three different
layers (SDK-level, workflow-level, org-level).

**Comprehension check:** Name Claude Code's full authentication
precedence stack from highest to lowest priority, and identify which of
the three documented budget-enforcement layers is the only one that
counts subagent spend toward a shared cap.

**Exercise:** Configure two competing auth sources for one harness
(e.g. an API key env var and an OAuth login) and verify which one wins,
matching it against this page's documented precedence order.

### Cluster 5: Skills & Tools

**Cluster overview:** the tool surface itself, what ships as a
default-on skill vs. user-authored content, how MCP servers get
discovered/registered/invoked, and the harness-specific companion to
the general agent-loop page -- how the abstract loop actually gets
implemented in real code.

#### Module: Built-in tools ([built-in-tools.md](built-in-tools.md))

**Key concepts:** the full tool inventory per harness (Claude Code's
`tools-reference` table, Copilot CLI's permission-"kind" vocabulary,
OpenCode's `allow`/`ask`/`deny` model); the `Edit` tool's three-gate
check as a named concrete mechanism.

**Comprehension check:** What does "permission-required" mean as a
column in Claude Code's own tools-reference table, and name one tool
that requires it and one that doesn't.

**Exercise:** For one harness, enumerate every built-in tool it exposes
in a real session (via a documented introspection command if one
exists) and classify each as permission-required or not, checking your
classification against the page's own table.

#### Module: Built-in skills ([built-in-skills.md](built-in-skills.md))

**Key concepts:** what ships as a skill by default vs. user-authored
content; Claude Code's bundled-skill set and `disableBundledSkills`/
`skillOverrides` visibility controls; OpenCode's finding of no
confirmed bundled skills at all.

**Comprehension check:** Name two of Claude Code's bundled skills this
page documents, and state what `disableBundledSkills` controls.

**Exercise:** Disable one bundled skill in a harness that supports it,
confirm the skill is genuinely unavailable in a real session, then
re-enable it and confirm it returns.

#### Module: MCP integration ([mcp-integration.md](mcp-integration.md))

**Key concepts:** discovery/registration/invocation of MCP servers;
config formats and transports across harnesses; tool-calling semantics
once a server is registered.

**Comprehension check:** Name one config file format used to register
an MCP server in one harness this page documents, and describe the
transport it uses to actually talk to that server.

**Exercise:** Register a real MCP server (any publicly available one)
with one harness following this page's documented config format, and
verify its tools appear and are invocable in a live session.

#### Module: Agent loop implementations ([agent-loop-implementations.md](agent-loop-implementations.md))

**Key concepts:** the harness-specific companion to the general
agent-loop page; Claude Code's Agent SDK-documented loop (turns,
`max_turns`/`max_budget_usd`, compaction, parallel tool execution) vs.
OpenCode's source-verified loop (`packages/core/src/session/runner/max-steps.ts`).

**Comprehension check:** What does `max_turns` bound in Claude Code's
documented Agent SDK loop, and how does that differ from what
`max_budget_usd` bounds?

**Exercise:** Drive a real session past a documented turn or step limit
(Claude Code's `max_turns` or OpenCode's step-limit system-prompt
injection) and observe exactly what happens when the limit is hit --
does the loop halt, warn, or inject a new instruction?

### Cluster 6: Retrieval-Augmented Generation (`references/rag/`)

**Cluster overview:** how a real RAG pipeline is built, tuned, and
evaluated -- as opposed to how any one harness decides whether to use
retrieval at all, which is the Archon-tier
[context-retrieval-and-agentic-search.md](context-retrieval-and-agentic-search.md)'s
concern, not this cluster's. Every module below cites `references/rag/`
pages directly; those pages attribute their own claims to the
HuggingFace Cookbook notebooks and Lewis et al. (2020), not to this
wiki-book's own VERIFIED/BEST-CURRENT-UNDERSTANDING grounding.

#### Module: RAG foundations ([../rag/foundations.md](../rag/foundations.md))

**Key concepts:** Lewis et al.'s parametric/non-parametric memory split;
RAG-Sequence vs. RAG-Token; the HuggingFace Agents Course's agentic-RAG
reframing of retrieval as one callable tool among several rather than a
fixed pipeline stage.

**Comprehension check:** What does Lewis et al.'s abstract name as the
two problems that compound a language model's limited ability to
"access and precisely manipulate knowledge," and how does non-parametric
memory address each?

**Exercise:** Take a factual question your own knowledge is uncertain
on, answer it once from memory alone, then again after retrieving one
supporting document, and write two sentences on which of Lewis et al.'s
named failure modes (no provenance, stale knowledge) the second answer
actually fixed.

#### Module: The basic RAG pipeline ([../rag/basic-rag-pipeline.md](../rag/basic-rag-pipeline.md))

**Key concepts:** the introductory LangChain + Zephyr + FAISS pipeline
over GitHub issues; `GitHubIssuesLoader` -> `RecursiveCharacterTextSplitter`
-> embed -> retrieve -> prompt -> generate as the baseline shape every
later module varies.

**Comprehension check:** Why does the notebook's own worked example
("how do you combine multiple adapters?") fail when asked of the base
model with no retrieved context, and what specifically does retrieval
add back?

**Exercise:** Reproduce the basic pipeline's shape (loader, splitter,
embedder, retriever, generator) against a small corpus of your own
choosing, and identify which of the five stages you had to change to
fit your corpus's format.

#### Module: Advanced RAG techniques ([../rag/advanced-rag-techniques.md](../rag/advanced-rag-techniques.md))

**Key concepts:** the character-vs-token chunking trap (a
character-based `chunk_size` silently disagreeing with a tokenizer's
count); PaCMAP embedding-space visualization; ColBERTv2 cross-encoder
reranking via RAGatouille.

**Comprehension check:** Why does a plain `RecursiveCharacterTextSplitter`
with a character-based `chunk_size` risk producing chunks that overflow
an embedding model's actual token budget, and what fix does this page
document?

**Exercise:** Take the pipeline you built in the previous module, add a
reranking stage over its top-k retrieved results, and compare the
top-1 result before and after reranking on the same query.

#### Module: Vector store integrations ([../rag/vector-store-integrations.md](../rag/vector-store-integrations.md))

**Key concepts:** three notebooks swapping the retriever half of the
basic pipeline onto Milvus, Elasticsearch, and MongoDB Atlas while
holding the retrieve-then-generate shape constant.

**Comprehension check:** Name one production vector store this page
documents and the embedding model the corresponding notebook pairs it
with.

**Exercise:** Swap your own pipeline's in-memory vector index (FAISS or
similar) for one of the three production stores this page documents,
and note what changed at the retrieval-call site versus what stayed
identical.

#### Module: Semantic caching for RAG ([../rag/semantic-caching.md](../rag/semantic-caching.md))

**Key concepts:** cache placement (before retrieval, not before
generation); FAISS `IndexFlatL2` with a Euclidean distance threshold;
FIFO eviction.

**Comprehension check:** Why does this page's notebook place the
semantic cache before the retrieval step rather than before the final
LLM call, given that a RAG system has two expensive, repeatable steps?

**Exercise:** Add a semantic cache in front of your pipeline's retrieval
call, using a distance threshold of your choosing, and demonstrate a
cache hit on two differently-worded queries that carry the same intent.

#### Module: Structured generation for RAG ([../rag/structured-generation-for-rag.md](../rag/structured-generation-for-rag.md))

**Key concepts:** source-snippet highlighting as a provenance mechanism;
the naive JSON-prompting approach and where it breaks; Outlines'
logit-biasing constrained-decoding mechanism as the fix.

**Comprehension check:** What provenance problem, named back in
`foundations.md`, does this page's source-highlighting feature
concretely solve?

**Exercise:** Modify your pipeline's generation step to output a
structured answer object that names which retrieved chunk(s) the answer
draws from, using either prompting or a constrained-decoding library.

#### Module: RAG evaluation ([../rag/rag-evaluation.md](../rag/rag-evaluation.md))

**Key concepts:** synthetic QA-dataset generation from the knowledge
base itself; groundedness/relevance/standalone-ness critique agents as
a quality filter; an LLM-as-judge (GPT-4-style) scoring rubric.

**Comprehension check:** Name the three critique-agent scores this
page's pipeline filters a synthetic QA pair on, and what happens to a
pair that fails any one of them.

**Exercise:** Generate five synthetic QA pairs from your own pipeline's
knowledge base, critique each on this page's three axes, and run the
surviving pairs through an LLM-as-judge comparison of your pipeline's
answer against the synthetic "true" answer.

#### Module: Agentic RAG with LlamaIndex ([../rag/agentic-rag-with-llamaindex.md](../rag/agentic-rag-with-llamaindex.md))

**Key concepts:** LlamaIndex's Loading/Indexing/Querying three-phase
framing as an alternative vocabulary to LangChain's load/split/embed
/index/retrieve/prompt/generate; a fully local Ollama + Llama 2 +
`BAAI/bge-base-en-v1.5` stack chosen specifically to avoid an
OpenAI-by-default dependency.

**Comprehension check:** What does this page identify as LlamaIndex's
"OpenAI-by-default trap," and what concrete substitution does the
notebook make to avoid it?

**Exercise:** Rebuild your basic pipeline (or a subset of it) using
LlamaIndex instead of LangChain, and note which of its three named
phases (Loading/Indexing/Querying) corresponds to which of your original
pipeline's stages.

#### Module: RAG over heterogeneous data sources ([../rag/heterogeneous-data-sources.md](../rag/heterogeneous-data-sources.md))

**Key concepts:** Unstructured's partition-then-chunk pipeline for mixed
document formats (PDF, PPTX, EPUB, HTML) in one corpus; Jina Reranker v2
scoring whole SQL table schemas directly, with no vector index at all.

**Comprehension check:** Why does the SQL-backed notebook this page
documents skip the usual chunk-and-embed retrieval step entirely, and
what does it use instead?

**Exercise:** Pick one document in a format your existing pipeline
cannot currently ingest (a PDF, a PPTX, or similar), add it to your
knowledge base using Unstructured's partition-then-chunk approach this
page documents, and confirm the pipeline retrieves from it correctly.

### Cluster 7: Agentic SDLC practitioner mechanics (`references/sdlc/`)

**Cluster overview:** the Agentic SDLC Handbook's own instrumented
-codebase discipline -- primitive types, load modes, the four-phase
lifecycle, and the package/lockfile model that governs how markdown
files actually reach and influence a model's context, at the same
mechanics depth as Clusters 1-5, but sourced single-source from the
handbook ("the handbook says") rather than this wiki-book's own
cross-verified pages.

#### Module: The reference architecture and the runtime machine ([../sdlc/04-the-reference-architecture.md](../sdlc/04-the-reference-architecture.md), [../sdlc/11-the-runtime-machine.md](../sdlc/11-the-runtime-machine.md))

**Key concepts:** the Human/Agent/Platform three-layer participant
model (Ch. 4); the four parts of the agentic runtime machine --
Model/Harness/Agent Source Code/Client -- and "the harness is the
compiler" framing (Ch. 11); cross-harness file-naming incompatibility as
a direct consequence of the Agent Source Code layer having no shared
standard.

**Comprehension check:** In the "harness is the compiler" framing, what
plays the role of source code, and what plays the role of the compiled
artifact?

**Exercise:** Name one concrete cross-harness file-naming incompatibility
(e.g. `CLAUDE.md` vs. `AGENTS.md`) and explain, using the four-part
runtime-machine model, why the same markdown content still produces
different behavior in two harnesses despite meaning the same thing to a
human reader.

#### Module: The instrumented codebase ([../sdlc/12-the-instrumented-codebase.md](../sdlc/12-the-instrumented-codebase.md))

**Key concepts:** the seven primitive types (instructions, and six
others this page's own table covers); the five load modes (eager
preload, lazy on-demand, dispatcher-mediated, user-invoked,
event-driven); the instrumentation audit as a practice for converting
tacit team knowledge into structured, harness-loadable files.

**Comprehension check:** Name the five load modes this page documents,
and give one primitive type whose load mode is "eager preload, scoped by
`applyTo` glob."

**Exercise:** Pick a real convention from a codebase you know that only
lives "in the team's heads" (an unwritten pattern, a deprecated approach
to avoid), and write it up as one of the seven primitive types, choosing
the load mode that best matches when an agent should actually see it.

#### Module: The load lifecycle ([../sdlc/14-the-load-lifecycle.md](../sdlc/14-the-load-lifecycle.md))

**Key concepts:** the four-phase Resolve -> Materialize -> Bind ->
Activate pipeline; the three binding modes; the phantom-dependency and
bundle-leakage anti-patterns; the governing claim that "a skill... can
fail to bind -- and the harness will not tell you why."

**Comprehension check:** A skill with correct frontmatter, in the right
directory, with a sharp description, fails to activate with no error
message. Per this page's own vocabulary, which phase is the most likely
point of failure, and why does the fix rarely live in the skill file
itself?

**Exercise:** Take a primitive you wrote in the previous module's
exercise and trace it explicitly through all four phases, naming which
tool or actor owns each phase and how many times per session/install
each phase runs.

#### Module: Attention and context economy ([../sdlc/15-attention-and-context-economy.md](../sdlc/15-attention-and-context-economy.md))

**Key concepts:** window (hard token ceiling) vs. attention (a smaller,
position-sensitive effective-focus cache); context rot and attention
starvation as two distinct silent-failure modes; the U-shaped attention
curve (citing Liu et al.'s "Lost in the Middle" and Anthropic's
needle-in-a-haystack evaluations).

**Comprehension check:** What is the difference between "an instruction
the model has read" and "an instruction the model has seen," per this
page's own governing claim, and which of the two does attention
starvation describe?

**Exercise:** Construct a test prompt that places one explicit,
technically-in-scope instruction in the middle of a long document, run
it against a real model, and check whether the instruction was followed
-- then repeat with the same instruction moved to the start or end and
compare.

#### Module: Primitives as code ([../sdlc/21-primitives-as-code.md](../sdlc/21-primitives-as-code.md))

**Key concepts:** the package model (one skill = one Module/Facade, a
bundle = a Composite, a dependency edge = a Package Reference); the
lockfile pinning a resolved dependency graph by content hash;
overrides and versioning as the mechanism that keeps two teams' shared
content from drifting apart.

**Comprehension check:** In this page's opening scenario, two skills
disagree about a shared review checklist. What structural problem, per
this page's own diagnosis, caused the disagreement, and how does
treating the checklist as a package (rather than embedding it in each
skill) fix it?

**Exercise:** Take two primitives you have written (in this cluster's
earlier exercises or elsewhere) that share some content, and refactor
that shared content into a single declared dependency both primitives
reference, rather than each embedding its own copy.

#### Module: Appendix A, the cross-harness reference ([../sdlc/appendix-a-cross-harness-reference.md](../sdlc/appendix-a-cross-harness-reference.md))

**Key concepts:** the master comparison table mapping ten APM primitive
concepts (project-wide rules, scope-attached rules, personas, skills,
hooks, MCP config, session compaction, and others) to their concrete
file/config convention across five harnesses (Copilot, Claude Code,
Cursor, Codex CLI, OpenCode).

**Comprehension check:** Pick one row of this page's master table (e.g.
"project-wide rules") and name the concrete file/path convention it
gives for two different harnesses.

**Exercise:** Extend this page's own table with one additional row for
a primitive concept it does not cover, filling in the concrete
file/config convention for at least three of the five harnesses,
citing where you found or verified each cell.

### Cluster 9: AI model classification (`references/models/`)

**Cluster overview:** how a model is classified along four largely
independent axes -- what it's for, how big it is, how its parameters
are internally organized, and at what numeric precision it actually
runs -- at the same specific, mechanics-grade depth as Clusters 1-5,
but sourced from Hugging Face's own documentation and a named community
writeup rather than from a shipped agent harness. Every module below
cites `references/models/` pages directly; those pages attribute their
own claims to the Hugging Face Hub/`transformers`/Optimum documentation
and Maxime Labonne's frankenMoE blog post, applying that same-shaped
VERIFIED/BEST-CURRENT-UNDERSTANDING discipline internally but scoped to
that named corpus, not to this wiki-book's own `references/harnesses/`
sources.

#### Module: Model terminology ([../../references/models/model-terminology.md](../../references/models/model-terminology.md))

**Key concepts:** the pretrained/fine-tuned/LLM distinction; encoder,
decoder, and encoder-decoder (seq2seq) architectures; causal vs. masked
language modeling; tokens, input IDs, and attention masks; a model's
backbone vs. its task-specific head; feature-extraction and multimodal
terminology.

**Comprehension check:** What is the difference between a model's
backbone and a task-specific head, and why does swapping a head for a
new task not require retraining the backbone from scratch?

**Exercise:** Take a text-generation model you have used and identify,
from its model card or config, whether it is decoder-only, encoder-only,
or encoder-decoder, and explain what causal vs. masked language modeling
has to do with that architectural choice.

#### Module: Task and pipeline classification ([../../references/models/task-and-pipeline-classification.md](../../references/models/task-and-pipeline-classification.md))

**Key concepts:** the Hub's task/pipeline-tag taxonomy across
NLP/Vision/Audio/Multimodal/Tabular/RL categories; `text-generation` as
an agent's own reasoning loop; `feature-extraction`/`sentence-similarity`
for embeddings, RAG, and semantic routing/caching; `summarization` for
context compaction; `text-classification`/`token-classification` for
routing, guardrails, and entity extraction.

**Comprehension check:** Which Hub task tag would you reach for to build
a semantic cache or a RAG retriever, and why is that a different task
type than the one powering the agent's own reasoning loop?

**Exercise:** For an agent-harness feature of your choosing (a
context-compaction step, a routing/guardrail check, or a RAG retriever),
name the specific Hub task/pipeline tag this page documents as the right
fit, and explain why a different tag on this page's own list would be a
worse fit.

#### Module: Parameter count and scale ([../../references/models/parameter-count-and-scale.md](../../references/models/parameter-count-and-scale.md))

**Key concepts:** what a parameter is; the `7B`/`13B`/`70B` naming
convention; the verified `~4*X GB` (float32)/`~2*X GB` (bfloat16
/float16) VRAM rule of thumb; the KV cache as a second,
context-length-dependent memory cost distinct from weight VRAM
(MQA/GQA as mitigations); small/mid-scale/frontier-hosted capability
-tier tradeoffs.

**Comprehension check:** Using this page's VRAM rule of thumb, roughly
how much VRAM does a 13B-parameter model need at bfloat16, and why does
an agent's growing session context add a second, separate memory cost on
top of that number?

**Exercise:** Pick a real model you could run locally and a target
context length for an agent session, and compute, from this page's own
worked examples, both its weight VRAM cost and roughly how its KV cache
cost would grow as that context fills.

#### Module: Mixture of Experts and frankenMoE ([../../references/models/mixture-of-experts-and-frankenmerging.md](../../references/models/mixture-of-experts-and-frankenmerging.md))

**Key concepts:** sparse MoE layers and the gate/router network;
`num_local_experts` vs. `num_experts_per_tok`; the frankenMoE-vs
-native-MoE training-methodology distinction; MergeKit's three
router-initialization methods (random, cheap_embed, hidden); the
memory-vs-speed-vs-knowledge-preservation tradeoffs; the worked
Beyonder-4x7B-v3 example.

**Comprehension check:** What does `num_experts_per_tok` actually bound,
and why does a sparse MoE model's active-parameter count at inference
time differ from its total parameter count?

**Exercise:** Using this page's three router-initialization methods,
argue which one you'd choose for merging four already-fine-tuned dense
models into a frankenMoE, and why the other two would serve that goal
worse.

#### Module: Quantization ([../../references/models/quantization.md](../../references/models/quantization.md))

**Key concepts:** the definition and motivation for quantization;
float16/bfloat16/int16/int8 formats; the affine and symmetric int8
quantization schemes; per-tensor vs. per-channel granularity; the three
calibration approaches (dynamic PTQ, static PTQ, QAT); a concrete worked
VRAM example (29 GB to 15 GB to 9.5 GB across bf16/int8/int4) and its
accompanying inference-speed tradeoff.

**Comprehension check:** What is the practical difference between
per-tensor and per-channel quantization granularity, and which one does
this page document as generally preserving more accuracy at the same
bit-width?

**Exercise:** Using this page's own worked VRAM example as a template,
pick a real model you have access to, quantize it (or work through the
arithmetic if your hardware can't run it) at two of the three precisions
this page compares, and record the actual or computed memory and speed
difference.

### Cluster 10: Local/self-hosted inference engines (`references/inference-engines/`)

**Cluster overview:** how a model actually gets loaded, quantized,
cached, batched, offloaded, and served once it is running on hardware
you (rather than a hosted API provider) control -- eleven engine
-agnostic mechanisms followed by three per-engine implementation pages
(llama.cpp, Ollama, KTransformers), at the same specific, mechanics
-grade depth as Clusters 1-5, but sourced from each engine's own
documentation or repository. Every module below cites
`references/inference-engines/` pages directly; several of those pages
in turn cross-link Cluster 9's own quantization and Mixture-of-Experts
pages rather than re-deriving those concepts, so this cluster assumes
Cluster 9 has already been covered.

#### Module: Model file formats for inference ([../../references/inference-engines/model-file-formats.md](../../references/inference-engines/model-file-formats.md))

**Key concepts:** why a training-checkpoint format and an
inference-serving format solve different problems; GGUF's predecessors
(GGML/GGMF/GGJT) and the architecture-identification failure they had;
GGUF's four-section layout (header, typed/namespaced metadata KV pairs,
tensor infos, tensor data); the per-tensor `ggml` type enumeration.

**Comprehension check:** What specific failure did GGUF's predecessor
formats have that GGUF's own metadata section fixes, and why does that
failure matter for a harness that treats "swap the local model" as a
cheap operation?

**Exercise:** Inspect a real GGUF file's metadata with a documented tool
this page names or points to, and identify at least three distinct
tensor precisions mixed within the same file.

#### Module: Memory-mapped model loading ([../../references/inference-engines/memory-mapped-model-loading.md](../../references/inference-engines/memory-mapped-model-loading.md))

**Key concepts:** `mmap`-based loading trading a full-file copy for
lazy, page-cache-backed loading; GGUF's alignment requirement as the
structural precondition that makes it possible; the `auto`/`mmap`
/`mlock`/`mmap+mlock`/`dio` load-mode surface; the load-speed-vs
-pageout-risk tradeoff each mode makes.

**Comprehension check:** Why does mmap-based loading specifically
require GGUF's alignment guarantee to work correctly, and what risk does
`mlock` exist to close?

**Exercise:** Load the same model twice under two different load modes
this page documents, and compare the wall-clock time to first token and
(if observable) memory behavior between the two runs.

#### Module: Quantization as an inference-engine-level concern ([../../references/inference-engines/quantization-at-inference-time.md](../../references/inference-engines/quantization-at-inference-time.md))

**Key concepts:** how an engine *consumes*, rather than produces, an
already-quantized tensor (cross-linking Cluster 9's own quantization
module); why dequantization happens inline, per weight block, at
compute time rather than once at load time; GGUF's mixed-per-tensor
-precision consequence; KV-cache quantization and offload placement as
runtime knobs that compose with a fixed weight quantization.

**Comprehension check:** Why does "the model file is quantized" not
automatically mean "inference is faster," per this page's own account of
when dequantization actually happens?

**Exercise:** Run the same prompt against a model at two different
KV-cache quantization settings this page documents, and record any
difference in memory use, speed, or output quality you observe.

#### Module: The KV cache and context-window management ([../../references/inference-engines/kv-cache-and-context-window-management.md](../../references/inference-engines/kv-cache-and-context-window-management.md))

**Key concepts:** why KV-cache cost scales with context length rather
than model size; context-window sizing as an explicit, VRAM-aware
setting; the documented call-out that agentic workloads need a
larger-than-default window; KV-cache quantization as a precision axis
independent of weight quantization.

**Comprehension check:** Why does this page treat KV-cache size as a
per-session cost distinct from the model's own weight VRAM cost, and
what documented setting controls it directly?

**Exercise:** Configure a local engine's context-window size to a value
this page's own documentation calls out as agent-workload-appropriate,
and observe, via a memory/usage surface the engine exposes, how the KV
cache's memory footprint changes as a long agent session fills that
window.

#### Module: Sampling and decoding parameters ([../../references/inference-engines/sampling-and-decoding-parameters.md](../../references/inference-engines/sampling-and-decoding-parameters.md))

**Key concepts:** the shared core parameter set (`temperature`, `top_k`,
`top_p`, `repeat_penalty`/`repeat_last_n`, `seed`, `num_predict`,
`stop`); grammar-constrained decoding (GBNF) as a token-masking
mechanism distinct from reweighting, and its automatic
JSON-Schema-to-grammar conversion; why this mechanism, not the chat
template alone, is what makes a `tools` array reliably yield parseable
`tool_calls`.

**Comprehension check:** What is the mechanistic difference between a
sampling parameter like `top_p` and a grammar constraint like GBNF, and
why does only the latter guarantee syntactically valid output?

**Exercise:** Define a JSON Schema for a tool call, let the engine
convert it to a grammar per this page's documented mechanism, and
confirm decoding under that grammar never produces an unparseable
tool-call payload across several runs.

#### Module: Batching and continuous batching ([../../references/inference-engines/batching-and-continuous-batching.md](../../references/inference-engines/batching-and-continuous-batching.md))

**Key concepts:** why memory-bandwidth-bound single-token decoding makes
batching valuable; the slot-based continuous-batching design
(`--parallel`/`--batch-size`/`--ubatch-size`); why continuous batching,
not a static batch, is what actually captures that benefit under real,
staggered request arrival.

**Comprehension check:** Why does a static batch fail to capture the
same throughput benefit continuous batching does, under real, staggered
request arrival?

**Exercise:** Fire several concurrent requests at a locally served model
with continuous batching enabled, and compare observed throughput
against the same requests sent one at a time.

#### Module: CPU/GPU/heterogeneous offloading, and expert offloading ([../../references/inference-engines/cpu-gpu-heterogeneous-offloading.md](../../references/inference-engines/cpu-gpu-heterogeneous-offloading.md))

**Key concepts:** layer-granularity `--gpu-layers`/`--device` hybrid
inference as the general-purpose default; why that granularity cannot
avoid holding every MoE expert in memory at once (cross-linking Cluster
9's own MoE module); arithmetic-intensity-guided offloading (the ~512
-vs-~0.075 MLA-vs-expert figures) as the finer-than-layer strategy that
makes a 671B-parameter MoE model locally deployable at all.

**Comprehension check:** Why can't a plain layer-granularity offloading
scheme avoid loading every expert of an MoE model into memory at once,
and what finer-grained strategy does this page document to get around
that?

**Exercise:** Using a model too large for your available VRAM, configure
layer-granularity offloading to split it across CPU and GPU, and record
which layer count is the largest you can offload to GPU before running
out of memory.

#### Module: Multi-GPU inference ([../../references/inference-engines/multi-gpu-and-tensor-parallelism.md](../../references/inference-engines/multi-gpu-and-tensor-parallelism.md))

**Key concepts:** `--split-mode layer` (throughput-oriented, tolerant of
slow interconnects) vs. `--split-mode tensor` (experimental,
latency-oriented, needs a fast interconnect); the `--tensor-split`
/`--main-gpu` configuration surface; how this composes with, rather than
replaces, expert-placement strategy.

**Comprehension check:** Which of this page's two split modes would you
choose for a throughput-seeking multi-agent harness fanning out many
concurrent requests, and which for a single latency-critical interactive
loop, and why?

**Exercise:** If you have access to two or more GPUs, run the same model
under both split modes this page documents and compare tokens/sec and
per-request latency between them.

#### Module: Speculative decoding ([../../references/inference-engines/speculative-decoding.md](../../references/inference-engines/speculative-decoding.md))

**Key concepts:** the draft-then-verify-in-one-batch mechanism as a pure
latency optimization with no output-distribution change; the
model-based (draft model, EAGLE-3, DFlash, DSpark) and pattern-based
(n-gram family) drafter taxonomy; why payoff is entirely
acceptance-rate-dependent; the two agent-harness workload shapes that
line up well with it (context-echoing generation; an already-resident
small model repurposed as a draft model).

**Comprehension check:** Why does this page insist speculative decoding
changes no output distribution, only latency -- what property of the
verify step guarantees that?

**Exercise:** Enable speculative decoding with a draft model or n-gram
drafter this page documents, and measure the acceptance rate and latency
improvement on a context-echoing task (e.g. summarizing a document
already in context) versus a task with little textual overlap.

#### Module: Server/API modes ([../../references/inference-engines/server-api-modes.md](../../references/inference-engines/server-api-modes.md))

**Key concepts:** one-shot CLI invocation vs. a persistent server
process; what "OpenAI-compatible" concretely covers and where each
engine's own documented compatibility gaps are; native implementation of
the same endpoint family; why concurrency-aware serving (batching), not
the API shape alone, is what actually delivers the throughput a harness
integration is really after.

**Comprehension check:** Why does this page argue that an
OpenAI-compatible API surface alone is not what delivers throughput to a
harness integration, and what mechanism from an earlier module actually
does?

**Exercise:** Point a harness or client that speaks the OpenAI API shape
at a locally served engine's OpenAI-compatible endpoint, and identify
one documented compatibility gap you actually hit or would need to work
around.

#### Module: Model management and distribution ([../../references/inference-engines/model-management-and-distribution.md](../../references/inference-engines/model-management-and-distribution.md))

**Key concepts:** direct-file-path/Hugging-Face-reference model loading;
a name/manifest/Modelfile-build layer on top of the same GGUF ecosystem
(`pull`/`create`/`show`/`rm`, Modelfile-as-Dockerfile-analogue); a
curated registry for a run-shortcut command; which of the documented
responsibility splits best fits reproducible, inspectable per-persona
model configuration.

**Comprehension check:** What does this page's Modelfile-as-Dockerfile
analogy actually mean, and what specifically does a Modelfile let you
version that a bare model file path does not?

**Exercise:** Write a Modelfile, or the equivalent manifest this page
documents, that pins a specific model, a specific system prompt, and
specific sampling parameters together as one named, reproducible unit,
and confirm two different invocations of that name produce the pinned
configuration.

#### Module: llama.cpp ([../../references/inference-engines/llama-cpp.md](../../references/inference-engines/llama-cpp.md))

**Key concepts:** project goals and hardware-backend breadth (Apple
Silicon, x86, RISC-V, CUDA/HIP/MUSA/Vulkan/SYCL and more); the `llama
cli`/`llama serve` binaries; the K-quant/I-quant GGUF quantization-type
naming families and the `Q4_K_M` default recommendation; Ollama's own
documented dependency on llama.cpp as its backend; the convenience-vs
-hardware-breadth tradeoff of choosing it directly.

**Comprehension check:** What does choosing llama.cpp directly, rather
than a wrapper built on top of it, trade away and what does it gain, per
this page's own account?

**Exercise:** Download or convert a model to GGUF, run it directly via
llama.cpp's own CLI or server binary at the `Q4_K_M` quantization this
page recommends as a default, and record the concrete command and flags
you used.

#### Module: Ollama ([../../references/inference-engines/ollama.md](../../references/inference-engines/ollama.md))

**Key concepts:** the confirmed llama.cpp dependency, held alongside
Ollama's newer, directly-`ggml`-based Go engine built for multimodal
architectures; the full Modelfile instruction set; documented
GPU-vendor support and VRAM-based automatic scheduling; the dual
native-REST and OpenAI-compatible API surfaces; first-party integrations
with named coding-agent harnesses.

**Comprehension check:** Why does Ollama maintain two separate backends
(llama.cpp and its own Go engine) rather than one, per this page's own
account of what each is for?

**Exercise:** Pull a model via Ollama, write a Modelfile that customizes
its system prompt or parameters, and confirm which of the two backends
this page documents actually served your request (or reason through
which one should have, given the model's architecture).

#### Module: KTransformers ([../../references/inference-engines/ktransformers.md](../../references/inference-engines/ktransformers.md))

**Key concepts:** what the project is today (`kt-kernel`/`sglang-kt`
serving, LLaMA-Factory-integrated LoRA fine-tuning), held explicitly
apart from its upstream repository's own documented YAML
operator-injection mechanism (`match`/`replace` rules,
`optimize_and_load_gguf`, `generate_device`/`prefill_device` placement);
its own architecture-coupled precision/backend naming; its curated
large-MoE model list up to DeepSeek R1's 671B parameters; why it is the
answer for a harness builder specifically wanting a frontier-scale
open-weight model running on local hardware.

**Comprehension check:** What problem does KTransformers' operator
-injection mechanism (`match`/`replace` rules) actually solve, and why
does a harness builder wanting a 671B-parameter model running locally
reach for KTransformers rather than llama.cpp's own layer-granularity
offloading?

**Exercise:** Using this page's own curated model list, pick one large
MoE model, and sketch (or, if hardware allows, actually configure) the
`generate_device`/`prefill_device` placement this page documents for
running it on a mixed CPU/GPU setup.

### Capstone: cross-harness mechanism comparison + operator configuration

Choose one cluster above (Clusters 1-5 for a cross-harness mechanism
comparison, or Cluster 6/7/9/10 for an equivalent artifact grounded in
the RAG, Agentic-SDLC, model-classification, or inference-engine
material instead -- see the variant instructions below). For that
cluster's mechanism (e.g. "how context gets compressed
mid-run," or "how a permission decision gets enforced"), produce two
artifacts: (1) a comparison table with one row per harness (Claude Code,
Copilot CLI, OpenCode) naming the specific config key/file path/tool
name/limit each uses for that mechanism, with a citation to the source
page for each cell; and (2) a real, working configuration file (a
`settings.json`, a hooks config, a permission rule set, etc.) for at
least one of those harnesses that deliberately exercises the documented
limit or gate -- not a toy example, a configuration you actually ran
against a live session and can show the output of. A grader checks that
the table's cells are traceable to the cited page (not invented) and
that the configuration artifact actually does what it claims when run.

**Cluster 6/7/9 variant.** Clusters 6, 7, and 9 have no second harness
(or, for Cluster 9, no comparable second *implementation* at all) to
compare against -- RAG-the-technique, the SDLC handbook's
instrumented-codebase discipline, and the Hub's own model-classification
taxonomy are each a single conceptual source, not
three-implementations-of-one-mechanism like Clusters 1-5. A learner
choosing this variant instead produces: (1) a working artifact from one
of that cluster's own exercises above (a real pipeline component for
Cluster 6, a real primitive/lockfile pairing for Cluster 7, a real
classification worked-through on an actual model's card or config for
Cluster 9) that you actually ran or actually checked and can show the
output of; and (2) a short comparison note, with citations, of how that
cluster's mechanism differs from the closest analogous mechanism in
Clusters 1-5 (e.g. RAG's semantic-cache placement vs. `caching.md`'s
prompt-prefix caching; the SDLC handbook's load lifecycle vs.
`instruction-context-budget.md`'s eager-load budget; a model's parameter
-count-driven VRAM cost vs. `context-compression.md`'s own
context-length-driven memory pressure) -- the point of the note is to
keep the two epistemic registers (this book's own VERIFIED tagging vs.
Clusters 6/7/9's attribution to their own named sources) visibly
distinct rather than blurred together.

**Cluster 10 variant.** Cluster 10 sits closer to Clusters 1-5's own
shape than Clusters 6/7/9 do -- three real, named engines (llama.cpp,
Ollama, KTransformers) genuinely exist to compare, per this cluster's
own per-engine implementation pages -- but the cluster's engine-agnostic
concept pages document each mechanism primarily against llama.cpp's own
concrete flags, cross-referencing Ollama's and KTransformers' divergent
behavior only where a page's own text calls it out (e.g. Ollama's
VRAM-tiered automatic context-window default vs. llama.cpp's explicit
`--ctx-size`), rather than tabulating all three side by side the way
Clusters 1-5's own core-mechanics pages do for Claude Code, Copilot CLI,
and OpenCode. A learner choosing this variant may produce either: (a)
the same two-artifact structure as the main capstone above, but across
engines instead of harnesses -- a comparison table with one row per
engine naming the specific flag/environment variable/config surface each
uses for one mechanism (e.g. context-window sizing, or GPU/CPU
placement), with citations, plus a real, working configuration for at
least one engine that you actually ran and can show the output of; or
(b) the Cluster 6/7/9 variant's shape instead, if the mechanism you pick
genuinely has no clean three-engine tabulation in this cluster's own
pages -- state explicitly which shape you chose and why the cluster's
own material did or didn't support the three-way table.

---

## Transition 3: Demiurge -> Archon

**Overview.** The Demiurge can operate any of the three harnesses at
administrator depth but has been working from a settled, shipped
design; the cognitive shift this transition asks for is moving from
"trace what exists" to "justify what should exist, including where
nothing shipped has a settled answer yet." Per
`reader-proficiency-tiers.md`, the Archon can read design-space pages
critically and argue from primitives, and can design tool schemas,
testing pyramids, multi-agent topologies, and observability strategies
from scratch -- the ten pages in this band are original design-space
surveys and syntheses, not single-harness research reports, and the
exercises below are correspondingly generative rather than
observational. Per that same page's Archon-tier extension subsection
(added 2026-08-24), this band also now includes a ten-item Agentic-SDLC
design-space/methodology cluster (Cluster 8 below, `references/sdlc/`)
-- original synthesis and methodology in the same generative-not
-observational spirit as the ten core pages, but grounded "the handbook
says" rather than this book's own VERIFIED/BEST-CURRENT-UNDERSTANDING
tagging.

**Learning objectives.** By the end of this band, the learner can:
- Take a documented negative finding (a mechanism no shipped harness
  implements, per one of these pages) and produce a from-scratch design
  sketch for it, reusing named primitives already documented elsewhere
  in this book rather than inventing new infrastructure gratuitously.
- Critique a shipped design choice (e.g. Claude Code's `TodoWrite`->
  `Task*` split) against a named external design principle (e.g.
  Anthropic's own tool-consolidation guidance) and argue whether the
  divergence is a mistake, a tradeoff, or an artifact of history.
- Design a tool schema, a testing pyramid, a multi-agent topology, or
  an observability strategy for a hypothetical new harness feature,
  citing the primitives and literature these ten pages ground their own
  arguments in.
- Distinguish a genuine technical ceiling from a deliberate,
  team-specific scope decision when a page raises that question, and
  argue for one interpretation using the page's own evidence.
- Critique the Agentic SDLC Handbook's own original methodology (the
  five-phase execution meta-process, the Rosetta Stone pattern
  catalogue, the 19-anti-pattern taxonomy) against this book's own
  independently-grounded design-space pages where the two overlap, and
  check a named methodology claim against at least one of the
  handbook's own real-world case studies rather than accepting it in
  the abstract.

### Session breakdown (agenda only), Demiurge -> Archon

A pacing layer chunking this transition's 10 modules into 13
schedulable teaching sessions (organized around a two-way split this
band's own pages already draw for themselves in `index.md` -- five
design-space/original-survey modules and five production-completeness
/gap-closing modules -- one session per module, plus one per-cluster
synthesis session, plus a final capstone session) now lives at
`resources/airchon-teacher/demiurge-to-archon-sessions.md`
-- scoped to `airchon-teacher`'s own domain rather than kept as general
wiki-book content, the same reasoning and precedent as Transitions 1
and 2's own session breakdowns (see their pointer paragraphs above and
`CHANGELOG.md`). This page's learning objectives, modules, comprehension
checks, exercises, and capstone below remain the authoritative source
that file's agendas point back to -- it adds pacing, not new content.
**Note (2026-08-24):** as with the Transition 2 pacing file, this
13-session count predates Cluster 8 below and covers only the original
ten-page band; a future pacing pass on that file (out of scope for this
page) is needed to fold in session agendas for the Agentic-SDLC
design-space cluster.

### Module: The multi-agent coordination design space ([multi-agent-coordination-design-space.md](multi-agent-coordination-design-space.md))

**Key concepts:** topology patterns from the general multi-agent-systems
literature (centralized/decentralized/layered/shared-message-pool);
blackboard architectures; consensus/voting and market-based (Contract
Net Protocol) task allocation, and where each shipped harness mechanic
actually lands on that map.

**Comprehension check:** Which shipped feature does this page identify
as the clearest real blackboard-architecture instance, and which
coordination pattern does it find no shipped harness implements at all?

**Exercise:** Design a market-based (competitive-bidding) task
allocation mechanism for subagent dispatch in a hypothetical new
harness, specifying the bid signal, the auctioneer role, and how it
would interoperate with the capability-based dispatch this page finds
in all three real harnesses today.

### Module: Tool schema / interface design ([tool-schema-and-interface-design.md](tool-schema-and-interface-design.md))

**Key concepts:** JSON Schema authoring grounded in Anthropic's own
tool-use docs; the few-powerful-vs-many-narrow tradeoff tested against
this book's own tool-count inventory; idempotency/error-message design
per the MCP spec's four tool annotation hints.

**Comprehension check:** Name the MCP specification's four tool
annotation hints this page documents, and explain what
`destructiveHint` is supposed to signal to a client.

**Exercise:** Design a complete JSON Schema tool definition for a new
tool of your choosing, including a description written to the
good-vs-poor standard this page documents, `strict: true` constraints,
and all four MCP annotation hints set to their correct values for that
tool's actual behavior.

### Module: System-prompt / agent-instruction design as a craft ([system-prompt-design-as-craft.md](system-prompt-design-as-craft.md))

**Key concepts:** tool-calling-style phrasing and the "right altitude"
framing; few-shot tool-call examples vs. prose constraints as
complementary techniques; compaction-survival phrasing and
prompt-injection-resistant authoring as a complement to (not substitute
for) enforcement architecture.

**Comprehension check:** What does this page mean by "right altitude"
in system-prompt phrasing, and why does it treat prompt-injection
resistance as authoring-side rather than enforcement-side?

**Exercise:** Write a system-prompt section for a hypothetical new tool
that (a) uses canonical rather than exhaustive examples per this page's
own distinction, and (b) includes explicit compaction-survival phrasing
of the kind this page cites Anthropic's own documented sample
instruction for.

### Module: Context retrieval / RAG vs. agentic search as a design space ([context-retrieval-and-agentic-search.md](context-retrieval-and-agentic-search.md))

**Key concepts:** the RAG-vs-agentic-search design space; the finding
that none of the three harnesses ships embeddings-based retrieval as
its primary code-discovery strategy; the open question of whether an
embeddings-for-candidates/agentic-search-for-verification hybrid is a
genuine ceiling or a scope choice.

**Comprehension check:** What reason does this page cite (via a
secondary-sourced attribution) for Claude Code reversing an early
RAG+vector-db implementation?

**Exercise:** Argue, in writing, for one side of this page's own closing
question (ceiling vs. scope choice), citing at least two of the page's
own findings as evidence, and sketch what a hybrid
embeddings-plus-agentic-search retrieval layer would concretely need to
add to one real harness's documented architecture.

### Module: Advanced/novel planning and execution architectures ([advanced-planning-and-execution-architectures.md](advanced-planning-and-execution-architectures.md))

**Key concepts:** the negative finding that no shipped harness
implements tree-search/MCTS planning, loop-integrated self-critique,
per-step multi-model ensembling, or speculative tool execution; the
literature each of those four mechanisms is grounded in (Tree of
Thoughts, Reflexion, Mixture-of-Agents, speculative decoding lineage).

**Comprehension check:** Name one of the four missing mechanisms this
page surveys and the specific paper it cites as that mechanism's
literature grounding.

**Exercise:** Using this book's own already-documented primitives
(Dynamic workflows' script-held plan, `PostToolUse`/`tool.execute.after`
hooks, fan-out's parallel-dispatch machinery), sketch a from-scratch
design for loop-integrated self-critique in a hypothetical harness,
citing which existing primitive each part of your design reuses.

### Module: Evals and testing a harness ([evals-and-testing-a-harness.md](evals-and-testing-a-harness.md))

**Key concepts:** the four-layer testing pyramid (unit-level wire-format
correctness -> session/integration correctness -> API/route-surface
coverage -> end-to-end capability evals); OpenCode's fully source-read
test suite as a concrete worked example (VCR-style cassettes, golden
regression matrix, deterministic streaming-event unit tests).

**Comprehension check:** Name OpenCode's VCR-style test package and
explain what `CI=true`-hard-fails-on-missing-cassette discipline
enforces.

**Exercise:** Design a four-layer test plan (one concrete test per
layer) for a hypothetical new tool you are adding to an existing
harness, modeled directly on OpenCode's documented pyramid, specifying
what each layer's test actually asserts.

### Module: MCP supply-chain trust/vetting ([mcp-supply-chain-trust.md](mcp-supply-chain-trust.md))

**Key concepts:** the three separable trust axes (identity/code-safety/
continuity); the named attack taxonomy (tool description poisoning,
tool shadowing, tool-name squatting, rug pulls); the finding that no
shipped harness re-verifies a previously-approved server's tool
definitions on update.

**Comprehension check:** What is a "rug pull" in this page's attack
taxonomy, and why does the finding that no harness re-verifies tool
definitions on update make that attack specifically dangerous?

**Exercise:** Design a re-verification mechanism (a concrete check, not
a policy statement) that would close the update-time gap this page
identifies, specifying what gets hashed/signed/compared and at what
lifecycle point the check would need to run.

### Module: Observability and self-diagnostics ([observability-and-self-diagnostics.md](observability-and-self-diagnostics.md))

**Key concepts:** the four separable observability layers this page
argues for (cost export, execution tracing, interactive debug surface,
vendor product telemetry); Claude Code's beta OTel traces span
hierarchy; the argument that a harness should keep these layers
structurally distinct rather than sharing one pipe.

**Comprehension check:** Name the four observability layers this page
argues should stay structurally distinct, and give one real harness
example of two of those layers actually being conflated.

**Exercise:** Design an observability architecture for a hypothetical
new harness feature that keeps all four layers this page names
genuinely separate, specifying one concrete signal (a metric, a span,
a log line, or a debug command) for each layer.

### Module: Packaging, distribution, and self-update mechanics ([packaging-distribution-and-self-update.md](packaging-distribution-and-self-update.md))

**Key concepts:** multi-channel distribution (installer scripts,
package managers, signed repos) and integrity chains (GPG/code
signing); auto-update mechanics and their failure modes (a streamed-
download memory fix, a launcher-preservation fix); OpenCode's fully
source-verified per-install-method upgrade branching.

**Comprehension check:** Name one integrity mechanism this page
documents that a distribution channel uses to prove a downloaded binary
hasn't been tampered with.

**Exercise:** Design an auto-update mechanism for a hypothetical new
harness that explicitly addresses one documented failure mode from this
page (e.g. a streamed-download memory issue, or a launcher-preservation
gap), specifying the concrete safeguard you'd add.

### Module: TUI/CLI application architecture ([tui-cli-application-architecture.md](tui-cli-application-architecture.md))

**Key concepts:** the rendering-engine/component-model/input-handling
layer above streaming-and-incremental-rendering.md's buffering
concerns; OpenCode's fully source-verified OpenTUI stack (native Zig
core, Flexbox layout, Solid reconciler) and its keybinding mode-stack
architecture.

**Comprehension check:** What does this page mean by a keybinding
"mode-stack," and how does OpenCode's implementation of it differ from
a flatter keybinding-scoping model?

**Exercise:** Design a three-tier primitive/composite/dialog component
hierarchy (modeled on this page's description of OpenCode's own) for a
hypothetical new interactive dialog in a TUI harness, specifying which
primitives compose into which composite, and where a modal
keybinding-stack push/pop would need to occur.

### Cluster 8: Agentic SDLC design-space and methodology (`references/sdlc/`)

**Cluster overview:** the Agentic SDLC Handbook's own original synthesis
and methodology material -- a practitioner's-mindset overview, an
authoring-craft discipline (PROSE), a control-boundary thesis
(deterministic/probabilistic), a multi-agent composition catalogue, a
five-phase execution methodology, a Gang-of-Four pattern catalogue, a
19-item anti-pattern taxonomy, a recursive-composition synthesis, and
four real-world case studies plus a worked-example appendix -- held to
the same generative, argue-from-primitives bar as the ten core modules
above, but single-source ("the handbook says") rather than
independently cross-verified.

#### Module: The practitioner's mindset ([../sdlc/09-10-part-iii-preface-and-practitioners-mindset.md](../sdlc/09-10-part-iii-preface-and-practitioners-mindset.md))

**Key concepts:** the eight terms practitioners cannot avoid (Primitive,
Manifest, Lockfile, CODEOWNERS, Harness, Subagent, Recursion bound, MCP);
the five-layer supply chain restated from Ch. 4; the four composition
patterns (Panel/Wave/Scatter-Gather/Subagent) named as the field's
converged vocabulary before Ch. 17 develops them mechanically.

**Comprehension check:** Name the four composition patterns this
overview introduces, and which one the handbook treats as the "anchor
case" that concentrates every other discipline into one observable
instance.

**Exercise:** Using only this page's eight practitioner terms, write a
250-word abstract description of a hypothetical multi-agent code review
-- the same "stay abstract, use only the vocabulary given" discipline
Transition 1's own capstone required, now applied to SDLC vocabulary
instead of agent-loop vocabulary.

#### Module: The PROSE framework ([../sdlc/prose-framework.md](../sdlc/prose-framework.md))

**Key concepts:** the five constraints (Progressive Disclosure, Reduced
Scope, Orchestrated Composition, Safety Boundaries, Explicit Hierarchy)
and their paired anti-patterns; the handbook's own framing of PROSE as
"an opinionated discipline, not a standards body or a published spec."

**Comprehension check:** Name one of PROSE's five constraints, its
paired anti-pattern, and one concrete authoring practice this page gives
for satisfying the constraint.

**Exercise:** Critique PROSE's five constraints against this book's own
[System-prompt / agent-instruction design as a
craft](system-prompt-design-as-craft.md), naming one point where the two
converge on the same underlying practice under different names, and one
point where they diverge.

#### Module: The deterministic/probabilistic boundary ([../sdlc/16-deterministic-probabilistic-boundary.md](../sdlc/16-deterministic-probabilistic-boundary.md))

**Key concepts:** the "two computers, one program" framing; the seam
where "the model proposes; the gate disposes"; strong-form vs. weak-form
supervised execution; hallucination as a system property rather than a
model defect.

**Comprehension check:** What does this page's opening example (an
agent fabricating a customer name and creating a real GitHub issue)
argue was the actual root cause of the incident, in the chapter's own
vocabulary?

**Exercise:** Take a hypothetical new agent capability of your choosing,
and specify exactly where its seam sits -- which actions the
probabilistic side may only propose, and what deterministic gate must
approve them before they take effect.

#### Module: Multi-agent orchestration ([../sdlc/17-multi-agent-orchestration.md](../sdlc/17-multi-agent-orchestration.md))

**Key concepts:** the single- vs. multi-agent decision matrix (files
changed, concerns, dependency shape, expertise, time pressure, context
-overload risk); the Writer/Reviewer/Tester specialization pattern; the
one-file-one-agent rule.

**Comprehension check:** Per this page's decision matrix, name two
dimensions that push a task toward multiple agents rather than one, and
state the approximate file-count boundary this page gives (while noting
its own caveat about that boundary's precision).

**Exercise:** Critique this page's composition patterns against this
book's own [The multi-agent coordination design
space](multi-agent-coordination-design-space.md), naming which of that
page's topology categories (centralized/decentralized/layered/
blackboard/consensus/market-based) each of Panel/Wave/Scatter-Gather
/Subagent most closely maps to.

#### Module: The execution meta-process ([../sdlc/18-the-execution-meta-process.md](../sdlc/18-the-execution-meta-process.md))

**Key concepts:** the five-phase AUDIT/PLAN/WAVE/VALIDATE/SHIP
methodology; the plan-approval gate described as "the single most
important gate"; the one-file-one-agent rule carried over from Ch. 17;
the ADAPT loop for handling escalations mid-execution.

**Comprehension check:** Name the five phases in order, and state which
one this page's own text singles out as the "highest-impact moment in
the entire process."

**Exercise:** Apply the five-phase methodology, on paper, to a
hypothetical 40-file change of your own choosing -- naming what an
AUDIT pass would need to look for, how you would decompose the work
into waves, and what a VALIDATE pass would run after each wave.

#### Module: Architectural patterns, a Rosetta Stone ([../sdlc/19-architectural-patterns-rosetta-stone.md](../sdlc/19-architectural-patterns-rosetta-stone.md))

**Key concepts:** the four-layer substrate (Foundation/Assembly
/Composition/Execution); the precise/partial/weak-or-none classical
-analogue rating scheme; the claim that Composition-layer patterns map
cleanest to Gang-of-Four because "composition has been a solved problem
in software since the 1990s."

**Comprehension check:** Name this page's four architectural layers in
order, and state which one Ch. 14's load lifecycle belongs to.

**Exercise:** Pick one pattern from this page's catalogue rated
"partial" or "weak/none," and argue, using this book's own independently
-grounded pages as evidence, whether a cleaner classical analogue exists
than the one this page settles on.

#### Module: Anti-patterns and failure modes ([../sdlc/20-anti-patterns-and-failure-modes.md](../sdlc/20-anti-patterns-and-failure-modes.md))

**Key concepts:** the 19-anti-pattern taxonomy, each mapped to one of
PROSE's five constraints; the governing claim that "AI failures don't
crash, they produce plausible wrong output"; the anti-patterns'
handbook-stated origin, each "born from a failure."

**Comprehension check:** Name two anti-patterns this page maps to the
same PROSE constraint, and explain in one sentence each how they differ
in symptom despite sharing a root-cause category.

**Exercise:** Pick one anti-pattern from this page's table, find (or
construct) a real transcript exhibiting its symptom, and write a
one-paragraph root-cause diagnosis and fix in this page's own
symptom/root-cause/fix/recovery format.

#### Module: The reference architecture, earned ([../sdlc/22-the-reference-architecture-earned.md](../sdlc/22-the-reference-architecture-earned.md))

**Key concepts:** composition as a recursive Skill-Persona-Persona
-Skill triplet applied at every depth; the Maya's-PR-#4711 worked
example (a Security Reviewer dispatching a fresh CVE Triage Skill
mid-review when it hits a change class outside its own rubric).

**Comprehension check:** In the Maya's-PR-#4711 example, what triggers
the Security Reviewer to dispatch a new Skill mid-thread, and what does
that Skill load in turn?

**Exercise:** Design a hypothetical review pipeline of your own that
applies this page's "one composition rule, applied many times" claim to
at least three levels of recursive depth, naming what dispatches what
at each level.

#### Module: Case studies and the Genesis worked example ([../sdlc/23-case-study-apm-overhaul.md](../sdlc/23-case-study-apm-overhaul.md), [../sdlc/24-case-study-handbook-writing.md](../sdlc/24-case-study-handbook-writing.md), [../sdlc/25-case-study-publishing-pipeline.md](../sdlc/25-case-study-publishing-pipeline.md), [../sdlc/26-case-study-growth-engine.md](../sdlc/26-case-study-growth-engine.md), [../sdlc/appendix-b-genesis-worked-example.md](../sdlc/appendix-b-genesis-worked-example.md))

**Key concepts:** PR #394's 75-file/6-agent-panel/8-plan-iteration/5
-wave overhaul and its "context remains finite, output remains
probabilistic, human judgment is the differentiator" lessons; the
11-persona/4-pod handbook-writing project; the five-fix PDF-rendering
publishing pipeline; the growth-engine project's platform-limitation
escalation and persona-drift incident; Genesis's own before/after fix of
a panel-in-one-thread anti-pattern into fan-out-with-arbiter.

**Comprehension check:** Name one concrete numeric detail from the PR
#394 case study (file count, agent count, plan-iteration count, or wave
count) and one named escalation type from that same case study.

**Exercise:** Read the Genesis worked example's before/after fix, and
apply the same diagnostic move (name the anti-pattern, name why it
"looks like X but executes as Y," name the concrete fix) to one
composition choice in a real or hypothetical multi-agent system of your
own.

### Capstone: from-scratch harness design document

Produce a design document (not code) for one substantial, genuinely
novel feature of a hypothetical new harness -- something this book's
Demiurge-band pages document as either unshipped anywhere (a gap
surfaced by one of the ten design-space pages above) or shipped
inconsistently across the three real harnesses. The document must:
(1) state the design problem in the vocabulary of the relevant
design-space page(s); (2) survey what each real harness currently does
or doesn't do, with citations to the specific Demiurge-band page(s)
that established that finding; (3) propose a concrete design -- tool
schemas, config keys, permission gates, observability signals, or
topology, as the feature requires -- reusing named existing primitives
from this book wherever a suitable one exists rather than inventing
new machinery gratuitously; (4) name at least one open question the
design does not resolve, in the same VERIFIED/BEST-CURRENT-
UNDERSTANDING spirit this book uses elsewhere, i.e. explicitly flagged
as unresolved rather than papered over. A grader checks that the
document engages with real cited findings from the ten Archon-band
pages (not invented ones) and that its open-questions section is
honest rather than decorative -- an Archon-tier deliverable that claims
to have resolved everything has failed the capstone as surely as one
that cites nothing.

**Cluster 8 variant.** A learner may instead root the capstone in
Cluster 8: propose a from-scratch feature or fix for a gap Cluster 8's
own pages surface (an unresolved anti-pattern, a missing re
-verification step in the load lifecycle, a genuinely new composition
pattern beyond Panel/Wave/Scatter-Gather/Subagent), following the same
four-part structure above but citing Cluster 8's pages and at least one
of its case studies in place of the ten core Archon-band pages. The same
grader standard applies, with one addition specific to this variant: the
document must explicitly flag, in its own text, that its cited findings
carry Cluster 8's "the handbook says" grounding status rather than this
book's own VERIFIED tagging -- omitting that distinction is treated as a
capstone failure in its own right, not a stylistic nicety, per this
book's grounding discipline.
