# RAG: definitions and techniques

A reference for Retrieval-Augmented Generation — definitions,
architecture patterns, evaluation, and implementation techniques.
Sourced primarily from the **HuggingFace Cookbook** notebooks and
foundational papers. Claims here are attributed to those sources
directly; this area covers RAG-the-technique, not any specific
harness's internal implementation of retrieval (that belongs in
`references/harnesses/`).

`airchon-author` is the writer for this area; `airchon-mentor` reads
it. No independent cross-verification is performed beyond what the
original sources contain — treat claims as "the source says" rather
than independently verified.

## Primary sources

- **Lewis et al. (2020)**, "Retrieval-Augmented Generation for
  Knowledge-Intensive NLP Tasks" — `arxiv.org/abs/2005.11401`
- **HuggingFace Cookbook** — `huggingface.co/learn/cookbook/`
- **HuggingFace Agents Course**, Unit 3 "Agentic RAG" —
  `huggingface.co/learn/agents-course/en/unit3/agentic-rag/agentic-rag`

## Pages

1. [RAG foundations: the Lewis et al. formulation and the agentic
   reframing](foundations.md) -- parametric/non-parametric memory,
   RAG-Sequence vs. RAG-Token, and the HuggingFace Agents Course's
   agentic-RAG reframing of retrieval as one tool among several
2. [The basic RAG pipeline: LangChain, Zephyr, and FAISS over GitHub
   issues](basic-rag-pipeline.md) -- the cookbook's introductory
   notebook (`rag_zephyr_langchain`); the baseline every later page's
   "advanced" or "custom-data" variant is a delta against
3. [Advanced RAG techniques: token-aware chunking, embedding
   visualization, and reranking](advanced-rag-techniques.md) -- the
   `advanced_rag` notebook: the character-vs-token chunking trap,
   PaCMAP embedding visualization, and ColBERTv2 cross-encoder
   reranking via RAGatouille
4. [Vector store integrations: Milvus, Elasticsearch, and MongoDB
   Atlas](vector-store-integrations.md) -- three notebooks
   (`rag_with_hf_and_milvus`, `rag_with_hugging_face_gemma_elasticsearch`,
   `rag_with_hugging_face_gemma_mongodb`) swapping the retriever half
   of the basic pipeline onto three production vector stores
5. [Semantic caching for RAG: placement, threshold, and
   eviction](semantic-caching.md) -- the `semantic_cache_chroma_vector_database`
   notebook: why the cache sits between the user and retrieval (not
   between the user and the LLM), FAISS `IndexFlatL2` with a
   Euclidean threshold, and FIFO eviction
6. [Structured generation for RAG: from prompting to constrained
   decoding](structured-generation-for-rag.md) -- the
   `structured_generation` notebook: source-snippet highlighting,
   Pydantic-schema grammars, and Outlines' logit-biasing mechanism
7. [RAG evaluation: synthetic datasets, critique agents, and
   LLM-as-judge](rag-evaluation.md) -- the `rag_evaluation` notebook:
   synthetic QA generation, groundedness/relevance/standalone critique
   agents, and a Prometheus-style GPT-4 judge rubric
8. [Agentic RAG with LlamaIndex: the "librarian" pattern and a fully
   local stack](agentic-rag-with-llamaindex.md) -- the
   `rag_llamaindex_librarian` notebook: LlamaIndex's Loading/Indexing/
   Querying phases, its OpenAI-by-default trap, and a fully local
   Ollama + Llama 2 stack
9. [RAG over heterogeneous data sources: unstructured documents and SQL
   databases](heterogeneous-data-sources.md) -- two notebooks
   (`rag_with_unstructured_data`, `rag_with_sql_reranker`) that replace
   the usual chunk-and-embed retrieval unit: Unstructured's
   partition-then-chunk pipeline for mixed document formats, and Jina
   Reranker v2 scoring whole SQL table schemas with no vector index at
   all

All eleven HuggingFace Cookbook notebooks identified as this area's
source material are now covered by the pages above. `foundations.md`
additionally covers the two non-cookbook primary sources (Lewis et al.
2020 and the HuggingFace Agents Course Unit 3 page).
