# Case study: building a growth engine

Source: **The Agentic SDLC Handbook**, Daniel Meppiel, Part IV case study --
https://danielmeppiel.github.io/agentic-sdlc-handbook/case-study-growth-engine.html.
See [index.md](index.md) for why this lives here rather than in
`references/harnesses/`.

A worked example of the book's technical patterns applied to building
a growth engine around the handbook launch: email capture, a landing
page, DNS/email infrastructure, a PII audit of the repository, and
launch preparation -- run across "checkpoints 014-019, 6 phases, 18
implementation tasks," roughly 8 hours of wall-clock time across
multiple sessions.

## The problem

Ship a working acquisition/growth system -- not just advice about
one -- with agents doing the strategy synthesis and the build work,
and the human doing scope-setting and anything requiring judgment an
agent fleet structurally cannot supply. Three distinct technical
sub-problems drove the case study's content: (1) automating a
third-party email platform's UI, (2) generating landing-page copy
that was actually grounded in the real page, and (3) auditing a
repository for personal data at scale.

## Agentic techniques applied

**Large panel-based deliberation, with a scope-correction override.**
"Across six phases, the orchestrator convened panels with fifteen
domain-specific personas (publishing strategy, growth, branding,
LinkedIn, security) that produced synthesised recommendations through
moderator agents" -- seven panels in total. Early panels drifted off
task, "over-index[ing] on career coaching," which the user corrected
directly: "Focus on the growth engine -- brand, followers, industry
gravitas, tactical distribution." The case study identifies this as
**the Architect role from Chapter 14** -- scope correction when agent
output drifts from the actual objective.

**Escalating automation attempts against a genuine platform wall.**
Automating the Kit email platform's UI went through three distinct
technical approaches before the case study calls it correctly
escalated to a human:

1. **Playwright scripts** -- login, tag creation, and form creation
   all succeeded, but the React textarea in the confirmation-message
   field rejected every input method tried (`.fill()`, `Meta+a`, a
   JS-level setter), and the automation dropdown turned out to be a
   React combobox, not a native `<select>`.
2. **Playwright MCP server** -- added `browser_snapshot` and
   `browser_take_screenshot` capabilities, but hit the same
   fundamental blocker: "React's virtual DOM rejects external
   mutations."
3. **Kit's V3 REST API** -- listing forms and tags worked, but
   `/v3/automations` returned a 404 -- the endpoint simply isn't
   exposed.

At that point "the orchestrator produced a 3-step manual checklist
and the human completed it in two minutes": open the Kit form editor,
paste the confirmation text into the textarea, and select "Add
subscriber to sequence: Welcome" from the automation dropdown. The
case study's framing: "The methodology's value was not in automating
this task -- it was in recognising when to stop trying. Each approach
was trusted to work based on partial success before validating the
fundamental constraint." Three attempts, three genuine platform
limitations, then escalation -- not a fourth attempt.

**Progressive disclosure applied to landing-page generation.** The
first two attempts at rewriting landing-page copy failed outright --
"one stalled for eight minutes, the other produced generic copy --
because they lacked the actual HTML." The third attempt embedded the
full page source in context and "immediately produced field-by-field
rewrites." The case study's stated principle: "Progressive disclosure
means providing the *right* context, not the *least* context" -- a
direct refinement of the PROSE framework's Progressive Disclosure
constraint (see [prose-framework.md](prose-framework.md)).

**Parallel dispatch for a PII audit, with a safety-boundary edge
case.** Four agents were dispatched in parallel to scan the
repository for sensitive data. Three completed normally, together
surfacing findings across 25+ files. The fourth refused outright: the
career directory it was scanning contained personal documents, and
its own safety guardrails triggered. The case study treats this as a
genuine edge case rather than a bug: the refusal was "correct in
principle (the files *were* sensitive), but the task was finding
sensitive content to *remove* it -- an edge case where safety
boundaries and task objectives were aligned but the agent couldn't
distinguish audit-to-remove from audit-to-exploit." The orchestrator
worked around it with manual grep analysis, and remediation used
`git-filter-repo` to scrub history.

**Persona-drift correction and its blast radius.** The orchestrator's
authority profile for the user incorrectly described them as a
"software engineer" (they are a "Global Black Belt with 14+ years
enterprise strategy"). Once corrected, "the correction propagated
across all files -- landing page, preface, chapter bios, panel
briefs." The case study names this **Anti-Pattern #17 (Persona
Drift)** compounded by **Anti-Pattern #7 (The Trust Fall)**: "The
authority profile had been generated in an earlier wave and accepted
without human verification. A single factual error -- job title --
cascaded into every downstream deliverable that referenced the
author's credentials."

**Infrastructure pivot mid-build.** During DNS setup for the growth
engine's email capture, the orchestrator discovered the domain
registrar had silently discontinued free email forwarding. It pivoted
to **ImprovMX** (free tier), configured MX records, added SPF and
DKIM entries, and verified delivery -- without escalating, since it
was a like-for-like infrastructure substitution rather than a scope
change.

## Concrete numbers

| Metric | Value |
|---|---|
| Implementation phases | 6 (checkpoints 014-019) |
| Implementation tasks | 18 |
| Wall-clock time | ~8 hours across multiple sessions |
| Expert panels convened | 7 |
| Distinct agent personas | 15 |
| Kit automation approaches tried | 3 (Playwright scripts, Playwright MCP, REST API) -- all blocked by genuine platform limits |
| Manual-checklist resolution time | 2 minutes |
| Landing-page generation attempts | 3 (first two failed for lack of real page context) |
| Parallel PII-audit agents | 4 (3 completed, 1 refused on safety grounds) |
| Files with PII findings | 25+ |
| Anti-patterns observed | 3 (#17 Persona Drift, #7 The Trust Fall, #5 Scope Creep) |

## Lessons learned

- **Escalation discipline over persistence:** "When three automated
  approaches each hit a genuine platform limitation, escalating to a
  human with a precise checklist is the correct move -- not a fourth
  attempt."
- **Progressive disclosure means the right context, not the least
  context** -- the landing-page rewrites only succeeded once the
  agent had the actual page source, not a description of it.
- **Persona/authority errors compound silently:** a single wrong
  fact accepted without verification in one wave propagated into
  every later deliverable that referenced it; catching persona drift
  early is cheaper than unwinding it later.
- **Safety guardrails can misfire on legitimate audit-to-remove
  tasks:** a refusal can be "correct in principle" about the
  sensitivity of content while still blocking the very task meant to
  remediate it -- worth designing a manual-fallback path for, rather
  than treating every refusal as agent failure.
- **Pivots are normal and should be absorbable without escalation
  when they're infrastructure substitutions, not scope changes:**
  "the plan changed repeatedly, and the orchestration protocol
  absorbed each one."
- **Overall success criterion:** "The growth engine shipped. The
  system worked not because every agent succeeded -- the Kit
  automation plainly failed -- but because the orchestrator knew when
  to pivot and when to stop."

## Source

Part IV case study, **The Agentic SDLC Handbook** by Daniel Meppiel --
https://danielmeppiel.github.io/agentic-sdlc-handbook/case-study-growth-engine.html
