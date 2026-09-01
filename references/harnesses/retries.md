# Retries -- Claude Code, GitHub Copilot CLI, OpenCode, pi, Hermes Agent, and DeepSeek Harness

**Scope note.** This page is about **failure recovery on a single outbound
model-provider request** -- what counts as a transient failure worth
retrying (a 5xx, a 429, a dropped connection, a stalled stream) versus a
terminal one that should surface immediately (auth failure, context
overflow, a malformed request), how the delay before the next attempt is
computed (fixed backoff, exponential backoff, jitter, an honoured
`Retry-After`/`retry-after-ms` response header), what caps exist on attempt
count and delay size, and what the user actually sees while it happens. It
is a distinct axis from [context-compression.md](context-compression.md)
(reacting to a **context-window overflow**, a different failure mode
entirely) and from [caching.md](caching.md) (reusing a **successful**
prior request's prefix) -- a request can retry cleanly with a warm cache,
and a context-overflow error is, as shown below, explicitly carved out of
every retry policy this page found rather than treated as a retryable
failure.

Every claim is tagged VERIFIED (fetched this session) or BEST CURRENT
UNDERSTANDING, UNCONFIRMED. Claude Code, Copilot CLI, OpenCode, pi,
Hermes Agent, and DeepSeek Harness are six separate products; a retry
rule confirmed for one is never assumed to hold for another without its
own citation.

---

## 1. Claude Code

Primary source: `code.claude.com/docs/en/errors`, fetched fresh this
session (2026-07-31) -- a dedicated "Automatic Retries in Claude Code"
section on the errors-reference page -- cross-referenced against
`github.com/anthropics/claude-code` `CHANGELOG.md` (fetched fresh this
session via `gh api repos/anthropics/claude-code/contents/CHANGELOG.md`,
full 5,248-line file, grepped for `retry`/`retries`/`backoff`/`529`/
`overloaded`/`CLAUDE_CODE_MAX_RETRIES`/`CLAUDE_CODE_RETRY_WATCHDOG`).
VERIFIED unless tagged otherwise.

### 1.1 The documented policy: bounded, category-gated, exponential

The docs state the top-line number directly: "Claude Code retries
transient failures up to **10 times** with exponential backoff before
showing an error. However, not all failures are retried." The categories
are split cleanly into retried and not-retried:

```mermaid
flowchart TD
    Err["A request fails"] --> Classify{"What kind of failure?"}
    Classify -->|"Server error, overloaded\nresponse, request timeout"| Retry1["Retried\n(up to CLAUDE_CODE_MAX_RETRIES, default 10)"]
    Classify -->|"Dropped connection before any\npart of the response completed\n(v2.1.198+)"| Retry2["Retried\nsame backoff, turn continues"]
    Classify -->|"429 throttle without plan-quota\nheaders, subscription sign-in\n(v2.1.199+)"| Retry3["Retried\n(API-key/Enterprise already did before v2.1.199)"]
    Classify -->|"TLS certificate validation failure\n(v2.1.199+)"| Fail1["NOT retried -- surfaced on\nfirst attempt so cert setup can be fixed"]
    Classify -->|"Mid-response server error, dropped\nconnection, or stalled stream\nAFTER a block already completed\n(v2.1.199+)"| Fail2["NOT retried -- completed output kept,\nincomplete-response notice shown instead"]
    Classify -->|"Bedrock streaming response with\nunexpected content-type (v2.1.208+)"| Fail3["NOT retried -- a rewriting gateway/proxy\nwould rewrite the retry identically"]
```

Two distinctions inside this classification are easy to miss and worth
stating precisely, both from the docs' own wording. First, **transient TLS
conditions** (a handshake timeout) are still retried -- only certificate
**validation** failures (a TLS-inspecting proxy, a missing
`NODE_EXTRA_CA_CERTS` bundle, an expired certificate) fail fast, because
those need a configuration fix the retry loop cannot produce. Second, the
mid-response carve-out is itself a version-dated behavior change: "Before
v2.1.199, partial output was discarded and the whole turn reported as
error" -- the current behavior preserves whatever text or tool call
already completed and appends `API Error: Server error mid-response. The
response above may be incomplete.` instead of failing the turn outright.

### 1.2 Environment variables

| Variable | Default | Effect |
|---|---|---|
| `CLAUDE_CODE_MAX_RETRIES` | 10 | Attempt count. Capped at 15 as of v2.1.186; as of v2.1.199, setting `CLAUDE_CODE_RETRY_WATCHDOG` raises the default and removes that cap entirely. Lowering it surfaces failures faster in scripts/CI. |
| `CLAUDE_CODE_RETRY_WATCHDOG` | unset | Set to `1` for unattended sessions (CI): retries `429`/`529` capacity errors **indefinitely** rather than failing after `CLAUDE_CODE_MAX_RETRIES` attempts, and (v2.1.199+) separately raises the default retry count for *other* transient errors (server errors, timeouts, dropped connections) to roughly 300 attempts (~3 hours of accumulated backoff) and lifts the 15-attempt cap on an explicitly set `CLAUDE_CODE_MAX_RETRIES`. |
| `API_TIMEOUT_MS` | 600000 | Per-request timeout in milliseconds; raise for slow networks/proxies. |

`CHANGELOG.md` independently confirms both halves of this table at the
versions the docs cite: v2.1.186 "Changed `CLAUDE_CODE_MAX_RETRIES` to cap
at 15; for unattended sessions, use `CLAUDE_CODE_RETRY_WATCHDOG` instead,"
and v2.1.199 "Transient server rate-limit errors (429s unrelated to your
usage limit) are now retried automatically with backoff for subscribers
instead of failing the turn" plus "`CLAUDE_CODE_RETRY_WATCHDOG` now raises
the default retry count for non-capacity transient errors to 300 and
lifts the cap of 15 on `CLAUDE_CODE_MAX_RETRIES`" -- independent
confirmation from a second source of the exact same version-gated change.

### 1.3 What the user sees, and how that UX itself changed release to release

While retrying, the spinner shows a `Retrying in Ns · attempt x/y`
countdown. The label reveal timing changed twice, and `CHANGELOG.md`
dates both changes precisely:

- **v2.1.185** ("Improved API retry UX" family): if no data arrives on the
  response stream for 20 seconds *before any retry has started*, the line
  reads `Waiting for API response · will retry in … · check your
  network` -- the request has not failed yet at this point, this is a
  stalled-connection countdown, not a retry-attempt countdown. The
  changelog's own wording for this change: "The stream-stall hint now
  reads 'Waiting for API response · will retry in …' instead of 'No
  response from API · Retrying in …', and triggers after 20s of silence
  instead of 10s."
- **v2.1.198**: the label switches from a generic `API error` to the
  specific failure reason (network down, TLS handshake failed, rate
  limit) starting from the **third** attempt (or the final attempt, if
  `CLAUDE_CODE_MAX_RETRIES` allows fewer than three) -- earlier versions
  only revealed the specific reason on the very last attempt. The same
  version also adds a status-page pointer once the reason is known to be
  a 529 overload: `status.claude.com` for the Anthropic API, or the
  provider/gateway hostname for anything else. `CHANGELOG.md`'s own line
  for the general shape of this change: "Improved API retry UX: the error
  reason is now shown after the second attempt, and a status page link
  replaces the spinner tip when the API is overloaded."
- **v2.1.214**: during [advisor](memory-management.md) consultation
  specifically, the stall banner's threshold is widened from 20 seconds
  to 90 seconds, "because advisor reviews can send nothing for well over
  20 seconds" -- a targeted exception to the general stall-detection
  timing to avoid a false-positive stall warning on a call whose own
  normal latency profile is longer.

Two further UX bugs the changelog records as fixed, evidence the
countdown display itself needed its own hardening independent of the
retry logic underneath it: v2.1.101 "Fixed the API retry indicator
('Retrying in 0s · attempt N/10') staying on screen after the retry
succeeded," and v2.1.101 (same entry set) "Fixed API retry countdown
sticking at '0s' instead of counting down between attempts."

### 1.4 Backoff-minimum and circuit-breaker fixes worth their own note

Two changelog entries describe Claude Code correcting its *own* backoff
math after it initially undercounted or over-retried:

- **v2.1.98**: "Fixed 429 retries burning all attempts in ~13s when the
  server returns a small `Retry-After` — exponential backoff now applies
  as a minimum." Before this fix, a server-supplied `Retry-After` shorter
  than the exponential schedule would be honoured literally, letting the
  client exhaust its entire 10-attempt budget in seconds against a
  server that kept returning a short `Retry-After` on every attempt; the
  fix makes the client-computed exponential delay a **floor**, not just a
  ceiling override, when the header value is smaller than what backoff
  would already produce.
- **v2.1.76**: "Fixed auto-compaction retrying indefinitely after
  consecutive failures — a circuit breaker now stops after 3 attempts."
  This is a *different* retry loop from the main API-request policy in
  §1.1-1.2 -- it is [compaction's](context-compression.md) own internal
  retry-the-summarization-call loop, and it is the one place this session
  found Claude Code applying a **small, hard-coded circuit breaker** (3
  attempts, no configurability) rather than the large-but-eventually-
  unbounded-via-watchdog policy the main request path uses. Worth flagging
  as a contrast point for §4.5 and §5: the same product ships two
  philosophically different retry postures for two different subsystems.

A related historical reversal, evidence Claude Code has previously
over-corrected in the *other* direction (too little retrying) and had to
revert: v2.1.111 "Reverted the v2.1.110 cap on non-streaming fallback
retries — it traded long waits for more outright failures during API
overload," following v2.1.110's own "Fixed non-streaming fallback retries
causing multi-minute hangs when the API is unreachable" -- a cap
introduced specifically to fix a hang, then reverted one version later
once it was shown to convert overload conditions into outright failures
instead of (slower, but eventually successful) waits.

### 1.5 `fallbackModel`: a bounded, error-type-gated retry-on-a-different-model

v2.1.166 adds a mechanism adjacent to, but distinct from, retrying the
*same* request: "Added `fallbackModel` setting to configure up to three
fallback models tried in order when the primary model is overloaded or
unavailable," paired in the same version with "Claude Code now retries a
turn once on the fallback model when the API rejects an unexpected
non-retryable error; auth, rate-limit, request-size, and transport errors
still surface immediately." The explicit carve-out list here -- auth,
rate-limit, request-size, transport -- mirrors the non-retryable
classification pattern this page also finds, independently, in OpenCode's
error-reason taxonomy (§3.2): every harness examined this session treats
authentication and malformed-request failures as never worth a retry of
any kind, same-model or fallback-model.

### 1.6 Retries as a pervasive engineering surface beyond the main API call

`CHANGELOG.md` records retry-hardening fixes across subsystems that are
not the primary model-request path at all, worth naming briefly to show
the full footprint of "retry" as a recurring engineering concern in this
codebase rather than a single policy object: MCP capability discovery
(v2.1.191, "capability discovery (`tools/list`, `prompts/list`,
`resources/list`) now retries transient network errors with short
backoff"), MCP server startup (v2.1.126, "MCP servers that hit a
transient error during startup now auto-retry up to 3 times instead of
staying disconnected"), MCP OAuth (v2.1.191, "discovery and token
requests now retry once after transient network errors"), the
auto-updater (v2.1.147, "retries transient network failures, reports
specific error categories and OS error codes on failure" -- corrected
from an earlier v2.1.144 mislabel here after a fresh re-fetch of
`CHANGELOG.md` while researching
[packaging-distribution-and-self-update.md](packaging-distribution-and-self-update.md);
that page treats the auto-updater as a first-class topic and is the
canonical citation for its full history), remote managed
settings (v2.1.140, "Fixed remote managed settings not retrying on 401 —
now retries once with a force-refreshed token"), and voice mode
(v2.1.204, "Fixed voice dictation retrying in an unbounded loop when the
microphone or audio recorder fails — repeated capture failures now pause
voice input" -- notably a case of an **unbounded** retry loop being fixed
by adding a bound, the opposite direction of the compaction circuit
breaker in §1.4 but the same underlying lesson).

### 1.7 Hook and permission-layer interaction

Retries are also exposed as a first-class outcome inside Claude Code's own
hook and auto-mode-classifier surfaces, not only inside the raw
API-request loop: v2.1.89 adds a `PermissionDenied` hook that "fires after
auto mode classifier denials — return `{retry: true}` to tell the model it
can retry," and the same version lets a user manually retry a denied
command from `/permissions` → Recent tab with the `r` key. This is a
retry decision made by a *policy/permission* layer, not a
transport/error-classification layer -- included here because it is the
one place in Claude Code's own vocabulary where "retry" names a
model-facing permission outcome rather than an HTTP-failure response.

---

## 2. GitHub Copilot CLI

Sources: `docs.github.com/en/enterprise-cloud@latest/copilot/tutorials/
copilot-chat-cookbook/debugging-errors/handling-api-rate-limits` (fetched
fresh this session, 2026-07-31) and `github.com/github/copilot-cli`
`changelog.md` (fetched fresh this session via `gh api
repos/github/copilot-cli/contents/changelog.md`, full 2,898-line file,
grepped for `retry`/`retries`/`backoff`/`rate.limit`/`429`/`throttle`).
Copilot CLI is closed source -- everything below is inferred from
documented behavior and the product's own changelog, never from an
implementation file, the same standing caveat as
[context-compression.md](context-compression.md) §2 and
[caching.md](caching.md) §2.

### 2.1 What is documented at the platform level -- and its real scope

The "Handling API rate limits" cookbook page is **not** a description of
Copilot CLI's own internal retry mechanism; it is generic guidance for
developers building *against* the Copilot Chat API, showing example client
code (a `Retry` class configured for `total=3`, `backoff_factor=0.3`,
targeting status codes 500/502/504). Checked directly this session: the
page never states that Copilot CLI itself implements this pattern, an
equivalent one, or any specific attempt count/backoff formula for its own
requests. This is flagged plainly rather than blended into a
CLI-specific-sounding claim: **the only source that actually describes
Copilot CLI's own retry behavior is its changelog** (§2.2), read as a
history of shipped fixes rather than a specification.

### 2.2 Changelog-traced evidence of the CLI's actual retry behavior

```mermaid
stateDiagram-v2
    state "0.0.389 (2026-01-22)<br/>Rate-limit errors show retry timing" as Era1
    state "0.0.407 (2026-02-11)<br/>Streaming auto-retries on server-error interruption" as Era2
    state "1.0.13/1.0.14 (2026-03-30/31)<br/>MCP registry lookups gain automatic retries" as Era3
    state "1.0.25 (2026-04-13)<br/>MCP remote server auto-retry on transient network failure" as Era4
    state "1.0.32 (2026-04-17)<br/>Rate-limited sessions pause+auto-retry queued messages" as Era5
    state "1.0.35 (2026-04-23)<br/>continueOnAutoMode: switch model instead of pausing" as Era6
    state "1.0.52 (2026-05-23)<br/>HTTP/2 upload stall retries over HTTP/1.1" as Era7
    state "1.0.55/1.0.57 (2026-05-28/06-01)<br/>update/version rate-limit auth + vote_memory throttling" as Era8
    state "1.0.66 (2026-06-30)<br/>Fixed a heartbeat retry loop retrying forever every few seconds" as Era9

    Era1 --> Era2: message clarity, then stream-level resilience
    Era2 --> Era3: MCP-specific retry surfaces begin appearing
    Era3 --> Era4
    Era4 --> Era5: session-level rate-limit handling matures
    Era5 --> Era6: automatic mitigation added, not just a pause
    Era6 --> Era7: transport-layer retry (protocol downgrade)
    Era7 --> Era8: peripheral (non-chat) endpoints get their own rate-limit handling
    Era8 --> Era9: an actual unbounded-retry bug gets fixed
```

Reading the changelog oldest-to-newest (it is itself newest-first):

- **0.0.389 (2026-01-22).** "Rate limit errors now show retry timing in
  user-friendly messages" -- the earliest entry this session found that
  names retry behavior explicitly, evidence the underlying retry
  mechanism (whatever it was) already existed and this fix is purely
  about how its timing is communicated.
- **0.0.407 (2026-02-11).** "Streaming responses automatically retry when
  interrupted by server errors" -- a stream-level auto-retry, the closest
  changelog analog to Claude Code's mid-response dropped-connection retry
  (§1.1), though without a stated attempt count or backoff formula.
- **1.0.13 (2026-03-30) / 1.0.14 (2026-03-31).** "MCP registry lookups are
  more reliable with automatic retries and request timeouts" -- appears
  identically worded across both versions, evidence of either a
  same-release backport or a fix re-landing; either way this is Copilot
  CLI's MCP-discovery-retry analog to Claude Code's own MCP
  capability-discovery retry (§1.6).
- **1.0.25 (2026-04-13).** "MCP remote server connections automatically
  retry on transient network failures" -- extends the same pattern from
  registry lookups to live remote MCP server connections.
- **1.0.32 (2026-04-17).** "Rate-limited sessions now pause queued
  messages and automatically retry instead of dropping them," alongside
  "Rate limit error messages now show specific context based on the type
  of limit reached" in the same release -- the first entry that
  describes session-level (not just single-request-level) rate-limit
  handling: queued user messages survive a rate-limit pause rather than
  being discarded.
- **1.0.34 (2026-04-20) / 1.0.35 (2026-04-23).** "Add `continueOnAutoMode`
  config option to automatically switch to auto model on rate limit
  instead of pausing" -- a documented *alternative* to retrying the same
  model: rather than waiting out a rate limit, this option reroutes the
  session to Copilot's automatic model-selection feature, trading model
  choice for continuity. This is a materially different mitigation
  strategy from anything found in Claude Code's or OpenCode's own retry
  logic -- neither of those switches models automatically on a rate limit
  the way this Copilot CLI setting does (Claude Code's `fallbackModel`,
  §1.5, is the closest analog, but it is gated on "overloaded or
  unavailable," not specifically rate-limit-only, and is a fixed ordered
  list rather than a live auto-selection feature).
- **1.0.52 (2026-05-23).** "Requests that time out due to an HTTP/2 upload
  stall automatically retry over HTTP/1.1" -- a protocol-downgrade retry,
  a distinct category from a same-protocol backoff-and-resend; notably,
  1.0.57 (2026-06-01) later changes the *default* transport to HTTP/1.1
  outright "improving reliability on some network paths," with
  `COPILOT_ENABLE_HTTP2=1` to opt back into HTTP/2 -- suggesting the
  underlying HTTP/2 stall problem this retry was mitigating was common
  enough to justify changing the default instead of only retrying around
  it.
- **1.0.55 (2026-05-28) / 1.0.57 (2026-06-01).** Two entries about
  rate-limit handling on *peripheral* (non-chat) endpoints specifically:
  "`copilot update` and `copilot version` authenticate release API
  requests to avoid rate limit errors in shared-NAT environments"
  (1.0.55) and "Actionable error message shown when GitHub API rate limit
  is hit during `copilot update`" (1.0.57) -- both about the GitHub
  release-API rate limit the updater itself can hit, not the model-chat
  rate limit this page is otherwise about; included to flag that "rate
  limit" in this changelog spans at least two independent rate-limited
  surfaces (chat completions and the GitHub REST API the updater calls).
  The same 1.0.55 release also throttles `vote_memory` tool calls "per
  response and per interaction to prevent runaway voting bursts" -- a
  self-imposed request-rate cap on the CLI's own side, the inverse
  direction from retrying *after* a provider-imposed limit is hit.
- **1.0.66 (2026-06-30).** "Fixed remote sessions continuing to send
  heartbeats after their worker was replaced, which left long-lived
  desktop and IDE processes retrying a rejected request every few seconds
  forever" -- a concrete, named instance of an actually-unbounded retry
  bug in Copilot CLI's own remote-session heartbeat path, structurally
  the same category of failure mode this page finds independently
  source-verified in OpenCode's session-level retry policy (§3.4),
  though found here only as a changelog bug-fix entry rather than as a
  standing architectural property -- this specific loop was fixed, not
  left as a documented limitation.

### 2.3 What is not documented

No page or changelog entry fetched this session states Copilot CLI's own
equivalent of `CLAUDE_CODE_MAX_RETRIES` (a user-configurable attempt
count), an explicit backoff formula (base delay, multiplier, jitter), a
stated maximum backoff delay, or whether a `Retry-After`/`retry-after-ms`
response header is honoured for the CLI's own model-completion requests
specifically (as opposed to the generic client-side example code on the
cookbook page in §2.1). Given the changelog's own repeated framing of
individual retry fixes as one-off, per-subsystem changes (MCP registry,
MCP remote servers, streaming responses, HTTP/2 stalls, remote-session
heartbeats) rather than references to one shared, named retry-policy
module, it is plausible each subsystem implements its own retry logic
independently rather than routing through one central policy the way
Claude Code's docs describe a single named mechanism (§1.1) or OpenCode's
source shows two explicit, shared modules (§3) -- but this is **BEST
CURRENT UNDERSTANDING, UNCONFIRMED**: no Copilot CLI source is public to
verify it, and no changelog entry or docs page states the architecture
explicitly either way.

---

## 3. OpenCode

Source: `github.com/anomalyco/opencode`, `dev` branch, fetched live via
`gh search code` and `gh api` this session (2026-07-31) -- flagging per
this project's standing caveat that `dev` is not a stable release tag and
this code may not reflect the current stable release. `opencode.ai/docs/
config/` was also fetched fresh this session and confirmed, as a checked
negative result, to document no retry-related configuration key (§3.6).
Unlike Claude Code and Copilot CLI, everything in this section is
verified from source, not inferred from documentation.

### 3.1 Two distinct, layered retry mechanisms

```mermaid
flowchart TD
    Turn["Session turn begins\n(SessionProcessor.process)"] --> Stream["llm.stream(streamInput)"]
    Stream --> HTTP["HTTP request via RequestExecutor.execute\n(packages/llm/src/route/executor.ts)"]
    HTTP --> Classify{"Response status /\ntransport outcome"}
    Classify -->|"429 (RateLimitReason) or\n5xx/503/504/529 (ProviderInternalReason)"| Bounded["retryStatusFailures():\nMAX_RETRIES = 2 (3 attempts total)\nhonors retry-after(-ms) header, else\nexponential+/-20% jitter, capped at 10s"]
    Classify -->|"401/403 (Auth), context-overflow/\n400/404/409/413/422 (InvalidRequest),\n429-with-quota-body (QuotaExceeded),\ncontent-policy, transport, unknown"| NonRetryableExec["retryable = false at this layer\nfails immediately, propagates as LLMError"]
    Bounded -->|attempts exhausted| LLMErrorOut["LLMError propagates up"]
    NonRetryableExec --> LLMErrorOut
    LLMErrorOut --> SessionCatch["Effect.retry(SessionRetry.policy(...))\nwraps the WHOLE turn effect\n(packages/opencode/src/session/retry.ts,\nwired in packages/opencode/src/session/processor.ts)"]
    SessionCatch --> Classify2{"SessionRetry.retryable(error)\n(its own, separate classification\nover SessionV1.APIError)"}
    Classify2 -->|"context-overflow"| StopSession["Cause.done -- never retried"]
    Classify2 -->|"5xx (always, even if SDK\ndidn't mark retryable),\nfree-tier/Go-limit messages,\nplain-text rate-limit/overload patterns"| UnboundedRetry["No attempts cap in the Schedule.\ndelay(): honors retry-after(-ms) header\nuncapped except by the ~24.8-day\n32-bit setTimeout ceiling;\nelse 2s x 2^(attempt-1), capped at 30s"]
    UnboundedRetry -->|"wait, then re-run the\nwhole turn effect"| Turn
```

The critical architectural fact this diagram makes explicit: OpenCode
does not have *one* retry policy, it has two, layered, with genuinely
different bounding behavior. The inner layer
(`packages/llm/src/route/executor.ts`) retries a single HTTP request a
small, hard-coded number of times. If that is exhausted, the resulting
`LLMError` is not the end of the story -- it propagates up into
`packages/opencode/src/session/processor.ts`, where the **entire
turn-processing effect** is wrapped in `Effect.retry(SessionRetry.policy
(...))`, a second, independent retry loop with its own error
classification and, as shown below, no attempts cap at all.

### 3.2 The inner layer: `RequestExecutor`'s bounded, jittered transport retry

VERIFIED, `packages/llm/src/route/executor.ts`. The constants:
`MAX_RETRIES = 2` (so up to 2 retries, 3 attempts total),
`BASE_DELAY_MS = 500`, `MAX_DELAY_MS = 10_000`. `retryDelay()`'s logic:
if the failed response carried a `retry-after-ms` or `retry-after`
header, that value is used directly (`Math.min(error.retryAfterMs,
MAX_DELAY_MS)`, capped at 10 seconds regardless of what the header said);
otherwise the delay is `Random.nextBetween(base*2^attempt*0.8,
base*2^attempt*1.2)` -- an explicit **±20% jitter band** around the
exponential value, also capped at 10 seconds, computed via Effect's
`Random` service rather than a fixed multiply.

Retryability at this layer is determined by a `retryable` getter defined
per error-reason class in `packages/llm/src/schema/errors.ts`, source-read
in full this session:

| Reason (`_tag`) | HTTP trigger | `retryable` |
|---|---|---|
| `RateLimit` | 429 (without a quota-exceeded body pattern) | `true` |
| `ProviderInternal` | `status >= 500`, or `retryableStatus(status)` (429/503/504/529) | `true` |
| `Authentication` | 401, 403 | `false` |
| `QuotaExceeded` | 429 whose body matches `insufficient[-_\s]?quota\|quota[-_\s]?exceeded` | `false` |
| `ContentPolicy` | body matches `content[-_\s]?policy\|content_filter\|safety` | `false` |
| `InvalidRequest` | 400, 404, 409, 413, 422 (flags `classification: "context-overflow"` via `isContextOverflow(body)` when applicable) | `false` |
| `Transport` | timeout, connection failure, any non-HTTP client error | `false` |
| `InvalidProviderOutput`, `UnknownProvider`, `NoRoute` | malformed/unrecognized responses, no matching route | `false` |

Two details worth stating precisely because they are easy to
misread from the table alone: first, a 429 is routed to `QuotaExceeded`
(non-retryable) specifically when its body names an exhausted quota, and
to `RateLimit` (retryable) otherwise -- the same status code produces two
different retryability outcomes depending on body content, mirroring
Claude Code's own documented distinction between a plan-usage-limit 429
and a transient-capacity 429 (§1.1, §1.2). Second, **transport-level
failures (network errors, timeouts) are `retryable: false` at this inner
layer** -- they are not retried by `RequestExecutor` at all; any retrying
of a raw connection failure happens only if it survives up to the outer,
session-level layer (§3.3), a genuinely different code path with its own,
separate classification logic operating on a different error shape.

### 3.3 The outer layer: `SessionRetry`, wrapping the entire turn

VERIFIED, `packages/opencode/src/session/retry.ts` (full file read this
session) and its call site in `packages/opencode/src/session/
processor.ts` line 660-674, confirmed via `gh search code`. The wiring is
`Effect.retry(SessionRetry.policy({ provider, parse, set }))` applied to
the whole `Effect.gen` block that streams the turn and handles every
event -- not to a single HTTP call. `SessionRetry.policy()` returns an
Effect `Schedule` built with `Schedule.fromStepWithMetadata`: on every
failure it calls its own `retryable(error, provider)` function (a
different function from, and operating on a different error type than,
§3.2's per-reason `retryable` getters -- this one inspects
`SessionV1.APIError`, a higher-level representation, via
`SessionV1.APIError.isInstance(error)`) and, if that returns a truthy
`Retryable` object, computes a delay, publishes a `{ type: "retry",
attempt, message, action, next }` session-status update (this is what
drives the UI's own retry countdown, distinct from Claude Code's spinner
in §1.3 but serving the identical purpose), and schedules the next
attempt; if `retryable()` returns `undefined`, the schedule calls
`Cause.done(meta.attempt)` and the turn fails for good.

`retryable()`'s classification, read directly from source: **context-
overflow errors are never retried** (`SessionV1.ContextOverflowError.
isInstance(error)` short-circuits to `undefined` immediately, the same
carve-out every harness examined on this page applies); any `APIError`
whose status is `>= 500` is retried **even if the provider SDK's own
`isRetryable` flag says otherwise** -- a source comment states this
explicitly: "5xx errors are transient server failures and should always
be retried, even when the provider SDK doesn't explicitly mark them as
retryable." Beyond raw status codes, the function also special-cases two
named commercial conditions with their own user-facing messaging: a
`FreeUsageLimitError` response body produces a `"subscribe"`-labeled
action pointing at `opencode.ai/go` (the `GO_UPSELL_MESSAGE` constant,
literally "Free usage exceeded, subscribe to Go"), and a
`GoUsageLimitError` body produces a formatted "resets in N days/hours/
minutes" message computed from the response's `retry-after` header,
with an `"open settings"` action link to a workspace-specific Go page.
Beyond structured `APIError` instances, `retryable()` also pattern-
matches plain-text error messages for phrases like "rate limit," "too
many requests," and "rate increased too quickly," and JSON-encoded
provider error bodies for `type: "too_many_requests"`, an `error.code`
containing `"rate_limit"`, or a top-level `code` containing `"exhausted"`
or `"unavailable"` -- a materially broader, string-matching-based
retryability net than the inner layer's clean status-code/tag-based
table in §3.2.

`delay()`'s formula, also read directly: if the failing `APIError`
carries response headers, a `retry-after-ms` value (if present and
numeric) is used verbatim; otherwise a `retry-after` value is parsed
either as seconds or, failing that, as an HTTP date string and converted
to a remaining-millisecond offset; if neither header value parses, the
function falls through to `RETRY_INITIAL_DELAY * RETRY_BACKOFF_FACTOR **
(attempt - 1)` -- 2000ms times 2 to the power of (attempt minus one) --
**with headers present but no parseable value, this exponential result is
only capped by `RETRY_MAX_DELAY = 2_147_483_647`**, i.e. the maximum
32-bit signed integer JavaScript's `setTimeout` accepts, roughly 24.8
days. Only when the error carries **no response headers at all** does the
function apply the tighter `RETRY_MAX_DELAY_NO_HEADERS = 30_000` (30
seconds) cap instead. There is no cap on the **number** of attempts
anywhere in this file or at its call site -- the `Schedule` keeps
recursing for as long as `retryable()` keeps returning a truthy result,
which for a `>= 500` status is unconditional.

### 3.4 Corroborating this from a live, fetched GitHub Issue

VERIFIED, `gh issue view 17648 --repo anomalyco/opencode`, fetched fresh
this session. The issue reports precisely the behavior the source in §3.3
predicts: against a GitHub Copilot-backed provider endpoint returning
transient `"Could not relay message upstream"` errors (themselves 5xx-class,
per §3.3's always-retry-5xx rule), the reporter's logs show **173
consecutive retry failures over 2.5 hours**, with per-attempt backoff
growing from roughly 2 seconds at attempt 1 to over 7 minutes by attempt
10 and continuing to grow, with no circuit breaker and no way to abort
other than killing the process. The issue's own code excerpt quotes an
older version of `delay()` in which the with-headers branch had **no cap
applied at all** (not even the 24.8-day `RETRY_MAX_DELAY` ceiling this
session's fetch of the current `dev` branch shows via `cap()`) -- meaning
the `cap()` wrapper appears to be a partial mitigation added after this
issue was filed, narrowing the unbounded-growth window from "no ceiling"
to "a 24.8-day ceiling," which does not address the issue's actual
request (a sane, configurable maximum measured in minutes, plus an
attempts cap). The issue itself links to `github.com/sst/opencode` rather
than `anomalyco/opencode` in its source-code references -- a different
repository path this session did not independently resolve (possibly an
earlier name or a fork/rename in this project's history) -- flagged here
rather than silently normalized to the org this page otherwise cites.
Several adjacent issue titles surfaced by this session's `WebSearch` (not
individually fetched, so not claimed as independently verified, only
named as a consistent pattern of user reports): "Session processor
retries indefinitely with unbounded exponential backoff — no max retries
or circuit breaker," "Rate limit retries every ~1 second with no backoff
or max limit," "LLM provider SDK lacks retry logic for transient API
errors," "Infinite retry loop on HTTP 500 causes opencode to hang
indefinitely," "Excessive retry backoff (~2 weeks) on 'Quota Exceeded'
with no mechanism to reset/force retry," and two open feature requests
asking for exactly the missing levers: a configurable `maxAttempts`/
`maxDelay` for `SessionRetry`, and an option to swap exponential backoff
for a fixed interval.

### 3.5 A third, unrelated retry utility: `packages/core/src/util/retry.ts`

VERIFIED, full file read this session. This is a small, generic,
**bounded-by-default** retry helper (`attempts = 3`, `delay = 500`,
`factor = 2`, `maxDelay = 10000`) that retries based on a
string-substring match against a fixed list of transient network-error
message fragments (`"load failed"`, `"network connection was lost"`,
`"failed to fetch"`, `"econnreset"`, `"econnrefused"`, `"etimedout"`,
`"socket hang up"`) rather than on any structured HTTP-status
classification. This is architecturally unrelated to either §3.2's
`RequestExecutor` or §3.3's `SessionRetry` -- there is no source evidence
found this session that the LLM request path calls into this function --
and its existence, alongside the two purpose-built LLM-specific retry
layers, is worth naming precisely because it shows a third, independently
maintained retry implementation coexisting in the same codebase, each
with its own bound (or lack thereof).

### 3.6 Config surface: none found

`opencode.ai/docs/config/`, fetched fresh this session, was checked
specifically for a retry-related key and confirmed to define **no**
`retry`, `maxRetries`, `backoff`, or similar setting anywhere on the
page -- the only related keys documented there govern request and
stream-chunk **timeouts**, a different concern. This matches the pattern
[caching.md](caching.md) §3.5 found for OpenCode's prompt-caching policy:
a mechanism that is entirely programmatic (constants in `retry.ts`,
`executor.ts`) with no exposed user-facing lever, and, per §3.4's cited
Issues, an explicit, currently-unmet feature request from users of the
project to add one.

---

## 4. pi

**A package-naming note this book owes itself.** This session fetched
`github.com/earendil-works/pi`'s own `package.json` files directly (`gh api
repos/earendil-works/pi/contents/packages/ai/package.json` and .../
`packages/coding-agent/package.json`) to settle the spelling inconsistency
flagged across this book's existing pi sections. Both spellings this book has
used are correct -- they name two different sibling packages in the same
monorepo, not one package under two names: `packages/ai` publishes as
`@earendil-works/pi-ai` (`"description": "Unified LLM API with automatic model
discovery and provider configuration"`, the wire-protocol/multi-provider layer
[llm-api-contract.md](llm-api-contract.md) §3.5 and
[auth-and-usage-accounting.md](auth-and-usage-accounting.md) §4 document), and
`packages/coding-agent` publishes as `@earendil-works/pi-coding-agent`
(`"description": "Coding agent CLI with read, bash, edit, write tools and
session management"`, `"bin": {"pi": "dist/bundle/cli.js"}` -- the actual `pi`
CLI product every other pi section in this book, and the retry-specific
material below, is really about). A third sibling package this session's
research also surfaced, relevant specifically to this page, is
`packages/agent`, publishing as `@earendil-works/pi-agent-core`
(`"description": "General-purpose agent with transport abstraction, state
management, and attachment support"`) -- the durable execution engine
`pi-coding-agent` is itself built on top of, source of §4.6 below. All three
are versioned in lockstep (`0.84.4` at the time of this session's fetch) inside
one repository; treat any future single-spelling citation elsewhere in this
book as shorthand for whichever of the three the surrounding claim concerns,
not evidence of one package renaming itself.

### 4.1 Three layers, not one: transport retry, turn retry, and durable retry state

```mermaid
flowchart TD
    Turn["Agent turn or compaction/summarization call\n(packages/coding-agent)"] --> Outer["retryAssistantCall()\npackages/ai/src/utils/retry.ts\nwraps the WHOLE assistant-producing call"]
    Outer --> Classify1{"response.stopReason"}
    Classify1 -->|"'aborted'"| Term1["Terminal -- never retried"]
    Classify1 -->|"'error', isRetryableAssistantError()\ntrue (regex over errorMessage text)"| Bounded1["Retry: settings.retry.maxRetries\n(default 3), delay = baseDelayMs * 2^(attempt-1)\n(default 2000ms: 2s,4s,8s), no jitter"]
    Classify1 -->|"'error', pattern says non-retryable\n(quota/billing/GoUsageLimit text)"| Term2["Terminal -- returned immediately"]
    Bounded1 --> Inner["Each retried attempt calls down into:\nretryProviderRequest()\npackages/ai/src/utils/provider-retry.ts\nwraps ONE raw SDK/HTTP request"]
    Inner --> Classify2{"HTTP status / x-should-retry header"}
    Classify2 -->|"408, 409, 429, >=500,\nor x-should-retry: true"| Bounded2["Retry: settings.retry.provider.maxRetries\n(default 0 -- OFF), honors\nretry-after(-ms) header capped at\nmaxRetryDelayMs (default 60s),\nelse min(0.5*2^i, 8s) with -0..25% jitter"]
    Classify2 -->|"other status, or maxRetryDelayMs\nexceeded"| Escalate["Throws -- message text ('retry delay'\netc.) re-enters the OUTER classifier\nas a retryable error"]
    Escalate --> Classify1
    Bounded1 --> Durable["pi-agent-core (packages/agent):\nRetryPolicy captured inline in durable\noperation state; retryable failure ->\n'retry_wait' state {nextAttempt, notBefore};\nsurvives process crash/resume"]
```

The critical fact this diagram makes explicit, source-verified across three
distinct files this session read in full: pi does not have one retry
mechanism, it has an **outer, turn-level policy wrapping an inner,
request-level policy**, both independently configurable and independently
capped, plus a third, structurally separate concern -- a durable,
crash-recoverable representation of retry state inside `pi-agent-core`'s own
operation state machine, covered in §4.6. This is architecturally closest to
OpenCode's own two-layer split (§3.1), but pi's two layers classify
retryability by genuinely different means from each other (regex/string
matching on error text at the outer layer; HTTP status codes and an
SDK-supplied header at the inner layer) rather than by two independent
readings of the same structured error taxonomy the way OpenCode's inner and
outer layers both do.

### 4.2 The inner, request layer: `retryProviderRequest` -- reimplementing the SDKs' own policy, made abortable

VERIFIED, `packages/ai/src/utils/provider-retry.ts`, full file read this
session. The module's own doc comment states its purpose plainly: "Reproduce
the retry behavior used by the OpenAI and Anthropic SDKs while making their
backoff sleep interruptible. Their built-in retry timers ignore the request
AbortSignal, so callers must invoke the SDK with `maxRetries: 0` and wrap the
request with this helper." A second comment marks this as a maintenance
liability pi's own authors flagged explicitly: `isRetryableProviderError`
carries the note "Mirrors the pinned OpenAI/Anthropic SDK retry policy; review
when either SDK is upgraded" -- i.e. this is a deliberately hand-copied
reimplementation of a third party's retry logic, not a wrapper that delegates
to it, and pi's own source acknowledges the resulting drift risk.

Retryability: an `x-should-retry` response header, if present, wins outright
(`"true"` retries, `"false"` does not); otherwise the function retries on HTTP
408, 409, 429, or any status `>= 500`, or on any error with no status at all
(a raw transport failure). Backoff: a `retry-after-ms` header value is used
verbatim if present and parseable; failing that, a `retry-after` header is
parsed as either a seconds count or an HTTP date and converted to a
millisecond offset; failing both, the function falls back to `Math.min(0.5 *
2 ** retryIndex, 8) * 1000` -- an exponential schedule capped at 8 seconds --
multiplied by `(1 - Math.random() * 0.25)`, i.e. **negative-only jitter**: the
computed delay is always shortened by 0-25%, never lengthened, a materially
different jitter shape from OpenCode's symmetric ±20% band (§3.2) or Claude
Code's floor-only treatment of a short server `Retry-After` (§1.4). Either
header-derived or computed, the delay is passed through
`validateServerRetryDelayMs()`, which **throws** rather than waits if the
value exceeds `maxRetryDelayMs` (default 60,000ms): "Server requested Ns retry
delay (max: Ms)." -- a fail-fast-on-an-excessive-server-requested-wait
behavior distinct from every other harness this page examines, none of which
document refusing to honor an oversized `Retry-After` outright.

`maxRetries` at this layer defaults to `0` -- **off** -- per the function
signature (`options.maxRetries ?? 0`) and confirmed independently by
`settings.md`'s own default table in §4.4 below. A comment on the retry loop
itself records a subtle correctness property: "Each retry is a fresh SDK
request, so X-Stainless-Retry-Count remains zero" -- because pi disables the
Stainless-generated OpenAI/Anthropic SDK client's own internal retry counter
(`maxRetries: 0`) and re-issues a wholly new request object per attempt
itself, the SDK's own telemetry header never reflects that a retry happened
at all, a client-observable side effect of choosing to reimplement rather than
delegate to the SDK's retry loop. Aborts are handled by an
`AbortSignal`-aware `abortableSleep()` that rejects immediately if the signal
is already aborted or fires mid-sleep, converting to a named `AbortError`.

### 4.3 The outer, turn layer: `retryAssistantCall` and its string-pattern error classifier

VERIFIED, `packages/ai/src/utils/retry.ts`, full file read this session,
cross-checked against `packages/ai/test/retry.test.ts`'s 20+ classification
cases. `retryAssistantCall()` wraps `produce(): Promise<AssistantMessage>` --
a whole assistant-message-producing call, which in practice is either one
agent turn or (per §4.5) one compaction/summarization call, not a single HTTP
request. Its own doc comment states the full behavior: "A successful response
is returned immediately. Aborts are terminal and never retried... A
non-retryable error... is returned immediately so deterministic errors fail
fast. Otherwise retries up to `maxRetries` times with exponential backoff."
The policy shape is the same `{enabled, maxRetries, baseDelayMs}` triple
`settings.md` documents (§4.4); the per-attempt delay is `baseDelayMs * 2 **
(attempt - 1)` with **no jitter at all** at this layer -- jitter here exists
only one layer down, inside §4.2's inner retry.

Classification (`isRetryableAssistantError`) is deliberately **not**
status-code-based -- it is two large, named, hand-maintained regular
expressions matched against the plain-text `errorMessage` string, source-read
in full: `NON_RETRYABLE_PROVIDER_LIMIT_ERROR_PATTERN` (checked first, wins on
a tie) matches OpenCode's own `GoUsageLimitError`/`FreeUsageLimitError` JSON
error-type names, subscription-limit wording ("Monthly usage limit reached,"
"available balance"), and generic quota/billing exhaustion text
(`insufficient_quota`, "out of budget," "quota exceeded," "billing");
`RETRYABLE_PROVIDER_ERROR_PATTERN` matches generic overload/rate-limit/HTTP
5xx wording, wrapper text for upstream failures (including an OpenRouter
"Provider returned error" pattern and an "exceeded request buffer limit while
retrying upstream" pattern, both tagged to specific pi GitHub issue numbers in
source comments, `#2264` and unlabeled respectively), a long list of
network/transport-failure substrings (`ENOTFOUND`, `EAI_AGAIN`, "socket hang
up," "connection refused," generic `timeout`), WebSocket-specific close/error
text, SDK-specific premature-stream-ending messages (Anthropic's "stream ended
before message_stop," tagged `#4433`; a Bedrock/Smithy HTTP/2 no-response
error, tagged `#3594`), explicit retry-guidance phrases some providers emit
mid-stream ("you can retry your request," "try your request again," tagged
`#6019`), gRPC's `ResourceExhausted` (for NVIDIA NIM), and -- the one pattern
that exists purely to couple this layer to §4.2 -- the literal substring
`"retry delay"`, with a source comment explaining why: "Provider-requested
retry delay cap failures should flow through the outer retry policy so
callers can surface/abort the backoff (`#1123`)." This is a **deliberate,
named cross-layer coupling**: when §4.2's inner layer throws its
`maxRetryDelayMs`-exceeded error, that thrown error's own message text is
worded so it matches this outer layer's retryable pattern, meaning an
inner-layer cap violation does not simply fail the turn outright -- it
re-enters the outer, turn-level retry budget and backoff instead, exactly as
the flowchart in §4.1 shows.

Callback hooks (`onRetryScheduled`, `onRetryAttemptStart`, `onRetryFinished`)
fire around each attempt; `onRetryScheduled` is what the coding-agent product
uses to drive user-facing retry countdown UI, and (per §4.5) the identical
mechanism is reused, under a different event name, for compaction's own
summarization retries. An abort that lands **during** the backoff sleep is
normalized to the same `stopReason: "aborted"` `AssistantMessage` shape a
provider-level abort would produce, "so callers do not need to care when
cancellation happened" -- the same don't-make-the-caller-distinguish-abort-
timing design goal §3.3 found, independently, in OpenCode's own
`SessionRetry`.

### 4.4 Settings surface, and the documented reason to keep the inner layer off

VERIFIED, `packages/coding-agent/docs/settings.md`, "Retry" section, fetched
in full this session.

| Setting | Type | Default | Effect |
|---|---|---|---|
| `retry.enabled` | boolean | `true` | Enables the outer, §4.3 turn-level retry |
| `retry.maxRetries` | number | `3` | Outer-layer attempt cap |
| `retry.baseDelayMs` | number | `2000` | Outer-layer backoff base (2s, 4s, 8s at attempts 1-3) |
| `retry.provider.timeoutMs` | number | SDK default | Per-request timeout passed to the underlying SDK client |
| `retry.provider.maxRetries` | number | `0` | Inner, §4.2-layer attempt cap -- **off** by default |
| `retry.provider.maxRetryDelayMs` | number | `60000` | Inner-layer cap beyond which a server-requested delay fails fast instead of waiting (§4.2); `0` disables the cap entirely |

The docs state the reason for the inner layer's off-by-default posture
directly, and it is a genuine architectural warning, not a generic
recommendation: "Keep `retry.provider.maxRetries` at `0` unless provider-level
retries are explicitly needed. Setting it above `0` can make SDK/provider
retries handle out-of-usage-limit errors before Pi sees them, which may block
the agent until the provider quota resets in some circumstances." In other
words, turning on the inner, status-code-based layer risks the SDK itself
silently absorbing and re-waiting-out an error that the outer,
string-pattern-based layer would have classified as a **non-retryable**
quota/billing exhaustion and failed fast on instead -- the two layers'
independently-authored classifiers can disagree, and the documented
recommendation is to let the outer layer see every failure first by leaving
the inner layer's own retry budget at zero.

### 4.5 Reuse by compaction: the same policy, not a separate hard-coded loop

VERIFIED, `packages/coding-agent/test/suite/regressions/
6647-compaction-retries-transient-stream-drop.test.ts`, full file read this
session, plus its own doc comment: "Regression for `#6647`: compaction runs a
single non-retried summarization call, so a transient mid-stream socket death
(`terminated`) failed the whole compaction. Verifies that summarization now
reuses `settings.retry` (bounded retries with exponential backoff gated on
`isRetryableAssistantError`), emits `summarization_retry_*` events, and that
aborts / non-retryable errors are not retried." The test suite exercises this
directly: a scripted transient `"terminated"` error retried twice before a
scripted success (asserting exactly `maxAttempts + 1` calls and a matching
`summarization_retry_scheduled`/`summarization_retry_finished` event pair), a
scripted `"insufficient_quota"` error that is **not** retried at all (zero
`summarization_retry_scheduled` events, immediate rejection), a case with
`retry.enabled: false` behaving identically to the non-retryable case, a case
where `maxRetries` is exhausted and the failure still propagates after the
correct number of attempts, and a case where `abortCompaction()` mid-backoff
is asserted to terminate the retry loop and mark `compaction_end` as
`aborted: true`.

This is a direct, worthwhile contrast against Claude Code's own compaction
retry loop (§1.4): Claude Code ships compaction's own **separate, small,
hard-coded circuit breaker** (3 attempts, no configurability, per its
changelog's v2.1.76 entry) rather than routing through its main API-request
policy. pi does the opposite -- compaction's summarization call is wired
through the exact same `retryAssistantCall`/`settings.retry` policy an
ordinary agent turn uses, configurable by the same two settings-file keys,
distinguished from an ordinary turn only by which `summarization_retry_*`
event name the callbacks emit. [context-compression.md](context-compression.md)
§4.5 documents the companion fact this page does not re-derive: pi keeps
**overflow recovery** (a context-window-exceeded failure) on a structurally
separate code path from this retry-with-backoff mechanism entirely --
`custom-provider.md`'s own guidance warns a custom-provider author
specifically against letting an overflow-error-message normalization also
match rate-limit/throttling text, "would falsely trigger compaction instead
of pi's normal retry-with-backoff path" -- the same clean-carve-out discipline
this page finds independently, from source, in OpenCode's context-overflow
handling (§3.2-3.3) and Claude Code's docs (§1.1).

### 4.6 A third, structurally distinct layer: durable, crash-recoverable retry state in `pi-agent-core`

VERIFIED, `github.com/earendil-works/pi`'s `packages/agent/docs/harness.md`
(the `@earendil-works/pi-agent-core` package's own design document, fetched in
full this session), read alongside `packages/agent/src/harness/
agent-harness.ts` (source, also fetched in full). This is a formal,
state-machine-level specification for a different concern than §4.2-4.5:
**surviving a process crash or restart mid-retry**, something no other
harness's retry mechanism this page documents is shown to do explicitly.
`agent-harness.ts` holds a `private retryPolicy: RetryPolicy` field defaulting
to `{ enabled: false, maxRetries: 0, baseDelayMs: 1000 }` when no policy is
supplied at construction -- **disabled by default at this framework layer**;
it is `pi-coding-agent`'s own `settings.md` defaults (§4.4) that turn it on
for end users of the actual CLI product, a distinct default from the
framework it is built on, worth stating precisely rather than conflating the
two.

`harness.md`'s own state tables describe the mechanism: at the moment an
assistant-generation checkpoint begins, the harness "conditionally
snapshot[s] current lane config, stream options, and normalized retry policy
inline into the context" as part of one atomic transaction moving the
operation into a `ready` state with `nextAttempt: 1`. On a retryable error
with attempts remaining, the operation moves to a dedicated `retry_wait`
state carrying `nextAttempt: k+1` and a `notBefore` timestamp -- a durable
register, not an in-memory timer -- and the doc states explicitly: "For each
attempt... an elapsed retry wait first returns to `ready`," meaning if the
process crashes or restarts while a retry backoff is pending, reopening the
operation reads this durable `retry_wait` state directly rather than
inferring position from a journal, and resumes the wait (or immediately
proceeds, if `notBefore` has already elapsed) "under the **captured** retry
policy" from when the operation began -- explicitly *not* whatever the
harness's live retry-policy setting might have changed to in the meantime.
The doc is equally explicit that this state machine checks context-window
**overflow** before retryable-error classification ("retryable `error`,
attempts remain / otherwise" is evaluated only after the overflow branch),
independently corroborating, from this different and more formal source, the
overflow-is-a-separate-path finding §4.5 already draws from
`custom-provider.md`. Numeric edges are stated precisely too:
`RetryPolicy`'s `maxRetries` and `baseDelayMs` "must be finite non-negative
safe integers and `maxRetries + 1` must remain safe; disabled retry
normalizes to one attempt," and "exponential delay and `notBefore` arithmetic
saturate at `Number.MAX_SAFE_INTEGER`" -- an explicit overflow guard on the
backoff math itself, a concern none of Claude Code's, Copilot CLI's, or
OpenCode's own retry documentation states this page found equivalently.

---

## 5. Hermes Agent (Nous Research)

Primary sources, all VERIFIED and fetched or cross-checked fresh this
session (1 September 2026): `hermes-agent.nousresearch.com/docs/user-guide/
configuration` and `.../user-guide/features/fallback-providers` (WebFetch,
plus the site's own concatenated `llms-full-*.txt` doc dump, fetched via
`curl` and grepped for `retry`/`backoff`/`429`/`api_max_retries`), and --
unlike Claude Code and Copilot CLI above, and like OpenCode and pi -- this
harness's own public implementation, `github.com/NousResearch/hermes-agent`
(`main` branch): `agent/retry_utils.py`, `agent/error_classifier.py`,
`agent/conversation_loop.py`, `agent/turn_retry_state.py`,
`agent/nous_rate_guard.py`, `run_agent.py`, and five regression test files,
all fetched in full via `raw.githubusercontent.com` and `gh api`. Hermes
Agent is a sixth, independent, self-hosted product with no dependency on
any harness covered elsewhere on this page -- see [Permissions &
sandboxing architecture](permissions-and-sandboxing.md) §6 for this book's
fuller architectural introduction, not repeated here.

### 5.1 The loop: `while retry_count < max_retries` in `conversation_loop.py`

```mermaid
flowchart TD
    Call["API call attempt\n(agent/conversation_loop.py, run_conversation)"] --> Err{"Exception raised?"}
    Err -->|"no"| Done["finish_reason='stop', continue turn"]
    Err -->|"yes"| Classify["classify_api_error()\nagent/error_classifier.py\n-> ClassifiedError{reason, retryable,\nshould_compress, should_rotate_credential,\nshould_fallback}"]
    Classify --> NousGuard{"provider == nous AND\ncross-session rate-limit\nfile says still limited?"}
    NousGuard -->|"yes"| Fallback1["skip call entirely,\ntry fallback_providers"]
    NousGuard -->|"no"| AuthCk{"401/403?"}
    AuthCk -->|"yes"| AuthRefresh["one-shot per-provider OAuth\nrefresh (codex/anthropic/nous/\ncopilot/vertex) via TurnRetryState guard"]
    AuthRefresh -->|"refreshed"| Call
    AuthRefresh -->|"failed"| AuthFail["auth_failover_attempted ->\nfallback_providers chain"]
    AuthCk -->|"no"| PoolCk["_recover_with_credential_pool()\n(rotate to next key in pool)"]
    PoolCk -->|"rotated"| Call
    PoolCk -->|"no pool / exhausted"| FormatCk["format-recovery one-shots:\nimage shrink, thinking-sig strip,\nlength-continuation, grammar fallback, ..."]
    FormatCk -->|"handled"| Call
    FormatCk -->|"classified.retryable == False\n(is_client_error)"| Terminal["abort retry loop,\ntry fallback_providers once"]
    FormatCk -->|"retryable == True,\nretry_count < max_retries"| Backoff["jittered_backoff() or\nadaptive_rate_limit_backoff()\nor Retry-After header (capped 600s)"]
    Backoff --> Call
    FormatCk -->|"retry_count >= max_retries"| Recover["_try_recover_primary_transport()\n(one-shot; resets retry_count=0)"]
    Recover -->|"recovered"| Call
    Recover -->|"failed"| Fallback2["_try_activate_fallback()\n(resets retry_count=0, one shot/turn)"]
    Fallback1 --> Fallback2
    Terminal --> Fallback2
    Fallback2 -->|"activated"| Call
    Fallback2 -->|"no chain / exhausted"| Give["return failed=True,\nfailure_reason, failure_retryable"]
```

Hermes' primary-model retry mechanism lives entirely inside one function,
`run_conversation` in `agent/conversation_loop.py` (502KB of source, fetched
in full this session): `max_retries = agent._api_max_retries` set once per
API-call block, `while retry_count < max_retries:` as the loop condition,
and a fresh `TurnRetryState()` instance per iteration bookkeeping which
one-shot recovery branch has already fired. `agent._api_max_retries` is
wired from `agent.api_max_retries` in `config.yaml`
(`agent/agent_init.py`: `_raw_api_retries = _agent_section.get
("api_max_retries", 3)`), documented directly: "`agent.api_max_retries`
controls how many times Hermes retries a provider API call on transient
errors (rate limits, connection drops, 5xx) **before** fallback-provider
switching engages. The default is `3` -- four attempts total." A
regression test (`tests/run_agent/test_api_max_retries_config.py`, closing
issue `#11616`, "make the hardcoded `max_retries = 3` in the agent's API
retry loop user-configurable so fallback-provider setups can fail over
faster on flaky primaries instead of burning ~3x180s on the same stall")
confirms both the `3`-attempt legacy default and that setting
`agent.api_max_retries: 1` or `: 5` in config propagates directly to
`agent._api_max_retries`. This four-attempts-by-default cap is considerably
tighter than Claude Code's 10 (§1.1) and structurally different from
OpenCode's effectively uncapped outer `SessionRetry` (§3.3) or pi's
separately-configurable 3-attempt outer layer (§4.4) -- Hermes ties its
one and only primary-call retry budget directly to when fallback-provider
switching takes over, rather than layering an inner transport retry
beneath an outer turn retry the way OpenCode and pi both do.

### 5.2 Error classification: `FailoverReason`, a nine-axis taxonomy with per-branch recovery hints

VERIFIED, `agent/error_classifier.py` (99,558 bytes, read in full this
session). The module's own docstring states its role precisely: "Provides
a structured taxonomy of API errors and a priority-ordered classification
pipeline that determines the correct recovery action (retry, rotate
credential, fallback to another provider, compress context, or abort)...
the main retry loop in run_agent.py consults for every API failure" (the
comment is stale on the caller's filename -- the consultation call site
this session found is `agent/conversation_loop.py`, not `run_agent.py`
directly, but the classifier module itself is unchanged by that). Every
call to `classify_api_error()` returns a `ClassifiedError` dataclass
carrying a `FailoverReason` enum value (`auth`, `auth_permanent`,
`billing`, `rate_limit`, `upstream_rate_limit`, `overloaded`,
`server_error`, `timeout`, `ssl_cert_verification`, `context_overflow`,
`payload_too_large`, `image_too_large`, `image_corrupt`, `model_not_found`,
`provider_policy_blocked`, `content_policy_blocked`, `format_error`,
`invalid_encrypted_content`, `multimodal_tool_content_unsupported`,
`thinking_signature`, `long_context_tier`,
`oauth_long_context_beta_forbidden`, `llama_cpp_grammar_pattern`, and a
catch-all `unknown`) plus four independent boolean recovery hints --
`retryable`, `should_compress`, `should_rotate_credential`,
`should_fallback` -- that "the retry loop checks... instead of
re-classifying the error itself." This is a richer, more explicitly
multi-dimensional taxonomy than any of Claude Code's documented category
list (§1.1), OpenCode's `retryable: boolean` field on its structured error
schema (§3.2), or pi's two independent regex/status-code classifiers
(§4.1-4.2): a single Hermes classification carries retryability, a
compress-instead-of-retry signal, a credential-rotation signal, and a
fallback-worthiness signal as four separately-settable flags on one
result, letting a single error (e.g. a 429 classified `rate_limit`) drive
three different recovery actions in sequence (rotate credential, then
retry with backoff, then escalate to fallback) rather than one.

The status-code dispatch in `_classify_by_status()` (lines 1243-1535,
read in full) is worth reproducing at the level of concrete carve-outs
this page's other sections document for their own harnesses: 401 is
`retryable=False` but `should_rotate_credential=True` --
"credential pool rotation and provider-specific refresh (Codex, Anthropic,
Nous) run *before* the retryability check... if those succeed, the loop
`continue`s. If they fail, `retryable=False` ensures we hit the
client-error abort path." 402 and billing-pattern 403/404/429 bodies
(a `_BILLING_PATTERNS` list of 18 phrases including `"insufficient
credits"`, `"out of extra usage"`, `"account is deactivated"`) are
`retryable=False` -- a real fix, `#31273`, had to *remove*
`FailoverReason.billing` from an exclusion set that previously let a 402
fall through to the generic retry-backoff path regardless of
`retryable`, with the regression test's own real-world citation: "~$40
burned in 48h on a 24/7 gateway routing Telegram + Discord traffic" from a
single pay-per-token 402 retried `api_max_retries` times per turn, every
turn. 413 is `retryable=True, should_compress=True`. 429 runs a
multi-signal disambiguation the classifier's own comments call out by
issue number: an `_OVERLOADED_PATTERNS` match (Z.AI/Zhipu server-wide
overload sharing HTTP 429 with genuine per-credential throttling) routes
to `overloaded` and retries the *same* credential rather than rotating it
("`#14038`... the correct recovery is 'back off and retry the same key',
NOT 'rotate the credential' (which exhausts the pool while the endpoint is
still busy)"); an OpenRouter-aggregator-wrapped upstream 429 routes to
`upstream_rate_limit` with `should_rotate_credential=False,
should_fallback=True` ("the user's key is healthy, so marking it
exhausted / rotating is wrong and burns the key for ~24min"); an explicit
usage-limit or billing phrase without an explicit rate-limit phrase routes
to non-retryable `billing` (`#39441`); everything else routes to
retryable `rate_limit`. 500/502 and 503/529 both carry a request-
validation-signal carve-out ("some OpenAI-compatible gateways return
request-validation errors with a 5xx status... these are deterministic --
every retry gets the identical rejection -- so the generic '5xx ->
retryable server_error' rule turns one bad request into a retry flood")
and a context-overflow-as-5xx carve-out for local inference servers
(llama.cpp/Ollama/vLLM) that report overflow via HTTP 500 instead of the
standard 400/413, routed to `context_overflow` (compress, don't retry
blindly) rather than blind `server_error` retries. 408 routes to
retryable `timeout` per RFC 9110 §15.5.9 rather than falling into the
generic non-retryable 4xx bucket. Content-policy/safety-filter refusals
are a further, source-and-test-confirmed carve-out
(`tests/run_agent/test_18028_content_policy_blocked.py`, `#18028`): the
provider often raises *without a status code at all* ("This content was
flagged for possible cybersecurity risk..."), which previously fell
through to the retryable `unknown` catch-all and burned all
`api_max_retries` attempts on a deterministic refusal before surfacing
"API failed after 3 retries" with no explanation; the fix pattern-matches
the message text directly to non-retryable `content_policy_blocked` with
`should_fallback=True`, narrow enough (per its own defensive test) not to
collide with a generic 400 format error or OpenRouter's distinct
account-level `provider_policy_blocked` classification.

### 5.3 Backoff: `jittered_backoff()`, a positive-only-jitter exponential with a provider-specific long-tail carve-out

VERIFIED, `agent/retry_utils.py` (209 lines, read in full this session).
The module's own docstring states its purpose as a deliberate departure
from a fixed schedule: "Replaces fixed exponential backoff with jittered
delays to prevent thundering-herd retry spikes when multiple sessions hit
the same rate-limited provider concurrently." `jittered_backoff(attempt,
*, base_delay=5.0, max_delay=120.0, jitter_ratio=0.5)` computes `delay =
min(base_delay * 2**(attempt-1), max_delay)` then adds `jitter =
uniform(0, jitter_ratio * delay)` -- **positive-only** jitter (the
computed delay is always lengthened, by 0-50% at the default ratio),
the mirror-image of pi's own negative-only (-0 to -25%) jitter shape
(§4.2) and a different shape again from OpenCode's symmetric ±20% band
(§3.2). The jitter's random seed is deliberately decorrelated across
concurrent callers within one process: a module-level `_jitter_counter`
protected by a `threading.Lock` is combined with `time.time_ns()` via XOR
so "multiple sessions retrying simultaneously" don't compute the same
delay from a coarse clock tick, a concern this page has not seen stated
explicitly for any of Claude Code's, Copilot CLI's, or OpenCode's own
jitter implementations. The function is called with two different
`(base_delay, max_delay)` pairs at two distinct call sites in
`conversation_loop.py`: the main API-error retry path uses `base_delay=2.0,
max_delay=60.0` (line 6892: "for rate limits, respect the Retry-After
header if present" first, falling back to `jittered_backoff` only when no
header is present), while a structurally separate sub-loop handling
**invalid/malformed API responses** (empty or garbled completions, not
exceptions) reuses the same `retry_count`/`max_retries` loop variables but
calls `jittered_backoff(retry_count, base_delay=5.0, max_delay=120.0)`
(line 3709) -- two different backoff schedules sharing one attempt
counter and one cap, a design wrinkle distinct from any other harness's
retry architecture this page documents.

When a `Retry-After` header is present on a rate-limited response, Hermes
honors it verbatim but **caps it at 600 seconds (10 minutes)**, and the
source comment states precisely why the earlier, tighter cap was wrong:
"Cap at 10 minutes. Anthropic Tier 1 input-token buckets reset in ~171s,
so a 120s cap caused us to retry before the actual reset window and
re-trip the limit. 600s covers all realistic provider reset windows while
still rejecting pathological values. (`#26293`)" -- i.e. an earlier,
smaller ceiling was itself a self-inflicted retry-amplification bug, fixed
by widening the cap rather than tightening it, the opposite correction
direction from Claude Code's own v2.1.98 fix (§1.4), which *enforces* a
computed minimum against a small server-supplied `Retry-After` rather than
capping a large one. A dedicated `parse_retry_after_seconds()` helper
(also in `retry_utils.py`, exercised by its own test class) accepts either
a raw header value or a headers-mapping object, parses a numeric string,
a bare number, or an RFC 7231 HTTP-date form, and clamps negative deltas
to `0.0`.

A third, narrowly-scoped backoff policy sits beside the generic one:
`adaptive_rate_limit_backoff()` recognizes a specific Z.AI Coding Plan
GLM-5.2 overload signature (HTTP 429, body error code `"1305"`, message
"The service may be temporarily overloaded...", matched only when the
request's own `base_url` and `model` confirm the narrow provider/model
pair, "so ordinary quota/billing 429s still fail fast through the
existing classifier") and, for that signature only, keeps the first three
retries ("`short_attempts`") on the normal short exponential schedule,
then switches to a fixed table of **progressively longer waits -- 30s,
60s, 90s, 120s -- each with a smaller, 0.2 jitter ratio** ("keeps long
waits readable while still avoiding synchronized retry storms"). A
companion function, `zai_coding_overload_retry_ceiling()`, exists purely
to solve a self-discovered dead-code bug the module's own docstring names
directly: "With the default `api_max_retries` (3) equal to
`short_attempts` (3), the loop always gave up before reaching the long
tier, leaving the whole long-backoff schedule as dead code" -- so the
retry loop extends its own ceiling specifically for this error signature
(`conversation_loop.py` line 5684: `max_retries = max(max_retries,
zai_coding_overload_retry_ceiling())`), a provider-specific,
self-correcting exception to the otherwise-uniform `api_max_retries`
budget that this page finds no equivalent of in Claude Code's, Copilot
CLI's, OpenCode's, or pi's own retry documentation or source.

### 5.4 Disabling the SDK's own retry loop -- and the one path where it stays on

VERIFIED, `run_agent.py` (line 5748, read in context this session). For
per-request OpenAI-wire clients, Hermes sets `request_kwargs["max_retries"]
= 0` explicitly, and the source comment states the reasoning in the same
terms this page's own pi section (§4.2/§4.4) documents independently for a
wholly different codebase: "should not run the SDK's built-in retry loop:
the agent's outer loop owns retries with credential rotation, provider
fallback, and backoff that the SDK can't see. Leaving SDK retries on
(default 2) compounds with our outer retries and lets a single hung
provider request stretch to ~3x the per-call timeout before our stale
detector reports it." This is the third harness this page finds
explicitly disabling an underlying SDK's or provider's own retry policy to
prevent double-counted compounding -- alongside pi's `retry.provider.
maxRetries: 0` default (§4.4) and, in effect, OpenCode's own inner/outer
split (§3.1) -- independently arrived at in a third, unrelated codebase.
The comment also notes the scope of the fix precisely: "Shared/primary
clients and Anthropic / Bedrock paths are unaffected (they don't go
through here)" -- the `max_retries=0` override is scoped to the
OpenAI-wire request path specifically, not universal.

Nous Portal is the one path this session found where the underlying SDK's
own retries are **not** disabled, and Hermes' own source documents the
resulting amplification directly as the reason a wholly separate
cross-session file exists. `agent/nous_rate_guard.py`'s module docstring:
"Each 429 from Nous triggers up to 9 API calls per conversation turn (3
SDK retries x 3 Hermes retries), and every one of those calls counts
against RPH. By recording the rate limit state on first 429 and checking
it before subsequent attempts, we eliminate the amplification effect." The
guard persists rate-limit state to a shared file
(`~/.hermes/rate_limits/nous.json`, written via the same `atomic_replace()`
helper §5.3's Windows-retry logic uses) so that CLI, gateway, cron, and
auxiliary-task sessions all check one on-disk state before issuing a new
Nous request, extracting the best available reset estimate in priority
order from `x-ratelimit-reset-requests-1h`, `x-ratelimit-reset-requests`,
then a generic `retry-after` header. `conversation_loop.py`'s own retry
loop consults this guard as its very first action on every iteration when
`agent.provider == "nous"` (before even attempting the API call): if
another process already recorded an active rate limit, the loop skips the
call entirely and goes straight to `_try_activate_fallback()` rather than
spending one of its own `api_max_retries` attempts (and, transitively, up
to three SDK-level sub-attempts) confirming what a sibling session already
knows. This is a cross-process retry-budget-sharing mechanism this page
finds no equivalent of, confirmed or claimed, in any of Claude Code's,
Copilot CLI's, OpenCode's, or pi's own retry architecture -- all four are
documented and sourced as strictly single-process/single-session retry
state.

### 5.5 One-shot recovery guards and the two retry-budget resets

VERIFIED, `agent/turn_retry_state.py` (94 lines, read in full this
session). Its own docstring names the design problem directly: the inner
retry loop "makes several distinct recovery attempts on a single model API
call: a credential-pool 429 retry, a per-provider OAuth refresh (codex,
anthropic, nous, copilot), a long-context compression restart, a length-
continuation restart, and a handful of format-recovery branches...
[which] used to be ~16 bare `*_attempted` / `has_retried_*` /
`restart_with_*` locals declared inline before the loop and threaded
through its 2,400-line body." `TurnRetryState` is a single dataclass, one
fresh instance per API-call block, collapsing those into named one-shot
boolean guards (`codex_auth_retry_attempted`,
`nous_paid_entitlement_refresh_attempted`,
`copilot_stale_cred_retry_attempted`, `thinking_sig_retry_attempted`,
`image_shrink_retry_attempted`, `llama_cpp_grammar_retry_attempted`,
`auth_failover_attempted`, and more) plus a small set of `restart_with_*`
signals the loop reads after an attempt to decide whether to rebuild the
request and retry. Two of these guards double as **retry-budget resets**,
distinct from the four-attempt `api_max_retries` cap itself: when
`_try_recover_primary_transport()` (a one-shot rebuild of the primary HTTP
client for a stale connection pool or TCP reset) succeeds, or when
`_try_activate_fallback()` successfully swaps to a `fallback_providers`
entry, `conversation_loop.py` sets `retry_count = 0` and restarts the
`while` loop with a fresh attempt budget against the recovered or new
target -- so `api_max_retries` bounds each *target* (the current primary
client, then the recovered primary, then each fallback in turn) rather
than the whole turn. A live regression, `#32646` ("fallback_providers not
activated when HTTP 429 follows a successful primary-transport
recovery"), documents exactly this reset interacting badly with a race:
"an eager-fallback attempt that lost its race with a concurrent session
mutating the on-disk credential pool could leave `_fallback_index`
advanced past the chain length without setting `_fallback_activated` to
True. The subsequent 429s then short-circuited the eager-fallback gate...
so the retry budget burned on the primary model with no fallback ever
attempted" -- fixed by resetting `_fallback_index`, `_fallback_activated`,
and `TurnRetryState.has_retried_429` together whenever transport recovery
fires, so a post-recovery 429 always gets a fresh fallback-chain attempt
rather than inheriting stale bookkeeping from before the reset.

### 5.6 `fallback_providers`: the alternative-to-retry mitigation, reset-aware and turn-scoped

VERIFIED, `hermes-agent.nousresearch.com/docs/user-guide/features/
fallback-providers`, fetched fresh this session. A top-level
`fallback_providers:` list (the legacy singular `fallback_model:` key is
still honored for back-compat) names an ordered chain of backup
`provider`/`model` pairs Hermes swaps to "mid-session without losing your
conversation" once the primary exhausts its `api_max_retries` budget on
rate limits or server errors, or immediately (no retry spent at all) on
auth failures or a 404. This is the same general alternative-to-retry
concept this page's own §1.5 (Claude Code `fallbackModel`), §2.4
(Copilot CLI `continueOnAutoMode`), and §4 intro (pi has none) already
document, but Hermes' own docs state two behaviors this page has not
sourced for any of the other three: the switch is **turn-scoped, not
session-scoped** ("each new user message starts with the primary model
restored... within a single turn, fallback activates at most once -- if
the fallback also fails, normal error handling takes over (retries, then
error message). This prevents cascading failover loops within a turn
while giving the primary model a fresh chance every turn"), and the
per-turn retry decision is **reset-aware**: "when the primary's
credentials report a rate-limit reset time that hasn't elapsed yet
(subscription windows like Claude Pro/Max's 5-hour blocks or Codex weekly
limits report these as hours or days), Hermes skips the doomed retry and
stays on the fallback until the reset passes -- avoiding two pointless
provider switches (and two prompt-cache invalidations) per turn." The docs
also name an unavoidable cost documented nowhere else on this page: prompt
caches are keyed to the serving model/account, so "when fallback fires,
the new provider:model has no cached prefix for your conversation, so the
next request re-reads the entire history at full input-token price... the
same applies when the turn ends and the primary is restored." This ties
the fallback mechanism this page documents (§5.4-§5.5) directly to a
real, quantified cost this book's own [caching.md](caching.md) does not
otherwise attach to a retry/fallback event for any of the other three
harnesses.

### 5.7 Self-reported failure modes

Five distinct, source-and-issue-number-confirmed bugs this session found
in Hermes' own repository, each fixed by a dedicated regression test named
after the closed issue: `#11616` (a hardcoded `max_retries = 3` had no
config surface at all, closed by adding `agent.api_max_retries`); `#31273`
(`FailoverReason.billing` was wrongly excluded from the non-retryable
abort path, letting a single HTTP 402 burn `api_max_retries` paid attempts
against an exhausted balance every turn, "~$40 burned in 48h on a 24/7
gateway"); `#18028` (a status-code-less content-policy refusal fell into
the retryable `unknown` catch-all and burned all retries on a
deterministic safety-filter block before surfacing an unhelpful "API
failed after 3 retries"); `#14038` (Z.AI/Zhipu's server-wide-overload 429
was indistinguishable from a genuine per-credential rate limit, so the
classifier rotated a perfectly healthy credential out of the pool instead
of backing off and retrying it); and `#32646` (a race in fallback-index
bookkeeping after a successful primary-transport recovery silently
disabled the fallback chain for the rest of the turn). None of these
required a coordinated rewrite of the retry mechanism itself -- each is a
narrow classification or bookkeeping fix layered onto the same
`while retry_count < max_retries` loop and `FailoverReason` taxonomy --
which this page notes as a different failure-mode shape from Claude
Code's historical over-tightening/under-bounding swings (§1.7) or
OpenCode's still-open unbounded-`SessionRetry` issue (§3.4): Hermes' own
self-reported bugs are consistently about *misclassification* (an error
routed to the wrong `FailoverReason`, burning a bounded budget on a case
that should have failed fast or bypassed the budget entirely) rather than
the retry budget itself being absent or unbounded.

---

## 6. DeepSeek Harness

Primary sources, all VERIFIED and fetched fresh this session (1
September 2026): `github.com/deepseek-ai/deepseek-harness`, `master`
branch -- `packages/llm/llm/src/retry-policy.ts` (the policy schema and
resolver), `packages/llm/llm/src/error.ts` (the `LlmError`/`LlmFailure`
types and canonical error codes), `packages/llm/llm-retry/src/index.ts`
(the retry executor plugin), `packages/llm/llm-retry/src/types.ts`
(durable event payloads), `packages/llm/llm-retry/src/invariant.ts`
(in-session retry invariant validation), `packages/llm/llm-retry/src/
history.ts` (durable provider-route lookup), `packages/llm/llm-retry/
README.md` (the package's own user/maintainer reference), `.agents/
notes/implemented/feature/2026-07-24-provider-retry-policies.md` (the
architectural decision record), `.agents/notes/implemented/
simplification/2026-07-27-request-error-retry-action.md` (the recovery
control flow), `packages/util/timeout/src/index.ts` (`MAX_TIMER_DELAY_MS`
= 2,147,483,647), `packages/llm/llm-retry/tests/retry.spec.ts` (the
comprehensive unit test suite, 20+ cases), and `packages/llm/llm-retry/
tests/transport-recovery.spec.ts` (wire-level recovery integration
tests through the real DeepSeek HTTP/SSE adapter). DeepSeek Harness
("DSH") is a developer-preview, plugin-architecture agent platform;
its retry mechanism is genuinely source-verified end to end, from the
configurable per-provider policy through the durable executor to the
invariant checker, plus two independent test suites.

### 6.1 Architecture: provider-owned policy, plugin-owned execution, durable before wait

```mermaid
flowchart TD
    Fail["Model request fails\n(agent/request-error waterfall)"] --> HasPolicy{"failure.retryPolicy\ndefined? (bound to\nserving registration at\ncall time)"}
    HasPolicy -->|"undefined\n(no adapter served)"| Delegate1["return next()\ndelegates downstream"]
    HasPolicy -->|"defined"| Mode{"policy.mode?"}
    Mode -->|"'always'"| AlwaysDownstream["settleDownstream(next())\nfirst; if downstream\nreturns {kind:'retry'}\nhonor it immediately"]
    AlwaysDownstream -->|"downstream fails\nor returns non-retry"| CodeCheckA{"failure.providerRetryAfterMs\n> policy.maxDelayMs?"}
    CodeCheckA -->|"yes"| UseLocalA["localDelay(policy, retry, random)\nwith jitter and cap"]
    CodeCheckA -->|"no, header valid"| UseHeaderA["delayMs = providerRetryAfterMs\nexact, unjittered"]
    CodeCheckA -->|"no header"| UseLocalA
    UseLocalA --> AppendA["append llm/retry event\n(durable before wait)\ncancellableDelay(delayMs, signal)"]
    UseHeaderA --> AppendA
    AppendA -->|wait completes| AppendStartedA["append llm/retry-started\nreturn {kind:'retry'}\nloop re-runs same step"]
    Mode -->|"'normal'"| CodeEligible{"failure.code in\npolicy.retryableCodes?"}
    CodeEligible -->|"no"| Delegate2["return next()\n(non-retryable)"]
    CodeEligible -->|"yes"| BudgetCheck{"previousRetry >=\npolicy.maxRetries?"}
    BudgetCheck -->|"yes"| Delegate3["return next()\n(budget exhausted)"]
    BudgetCheck -->|"no"| HeaderCheck{"failure.providerRetryAfterMs\n> policy.maxDelayMs?"}
    HeaderCheck -->|"yes (over-cap)"| Delegate4["return next()\n(over-cap = non-retryable for normal)"]
    HeaderCheck -->|"no, header valid"| UseHeaderN["delayMs = providerRetryAfterMs\nexact, unjittered"]
    HeaderCheck -->|"no header"| UseLocalN["localDelay(policy, retry, random)\nwith jitter and cap"]
    UseHeaderN --> AppendN["append llm/retry event\n(durable before wait)\ncancellableDelay(delayMs, signal)"]
    UseLocalN --> AppendN
    AppendN -->|wait completes| AppendStartedN["append llm/retry-started\nreturn {kind:'retry'}\nloop re-runs same step"]
```

The critical architectural fact this diagram makes explicit: DeepSeek
Harness splits retry into two distinct, cleanly separated concerns. The
**policy** is owned by each concrete provider adapter's configuration
and resolved at adapter-registration time into an immutable
`ResolvedRetryPolicy` object captured in the serving registration. The
**execution** is owned by the optional `@deepseek-ai/dsh-llm-retry`
plugin, a Cordis function plugin with **zero configuration of its own**
-- the README states this plainly: "This policy executor has no config;
providers own `retryPolicy`." A `validateConfig()` guard even rejects
the typo of placing `retryPolicy` on the executor itself with the
message "retryPolicy belongs under each provider configuration." The
plugin operates entirely on the resolved policy already bound to the
failed step's serving registration -- it never re-resolves from the
mutable provider registry, so an adapter swap while a request is in
flight cannot retroactively change the recovery contract.

Another distinguishing property: every scheduled retry is **durable
before its wait**. The plugin appends a non-surface `llm/retry` event
to the session log *before* starting the backoff timer, and a matching
`llm/retry-started` event immediately before the retry executes. The
provider-retry-policies Agent Note states this as the core design rule:
"durable before wait, open-step boundaries. A retry is scheduled through
the session log before any timer starts, so a crash or cancellation
never leaves an invisible pending retry." This is a session-log
durability guarantee -- not the same as pi's agent-core process-crash
recovery (§4.6), which persists retry state as a first-class operation
state in its own state machine -- but it shares the same design goal:
no invisible or un-reconstructable retry. The invariant companion
(`packages/llm/llm-retry/src/invariant.ts`) validates each `llm/retry`
and `llm/retry-started` event at load time and on every append,
binding the provider to the failed step's durable `request/header`,
requiring monotonically increasing retry counts keyed by provider and
canonical policy hash, and ensuring each `llm/retry-started` pairs one
prior scheduled attempt with the same `retryId`.

### 6.2 Two policy modes: `normal` (bounded, code-gated) and `always` (unbounded, downstream-first)

VERIFIED, `packages/llm/llm/src/retry-policy.ts` and `packages/llm/
llm-retry/README.md`. The schema defines exactly two modes via a
discriminated union on `mode`:

**Normal mode** (`mode: 'normal'`). Retries only failures whose
`failure.code` appears in the configured `retryableCodes` list, up to
`maxRetries` retries (so `maxRetries` + 1 total attempts). When the
failure code is not in the eligible set, or when the budget is
exhausted, the plugin calls `next()` and delegates to whatever later
policy sits in the `agent/request-error` waterfall. A provider-sent
`Retry-After` value exceeding `maxDelayMs` causes **immediate
delegation** rather than waiting -- normal mode treats an over-cap
server delay the same way it treats an exhausted budget or a
non-retryable code: the failure is not this policy's to recover from.

The default `retryableCodes`, source-verified as `DEFAULT_RETRYABLE_CODES`
in `retry-policy.ts`:

| Code | Meaning |
|---|---|
| `EMPTY_RESPONSE` | A provider completion that returned zero content blocks -- "Providers occasionally emit a degenerate completion (a terminal stop with zero output); adapters classify it as this failure... The attempt produced nothing durable, so retry policy treats it as safe to repeat." (`error.ts` doc comment) |
| `RATE_LIMIT` | A HTTP 429 (transient capacity throttle), distinguished by adapter-level classification from the non-retryable `QUOTA` code |
| `SERVER` | A HTTP 5xx server error |
| `TIMEOUT` | A per-request timeout, classified by the harness's idle-watchdog layer (`packages/util/timeout/src/index.ts`) |
| `TRANSPORT` | A raw connection failure, reset, or dropped stream |

The default `maxRetries` is `5` (so six total attempts), a deliberate
decision documented in the Agent Note: "Omission selects the shared core
normal default of five retries for every composition, including Web,
headless, and custom profiles."

**Always mode** (`mode: 'always'`). Retries **every** model-request
failure with no attempt limit, stopping only on success, turn
cancellation, or plugin disposal. Before applying its own retry,
always mode first awaits downstream recovery (`settleDownstream(next())`)
and honors a downstream `{kind: 'retry'}` decision -- this lets a
specialized later policy (such as context-overflow compaction) make
progress rather than being bypassed by an always-mode retry that would
simply repeat the same overflowing request. If downstream returns a
non-retry decision or throws, always mode falls back to its own
unbounded retry. An over-cap `Retry-After` header does **not** cause
delegation in always mode -- instead, the plugin uses its configured
local backoff computed by `localDelay()`, preserving the guarantee that
always mode keeps trying. The README's Known Limitations section states
this trade-off plainly: "Always mode retries permanent failures --
authentication, quota, invalid-request, protocol, and unrecoverable
context errors continue until success, cancellation, or disposal;
deployments own provider-specific cost and latency controls."

This two-mode design is architecturally distinct from every other
harness on this page. Claude Code has one bounded policy with a
watchdog override (§1). Copilot CLI has undocumented per-subsystem
retry (§2). OpenCode has two layers with different classifiers but both
bounded-or-not at the layer level (§3). pi has a deliberately-off inner
layer and an outer string-pattern layer (§4). Hermes has a bounded loop
with `FailoverReason`-gated recovery (§5). DeepSeek Harness alone makes
the bounded/unbounded choice a **per-provider-route configuration
decision** -- the same deployment can run a DeepSeek endpoint in normal
mode with 5 retries while running an internal self-hosted endpoint in
always mode, and both policies execute through the same plugin on the
same waterfall. The canonical YAML example in the Agent Note illustrates
exactly this:

```yaml
providers:
  - provider: deepseek
    retryPolicy:
      mode: normal
      maxRetries: 2
      retryableCodes: [EMPTY_RESPONSE, RATE_LIMIT, SERVER, TIMEOUT, TRANSPORT]
      backoff:
        initialDelayMs: 500
        maxDelayMs: 10000
        jitterRatio: 0.1
  - provider: internal
    retryPolicy:
      mode: always
      backoff:
        initialDelayMs: 1000
        maxDelayMs: 30000
        jitterRatio: 0.2
```

### 6.3 Backoff: symmetric jitter around exponential, server `Retry-After` honored exactly when under cap

VERIFIED, `packages/llm/llm-retry/src/index.ts` (`localDelay()`
function) and `retry-policy.ts` (defaults, schema, and resolver).

`localDelay()` computes the exponential term as `Math.min(config.
initialDelayMs * 2 ** Math.min(retry - 1, 1024), config.maxDelayMs)`
-- the exponent is itself capped at 1024 to prevent `Infinity` on very
large retry counts, then the result is capped at `maxDelayMs`. Jitter
is then applied as `1 - config.jitterRatio + 2 * config.jitterRatio *
random()`, a symmetric multiplier around 1.0 in the range `[1 -
jitterRatio, 1 + jitterRatio]` -- the test suite confirms both bounds:
the `jitterRatio: 1` case with `random() => 0` produces a zero-delay
schedule (`1 - 1 + 0 = 0`), and the `jitterRatio: 0.1` case with
`random() => 0` produces a 10% shortening (`1 - 0.1 + 0 = 0.9`), while
`random() => 1` produces a 10% lengthening (`1 - 0.1 + 0.2 = 1.1`).
The final value is again capped at `maxDelayMs`.

This is a **symmetric jitter** shape -- different from Hermes' positive-
only jitter (§5.3), pi's negative-only jitter (§4.2), and OpenCode's
symmetric ±20% band (§3.2). The default `jitterRatio` is `0.1` (±10%),
smaller than any of those three.

When the `LlmFailure` carries a `providerRetryAfterMs` field (set by
the adapter from a `Retry-After` or `retry-after-ms` HTTP header), the
delay logic branches by mode:

- **Normal mode**: if `providerRetryAfterMs > policy.maxDelayMs`, the
  request is **delegated** (not retried by this policy) -- an over-cap
  server delay is treated as equivalent to a non-retryable code. If the
  value fits, it is used **verbatim and unjittered**.
- **Always mode**: if `providerRetryAfterMs > policy.maxDelayMs`, the
  plugin falls back to `localDelay()` (the jittered local backoff)
  rather than delegating. If the value fits, it is used verbatim and
  unjittered, same as normal.

The test suite verifies both branches precisely: `normalConfig({
backoff: { jitterRatio: 1 } })` with `providerRetryAfterMs: 2_000`
and `maxDelayMs: 10_000` produces `delayMs: 2_000` (exact, no jitter);
`normalConfig()` with `providerRetryAfterMs: 10_001` and the default
`maxDelayMs: 10_000` produces no `llm/retry` event at all (delegated);
and `alwaysConfig()` with `providerRetryAfterMs: 10` and `maxDelayMs:
4` produces the local backoff delay `3` (random `=> 1`, `2 * 1.5 *
1 = 3`, capped at 4).

Default backoff constants, all source-verified: `initialDelayMs: 500`,
`maxDelayMs: 10_000` (10 seconds), `jitterRatio: 0.1`, all validated
against `MAX_TIMER_DELAY_MS = 2_147_483_647` from `@deepseek-ai/
dsh-timeout`.

### 6.4 The `agent/request-error` waterfall and `RequestErrorAction`

VERIFIED, `.agents/notes/implemented/simplification/2026-07-27-
request-error-retry-action.md`, `packages/llm/llm-retry/src/index.ts`
(the `recover()` function), and the test suite.

The retry plugin is one listener in the `agent/request-error` Cordis
waterfall. When it receives a failure, its `recover()` function decides
whether to retry (returning `{kind: 'retry'}`) or delegate (calling
`next()` to pass to the next listener). The control flow is:

1. If `retryPolicy === undefined` (no adapter served the request), call
   `next()` immediately.
2. In **always mode**: `await settleDownstream(next())` first. If the
   downstream result is a `{kind: 'retry'}` decision, return it
   immediately without scheduling the plugin's own retry. If the
   downstream throws or returns a non-retry decision, fall through to
   the plugin's own retry scheduling. (A source comment warns: "A later
   policy that ignores cancellation and never settles also prevents
   fallback, turn quiescence, and plugin disposal from completing.")
3. In **normal mode**: if `failure.code` is not in `retryableCodes`,
   call `next()`. If the budget is exhausted (`previousRetry >=
   maxRetries`), call `next()`.

If the decision is to retry, the plugin computes the delay, appends the
`llm/retry` event, waits on a `cancellableDelay()` (a `setTimeout`
wrapped in `AbortSignal.any([signal, lifetime.signal])` for both turn
cancellation and plugin-disposal awareness), appends `llm/retry-started`,
and returns `{kind: 'retry'}`. The loop then closes the failed step and
re-runs the same step inside the same open turn over the same durable
history.

Disposal correctness is precisely specified: the plugin's `ctx.effect()`
cleanup aborts the lifetime `AbortController`, then `await Promise.
allSettled([...active])` drains every in-flight recovery. The test
suite verifies this in four disposal/cancellation scenarios: (a) abort
during backoff (`retryFiber.dispose()` while a timer is pending --
adapter gets exactly one request, no second step opens), (b) delegated
recovery blocks disposal until it settles (a downstream listener holds
a promise; disposal does not complete until it resolves), (c)
cancellation during delegated recovery (user cancel reaches idle only
after the downstream settles), and (d) a callback captured before
disposal, invoked after disposal, is rejected silently without entering
any downstream policy.

### 6.5 Retry history: keyed by provider and canonical policy hash

VERIFIED, `packages/llm/llm-retry/src/index.ts` and `packages/llm/
llm-retry/src/invariant.ts`. The retry counter does not accrue
globally -- it accrues per-provider-per-policy-key. `retryPolicyKey()`
derives a canonical key by serializing `[mode, maxRetries,
[...retryableCodes].sort(), initialDelayMs, maxDelayMs, jitterRatio]`
for normal mode and `[mode, initialDelayMs, maxDelayMs, jitterRatio]`
for always mode. The sorted codes ensure that set-membership-based
eligibility checks are order-independent. The session-projection state
(`llmRetry`) maps `JSON.stringify([provider, policyKey])` to `{retry,
retryId}`, so a route replacement that changes the policy (different
backoff constants, different eligible codes, or a different mode) starts
a fresh retry count and initial delay even though the provider name is
the same.

The `RetryId` is a branded UUID (`randomUUID()`) stable across all
attempts in one retry chain. The invariant checker verifies that
consecutive `llm/retry` events with the same provider and policy key
carry the same `retryId`, that `retry` increments monotonically from 1,
and that each `llm/retry-started` pairs one prior scheduled attempt by
`retryId` and retry number.

The test suite verifies this scoping end to end: a test where the
provider switches from `mock` to `other` after the first failure shows
two independent retry counters -- `{provider: 'mock', retry: 1}` and
`{provider: 'other', retry: 1}` -- and the adapter's `requests.map(r
=> r.provider)` confirms the sequence `['mock', 'other', 'other']`.

### 6.6 Error codes and non-retryable carve-outs

VERIFIED, `packages/llm/llm/src/error.ts` and `packages/llm/llm/src/
retry-policy.ts`. DSH uses a flat, provider-neutral `code` string on
every `LlmFailure` -- the error.ts doc comment states: "Stable
machine-routable failure class (e.g. `RATE_LIMIT`); route on this,
never by parsing `message`." The five default retryable codes listed in
§6.2 are the full set; any code not in a provider's `retryableCodes` is
non-retryable for that provider's normal mode.

Two specific codes are explicitly carved out and worth naming because
they parallel the same carve-outs every other harness on this page
applies:

- **`CONTEXT_WINDOW_EXCEEDED_CODE`** (`'CONTEXT_WINDOW_EXCEEDED'`): not
  in the default `retryableCodes`. DSH handles context overflow through
  a separate compaction subsystem (the `@deepseek-ai/dsh-compaction`
  seam), not through the request-retry path -- the same architectural
  separation Claude Code (§1.1), OpenCode (§3.2-3.3), pi (§4.5), and
  Hermes (§5.2) all enforce. The `error.ts` module exports dedicated
  classifier functions (`isContextWindowExceededError()` and
  `isQuotaExceededError()`) that test for the provider-specific wording
  patterns by which OpenAI-compatible providers deliver these errors,
  so adapters can reliably normalize them to the correct code.
- **`QUOTA_EXCEEDED_CODE`** (`'QUOTA'`): not in the default
  `retryableCodes`, and the twin classifier `isQuotaExceededError()`
  recognizes phrase patterns like `"insufficient_quota"`,
  `"quota_exceeded"`, `"balance_depleted"`, and `"out of budget"`.
  This is the same 429-with-quota-body distinction Claude Code (§1.1),
  OpenCode (§3.2), pi (§4.3), and Hermes (§5.2) all draw -- a 429 whose
  body names an exhausted account balance is terminal, not transient.
- **`INVALID_CREDENTIAL_CODE`** (`'INVALID_CREDENTIAL'`): the error.ts
  doc comment states this is "Deliberately outside the default retryable
  set -- a malformed credential fails identically on every attempt." The
  same non-retryable outcome every harness this page documents applies
  to authentication failures.

In always mode, none of these carve-outs apply -- `AUTH`, `QUOTA`,
`CONTEXT_WINDOW_EXCEEDED`, and every other code are retried
unconditionally. The README's Known Limitations section calls this out
explicitly: "Always mode retries permanent failures -- authentication,
quota, invalid-request, protocol, and unrecoverable context errors
continue until success, cancellation, or disposal; deployments own
provider-specific cost and latency controls."

### 6.7 What the model sees: nothing

VERIFIED, `packages/llm/llm-retry/README.md`, the error.ts `errorChain()`
function, and the test suite. The README's "Model Experience" section
states this in four parts:

1. **No retry event, delay, provider error, or failed partial output
   is model-visible.** The retried step reconstructs the same explicit
   provider/model request from durable surface history (the same
   `deriveMessages()` output the original attempt would have produced)
   unless a downstream recovery policy deliberately changes that
   surface.
2. **Each retry is a new provider request and may repeat input-token
   billing.** Normal mode has a finite budget; always mode can consume
   unbounded requests until success or cancellation.
3. **The reconstructed request preserves the prior prefix and is
   eligible for provider cache reuse** under that provider's own rules.
   The non-surface `llm/retry` event does not change cache identity.
4. **Failed chunks never enter derived messages.** The test suite
   exercises this directly: a `partialToolFailure` that emits text and
   a tool-call block before throwing a `TRANSPORT` error results in
   zero `tool/call` events, zero `assistant/message` events referencing
   the failed chunks' seq numbers, and the recovered response contains
   neither the provider diagnostic text nor the discarded partial
   output. The test asserts: `retriedContext = JSON.stringify(
   adapter.requests[1]?.messages)` does not contain the diagnostic
   string or the discarded partial text, while the `llm/retry` event
   itself does carry the failure message (in the durable log, for
   debugging and invariants, not in model context).

This is a stronger isolation guarantee than pi's or Hermes' own retry
mechanisms document: DSH's design explicitly rejects "put the error
into model context" as a considered and rejected alternative (the Agent
Note states: "rejected because a transport or provider diagnostic is
operational state, not conversation content. It can expose sensitive
provider details and changes the retried request instead of repeating
the failed request").

### 6.8 Wire-level verification: the transport-recovery integration test

VERIFIED, `packages/llm/llm-retry/tests/transport-recovery.spec.ts`.
These tests exercise the retry executor through the **real DeepSeek
HTTP/SSE adapter** and a `startMockLlmServer()`, not through a scripted
adapter -- the shortest end-to-end path from HTTP transport failure
through `LlmError` normalization, policy application, durable event
append, backoff, and recovery. Six cases worth naming:

- **Refused-connection recovery**: the server is not running when the
  first attempt fires; a `llm/retry` event with `failure.code:
  'TRANSPORT'` is appended; the test then starts the server during
  backoff, and the second attempt succeeds. This proves the
  `cancellableDelay` scheduling works for a genuinely refused TCP
  connection, not just a simulated error.
- **Stream-disconnect and partial-disconnect recovery**: the mock server
  drops the connection mid-stream; the adapter classifies this as
  `TRANSPORT`; the retried request sends the same body, and the
  `assistant/chunk` events from the failed attempt are excluded from
  the final `assistant/message`.
- **Empty-completion recovery**: the mock server returns a wire-valid
  completion with zero content; the adapter classifies this as
  `EMPTY_RESPONSE` (the same `EMPTY_RESPONSE_CODE` the unit test
  exercises); retry succeeds.
- **Clean partial EOF is non-default-retryable**: a mock `partial_eof`
  behavior produces an SSE stream that ends cleanly without `[DONE]`;
  the adapter classifies this as `STREAM_CLOSED`, which is **not** in
  the default `retryableCodes`. The test confirms no `llm/retry` event
  appears and the turn ends with an error -- verifying that the
  default code list is genuinely bounded, not universal.
- **Stall-to-timeout recovery**: a mock stalled body triggers the
  adapter's idle-watchdog timeout, classified as `TIMEOUT`; retry
  succeeds on the next request.
- **Budget exhaustion**: three consecutive `connection_reset` behaviors
  exhaust a `maxRetries: 2` budget; the test confirms exactly two
  `llm/retry` events, exactly three adapter requests, and a terminal
  `turn/end` with `error.code: 'TRANSPORT'`.

---

## 7. Synthesis

| Dimension | Claude Code | Copilot CLI | OpenCode | pi | Hermes Agent | DeepSeek Harness |
|---|---|---|---|---|---|---|
| Verifiability | Docs + changelog; no public implementation | Changelog only; docs page found is generic platform guidance, not CLI-specific | Source-verified (`packages/llm`, `packages/opencode`), `dev` branch (caveat applies) | Source-verified across all three sibling packages (`pi-ai`, `pi-coding-agent`, `pi-agent-core`), `main` branch, plus its own settings docs and a regression-test file | Source-verified (`agent/retry_utils.py`, `agent/error_classifier.py`, `agent/conversation_loop.py`, `agent/turn_retry_state.py`, `agent/nous_rate_guard.py`, `run_agent.py`), `main` branch, plus its own docs and five issue-numbered regression tests | Source-verified end to end (`packages/llm/llm/src/retry-policy.ts`, `packages/llm/llm-retry/src/index.ts`, `types.ts`, `invariant.ts`, `history.ts`, `error.ts`, `README.md`, architectural decision record, two independent test suites including wire-level integration against the real DeepSeek HTTP/SSE adapter), `master` branch |
| Architecture | One documented, named policy ("Automatic Retries") | Not documented as one named mechanism; changelog implies per-subsystem fixes (MCP, streaming, HTTP/2) rather than one shared module (BEST CURRENT UNDERSTANDING, UNCONFIRMED) | Two explicit, source-verified layers: bounded transport retry (`RequestExecutor`) wrapped by a separately-classified, effectively unbounded session-turn retry (`SessionRetry`) | Two explicit, source-verified layers with deliberately different classifiers (status-code-based inner `retryProviderRequest`, string-pattern-based outer `retryAssistantCall`), plus a third, durable crash-recovery state machine in `pi-agent-core` tracking retry state across process restarts | One loop (`while retry_count < max_retries` in `conversation_loop.py`) wrapping a nine-`FailoverReason` taxonomy with four independent per-branch recovery flags (`retryable`/`should_compress`/`should_rotate_credential`/`should_fallback`), plus one-shot `TurnRetryState` guards for credential rotation, per-provider OAuth refresh, and format recovery, and a resettable budget that restarts at each new target (recovered primary, then each fallback) | One plugin (`@deepseek-ai/dsh-llm-retry`) executing per-provider-route policies on the `agent/request-error` waterfall; two modes (`normal` bounded/code-gated, `always` unbounded/downstream-first); policy owned by provider adapter config, executor owns no config; durable `llm/retry` events appended before wait; invariant companion validates events at load and append time |
| Default attempt cap | 10 (`CLAUDE_CODE_MAX_RETRIES`), capped at 15 unless `CLAUDE_CODE_RETRY_WATCHDOG` is set (then ~300 or unlimited for capacity errors) | Not documented | Inner layer: 2 retries (3 attempts). Outer layer: **no cap** in the `Schedule` itself | Outer layer: 3 (`retry.maxRetries`, configurable). Inner layer: 0 -- **off by default** (`retry.provider.maxRetries`), and `pi-agent-core`'s own framework-level default is also `{enabled: false}` | 3 (`agent.api_max_retries`, configurable) -- **four attempts total** before fallback-provider switching engages; extended dynamically (to a computed ceiling) only for one narrow Z.AI Coding Plan overload signature | Normal mode: 5 (`maxRetries`, configurable per-provider). Always mode: **no cap** -- retries every failure until success, cancellation, or plugin disposal |
| Backoff formula | Exponential, with the client-computed value enforced as a *minimum* even against a small server `Retry-After` (v2.1.98 fix) | Not documented for the CLI's own requests (cookbook page shows only example client code) | Inner: exponential with ±20% jitter, capped at 10s. Outer: `retry-after(-ms)` header if present (capped only by ~24.8-day 32-bit ceiling), else 2s×2^(attempt-1) capped at 30s if no headers at all | Outer: `baseDelayMs * 2^(attempt-1)` (default 2s, 4s, 8s), **no jitter**. Inner: `retry-after(-ms)` header if present (capped at `maxRetryDelayMs`, default 60s, or throws if exceeded rather than waiting), else `min(0.5*2^i, 8s)` with **negative-only** (-0 to -25%) jitter | `jittered_backoff()`: `min(base_delay * 2^(attempt-1), max_delay) + uniform(0, jitter_ratio*delay)` -- **positive-only** jitter (0-50% at the default 0.5 ratio), decorrelated across concurrent callers via a locked counter XORed into the RNG seed; `Retry-After` honored and capped at 600s; a separate provider-specific carve-out (Z.AI GLM-5.2 overload) escalates to a fixed 30/60/90/120s long-wait table after 3 short retries | `localDelay()`: `min(initialDelayMs * 2^(min(retry-1, 1024)), maxDelayMs) * [1 - jitterRatio + 2 * jitterRatio * random()]`, capped at `maxDelayMs` -- **symmetric** jitter (default ±10%); defaults 500ms initial, 10s max. `providerRetryAfterMs` used exact and unjittered when under `maxDelayMs`; over-cap causes **normal mode to delegate** and **always mode to fall back to local backoff** |
| Non-retryable carve-outs | TLS cert validation, Bedrock content-type mismatch, mid-response partial failures (kept, not retried) | Not documented at this granularity | Auth (401/403), quota-exceeded, content-policy, invalid-request/context-overflow, transport errors -- all `retryable: false` at the inner layer; context-overflow additionally hard-excluded at the outer layer | Quota/billing/Go-usage-limit text (checked first, wins ties) at the outer layer; aborts are terminal at both layers; overflow is checked before retryable-error classification and routed to compaction instead, confirmed independently from both `custom-provider.md` and `pi-agent-core`'s own state-machine doc | 401/402/403-billing/404-billing/content-policy-blocked/most-other-4xx are `retryable=False`; 413/429(non-billing)/408/500-502/503-529/context-overflow-as-5xx are `retryable=True`; a request-validation-signal carve-out on 500/502 fails fast instead of retrying a deterministic rejection | Normal mode: only configured `retryableCodes` are retried (default: `EMPTY_RESPONSE`, `RATE_LIMIT`, `SERVER`, `TIMEOUT`, `TRANSPORT`); everything else delegates (including `AUTH`, `QUOTA`, `CONTEXT_WINDOW_EXCEEDED`, `INVALID_CREDENTIAL`, `STREAM_CLOSED`). Always mode: **no carve-outs** -- every code is retried until success, cancellation, or disposal. Over-cap `Retry-After` causes delegation in normal mode, local backoff fallback in always mode |
| User-visible retry UX | Spinner countdown `Retrying in Ns · attempt x/y`; reason label revealed at attempt 3 (v2.1.198); stall banner at 20s (90s during advisor calls) | Not documented in mechanism-level detail; changelog confirms "user-friendly" rate-limit timing messages exist (0.0.389) | Session-status object (`{type:"retry", attempt, message, action, next}`) rendered by the TUI's/app's own `SessionRetry` component | `onRetryScheduled`/`onRetryAttemptStart`/`onRetryFinished` callbacks drive UI countdown; the identical mechanism is reused for compaction under a `summarization_retry_*` event name instead | Buffered/emitted status lines (`⏳ Retrying in Ns (attempt x/y)...`, a distinct `⏱️ Provider overloaded` / `Rate limited` label plus an adaptive-policy note) with 200ms-granularity interrupt checks during the sleep and a periodic activity touch every ~30s so the gateway's inactivity monitor doesn't misreport a live backoff wait as a stall | Non-surface `llm/retry` and `llm/retry-started` events in the session log drive TUI rendering; normal events carry finite `maxRetries`, always events omit it (UIs render the limit as `∞`). No retry event, delay, provider error, or failed partial output is model-visible |
| Alternative-to-retry mitigation | `fallbackModel`: up to 3 ordered fallback models, retried once on an unexpected non-retryable error (auth/rate-limit/request-size/transport excluded) | `continueOnAutoMode`: auto-switches to auto model-selection on rate limit instead of pausing | Free-tier/Go-usage-limit responses surface a subscribe/upgrade action link rather than only backing off | None found; quota/billing text is classified non-retryable and fails fast instead | `fallback_providers`: an ordered chain, turn-scoped (resets to primary every new message) and reset-aware (skips a doomed retry and stays on the fallback when a known subscription reset time hasn't elapsed yet); documented cost is a forced prompt-cache invalidation on every switch in and back out | Always mode's downstream-first posture lets later policies (e.g. compaction, model-switch) act before retry applies; no dedicated fallback-provider chain in the `llm-retry` plugin itself (composability via the waterfall replaces a built-in chain) |
| User-facing config lever | `CLAUDE_CODE_MAX_RETRIES`, `CLAUDE_CODE_RETRY_WATCHDOG`, `API_TIMEOUT_MS` | None found | None found on the docs config page; two open feature requests ask for exactly this (§3.4) | `retry.enabled`, `retry.maxRetries`, `retry.baseDelayMs`, `retry.provider.timeoutMs`, `retry.provider.maxRetries`, `retry.provider.maxRetryDelayMs` -- the most granular documented lever of the four harnesses examined | `agent.api_max_retries` (single lever for the whole primary-call budget); `fallback_providers` / `hermes fallback` for the chain itself; no separate backoff-shape config found | Per-provider `retryPolicy` in adapter config: `mode`, `maxRetries`, `retryableCodes`, and `backoff.{initialDelayMs, maxDelayMs, jitterRatio}`. Executor plugin has **no config** -- `validateConfig()` rejects misdirected keys. Minimal example in README shows a two-provider YAML with different modes |
| Known failure mode, self-reported | Historical: v2.1.110's retry cap had to be reverted one version later for trading hangs for outright failures; voice-mode retry loop was unbounded until fixed (v2.1.204) | A remote-session heartbeat loop retried a rejected request "every few seconds forever" until fixed in 1.0.66 | Live, open issue (#17648, fetched this session): 173 consecutive retries over 2.5 hours, backoff growing past 7 minutes with no circuit breaker, corroborated by several further open issues/feature requests found (not independently fetched) | Historical: compaction's summarization call previously ran an unretried single call at all (`#6647`, fixed by wiring it into the shared `retry.*` policy); no equivalent open unbounded-retry issue found this session | Historical, all fixed with a named regression test: `#31273` (a 402 billing wall was wrongly retried, "~$40 burned in 48h"); `#18028` (a status-code-less content-policy refusal burned all retries as `unknown`); `#14038` (a Z.AI server-overload 429 wrongly rotated a healthy credential); `#32646` (a fallback-index race silently disabled the fallback chain post-recovery); plus a documented, still-relevant amplification on the Nous Portal path specifically (SDK retries not disabled there): up to 9 calls per turn (3 SDK x 3 Hermes) against one rate limit, mitigated by a cross-session on-disk guard rather than a code fix to the multiplication itself | Always mode is explicitly documented as retrying permanent failures (auth, quota, context overflow) until success, cancellation, or disposal -- a known limitation, not a bug, with the README stating "deployments own provider-specific cost and latency controls." A non-default-retryable code (`STREAM_CLOSED` for clean partial EOF) correctly surfaces as a terminal error, verified by integration test. No historical misclassification bugs found in the fetched sources; the invariant companion catches classification errors at load and append time |

**The design lesson.** All six harnesses draw the same basic
distinction -- a status-code/error-type taxonomy that separates
"try again, this is transient" from "stop, this needs a human or a
different request" -- and all six exclude authentication failures,
malformed requests, and (where the concept applies) context-overflow from
retry outright. Where they diverge sharply is in how tightly the *retry
budget itself* is bounded once a failure is classified as transient.
Claude Code documents one named policy with an explicit, if
watchdog-adjustable, ceiling, and treats its own historical
over-tightening (the reverted v2.1.110 cap) and under-bounding (the fixed
voice-mode and compaction loops) as bugs to fix in either direction.
Copilot CLI's changelog reads as a series of independent, per-subsystem
retry hardenings rather than evidence of one shared, named policy, with
at least one instance (the 1.0.66 heartbeat loop) of a genuinely unbounded
retry shipping and later being fixed. OpenCode is the one harness of the
six whose *current*, still-open state is a documented-by-its-own-users
unbounded retry: its inner transport layer is tightly bounded (2 retries,
10-second cap, jittered), but that bound is not the retry budget a user
actually experiences, because the outer, whole-turn-wrapping
`SessionRetry` layer above it has no attempts cap at all and, for the
common case of a provider that returns rate-limit or overload headers on
every attempt, is bounded only by a 32-bit integer overflow point roughly
24.8 days away -- a gap this page's own source-reading and its
cross-referenced, live-fetched GitHub Issue agree on independently. pi is
the one harness of the six that inverts the usual bounding direction: its
inner, SDK-mirroring layer is the one left effectively unbounded-by-default
in the sense of being *off* (`maxRetries: 0`), specifically because its own
docs identify a correctness risk in turning it on (an SDK-level retry could
silently re-wait-out an error the outer, string-pattern classifier would
have failed fast on as a quota/billing exhaustion); the outer, turn-level
layer carries the real, small, user-configurable budget (3 attempts by
default), and a third, independent concern -- surviving a process crash
mid-backoff -- is handled by a wholly separate, source-verified durable
state machine in `pi-agent-core` that snapshots the retry policy inline into
crash-recoverable operation state, a property this page found no equivalent
of, confirmed or claimed, in any of the other five harnesses examined
before it. Hermes Agent is the harness on this page with the richest,
most explicitly multi-dimensional error taxonomy (a `FailoverReason` enum
with four independent recovery-hint booleans on every classification) and
the tightest default primary-call budget of any of the six (three
retries, four attempts, before fallback engages) -- but it is also the one
harness whose own self-reported bug history is consistently about
*misclassification* rather than an absent or unbounded budget: `#31273`
and `#18028` are both cases where a genuinely terminal error was routed
into a retryable bucket and burned real money or real time before being
fixed, and `#14038` is the mirror case, a genuinely transient error
initially routed into the wrong *recovery action* (credential rotation
instead of same-key backoff) rather than the wrong retry/no-retry
verdict. Hermes is also the only harness of the six this page finds
disabling an underlying SDK's own retry loop *inconsistently rather than
uniformly* -- `max_retries=0` on the OpenAI-wire request path for the
same double-counting reason pi's own docs state explicitly (§4.4;
§5.4 above), but left enabled on the Nous Portal path, where the
resulting compounding (3 SDK retries x 3 Hermes retries per rate-limited
turn) is significant enough that Hermes ships a dedicated, persisted,
cross-session file (`agent/nous_rate_guard.py`) purely to blunt it rather
than closing the gap at its source -- a real, if narrow, architectural
inconsistency this page's reading of the other five harnesses' retry
mechanisms did not surface an equivalent of.

DeepSeek Harness is the newest and architecturally most articulated of
the six: its separation of policy ownership (each provider adapter
configuration) from execution ownership (a single zero-config plugin on the
`agent/request-error` waterfall) is the cleanest policy/executor split on
this page, and its `normal`/`always` mode choice makes the
bounded-versus-unbounded decision a per-route deployment concern rather
than a per-harness or per-layer global. The default 5-retry normal policy
(with `EMPTY_RESPONSE` as a retryable code, a category no other harness on
this page includes by default) sits between Claude Code's 10 and Hermes'/pi's
3. The always mode's downstream-first posture is a genuinely different
compositional strategy from any other harness: it gives later waterfall
listeners (compaction, model-switch, specialized recovery) a chance to act
before retry applies, rather than having retry short-circuit them. The
durable-before-wait discipline (appending the `llm/retry` event before
starting the timer, plus an invariant companion that validates the entire
retry sequence at load time and on append) provides a log-level
accountability guarantee none of the other five harnesses document an
equivalent of at this level of precision (pi's durable crash-recovery
state machine in `pi-agent-core` is the closest analog, but it serves a
different concern: surviving process crashes mid-retry, not validating
invariant correctness of the retry log itself). The one design trade-off
that carries operational weight is the same one OpenCode's still-open
unbounded-retry issues surface: always mode has no attempt cap on
permanent failures, and the README explicitly documents this as the
deployer's responsibility, not the executor's. Whether the "composability
via waterfall replaces a built-in fallback chain" design proves more or
less robust in practice than Hermes' dedicated `fallback_providers` chain
or Claude Code's `fallbackModel` is a question this page's source-level
analysis cannot yet answer -- it would require production-incident data
from real DSH deployments, none of which exist at developer-preview time.

---

## Sources

All fetched fresh 2026-07-31 unless noted otherwise.

**Claude Code (authoritative for its own documented behavior only):**
- `https://code.claude.com/docs/en/errors` -- the primary source for §1:
  the "Automatic Retries in Claude Code" section's retried/not-retried
  category list, the environment-variable table, the retry-UX countdown
  and label-reveal-timing behavior, and the mid-response
  partial-output-preservation behavior.
- `https://github.com/anthropics/claude-code` `CHANGELOG.md`, fetched
  fresh this session via `gh api repos/anthropics/claude-code/contents/
  CHANGELOG.md` (full 5,248-line file) -- every dated/versioned entry
  cited in §1.2-1.7 (v2.1.76 compaction circuit breaker, v2.1.89
  `PermissionDenied` hook `{retry:true}` and `/permissions` retry-with-`r`,
  v2.1.98 429-`Retry-After`-as-minimum fix, v2.1.101 retry-indicator UX
  fixes, v2.1.110/2.1.111 non-streaming-fallback-retry-cap
  revert, v2.1.126 MCP startup auto-retry, v2.1.140 managed-settings
  401-retry, v2.1.147 auto-updater retry hardening (see
  [packaging-distribution-and-self-update.md](packaging-distribution-and-self-update.md)
  for the full auto-update mechanism), v2.1.166
  `fallbackModel` and retry-once-on-fallback, v2.1.185 stream-stall hint
  timing, v2.1.186 `CLAUDE_CODE_MAX_RETRIES` cap at 15, v2.1.191 MCP
  capability-discovery and OAuth retry, v2.1.198 dropped-connection retry
  and error-reason-reveal timing, v2.1.199
  `CLAUDE_CODE_RETRY_WATCHDOG`/subscription-429-retry, v2.1.204 voice
  dictation unbounded-retry-loop fix, v2.1.208 Bedrock
  content-type-mismatch no-retry, v2.1.214 advisor stall-threshold
  widening). Authoritative for its own behavior-change history only; this
  repo ships no implementation source.

**GitHub Copilot CLI (authoritative for its own behavior-change history
only; no implementation source exists in this repo):**
- `https://docs.github.com/en/enterprise-cloud@latest/copilot/tutorials/
  copilot-chat-cookbook/debugging-errors/handling-api-rate-limits` --
  checked this session and confirmed to be generic platform-level client
  guidance, not a CLI-specific retry-mechanism specification (§2.1).
- `https://github.com/github/copilot-cli` `changelog.md`, fetched fresh
  this session via `gh api repos/github/copilot-cli/contents/
  changelog.md` (full 2,898-line file, grepped for retry/rate-limit
  terms) -- every dated entry cited in §2.2 (0.0.389 rate-limit-timing
  messages, 0.0.407 streaming auto-retry, 1.0.13/1.0.14 MCP registry
  retries, 1.0.25 MCP remote-server auto-retry, 1.0.32 rate-limited
  session pause-and-retry, 1.0.34/1.0.35 `continueOnAutoMode`, 1.0.52
  HTTP/2-stall-retries-over-HTTP/1.1 and 1.0.57's related default-to-
  HTTP/1.1 change, 1.0.55/1.0.57 update/version rate-limit handling and
  `vote_memory` throttling, 1.0.66 the fixed heartbeat retry-forever bug).

**OpenCode (authoritative for its own documented behavior AND, unlike the
two harnesses above, its own real implementation; `dev` branch, not a
stable release tag):**
- `https://github.com/anomalyco/opencode`, `dev` branch, fetched via
  `gh search code` (to locate call sites: `exponential`, `backoff`,
  `retry`, `retryable`, `SessionRetry`) and `gh api` (full file contents)
  this session -- full contents of `packages/opencode/src/session/
  retry.ts`, `packages/core/src/util/retry.ts`,
  `packages/llm/src/route/executor.ts`, `packages/llm/src/schema/
  errors.ts`, and the `SessionRetry.policy(...)` call site in
  `packages/opencode/src/session/processor.ts` (lines 627-693) --
  covering §3.1-3.5 in full.
- `https://opencode.ai/docs/config/`, fetched fresh this session --
  confirmed, as a checked negative result, that the page documents no
  retry/backoff/max-retries configuration key (§3.6).
- `gh issue view 17648 --repo anomalyco/opencode`, fetched fresh this
  session -- the live, user-reported corroboration of the unbounded
  session-level retry behavior cited in §3.4, including its own quoted
  (and since partially superseded) excerpt of `delay()`.

**pi (authoritative for its own documented behavior AND its own real
implementation across all three sibling packages; fetched 1 September 2026
from `github.com/earendil-works/pi`, `main` branch):**
- `packages/ai/package.json` and `packages/coding-agent/package.json` (via
  `gh api repos/earendil-works/pi/contents/...`) -- settled this book's own
  spelling inconsistency: `@earendil-works/pi-ai` and
  `@earendil-works/pi-coding-agent` are two different sibling packages in one
  monorepo, not two names for one package (§4 intro).
- `packages/ai/src/utils/provider-retry.ts` (via `gh api`, full 125-line file)
  -- the inner, request-level `retryProviderRequest()` mechanism covered in
  §4.2: its status-code/`x-should-retry`-header retryability rule, its
  header-honoring/negative-jitter/`maxRetryDelayMs`-capped backoff formula,
  its default-off `maxRetries`, and its own "mirrors the pinned OpenAI/
  Anthropic SDK retry policy" and "X-Stainless-Retry-Count remains zero"
  source comments.
- `packages/ai/src/utils/retry.ts` (via `gh api`, full 229-line file) and
  `packages/ai/test/retry.test.ts` (via `gh api`, full 223-line file) -- the
  outer, turn-level `retryAssistantCall()`/`isRetryableAssistantError()`
  mechanism covered in §4.3: its two named regex classifiers (including the
  deliberate `"retry delay"` cross-layer coupling to §4.2, sourced to pi's
  own `#1123`/`#2264`/`#3594`/`#4433`/`#6019` issue-number comments), its
  no-jitter exponential backoff, and its abort-during-backoff normalization.
- `packages/coding-agent/docs/settings.md`, "Retry" section (via `gh api`,
  fetched in full) -- the `retry.*`/`retry.provider.*` settings table and the
  docs' own stated reason to keep `retry.provider.maxRetries` at `0`, both
  covered in §4.4.
- `packages/coding-agent/test/suite/regressions/
  6647-compaction-retries-transient-stream-drop.test.ts` (via `gh api`, full
  file) -- the regression test and its own doc comment covered in §4.5,
  confirming compaction's summarization call now reuses `settings.retry` and
  emits `summarization_retry_*` events rather than running one unretried call
  as it previously did.
- `packages/agent/package.json`, `packages/agent/docs/harness.md`, and
  `packages/agent/src/harness/agent-harness.ts` (via `gh api`, all fetched in
  full) -- the `@earendil-works/pi-agent-core` package's own formal
  state-machine specification and source, covered in §4.6: the durable,
  crash-recoverable `retry_wait`/`notBefore` operation state, the
  captured-at-start retry-policy semantics, the framework-level
  `{enabled: false}` default distinct from the coding-agent CLI's own
  enabled-by-default settings, and the `Number.MAX_SAFE_INTEGER` backoff-math
  saturation guard.

**Hermes Agent (authoritative for its own documented behavior AND its own
real implementation; fetched 1 September 2026 from
`hermes-agent.nousresearch.com/docs/` and `github.com/NousResearch/
hermes-agent`, `main` branch):**
- `https://hermes-agent.nousresearch.com/docs/user-guide/configuration`
  (WebFetch) and the site's own concatenated `llms-full-*.txt` documentation
  dump (fetched via `curl`, grepped for `retry`/`backoff`/`429`/
  `api_max_retries`) -- the primary source for §5.1's `agent.api_max_retries`
  config key, its default of `3` (four attempts total), and its documented
  purpose ("before fallback-provider switching engages").
- `https://hermes-agent.nousresearch.com/docs/user-guide/features/
  fallback-providers` (WebFetch) -- the primary source for §5.6: the
  `fallback_providers`/legacy `fallback_model` config surface, the
  turn-scoped/reset-aware per-turn retry-vs-fallback decision, the
  documented rate-limit/server-error/auth-failure/not-found trigger
  conditions, and the stated prompt-cache-invalidation cost of switching.
- `agent/retry_utils.py` (via `raw.githubusercontent.com`, full 209-line
  file) -- §5.3's `jittered_backoff()` formula (exponential with
  positive-only jitter, locked-counter/XOR seed decorrelation),
  `parse_retry_after_seconds()`, and the Z.AI Coding Plan GLM-5.2
  `adaptive_rate_limit_backoff()`/`zai_coding_overload_retry_ceiling()`
  provider-specific long-tail carve-out and its own documented dead-code
  bug (`api_max_retries` originally equal to `short_attempts`).
- `agent/error_classifier.py` (via `raw.githubusercontent.com`, full
  99,558-byte file) -- §5.2's `FailoverReason` taxonomy, `ClassifiedError`
  dataclass, and the `_classify_by_status()`/`_classify_400()` dispatch
  logic and its issue-numbered carve-out comments (`#14038` overload-vs-
  rate-limit, `#39441` billing-vs-rate-limit-text, `#26293` server-injected-
  param exception, RFC 9110 §15.5.9 for 408).
- `agent/conversation_loop.py` (via `raw.githubusercontent.com`, full
  502,391-byte file, grepped for the retry-loop symbols) -- §5.1 and §5.3-5.5's
  `while retry_count < max_retries` loop itself, the two distinct
  `jittered_backoff()` call sites (main API-error path vs. the invalid-
  response sub-loop), the `Retry-After`-header-capped-at-600s logic and its
  `#26293` rationale, the Nous-Portal cross-session rate-limit guard
  integration, the credential-pool/auth-refresh/primary-transport-recovery/
  fallback-activation sequence, and the interrupt-aware incremental sleep.
- `agent/turn_retry_state.py` (via `raw.githubusercontent.com`, full
  94-line file) -- §5.5's `TurnRetryState` dataclass, its own docstring
  describing the ~16-bare-local refactor it replaced, and the
  `restart_with_*`/one-shot-guard design it documents.
- `agent/nous_rate_guard.py` (via `raw.githubusercontent.com`, full
  11,108-byte file) -- §5.4's cross-session, persisted Nous Portal
  rate-limit guard and its own "3 SDK retries x 3 Hermes retries" (up to
  9 calls per turn) amplification-effect documentation.
- `run_agent.py` (via `raw.githubusercontent.com`, full 464,854-byte file,
  grepped for the retry/client-construction symbols) -- §5.4's
  `request_kwargs["max_retries"] = 0` OpenAI-wire-client override and its
  own source comment on SDK/outer-loop retry compounding.
- `tests/run_agent/test_api_max_retries_config.py`, `tests/run_agent/
  test_31273_402_not_retried.py`, `tests/run_agent/
  test_18028_content_policy_blocked.py`, `tests/run_agent/
  test_32646_fallback_429_after_timeout.py`, and `tests/test_retry_utils.py`
  (all via `raw.githubusercontent.com`, fetched in full) -- the five
  issue-numbered regression tests (`#11616`, `#31273`, `#18028`, `#32646`)
  cited in §5.1-5.2 and §5.7's self-reported-failure-mode summary, and the
  `jittered_backoff()`/Z.AI-overload-ceiling unit tests corroborating §5.3's
  formula and dead-code-bug narrative.

**DeepSeek Harness (authoritative for its own documented behavior AND its
own real implementation; fetched 1 September 2026 from
`github.com/deepseek-ai/deepseek-harness`, `master` branch):**
- `packages/llm/llm/src/retry-policy.ts` (via `gh api`, full 193-line file)
  -- §6.2's two-mode policy schema (`NormalRetryPolicyConfig`/
  `AlwaysRetryPolicyConfig`), the `resolveRetryPolicy()` resolver, all
  default constants (`DEFAULT_MAX_RETRIES = 5`, `DEFAULT_INITIAL_DELAY_MS =
  500`, `DEFAULT_MAX_DELAY_MS = 10_000`, `DEFAULT_JITTER_RATIO = 0.1`,
  `DEFAULT_RETRYABLE_CODES`), validation rules, and the
  `RetryPolicySchema` embedded in adapter configuration.
- `packages/llm/llm/src/error.ts` (via `gh api`, full file) -- §6.6's
  `HarnessError` base class, `LlmError` subclass, `LlmFailure` type,
  canonical codes (`CONTEXT_WINDOW_EXCEEDED_CODE`, `QUOTA_EXCEEDED_CODE`,
  `EMPTY_RESPONSE_CODE`, `INVALID_CREDENTIAL_CODE`), the
  `isContextWindowExceededError()` and `isQuotaExceededError()` classifier
  functions, and the `errorChain()` renderer.
- `packages/llm/llm-retry/src/index.ts` (via `gh api`, full 279-line file)
  -- §6.1 and §6.3-6.4's retry executor plugin: `apply()`, `recover()`,
  `localDelay()`, `retryPolicyKey()`, `backoff()`, `cancellableDelay()`,
  `settleDownstream()`, the `validateConfig()` guard rejecting misdirected
  keys, the session-projection state (`llmRetry`), the disposal/drain
  cleanup, and the `RetryInternals` test-injection interface.
- `packages/llm/llm-retry/src/types.ts` (via `gh api`, full file) --
  §6.1's `LlmRetryEventData` discriminated union (normal vs. always
  mode payloads) and `LlmRetryStartedEventData`, declared as session
  event types.
- `packages/llm/llm-retry/src/invariant.ts` (via `gh api`, full file) --
  §6.1 and §6.5's invariant companion: `validateRetry()`, `validateStarted()`,
  `validateSession()`, provider-identity binding against `request/header`,
  retry-number monotonicity, `retryId` stability, and timer-delay bounds.
- `packages/llm/llm-retry/src/history.ts` (via `gh api`, full file) --
  §6.1's `providerForOpenStep()` durable request-route lookup.
- `packages/llm/llm-retry/src/brand.ts` (via `gh api`, full file) -- the
  `RetryId` branded type and constructor.
- `packages/llm/llm-retry/README.md` (via `gh api`, full file) --
  §6.1-6.7's user/maintainer reference: the Summary, Use this package,
  Understand the implementation, Model Experience, and Known Limitations
  and Deferred Work sections, including the "retryPolicy belongs under
  each provider configuration" guard, the normal/always mode descriptions,
  the `EMPTY_RESPONSE` retry rationale, and the always-mode permanent-
  failure limitation.
- `.agents/notes/implemented/feature/2026-07-24-provider-retry-policies.md`
  (via `gh api`, full file) -- §6.1-6.7's architectural decision record:
  the per-provider-route policy decision, the "durable before wait, open-
  step boundaries" design rule, the normal/always mode semantics, the
  `Retry-After` over-cap behavior, the considered-and-rejected alternatives
  (one executor-level switch, separate provider list, very large finite
  count, adapter-specific omission defaults, LLM deployment-level default,
  UI-written profiles, provider-SDK retries, put the error into model
  context), and the verification summary.
- `.agents/notes/implemented/simplification/2026-07-27-request-error-
  retry-action.md` (via `gh api`, full file) -- §6.4's `RequestErrorAction`
  waterfall control flow: the `{kind: 'retry'}` action, `next()` delegation,
  and the removal of `Agent.retry()`.
- `packages/util/timeout/src/index.ts` (via `gh api`, full file) --
  `MAX_TIMER_DELAY_MS = 2_147_483_647` and the `deadline()`/`idleWatchdog()`
  timeout utilities used by the adapter layer.
- `packages/llm/llm-retry/tests/retry.spec.ts` (via `gh api`, full
  630+ line file) -- §6.2-6.7's comprehensive unit test suite: 20+ cases
  covering normal-mode bounded retry with jitter pinning, `EMPTY_RESPONSE`
  default-code retry, partial-failure chunk isolation, exhausted-budget
  terminal failure, zero-delay jitter bound, `Retry-After` accepted and
  rejected, always-mode unbounded retry, always-mode over-cap `Retry-After`
  fallback to local backoff, non-retryable delegation, provider-select
  policy, serving-registration capture, changed-policy history reset,
  finite budget per-provider scope, downstream-first composition,
  disposal drain and abort, cancellation drain, captured-callback rejection,
  and misdirected-config rejection.
- `packages/llm/llm-retry/tests/transport-recovery.spec.ts` (via `gh api`,
  full file) -- §6.8's wire-level integration tests through the real
  DeepSeek HTTP/SSE adapter: refused-connection recovery, stream-disconnect
  and partial-disconnect recovery, empty-completion recovery, clean partial
  EOF as non-default-retryable `STREAM_CLOSED`, stall-to-timeout recovery,
  and budget exhaustion.
