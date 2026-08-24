# The reference architecture, earned

Source: **The Agentic SDLC Handbook**, Daniel Meppiel, Ch. 22 --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch22-the-reference-architecture-earned.html.
See [index.md](index.md) for why this lives here rather than in
`references/harnesses/`.

This chapter revisits the reference architecture introduced in Ch. 4
after Part III's practitioner chapters, and argues that its
Skill-Persona-Context triplet is not a flat description of one
system's layout but a single composition rule applied recursively at
every depth.

## 22.1 Composition is recursive

Core principle: "the same Skill-Persona-Context triplet repeats at
every depth." The architecture's five-layer picture (Ch. 4, Figure
4.2) follows one rule applied repeatedly: a Skill dispatches Personas;
each Persona, in its own thread, may dispatch further Skills; those
Skills may dispatch further Personas. One composition rule, applied
many times, forms the complete system shape.

**Worked example -- Maya's PR #4711.** The pull request touches
`payments/charge.py` and bumps `stripe-python` from 7.2 to 7.4. The
team's review Skill fans out to six Personas in subagent threads: Tech
Lead, Senior Backend Engineer, Security Reviewer, Accessibility
Reviewer, Documentation Editor, Product Reviewer. When the Security
Reviewer encounters the version bump -- a change class outside its
rubric -- it dispatches a `CVE Triage Skill` in a fresh thread, which
loads its own pair of Personas: Threat Modeller and Compliance Check.

The nested Skill is declared as a manifest dependency, resolved the
same way any package dependency is:

```yaml
# packages/payments-review/apm.yml
name: payments-review
version: 2.3.0
description: Multi-lens code review for the payments service.
author: payments-platform
dependencies:
  apm:
    - org/cve-triage#v1.4.2
    - org/perf-review#v0.9.1
```

Nested Skills are declared under `dependencies.apm`, resolved via
`apm install`, and pinned in `apm.lock.yaml` like standard package
dependencies -- forming a directed graph of well-typed primitives,
owned via CODEOWNERS. "The same package manager that handles one
level of composition handles seven."

Existing operational disciplines port unchanged into this recursive
graph: semantic versioning, lockfiles, content hashing, CODEOWNERS
files, deprecation windows.

## 22.2 What makes the recursion governable

Two governing conventions keep the recursion from becoming
unaccountable:

**Convention 1 -- every Skill carries an eval as discipline.** A
Skill must declare what its output looks like and how to determine
correctness. The eval is the parent's stop condition: without one, the
parent must either re-dispatch (at cost) or trust the result without
verification. Today the eval lives alongside the bundle as test
inputs, expected outputs, and a runner maintained by the Skill's
author; a schema will formalize this later.

**Convention 2 -- every dispatch persists its plan.** A subagent
thread writes its working plan to a file readable by its parent,
returning not just a verdict but "verdict + plan trace," persisted
alongside the run. This lets an auditor six months later reconstruct
the decision without re-running it.

Eval bounds recursion **in space**: each level returns one well-typed
artefact. Plan persistence bounds recursion **in time**: each level
is reconstructible after the fact. "A Skill that fails eval-and-plan
is a prompt with ambitions." The return value from a dispatch is "a
Skill, of a known version, against a known Context, returning an
artefact that passed a known eval, with the trace on disk."

## 22.3 A Panel, walked end to end

The chapter walks Maya's PR #4711 through seven steps:

1. **Trigger.** Maya labels PR #4711 `needs-review`. A label-watcher
   in CI checks out the diff at the head commit and invokes the
   harness against the Review Skill bundle resolved as
   `org/payments-review#v2.3.0` from the project lockfile. The diff
   spans twelve files, including `payments/charge.py` (logic) and
   `requirements.txt` (`stripe-python` 7.2 -> 7.4).

2. **Load.** The Review Skill manifest declares its six Persona
   dependencies and a Context block containing: the diff via `git`;
   the codebase as files; the linked Jira ticket via a Jira MCP
   server; the team's security policies as files in a policy repo;
   the originating RFC from the wiki; and Figma frames from the PR
   description as multi-modal artefacts.

3. **Fan out.** The harness (Copilot CLI, Claude Code, Cursor, or a
   team-configured runtime) reads the compiled context, sees the
   Review Skill's six Persona dependencies, and opens six subagent
   threads simultaneously -- no user invocation required; the harness
   infers the dispatch from the loaded Skill, "like a build tool
   inferring compile steps from a manifest." Each thread receives the
   diff, its own context slice, and its own context budget; the
   lenses cannot contaminate each other (no cross-visibility).

4. **Recursion fires.** The Security Reviewer's rubric covers
   code-level concerns in-line but treats third-party dependency
   changes as requiring its own Skill. On encountering the
   `stripe-python` bump it dispatches `org/cve-triage#v1.4.2` in a
   fresh thread; CVE Triage loads its two Personas (Threat Modeller,
   Compliance Check) and its own Context (package advisory feed,
   project SBOM, organisation allow-list), returning:

   > **CVE Triage trace -- `stripe-python` 7.2 -> 7.4**
   > Advisories in range: 1 (CVE-2024-XXXX, severity moderate, fixed
   > in 7.4.1).
   > Allow-list status: package present at any version >= 7.0.
   > Verdict: ALLOW with pin to 7.4.1.
   > Plan persisted: `runs/2025-03-04/cve-triage-4711.md`.

5. **Verdicts return.** Each of the six Personas writes a one-line
   verdict plus a longer reasoning trace: Tech Lead -- approve,
   modulo synthesis; Senior Backend Engineer -- approve, flag
   `charge.py:142` as an extraction candidate for follow-up; Security
   Reviewer -- approve **with pin** to `stripe-python==7.4.1`,
   CVE-2024-XXXX trace attached; Accessibility Reviewer -- not
   applicable, no UI surface touched; Documentation Editor -- request
   changes, `docs/api.md` still references 7.2 retry behaviour;
   Product Reviewer -- approve, matches RFC-217 acceptance criteria.

6. **Synthesise.** The Tech Lead Persona, acting as synthesiser,
   receives the six verdicts plus the CVE trace. Synthesis is
   structured to preserve dissent rather than average it: any
   "request changes" survives unless explicitly overridden by a
   higher-priority lens, so the Documentation Editor's request and the
   Security Reviewer's pin both survive into the composed verdict:

   > **Verdict: REQUEST CHANGES.** Two follow-ups before merge:
   > 1. Pin `stripe-python==7.4.1` (Security; CVE-2024-XXXX trace
   >    attached).
   > 2. Update `docs/api.md` retry-behaviour note for 7.4 surface
   >    (Docs).
   >
   > Otherwise: approved against RFC-217. Recommend filing
   > `charge.py:142` extraction as a separate ticket.

7. **Maya reads one comment, acts on it.** She accepts the
   `stripe-python==7.4.1` pin into the diff, opens `DOCS-892` against
   `docs/api.md`, and re-labels the PR `needs-review` to fire a
   second pass.

The run persists as a trail:

```
runs/2025-03-04/4711/
├── plan.md
├── personas/
│   ├── tech-lead.md
│   ├── senior-backend.md
│   ├── security-reviewer.md
│   ├── accessibility-reviewer.md
│   ├── doc-editor.md
│   └── product-reviewer.md
├── nested/
│   └── cve-triage-stripe-python-7.4.md
├── synthesis.md
└── lockfile-snapshot.apm.lock.yaml
```

"Six months later, an auditor reading the lockfile and persisted plans
can reconstruct the entire decision tree without re-running anything."
The Tech Lead synthesiser never saw the threat-modelling thread; it
saw the Security Reviewer's verdict with the CVE trace as ground
truth. Maya never saw any of the eight Persona threads; she saw one
verdict. "The recursion is invisible from above and inspectable from
below."

## 22.4 What this changes for the architect

Three implications follow:

1. **MCP is one access mechanism, not the architecture.** The Model
   Context Protocol is an open standard stewarded by LF Projects under
   the Linux Foundation, and it sits in the Context half of the
   Skill-Persona-Context triplet, alongside files, CLI invocations,
   fetched URLs, and multi-modal artefacts -- a Persona can read a
   Jira instance, an internal API, or a SharePoint corpus via an MCP
   server without knowing the transport details. "Treating MCP as the
   architecture rather than as one mechanism is the most common shape
   of mistake an architect new to this substrate makes." An MCP
   catalogue is not a substitute for a Skill registry, eval
   discipline, or a lockfile.

2. **The patterns you already know apply.** Skill = Module with
   Facade (one entry point, one stable contract, swappable internals);
   Persona = Strategy (same input shape, different evaluation policy);
   the harness orchestrating a Panel = Mediator with Scatter-Gather
   distribution. "The substrate is new; the patterns are not." (The
   full Rosetta Stone and four-layer reconciliation is in Ch. 19,
   Section 19.3.)

3. **Registry and CODEOWNERS decisions matter this week, not agent
   vendor.** A team with an installed supply chain can change
   harnesses, frameworks, or cloud providers without re-authoring its
   primitives; a team without one cannot. (The five-day plan for this
   is in Ch. 27.)

## TL;DR -- one rule, applied recursively

1. **Composition is recursive.** The same Skill-Persona-Context
   triplet repeats at every depth; the dependency graph's shape
   mirrors the code dependency graph's shape.
2. **Eval and plan-persistence are what make it governable.** Eval
   bounds recursion in space; persisted plans bound it in time. A
   Skill missing either is a prompt with ambitions.
3. **Each level reads the level below as one primitive.** The
   synthesiser sees one verdict; the auditor reads the trail
   underneath. Invisible from above, inspectable from below.
4. **MCP is one access mechanism, not the architecture.** It lives in
   the Context half of the triplet alongside files, CLI invocations,
   and fetched URLs. Treating it as the substrate is the most common
   first-contact mistake.
5. **Your existing instincts are the right instincts.** Modules,
   strategies, mediators, lockfiles, CODEOWNERS -- the substrate is
   new, but the disciplines port across without modification.

## Source

Part III, Ch. 22: The Reference Architecture, Earned --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch22-the-reference-architecture-earned.html
