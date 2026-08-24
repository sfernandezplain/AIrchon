# Case study: writing a ~68,000-word book with agent fleets

Source: **The Agentic SDLC Handbook**, Daniel Meppiel, Part IV case study --
https://danielmeppiel.github.io/agentic-sdlc-handbook/case-study-handbook-writing.html.
See [index.md](index.md) for why this lives here rather than in
`references/harnesses/`.

The handbook's meta-case-study: the book itself -- 15 chapters, roughly
68,000 words -- was "drafted and composed through agentic
orchestration in a single Copilot CLI session." Domain expertise and
editorial direction came from Daniel Meppiel (Global Black Belt at
Microsoft, APM's creator); Copilot CLI managed the agent team. The
agent team was packaged and distributed using APM itself: "8 persona
definitions as `.agent.md` files, an orchestration workflow as
`SKILL.md`, declared as a dependency in `apm.yml`, and deployed via
`apm install`" -- APM was used to build the handbook that teaches
about APM.

## Team topology: 11 personas in four pods

- **Editorial Pod** -- Chief Editor (cross-chapter coherence),
  Thought Leadership Advisor (positioning).
- **Domain Expert Pod** -- C-Suite Strategist, Practitioner Authority,
  Market Analyst, Platform Strategist.
- **Review Pod** -- CTO Proxy, Dev Lead Proxy.
- **Audit Pod (dynamic)** -- Illustrator, Fact-Ref-Checker, Publishing
  Advisor.

"Each persona was a *primitive* -- a composable instruction unit
defined in a single `.agent.md` file."

**Dynamic persona creation.** Three personas were not defined at the
project's start but created mid-project in response to discovered
gaps:

1. **Illustrator** -- created when an integration review revealed
   missing visual anchors.
2. **Fact-Ref-Checker** -- created after inconsistent statistics were
   found across chapters (75 flags located, 5 critical).
3. **Publishing Advisor** -- created to evaluate distribution paths.

This is offered as a worked example of the principle that "primitives
should be created and iterated throughout a project, not frozen at
inception."

## Execution pipeline: wave-based orchestration

Four writing waves plus integration and polish:

- **Phase 0** -- corpus audit (4 agents) -> Editor synthesis.
- **Phase 1** -- architecture attempt (initially failed as a single
  monolithic dispatch; then split into two parallel agents).
- **Wave 0** -- 1 chapter (test cycle).
- **Wave 1** -- 4 chapters (the chapters with the most source
  material).
- **Wave 2** -- 5 chapters (the hardest, requiring fresh writing).
- **Wave 3** -- 5 chapters (integration chapters requiring
  cross-references).
- **Integration** -- block reviews, fix agents, polish, README.

"Wave ordering was deliberate," embodying *context budgeting*:
"right-sizing each wave's scope to what the agents could handle with
available context."

**Draft-review-revise cycle**, applied per chapter:

1. **Draft** -- a domain-specialist agent writes the chapter
   (3,000-5,000 words).
2. **Parallel review** -- CTO Proxy reviews for an executive audience,
   Dev Lead Proxy for a practitioner audience, Chief Editor for
   coherence and voice.
3. **Revise** -- a revision agent applies the synthesised, consensus
   set of fixes.

In later waves the orchestrator batched reviews by persona rather than
by chapter -- "sending one reviewer all 5 chapters at once rather than
dispatching 15 separate reviews" -- cutting overhead without losing
coverage.

## Concrete numbers

- **~68,000 words** across 15 chapters.
- **11 personas** (8 defined at inception + 3 created dynamically).
- **50+ dispatches** in total.
- **4 writing waves** plus integration and polish phases.
- **25 Mermaid diagrams** embedded in the finished book.
- **75 fact-check flags** identified (5 critical).
- **40 visual opportunities** identified.
- **5 APM mentions** across ~475 words total, added as deliberate
  late insertions (see below).
- **4 escalation events** that interrupted the normal flow.

## File and workflow structure

- Individual `.agent.md` files -- 8 initial personas + 3 created
  dynamically.
- A `SKILL.md` orchestration workflow.
- An `apm.yml` dependency declaration.
- Deployment via `apm install`.

Example of the dynamic-persona pattern given for the Fact-Ref-Checker:

```
# .github/agents/fact-ref-checker.agent.md
---
name: Fact-Ref-Checker
role: Claims Auditor
---
[Instructions for auditing factual accuracy, sourcing, consistency,
and falsifiability]
```

## Problems encountered and how they were solved

**1. Architecture agent timeout (Anti-patterns #11 and #6).** A single
agent dispatched to produce the full 15-chapter architecture failed
after 26 minutes from context window exhaustion: "The orchestrator
assigned monolithic scope to one agent, violating the *one file, one
agent per wave* isolation principle." Fix: split into two parallel
agents -- Part 1 (chapters 1-9) and Part 2 (chapters 10-16 plus
cross-cutting concerns) -- both of which completed successfully,
producing 1,020 lines of chapter specifications.

**2. Chief Editor synthesis scope (Anti-pattern #2).** The four
corpus-audit specialists' parallel outputs needed cross-cutting
synthesis that no individual specialist could provide. Escalated to
the Chief Editor persona, whose explicit role was cross-chapter
coherence, producing "7 consensus themes, 6 resolved tensions, 10
cuts, and 9 identified gaps."

**3. User veto on `apm compile`.** During the APM strategic-insertion
phase, the human author intervened directly: "Do not mention `apm
compile` -- niche feature." All six planned insertions were adapted to
respect this constraint -- demonstrating that "human judgment remains
the bottleneck and the differentiator."

**4. Panel disagreement on APM prominence.** The Market Analyst wanted
greater visibility for APM; the Thought Leadership Advisor wanted
less. "The Chief Editor resolved the disagreement with a single
principle: 'The book is 100% useful without APM. APM appears as
proof, not prerequisite.'"

## Notable discovery

Across ~68,000 words the manuscript contained zero mentions of APM
until strategic insertions were made deliberately at the end: "A book
about AI-native software development, written by APM's creator, using
APM's orchestration infrastructure, contained zero mentions of APM
across ~68,000 words. This was not a bug -- it was the methodology
working correctly." Each agent had been dispatched with
chapter-specific scope; no agent's instructions included "promote the
author's project." That absence of self-promotion is what prompted the
deliberate strategic assessment leading to four surgical insertions
(~475 words across 5 chapters).

## Lessons learned

1. **Structural properties held.** "The five structural properties
   held under editorial conditions." Composition-level orchestration
   (coordinating prose-writing agents, not code agents) "scaled
   without modification to the wave model."
2. **Context remains finite.** "Regardless of model capability, there
   is always a limit to how much an agent can consider effectively."
3. **Composition is load-bearing.** "15 chapters required 50+
   dispatches, 4 waves, and 2 integration passes. No single agent
   could hold the full manuscript."
4. **Explicit knowledge beats implicit.** Once governing principles
   were articulated (e.g. "The book is 100% useful without APM"),
   subsequent decisions became "mechanical" -- true for the
   authenticity strategy as well.
5. **Dynamic primitives beat a fixed team.** Creating personas
   mid-project in response to process gaps proved more effective than
   freezing the team at inception.
6. **Transparency as strength.** The README was rewritten to showcase
   the pipeline explicitly, listing the 11-agent team and 5-stage
   pipeline, under the framing rule "built using the same methodology
   it teaches" -- never "AI-written."

## Source

Part IV case study, **The Agentic SDLC Handbook** by Daniel Meppiel --
https://danielmeppiel.github.io/agentic-sdlc-handbook/case-study-handbook-writing.html
