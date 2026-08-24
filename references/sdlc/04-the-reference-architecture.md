# The Agentic SDLC reference architecture

Source: **The Agentic SDLC Handbook**, Daniel Meppiel, Ch. 4 --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch04-the-reference-architecture.html.
See [index.md](index.md) for why this lives here rather than in
`references/harnesses/`.

## The wrong unit of architecture

The chapter's opening argument: standardisation effort should target
"the layered supply chain that connects" agents and platforms, not
picking a single tool vendor. The reasoning: "the output of one phase
has to become the input of the next phase, across teams, across
business units, across vendors, for years" -- a vendor choice doesn't
solve that continuity problem.

## The three layers (participant structure)

A coarse model of who/what does the work:

1. **Human Layer** -- where "judgment, accountability, and strategic
   decisions live": setting objectives, making architectural choices,
   defining quality standards, bearing responsibility.
2. **Agent Layer** -- where "AI capabilities execute within defined
   boundaries": generating code, producing reviews, drafting tests,
   surfacing patterns, operating within constraints the Human Layer
   sets via the PROSE framework (Ch. 13 -- see
   [prose-framework.md](prose-framework.md)).
3. **Platform Layer** -- the infrastructure enabling both: "source
   control, CI/CD pipelines, identity and access management,
   observability, artifact registries, and the APIs that connect
   them."

Layers stack (each depends on the one below); the Human and Agent
layers interact bidirectionally on top of the Platform layer.

## Mapping the layers across the lifecycle

Eight SDLC phases, each rated Now / Emerging / Directional for how far
agentic participation has actually matured, with human/agent/platform
responsibilities per phase:

| Phase | Human | Agent | Platform | Maturity |
|---|---|---|---|---|
| Ideate | Set objectives, scope | Research, surface conflicts | Knowledge bases, collaboration | Emerging |
| Plan | Architecture choices | Draft ADRs, decompose tasks | Issue trackers, project mgmt | Emerging |
| Code | Review output | Multi-file generation | IDE, SCM, context APIs | Now |
| Build | Own build config | Diagnose failures | CI/CD, dependency mgmt | Now |
| Test | Define test policy | Generate tests, coverage gaps | Test frameworks, infrastructure | Emerging |
| Review | Final code sign-off | Automated review, catch defects | PR APIs, policy engines | Now |
| Release | Go/no-go decision | Draft changelogs, flag breaking changes | Deployment pipelines, gates | Emerging |
| Operate | Own incident response | Correlate alerts, suggest actions | Monitoring, alerting, logs | Directional |

These eight phases roll up into three organisational buckets:

- **Intent** (Ideate + Plan) -- "What are we building and why?" --
  mostly Emerging.
- **Build** (Code + Build + Test + Review) -- "How do we turn intent
  into verified software?" -- the most mature bucket.
- **Operate** (Release + Operate) -- "How do we get software to users
  and keep it running?" -- Emerging/Directional.

The maturity tagging is deliberately blunt about limits: even where a
capability "works," e.g. test generation, "strategic test design still
requires human judgment" -- the Now/Emerging/Directional label tracks
what's actually proven in production, not what's technically possible
in a demo.

## The five-layer landscape (technical supply chain)

A second, orthogonal model -- the actual technical stack the layers
above run on, bottom to top:

1. **Platform** -- cloud, source control, identity, audit substrate.
2. **Context & Capabilities** -- organisation-authored procedures,
   lenses, knowledge bundles, expressed as version-controlled text.
3. **Governance and Distribution** -- catalogue, approval rules,
   declared dependencies, internal registry, package manager,
   ownership rules.
4. **Agent Harness** -- the runtime application developers and
   business users actually execute (vendor-specific, but all
   consuming the same load contract from layer two/three).
5. **SDLC Phases** -- Plan, Spec, Build, Review, Test, Deploy,
   Operate -- the visible application output.

The organising principle: "the artefact that flows up the layers is
the AI capability itself, behaving the way a software dependency
behaves" -- declared, resolved against a registry, installed at a
known version, replaced on publication. The governance layer (three)
is explicitly where "the auditable record of which AI capabilities ran
in production, at what version, and with whose approval" has to live
-- not at the runtime layer, not at the platform layer. Two enablers
make the model work in practice: discoverability (an IDP-backed
catalogue) and rollout (vendor harness-managed settings). The
handbook's cited reference implementation of this layer is
Microsoft's `zava-agent-config`.

## What changes about roles

A role-by-role table of what stays human, what agents absorb, and what
shifts in emphasis:

| Role | Stays human | Agents handle | Shift |
|---|---|---|---|
| Product Manager | Strategic prioritisation, stakeholder alignment, go/no-go | Research synthesis, competitive analysis, requirement drafting | More judgment, less information-gathering |
| Architect | System design decisions, technology selection, cross-team coordination | ADR drafting, dependency analysis, pattern detection | More review, less documentation |
| Developer | Code review, architectural compliance, complex problem-solving | Routine implementation, boilerplate, test generation, refactoring | More time specifying intent, less time typing code |
| QA Engineer | Test strategy, edge-case identification, exploratory testing | Test generation, coverage analysis, regression detection | More test design, less test writing |
| SRE/Ops | Incident ownership, capacity planning, reliability decisions | Alert correlation, runbook execution, incident timeline drafting | More system understanding, less routine response |

Pattern statement: "Agents absorb the mechanical and
information-processing work, while humans focus on the judgment,
strategy, and accountability work." Three new roles fall out of the
five-layer stack: **Domain Specialist** (authors procedures and lenses
at layer two), **Agentic Workflow Engineer** (pairs with the domain
specialist on complex procedures), and **Agent Operations Specialist**
(operates the registry/package-manager/ownership rules at layer
three, typically inside the platform team).

## The architecture decision matrix -- where to start

A phase-by-phase table for deciding where to invest first:

| Phase | Start if... | First investment | Maturity prerequisite | Timeline |
|---|---|---|---|---|
| Code | Developers already use AI tools | Custom instructions encoding conventions | Linter, test suite, CI | 2-4 weeks |
| Review | PR review is a bottleneck | Agent-assisted review with human sign-off | Documented standards, clear criteria | 4-8 weeks |
| Test | Low coverage, brittle tests | Agent-generated tests, human-defined strategy | Test framework, coverage tooling, policy | 4-8 weeks |
| Plan | Slow planning, inconsistent artefacts | ADR templates, specification structures | Issue tracker, documented decisions | 8-12 weeks |
| Build | CI failures consume time | Agent-assisted diagnostics, fix suggestions | CI/CD with structured error output | 4-8 weeks |
| Release | Manual, error-prone releases | Agent-drafted changelogs, breaking-change detection | Semantic versioning, structured commits | 8-12 weeks |
| Ideate | Ad hoc research/discovery | Agent-assisted synthesis, prior-art surfacing | Knowledge base, searchable decision history | 12-18 weeks |
| Operate | Slow incident diagnosis | Agent-assisted alert correlation, timeline drafting | Observability stack, structured runbooks | 12-18 weeks |

Three observations the chapter draws from the table: (1) "start where
the tooling is mature and the payoff is immediate" -- Code, Review,
Test; (2) "invest in context before investing in agents" -- the listed
prerequisites are documentation, structure, and tooling, not agent
capability itself; (3) "expand based on evidence, not ambition."

## Build, buy, or compose

A second decision matrix, this time by context domain rather than
SDLC phase:

| Domain | Build | Buy | Compose |
|---|---|---|---|
| Work context | Internal knowledge base, custom decision-record tooling | Internal KB SaaS, collaboration-platform wikis | API connectors bridging tools to agent context |
| Data context | Custom domain-model documentation, internal taxonomies | Data catalog platforms, governed metadata | Federation layers exposing data definitions |
| Code context | Internal capability authoring, custom rules/configurations | Runtime-vendor integrated surfaces | Open-source community bundles, registry-distributed configurations |

Pattern: work and data context are organisation-specific and need
build/compose; code context is the most composable domain, because it
has standardised formats and community-shared bundles distributed
through the layer-three registry. Strategic framing for vendor
evaluation: "no single vendor covers the AI-capability supply chain
end-to-end today" -- plan for composed solutions and evaluate vendors
on how their pieces fit into the supply chain, not on end-to-end
coverage claims.

## Start anywhere, expand deliberately -- the phased-adoption timeline

A gated rollout plan with explicit go/no-go criteria at each stage:

- **Month 1**: one team, one phase (usually Code), one investment
  (custom instructions for the team's top five conventions). Measure
  agent output quality before/after. **Gate to expand**: agent code
  passes linting on first attempt 70%+ of the time, and the team has
  documented five or more conventions in machine-readable form.
- **Month 3**: extend to Review -- agent-assisted code review with
  human sign-off. Measure review turnaround time and defect escape
  rate. **Gate**: agent rejection rate at or below the human baseline,
  and median review turnaround down 15%+.
- **Month 6**: add Test -- agent-generated test cases against a
  human-defined strategy. Measure coverage change and test
  maintenance cost. **Gate**: coverage up 10+ percentage points on
  agent-covered modules, with rework under 30%.
- **Month 12**: evaluate Plan and Build phases. **Gate**: human
  intervention rate down 20%+ from the Month 3 baseline, and two or
  more context feedback cycles have measurably improved quality.
- **Month 18**: assess Operate-phase readiness. **Gate**: structured
  runbooks exist for 80%+ of common incident types, and alert
  correlation accuracy is at 90%+.

Key principle: "the sequence matters more than the timeline" -- the
dates are illustrative, the gated ordering (mature-tooling phases
first, Operate last) is the actual claim. The chapter closes by noting
the five-layer landscape generalises beyond software to any
procedure-shaped enterprise work: legal review, financial close, M&A
diligence, marketing approvals, regulatory filings.

## Source

Ch. 4, Part II (For Leaders), *The Agentic SDLC Handbook* --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch04-the-reference-architecture.html.
(Part II is otherwise leadership/governance content out of scope for
this folder -- Ch. 4 is captured here as the one named exception, per
its reference-architecture content being technical rather than
leadership-facing.)
