# The execution meta-process

Source: **The Agentic SDLC Handbook**, Daniel Meppiel, Part III (For
Practitioners), Ch. 18 --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch18-the-execution-meta-process.html.
See [index.md](index.md) for why this lives here rather than in
`references/harnesses/`.

Opening claim: "Here is what nobody tells you about using AI agents on
a real codebase: the agent is the easy part. The hard part is knowing
what to ask, in what order, and when to stop asking and start
verifying." The chapter's subject is a methodology for operationalising
agent-driven change across a real codebase -- moving from "I need to
change 75 files" to "the PR is merged with zero regressions" -- that
sits above any specific tool's mechanics: "It works regardless of
which AI coding tool you use, because it operates at a level above any
specific tool's mechanics."

## The five phases

1. **AUDIT** -- build a multi-perspective understanding of the code
   before any change begins. Dispatch 2-4 expert agents in parallel,
   each with a distinct lens (architecture, domain, security); this is
   a strictly **read-only** operation -- agents explore, never modify.
   Output: ranked findings with severity, file-and-line citations, and
   remediation guidance. Human decision: review the audit reports and
   decide which findings matter now versus which are deferred.
2. **PLAN** -- define scope explicitly (what's in, out, deferred), name
   agent teams with designated personas (e.g. "python-architect
   leads," "cli-logging-expert leads"), decompose the work into
   dependency-ordered waves (Wave 0 has no dependencies; Wave N depends
   only on Waves 0..N-1), list priority-ordered principles for trading
   off decisions, and enumerate hard constraints ("Do NOT modify test
   infrastructure"). Human decision: approve the plan -- described as
   "the highest-impact moment in the entire process." "No implementation
   starts until you approve the plan. This is the single most important
   gate."
3. **WAVE** -- execute each wave as a set of tasks with no unmet
   dependencies, dispatching parallel agents grouped so no two agents
   edit the same file simultaneously (the **one-file-one-agent rule**,
   carried over from Chapter 17). Each agent receives precise
   instructions: which files, what patterns, what constraints, what
   verification to run.
4. **VALIDATE** -- run the full test suite after every wave (unit,
   acceptance, optionally integration/end-to-end); spot-check the most
   complex changes, boundary conditions named in the plan, and areas
   where agents are most likely to err. Human decision: ready to ship?
5. **SHIP** -- final verification and merge: update the changelog if
   not already done during wave execution, push the branch, merge once
   CI passes. Output: a merged PR with a bisectable history -- one
   commit per wave, each with passing tests.

Figure 18.1 in the source traces this as a loop, not a straight line:
AUDIT -> PLAN -> WAVE -> VALIDATE, with three branches out of VALIDATE
-- "all waves done" to SHIP, "next wave" back to WAVE, and "failure" to
the ADAPT loop, which feeds back into PLAN.

## The checkpoint: four parts, every wave

"A checkpoint is the pause between waves. It is the mechanism that
makes the meta-process safe." Every wave passes through the same four
checks:

1. **Test gate** -- the full test suite runs; if any test fails, the
   wave is not committed and the failure is triaged.
2. **Spot-check** -- a human reviews a sample of changes (boundary
   conditions, pattern compliance, scope discipline).
3. **Commit** -- every wave gets its own commit with a descriptive
   message.
4. **Plan review** -- optionally, review and adjust the remaining plan.

The rule is absolute: "Every wave ends with green tests and a commit.
No exceptions." The rationale is bisectability: "If wave 3 introduces a
regression, and you haven't tested since wave 0, you don't know
whether the regression was introduced in wave 1, 2, or 3. You can't
bisect. You can't revert a single wave."

## The ADAPT loop

When a checkpoint fails -- tests are red, an agent is stuck, a
dependency was missed -- the meta-process does not stop; it adapts.
"The ADAPT loop...is not a fallback. It is a designed part of the
process." Figure 18.3 traces the cycle: **DETECT** (failure or stall)
-> **DIAGNOSE** (root cause) -> **ADJUST** (modify the plan) ->
**EXECUTE** (re-run the wave), with a dotted "if new issue" edge back
to DETECT.

The loop specifically handles: agent stalling (context exhaustion),
merge conflicts (if waves share files), stale context (if waves are
too coarse), and cascading failures (if dependencies were missed). But
adaptation is disciplined, not loose: "Adaptation is conservative. You
add tasks, split tasks, reorder waves. You do not skip validation. You
do not merge unvalidated work. The checkpoint discipline holds
even -- especially -- when things go wrong."

## Wave sizing

| Factor | Smaller waves (2-4 agents) | Larger waves (6-10 agents) |
|---|---|---|
| Execution time | 3-5 minutes | 8-12 minutes (slowest agent dominates) |
| Debug difficulty | Low -- few changes to inspect | High -- more changes interacting |
| Commit granularity | Fine -- easy to bisect | Coarse -- harder to isolate regressions |
| Overhead | Higher -- more validation cycles | Lower -- fewer cycles |

Decision heuristic: start with smaller waves; combine tasks only when
they are genuinely independent and the validation overhead outweighs
the debugging advantage.

**The self-sufficiency test**, applied to every task before it enters
a wave: can an agent complete this without asking a question? If no,
the task isn't ready -- refine the instructions, split the task, or
defer it to a later wave. Purpose: eliminate mid-wave escalations.

## Worked example: PR #394 (APM auth + logging overhaul)

Scope: five cross-cutting concerns (auth-resolver deduplication,
verbose-logging coverage gaps, `CommandLogger` migration, unicode
symbol cleanup, test coverage) across 75 files. Full execution log,
escalation events, and plan iterations are documented in the Part IV
case study.

| Phase | Duration | Agents | Outcome |
|---|---|---|---|
| Audit | 3 min | 2 parallel (architecture + logging/UX) | Severity-ranked findings with file-line citations |
| Planning | 5 min | -- | 8 iterations; all findings kept in scope; 2 teams defined |
| Wave 0 -- Foundation | 5 min | 2 parallel | Resolver dedup + symbol definitions; tests green |
| Waves 1-2 -- Core | 8 min | 5 parallel | Verbose logging + `CommandLogger` migration; tests green |
| Wave 2b -- Recovery | 7 min | 2 replacement | `install.py` agent stalled on context exhaustion; split and re-dispatched |
| Wave 3 -- Polish | 4 min | 1 | Unicode symbol cleanup; tests green |
| Ship | 2 min | -- | Spot-check, full suite green, CI passed, merged |

Total execution time: roughly 90 minutes, reflecting "an experienced
practitioner with mature instrumentation" -- a first attempt is
estimated at three times longer.

Example plan structure, close to verbatim:

```
Scope
  Auth resolver deduplication, verbose coverage gaps,
  CommandLogger migration, unicode cleanup.
  Out of scope: New auth providers, CLI help text changes.

Teams
  Architecture: python-architect leads.
    Owns: type safety, separation of concerns, dead code.
  Logging/UX: cli-logging-expert leads.
    Owns: verbose coverage, CommandLogger, symbols.

Waves
  Wave 0 (foundation): Protocol types, method moves — fully parallel.
  Wave 1 (core): Verbose coverage — depends on Wave 0 APIs.
  Wave 2 (migration): CommandLogger migration — depends on Wave 1 patterns.
  Wave 3 (polish): Unicode cleanup — depends on Wave 2 completeness.

Principles (priority order)
  1. SECURITY — no token leaks, no path traversal.
  2. CORRECTNESS — tests pass, behavior preserved.
  3. UX — first-class developer experience in every message.
  4. KISS — simplest correct solution.
  5. SHIP SPEED — favor shipping over perfection.

Constraints
  Do NOT modify test infrastructure.
  Do NOT change CLI command signatures.
  Do NOT alter public API return types.
```

**Three practitioner roles, three interventions, no overlap** (the
roles are defined in Chapter 10):

1. **Architect** (during planning) -- decided to keep every severity
   level in scope rather than defer moderate findings; a judgement call
   about priorities, release timeline, and the cost of context-switching.
2. **Escalation handler** (during Wave 2) -- diagnosed the `install.py`
   agent's stall (58 call sites exhausted its context window) and
   chose to split the remaining work across two replacement agents
   rather than retry the single agent.
3. **Reviewer** (during Wave 2b) -- triaged a test failure (an
   ordering issue in the migration: a function call was migrated but
   its setup code wasn't) and directed a targeted fix.

## Scaling the process

**Small changes (fewer than 10 files):** audit compresses to a single
expert agent; planning is a mental model with one wave; execution is
one wave of 1-2 agents. Validate and ship are unchanged. Formality
compresses; the structure is preserved.

**Large changes (more than 100 files):** audit expands to 4-6 expert
agents across different subsystems/concerns; planning expands to 6-10
waves with careful dependency mapping; execution splits into a
two-team structure (architecture team plus domain team); the ADAPT
loop is more likely to trigger, so the plan should anticipate recovery
waves. The preservation rule holds regardless of scale: each wave
remains independently verifiable.

## What the meta-process produces

1. **Bisectable history** -- one commit per wave, each with passing
   tests, so regressions can be pinpointed.
2. **Auditable decisions** -- the plan, checkpoint records, and
   escalation records document the full decision chain.
3. **Reproducible process** -- the same process, codebase, and context
   files produce substantially similar output across practitioners.
4. **Proportional cost** -- time scales with the scope of the change,
   not the size of the whole codebase.

## How this connects to neighbouring chapters

Chapter 10 supplies the three practitioner roles (architect,
escalation handler, reviewer) that surface during execution. Chapter
13's PROSE constraints shape instructions given during wave execution.
Chapters 14 and 15 (load lifecycle; attention and context economy)
govern what reaches the model and how much of it survives attention.
Chapter 16 (the deterministic/probabilistic boundary) is what makes
gated execution safe. Chapter 17 (multi-agent orchestration) is the
source of session-isolation discipline and the one-file-one-agent
rule. Chapter 20 (anti-patterns and failure modes) catalogues the
silent failures -- a token-type correction and a silent `NameError` --
that this chapter's escalations during validation caught. Part IV's
Case Study 1 carries the full execution log for PR #394.

## Source

Ch. 18, Part III -- For Practitioners, *The Agentic SDLC Handbook* by
Daniel Meppiel --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch18-the-execution-meta-process.html
