# The agentic runtime machine

Source: **The Agentic SDLC Handbook**, Daniel Meppiel, Part III (For
Practitioners), Ch. 11 --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch11-the-runtime-machine.html.
See [index.md](index.md) for why this lives here rather than in
`references/harnesses/`.

## The problem it addresses

The chapter opens with Maya, a senior engineer who instruments a
repository with `.instructions.md` files for GitHub Copilot, then
switches to Claude Code expecting the same primitives to work. They
don't -- the files exist but are invisible, because Claude Code's
harness uses a different file-naming and scoping convention. "Same
files. Same model family. Different harness. Silence." The chapter's
framing: the problem is not the model or the primitives themselves --
it's that Maya was "programming against a language whose compiler
[she] did not know [she] was using" without realising which of four
independent runtime components had actually changed.

## The four parts of the runtime machine

**1. The Model** -- the inference engine (GPT-5, Claude Sonnet, Gemini,
etc.). Takes text in, produces text out; by itself has no tools, no
persistent memory, no awareness of the codebase. "Most failures
attributed to the model are not the model's fault."

**2. The Harness** -- the program driving the model, running when you
type `gh copilot`, `claude`, `cursor`, or `codex`. It manages the
conversation, calls tools, decides which files load into context and
when, and decides what to do with model output. "The harness is the
program that varies the most across vendors." Examples: GitHub
Copilot, Anthropic Claude Code, Cursor, OpenAI Codex, OpenCode.

**3. Agent Source Code** -- the directory layout the harness consults
for context decisions. "Not a passive store of documentation" but
"executable configuration": a file at a particular path with
particular frontmatter changes behaviour even though model and harness
are unchanged. This is the layer Maya was unknowingly programming
against.

**4. The Client** -- the process deciding when a session runs and what
bootstrap context it carries. Can be interactive (developer in a
terminal, IDE plugin) or programmatic (GitHub Actions, cron, webhook,
CI runner). Orthogonal to the harness: the same orchestrator can spawn
multiple harnesses in one run. It is the first layer that can rewrite
what lower layers see.

Figure 11.1 depicts these as interconnected: Client <-> Harness <->
Model, with Tools <-> Harness and Harness <-> Source Code.

## The three recurring filename shapes (a 30-second glossary)

**`.instructions.md`** -- scoped conventions carrying an `applyTo`
glob (e.g. `applyTo: "src/api/**"`) in frontmatter; when the agent
touches a matching file, the harness preloads the body. Closest
analogue: ".editorconfig the AI reads."

**`SKILL.md`** -- a reusable decision framework the agent decides to
load when a task matches the skill's declared purpose; activated on
demand, not on every file touch.

**`.agent.md`** -- a specialist persona run as a separate sub-thread,
routed through the harness's delegation tool; inherits its declared
model, tools, and instructions.

## The harness as compiler

Central claim: "The harness is the compiler." Model = runtime; agent
source code = source tree; harness = the program deciding what
compiles to what, in what order, at what visibility.

**Cross-harness incompatibility example.** A single substrate concept
-- text the model sees automatically when working in a particular
codebase region -- is implemented incompatibly:

| Property | GitHub Copilot | Anthropic Claude Code |
|---|---|---|
| File name | `api.instructions.md` (any stem) | `CLAUDE.md` (exact, conventional name) |
| Folder | `.github/instructions/` | Nested in the subtree, e.g. `src/api/CLAUDE.md` |
| Scope predicate | `applyTo: "src/api/**"` glob in frontmatter | Implicit, by directory hierarchy |
| Multiple files | Many `.instructions.md` files, glob-matched | One closest `CLAUDE.md` wins per subtree |
| External references | Plain markdown links | `@path` directive (inlines the file) |
| User-scope variant | `.copilot/instructions/` in home directory | `~/.claude/CLAUDE.md` in home directory |
| Loaded when | Thread touches a matching path | Thread starts work in that subtree |

"Both harnesses implement the same substrate concept... but the syntax
is incompatible." This is not a bug -- it is the unavoidable
consequence of different compilers with different file-layout
opinions.

**Load order.** Figure 11.2 maps the cross-harness load sequence: both
harnesses follow the same conceptual steps -- user config (scope
level), project base (project level), scoped rules (path-attached),
skills available, agents available -- but the file paths diverge
entirely (`.github/instructions/` vs. a nested `CLAUDE.md` hierarchy).

**Portability fix.** Mechanical: "Provide a thin shim file at the
harness's expected path that re-exports the canonical primitives." For
example, a `CLAUDE.md` at repo root saying "for code under
`src/api/`, follow `@.github/instructions/api.instructions.md`" makes
Copilot-tuned primitives visible to Claude Code.

**Harness-switching cost.** "When you choose a harness, you are
choosing a compiler. The decision is not reversible by editing a
config file. Switching harnesses is a port, with all the same costs
and gotchas as porting a program from one language to another."

## Markdown as code, not documentation

Instruction files have every property of code artifacts:

1. **Parsed** -- frontmatter is read by the harness; a malformed field
   fails silently.
2. **Linked** -- references (`@path` directives, markdown links) form
   real dependency graphs.
3. **Loaded** -- at a defined session moment, the harness reads the
   contents and places them in the model's context (observable in
   verbose mode).
4. **Executed** -- the text steers the next token the model emits;
   poorly worded instructions bias output the way buggy code does.

**Precision matters.** "Never use `_rich_info()` in error handlers"
and "avoid `_rich_info()` in error handlers" are not equivalent -- the
first prevents a regression, the second hedges enough that the agent
uses it anyway.

**Implication:** "Treating them as documentation that occasionally
affects the agent leaves you debugging through guesswork. Treating
them as code lets you bring the full apparatus of code review, version
control, and observability to bear."

## Inference per-thread; filesystem shared

The chapter's load-bearing claim: "Inference is per-thread; the
filesystem is shared."

**Inference:** the harness spawns a session with a private thread
(context window, token budget, conversation log). The thread is born
empty and dies forgotten -- anything learned, decided, or received is
gone when the session ends. There is no persistent memory inside the
model; a session is "amnesiac by construction."

**Filesystem:** the only thing that survives between sessions. Every
primitive lives there; every plan, memento, and lockfile persists.
Parallel threads share zero context and communicate via the filesystem
only.

**Operational consequences.** When a long session risks losing its
thread, use the plan-write-then-reload pattern: the agent writes a
plan to a file mid-session and re-reads it at decision points -- the
plan survives inference even though inference doesn't survive the
session. When a parent fans work out to children, the children inherit
nothing except what the parent wrote down; a worker needing
architecture decisions must read the files the parent wrote, not query
the parent's context.

"If you accept one sentence from this chapter, accept that one. The
amnesia of the model and the persistence of the filesystem are the
load-bearing asymmetry."

## Deployment topology variants

Three canonical deployments of the four-part model:

**Full Local** -- client, harness, agent source code, and model all on
the developer's laptop; a local GGUF or Ollama serves inference; the
harness reads files from the local checkout; nothing leaves the
machine. Use case: air-gapped, compliance-sensitive, zero-cost
experimentation.

**Hybrid (local client, cloud model)** -- client, harness, and agent
source code stay local; only inference calls cross the network. The
default for most developers running Claude Code or Copilot CLI;
primitives remain local and the model never persists them.

**Full Cloud** -- client, harness, model, and agent source code all run
in the cloud. Canonical example: GitHub's Copilot Coding Agent -- a
pull-request event triggers a cloud harness that checks out the repo,
loads primitives, drives inference, and pushes commits without
touching the developer's machine.

"Layer-locality is a deployment decision, not an architectural one.
The four-part model is the same in every case; only the network
boundary moves."

## Skills and cross-harness portability

The `SKILL.md` entrypoint with description-driven activation has
achieved substantial convergence: GitHub Copilot uses
`.github/skills/<name>/SKILL.md`, Claude Code uses
`.claude/skills/<name>/SKILL.md`, and several other harnesses have
adopted a compatible form. "Skills port across harnesses more cleanly
than scope-attached rules because the standard pinned the file name
and the activation contract."

Alternative conventions named: Cursor's `.cursor/rules/` directory, and
OpenAI Codex / OpenCode's `AGENTS.md` convention, adopted as a
portable lingua franca.

## TL;DR: four parts, one machine

1. **Name the four parts** -- model, harness, agent source code,
   client. When behaviour differs between setups, ask which part
   changed first.
2. **Treat markdown as code** -- parsed, linked, loaded, executed.
   Version it, review it, lint it, and write it precisely; the next
   agent should not have to hedge.
3. **The harness is a compiler** -- same primitives plus a different
   harness equals a different program; cross-harness portability is a
   deliberate project plan, not an afterthought.
4. **Inference is per-thread, the filesystem is shared** -- threads are
   amnesia-prone; the filesystem is the only persistent memory. Every
   coordination pattern later in the book follows from this asymmetry.

## What this chapter unlocks

The chapter closes by pointing forward: Chapter 12 treats agent source
code as a built artifact and introduces the seven primitives as a
programming language; Chapter 14 covers the load lifecycle in detail
(verbose output, the transitive closure of files that load when a
primitive activates); Chapter 16 covers the deterministic/probabilistic
boundary (the harness is deterministic, the model probabilistic);
Chapter 17 revisits the per-thread/shared-filesystem asymmetry for
multi-agent fan-out topologies; and Appendix A supplies a cross-harness
reference matrix for actual porting projects.

## Source

Ch. 11, Part III -- For Practitioners, *The Agentic SDLC Handbook* by
Daniel Meppiel --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch11-the-runtime-machine.html
