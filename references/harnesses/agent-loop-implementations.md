# Agent loop: Claude Code, GitHub Copilot CLI, and OpenCode, and how to verify each

**Scope note.** [agent-loop.md](agent-loop.md) is deliberately general-concepts
only (Thought/Action/Observation, ReAct, stop-and-parse) and holds no
harness sections on purpose. This page is the harness-specific
companion: what Claude Code, Copilot CLI, and OpenCode each
document/implement about their own loop, and -- per AUTHORITY OVERREACH
discipline -- no harness's mechanism is assumed to describe another's.
Added 2026-08-24: a Copilot CLI section, closing a real gap this page
previously left (it originally covered only two of the book's three
target harnesses); the Claude Code and OpenCode sections below are
unchanged from the original 2026-07-30 write. Added 2026-09-01: a pi
section (§4), covering a fourth harness already documented elsewhere in
this book (see that section's own opening note for exactly which pages)
but not previously covered on this specific page.

## 1. Claude Code (Agent SDK docs)

```mermaid
sequenceDiagram
    participant Caller as SDK caller
    participant Harness as Claude Code (Agent SDK loop)
    participant Claude as Claude
    participant Tools as Tools

    Caller->>Harness: prompt
    Harness->>Claude: system prompt + tool defs + history (SystemMessage "init")
    loop each turn
        Claude->>Harness: AssistantMessage (text and/or tool calls)
        alt tool calls requested
            Harness->>Tools: execute (hooks may intercept before execution)
            Tools-->>Harness: tool results
            Harness->>Claude: UserMessage (tool results appended)
        else no tool calls
            Harness->>Caller: ResultMessage (subtype "success")
        end
    end
    Note over Harness,Claude: max_turns / max_budget_usd end the loop early with<br/>ResultMessage subtype "error_max_turns" / "error_max_budget_usd"
```

VERIFIED (`code.claude.com/docs/en/agent-sdk/agent-loop`, fetched
2026-07-30): the SDK "runs the same execution loop that powers Claude
Code." The loop-at-a-glance is five stages: **receive prompt** (system
prompt, tool definitions, conversation history all present from the
start; SDK yields a `SystemMessage` subtype `"init"`); **evaluate and
respond** (Claude may respond with text, request tool calls, or both;
SDK yields an `AssistantMessage`); **execute tools** (SDK runs each
requested tool, results feed back to Claude; hooks can intercept
before execution); **repeat** (steps 2-3 cycle; "each full cycle is one
turn"); **return result** (a final text-only `AssistantMessage`
followed by a `ResultMessage` with usage/cost/session ID).

VERIFIED (same page): the stop condition is explicit -- "Turns continue
until Claude produces output with no tool calls, at which point the
loop ends." Two hard caps exist independent of that natural stop:
`max_turns`/`maxTurns` (counts tool-use turns only) and
`max_budget_usd`/`maxBudgetUsd` (spend threshold, and it "covers
subagents: their spend counts toward the total"). Hitting either cap
yields a `ResultMessage` with `subtype: "error_max_turns"` or
`"error_max_budget_usd"` instead of `"success"` -- the loop does not
silently truncate, it reports which limit ended it.

VERIFIED (same page): tool results are appended as a `UserMessage`
"with the tool result content sent back to Claude" -- mechanically
the same append-to-context shape the Hugging Face course describes
generically in [agent-loop.md](agent-loop.md) section 2, now with
Claude-Code-specific naming (`UserMessage`, not "Observation"). The
context window "does not reset between turns within a session";
compaction (summarizing older history) is the documented mechanism for
when it approaches the limit, emitting `subtype: "compact_boundary"`.

VERIFIED (same page): parallel tool execution is real but
selective -- "Read-only tools ... can run concurrently. Tools that
modify state (like Edit, Write, and Bash) run sequentially to avoid
conflicts." Custom tools default to sequential unless annotated
`readOnlyHint`.

**Where to verify further, for Claude Code specifically:** this Agent
SDK page is documentation of a *product surface* (the SDK you can
build on), not published source code -- Claude Code itself is closed
source (per this skill's own SOURCE AUTHORITY rules,
`github.com/anthropics/claude-code` is authoritative only for its
CHANGELOG/README/examples/plugins/Issues, never for internal
implementation). If a claim needs to go deeper than what this docs
page states, the honest answer is "not independently verifiable from a
public source" -- do not fill that gap with OpenCode's or any other
harness's mechanism.

## 2. GitHub Copilot CLI

**Source and authorship note.** Copilot CLI is closed source, and
`docs.github.com/copilot` -- checked this session -- publishes no
dedicated agent-loop page for it (unlike Claude Code's Agent SDK docs
above). The grounding for this section is instead
`github.com/github/copilot-sdk`'s own `docs/features/agent-loop.md` and
`docs/features/session-limits.md` (fetched via `gh api` 2026-08-24) --
the Copilot SDK, a separate, adjacent client-library product this book
already treats cautiously elsewhere (`llm-api-contract.md` §3.2,
`session-persistence.md` §2: consistent-with-but-not-proof-of the CLI's
internal behavior). This particular document is a stronger source than
those two prior citations, though, because it explicitly assigns the
loop's authorship to the CLI rather than to itself: "The **SDK** is a
transport layer -- it sends your prompt to the **Copilot CLI** over
JSON-RPC and surfaces events back to your app. The **CLI** is the
orchestrator that runs the agentic tool-use loop, making one or more
LLM API calls until the task is done." That sentence is treated here as
VERIFIED evidence about the CLI's own loop shape, not the SDK's --
while still flagging, honestly, that no first-party
`docs.github.com`/`github.com/github/copilot-cli` page independently
corroborates it this session.

```mermaid
flowchart TD
    U["User prompt via session.send()"] --> T["LLM API call = one turn<br/>(assistant.turn_start)"]
    T --> Q{"toolRequests in<br/>the response?"}
    Q -->|Yes| X["CLI executes tools,<br/>collects results"]
    X -->|"Results fed back<br/>as next turn's input"| T
    Q -->|No| F["Final text response"]
    F --> I(["session.idle<br/>(always emitted, ephemeral)"])
    F -.->|"model called task_complete"| C(["session.task_complete<br/>(optional, persisted, has summary)"])
    I -->|"autopilot mode only,<br/>no task_complete seen"| N["Synthetic nudge message injected:<br/>'you have not yet marked the task complete...'"]
    N --> T
```

VERIFIED (`copilot-sdk` `docs/features/agent-loop.md`): a **turn** is
defined precisely as one LLM API call and its consequences -- "1. The
CLI sends the conversation history to the LLM. 2. The LLM responds
(possibly with tool requests). 3. If tools were requested, the CLI
executes them. 4. `assistant.turn_end` is emitted." The model sees the
**full conversation history** on every call (system prompt, user
message, and all prior tool calls/results) -- mechanically the same
append-to-context shape [agent-loop.md](agent-loop.md) describes
generically and [agent-loop-implementations.md](#1-claude-code-agent-sdk-docs)
§1 documents for Claude Code's own `UserMessage`-appended tool results.
The doc states plainly: "each iteration of this loop is exactly one LLM
API call... there are no hidden calls" for planning, evaluation, or
completion-checking -- a specific, falsifiable claim about the absence
of any separate deliberation step, offered as a documented worked
example: a search-heavy question can take four turns (grep/glob, read,
read-more, final no-tool-request answer) before the loop naturally
ends.

VERIFIED (same doc): the loop's natural stop condition is model-driven,
not harness-driven -- "The CLI is purely mechanical: 'model asked for
tools -> execute -> call model again.' The **model** is the
decision-maker for when to stop." A turn with no `toolRequests` in the
response ends the loop and emits `session.idle`.

VERIFIED (same doc): **two separate completion signals** exist, and the
doc is explicit that they carry different guarantees, not synonyms.
`session.idle` is always emitted when the tool-use loop ends, is
ephemeral (not persisted to disk, not replayed on resume), and means
only "the agent has stopped processing" -- a mechanical signal. This is
the recommended "done" signal for a caller (the SDK's `sendAndWait()`
blocks on it). `session.task_complete` is optional -- it requires the
model to explicitly call a `task_complete` tool -- is persisted to the
session's event log, carries an optional `summary` field, and means the
*model itself* considers the overall task fulfilled: a semantic signal
the harness cannot manufacture on the model's behalf.

VERIFIED (same doc): **autopilot mode** (the headless/autonomous mode
this book's [tui-cli-application-architecture.md](tui-cli-application-architecture.md)
§2 documents as one stop on Copilot CLI's mode-cycling `Shift+Tab`
wheel, not re-described here) turns that optional signal into a second,
harness-enforced completion gate. If the tool-use loop ends without the
model having called `task_complete`, the CLI "injects a synthetic user
message nudging the model": *"You have not yet marked the task as
complete using the task_complete tool. If you were planning, stop
planning and start implementing. You aren't done until you have fully
completed the task."* That synthetic message is read by the model as an
ordinary new user turn, which restarts the tool-use loop -- structurally
the same "inject a system-level instruction into the message stream to
force one more model turn" shape OpenCode's step-limit prompt injection
uses below (§3), though the *triggering condition* is the inverse: OpenCode
injects on a step-count ceiling being *reached*, Copilot CLI's autopilot
injects on a specific completion signal being *absent*. The same doc
documents the nudge's own anti-premature-completion guidance (don't call
`task_complete` with open questions, an unresolved error, or remaining
steps), producing what it calls a **two-level completion mechanism** in
autopilot: the model calls `task_complete` and the CLI reports
`session.task_complete`, or the model stops without it and gets nudged
back into the loop. In ordinary interactive mode, per the same doc, the
CLI issues no such nudge and `task_complete` may simply never appear
(conversational Q&A, model discretion, or an interrupted session) --
`session.idle` still fires regardless, because it is mechanical, not
semantic.

VERIFIED (`copilot-sdk` `docs/features/session-limits.md`, fetched via
`gh api` 2026-08-24): Copilot CLI has no documented hard turn-count cap
analogous to Claude Code's `max_turns` (§1 above). What it has instead
is a **soft, spend-denominated** cap -- `sessionLimits.maxAiCredits`,
forwarded by the SDK to the CLI at session creation/resume -- and the
doc is explicit that it is checked *after* a model call returns rather
than before one is dispatched: "Usage is checked after model calls
return, so one response can exceed the configured value before the
runtime blocks the next model call." Hitting it does not silently end
the loop the way Claude Code's `max_budget_usd` cap does; it raises a
`session_limits_exhausted.requested` event that "needs a user decision
before continuing" (resolved via a `session_limits_exhausted.completed`
event carrying the user's chosen action) -- a pause-for-a-decision
mechanism, not a hard stop, and this page cross-references rather than
re-derives [auth-and-usage-accounting.md](auth-and-usage-accounting.md)
as the fuller home for Copilot CLI's broader budget/cost-accounting
picture. Separately, this book's
[hooks-lifecycle-extensibility.md](hooks-lifecycle-extensibility.md) §2
already documents a changelog-verified, *loop-runaway* guard distinct
from both of the above: an `agentStop` hook that always returns "block"
no longer loops indefinitely -- the CLI ends the turn after **8
consecutive blocks** -- cross-referenced here, not repeated, because it
guards the hook-interception layer around the loop rather than the
loop's own turn-counting.

**Where to verify further, for Copilot CLI specifically:** the same
caveat this page states for Claude Code applies here with equal force
-- Copilot CLI itself ships no public source, so `agent-loop.md`'s
description of "the CLI is the orchestrator" is documentation of a
*product surface* (the SDK's own account of CLI behavior), not
independently cross-checkable source code. `github.com/github/copilot-sdk`
does ship real, public source for its own client bindings (TypeScript,
Python, Go, .NET, Java, Rust), but that is the JSON-RPC *client*, not
the CLI process's internal loop implementation -- do not conflate
"the SDK's source is public" with "the CLI's loop is independently
verifiable," and do not assume Claude Code's or OpenCode's own
loop-ending mechanics (below) apply here without a Copilot-specific
citation.

## 3. OpenCode

```mermaid
flowchart TD
    P[Primary agent] -->|Task tool| S[Subagent, specialized]
    P --> C{Step limit reached?}
    C -->|No| P
    C -->|Yes| Inj["MAX_STEPS_PROMPT injected<br/>(packages/core/src/session/runner/max-steps.ts)"]
    Inj --> Force[Tools disabled; model forced to a text-only summarization turn]
```

BEST CURRENT UNDERSTANDING, UNCONFIRMED (`opencode.ai/docs/`, the
top-level docs page, fetched 2026-07-30): this page covers install,
config, and basic usage, and explicitly does not describe loop
mechanics -- confirmed by fetching it directly and finding no such
content, not assumed absent.

VERIFIED (`opencode.ai/docs/agents/`, fetched 2026-07-30): OpenCode
distinguishes **primary agents** ("the main assistants you interact
with directly") from **subagents** ("specialized assistants that
primary agents can invoke for specific tasks"), invoked via a `Task`
tool ("invoke the Task tool"). Tool access is governed by a
permissions framework per agent: "Allow all operations without
approval," an `ask` mode, or "Disable the tool" entirely.

VERIFIED (same page): there is a documented step limit distinct from
Claude Code's turn/budget caps. "When the limit is reached, the agent
receives a special system prompt instructing it to respond with a
summarization of its work" -- i.e. the stop condition is enforced by
injecting a system prompt, not just truncating the stream.

VERIFIED (`github.com/anomalyco/opencode`, `dev` branch, fetched via
`gh api` 2026-07-30 -- flagging per this skill's own caveat that `dev`
is not a stable release tag): the exact prompt text lives in
`packages/core/src/session/runner/max-steps.ts`, exported as
`MAX_STEPS_PROMPT`:

> "CRITICAL - MAXIMUM STEPS REACHED / The maximum number of steps
> allowed for this task has been reached. Tools are disabled until
> next user input. Respond with text only." ... "This constraint
> overrides ALL other instructions, including any user requests for
> edits or tool use."

This is a real, currently-live implementation detail (not a docs
paraphrase) confirming the docs page's claim mechanically: the loop's
hard stop is a hard-coded prompt injected into the same message
stream the model reads, forcing a text-only turn.

**Where the loop implementation actually lives, for further
verification:** `packages/core/src/session/` is the real directory,
confirmed live via `gh api repos/anomalyco/opencode/contents/...` this
session -- specifically `session/runner/` (`index.ts`, `llm.ts`,
`max-steps.ts`, `model.ts`, `to-llm-message.ts`), `session/execution.ts`
and `session/execution/`, `session/compaction.ts`,
`session/run-coordinator.ts`. This session only opened
`max-steps.ts` directly; `runner/index.ts` and `execution.ts` are the
next files to read for the turn-by-turn control flow itself (message
send, tool-call parse, result append) -- BEST CURRENT UNDERSTANDING
that these are the right files, based on their names and directory
position, not yet read this session. Because OpenCode is genuinely
open-source (unlike Claude Code and Copilot CLI), this is the one
harness of the three where "go read the loop" is a literal, actionable
instruction rather than a dead end.

## 4. pi

**Source and naming note, resolved this session.** This book's other pi
sections (`llm-api-contract.md` §3.5, `hooks-lifecycle-extensibility.md`,
`permissions-and-sandboxing.md`, `session-persistence.md`,
`configuration.md`, `auth-and-usage-accounting.md`, `built-in-skills.md`,
`context-compression.md` §4, `model-routing-and-selection.md`) cite pi
under two different package spellings, `@earendil-works/pi-ai` and
`@earendil-works/pi-coding-agent`. VERIFIED, fetched 1 September 2026
directly from `github.com/earendil-works/pi` (`main` branch, confirmed
live via `gh api repos/earendil-works/pi` that this -- not a separate
`pi-mono` repository some internal doc links point at -- is the
canonical, non-redirecting repository identity): this is **not** an
error to resolve in favour of one spelling over the other. `pi` is a
monorepo shipping at least three separate, independently-versioned npm
packages under the same `0.84.4` release, each with its own
`package.json` read in full this session: `@earendil-works/pi-ai`
(`packages/ai`, described in its own `package.json` as "Unified LLM API
with automatic model discovery and provider configuration" -- the
wire-protocol layer `llm-api-contract.md` §3.5 documents),
`@earendil-works/pi-agent-core` (`packages/agent`, README: "Stateful
agent with tool execution and event streaming. Built on
`@earendil-works/pi-ai`" -- **the package this section is actually
about**, since it is the one that implements the turn loop), and
`@earendil-works/pi-coding-agent` (`packages/coding-agent`,
`package.json`: "Coding agent CLI with read, bash, edit, write tools and
session management," `bin: { pi: "dist/bundle/cli.js" }` -- the actual
shipped `pi` CLI product, which embeds `pi-agent-core` as a dependency
and layers tools, sessions, settings, and compaction policy on top of
it). Every prior page's citation of either of the two previously-used
names is independently correct for what it was describing; neither
this page nor any prior one has stated the existence of the third,
loop-implementing package, `pi-agent-core`, until now.

```mermaid
sequenceDiagram
    participant App as coding-agent (AgentSession)
    participant Loop as pi-agent-core (agentLoop/runLoop)
    participant LLM as Model (via pi-ai)
    participant Tools as Tools

    App->>Loop: agent.prompt(text) / agentLoop(prompts, context, config)
    Loop->>Loop: emit agent_start, turn_start
    loop each turn
        Loop->>LLM: streamAssistantResponse (context, tools)
        LLM-->>Loop: AssistantMessage (stopReason: toolUse / stop / length / error / aborted)
        alt stopReason is toolUse and no length-truncation
            Loop->>Tools: executeToolCalls (sequential or parallel)
            Tools-->>Loop: ToolResultMessage[]
            Loop->>Loop: emit turn_end; shouldStopAfterTurn? -> agent_end
            Loop->>App: prepareNextTurn hook (compaction check happens here)
            Loop->>Loop: emit turn_start (next turn)
        else stopReason is stop (no tool calls)
            Loop->>App: getFollowUpMessages()
            alt follow-ups queued
                Loop->>Loop: inject as pendingMessages, continue
            else none queued
                Loop->>Loop: emit agent_end
            end
        else stopReason is error or aborted
            Loop->>Loop: emit turn_end, agent_end (immediate)
        end
    end
```

**What constitutes one turn.** VERIFIED, `packages/agent/src/types.ts`
(full file read this session): the `AgentEvent` union's own code comment
states the definition plainly -- "Turn lifecycle - a turn is one
assistant response + any tool calls/results." Mechanically, VERIFIED
from `packages/agent/src/agent-loop.ts` (full file read this session,
the `runLoop()` function): a `turn_start` event is emitted, one
assistant response is streamed via `streamAssistantResponse()` (which
itself emits `message_start`/`message_update`/`message_end` for the
streaming deltas), any `toolCall` content blocks in that response are
then executed (`executeToolCalls()`, sequential or parallel per
`config.toolExecution`, default `"parallel"`), and a `turn_end` event
closes the turn carrying the assistant message and its tool results
together -- the same one-LLM-call-plus-its-tool-execution unit Copilot
CLI's own `agent-loop.md` names a turn as (§2 above), though pi's own
turn additionally brackets the tool execution *inside*
the same `turn_start`/`turn_end` pair rather than treating tool
execution as a step the harness performs between two separate LLM-call
turns.

**The natural stop condition is model-driven, with no documented hard
turn-count or budget cap layered on top of it.** VERIFIED, same file:
the inner loop continues (`hasMoreToolCalls || pendingMessages.length >
0`) for as long as the assistant's message contains tool calls that
were not all flagged `terminate: true`, or steering messages are
queued; once a turn produces no tool calls and no messages are pending,
the outer loop checks `config.getFollowUpMessages()` once more and, if
that returns nothing, breaks and emits `agent_end` -- the same "the
model itself is the decision-maker for when to stop" shape this page's
§2 documents for Copilot CLI, reached here by an unrelated engineering
team. VERIFIED, `packages/agent/src/types.ts`'s `AgentLoopConfig`
interface (read in full): there is no `maxTurns`, `maxBudgetUsd`,
`maxSteps`, or any other numeric cap field anywhere in the type the
low-level loop is configured with -- the loop's only means of an
externally-forced early stop is the `shouldStopAfterTurn` hook, an
arbitrary predicate the *embedding application* supplies (it "returns
true" to end the run "before starting another LLM call," checked
immediately after `turn_end` is emitted, ahead of `prepareNextTurn`).
VERIFIED, `packages/coding-agent/docs/settings.md` and
`packages/coding-agent/docs/usage.md` (both fetched and grepped in
full this session for `turn`, `budget`, `step`, `limit`): pi's own
shipped CLI documents no hard cap analogous to Claude Code's
`max_turns`/`max_budget_usd` (§1) or OpenCode's step-limit (§3). The
nearest neighbouring numeric cap the settings doc names,
`retry.provider.maxRetries` (default `0`), governs provider/SDK-level
HTTP retry attempts *within a single LLM call*, not the number of
turns a run may take -- a different axis entirely, not a loop-ending
mechanism, and the settings doc itself warns raising it above `0` "can
make SDK/provider retries handle out-of-usage-limit errors before Pi
sees them," i.e. it can actively mask rather than enforce a budget
limit. Absence of a documented cap in the docs fetched this session is
"not found," not "proven absent" -- the same epistemic caveat this
page's OpenCode section already applies to its own open questions.

**Compaction's relationship to the loop is the `prepareNextTurn` hook,
not a separate out-of-band check.** VERIFIED,
`packages/coding-agent/docs/compaction.md` (already cited in
[context-compression.md](context-compression.md) §4, cross-referenced
here rather than re-derived): "Pi checks this threshold after tools
finish and their results are appended, before starting the next
assistant response. If the threshold is crossed, Pi compacts inside
the same agent run and resumes with the summary and retained messages.
It skips this between-turn check when the completed tool batch
terminates the run and no queued message requires another response."
VERIFIED, cross-checked against source this session,
`packages/coding-agent/src/core/agent-session.ts` (grepped for
`prepareNextTurn`): the coding-agent layer wires its own compaction
check into the low-level loop by wrapping
`this.agent.prepareNextTurnWithContext`, the exact hook
`packages/agent/src/agent-loop.ts`'s `runLoop()` calls immediately
before emitting the next `turn_start` -- confirming mechanically, not
just by documentation cross-reference, that pi's compaction trigger
point is this hook and not a separate poll loop or timer. Because
`prepareNextTurn` is only reached when the inner loop is about to
continue, the doc's own stated skip condition ("terminates the run and
no queued message requires another response") falls out directly from
the source: a run that is about to emit `agent_end` never reaches the
`prepareNextTurn` call at all.

**A truncated-output edge case with no documented analogue elsewhere in
this book.** VERIFIED, `packages/agent/src/agent-loop.ts`
(`failToolCallsFromTruncatedMessage()`): if an assistant message's
`stopReason` is `"length"` (the model's output was cut off by the
token limit) and that message nonetheless contains tool calls, pi
never executes any of them. A `"length"` stop means "every tool call
in the message may carry truncated arguments" even if a best-effort
streaming JSON-salvage parser made them look syntactically valid and
schema-validate cleanly, so the loop synthesizes an error
`ToolResultMessage` for each one instead, instructing the model in the
error text to "re-issue the tool call with complete arguments" --
letting the model retry on the next turn rather than risking execution
of a write/edit/bash call built from truncated input. This is a
concrete pi-specific safety behavior at the loop level; none of §1-§3
above documents an equivalent stopReason-length-gates-tool-execution
rule for Claude Code, Copilot CLI, or OpenCode, though this page does
not claim any of the three lacks one -- only that no source read for
those sections this book states one.

**Steering and follow-up message queues: a user-initiated reinjection
mechanism, not a limit-triggered one.** VERIFIED,
`packages/coding-agent/docs/usage.md` and
`packages/agent/src/types.ts`: pi's interactive mode lets a user queue
a **steering message** (Enter) or a **follow-up message** (Alt+Enter)
while the agent is still working. A steering message is drained via
`config.getSteeringMessages()` and injected as soon as the current
turn's tool calls finish executing, before the next LLM call --
"tool calls from the current assistant message are not skipped." A
follow-up message is drained via `config.getFollowUpMessages()` only at
the point the agent would otherwise stop (no more tool calls pending
and no steering messages queued), and its presence is precisely what
makes the outer `while (true)` loop in `runLoop()` continue instead of
breaking to `agent_end`. Two independent settings, `steeringMode` and
`followUpMode` (both documented in `settings.md`, both defaulting to
`"one-at-a-time"`, the alternative being `"all"`), control whether a
drain point delivers every queued message at once or only the oldest
one, deferring the rest to the next drain point. Architecturally, this
is the same "inject a message into the stream to produce one more
model turn" move Copilot CLI's autopilot nudge (§2 above) and
OpenCode's `MAX_STEPS_PROMPT` (§3 above) both perform -- but the
*trigger* is categorically different from either: OpenCode injects on
a step-count ceiling being reached and Copilot CLI's autopilot injects
on a completion-signal being absent, both harness-side conditions,
whereas pi's own queues are drained only because a human explicitly
queued something -- there is no threshold or counter behind either
drain point.

**Subagents and a second, separate loop-adjacent runtime worth flagging
as an open question, not a settled fact.** BEST CURRENT UNDERSTANDING,
UNCONFIRMED: `packages/agent/src/harness/` is a real, implemented
subsystem (confirmed via a directory listing this session showing
`agent-harness.ts`, a `session/` subdirectory, and its own test suite,
`vitest.harness.config.ts`) documented at far greater length in
`packages/agent/docs/harness.md` -- a 200KB+ specification for a
durable, crash-recoverable `AgentHarness` built around named "lanes"
(cursors into a shared conversation tree), of which the spec states
directly: "Additional lanes support Slack threads, subagents, and other
parallel work over shared history." This reads as architecturally
comparable to OpenCode's primary/subagent split (§3) at the level of
intent, but this session did not read the harness.md spec in full given
its size, and grepping it found no `maxTurns`/`budget`/step-limit
concept there either. VERIFIED, however, cross-checking actual source
this session: `AgentHarness` is imported only by
`packages/coding-agent/src/server/create-harness.ts` in the shipped CLI
package, while `packages/coding-agent/src/core/agent-session.ts` --
whose own doc comment states it is "shared between all run modes
(interactive, print, rpc)" -- imports `Agent`, not `AgentHarness`, from
`@earendil-works/pi-agent-core`. So the turn loop this section documents
above (`agentLoop()`/`runLoop()`, the simpler of the two) is confirmed
to be what actually drives pi's ordinary interactive, print, and RPC
sessions; `AgentHarness`'s exact deployment surface -- an experimental
alternate server mode, a future replacement, something else -- was not
determined this session and should not be assumed to describe pi's
primary turn loop without a further, dedicated source read of
`packages/coding-agent/src/server/create-harness.ts`'s own caller(s) and
`harness.md` itself.

## 5. Comparison

All four document the same shape at the level the Hugging Face course
teaches generically -- evaluate, act, observe, repeat, stop when the
model stops requesting tools or a hard limit is hit. Concrete
differences, all VERIFIED from each harness's own source above:

- **Stop enforcement mechanism.** Claude Code's hard caps
  (`max_turns`, `max_budget_usd`) end the loop from the *harness side*
  and report a distinct `ResultMessage` subtype -- no further model
  turn happens. OpenCode's step limit ends the loop from *inside the
  model's own next turn*: a system prompt is injected demanding a
  text-only summarization response, so there is one more model call
  after the limit is hit, not zero. Copilot CLI's ordinary stop
  condition is purely model-driven (a turn produces no `toolRequests`,
  the loop ends, `session.idle` fires) with no turn-count cap
  documented at all; its **autopilot** mode adds a conditional
  reinjection mechanism structurally closer to OpenCode's than to
  Claude Code's -- a synthetic user message forces one more model turn
  -- but triggered by the *absence* of an explicit `task_complete`
  signal rather than by a step counter reaching zero. pi's ordinary
  stop condition is likewise purely model-driven (a turn with no tool
  calls, plus no queued follow-up message, ends the loop) and, per its
  own `AgentLoopConfig` type and its CLI's own settings/usage docs, has
  **no documented hard turn-count or budget cap at all** -- closer to
  Copilot CLI's undocumented-cap posture than to Claude Code's or
  OpenCode's, though pi's absence of a cap is source-verified (the
  config type has no such field) rather than merely undocumented on a
  closed product. pi's own reinjection mechanism (steering/follow-up
  message queues) is triggered neither by a harness-side counter
  (OpenCode) nor by an absent completion signal (Copilot CLI) but
  purely by explicit user action -- a third, distinct trigger class for
  the same "inject a message to force one more turn" move.
- **Budget/limit shape.** Claude Code's `max_budget_usd` is a hard,
  pre-emptively-enforced spend cap that ends the loop outright.
  Copilot CLI's nearest analogue, `sessionLimits.maxAiCredits`, is
  softer on two axes at once: it is checked only *after* a model call
  returns (so one call can overshoot it) and, on exhaustion, raises an
  event requiring a user decision rather than silently ending the run.
  OpenCode's step limit is shaped like a turn-count cap rather than a
  spend cap, and (per its own stop-enforcement behavior above) never
  produces a hard stop with zero further model calls the way Claude
  Code's caps do. pi has no analogue at all in this dimension -- its
  nearest numeric cap, `retry.provider.maxRetries`, bounds per-call HTTP
  retries, not turns or spend, and defaults to `0` (disabled).
- **Verifiability.** Claude Code's and Copilot CLI's loops are each
  knowable only through what their respective companies choose to
  document (the Agent SDK page for Claude Code; the separate Copilot
  SDK's own docs, which explicitly attribute the loop to the CLI, for
  Copilot CLI) -- neither has a public implementation to cross-check
  the claim against. OpenCode's is knowable two ways that can be
  checked against each other: the docs page's claim and the actual
  `max-steps.ts` source, which is what this page did for OpenCode
  specifically. pi is the most directly verifiable of the four on this
  page's own subject: `packages/agent/src/agent-loop.ts` and
  `types.ts` are the actual, currently-shipping loop implementation
  (not a docs paraphrase), and this page additionally confirmed by
  reading `agent-session.ts`'s own import statement that this is the
  implementation driving pi's real interactive/print/RPC sessions,
  rather than the separate, larger `AgentHarness` specification that
  also lives in the same package.
- **Turn/tool-execution boundary.** Claude Code, Copilot CLI, and
  OpenCode all treat "one LLM call" as the atomic turn unit, with tool
  execution happening *between* two turns. pi's own `turn_start`/
  `turn_end` pair instead brackets one LLM call *and* the execution of
  every tool call that response contained, as one turn -- a smaller
  but real structural difference in the same overall Action/Observation
  shape.

BEST CURRENT UNDERSTANDING, UNCONFIRMED: whether OpenCode has an
analogue to Claude Code's budget cap (`max_budget_usd`) or to its
read-only-vs-mutating parallel tool execution split -- neither was
seen in the pages/files fetched this session; would need
`session/execution.ts` and the permission-framework docs read directly
before claiming either way. Likewise UNCONFIRMED: whether Copilot CLI
has any hard, harness-side turn-count cap at all distinct from the
soft `maxAiCredits` spend cap and the `agentStop`-hook 8-consecutive-
block guard documented above -- no such cap was found in the Copilot
SDK docs or the CLI's own changelog fetched this session, which is
"not found," not "proven absent." Likewise UNCONFIRMED for pi: whether
`AgentHarness` (§4's closing paragraph) ever governs turn-loop
behavior for any real deployment of the CLI, and what its own
lane-based subagent mechanism's turn/step semantics are -- `harness.md`
was not read in full this session given its size.

## Sources

- `code.claude.com/docs/en/agent-sdk/agent-loop` -- fetched 2026-07-30.
  Authoritative for the Claude Code Agent SDK's documented loop
  behavior (stages, message types, turn/budget caps, compaction,
  parallel tool execution). Not a claim about internal implementation
  Anthropic hasn't published.
- `github.com/github/copilot-sdk`, `docs/features/agent-loop.md` and
  `docs/features/session-limits.md`, fetched via `gh api` 2026-08-24.
  Authoritative for the Copilot SDK's own documented description of
  Copilot CLI's tool-use loop (turn definition, `session.idle` vs.
  `session.task_complete`, autopilot's nudge mechanism) and its
  AI-Credits session-limit mechanism. An adjacent-product source, not
  Copilot CLI's own first-party docs -- flagged as such throughout §2
  -- because `docs.github.com/copilot` publishes no dedicated
  agent-loop page for the CLI as of this session's check.
- `github.com/github/copilot-cli` `changelog.md`, fetched via `gh api`
  2026-08-24 -- cross-referenced for the `agentStop`-hook
  8-consecutive-block cap already documented in
  [hooks-lifecycle-extensibility.md](hooks-lifecycle-extensibility.md),
  and checked (with no relevant hits) for any documented hard turn- or
  step-count cap on the main loop itself.
- `opencode.ai/docs/agents/` and `opencode.ai/docs/` -- fetched
  2026-07-30. Authoritative for OpenCode's documented agent/subagent
  model, permissions framework, and the existence of a step limit.
- `github.com/anomalyco/opencode`, `dev` branch, via `gh api` --
  fetched 2026-07-30 (directory listings of `packages/core/src`,
  `packages/core/src/session`, `packages/core/src/session/runner`, and
  the full contents of `max-steps.ts`). Authoritative for OpenCode's
  real implementation, with the standing caveat that `dev` is not a
  stable release tag and may not match the current stable release.
- Hugging Face Agents Course -- see [agent-loop.md](agent-loop.md)'s
  own Sources section; used here only for the shared vocabulary this
  page maps onto, not re-cited as harness-specific evidence.
- `github.com/earendil-works/pi`, `main` branch, fetched 1 September
  2026 -- confirmed via `gh api repos/earendil-works/pi` as the
  canonical, non-redirecting repository (not the `pi-mono` name some
  internal doc links reference). Full-file reads via `gh api
  repos/earendil-works/pi/contents/<path>`:
  `packages/ai/package.json` and `packages/agent/package.json` and
  `packages/coding-agent/package.json` (resolving the
  `pi-ai`/`pi-agent-core`/`pi-coding-agent` three-package naming);
  `packages/agent/src/agent-loop.ts` and `packages/agent/src/types.ts`
  (the turn-loop implementation itself: turn definition, stop
  conditions, `shouldStopAfterTurn`/`prepareNextTurn` hooks, truncated-
  tool-call handling); `packages/agent/README.md` (the `Agent` class,
  event-sequence walkthrough); `packages/coding-agent/docs/settings.md`
  and `docs/usage.md` (grepped for turn/budget/step-limit config keys,
  and for the steering/follow-up keybindings and `steeringMode`/
  `followUpMode` defaults); `packages/coding-agent/docs/compaction.md`
  (the between-turn compaction-check description, also cited in
  [context-compression.md](context-compression.md) §4); and
  `packages/coding-agent/src/core/agent-session.ts` (grepped for
  `prepareNextTurn`, confirming the compaction-hook wiring, and for its
  own `AgentSession`/`AgentHarness` import statements, confirming which
  loop implementation drives pi's real interactive/print/RPC sessions).
  `packages/agent/docs/harness.md` and the `packages/agent/src/harness/`
  directory were confirmed to exist and were spot-checked (directory
  listing, targeted greps for turn/budget/step-limit terms, the
  "lanes... subagents" quote) but not read in full given the document's
  size (200KB+) -- flagged as an open question in §4's own closing
  paragraph, not treated as fully verified.
