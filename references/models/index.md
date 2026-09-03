# Model classification wiki-book -- index

A prose-navigable reference on how AI models are classified and what
each classification means, specifically in the context of **agentic AI
development** -- built as a sibling to `references/harnesses/`,
`references/rag/`, and `references/sdlc/`, and readable by
`airchon-mentor` and `airchon-teacher` the same way those areas are.
Every claim in every page is tagged VERIFIED (fetched from a named,
authoritative source this session) or BEST CURRENT UNDERSTANDING,
UNCONFIRMED -- never blended. See each page's own "Sources" section for
what was actually checked and when.

`airchon-author` is the writer for this area; `airchon-mentor` and
`airchon-teacher` read it. Written LAZY, on demand, as real questions
need each topic -- not pre-built speculatively beyond the four axes
this book's founding request named.

## Scope: four classification axes

A model can be classified along several independent axes at once, and
a model card typically reports all of them. This book covers four,
each getting its own page, ordered here foundational -> advanced:

1. **Terminology** -- the shared vocabulary (encoder/decoder, tokens,
   pretraining, fine-tuning) every other page assumes.
2. **Task / pipeline type** -- *what the model does* (text-generation,
   feature-extraction, question-answering, and so on).
3. **Parameter count / scale** -- *how big it is*, and what that costs
   to run.
4. **Architecture: dense vs. Mixture of Experts** -- *how its
   parameters are organized internally*.
5. **Precision / quantization** -- *at what numeric precision it
   actually runs at deployment time*.

## Primary sources

- **Hugging Face Hub docs, "Tasks"** -- `huggingface.co/docs/hub/models-tasks`
  (as currently published, a contributor's guide for proposing new Hub
  task types, not a task-definition page itself -- see
  task-and-pipeline-classification.md §1 for the live finding)
- **Hugging Face `transformers` glossary** --
  `huggingface.co/docs/transformers/glossary`
- **Maxime Labonne, "Create Mixtures of Experts with MergeKit"** --
  `huggingface.co/blog/mlabonne/frankenmoe`
- **Hugging Face Optimum, "Quantization" concept guide** --
  `huggingface.co/docs/optimum/concept_guides/quantization`

Two supplementary Hugging Face docs pages were fetched where the four
sources above did not themselves contain the concrete definitions or
numbers a page needed (see each affected page's own Sources section
for exactly which claims they ground): the individual
`huggingface.co/tasks/<task-name>` pages (per-task definitions, since
`docs/hub/models-tasks` itself does not enumerate them), and
`huggingface.co/docs/transformers/llm_tutorial_optimization` (the
parameter-count-to-VRAM rule of thumb and quantized-VRAM worked
examples, since neither the glossary nor the Optimum guide states the
formula directly in those terms).

## Pages

1. [Model terminology: a grounding glossary](model-terminology.md) --
   sourced from the `transformers` glossary; defines pretrained/
   fine-tuned/LLM, encoder/decoder/encoder-decoder (seq2seq)
   architectures, causal vs. masked language modeling, tokens/input
   IDs/attention masks, model heads and backbones, and
   feature-extraction/multimodal terms. Every later page in this book
   links back here rather than redefining these terms.
2. [Task and pipeline classification: what a model is *for*](task-and-pipeline-classification.md) --
   the Hub's task/pipeline-tag taxonomy (NLP/Vision/Audio/Multimodal/
   Tabular/RL categories), with a full agentic-development treatment of
   each NLP task type an agent-building project actually encounters:
   `text-generation` (an agent's own reasoning loop),
   `text2text-generation` (fixed input-to-output transforms; the
   dedicated Hub page for this tag 404'd this session, noted openly),
   `feature-extraction` and `sentence-similarity` (embeddings, RAG,
   semantic routing/caching), `question-answering` (extractive vs.
   generative), `summarization` (context compaction),
   `text-classification` and `token-classification` (routing,
   guardrails, entity extraction), `fill-mask` (encoder pretraining,
   mostly a model-preparation-time concern), and `translation`.
3. [Parameter count and scale: the second classification axis](parameter-count-and-scale.md) --
   what a parameter is, the `7B`/`13B`/`70B` naming convention, the
   verified `~4*X GB` (float32) / `~2*X GB` (bfloat16/float16) VRAM
   rule of thumb with worked examples (GPT-3, Llama-2-70b, Falcon-40b,
   StarCoder), why growing agent-session context makes the KV cache a
   second scale-dependent memory cost (MQA/GQA as mitigations), and the
   small/mid-scale/frontier-hosted capability-tier tradeoffs an
   agent-harness builder chooses between.
4. [Mixture of Experts and frankenMoE: the architecture axis](mixture-of-experts-and-frankenmerging.md) --
   sparse MoE layers and the gate/router network, `num_local_experts`
   vs. `num_experts_per_tok`, the frankenMoE-vs-native-MoE training-
   methodology distinction, MergeKit's three router-initialization
   methods (random, cheap_embed, hidden), the memory-vs-speed-vs-
   knowledge-preservation tradeoffs, and the worked Beyonder-4x7B-v3
   example.
5. [Quantization: the deployment-precision axis](quantization.md) --
   the definition and motivation, float16/bfloat16/int16/int8 formats,
   the affine and symmetric int8 quantization schemes, per-tensor vs.
   per-channel granularity, the three calibration approaches (dynamic
   PTQ, static PTQ, QAT) and calibration techniques, a concrete worked
   VRAM example (29 GB to 15 GB to 9.5 GB across bf16/int8/int4), the
   accompanying inference-speed tradeoff, and a synthesis of when an
   agentic pipeline should actually quantize which of its models.
