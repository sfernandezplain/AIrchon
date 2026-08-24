# The PROSE framework

Source: **The Agentic SDLC Handbook**, Daniel Meppiel, Ch. 13 --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch13-the-prose-specification.html.
See [index.md](index.md) for why this lives here rather than in
`references/harnesses/`.

The handbook is explicit that PROSE is "an opinionated discipline, not
a standards body or a published spec" -- distilled practice patterns
for authoring specs, prompts, and project structure so that AI-agent
output stays reliable, verifiable, and maintainable, not a technical
mechanism of how a harness or model itself works.

## The problem it addresses

"Context is finite and attention degrades under load." PROSE
constrains how information flows to an agent, how tasks are sized, and
how systems are composed, to keep output reliable despite the
inherent variance in model output.

## The five constraints

**P -- Progressive Disclosure.** Structure information to reveal
complexity progressively; context arrives just-in-time, not
just-in-case. Practice: hyperlinked references with descriptive labels
(`[authentication patterns](../../docs/auth-patterns.md)`) instead of
inlining full docs; skill metadata describes when to activate before
loading full content. Anti-pattern: "context dumping" -- inlining
thousands of words of unrelated guidance into one document.

**R -- Reduced Scope.** Match task size to context capacity; complex
work is decomposed into tasks sized to fit. Sizing heuristic: "the
best-sized task is one the agent can complete without asking a
follow-up question." Practice: phase decomposition (separate planning,
implementation, testing into distinct sessions with fresh context);
split work by domain rather than combining frontend and backend in one
session. Anti-pattern: adding requests incrementally mid-session
("also update tests," "refactor this too"), fragmenting attention
across domains.

**O -- Orchestrated Composition.** Favour small, chainable primitives
over monolithic frameworks; build complex behaviour by composing
simple, well-defined units. Practice: atomic instruction files,
skills, agents, prompts, and specs, each with a focused purpose;
workflows reference these building blocks by composition rather than
duplicating their content. Anti-pattern: a 3,000-word mega-prompt
covering role, standards, error handling, testing, security, and
output format all at once -- impossible to debug when something fails.

**S -- Safety Boundaries.** Every agent operates within explicit
boundaries: what tools are available (capability), what context is
loaded (knowledge), what requires human approval (authority). Practice:
per-agent tool whitelists (never wildcards), validation gates requiring
human approval for sensitive operations, knowledge scoping via pattern
matching, deterministic tools as "truth anchors" grounding probabilistic
generation. Standard roles: code writer (write access to domain files,
must pause before API changes), reviewer (read-only), test runner,
deployer (deployment scripts only, human approval gates). Anti-pattern:
an agent with access to every tool and no oversight, able to modify
production config or rewrite CI pipelines on an unexpected output.

**E -- Explicit Hierarchy.** Instructions form a hierarchy from global
to local; local context inherits from and may override global context.
Practice: a root `AGENTS.md` sets global standards, `backend/AGENTS.md`
adds API-layer rules, `backend/auth/AGENTS.md` adds security rules --
an agent resolves context by walking from most specific to most
general. Pattern-scoped instructions use `applyTo` frontmatter to
target file patterns at increasing specificity without directory
restructuring. Anti-pattern: one flat instruction file for every
domain, forcing every agent to load CSS naming conventions while
implementing Python.

## How the constraints interact

They're self-reinforcing, not independent: Progressive Disclosure
controls attention load while Explicit Hierarchy defines what loads
where; Reduced Scope constrains safety scope while Safety Boundaries
constrain what agents can change. The handbook illustrates this with
three failure stories where missing one constraint let a failure
through that its partner constraint alone couldn't catch.

## Applying it: example project layout

```
project/
├── AGENTS.md                 # Global rules
├── backend/AGENTS.md         # Domain rules
└── .github/instructions/
    └── auth.instructions.md  # Module rules with applyTo pattern
```

Each agent declares a tools whitelist (e.g. `editFiles`, `runCommands`,
`search`, `testRunner` -- never wildcards), explicit file boundaries
(which directories it may modify), and validation gates (`**STOP**`
directives before security-sensitive or schema-modifying changes).

Worked example -- implementing JWT authentication decomposed into five
Reduced-Scope sessions, each with fresh context: (1) design token
schema and validation types, (2) implement authentication middleware,
(3) build the refresh endpoint with token rotation, (4) write
integration tests, (5) update the frontend login form -- using a
different agent, different instructions, and no access to backend
internals beyond the API contract.

## Compliance checklist

A 12-point checklist evaluates whether a setup satisfies PROSE, grouped
by constraint (files over 100 lines use links with descriptions;
tasks state as a single sentence; each file addresses one concern;
tool lists are explicit with gates before sensitive operations; three
or more specificity levels exist). Priority when triaging failures:
**Safety Boundaries first** (greatest blast radius), then **Hierarchy**,
then the remaining discipline/refactoring issues (Progressive
Disclosure, Reduced Scope, Composition) addressed based on whichever
failure mode the team is actually experiencing.
