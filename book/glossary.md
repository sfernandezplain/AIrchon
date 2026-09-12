# Glossary -- The Road to Agentic Archon

> **Status:** complete 2026-09-12. Every term below is introduced in at least one chapter with a link to this file's anchor; every entry links back to defining/heavily-using chapters. No dangling glossary anchor (Gate 3 glossary coverage PASS).

## How to use

Terms are alphabetized within letter sections. Each entry gives a one-line plain-language definition (Beck/Fowler), a mechanism paragraph naming the actual config keys/file paths/tool names the wiki verified, and backlinks to defining chapters. First introduction of a term in a chapter links to this file's anchor (`../glossary.md#term-slug`); this entry links back.

---

## A

### Agent loop {#agent-loop}
LLM + tools running a Thought/Action/Observation `while` loop until a stop condition. The loop's state is the growing prompt; each Observation is appended and re-read on every future turn. See [Ch.02](../chapters/02-agent-loop.md), [Ch.03](../chapters/03-agent-loop-implementations.md). Distilled from [`references/harnesses/agent-loop.md`](../references/harnesses/agent-loop.md) (Hugging Face Agents Course).

### Agent topology {#agent-topology}
The four axes that place any agentic system: reactive vs. deliberative, single vs. multi-agent, tool-augmented vs. autonomous, and narrow vs. broad component decomposition plus where a harness sits relative to a bare loop. See [Ch.01](../chapters/01-topology.md). From [`references/harnesses/agent-topology.md`](../references/harnesses/agent-topology.md).

### AGENTS.md {#agents-md}
Human-authored project instruction file (`AGENTS.md` or `CLAUDE.md`), discovered by walking from cwd to root, concatenated broadest-first-nearest-last, with per-harness fallback rules and first-match-per-directory precedence in pi (`AGENTS.override.md` > `AGENTS.md` > `CLAUDE.md`). See [Ch.04](../chapters/04-memory-context.md), [Ch.07](../chapters/07-config-permissions.md). From [`references/harnesses/memory-management.md`](../references/harnesses/memory-management.md) (Sections 1-6) and `instruction-context-budget.md`.

### Auth precedence {#auth}
Which credential source wins when multiple auth sources are configured (env var vs. OAuth login vs. settings file, harness-specific ordering). See [Ch.07](../chapters/07-config-permissions.md). From [`references/harnesses/auth-and-usage-accounting.md`](../references/harnesses/auth-and-usage-accounting.md).

## B

### Batching / continuous batching {#batching}
How concurrent requests share one loaded local model: slot-based continuous batching (`--parallel`/`--batch-size`/`--ubatch-size`) vs. static batch, critical for fan-out throughput against one local model. See [Ch.11](../chapters/11-models-engines.md). From [`references/inference-engines/batching-and-continuous-batching.md`](../references/inference-engines/batching-and-continuous-batching.md).

### Budget enforcement (three layers) {#budget}
SDK/loop-level (`max_turns`/`max_budget_usd`/`maxAiCredits`/`IterationBudget`), workflow-level, and org-level (Managed/MDM) -- three distinct enforcement depths with different subagent-accounting rules. See [Ch.03](../chapters/03-agent-loop-implementations.md), [Ch.07](../chapters/07-config-permissions.md). From [`references/harnesses/agent-loop-implementations.md`](../references/harnesses/agent-loop-implementations.md), `auth-and-usage-accounting.md`.

### Built-in skills {#built-in-skills}
What ships as a skill by default (present in every session) vs. user-authored content. Claude Code bundled set (`/doctor`, `/code-review`, etc.) with `disableBundledSkills`; Copilot CLI Forge-generated; OpenCode none native; pi/Hermes `agentskills.io`. See [Ch.08](../chapters/08-skills-tools.md). From [`references/harnesses/built-in-skills.md`](../references/harnesses/built-in-skills.md).

### Built-in tools {#built-in-tools}
The finite tool inventory per harness (Read/Write/Edit/Bash/Grep/Glob/Task/...) with the `permission-required` column and the Edit three-gate check. See [Ch.08](../chapters/08-skills-tools.md). From [`references/harnesses/built-in-tools.md`](../references/harnesses/built-in-tools.md).

## C

### Caching (prompt/context caching) {#caching}
Server-side prefix reuse (not shrinking) -- a common prefix whose next turn charges ~0.1x. Scope/TTL-by-auth-path, breakpoint placement (`packages/llm/src/cache-policy.ts` auto-placement), invalidate-vs-preserve lists. Editing an early section invalidates; appending preserves. See [Ch.04](../chapters/04-memory-context.md). From [`references/harnesses/caching.md`](../references/harnesses/caching.md).

### Cache Augmented Generation (CAG) {#cag}
Loading the entire knowledge base into the context window and caching the prefix instead of retrieving -- viable only when KB fits in the window and prompt caching makes re-reading affordable. See [Ch.09](../chapters/09-rag.md). From [`references/rag/cache-augmented-generation.md`](../references/rag/cache-augmented-generation.md) (Ovadia et al. + Anthropic prompt-caching docs, BEST CURRENT UNDERSTANDING).

### ColBERTv2 / reranking (RAGatouille) {#colbert}
Cross-encoder second-pass re-scoring of top-k retrieved candidates (joint query+doc attention) via RAGatouille. See [Ch.09](../chapters/09-rag.md). From [`references/rag/advanced-rag-techniques.md`](../references/rag/advanced-rag-techniques.md).

### Compaction / context compression {#compaction}
Mid-run shrinking when the window fills: Claude Code evict-then-summarize (two-phase, thrash guard), Copilot CLI 95%-trigger checkpoint compaction, OpenCode `prune()`/`process()` pipeline, Hermes Agent dual-threshold (85% gateway + 50% `ContextEngine`). Distinct from instruction-budget trimming and from compaction *survival* (what re-injects after). See [Ch.04](../chapters/04-memory-context.md). From [`references/harnesses/context-compression.md`](../references/harnesses/context-compression.md).

### Configuration (settings hierarchies) {#configuration}
Where config lives and which scope wins: Claude Code four-scope (`Managed/User/Project/Local`, permission-rules-merge exception); Copilot CLI `~/.copilot` chain with bounded repo `settings.json`; OpenCode eight-source `mergeConfigConcatArrays()` with `{env:}`/`{file:}` substitution; pi two-scope with `defaultTools` exception; Hermes `~/.hermes/` `config.yaml`+`.env`; DeepSeek Cordis plugin tree. See [Ch.07](../chapters/07-config-permissions.md). From [`references/harnesses/configuration.md`](../references/harnesses/configuration.md).

### Coordination design space {#coordination-design-space}
General multi-agent literature patterns -- blackboard, consensus/voting (LLM-Blender, debate), and the negative finding of no market-based/competitive-bidding allocation in any harness. See [Ch.05](../chapters/05-coordination.md). From [`references/harnesses/multi-agent-coordination-design-space.md`](../references/harnesses/multi-agent-coordination-design-space.md).

## D

### Deterministic orchestration {#deterministic-orchestration}
Fixed-graph/workflow harnesses where the graph controls flow (LangGraph `StateGraph`, Microsoft Conductor, GitHub Agentic Workflows `gh-aw` with `engine:` wrapping a real CLI and `.lock.yml` derived artifact). See [Ch.12](../chapters/12-advanced.md) and [`references/sdlc/16-deterministic-probabilistic-boundary.md`](../references/sdlc/16-deterministic-probabilistic-boundary.md). From [`references/harnesses/deterministic-orchestration.md`](../references/harnesses/deterministic-orchestration.md).

## F

### Fan-out (subagent dispatch) {#fan-out}
Launch mechanics distinct from handoff: Claude Code three layers (in-conversation caps, background `claude agents` no hard cap, Workflow `pipeline()` 16/1000); Copilot CLI changelog-traced limits + `/fleet`; OpenCode `FiberSet.awaitEmpty`; DeepSeek `SubagentRuntime.start()`/`.startContinuable()`; pi none native. See [Ch.05](../chapters/05-coordination.md). From [`references/harnesses/fan-out.md`](../references/harnesses/fan-out.md).

## G

### GGUF {#gguf}
GPT-Generated Unified Format -- a purpose-built inference-serving format with header / typed KV metadata / tensor infos / tensor data sections and per-tensor `ggml` type mixins, succeeding GGML/GGMF/GGJT's breaking-change-unsafe lineage. See [Ch.11](../chapters/11-models-engines.md). From [`references/inference-engines/model-file-formats.md`](../references/inference-engines/model-file-formats.md).

## H

### Handoff {#handoff}
Agent-to-agent context transfer (what crosses the spawn boundary): Claude Code fresh-context `SendMessage`+agent ID (forks vs. named), OpenCode `Task` `session.create(parentID)` + `task_id` resume, pi `handoff.ts` LLM-generated human-reviewed, Hermes in-process child `AIAgent`. Distinct from compaction survival. See [Ch.05](../chapters/05-coordination.md). From [`references/harnesses/handoff-mechanism.md`](../references/harnesses/handoff-mechanism.md).

### Harness {#harness}
The tools, context management, and execution environment that turn a language model into a capable agent -- "Claude Code is the harness; Claude is the model inside it" (Claude Code glossary, VERIFIED). Adopted umbrella term for all six harnesses in this book by architectural analogy. See [Ch.01](../chapters/01-topology.md) Section 6. From [`references/harnesses/agent-topology.md`](../references/harnesses/agent-topology.md) (Claude Code glossary).

### Hooks (lifecycle) {#hooks}
User-owned code sitting inside the loop's control flow: Claude Code ~30-event catalogue where only `exit 2` / `{"decision":"block"}` blocks; OpenCode `event` bus vs. typed `Hooks` interface. See [Ch.07](../chapters/07-config-permissions.md). From [`references/harnesses/hooks-lifecycle-extensibility.md`](../references/harnesses/hooks-lifecycle-extensibility.md).

### HyDE (Hypothetical Document Embeddings) {#hyde}
Generating a hypothetical answer, embedding it instead of the query, and retrieving against the corpus (encoder bottleneck filters false details). Contrasted with Rewrite-Retrieve-Read. See [Ch.09](../chapters/09-rag.md). From [`references/rag/advanced-rag-techniques.md`](../references/rag/advanced-rag-techniques.md) (Gao et al. 2022).

## I

### Inference engine {#inference-engine}
A local, self-hosted LLM runtime -- llama.cpp (foundational, maximal backends), Ollama (registry/Modelfile/REST over llama.cpp + Go engine), KTransformers (heterogeneous CPU/GPU for large MoE). Eleven engine-agnostic mechanisms (GGUF, `mmap`, KV-cache, sampling, batching, offloading, speculative decoding, ...) plus per-engine choice. See [Ch.11](../chapters/11-models-engines.md). From [`references/inference-engines/index.md`](../references/inference-engines/index.md).

### Instruction context budget {#instruction-budget}
The eagerly-loaded instruction tier and levers for keeping it small: why `@` imports don't help, path-scoped `paths:`/`applyTo:` as deferral, skills as invoke-only tier, exclusion/trim. See [Ch.04](../chapters/04-memory-context.md). From [`references/harnesses/instruction-context-budget.md`](../references/harnesses/instruction-context-budget.md).

### Inter-agent messaging {#messaging}
The wire once agents are running: Claude Code `SendMessage` file-based mailbox (`~/.claude/teams/{team}/inboxes/{agent}.json`) with structured protocol messages; Copilot CLI one-directional `subagent.*` stream; OpenCode ordinary SSE message row; pi none; Hermes `state.db`-republished synthetic message. See [Ch.05](../chapters/05-coordination.md). From [`references/harnesses/inter-agent-messaging.md`](../references/harnesses/inter-agent-messaging.md).

## K

### KV cache {#kv-cache}
The per-token cached key-value state that makes generation O(1) per step but scales with context length (not model size), with VRAM-aware sizing (`--ctx-size` / `OLLAMA_CONTEXT_LENGTH`) and optional quantized type (`--cache-type-k`/`-v`). See [Ch.11](../chapters/11-models-engines.md). From [`references/inference-engines/kv-cache-and-context-window-management.md`](../references/inference-engines/kv-cache-and-context-window-management.md).

## L

### LLM API contract {#llm-api-contract}
The provider wire contract: Anthropic Messages (`tool_use`/`tool_result`/`stop_reason` + `message_start`..`message_stop`) vs. OpenAI Responses (`tool_calls`/`call_id`/`finish_reason`) and OpenCode's `Protocol`/`Endpoint`/`Auth`/`Framing` unification. See [Ch.06](../chapters/06-transport.md). From [`references/harnesses/llm-api-contract.md`](../references/harnesses/llm-api-contract.md).

### Load lifecycle (SDLC) {#load-lifecycle}
The four-phase Resolve/Materialize/Bind/Activate pipeline a markdown primitive crosses from disk to the model's context, with three binding modes (deterministic/probabilistic/conditional) and phantom-dependency/bundle-leakage as edge anti-patterns. See [Ch.10](../chapters/10-sdlc.md). From [`references/sdlc/14-the-load-lifecycle.md`](../references/sdlc/14-the-load-lifecycle.md) (the handbook says).

## M

### MCP integration {#mcp}
Discovery/registration/transport/tool-calling for MCP servers: `sanitize(server)_sanitize(tool)` naming, pagination, capability negotiation (`roots`/`sampling`/`elicitation`), `.well-known/opencode` defaults, pi's no-native-client stance. See [Ch.08](../chapters/08-skills-tools.md). From [`references/harnesses/mcp-integration.md`](../references/harnesses/mcp-integration.md).

### Memory management {#memory}
Instruction-file hierarchies (CLAUDE.md/AGENTS.md load order, `@` imports, `.claude/rules/`) plus agent-authored stores (Claude Code auto memory `MEMORY.md` 200 lines/25KB + topic files; Copilot Memory server-side `store_memory`/`vote_memory` with 28-day expiry; OpenCode/pi no native agent-authored tool) and compaction-survival asymmetry. See [Ch.04](../chapters/04-memory-context.md). From [`references/harnesses/memory-management.md`](../references/harnesses/memory-management.md).

### Middleware (library-as-harness) {#middleware}
An in-process, construction-time-composed onion wrapper around the model call (rewrites before the step vs. a hook's observe/veto after) -- instantiated by LangChain Deep Agents (`create_deep_agent()` as LangGraph runtime + bare `create_agent()` + bundled middleware/backend/subagent/skills stack with `BackendProtocol` and `CompiledSubAgent`). See [Ch.12](../chapters/12-advanced.md). From [`references/harnesses/middleware-composed-agent-harnesses.md`](../references/harnesses/middleware-composed-agent-harnesses.md).

### Mixture of Experts (MoE) / frankenMoE {#moe}
A sparse architecture where only `num_experts_per_tok` of `num_local_experts` fire per token, with frankenMoE (MergeKit `random`/`cheap_embed`/`hidden` router init stitching dense checkpoints) vs. native training. See [Ch.11](../chapters/11-models-engines.md). From [`references/models/mixture-of-experts-and-frankenmerging.md`](../references/models/mixture-of-experts-and-frankenmerging.md).

### Model classification (four axes) {#model-classification}
Terminology (encoder/decoder etc.) -> task/pipeline type (`text-generation`, `feature-extraction`, ...) -> parameter count/scale (VRAM `4*X`/`2*X` + KV-cache cost) -> architecture (dense vs. MoE) -> quantization (precision axis). See [Ch.11](../chapters/11-models-engines.md). From [`references/models/index.md`](../references/models/index.md).

## O

### Observability {#observability}
How the harness itself is debugged/operated: debug flags (`--debug`, `/heapdump`), introspection (`/context`/`/hooks`/`/mcp`/`/status`/`/doctor`), and customer-configured OTel traces (`claude_code.*` spans, `traceparent`) vs. default-on vendor telemetry -- distinct from cost-and-usage accounting's own OTel pipe. See [Ch.12](../chapters/12-advanced.md). From [`references/harnesses/observability-and-self-diagnostics.md`](../references/harnesses/observability-and-self-diagnostics.md).

### Orchestration {#orchestration}
Who holds the plan across agents: turn-by-turn (each turn's model decides) vs. script-held (`agent()`/`pipeline()`, start-order resume, 16/1000 caps) vs. `/fleet` orchestrator-agent. See [Ch.05](../chapters/05-coordination.md). From [`references/harnesses/orchestration.md`](../references/harnesses/orchestration.md).

## P

### Permissions / sandboxing {#permissions}
The rule-schema vs. enforcement-architecture split: per-tool `allow`/`ask`/`deny` with glob and per-agent overrides as schema, plus Claude Code's two-layer OS sandboxed Bash (filesystem+network) or OpenCode's no-OS-sandbox enforcement. See [Ch.07](../chapters/07-config-permissions.md). From [`references/harnesses/permissions-and-sandboxing.md`](../references/harnesses/permissions-and-sandboxing.md).

### PROSE framework {#prose}
Five constraints (the handbook's own names for making output reliable/verifiable/maintainable) that every one of the nineteen anti-patterns in `20-anti-patterns-and-failure-modes.md` is mapped onto. See [Ch.10](../chapters/10-sdlc.md). From [`references/sdlc/prose-framework.md`](../references/sdlc/prose-framework.md) (the handbook says).

## Q

### Quantization {#quantization}
The deployment-precision axis: affine vs. symmetric int8, per-tensor vs. per-channel granularity, dynamic PTQ vs. static PTQ vs. QAT calibration, float16/bfloat16/int16/int8, with the worked 29 GB -> 15 GB -> 9.5 GB VRAM cascade; plus the inference-engine complement (inline per-block dequantization at compute time, GGUF mixed types, KV-cache quantization). See [Ch.11](../chapters/11-models-engines.md). From [`references/models/quantization.md`](../references/models/quantization.md) and [`references/inference-engines/quantization-at-inference-time.md`](../references/inference-engines/quantization-at-inference-time.md).

## R

### RAG (Retrieval-Augmented Generation) {#rag}
Parametric (weights) + non-parametric (retrieved documents) memory -- RAG-Sequence vs. RAG-Token, the five-stage baseline pipeline (`GitHubIssuesLoader` -> `RecursiveCharacterTextSplitter` -> embed -> FAISS -> prompt -> generate), and the agentic reframing (retrieval as one tool among several). See [Ch.09](../chapters/09-rag.md). From [`references/rag/foundations.md`](../references/rag/foundations.md) (Lewis et al. 2020 + HuggingFace Agents Course).

### RAGAS {#ragas}
Four reference-free metrics for evaluating RAG without ground truth: Faithfulness, Context Precision, Context Recall, Response Relevancy. See [Ch.09](../chapters/09-rag.md). From [`references/rag/rag-evaluation.md`](../references/rag/rag-evaluation.md) (RAGAS paper/docs).

### ReAct (Thought/Action/Observation) {#react}
The named pattern behind the loop -- a while-loop over Thought (model decides the next step), Action (call a tool with arguments), Observation (tool result appended to the prompt). See [Ch.02](../chapters/02-agent-loop.md). From [`references/harnesses/agent-loop.md`](../references/harnesses/agent-loop.md) (Hugging Face Agents Course).

### Retries {#retries}
Failure recovery on a single outbound model-provider request (distinct from context-overflow handling and cache-prefix reuse): bounded transport + uncapped whole-turn wrapping (OpenCode source-verified), Claude Code `CLAUDE_CODE_MAX_RETRIES`/category list, Copilot CLI per-subsystem hardenings. See [Ch.06](../chapters/06-transport.md). From [`references/harnesses/retries.md`](../references/harnesses/retries.md).

### Runtime machine (SDLC) {#runtime-machine}
The Agentic SDLC Handbook's four-part system -- Model / Harness / Agent Source Code / Client -- with "the harness is the compiler" framing and the inference-per-thread / filesystem-shared asymmetry. See [Ch.10](../chapters/10-sdlc.md). From [`references/sdlc/11-the-runtime-machine.md`](../references/sdlc/11-the-runtime-machine.md) (the handbook says).

## S

### Safe outputs {#safe-outputs}
A read-only agent job handing structured intent to a separate write-scoped GitHub Actions job via two-stage pre-check/apply-time validation -- a job/credential-boundary separation for the deterministic/probabilistic seam, argued as strictly stronger than any in-process permission gate. See [Ch.07](../chapters/07-config-permissions.md), [Ch.12](../chapters/12-advanced.md). From [`references/harnesses/deterministic-orchestration.md`](../references/harnesses/deterministic-orchestration.md) (GitHub Agentic Workflows).

### Sampling / speculative decoding {#sampling}
Shared core sampling params (`temperature`/`top_k`/`top_p`/`repeat_penalty`/`seed`/`num_predict`/`stop`) + grammar-constrained GBNF (token-masking vs. reweighting, auto JSON-Schema->grammar) and draft-then-verify speculative decoding (acceptance-rate dependent). See [Ch.11](../chapters/11-models-engines.md). From [`references/inference-engines/sampling-and-decoding-parameters.md`](../references/inference-engines/sampling-and-decoding-parameters.md), `speculative-decoding.md`.

### Session persistence {#session-persistence}
How a completed session survives a process restart: Claude Code JSONL under `~/.claude/projects/`, Copilot CLI session databases under `~/.copilot/`, OpenCode SQLite with `fork()` + shadow-git `SessionRevert`, pi JSONL tree. Distinct from in-run compaction survival and agent-to-agent handoff. See [Ch.04](../chapters/04-memory-context.md). From [`references/harnesses/session-persistence.md`](../references/harnesses/session-persistence.md).

### Stop-and-parse {#stop-and-parse}
How an action gets out of the model: emit in a predetermined format (JSON, code, function-calling), stop generating, external parser picks the tool and extracts args. Distinct failure modes live at this layer. See [Ch.02](../chapters/02-agent-loop.md). From [`references/harnesses/agent-loop.md`](../references/harnesses/agent-loop.md).

### Streaming {#streaming}
The client/UI-side layer above the wire-level SSE contract: buffering vs. reassembly (waiting for `content_block_stop`) vs. pacing, with delta-coalescing as a performance example. See [Ch.06](../chapters/06-transport.md). From [`references/harnesses/streaming-and-incremental-rendering.md`](../references/harnesses/streaming-and-incremental-rendering.md).

### System prompt design {#system-prompt}
The craft of writing the prompt that makes tools reliably callable: tool-calling-style phrasing, aggressive-language dial-back, parallel-tool-call prompting, canonical vs. exhaustive examples, per-turn assembly (`SystemPrompt.Service`/`buildSystemPrompt()`/three-tier `stable`/`context`/`volatile` Hermes prompt). See [Ch.08](../chapters/08-skills-tools.md). From [`references/harnesses/system-prompt-design-as-craft.md`](../references/harn/-nesses/system-prompt-design-as-craft.md).

## T

### Turn (agent turn) {#turn}
What one turn is -- the unit the harness counts and caps: Claude Code one-Claude-response-with-tool-execution; Copilot CLI exactly one LLM API call (`assistant.turn_start` to `turn_end`); OpenCode primary/subagent step; pi `turn_start` -> `turn_end` with tool execution inside; Hermes one LLM-call-plus-tool-round (and, in docstring, the whole `run_conversation()` call); DeepSeek Cordis plugin driver turn. See [Ch.03](../chapters/03-agent-loop-implementations.md). From [`references/harnesses/agent-loop-implementations.md`](../references/harnesses/agent-loop-implementations.md).

## Backlinks from glossary to defining chapters

| Chapter | Terms defined/heavily used there |
|---------|----------------------------------|
| Ch.01 Topology | agent-topology, harness, reactive/deliberative (see prose) |
| Ch.02 Loop | agent-loop, ReAct, stop-and-parse |
| Ch.03 Implementations | turn, budget (three layers), stop condition |
| Ch.04 Memory & Context | AGENTS.md, memory, instruction-budget, compaction, caching, session-persistence |
| Ch.05 Coordination | orchestration, handoff, fan-out, messaging, coordination design space |
| Ch.06 Transport | llm-api-contract, streaming, retries, model-routing (see prose), configuration (where routing overlaps) |
| Ch.07 Config/Permissions | configuration, permissions, hooks, auth, budget (org layer), safe-outputs |
| Ch.08 Skills & Tools | built-in-tools, built-in-skills, mcp, tool-schema/system-prompt (see prose) |
| Ch.09 RAG | rag, ColBERT, HyDE, CAG, RAGAS, semantic caching (see prose) |
| Ch.10 SDLC | runtime-machine, load-lifecycle, PROSE |
| Ch.11 Models & Engines | model-classification, MoE, quantization, GGUF, KV-cache, batching, inference-engine, sampling |
| Ch.12 Advanced | observability, middleware, deterministic-orchestration, safe-outputs |

---

*Glossary generated 2026-09-12 by `airchon-communicator`. Every anchor above is linked from at least one chapter introduction; every row above links back.*
