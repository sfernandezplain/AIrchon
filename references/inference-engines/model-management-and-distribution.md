# Model management and distribution: pulling, registries, and manifest-style model definitions

A model *file* -- a `.gguf`, per
[model-file-formats.md](model-file-formats.md) -- has to actually get
onto a machine before an engine can load it, and an operator running
more than a handful of models needs a way to name, version, and
configure them without hand-managing loose files. This is a genuinely
different layer from everything else in this book: it is about
*distribution and naming*, not about how inference itself executes.
The three engines this book covers sit at three different points on
this axis -- llama.cpp treats a model as "a file path (or a
Hugging-Face-hosted reference) you hand to a binary," Ollama builds a
full local registry-and-manifest system on top of that, and
KTransformers sits closer to llama.cpp's file-based end but adds its
own curated model registry for its `kt run` shortcut.

## 1. llama.cpp: direct file paths and Hugging Face references

VERIFIED (`ggml-org/llama.cpp`'s top-level `README.md`, fetched
2026-09-03): the project's own quick-start examples show both a local
file path and a direct Hugging-Face-hosted reference working
interchangeably against the same binaries -- `llama cli -hf
ggml-org/Qwen3.5-0.8B-GGUF` and `llama serve -hf
ggml-org/Qwen3.5-0.8B-GGUF` both resolve a `-hf` reference (a Hugging
Face repo identifier) directly, downloading the referenced GGUF file
on demand rather than requiring a separate, manual download step
first. There is no persistent local registry concept beyond this --
each invocation names a file or a Hugging Face reference explicitly,
and it is the operator's (or a wrapping harness's) own responsibility
to track which files/references correspond to which locally-cached
copies.

## 2. Ollama: names, manifests, and a Modelfile-based build layer

VERIFIED (`docs.ollama.com`'s API documentation pages, fetched
2026-09-03, and Ollama's own GitHub `README.md`, fetched the same
session): Ollama layers a full model-management system on top of the
same underlying GGUF files. A **model name** (e.g. `gemma4`, or a
user-namespaced `name/model:tag`) is the unit an operator interacts
with -- `ollama pull <name>` fetches it from Ollama's own model
registry (`ollama.com/library`) into local storage, `ollama run <name>`
pulls-if-needed and then starts an interactive session, `ollama list`/
`/api/tags` enumerates what is already pulled locally, `ollama show`
inspects a given model's resolved configuration (including its
effective Modelfile, via `ollama show --modelfile <name>`), and
`ollama rm`/`/api/delete` removes a local copy. A **Modelfile** (see
[ollama.md](ollama.md) §2 for its full instruction set) is Ollama's own
build-definition layer on top of this: it names a `FROM` base (an
existing pulled model name, a raw Safetensors directory, or a GGUF file
path), can layer on parameter defaults, a chat template, a system
prompt, LoRA adapters, and few-shot example messages, and `ollama
create <name> -f ./Modelfile` compiles that definition into a new,
independently-nameable local model -- conceptually close to how a
Dockerfile builds a named, distributable image on top of a base image,
which is also where the "manifest" framing comes from: each named
model Ollama manages resolves, under the hood, to a manifest describing
which underlying blob(s) (weights, template, parameters) that name
actually points to, letting several names share an unchanged
underlying weight blob rather than duplicating it on disk. VERIFIED
(`docs.ollama.com/import.md`, fetched 2026-09-03): a GGUF file that did
not originate from Ollama's own registry (a community re-quantization,
or a file the operator converted from Safetensors with llama.cpp's own
`convert_hf_to_gguf.py`) can be imported the same way, via a Modelfile
whose `FROM` line points at that file's local path -- Ollama's naming/
manifest layer is additive on top of llama.cpp's GGUF ecosystem, not a
separate, incompatible format of its own.

```mermaid
flowchart LR
    HF["Hugging Face repo<br/>(Safetensors or GGUF)"] -->|convert_hf_to_gguf.py<br/>(llama.cpp tooling)| GGUF["Local .gguf file"]
    REG["ollama.com/library<br/>(registry)"] -->|ollama pull| LOCAL["Locally pulled model<br/>(manifest + blobs)"]
    GGUF -->|Modelfile FROM ./file.gguf| CREATE["ollama create<br/>-> new named model"]
    LOCAL -->|Modelfile FROM base-name| CREATE
    CREATE --> RUN["ollama run / API request<br/>by name"]
```

## 3. KTransformers: a curated registry for its own launch shortcut

VERIFIED (`ktransformers.net`'s inference-overview documentation,
fetched 2026-09-03): the `kt run <model>` command resolves a model
name against KTransformers' own **built-in registry**, using
pre-configured defaults for that model (quantization method, expert-
placement strategy, and so on) so an operator does not need to hand-
author the full YAML operator-injection configuration for a model the
registry already knows about. The manual alternative -- invoking
`python -m sglang.launch_server` directly with explicit `--kt-*`
arguments -- is documented as the path for "scenarios requiring
explicit model paths, tensor parallelism configuration, or custom
serving parameters," i.e. for models or hardware configurations the
built-in registry does not already have a curated default for. This is
structurally closer to llama.cpp's direct-reference model (§1) than to
Ollama's full manifest/versioning system (§2): the registry's role is
narrower, supplying known-good defaults for a curated model list rather
than providing general-purpose local naming, tagging, and layered
model composition for arbitrary models.

## 4. Why an agent-harness builder cares

Model-management surface is the layer a harness's own configuration
and deployment tooling actually touches most often, and the three
engines' different designs push different responsibilities onto the
harness itself. Pointing a harness at llama.cpp (§1) means the
harness's own configuration must track file paths or Hugging Face
references directly -- reproducibility depends on the harness pinning
an exact reference or file hash itself. Pointing a harness at Ollama
(§2) means the harness can instead configure by a stable local name,
delegating version/file tracking to Ollama's own manifest system, and
can rely on a Modelfile to pin exactly which sampling defaults, system
prompt, and chat template that name resolves to -- valuable when a
harness wants a specific agent persona's model configuration to be
reproducible and inspectable (`ollama show --modelfile`) independently
of the harness's own code. Pointing a harness at KTransformers (§3) for
one of its curated large-MoE models means leaning on the registry's own
tuned defaults for exactly the hard, model-specific expert-placement
tuning [cpu-gpu-heterogeneous-offloading.md](cpu-gpu-heterogeneous-offloading.md)
§3 describes, while still retaining the manual `--kt-*` path as an
escape hatch for a harness deployment with atypical hardware or a model
the registry does not yet cover.

## Sources

- `ggml-org/llama.cpp`, top-level `README.md` -- fetched 2026-09-03.
  Source of the `-hf` Hugging-Face-reference quick-start pattern in §1.
- `docs.ollama.com`, API documentation pages (`api/pull.md`,
  `api/tags.md`, `api/delete.md`, `api/create.md`, `modelfile.md`) and
  `github.com/ollama/ollama` `README.md` -- fetched 2026-09-03.
  Authoritative for §2's pull/run/list/show/rm/create model-management
  surface and the Modelfile-as-build-layer framing.
- `docs.ollama.com/import.md` -- fetched 2026-09-03. Source of §2's
  GGUF-import path and its explicit naming of llama.cpp's
  `convert_hf_to_gguf.py` as an acquisition route for GGUF files
  Ollama did not itself produce.
- `ktransformers.net`, inference-overview and installation
  documentation pages -- fetched 2026-09-03. Authoritative for §3's
  `kt run` built-in registry and the manual `sglang.launch_server
  --kt-*` alternative path.
