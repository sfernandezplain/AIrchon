# Foreword -- The Road to Agentic Archon

## Who this book is for

This book is a single, ordered path through territory that the wiki (`references/**`) covers as a dense, cross-linked research shelf. That shelf grew LAZY -- page by page, as real questions demanded real sources -- and it is the more complete, more cited place to settle an argument about how a particular harness behaves on a particular day. The book is what you read when you want the *order*.

Four tiers name where a reader lands today. They are the same four `resources/airchon-teacher/reader-proficiency-tiers.md` uses -- this book does not rename them.

- **Slumberer.** You treat the harness as a black box and debug by rephrasing prompts. You will leave Part I (topology and the loop) able to name the stage that produced a line rather than asking why the model did it.
- **Gnostic.** You have the vocabulary and the map but have never traced a request through a real harness's documented machinery. Part II (general concepts, Ch.04-12) hangs each abstract mechanism on actual config keys, file paths, and tool names -- one harness at a time, then comparatively.
- **Demiurge.** You can already trace one harness and operate it at power-user depth. Part III (harness-by-harness syntheses) and the glossary are your reference shelf inside the book -- the place you check how an assumption from one harness lands on another.
- **Archon.** You design new harness features and mentor others. You will read this book for its ordering decisions and its diagrams; the wiki remains your source shelf for the citations behind them.

## How to read this book

Front-to-back in `index.md` order is the designed path. Prerequisites are explicit per chapter; skipping breaks them. The harness-by-harness pages (`harnesses/*.md`) are reference after the general-concept chapters -- read the general chapter that teaches the concept first, then the harness synthesis for that harness. The glossary is deliberately last. Terms are introduced where they are first needed and linked there; you should not need a term that only appears three chapters later.

If you are in a hurry, read the foreword, then `Ch.01 Topology` and `Ch.02 Agent Loop`, then the harness page for the harness you actually use. You can come back for the rest in order.

## Voice and conventions

The voice is Kent Beck / Martin Fowler -- clear, concrete, example-rich, and built on progressive disclosure. Each chapter does a small thing first: it names the idea in one sentence, shows the smallest concrete example, then expands the full mechanism and its edge cases. **Verbosity in this book is a virtue, not a vice.** The operator explicitly requested detailed, verbose chapters for developers who want to understand agentic architecture *in all detail* -- not concise summaries that assume a concept is already explained. This book therefore follows one rule without exception: **no concept is used before it is taught**. When quantization is mentioned, the chapter first explains what quantization *is* in plain language (coarser numbers for less memory/bandwidth) before naming affine vs. symmetric schemes. When the KV cache is invoked, the chapter first explains *why* caching exists (avoid recomputing attention over the whole history) before naming `--cache-type-k`. When MoE appears, the chapter first explains *what an expert is* (a feed-forward sublayer that only some tokens visit) before naming `num_local_experts`. That is honored per chapter; think of each chapter as a short essay with running examples, not a bullet-point digest. A developer who reads front-to-back should never need a term that only appears three chapters later without having met it as a defined, illustrated idea first.

Three conventions run throughout:

- **Mermaid legend.** `flowchart` = structure (what connects to what). `sequenceDiagram` = flow across turns or agents (who calls whom, who appends what). `stateDiagram-v2` = states and transitions (how a session moves from one mode to another). Every diagram sits directly above the prose it illustrates; the diagram is a companion, not a replacement -- the prose below it remains the authoritative, detailed account.
- **Grounding tags.** VERIFIED vs BEST CURRENT UNDERSTANDING, UNCONFIRMED are inherited from the wiki page that chapter distills. Citations name the wiki source page (`references/harnesses/caching.md` § sources), not pretraining. When a chapter notes a gap, it says so plainly and points to `airchon-author` for the research rather than inventing the mechanism.
- **Navigation footer.** Every chapter ends with `Prev | Index | Next | Glossary` links. The index leads to chapters, chapters lead to the next page, glossary terms are bidirectional. That chain is verified on every book build; a broken link fails the build.

## What this book is, and what the wiki is for

The wiki (`references/harnesses/`, `references/sdlc/`, `references/rag/`, `references/models/`, `references/inference-engines/`) is the verified research shelf, written on demand from primary sources (official docs, each harness's own public repo, the Agentic SDLC Handbook, the HuggingFace Cookbook). The book is the ordered, distilled, pedagogical counterpart. The wiki stays canonical for source truth; the book is canonical for learning order. When a chapter cites `references/...`, it means that wiki page's own sources were already fetched and cited -- this book does not re-cite them from memory.

The scaffold for this book lives alongside the wiki at `/book/`, owns the only write surface there, and is maintained by `airchon-communicator`. The general-concept chapters are taught in the order `resources/airchon-teacher/knowledge-path-curriculum.md` encodes for Clusters 1-10 (Memory&Context -> Coordination -> Transport -> Config -> Skills&Tools -> RAG -> SDLC mechanics -> Models -> Inference Engines), with concrete harness-by-harness synthesis pages at the end, and a glossary to tie the terminology together.

## Navigation

- [Index](index.md) -> Ch.01 Topology -> ... -> Ch.12 Advanced -> Harness syntheses -> [Glossary](glossary.md)
- Every chapter footer: `Prev | Index | Next | Glossary` -- all links must resolve. The book build verifies this before it is considered complete.
