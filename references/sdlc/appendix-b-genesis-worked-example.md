# Appendix B: Genesis worked example -- panel re-architecture

Source: **The Agentic SDLC Handbook**, Daniel Meppiel, Appendix B --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/appendix-b-genesis-worked-example.html.
See [index.md](index.md) for why this lives here rather than in
`references/harnesses/`.

**Author disclosure, stated on the page.** Genesis is a tool built by
the handbook's own author -- "one of several emerging answers to the
discipline the practitioner chapters argue for," MIT-licensed and open
source, installable via `apm install danielmeppiel/genesis`. The
appendix is explicit that "the mechanics it demonstrates -- Panel
anti-pattern, fan-out fix, compliance check -- port to any
package-managed primitive set; the file paths and slash commands do
not." The worked example itself is the bundle's own
[`skills/genesis/examples/02-review-panel-architecture.md`](https://github.com/danielmeppiel/genesis/blob/main/skills/genesis/examples/02-review-panel-architecture.md),
written to be readable cold -- without prior Genesis context -- per
the bundle's own examples index
([`skills/genesis/examples/README.md`](https://github.com/danielmeppiel/genesis/blob/main/skills/genesis/examples/README.md)).
It "opens with a panel that breaks, diagnoses why in three short
truths, and ends with the version that works."

## B.1 The anti-pattern -- panel-in-one-thread

**Before state.** The starting design runs five mandatory specialist
lenses, one conditional specialist, and an arbiter -- all inside one
thread. The thread loads each persona file in turn, plays each lens,
accumulates findings in working notes, then loads the arbiter persona
and synthesizes a single output comment. As the appendix puts it: "It
looks like a panel; it executes as a single loop."

The example diagnoses the failure via three "durable truths" before
showing the fix:

- **Truth #1 -- context is finite and fragile.** "By the time the
  arbiter step runs, the thread's window contains the orchestrator
  wrapper, five personas' text, five sets of findings, the conditional
  persona, the arbiter persona, and the synthesis template." The first
  lens's text is far from focus by then, and its nuances have decayed
  influence on the synthesis.
- **Truth #2 -- context must be explicit.** The lenses cannot operate
  independently: "each lens reads the prior lenses' findings whether
  the design wants that or not, because all share the window." This
  cross-pollination corrupts the "independent specialist" contract the
  design claims to deliver.
- **Truth #3 -- output is probabilistic.** Variance is highest exactly
  where the design demands the most precision -- "the arbiter's
  synthesis runs at the deepest point of attention degradation in the
  whole thread."

The example then names the failures in the classical-principle
vocabulary Genesis uses elsewhere: **shared mutable state** (every
lens writes to the same window), **context thrash** (one thread plays
five distinct lenses), and an **unreached escape hatch** (a textbook
fan-out target executed as a single loop).

**Compliance table (old design column).** The anti-pattern half closes
with a compliance summary so the recovery is auditable line by line:

| Check | Old design | New design |
|---|---|---|
| Reduced Scope (per-lens fresh window) | FAIL | PASS |
| Orchestrated Composition (independent contracts) | FAIL | PASS |
| Single-writer interlock on output | PASS | PASS |
| God module avoidance | FAIL (one thread = many lenses) | PASS |
| Fan-out where applicable | FAIL | PASS |

## B.2 The corrected design -- fan-out with arbiter

**After state.** "The redesigned shape is fan-out plus a synthesizer
realizing the panel pattern. Each lens gets its own thread with its
own fresh context window. The orchestrator is the only writer to the
output sink. The arbiter is a distinct persona that runs in its own
thread, loaded with the arbiter persona file plus the lens findings as
input -- never the lens personas themselves."

**Diagram artifact.** The page includes a flowchart of the corrected
architecture: a "Panel orchestrator" node branches out to seven
personas -- Architect, Logging UX, DevX UX, Security, Growth, Auth
(dotted line, marked conditional), and Arbiter (dashed outline,
marking it as newly introduced) -- with every arrow originating from
the orchestrator.

**The corrected flow, as described:** the orchestrator spawns one
child thread per lens, scoped to the PR under review; the conditional
lens (Auth) spawns only when its trigger fires. Each child returns
findings to the orchestrator; a completeness gate checks the set; the
orchestrator then spawns the arbiter thread with the arbiter persona
plus the collected findings, and writes the synthesized verdict to the
output sink under a single-writer interlock. The page notes Genesis's
own source file continues from there with a handoff-packet template.

**Thread vs. persona, disambiguated.** The example insists on this
distinction: "a thread is a runtime spawn with a fresh context window;
a persona is a markdown file used as a scoping prompt at thread
start." The Architect thread is not the Architect persona; the persona
is not a thread -- "the thread exists because the design needs fresh
context; the persona exists because the design needs a focused lens.
They cooperate across the spawn boundary."

**Compliance table, corrected.** The four rows that failed above flip
to PASS once the fan-out is in place; single-writer was already PASS
in the old design but "now holds by construction rather than by
coincidence of the loop."

**Composition-over-inheritance rationale.** The orchestrator-as-
single-writer rule is described as the separation-of-concerns stance
from Genesis's own composition substrate -- "composition over
inheritance, with each lens persona depended on via link rather than
inlined into the orchestrator."

**Related examples cited on the page (not reproduced here).** For a
denser instance with six personas plus an arbiter against a real
PR-review surface, the page points to the bundle's
[`skills/genesis/examples/04-pr-review-advisory.md`](https://github.com/danielmeppiel/genesis/blob/613f2a64a4a193cacd45fd4439a093044ae3178d/skills/genesis/examples/04-pr-review-advisory.md).
For a "restraint-as-discipline counterpart," it points to
[`skills/genesis/examples/05-pr-review-verdict.md`](https://github.com/danielmeppiel/genesis/blob/613f2a64a4a193cacd45fd4439a093044ae3178d/skills/genesis/examples/05-pr-review-verdict.md),
where the same cold-load discipline records two patterns as
considered and rejected rather than adopted: **A8 Alignment Loop --
considered, rejected** and **A5 Wave Execution -- considered,
rejected**. The appendix names these two entries but does not restate
their rejection rationale on this page -- that reasoning lives in the
sibling file itself, not in Appendix B.

## Source

Appendix B, **The Agentic SDLC Handbook** by Daniel Meppiel --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/appendix-b-genesis-worked-example.html
