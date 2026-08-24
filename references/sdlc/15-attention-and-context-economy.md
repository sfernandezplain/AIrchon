# Attention and context economy

Source: **The Agentic SDLC Handbook**, Daniel Meppiel, Part III (For
Practitioners), Ch. 15 --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch15-attention-and-context-economy.html.
See [index.md](index.md) for why this lives here rather than in
`references/harnesses/`.

## The problem it addresses

Governing claim: "There is a difference between an instruction the
model has read and an instruction the model has seen." A context
window and attention are distinct quantities -- the window is
addressable memory, attention is a smaller, position-sensitive cache
that degrades non-linearly under load.

Opening scenario: a code reviewer loaded with an 800-line
architectural-decisions document begins ignoring an explicit,
technically-in-scope rule (flagging deprecated `auth_v1` usage)
because that rule is buried in the middle of a 35,000-token payload.

Where Chapter 14 covered the deterministic mechanics of *whether*
content reaches the model at all, this chapter covers the
probabilistic side: what happens to that content once it's inside.

## Window vs. attention

- **Window** -- the hard upper bound (e.g. 200K tokens) on what can be
  sent at all; analogous to a CPU's addressable memory.
- **Attention** -- the effective focus capacity; analogous to an L1
  cache; much smaller than the window.

**Context rot** -- "slow degradation that long sessions exhibit even
when nothing in the input has technically changed." The window hasn't
shrunk; the cache has fragmented.

**Attention starvation** -- a silent failure mode where the agent
behaves as if it was never instructed on something provably loaded
into context.

## Position-sensitivity: the attention curve

Accuracy is U-shaped across the window (citing Liu et al.'s "Lost in
the Middle" and Anthropic's needle-in-a-haystack evaluations, with
degradation measured in tens of percentage points):

- **Head (strong)** -- system prompt, project-base instructions, scope
  rules.
- **Mid-payload (weakest)** -- old turns, tool outputs, error pastes --
  described as "where instructions go to die."
- **Recent turns (strong)** -- roughly the last 5-10 turns.
- **Tail (strongest)** -- the current turn, the diff under review.

As new turns accumulate at the tail, content originally at the head
drifts into the mid-payload trough: "yesterday's head is today's
middle."

## The three levers of the attention economy

**Lever one -- Progressive disclosure.** "Only load the thing when you
need it." Split rules by scope; reference modules instead of inlining
them; use on-demand fetch tools. Example given: the `agentskills.io`
standard, where a `SKILL.md`'s description and activation predicate
are exposed cheaply, and the body only pulls into context when the
dispatcher matches the description against the current task. This
prevents loading a static architectural doc on every code review;
instead it loads only when a diff actually touches an interface
boundary.

**Lever two -- Subagent isolation.** "Fresh context window per scoped
task." Spawn child threads with independent context when work is
genuinely independent. Ties back to an asymmetry from Chapter 11:
"inference is per-thread; the filesystem is shared." The parent hands
off knowledge via the filesystem (a plan file, a focused brief, a
pinned reference) rather than via the parent's own polluted context.
This prevents a single long thread from accumulating attention waste
across every phase (planning -> research -> implementation ->
debugging -> review); each subagent instead operates in the
strong-attention portion of the U-curve.

**Lever three -- Plan-write-then-reload.** "Defeat drift by writing the
plan to a file and re-reading the file at decision points." The agent
writes a short, structured `plan.md` early (not a transcript), and
re-reads it before each consequential step (a refactor, a destructive
tool call, a final review). The plan starts at the head of context but
slips into the trough after ~20 turns; re-reading pulls it back to the
tail, where attention is strongest, exactly when it's needed. Frames
the filesystem as durable memory against an amnesiac inference layer.
Worked example cited: PR #394 (the Part IV case study), where the plan
was written, edited, and re-loaded at every wave boundary, and the
agent's behaviour at hour six was indistinguishable from hour one.

## Diagnosing attention starvation

Three diagnostic questions:

1. **How many tokens were in context at the failure moment?** (If more
   than a third of the window, attention is the prime suspect.)
2. **Where in the payload was the failed instruction?** (If in the
   middle, position is the prime suspect.)
3. **How many tool outputs/pasted blobs occurred since the instruction
   was last reinforced?** (More than a handful means recency bias is
   eating earlier inputs.)

### Symptom-to-cause table

| Symptom | Root cause | First check |
|---|---|---|
| Agent ignores a scope-loaded instruction | Rule sits in the middle of a long payload; effective attention has moved past it | Token count; position of the rule |
| Output references a file from 20 turns ago incorrectly | Earlier file contents no longer in active attention | Conversation length; tool calls since the file was last read |
| Agent forgets to call a tool it called 5 turns ago | Tool-use cues competing with accumulated context | Tool description position; window fullness |
| Hallucinated codebase detail | Grounding evidence missing, pushed out, or mid-payload | Transitive-closure check of loaded files |
| Quality cliff after an error-debugging exchange | Pasted errors bloat context; original task slips out of attention | Number of error blobs; error-text-to-task-text ratio |
| Inconsistent answers across two sessions | One session loaded more peripheral material than the other | Diff the two sessions' loaded-file lists |

## The practitioner's budget table

| Category | Cost | Benefit | Treatment |
|---|---|---|---|
| Project-base rules (always relevant) | Low (<500 tokens) | High (frames every turn) | Always-loaded at head |
| Scope-attached rules | Low-moderate | High (when in scope) | Always-loaded by scope predicate; carve scope tightly |
| On-demand skill body | Moderate | High (when activated) | Progressive disclosure; description-driven activation |
| Reference architectural docs | High | Low per turn, occasionally critical | Skill that pulls only on a matching diff; never always-loaded |
| Source files for the current change | Moderate-high | Essential | Load directly; trim unrelated files; rely on type stubs |
| Tool output from earlier turns | Grows without bound | Low after 1-2 turns | Summarize into the plan; let raw output sediment |
| Pasted error tracebacks | High | Low past the first paste | After 2 pastes, reset; carry forward a one-line summary |
| Conversation history >10 turns | High | Low (mostly recency illusions) | Reset the session; carry forward `plan.md` |
| External doc (web fetch) | Very high | High for one decision, low afterward | Bounded-scope grounding; cite the answer, drop the dump |
| Repository-wide grep/search | Very high | Rarely needed | Replace with targeted reads |
| Vendor model card/general guidance | High | Near zero for the task | Do not load |

Two governing heuristics, claimed to correctly classify roughly 80% of
loading mistakes seen in teams' first months:

- "Anything needed on every turn earns a place at the head; everything
  else should be progressive."
- "Anything that grows without bound across a session is a candidate
  for periodic reset and one-paragraph summary."

## The five access mechanisms

These are presented as exhausting the entire surface through which an
agent reaches outside its own prompt:

1. **Files** -- the local filesystem: markdown primitives
   (`.skill.md`, `.instructions.md`, `.agent.md`), source code,
   lockfiles, persisted plans. Highest reliability, lowest latency,
   deterministic across runs; the default for stageable content.
2. **CLI** -- shell commands (`git`, `grep`, `rg`, `jq`, `kubectl`,
   project scripts). An escape hatch to everything the local
   environment exposes; the agent inherits the operator's toolchain at
   zero integration cost.
3. **Web fetch** -- external URLs (vendor docs, RFCs, public
   references). High value when bounded, corrosive when unbounded.
   Requires **"bounded-scope grounding"** discipline: name what the
   fetch is authoritative for *before* fetching, and drop everything
   else.
4. **APIs and MCP** -- structured calls to remote services; the Model
   Context Protocol standardizes this layer, turning per-vendor
   integration into a per-server contract.
5. **Multi-modal capabilities** -- image, audio, video, screen capture
   as input; speech as output. Used for screenshot-driven UI work,
   design-doc figures, video walkthroughs. Subject to the same
   attention-budget physics as text -- a screenshot is not free.

Three cross-mechanism rules: the recursion bound is independent of
access mechanism, since all five land in the same harness loader and
attention window; these five mechanisms are the entire surface, no
sixth exists; and the choice of mechanism is a design decision, not an
accident, since the consequence differs (a file is reproducible, a CLI
call captures the local environment, a web fetch is fresh but
external).

## Anti-patterns and failure modes

**The eight-hundred-line architectural-decisions document.** Adding
comprehensive reference material with good intent but without
progressive-disclosure structure causes rules that matter to slip into
the attention trough.

**The do-everything parent thread.** Using a single long thread for
planning, research, implementation, debugging, and review accumulates
attention waste across every phase; the review phase ends up paying
for the debugging phase's pasted errors.

**Unbounded tool output accumulation.** Raw tool outputs sediment into
the mid-payload, taxing attention for every subsequent turn.

**Mid-payload trapping.** "The trough is where instructions go to die.
Anything you place in the middle of a long payload has to be
exceptional to survive."

## Connection back to PROSE (Ch. 13)

The chapter reframes three of the five PROSE constraints as expressions
of the same underlying physics:

- **P** (Progressive Disclosure) -- load on demand.
- **R** (Reduced Scope) -- carve scope tightly.
- **O** (Orchestrated Composition) -- structure with subagents.

"These are not three preferences, they are the three levers of the
attention economy expressed as constraints on the primitives a team
writes. The constraint exists because the physics exists."

## Terms of art coined/used

- "There is a difference between an instruction the model has read and
  an instruction the model has seen."
- "There is no free context. There is no neutral content."
- "Context rot" / "the cache has fragmented."
- "The trough is where instructions go to die."
- "Bounded-scope grounding" -- the discipline for external sources.
- "Context engineering" -- named as the combined discipline of the
  load lifecycle (Ch. 14) plus attention management (Ch. 15).

## Forward references

- **Chapter 16** (Deterministic/Probabilistic Boundary) -- where
  attention failures must be caught, at the deterministic seam.
- **Chapter 17** (Multi-Agent Orchestration) -- subagent isolation as a
  structural primitive; the Panel pattern.
- **Chapter 18** (Execution Meta-Process) -- plan-write-then-reload as
  a cross-wave discipline; the agent stack trace.

## Source

Ch. 15, Part III -- For Practitioners, *The Agentic SDLC Handbook* by
Daniel Meppiel --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/ch15-attention-and-context-economy.html
