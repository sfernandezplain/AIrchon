# The LLM API contract -- messages, content blocks, streaming, stop reasons

**Scope note.** This page is the layer *underneath* every other page in
this book. It is the wire-level contract between a harness and the model
provider's HTTP API: the request/response JSON shape, the roles a message
can carry, the typed content-block vocabulary a model uses to say "call
this tool" versus "here is text," the Server-Sent-Events (SSE) framing a
streamed response arrives in, and the enumerated reasons a generation
stops. It is deliberately distinct from
[agent-loop.md](agent-loop.md), which assumes this layer already exists
and describes what a harness's control loop *does* with it once tool
calling already works (the Thought -> Action -> Observation cycle, the
while-loop framing, stop-and-parse). Concretely: a `tool_use` content
block arriving over the wire **is** the Action; the harness executing
that tool and posting a `tool_result` block back **is** the Observation
being appended to context. This page grounds that mechanism at the byte
level; agent-loop.md names the pattern.

Two materially different wire contracts are in play across the six
harnesses this book covers, because they are built by different vendors
against different providers: **Anthropic's Messages API** (a typed
content-block array per message, one `stop_reason` field) and
**OpenAI's Chat Completions / Responses APIs** (a `tool_calls` array
attached to an assistant message, a `finish_reason` field, and, for the
Responses API specifically, a stream of named `response.*` events
distinct from Anthropic's `content_block_*` event names) -- with pi's
own §3.5 additionally naming Google's Generative AI API as a fourth wire
family its own provider abstraction speaks natively, not independently
detailed at the wire level on this page the way §1/§2 detail the other
two, and Hermes Agent's own §3.6 (added 1 September 2026) confirming from
source that the same two wire families -- plus AWS Bedrock's distinct
Converse API -- are all reachable through exactly two pinned SDK
packages, the `openai` package doing double duty for both of §2's OpenAI
contracts. Every claim below is tagged VERIFIED (fetched this session from a
named source) or BEST CURRENT UNDERSTANDING, UNCONFIRMED, and a fact
verified for one provider's API is never assumed to hold for the other's
without its own citation -- the same authority-overreach guard this book
applies across harnesses applies here across model-provider APIs too.

---

## 1. The Anthropic Messages API contract

VERIFIED, `platform.claude.com/docs/en/api/messages` (redirected live
this session from `docs.claude.com/en/api/messages` -- both hostnames
serve Anthropic's own Claude Developer Platform documentation),
`platform.claude.com/docs/en/docs/build-with-claude/streaming`
(redirected identically from `docs.claude.com/.../streaming`), both
fetched fresh 2026-08-01. This section is authoritative for what the
Anthropic Messages API itself specifies, not for how any specific
harness's own agent loop chooses to use it -- that distinction is
carried into §3.1 below.

### 1.1 Request shape

A `POST /v1/messages` request's fields, as documented: `model`
(required), `messages` (required, an array of role-tagged content),
`max_tokens` (required -- the docs state a value of `0` populates only
the prompt cache and generates nothing), `system` (a string or an array
of `TextBlockParam`, the top-level, once-per-request system prompt),
`tools` (an array of tool definitions), `tool_choice`, `stream`
(boolean), `temperature`/`top_p`/`top_k`, `stop_sequences`, `metadata`,
`thinking` (extended-thinking configuration), `cache_control`, and a
`service_tier` field. `tool_choice` takes one of four shapes: `"auto"`
(model decides), `"any"` (model must call some tool), `"tool"` (a named,
forced tool call), or `"none"`, with an optional
`disable_parallel_tool_use` flag alongside any of them.

### 1.2 Roles and the messages array

Each message object carries exactly two required fields, `role` and
`content`. Three role values are documented: `"user"` (input, and where
a client posts back the results of tool execution), `"assistant"`
(prior model output, including any `tool_use` blocks the model itself
emitted), and `"system"` -- explicitly distinguished from the top-level
`system` request parameter as a **mid-conversation** system instruction
(`MidConversationSystemBlockParam`), applying only from its position in
the array onward rather than as the request's privileged prime prompt.
Consecutive same-role turns are combined into a single turn by the API.
This page does not cover what actually gets loaded into that top-level
`system` field or how large it is allowed to grow before eviction --
that is [instruction-context-budget.md](instruction-context-budget.md)'s
and [memory-management.md](memory-management.md)'s territory; this page
only names the wire slot it occupies.

### 1.3 The content-block vocabulary

`content` is either a bare string or an array of typed content blocks.
The documented block types, with the two load-bearing ones spelled out
in full because they are the literal wire form of the agent loop's
Action/Observation exchange:

| Block type | Emitted by | Purpose |
|---|---|---|
| `text` | either | plain generated or supplied text |
| `image` | client (request) | base64 or URL-sourced image input |
| `document` | client (request) | PDF/text document input, with citation support |
| `tool_use` | **model** (in a prior turn, replayed back in the next request) | the model's call: `{type: "tool_use", id, name, input}` |
| `tool_result` | **client** | the client's answer to a `tool_use`: `{type: "tool_result", tool_use_id, content, is_error}` |
| `thinking` | model | extended-thinking output: `{type: "thinking", thinking, signature}` |
| `redacted_thinking` | model | a thinking block the API has redacted: `{type: "redacted_thinking", data}` |
| `server_tool_use` / matching `*_tool_result` blocks | model / API | Anthropic-hosted tools (`web_search`, `web_fetch`, `code_execution`, `bash_code_execution`, etc.) executed server-side, not by the client |
| `search_result` | client | structured search-style content supplied back to the model |

The `tool_use` block's `id` (a `toolu_...`-prefixed string) is the
correlation key: the client's subsequent `tool_result` block **must**
carry a matching `tool_use_id`, and `is_error: true` on that block is
the documented mechanism for telling the model the tool call itself
failed (as distinct from the tool succeeding but returning content the
model dislikes) -- this is the exact wire-level substrate of the "bad
Observation handling" failure class agent-loop.md names abstractly.

### 1.4 The response object and the `stop_reason` enumeration

A non-streaming response returns `id`, `type` (always `"message"`),
`role` (always `"assistant"`), `content` (an array of the block types
above), `model`, `stop_reason`, `stop_sequence`, and `usage`
(`input_tokens`, `output_tokens`, plus cache-specific fields covered in
depth by [caching.md](caching.md)). The full documented `stop_reason`
enumeration:

| `stop_reason` | Meaning |
|---|---|
| `end_turn` | natural stopping point; response complete |
| `max_tokens` | the `max_tokens` request limit (or the model's context window) was hit |
| `stop_sequence` | a custom `stop_sequences` string was generated |
| `tool_use` | the model emitted one or more `tool_use` blocks and is waiting on results -- this is the value that tells a harness's loop "re-enter the Action/Observation half of the cycle instead of surfacing text to the user" |
| `pause_turn` | a long-running turn (typically involving a server-side tool) was paused; the client is expected to send the response straight back to continue it |
| `refusal` | a streaming safety classifier intervened mid-generation |
| `model_context_window_exceeded` | the model's own context window, not just `max_tokens`, was exceeded |

### 1.5 Streaming: the SSE event sequence

When `stream: true`, the API emits a Server-Sent-Events stream whose
documented event flow is fixed: one `message_start` (a `Message` shell
with empty `content`), then, per content block, a
`content_block_start` / one-or-more `content_block_delta` /
`content_block_stop` triad (each block carrying an `index` matching its
final position in the `content` array), then one-or-more
`message_delta` events carrying top-level changes (`stop_reason`,
cumulative `usage`), and finally one `message_stop`. `ping` events may
appear anywhere and carry no data of interest; `error` events (e.g. an
`overloaded_error`, the streaming analogue of an HTTP 529) can appear
mid-stream and the docs explicitly instruct clients to handle unknown
future event types gracefully, per the API's own versioning policy.

```mermaid
sequenceDiagram
    participant C as Client (harness)
    participant A as Anthropic Messages API
    C->>A: POST /v1/messages (stream: true, messages, tools)
    A-->>C: message_start (empty content)
    A-->>C: content_block_start (index 0, type text)
    A-->>C: content_block_delta x N (text_delta)
    A-->>C: content_block_stop (index 0)
    A-->>C: content_block_start (index 1, type tool_use, input {})
    A-->>C: content_block_delta x N (input_json_delta, partial_json fragments)
    A-->>C: content_block_stop (index 1)
    A-->>C: message_delta (stop_reason: tool_use)
    A-->>C: message_stop
    Note over C: parse tool_use block, execute the tool
    C->>A: POST /v1/messages (append assistant tool_use msg + user tool_result msg)
    A-->>C: message_start ... (next turn begins)
```

Three delta types matter beyond plain `text_delta`. **`input_json_delta`**
carries a `tool_use` block's `input` as it is generated: the docs are
explicit that these are "partial JSON strings," never valid JSON on
their own, and that a client must accumulate the string fragments and
parse the whole thing only once `content_block_stop` arrives (or use an
SDK's accumulator helper) -- and that "current models only support
emitting one complete key and value property from `input` at a time,"
so a caller should expect silence between deltas while the model works
on the next key. **`thinking_delta`** carries extended-thinking text
incrementally, the same way `text_delta` carries ordinary text; a
**`signature_delta`** event -- carrying a cryptographic signature used
to verify the thinking block's integrity -- always arrives immediately
before that block's `content_block_stop`. When thinking is configured
with `display: "omitted"`, no `thinking_delta` events are sent at all;
the block opens, receives only its `signature_delta`, and closes.

The docs also describe a documented **error-recovery** procedure for a
stream interrupted mid-response: capture whatever content blocks
completed, then construct a continuation request. For Claude 4.5 and
earlier models this continuation is built by placing the captured
partial text as the *start* of a new assistant message; for Claude 4.6
and later models the same partial content is instead wrapped in a new
**user** message instructing the model to continue from where it left
off -- the docs flag this as a genuine behavior change between model
generations, not a client-side choice. Tool-use and thinking blocks
specifically are called out as **not** partially recoverable this way;
only a completed text block can be resumed from.

---

## 2. The OpenAI Responses API contract (and where Chat Completions differs)

VERIFIED, `developers.openai.com/api/docs/guides/function-calling`
(redirected live this session from
`platform.openai.com/docs/guides/function-calling` -- OpenAI's own
developer documentation), fetched fresh 2026-08-01. The page fetched
documents OpenAI's newer **Responses API** specifically (its own
streaming event names below are Responses-API-specific); the older,
still-widely-supported **Chat Completions API**'s classic
`tool_calls`/`role: "tool"` shape is described from general prior
knowledge, not from a page re-fetched this session, and is explicitly
marked BEST CURRENT UNDERSTANDING, UNCONFIRMED where it is mentioned
below -- treat that half as a plausible sketch to verify independently
before relying on it, not as this page's own grounded claim.

### 2.1 Roles and tool-call shape (Responses API, VERIFIED)

The documented roles are `system`, `user`, `assistant`, and `tool`. When
the model calls a tool, the assistant's output includes an entry with a
`call_id` ("used later to submit the function result"), a `name`, and a
JSON-**encoded string** of `arguments` (not a parsed object the way
Anthropic's `tool_use.input` already is one) -- the entry's `type` is
`"function_call"` for schema-defined tools or `"custom_tool_call"` for
free-text tools. A tool result is sent back as
`{"role": "tool", "tool_call_id": <call_id>, "content": <result>}`,
where `content` "should typically be a string, where the format is up
to you (JSON, error codes, plain text, etc.)" -- a materially looser,
un-typed contract than Anthropic's `tool_result` block, which at least
distinguishes `is_error` as a structured field rather than leaving error
signalling entirely to string content.

### 2.2 `finish_reason` (VERIFIED, as documented on this page)

Four values are named on the fetched page: `stop` (natural completion),
`length` (token limit reached), `tool_calls` (the model invoked one or
more tools), and `content_filter` (a safety policy blocked completion).
This is a visibly coarser vocabulary than Anthropic's seven-value
`stop_reason` enumeration in §1.4 -- there is no OpenAI-documented
analogue, on this page, to Anthropic's `pause_turn` (mid-turn
server-tool continuation) or its `refusal`/`model_context_window_exceeded`
split from plain `length`.

### 2.3 Streaming (Responses API, VERIFIED)

The documented event sequence is `response.output_item.added`
(announces a new tool call with empty arguments), one or more
`response.function_call_arguments.delta` events (progressive JSON
argument chunks -- the direct analogue of Anthropic's
`input_json_delta`), and a terminal
`response.function_call_arguments.done` carrying the fully assembled
arguments string. The page's own framing: a client is "aggregating
chunks into an encoded `arguments` JSON object," the same
accumulate-then-parse discipline Anthropic's docs describe for
`input_json_delta` in §1.5, just under different event names.

### 2.4 Chat Completions' classic shape (BEST CURRENT UNDERSTANDING, UNCONFIRMED)

Not re-verified this session, offered only as a commonly-known,
still-in-wide-use contrast point: the older Chat Completions API
represents a tool call as a `tool_calls` array on the assistant message,
each entry shaped `{id, type: "function", function: {name, arguments}}`
(`arguments` again a JSON-encoded string), with the client's reply as a
message of `role: "tool"` carrying a `tool_call_id` matching that `id`.
Streaming chunks carry a `delta.tool_calls[].function.arguments`
fragment per chunk, accumulated client-side by array index until a
chunk's `finish_reason` becomes `tool_calls`. Anyone relying on this
paragraph specifically should re-verify it against OpenAI's current
Chat Completions reference before treating it as settled -- it is
recalled, not freshly read, this session.

---

## 3. How each harness sits on top of this layer

### 3.1 Claude Code (Claude Agent SDK)

VERIFIED, `code.claude.com/docs/en/agent-sdk/streaming-output`, fetched
fresh 2026-08-01 -- authoritative for the Claude Agent SDK's own
documented behavior specifically (the layer Claude Code itself is built
on), distinct from §1's claim about the raw Anthropic API those
mechanics wrap.

By default the SDK yields only complete, already-accumulated message
objects -- `AssistantMessage`, plus a `SystemMessage` (session
initialization, and, per its `compact_boundary` subtype, a marker for
when [context compaction](context-compression.md) occurred), and a
terminal `ResultMessage`. Setting `include_partial_messages` (Python) /
`includePartialMessages` (TypeScript) to `true` additionally yields a
`StreamEvent` (Python) / `SDKPartialAssistantMessage` with
`type: "stream_event"` (TypeScript) for **every** raw event described in
§1.5 -- the docs state plainly that this wrapper's `event` field is "the
raw streaming event from the Claude API" and, in the TypeScript type
definition, is typed as `BetaRawMessageStreamEvent`, i.e. the Anthropic
SDK's own event type, not a Claude-Code-specific reshaping of it. The
wrapper adds exactly three fields the raw API event does not carry:
`uuid`, `session_id`, and `parent_tool_use_id` (always `null` on the
main session -- subagent-attributed streaming deltas are documented as
not forwarded at the partial-event level at all; only the later,
complete `AssistantMessage` carries a populated `parent_tool_use_id` for
attributing output to a [subagent](handoff-mechanism.md)).

```mermaid
flowchart TD
    API["Anthropic Messages API SSE\n(message_start ... message_stop, per S1.5)"] --> SDK["Claude Agent SDK\ninclude_partial_messages / includePartialMessages = true"]
    SDK --> SE["StreamEvent / SDKPartialAssistantMessage\nevent = raw BetaRawMessageStreamEvent\n+ uuid, session_id, parent_tool_use_id (null on main session)"]
    SDK --> AM["AssistantMessage\n(complete, accumulated -- always emitted regardless of the flag)"]
    AM --> Exec["Harness executes any tool_use blocks\n(subject to the permission layer)"]
    Exec --> Next["tool_result appended, next Messages API request sent"]
    AM --> RM["ResultMessage\n(turn result / structured_output, per its own known limitation)"]
```

The docs' own documented limitation: structured output "appears only in
the final `ResultMessage.structured_output`, not as streaming deltas" --
i.e. §1's `input_json_delta`-style incremental JSON is available for
ordinary tool calls but not for the SDK's separate structured-output
feature. The message-flow ordering the docs give matches §1.5's SSE
sequence exactly, prefixed by `StreamEvent` wrappers and followed by the
accumulated `AssistantMessage`, then repeating for each further turn
until a `ResultMessage` closes out the exchange -- this is the literal
wire-level substrate that
[agent-loop-implementations.md](agent-loop-implementations.md)'s
turn-by-turn description of Claude Code's loop is built on top of.

Claude Code natively speaks this Anthropic-shaped contract regardless
of backend: BEST CURRENT UNDERSTANDING, UNCONFIRMED (reasoned from, not
directly re-verified against, this session's own fetch) that the same
`BetaRawMessageStreamEvent` typing applies whether the request is served
by the direct Anthropic API, Bedrock, or Vertex -- corroborating,
cross-page evidence from a prior session
([caching.md](caching.md)'s v2.1.211 Bedrock/Foundry prompt-cache-parity
fix) is consistent with those three backends sharing this same
content-block-shaped contract even though their auth, pricing, and TTL
behavior differ, but no source fetched in *this* session states outright
that the raw bytes on the wire are byte-identical Messages API JSON
across all three backends -- only that the SDK's own typed event surface
is Anthropic's own type regardless of which one is in use.

### 3.2 GitHub Copilot CLI

Copilot CLI is closed source; unlike §3.1 and §3.3, no first-party doc
describes its request/response JSON schema directly. Everything below
is inferred from `github.com/github/copilot-cli`'s own `changelog.md`
(fetched fresh this session via `gh api
repos/github/copilot-cli/contents/changelog.md`, grepped for
`tool_call`, `streaming`, `finish_reason`, `Responses API`, `reasoning`),
read as a history of shipped behavior, not a specification -- the same
standing caveat this book applies to Copilot CLI everywhere its
internals are closed (see [retries.md](retries.md) §2.1,
[context-compression.md](context-compression.md) §2,
[caching.md](caching.md) §2 for the identical pattern on other topics).

The changelog names OpenAI's **Responses API** as a real, internally
distinguished provider-protocol family the CLI itself routes against,
not merely a term this page is importing from §2: v1.0.62 (2026-06-13)
lists "Honor `max_output_tokens` for BYOK Responses providers" and "MCP
server names with dots and slashes map to valid Responses API
namespaces" in the same release, and v1.0.52 (2026-05-23) separately
notes "AI Credits usage correctly displays after sessions using the
Responses API" as its own fixed bug -- three independent entries, two
releases apart, all treating "Responses API" as a named internal
category of session rather than a one-off phrase. This is consistent
with Copilot CLI's own multi-model support (Claude, GPT, Gemini,
documented elsewhere in this book's
[configuration.md](configuration.md) and [retries.md](retries.md)
coverage) requiring it to speak more than one upstream wire contract
internally, but the changelog never states its own dispatch architecture
explicitly the way OpenCode's source does in §3.3 -- flag this as BEST
CURRENT UNDERSTANDING, UNCONFIRMED beyond the three bare named facts
above.

The changelog also shows recurring "reasoning effort"/"reasoning
summary"/"reasoning token" entries across dozens of releases (v1.0.62's
"Keep blank lines between reasoning summary sections," v1.0.52's
"Reasoning tokens display as a parenthetical on output token count," and
"Show accurate Anthropic reasoning token counts" among others) --
evidence that a thinking/reasoning content type analogous to §1's
`thinking`/`thinking_delta` blocks or an OpenAI reasoning-model
equivalent is genuinely present and user-configurable
("reasoning effort" as a per-model, per-agent, per-session setting) in
Copilot CLI's own model-facing traffic, but no changelog entry or docs
page fetched this session states the exact wire shape of that content
(a distinct block type, a string field, a separate API parameter) --
this is named as a confirmed *feature* without a confirmed *wire
representation*.

**Adjacent-surface citation, explicitly bounded.** VERIFIED,
`github.com/github/copilot-sdk`'s `docs/auth/byok.md`, fetched fresh
this session -- **the Copilot SDK, a separate, distinct product from
Copilot CLI itself** (the same adjacent-surface caveat
[orchestration.md](orchestration.md) applies to this SDK's Fleet-mode
runtime). Its own `ProviderConfig` documents a `type` field accepting
`"openai" | "azure" | "anthropic"` and a `wireApi` field accepting
`"completions"` (Chat Completions, "broad model compatibility") or
`"responses"` (the newer Responses API, for "multi-turn state
management, tool namespacing, and reasoning support") -- explicitly only
for the OpenAI/Azure provider types, since the same document states
outright: "Anthropic models always use the Messages API regardless of
this setting." This is a real, source-verified three-way protocol
dispatch (Anthropic Messages / OpenAI Chat Completions / OpenAI
Responses) inside a genuinely GitHub-authored product, and it is
architecturally consistent with the three-family split this page
documents in §1-§2 -- but it describes the **Copilot SDK's** dispatch,
not a confirmed description of the **Copilot CLI's** own internal
routing, which remains the BEST CURRENT UNDERSTANDING, UNCONFIRMED
paragraph above it.

### 3.3 OpenCode

VERIFIED, `github.com/anomalyco/opencode`, `dev` branch, fetched fresh
this session via `gh search code` (to locate files) and `curl` against
`raw.githubusercontent.com` (to read full file contents, working around
this session's `gh api`/base64 decoding failure on this platform) --
flagging per this project's standing caveat that `dev` is not a stable
release tag. Unlike §3.2, OpenCode's own multi-provider wire-contract
handling is fully source-verified, not inferred from documentation, and
is the most architecturally explicit of Claude Code, Copilot CLI, and
OpenCode specifically on this exact topic -- §3.4 below covers DeepSeek
Harness's own, differently-pitched contribution to this same question.

`packages/llm/AGENTS.md` (the package's own maintainer-facing design
document, read in full) states the core decomposition directly: a
**route** is "the registered, runnable composition of four orthogonal
pieces" -- **Protocol** (owns request-body construction and the
streaming-event-to-common-event state machine), **Endpoint** (URL
construction), **Auth** (per-request authentication, including
Bedrock-SigV4-style request signing), and **Framing** (bytes to frames;
SSE via `Framing.sse` is shared across protocols, while Bedrock keeps
its own AWS event-stream binary framing). Concrete protocol modules
under `packages/llm/src/protocols/`: `anthropic-messages.ts` (§1's
contract), `openai-chat.ts` and `openai-responses.ts` (§2's two
contracts), `gemini.ts`, `bedrock-converse.ts` (with
`bedrock-event-stream.ts` supplying its distinct binary framing), and
`openai-compatible-chat.ts` -- a route that reuses `OpenAIChat.protocol`
verbatim for any OpenAI-shaped third-party endpoint (DeepSeek, TogetherAI,
Cerebras, Baseten, Fireworks, DeepInfra), which `AGENTS.md` gives as the
concrete payoff of the four-axis split: "each provider deployment is a
5-15 line `Route.make(...)` call instead of a 300-400 line route clone."

```mermaid
flowchart LR
    Req["LLM.request(...)\n(provider-neutral LLMRequest)"] --> Route["Route.make: Protocol + Endpoint + Auth + Framing"]
    Route --> P1["AnthropicMessages.protocol"]
    Route --> P2["OpenAIChat.protocol\n(+ openai-compatible-chat.ts reuse)"]
    Route --> P3["OpenAIResponses.protocol"]
    Route --> P4["Gemini.protocol / BedrockConverse.protocol\n(+ bedrock-event-stream.ts framing)"]
    P1 --> Wire1["real Anthropic Messages SSE\n(content_block_delta, stop_reason)"]
    P2 --> Wire2["real OpenAI-shaped SSE\n(delta.tool_calls / function_call_arguments, finish_reason)"]
    Wire1 --> Norm["per-protocol mapFinishReason()\n-> shared FinishReason enum"]
    Wire2 --> Norm
    Norm --> Event["normalized LLMEvent stream\n(tool-call, tool-result, finish, provider-error, ...)"]
    Event --> Loop["session turn processor\n(packages/opencode/src/session)"]
```

**The normalized event vocabulary.** VERIFIED,
`packages/llm/src/schema/events.ts` (full file read this session). Every
protocol's stream parser -- regardless of which of §1/§2's wire formats
it is reading -- emits the same tagged union of `LLMEvent`s:
`step-start`, `text-start`/`text-delta`/`text-end`,
`reasoning-start`/`reasoning-delta`/`reasoning-end`,
`tool-input-start`/`tool-input-delta`/`tool-input-end`, `tool-call`,
`tool-result`, `tool-error`, `step-finish`, `finish`, and
`provider-error`. This is the same content-block-versus-tool-call
distinction §1 and §2 draw at the wire level, re-expressed as one
shared, provider-neutral event alphabet -- `tool-input-delta` is
OpenCode's single normalized name for both Anthropic's
`input_json_delta` and OpenAI's `function_call_arguments.delta`/
`tool_calls[].function.arguments` chunk streams.

**The `FinishReason` normalization, read directly from two separate
protocol files.** VERIFIED, `packages/llm/src/schema/ids.ts`: the shared
enum is `Schema.Literals(["stop", "length", "tool-calls",
"content-filter", "error", "unknown"])`. Each protocol's own
`mapFinishReason()` function, read in full from source, maps its
provider's native vocabulary onto this one shared enum:

| Provider-native value | Protocol file | Mapped `FinishReason` |
|---|---|---|
| `end_turn`, `stop_sequence`, `pause_turn` | `anthropic-messages.ts` | `"stop"` |
| `max_tokens` | `anthropic-messages.ts` | `"length"` |
| `tool_use` | `anthropic-messages.ts` | `"tool-calls"` |
| `refusal` | `anthropic-messages.ts` | `"content-filter"` |
| (anything else, incl. `model_context_window_exceeded`) | `anthropic-messages.ts` | `"unknown"` |
| `stop` | `openai-chat.ts` | `"stop"` |
| `length` | `openai-chat.ts` | `"length"` |
| `content_filter` | `openai-chat.ts` | `"content-filter"` |
| `function_call`, `tool_calls` | `openai-chat.ts` | `"tool-calls"` |
| (anything else) | `openai-chat.ts` | `"unknown"` |

This table is a direct, source-read demonstration of the exact
normalization problem §1 and §2 describe in the abstract: Anthropic's
seven-value, single-field `stop_reason` and OpenAI's four-value
`finish_reason` are two genuinely different enumerations (notably,
Anthropic's `pause_turn` collapses into plain `"stop"` here, discarding
the "resume this specific turn" nuance §1.4 documents, and Anthropic has
no native analogue at all to being folded into `"error"`, since
OpenCode's own enum reserves that value for transport/provider failures
rather than any Anthropic `stop_reason` value).

**Provider-executed (hosted) tools pass through untouched.** VERIFIED,
`packages/llm/AGENTS.md`: Anthropic's `web_search`/`code_execution`/
`web_fetch` and OpenAI Responses' `web_search_call`/`file_search_call`/
`code_interpreter_call`/`mcp_call`/`local_shell_call`/
`image_generation_call`/`computer_use_call` all surface as an ordinary
`tool-call` event carrying `providerExecuted: true`, with a matching
`tool-result` event also flagged `providerExecuted: true` -- callers are
instructed to detect this flag and **skip local dispatch** entirely (no
handler invoked, no "unknown tool" `tool-error` raised), since the
provider already ran the tool server-side. Continuing a conversation
afterward is itself protocol-specific: "Anthropic encodes them back as
`server_tool_use` + `web_search_tool_result` ... blocks; OpenAI Responses
callers typically use `previous_response_id` instead of resending hosted
tool items" -- a concrete instance of the two contracts' shapes leaking
into how a harness must continue a conversation, not just how it parses
one.

**The `<system-update>` chronological-system-message fallback.** VERIFIED,
`packages/llm/AGENTS.md`: OpenCode's own `Message.system(...)` operator
represents a provider-neutral, mid-conversation system update -- the
same wire slot §1.2 names as Anthropic's dedicated mid-conversation
`"system"` role. Because that native role is model/route-specific
(`AGENTS.md` names it as natively lowered only for Anthropic Messages on
`claude-opus-4-8`), every other route lowers the same operator "in place
into ordinary user-compatible text using this stable escaped
representation": a plain-text block wrapped in literal
`<system-update>...</system-update>` tags, chosen because it "preserves
ordering while visibly lowering authority" when the underlying wire
format has no dedicated slot for it. `AGENTS.md` explicitly warns against
inserting untrusted content (retrieved documents, tool output, web
content) into this privileged channel -- keeping it strictly for the
harness's own operator-issued updates.

**Two execution paths converge on the same event alphabet.**
`packages/llm/AGENTS.md` names `packages/opencode/src/session/llm.ts` as
"the session-owned orchestration layer that decides whether a request
uses AI SDK or this package's native route runtime," with
`native-request.ts` lowering session data into this package's own
`LLMRequest`, `native-runtime.ts` executing it via the route pipeline
described above, and `ai-sdk.ts` separately "converting AI SDK stream
parts into this package's shared `LLMEvent`s" for the default path that
still goes through the third-party Vercel AI SDK rather than OpenCode's
own native protocol implementations. VERIFIED corroboration from
`packages/opencode/src/session/message-v2.ts` (full file read this
session): the session layer converts stored `WithParts` message rows
into the AI SDK's own `UIMessage`/`ModelMessage` shapes via a
`toModelMessagesEffect` function whose logic includes a documented,
provider-specific media-in-tool-result workaround -- because
"OpenAI-compatible APIs only support string content in tool results,"
media attached to a tool's output is stripped out and re-injected as a
synthetic follow-up user message (prefixed
`SYNTHETIC_ATTACHMENT_PROMPT = "Attached media from tool result:"`) for
any model whose `model.api.npm` package does not appear in a hard-coded
allow-list (`@ai-sdk/anthropic`, `@ai-sdk/openai`,
`@ai-sdk/amazon-bedrock/mantle` unconditionally; `@ai-sdk/amazon-bedrock`
and `@ai-sdk/xai` only for image attachments; `@ai-sdk/google` only for
`gemini-3`-family models) -- a second, independent, source-verified
instance of §1 vs §2's contract differences (here, specifically:
Anthropic's `tool_result` content array accepting arbitrary block types
vs. several OpenAI-compatible surfaces accepting only a string) forcing
a harness to actively paper over the gap rather than merely translate
field names.

### 3.4 DeepSeek Harness

VERIFIED, fetched 20 August 2026 directly from `deepseek-ai/deepseek-harness`
(`master` branch) -- `docs/capability-seams.md`, `docs/glossary.md`, and
`docs/architecture.md`. DeepSeek Harness (`dsh`, MIT-licensed, in developer
preview as of this fetch -- see [Hooks and lifecycle
extensibility](hooks-lifecycle-extensibility.md) §4 for this book's fuller
introduction to the harness and its Cordis plugin substrate, not repeated
here) names, as an explicit, first-class architectural term, the exact
provider-swap pattern this page's §3.3 already found OpenCode's source
exhibiting *without* a comparable name: a **capability seam**. The docs
define it as three interdependent roles -- a **Service Definition** (the
package declaring the interface a seam promises to expose), one or more
**Service Providers** (packages implementing that interface), and one or
more **Consumers** (packages that depend on the seam's interface without
knowing which provider is mounted underneath it). `ctx.llm` is the seam
governing exactly the wire-contract question this page is about: its
Service Definition specifies what an LLM-request capability must expose,
and the harness ships (at minimum) three real, interchangeable Providers
against it -- `llm-deepseek`, `llm-pi-ai`, and `llm-replay` (a deterministic,
recorded-fixture provider, functionally analogous in purpose to
[Evals and testing a harness](evals-and-testing-a-harness.md)'s coverage of
OpenCode's own `@opencode-ai/http-recorder` VCR-style cassette package,
though DeepSeek's docs frame it as a swappable seam provider rather than a
dedicated test package). The agent loop itself is named directly as the
seam's Consumer, reaching the currently-mounted provider through a
provider-neutral interface it never inspects to determine which concrete
wire contract (Anthropic Messages-shaped, OpenAI-shaped, or something else
entirely) is actually in play underneath. The docs state the architectural
payoff in one line: "Seams are why one provider swap changes the whole
product" -- swapping the mounted `ctx.llm` provider changes what speaks to
the model with no code change required in the agent loop that consumes it.

This three-role decomposition is not merely a vocabulary restatement of
§3.3's four-axis `Protocol`/`Endpoint`/`Auth`/`Framing` split -- it operates
one level of abstraction higher. OpenCode's four axes describe *how a
single route is assembled internally* (which URL, which auth scheme, which
byte-framing, which request-body shape); DeepSeek's capability-seam
vocabulary instead names *the substitutability boundary itself*, independent
of how many axes a given provider's own implementation happens to need
internally. The two are compatible, not competing: an OpenCode-style
`Route.make(Protocol, Endpoint, Auth, Framing)` composition is a plausible
concrete shape a `ctx.llm` Service Provider could take internally, but
DeepSeek's docs do not decompose their own `llm-deepseek`/`llm-pi-ai`
providers into named axes the way `packages/llm/AGENTS.md` does for
OpenCode's routes -- so this page treats the seam vocabulary as a naming
contribution over an already-independently-verified pattern, not as
evidence that DeepSeek's own providers are internally structured the same
four-axis way OpenCode's are. The architecture doc gives a matching rule for
when something should **not** be split into a seam at all: `ctx.sessions`
(the append-only session-event log documented in [Session & transcript
persistence](session-persistence.md) §4) and `ctx.invariants` (package-
attributed checks) are deliberately kept as **core services** rather than
seams, on the stated principle that a seam exists specifically where
deployment-time or provider-time substitutability is the actual design
point -- not wherever an interface merely exists.

### 3.5 pi (`@earendil-works/pi-ai`)

VERIFIED, fetched 20 August 2026 directly from `github.com/earendil-works/pi`, `main`
branch: `packages/ai/README.md` in full (a 513+-line first-party package README, not
inferred behavior), cross-referenced against `packages/coding-agent/docs/models.md` and
`packages/coding-agent/docs/providers.md` for the config-facing side of the same
abstraction. Like OpenCode (§3.3), pi's own multi-provider layer is source-README-
documented at genuine implementation precision rather than inferred from changelog
entries the way Copilot CLI's is (§3.2) -- the README itself states the package's stated
purpose directly: "Unified LLM API with provider collections, automatic auth resolution,
token and cost tracking, and simple context persistence and hand-off to other models
mid-session," with the explicit design constraint that it "only includes models that
support tool calling (function calling), as this is essential for agentic workflows."

**Four wire-protocol families, the same set this page's own §1/§2 structure already
organizes around.** `pi-ai` names, as real internal API-type discriminators (both in
`models.json`'s own `api` field, per `models.md`, and in its own provider factories),
exactly the same four protocol families OpenCode's `packages/llm/AGENTS.md` decomposes
its routes around (§3.3): `openai-completions` (OpenAI Chat Completions, described in
`models.md` as "most compatible" -- the fallback shape for third-party OpenAI-compatible
servers such as Ollama, vLLM, and LM Studio), `openai-responses` (OpenAI's newer Responses
API, §2), `anthropic-messages` (§1), and `google-generative-ai`. Unlike OpenCode's
`Route.make(Protocol, Endpoint, Auth, Framing)` four-*axis* composition, pi's own
documented model does not name a comparably explicit endpoint/auth/framing decomposition
for constructing a route -- the `api` field alone selects the wire contract, with
per-provider `baseUrl`/`apiKey`/`headers`/`compat` fields layered on as configuration
rather than as named architectural axes -- so treat pi's provider abstraction as
covering the *same protocol-family ground* §1-§2 and OpenCode's §3.3 already establish,
without assuming it is internally structured the same four-axis way.

```mermaid
flowchart LR
    Ctx["pi-ai Context\n(systemPrompt + messages + tools)"] --> Stream["models.stream(model, context)"]
    Stream --> P1["anthropic-messages\nprotocol"]
    Stream --> P2["openai-completions\nprotocol"]
    Stream --> P3["openai-responses\nprotocol"]
    Stream --> P4["google-generative-ai\nprotocol"]
    P1 --> Norm["normalized StreamEvent union:\nstart / text_* / thinking_* /\ntoolcall_* / done / error"]
    P2 --> Norm
    P3 --> Norm
    P4 --> Norm
    Norm --> Final["AssistantMessage\n(content blocks + 5-value stopReason + usage/cost)"]
```

**A normalized `StreamEvent` union, directly comparable to OpenCode's `LLMEvent`.**
VERIFIED, the README's own Quick Start streaming example: every provider's stream,
regardless of which of the four wire families above produced it, yields the same tagged
event sequence -- `start`, `text_start`/`text_delta`/`text_end`,
`thinking_start`/`thinking_delta`/`thinking_end`, `toolcall_start`/`toolcall_delta`/
`toolcall_end`, `done`, and `error`. This is architecturally the same move OpenCode's
`LLMEvent` tagged union makes (§3.3) -- one shared, provider-neutral event alphabet
standing in for however many distinct wire-level event names the four underlying
protocols actually use -- with `toolcall_delta` as pi's own single normalized name for
both Anthropic's `input_json_delta` and OpenAI's `function_call_arguments.delta`/
`tool_calls[].function.arguments` partial-JSON streams, the exact same normalization
OpenCode's `tool-input-delta` performs (§3.3). `toolcall_end` carries the fully assembled
`toolCall.arguments` object (already parsed, not a raw string the caller must
`JSON.parse()` themselves), consistent with pi's Quick Start example passing it directly
into a tool dispatcher without a parsing step.

**A five-value `stopReason` enum, the leanest of the three normalized enumerations this
page has now catalogued.** VERIFIED, the README's own "Stop Reasons" section: every
`AssistantMessage` carries a `stopReason` of `"stop"` (final message for the turn),
`"length"` (hit the max-token limit), `"toolUse"` (calling tools, expects results),
`"error"`, or `"aborted"` (cancelled via an `AbortSignal`) -- plus a sixth,
partial-message-only value, `"pending"`, reserved for a still-streaming message whose
final reason is not yet known and explicitly never persisted to a completed message
(cross-referenced against [session-persistence.md](session-persistence.md) §5.2's own
`StopReason` type listing, which names the identical six values from the session-format
angle). Set directly alongside the other two enumerations this book has now fully
catalogued -- Anthropic's own seven-value `stop_reason` (§1.3), OpenAI's four-value
`finish_reason` (§2.2), and OpenCode's shared six-value `FinishReason` (§3.3) -- pi's
five terminal values (excluding `"pending"`, which no other harness's own enum needs a
placeholder for since none of them documents an equivalent partial-message state as part
of the enum itself) is the smallest surface of the four, folding Anthropic's
`pause_turn`/`refusal`/`model_context_window_exceeded` distinctions and OpenAI's
`content_filter` value down into its own plain `"error"` rather than preserving them as
separate cases -- the same *kind* of lossy-but-simplifying normalization OpenCode's own
`mapFinishReason()` performs (§3.3's table), reached independently by a second,
unrelated engineering team.

**Auth resolution and header merging are handled as an explicit, ordered pipeline,
distinct from Copilot CLI's undocumented internals (§3.2) and closer in spirit to
OpenCode's fully-specified route composition (§3.3).** `models.stream()`/`complete()`
resolve auth "through the owning provider" (environment variable, a stored credential
from `/login`, or a refreshed OAuth token) and merge it into the request, with an
explicit per-request override always winning over whatever the provider would have
resolved on its own. A separate, `Models`-level `transformHeaders` option runs once, after
provider-auth headers, `model.headers`, and any explicit `options.headers` have already
been merged (case-insensitively, with a later stage always able to override an earlier
one, and a `null` value able to suppress a lower-level default entirely) but strictly
*before* the request is actually dispatched to a `Provider.stream*()` implementation --
the documented ordering is `provider auth headers -> model.headers -> explicit
options.headers -> transformHeaders -> Provider.stream*()`. A `CredentialStore`
abstraction (`read`/`list`/`modify`/`delete`, one type-tagged credential per provider)
backs this: OAuth token refresh is explicitly serialized through the store's own
`modify()` read-modify-write operation "so concurrent requests and processes cannot
double-refresh a rotated token," and a stored credential is documented as *owning* its
provider outright -- "environment variables are only consulted when nothing is stored,
and a failed refresh never silently falls back to an env key," a fail-closed rather than
fail-open posture on credential resolution worth setting alongside
[auth-and-usage-accounting.md](auth-and-usage-accounting.md)'s own pi section, which
covers the credential-storage surface this paragraph's resolution pipeline sits on top
of, not repeated here.

**Error handling never throws out of the stream.** VERIFIED: a request failure
(including an abort or a tool-argument validation failure) surfaces as an ordinary
`error`-typed `StreamEvent` mid-stream, and the *final* accumulated message itself also
carries `stopReason: "error"`/`"aborted"` plus whatever partial `content` and partial
`usage`/`cost` had already accumulated before the failure -- a caller that only inspects
the final message, never touching the event stream directly, still gets a fully
populated, if partial, `AssistantMessage` to reason about rather than a thrown exception
propagating out of the streaming call itself. This is a materially different error-
surfacing discipline from what this page's other four contract descriptions state (none
of §1/§2/§3.1-§3.4 documents an equivalent "the terminal object is always well-formed,
even on failure" guarantee as an explicit design point, though none rules it out either
-- this is offered as a positive finding for pi specifically, not a comparative claim
about the others' absence of the same behavior).

**A direct, named cross-harness dependency worth flagging explicitly.** §3.4 above
already names `llm-pi-ai` as one of the real Service Providers DeepSeek Harness ships for
its own `ctx.llm` capability seam, alongside `llm-deepseek` and the fixture-replaying
`llm-replay`. That name is not a coincidence of vocabulary: it is DeepSeek Harness
depending directly on pi's own `@earendil-works/pi-ai` package (the exact package this
section documents) as one of its swappable LLM-request providers -- a genuine, concrete
instance of one harness in this book consuming another's own multi-provider abstraction
as a mounted implementation, rather than merely resembling it architecturally. This
session did not additionally verify the `llm-pi-ai` provider's own source (only
DeepSeek's docs naming it, per §3.4's citation), so treat "DeepSeek wraps pi-ai
unmodified" as the plain reading of the provider's name rather than as independently
confirmed integration-code detail.

### 3.6 Hermes Agent (Nous Research)

VERIFIED, fetched 1 September 2026 directly from `github.com/NousResearch/hermes-agent`
(`main` branch): `pyproject.toml` (in full), `agent/chat_completion_helpers.py` (the
full 5,109-line file), `agent/transports/base.py`, `agent/transports/types.py`, and
`agent/error_classifier.py` (the full ~99 KB file), all read via `curl` against
`raw.githubusercontent.com`, cross-referenced against Hermes' own documentation site,
`hermes-agent.nousresearch.com/docs/user-guide/features/fallback-providers.md` and
`.../provider-routing.md`, both fetched fresh this session (WebFetch/`curl`). Unlike
§3.2's closed-source Copilot CLI, Hermes' wire-contract handling is fully
source-verified at implementation precision -- the deepest level of verification this
page achieves for any harness alongside OpenCode (§3.3) -- while also, uniquely among
the six harnesses this page now covers, shipping user-facing documentation that
independently corroborates the source-level retry/fallback behavior rather than only
describing configuration syntax. Hermes Agent is a sixth, independent, self-hosted
product -- see [Permissions & sandboxing architecture](permissions-and-sandboxing.md)
§6 and [Hooks and lifecycle extensibility](hooks-lifecycle-extensibility.md) §6 for
this book's fuller architectural introduction to the harness itself, not repeated here.

**The OpenAI Python SDK as Hermes' default transport, regardless of which provider is
actually being spoken to.** `pyproject.toml`'s own dependency-scope comment states the
rule directly: "Scope rule: only packages used by EVERY hermes session belong here" in
`[project.dependencies]`, and `openai==2.24.0` -- exact-pinned, per the file's own
supply-chain-hardening rationale citing the 2026-05 `mistralai` PyPI worm incident -- is
the one LLM-client package in that core list. `anthropic==0.87.0` is instead declared as
an *optional extra* ("Native Anthropic provider — only needed when provider=anthropic
(not via OpenRouter or other aggregators)"), lazy-installed on demand. This means every
OpenAI-Chat-Completions-shaped backend Hermes talks to by default -- OpenRouter, Nous
Portal, GitHub Models, NVIDIA NIM, Kimi/Moonshot, TokenHub, LM Studio, Qwen Portal,
xAI's chat-completions endpoint -- is dispatched through the same one pinned OpenAI SDK
instance (`request_client.chat.completions.create(**api_kwargs)`, read directly at
`chat_completion_helpers.py:1003`), and that the native Anthropic SDK is reserved for
the one `api_mode` (`anthropic_messages`) that talks to Anthropic's own Messages API
(§1) directly rather than through an aggregator. `pyproject.toml`'s own comment on the
`pydantic` version bump additionally confirms that OpenAI's newer **Responses API**
(§2) is reached through that *same* `openai==2.24.0` package's own `.responses`
resource, not a separate client: the comment names a segfault "when the OpenAI SDK's
Responses API resource is exercised from a non-main thread, which is the
`codex_responses` dispatch in `agent/chat_completion_helpers.py:_call`." AWS Bedrock is
the one genuinely separate transport: `build_api_kwargs`'s own comment states plainly
that `bedrock_converse` mode "bypasses the OpenAI client entirely," calling boto3's
native `client.converse()` / `converse_stream()` Bedrock Converse API directly, with
`agent/bedrock_adapter.py`'s `normalize_converse_response()` producing "an
OpenAI-compatible SimpleNamespace so the rest of the agent loop can treat bedrock
responses like chat_completions responses" -- normalizing at the *response* layer for
Bedrock specifically, rather than Bedrock speaking through any shared request-building
transport class. Four `api_mode` values in total, read directly out of
`build_api_kwargs`'s own branching (`chat_completion_helpers.py:1829-2156`):
`anthropic_messages`, `bedrock_converse`, `codex_responses`, and the default
`chat_completions`.

```mermaid
flowchart TD
    Build["build_api_kwargs(agent, messages, tools)"] --> Mode{api_mode}
    Mode -->|anthropic_messages| Ant["anthropic SDK (extra)\nclient.messages.create/.stream()\n-> Anthropic Messages API, S1"]
    Mode -->|bedrock_converse| Bed["boto3 bedrock-runtime client\nconverse() / converse_stream()\n-- bypasses OpenAI client entirely"]
    Mode -->|codex_responses| Codex["openai SDK (core)\n.responses resource\n-> OpenAI Responses API, S2"]
    Mode -->|chat_completions default| Chat["openai SDK (core)\n.chat.completions resource\n-> OpenAI Chat Completions,\nspoken to OpenRouter/Nous Portal/\nGitHub Models/NVIDIA NIM/Kimi/\nxAI/LM Studio/Qwen Portal etc."]
    Ant --> Transport["ProviderTransport:\nconvert_messages -> convert_tools\n-> build_kwargs -> normalize_response"]
    Codex --> Transport
    Chat --> Transport
    Bed --> BedNorm["normalize_converse_response()\n(response-layer only, no shared\nProviderTransport class)"]
    Transport --> NR["NormalizedResponse\n(content, tool_calls, finish_reason,\nreasoning, usage, provider_data)"]
    BedNorm --> NR
    NR --> Loop["agent loop (run_agent.py)"]
```

**The `ProviderTransport` pipeline and a `NormalizedResponse` whose canonical
`finish_reason` is OpenAI's own four-value vocabulary.** `agent/transports/base.py`'s
`ProviderTransport` abstract base class names its own scope explicitly in its module
docstring: a transport owns exactly "`convert_messages → convert_tools → build_kwargs →
normalize_response`" for one `api_mode`, and does **not** own "client construction,
streaming, credential refresh, prompt caching, interrupt handling, or retry logic --
those stay on `AIAgent`." This is a narrower slice of responsibility than OpenCode's own
four-axis `Route.make(Protocol, Endpoint, Auth, Framing)` composition (§3.3), which
folds endpoint construction and per-request auth into the same route object: Hermes
keeps request/response *shape* conversion in the transport layer and pushes auth,
client lifecycle, and retry one level up onto the agent object itself, a different
division of the same normalization problem rather than a thinner version of OpenCode's.
`agent/transports/types.py`'s shared dataclasses give the transport layer's shared
output vocabulary directly: `ToolCall` (`id`, `name`, a JSON-**string** `arguments`
field -- the OpenAI-shaped, not Anthropic-shaped, convention per §2.1 -- plus a
`provider_data` dict carrying protocol-specific extras such as Codex's
`call_id`/`response_item_id` or Gemini's `thought_signature`), `Usage`
(`prompt_tokens`/`completion_tokens`/`total_tokens`/`cached_tokens`), and
`NormalizedResponse` (`content`, `tool_calls`, `finish_reason`, `reasoning`, `usage`,
`provider_data`). The dataclass's own inline comment names `finish_reason`'s canonical
value set outright: `"stop"`, `"tool_calls"`, `"length"`, `"content_filter"` -- this is
**OpenAI's own four-value Chat Completions/Responses vocabulary** (§2.2) adopted
verbatim as Hermes' normalization target, in contrast to OpenCode's bespoke six-value
`FinishReason` enum (§3.3) or pi's own five-terminal-plus-`"pending"` `stopReason` enum
(§3.5) -- both of the other two source-verified harnesses on this page invent their own
enum rather than canonicalizing onto either upstream vocabulary directly. The generic
`map_finish_reason(reason, mapping)` helper each transport's own mapping dict feeds
through falls back to `"stop"` for an unrecognized or `None` reason -- a more permissive
default-on-unknown behavior than OpenCode's dedicated `"unknown"` bucket (§3.3's table),
worth flagging as a real, if narrow, normalization-fidelity difference: an
unrecognized stop signal reads as ordinary successful completion in Hermes' scheme
rather than as its own distinguishable case.

**Streaming across all four `api_mode` values, plus a harness-level "discard and
reconnect" recovery strategy distinct from Anthropic's own documented resumption
procedure.** `interruptible_streaming_api_call`'s own docstring enumerates all four
paths directly: `chat_completions` sets `stream: true` against an OpenAI-compatible
endpoint through the `openai` SDK; `anthropic_messages` opens
`request_client.messages.stream(**final_kwargs)` -- confirmed read directly at
`chat_completion_helpers.py:4690` -- the native Anthropic SDK's own streaming context
manager, whose `get_final_message()` accumulator (also read directly) is what
reconstructs the same `content_block_*`/`message_delta` sequence §1.5 documents at the
wire level; `codex_responses` delegates to `_run_codex_stream`, reached through the
`openai` SDK's own `.responses` streaming surface (§2.3's `response.*` event names);
and `bedrock_converse` uses boto3's `converse_stream()`, whose own worker-thread
comment warns it "blocks inside `for event in event_stream` with NO read timeout,"
requiring Hermes' own stale-timeout watchdog to detect a wedged Bedrock stream that the
SDK itself will not time out. A stream-level retry budget,
`env_int("HERMES_STREAM_RETRIES", 2)` (three total attempts by default,
user-configurable), governs a documented, code-level distinction not found on this
page's other five harness sections: a stream interrupted **mid-tool-call** (tracked via
a `_can_silent_retry` guard) triggers a **silent reconnect** -- partial-JSON
accumulators are cleared, a user-visible "⚠ Connection dropped mid tool-call;
reconnecting…" notice fires, the stale request client is closed, and the identical
streaming request is resent over a fresh connection, discarding the partial delivery
entirely -- rather than attempting anything resembling Anthropic's own documented
partial-content continuation procedure (§1.5's Claude-4.5-vs-4.6 resume-as-assistant-
prefix-vs-resume-as-new-user-message split). This is a harness-level recovery choice
operating a layer above where Anthropic's own resumption mechanism would even apply,
not a violation of it: Hermes chooses to restart the whole streaming call rather than
splice a captured partial text block back in. A related, provider-shaped edge case is
also handled explicitly: some OpenRouter-fronted providers encode a genuine API error
as SSE `data:` payload content instead of raising an SDK-level exception, and Hermes'
own `ProviderStreamError` class plus `_parse_provider_sse_events`/
`_provider_stream_error_from_text` helpers parse that raw SSE text back into a
structured, classifiable error rather than letting it surface as an opaque JSON-decode
failure.

**The `FailoverReason` error taxonomy and its exponential-backoff, per-turn fallback
logic.** `agent/error_classifier.py`'s own module docstring states its purpose plainly:
"a structured taxonomy of API errors and a priority-ordered classification pipeline
that determines the correct recovery action (retry, rotate credential, fallback to
another provider, compress context, or abort)." The `FailoverReason` enum names
roughly twenty distinct failure classes grouped by category -- `auth`/`auth_permanent`
(transient-vs-permanent authentication failure), `billing`/`rate_limit`/
`upstream_rate_limit` (a 429 attributable to the aggregator's *upstream model*, not the
caller's own key, triggering model fallback rather than credential rotation),
`overloaded`/`server_error` (503/529 vs. 500/502), `timeout`/`ssl_cert_verification`
(the latter explicitly non-retryable, since a TLS handshake failure "is deterministic
for the host" and retrying only reproduces it), `context_overflow`/`payload_too_large`/
`image_too_large`/`image_corrupt`, `model_not_found`/`provider_policy_blocked`/
`content_policy_blocked`, `format_error`/`invalid_encrypted_content`/
`multimodal_tool_content_unsupported`, several Anthropic- and llama.cpp-specific
classes (`thinking_signature`, `long_context_tier`,
`oauth_long_context_beta_forbidden`, `llama_cpp_grammar_pattern`), and a catch-all
`unknown` (retryable with backoff). Each classification returns a `ClassifiedError`
dataclass carrying not just the `reason` but four boolean recovery-hint fields the
retry loop consults directly rather than re-deriving them itself: `retryable`,
`should_compress`, `should_rotate_credential`, and `should_fallback`.
`classify_api_error`'s own docstring names its priority-ordered pipeline as nine
stages (numbered 0-8): a plugin `transform_api_error_classification` hook first (an
explicit hook-driven extension point onto this exact classification decision, per
[Hooks and lifecycle extensibility](hooks-lifecycle-extensibility.md)'s own territory),
then provider-specific pattern special-cases, HTTP-status-aware refinement, error-code
classification, message-pattern matching, SSL/TLS transient-alert detection,
server-disconnect-plus-large-session heuristics treated as context overflow, generic
transport-error heuristics, and finally the `unknown` fallback. `try_activate_fallback`
implements the documented exponential backoff directly: `60 * (2 ** backoff_count)`
seconds, capped at 14,400 (four hours), escalating only on *consecutive* rate-limit/
billing failures and reset by a successful primary-provider restore -- so a single 429
only benches the primary for 60 seconds, not the full four-hour ceiling. Hermes' own
`fallback-providers.md` documentation corroborates this from the user-facing side
without contradicting the source: rate limits and server errors trigger fallback "after
exhausting retry attempts," while auth failures (401/403) and not-found (404) trigger
it "immediately (no point retrying)" -- i.e. `retryable=False` in the classifier's own
terms -- and fallback is documented as strictly **per-turn**, activating at most once
per user turn and restoring the primary automatically on the next turn, with a
"reset-aware" refinement that skips a doomed primary retry when the primary's own
credential reports a known rate-limit-reset timestamp (Claude Pro/Max's 5-hour windows,
Codex weekly limits) that has not yet elapsed. This same trigger-and-backoff machinery
is what activates the credential-pool rotation
([Model routing / selection](model-routing-and-selection.md) §5.2 documents the pool's
own `fill_first`/`round_robin`/`least_used`/`random` selection policy once rotation is
triggered) -- this page documents the failure classification that *decides* to rotate;
that page documents what happens once it does.

**`extra_body` as the generic escape hatch for aggregator-specific request fields.**
Hermes' own `provider-routing.md` documentation states the wire mechanism directly:
OpenRouter/Nous Portal provider-routing preferences (`sort`, `only`, `ignore`, `order`,
`require_parameters`, `data_collection`) are "passed... via the `extra_body.provider`
field," with the docs explicitly naming `extra_body` as "the OpenAI Python SDK
argument" that "becomes the top-level `provider` object in the JSON request." This
confirms, from Hermes' own documentation rather than inferred behavior, that the
`openai` SDK's own generic `extra_body` kwarg -- a mechanism for injecting fields the
SDK's typed parameters do not model -- is Hermes' standard channel for aggregator-level
routing metadata riding on top of an otherwise-ordinary OpenAI Chat Completions request,
distinct from the `should_fallback`/provider-swap machinery described immediately above:
provider routing selects *which upstream sub-provider* an aggregator uses for a request
that is still going to the same aggregator, where fallback swaps the aggregator/provider
entirely.

---

## 4. Synthesis

| Dimension | Anthropic Messages API | OpenAI Chat Completions / Responses API |
|---|---|---|
| Tool call representation | typed `tool_use` content block inside the `content` array, `input` already a parsed object | `tool_calls`/output-item array on the assistant message/output, `arguments` a JSON-**encoded string** the caller must parse |
| Tool result representation | typed `tool_result` content block, structured `is_error` boolean | `role: "tool"` message, unstructured `content` (string) |
| Turn-stop vocabulary | 7-value `stop_reason` (`end_turn`, `max_tokens`, `stop_sequence`, `tool_use`, `pause_turn`, `refusal`, `model_context_window_exceeded`) | 4-value `finish_reason` (Responses/Chat: `stop`, `length`, `tool_calls`, `content_filter`) |
| Streaming tool-input delivery | `content_block_delta` events of `delta.type: "input_json_delta"`, partial JSON strings keyed by block `index` | `response.function_call_arguments.delta` (Responses) or `delta.tool_calls[].function.arguments` (Chat Completions, unconfirmed this session), partial JSON strings |
| Reasoning/thinking content | `thinking`/`redacted_thinking` blocks, `thinking_delta` + terminal `signature_delta` | reasoning-effort-configurable, but this page found no OpenAI wire-shape citation fetched this session for its own reasoning content type |
| Mid-conversation system updates | native `"system"`-role message, distinguished from the top-level `system` request field | not documented on the pages fetched this session |

| Harness | How it sits on this layer |
|---|---|
| Claude Code (Agent SDK) | Wraps the raw Anthropic SSE events (§1.5) in a `StreamEvent`/`SDKPartialAssistantMessage` carrying `parent_tool_use_id`/`session_id`/`uuid`, alongside always-emitted accumulated `AssistantMessage`/`ResultMessage` objects; the wrapped `event` field is Anthropic's own SDK type, unmodified |
| Copilot CLI | Closed source; changelog confirms "Responses API" as a real internally-named provider-protocol category (BYOK sessions, MCP namespace mapping, AI-credits display) across three separate releases, and confirms a reasoning-content *feature* exists, but does not document the exact request/response schema; the separate, adjacent Copilot SDK product documents an explicit three-way `anthropic`/`openai` (`completions`)/`openai` (`responses`) dispatch that is architecturally consistent with, but not proof of, Copilot CLI's own internal routing |
| OpenCode | Fully source-verified: a four-axis `Protocol`/`Endpoint`/`Auth`/`Framing` route composition, one protocol module per wire contract (`anthropic-messages.ts`, `openai-chat.ts`, `openai-responses.ts`, `gemini.ts`, `bedrock-converse.ts`), each with its own `mapFinishReason()` normalizing into one shared six-value `FinishReason` enum and one shared `LLMEvent` tagged union, plus explicit, source-documented workarounds where the contracts genuinely disagree (hosted-tool continuation shape, tool-result media support, native vs. text-wrapped mid-conversation system updates) |
| DeepSeek Harness | Fully source-verified (docs, not implementation code, for this specific point): names the substitutability boundary itself, one level of abstraction above OpenCode's four axes, as a **capability seam** -- a Service Definition/Provider/Consumer three-role unit, with `ctx.llm` as the seam governing this page's own subject, real interchangeable providers (`llm-deepseek`, `llm-pi-ai`, `llm-replay`) mounted underneath a provider-neutral Consumer interface the agent loop itself never inspects |
| pi | Fully README-verified (a first-party package README documenting the implementation at genuine precision, though this session did not additionally cross-check pi's own TypeScript source): the same four wire-protocol families (`anthropic-messages`/`openai-completions`/`openai-responses`/`google-generative-ai`) as named `api` discriminators, a normalized `StreamEvent` tagged union directly comparable to OpenCode's `LLMEvent`, a five-terminal-value `stopReason` enum (the leanest of the four enumerations this page catalogues) plus a sixth partial-only `"pending"` value, an explicit ordered auth/header-merge pipeline with a fail-closed stored-credential-owns-its-provider rule, and a documented guarantee that stream failures never throw -- they surface as an `error` event plus a still-well-formed final message |
| Hermes Agent | Fully source-verified (`agent/chat_completion_helpers.py`, `agent/transports/base.py`/`types.py`, `agent/error_classifier.py`): one pinned `openai==2.24.0` SDK instance serves both of §2's OpenAI contracts (Chat Completions for the `chat_completions` default, the same package's `.responses` resource for `codex_responses`) across every OpenAI-compatible aggregator/gateway, a separate optional `anthropic==0.87.0` SDK serves §1's contract natively, and AWS Bedrock's Converse API is reached via boto3 directly, bypassing both SDKs; a `ProviderTransport` ABC (`convert_messages → convert_tools → build_kwargs → normalize_response`) normalizes onto a shared `NormalizedResponse` whose `finish_reason` canonicalizes onto **OpenAI's own** four-value vocabulary rather than a bespoke enum; a ~20-member `FailoverReason` taxonomy plus a `ClassifiedError`'s four boolean recovery hints drive exponential-backoff (60s doubling to a 4h cap) per-turn provider fallback and credential-pool rotation |

**The design lesson.** Every harness examined on this page has to solve
the same underlying problem even though only OpenCode's solution is
fully visible from the outside: a model provider's content-block or
tool-call vocabulary, its finish/stop-reason enumeration, and its
streaming delta-accumulation discipline are all provider-specific, and
a harness that speaks to more than one provider (which all three
harnesses in this book do, to varying documented degrees) needs a
normalization layer sitting directly on top of §1/§2's raw wire formats
and directly underneath the agent-loop mechanics
[agent-loop.md](agent-loop.md) and
[agent-loop-implementations.md](agent-loop-implementations.md)
describe. OpenCode's source names and implements that layer explicitly
(`Route`/`Protocol`/`LLMEvent`/`FinishReason`); Claude Code's Agent SDK
mostly avoids needing one by wrapping a single provider's own typed SDK
events directly; Copilot CLI's own version of this layer is real
(the changelog proves at least an OpenAI-Responses-API-aware provider
category exists) but not source-visible, leaving its exact shape as
this page's one clearly-flagged remaining gap. DeepSeek Harness's own
docs supply, independently of OpenCode's engineering, a genuinely useful
*name* for the underlying design principle both harnesses converge on --
"provider-neutral consumer, swappable provider, one shared interface" --
without this page treating that naming contribution as evidence either
harness's own internal axis structure resembles the other's. pi supplies a
fourth, independently-arrived-at instance of the same normalization move,
this time documented at package-README precision rather than either
inferred from a changelog or read from a source file directly: a shared
`StreamEvent` alphabet and a shared `stopReason` enum standing in for the
same four wire-protocol families this page's own §1-§2 structure already
organizes around. That four separate engineering efforts -- Anthropic's
own SDK wrapping (via Claude Code), OpenCode's `Route`/`LLMEvent`
machinery, DeepSeek's capability-seam vocabulary, and pi's own
`StreamEvent`/`stopReason` pair -- all converge on "one normalized event
union plus one normalized terminal-reason enum" as the right shape for
this exact problem, each reached independently, is itself a datapoint
worth taking seriously: this looks like a discovered necessity of
building a multi-provider agent harness, not a coincidence of API design
taste. Hermes Agent supplies a fifth, source-verified instance of the same
convergence -- its own `ProviderTransport`/`NormalizedResponse` pair -- but
with a materially different choice at the one point where it could have
invented a sixth bespoke enum: rather than following OpenCode's, pi's, and
(by necessity) Claude Code's own path of minting a new terminal-reason
vocabulary, Hermes canonicalizes directly onto OpenAI's own four-value
`finish_reason` set, treating one upstream provider's vocabulary as the
shared target rather than designing a neutral fifth one -- a plausible
consequence of the `openai` SDK already being Hermes' one pinned,
every-session-loaded dependency (§3.6) that OpenCode and pi, with no
single default SDK of comparable centrality, did not have the same
incentive toward. Separately, Hermes' error-classification layer
(`FailoverReason`/`ClassifiedError`, §3.6) is this page's first
source-verified example of a harness maintaining a wire-error taxonomy
detailed enough to distinguish *why* a request should be retried,
credential-rotated, provider-failed-over, or context-compressed as four
independently-triggerable recovery actions rather than a single generic
retry-with-backoff path -- a layer this page's other five harness sections
do not document at comparable resolution, though none of them is shown to
lack one.

---

## Sources

All fetched fresh 2026-08-01 unless noted otherwise.

**Anthropic (authoritative for the Messages API contract itself, not
for any specific harness's use of it):**
- `https://platform.claude.com/docs/en/api/messages` (redirected live
  this session from `https://docs.claude.com/en/api/messages`) --
  request/response field reference, content-block types, `stop_reason`
  enumeration; covers §1.1-§1.4.
- `https://platform.claude.com/docs/en/docs/build-with-claude/streaming`
  (redirected live this session from the equivalent `docs.claude.com`
  path) -- SSE event flow, delta types, error recovery; covers §1.5.

**OpenAI (authoritative for its own API contract itself, not for
Copilot CLI's or OpenCode's use of it):**
- `https://developers.openai.com/api/docs/guides/function-calling`
  (redirected live this session from
  `https://platform.openai.com/docs/guides/function-calling`) -- Responses
  API tool-calling shape, `finish_reason` enumeration, streaming event
  names; covers §2.1-§2.3. §2.4 (classic Chat Completions shape) is
  explicitly marked as recalled, not re-verified this session.

**Claude Code (authoritative for the Claude Agent SDK's own documented
behavior; this repo ships no implementation source):**
- `https://code.claude.com/docs/en/agent-sdk/streaming-output` --
  `StreamEvent`/`SDKPartialAssistantMessage` shape, message-flow
  ordering, the structured-output streaming limitation; covers §3.1 in
  full.

**GitHub Copilot CLI (authoritative for its own behavior-change history
only; no implementation source exists in this repo):**
- `https://github.com/github/copilot-cli` `changelog.md`, fetched fresh
  this session via `gh api repos/github/copilot-cli/contents/
  changelog.md` (full file, grepped for `tool_call`, `streaming`,
  `finish_reason`, `Responses API`, `reasoning`) -- v1.0.62 (2026-06-13)
  and v1.0.52 (2026-05-23) "Responses API" entries and the recurring
  reasoning-effort/reasoning-summary/reasoning-token entries cited in
  §3.2.
- `https://github.com/github/copilot-sdk` `docs/auth/byok.md`, fetched
  fresh this session -- adjacent-surface-only citation of the Copilot
  SDK's own `ProviderConfig` (`type`, `wireApi`) three-way protocol
  dispatch, explicitly flagged as describing a different product from
  Copilot CLI itself.

**OpenCode (authoritative for its own documented behavior AND, unlike
the two harnesses above, its own real implementation; `dev` branch, not
a stable release tag):**
- `https://github.com/anomalyco/opencode`, `dev` branch, located via
  `gh search code` and read via `curl` against
  `raw.githubusercontent.com` this session (working around a local
  `gh api`/base64-decoding failure on this platform) -- full contents of
  `packages/llm/AGENTS.md`, `packages/llm/src/schema/events.ts`,
  `packages/llm/src/schema/ids.ts` (the `FinishReason` enum),
  `packages/llm/src/protocols/anthropic-messages.ts` and
  `packages/llm/src/protocols/openai-chat.ts` (both `mapFinishReason()`
  implementations, grepped and read in context), and
  `packages/opencode/src/session/message-v2.ts` -- covering §3.3 in
  full.

**DeepSeek Harness (authoritative for its own documented capability-seam
vocabulary; fetched 20 August 2026, `master` branch of
`deepseek-ai/deepseek-harness`, developer preview at time of fetch --
see [Hooks and lifecycle extensibility](hooks-lifecycle-extensibility.md)
§4's Sources for the full repository-metadata citation, not repeated
here):**
- `docs/capability-seams.md` -- the Service Definition/Provider/Consumer
  three-role definition, the `ctx.llm` seam and its named providers
  (`llm-deepseek`, `llm-pi-ai`, `llm-replay`), the "one provider swap
  changes the whole product" quote; covers §3.4 in full.
- `docs/glossary.md` and `docs/architecture.md` -- the seam-vs-core-service
  distinction (`ctx.sessions`/`ctx.invariants` deliberately kept unseamed),
  cross-checked against the same two files' citation in
  [Session & transcript persistence](session-persistence.md) §4.

**pi (authoritative for its own documented behavior; fetched 20 August 2026 from
`github.com/earendil-works/pi`, `main` branch):**
- `packages/ai/README.md` (via `gh api
  repos/earendil-works/pi/contents/packages/ai/README.md`, in full, 513+ lines) -- the
  primary source for all of §3.5: the package's own stated purpose and tool-calling-only
  model scope, the four wire-protocol-family `api` discriminators, the full supported-
  providers list, the normalized `StreamEvent` tagged union (Quick Start streaming
  example), the "Stop Reasons" section's five-terminal-plus-`"pending"` enumeration, the
  "How Auth Resolves"/"Transforming Request Headers"/"Credential Store" sections'
  ordered auth-and-header-merge pipeline and fail-closed stored-credential rule, and the
  "Error Handling" section's stream-never-throws guarantee.
- `packages/coding-agent/docs/models.md` and `packages/coding-agent/docs/providers.md`
  (fetched the same way) -- cross-referenced for the config-facing side of the same
  abstraction (`models.json`'s `api` field, provider/model `compat` overrides, the
  credential-resolution order also covered in
  [auth-and-usage-accounting.md](auth-and-usage-accounting.md)'s own pi section).

**Hermes Agent (authoritative for its own documented behavior; fetched 1 September
2026 from `github.com/NousResearch/hermes-agent`, `main` branch, via `curl` against
`raw.githubusercontent.com`):**
- `pyproject.toml` (in full) -- the `openai==2.24.0` core dependency and
  `anthropic==0.87.0` optional-extra split, the supply-chain-hardening exact-pin
  rationale, and the `pydantic`-bump comment naming the `codex_responses` dispatch as
  the OpenAI SDK's own `.responses` resource; covers §3.6's opening SDK-foundation
  claim.
- `agent/chat_completion_helpers.py` (the full 5,109-line file) -- `build_api_kwargs`'s
  four-`api_mode` branching (`chat_completion_helpers.py:1829-2156`), the
  `ProviderStreamError`/SSE-error-parsing helpers, `_dispatch_nonstreaming_api_request`'s
  per-mode dispatch (including the `bedrock_converse` "bypasses the OpenAI client
  entirely" comment), `try_activate_fallback`'s exponential-backoff/per-turn-cooldown
  logic, and `interruptible_streaming_api_call`'s four-mode streaming docstring plus its
  `HERMES_STREAM_RETRIES`-gated mid-tool-call silent-reconnect path (read directly
  around line 4871 and lines 4980-5109); the native Anthropic SDK's
  `request_client.messages.stream(**final_kwargs)` call confirmed directly at line 4690.
- `agent/transports/base.py` -- the `ProviderTransport` ABC's own
  `convert_messages → convert_tools → build_kwargs → normalize_response` scope
  docstring and its explicit "does NOT own" exclusion list.
- `agent/transports/types.py` -- the shared `ToolCall`/`Usage`/`NormalizedResponse`
  dataclasses and the `finish_reason` docstring naming OpenAI's own four-value
  vocabulary (`"stop"`, `"tool_calls"`, `"length"`, `"content_filter"`) as the
  canonical normalized target, plus `map_finish_reason()`'s unknown-falls-back-to-
  `"stop"` behavior.
- `agent/error_classifier.py` (the full ~99 KB file) -- the module docstring's stated
  purpose, the `FailoverReason` enum's full ~20-member taxonomy, the `ClassifiedError`
  dataclass's four boolean recovery-hint fields, and `classify_api_error`'s own
  nine-stage (0-8) priority-ordered classification pipeline docstring.
- `hermes-agent.nousresearch.com/docs/user-guide/features/fallback-providers.md`
  (WebFetch/`curl`) -- the "When Fallback Triggers" status-code-to-trigger table,
  the per-turn/reset-aware fallback semantics, and the prompt-cache-invalidation
  warning on every provider swap.
- `hermes-agent.nousresearch.com/docs/user-guide/features/provider-routing.md`
  (WebFetch/`curl`) -- the `provider_routing` config schema and the "How It Works"
  section's direct statement that these preferences ride the OpenAI Python SDK's own
  `extra_body` argument onto the aggregator's top-level `provider` JSON field.
