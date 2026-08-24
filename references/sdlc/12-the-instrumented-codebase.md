# The instrumented codebase

Source: **The Agentic SDLC Handbook**, Daniel Meppiel, Part III (For
Practitioners), Ch. 12 --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch12-the-instrumented-codebase.html.
See [index.md](index.md) for why this lives here rather than in
`references/harnesses/`.

## The problem it addresses

Chapter 11 named the four parts of the agentic runtime machine —
Model, harness, agent source code, client — and identified _agent
source code_ as the part the developer programs against. A repository
instrumented for agentic work is full of markdown that isn't
documentation. These files are parsed, linked, loaded, and executed.
They version-control alongside the application code they steer, review
in pull requests, and create a feedback loop: when an agent misbehaves,
you fix the file that should have prevented the mistake, not the
generated code.

Every mature project carries two kinds of knowledge. The first lives in
the code itself — types, function signatures, directory structure, test
assertions. Any agent can read this. The second lives in the team's
heads: which authentication pattern is current and which is deprecated,
why the logging module wraps the standard library, what "follows the
BaseIntegrator pattern" means in practice. An agent cannot read this.
It will guess, and it will guess wrong. **Instrumentation** is the
practice of converting the second kind into structured files the
harness loads as context.

## The seven primitive types

Seven categories cover the full range of knowledge an agent needs.
Each carries an implicit _load mode_ — the moment the harness decides
to read it into the model's context. Five modes are in play: **eager
preload** (read at session start); **lazy on-demand** (the agent
decides to load based on a description match); **dispatcher-mediated**
(a parent thread routes to a specialist); **user-invoked** (the
developer runs it as a workflow); **event-driven** (a client process
fires it in response to an outside event). Chapter 14 covers the
mechanics of each.

### Instructions

**Load mode:** eager preload, scoped by `applyTo` glob.

**Purpose:** Encode project conventions scoped to specific files,
directories, or file types. Tell an agent "when you touch code in this
scope, follow these rules."

**File format:** `.instructions.md` with frontmatter specifying scope.

```markdown
---
applyTo: "src/api/**"
description: "API layer conventions for endpoint implementation"
---

# API Development Rules

## Middleware Registration
- All middleware decorators are registered in `middleware.py`, never inline on routes.

## Rate Limiting
- Use `app.rate_limiter.RateLimiter`, not third-party libraries.
- Rate limit values come from environment variables, never hardcoded.

## Error Responses
- All error responses use `APIError.from_exception()` for consistent format.
- Never return raw exception messages to clients.
```

**Design test:** Can you state the scope in one `applyTo` pattern?
Does every rule in the file apply to that scope? If you're writing
rules that apply to two unrelated domains, split the file. If your
instruction file exceeds 40–50 lines, it's trying to do too much —
every line of instruction competes for attention with the source code
the agent needs to read.

### Agents

**Load mode:** dispatcher-mediated.

**Purpose:** Define specialist personas with domain expertise,
calibrated judgment, and explicit behavioral boundaries. An agent
configuration is the answer to "who should work on this?" — in terms
of what expertise, priorities, and constraints the task requires.

**File format:** `.agent.md` with frontmatter specifying model, tools,
and description.

Four elements make an agent configuration effective:

1. **Domain expertise.** Specific enough to constrain decisions. "You
   are an expert Python developer" is too broad. "You specialize in CLI
   tool design using the Click framework" constrains the solution space
   meaningfully.
2. **Named patterns.** When the agent knows patterns by name
   ("BaseIntegrator," "CommandLogger") it can reference them in its
   reasoning and produce code that uses them correctly.
3. **Anti-patterns.** What the agent must never do. These encode
   institutional memory; each item represents a mistake that happened
   at least once.
4. **Tool boundaries.** Which tools the agent can invoke. Tool
   boundaries are safety boundaries made concrete.

Start with three to five agent configurations. An architect, a domain
expert for your core business logic, and a documentation writer cover
most tasks.

### Skills

**Load mode:** lazy on-demand, description-driven activation. The
harness preloads only the skill's `description` frontmatter; the body
stays unread until the agent decides — based on the description
matching the current task — to pull the rest into context.

**Purpose:** Package reusable decision frameworks that activate based
on code patterns. A skill is more than a set of rules; it teaches an
agent how to think about a specific domain.

**File format:** A directory containing a `SKILL.md` file, optionally
with examples and supporting context.

Skills differ from instructions in an important way: they provide
_decision frameworks_, not just rules. A rule says "use
`_rich_warning()` for warnings." A decision framework says "every
warning must answer 'what should the user do about this?'" The
framework generalizes to situations the author didn't anticipate.

**Design test:** Does this knowledge apply across multiple files? Does
it require more than a few rules to express? Is it triggered by a
detectable code pattern? All three yes → skill. Single directory →
instruction. General disposition → agent configuration.

### Prompts

**Load mode:** user-invoked.

**Purpose:** Define reusable, parameterized workflows that orchestrate
multi-step tasks. The agentic equivalent of a script or a makefile
target.

**File format:** `.prompt.md` with frontmatter specifying execution
mode and tools.

Prompts are the bridge between ad-hoc chat and systematic workflows.
Without them, every time a developer wants a structured code review,
they have to reconstruct the review framework from memory.

### Memory

**Load mode:** eager preload, persistent.

**Purpose:** Preserve knowledge across sessions. Agents are stateless;
every conversation starts from zero. Memory files give them access to
accumulated decisions, resolved trade-offs, and project history that
would otherwise vanish between sessions.

**File format:** `.memory.md`, structured by domain.

Memory files capture the knowledge that doesn't fit in instructions
because it isn't a rule; it's context. The distinction matters: "use
JWT for authentication" is a rule (instruction). "We migrated from
sessions to JWT in Q1, and the old SessionAuth class is still in the
code but deprecated" is context (memory). An agent that knows only the
rule might accidentally use the deprecated class. An agent that also
has the memory won't.

Memory files are the most likely primitive to drift from reality.
Include dates. Review them quarterly. If a section hasn't been updated
in six months, verify that it's still accurate or remove it.

> **Note: memory storage varies by tool.** Some tools implement memory
> as structured databases rather than flat files. The principles —
> persistence, discoverability, and staleness management — are the same
> regardless of the storage mechanism.

### Orchestration

**Load mode:** user-invoked workflow.

**Purpose:** Bridge planning and implementation by defining structured
specifications that can be executed by humans or agents with the same
precision. Orchestration files decompose large features into
implementation-ready units.

**File format:** `.spec.md` for specifications, or workflow
composition files that coordinate multiple context files.

Specification files make the "Reduced Scope" constraint (Ch. 13)
operational. Instead of telling an agent "implement rate limiting" and
hoping it figures out the approach, the spec defines scope, components,
contracts, and success criteria upfront.

### Hooks

**Load mode:** event-driven, harness-mediated.

**Purpose:** Define automated actions triggered by development events.
Hooks bridge the gap between passive context (instructions, memory) and
active behavior, making the instrumented codebase reactive rather than
waiting to be queried.

**File format:** Configured via tool-specific hook mechanisms (VS Code
tasks, GitHub Actions triggers, copilot hooks configuration) rather
than a single portable file format.

Examples: auto-run linting on save; trigger test generation when a new
source file is created; auto-update memory files after a successful PR
merge; run a security-reviewer agent on every change to `src/auth/`.

Start with one or two hooks: a linting check on save and a test prompt
on new file creation cover the highest-impact triggers.

## Tool support

The seven types are conceptual categories, not file format
specifications. How each maps to a concrete file depends on which
harness reads it. Two tiers apply: a **portable tier** of body prose
(instructions, memory entries, specs, skill decision frameworks) that
moves freely as markdown; and a **harness-specific tier** of wiring
(scoping syntax, agent activation, prompt invocation, hook
configuration) that you rewrite on a port. The knowledge is roughly
80% of the value; the wiring is the rest. Appendix A holds the dated
cross-harness reference matrix.

## Directory structure

```
project/
├── .github/
│   ├── copilot-instructions.md       # Global project principles
│   ├── instructions/
│   │   ├── api.instructions.md       # applyTo: "src/api/**"
│   │   ├── auth.instructions.md      # applyTo: "src/auth/**"
│   │   ├── frontend.instructions.md  # applyTo: "src/ui/**/*.tsx"
│   │   ├── testing.instructions.md   # applyTo: "**/test/**"
│   │   └── database.instructions.md  # applyTo: "src/db/**"
│   ├── agents/
│   │   ├── architect.agent.md
│   │   ├── backend-dev.agent.md
│   │   ├── security-reviewer.agent.md
│   │   └── doc-writer.agent.md
│   ├── skills/
│   │   ├── cli-logging-ux/
│   │   │   ├── SKILL.md
│   │   │   └── examples/
│   │   ├── error-handling/
│   │   │   └── SKILL.md
│   │   └── api-middleware/
│   │       └── SKILL.md
│   ├── prompts/
│   │   ├── code-review.prompt.md
│   │   ├── feature-impl.prompt.md
│   │   └── bug-investigation.prompt.md
│   └── specs/
│       ├── feature-template.spec.md
│       └── api-endpoint.spec.md
├── .memory.md                        # Project-level memory
├── AGENTS.md                         # Root discovery file
├── src/
│   ├── api/
│   │   └── AGENTS.md                # API-specific context
│   └── auth/
│       └── AGENTS.md
└── ...
```

Three observations: context files live in `.github/`, centralized so
the knowledge layer is findable; each primitive type has its own
directory; each directory stays flat — a flat list of 15
descriptively-named files scans faster than a three-level tree.

## How primitives compose

When an agent is asked to modify `src/api/users.py`, the effective
context assembles from: global principles → scoped instructions (only
those whose `applyTo` glob matches) → activated skills (pattern
matches) → agent persona (model, tools) → memory (versioning
decisions, deprecated `SessionAuth`) → prompt or spec (the specific
workflow). Each layer adds specificity; none contradicts the layer
above. A conflict indicates a design error in the instrumentation, not
a resolution the agent should attempt.

## The instrumentation audit

Before building any of this, take stock of what your codebase already
has and what it's missing. Five steps:

**Step 1: List your conventions.** Spend 30 minutes with your team.
Write down every convention, pattern, and constraint a new engineer
would need to learn in their first two weeks. Don't filter. Don't
organize. You'll typically get 30–60 items.

**Step 2: Classify each item.** Mark where it lives today — in code
(partially visible), in docs (invisible unless explicitly loaded), or
in heads (completely invisible). The "in heads" column is your
instrumentation debt.

**Step 3: Rank by failure cost.** Critical (security, data corruption),
High (architectural debt), Medium (rework in review), Low (style
preferences).

**Step 4: Map each item to a primitive type.**

| If the knowledge... | Use... |
|---|---|
| Is a rule scoped to specific files/directories | An instruction file |
| Requires specialist expertise or a specific model | An agent configuration |
| Applies across files and needs a decision framework | A skill |
| Defines a repeatable multi-step process | A prompt |
| Records a decision, trade-off, or historical fact | A memory file |
| Specifies a feature with components and success criteria | A specification |
| Defines an automated response to a development event | A hook |

**Step 5: Write your starter set.** Begin with 3–5 context files
covering your critical items. The feedback loop will guide you to what
is actually needed faster than upfront planning.

## Before and after: a concrete example

The handbook documents a before/after on a mid-size Python backend
(80,000 lines, REST API, message queue, auth module, CLI). Before
instrumentation, asking an agent to "add a health check endpoint"
produced code using Flask patterns (the project used FastAPI), a raw
database connection instead of the project's `HealthChecker` service, a
plain JSON response (ignoring the project's standard response
envelope), inline object construction in tests (violating the factory
pattern), and no route registration in the middleware pipeline —
everything compiling, tests passing, and three review comments of the
form "we don't do it that way here."

After instrumentation, the same task loaded global instructions, API
instructions (FastAPI conventions, standard response envelope, route
registration), the API middleware skill (the registration pipeline),
the backend-dev agent, and a new-endpoint prompt. The result needed no
convention-related review comments at all. The difference was 150 lines
of markdown distributed across 8 files, not a better model.

The handbook reports across projects that have undergone this
transformation: convention-violating outputs drop from 40–60% of
generated code to under 10%.
