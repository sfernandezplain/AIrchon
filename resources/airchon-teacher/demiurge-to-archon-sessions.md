# Session breakdown (agenda only): Demiurge -> Archon

**What this file is.** A pacing layer on top of
[knowledge-path-curriculum.md](../../references/harnesses/knowledge-path-curriculum.md)'s
"Transition 3: Demiurge -> Archon" section -- the 10-page design-space
/original-survey/production-completeness band. That page's learning
objectives, per-module key concepts, comprehension checks, and
exercises answer "what has to be taught." This file answers a
different, added question: "how do you chunk that same material into
discrete, schedulable teaching sessions, sized so no single sitting is
overloaded and no sitting is so thin it isn't worth convening" -- the
same question the sibling files
[slumberer-to-gnostic-sessions.md](slumberer-to-gnostic-sessions.md)
and [gnostic-to-demiurge-sessions.md](gnostic-to-demiurge-sessions.md)
answered for Transitions 1 and 2, scaled to a band roughly half the
module count of Transition 2's (10 modules against 21) but different
in kind, not just in size: this band's own ten pages are, in
`reader-proficiency-tiers.md`'s own words, "original design-space
surveys and syntheses, not single-harness research reports" -- several
self-describe in `index.md` as an "ORIGINAL DESIGN-SPACE SURVEY" or as
explicit "table stakes" production-completeness coverage rather than a
differentiating design decision -- so this file's sessions carry
correspondingly more generative agenda items (sketch a from-scratch
mechanism, design a re-verification check) per module than either
prior transition's more observational ones.

**Why this lives here, not in the wiki-book.** `references/harnesses/`
is the general-purpose, cross-agent wiki-book -- `airchon-mentor` reads
it conversationally, `airchon-author` is its only writer, and its
content (harness-internals research, the tier rubric, the curriculum
scaffold) serves any reader. Session pacing for actually *running* a
Demiurge->Archon course is different in kind: it is scoped to one
specific agent's own domain (`airchon-teacher`'s proficiency-tier
mission) rather than general reference material. Written directly here,
alongside its two siblings, rather than ever having lived inline in
`knowledge-path-curriculum.md` first -- see that page's own pointer
paragraph under "Transition 3" and `CHANGELOG.md` for the provenance
of this scoping decision, first established for Transition 1 and
repeated without a wiki-book detour for Transition 2 and now this one.
As of 2026-08-18, `airchon-teacher` directly consumes this file the
same way it now consumes its Transition-1 sibling -- see that file's
own note on this (and `CHANGELOG.md`'s 2026-08-18 entry) for the shared
rationale, not repeated here. The 10 module-content sessions below
(Sessions 1-5, 7-11) name no exercise of
their own -- Course-Delivery Flow pulls each one's practical exercise
live from its corresponding module's own Exercise field in
`knowledge-path-curriculum.md` instead of duplicating that text here;
only the two cluster-synthesis sessions and the final capstone keep
their own named exercise below, unchanged.

Like the rest of `knowledge-path-curriculum.md`'s pedagogical
scaffolding (comprehension checks, exercises, capstone), this session
breakdown is original pedagogical design, not a researched claim about
how anyone actually learns. Every item named in each session's agenda
below is inherited by reference from `knowledge-path-curriculum.md`'s
own Module sections for this transition (its "Key concepts,"
"Comprehension check," and "Exercise" fields) or from its own Capstone
section -- nothing here is a new concept not already scoped there; a
session's job is only to say *which* items get discussed together and
in what grouping, not to re-explain them. Every item below is also
phrased generically per `airchon-teacher.agent.md`'s Harness-Agnostic
boundary: no underlying model vendor is named anywhere in this file --
only the three harness names this whole book compares (Claude Code,
Copilot CLI, OpenCode) are named, exactly where the source curriculum
page itself names one of them as a concrete worked example.

```mermaid
flowchart TB
    subgraph CA["Cluster A: Design-space and generative reasoning (Sessions 1-6)"]
        S1["S1 Multi-agent coordination (5)"] --> S2["S2 Tool schema design (3)"]
        S2 --> S3["S3 System-prompt craft (4)"]
        S3 --> S4["S4 Context retrieval design space (3)"]
        S4 --> S5["S5 Advanced planning architectures (5)"]
        S5 --> S6["S6 Cluster A synthesis (6)"]
    end
    subgraph CB["Cluster B: Production-completeness and gap-closing (Sessions 7-12)"]
        S7["S7 Evals and testing (4)"] --> S8["S8 MCP supply-chain trust (4)"]
        S8 --> S9["S9 Observability (3)"]
        S9 --> S10["S10 Packaging and self-update (4)"]
        S10 --> S11["S11 TUI/CLI architecture (3)"]
        S11 --> S12["S12 Cluster B synthesis (6)"]
    end
    CA --> CB
    CB --> S13["S13 Final capstone: from-scratch harness design document (5)"]
```

**Why 13 sessions, not fewer or more.** The band's 10 modules carry, in
total, 38 discrete key-concept items when each module's own "Key
concepts" field is broken into its constituent teaching points (the
same granularity both sibling files used) -- ranging module-by-module
from 3 items (tool-schema-and-interface-design.md,
context-retrieval-and-agentic-search.md, observability-and-self-
diagnostics.md, tui-cli-application-architecture.md) to 5
(multi-agent-coordination-design-space.md,
advanced-planning-and-execution-architectures.md, the two richest
modules in the band, each naming four or more distinct sub-mechanisms
in one "Key concepts" field). Three session-count choices were
rejected before settling on 13:

- **One session per cluster (2 sessions total)** would force 18-20
  key-concept items -- five modules' worth, each already requiring
  generative, design-from-scratch engagement rather than the more
  observational recall the two prior transitions' comprehension checks
  asked for -- into a single sitting. That is three to four times the
  3-6-item range both sibling files established as the sensible floor
  and ceiling, and it would collapse first exposure to genuinely
  distinct design questions (e.g. a tool-annotation-hint schema
  question and a compaction-survival-phrasing question) into the same
  block.
- **One session per module with no synthesis sessions at all (10
  sessions)** would teach every module's key concepts but discard the
  natural two-way split this band's own pages already draw for
  themselves -- several of the five Cluster-A pages self-describe in
  `index.md` as an "ORIGINAL DESIGN-SPACE SURVEY" or a "design-space
  companion" to an earlier mechanics page, while the five Cluster-B
  pages self-describe as explicit "table stakes" coverage "not a
  differentiating design decision," closing named items on a prior
  gap-analysis pass. Dropping the two synthesis sessions that let a
  reader integrate within each of those self-described groupings would
  leave the comprehension-check-and-exercise practice this band's
  material organizes itself around with nowhere to happen short of one
  end-of-transition sitting holding all ten comprehension checks plus
  exercise selection at once -- the same overload failure the
  cluster-per-session option above was rejected for, merely deferred to
  the end.
- **Splitting any individual module's already-short 3-5-item
  key-concepts list across two sessions** would produce sittings of one
  or two items each -- precisely the "so thin it's pointless" failure
  mode `slumberer-to-gnostic-sessions.md` names as the reason it
  rejected four-or-more sessions for its own, much smaller band.

13 is the smallest count that avoids all three failure modes at once:
**10 module-content sessions** (Sessions 1-5 and 7-11 -- one per
module, agenda drawn directly and only from that module's own "Key
concepts" field, sized 3-5 items exactly as that field's own
granularity dictates, no combining and no further splitting), **2
cluster-synthesis sessions** (Sessions 6 and 12 -- one per cluster,
immediately after that cluster's own module sessions, each sized 6
items: one item per module in the cluster, each item being that
module's own "Comprehension check" question walked cold, plus one item
selecting a single representative "Exercise" from that cluster's
modules to actually run, rather than attempting all five of that
cluster's exercises in one sitting), and **1 final capstone session**
(Session 13, sized 5 items, breaking the transition's own single
"from-scratch harness design document" capstone task into its concrete
deliverable steps). This keeps every session in the same 3-6 item
range both prior transitions established as the sensible floor and
ceiling, while letting the course's own shape mirror the two-way
design-space-vs-production-completeness split this band's own pages
already draw for themselves in `index.md`, rather than inventing a
different grouping.

---

## Cluster A: Design-space and generative reasoning (Sessions 1-6)

**Session 1 -- The multi-agent coordination design space.** Items to
cover, in order:
1. Topology patterns from the general multi-agent-systems literature:
   centralized, decentralized, layered, and shared-message-pool
   coordination.
2. Blackboard architectures as a shared-scratchpad coordination
   pattern.
3. Consensus/voting among peer agents as a coordination pattern.
4. Market-based (competitive-bidding, Contract-Net-Protocol-style)
   task allocation as a coordination pattern.
5. Where each shipped harness mechanic (Claude Code, Copilot CLI,
   OpenCode) actually lands on this topology map, including which
   pattern none of the three implements at all.

**Session 2 -- Tool schema / interface design.** Items to cover, in
order:
1. JSON Schema authoring for tool definitions, per official tool-use
   documentation guidance: description quality and grammar-constrained,
   strictly-typed parameter schemas.
2. The few-powerful-vs-many-narrow tool-count tradeoff, tested against
   a real cross-harness tool-count inventory.
3. Idempotency and error-message design via the Model Context
   Protocol specification's four tool annotation hints
   (`readOnlyHint`/`destructiveHint`/`idempotentHint`/`openWorldHint`).

**Session 3 -- System-prompt / agent-instruction design as a craft.**
Items to cover, in order:
1. Tool-calling-style phrasing and the "right altitude" framing for
   instruction text.
2. Few-shot tool-call examples vs. prose constraints as complementary
   authoring techniques.
3. Compaction-survival phrasing: writing instructions that remain
   effective after a context-compaction event.
4. Prompt-injection-resistant authoring as a complement to -- never a
   substitute for -- enforcement architecture.

**Session 4 -- Context retrieval / RAG vs. agentic search as a design
space.** Items to cover, in order:
1. The retrieval-augmented-generation-vs-agentic-search design space,
   as two competing code-discovery strategies.
2. The finding that none of Claude Code, Copilot CLI, or OpenCode ships
   embeddings-based retrieval as its primary code-discovery strategy
   today, all three converging on iterative search instead.
3. The open question this design space raises: is an
   embeddings-for-candidates/agentic-search-for-verification hybrid a
   genuine technical ceiling none of the three has reached, or a
   deliberate operational-scope choice each team declined to own?

**Session 5 -- Advanced/novel planning and execution architectures.**
Items to cover, in order:
1. The negative finding: no shipped harness implements tree-search
   -style planning, a loop-integrated self-critique mechanism, per-step
   multi-model ensembling, or speculative tool execution inside its
   primary task loop.
2. Tree-search/best-of-N-style planning and the literature it is
   grounded in.
3. Loop-integrated self-critique and the literature it is grounded in.
4. Per-step multi-model ensembling and the literature it is grounded
   in.
5. Speculative tool execution and the literature it is grounded in,
   including a reasoned account of why a read/write tool-kind safety
   distinction plausibly blocks it from shipping today.

**Session 6 -- Cluster A synthesis.** No new material -- every item
here is integration of Sessions 1-5, not a new concept:
1. Walk multi-agent-coordination-design-space.md's comprehension check:
   which shipped feature is the clearest real blackboard-architecture
   instance, and which coordination pattern no shipped harness
   implements at all.
2. Walk tool-schema-and-interface-design.md's comprehension check: the
   four tool annotation hints, and what the destructive-action hint is
   supposed to signal to a client.
3. Walk system-prompt-design-as-craft.md's comprehension check: what
   "right altitude" means in system-prompt phrasing, and why
   prompt-injection resistance is treated as authoring-side rather than
   enforcement-side.
4. Walk context-retrieval-and-agentic-search.md's comprehension check:
   the cited reason for one harness reversing an early
   retrieval-augmented-generation-plus-vector-database implementation.
5. Walk advanced-planning-and-execution-architectures.md's
   comprehension check: one of the four missing mechanisms and the
   specific paper grounding it in the literature.
6. Run one representative exercise from this cluster (recommended:
   advanced-planning-and-execution-architectures.md's -- sketch a
   from-scratch design for loop-integrated self-critique, reusing this
   book's own already-documented primitives and naming which existing
   primitive each part of the design reuses).

---

## Cluster B: Production-completeness and gap-closing (Sessions 7-12)

**Session 7 -- Evals and testing a harness.** Items to cover, in
order:
1. The four-layer testing pyramid: unit-level wire-format correctness,
   session/integration correctness, API/route-surface coverage, and
   end-to-end capability evals.
2. Record/replay ("cassette"-style) testing as a worked example of the
   pyramid's lower layers.
3. A golden regression matrix run across many provider/model targets as
   a worked example of the pyramid's upper layers.
4. Deterministic streaming-event unit testing as a worked example of
   asserting exact event sequences across a split-mid-stream chunk
   boundary.

**Session 8 -- MCP supply-chain trust/vetting.** Items to cover, in
order:
1. The three separable trust axes: identity, code-safety, and
   continuity.
2. The named attack taxonomy: tool description poisoning, tool
   shadowing, and tool-name squatting.
3. The "rug pull" attack specifically, and why it is fundamentally a
   continuity-axis problem rather than an identity- or code-safety-axis
   one.
4. The finding that no shipped harness re-verifies a previously
   -approved server's tool definitions on update.

**Session 9 -- Observability and self-diagnostics.** Items to cover,
in order:
1. The four separable observability layers this design space argues
   for: cost export, execution tracing, an interactive debug surface,
   and vendor product telemetry.
2. A worked example of a beta distributed-tracing signal with a
   request/tool-call/hook span hierarchy.
3. The argument that a harness should keep these four layers
   structurally distinct rather than sharing one undifferentiated pipe.

**Session 10 -- Packaging, distribution, and self-update mechanics.**
Items to cover, in order:
1. Multi-channel distribution: installer scripts, package managers, and
   signed repositories.
2. Integrity chains: cryptographic signing and code-signing
   verification of a downloaded binary.
3. Auto-update mechanics and their failure modes: a streamed-download
   memory issue and a launcher-preservation gap, as two concrete named
   examples.
4. A fully source-verified example of per-install-method upgrade
   branching (the update logic differing by which channel originally
   installed the harness).

**Session 11 -- TUI/CLI application architecture.** Items to cover, in
order:
1. The rendering-engine/component-model/input-handling layer, one level
   above lower-level buffering/reassembly/pacing concerns.
2. A fully source-verified terminal-UI stack: a native systems-language
   rendering core, a flexbox-style layout engine, and a
   reconciler-based component library.
3. A keybinding "mode-stack" architecture (push/pop, shadowing) as a
   design choice distinct from a flatter keybinding-scoping model.

**Session 12 -- Cluster B synthesis.** No new material -- every item
here is integration of Sessions 7-11, not a new concept:
1. Walk evals-and-testing-a-harness.md's comprehension check: the
   record/replay test package named, and what its
   hard-fail-on-a-missing-recording discipline enforces.
2. Walk mcp-supply-chain-trust.md's comprehension check: what a "rug
   pull" is in this attack taxonomy, and why the no-re-verification
   -on-update finding makes that attack specifically dangerous.
3. Walk observability-and-self-diagnostics.md's comprehension check:
   the four observability layers, and one real example of two of them
   being conflated in a shipped product.
4. Walk packaging-distribution-and-self-update.md's comprehension
   check: one integrity mechanism a distribution channel uses to prove
   a downloaded binary hasn't been tampered with.
5. Walk tui-cli-application-architecture.md's comprehension check: what
   a keybinding "mode-stack" is, and how one harness's implementation
   of it differs from a flatter keybinding-scoping model.
6. Run one representative exercise from this cluster (recommended:
   mcp-supply-chain-trust.md's -- design a concrete re-verification
   mechanism, specifying what gets hashed/signed/compared and at what
   lifecycle point the check would need to run, that closes the
   update-time trust gap this cluster's own finding identifies).

---

## Session 13 -- Final capstone: from-scratch harness design document

No new material -- every item here is execution of
`knowledge-path-curriculum.md`'s own Transition-3 capstone task, broken
into its concrete deliverable steps:
1. Select one substantial, genuinely novel feature that this band's ten
   pages document as either unshipped anywhere or shipped inconsistently
   across the three real harnesses.
2. State the design problem in the vocabulary of the relevant
   design-space page(s) covered in Sessions 1-11.
3. Survey what each real harness currently does or doesn't do, with
   citations to the specific session/module page(s) that established
   that finding.
4. Propose a concrete design -- tool schemas, config keys, permission
   gates, observability signals, or coordination topology, as the
   feature requires -- reusing named existing primitives from this book
   wherever a suitable one exists rather than inventing new machinery
   gratuitously.
5. Name at least one open question the design does not resolve,
   flagged honestly as unresolved rather than papered over, and
   self-check (or peer-review) the whole document against the
   capstone's own grading criteria: that it engages with real cited
   findings from the ten Cluster A/B pages, and that its open-questions
   section is honest rather than decorative.
