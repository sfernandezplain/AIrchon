# The load lifecycle

Source: **The Agentic SDLC Handbook**, Daniel Meppiel, Part III (For
Practitioners), Ch. 14 --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch14-the-load-lifecycle.html.
See [index.md](index.md) for why this lives here rather than in
`references/harnesses/`.

## The problem it addresses

The chapter opens on a debugging scenario: an engineer writes a skill
with correct frontmatter, in the right directory, with a sharp
description -- and it fails to activate, with no error message
anywhere. An hour is lost suspecting the skill itself. The chapter's
governing claim: "A skill with a correct frontmatter, in the right
directory, with a sharp description, can fail to bind -- and the
harness will not tell you why. The fix is almost never in the skill."
With the lifecycle's vocabulary in hand, "the diagnosis is the second
sentence above and the fix is mechanical."

This chapter covers the **deterministic** mechanics of how content
reaches the model at all (lockfiles, verbose logs, path predicates,
binding modes). Chapter 15 covers the probabilistic side -- what
happens to that content once it's inside the model's attention.

## The four-phase lifecycle: Resolve -> Materialize -> Bind -> Activate

Every primitive (rule file, skill, agent persona) passes through the
same sequential pipeline before it can influence model output.

**1. Resolve** -- The package manager walks the dependency graph and
writes a lockfile, answering "what actually loads when this primitive
activates?" Owned by an explicit tool invocation (`apm install`,
`apm compile`), once per install. Practice: run the resolver in
dry-run mode (`--dry-run`) and read the printed closure before
committing manifest changes.

**2. Materialize** -- Files land at the paths the harness actually
parses (`.github/`, `.claude/`, `.cursor/`, `AGENTS.md`). This
translates the "what" from Resolve into "where" on disk. Owned by the
install step/developer, once per install. The same primitive
materializes to different paths depending on harness (Copilot, Claude
Code, Cursor, Codex, OpenCode).

**3. Bind** -- The harness classifies each materialized file into one
of three binding modes: eager preload, lazy on-demand, or
dispatcher-mediated. Owned by the harness at session start, once per
session. Binding mode is determined by file name, folder structure,
and frontmatter -- not by authorial intent.

**4. Activate** -- The dispatcher selects which lazy primitives
actually load, given the current task and remaining budget. Owned by
the harness dispatcher, at session start and at every subsequent
decision point where the dispatcher can pull more text into context.
This phase is partly probabilistic (description matching, budget
pressure) rather than fully deterministic.

The flow is strictly sequential: **R -> M -> B -> A**.

## Cross-harness materialization reference

| Primitive type | GitHub Copilot | Anthropic Claude Code | Cursor | Codex/OpenCode |
|---|---|---|---|---|
| Project-wide rules | `.github/copilot-instructions.md` | `CLAUDE.md` at repo root | `.cursor/rules/*.mdc` | `AGENTS.md` at repo root |
| Scope-attached rules | `.github/instructions/*.instructions.md` with `applyTo` glob | Nested `CLAUDE.md` per subtree | `.cursor/rules/*.mdc` with `globs` | Nested `AGENTS.md` per subtree |
| Skill (module entrypoint) | `.github/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` | (none) | (partial via `AGENTS.md`) |
| Persona/specialist | `.github/agents/<name>.agent.md` | `.claude/agents/<name>.md` | (none) | (none) |

## The three binding modes

**Eager preload.** Read into context at session start regardless of
what the user asked for. Examples: project-wide rules
(`copilot-instructions.md`, root `CLAUDE.md`, `AGENTS.md`); a
scope-attached variant loads eagerly whenever a path predicate
matches. Deterministic, but the mode most likely to crowd out
everything else in the budget.

**Lazy on-demand.** Registered with the dispatcher at session start
(its description loads eagerly into a registry); the body only loads
if the dispatcher decides the task warrants it. Skills are the
canonical form. Partly probabilistic, since it depends on
description-driven matching, but it's what lets a project ship 100
skills without burning budget on all of them every session.

**Dispatcher-mediated.** Neither eager nor offered to the activation
matcher; sits behind the dispatcher and is invoked explicitly by
another primitive. Examples: specialist persona files
(`.github/agents/*.agent.md`, `.claude/agents/*.md`), panel skills,
fan-out workers. Cleanest budget story of the three -- costs nothing
in the parent session.

### Binding-mode timeline

| Primitive type | Binding mode | Loaded when | Budget cost |
|---|---|---|---|
| Project-wide rules | Eager preload | Every session, immediately at start | Paid every session, unconditionally |
| Scope-attached rules | Eager (conditioned) | Whenever the thread touches a matching path | Paid on every session matching scope |
| Persona file (specialist) | Dispatcher-mediated | Parent spawns a child thread and names the persona | Paid only inside the child's context |
| Skill (`SKILL.md`) | Lazy on-demand | Description matches the task; dispatcher pulls the body | Description: small, eager; body: full, on activation |
| Sub-agent / wave panel | Dispatcher-mediated | Parent invokes the dispatcher and it selects | Paid in each spawned child, not the parent |

## Determinism vs. probabilism in Activate

**Deterministic factors:**
1. **Path predicates** -- an `applyTo` glob either matches the current
   working path or it doesn't (testable in seconds).
2. **Frontmatter validity** -- a YAML parser either accepts the
   frontmatter or it doesn't; malformed frontmatter is invisible to
   the dispatcher.
3. **Lockfile-driven closure** -- the same `apm install` against the
   same lockfile produces the same layout on every machine.

**Probabilistic factors:**
4. **Description matching** -- the model reads a skill's description
   against the current task; similar-but-not-identical tasks may match
   differently. Precision guidance: "precise verbs, named triggers
   ('when authoring Alembic migrations'), explicit scope predicates
   ('under `migrations/versions/`') raise hit rate; vague descriptions
   lower it."
5. **Budget pressure** -- when eager preloads consume a large fraction
   of the budget, the dispatcher down-ranks lazy candidates that
   aren't strictly required. Crucially, the skill isn't unloaded; it
   is **"un-considered"** -- visible in verbose logs as "registered but
   never pulled."

## Failure modes / anti-patterns

**Phantom dependency.** A primitive is required at runtime but never
declared as a dependency edge. It "just happens" to load because it
exists in the developer's own environment; a clean install on a
teammate's machine fails. Fix: every file a primitive needs must be
either inlined, a sibling in the same source tree, or declared as an
external module with a real edge.

**Bundle leakage.** A published module ships with files outside its
declared distribution boundary (eval scenarios, contributor notes, dev
fixtures). The consumer's installer materializes these into the
harness layout, where the dispatcher matches them as if they were real
primitives. Fix: publisher-side discipline -- keep maintainer-only
files outside the directory the package manager auto-publishes.

**Over-eager scope predicates.** An `applyTo: "**"` rule, or an
800-line project-wide `CLAUDE.md`, consumes enough budget that lazy
skill candidates go un-considered even when they match. Indicator:
verbose logs show "registered but not pulled."

## The worked example

A platform engineer creates a skill at
`.github/skills/db-migrations/SKILL.md` with correct frontmatter and a
sharp description: *"Activate when authoring or reviewing Alembic
database migrations under `migrations/versions/`. Use for naming,
batch operations, and reversible downgrade authoring."* It does not
bind when the agent touches a real migration file. The engineer
retypes the description three ways, adds keywords, moves the file,
modifies globs -- nothing works.

Verbose mode reveals the actual cause: a parent instruction file at
`.github/instructions/python.instructions.md`, with
`applyTo: "**/*.py"`, pulls 6,200 tokens every time the agent touches
a `.py` file. The load window is three-quarters full before the
dispatcher even considers on-demand skills. The skill was never
un-considered because of its description -- it was un-considered
because of budget consumed by the parent rule. The fix is mechanical:
reduce the eager preload's scope, or trim the Python guidance file.

## Terms of art coined/used

- **"Transitive closure"** -- what actually loads includes nested
  dependencies, not just what's declared directly.
- **"The dispatcher down-ranks"** (not "deselects") -- a skill remains
  registered but un-considered.
- **"Composition modes"** -- inline / local sibling / external module.
- **"Load window" / "budget"** -- the context token space.
- **"Description matcher"** -- the activation logic based on
  task/description alignment.

## Checklist: when a primitive is silent

1. **Resolve** the dependency graph and pin the closure -- every
   transitive primitive must be in the lockfile, or it's a phantom.
2. **Materialize** files at the harness's expected paths -- the
   translation is mechanical, not magical.
3. **Bind** every file into one of the three modes -- the mode is set
   by file name, folder, and frontmatter, not by intent.
4. **Activate** the right primitives per task -- path predicates,
   lockfiles, and frontmatter are deterministic; description matching
   and budget pressure are probabilistic; verbose logs surface both.
5. **When a primitive is silent, ask which phase failed first** -- each
   phase has a one-minute test; the hour lost in the chapter's opening
   scenario is an hour you don't have to lose.

## Source

Ch. 14, Part III -- For Practitioners, *The Agentic SDLC Handbook* by
Daniel Meppiel --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch14-the-load-lifecycle.html
