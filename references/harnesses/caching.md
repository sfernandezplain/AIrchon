# Prompt/context caching -- Claude Code, GitHub Copilot CLI, and OpenCode

**Scope note.** This page is about **server-side prefix reuse** -- the
mechanism that lets a provider (Anthropic, Bedrock, OpenAI, Gemini) skip
recomputing the KV-cache/attention state for a prompt prefix it has already
processed, billing the reuse at a fraction of the standard input-token
rate. It is a distinct axis from
[context-compression.md](context-compression.md) (mid-run **shrinking** of
the conversation to fit a window) and from
[memory-management.md](memory-management.md) (what instruction/memory
content gets **loaded** and when) -- a session can have a perfectly warm
cache and still need compaction, and compaction itself, as shown below, is
itself a cache-reading operation in at least one harness. Where a claim
already lives in one of those pages it is cited by cross-reference rather
than re-derived.

Every claim is tagged VERIFIED (fetched this session, or already verified
and cited in a page linked above) or BEST CURRENT UNDERSTANDING,
UNCONFIRMED. Claude Code, Copilot CLI, and OpenCode are three separate
products built on top of (in Claude Code's case, exclusively) or across (in
Copilot CLI's and OpenCode's case) multiple model providers -- nothing
confirmed for one harness, or for the underlying Anthropic/Bedrock API
mechanism itself, is assumed to hold for another harness without its own
citation.

---

## 1. Claude Code

Primary source: `code.claude.com/docs/en/prompt-caching`, fetched fresh
this session (2026-07-30) -- a dedicated page devoted entirely to this
mechanism, cross-referenced against `code.claude.com/docs/en/costs`
(also fetched fresh this session) and `github.com/anthropics/claude-code`
`CHANGELOG.md` (fetched fresh this session for this page, superseding the
partial reads cited in earlier pages). VERIFIED unless tagged otherwise.

### 1.1 The mechanism: exact prefix matching over a growing request

Claude Code re-sends the entire conversation on every turn -- there is no
server-side session state the model "remembers" between requests. What
prompt caching does is let the API recognize that most of a new request is
byte-identical to the previous one and skip reprocessing that shared
**prefix**. The docs state the matching rule precisely: "The match is
exact, so a change anywhere in the prefix recomputes everything after it.
There is no per-file or per-segment caching." This is a single linear
prefix match, not a content-addressed cache keyed by individual files or
messages -- a change to anything before a given point invalidates
everything after it, regardless of whether that later content itself
changed.

To maximize how much of each request stays behind a stable prefix, Claude
Code orders the request into three layers, least-volatile first:

| Layer | Content | Changes when |
|---|---|---|
| System prompt | Core instructions, tool definitions, output style | The set of loaded tool definitions changes, or Claude Code is upgraded |
| Project context | CLAUDE.md, auto memory, unscoped rules | Session starts, or after `/clear` or `/compact` |
| Conversation | Messages, responses, tool results | Every turn |

Two settings sit outside the prompt text entirely but are still part of
the cache key: **model** (each model has its own cache -- switching with
`/model` recomputes the entire request with zero cache hits even though
the content is identical) and **effort level** (also independently keyed;
Claude Code shows a confirmation dialog before an effort change that would
invalidate the cache, but skips it when the change resolves to the level
already in effect).

### 1.2 What invalidates the cache -- and what doesn't

```mermaid
flowchart TD
    subgraph Invalidates["Invalidates the cache"]
        M1["Switching models (/model, opusplan toggle,\nautomatic model fallback)"]
        M2["Changing effort level"]
        M3["Turning on fast mode (first turn only)"]
        M4["MCP server connect/disconnect\n(only if tools load into the prefix,\ni.e. tool search unavailable/disabled)"]
        M5["Enabling/disabling a plugin that bundles\nan MCP server (same rule as M4)"]
        M6["Denying an entire tool by bare name\n(e.g. Bash, WebFetch, wildcard glob)"]
        M7["Compacting the conversation (/compact,\nauto-compact)"]
        M8["Upgrading Claude Code (new system prompt/tools)"]
    end
    subgraph Keeps["Keeps the cache"]
        K1["Editing repo files (appends a system-reminder)"]
        K2["Editing CLAUDE.md mid-session\n(doesn't apply until next /clear or restart)"]
        K3["Changing output style mid-session\n(same deferred-apply pattern)"]
        K4["Changing permission mode"]
        K5["Invoking skills/commands\n(appended as user messages)"]
        K6["/recap (appends display output only)"]
        K7["/rewind (truncates to an\nalready-cached earlier prefix)"]
        K8["Spawning a subagent\n(parent's prefix untouched)"]
    end
```

Most listed behaviors reduce to the single prefix-match rule in §1.1.
Content that is **appended** after the existing conversation -- skill and
command instructions, plan-mode text, a subagent's returned result --
leaves everything before it cache-hit-eligible, which is why plan mode and
skill loading are explicitly called out in the docs as not disturbing the
cached prefix. Content that changes the **system-prompt or tool-definition
layer** invalidates everything downstream of it, because all later content
now sits behind a different prefix.

Two invalidation triggers deserve their own note because they are easy to
trigger unintentionally mid-session:

- **MCP server connect/disconnect.** Whether this invalidates the cache
  depends entirely on whether that server's tools are **deferred** (the
  default on supported models, via [tool search](mcp-integration.md)) or
  **loaded into the prefix**. Deferred tools only append new content when
  a server connects, so no invalidation. Tools loaded into the prefix --
  which happens when tool search is unavailable/disabled (Google Cloud's
  Agent Platform, a custom `ANTHROPIC_BASE_URL` gateway, or an Azure-hosted
  Microsoft Foundry deployment once Claude Code detects the deployment
  rejects tool search), when a server or tool is marked `alwaysLoad`, or
  under threshold-based loading -- invalidate on any change to that tool
  list. The docs flag that this can happen with **no action from the
  user**: a stdio server's process exiting, an HTTP session expiring, or an
  automatic reconnection after a transient failure all change the tool set
  mid-session.
- **Compacting the conversation.** By design this replaces message history
  with a summary, so the conversation layer's prefix is gone -- but the
  system-prompt layer is reused and project context is reloaded from disk
  (cache-hitting only if CLAUDE.md/memory are unchanged since session
  start). Critically, the summarization request itself is a normal API call
  built from the same system prompt, tools, and history as the live
  conversation plus an appended summarization instruction -- so **while the
  cache is warm, `/compact` reads that prefix from cache and costs a
  fraction of what the context size suggests.** Only after a break longer
  than the cache lifetime (§1.3) does a `/compact` reprocess the full
  history as uncached input -- which the docs state explicitly is why
  `/compact` is most expensive when resuming an old session. This is a
  concrete mechanism-level detail this page adds to
  [context-compression.md](context-compression.md) §1: compaction's own
  cost is itself gated by cache state, not a fixed cost proportional to
  context size.

`/rewind` (see checkpointing) is called out as cache-favorable specifically
*because* it truncates back to a prefix that was already cached at that
point, rather than -- like compaction -- building a new, shorter prefix
from scratch: "Rewinding truncates back to a prefix that is already
cached, rather than building a new one as compaction does."

### 1.3 Cache lifetime (TTL) and where the cache physically lives

The underlying Anthropic API offers two TTLs, and Claude Code selects
between them automatically based on how the session authenticates:

- **Claude subscription (Pro/Max/Team/Enterprise):** requests the
  **one-hour TTL** automatically, so the cache survives breaks of up to an
  hour. If the session has gone over its plan usage limit and is drawing on
  usage credits, Claude Code is billed for that usage, and since cache
  writes cost more at the one-hour TTL, it **automatically drops to the
  five-minute TTL** in that state.
- **API key, Amazon Bedrock, Google Cloud's Agent Platform, Microsoft
  Foundry, or Claude Platform on AWS:** the TTL defaults to the cheaper
  **five minutes**, since usage is billed per token. Setting
  `ENABLE_PROMPT_CACHING_1H=1` opts into the one-hour TTL on these paths.
- **Override:** `FORCE_PROMPT_CACHING_5M=1` forces five minutes regardless
  of authentication -- useful for debugging cache behavior or overriding an
  `ENABLE_PROMPT_CACHING_1H` set in managed settings.
- On Amazon Bedrock specifically, prompt-caching support, minimum
  cacheable prefix length, and one-hour-TTL availability all **vary by
  model** -- the docs point to AWS's own supported-models/regions/limits
  page if cache token counts stay at zero.

Each cache-hitting request resets the TTL timer, so a session stays warm
indefinitely as long as requests keep arriving within the window; only a
gap longer than the TTL forces a full, uncached reprocess on the next
turn. Where the cache **physically lives** depends on the same
authentication path: Anthropic's own infrastructure for API-key/
subscription/Claude-Platform-on-AWS traffic, the cloud provider's own
serving infrastructure for Bedrock/Google Cloud's Agent Platform, and
either Azure or Anthropic infrastructure for Microsoft Foundry depending on
its hosting option. A custom `ANTHROPIC_BASE_URL` or LLM gateway forwards
the cache-control marker along, but whether it actually takes effect
depends on that gateway -- and if the gateway rejects the breakpoint marker
outright, {/* per docs */} Claude Code retries the request without it and
leaves that block permanently uncached for the rest of the conversation.
As of v2.1.211 (per `CHANGELOG.md`), mid-conversation system context that
Claude Code appends (e.g. file-change notices) is cached the same way on
Bedrock/its Mantle endpoint, Google Cloud's Agent Platform, and Microsoft
Foundry as it is on the Claude API; before that version these providers
billed that appended block as uncached input on every request -- a
regression separately confirmed in the changelog: "Fixed a prompt-caching
regression on Bedrock, Vertex, Mantle, and Foundry that billed the
trailing system context block as fresh input tokens on every request."

### 1.4 Cache scope: effectively one machine, one directory

The docs state plainly that "the cache is effectively scoped to one
machine and directory." The system prompt embeds the working directory,
platform, shell, OS version, and auto-memory paths, so two sessions in
different directories -- including different **worktrees of the same
repository** -- build different prefixes and never share a cache entry.
Parallel sessions in the *same* directory build matching prefixes and do
share the cache; sequential sessions share it only if the git-status
snapshot captured at startup (branch, recent commits) still matches. The
underlying API cache is broader than this -- caches are isolated between
organizations, and on some providers between workspaces within an
organization -- but within those boundaries, any two requests with the
same model and prefix hit the same server-side entry. For Agent SDK
callers running a fleet of automated processes across many machines, the
docs point to a separate mechanism (suppressing the per-machine sections of
the system prompt) to let unrelated processes share a cache -- flagged here
as an SDK-specific lever, not a CLI-default behavior.

### 1.5 Subagents and forks: separate caches, one exception

A [subagent](handoff-mechanism.md) starts an entirely separate
conversation with its own system prompt and tool set, so it builds its own
cache from zero hits on its first call. Subagents use the five-minute TTL
**even on a subscription** -- the docs state the automatic one-hour TTL is
specific to the main conversation. The parent's own cache is unaffected;
from the parent's perspective, the subagent's call and returned result are
just appended content. A **fork** (see
[handoff-mechanism.md](handoff-mechanism.md)), by contrast, inherits the
parent's system prompt, tools, and full conversation history exactly, so
its very first request reads the parent's cache -- and the docs note the
compaction summarization call (§1.2) uses this same prefix-sharing
approach.

Separately, `CHANGELOG.md` records a fix specifically for subagent
progress-summary requests missing the cache entirely (a roughly 3x
reduction in `cache_creation` tokens once fixed) -- evidence that even
within a single harness, different internal request types (a subagent's
main turns vs. its progress-summary side-channel) can silently diverge in
whether they hit the shared prefix, until caught and fixed.

### 1.6 Observability: the two token fields, `/usage`, and OpenTelemetry

Every API response reports two fields that make cache performance directly
measurable:

| Field | Meaning |
|---|---|
| `cache_creation_input_tokens` | Tokens written to the cache this turn, billed at the cache-write rate |
| `cache_read_input_tokens` | Tokens served from cache this turn, billed at roughly 10% of the standard input rate |

The docs frame the diagnostic directly: "A high read-to-creation ratio
means caching is working well. If creation stays high turn after turn,
something is changing in your prefix" -- pointing back at §1.2's
invalidation list as the usual cause. `/usage`'s Session block shows this
per-model, e.g. `claude-sonnet-4-6: 1.2k input, 5.3k output, 940.0k cache
read, 50.0k cache write ($0.55)` (verified, `costs` page). On a
Pro/Max/Team/Enterprise plan, `/usage`'s breakdown additionally **flags**
cache misses specifically when they account for 10% or more of recent
usage, alongside a tip to reduce them (cited, `costs` page §"Using the
`/usage` command"). A statusline script reading the `current_usage` object
is the docs' suggested way to watch these fields live, and the
OpenTelemetry exporter reports cache-read and cache-creation tokens
per-user and per-session for organization-wide visibility. `CHANGELOG.md`
adds two dated observability fixes worth flagging as historical
gotchas rather than current bugs: `cache_creation_input_tokens` at one
point reported as `0` when the API reported cache writes only via a nested
`cache_creation` breakdown object (fixed), and `/cost` gained a
per-model-and-cache-hit breakdown for subscription users as a distinct,
later addition.

### 1.7 Why usage climbs in a long session -- caching's cost-side implication

[costs page, cross-referenced] explicitly names prompt caching as one of
the reasons a long-idle session's usage looks disproportionate to recent
activity: "Claude Code re-reads that history at the cached token rate, so
a one-line question in a session that has been open all day still draws
usage for the whole conversation" -- and separately, "your first message
after a break longer than the cache lifetime misses the cache and
reprocesses your full context." On Pro/Max, resuming a large session after
a long break triggers Claude Code's own mitigation: it offers to [resume
from a summary](memory-management.md) so the following requests don't
carry the full uncached history. `CHANGELOG.md` records a targeted nudge
in the same spirit -- v(unspecified, changelog-dated) added "an idle-return
prompt that nudges users returning after 75+ minutes to `/clear`, reducing
unnecessary token re-caching on stale sessions."

### 1.8 Disabling caching and org-wide policy

Six environment variables, settable per-user or in the `env` block of
managed settings for an organization-wide policy:

| Variable | Effect |
|---|---|
| `DISABLE_PROMPT_CACHING` | Disable for all models |
| `DISABLE_PROMPT_CACHING_HAIKU` | Disable for Haiku only |
| `DISABLE_PROMPT_CACHING_SONNET` | Disable for Sonnet only |
| `DISABLE_PROMPT_CACHING_OPUS` | Disable for Opus only |
| `DISABLE_PROMPT_CACHING_FABLE` | Disable for Fable only |
| `ENABLE_PROMPT_CACHING_1H` / `FORCE_PROMPT_CACHING_5M` | TTL override, §1.3 |

`CHANGELOG.md` records a startup warning added when any
`DISABLE_PROMPT_CACHING*` variable is set, and a fix for a related
interaction bug: subscribers who set `DISABLE_TELEMETRY` used to fall back
to the five-minute TTL instead of the subscription's one-hour default
(fixed). `ENABLE_PROMPT_CACHING_1H_BEDROCK` is called out in the changelog
as deprecated but still honored, superseded by the provider-agnostic
`ENABLE_PROMPT_CACHING_1H`. `--exclude-dynamic-system-prompt-sections`
(print-mode flag, per changelog) exists specifically "for improved
cross-user prompt caching" -- stripping per-user/per-machine dynamic
sections so unrelated automated processes on different machines can still
share a cache entry, the CLI-flag counterpart to the SDK-level mechanism
noted in §1.4.

### 1.9 The underlying Anthropic API mechanism (bounded citation)

The Claude Code docs repeatedly point to
`platform.claude.com/docs/en/build-with-claude/prompt-caching` for "the
underlying API mechanism, breakpoints, and pricing" rather than restating
it -- fetched fresh this session, this page is authoritative for the raw
Anthropic Messages API feature that Claude Code (and, independently,
OpenCode's Anthropic protocol adapter, §3.2) both sit on top of, **not**
for Claude-Code-specific behavior, which stays scoped to §1.1-1.8 above.
The mechanism it documents: up to **4 explicit `cache_control` breakpoints**
per request (or one automatic top-level breakpoint that places itself on
the last cacheable block); `"ephemeral"` is currently the only cache type;
a **5-minute TTL** at a 1.25x base-input write cost and 0.1x base-input
read cost, or a **1-hour TTL** (`"ttl": "1h"`) at a 2x write cost with the
same 0.1x read cost; a per-model **minimum cacheable prompt length**
ranging from 512 tokens (Opus 5, Fable 5, Mythos 5) up to 4,096 tokens
(Opus 4.6/4.5, Haiku 3.5/4.5) -- prompts below the minimum are processed
without caching and without an error; cache hits require exact,
byte-for-byte matches of every block up to and including the marked one;
and a documented **20-block lookback window**, meaning a cache read walks
backward from the current breakpoint checking at most 20 prior positions
for a matching entry before giving up, which is why a single trailing
breakpoint stops working once a conversation grows past that window and a
second, earlier breakpoint is needed to keep the older prefix reachable.
Cache invalidation follows a stated **hierarchy, tools -> system ->
messages**: a change at any level invalidates that level and everything
after it, but never anything before it (e.g. toggling web search
invalidates the tools cache but leaves system/messages caches intact).
None of this 4-breakpoint/20-block/hierarchy detail is Claude-Code-specific
prose on the `code.claude.com` pages themselves -- it is cited here from
the Anthropic API page specifically because Claude Code's own docs assume
it as background rather than re-explaining it.

---

## 2. GitHub Copilot CLI

Sources: `docs.github.com/en/enterprise-cloud@latest/copilot/tutorials/
optimize-ai-usage` (fetched fresh this session, 2026-07-30) and
`github.com/github/copilot-cli` `changelog.md` (fetched fresh this session
via `gh api repos/github/copilot-cli/contents/changelog.md`, full 2,898-line
file). VERIFIED unless tagged otherwise. Copilot CLI is closed source --
everything below is inferred from documented behavior and the product's
own changelog, never from an implementation file, the same standing
caveat as [context-compression.md](context-compression.md) §2.

### 2.1 What the docs say the mechanism is

The "Optimizing your AI usage" tutorial states the underlying rationale in
agentic-coding terms directly comparable to Claude Code's own framing:
"the same large context -- system prompt, file contents, tool definitions
-- is sent repeatedly across many turns," and caching lets the model
"store portions of a conversation's context so they don't need to be
reprocessed on every request." Cached tokens are "typically billed at 10%
of the normal input price" -- the same 0.1x multiplier the Anthropic API
documents for its own cache reads (§1.9), though the Copilot CLI page does
not attribute this figure to any specific underlying provider, since
Copilot CLI routes across multiple model families (GPT, Claude, Gemini,
and BYOK/BYOM providers per [built-in-tools.md](built-in-tools.md)).

### 2.2 Cache lifetime: a documented, provider-differentiated TTL

VERIFIED, same page: caches expire "after periods of inactivity -- **24
hours for OpenAI models and 1 hour for most others**." This is a
concretely different TTL structure from both Claude Code (5 minutes/1
hour, chosen by authentication path, §1.3) and the raw Anthropic API
(5 minutes/1 hour, chosen by an explicit `ttl` parameter, §1.9) -- Copilot
CLI's 24-hour figure for OpenAI models has no analog in either of those,
consistent with OpenAI's own implicit prompt-caching mechanism (server-side,
automatic above a token threshold, no client-side breakpoint marker
required) being a genuinely different design from Anthropic/Bedrock's
explicit-breakpoint model. This page does not state what "most others"
covers beyond implying non-OpenAI models default to the shorter window.

### 2.3 What invalidates the cache

The same page names three triggers, structurally close to Claude Code's
list (§1.2) but stated at a coarser grain, without Claude Code's
layer-by-layer breakdown:

1. **Model switching**: "A different model can't reuse another model's
   cache, so the next request rebuilds it from scratch" -- the same
   model-is-part-of-the-cache-key rule as §1.1.
2. **Session inactivity** past the TTL in §2.2.
3. **Configuration changes**: "reasoning effort level, context size, or
   the set of enabled tools and MCP servers during a session invalidates
   the cache" -- context size here plausibly refers to the [context-tier
   selection](context-compression.md) (200K vs. 1M) mechanism documented
   for compaction/truncation in that page; this document did not find a
   source stating explicitly that tier selection and cache invalidation
   share the same enforcement path, so treat that specific link as **BEST
   CURRENT UNDERSTANDING, UNCONFIRMED** even though both are named on the
   same page.

A documented mitigation: Copilot CLI's **auto model selection** feature
"protects your cache" by only switching models "at natural cache
boundaries, when a new session starts or after you run `/compact`, never
mid-task" -- an explicit design choice to avoid the exact mid-task
model-switch cache miss that Claude Code's docs warn about for manual
`/model` switches (§1.1), applied here to an *automatic* selection feature
specifically so it can't silently trigger the same cost spike.

### 2.4 Changelog-traced evolution of cache observability

```mermaid
stateDiagram-v2
    state "v0.0.359 (2025-11-17)<br/>Cached-tokens-zero bug" as Era1
    state "v1.0.x era<br/>/usage shows cache write + read" as Era2
    state "v1.0.x era<br/>Cache-write pricing shown for omitted models" as Era3
    state "Later entry<br/>OTel GenAI cache attributes corrected" as Era4
    state "Later entry<br/>Input usage totals include cached tokens" as Era5

    Era1 --> Era2: from a display bug to a real breakdown
    Era2 --> Era3: pricing visibility catches up to token visibility
    Era3 --> Era4: machine-readable telemetry gets the same fields
    Era4 --> Era5: accounting consistency fix
```

Reading the changelog oldest-to-newest (it is itself newest-first) shows
cache **observability** maturing as a distinct thread from the caching
mechanism itself, which the changelog never describes in mechanism-level
terms (no breakpoint count, no explicit TTL-parameter equivalent to
Anthropic's `ttl: "1h"`, is ever named):

- **v0.0.359 (2025-11-17).** "Fix a bug where cached tokens were displaying
  as zero at the end of the session" -- the earliest cache-related entry
  found, evidence the feature (or at least its accounting) predates this
  changelog window and was already being actively debugged.
- **(undated in this excerpt, later).** "Show cache write tokens alongside
  cache read tokens in /usage display" -- the CLI's `/usage` surface gains
  the read/write pair, the same two-field breakdown Claude Code's `/usage`
  shows (§1.6).
- **(undated, later still).** "Display cache-write pricing for models that
  omit it" -- a gap-filling fix implying some models' pricing metadata
  didn't originally carry a cache-write rate at all.
- **(undated, later).** "OpenTelemetry GenAI spans now emit
  `gen_ai.usage.cache_read.input_tokens`, `gen_ai.usage.cache_creation.
  input_tokens`, and `gen_ai.usage.reasoning.output_tokens` per the GenAI
  semantic conventions spec (previously used incorrect underscore-separated
  names)" -- a naming-convention correction, not a new capability, but it
  fixes the OTel field names to match the spec Claude Code's own OTel
  export presumably targets too (not independently re-verified against
  Claude Code's own OTel schema this session -- flagged rather than
  assumed identical).
- **(undated, later).** "Ensure input token usage includes cached, update
  token formatting to clarify" -- an accounting-correctness fix, the same
  category of bug as Claude Code's `cache_creation_input_tokens` reporting
  `0` fix (§1.6): both harnesses independently had to patch a case where a
  cache-related token count didn't roll up correctly into a displayed
  total.
- Two further entries confirm cache state is treated as something that
  must **survive** specific operations rather than being casually rebuilt:
  "Resumed sessions reproduce the original attached-file references even
  if those files later change on disk, avoiding prompt-cache resets," and
  a note that custom-agent instructions "are no longer duplicated each
  turn, reducing context window usage" (a token-bloat fix adjacent to, but
  not stated as, a caching fix specifically).

### 2.5 What is not documented

No page or changelog entry fetched this session states Copilot CLI's
equivalent of Anthropic's explicit `cache_control` breakpoint mechanism, a
breakpoint count cap, a lookback-window figure, or per-provider minimum
cacheable-token thresholds. Given that Copilot CLI is a multi-provider
harness (per [built-in-tools.md](built-in-tools.md), routing across GPT,
Claude, Gemini, and BYOK/BYOM models), it is plausible the CLI delegates to
each provider's own native caching behavior (explicit breakpoints on
Anthropic-family models it routes to, implicit server-side caching on
OpenAI/Gemini-family models) the same way OpenCode's `packages/llm`
explicitly branches on provider (§3.2-3.3) -- but this is **BEST CURRENT
UNDERSTANDING, UNCONFIRMED**: no Copilot CLI source is public to verify it
the way OpenCode's is, and no docs page states the provider-dispatch logic
explicitly. Treat it as a plausible architectural inference, not a
confirmed fact.

---

## 3. OpenCode

Source: `github.com/anomalyco/opencode`, `dev` branch, fetched live via
`gh search code` and `gh api` this session (2026-07-30) -- flagging per
this project's standing caveat that `dev` is not a stable release tag and
this code may not reflect the current stable release. Unlike Claude Code
and Copilot CLI, this harness's caching logic is not inferred from
documentation at all in this section -- `opencode.ai/docs/providers/` and
`opencode.ai/docs/config/` were both fetched fresh this session and
**confirmed to contain no mention of prompt caching, `cache_control`,
cache breakpoints, or a `cache` configuration key** (a checked negative
result, not an assumption) -- so everything below comes from
`packages/llm`, the one package in this repository dedicated to the
provider-facing LLM request/response contract.

### 3.1 `cache-policy.ts`: a protocol-neutral policy resolved before lowering

VERIFIED, `packages/llm/src/cache-policy.ts`. Every outbound `LLMRequest`
carries an optional `cache` field of type `CachePolicy` --
`"auto" | "none" | CachePolicyObject` -- resolved once, before the
per-protocol request-body builder runs:

```mermaid
flowchart TD
    Req["LLMRequest.cache field"] --> Resolve{"resolve(policy)"}
    Resolve -->|undefined or 'auto'| Auto["AUTO: { tools: true, system: true,\nmessages: 'latest-user-message' }"]
    Resolve -->|'none'| None["NONE: {} (no auto placement)"]
    Resolve -->|object form| Custom["exactly what the caller specified"]
    Auto --> Gate{"request.model.route.id in\nRESPECTS_INLINE_HINTS?\n(anthropic-messages, bedrock-converse)"}
    None --> Gate
    Custom --> Gate
    Gate -->|No: OpenAI, Gemini| NoOp["No-op -- provider does\nimplicit server-side caching"]
    Gate -->|Yes| Mark["markLastTool() / markLastSystem() /\nmarkMessages() inject CacheHints"]
    Mark --> Lower["Per-protocol lowering emits the\nwire-format marker (cache_control / cachePoint)"]
```

The default (`undefined` or `"auto"`) resolves to
`{ tools: true, system: true, messages: "latest-user-message" }` -- three
breakpoints placed at the **last tool definition**, the **last system
part**, and the **latest user message**. The source comment states the
rationale for the third breakpoint's position directly: "in a tool-use
loop, a single user turn expands into many assistant/tool round-trips, all
sharing that prefix. Caching at that boundary lets every intra-turn API
call hit." This is a materially different framing from Claude Code's
documented layer table (§1.1), which treats the whole conversation as one
growing layer -- OpenCode's `packages/llm` instead explicitly optimizes for
the *sub-turn* structure of a single tool-use loop, anchoring one
breakpoint at the most recent user message specifically so every
subsequent assistant/tool-result exchange within that same turn reads the
same cached prefix rather than only benefiting cache hits turn-to-turn.

The package's own README states the justification in the same terms
Claude Code's docs use independently: "the math justifies the default:
Anthropic's 5-minute cache write is 1.25x base, read is 0.1x, so a single
reuse within 5 minutes already wins" -- the identical pricing figures
verified from the Anthropic API docs in §1.9, cited here as a second,
independent confirmation of those multipliers from a different vantage
point (an implementer's own justifying comment, not just the API's own
pricing page).

`resolve()` is additive, not destructive: a manual `CacheHint` placed on
any individual text/system/tool/tool-result part is preserved through auto
placement -- `markLastTool`/`markLastSystem`/`markMessageAt` each check
`if (existing.cache) return` before writing, so "auto" only **fills gaps**
the caller left empty rather than overwriting explicit choices.

Granular override is available as the object form of `CachePolicy`:
`{ tools?: boolean, system?: boolean, messages?: "latest-user-message" |
"latest-assistant" | { tail: number } }`, plus an independent `ttlSeconds`
override. A one-off completion can opt out entirely with `cache: "none"`
-- the README notes the worst case of leaving auto on for a single-shot
call is harmless, since "one-shot completions below the per-model
minimum-cacheable-token threshold silently no-op on the wire."

### 3.2 Per-protocol lowering: Anthropic Messages and Bedrock Converse

VERIFIED, `packages/llm/src/protocols/anthropic-messages.ts` and
`packages/llm/src/protocols/utils/bedrock-cache.ts` (with shared TTL logic
in `packages/llm/src/protocols/utils/cache.ts`). Both protocols enforce a
hard-coded **4-breakpoint cap per request**
(`ANTHROPIC_BREAKPOINT_CAP` / `BEDROCK_BREAKPOINT_CAP = 4`) -- matching the
Anthropic API's own documented cap in §1.9 exactly, and confirmed in
source comments as a deliberate mirror of the wire-level 400-error limit:
"Anthropic accepts at most 4 explicit `cache_control` breakpoints per
request... Beyond the cap the API returns a 400 -- so the lowering layer
counts emitted markers and silently drops any that exceed it." A shared
`Breakpoints` counter (`{ remaining, dropped }`) threads through the whole
request-lowering pass; when it hits zero, further requested cache markers
are dropped rather than sent, and a dropped count is logged as a warning:
"dropped N cache breakpoint(s); the API allows at most 4 per request."

The budget is allocated in a stated invalidation-hierarchy order -- **tools
-> system -> messages** -- matching the Anthropic API's own documented
hierarchy (§1.9): a source comment states the reasoning explicitly, "Tools
live highest in the cache hierarchy, so when callers over-mark we keep
their tool hints and shed the message-tail ones first." TTL is bucketed by
a shared helper, `ttlBucket(ttlSeconds)`, which returns `"1h"` for any
`ttlSeconds >= 3600` and otherwise `undefined` (meaning the provider's
5-minute default) -- both Anthropic Messages (`EPHEMERAL_1H = { type:
"ephemeral", ttl: "1h" }`) and Bedrock Converse
(`cachePoint: { type: "default", ttl: "1h" }`) apply this identically,
confirmed as one shared function rather than two independently-maintained
thresholds. Bedrock's marker is positional (a `cachePoint` block emitted
immediately after the content to be cached) rather than an attribute on
the content block itself the way Anthropic's `cache_control` field is --
a real wire-format difference the shared `Breakpoints` counter and
`ttlBucket` helper abstract away from the caller.

One schema detail flagged rather than resolved: `CacheHint`'s `type` field
is a union of `"ephemeral"` **and** `"persistent"`
(`packages/llm/src/schema/options.ts`), but both lowering functions
(`cacheControl` in `anthropic-messages.ts`, `block` in
`bedrock-cache.ts`) treat the two identically -- `if (cache?.type !==
"ephemeral" && cache?.type !== "persistent") return undefined` -- with no
branch that changes the emitted wire marker or TTL behavior based on which
value was set. *BEST CURRENT UNDERSTANDING, UNCONFIRMED:* whether
`"persistent"` is a forward-looking schema placeholder for a future
non-ephemeral cache type Anthropic/Bedrock don't yet expose, dead code, or
consumed differently somewhere not searched this session -- no source
fetched this session distinguishes the two at the point where the wire
request is actually built.

### 3.3 OpenAI and Gemini: a deliberate no-op

VERIFIED, `cache-policy.ts`:
`RESPECTS_INLINE_HINTS = Set(["anthropic-messages", "bedrock-converse"])`.
`applyCachePolicy()`'s very first line is
`if (!RESPECTS_INLINE_HINTS.has(request.model.route.id)) return request`
-- for every other protocol, the entire cache-policy pass is skipped
outright rather than emitting a marker that would be ignored. The source
comment names the reason: "Protocols whose wire format ignores inline
cache markers (OpenAI's implicit prefix caching, Gemini's implicit +
out-of-band `CachedContent`). Skip the whole policy pass for these --
emitting hints would be harmless but pointless." The package README states
the same split as a one-line provider-behavior table: OpenAI Chat/
Responses do "implicit caching above 1024 tokens" and Gemini does
"implicit caching on 2.5+; explicit `CachedContent` is out-of-band" -- both
no-ops from `cache: "auto"`'s perspective, confirming OpenCode's own
architecture treats explicit-breakpoint caching (Anthropic/Bedrock) and
implicit automatic caching (OpenAI/Gemini) as two fundamentally different
mechanisms it does not try to unify at the request-construction level,
only at the response-accounting level (§3.4).

### 3.4 Normalized token accounting across providers

VERIFIED, `anthropic-messages.ts` `mapUsage`/`mergeUsage`. Anthropic
reports usage as `input_tokens` (the API's own *non-cached* count),
`cache_creation_input_tokens`, and `cache_read_input_tokens` as separate
fields, streamed incrementally (`message_start` then a final,
authoritative `message_delta`). OpenCode sums these into one inclusive
`inputTokens` figure for its own internal `Usage` type, while separately
preserving the breakdown as `nonCachedInputTokens`, `cacheReadInputTokens`,
and `cacheWriteInputTokens` -- the README states this normalization is
provider-wide: "Normalized cache usage is read back into
`response.usage.cacheReadInputTokens` and `cacheWriteInputTokens` across
every provider." This is the mechanism referenced in
[context-compression.md](context-compression.md) §3.2's overflow-detection
formula (`tokens.total || input+output+cache.read+cache.write`) -- the
compaction-trigger token count and the caching subsystem's own accounting
draw from the same normalized `Usage` fields, source-confirmed here as the
same object rather than two independently-computed totals.

### 3.5 Config surface: none -- this is a programmatic, not user-facing, knob

A discrepancy worth stating as plainly as
[context-compression.md](context-compression.md) §3.6 states its own:
`opencode.ai/docs/providers/` and `opencode.ai/docs/config/` were both
checked this session and **neither documents a user-facing `cache`
configuration key at all**. Unlike `compaction.auto`/`compaction.prune`/
`compaction.reserved`, which are documented (if incompletely) on the
config page, prompt caching in OpenCode appears to be entirely a
programmatic `LLMRequest.cache` field -- set (or left at its `"auto"`
default) by whatever code constructs the request, not something a user
configures in `opencode.json`/`opencode.jsonc`. *BEST CURRENT
UNDERSTANDING, UNCONFIRMED:* this session did not find a call site in
`packages/opencode` that reads a user-facing config value into
`LLMRequest.cache` for ordinary session turns, so whether an end user has
any documented lever to influence caching at all (short of an unlisted
`providerOptions` escape hatch, per the README's three-tier
generation/providerOptions/http override system) is not confirmed either
way from what was searched this session.

---

## 4. pi (`@earendil-works/pi-ai`)

VERIFIED, fetched 1 September 2026 directly from `github.com/earendil-works/pi`, `main`
branch. **A naming clarification this section resolves rather than repeats.** This
repository is a monorepo publishing (at minimum) two separate npm packages under the
`@earendil-works` scope, confirmed from each package's own `package.json` fetched this
session: `packages/ai` publishes `@earendil-works/pi-ai` ("Unified LLM API with automatic
model discovery and provider configuration") -- the provider-abstraction layer this page's
caching mechanics live in, and the same package [llm-api-contract.md](llm-api-contract.md)
§3.5 and [auth-and-usage-accounting.md](auth-and-usage-accounting.md) document from their
own angles -- while `packages/coding-agent` publishes `@earendil-works/pi-coding-agent`
("Coding agent CLI with read, bash, edit, write tools and session management"), the harness
itself, which declares `@earendil-works/pi-ai` as an ordinary version-pinned dependency
(`"@earendil-works/pi-ai": "^0.84.4"` in `packages/coding-agent/package.json`, read this
session). Both spellings this book uses elsewhere (`pi-ai` in
[llm-api-contract.md](llm-api-contract.md)/[auth-and-usage-accounting.md](auth-and-usage-accounting.md)
and `pi-coding-agent` in
[deterministic-orchestration.md](deterministic-orchestration.md)/[session-persistence.md](session-persistence.md))
are independently correct package names for two different, real npm packages in this one
repository -- not an inconsistency to fix, since each citing page names the package
actually relevant to its own topic. This section's own subject -- caching mechanics -- is
`@earendil-works/pi-ai`'s, read directly from `packages/ai/src/api/anthropic-messages.ts`,
`openai-responses.ts`, `openai-completions.ts`, `bedrock-converse-stream.ts`,
`google-generative-ai.ts`, `google-vertex.ts`, `google-shared.ts`, `types.ts`, and
`openai-prompt-cache.ts` (full files, read this session), cross-referenced against
`packages/ai/README.md` and, for the CLI-facing configuration surface,
`packages/coding-agent/docs/models.md`, `providers.md`, `environment-variables.md`,
`settings.md`, `compaction.md`, and `packages/coding-agent/src/core/compaction/compaction.ts`.

### 4.1 `CachePolicy`: one `CacheRetention` enum, one resolver function, copied into four protocols

VERIFIED, `packages/ai/src/types.ts` line 108: `export type CacheRetention = "none" | "short"
| "long"`, documented inline as "Prompt cache retention preference. Providers map this to
their supported values. Default: `short`." Every `StreamOptions`/`SimpleStreamOptions` call
accepts an optional `cacheRetention` field of this type, resolved by a `resolveCacheRetention()`
function that is -- confirmed by reading all four occurrences directly -- byte-for-byte
identical logic, independently copy-pasted (not shared via an import) into
`anthropic-messages.ts`, `openai-responses.ts`, `openai-completions.ts`, and
`bedrock-converse-stream.ts`:

```mermaid
flowchart TD
    Call["models.stream/complete(model, context, options)"] --> Opt{"options.cacheRetention set?"}
    Opt -->|yes| Use["use it directly"]
    Opt -->|no| Env{"PI_CACHE_RETENTION env == 'long'?"}
    Env -->|yes| Long["'long'"]
    Env -->|no| Short["'short' (default)"]
    Use --> Retention["resolved CacheRetention"]
    Long --> Retention
    Short --> Retention
    Retention --> SessId{"retention === 'none'?"}
    SessId -->|yes| NoSess["cacheSessionId = undefined"]
    SessId -->|no| Sess["cacheSessionId = options.sessionId"]
    Retention --> Proto["per-protocol lowering (S4.2-S4.6)"]
```

The inline comment on the `PI_CACHE_RETENTION` branch -- "Defaults to `short` and uses
`PI_CACHE_RETENTION` for backward compatibility" -- indicates the environment variable
predates the per-request `cacheRetention` option and is kept as a persistent,
non-per-call override rather than the primary mechanism. Every one of the four protocols
also derives a `cacheSessionId` from the same resolved value with the identical one-line
rule -- `const cacheSessionId = cacheRetention === "none" ? undefined : options?.sessionId`
-- which then threads into whatever provider-specific session/cache-key mechanism that
protocol uses (an Anthropic `x-session-affinity` header, an OpenAI `prompt_cache_key` body
field, or nothing at all for Bedrock, which has no session-scoped cache key of its own).
One `sessionId` option, one `cacheRetention` option, and up to four independently-lowered
wire mechanisms is the architectural shape this whole section documents.

### 4.2 Anthropic Messages: three placement sites, `"stealth mode"` system-prompt duplication, and a cap respected by construction

VERIFIED, `packages/ai/src/api/anthropic-messages.ts`. `getCacheControl(model, cacheRetention,
env)` returns no marker at all when the resolved retention is `"none"`; otherwise it returns
`{ type: "ephemeral", ...(ttl && { ttl }) }`, where `ttl` is set to `"1h"` only when retention
is `"long"` **and** the model's own `compat.supportsLongCacheRetention` is true (default
`true` -- some Anthropic-compatible providers set it `false`). The resulting `cacheControl`
object is placed at exactly three sites in `buildParams()`:

1. **The system prompt.** For an OAuth (Claude subscription) token, the source under a
   comment literally reading `"Stealth mode: Mimic Claude Code's tool naming exactly"`
   constructs **two** system blocks -- a hardcoded `"You are Claude Code, Anthropic's
   official CLI for Claude."` identity string, followed by the caller's own
   `context.systemPrompt` -- and marks **both** with `cache_control`. For a plain API key,
   only the caller's own system prompt is sent, with one `cache_control` marker. This is a
   real, source-confirmed instance of pi's own OAuth path deliberately impersonating Claude
   Code's own system-prompt identity (also renaming tool calls via `toClaudeCodeName()` in
   the same code path) -- flagged here specifically because it means the *number* of
   system-level cache breakpoints pi emits (one or two) depends on which auth mode is active,
   not just on whether caching is enabled.
2. **The last tool definition** (`index === tools.length - 1` inside `convertTools()`),
   gated by `compat.supportsCacheControlOnTools` (default `true`; the source names Fireworks
   as a provider where this is set `false` because it "does not support this field on tools
   and may reject or ignore it").
3. **The last cacheable content block of the last message in the array**, if that message's
   `role` is `"user"` -- specifically the trailing `text`, `image`, or `tool_result` block,
   per a dedicated post-pass in `convertMessages()` under the comment "Add `cache_control` to
   the last user message to cache conversation history."

Because pi places **at most one** breakpoint at each of these three sites regardless of how
many tools or how much conversation history exists, the total emitted `cache_control` count
is bounded at exactly two (OAuth) or one (API key) system-prompt markers plus one tool marker
plus one message marker -- **at most four**, landing exactly on the Anthropic API's own
4-breakpoint cap ([llm-api-contract.md](llm-api-contract.md) §1.9,
[caching.md](caching.md) §1.9) by construction, not by an explicit runtime counter the way
OpenCode's `Breakpoints` object enforces the same cap defensively (§3.2). No source read this
session shows pi counting or dropping breakpoints -- the placement logic itself simply never
produces more than four.

### 4.3 TTL is a caller-declared toggle, not an auth-path inference -- the sharpest contrast with Claude Code

Claude Code (§1.3) infers its TTL automatically from *how the session authenticates*
(subscription -> 1h by default, API key/Bedrock/Vertex/Foundry -> 5m by default). pi instead
exposes `cacheRetention` as an explicit, caller- or environment-declared choice that is
**orthogonal to authentication mode**: an OAuth-authenticated pi session with
`cacheRetention: "short"` (the default) gets the plain 5-minute ephemeral cache with no `ttl`
field at all, and an API-key-authenticated session with `cacheRetention: "long"` gets the
same `ttl: "1h"` marker an OAuth session would. The only persistent, non-per-call way to opt
every request into the long tier is the `PI_CACHE_RETENTION=long` environment variable,
documented in `packages/coding-agent/docs/environment-variables.md`: "Set to `long` for
extended provider prompt caching where supported." A provider- or model-level override in
`models.json` (`compat.supportsLongCacheRetention: false`, documented in
`packages/coding-agent/docs/models.md`) can also refuse the long tier outright regardless of
what the caller or environment variable requests.

### 4.4 OpenAI Responses and Chat Completions: `prompt_cache_key`/`prompt_cache_retention`, an explicit opt-out for GPT-5.6+, and a second, independent Anthropic-flavored path for hybrid providers

VERIFIED, `packages/ai/src/api/openai-responses.ts` and `openai-completions.ts`. Both
protocols build a `prompt_cache_key` body field from `options.sessionId`, clamped to 64
characters by `clampOpenAIPromptCacheKey()` (`packages/ai/src/api/openai-prompt-cache.ts`,
`OPENAI_PROMPT_CACHE_KEY_MAX_LENGTH = 64`) -- OpenAI's own key-based mechanism for routing
repeat requests toward the same cached prefix, distinct from Anthropic's breakpoint-marker
approach. Responses always sends the key whenever retention is not `"none"`; Completions
sends it whenever retention is not `"none"` **and** the endpoint is native OpenAI
(`model.baseUrl.includes("api.openai.com")`), or, for non-native OpenAI-compatible
endpoints, only when retention is `"long"` **and** `compat.supportsLongCacheRetention` --
a narrower condition than the Responses path. Both protocols additionally send
`prompt_cache_retention: "24h"` when retention is `"long"` and the model's
`compat.supportsLongCacheRetention` allows it -- the 24-hour figure matching, independently,
the same OpenAI-model TTL figure Copilot CLI's own docs state (§2.2), here confirmed from a
different vantage point (pi's own request-construction source rather than a Microsoft/GitHub
tutorial page).

A capability found nowhere else in this page: Responses additionally sends
`prompt_cache_options: { mode: "explicit" }` specifically when retention is `"none"` **and**
`compat.supportsExplicitPromptCacheMode` is true -- a flag the source and
`packages/coding-agent/docs/models.md` both describe as gating "`prompt_cache_options`
(OpenAI GPT-5.6+ explicit prompt caching); older OpenAI models reject the parameter." This
means pi can, on capable models, **affirmatively suppress OpenAI's own implicit automatic
caching** when the caller asks for `cacheRetention: "none"` -- a materially different lever
than anything else this page documents: Claude Code and Copilot CLI never address turning off
the underlying provider's own caching at all, and OpenCode's own OpenAI path (§3.3) is a pure
no-op that neither engages nor disables the provider default.

Orthogonally, `openai-completions.ts` implements a **second, independent** caching strategy
gated by a distinct compat flag: when `compat.cacheControlFormat === "anthropic"` (an explicit
per-provider opt-in, documented in `models.md` as "for OpenAI-compatible providers that
expose Anthropic-style prompt caching through `cache_control` markers on text content and
tool definitions"), `applyAnthropicCacheControl()` places `cache_control` markers on the
system/developer message, the last tool definition, and the last user/assistant/tool
message's trailing text block -- the same three-site placement heuristic §4.2 documents for
the real Anthropic Messages protocol, reimplemented against an OpenAI-Chat-Completions-shaped
request body for providers that speak the OpenAI wire format but expose Anthropic-style cache
semantics underneath it. `cacheControlFormat` and the `prompt_cache_key`/
`prompt_cache_retention` mechanism are independent, non-exclusive levers on the same
`OpenAICompletionsCompat` object -- a provider can plausibly need either, both, or neither
depending on which underlying caching model it actually implements.

### 4.5 Amazon Bedrock Converse: eligibility inferred from the model catalog, not requested by the caller

VERIFIED, `packages/ai/src/api/bedrock-converse-stream.ts`. `supportsPromptCaching(model, env)`
returns `true` only when the model's `id`/`name` contains a recognizable Claude reference
(matched against `"claude"`, `"anthropic.claude"`, `"anthropic/claude"` substrings), naming
the concretely supported families in a source comment: "Claude 3.5 Haiku, Claude 3.7 Sonnet,
Claude 4.x models, Claude 5 models." For application inference profiles -- whose ARN does not
embed the model name, making this local detection impossible -- the environment variable
`AWS_BEDROCK_FORCE_CACHE=1` forces eligibility on, documented identically in
`packages/coding-agent/docs/providers.md`. The same source comment separately notes "Amazon
Nova models have automatic caching and don't need explicit cache points" -- an
implicit-vs-explicit split drawn *within* a single cloud provider's own model catalog, echoing
(without being identical to) the cross-vendor Anthropic-explicit/OpenAI-Gemini-implicit split
OpenCode's architecture draws across providers (§3.3). When eligible and retention is not
`"none"`, a `{ cachePoint: { type: CachePointType.DEFAULT, ...(long && { ttl:
CacheTTL.ONE_HOUR }) } }` block is appended after the system-prompt content and again after
the last user message's content -- the same two of §4.2's three Anthropic placement sites
(system, last user message), but **not** the tool-definition site: this session's read of
`convertToolConfig()` (the function building Bedrock's `toolConfig` block) found no
`cachePoint` reference anywhere in it, so Bedrock Converse tool definitions do not receive a
cache breakpoint through this code path -- a confirmed structural omission relative to the
Anthropic Messages protocol's own three-site placement, not merely an unconfirmed gap.

### 4.6 Google Generative AI and Vertex: read-only accounting, zero request-side markers

VERIFIED (checked negative result), `packages/ai/src/api/google-generative-ai.ts`,
`google-vertex.ts`, and `google-shared.ts` (all read in full). None of the three files
constructs any cache-related request field -- the only `cache`-related code in either
provider file is on the **response** side: `cacheRead: chunk.usageMetadata.cachedContentTokenCount
|| 0` and a hardcoded `cacheWrite: 0` (Gemini's API never reports a cache-write count back).
The non-cached input token count is explicitly computed as `promptTokenCount -
cachedContentTokenCount`, meaning a cache hit is visible only as a reduced non-cached-input
figure plus a populated `cacheRead` count in the response usage object -- never as anything
the client sends. This independently confirms, from pi's own source, the same implicit,
automatic, no-client-marker Gemini caching model OpenCode's own source establishes at §3.3
and its README states as a provider-behavior fact ("implicit caching on 2.5+").

### 4.7 Session-affinity headers: a caching-adjacent mechanism, not the cache marker itself

VERIFIED, `types.ts` and `models.md`. Distinct from any `cache_control`/`cachePoint`/
`prompt_cache_key` marker, pi separately supports **session-affinity headers** -- a
routing-level mechanism ensuring repeated requests from the same logical session land on the
same backend replica or shard, which is a precondition for that replica's own server-side
cache to actually be reachable on providers whose caching is tied to a specific served
instance rather than a globally shared cache tier. The source names Fireworks explicitly:
"session affinity for prompt cache routing (requests to the same replica maximize cache
hits)." Three documented header formats, selected by `compat.sessionAffinityFormat`:
`"openai"` (`session_id` + `x-client-request-id`, plus `x-session-affinity` on Chat
Completions specifically), `"openai-nosession"` (omits the underscore-bearing `session_id`
header for servers that reject it), and `"openrouter"` (`x-session-id`). `models.md` states
plainly that none of these header formats affects the `prompt_cache_key` body parameter
itself, which remains governed purely by `cacheRetention` -- the header and the body-level
cache key are two independent levers both threaded from the same underlying `sessionId`
value, not one mechanism wearing two names.

### 4.8 Compaction and branch summaries: an explicit cache opt-out -- the opposite policy from Claude Code

VERIFIED, `packages/coding-agent/src/core/compaction/compaction.ts` (function building the
summarization request options): `cacheRetention: "none"` is set explicitly for every
compaction and branch-summary call, alongside a fresh routing session ID
(`options.sessionId ?? uuidv7()`) when the caller did not already supply one, under the
inline comment "Avoid cache writes for one-off summaries. Reuse caller-supplied routing when
available; callers without a session ID, including branch summaries, receive a fresh routing
ID." `packages/coding-agent/docs/compaction.md` restates this from the user-facing side:
"Compaction and branch-summary requests use fresh routing session IDs and, where supported by
the provider, disable prompt-cache writes because these one-off prompts are unlikely to be
reused." This is a direct, source-confirmed point of contrast with Claude Code's own
documented stance on the identical operation (§1.2): Claude Code's docs describe its own
compaction summarization request as an ordinary API call that **benefits from** reading the
live, still-warm prefix from cache, treating summarization as cache-favorable. pi's
coding-agent takes the opposite design position for the same kind of request -- treating a
summarization prompt as inherently cache-averse because the summary text itself is judged
unlikely to recur -- and deliberately declines to write it into the cache at all. Both are
VERIFIED, for their own harness only; the difference is a genuine design divergence between
two independent engineering teams solving the same problem (what to do with a one-off
summarization call's cache footprint), not an error in either.

### 4.9 Observability: per-model cache-rate metadata, a cost-tier interaction, the Anthropic-only `cacheWrite1h` split, and an opt-in transcript notice

VERIFIED, `types.ts`, `models.md`. Every model's `cost` object carries four required
per-million-token rates -- `input`, `output`, `cacheRead`, `cacheWrite` -- and `models.md`
documents a cost-**tier** mechanism (an alternate full rate set that applies once usage
crosses a threshold) triggering "when total input usage (`input + cacheRead + cacheWrite`)
exceeds `inputTokensAbove`" -- meaning cache-read and cache-write tokens, despite being billed
at a fraction of the base input rate, still count toward the raw token volume that can push a
request into a costlier tier. A `cacheWrite1h` field on the `Usage` type is documented inline
as a "Subset of `cacheWrite` written with 1h retention. Only Anthropic reports this split" --
sourced in `anthropic-messages.ts` from the API's own nested `event.message.usage.cache_creation
?.ephemeral_1h_input_tokens` field, the identical nested breakdown object Claude Code's own
changelog separately records a reporting bug against (§1.6) -- pi's own accounting already
reads this nested field directly rather than only the flat `cache_creation_input_tokens`
count, though no source read this session states pi and Claude Code share any code or ever
compared notes on this; the parallel is this page's own observation from two independent
implementations reading the same upstream API field. On the CLI side,
`packages/coding-agent/docs/settings.md` documents `showCacheMissNotices` (boolean, default
`false`): "Show transcript notices for significant prompt-cache misses and compaction or
branch-summary usage" -- an opt-in visibility feature functionally adjacent to Claude Code's
own `/usage` cache-miss flagging (§1.6), but off by default rather than always-on, and the TUI
footer documented in `usage.md` folds "token/cache usage, cost, context usage" into one
per-session summary line.

### 4.10 The configuration surface, summarized

Taken together: a persistent `PI_CACHE_RETENTION` environment variable, a per-request
`cacheRetention` option (`"none" | "short" | "long"`, default `"short"`), a per-provider or
per-model `compat` override block in `models.json` (`supportsLongCacheRetention`,
`supportsCacheControlOnTools`, `cacheControlFormat`, `sendSessionAffinityHeaders`,
`sessionAffinityFormat`, `supportsExplicitPromptCacheMode`), a Bedrock-specific
`AWS_BEDROCK_FORCE_CACHE` escape hatch, and an opt-in `showCacheMissNotices` UI setting. This
is a documented, user-facing configuration surface that is materially larger and more
explicit than OpenCode's (§3.5, which found none beyond an unlisted `providerOptions` escape
hatch) and shaped differently from both Claude Code's (§1.8: entirely disable-toggle-plus-
TTL-override env vars, no explicit retention enum exposed to the caller) and Copilot CLI's
(§2: no documented configuration surface found at all).

---

## 5. Synthesis

| Dimension | Claude Code | Copilot CLI | OpenCode | pi |
|---|---|---|---|---|
| Verifiability | Docs-only; no public implementation | Docs + changelog only; no public implementation | Source-verified (`packages/llm`), `dev` branch (caveat applies) | Source-verified (`packages/ai`), `main` branch |
| Underlying provider(s) | Anthropic API exclusively (+ Bedrock/Vertex/Foundry as hosting, not model-family, variants) | Multi-provider (GPT, Claude, Gemini, BYOK/BYOM) | Multi-provider, explicit branch per protocol (Anthropic/Bedrock explicit breakpoints; OpenAI/Gemini implicit no-op) | Multi-provider (Anthropic, OpenAI Responses/Completions, Google, Bedrock, plus OpenAI-compatible third parties); explicit per-protocol branch, same shape as OpenCode |
| Cache-key inputs named | Model, effort level, tool-definition set, plugin/MCP state, request-header flags (fast mode) | Model, reasoning effort, "context size," enabled tools/MCP servers | Model route id (gates whether the policy pass runs at all); breakpoint placement itself is prefix-based, not a separate key | `cacheRetention` (explicit enum, not inferred from auth), `sessionId` (feeds both session-affinity headers and OpenAI's `prompt_cache_key`) |
| Default breakpoint placement | Not client-controlled -- Anthropic API applies its own default policy; Claude Code's contribution is *request ordering* (layer table, §1.1) so a stable prefix exists to cache | Undocumented at this granularity | Explicit, source-defined: last tool def + last system part + latest user message (`cache-policy.ts`) | Explicit, source-defined: system prompt (one or two blocks depending on OAuth "stealth mode") + last tool def + last user message's last block (§4.2) |
| Breakpoint cap | Inherited from the Anthropic API (4, §1.9); not itself re-stated as a Claude-Code-specific number | Not documented | Explicit, enforced client-side before the request is sent (`ANTHROPIC_BREAKPOINT_CAP`/`BEDROCK_BREAKPOINT_CAP = 4`), matching the API cap | Respected by construction (at most 4 breakpoints ever placed: 1-2 system + 1 tool + 1 message), not by an explicit runtime counter |
| TTL options | 5m / 1h, chosen automatically by auth path, overridable via env vars | 1h (most models) / 24h (OpenAI models specifically) | 5m default / 1h via `ttlSeconds >= 3600` bucket, per explicit `CacheHint.ttlSeconds` | 5m ("short", default) / 1h (Anthropic/Bedrock "long") or 24h (OpenAI "long"), an explicit `cacheRetention` value orthogonal to auth mode |
| Cache-write cost multiplier (Anthropic) | 1.25x (5m) / 2x (1h) of base input -- cited from the API docs, not restated as Claude-Code-specific | Not stated | Cited identically in the package's own README as the design rationale for defaulting caching on | Not independently re-stated as a multiplier in source; `cost.cacheWrite` is a per-model $/M-token rate, not a multiplier formula |
| Cache-read cost multiplier | ~10% of standard input rate (both Claude Code docs and Anthropic API docs state this) | "~10% of the normal input price" | Not independently re-stated as a fixed multiplier in source; consistent with the same underlying API | Not independently re-stated as a fixed multiplier; `cost.cacheRead` is a per-model $/M-token rate |
| Observability fields | `cache_creation_input_tokens` / `cache_read_input_tokens`, surfaced in `/usage`, `/cost`, OTel | OTel `gen_ai.usage.cache_read.input_tokens` / `gen_ai.usage.cache_creation.input_tokens`, `/usage` cache write+read display | `cacheReadInputTokens` / `cacheWriteInputTokens` normalized into the shared internal `Usage` type across every provider | `usage.cacheRead` / `usage.cacheWrite` / Anthropic-only `usage.cacheWrite1h`, plus opt-in `showCacheMissNotices` transcript notices and a TUI footer line |
| Compaction/cache interaction | Compaction's own summarization request itself reads the live prefix from cache while warm (§1.2) | Not documented at this level of mechanism | Compaction's overflow-detection formula consumes the same normalized cache-read/cache-write token fields (§3.4/context-compression.md §3.2) | Compaction/branch-summary requests explicitly set `cacheRetention: "none"` to avoid a cache write for a one-off prompt (§4.8) -- the opposite policy from Claude Code's |
| User-facing config lever | Five `DISABLE_PROMPT_CACHING*` env vars + two TTL env vars, settable in managed settings org-wide | Not documented (no equivalent env-var table found) | None found on the docs config page; appears to be a programmatic `LLMRequest.cache` field only (§3.5) | `PI_CACHE_RETENTION` env var, per-request `cacheRetention` option, and per-provider/model `compat` fields in `models.json` (§4.10) -- the most explicit documented surface of the four |
| Subagent/fork cache behavior | Subagent: separate cache, 5m TTL even on subscription. Fork: inherits and reads parent's cache | Not documented | Not investigated this session (out of scope of `packages/llm`; would require `packages/opencode`'s subagent/session-forking call sites) | Not investigated this session (out of scope of `packages/ai`; would require `packages/coding-agent`'s own subagent/handoff call sites) |

**The design lesson.** All four harnesses converge on the same
underlying economic argument -- a cache read costs roughly a tenth of a
fresh input token, so any request that shares a meaningful prefix with a
prior one is worth caching by default -- but they diverge sharply in how
much of the *mechanism* is under the harness's own control versus
inherited wholesale from the model provider. Claude Code sits on exactly
one provider family and spends its own documentation explaining *client-
side discipline* around that provider's cache (request ordering into
stable layers, TTL selection by auth path, a long list of actions users
can take that accidentally break the prefix) rather than the cache
mechanism itself, which it treats as Anthropic's to document. Copilot CLI,
routing across heterogeneous providers, documents only the outward
contract (a 10% read discount, a 24h/1h TTL split by provider family) and
leaves the provider-dispatch mechanism unstated -- consistent with, but not
proven identical to, OpenCode's approach. OpenCode is the one harness of
the three that makes the provider-dispatch decision a literal, readable
`if` in `cache-policy.ts` (explicit breakpoints for Anthropic/Bedrock, a
deliberate no-op for OpenAI/Gemini's implicit caching) -- and it is
notable that OpenCode's own breakpoint-placement heuristic (anchor on the
latest user message specifically to cover an entire tool-use loop's
intra-turn round-trips) is a more granular, source-stated optimization
than anything Claude Code's or Copilot CLI's own docs state about *where*
within a request their own default breakpoint lands. pi is the harness that
pushes the *caller's* control furthest: rather than inferring a TTL from
authentication (Claude Code) or leaving the whole mechanism to a
provider-neutral no-op/breakpoint split with no exposed configuration
(OpenCode), pi exposes `cacheRetention` as an explicit three-value enum a
caller or a persistent environment variable can set independently of how
the session authenticates, and reaches further than any of the other three
by actually toggling a provider's own *implicit* caching off
(`prompt_cache_options: { mode: "explicit" }` on capable OpenAI models when
the caller opts out) rather than only ever adding markers on top of it.
pi's own compaction/branch-summary opt-out (§4.8) is also the one place in
this page's whole four-harness comparison where two harnesses take
*opposite* stances on the identical mechanism -- Claude Code treats its
compaction call as cache-favorable and lets it ride the warm prefix, pi's
coding-agent treats the same kind of call as cache-averse and deliberately
declines to write it -- which is itself evidence that "should a one-off
summarization request touch the cache" is a genuine, unresolved design
choice rather than a fact about the underlying API that all correct
implementations must converge on.

---

## Sources

All fetched fresh 2026-07-30 unless noted otherwise.

**Claude Code (authoritative for its own documented behavior only):**
- `https://code.claude.com/docs/en/prompt-caching` -- the primary source
  for §1: layer ordering, the full invalidate/keep-cache action lists,
  cache lifetime by authentication path, cache scope (machine/directory),
  the two token-count fields, subagent/fork cache behavior, and the
  `DISABLE_PROMPT_CACHING*`/TTL environment variable tables.
- `https://code.claude.com/docs/en/costs` -- "Reduce token usage" section
  naming prompt caching as an automatic cost optimization, the `/usage`
  Session-block example output, and the "Why usage climbs in a long
  session" section's cache-miss/cache-lifetime framing.
- `https://github.com/anthropics/claude-code` `CHANGELOG.md`, fetched fresh
  this session via `gh api repos/anthropics/claude-code/contents/
  CHANGELOG.md` (full file) -- every dated/versioned entry cited in
  §1.3-1.8 (v2.1.211 Bedrock/Mantle/Foundry system-context caching,
  the Bedrock/Vertex/Mantle/Foundry billing regression fix, the
  `cache_creation_input_tokens`-reporting-as-0 fix, the 1h-TTL-silently-
  downgraded fix, `ENABLE_PROMPT_CACHING_1H`/`FORCE_PROMPT_CACHING_5M`
  origin, `ENABLE_PROMPT_CACHING_1H_BEDROCK` deprecation,
  `--exclude-dynamic-system-prompt-sections`, the subagent-progress-summary
  cache-miss fix, the per-model/cache-hit `/cost` breakdown, and the
  75-plus-minute idle-return nudge). Authoritative for its own
  behavior-change history only; this repo ships no implementation source.

**GitHub Copilot CLI (authoritative for its own behavior-change history
only; no implementation source exists in this repo):**
- `https://docs.github.com/en/enterprise-cloud@latest/copilot/tutorials/
  optimize-ai-usage` -- the primary source for §2.1-2.3: the caching
  rationale, the 10%-of-normal-input pricing figure, the 24h(OpenAI)/1h
  (most others) TTL split, the three named invalidation triggers, and the
  auto-model-selection cache-boundary protection.
- `https://github.com/github/copilot-cli` `changelog.md`, fetched fresh
  this session via `gh api repos/github/copilot-cli/contents/
  changelog.md` (full 2,898-line file, grepped for cache-related entries)
  -- the v0.0.359 cached-tokens-zero bug and every subsequent
  cache-observability entry cited in §2.4 (the `/usage` cache write+read
  display, cache-write-pricing-for-omitted-models fix, the OTel GenAI
  cache-attribute naming correction, the input-usage-includes-cached fix,
  and the attached-file/prompt-cache-reset and custom-agent-instruction-
  duplication entries).

**OpenCode (authoritative for its own documented behavior AND, unlike the
two harnesses above, its own real implementation; `dev` branch, not a
stable release tag):**
- `https://github.com/anomalyco/opencode`, `dev` branch, fetched via
  `gh search code` (to locate call sites: `cache_control`, `cacheControl`,
  `ephemeral`) and `gh api` (full file contents) this session -- full
  contents of `packages/llm/src/cache-policy.ts`,
  `packages/llm/src/protocols/anthropic-messages.ts` (cache-related
  sections), `packages/llm/src/protocols/utils/bedrock-cache.ts`,
  `packages/llm/src/protocols/utils/cache.ts`,
  `packages/llm/src/schema/options.ts` (`CacheHint`/`CachePolicy`
  definitions), and `packages/llm/README.md`'s "Caching" section --
  covering §3.1-3.4 in full.
- `https://opencode.ai/docs/providers/` and `https://opencode.ai/docs/
  config/`, fetched fresh this session -- confirmed, as a checked negative
  result rather than an assumption, that neither page documents a
  user-facing prompt-caching configuration surface (§3.5).
- `https://platform.claude.com/docs/en/build-with-claude/prompt-caching`,
  fetched fresh this session -- authoritative for the underlying Anthropic
  Messages API mechanism only (§1.9), cited here because both Claude
  Code's own docs and OpenCode's Anthropic protocol adapter build on this
  exact API surface: the 4-breakpoint cap, the `"ephemeral"` cache type,
  5-minute/1-hour TTL pricing multipliers, per-model minimum cacheable
  prompt lengths, the tools -> system -> messages invalidation hierarchy,
  and the 20-block cache-read lookback window.

**pi (authoritative for its own documented behavior; fetched 1 September 2026 from
`github.com/earendil-works/pi`, `main` branch):**
- `packages/ai/package.json` and `packages/coding-agent/package.json` (via `gh api
  repos/earendil-works/pi/contents/...`) -- confirming the two distinct npm package names
  (`@earendil-works/pi-ai`, `@earendil-works/pi-coding-agent`) and their dependency
  relationship, resolving §4's opening naming clarification.
- `packages/ai/src/types.ts` (full file) -- the `CacheRetention` type definition, the
  `Usage`/`Model.cost` cache fields (`cacheRead`, `cacheWrite`, `cacheWrite1h`), and the
  `AnthropicMessagesCompat`/`OpenAICompletionsCompat`/`OpenAIResponsesCompat`
  cache-related field documentation; covers §4.1, §4.9.
- `packages/ai/src/api/anthropic-messages.ts` (full file) -- `resolveCacheRetention()`,
  `getCacheControl()`, the OAuth "stealth mode" system-prompt duplication, and the three
  `cache_control` placement sites (system, last tool, last user-message block); covers
  §4.2, §4.3.
- `packages/ai/src/api/openai-responses.ts`, `openai-completions.ts`, and
  `openai-prompt-cache.ts` (full files) -- `prompt_cache_key`/`prompt_cache_retention`/
  `prompt_cache_options` construction, the `clampOpenAIPromptCacheKey()` 64-character clamp,
  and the `cacheControlFormat: "anthropic"` Anthropic-style fallback path
  (`applyAnthropicCacheControl()`); covers §4.4.
- `packages/ai/src/api/bedrock-converse-stream.ts` (full file) -- `supportsPromptCaching()`'s
  Claude-family detection and `AWS_BEDROCK_FORCE_CACHE` override, the two `cachePoint`
  placement sites, and the confirmed absence of a `cachePoint` in `convertToolConfig()`;
  covers §4.5.
- `packages/ai/src/api/google-generative-ai.ts`, `google-vertex.ts`, and `google-shared.ts`
  (full files) -- confirmed, as a checked negative result, that no request-side cache field
  is ever constructed for either Google API family; covers §4.6.
- `packages/ai/README.md` (full file, 513+ lines) -- cross-referenced for the session-affinity
  header-format table and the `cacheRetention`/`sessionId` faux-provider example; covers §4.7.
- `packages/coding-agent/docs/models.md`, `providers.md`, `environment-variables.md`,
  `settings.md`, and `compaction.md`, plus `packages/coding-agent/src/core/compaction/
  compaction.ts` (all fetched via `gh api`) -- the `PI_CACHE_RETENTION` environment variable,
  the `compat` field documentation table, the Bedrock prompt-caching provider note, the
  `showCacheMissNotices` setting, and the compaction/branch-summary `cacheRetention: "none"`
  opt-out and its accompanying doc-page prose; covers §4.3, §4.5, §4.8, §4.9, §4.10.
