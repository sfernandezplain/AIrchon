# Server/API modes: why an OpenAI-compatible surface matters to a harness

The engines in this book can be used two structurally different ways:
as a **one-shot CLI invocation** that loads the model, runs a single
prompt to completion, and exits (paying the full model-load cost --
mitigated but not eliminated by
[memory-mapped-model-loading.md](memory-mapped-model-loading.md) --
on every single call), or as a **persistent server process** that
loads the model once and then answers many independent requests over
HTTP for as long as it stays running, gaining
[batching-and-continuous-batching.md](batching-and-continuous-batching.md)'s
throughput benefits across whatever concurrent load actually arrives.
Every engine this book covers ships a server mode, and all three
converge on exposing at least part of that server's surface as an
**OpenAI-compatible REST API** -- the same request/response shape
`api.openai.com/v1/chat/completions` popularised -- rather than each
inventing its own bespoke protocol.

## 1. What "OpenAI-compatible" concretely means

VERIFIED (`docs.ollama.com/api/openai-compatibility.md`, fetched
2026-09-03, describing Ollama's own implementation of this shared
surface): the compatible endpoint set generally covers **chat
completions** (`/v1/chat/completions` -- streaming, JSON mode, vision
input, and tool/function calling), **completions**
(`/v1/completions` -- older, non-chat text-continuation shape),
**models** (`/v1/models` and `/v1/models/{model}` -- listing and
describing what is currently available to call), and **embeddings**
(`/v1/embeddings`). Compatibility is rarely total: Ollama's own
documentation names concrete gaps -- `logprobs` is "not yet supported"
on chat completions, the completions endpoint "currently accepts only
string prompts rather than token arrays," vision input is "limited to
base64-encoded images, not direct URLs," and `logit_bias`,
`tool_choice`, and `user` "remain unsupported across endpoints." The
practical implication for a harness: pointing an existing
OpenAI-SDK-based integration at a local engine's base URL (Ollama's
own documented pattern: `base_url='http://localhost:11434/v1/'` with
any placeholder API key, since one is "required but ignored" by the
client library) works as a drop-in swap for the *common* request
shapes a harness is likely to already be using, but a harness that
depends on one of the specific unsupported fields needs to check the
serving engine's own compatibility notes rather than assume full
parity, since "OpenAI-compatible" is a documented-per-engine subset
claim, not a formal, versioned specification either engine commits to
matching completely.

## 2. llama-server's own native implementation

VERIFIED (`ggml-org/llama.cpp`'s `tools/server/README.md`, fetched
2026-09-03): llama-server implements this same endpoint family
natively in C/C++ -- `/v1/chat/completions` (with streaming, function
calling, and tool use), `/v1/completions` (with multimodal input
support), and `/v1/embeddings` (normalised embeddings) -- as a single
lightweight HTTP server binary with no separate runtime dependency,
serving from `127.0.0.1:8080` by default alongside a built-in web
chat interface. Because llama-server is the same binary this book's
other pages describe for continuous batching, KV-cache management, and
offloading, all of those mechanisms operate transparently underneath
whichever API surface (native or OpenAI-compatible) a given request
arrives through -- the API layer is a request/response translation on
top of the same underlying engine, not a separate code path with its
own performance characteristics.

## 3. Why an OpenAI-shaped API is the load-bearing compatibility layer for agent harnesses

Most agent-harness tooling -- SDKs, framework integrations, and the
harnesses this project's own `references/harnesses/` book documents --
was built against, or at minimum offers, an OpenAI-Chat-Completions-
shaped client as its lowest common denominator for talking to *any*
model provider. An inference engine that speaks that same shape at its
HTTP boundary can be swapped in for a hosted API with a base-URL and
API-key change alone, with zero harness-side code change, which is
precisely why all three engines in this book converge on offering it
even though each has, or could have, its own bespoke native protocol
instead (Ollama's own `/api/chat`, `/api/generate`, and related
endpoints, per [ollama.md](ollama.md) §4, remain available
*alongside* its OpenAI-compatible surface, not replaced by it). The
tool-calling half of that compatibility is specifically the grammar-
constrained-decoding mechanism covered on
[sampling-and-decoding-parameters.md](sampling-and-decoding-parameters.md)
§3: an OpenAI-shaped `tools` array in the request only reliably
produces a parseable `tool_calls` response if the serving engine backs
that request shape with an actual enforcement mechanism, not merely
with a chat template that *asks* the model nicely to emit JSON.

## 4. Why concurrency-aware serving matters more than the API shape alone

A harness evaluating "can I point my existing OpenAI-client-based
tool-calling code at a local engine and expect it to behave the way my
hosted-API integration does" needs to separate two different questions
this book keeps structurally apart: whether the *request/response
shape* matches (this page, and each engine's own compatibility-gap
list per §1), and whether the *serving behaviour under concurrent load*
matches (continuous batching, per
[batching-and-continuous-batching.md](batching-and-continuous-batching.md)).
A single-shot CLI invocation can technically be wrapped in an
ad-hoc HTTP handler to *look* OpenAI-compatible at the shape level
while still serializing every concurrent request behind a single
model-load-and-run cycle -- the genuine multi-agent throughput benefit
a harness is usually really after only materialises once the engine's
own persistent server mode, with its own continuous-batching design,
is what is actually answering the requests.

## Sources

- `docs.ollama.com/api/openai-compatibility.md` -- fetched 2026-09-03.
  Authoritative for §1: the supported OpenAI-compatible endpoint set,
  the documented feature gaps (logprobs, token-array prompts,
  image-URL vision input, `logit_bias`/`tool_choice`/`user`), and the
  base-URL/placeholder-API-key connection pattern.
- `ggml-org/llama.cpp`, `tools/server/README.md` -- fetched
  2026-09-03. Authoritative for §2: llama-server's native
  OpenAI-compatible endpoint implementation, default bind address, and
  built-in web UI.
- [sampling-and-decoding-parameters.md](sampling-and-decoding-parameters.md)
  §3, this book's own page, for the grammar-constrained-decoding
  mechanism §3 above cross-links as the actual enforcement layer behind
  OpenAI-shaped tool-calling requests.
