# Ollama: a model-registry, Modelfile, and REST layer over llama.cpp (and its own engine)

Where [llama-cpp.md](llama-cpp.md) is the low-level, direct-to-binary
engine, Ollama is the operator-facing product layer built on top of
that same GGUF ecosystem: a single installable application that adds
model naming and pulling, a declarative model-customisation format
(the Modelfile), a persistent local server with both a native and an
OpenAI-compatible REST API, and (as of its newer engine, §1) a path to
supporting model architectures beyond what a llama.cpp-only backend
covered. This page covers what is genuinely Ollama-specific; the
sampling parameters, context-length mechanics, GPU-offload behaviour,
and OpenAI-API shape it exposes are the same general concepts this
book's own dedicated pages already cover, cross-linked throughout
rather than re-explained here.

## 1. Relationship to llama.cpp: a dependency, not a fork, and now a dual-engine design

VERIFIED (`github.com/ollama/ollama`'s own top-level `README.md`,
fetched 2026-09-03): Ollama's own "Supported backends" section names
exactly one entry -- "[llama.cpp] project founded by Georgi Gerganov"
-- stating the dependency directly rather than leaving it to inference.
This confirms the relationship this book's framing assumed going in:
Ollama does not reimplement inference from scratch, it wraps
llama.cpp's own engine and adds the naming/registry/REST layers
described in §2-4.

That said, VERIFIED (Ollama's own blog post, "Ollama's new engine for
multimodal models," `ollama.com/blog/multimodal-models`, fetched
2026-09-03): this is no longer the *complete* picture as of Ollama's
newer architecture. The post states Ollama previously "depended
entirely on the llama.cpp project, which offered first-class support
for text-only models," but that multimodal models -- which split a
text decoder and a vision encoder into genuinely separate components
requiring model-specific orchestration -- outgrew what a single shared
llama.cpp-only integration path could support cleanly without
"patching multiple files or adding cascading if statements" for each
new architecture. Ollama's response was to build a **second, own
engine**, written in Go, that talks to the underlying `ggml` tensor
library *directly* rather than exclusively through llama.cpp's own
C/C++ layer -- the post's own framing: "being able to access GGML
directly from Go has given a portable way to design custom inference
graphs" for architectures the shared llama.cpp path did not already
support, with each such model shipping as a "fully self-contained"
module carrying its own projection layer. The fetched blog post does
not state outright whether llama.cpp remains the path for every
text-only model going forward or has been fully superseded for those
too -- held here as an explicit open question rather than assumed
either way, consistent with this book's GROUNDING DISCIPLINE. What is
VERIFIED is that both statements are true of Ollama today: it is
built on llama.cpp as a dependency (§1's first citation), and it has
also built its own direct-`ggml` engine specifically to cover
multimodal architectures that dependency alone did not serve well.

## 2. The Modelfile: a declarative model-build format

VERIFIED (`docs.ollama.com/modelfile.md`, fetched 2026-09-03): a
Modelfile is Ollama's own configuration-as-code format for defining a
named, distributable model configuration, using one-instruction-per-
line syntax:

- **`FROM`** (required) -- the base: an existing pulled model name, a
  Safetensors directory, or a GGUF file path (per
  [model-management-and-distribution.md](model-management-and-distribution.md)
  §2).
- **`PARAMETER`** -- sets sampling/runtime defaults for this model,
  using exactly the general decoding-parameter vocabulary this book's
  [sampling-and-decoding-parameters.md](sampling-and-decoding-parameters.md)
  §1 documents (`temperature`, `top_k`, `top_p`, `repeat_penalty`,
  `repeat_last_n`, `seed`, `num_predict`, `stop`) plus `num_ctx` (the
  context-window size, per
  [kv-cache-and-context-window-management.md](kv-cache-and-context-window-management.md)
  §2, default `2048`).
- **`TEMPLATE`** -- the prompt structure sent to the model, written in
  Go template syntax with variables such as `{{ .System }}`,
  `{{ .Prompt }}`, and `{{ .Response }}` -- Ollama's own equivalent of
  the Jinja2 chat templates llama.cpp's server consumes for tool-calling
  (per [sampling-and-decoding-parameters.md](sampling-and-decoding-parameters.md)
  §3), specific to this Modelfile authoring surface rather than the
  same template language.
- **`SYSTEM`** -- the default system message baked into this named
  model.
- **`ADAPTER`** -- applies a fine-tuned LoRA adapter (Safetensors or
  GGUF format) on top of the base model, without merging it into a new
  full-weight file.
- **`LICENSE`** -- attaches licensing text for redistribution.
- **`MESSAGE`** -- seeds few-shot example turns (system/user/assistant
  roles) directly into the model's own conversational prior, baked in
  at build time rather than repeated in every request.

`ollama create <name> -f ./Modelfile` compiles this definition into a
new, independently nameable local model; `ollama run <name>` then
starts a session against it, and `ollama show --modelfile <name>`
recovers the effective Modelfile for any already-built model
(including ones that started life as a plain pulled model with no
custom Modelfile of the operator's own).

## 3. GPU support and scheduling

VERIFIED (`docs.ollama.com/gpu.md`, fetched 2026-09-03): Ollama
documents support across a broader named vendor list than llama.cpp's
own backend table foregrounds -- NVIDIA (compute capability 5.0+,
requiring driver 550+, with compute 5.0-6.2 specifically requiring
driver 570+), AMD (Radeon RX/PRO, Ryzen AI, and Instinct series via
ROCm v7), Apple (Metal, for integrated GPUs), and Intel discrete GPUs
via Vulkan, plus a general "additional vendors ... through Vulkan on
Windows and Linux" catch-all. Multi-GPU selection is exposed through
environment variables rather than CLI flags -- `CUDA_VISIBLE_DEVICES`
(NVIDIA), `ROCR_VISIBLE_DEVICES` (AMD), and `GGML_VK_VISIBLE_DEVICES`
(Vulkan) -- and the documentation states directly that "the Ollama
scheduler leverages available VRAM data reported by the GPU libraries
to make optimal scheduling decisions," i.e. Ollama automates the
device-placement decision llama.cpp exposes as an explicit
`-ngl`/`--gpu-layers` flag (per
[cpu-gpu-heterogeneous-offloading.md](cpu-gpu-heterogeneous-offloading.md)
§1) rather than requiring the operator to size it by hand -- consistent
with §2's automated-by-VRAM framing of Ollama's context-length
defaults.

## 4. Dual API surfaces: native REST and OpenAI-compatible

VERIFIED (`docs.ollama.com`'s API documentation and
`github.com/ollama/ollama`'s `README.md`, both fetched 2026-09-03):
Ollama exposes a **native REST API** (`/api/generate`, `/api/chat`,
`/api/pull`, `/api/tags`, and related model-management endpoints
covered in
[model-management-and-distribution.md](model-management-and-distribution.md)
§2, served from `localhost:11434/api` by default, or
`ollama.com/api` for its hosted cloud variant) alongside first-party
`ollama-python` and `ollama-js` client libraries, and **separately**
the OpenAI-compatible surface
([server-api-modes.md](server-api-modes.md) §1 covers this in depth --
`/v1/chat/completions`, `/v1/completions`, `/v1/models`,
`/v1/embeddings`, plus a newer `/v1/responses` endpoint added in
version 0.13.3 supporting streaming and tool calling but not stateful
requests). The two surfaces are not aliases of each other with
different names -- they are genuinely separate endpoint families a
harness can choose between, and Ollama's own README explicitly
advertises direct integration with several named coding-agent
harnesses (Claude Code, Codex, Copilot CLI, DeepSeek Harness, Droid,
and OpenCode, each launchable via `ollama launch <name>`) -- a
first-party acknowledgement that agent-harness compatibility is a
named design goal of the product, not an incidental side effect of
its API shape.

## 5. Why an agent-harness builder specifically cares about Ollama

Relative to invoking llama.cpp directly, Ollama trades away some of
llama.cpp's raw configurability (its automated VRAM-based
scheduling and context-length defaults are conveniences a harness
operator cannot as directly override at the same granularity as
llama.cpp's own explicit `-ngl`/`--ctx-size` flags, short of the
documented environment-variable/Modelfile-parameter escape hatches) in
exchange for **operational simplicity that maps directly onto
harness-configuration concerns**: a Modelfile is a natural place to
pin an agent persona's exact sampling defaults, system prompt, and
chat template as one reviewable, versionable artifact
(`ollama show --modelfile` making that configuration inspectable after
the fact), and the named first-party harness integrations in §4 mean a
harness builder evaluating Ollama specifically for agentic use is
building on a path the vendor has already exercised, rather than an
unverified integration surface.

## Sources

- `github.com/ollama/ollama`, top-level `README.md` -- fetched
  2026-09-03. Authoritative for §1's "Supported backends: llama.cpp"
  statement and §4's coding-agent integration list
  (`ollama launch <name>`).
- `ollama.com/blog/multimodal-models`, "Ollama's new engine for
  multimodal models" -- fetched 2026-09-03. Authoritative for §1's
  new-engine rationale, the direct-`ggml`-access design, and the
  self-contained-per-model architecture, including the explicitly
  flagged open question about llama.cpp's remaining role for
  text-only models.
- `docs.ollama.com/modelfile.md` -- fetched 2026-09-03. Authoritative
  for §2's full Modelfile instruction set and the `ollama create`/
  `ollama show --modelfile` workflow.
- `docs.ollama.com/gpu.md` -- fetched 2026-09-03. Authoritative for
  §3's supported GPU vendor list, driver requirements, multi-GPU
  environment variables, and the VRAM-based scheduler statement.
- `docs.ollama.com`'s API documentation pages (`api/introduction.md`,
  `api/openai-compatibility.md`) and `github.com/ollama/ollama`'s
  `README.md` -- fetched 2026-09-03. Authoritative for §4's dual
  native/OpenAI-compatible API surface and the base-URL/port defaults.
