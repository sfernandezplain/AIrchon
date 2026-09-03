# Quantization as an inference-engine-level concern

[`references/models/quantization.md`](../models/quantization.md)
covers quantization as a *scheme* -- what affine and symmetric mappings
are, how calibration works, why per-tensor vs. per-channel granularity
trades accuracy for overhead, and the concrete VRAM/speed/accuracy
tradeoffs of running a model at `int8` or `int4` rather than `bf16`.
This page does not re-derive any of that; it covers the narrower,
engine-specific question that sits one layer down from it: **given a
model whose weights are already quantized, what does the inference
engine that loads and runs it actually have to do differently from
running a full-precision model?**

## 1. The engine consumes, it does not (usually) decide, the scheme

For all three concrete engines this book covers, quantization is
almost always something that happened *before* the engine ever sees
the model file, not a step the serving engine performs live. A GGUF
file, per [model-file-formats.md](model-file-formats.md) §4, already
declares each tensor's stored type from `ggml`'s type enumeration
(`F16`, `Q4_K_M`, `Q8_0`, and so on) -- the engine's job at load time is
to read that declared type off the tensor-info section and dispatch to
the matching dequantization/compute kernel, not to choose or compute a
quantization scheme itself. The actual *production* of a quantized
GGUF file is a separate, offline conversion step (llama.cpp's own
`convert_hf_to_gguf.py` plus its `quantize` tool, covered as
engine-specific detail on [llama-cpp.md](llama-cpp.md) §3) that a model
publisher or a community "quantizer" runs once, upstream of any
inference engine ever loading the result. KTransformers is a partial
exception worth flagging explicitly: because it targets very large MoE
checkpoints that arrive from their publisher already in a specific
low-precision format (e.g. DeepSeek's own native FP8 release weights),
part of its own tooling exists to *convert between* precision/backend
weight layouts (e.g. into its AMX-optimized `AMXINT4`/`AMXINT8` layouts)
rather than only to consume an already-community-quantized file -- see
[ktransformers.md](ktransformers.md) §3 for that engine-specific detail.

## 2. Dequantize-at-compute-time, not decompress-then-run

VERIFIED (Hugging Face Optimum's quantization guide, as cited on
[`references/models/quantization.md`](../models/quantization.md) §6,
fetched 2026-09-03 in that book): a quantized model does not run its
matrix multiplications in the quantized dtype end-to-end and does not
get "unpacked" into a full-precision copy before inference begins
either. Instead, the guide describes the actual runtime sequence as
"quantize all weights to the target precision; load the quantized
weights... pass the input sequence... in [higher] precision;
dynamically dequantize weights to [higher precision] to perform the
computation" -- dequantization happens **inline, per weight block, at
the moment that block is needed for a matmul**, not as a one-time
unpacking pass at load time. This is the direct explanation for a
counter-intuitive fact the same guide states plainly: "inference time
is often *not* reduced when using quantized weights, but rather
increases" relative to running the same operation at full precision --
the memory-bandwidth savings of moving fewer bytes off disk and out of
VRAM are real and substantial, but the dequantization arithmetic itself
adds compute overhead per weight block that a full-precision run never
pays at all. An inference engine's quantization support is therefore
really "a set of fused dequantize-and-multiply kernels for each
supported storage type," not merely "the ability to read a smaller
file."

## 3. Mixed-precision tensors within one loaded model

Because GGUF (§1 above, and [model-file-formats.md](model-file-formats.md)
§4) declares a type *per tensor* rather than one type for the whole
file, an engine loading a GGUF model routinely runs several different
dequantization kernels within a single forward pass: embedding and
output-projection tensors are commonly left at a higher precision
(`F16` or `Q8_0`) while the bulk of the feed-forward and attention
weight tensors are quantized more aggressively (`Q4_K_M` and similar).
An engine's quantization support surface is therefore not "does it
support quantization" as a single yes/no, but "which of the type
enum's ~40 values does its kernel set actually implement" -- llama.cpp's
own naming convention for that type space (the `K`-quant vs. `I`-quant
families, and what the `_S`/`_M`/`_L`/`_XS`/`_XXS` suffixes mean) is
engine-specific detail covered on [llama-cpp.md](llama-cpp.md) §3
rather than re-derived here, since it is llama.cpp's own naming
scheme rather than a property of quantization as a general concept.

## 4. Runtime knobs an engine exposes around a fixed weight quantization

Even though the weight quantization itself is fixed at load time by
the file, engines still expose runtime choices that interact with it:

- **KV-cache quantization** is a separate, independent precision
  choice from weight quantization -- see
  [kv-cache-and-context-window-management.md](kv-cache-and-context-window-management.md)
  for llama.cpp's `--cache-type-k`/`--cache-type-v` flags, which can
  store the *activations* generated during a session (the KV cache) at
  a lower precision than the weights themselves, trading a further
  slice of accuracy for a further reduction in the memory that grows
  with context length rather than with model size.
- **GPU-layer offloading decisions** (see
  [cpu-gpu-heterogeneous-offloading.md](cpu-gpu-heterogeneous-offloading.md))
  are made per already-quantized tensor -- the engine decides *where*
  a given quantized tensor's dequantize-and-multiply kernel runs (CPU
  vs. GPU), not whether to requantize it differently for one device
  versus another.

## 5. Why an agent-harness builder cares

For a harness operator choosing which community GGUF re-quantization
of a base model to actually deploy, the practical decision this page's
findings feed into is exactly the synthesis
[`references/models/quantization.md`](../models/quantization.md) §7
already lays out at the scheme level (prefer `int8`-class quantization
when the accuracy margin matters and the extra VRAM is affordable;
prefer `int4`-class quantization when fitting on the smallest available
accelerator is the binding constraint) -- with one inference-engine-
specific addition from §2 above: because dequantization is a genuine
per-token compute cost, not a one-time unpacking cost, a harness
running a **high call-volume, low-latency-budget** workload (e.g. many
short tool-routing calls fired in a fast agent loop) should benchmark
actual generation speed at the target quantization level rather than
assuming "smaller file" and "faster inference" are the same claim --
the octocoder VRAM/speed measurements on the models book's own
quantization page show the memory win is close to guaranteed while the
latency effect can go either direction depending on hardware and batch
size.

## Sources

- [`references/models/quantization.md`](../models/quantization.md),
  this project's existing quantization reference (Hugging Face Optimum
  quantization concept guide and `transformers` docs, both fetched
  2026-09-03 in that book) -- authoritative for every scheme-level
  claim this page builds on (§2's dequantize-at-compute-time behaviour,
  §5's accuracy/VRAM/speed synthesis) rather than re-fetched
  independently here.
- [model-file-formats.md](model-file-formats.md) §4, this book's own
  page, for the GGUF per-tensor type declaration and the `ggml` type
  enumeration §1 and §3 above build on.
- §1's characterisation of quantization as normally an offline,
  pre-serving step (as opposed to something the serving engine itself
  performs) is BEST CURRENT UNDERSTANDING, UNCONFIRMED as a general
  claim about inference engines -- it follows from how GGUF's own
  format is structured (a fixed declared type per tensor, read at load
  time) rather than from an explicit statement to that effect in any
  of the three source documents, with the KTransformers weight-layout-
  conversion tooling flagged as a partial, sourced exception (see
  [ktransformers.md](ktransformers.md) §3).
