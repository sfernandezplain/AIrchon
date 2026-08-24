# Part III preface & the practitioner's mindset

Source: **The Agentic SDLC Handbook**, Daniel Meppiel, Ch. 9 --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch09-part-iii-preface.html
-- and Ch. 10 --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch10-the-practitioners-mindset.html.
Combined onto one page because Ch. 9 is a short map/preface, not a
full chapter in its own right. See [index.md](index.md) for why this
lives here rather than in `references/harnesses/`.

## Ch. 9 -- A map for Part III

Framing statement for the whole part: Part III is "not a more-detailed
version of Part II -- it is the practitioner-grade rewrite" of the
system Part II's leadership chapters describe.

### Eight terms practitioners cannot avoid

- **Primitive** -- a unit at the Context & Capabilities layer (Skill,
  Persona, or Context bundle), stored as markdown.
- **Manifest** -- the `apm.yml` file declaring a repository's primitive
  dependencies.
- **Lockfile** -- `apm.lock.yaml`, pinning the resolved transitive
  dependency graph by content hash.
- **CODEOWNERS** -- the GitHub file controlling who may merge changes
  to primitives.
- **Harness** -- the runtime application (Codex CLI, Claude Code,
  Copilot, Cursor, OpenCode).
- **Subagent** -- a thread spawned by the harness with an independent
  context budget.
- **Recursion bound** -- an operational limit preventing a dispatch
  tree from running away.
- **MCP** -- Model Context Protocol, the open standard for system
  access.

### The five-layer supply chain, restated

Same model as Ch. 4 (see
[04-the-reference-architecture.md](04-the-reference-architecture.md)):
Platform (cloud infra, source control) -> Context & Capabilities
(markdown-based Skills, Personas, Context bundles) -> Governance and
Distribution (the package-manager layer, APM as its primary instance)
-> Agent Harness (the runtime execution layer) -> SDLC phases (Plan,
Spec, Build, Review, Test, Deploy, Operate as application output).

### Four named composition patterns

Referenced throughout the rest of Part III:

- **Panel** -- a mediator running scatter-gather: multiple specialist
  threads review the same artefact in parallel.
- **Wave** -- a pipeline: one thread's output becomes the next
  thread's input.
- **Scatter-Gather** -- fan out, collect, and return, without a
  synthesis lens.
- **Subagent** -- the general term for any spawned thread with an
  independent context budget.

Part III itself runs 14 chapters (10-22), which the preface describes
as progressing "from mindset through execution patterns to earned
reference architecture" -- Ch. 10 (this page) starts that progression.

## Ch. 10 -- The practitioner's mindset

### 10.1 The autocomplete trap

The chapter opens by rejecting the mental model of AI as "a text
predictor that occasionally saves keystrokes" as fundamentally wrong
for agentic development. The distinction it draws: "An agent is not
predicting your next line. An agent is attempting to execute a task:
reading files, making decisions about structure, writing code across
multiple locations, running tests, interpreting failures." That's why
agent failures are more expensive than autocomplete failures -- they
"produce code that compiles, passes a superficial review, and encodes
the wrong assumptions into your system." The corrected mental model:
"AI is a capable but amnesiac engineer that needs explicit context to
do useful work."

### 10.2 From writing code to engineering context

The practitioner's primary output shifts from code to context, and the
skill being measured shifts "from the quality of what you write" to
"the quality of the boundaries you define." Three categories of
context an engineer must supply:

1. **Structural context** -- codebase layout, module boundaries,
   dependency relationships, naming conventions, patterns to follow.
2. **Constraint context** -- files that are off-limits, behavioural
   contracts to preserve, refactorings that would break downstream
   consumers.
3. **Domain context** -- business logic, edge cases, implicit rules
   held in team knowledge but absent from the code itself.

Worked contrast -- **bad** specification: "Migrate all
`_rich_info()` calls to `logger.info()`," which silently drops the
fact that some calls inside error handlers are deliberate workarounds.
**Good** specification: "Migrate `_rich_info()` calls to
`logger.info()`, except in error-handling paths where `_rich_info()`
is called before the logger is initialized -- in those cases, keep the
existing call and add a `# TODO` comment."

### 10.3 Your three roles

- **Architect** -- before any coding, decompose tasks into pieces that
  fit an agent's context window; sequence dependencies; define
  constraints (must do / must not do / must preserve); allocate files
  to agents; determine granularity.
- **Reviewer** -- after agent output, evaluate whether the agent stayed
  within its defined boundaries and whether those boundaries were
  correct. Focus on failures that are "locally coherent but globally
  inconsistent" -- code that works in isolation but violates a
  system invariant the agent had no way to know about. Three review
  questions: did the agent follow the specified constraints? Did the
  constraints miss anything important? Does this code fit with the
  rest of the system in ways the agent couldn't have known?
- **Escalation Handler** -- resolve ambiguities the specification
  didn't address, handle test failures that require judgment, and
  surface decisions that need human expertise (trade-offs, scope
  questions, architectural calls with long-term consequences).

The mix shifts over time but doesn't disappear: early practice leans
heavily on Reviewer; as specifications improve, Architect dominates;
Escalation Handler stays roughly constant regardless.

### 10.4 When to use agents and when to code manually

A decision flow: can you specify the task clearly in under two
minutes? If yes, is the spec shorter than the code would be? If yes,
is the scope bounded? If all three hold, **delegate to an agent**. Any
"no" along that chain, check whether the task splits into a
bounded/agent part and a judgment/manual part -- split if it does,
otherwise **code it yourself**.

Use agents when the task is well-specified, repetitive, or
parallelisable (e.g. migrating call sites across 40 files, adding
structured logging to 15 endpoints following the same pattern), or
when you need a research assistant to explore an unfamiliar codebase.

Code manually when the task requires deep contextual judgment
(refactoring APIs under backward-compatibility constraints, fixing
bugs that span multiple modules, trade-off-laden design decisions),
when the specification would be longer than the implementation, when
you're still learning the codebase (you can't review agent output
effectively if you don't understand the task), or when the task is a
one-off that will never repeat (the specification overhead exceeds the
benefit).

### 10.5 The cost of over-reliance

**Skill atrophy** -- if you stop writing code, your judgment for
reviewing it atrophies, because code review depends on staying
familiar with language patterns, idioms, and failure modes.
Mitigation: deliberately reserve categories of work -- the complex,
novel, and architecturally significant -- for manual implementation.

**The "almost done" trap** -- agent output that's 90% correct tempts
you into spending 20 minutes fixing the remaining 10%, repeated across
batches, until by day's end you've spent more time fixing than you
would have spent writing from scratch. Discipline rule: if you're
making non-trivial corrections to more than 20-30% of an agent's
output on a given task, the specification or the task selection was
wrong -- stop fixing, and either improve the specification and
re-dispatch, or do the task yourself.

### 10.6 First day: a task from start to finish

A worked, timestamped example -- add rate limiting to the
`/api/projects` endpoint (100 requests/minute per API key, 429 with a
`Retry-After` header when exceeded):

- **0:00 (Architect)** -- decompose into middleware/decorator, wiring
  to the endpoint, and tests. Identify a reusable pattern
  (`middleware/auth.py`). Write a precise middleware specification
  including the Redis key format and configuration defaults.
- **0:04 (Dispatch + parallel work)** -- send the middleware task to
  an agent; write the three-line endpoint wiring yourself since it's
  faster manually; draft the test specification in parallel.
- **0:08 (Reviewer)** -- the agent's middleware checks out on decorator
  signature and Redis client use, but it catches `redis.ConnectionError`
  and fails open, whereas team policy requires a 503 response instead
  -- a constraint the agent had no way to infer. Decision: fix it
  yourself (two lines) rather than re-dispatch, and document the
  fail-closed policy in persistent instruction files for future
  agents.
- **0:12 (Dispatch tests)** -- send the test specification while
  reviewing the middleware a second time.
- **0:16 (Escalation Handler)** -- the test agent returns four tests,
  but one uses sleep-based timing assertions, which you know are flaky
  in CI -- knowledge specific to your deployment context. You rewrite
  the assertion with `unittest.mock.patch` to freeze time instead.
- **0:20 (Validate)** -- full test suite green, PR opened. You wrote
  roughly 10 lines; agents wrote roughly 120. You also improved
  standing infrastructure: middleware instructions now encode the
  fail-closed policy, and test instructions now warn against
  sleep-based assertions.

Observation: four role transitions inside twenty minutes, without
conscious effort -- "the natural rhythm of working with agents."

### 10.7 The mindset in practice

Three habit changes:

1. Before starting a task, ask "can I specify this precisely enough
   for an agent?" If yes, specify and dispatch; if no, split it or do
   it yourself.
2. When something fails, fix the context -- the instruction, the
   specification, the decomposition -- not just the generated code.
   Fix the system, not the symptom.
3. The third time you explain a convention, write it down in a
   persistent file. Team knowledge becomes infrastructure, not oral
   tradition.

Closing statement: "The AI is a capable, fast, amnesiac engineer. Your
job is architect, reviewer, and escalation handler -- the roles that
require continuity, judgment, and accountability. The agent handles
volume. You handle direction."

## Source

Ch. 9 and Ch. 10, Part III (For Practitioners), *The Agentic SDLC
Handbook* --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch09-part-iii-preface.html
and
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch10-the-practitioners-mindset.html.
