# Evals and testing a harness -- validating that a from-scratch harness actually works

**Scope note.** Every other page in this book describes a mechanism a
harness *has*; this page describes how a builder would know that
mechanism actually *works*, and keeps working after the next change. It
deliberately separates two questions that get conflated constantly in
public discussion of "agent evals": whether the **model** is capable
(can it plan, use tools sensibly, solve the task) versus whether the
**harness** is correct (does it reassemble a streamed tool call byte-for-
byte, does a permission rule actually block what it claims to block,
does a compacted transcript still round-trip). A capability benchmark
run against Claude Opus inside Claude Code and the same model inside a
different harness can produce different scores for reasons that have
nothing to do with the model -- Anthropic's own engineering writing
says this plainly (§2.2 below) -- which is precisely why a harness
needs its own, harness-scoped test suite distinct from any end-to-end
capability benchmark. This page does not re-derive the wire-level
contract a tool-call-parsing test is actually checking --
[llm-api-contract.md](llm-api-contract.md) §1.5/§2.3 already grounds
the `input_json_delta`/`function_call_arguments.delta` accumulate-then-
parse discipline, and
[streaming-and-incremental-rendering.md](streaming-and-incremental-rendering.md)
§3.1-§3.2 already shows, from OpenCode's own source, exactly which
layer of a harness holds a still-partial argument string in memory and
when it gets parsed. This page picks up one level higher: what
automated, repeatable check would actually catch a regression in that
mechanism before a user does.

Every claim below is tagged VERIFIED (fetched or read from source this
session, source named) or BEST CURRENT UNDERSTANDING, UNCONFIRMED.
Claude Code and Copilot CLI are both closed source, so -- as with every
other topic this book has covered for them -- their own `CHANGELOG.md`s
are read as a *history of shipped behavior*, not a specification, and
neither repository ships an internal test suite to inspect. OpenCode is
different on this exact topic in a way no other page in this book has
been able to say yet: its repository does not just implement the
mechanism, it ships the actual regression-test source code that
protects it, down to the literal expected-event-array assertions on a
tool-call reassembly function. pi (§5 below) is a second open-source
harness in this same position -- its own monorepo ships hundreds of
`*.test.ts` files and a dedicated model-backed eval package -- but
arrives at that CI-safe visibility through a materially different
architecture from OpenCode's record/replay cassettes: a synthetic,
in-process "faux" model provider rather than recorded real-provider
traffic. That asymmetry between the two closed-source harnesses and
the two open-source ones shapes this page's structure -- OpenCode's
and pi's sections are the only two grounded in real test code rather
than inferred from documentation or a changelog.

```mermaid
flowchart TD
    L1["Layer 1: unit-level wire-format correctness\n(does a fragmented tool_use/function_call\nreassemble to the exact right parsed object?\nis finish_reason/stop_reason mapped correctly?)"]
    L2["Layer 2: session/integration correctness\n(does the whole turn loop reconstruct correctly\nfrom a recorded real transcript? do permission\nrules, compaction, event schemas survive?)"]
    L3["Layer 3: API/route-surface coverage\n(does every documented endpoint/command\nactually decode requests and return the\nshape its own contract promises?)"]
    L4["Layer 4: end-to-end capability evals\n(does the agent solve the task at all --\nGAIA, SWE-bench-style, tau-bench-style benchmarks;\nmeasures model + harness together, not harness alone)"]
    L1 --> L2 --> L3 --> L4
    Note1["Deterministic, harness-only,\nno live model call needed"] -.-> L1
    Note1 -.-> L2
    Note2["Requires a live or recorded model call;\nmeasures the model AND the harness's\nscaffolding around it together"] -.-> L4
```

---

## 1. General concepts: what "testing a harness" decomposes into

VERIFIED, `huggingface.co/learn/agents-course/bonus-unit2/monitoring-and-evaluating-agents-notebook`,
fetched fresh this session -- authoritative for general, framework-neutral
agent-evaluation vocabulary and pedagogy, not for any specific harness's
own practice (per this book's standing authority-overreach guard on
this source). The course draws a foundational split between **online
evaluation** ("live feedback" -- monitoring an agent in production,
tracking cost, latency, and real user responses as they happen) and
**offline evaluation** ("systematic checks before or during
development" -- controlled, pre-deployment quality checks run against a
fixed dataset rather than live traffic). It also names a **trace** as
the complete recorded sequence of an agent's steps, with sub-spans for
individual tool calls and model invocations -- the same execution
record this book's [session-persistence.md](session-persistence.md)
covers as durable storage and
[streaming-and-incremental-rendering.md](streaming-and-incremental-rendering.md)
covers as a live event stream, here treated instead as the *unit of
inspection* an evaluator reads after the fact.

The course's own regression-testing methodology, read directly from the
fetched page: populate a dataset of input/output pairs representing
expected behavior; run the agent against every item in that dataset;
record each output and link it back to its originating test case;
compare results across configurations (a different model, a different
tool set, a changed prompt); and visualize the comparisons side by side
to spot where a change moved the needle. **LLM-as-a-judge** -- using a
second model to score an output against stated criteria -- is named as
the mechanism that lets this comparison run unattended rather than
requiring a human to read every trace. The course's own capstone (Unit
4, not re-fetched in full this session but referenced by the same
source material) has a learner build an agent and score it against a
subset of the **GAIA** benchmark, a concrete example of the fourth,
outermost layer in this page's diagram: a benchmark that scores an
agent's ability to actually complete real tasks, not any one harness
mechanism in isolation.

This general vocabulary maps cleanly onto the four-layer pyramid this
page's diagram draws, but the mapping itself -- which layer a given
piece of harness-specific evidence actually belongs to -- is this
page's own synthesis, not a claim from the Hugging Face course, which
does not discuss Claude Code, Copilot CLI, or OpenCode by name at all.

---

## 2. Claude Code

Claude Code is closed source; no test suite exists in
`github.com/anthropics/claude-code` to read. Two of Anthropic's own
engineering blog posts, however, document real, first-party guidance on
evaluating agent behavior -- read as Anthropic's own stated practice,
not merely third-party advice, since both are published directly under
`claude.com`/`anthropic.com`'s own engineering domains.

### 2.1 Anthropic's published evals guidance for agents built on the Claude Agent SDK

VERIFIED, `claude.com/blog/building-agents-with-the-claude-agent-sdk`,
fetched fresh this session. The post states its central testing
directive plainly: "If your agent's performance varies as you add
features, build a representative test set for programmatic evaluations
(or evals) based on customer usage" -- i.e. the recommended dataset for
an eval suite is drawn from real observed usage, not authored
speculatively, and the post frames this as a release-gating discipline
rather than a one-off exercise: don't ship a prompt or model change "on
vibes," score it against the eval dataset first, and keep a scheduled
evaluation run watching for regressions the eval set itself did not
predict. Three concrete verification methods are named, each with an
explicit tradeoff called out:

- **Rules-based feedback** -- "the best form of feedback is providing
  clearly defined rules for an output, then explaining which rules
  failed and why," with code linting given as the canonical example.
  This is the same category Layer 1 of this page's pyramid names --
  deterministic, mechanical, no model-judgment involved.
- **Visual feedback** -- screenshots or renders, for verifying UI
  generation and other visually-checkable tasks, a check that has no
  clean textual assertion to write against.
- **LLM as judge** -- a second model scoring output against fuzzy
  criteria, with an explicit caution attached: the post states this
  "is generally not a very robust method, and can have heavy latency
  tradeoffs" -- a real, first-party caveat on the exact technique the
  Hugging Face course in §1 recommends more unreservedly, worth reading
  side by side as two sources disagreeing in emphasis on the same
  method's reliability.

The post also frames failure-mode diagnosis as a design question, not
only a testing one: does the agent misunderstand the task (a missing-
information problem), does it fail the same way repeatedly (evidence
that a formal, rules-based check is needed rather than more prompting),
and can it recover from its own errors -- questions that shape what an
eval dataset should even be checking for, prior to writing any
assertions.

### 2.2 The evaluator-agent pattern, and why harness design is inseparable from capability evals

VERIFIED, `anthropic.com/engineering/harness-design-long-running-apps`,
fetched fresh this session. This post's central, explicitly stated
claim is the reason this page opened with the model-versus-harness
distinction: capability evaluations on multi-step tasks are, in the
post's own words, deeply influenced by harness design, not just the
underlying model -- "the infrastructure around the model" is described
as "just as critical as the model itself" to a measured capability
score. The post's own concrete testing mechanism is a dedicated
**evaluator agent** distinct from the agent doing the work: for a DAW
(audio workstation) build example, the evaluator used Playwright to
exercise the built application through its actual UI, and identified
real functional gaps that way -- non-functional audio recording, missing
clip-manipulation features -- rather than by reading source code or
trusting the builder agent's own self-report.

The post frames the evaluator's own correctness as a design problem in
its own right, not a solved given: rather than reaching for standardized
external benchmarks, it describes hand-authored, criteria-based grading
rubrics (four named criteria for frontend work -- design quality,
originality, craft, and functionality -- explicitly built to convert
"subjective judgements into concrete, gradable terms" an evaluator agent
can apply consistently) and, for full-stack work, grading against a
**sprint contract** -- an agreed specification of testable behaviors
fixed *before* implementation begins, so the evaluator has a stable
target rather than grading against a moving or retroactively-justified
standard. The post's own description of tuning this evaluator is
manual and iterative, not itself automated: "read the evaluator's logs,
find examples where its judgment diverged from mine, and update the
[evaluator's] prompt to solve for those issues" -- i.e. even a
purpose-built evaluator agent needs its own review-and-correct loop
before its verdicts can be trusted, a recursive version of exactly the
verification problem this whole page is about.

### 2.3 Headless mode as documented scaffolding for building an external eval/CI harness

VERIFIED, `code.claude.com/docs/en/headless`, fetched fresh this
session. Nothing on this page describes an eval framework Anthropic
ships, but several documented features are explicitly framed around
making Claude Code's own output deterministic and machine-checkable --
i.e. this is the raw material a builder would use to construct the
Layer 1-3 checks this page's pyramid names, aimed at Claude Code itself
rather than at a project Claude Code is working on:

- **`--bare` mode** is documented as skipping auto-discovery of hooks,
  skills, plugins, MCP servers, auto memory, and CLAUDE.md entirely,
  with the docs stating outright: "Bare mode is useful for CI and
  scripts where you need the same result on every machine" -- a
  directly-named determinism guarantee, since a hook or MCP server
  picked up incidentally from a teammate's `~/.claude` or a project's
  `.mcp.json` is exactly the kind of environment-dependent variable
  that would make a CI-run eval non-reproducible. The docs flag it as
  "the recommended mode for scripted and SDK calls" and note it will
  become `-p`'s default in a future release.
- **`--output-format json`** returns "structured JSON with result,
  session ID, and metadata," including `total_cost_usd` and a
  per-model cost breakdown the docs describe as lettings "scripted
  callers track spend per invocation" -- directly useful for an eval
  harness that wants to log cost alongside correctness per test case,
  the same per-case bookkeeping the Hugging Face course's methodology
  in §1 calls for.
- **`--output-format json` combined with `--json-schema`** validates
  the response against a caller-supplied JSON Schema and surfaces the
  result in a `structured_output` field -- the docs are explicit that
  an invalid schema itself is now a hard error (`Error: --json-schema
  is not a valid JSON Schema`), a changelog-traced hardening from
  v2.1.205 onward (before that version, the docs state, "Claude Code
  silently ignored an invalid schema and returned unstructured text");
  this is precisely the kind of schema-validated, assertion-friendly
  output shape an automated correctness check over many test prompts
  would want to diff against expected values.
- The **`system/init` event's `plugin_errors` and `mcp_server_errors`
  fields** are the one place this page found explicit, first-party CI
  language on `code.claude.com/docs` itself: the docs' own subsection
  is titled "Fail CI when a plugin or MCP server doesn't load," and
  states the field is "omitted when there are no errors, so a CI gate
  can fail on a non-empty array" -- a documented, load-bearing
  CI-integration contract, not a side effect a builder would have to
  discover by trial and error.
- The docs close by pointing to dedicated **GitHub Actions** and
  **GitLab CI/CD** pages for wiring the Agent SDK into pipeline
  automation directly, named as the intended next step past ad hoc
  `-p` scripting -- this page did not re-fetch either of those pages
  this session, so their own content is not claimed here beyond their
  existence as documented integration points.

### 2.4 The changelog's own "regression" vocabulary, read as proxy evidence

VERIFIED, `github.com/anthropics/claude-code` `CHANGELOG.md`, fetched
fresh this session via `gh api repos/anthropics/claude-code/contents/
CHANGELOG.md` (full 5,248-line file), grepped for `regression`. The
changelog uses that exact word, paired with the specific version that
introduced the bug, dozens of times across its history -- a small,
representative sample: "Fixed plugins enabled via the `--settings` CLI
flag not loading (regression since v2.1.181)," "Fixed a prompt-caching
regression on Bedrock, Vertex, Mantle, and Foundry that billed the
trailing system context block as fresh input tokens on every request,"
"Fixed a startup regression (~120ms per launch in fresh environments,
introduced in 2.1.169)," and "Fixed a regression where the context
window blocking limit was calculated too aggressively, blocking users
at ~65% context usage instead of the intended ~98%." Read plainly, this
dated, versioned self-tagging is the *only* externally visible evidence
this page found of Anthropic's own internal fix-verify discipline for
Claude Code, since the repository ships no test suite to inspect
directly (the same standing limitation every other page in this book
notes for Claude Code's internals). It should be read carefully for
what it does and does not prove: it demonstrates that regressions are
identified, attributed to a specific prior version, and fixed on a
sustained, ongoing basis -- consistent with an internal regression-test
suite existing and being extended after each escaped bug, per the
usual "add a test for the bug you just fixed" discipline -- but the
changelog itself never states that such a suite exists, its shape, or
its coverage; that inference is BEST CURRENT UNDERSTANDING, UNCONFIRMED,
not a fact this page can cite the changelog as directly asserting.

---

## 3. GitHub Copilot CLI

Copilot CLI is likewise closed source, with no test suite to inspect in
`github.com/github/copilot-cli`. Unlike Claude Code, this page found no
equivalent first-party engineering blog post from GitHub describing an
evals methodology for the CLI specifically -- a real, flagged gap
relative to §2.1/§2.2's two Anthropic posts, not merely an omission in
this page's own research.

### 3.1 Documented non-interactive/programmatic execution

VERIFIED, `docs.github.com/en/copilot/reference/copilot-cli-reference/
cli-programmatic-reference`, fetched fresh this session. The page names
its own intended audience directly: "scripts, CI/CD pipelines, and
automation workflows." The core primitive is `-p PROMPT` ("Execute a
prompt in non-interactive mode. The CLI runs the prompt and exits when
done"), with `-s` documented as suppressing "stats and decoration,
outputting only the agent's response. Ideal for piping output in
scripts" -- the same script-friendly-output goal Claude Code's `-p`
mode serves, though the two harnesses arrived at it via different flag
vocabularies (`--output-format text` vs. Copilot's default `-p` output
plus `-s` to strip decoration). Two session-capture flags are also
documented -- `--share=PATH` ("Export the session transcript to a
markdown file after non-interactive completion") and `--share-gist`
("Publish the session transcript as a secret GitHub gist after
completion") -- both directly useful for the kind of trace-capture-per-
test-case §1's general methodology calls for, since a Markdown
transcript export is a durable, reviewable artifact per invocation.
Environment variables `COPILOT_ALLOW_ALL`, `COPILOT_MODEL`, and
`COPILOT_GITHUB_TOKEN` are documented as the automation-configuration
surface. **A genuine gap found on this specific page**: it documents
none of `--output-format json`/JSONL, structured-response parsing, or
exit-code/error-handling behavior -- despite the CLI's own changelog
(§3.2 below) confirming a JSON output flag exists; this docs page is
simply narrower in scope than Claude Code's equivalent headless-mode
page, not evidence the feature itself is undocumented anywhere.

### 3.2 Changelog-traced scaffolding for external, script-driven verification

VERIFIED, `github.com/github/copilot-cli` `changelog.md`, fetched fresh
this session via `gh api repos/github/copilot-cli/contents/
changelog.md` (full 2,898-line file), grepped for `regression`,
`benchmark`, `test suite`, `non-interactive`, `headless`,
`--output-format`, and `programmatic`. Several dated entries build up
exactly the kind of scriptable, assertion-friendly surface §2.3 already
documents for Claude Code, arrived at independently and on a different
timeline:

- **v0.0.422 (2026-03-05)**: "Add --output-format json flag to emit
  JSONL in prompt mode for programmatic integrations" -- the direct
  Copilot CLI analogue of Claude Code's `--output-format json`/
  `stream-json`, confirming machine-parseable output is a real,
  shipped CLI feature even though the docs page checked in §3.1 does
  not mention it.
- **v1.0.16 (2026-04-02)**: "Add PermissionRequest hook to allow
  scripts to programmatically approve or deny tool permission
  requests" -- a scripted-approval mechanism an automated test harness
  could use to drive a Copilot CLI session through a fixed,
  reproducible permission-decision path without a human at the
  keyboard, the same non-interactive-determinism goal Claude Code's
  `--bare`/`--allowedTools` flags serve.
- **v1.0.33 (2026-04-20)**: "Non-interactive mode waits for all
  background agents to finish before exiting" -- a correctness fix
  directly relevant to any test harness driving Copilot CLI
  programmatically: before this version, a script capturing `-p`
  output could plausibly race a still-running background agent and
  observe an incomplete result, exactly the kind of flaky-test hazard
  a CI-oriented eval suite would need to be immune to.
- **v1.0.69 (2026-07-07)**: "Add auto allow-all mode that auto-approves
  requests an LLM judge evaluates as acceptable" -- a genuinely
  interesting, source-confirmed instance of "LLM as judge" (the exact
  technique named in both §1 and §2.1) being used operationally
  *inside* the harness's own permission-decision pipeline, not as an
  external eval technique applied to the harness from outside. This is
  a different use of the same mechanism from anything else on this
  page and should not be conflated with an evals practice for
  validating Copilot CLI itself -- it is the harness using an LLM
  judge on live traffic, not a test author using one to score a
  recorded eval run.

### 3.3 The changelog's own regression vocabulary

The same `regression`-tagged, dated bug-fix pattern §2.4 documents for
Claude Code recurs here on an independent timeline: "Fix a regression
that caused 'Invalid session id' errors for agent shell calls," "Fixed
timeline entry regression where read_agent and other tools showed
incorrect content," "Fixed a regression where calling `/model` with an
argument did not work properly," and "Moved Kitty protocol support
behind the `COPILOT_KITTY` environment variable due to observed
regressions" (the last explicitly cross-referencing two GitHub Issues,
#257 and #259, as the source of the observed regression reports). The
same caveat from §2.4 applies identically: this is proxy evidence of an
ongoing internal fix-verify discipline, not a confirmed description of
any specific internal test-suite architecture, since -- as with Claude
Code -- no implementation source exists in this repository to check
that inference against.

---

## 4. OpenCode

VERIFIED throughout this section, `github.com/anomalyco/opencode`,
`dev` branch (not a stable release tag, per this project's standing
flag), located via `gh search code`/`gh api .../git/trees` and read in
full via `curl` against `raw.githubusercontent.com` this session. This
is the one harness in this book where "how would you test this" has a
literal, source-read answer rather than an inferred or documented one
-- the repository's own `git` tree lists hundreds of `*.test.ts` files
spread across every package (`packages/core/test/`, `packages/llm/
test/`, `packages/app/src/**/*.test.ts`, `packages/httpapi-codegen/
test/`, and more), and this section reads a representative, directly
relevant slice of that suite rather than claiming to have read all of
it.

```mermaid
sequenceDiagram
    participant Test as Test file (bun:test / recordedTests)
    participant Recorder as @opencode-ai/http-recorder
    participant Cassette as JSON cassette on disk\n(test/fixtures/recordings/**)
    participant API as Real provider API\n(Anthropic, OpenAI, Bedrock, Gemini, ...)
    Note over Test,API: RECORD=true (local, deliberate re-record)
    Test->>Recorder: run scenario (mode: record)
    Recorder->>API: real HTTP/WebSocket request
    API-->>Recorder: real response (streamed or not)
    Recorder->>Cassette: write redacted JSON cassette
    Note over Test,API: default / CI (mode: replay)
    Test->>Recorder: run scenario (mode: replay)
    Recorder->>Cassette: read matching cassette
    alt cassette exists
        Cassette-->>Recorder: recorded bytes, replayed verbatim
        Recorder-->>Test: deterministic response, no network call
    else cassette missing
        Recorder-->>Test: test skipped locally / hard fail when CI=true
    end
```

### 4.1 The record/replay cassette architecture

VERIFIED, `packages/http-recorder/README.md` (full file read this
session). The package's own one-line purpose statement: "Record real
Effect HTTP and WebSocket traffic once, then replay it from
deterministic JSON cassettes," recommended explicitly for "provider
integrations, retries, polling, multi-step flows, and any test where
hand-written HTTP mocks hide too much of the real request shape" -- a
direct, stated rejection of the alternative (a developer hand-writing a
fake response body) on the grounds that a hand-written mock tends to be
simpler and rounder than what a real API actually returns, hiding the
exact edge cases (odd chunk boundaries, provider-specific field
ordering, real error payloads) a tool-call-parsing test most needs to
catch. The README's own stated CI-safety discipline is exactly the
detail that makes this suite trustworthy as a regression gate rather
than a source of silent false negatives: "When `CI=true`, missing
cassettes fail instead of recording" -- i.e. a CI run can never
silently fall back to live-recording mode and never silently skip a
test because its cassette went missing; a missing cassette in CI is a
hard failure demanding a deliberate, human-triggered re-record.
`packages/llm/test/recorded-test.ts` (full file read this session)
implements the harness consuming this package for the LLM-protocol
suite specifically: a `mode` derived from `process.env.RECORD ===
"true"`, secret redaction merged from both a group-level and a
per-case `RecorderOptions` (headers, allowed request/response headers,
query parameters, and JSON fields can each be independently redacted or
allow-listed before a cassette is ever written to disk), and
`packages/llm/test/recorded-utils.ts` (full file read this session)
supplying an env-var-driven test-selection mechanism --
`RECORDED_PREFIX`, `RECORDED_PROVIDER`, `RECORDED_TAGS`, and
`RECORDED_TEST` -- letting a maintainer re-run or re-record just the
Anthropic-tagged subset, or just one named scenario, rather than the
entire provider matrix on every local iteration.

### 4.2 The golden-scenario regression matrix: one scenario, run against ~18 provider/model targets

VERIFIED, `packages/llm/test/provider/golden.recorded.test.ts` (full
223-line file read this session), `packages/llm/test/recorded-golden.ts`
(full file), and `packages/llm/test/recorded-scenarios.ts` (opening
~140 lines read in full). This is the file most directly answering the
handoff's own framing of this topic -- "benchmark-style correctness
checks on tool-call parsing." A single shared scenario generator,
`weatherToolLoopRequest`/`goldenWeatherToolLoopRequest` (a fixed system
prompt instructing the model to call a `get_weather` tool exactly once,
then reply with an exact scripted sentence, "Paris is sunny"), and a
shared driver, `runWeatherToolLoop`, which runs an actual multi-step
tool loop (dispatching the real `weatherRuntimeTool` handler against
the model's `tool-call` events, feeding results back as `Message.tool`
entries, capped at 10 steps) are each defined **once** and then reused
identically across a declared list of concrete provider/model targets
in `golden.recorded.test.ts`: OpenAI Chat (`gpt-4o-mini`), OpenAI
Responses (`gpt-5.5`, both HTTP and WebSocket transports), Anthropic
(Haiku 4.5 and Opus 4.7), Gemini 2.5 Flash, xAI (Grok 3 Mini and Grok
4.3), Cloudflare AI Gateway and Cloudflare Workers AI (each in a
plain-text and a tools-capable model variant), and four OpenAI-
compatible third-party endpoints reached through `openai-compatible-
chat.ts` -- DeepSeek, TogetherAI, Groq, and three separate OpenRouter-
routed models (GPT-4o-mini, GPT-5.5, and Claude Opus 4.7 all proxied
through OpenRouter specifically). Each target declares which named
scenario IDs it exercises (`text`, `tool-call`, `tool-loop`,
`image-tool-result`, `reasoning`, `reasoning-continuation`) via a
shared `ScenarioInput` type, a `requires` list of environment variables
that gate whether the scenario can even attempt a live re-record, and
an optional `tags` array (`"flagship"` marking the more expensive
frontier-model variants of a given provider) that the env-var selection
mechanism in §4.1 can filter on. The practical effect: the identical
logical question -- "does a tool call survive a full request/response/
tool-execution/continuation round trip, parsed correctly, for this
specific protocol implementation" -- is asked against every protocol
family this book's [llm-api-contract.md](llm-api-contract.md) §3.3
documents (`anthropic-messages.ts`, `openai-chat.ts`, `openai-
responses.ts`, `gemini.ts`, plus the `openai-compatible-chat.ts` reuse
path), turning a single authored scenario into a genuine cross-protocol
regression matrix rather than one test per protocol independently
authored and prone to drifting out of parity with each other.

### 4.3 Unit-level correctness tests on the reassembly algorithm itself

VERIFIED, `packages/llm/test/tool-stream.test.ts` (full 99-line file
read this session) -- the layer directly underneath §4.2's live-request-
shaped tests, and the one most precisely answering "correctness checks
on tool-call parsing" in the narrowest possible sense: pure,
deterministic unit tests on `ToolStream`, the module
[llm-api-contract.md](llm-api-contract.md) §3.3 already names as the
per-protocol fragment-accumulation logic. One test drives
`ToolStream.appendOrStart` across **two separate calls** with
OpenAI-shaped delta fragments split mid-JSON-string
(`'{"query"'` then `':"weather"}'`), asserting the exact
`tool-input-start`/`tool-input-delta` event sequence produced by each
call individually and the final `tool-input-end`/`tool-call` event
(with `input` already parsed to `{ query: "weather" }`) produced once
`ToolStream.finish` is called -- a literal, assertion-backed
demonstration of surviving a chunk boundary landing mid-string, the
exact scenario this book's other pages (llm-api-contract.md §1.5's
"partial JSON strings" warning, and a real, changelog-confirmed Claude
Code bug fixed in v2.1.92 per
[streaming-and-incremental-rendering.md](streaming-and-incremental-rendering.md)
§1.2) discuss only in the abstract or via a dated bug-fix log entry.
Further cases assert: `ToolStream.appendExisting` against a tool the
stream never saw a start event for correctly fails with a named
`LLMError` ("missing tool") rather than silently producing a malformed
result; `ToolStream.finishWithInput` correctly discards accumulated
deltas in favor of an authoritative final-input override without
losing the tool's identity or name; and `ToolStream.finishAll` correctly
preserves a `providerExecuted: true` flag on a hosted tool call (the
same server-executed-tool passthrough
[llm-api-contract.md](llm-api-contract.md) §3.3 documents) while
clearing every pending tool from the stream's internal state at once.
These are the kind of tests that need no network access, no API key,
and run in milliseconds -- deliberately the cheapest, fastest-feedback
layer of this whole page's pyramid, sitting directly below §4.2's
recorded, protocol-shaped scenarios.

### 4.4 Event-serialization regression tests, including a schema-backward-compatibility check

VERIFIED, `packages/core/test/session-runner-tool-events.test.ts` (full
136-line file read this session). This file tests the layer
[streaming-and-incremental-rendering.md](streaming-and-incremental-rendering.md)
§3.1 already documents from source (`publish-llm-event.ts`'s
republishing of `LLMEvent`s onto the session's own `SessionEvent` bus),
specifically for correctness of the *serialized* event shape rather
than the accumulation logic itself. One test confirms a local tool's
successful result containing a base64-encoded image is serialized
**exactly once** rather than duplicated across the event's `content`
and (legacy) `result` fields -- asserted by literally counting the
number of times the base64 string appears in the serialized JSON
(`serialized.split(base64)).toHaveLength(2)`, i.e. exactly one
occurrence) and asserting the modern field lacks a redundant `result`
property entirely. A second test confirms the opposite for a
**provider-executed** tool result, which deliberately *does* retain its
compatibility `result` field -- directly testing the same local-vs-
provider-executed divergence this book's other pages document as a
real architectural fork. A third test confirms a binary-read failure
emits a `tool.failed` event and never a spurious `tool.success` event.
The most notable single test in the file, from a pure
regression-engineering standpoint: **"old success event data containing
result still decodes"** -- it hand-constructs a payload shaped like an
*older* version of this same event schema (carrying a `result` field a
newer schema version no longer requires) and asserts
`Schema.decodeUnknownSync` still accepts it. This is a literal,
automated backward-compatibility regression test protecting exactly the
failure mode a durable, on-disk event/session-persistence format (this
book's own [session-persistence.md](session-persistence.md) documents
OpenCode's SQLite-backed message/event storage) would otherwise be
vulnerable to silently breaking on the next schema change.

### 4.5 Integration-level tests: the whole session loop against a recorded real transcript

VERIFIED, `packages/core/test/session-runner-recorded.test.ts` (opening
~80 lines of a 193-line file read this session). This test sits one
full layer above both §4.2 (a request/response round trip in isolation)
and §4.3-§4.4 (pure unit tests on individual functions): it wires
together real, non-mocked instances of the actual production dependency
graph -- `SessionRunner`, `SessionRunnerLLM`, `SessionProjector`,
`SessionExecution`, a real SQLite-backed `Database` layer, a real
`ToolRegistry`/`ToolOutputStore` -- alongside a small number of
deliberately mocked peripheral services (`PermissionV2.Service` mocked
to `Effect.die("unused")` on every method, confirming this specific
test path never needs a permission decision; `SkillGuidance` and
`ReferenceGuidance` both mocked to return an empty `SystemContext`,
keeping the test's system prompt minimal and deterministic) and drives
the whole assembly against a **recorded** OpenAI Chat cassette
(`session-runner/openai-chat-streams-text.json`, using the identical
`HttpRecorder`/cassette mechanism §4.1 documents, gated the same way on
`process.env.RECORD === "true"`). The practical effect: this is the
test that would catch a bug in how the session layer *itself*
reconstructs a message from a real streamed transcript, as distinct
from a bug in the lower-level LLM-client parsing §4.2/§4.3 already
cover in isolation -- the same "session/integration correctness" layer
this page's opening pyramid names as Layer 2, here shown to be a real,
source-verified test class in OpenCode specifically rather than a
theoretical category.

### 4.6 Route-coverage: a dedicated DSL-driven HTTP API exerciser

VERIFIED, `packages/opencode/test/server/httpapi-exercise/index.ts`
(header comment and opening ~90 lines of a 1,802-line file read this
session) and `packages/opencode/test/server/httpapi-exercise/dsl.ts`
(first 80 lines of a 210-line file read this session). The file's own
header comment states its purpose and explicitly distinguishes it from
ordinary unit testing: "The goal is not to be a normal unit test file.
This is a route-coverage harness: every public route should have a
small scenario that proves the route decodes requests, uses the right
instance context, mutates storage when expected, and returns the
expected response shape." The DSL itself (`http.protected.get/post/...`
chained with `.seeded(...)`, `.at(...)`, `.json(...)`/`.jsonEffect(...)`,
`.mutating()`, `.stream()`, and an auth-policy selector --
`.protected()`/`.public()`/`.publicBypass()`) declares one scenario per
documented HTTP API route against a real, in-process server instance
backed by a `TestLLMServer` fake rather than a live model, with the
comment's own stated safety discipline: the script "intentionally
isolates `OPENCODE_DB` before importing modules that touch storage,"
since scenarios "may create/delete sessions and reset the database
after each run," explicitly warning this "must never point at a
developer's real session database." This is a genuinely distinct
correctness layer from §4.2-§4.5: none of the earlier tests check
whether the *documented public API surface itself* -- the same
Server-Sent-Events/HTTP layer
[inter-agent-messaging.md](inter-agent-messaging.md) documents carrying
live session events -- actually round-trips correctly end to end for
every route, only whether the LLM-protocol or session-execution layers
underneath it behave correctly in isolation.

### 4.7 The CI pipeline gluing these layers together

VERIFIED, `.github/workflows/test.yml` (full 151-line file read this
session). Two top-level jobs run on every push to `dev` and every pull
request, each matrixed across Linux and Windows runners
(`blacksmith-4vcpu-ubuntu-2404`/`blacksmith-4vcpu-windows-2025`):

```mermaid
flowchart LR
    PR["push to dev / pull_request"] --> Unit["unit job (Linux + Windows)\nbun turbo test"]
    Unit --> Gen["Check generated client\n(Linux only, packages/client)"]
    Unit --> Exercise["Run HttpApi exerciser gates\n(Linux only, S4.6's DSL harness)"]
    PR --> E2E["e2e job (Linux + Windows)\nPlaywright against packages/app"]
    E2E --> Artifacts["Upload Playwright artifacts on failure\n(retention: 7 days)"]
```

The **`unit`** job runs `GITHUB_ACTIONS=false bun turbo test` -- the
single command that fans out across every package's own `*.test.ts`
suite (§4.2-§4.5's files among them) via Turborepo's own task
orchestration, with a Windows-specific env override
(`OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER: true` on Windows only)
flagging a real, cross-platform filesystem-watcher difference the suite
has to route around. Two further steps run **Linux-only**, after the
main unit-test step: `bun run check:generated` inside
`packages/client` (protecting the generated API client against drifting
out of sync with its own source schema -- a codegen-freshness
regression class distinct from anything in §4.1-§4.6) and `bun run
test:httpapi` inside `packages/opencode` -- the literal command that
invokes §4.6's route-coverage exerciser as its own, separately timed
CI gate rather than folding it into the ordinary `bun turbo test` run.
A wholly separate **`e2e`** job installs Playwright (with its own
browser-binary cache keyed on the pinned Playwright version read
directly out of `package.json`) and runs `bun --cwd packages/app
test:e2e:local` against the web/desktop app surface specifically,
uploading a `playwright-report`/`test-results` artifact "if-no-files-
found: ignore" but always attempted (`if: always()`) so a failing run's
traces survive the job for later inspection -- the practical, CI-level
implementation of exactly the trace-capture-per-test-case discipline
§1's general methodology names.

---

## 5. pi

VERIFIED throughout this section unless flagged otherwise,
`github.com/earendil-works/pi`, `main` branch, located via `gh api
repos/earendil-works/pi/git/trees/main?recursive=true` (full repository
file-tree listing, filtered for test/CI/eval paths) and individual files
read in full via `gh api repos/earendil-works/pi/contents/<path>` this
session. Like OpenCode, pi is a harness whose own repository is
genuinely inspectable rather than being read only through documentation
or a changelog; unlike OpenCode, its CI-safe deterministic layer is
built on a synthetic in-process model provider rather than recorded
real-provider HTTP traffic, and it additionally ships a *second*,
explicitly separate package purpose-built for model-backed behavioral
evaluation -- a distinction this book's other pi-covering pages have not
had occasion to surface, since none of them examine pi's own test
infrastructure.

### 5.1 Resolving this book's own inconsistent `pi-ai`/`pi-coding-agent` naming: both are correct, for different packages

VERIFIED, `package.json` read in full for `packages/ai`, `packages/coding-agent`,
`packages/agent`, and `packages/evals`, plus the repository-root
`package.json`, all fetched this session. pi is not a single npm
package but an npm-workspaces monorepo, `pi-monorepo` (the root
`package.json`'s own `name` field, marked `"private": true"`), declaring
workspaces across `packages/*`, `packages/session-backends/*`, and five
`packages/coding-agent/examples/extensions/*` example directories. This
resolves the naming question the handoff for this section asked to
verify: **`@earendil-works/pi-ai`** and **`@earendil-works/pi-coding-agent`**
are both real, correctly-named, currently-published packages inside
this one monorepo, not a spelling drift between two names for the same
thing --

- `packages/ai`'s `package.json` names the package `@earendil-works/pi-ai`
  ("Unified LLM API with automatic model discovery and provider
  configuration," version `0.84.4`, exposing a `pi-ai` CLI binary via its
  own `bin` field) -- this is the LLM-protocol/provider-adapter layer
  [llm-api-contract.md](llm-api-contract.md) §3.5 already documents as
  `pi-ai`, and the correct package for any claim about anthropic/openai/
  gemini/bedrock wire-protocol handling specifically.
- `packages/coding-agent`'s `package.json` names the package
  `@earendil-works/pi-coding-agent` ("Coding agent CLI with read, bash,
  edit, write tools and session management," same version `0.84.4`,
  exposing the actual `pi` CLI binary end users invoke), and declares a
  direct `dependencies` entry on `@earendil-works/pi-ai` (pinned
  `^0.84.4`) alongside three sibling first-party packages --
  `@earendil-works/pi-agent-core`, `@earendil-works/pi-client`,
  `@earendil-works/pi-protocol`, and `@earendil-works/pi-tui`. This is
  the correct package name for any claim about the CLI/TUI, session
  management, skills, hooks/extensions, or permissions/sandboxing --
  i.e. the subject matter of this book's other pi-covering pages
  (hooks-lifecycle-extensibility.md, permissions-and-sandboxing.md,
  session-persistence.md, configuration.md, auth-and-usage-accounting.md,
  built-in-skills.md, context-compression.md,
  model-routing-and-selection.md).
- A third, less-cited package this session's research turned up:
  `packages/agent`'s `package.json` names it
  `@earendil-works/pi-agent-core` ("General-purpose agent with transport
  abstraction, state management, and attachment support") -- a layer
  underneath `pi-coding-agent` that `pi-coding-agent` itself depends on
  (`@earendil-works/pi-agent-core: "^0.84.4"` in its own dependency
  list), and the package that actually hosts the `session/testing`
  conformance-test-generator subpath export discussed in §5.3 below.
- A fourth, private, non-published package, `packages/evals`'s
  `package.json` names it `@earendil-works/pi-evals` (`"private": true`)
  -- the model-backed eval package discussed in §5.4, deliberately never
  shipped to the npm registry since it exists only to test pi itself,
  not to be depended on by anything downstream.

Every one of these packages shares the same repository
(`git+https://github.com/earendil-works/pi.git`, distinguished only by
each `package.json`'s own `repository.directory` field) and the same
version number at any given commit (`0.84.4` for all four checked this
session), kept in lockstep by the root `package.json`'s own
`version:patch`/`version:minor`/`version:major` scripts (each running
`npm version --workspaces` followed by a `scripts/sync-versions.js`
pass). Read plainly: this book's prior pages citing `pi-ai` were correct
about the LLM layer, and its prior pages citing `pi-coding-agent` were
correct about the agent/CLI layer -- the apparent inconsistency the
handoff flagged is not an error to fix, it is two different packages in
the same monorepo, each cited correctly for the mechanism each page was
actually describing.

```mermaid
flowchart TD
    Mono["pi-monorepo (root package.json, private)\nnpm workspaces: packages/*"]
    Mono --> AI["@earendil-works/pi-ai\n(packages/ai) -- LLM protocol/provider layer\nbin: pi-ai"]
    Mono --> Core["@earendil-works/pi-agent-core\n(packages/agent) -- transport-agnostic agent loop,\nsession/testing conformance-suite export"]
    Mono --> CA["@earendil-works/pi-coding-agent\n(packages/coding-agent) -- the CLI/TUI end users run\nbin: pi"]
    Mono --> Evals["@earendil-works/pi-evals\n(packages/evals, private) -- model-backed\nbehavioral eval suite, not published"]
    CA -- depends on --> AI
    CA -- depends on --> Core
    Evals -- devDependency on --> AI
    Evals -- devDependency on --> CA
```

### 5.2 The CI-safe deterministic layer: a synthetic "faux" model provider, not recorded real-provider traffic

VERIFIED, `packages/ai/src/providers/faux.ts` (opening ~60 lines read
this session) and `packages/coding-agent/test/suite/README.md` (full
file, four lines). Where OpenCode's CI-safe layer (§4.1 above) replays
JSON cassettes recorded once from real provider traffic, pi's
equivalent layer instead runs against `faux` -- an entirely synthetic,
in-process `Provider` implementation registered under
`DEFAULT_API = "faux"`/`DEFAULT_PROVIDER = "faux"`/`DEFAULT_MODEL_ID =
"faux-1"`, exposing helper constructors (`fauxText`, `fauxThinking`,
`fauxToolCall`, and -- used directly in the regression test read in
§5.3 -- `fauxAssistantMessage`) that let a test author script an exact
assistant response (text, thinking blocks, and/or tool calls) without
ever making an HTTP request or needing a real API key. The
`packages/coding-agent/test/suite/README.md` file states this as an
explicit, enforced project convention for its own newer harness-based
test suite: "Use the faux provider from `packages/ai/src/providers/
faux.ts`... Do not use real provider APIs, real API keys, network
calls, or paid tokens... Keep these tests CI-safe and deterministic,"
alongside a companion rule that these new `test/suite/` tests should
build on a shared `test/suite/harness.ts` helper rather than the
project's older, superseded `test/test-harness.ts` path "unless a
missing capability forces it" -- i.e. pi's own test suite is mid-
migration between two harness-construction conventions, with the newer
one the explicitly documented default for new tests. This architectural
choice -- synthesize the model's output entirely rather than record and
replay a real one -- trades away OpenCode's benefit of exercising real
provider-specific response shapes (odd chunk boundaries, real error
payloads) in favor of never needing network access, secrets redaction,
or a `CI=true`/missing-cassette failure mode at all; the tradeoff itself
is this page's own synthesis, not a claim either project's own
documentation makes about the other.

### 5.3 Issue-numbered regression tests, and the broader per-provider/per-package test surface

VERIFIED, `packages/coding-agent/test/suite/regressions/
7290-json-stream-linear.test.ts` (opening lines read in full this
session) and the full repository file-tree listing (§5, header). pi's
regression-test directory,
`packages/coding-agent/test/suite/regressions/`, names each file after
the GitHub issue number it fixes -- `2781-skill-collision-precedence.
test.ts`, `5109-exclude-tools.test.ts`, `6363-agent-settled-event.
test.ts`, and (the file read in full) `7290-json-stream-linear.test.ts`,
whose own `describe` block is literally titled `"regression #7290: JSON
event streams stay linear"` and which uses the §5.2 `faux` provider
(`fauxAssistantMessage`) to script two assistant responses of different
lengths and assert the JSON-serialized event stream's byte size scales
linearly rather than quadratically with response length -- a genuine,
source-verified performance regression test, not merely a correctness
one, protecting the same JSON-event-streaming surface this book's
[streaming-and-incremental-rendering.md](streaming-and-incremental-rendering.md)
covers for other harnesses only via inferred or documented behavior.
This is the same "name the bug you're protecting against" discipline
this page's §2.4/§3.3 found only as prose in Claude Code's and Copilot
CLI's changelogs -- pi instead encodes it directly as the test file's
own path and `describe` string, at the time of this session's research
counting more than 55 individually issue-numbered files under that one
directory alone.

Beyond that dedicated regression directory, the file-tree listing this
session read shows the same `*.test.ts` density spread across every
workspace package, each with its own `vitest.config.ts`: `packages/ai/
test/` alone contains well over 100 files, the great majority named
directly after a specific provider/feature pairing being protected --
`anthropic-eager-tool-input-compat.test.ts`, `bedrock-raw-stop-reason.
test.ts`, `openai-responses-partial-json-cleanup.test.ts`,
`google-shared-gemini3-unsigned-tool-call.test.ts`,
`mistral-tool-schema.test.ts`, and per-provider OAuth tests
(`anthropic-oauth.test.ts`, `github-copilot-oauth.test.ts`,
`openrouter-oauth.test.ts`, `xai-oauth.test.ts`, `kimi-coding-oauth.
test.ts`, among others) -- read plainly, this is the same "one test
scenario per protocol/provider" instinct OpenCode's golden-scenario
matrix (§4.2) applies via one shared scenario replayed across targets,
but here expressed instead as many separately-authored, provider-
specific test files rather than one shared scenario generator reused
across a declared target list; this session did not read enough of
these files individually to confirm whether pi also has a shared-
scenario abstraction analogous to OpenCode's `recorded-scenarios.ts`,
so that comparison is offered as a structural observation about naming
density, not a confirmed architectural equivalence.

A separate, reusable pattern this session found and did confirm by
reading an actual consuming test:
`packages/agent/src/harness/session/testing/` (a `conformance.ts`/
`index.ts`/`types.ts` module exported from `@earendil-works/pi-agent-core`
under the subpath `./session/testing`) exports a
`createSessionBackendConformance` helper -- a shared, parameterized test
suite generator that any concrete `SessionRepo` backend implementation
must pass. `packages/session-backends/sqlite-node/test/
conformance.test.ts` (opening ~30 lines read this session) is a live
consumer: it imports `createSessionBackendConformance` and
`SessionBackendFixture` from `@earendil-works/pi-agent-core/session/
testing`, supplies a factory constructing a real, temp-directory-backed
`SqliteSessionRepository`, and gets the entire shared conformance suite
run against that one concrete backend for free. `packages/server/src/
testing/` and `packages/telemetry/src/testing/` export the identically-
shaped pattern (a `conformance.ts`/`index.ts`/`types.ts` triple) for
their own respective interfaces, confirmed present in the file tree
though not read line-by-line this session -- i.e. "export a reusable
conformance-test generator alongside the interface it tests" is a
repeated, deliberate authoring convention across at least three of pi's
packages, not a one-off.

### 5.4 `packages/evals`: a dedicated, `vitest-evals`-based model-backed behavioral eval package, separate from the CI-safe suite above

VERIFIED, `packages/evals/README.md` (full file), `packages/evals/
package.json` (full file), `packages/evals/src/pi-harness.ts` (full
file), and `packages/evals/src/smoke.eval.ts` (full file), all read this
session. Distinct from every test discussed in §5.2-§5.3 -- which need
no network access, no API key, and run in milliseconds -- pi ships a
wholly separate package, `@earendil-works/pi-evals`, whose own README
states its purpose plainly: "Pi evals are behavioral, model-backed
checks for Pi workflows... Use them to measure end-to-end behavior and
compare prompts, tools, skills, models, or other harness
configurations." This is pi's own equivalent of this page's Layer 4 --
a real, live (or at minimum externally-authenticated) model call is
required, invoked via `npm run eval -- --provider openai --model
gpt-5.6-sol` (or the equivalent `PI_PROVIDER`/`PI_MODEL` environment
variables), authenticating through "Pi's normal `ModelRuntime`,
including Pi subscription credentials and provider API-key environment
variables" -- i.e. the same [auth-and-usage-accounting.md](auth-and-usage-accounting.md)
credential-resolution path this book already documents for pi's normal
runtime use, reused here for the eval runner rather than the eval
runner inventing its own separate credential mechanism.

The package's central adapter, `createPiCodingAgentHarness(...)` in
`src/pi-harness.ts`, is a genuine integration test of pi's own real
production code, not a mock: it calls `ModelRuntime.create()`,
`createAgentSessionServices(...)`, and `createAgentSessionFromServices(...)`
-- the identical `AgentSession` construction path a real interactive or
headless pi invocation uses -- inside a freshly created temp directory
pair (`cwd`/`agentDir`) per eval run, explicitly asserting `evalSession.
extensionRunner.getExtensionPaths().length !== 0` would be a thrown
error (i.e. asserting the eval session starts genuinely isolated, with
zero extensions loaded, not merely configured to look isolated), and
snapshotting the resulting session's own on-disk JSONL artifact (the
same session-persistence format
[session-persistence.md](session-persistence.md) documents) as a
`PI_SESSION_SNAPSHOT_ARTIFACT` attached to the Vitest test result before
the temp workspace is deleted. `src/smoke.eval.ts` (the package's own
minimal example, read in full) is a single, literal illustration of
this pattern: it prompts a `noTools: "all"`-configured harness with
"What's the capital of France? Respond with only the city name," then
asserts the trimmed output equals `"Paris"`, that `result.errors` is
empty, that the recorded provider/model match the environment's
`PI_PROVIDER`/`PI_MODEL`, and that `totalTokens` is greater than zero --
a genuine, live-model-backed correctness check exercising the real tool-
disable, prompt, and usage-accounting plumbing end to end, distinct from
every synthetic `faux`-provider test in §5.2-§5.3. The README documents
a second, more elaborate pattern layered on top -- `evalHarnessTable(...)`
combined with Vitest's own `describe.for(...)` -- for comparative evals
across named variants (e.g. a `baseline` vs. `candidate` harness pair,
run across a configurable number of `repetitions`), computing a
pass-rate "lift" (candidate pass rate minus baseline pass rate, in
percentage points) from judge-scored runs, with an explicit documented
convention that comparative suites should set `judgeThreshold: null` so
a low score is recorded as an observation rather than failing the
Vitest invocation outright -- i.e. pi's own eval-authoring guidance
draws exactly the reliability distinction Anthropic's own blog post (§2.1)
makes about LLM-as-judge scoring, independently arrived at and encoded
as a structural default (`judgeThreshold: null`) rather than merely
advisory prose. The README additionally names `vitest-evals` itself
(`github.com/getsentry/vitest-evals`, an external, third-party
dependency this session did not independently fetch or verify) as the
general suite/judge/assertion framework pi's own eval package builds on
top of, and separately points to `github.com/adewale/skill-eval-harness/`
for comparative-eval methodology guidance -- neither of those two linked
repositories was fetched this session, so their own content beyond
being named and linked from pi's README is not claimed here.

```mermaid
flowchart LR
    subgraph "CI-safe, deterministic (S5.2-S5.3)"
        Faux["faux provider\n(packages/ai/src/providers/faux.ts)"]
        Suite["test/suite + per-package *.test.ts\n(vitest --run, no network, no API key)"]
        Faux --> Suite
    end
    subgraph "Manual/local, model-backed (S5.4)"
        Runner["npm run eval\n(packages/evals/scripts/run-evals.mjs)"]
        RealModel["real provider API\n(needs PI_PROVIDER/PI_MODEL + credentials)"]
        Harness2["createPiCodingAgentHarness()\nreal AgentSession, isolated temp cwd/agentDir"]
        Judge["judge-scored comparative suites\n(evalHarnessTable + describe.for)"]
        Runner --> Harness2 --> RealModel
        Harness2 --> Judge
    end
    Suite -.->|"gated in CI (S5.5)"| CI["ci.yml: npm run check && npm test"]
    Runner -.->|"NOT invoked by any workflow found this session"| CI
```

### 5.5 The CI pipeline, and evals' deliberate exclusion from it

VERIFIED, `.github/workflows/ci.yml` (full file, read this session) and
the full `.github/workflows/` directory listing from this session's
repository-tree fetch (nine other named workflow files:
`approve-contributor.yml`, `build-binaries.yml`, `issue-analysis.yml`,
`issue-gate.yml`, `issue-triage-labels.yml`, `npm-audit.yml`,
`pr-gate.yml`, `publish-model-catalog.yml`,
`remove-inprogress-on-close.yml`; only `ci.yml`'s own content was read
this session, the other nine are named but not opened). `ci.yml` runs
one job, `build-check-test`, on every push and pull request to `main`,
installing Node 22 plus system libraries for canvas/image support
(`libcairo2-dev`, `libpango1.0-dev`, `libjpeg-dev`, `libgif-dev`,
`librsvg2-dev`, `fd-find`, `ripgrep`), then three sequential steps:
`npm run build`, `npm run check` (Biome linting plus several
project-specific consistency checks -- pinned-dependency versions,
relative-import hygiene, a generated `npm-shrinkwrap.json` freshness
check, a generated install-lock freshness check, and a TypeScript
`--noEmit` pass), and finally `npm test`. The root `package.json`'s own
`test` script resolves to `npm run test:scripts && npm run test
--workspaces --if-present` -- i.e. a small Node-native test file glob
(`node --test scripts/*.test.mjs`) followed by npm workspaces fanning
that same `test` command out across every package that defines one
(nearly all of them resolve to a bare `vitest --run`), the same
"one root command fans out across every package's own suite" shape
OpenCode's `bun turbo test` (§4.7) achieves via Turborepo instead of
plain npm-workspaces propagation. **Critically, `packages/evals`'s own
`test` script (`vitest run --config vitest.test.config.ts`) is included
in this workspace fan-out and does run in CI** -- but that script tests
the eval *package's own infrastructure* (`test/vitest-evals/
artifacts.test.ts`, `harness-table.test.ts`, `summary.test.ts`,
`test/pi-harness.test.ts`), not the model-backed `*.eval.ts` scenarios
themselves; the model-backed `eval` script (`npm run eval`, invoking
`scripts/run-evals.mjs`) is a **separate** script this session found no
reference to in `ci.yml` or in any other workflow's own filename, so --
BEST CURRENT UNDERSTANDING, UNCONFIRMED, since the other nine workflow
files were not individually opened this session -- pi's own
model-backed, judge-scored eval suite (§5.4) most plausibly runs
manually/locally against a developer's own chosen provider and
credentials rather than being gated automatically on every pull
request, for the same practical reason Anthropic's own guidance (§2.1)
flags LLM-as-judge scoring as latency-heavy and "not a very robust
method": a suite that costs real API spend and real wall-clock time per
run is a natural candidate to keep out of a required, blocking CI gate.
This is the one meaningful architectural difference from OpenCode's own
CI shape (§4.7), where even the live-network-adjacent Playwright `e2e`
job runs automatically on every push and PR; pi's equivalent
capability-level check appears, from what this session could directly
confirm, to be opt-in rather than gate-blocking.

### 5.6 Environment isolation for the test run itself

VERIFIED, `test.sh` (full file, read this session). Separately from
what gets tested, pi's own root-level `test.sh` wrapper (not itself
invoked by `ci.yml`, which calls `npm test` directly -- this session
found no reference to `test.sh` from within `ci.yml`) constructs an
isolated `mktemp`-created home directory, redirects `HOME`,
`USERPROFILE`, `TMPDIR`/`TMP`/`TEMP`, `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`,
npm's own user/global config and cache paths, and a deliberately broken
`GIT_ASKPASS` (`type -P false`) into that temp root, then runs `env -i`
with an explicitly reconstructed, minimal environment variable list
(preserving only `PATH`, `PWD`, platform-required Windows variables,
and `CI`/`GITHUB_ACTIONS` for runner-behavior detection) before invoking
`npm test` -- a self-described discipline of "start from an empty
environment and allow only required platform and test settings," with
its own cleanup trap refusing to delete anything that isn't a directory
it marked as its own (`test_root/.pi-test-owned`) moments earlier. Read
plainly, this script exists to guarantee the exact determinism property
Claude Code's `--bare` mode (§2.3) states its own purpose in almost
identical language for ("the same result on every machine") -- except
here the isolation is achieved by a wrapper script scrubbing the
external process environment before the test command ever starts,
rather than by a CLI flag telling the harness itself to skip
auto-discovery of its own configuration surface. A separate,
unrelated helper at the repository root, `pi-test.sh`, serves a
different purpose entirely: it is a `tsx`-driven wrapper for running
pi's own CLI directly from source (`packages/coding-agent/src/cli.ts`)
during development, with an optional `--no-env` flag that unsets over
30 named provider/credential environment variables (`ANTHROPIC_API_KEY`,
`OPENAI_API_KEY`, `AWS_*`, `AZURE_OPENAI_*`, and others, explicitly
cross-referenced in its own comment to `packages/ai/src/
env-api-keys.ts`) so a developer can manually verify pi's own
no-credentials-available behavior -- a manual-testing convenience
script, not a CI-invoked one, and not to be confused with `test.sh`'s
own automated-suite-isolation purpose despite the similar filename.

---

## 6. Synthesis

| Layer (per this page's own pyramid) | Claude Code | Copilot CLI | OpenCode | pi |
|---|---|---|---|---|
| Unit-level wire-format/tool-call-parsing correctness | Not source-visible; changelog shows dated reassembly *bugs* fixed (v2.1.92, v2.1.94, cross-referenced from streaming-and-incremental-rendering.md §1.2), not a visible test | Not source-visible; no equivalent changelog entries found this session | Source-verified: `tool-stream.test.ts`'s `ToolStream` unit tests, asserting exact event sequences across a deliberately split-mid-string chunk boundary (§4.3) | Source-verified: dozens of per-provider unit tests in `packages/ai/test/` (§5.3), run deterministically against the synthetic `faux` provider (§5.2) rather than recorded real traffic |
| Session/integration correctness | Not source-visible | Not source-visible | Source-verified: `session-runner-tool-events.test.ts` (event-serialization + schema-backward-compatibility, §4.4) and `session-runner-recorded.test.ts` (whole-loop-against-a-recorded-transcript, §4.5) | Source-verified: `test/suite/`'s harness-based `AgentSession`/`AgentSessionRuntime` tests plus an issue-numbered regression directory (55+ files, §5.3), and a reusable `createSessionBackendConformance` interface-conformance generator shared across at least three packages (§5.3) |
| Cross-provider/protocol regression matrix | Not applicable in the same sense (single first-party model provider) | Not applicable in the same sense | Source-verified: one shared golden scenario (`weatherToolLoopRequest`) run against ~18 provider/model targets spanning every protocol family llm-api-contract.md §3.3 documents (§4.2), using deterministic VCR-style recorded cassettes (§4.1) | Not confirmed as a single shared-scenario abstraction this session; instead, many separately-authored per-provider/per-feature test files (§5.3) -- a structural observation, not a confirmed architectural equivalence to OpenCode's matrix |
| API/route-surface coverage | Not source-visible | Not source-visible | Source-verified: a dedicated DSL-driven `httpapi-exercise` route-coverage harness, its own separately-timed CI gate (§4.6-§4.7) | Not confirmed this session; the file-tree search did not surface an equivalent dedicated route-coverage harness |
| First-party published evals *guidance* | Two Anthropic engineering posts: representative-test-set/gate-releases-on-evals discipline, three verification methods (§2.1), the evaluator-agent/criteria-rubric/sprint-contract pattern (§2.2) | None found this session -- a real, flagged gap relative to Claude Code | None found as separate published guidance; the test suite itself is the artifact, not a companion essay about testing philosophy | `packages/evals/README.md` doubles as both documentation and the artifact -- comparative-eval methodology (baseline/candidate lift, `judgeThreshold: null`) documented directly alongside the harness it describes (§5.4) |
| Documented scaffolding for external, script-driven verification | `--bare` determinism, `--output-format json`+`--json-schema`, `system/init`'s CI-gating `plugin_errors`/`mcp_server_errors` fields (§2.3) | `-p`/`-s` scripting mode, `--share`/`--share-gist` transcript export, changelog-confirmed `--output-format json` (v0.0.422), `PermissionRequest` hook (v1.0.16), non-interactive background-agent wait-to-completion fix (v1.0.33) (§3.1-§3.2) | The record/replay cassette package itself (`@opencode-ai/http-recorder`) is both the scaffolding and the thing being scaffolded around -- a first-party, in-repo testing tool, not merely a documented CLI flag surface | The `@earendil-works/pi-evals` package itself (`createPiCodingAgentHarness`, `evalHarnessTable`) is likewise both scaffolding and artifact (§5.4); separately, `test.sh`'s process-environment-scrubbing wrapper is a script-level determinism guarantee with no CLI-flag equivalent found this session (§5.6) |
| Changelog's own regression-fix vocabulary (proxy evidence only) | Extensive, dated, version-attributed (§2.4) | Extensive, dated, version-attributed (§3.3) | Present in commit history generally but not this page's focus, since actual test source is directly readable instead | Encoded directly as issue-numbered test file paths and `describe("regression #NNNN...")` strings rather than only changelog prose (§5.3) |
| End-to-end/capability benchmark integration (GAIA, SWE-bench, etc.) | Not researched this session beyond §2.2's evaluator-agent pattern | Not researched this session | Not researched this session | VERIFIED absent: `gh search code` for "GAIA" and "SWE-bench" scoped to `earendil-works/pi` returned no matches this session; pi's own capability-level checks (§5.4) are entirely first-party, prompt-and-judge-based, not integrated with any published third-party benchmark |

**The design lesson.** The single clearest, most load-bearing fact this
page's research turned up is the asymmetry itself: two harnesses ship
no way to check their own correctness claims from the outside beyond a
changelog's own honesty about dated regressions, while the other two --
OpenCode and pi -- ship the literal assertions. That asymmetry is a
direct consequence of this book's own standing open-source/closed-source
split (documented on every other page touching Claude Code's or Copilot
CLI's internals), not evidence that either closed-source team tests
less rigorously in private -- Anthropic's own two engineering posts
(§2.1-§2.2) are, if anything, unusually candid public evidence of a real
internal evals discipline, just one this page cannot verify the shape
of the way it can verify OpenCode's `ToolStream` test, its golden-
scenario matrix, or pi's own issue-numbered regression files line by
line. OpenCode and pi arrive at that same source-visible position by
genuinely different routes, and the difference is itself instructive: OpenCode
protects its CI-safe layer with recorded-and-replayed real provider
traffic (VCR-style cassettes), while pi protects its own equivalent
layer with an entirely synthetic in-process model (the `faux` provider,
§5.2) -- one preserves real provider-specific response shapes at the
cost of needing a deliberate, human-triggered re-record step when a
cassette goes missing, the other needs no network access or secrets-
redaction discipline at all but cannot, by construction, catch a
regression caused by a real provider changing its actual response shape
underneath the synthetic model's assumptions. Neither this page nor
either project's own documentation states one choice as strictly
superior to the other; both are read here as two legitimate, differently
-tradeoffed answers to the same "how do I test tool-call parsing without
paying for a live model on every CI run" problem. For a builder
validating a from-scratch harness, the concrete, transferable pattern
this page's research actually supports pulls from both: (1) fast,
deterministic unit tests on the fragment-accumulation algorithm itself,
needing no network access, whether achieved via a recorded cassette or a
synthetic fake model; (2) a small number of integration tests that wire
the real session loop against a recorded or synthetic, not live,
transcript; (3) either a shared "golden scenario" authored once and
replayed against every protocol/provider target the harness supports (OpenCode's
approach), or a densely issue-numbered regression directory naming each
test after the specific bug it protects against (pi's approach), so
protocol implementations or past bugs cannot silently regress
unnoticed; (4) a separate, explicit route/API-coverage pass distinct
from all of the above, because none of the first three layers actually
proves the documented public surface itself behaves as promised (source-
confirmed for OpenCode via its `httpapi-exercise` harness, §4.6; not
confirmed as present in pi this session, per the synthesis table above);
and (5) -- the one layer pi's own research surfaced most clearly of the
two open-source harnesses -- a separate, explicitly non-CI-gated,
model-backed eval package for judged, comparative, prompt-level
behavior, kept deliberately out of the blocking pull-request gate
because it costs real API spend and real wall-clock time per run
(§5.4-§5.5). Layer 4 (5, in pi's own case) of this page's opening
pyramid -- end-to-end capability evals such as GAIA (§1) -- sits outside
and above all of these, and, per Anthropic's own harness-design post
(§2.2), scores a combination of the model and the harness together; a
from-scratch harness builder who only ever runs that outermost layer has
no way to tell which of the two moved a score, which is the whole reason
the inner layers need to exist as their own, harness-scoped discipline
first. Notably, this session's own search of pi's repository found no
integration with any published third-party capability benchmark (GAIA,
SWE-bench, or similar, per the synthesis table's last row) -- pi's own
capability-level checks are entirely first-party and prompt-authored,
a real, citable finding about the scope of a comparatively young,
single-maintainer-adjacent open-source project's own eval investment,
not a criticism of its engineering rigor at the layers it does cover.

**A brief, bounded closing note.** This project's own `CLAUDE.md` states
plainly, as of this writing, that AIrchon itself -- the project this
wiki-book lives in -- "has no scripts, no `node:test` suite, and no
evals harness" of its own, on the grounds that `airchon-mentor` and
`airchon-author` are prose/research-driven rather than deterministic-
probe-driven the way a tool like AgentXRay's own `xray` skill family
is. That is a statement about this project's own tooling, not a claim
about any of the three harnesses this page researches -- it is
mentioned here only because the handoff note that prompted this page
named it explicitly as context, and it is worth being honest that this
book's own authoring process is closer to §2.1-§2.2's manual,
iterative evaluator-tuning loop than to §4's automated, assertion-backed
suite.

---

## Sources

All fetched or read fresh this session (2026-08-01) unless noted
otherwise.

**General agent-evaluation concepts (authoritative for framework-neutral
vocabulary and pedagogy, not for any specific harness):**
- `https://huggingface.co/learn/agents-course/bonus-unit2/monitoring-and-evaluating-agents-notebook`
  -- online vs. offline evaluation, traces, dataset-driven regression
  methodology, LLM-as-a-judge, the GAIA benchmark reference; covers §1
  in full.

**Claude Code (Anthropic's own engineering blogs are authoritative for
Anthropic's own stated practice and guidance; `code.claude.com/docs` is
authoritative for the Agent SDK/CLI's documented behavior; no
implementation source or test suite exists in
`github.com/anthropics/claude-code` to inspect directly):**
- `https://claude.com/blog/building-agents-with-the-claude-agent-sdk`
  -- representative-test-set/gate-on-evals guidance, the three
  verification methods (rules-based, visual, LLM-as-judge); covers §2.1
  in full.
- `https://www.anthropic.com/engineering/harness-design-long-running-apps`
  -- the evaluator-agent pattern, criteria-based grading rubrics, the
  sprint-contract concept, the harness-design-affects-capability-scores
  claim; covers §2.2 in full.
- `https://code.claude.com/docs/en/headless` -- `--bare` mode,
  `--output-format json`/`stream-json`, `--json-schema` validation and
  its v2.1.205 hardening, the `system/init` event's
  `plugin_errors`/`mcp_server_errors` CI-gating fields, the GitHub
  Actions/GitLab CI/CD pointers; covers §2.3 in full.
- `https://github.com/anthropics/claude-code` `CHANGELOG.md`, fetched
  via `gh api repos/anthropics/claude-code/contents/CHANGELOG.md` (full
  5,248-line file, grepped for `regression`) -- the dated,
  version-attributed regression-fix entries cited in §2.4.

**GitHub Copilot CLI (`docs.github.com/copilot` is authoritative for its
own documented behavior; no engineering-blog equivalent to Claude
Code's was found this session; no implementation source or test suite
exists in `github.com/github/copilot-cli` to inspect directly):**
- `https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference`
  -- `-p`/`-s` non-interactive mode, `--share`/`--share-gist`
  transcript export, the documented automation environment variables,
  and the confirmed absence of JSON-output documentation on this
  specific page; covers §3.1 in full.
- `https://github.com/github/copilot-cli` `changelog.md`, fetched via
  `gh api repos/github/copilot-cli/contents/changelog.md` (full
  2,898-line file, grepped for `regression`, `benchmark`, `test suite`,
  `non-interactive`, `headless`, `--output-format`, `programmatic`) --
  v0.0.422, v1.0.16, v1.0.33, and v1.0.69 entries cited in §3.2, and the
  dated regression-fix entries cited in §3.3.

**OpenCode (authoritative for its own documented behavior AND, unlike
the two harnesses above, its own real implementation and test source;
`dev` branch, not a stable release tag):**
- `https://github.com/anomalyco/opencode`, `dev` branch, located via
  `gh search code` and `gh api repos/anomalyco/opencode/git/trees/dev?recursive=true`
  (full repository file-tree listing) and read via `curl` against
  `raw.githubusercontent.com` this session -- full contents of
  `packages/http-recorder/README.md` (§4.1), `packages/llm/test/
  recorded-test.ts`, `packages/llm/test/recorded-utils.ts`,
  `packages/llm/test/recorded-runner.ts`, `packages/llm/test/
  recorded-golden.ts` (§4.1-§4.2), `packages/llm/test/provider/
  golden.recorded.test.ts` (full file) and the opening portion of
  `packages/llm/test/recorded-scenarios.ts` (§4.2), the full contents of
  `packages/llm/test/tool-stream.test.ts` (§4.3), the full contents of
  `packages/core/test/session-runner-tool-events.test.ts` (§4.4), the
  opening portion of `packages/core/test/session-runner-recorded.test.ts`
  (§4.5), the header comment and opening portion of `packages/opencode/
  test/server/httpapi-exercise/index.ts` and the opening portion of
  `packages/opencode/test/server/httpapi-exercise/dsl.ts` (§4.6), and
  the full contents of `.github/workflows/test.yml` (§4.7) -- covering
  §4 in full.

**pi (authoritative for its own documented behavior AND, like OpenCode
above, its own real implementation and test source; `main` branch;
package/repo naming cross-checked live from each package's own
`package.json` this session per §5.1):**
- `https://github.com/earendil-works/pi`, `main` branch, located via
  `gh api repos/earendil-works/pi/git/trees/main?recursive=true` (full
  repository file-tree listing, filtered for test/CI/eval paths) and
  individual files fetched via `gh api repos/earendil-works/pi/contents/
  <path>` this session -- the root `package.json` and the `package.json`
  for `packages/ai`, `packages/coding-agent`, `packages/agent`, and
  `packages/evals` (§5.1), the opening ~60 lines of `packages/ai/src/
  providers/faux.ts` and the full contents of `packages/coding-agent/
  test/suite/README.md` (§5.2), the opening lines of `packages/coding-
  agent/test/suite/regressions/7290-json-stream-linear.test.ts` and the
  opening ~30 lines of `packages/session-backends/sqlite-node/test/
  conformance.test.ts` (§5.3), the full contents of `packages/evals/
  README.md`, `packages/evals/src/pi-harness.ts`, and `packages/evals/
  src/smoke.eval.ts` (§5.4), the full contents of `.github/workflows/
  ci.yml` (§5.5), and the full contents of `test.sh` and `pi-test.sh`
  (§5.6) -- covering §5 in full. `gh search code` queries for `GAIA` and
  `SWE-bench` scoped to this repository, both returning no matches, are
  the source for §5's/§6's stated absence of third-party
  capability-benchmark integration.
