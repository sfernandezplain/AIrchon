# Case study: the APM auth + logging overhaul

Source: **The Agentic SDLC Handbook**, Daniel Meppiel, Part IV case study --
https://danielmeppiel.github.io/agentic-sdlc-handbook/case-study-apm-overhaul.html.
See [index.md](index.md) for why this lives here rather than in
`references/harnesses/`.

A worked example of the book's technical patterns (PROSE, wave-based
orchestration, escalation levels) applied to a real refactor of
**APM** (Application Performance Monitoring), a Microsoft open-source
repository -- PR #394, consolidating authentication, abstracting
logging, and adding diagnostic collection.

## The problem

A user reported confusing UX when `apm install` failed for GitHub
Enterprise Managed Users (EMU) packages. Diagnosis surfaced three
systemic failures:

- `_validate_package_exists()` ran a bare `git ls-remote` with no
  credentials; the `GITHUB_APM_PAT` environment variable was ignored
  for github.com hosts.
- Four inconsistent authentication implementations scattered across
  the install, download, copilot, and operations modules.
- "766 ad-hoc `_rich_*` logging calls across 27 files with no shared
  abstraction."

The fix ultimately touched **75 files** (47 planned + 28
dependency/test/configuration files).

## Agentic techniques applied

**PROSE constraints invoked by name:**

- *Progressive Disclosure* -- context budgeting; splitting work to fit
  finite context windows.
- *Reduced Scope* -- scope changes went through the plan gate (an
  L4 escalation) rather than expanding mid-wave.
- *Safety Boundaries* -- filesystem verification after every agent
  dispatch, checkpoint discipline, and behavioural assertions over
  raw pass/fail test counts.

**Orchestration approach:**

- A six-expert **audit panel**, run in parallel, during diagnosis:
  GitHub auth patterns, EMU constraints, Azure DevOps auth,
  architecture design, CLI UX, and documentation.
- A **fleet of roughly 25 agents** across **five execution waves**.
- A **one-file-one-agent-per-wave** rule to prevent merge conflicts.

**Session decomposition:** audit phase (expert panel) -> 8 plan
iterations before approval (v1-v8) -> 5 execution waves, each closed
out with checkpoint discipline -> a sequential shipping phase.

**Validation gates:** the full test suite ran after every wave;
target files were diffed on disk rather than accepting an agent's
self-report; checkpoints asserted on observable behaviour (e.g.
verbose mode actually producing output), not just test pass counts.

## Concrete numbers

| Metric | Value |
|---|---|
| Files changed | 75 (47 planned + 28 dependency) |
| Lines changed | +7,832 / -1,074 |
| Tests before | 2,829 |
| Tests after | 2,897 (+115 written, -47 consolidated = +68 net) |
| New tests | 78 unit + 26 integration + 11 diagnostics |
| Agent dispatches | ~25 across 5 waves |
| Audit-panel agents | 6 |
| Plan iterations | 8 (approved at v8) |
| Escalations | 5 (1x L2, 2x L3, 2x L4) |
| Wave execution time | ~90 minutes (active agent + human review) |
| Total wall-clock time | ~16 hours across 2 sessions |
| Human time split | ~30% planning, ~20% monitoring, ~25% interventions, ~25% review |

`install.py` alone contained 58 of the 766 `_rich_*` logging calls --
the largest single-file share.

New abstractions created: `AuthResolver`, `CommandLogger`,
`DiagnosticCollector`.

## Problems encountered and how they were solved

**Escalation 1 -- context window exhaustion (Anti-pattern #11).** The
agent migrating `install.py` (58 call sites, the largest single file)
ran 45+ minutes and then "stopped producing coherent output." The
orchestrator escalated to L3, wrote a Python script to strip 30 dead
else-branch fallbacks, and manually fixed 3 duplicate calls. Lesson:
58 call sites per dispatch was too many; the file should have been
split across two waves.

**Escalation 2 -- hallucinated edits (Anti-pattern #12).** An agent
reported all Unicode replacements complete (`✓`->`[+]`, `✗`->`[x]`,
`⚠`->`[!]`, `→`->`->`, `—`->`--`), but inspecting the file showed zero
changes -- it had written to a temporary copy. The orchestrator
performed the replacements manually across 4 files. Lesson: never
accept an agent's self-report without a `diff`.

**Escalation 3 -- stale context between waves (Anti-pattern #13).** The
expert panel misclassified `ghu_` tokens as EMU-specific; the user
corrected that EMU users actually receive standard
`ghp_`/`github_pat_` tokens. The incorrect host-gating logic was
removed from `AuthResolver` and auth tests re-run. Lesson: expert
findings must be validated before they become wiring instructions.

**Escalation 4 -- fine-grained PAT 403 (L4, plan-scope change).**
Authentication still failed with a valid fine-grained PAT; root cause
was that the `git ls-remote` URL format sent Basic auth, which GitHub
rejects for fine-grained PATs. The fix pivoted validation to the
GitHub REST API, giving a single code path for all token types. This
was handled correctly as an L4 escalation -- scope expanded through
the plan gate before execution resumed.

**Escalation 5 -- silent NameError in verbose logging.** `_rich_echo`
was never imported in `install.py`; the `verbose_log` lambda raised a
`NameError` that was silently swallowed by an outer `try/except`.
"2,829 passing tests did not catch a silent `NameError`" because the
suite never asserted on verbose output; a behavioural-assertion
checkpoint was added to catch this class of failure going forward.

## Lessons learned

Five explicit takeaways:

1. "Budget context before you dispatch. Count call sites; split at
   ~25 per agent. 58 was too many."
2. "Verify filesystem, not self-reports. `diff` target files after
   every dispatch. Agent success messages are probabilistic output."
3. "Expert panels are audits, not oracles. Panel findings must be
   validated before they become wiring instructions."
4. "Expand scope through the plan gate. Mid-planning expansion is
   healthy. Mid-wave expansion is dangerous."
5. "Checkpoints must assert behaviour. 2,829 passing tests did not
   catch a silent `NameError`. Assert on observable output."

Three universal properties the case study says were validated:

- **Context remains finite and fragile** -- the `install.py` escalation
  proved context budgeting is architecturally necessary, independent
  of model improvement.
- **Output remains probabilistic** -- the Unicode agent's success
  report diverged from actual filesystem state; reliability requires
  checkpoint discipline, not trust.
- **Human judgment remains the bottleneck and the differentiator** --
  the user's v7 escalation (demanding all commands be covered, not
  just `install`) was the highest-leverage decision in the project,
  and no agent suggested it.

Comparative baseline the chapter cites: "Similar-scope manual
refactors (consolidating authentication patterns across 40+ files)
have taken 3-5 days of focused engineering time."

## Source

Part IV case study, **The Agentic SDLC Handbook** by Daniel Meppiel --
https://danielmeppiel.github.io/agentic-sdlc-handbook/case-study-apm-overhaul.html
