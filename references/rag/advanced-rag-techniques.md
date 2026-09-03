# Advanced RAG techniques: token-aware chunking, embedding visualization, reranking, and query reformulation

Source: **"Advanced RAG on Hugging Face documentation using
LangChain"**, authored by Aymeric Roucher
(huggingface.co/learn/cookbook/advanced_rag, notebook fetched this
session as raw `.ipynb`). The notebook explicitly positions itself as
the sequel to the introductory notebook covered in
`basic-rag-pipeline.md` — its own opening line: "For an introduction to
RAG, you can check [this other cookbook]" (`rag_zephyr_langchain`) —
and frames its purpose around a single diagram it describes as marking,
"in blue[,] all possibilities for system enhancement," with the
notebook's own framing that "tuning the system properly will yield
significant performance gains." This page documents each of the
concrete tuning levers the notebook actually exercises: token-aware
chunking, embedding-space visualization, and cross-encoder reranking,
in that order, plus the further levers the notebook names but leaves as
future work.

## 1. The retriever half: chunk size, chunking method, and the token-vs-character trap

The notebook's knowledge base is the `m-ric/huggingface_doc` dataset
loaded via `datasets.load_dataset`, wrapped into LangChain `Document`
objects. Its first chunking pass uses a plain
`RecursiveCharacterTextSplitter` with `chunk_size=1000` characters and
a hierarchical, Markdown-aware separator list taken from LangChain's
own `MarkdownTextSplitter` class: `["\n#{1,6} ", "```\n", "\n\\*\\*\\*+\n",
"\n---+\n", "\n___+\n", "\n\n", "\n", " ", ""]` — i.e. split first on
Markdown headings, then code fences, then horizontal rules, then
paragraph and line breaks, and only fall back to splitting mid-word as
an absolute last resort. The notebook's own explanation of recursive
chunking in general: "the method will first break down the document
wherever there is a double line break... [then] again on simple line
breaks... then on sentence ends... if some chunks are still too big,
they will be split whenever they overflow the maximum size" — the
global document structure is preserved at the cost of some variation in
final chunk size.

The notebook then deliberately surfaces a subtle bug in that first
pass: chunk size was counted in **characters**, but the embedding
model (`thenlper/gte-small`) truncates its input at a fixed
`max_seq_length` counted in **tokens**. Plotting the resulting
token-length histogram, the notebook observes "the chunk lengths are
not aligned with our limit of 512 tokens, and some documents are above
the limit, thus some part of them will be lost in truncation" — a
character-based chunk-size parameter silently produces oversized
chunks whenever the underlying text is token-dense (code, dense
technical prose), and those chunks get silently truncated by the
embedder with no error raised. The fix demonstrated is to switch to
`RecursiveCharacterTextSplitter.from_huggingface_tokenizer(...)`, which
counts length via the embedding model's own tokenizer instead of raw
character count, with `chunk_overlap` set to `chunk_size / 10` and
duplicate chunks removed via a dict-keyed dedup pass over
`doc.page_content`. This chunking bug and its fix is the single most
concrete, reusable lesson this notebook contributes beyond the
introductory notebook: **always size chunks in the same unit the
embedding model itself will truncate on, not in characters, unless you
have separately verified the two are proportional for your corpus.**

## 2. Distance metric and index choice

The notebook builds the vector index with FAISS via
`langchain_community.vectorstores.FAISS`, explicitly setting
`distance_strategy=DistanceStrategy.COSINE` and normalizing embeddings
at encode time (`encode_kwargs={"normalize_embeddings": True}`),
because, per the notebook, "our particular model works well with
cosine similarity." It gives a compact definition of the three common
distance choices: "**Cosine similarity** computes the similarity
between two vectors as the cosinus of their relative angle... **Dot
product** takes into account magnitude, with the sometimes undesirable
effect that increasing a vector's length will make it more similar to
all others... **Euclidean distance** is the distance between the ends
of vectors," and notes that "once vectors are normalized, the choice of
a specific distance does not matter much" — i.e. cosine and normalized
dot product/Euclidean become equivalent rankings once every vector has
unit norm, so the real decision is whether to normalize, not which
metric name to pick afterward.

## 3. Visualizing the embedding space with PaCMAP

To make the abstract "nearest neighbor in embedding space" operation
concrete, the notebook projects the full set of chunk embeddings (384
dimensions, matching `gte-small`'s output size) down to two dimensions
with **PaCMAP**, chosen, per the notebook, over alternatives like
t-SNE or UMAP because "it is efficient (preserves local and global
structure), robust to initialization parameters and fast." It embeds a
user query into the same space and plots it as a distinctly marked
point among the corpus chunks, coloring chunks by source document, to
give a visual account of why nearest-neighbor search over embeddings
retrieves the chunks it does — semantically similar chunks cluster
spatially, and retrieval is literally "find the k corpus points closest
to the query's point." This is a diagnostic/pedagogical technique
specific to this notebook, not a production pipeline component.

## 4. The reader half: prompt, and reranking with ColBERTv2

The reader model is again `HuggingFaceH4/zephyr-7b-beta`, loaded
4-bit-quantized exactly as in `basic-rag-pipeline.md` §5, with the
notebook noting the reader's context window must be large enough to
hold the retrieved-context block: "the reader model's `max_seq_length`
must accommodate our prompt, which includes the context output by the
retriever call: the context consists of 5 documents of 512 tokens each,
so we aim for a context length of 4k tokens at least." The prompt is
built via `tokenizer.apply_chat_template` on an explicit system/user
message pair rather than a hand-written template string (the more
general approach the introductory notebook flagged but didn't use),
with the system message instructing the model to "give a comprehensive
answer to the question... Provide the number of the source document
when relevant. If the answer cannot be deduced from the context, do not
give an answer" — an explicit instruction against fabricating an answer
absent supporting context.

The notebook's headline addition over the introductory pipeline is
**reranking**: retrieve more candidates than are ultimately needed
(`num_retrieved_docs=30`), then rerank that larger candidate pool with
a stronger, more expensive model before truncating to the final
`num_docs_final=5` passed to the reader. The reranker used is
**ColBERTv2** (`colbert-ir/colbertv2.0`, `arxiv.org/abs/2112.01488`
per the notebook's own citation), loaded through the RAGatouille
library's `RAGPretrainedModel.from_pretrained`. The notebook's own
distinction between the embedding-based retriever and this reranker:
ColBERTv2 "instead of a bi-encoder like our classical embedding
models... is a cross-encoder that computes more fine-grained
interactions between the query tokens and each document's tokens" — a
bi-encoder embeds the query and each document independently and
compares fixed vectors (cheap, so it can scan the whole corpus), while
a cross-encoder jointly attends over the query and a candidate document
together (expensive, so it is only run over the retriever's already-
narrowed shortlist), trading throughput for precision at the reranking
stage specifically.

```mermaid
flowchart LR
    Q["Query"] --> BI["Bi-encoder retriever<br/>(FAISS, cosine, top-30)"]
    BI --> CE["ColBERTv2 cross-encoder rerank<br/>(RAGatouille)"]
    CE -->|top-5| CTX["Context block"]
    Q --> PROMPT["Chat-template prompt"]
    CTX --> PROMPT
    PROMPT --> READER["Zephyr-7b-beta<br/>(4-bit NF4)"]
    READER --> A["Answer"]
```

The notebook packages this into a single reusable function,
`answer_with_rag(question, llm, knowledge_index, reranker=None,
num_retrieved_docs=30, num_docs_final=5)`, which performs the
retrieve → optionally-rerank → truncate → build-context → prompt →
generate sequence end to end and returns both the answer and the
retained source chunks, printing progress at each stage
("Retrieving documents...", "Reranking documents...", "Generating
answer...").

## 5. Levers named but not implemented in this notebook

The notebook closes with an explicit, self-labeled "To go further"
list of further tuning levers it names but does not itself build,
which is useful precisely because it demarcates the boundary of what
this specific notebook actually demonstrates versus what it merely
gestures at:

- **Set up a proper evaluation pipeline** before iterating further — the
  notebook's own words: "you cannot improve the model performance that
  you do not measure" — pointed at in this reference area's
  `rag-evaluation.md`, a separate cookbook notebook by the same author
  that actually builds this.
- **Semantic chunking** as an alternative to recursive character/token
  chunking, named but not implemented here.
- **Changing the embedding model or the vector index** (FAISS is used
  throughout; alternatives are named, not swapped in).
- **Query expansion** — "reformulate the user query in slightly
  different ways to retrieve more documents" — named as a retrieval
  lever, not implemented in this notebook.
- **Prompt compression** of the retrieved context before it reaches the
  reader, and **citing sources / making the system conversational** as
  reader-side improvements — named, not implemented.

Each of these is a real, separate technique the notebook flags rather
than demonstrates; documenting them here as "named but unimplemented"
keeps this page's claims scoped to what was actually fetched and read
this session rather than inferring implementations that were not
shown.

## 6. Pre-retrieval query transformation: Rewrite-Retrieve-Read and HyDE

The techniques documented in §1–§4 above all operate either on the
retriever half (chunk sizing, indexing, reranking) or the reader half
(prompt design). This section documents a third category: techniques
that transform the *query itself* before retrieval — bridging the gap
between the user's input text and the knowledge needed to answer it.
These are **pre-retrieval** techniques, distinct from the
post-retrieval cross-encoder reranking documented in §4 (which
operates on the *retrieved results* after retrieval has already
happened). The notebook named "query expansion" in its §5
named-but-unimplemented list ("reformulate the user query in slightly
different ways to retrieve more documents"); the two papers below are
the foundational formalizations of that lever.

### 6.1 Query Rewriting: the Rewrite-Retrieve-Read framework

Xinbei Ma, Yeyun Gong, Pengcheng He, Hai Zhao, and Nan Duan, in "Query
Rewriting for Retrieval-Augmented Large Language Models"
(arxiv.org/abs/2305.14283, fetched this session from the arXiv
abstract page, EMNLP 2023), introduce the **Rewrite-Retrieve-Read**
framework. The paper's abstract states its core contribution: it
proposes "a new framework, Rewrite-Retrieve-Read instead of the
previous retrieve-then-read for the retrieval-augmented LLMs from the
perspective of the query rewriting." The paper's stated motivation:
"there is inevitably a gap between the input text and the needed
knowledge in retrieval" — the user's raw query may not match the
vocabulary, phrasing, or specificity of the documents that contain
the answer.

The framework, per the abstract, works as follows:

1. **Rewrite**: first prompt an LLM to generate (rewrite) the query.
2. **Retrieve**: use the rewritten query (not the original) to
   retrieve contexts — the paper's abstract states it uses "a web
   search engine to retrieve contexts," though the framework is
   general and the retriever can be any search system.
3. **Read**: pass the retrieved contexts to the LLM reader to
   generate the answer.

This is structurally a **pre-retrieval** transformation: the query is
modified *before* it reaches the retriever, not after. The
Retrieve-then-Read pipeline retrieves directly on the user's raw
input; Rewrite-Retrieve-Read inserts one LLM call — the rewrite —
before the retrieval step, then proceeds with the normal
retrieve-then-read flow. The abstract is explicit about where the
adaptation happens: "Unlike prior studies focusing on adapting either
the retriever or the reader, our approach pays attention to the
adaptation of the search query itself."

The paper also proposes a **trainable scheme** beyond the prompt-based
approach, per the abstract: "A small language model is adopted as a
trainable rewriter to cater to the black-box LLM reader. The rewriter
is trained using the feedback of the LLM reader by reinforcement
learning." In this scheme, the rewriter is not just a frozen LLM
prompted to rewrite — it is a small language model that is fine-tuned
via RL, where the reward signal comes from how well the LLM reader
performs on the downstream task (open-domain QA and multiple-choice QA)
using the rewritten query. The abstract reports that "experiments
results show consistent performance improvement, indicating that our
framework is proven effective and scalable."

The key distinction from HyDE (§6.2 below): Rewrite-Retrieve-Read
transforms the *query* into a better *query* before retrieval — the
rewritten query is still a question or search phrase, not a hypothetical
answer document. HyDE transforms the query into a hypothetical *answer*
and retrieves on that instead.

### 6.2 HyDE: Hypothetical Document Embeddings

Luyu Gao, Xueguang Ma, Jimmy Lin, and Jamie Callan, in "Precise
Zero-Shot Dense Retrieval without Relevance Labels"
(arxiv.org/abs/2212.10496, fetched this session from the arXiv
abstract page, submitted December 2022), introduce **HyDE**
(Hypothetical Document Embeddings). The paper's abstract states the
core idea: "Given a query, HyDE first zero-shot instructs an
instruction-following language model (e.g. InstructGPT) to generate a
hypothetical document. The document captures relevance patterns but is
unreal and may contain false details. Then, an unsupervised
contrastively learned encoder (e.g. Contriever) encodes the document
into an embedding vector. This vector identifies a neighborhood in the
corpus embedding space, where similar real documents are retrieved based
on vector similarity."

The mechanism, per the abstract, has a critical property that makes it
work despite the hypothetical document containing false details: "This
second step ground[s] the generated document to the actual corpus,
with the encoder's dense bottleneck filtering out the incorrect
details." In other words:

```mermaid
flowchart LR
    Q["User query"] --> LLM["Instruction-following LLM<br/>(e.g. InstructGPT)"]
    LLM --> HD["Hypothetical document<br/>(captures relevance patterns,<br/>may contain false details)"]
    HD --> ENC["Unsupervised encoder<br/>(e.g. Contriever)"]
    ENC --> EMB["Embedding vector"]
    EMB --> CORPUS["Corpus embedding space<br/>(vector similarity search)"]
    CORPUS --> RET["Real documents retrieved"]
```

The insight is that dense retrieval normally struggles with zero-shot
relevance — the abstract states it "remains difficult to create
effective fully zero-shot dense retrieval systems when no relevance
label is available" — because the query encoder must somehow map a
short user query into the same embedding neighborhood as the
full-length documents that answer it. HyDE sidesteps this by having
the LLM generate a *full-length hypothetical answer document* that is
already in the "document space" the encoder was trained on, and then
embedding that document (which captures the relevance pattern of the
answer) rather than the raw query (which does not).

The paper reports the following results, per the abstract: "HyDE
significantly outperforms the state-of-the-art unsupervised dense
retriever Contriever and shows strong performance comparable to
fine-tuned retrievers, across various tasks (e.g. web search, QA, fact
verification) and languages (e.g. sw, ko, ja)." This is a notable
claim: HyDE achieves performance comparable to *fine-tuned* retrievers
without any relevance labels at all, purely by leveraging the LLM's
ability to generate a plausible answer document and then using a
*zero-shot* encoder to embed it. The false details in the hypothetical
document do not derail retrieval because the encoder's dense bottleneck
— its compression of the document into a single embedding vector —
smooths over the specific incorrect claims while preserving the general
relevance pattern.

### 6.3 Position in the RAG technique taxonomy

Both Rewrite-Retrieve-Read and HyDE are **pre-retrieval query
transformation** techniques — they modify what the retriever sees
before retrieval happens. This positions them as a complement to, not
a replacement for, the post-retrieval reranking documented in §4
above. A RAG pipeline could in principle use both: rewrite or
Hypothetical-Document-embed the query first (§6), then retrieve a
candidate pool, then cross-encoder-rerank the candidates (§4), then
pass the final top-k to the reader. The pre-retrieval techniques
improve what enters the retrieval pipeline; the post-retrieval
techniques improve what exits it.

The distinction matters because the failure modes they address are
different. Reranking (§4) addresses the case where the bi-encoder
retriever ranks the right documents too low — it fixes ranking quality
within the retrieved set. Query transformation (§6) addresses the case
where the *query itself* is the bottleneck — the user's phrasing does
not match the document's vocabulary, or the query is too short/sparse
for the encoder to map into the right neighborhood. Reranking cannot
help if the relevant document was never retrieved in the first place;
query transformation can, by changing the query to retrieve better
candidates upfront.
