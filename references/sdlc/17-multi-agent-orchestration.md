# Multi-agent orchestration

Source: **The Agentic SDLC Handbook**, Daniel Meppiel, Ch. 17 --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch17-multi-agent-orchestration.html.
See [index.md](index.md) for why this lives here rather than in
`references/harnesses/`.

The chapter addresses what happens when a single agent thread hits a
change spanning 40+ files across multiple concerns: it becomes a
bottleneck not from lack of intelligence but from "lack of bandwidth."
Multi-agent orchestration solves this with specialised agent threads
(subagents), each working within a manageable context budget, composed
into one agentic system. The central discipline is "getting the
benefits of parallelism without paying the costs of chaos."

Part III's preface (Ch. 9) names four composition patterns the field
has converged on: **Panel**, **Wave**, **Scatter-Gather**, and
**Subagent**. Panel -- multiple specialist agent threads reviewing the
same artefact in parallel, each loading scope-attached rules and
producing independent findings, reconciled by a synthesizer (human or
arbiter agent) -- is treated as the anchor case, because it
"concentrates every other discipline in this chapter into a single,
observable case."

## When one agent is enough

A decision matrix for choosing single- vs. multi-agent execution:

| Dimension | Single agent | Multiple agents |
|---|---|---|
| Files changed | < 10 | > 15 |
| Concerns | 1 | 2+ |
| File dependencies | Linear | Graph (can parallelise) |
| Required expertise | One domain | Multiple domains |
| Time pressure | Low | Moderate to high |
| Risk of context overload | Low | High |

The boundary at 10-15 files is "approximate and experience-derived,
not precisely measured." When the case is marginal, the guidance is to
err toward a single agent.

## Agent specialisation patterns

**Pattern 1 -- Writer / Reviewer / Tester.** Separates code production
from validation across three roles: the writer optimises for
correctness and completeness; the reviewer "evaluates output on its
own merits, not anchored by the writer's reasoning" and receives the
diff plus the original source, not the writer's conversation history;
the tester optimises for verifiable behaviour. Diagrammed as
Writer -> Reviewer (receives code changes) -> Tester (receives
findings: bugs, logic errors, security) -> verified output.

**Pattern 2 -- Domain teams.** Organises agents by area of expertise
rather than by workflow stage. Each team owns a concern and all
related files -- e.g. an architecture team carrying type definitions,
module boundaries, the pattern catalogue, and the dependency graph,
alongside a domain-expert team carrying output conventions, symbol
dictionaries, UX guidelines, and migration patterns. This scales by
adding teams, with no agent carrying irrelevant context, and the
coordination cost sits between teams rather than within them.

*Concrete dispatch example.* Preparing a domain-team dispatch means
assembling three elements: (1) instruction files loaded into context,
e.g. `.ai/instructions.md` (project-wide conventions, always loaded)
plus `.ai/integrations/logging.md` (logging-specific patterns and
examples); (2) a dispatch prompt with a task description, an exclusive
file list, a reference to already-committed code, scoped instructions
(two files, not twelve), built-in validation (a test command to run
before reporting done), and explicit constraints; (3) the file-list
assignment itself, giving each agent exclusive ownership. Worked
prompt excerpt:

```
Migrate the following files from print-based output to the structured
logger established in Wave 0. Use the LoggerFactory pattern from
src/core/logger.py (committed and tested).

Files assigned to you (exclusive ownership this wave):
  - src/commands/install.py
  - src/commands/resolve.py
  - src/commands/validate.py

Constraints:
  - Do NOT modify any file not in this list.
  - Do NOT change function signatures or public APIs.
  - Preserve all existing behavior — update log output only.
  - Use _rich_info() for informational messages, _rich_warning()
    for warnings.

When complete, run: pytest tests/commands/ -x
Fix any failures before reporting done.
```

Preparing a dispatch prompt and file list takes an orchestrator
roughly 2-3 minutes, plus shared monitoring time across active agents.

**Pattern 3 -- Audit / Execute / Validate.** Separates read-only
discovery from read-write execution: audit agents explore the codebase
without modifying it (multiple can run simultaneously with no
interference); a human decision point sits between audit and
execution; execution agents receive scoped tasks with file
assignments; validation agents perform a read-only review. Diagrammed
as Audit agents (read-only) -> Planning (human decision) -> Execution
agents (read-write) -> Validation agents (read-only) -> Ship.

## Parallelisation strategies

**The one-file-one-agent rule.** "Within a single execution batch, no
two agents may modify the same file." This guards against the most
common failure mode in parallel execution: Agent A modifies a file,
then Agent B attempts the same file, and string-matching edits fail
silently or produce corrupted output because the expected text has
already changed.

**Wave-based parallelism.** Work is structured as a sequence of
batches ("waves") with explicit dependencies between them; within a
wave, agents are independent -- they share no files and make no
assumptions about each other's progress. Wave sizes of 2-3 agents are
optimal, completing in 3-5 minutes (the slowest agent dominates); a
wave of 8 agents still takes 8-10 minutes and increases failure risk.
Guidance: "prefer more, smaller waves over fewer, larger ones." An
example three-wave structure (Foundation, Core, Integration): Wave 0
runs Types/Utilities/Config agents in parallel, merged at a test
checkpoint; Wave 1 runs Migration/API/Auth agents, merged at another
checkpoint; Wave 2 runs Wiring/Tests agents. Dependencies flow
downward, and a timeline diagram shows Wave 0 completing in 5-7 time
units, Wave 1 spanning 7-15, and Wave 2 spanning 15-21, with
checkpoints at each wave boundary.

**Pipeline parallelism.** Review and test operations run in parallel
across workflow stages while execution agents work on later waves --
e.g. review agents can start reviewing Wave 0's output while execution
agents work on Wave 1, provided review is read-only and execution has
no backward dependency on review findings. A diagram shows Wave 0
agents running across time units 0-8, review across 8-12, and tests
across 8-18, overlapping with Wave 1 agents running 10-22 and their
review 22-26.

## Conflict resolution

**File conflicts** -- two agents need to modify the same file.
Resolution: merge the tasks into a single agent's scope, or move one
task to a later wave. Files that attract changes from multiple
concerns are coordination bottlenecks and should be assigned to one
agent per wave even if that means handling multiple concerns.

**Semantic conflicts** -- two agents produce independently correct but
mutually inconsistent output. Resolution is foundation-before-migration
wave ordering: changes that establish new patterns (type definitions,
utilities, conventions) go in early waves, and later waves consume
those patterns; the committed wave state is ground truth for the next
wave.

*Recovery walkthrough (PR #394).* Wave 0 established a new
`OperationError` type replacing the old `ValueError` pattern. Wave 1's
domain agent, focused on logging context without error-handling
context, added error paths still using the old `ValueError` pattern.
Integration tests caught the mixed error types. Recovery: (1)
detection via the integration test suite catching unhandled
exception-type mismatches; (2) diagnosis -- the orchestrator identified
the missing error-handling context in the Wave 1 dispatch prompt, in
about two minutes; (3) recovery -- a targeted Wave 2b with two agents:
one replacing every `ValueError` raise with `OperationError` across
three command modules, the other updating test files to assert on
`OperationError` fields. Key lesson: "fix forward rather than
reverting" -- a surgical recovery wave addresses a surgical failure;
the original logging migration was 90% correct and did not need
redoing.

**Design conflicts** -- agents follow genuinely different design
philosophies. Resolution: escalate to a human using the plan's
priority-ordered principles; if the principles don't resolve it, the
human decides and documents the rationale.

## The human as orchestrator

### The escalation protocol

A four-level escalation system:

| Level | Trigger | Response | Example |
|---|---|---|---|
| L1: Self-heal | Agent hits a debuggable test failure | Agent fixes and continues | Type error in generated code |
| L2: Retry | Agent produces incomplete output | Re-dispatch with a refined prompt | Agent missed 3 of 12 files in scope |
| L3: Human decides | Trade-off between competing principles | Human makes the design call | UX convention vs. architectural purity |
| L4: Scope change | A finding requires work outside the current plan | Human creates a follow-up task | Discovery of a pre-existing, unrelated bug |

Reference distribution from PR #394: roughly two-thirds of resolutions
were autonomous (L1), one-eighth were automated retries (L2), and
one-fifth were human decisions (L3/L4) -- three interventions across
~25 agent dispatches, a ~12-20% rate depending on how it's counted.
Guidance: if the L3+ rate exceeds 25%, "the plan needs more specific
principles or better task scoping"; if it's below 5%, "the work may be
too simple for multi-agent orchestration, or review may be
insufficient."

## The coordination tax: honest numbers

### Worked case study -- PR #394: APM Auth + Logging Overhaul

75 files across five concerns, handled by two teams (an
architecture team led by an architect agent, and a domain team led by
a logging-expert agent) across four waves plus one recovery wave.

- Total agent computation time: ~24 minutes.
- Total elapsed time: ~90 minutes (including human planning,
  monitoring, and review).
- Estimated sequential-execution alternative: 45-60 minutes of agent
  time plus 30-45 minutes of rework, i.e. 75-105 minutes total --
  parallelism saved roughly 21 minutes against that estimate.
- Wave sizes ranged from 1 to 5 agents.
- Human time breakdown: planning/partitioning ~30%, monitoring
  execution ~20%, handling interventions ~25%, post-execution review
  ~25% -- ~45 minutes of human time total.
- Intervention rate: 3 human interventions across ~25 agent dispatches
  (12%, below the 15-20% starting hypothesis); all three were judgment
  calls, none were design conflicts between agents.

Key insight: the multi-agent approach "did not save total elapsed
time but traded human planning time for agent quality" -- it replaced
30-45 minutes of debugging context-degraded output with 45 minutes of
coordination, for a better result.

### The sweet spot

Multi-agent orchestration pays for itself when: file count exceeds 20
across 2+ concerns; concerns partition cleanly; context degradation
(quality, not just speed) is the real bottleneck; and the team will
repeat this more than once (a second orchestration takes roughly half
the planning time of the first). Below the 20-file threshold, planning
overhead exceeds the parallelism benefit.

Overhead guidance: a well-planned execution spends 40-60% of human
time on coordination; a poorly planned one spends 70-80%+, at which
point "a single agent with good context would have been faster."

## Session management

Information flows between agents "through committed artifacts, not
through shared sessions." When Agent B needs Agent A's work, it reads
the committed files -- the same files that passed tests and validated
at the wave checkpoint -- never Agent A's internal reasoning or
discarded alternatives. A diagram shows three separate agent boxes,
each with an isolated conversation history, all connected to a shared
filesystem where committed files are the ground truth between waves.

## Anti-patterns

Named in the chapter's discussion of the Panel pattern (detailed
further in Appendix B's Genesis worked example):

- **PANEL-WITHOUT-SYNTHESIS** -- multiple lenses produce independent
  reports and the user reads N reports instead of one reconciled
  decision.
- **PANEL-IN-ONE-CONTEXT** -- all N lenses are played sequentially in
  a single context window, each contaminating the next; described as
  "the dominant senior-engineer failure."
- **IMBALANCED PANEL** -- the dissenting lens provides the
  highest-information signal, but the synthesis ignores it.

Other failure modes discussed: context degradation in single-agent
approaches once past roughly 20 files; dispatching into
Audit/Execute/Validate without the scope being fully known in advance;
and redispatching an entire failed wave instead of a surgical recovery
wave.

## Putting it together (workflow diagram)

The chapter closes with a complete multi-agent orchestration workflow,
diagrammed as: **1. ASSESS** scope -> **2. SPECIALIZE** team ->
**3. PARTITION** files -> **4. ORDER** waves -> **5. DISPATCH** execute
-> **6. VALIDATE** test & check, with feedback loops: a pass moves to
success; a failure moves to a DIAGNOSE step that branches either to
L1/L2 (retry, looping back to step 5) or to L3/L4 (human decides,
looping back to step 4).

## How this connects to neighbouring chapters

Chapter 16 (the deterministic/probabilistic boundary) is treated as
prerequisite: that seam applies between agents here as well as between
model and substrate. Chapter 18, "The Execution Meta-Process," is
described as the capstone that walks the Panel pattern end-to-end
against a real skill, using a five-phase meta-process. Chapter 22,
"The Reference Architecture, Earned," walks Panel end-to-end in full
detail. Chapter 4 defines the five-layer reference architecture,
including the Agent Harness layer that manages sessions, context
loading, and file I/O. Chapter 23 gives the detailed execution
walkthrough of the APM Auth + Logging Overhaul case study; Chapters 24
and 25 cover further case studies (writing a ~68,000-word book with
agent fleets; the publishing pipeline). Appendix B excerpts the
architectural-patterns treatment of PANEL-WITHOUT-SYNTHESIS,
PANEL-IN-ONE-CONTEXT, and IMBALANCED PANEL.

## Source

Ch. 17, Part III (For Practitioners), *The Agentic SDLC Handbook* --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch17-multi-agent-orchestration.html
