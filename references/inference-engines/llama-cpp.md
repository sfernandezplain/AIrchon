# llama.cpp: the foundational C/C++ inference engine

llama.cpp is the engine underneath, or adjacent to, both of this
book's other two concrete engines: Ollama builds a naming/registry/
Modelfile layer on top of it (§4 below, and
[ollama.md](ollama.md) §1), and KTransformers, while an
architecturally distinct heterogeneous-inference framework in its own
right (see [ktransformers.md](ktransformers.md)), targets the same
GGUF ecosystem llama.cpp originated. This page covers what is
genuinely specific to llama.cpp itself -- its quantization type naming,
its CLI/server binaries, and its own hardware-backend surface --
rather than re-explaining the general concepts (GGUF, mmap, KV cache,
batching, offloading, speculative decoding, grammars, OpenAI-compatible
serving) this book's own general-concept pages already cover in depth
and that llama.cpp is, in every case, the primary source grounding
those pages.

## 1. What it is and its design goals

VERIFIED (`ggml-org/llama.cpp`'s top-level `README.md`, fetched
2026-09-03): the project's own stated goal is "to enable LLM (and VLM)
inference with minimal setup and state-of-the-art performance on a
wide range of hardware -- locally and in the cloud." It is "a plain
C/C++ implementation without any dependencies," built on top of the
[`ggml`](https://github.com/ggml-org/ggml) tensor library, which is the
same library whose GGUF specification this book's own
[model-file-formats.md](model-file-formats.md) documents in depth.
Portability is a first-class design goal rather than an afterthought:
Apple Silicon is called out as "a first-class citizen" (ARM NEON,
Accelerate, and Metal), x86 gets AVX/AVX2/AVX512/AMX support, and
RISC-V gets RVV/ZVFH/ZFH/ZICBOP/ZIHINTPAUSE extension support --
alongside GPU acceleration via custom CUDA kernels (NVIDIA), HIP (AMD),
and MUSA (Moore Threads). The README's own backend table (fetched the
same session) lists over a dozen supported backends beyond these,
including Vulkan, SYCL, WebGPU, OpenCL, Ascend NPU (CANN), IBM zDNN,
and Snapdragon Hexagon (marked in-progress) -- a breadth of hardware
targets that is itself llama.cpp's defining project characteristic
relative to a GPU-cluster-oriented serving engine.

## 2. Binaries: `llama cli` and `llama serve`

VERIFIED (same source, plus `tools/cli/README.md` and
`tools/server/README.md`, both fetched 2026-09-03): the project ships
two primary user-facing binaries. `llama cli` (documented as `llama
cli -hf <repo>` in the README's own quick-start, resolving a Hugging
Face model reference directly, per
[model-management-and-distribution.md](model-management-and-distribution.md)
§1) runs a single interactive or scripted session against a loaded
model. `llama serve` (equivalently `llama-server`) launches the
persistent HTTP server this book's
[server-api-modes.md](server-api-modes.md) §2 and
[batching-and-continuous-batching.md](batching-and-continuous-batching.md)
§1 document -- OpenAI-compatible `/v1/chat/completions`,
`/v1/completions`, and `/v1/embeddings` endpoints, a built-in web chat
UI, and slot-based continuous batching, bound to `127.0.0.1:8080` by
default. A `docs/completions.md` and a dedicated GBNF-grammar
directory (`grammars/README.md`) round out the documented tooling
surface, alongside the quantization tool covered in §3 below.

## 3. GGUF quantization type naming: K-quants and I-quants

VERIFIED (`ggml-org/llama.cpp`'s `tools/quantize/README.md` and the
`ggml-org/ggml` GGUF specification, both fetched 2026-09-03): llama.cpp
defines the actual quantization *type names* that GGUF's tensor-info
section (per [model-file-formats.md](model-file-formats.md) §4)
references, organised into two families beyond the plain legacy types
(`Q8_0`, `Q4_0`, `Q4_1`, `Q5_0`, `Q5_1`, and full-precision `F16`/
`F32`/`BF16`):

- **K-quants** (`Q2_K`, `Q3_K_S`/`Q3_K_M`/`Q3_K_L`, `Q4_K_S`/`Q4_K_M`,
  `Q5_K_S`/`Q5_K_M`, `Q6_K`) -- the leading digit is the approximate
  bits-per-weight, `K` marks the "k-quant" block-wise scheme, and the
  `S`/`M`/`L` suffix (small/medium/large) selects among size/quality
  variants at that same bit-width -- more of the tensor's blocks get
  the higher-precision treatment as the suffix moves from `S` toward
  `L`, trading file size for accuracy.
- **I-quants** (`IQ1_S`/`IQ1_M`, `IQ2_XXS`/`IQ2_XS`/`IQ2_S`/`IQ2_M`,
  `IQ3_XXS`/`IQ3_XS`/`IQ3_S`/`IQ3_M`, `IQ4_XS`/`IQ4_NL`) -- "importance-
  based" quantization types, generally used at the more aggressive,
  sub-4-bit end of the range, with an analogous `XXS`/`XS`/`S`/`M`
  size-variant suffix pattern.

The documentation's own practical guidance names **`Q4_K_M`** as the
suggested default -- the balance point between size reduction and
retained inference speed/quality most users should reach for absent a
specific reason to go lower (VRAM-constrained, and willing to trade
more accuracy for it) or higher (accuracy-sensitive, with VRAM to
spare). This naming scheme is llama.cpp's own, engine-specific
vocabulary for the general quantization-consumption concern
[quantization-at-inference-time.md](quantization-at-inference-time.md)
covers, and for the underlying scheme concepts (affine/symmetric
mappings, calibration) documented in depth on this project's sibling
page, [`references/models/quantization.md`](../models/quantization.md).

## 4. Ollama's relationship to llama.cpp

VERIFIED (`github.com/ollama/ollama`'s own top-level `README.md`,
fetched 2026-09-03): Ollama's README lists its "Supported backends"
section as a single named entry -- "[llama.cpp] project founded by
Georgi Gerganov" -- stated as a direct dependency relationship, not
merely an ecosystem similarity. Ollama's own documentation separately
names `convert_hf_to_gguf.py` (llama.cpp's own conversion script) as
an acquisition path for GGUF files an operator wants to import (per
[model-management-and-distribution.md](model-management-and-distribution.md)
§2), confirming the GGUF files each engine consumes are the same
artifact type, produced by the same tooling lineage. This relationship
is not exclusive on Ollama's side, however -- see
[ollama.md](ollama.md) §1 for Ollama's own newer, directly-`ggml`-based
engine built for multimodal model families llama.cpp's own model
support did not originally cover as a single, self-contained module
per model.

## 5. Why an agent-harness builder specifically cares about llama.cpp

A harness builder who chooses to run llama.cpp directly, rather than
through Ollama's higher-level naming/registry layer, is trading
Ollama's convenience for llama.cpp's own two comparative strengths:
**breadth of hardware backend support** (§1's dozen-plus backend list,
directly relevant to a harness that must run on hardware Ollama's own
GPU-vendor list does not name, per [ollama.md](ollama.md) §3) and
**direct, first-party access to every mechanism this book's
general-concept pages describe** -- multi-GPU tensor/pipeline
parallelism (`--split-mode`, per
[multi-gpu-and-tensor-parallelism.md](multi-gpu-and-tensor-parallelism.md)),
speculative decoding (`--spec-type` and its draft-model family, per
[speculative-decoding.md](speculative-decoding.md)), and grammar-
constrained tool calling (`--jinja` plus GBNF/JSON-Schema constraints,
per [sampling-and-decoding-parameters.md](sampling-and-decoding-parameters.md)
§2-3) -- all exposed as direct CLI/server flags on the same binary a
harness is already invoking, with no intermediate layer's own feature
lag or translation gap to account for.

## Sources

- `ggml-org/llama.cpp`, top-level `README.md` -- fetched 2026-09-03.
  Authoritative for §1 (project goals, portability, backend table) and
  §2 (the `llama cli`/`llama serve` binaries and quick-start commands).
- `ggml-org/llama.cpp`, `tools/cli/README.md` and `tools/server/README.md`
  -- both fetched 2026-09-03. Authoritative for §2's binary-level
  detail, cross-referenced in depth on this book's own
  [memory-mapped-model-loading.md](memory-mapped-model-loading.md),
  [kv-cache-and-context-window-management.md](kv-cache-and-context-window-management.md),
  and [server-api-modes.md](server-api-modes.md) pages.
- `ggml-org/llama.cpp`, `tools/quantize/README.md` -- fetched
  2026-09-03. Authoritative for §3's K-quant/I-quant naming families
  and the `Q4_K_M` default recommendation.
- `ggml-org/ggml`, GGUF file format specification -- fetched
  2026-09-03. Cross-referenced for §3's GGML type enumeration, detailed
  in full on [model-file-formats.md](model-file-formats.md) §4.
- `github.com/ollama/ollama`, top-level `README.md` -- fetched
  2026-09-03. Authoritative for §4's direct "Supported backends:
  llama.cpp" statement.
