# Local/self-hosted inference engines wiki-book -- index

A prose-navigable reference on how **local, self-hosted LLM inference
engines** actually work -- built as a sibling to `references/harnesses/`,
`references/models/`, `references/rag/`, and `references/sdlc/`,
specifically in the context of **agentic AI development**: what an
agent-harness builder running a model on their own hardware, rather
than against a hosted API, needs to understand about how that model
actually gets loaded, quantized, cached, batched, offloaded, and
served. Every claim in every page is tagged VERIFIED (fetched from a
named, authoritative source this session) or BEST CURRENT
UNDERSTANDING, UNCONFIRMED -- never blended. See each page's own
"Sources" section for what was actually checked and when.

`airchon-author` is the writer for this area; `airchon-mentor` and
`airchon-teacher` read it. Written for three named source engines --
`llama.cpp`, Ollama, and KTransformers -- fetched directly this
session (2026-09-03), following linked documentation pages and, where
a docs site itself was thin, the underlying project repository's own
documentation, rather than written from prior knowledge alone.

## Organizing principle: concepts before implementations

This book mirrors how `references/harnesses/` separates general
harness-engineering concepts from per-harness specifics, and how
`references/models/` separates classification axes from any one
model's own card. It is split into two bands, in this order:

1. **General, engine-agnostic concepts** (below) -- the mechanisms all
   three engines instantiate in their own way: how a model file is
   structured and loaded, how its weights are consumed at a fixed
   precision, how generation state is cached and grown, how sampling
   actually picks tokens, how concurrent requests share one loaded
   model, how work is placed across CPU/GPU/multiple GPUs, how
   generation speed can be accelerated speculatively, and how all of
   this is packaged behind a servable API and a distributable model
   name.
2. **Per-engine implementation pages** (further below) -- what each of
   llama.cpp, Ollama, and KTransformers actually does with those
   concepts, covering only what is genuinely engine-specific (naming
   schemes, CLI surfaces, architectural relationships to each other)
   rather than re-deriving the shared mechanism a second time.

Where a general concept in this book depends on model-classification
concepts this project already covers elsewhere, the relevant page
cross-links to [`references/models/`](../models/index.md) directly
(most often [`quantization.md`](../models/quantization.md) and
[`mixture-of-experts-and-frankenmerging.md`](../models/mixture-of-experts-and-frankenmerging.md))
rather than re-deriving those concepts here.

## Primary sources

- **llama.cpp** -- `github.com/ggml-org/llama.cpp` (its top-level
  README, and linked `tools/`/`docs/`/`grammars/` documentation pages)
- **Ollama** -- `docs.ollama.com` (its documentation site, and
  `github.com/ollama/ollama`'s own top-level README and blog for
  detail the docs site did not itself carry)
- **KTransformers** -- `ktransformers.net/docs` (its current
  documentation site) and, where that site's current architecture
  description did not cover the underlying operator-injection
  mechanism, the upstream `kvcache-ai/ktransformers` project
  repository's own tutorial documentation

A fourth, already-existing project area,
[`references/models/`](../models/index.md) (Hugging Face Hub/
`transformers`/Optimum documentation and Maxime Labonne's frankenMoE
article), is a load-bearing prerequisite for two of this book's own
pages (quantization and MoE/expert-offloading) rather than a source
independently re-fetched here.

## Pages: general concepts (foundational -> advanced)

1. [Model file formats for inference: GGUF and why a purpose-built format exists](model-file-formats.md) --
   why a training-checkpoint format (Safetensors/`config.json`) and an
   inference-serving format solve different problems; GGUF's
   predecessors (GGML/GGMF/GGJT) and the "no way to identify which
   architecture, and no way to detect a breaking hyperparameter
   change" failure they had; GGUF's four-section layout (header,
   typed/namespaced metadata KV pairs, tensor infos, tensor data); its
   per-tensor `ggml` type enumeration (how a single file mixes
   precisions across tensors); and why this all matters for a harness
   treating "swap the local model" as a cheap operation.
2. [Memory-mapped model loading](memory-mapped-model-loading.md) --
   why `mmap`-based loading trades a full-file copy for lazy,
   page-cache-backed loading; GGUF's alignment requirement as the
   structural precondition that makes it possible; llama.cpp's
   `--load-mode` surface (`auto`/`mmap`/`mlock`/`mmap+mlock`/`dio`) and
   the load-speed-vs-pageout-risk tradeoff each mode makes; and why
   this favours a harness that swaps or restarts local models
   frequently.
3. [Quantization as an inference-engine-level concern](quantization-at-inference-time.md) --
   how an engine *consumes* (rather than produces) an already-quantized
   tensor, cross-linking
   [`references/models/quantization.md`](../models/quantization.md)
   for the underlying scheme; why dequantization happens inline, per
   weight block, at compute time rather than once at load time (and
   why that means quantized inference is not automatically *faster*,
   only smaller); GGUF's mixed-per-tensor-precision consequence; and
   the runtime knobs (KV-cache quantization, offload placement) that
   compose with a fixed weight quantization.
4. [The KV cache and context-window management during generation](kv-cache-and-context-window-management.md) --
   why the KV cache exists and why its cost scales with context length
   rather than model size; context-window sizing as an explicit,
   VRAM-aware setting (llama.cpp's `--ctx-size`, Ollama's
   VRAM-tiered automatic defaults and `OLLAMA_CONTEXT_LENGTH`,
   including Ollama's own documented call-out of agentic workloads
   needing a larger-than-default window); KV-cache quantization
   (`--cache-type-k`/`-v`) as a precision axis independent of weight
   quantization; and why this is the direct link into per-session
   memory planning for a long-running agent loop.
5. [Sampling and decoding parameters](sampling-and-decoding-parameters.md) --
   the shared core parameter set (`temperature`, `top_k`, `top_p`,
   `repeat_penalty`/`repeat_last_n`, `seed`, `num_predict`, `stop`);
   grammar-constrained decoding (GBNF) as a fundamentally different,
   token-masking mechanism rather than a reweighting one, and its
   automatic JSON-Schema-to-grammar conversion; and why this exact
   mechanism, not the chat template alone, is what makes an
   OpenAI-shaped `tools` array reliably yield parseable `tool_calls`.
6. [Batching and continuous batching of concurrent requests](batching-and-continuous-batching.md) --
   why memory-bandwidth-bound single-token decoding makes batching
   valuable; llama-server's slot-based continuous-batching design
   (`--parallel`/`--batch-size`/`--ubatch-size`) and why it, not a
   static batch, is what actually captures that benefit under real,
   staggered request arrival; and why this is the mechanism that
   decides whether a multi-agent fan-out pattern against one shared
   local model gets real throughput or serializes behind a queue.
7. [CPU/GPU/heterogeneous offloading, and expert offloading for MoE models](cpu-gpu-heterogeneous-offloading.md) --
   llama.cpp's layer-granularity `--gpu-layers`/`--device` hybrid
   inference as the general-purpose default; why that granularity
   cannot avoid holding every MoE expert in memory at once, per
   [`references/models/mixture-of-experts-and-frankenmerging.md`](../models/mixture-of-experts-and-frankenmerging.md);
   and KTransformers' "arithmetic intensity guided offloading" (the
   ~512-vs-~0.075 MLA-vs-expert figures) as the finer-than-layer
   strategy that makes a 671B-parameter MoE model locally deployable
   at all.
8. [Multi-GPU inference: pipeline (layer) parallelism vs. tensor parallelism](multi-gpu-and-tensor-parallelism.md) --
   llama.cpp's `--split-mode layer` (throughput-oriented, tolerant of
   slow interconnects) vs. `--split-mode tensor` (experimental,
   latency-oriented, needs a fast interconnect) and the
   `--tensor-split`/`--main-gpu` configuration surface; how this
   composes with, rather than replaces, KTransformers' own
   CPU/GPU expert-placement strategy; and which mode maps to a
   throughput-seeking multi-agent harness versus a single
   latency-critical interactive loop.
9. [Speculative decoding](speculative-decoding.md) --
   the draft-then-verify-in-one-batch mechanism as a pure latency
   optimisation with no output-distribution change; llama.cpp's
   model-based (draft model, EAGLE-3, DFlash, DSpark) and
   pattern-based (n-gram family) drafter taxonomy; why payoff is
   entirely acceptance-rate-dependent; and the two agent-harness
   workload shapes (context-echoing generation; an already-resident
   small model repurposed as a draft model) that line up well with it.
10. [Server/API modes: why an OpenAI-compatible surface matters to a harness](server-api-modes.md) --
    one-shot CLI invocation vs. a persistent server process; what
    "OpenAI-compatible" concretely covers and where each engine's own
    compatibility gaps are documented; llama-server's native
    implementation of the same endpoint family; and why concurrency-
    aware serving (§6 above), not the API shape alone, is what actually
    delivers the throughput a harness integration is really after.
11. [Model management and distribution: pulling, registries, and manifest-style model definitions](model-management-and-distribution.md) --
    llama.cpp's direct-file-path/Hugging-Face-reference model
    (`-hf`); Ollama's full name/manifest/Modelfile-build layer on top
    of the same GGUF ecosystem (`pull`/`create`/`show`/`rm`, and
    Modelfile-as-Dockerfile-analogue); KTransformers' curated
    registry for its `kt run` shortcut; and which of the three
    responsibility splits best fits a harness that needs reproducible,
    inspectable per-persona model configuration.

## Pages: per-engine implementations

12. [llama.cpp: the foundational C/C++ inference engine](llama-cpp.md) --
    project goals and hardware-backend breadth (Apple Silicon, x86,
    RISC-V, CUDA/HIP/MUSA/Vulkan/SYCL and more); the `llama cli`/
    `llama serve` binaries; the K-quant/I-quant GGUF quantization-type
    naming families and the `Q4_K_M` default recommendation;
    Ollama's own documented dependency on llama.cpp as its backend;
    and why a harness choosing llama.cpp directly is trading Ollama's
    convenience for hardware breadth and first-party access to every
    mechanism this book's general-concept pages describe.
13. [Ollama: a model-registry, Modelfile, and REST layer over llama.cpp (and its own engine)](ollama.md) --
    the confirmed llama.cpp dependency, held alongside Ollama's newer,
    directly-`ggml`-based Go engine built specifically for multimodal
    architectures llama.cpp's original text-only-first-class path did
    not cover as cleanly; the full Modelfile instruction set; documented
    GPU-vendor support and VRAM-based automatic scheduling; the dual
    native-REST and OpenAI-compatible API surfaces; and Ollama's own
    first-party integrations with named coding-agent harnesses
    (Claude Code, Codex, Copilot CLI, OpenCode, and others).
14. [KTransformers: heterogeneous CPU/GPU inference for large MoE models](ktransformers.md) --
    what the project is today (`kt-kernel`/`sglang-kt` serving,
    LLaMA-Factory-integrated LoRA fine-tuning), held explicitly apart
    from its upstream repository's own documented YAML operator-
    injection mechanism (`match`/`replace` rules, `optimize_and_load_gguf`,
    `generate_device`/`prefill_device` placement) that the current
    serving stack builds on top of; its own architecture-coupled
    precision/backend naming (`BF16`/`FP8`/`AMXINT4`/`AMXINT8`/`MXFP4`
    and more); its curated large-MoE model list (DeepSeek, Kimi,
    MiniMax, Qwen, GLM, up to DeepSeek R1's 671B parameters); and why
    it is the answer for a harness builder who specifically wants a
    frontier-scale, tool-competent open-weight model running on local
    hardware rather than a hosted API or a smaller dense model chosen
    to fit available VRAM.
