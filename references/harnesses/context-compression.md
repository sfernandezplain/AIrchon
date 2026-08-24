# Context compression -- Claude Code, GitHub Copilot CLI, OpenCode, and pi

**Scope note.** [instruction-context-budget.md](instruction-context-budget.md)
covers the *eagerly-loaded instruction* tier (CLAUDE.md/rules/skill
descriptions, `applyTo:`/`paths:` scoping) and how to keep it small.
[memory-management.md](memory-management.md) §1.7/§2.4 covers
compaction from the *memory-survival* angle -- which instruction/memory
tiers are re-injected from disk afterward. This page is the third
angle: the mid-run compression *mechanism itself* -- what actually
triggers it, what gets evicted vs. summarized vs. kept verbatim, the
exact token thresholds where known, and (for OpenCode specifically,
because it is the one harness of the three whose implementation is
publicly readable) the real source-level algorithm. Where a claim
already lives in one of those two pages, this page cites it rather
than re-deriving it, and adds the compression-specific mechanism that
neither page went into.

Every claim is tagged VERIFIED (fetched this session, or already
verified and cited in a page linked above) or BEST CURRENT
UNDERSTANDING, UNCONFIRMED. Claude Code, Copilot CLI, OpenCode, and pi
(Earendil Works) are four separate products from four separate
organizations/authors -- nothing confirmed for one is assumed for another.

---

## 1. Claude Code

Sources: `code.claude.com/docs/en/context-window`,
`code.claude.com/docs/en/how-claude-code-works`, and
`code.claude.com/docs/en/model-config`, all fetched fresh this session
(2026-07-30). VERIFIED unless tagged otherwise.

### 1.1 The two-phase mechanism, stated directly

The "How Claude Code works" page states the algorithm in one sentence:
"It clears older tool outputs first, then summarizes the conversation
if needed." That is a genuine two-phase design, not a single
summarization pass -- eviction of bulky, already-consumed tool output is
tried first because it is cheap (no model call, no information loss
for anything the model didn't need to keep referencing) and only
escalates to an LLM summarization call if clearing outputs alone
doesn't free enough room. The community term "microcompaction" for the
eviction phase does **not** appear on either docs page or in
`CHANGELOG.md` (grepped in a prior session) -- treat the *behavior* as
documented, the *name* as unofficial.

### 1.2 What the summary keeps and drops

The interactive context-window page states the summary's actual
contents, not just "a summary": it "keeps: your requests and intent,
key technical concepts, files examined or modified with important code
snippets, errors and how they were fixed, pending tasks, and current
work. It replaces the verbatim conversation: full tool outputs and
intermediate reasoning are gone. Claude can still reference the work
but won't have the exact code it read earlier." That is a fixed
six-part content model (intent, concepts, files+snippets, error
history, pending tasks, current work), not a free-form paraphrase --
structurally comparable in spirit to OpenCode's fixed Markdown template
in §3.4 below, though Claude Code's docs do not publish an equivalent
literal prompt template the way OpenCode's source does.

As of v2.1.198 (per `CHANGELOG.md`, cited previously in
memory-management.md §1.7), "the summarization request inherits the
session's extended thinking configuration" -- the compaction call
reasons with thinking on only if the session already had it on; this
does not change the user's own session settings afterward.

### 1.3 Trigger thresholds -- what is documented and what is not

```mermaid
flowchart TD
    U["Usage grows during the session"] --> C{"Approaching context limit?"}
    C -->|No| U
    C -->|Yes| W["Warning surfaces at 80% (raised from 60%, CHANGELOG)"]
    W --> A["Auto-compact fires automatically before the window fills"]
    A --> E["Evict older tool outputs first"]
    E --> S{"Enough freed?"}
    S -->|Yes| Done["Session continues"]
    S -->|No| Sum["Summarize conversation via LLM call<br/>(inherits extended-thinking setting, v2.1.198)"]
    Sum --> Refill{"Context refills immediately<br/>on 3rd consecutive attempt?"}
    Refill -->|Yes| Thrash["Auto-compaction stops;<br/>actionable error instead of looping"]
    Refill -->|No| Done
```

VERIFIED, `model-config` page: **Sonnet 5 on the Anthropic API always
runs at a 1,000,000-token window** (no `[1m]` suffix needed, no usage
credits required on any plan), and "sessions auto-compact before the
window fills, at about **967K tokens by default**"; `CLAUDE_CODE_AUTO_
COMPACT_WINDOW` overrides that threshold. Two configurations budget the
window at 200K instead and auto-compact at *that* boundary: routing
through an **LLM gateway** (`ANTHROPIC_BASE_URL` pointed at a gateway --
Claude Code can't verify 1M support behind a gateway unless you
explicitly select the `sonnet[1m]` picker entry), and
`CLAUDE_CODE_DISABLE_1M_CONTEXT=1`. Other models supporting extended
context (Fable 5, Opus 4.6+, Sonnet 4.6) have their own
plan-dependent 1M-vs-200K availability, documented in the same page's
"Extended context" table, but the page does not give an equivalent
"~967K" auto-compact figure for those models specifically -- only for
Sonnet 5. Do not generalize the 967K number to other models.

Separately, the earlier-verified **warning threshold** (not the
compaction trigger itself) is a `CHANGELOG.md` entry: "Increased
auto-compact warning threshold from 60% to 80%." No page fetched this
session or previously states an exact universal percentage at which
auto-compaction *itself* fires for the default 200K-class window --
only the Sonnet-5-specific 967K/1M figure above and the warning-UI
percentage are documented. Treat "what % triggers compaction on a
200K-class model" as **not independently confirmed** from a public
source.

### 1.4 Anti-thrash guard and model-fallback interaction

VERIFIED (`CHANGELOG.md`, cited previously): "after context refills
immediately following three consecutive compactions, auto-compaction
stops with an actionable error rather than looping." This is a hard
circuit-breaker on the two-phase mechanism above, distinct from the
warning threshold -- it fires when a single file or tool output is so
large that clearing-then-summarizing can't actually create headroom.

VERIFIED (`model-config` page, "Automatic model fallback" section): the
model-fallback chain also covers compaction -- "Claude Code won't fall
back to a model with a smaller context window than the primary's,
since summarizing there would cut off part of the conversation first.
If every fallback is smaller, compaction shows the original error and
you can retry." So compaction is fallback-chain-aware in a specific
direction: it will never silently summarize with a smaller-windowed
model than the one that filled the window in the first place.

### 1.5 Hooks and observability

`PreCompact` (cited previously, `CHANGELOG.md`) can block compaction by
exiting 2 or returning `{"decision":"block"}`. The Agent SDK's
documented loop (see [agent-loop-implementations.md](agent-loop-implementations.md)
§1) emits a `SystemMessage` / `ResultMessage` stream with a
`compact_boundary` subtype marking where compaction happened in that
stream -- a programmatic signal for anything built on the SDK, distinct
from the interactive CLI's `/compact` UI notice. `/context` is the
live inspection surface for current usage by category, and `/mcp`
breaks out per-MCP-server cost specifically.

### 1.6 Manual levers

`/compact focus on ...` (or a "Compact Instructions" section in
CLAUDE.md) steers what the summary keeps rather than accepting the
automatic pass's guess. `/clear` is a harder lever -- it discards the
conversation instead of summarizing it, recommended "when switching to
unrelated work" since old conversation both crowds out useful content
and costs tokens on every subsequent message even when compacted.
Delegating large reads to a subagent (see
[handoff-mechanism.md](handoff-mechanism.md)) avoids the problem
entirely by keeping bulky file contents in a context window that never
touches the main session's budget -- the context-window walkthrough
page quantifies this concretely for one example (a subagent reading
6,100 tokens of files and returning a 420-token summary).

---

## 2. GitHub Copilot CLI

Source: `github.com/github/copilot-cli` `changelog.md`, fetched fresh
this session via `gh api repos/github/copilot-cli/contents/
changelog.md` (2026-07-30), cross-referenced against
`docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/overview`
(fetched previously, cited in memory-management.md §2.4). VERIFIED
unless tagged otherwise. Unlike Claude Code and OpenCode, Copilot CLI
is closed source -- everything below is inferred from documented
behavior and the product's own changelog, never from an implementation
file.

### 2.1 A visible evolution, not one static mechanism

Reading the full changelog rather than just the current docs page
shows this is a feature that was *replaced*, not merely refined, and
the dates make the sequence unambiguous (changelog is newest-first;
these are read oldest-to-newest below):

```mermaid
stateDiagram-v2
    state "v0.0.334 (2025-10-03)<br/>Truncation-warning era" as Era1
    state "v0.0.374 (2026-01-02)<br/>Background auto-compaction" as Era2
    state "v0.0.385-0.0.399 (2026-01-19..29)<br/>Compaction checkpoints" as Era3
    state "v1.0.52-1.0.56 (2026-05-23..29)<br/>Context-tier enforcement" as Era4
    state "v1.0.76 (2026-07-29)<br/>Blocked-compaction warning" as Era5

    Era1 --> Era2: real summarization replaces plain truncation
    Era2 --> Era3: infinite sessions via checkpointed re-compaction
    Era3 --> Era4: tier selection (200K/1M) now constrains compaction end-to-end
    Era4 --> Era5: surfaces when compaction itself cannot free enough room
```

- **v0.0.334 (2025-10-03).** The earliest documented mechanism was
  plain truncation, not summarization: "Added a warning when
  conversation context approaches **≤20% remaining** of the model's
  limit that truncation will soon occur. At this point, we recommend
  you begin a new session." No compaction existed yet -- the
  documented remedy was to start over.
- **v0.0.374 (2026-01-02).** "Add auto-compaction at **95% token
  limit** and `/compact` command" -- the origin of real
  summarization-based compaction, matching the number the current docs
  page still states.
- **v0.0.380 (2026-01-13).** "Auto-compaction runs in background
  without blocking the conversation" -- established as async from the
  start, unlike Claude Code's `/compact`, which the interactive
  walkthrough shows as a foreground step in the timeline.
  **v0.0.384/0.0.385 (2026-01-16/19).** "Enable infinite sessions with
  automatic long-running context management through **compaction
  checkpoints**" and a fix: "Fixed bug causing model call failures
  after compaction in some scenarios" -- evidence the checkpoint
  mechanism was fragile enough early on to fail model calls, since
  fixed.
- **v0.0.386 (2026-01-19).** "Background compaction preserves tool
  call sequences correctly" -- a fix confirming compaction has to
  respect tool-call/tool-result pairing as a structural boundary, the
  same shape of constraint OpenCode's `select()`/`splitTurn()` handle
  explicitly in source (§3.4).
  **v0.0.389 (2026-01-22).** "Messages sent during `/compact` are
  automatically queued" -- a manual compaction does not drop or reject
  concurrent user input, it defers it.
- **v0.0.393/0.0.396/0.0.399 (2026-01-23/27/29).** "Show conversation
  compaction status as timeline messages instead of header indicator,"
  "Simplify compaction timeline entries," "Compaction messages show
  clearer command hints to view checkpoint summaries," and "**Skills
  remain effective after conversation history is compacted**" --
  checkpoints are individually viewable objects in the timeline, and
  skill state is explicitly exempted from whatever gets dropped.
- **v0.0.410 (2026-02-14).** "Reduced memory growth in long sessions by
  evicting transient events after compaction" -- a *second*, later
  eviction pass distinct from the compaction summary itself, targeting
  ephemeral event-log bloat that accumulates even after a session has
  already compacted once.
- **v1.0.26 (2026-04-14).** "Fix truncation logic for **codex
  models**" -- direct evidence that truncation/token-accounting logic
  is at least partly model-family-specific, not one universal
  algorithm across every backend Copilot CLI can route to.
- **v1.0.52/1.0.56 (2026-05-23/29).** "Context window tier selection
  (default ~200K vs 1M tokens) is now enforced end-to-end, so picking a
  tier actually constrains compaction, truncation, and token display,"
  and tier selection "now persists durably in session events and
  survives SDK-only resume paths so tier-derived limits are reapplied
  to request, compaction, and truncation logic without app-level
  repair" -- confirming compaction reads its token budget from the same
  tier setting that governs the rest of the request pipeline, and that
  this used to require app-level repair after resume (now fixed).
- **v1.0.76 (2026-07-29, the day before this page was written).**
  "Restore the early warning when unreclaimable system and tool context
  nears the limit, before **automatic compaction is blocked**." This is
  the newest and most structurally interesting entry: it names a
  failure mode where compaction cannot proceed at all -- when the fixed
  overhead (system prompt plus tool schemas, which compaction cannot
  compress away because they aren't conversation history) alone
  approaches the limit, there is nothing left for compaction to
  reclaim, and the CLI surfaces a warning *before* that state rather
  than silently failing once compaction is already blocked.

### 2.2 What is not documented

**Not found** anywhere in the docs pages or the full changelog: the
internal shape of the summarization algorithm itself (single-shot vs.
staged, whether it re-summarizes-of-a-summary or restarts from the
full original history each compaction, any fixed template analogous to
Claude Code's six-part content model or OpenCode's Markdown template).
The only load-bearing facts are outward behavior: **background**, **95%
trigger**, **checkpointed**, preserves **skills** and **extended
thinking**, evicts **transient events** in a later pass, and (as of
today's entry) can enter a **blocked** state distinguishable from
ordinary compaction. Whether `preCompact` can block compaction the way
Claude Code's `PreCompact` can is likewise **UNCONFIRMED** -- the hook
exists ("Add preCompact hook to run commands before context compaction
starts") but no changelog entry or doc states its return-value
contract.

### 2.3 Observability

VERIFIED (previously cited in memory-management.md §2.4, from the same
changelog): "chat spans after a successful compaction carry
`gen_ai.conversation.compacted=true`, and the summary is emitted as a
`CompactionPart` in `gen_ai.input.messages`" -- a machine-checkable OTel
marker, the closest Copilot CLI equivalent to Claude Code's
`compact_boundary` `ResultMessage` subtype.

---

## 3. OpenCode

Source: `github.com/anomalyco/opencode`, `dev` branch, fetched live via
`gh api` this session (2026-07-30) -- flagging per this project's
standing caveat that `dev` is not a stable release tag and this code
may not reflect the current stable release. This is the one harness of
the three where the compression algorithm is not inferred from
documentation at all -- it is read directly from source. `opencode.ai/docs/config/`
was also fetched this session for the documented config surface.

### 3.1 Two implementations exist in this repository -- flagged, not conflated

VERIFIED, live directory listing and file contents: there are **two**
files named `compaction.ts`, in two different packages, with two
different config schemas:

- `packages/core/src/session/compaction.ts` -- exports a
  `compactIfNeeded`/`compactAfterOverflow` factory (`make()`) built
  around a `ConfigV2.Compaction` schema (`auto`, `buffer`, `keep.tokens`,
  and an unused-by-this-file `prune` field). It is a comparatively
  simple engine: split history into a token-budgeted `head`/`recent`
  pair, summarize `head` with a fixed anchored-summary template
  (`buildPrompt`, detailed in §3.4), replace it.
- `packages/opencode/src/session/compaction.ts` -- registers a full
  Effect-TS `Context.Service` (`@opencode/SessionCompaction`) wired via
  `LayerNode.make(...)` with real dependencies (`Config`, `Session`,
  `Agent`, `Plugin`, `SessionProcessor`, `Provider`, `EventV2Bridge`,
  `RuntimeFlags`), built around a `ConfigV1.Info` schema (`auto`,
  `prune`, `reserved`, plus two fields undocumented on the config page:
  `tail_turns`, `preserve_recent_tokens`). It **imports `buildPrompt`
  from the core package** (`import { buildPrompt } from
  "@opencode-ai/core/session/compaction"`) -- so the two files share
  the summarization *prompt template* but not the same eviction/
  selection/scheduling logic.

This session found no call site instantiating `packages/core`'s
`make()` factory anywhere in `packages/opencode` (a `search/code` query
for its usage returned nothing but the test file for the *other*
implementation). *BEST CURRENT UNDERSTANDING, UNCONFIRMED:* the
`packages/opencode` service is the one actually wired into a running
CLI session (confirmed by its DI registration and by finding its
`prune()` method's real call site in `packages/opencode/src/session/
prompt.ts`, §3.3); whether `packages/core`'s engine is dead code, an
in-progress replacement, or consumed by some other embedding (the SDK,
a headless/server mode) not searched this session is **not
determined**. Everything from §3.2 onward describes the
`packages/opencode` (production) engine unless stated otherwise.

### 3.2 Overflow detection: the token budget

VERIFIED, `packages/opencode/src/session/overflow.ts`:

```
const COMPACTION_BUFFER = 20_000

usable(cfg, model) =
    reserved = cfg.compaction?.reserved ?? min(COMPACTION_BUFFER, model's max output tokens)
    model.limit.input
      ? max(0, model.limit.input - reserved)
      : max(0, model.limit.context - model's max output tokens)

isOverflow(cfg, tokens, model) =
    cfg.compaction?.auto === false        -> false (disabled)
    model.limit.context === 0             -> false (unknown/unbounded)
    else: (tokens.total || input+output+cache.read+cache.write) >= usable(...)
```

So the "usable" budget is the model's input-token limit minus a
**reserved** buffer (config key `compaction.reserved`, default the
smaller of 20,000 tokens or the model's own max-output-tokens figure) --
conceptually the same "leave headroom for the response" idea as
Claude Code's warning/auto-compact split, but expressed as one
subtraction rather than a percentage.

### 3.3 Two independently-scheduled passes, not one

```mermaid
flowchart TD
    Turn["Model turn completes, usage.tokens known"] --> OF{"isOverflow(tokens, model)?"}
    OF -->|No| Prune["prune() forked in background<br/>(Effect.forkIn(scope), errors ignored)"]
    OF -->|Yes, proactive| Flag["ctx.needsCompaction = true"]
    ProviderErr["Provider throws ContextOverflowError mid-generation"] --> Flag2["ctx.needsCompaction = true (overflow=true path)"]
    Flag --> Process["SessionCompaction.process()"]
    Flag2 --> Process
    Prune --> NextTurn["Next turn begins"]
    Process --> Select["select(): tail_turns preserved verbatim,<br/>splitTurn() for partial-turn budget fit"]
    Select --> Summarize["buildPrompt(): anchored-summary template,<br/>LLM call via dedicated 'compaction' agent"]
    Summarize --> Replace["Head replaced by summary message;<br/>tail + summary become new history"]
    Replace --> Continue{"input.auto and result == continue?"}
    Continue -->|Yes| Nudge["Synthetic 'Continue if you have next steps...'<br/>message appended (plugin-gated)"]
    Continue -->|No| Done["Turn ends"]
```

VERIFIED, `packages/opencode/src/session/processor.ts`: compaction has
**two distinct trigger paths**, both setting the same
`ctx.needsCompaction` flag that the streaming loop checks
(`Stream.takeUntil(() => ctx.needsCompaction)`) before deciding whether
`process()`'s result is `"compact"` (vs. `"stop"`/`"continue"`):

1. **Proactive**: after each streamed response, `isOverflow({ tokens:
   usage.tokens, model })` is checked against the token usage the
   provider reported for that turn.
2. **Reactive**: if the provider itself throws
   `SessionV1.ContextOverflowError` mid-generation (a hard overflow,
   not just "approaching" one), the same flag is set -- unless
   `compaction.auto === false` and the errroring message wasn't already
   a summary attempt, in which case it surfaces as a real error instead
   of looping.

Separately, VERIFIED in `packages/opencode/src/session/prompt.ts`:
`compaction.prune({ sessionID })` is invoked as
`.pipe(Effect.ignore, Effect.forkIn(scope))` at the tail of the main
prompt loop -- i.e. **forked as fire-and-forget after every turn**,
independent of whether that turn triggered overflow-based compaction at
all. This is the second, always-on eviction pass, distinct from the
summarization pass triggered by `isOverflow`/`ContextOverflowError`.

### 3.4 `prune()`: eviction-only, no LLM call

VERIFIED, `packages/opencode/src/session/compaction.ts`. A background
sweep with its own constants, independent of the summarization budget
in §3.2:

```
PRUNE_MINIMUM = 20_000   // only commit if total prunable exceeds this
PRUNE_PROTECT = 40_000   // always keep at least this many tokens of recent tool output
TOOL_OUTPUT_MAX_CHARS = 2_000
PRUNE_PROTECTED_TOOLS = ["skill"]   // never pruned regardless of age
```

The algorithm walks backward through session messages, counting only
completed tool-call output tokens, skipping the two most recent user
turns entirely (`turns < 2` guard) and stopping the walk the instant it
hits a prior summarized/compacted assistant message (so it never
re-prunes past an earlier compaction boundary). Anything within the
most recent `PRUNE_PROTECT` (40,000) tokens of tool output is left
alone; anything older is marked (`part.state.time.compacted =
Date.now()`) -- which erases its displayed output content -- but **only
if** the total amount found to prune exceeds `PRUNE_MINIMUM` (20,000)
tokens, i.e. a not-worth-it floor so a small amount of old output isn't
churned for negligible savings. This runs with no model call at all --
it is pure eviction, gated by `compaction.prune` (a boolean, default
`false` per `opencode.ai/docs/config/`).

### 3.5 `process()`: the summarization pass, in detail

VERIFIED, same file, plus `packages/opencode/src/config/compaction.ts`
(the `ConfigV1.Info` schema) and `packages/core/src/session/
compaction.ts` (the shared `buildPrompt`):

- **Tail preservation.** Messages are grouped into `turns` (one per
  user message, spanning to the next user message). The most recent
  `tail_turns` turns (config key `compaction.tail_turns`, default
  **2**, undocumented on the current config page) are kept verbatim if
  they fit a token budget, `preserveRecentBudget`: the config override
  `compaction.preserve_recent_tokens` (also undocumented on the config
  page) if set, else `min(8000, max(2000, floor(usable_context *
  0.25)))` -- i.e. **25% of the usable context window by default,
  clamped to a [2,000, 8,000]-token range**.
- **Partial-turn splitting.** If the most recent turns don't fit the
  budget as whole units, `splitTurn()` walks forward within the
  oldest-still-considered turn to find a message index where the
  *remaining* slice fits the leftover budget -- turns can be split
  mid-way rather than kept or dropped all-or-nothing.
- **Everything before the kept tail** (`head`) is what actually gets
  summarized away.
- **The prompt is a fixed, anchored-summary Markdown template**
  (`buildPrompt`, shared with the `core` package): six required
  sections -- **Objective**, **Important Details**, **Work State**
  (with **Completed**/**Active**/**Blocked** subsections), **Next
  Move**, and **Relevant Files** -- with an explicit rule set: "Keep
  every section, even when empty," "Use terse bullets, not prose
  paragraphs," "Preserve exact file paths, symbols, commands, error
  strings, URLs, and identifiers when known," and "Do not mention the
  summary process or that context was compacted."
- **Anchored, not from-scratch.** `completedCompactions()` scans
  history for prior compaction pairs and takes the *latest* one's
  summary text as an anchor. If one exists, the prompt instructs the
  model to "Update the anchored summary below using the conversation
  history above. Preserve still-true details, remove stale details,
  and merge in the new facts" -- rather than regenerating a full
  summary from the original conversation every time. This is a
  concrete, source-verified answer to a question Claude Code's own
  docs leave open (§1.2): OpenCode's second-and-later compactions are
  demonstrably incremental updates to a running note, not
  re-summarizations of the full original history.
- **Compaction runs as a real message, through a real agent.** The
  summarization call is dispatched through a dedicated **`compaction`
  agent** (`agents.get("compaction")`, which can carry its own
  `model:` distinct from the session's own model), and its result is
  stored as an ordinary assistant message in the session (`mode:
  "compaction"`, `summary: true`) with a `compaction` part attached to
  the parent user message -- i.e. compaction is not a side-channel
  operation invisible to the message store, it is inspectable session
  history like any other turn, with its own token/cost accounting
  fields (seeded at `cost: 0`).
- **Overflow-specific handling.** When triggered by the reactive
  `ContextOverflowError` path (§3.3) rather than proactive `isOverflow`,
  `process()` additionally looks backward for the most recent
  replayable user message, strips media attachments from it (media is
  often the actual cause of a hard overflow), and appends a synthetic
  explanatory message telling the model the attachments were dropped
  because they were too large.
- **Hard failure, not an infinite loop.** If the summarization prompt
  itself doesn't fit under `context - summaryOutput` even after
  selection (`Token.estimate(summaryPrompt) > context - summaryOutput`
  check in the `core` engine's parallel logic; the V1 engine's
  equivalent failure path raises `SessionV1.ContextOverflowError` with
  message "Session too large to compact - context exceeds model limit
  even after stripping media" or "...too large to compact - exceeds
  model context limit" for the replay case), `processor.message.error`
  is set and the turn ends with `"stop"` -- an explicit abort,
  analogous in *purpose* (don't loop forever) to Claude Code's
  three-strikes thrash guard, but a different concrete
  mechanism (single hard-fail vs. a counted retry limit).
- **Auto-continue nudge.** If the compaction that just ran was
  triggered automatically (`input.auto`) and succeeded, a synthetic
  user message is appended -- "Continue if you have next steps, or stop
  and ask for clarification if you are unsure how to proceed" -- gated
  by a plugin hook (`experimental.compaction.autocontinue`) that a
  plugin can disable (`{ enabled: false }`).
- **Events and instrumentation.** Every stage runs as a named
  Effect-TS span (`SessionCompaction.prune`, `.process`, `.select`,
  `.estimate`) and publishes its own typed events
  (`SessionCompactionEvent`: `Started`, `Ended`, and a
  session-level `Compacted` event) -- OpenCode's own equivalent of
  Claude Code's `compact_boundary` subtype and Copilot CLI's OTel
  `gen_ai.conversation.compacted` marker, verified from source rather
  than inferred.

### 3.6 Config surface -- documented vs. actually consumed

VERIFIED discrepancy, worth stating plainly rather than smoothing over:
`opencode.ai/docs/config/` documents exactly three `compaction` keys --
`auto` (default `true`), `prune` (default `false`), and `reserved` (a
token buffer) -- with this example:

```json
{
  "compaction": {
    "auto": true,
    "prune": false,
    "reserved": 10000
  }
}
```

The live `dev`-branch schema (`packages/opencode/src/config/
compaction.ts`, a `Schema.Class` named `ConfigV1.Compaction`) confirms
`auto`, `prune`, and `reserved` are real fields, but also declares
**two more that do not appear on the docs page**: `tail_turns` and
`preserve_recent_tokens` (both consumed directly in
`compaction.ts`/`overflow.ts` as shown in §3.2/§3.5). *BEST CURRENT
UNDERSTANDING, UNCONFIRMED:* whether this is a simple documentation gap
on a fast-moving product, or whether `tail_turns`/`preserve_recent_tokens`
are considered internal/unstable and intentionally left undocumented --
no source fetched this session states either way. Do not assume the
config page's three keys are the complete tunable surface.

---

## 4. pi

Sources for this section: VERIFIED, fetched 20 August 2026 directly from
`github.com/earendil-works/pi`'s `packages/coding-agent/docs/compaction.md`, in full,
cross-referenced against `packages/coding-agent/docs/extensions.md`'s
`session_before_compact`/`session_compact`/`session_compact_failed`/`session_before_tree`
event definitions and `packages/coding-agent/docs/custom-provider.md`'s overflow-detection
section.

### 4.1 Two named mechanisms sharing one summary format, not one mechanism with two names

pi's docs draw the same eviction-vs-summarization distinction the other three harnesses
draw, but shape it around two entirely separate *triggers* rather than two phases of one
pipeline: **compaction** (fired by the context-token threshold, or manually via
`/compact [instructions]`) and **branch summarization** (fired by `/tree` navigation,
covered from the session-tree-navigation angle in
[session-persistence.md](session-persistence.md) §5.3, not repeated here). `compaction.md`
states directly that "both use the same structured summary format and track file
operations cumulatively," and both use "fresh routing session IDs" for the summarization
call itself and, "where supported by the provider, disable prompt-cache writes because
these one-off prompts are unlikely to be reused" -- a cache-hygiene detail with its own
cross-reference in [caching.md](caching.md)'s own pi section. Unlike Claude Code's single
evict-then-summarize pipeline (§1.1) or OpenCode's `prune()`/`process()` pair triggered by
one overflow check (§3.3), pi's two mechanisms are triggered by unrelated user actions
(context pressure vs. tree navigation) that happen to converge on the same output shape.

### 4.2 Trigger and cut-point selection: turn-boundary-first, with an explicit split-turn fallback

Auto-compaction triggers when `contextTokens > contextWindow - reserveTokens`, with
`reserveTokens` defaulting to **16,384** tokens (configurable in
`~/.pi/agent/settings.json` or a project's own `.pi/settings.json`) -- the same
"leave headroom for the response" shape as OpenCode's `reserved` config key (§3.2) and
Claude Code's `967K`-of-`1M` auto-compact margin (§1.3), expressed here as a flat
subtraction rather than a percentage. The cut-point search then walks backward from the
newest message, accumulating token estimates until `keepRecentTokens` (default
**20,000**, same two config locations) is reached -- a fixed-token retention budget
directly comparable to OpenCode's `preserveRecentBudget` (§3.5), though pi's default is a
flat constant rather than OpenCode's `25%-of-usable-context-clamped-to-[2000,8000]`
formula.

```mermaid
flowchart LR
    New["Newest message"] -->|"walk backward,\naccumulate tokens"| Cut{"keepRecentTokens\n(default 20,000) reached?"}
    Cut -->|"at a valid cut point\n(user/assistant/bashExecution/\ncustom message)"| Split["Normal cut: whole turns kept verbatim"]
    Cut -->|"reached mid-turn,\nno valid boundary yet"| SplitTurn["Split turn: cut lands at an\nassistant message inside one\noversized turn"]
    Split --> Summarize["Summarize everything before\nthe cut point (LLM call)"]
    SplitTurn --> TwoSummaries["Two summaries generated and merged:\nhistory summary + turn-prefix summary"]
```

**Valid cut points are user messages, assistant messages, `BashExecution` messages, and
custom messages (`custom_message`/`branch_summary`) -- never a tool result**, because a
tool result must stay paired with the tool call that produced it; this is the same
structural constraint Copilot CLI's changelog names explicitly ("background compaction
preserves tool call sequences correctly," §2.1) and OpenCode's `select()`/`splitTurn()`
enforce in source (§3.5), independently arrived at by three unrelated teams. When a
*single* turn (one user message plus everything the assistant does in response, up to
the next user message) exceeds `keepRecentTokens` on its own, pi calls this a **split
turn**: the cut lands mid-turn at an assistant message, `isSplitTurn` is set, and pi
generates *two* summaries rather than one -- a history summary (of everything before the
oversized turn, if any) and a turn-prefix summary (of the early part of the oversized
turn itself) -- then merges them into the final `CompactionEntry`. Neither of the other
three harnesses' documented or source-read compaction logic names an equivalent
two-summary merge step for a single oversized turn specifically; OpenCode's `splitTurn()`
(§3.5) instead finds a message index within the oldest-still-considered turn where the
*remaining* slice fits the leftover budget, a conceptually adjacent but mechanically
different answer to the same "one turn is too big to cut cleanly" problem.

On repeated compactions, the newly summarized span starts at the *previous* compaction's
own kept boundary (`firstKeptEntryId`), not at the compaction entry itself -- so messages
that survived an earlier compaction get folded into the next summarization pass too,
rather than being permanently exempt once kept once. pi also recalculates `tokensBefore`
from the freshly rebuilt session context immediately before writing the new
`CompactionEntry`, so the recorded pre-compaction token count reflects the actual context
being replaced at that moment, not a stale earlier estimate.

### 4.3 The summary itself: a fixed template, explicitly *not* stated to be anchored/incremental

The structured summary format is a fixed Markdown skeleton with six required sections --
**Goal**, **Constraints & Preferences**, **Progress** (with **Done**/**In Progress**/
**Blocked** subsections), **Key Decisions**, **Next Steps**, and **Critical Context** --
closed out by a `<read-files>`/`<modified-files>` pair of tagged blocks listing every file
read or modified across the summarized span. This is the same *kind* of fixed,
multi-section content model as Claude Code's six-part keeps/drops list (§1.2) and
OpenCode's six-section anchored-summary template (§3.5) -- three independently-designed
harnesses converging on "a summary is a structured document with named sections, not
free prose" as the right shape for this kind of compression. Before summarization,
messages are serialized to a fixed line-prefixed text format (`serializeConversation()`)
that renders assistant tool calls as a single terse line (`read(path="foo.ts");
edit(path="bar.ts", ...)`) rather than the full tool-call JSON, explicitly "to prevent the
model from treating it as a conversation to continue" rather than a document to
summarize; tool results are truncated to 2,000 characters during this serialization step
specifically, since `read`/`bash` tool output is named as the typical largest contributor
to a summarization request's own token budget.

One structural difference from OpenCode is worth flagging precisely, because it inverts
that harness's own finding: OpenCode's `process()` is VERIFIED anchored/incremental --
each later compaction updates the *text* of the prior compaction's own summary rather
than resummarizing from the full original history (§3.5). pi's compaction docs describe
passing "the previous summary as iterative context when present" into the generation
call, which reads as the same intent, but §4.2's own finding that "the summarized span
starts at the previous compaction's kept boundary" describes *which messages get
re-read*, not whether the summary *text itself* is edited-in-place versus regenerated
from scratch with the old summary as a reference. No source fetched this session states
which of those two the underlying LLM call actually produces -- **BEST CURRENT
UNDERSTANDING, UNCONFIRMED**: treat pi's compaction as "incremental in spirit" (the
previous summary is always supplied as context) without asserting it is mechanically
anchored in OpenCode's specific verified sense (an in-place text update rather than a
fresh generation that happens to be shown the old text).

### 4.4 Extension hooks: cancel, replace, or fully author the summary yourself

`session_before_compact` fires before either auto-compaction or `/compact` and can return
`{ cancel: true }` to abort the compaction outright, or a full replacement
`{ compaction: { summary, firstKeptEntryId, tokensBefore, usage?, details? } }` object
that pi writes verbatim instead of running its own summarization call -- the extension
receives the same `preparation` object pi's own logic would have used (`messagesToSummarize`,
`turnPrefixMessages` for a split turn, `previousSummary`, extracted `fileOps`, and the
event's own `reason` field distinguishing `"manual"` (`/compact`)/`"threshold"`/`"overflow"`
triggers, plus a `willRetry` flag for the overflow-recovery case described in §4.5). A
companion `serializeConversation`/`convertToLlm` export lets an extension reuse pi's own
message-to-text conversion to build a custom summary with a *different* model entirely
(the documented worked example runs the summarization call against a cheaper or
differently-tuned model than the session's own). A sibling `session_before_tree` hook
offers the identical cancel-or-replace contract for branch summarization specifically.
`session_compact_failed` fires on any failed or aborted compaction (manual or automatic)
and is framed explicitly as a telemetry pairing point -- matching failures back to the
`session_before_compact` attempt that produced them -- the closest pi analog to Claude
Code's `compact_boundary` `ResultMessage` subtype (§1.5) and OpenCode's typed
`Compaction.Started`/`Ended`/`Compacted` events (§3.5), though expressed as a pair of
ordinary extension events rather than a dedicated telemetry schema.

### 4.5 Overflow recovery is a *separate* code path from ordinary threshold compaction, and interacts with retries specifically

`custom-provider.md`'s own guidance for implementing a custom LLM provider names a
recovery sequence distinct from §4.2's proactive threshold check: when a request fails
because it exceeds the model's context window, pi detects the overflow from the finalized
assistant message's `stopReason === "error"` plus an `errorMessage` matching one of pi's
known overflow patterns (`packages/ai/src/utils/overflow.ts`), then (1) drops the failed
assistant message from live context, (2) runs compaction, and (3) retries the request
**once**. This is the same *kind* of reactive, error-triggered compaction path OpenCode's
`ContextOverflowError` handling implements (§3.3's "reactive" branch), but pi's docs are
explicit that this path must be kept structurally separate from ordinary transport-level
retry-with-backoff: a custom-provider author normalizing their own overflow error message
is warned specifically not to let that normalization also catch rate-limit or throttling
errors, "Rewriting rate-limit or throttling errors (`rate limit`, `too many requests`)
would falsely trigger compaction instead of pi's normal retry-with-backoff path" -- i.e.
pi maintains (per this same-session finding) two genuinely distinct recovery mechanisms
for two distinct failure classes, an architecture worth cross-referencing against
[retries.md](retries.md)'s own pi section for the retry-with-backoff half of this split,
which this page does not cover.

### 4.6 Settings surface

```json
{
  "compaction": {
    "enabled": true,
    "reserveTokens": 16384,
    "keepRecentTokens": 20000
  }
}
```

All three keys are documented directly (no OpenCode-style docs/source gap found this
session): `enabled` (default `true`, disables auto-compaction entirely when `false` --
manual `/compact` still works) and the two threshold/budget values from §4.2. Unlike
Copilot CLI's undocumented internal algorithm (§2.2) or OpenCode's two-implementation
ambiguity (§3.1), pi's own compaction implementation is singular and its full tunable
surface (per the docs fetched this session) matches what the source-level description in
`compaction.md` actually consumes -- no undocumented-but-consumed config key comparable to
OpenCode's `tail_turns`/`preserve_recent_tokens` gap (§3.6) was found in the pi docs
fetched this session, though this book has not independently cross-checked pi's own
source to rule one out the way it did for OpenCode.

---

## 5. Synthesis

| Dimension | Claude Code | Copilot CLI | OpenCode | pi |
|---|---|---|---|---|
| Verifiability | Docs-only; no public implementation | Docs + changelog only; no public implementation | Source-verified, `dev` branch (caveat applies) | Docs-only, but source-available (this session read the docs, not the TypeScript source itself, so treat as docs-verified rather than source-verified) |
| Documented shape | Two-phase: evict tool outputs, then summarize if still needed | Background, checkpointed; internal algorithm undocumented | Two *independently scheduled* mechanisms: background eviction-only `prune()` + on-demand summarizing `process()` | Two *independently triggered* mechanisms sharing one summary format: threshold/manual compaction, and `/tree`-navigation branch summarization |
| Trigger | ~967K tokens default for Sonnet 5's 1M window (`CLAUDE_CODE_AUTO_COMPACT_WINDOW`); 200K-class threshold not documented as a %; 80% warning UI | 95% of token limit (origin entry, still matches docs) | `usable(cfg, model)` = input limit minus a reserved buffer (default min(20K, max-output)); checked proactively per-turn and reactively on a provider overflow error | `contextTokens > contextWindow - reserveTokens` (default `reserveTokens` 16,384); a separate reactive overflow-error path also exists (§4.5), structurally distinct from ordinary retry-with-backoff |
| Eviction-only pass | Implicit first phase of the same mechanism ("clears older tool outputs first") | "Evicting transient events after compaction" -- a later, separate pass per changelog | Explicit separate service method (`prune()`), forked fire-and-forget every turn, own thresholds (`PRUNE_PROTECT`=40K, `PRUNE_MINIMUM`=20K), exempts `skill` tool output | None documented -- pi's only two mechanisms are the two summarization paths in the row above; no fire-and-forget eviction-only pass distinct from compaction itself was found in the docs fetched this session |
| Summarization content model | Fixed six-part list (intent, concepts, files+snippets, errors+fixes, pending tasks, current work) | Undocumented internally | Fixed six-section Markdown template (Objective, Important Details, Work State [Completed/Active/Blocked], Next Move, Relevant Files) with explicit terse-bullet/preserve-identifiers rules | Fixed six-section Markdown template (Goal, Constraints & Preferences, Progress [Done/In Progress/Blocked], Key Decisions, Next Steps, Critical Context) plus tagged `<read-files>`/`<modified-files>` blocks; shared verbatim between compaction and branch summarization |
| Incremental vs. from-scratch re-summarization | Not stated either way in docs fetched | Not stated | VERIFIED anchored/incremental: later compactions update the prior summary text rather than resummarizing full history | Docs state the previous summary is passed "as iterative context" into each new summarization call, but do not state whether the summary text itself is edited in place or freshly generated with the old text as a reference -- BEST CURRENT UNDERSTANDING, UNCONFIRMED as strictly anchored in OpenCode's specific verified sense |
| Split-turn handling | Not named as a distinct case in docs fetched | Not named as a distinct case | `splitTurn()` finds a message index within the oldest-still-considered turn where the remaining slice fits the leftover budget | Named explicitly as `isSplitTurn`; generates and merges *two* summaries (a history summary and a turn-prefix summary) rather than finding one split index -- the only harness in this book's coverage that produces two summarization calls for one oversized turn |
| Thrash/failure guard | 3-consecutive-refill circuit breaker -> actionable error | Newest entry (v1.0.76): "automatic compaction blocked" state + early warning when unreclaimable overhead nears the limit | Hard single-shot abort (`ContextOverflowError`) when the summarization prompt itself won't fit, no retry counter | Reactive overflow path retries the request exactly **once** after compacting (§4.5); no documented multi-attempt thrash counter comparable to Claude Code's three-strikes guard was found |
| Pre-compaction hook | `PreCompact`, can block (exit 2 / `{"decision":"block"}`) | `preCompact` exists; blocking capability unconfirmed | Plugin hook `experimental.session.compacting` can inject context or replace the prompt entirely; `experimental.compaction.autocontinue` gates the post-compaction nudge | `session_before_compact` extension event can cancel (`{cancel: true}`) or fully replace the compaction with a custom `{summary, firstKeptEntryId, tokensBefore, usage?, details?}` object, including one authored by an entirely different model; a sibling `session_before_tree` hook offers the identical contract for branch summarization |
| Post-compaction continuation | No documented auto-nudge; user's next message resumes naturally | Not documented | Explicit synthetic "Continue if you have next steps..." message appended when the triggering compaction was automatic | Not documented as an auto-nudge in the pages fetched this session |
| Observability marker | `compact_boundary` `ResultMessage` subtype (Agent SDK) | OTel `gen_ai.conversation.compacted=true` + `CompactionPart` | Typed events (`Compaction.Started`/`Compaction.Ended`/`Compacted`) via Effect-TS spans | `session_compact`/`session_compact_failed` extension events, explicitly framed by the docs as a telemetry-pairing point (matching a failure back to its originating attempt) rather than a dedicated schema |
| Model-fallback interaction | Won't fall back to a smaller-context model during compaction | Context-tier (200K/1M) selection "enforced end-to-end" across compaction/truncation/token display | Compaction reads the same `usable()` budget the overflow check uses; no documented model-fallback-during-compaction behavior found | Not documented; pi's overflow-recovery path (§4.5) retries on the *same* model rather than falling back to a different one, per the pages fetched this session |

**The design lesson.** All four harnesses converge on the same
two-part shape once you look past terminology -- cheap eviction of
material the model no longer needs verbatim, escalating to an LLM
re-summarization pass only when eviction alone can't free enough room
-- but they diverge on how much of that shape is actually inspectable,
and pi complicates the "eviction-then-summarization" framing slightly by
not documenting a separate eviction-only pass at all: everything this
page found for pi routes through one of its two summarization mechanisms
(compaction or branch summarization), with no OpenCode-style `prune()`
equivalent quietly trimming old tool output in the background. Claude
Code and Copilot CLI describe the *outward contract* (what categories of
content the summary keeps, what threshold fires it, what survives)
without publishing the *mechanism* that produces it; OpenCode is the one
harness where the eviction floor, the token-budget math, the literal
summarization prompt, and the anchored-vs-from-scratch question are all
directly readable in a source file rather than inferred from behavior;
pi sits between the two postures -- its own docs describe the mechanism
in genuine algorithmic detail (cut-point rules, split-turn handling, the
literal summary template, the extension-hook contract) without this
session having cross-checked that description against pi's own
TypeScript source the way it did for OpenCode, so treat pi's entries in
this table as docs-verified rather than source-verified even though the
documentation itself reads at source-level precision. That asymmetry
should shape how confidently anything gets asserted about *why* a given
harness dropped a specific piece of context: for Claude Code and Copilot
CLI, "the docs/changelog say this is what's preserved" is the ceiling of
what can honestly be claimed; for OpenCode, the actual selection and
prompt-construction logic can be cited by function name and line-level
behavior, with the standing caveat that it was read on the `dev` branch,
not a tagged release; for pi, the docs themselves already operate at
that level of detail (naming the exact settings keys, the exact section
headings, the exact extension-event shapes), which is unusual among this
book's closed-and-partially-open harnesses and worth treating as a
genuinely distinct third position on the verifiability spectrum, not
merely "docs-only" in the same sense as Claude Code's or Copilot CLI's
sections above.

---

## Sources

All fetched 2026-07-30 unless noted otherwise (memory-management.md's §1.7/§2.4
sources, and agent-loop-implementations.md's Claude-Code-SDK source, were fetched in
a prior session and are cited above by cross-reference rather than
re-fetched; §4's pi section was added 2026-08-20).

**Claude Code (authoritative for its own documented behavior only):**
- `https://code.claude.com/docs/en/context-window` -- the interactive
  context-window walkthrough's "What survives compaction" table (cited
  previously) plus, fetched fresh this session, the "What the timeline
  shows" and embedded-component summary-content description (the
  six-part keeps/drops list) and the subagent token-savings example.
- `https://code.claude.com/docs/en/how-claude-code-works` -- "When
  context fills up" section, stating the two-phase evict-then-summarize
  mechanism verbatim, and the thrash-guard cross-reference.
- `https://code.claude.com/docs/en/model-config` -- Sonnet 5's 967K
  default auto-compact threshold, `CLAUDE_CODE_AUTO_COMPACT_WINDOW`,
  the LLM-gateway and `CLAUDE_CODE_DISABLE_1M_CONTEXT` exceptions, and
  the model-fallback-vs-compaction interaction.
- `https://github.com/anthropics/claude-code` `CHANGELOG.md` (fetched in
  a prior session, cited here by reference) -- 60%->80% warning
  threshold, three-consecutive-compaction thrash guard, `PreCompact`
  blocking, extended-thinking inheritance in summarization (v2.1.198).
  Authoritative for its own behavior-change history only; this repo
  ships no implementation source.

**GitHub Copilot CLI (authoritative for its own behavior-change history
only; no implementation source exists in this repo):**
- `https://github.com/github/copilot-cli` `changelog.md`, fetched fresh
  this session via `gh api repos/github/copilot-cli/contents/
  changelog.md` (full file, 2,890 lines) -- the v0.0.334 truncation-era
  entry, v0.0.374 auto-compaction origin, v0.0.380/384/385/386/389/393/
  396/399/410 checkpoint-and-eviction sequence, v1.0.26 codex-model
  truncation fix, v1.0.52/1.0.56 context-tier enforcement, and the
  v1.0.76 (2026-07-29) blocked-compaction warning entry.
- `https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/overview`
  (fetched in a prior session, cited by reference) -- the current 95%
  auto-compaction trigger and `/compact`/`/context`/`/usage` commands.

**OpenCode (authoritative for its own documented behavior AND, unlike
the two harnesses above, its own real implementation; `dev` branch,
not a stable release tag):**
- `https://github.com/anomalyco/opencode`, `dev` branch, fetched via
  `gh api` this session -- full contents of
  `packages/opencode/src/session/compaction.ts`,
  `packages/opencode/src/session/overflow.ts`,
  `packages/opencode/src/config/compaction.ts`,
  `packages/core/src/session/compaction.ts`,
  `packages/core/src/config/compaction.ts`,
  `packages/core/src/config/tool-output.ts`, plus targeted greps of
  `packages/opencode/src/session/processor.ts` and
  `packages/opencode/src/session/prompt.ts` for the `isOverflow`/
  `prune()` call sites, and repository code-search queries confirming
  `prune()`'s only production call site and the absence of a found call
  site for `packages/core`'s `make()` factory.
- `https://opencode.ai/docs/config/`, fetched fresh this session --
  the documented `compaction.auto`/`compaction.prune`/
  `compaction.reserved` config surface, checked directly against the
  source schema to surface the `tail_turns`/`preserve_recent_tokens`
  documentation gap in §3.6.
- `https://opencode.ai/docs/` -- fetched fresh this session; confirmed
  it contains no compaction-specific content (a negative result,
  established by fetching rather than assumed).

**pi (authoritative for its own documented behavior; fetched 20 August 2026 from
`github.com/earendil-works/pi`, `main` branch; this session read the docs, not pi's own
TypeScript source, for this page specifically -- see §5's verifiability note):**
- `packages/coding-agent/docs/compaction.md` (via `gh api
  repos/earendil-works/pi/contents/packages/coding-agent/docs/compaction.md`, in full) --
  §4.1's compaction-vs-branch-summarization split and shared-format statement, §4.2's
  trigger formula, cut-point rules, and split-turn two-summary merge, §4.3's fixed
  six-section summary template and `serializeConversation()` tool-call/tool-result
  serialization behavior, §4.4's `session_before_compact`/`session_compact`/
  `session_compact_failed`/`session_before_tree` extension-event contracts, and §4.6's
  full `compaction` settings-key table.
- `packages/coding-agent/docs/custom-provider.md` (fetched the same way) -- §4.5's
  overflow-detection sequence (`stopReason === "error"` plus a recognized `errorMessage`
  pattern, drop-compact-retry-once) and its explicit warning against conflating overflow
  normalization with pi's separate retry-with-backoff path, cross-referenced against
  [retries.md](retries.md)'s own pi section.
