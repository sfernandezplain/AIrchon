# References heading-index

Machine-maintained by `airchon-author` via `resources/scripts/build_references_index.py` -- never hand-edited. Regenerated one page-block at a time on every references/*/*.md edit (see `resources/references-index-maintenance.md`); this copy was last fully rebuilt via `bootstrap` mode.

Companion to each area's own `index.md` (topic-level summary) -- this file is section-level (heading text only, no line numbers: a stale heading fails to match and falls back to a normal read; a stale line number would silently point at the wrong content).

## references/harnesses/advanced-planning-and-execution-architectures.md
- 1. Re-confirming the gap, precisely
  - 1.1 Tree-search / MCTS-style planning
  - 1.2 Self-critique / reflection loops -- the one place this check found real, adjacent, shipped features
  - 1.3 Multi-model ensembling per step
  - 1.4 Speculative/predictive tool execution
- 2. The design space: what the wider literature actually proposes
  - 2.1 Tree-of-thought / best-of-N-with-a-verifier / MCTS-style planning
  - 2.2 Self-critique / reflection loops as an internal correctness mechanism
  - 2.3 Multi-model ensembling per step
  - 2.4 Speculative/predictive tool execution
- 3. Why the gap plausibly exists, and what closing it would cost
- 4. A sketch for a from-scratch harness that adopted these mechanisms
- 5. Synthesis
- Sources

## references/harnesses/agent-loop-implementations.md
- 1. Claude Code (Agent SDK docs)
- 2. GitHub Copilot CLI
- 3. OpenCode
- 4. pi
- 5. Hermes Agent (Nous Research)
  - 5.1 The entry point, and a genuine internal vocabulary clash over "turn"
  - 5.2 One iteration: request assembly, the provider call, and the tool-call gate
  - 5.3 Tool dispatch: a segment planner over parallel-safe and sequential-barrier runs
  - 5.4 The natural stop condition, and three distinct nudges that can override it
  - 5.5 Hard caps: iteration budget, a self-clearing grace call, and a real config-default inconsistency
- 6. DeepSeek Harness (DeepSeek AI)
  - 6.1 Turn and step: a two-level loop with an event-sourced session log
  - 6.2 The pre-step gate: rejection, message rewriting, and request-series markers
  - 6.3 The natural stop condition, the turn-stopping checkpoint, and steering reinjection
  - 6.4 Tool dispatch: a concurrency-safe classifier with rolling-pool parallelism
  - 6.5 Hard caps and budget enforcement: maxTokens per request, no documented step-count cap, and a max-tokens turn-end reason
  - 6.6 Compaction: a capability seam, not part of the loop spine
  - 6.7 Subagents: a multi-provider capability seam with continuable conversations
- 7. Comparison
- 8. Sources

## references/harnesses/agent-loop.md
- 1. The loop, as commonly taught
- 2. Observations are appended to context, not returned to a caller
- 3. How an action gets out of the model: stop-and-parse
- 4. Why the vocabulary matters for profiling
- Sources

## references/harnesses/agent-topology.md
- 1. What counts as an "agent" -- convergence and real divergence
- 2. Axis one -- reactive vs. deliberative
- 3. Axis two -- single-agent vs. multi-agent systems
- 4. Axis three -- tool-augmented vs. fully autonomous
- 5. The component decomposition -- "LLM + tools + memory + planning" and its rivals
- 6. Where a "harness" sits relative to a bare agentic system
- 7. Putting the axes together
- Sources

## references/harnesses/auth-and-usage-accounting.md
- 1. Claude Code
  - 1.1 Authentication methods and the login flow
  - 1.2 Credential storage and the six-source precedence stack
  - 1.3 Cost tracking: `/usage`, its `/cost`/`/stats` predecessors, and the statusline
  - 1.4 OpenTelemetry cost and usage metrics
  - 1.5 Budget enforcement: three genuinely distinct mechanisms, at three different layers
  - 1.6 Cloud-provider authentication as a distinct, credential-and-billing bundle
- 2. GitHub Copilot CLI
  - 2.1 Authentication methods and credential storage
  - 2.2 Premium requests: the unit Copilot bills usage in
  - 2.3 Cost/usage observability in the CLI: `/usage`'s own history
  - 2.4 Budget enforcement: GitHub's billing platform, not the CLI itself
- 3. OpenCode
  - 3.1 The `Auth.Service`: credential storage, three credential shapes, and provider-specific OAuth flows
  - 3.2 Cost/usage accounting: a models.dev-priced, per-message, reversible accumulator
  - 3.3 Budget enforcement: none found in the harness proper; a distinct provider-side router in OpenCode Zen only
- 4. pi
  - 4.1 A dual-mode credential store, spanning 29+ named providers
  - 4.2 Credential resolution order, and a `key` field with its own small expression language
  - 4.3 Usage and cost accounting: a structured `Usage` type on every message, no documented spend cap
- 5. Hermes Agent (Nous Research)
  - 5.1 Credential storage: `auth.json`, a layered `.env`/secret-manager ladder, and 100-plus named provider variables
  - 5.2 Credential pools and cross-provider fallback: two named, independent resilience layers
  - 5.3 Nous Portal: a bundled OAuth-and-subscription-billing product, plus a re-exportable subscription proxy
  - 5.4 Usage/cost accounting: `/usage`, `hermes insights`, a per-run JSON artifact, and no in-harness spend ceiling
- 6. DeepSeek Harness
  - 6.1 Two disjoint key spaces: `CredentialRef` (layered, env-var-shaped) and `CredentialKey` (plugin-owned, unlayered)
  - 6.2 The credential file, its 0600 boundary, and an honest limit the maintainers name directly
  - 6.3 OAuth and other human-obtained credentials: the `dsh-authorization` seam, and the `openai-codex` incident it fixed
  - 6.4 A distinct, non-billing auth layer: the Web Host's own launch-token session cookie
  - 6.5 Token/cost tracking: a replay-exact, per-token accounting service that never prices a currency figure
  - 6.6 Budget enforcement: none found in core; a documented recognition (not enforcement) of Claude Code's own budget cap when delegating to it
- 7. Synthesis
- Sources

## references/harnesses/built-in-skills.md
- 1. Claude Code
  - 1.1 Bundled skills -- present in every session by default
  - 1.2 The bundled-skill visibility controls
  - 1.3 First-party skills distributed as an opt-in plugin, not bundled
- 2. GitHub Copilot CLI
  - 2.1 A confirmed, changelog-traced built-in skill
  - 2.2 `configure-copilot` -- a subagent, not a skill, doing adjacent work
  - 2.3 Forge-generated draft skills -- the harness authoring its own skills
  - 2.4 SKILL.md format and discovery, Copilot CLI's documented version
- 3. OpenCode
  - 3.1 No bundled skills -- a purely generic extension point
  - 3.2 SKILL.md format and mechanism, as documented
- 4. pi
  - 4.1 An explicit, named-standard implementation, with a documented, deliberate deviation
  - 4.2 No confirmed bundled skills -- reading like OpenCode's posture, for the same evidentiary reason
  - 4.3 Explicit, first-class cross-harness directory reuse -- the deepest documented instance in this book
  - 4.4 Frontmatter surface: closest to OpenCode's in size, with one field neither other harness's confirmed set names
  - 4.5 Invocation: `/skill:name`, with an explicit model-reliability caveat
- 5. Hermes Agent (Nous Research)
  - 5.1 A second, independently sourced instance of the `agentskills.io` standard
  - 5.2 Loading discipline exposed as named, model-callable tools -- distinctive among every skills mechanism this page has sourced
  - 5.3 Autonomous, in-session skill authorship as an encouraged default behaviour
- 6. DeepSeek Harness (DeepSeek AI)
  - 6.1 Three-layers-of-package architecture: registry, provider, consumer
  - 6.2 Bundled skills -- a single opt-in badge, not a feature suite
  - 6.3 Repository-shipped skills in `.agents/skills/` -- first-party but not "bundled" by the CLI's own definition
  - 6.4 The independent invocation-policy model -- all four quadrants, enforced at every boundary
  - 6.5 Local discovery priority -- six ranked tiers, including the cross-harness `.agents/skills` path
  - 6.6 Frontmatter surface and provider contract
  - 6.7 Session catalog and hot-refresh -- durable, diffed by digest, not by content
- 7. Synthesis -- six different meanings of "built-in"
- Sources

## references/harnesses/built-in-tools.md
- 1. Claude Code
  - 1.1 The full built-in tool table
  - 1.2 Permission rule syntax
  - 1.3 Bash: process model, limits, backgrounding
  - 1.4 Edit: the three-gate check
  - 1.5 Read, Glob, Grep, WebFetch, WebSearch, LSP, Monitor
  - 1.6 What subagents and restricted modes don't get
- 2. GitHub Copilot CLI
  - 2.1 Two different vocabularies: permission "kinds" vs. functional tools
  - 2.2 Permission flags and persistence
- 3. OpenCode
  - 3.1 Built-in tool list
  - 3.2 Permission model
- 4. pi
  - 4.1 Two distinct npm packages behind one name -- resolving this book's own inconsistent spelling
  - 4.2 The canonical built-in tool set: eight tools, named as a closed union in source
  - 4.3 Session-start tool selection, not a per-call permission gate
  - 4.4 `grep`/`find` shell out to real `ripgrep`/`fd` binaries, auto-fetched on demand
  - 4.5 What's absent, by pi's own stated design, and how a user gets it back
- 5. Hermes Agent (Nous Research)
  - 5.1 An order-of-magnitude larger, dynamically-gated surface -- not a fixed table
  - 5.2 File and terminal core: read_file/write_file/patch/search_files, terminal/process
  - 5.3 Cognition and orchestration tools: todo, clarify, execute_code, delegate_task, memory, session_search, cronjob
  - 5.4 Toolset gating is an *availability* question, layered under, not instead of, the approval system
  - 5.5 Platform toolsets: the same product exposes a different tool surface per deployment context
- 6. DeepSeek Harness
  - 6.1 Plugin-packaged tool surface -- not a flat list, but a composed bundle
  - 6.2 The shipped tool packages and their model-visible names
  - 6.3 The filesystem and shell core: four tool packages, one seam
  - 6.4 Profile-driven composition, not a fixed tool set
  - 6.5 The three-waterfall guarded execution pipeline
  - 6.6 Two independent enforcement knobs, bundled into named presets
  - 6.7 What the goal, schedule, todo, and workflow tools do -- orchestration primitives with no single counterpart elsewhere on this page
- 7. Synthesis -- the same twelve jobs, six different tool surfaces
- Sources

## references/harnesses/caching.md
- 1. Claude Code
  - 1.1 The mechanism: exact prefix matching over a growing request
  - 1.2 What invalidates the cache -- and what doesn't
  - 1.3 Cache lifetime (TTL) and where the cache physically lives
  - 1.4 Cache scope: effectively one machine, one directory
  - 1.5 Subagents and forks: separate caches, one exception
  - 1.6 Observability: the two token fields, `/usage`, and OpenTelemetry
  - 1.7 Why usage climbs in a long session -- caching's cost-side implication
  - 1.8 Disabling caching and org-wide policy
  - 1.9 The underlying Anthropic API mechanism (bounded citation)
- 2. GitHub Copilot CLI
  - 2.1 What the docs say the mechanism is
  - 2.2 Cache lifetime: a documented, provider-differentiated TTL
  - 2.3 What invalidates the cache
  - 2.4 Changelog-traced evolution of cache observability
  - 2.5 What is not documented
- 3. OpenCode
  - 3.1 `cache-policy.ts`: a protocol-neutral policy resolved before lowering
  - 3.2 Per-protocol lowering: Anthropic Messages and Bedrock Converse
  - 3.3 OpenAI and Gemini: a deliberate no-op
  - 3.4 Normalized token accounting across providers
  - 3.5 Config surface: none -- this is a programmatic, not user-facing, knob
- 4. pi (`@earendil-works/pi-ai`)
  - 4.1 `CachePolicy`: one `CacheRetention` enum, one resolver function, copied into four protocols
  - 4.2 Anthropic Messages: three placement sites, `"stealth mode"` system-prompt duplication, and a cap respected by construction
  - 4.3 TTL is a caller-declared toggle, not an auth-path inference -- the sharpest contrast with Claude Code
  - 4.4 OpenAI Responses and Chat Completions: `prompt_cache_key`/`prompt_cache_retention`, an explicit opt-out for GPT-5.6+, and a second, independent Anthropic-flavored path for hybrid providers
  - 4.5 Amazon Bedrock Converse: eligibility inferred from the model catalog, not requested by the caller
  - 4.6 Google Generative AI and Vertex: read-only accounting, zero request-side markers
  - 4.7 Session-affinity headers: a caching-adjacent mechanism, not the cache marker itself
  - 4.8 Compaction and branch summaries: an explicit cache opt-out -- the opposite policy from Claude Code
  - 4.9 Observability: per-model cache-rate metadata, a cost-tier interaction, the Anthropic-only `cacheWrite1h` split, and an opt-in transcript notice
  - 4.10 The configuration surface, summarized
- 5. Hermes Agent (Nous Research)
  - 5.1 Three documented layers, and where they disagree
  - 5.2 The four-breakpoint budget: a stable-prefix-aware layout and a legacy fallback
  - 5.3 Route eligibility: one function resolving `(should_cache, use_native_layout)` across a dozen wire shapes
  - 5.4 TTL resolution, and a wire-measured clamp that contradicts the vendor's own published docs
  - 5.5 Placement mechanics: role-aware markers, a builder-declared sub-message boundary, and failover-safe re-decoration
  - 5.6 Model-identity cache-key sensitivity, and the mixture-of-agents caching bug this page can now explain precisely
  - 5.7 Mechanisms that are not an Anthropic-style marker at all
  - 5.8 Interaction with memory, compaction, and user-facing observability
- 6. Synthesis
- Sources

## references/harnesses/configuration.md
- 1. Claude Code
  - 1.1 Scopes and file locations
  - 1.2 Major key categories
  - 1.3 CLI flags and environment variables as session-level layers
  - 1.4 Reload semantics: what applies without a restart
  - 1.5 Migration and structural history, traced through `CHANGELOG.md`
  - 1.6 Cross-reference: what this section deliberately does not cover
- 2. GitHub Copilot CLI
  - 2.1 Configuration directory layout
  - 2.2 `settings.json` key categories
  - 2.3 Repository, local, and managed layers
  - 2.4 MDM-managed settings
  - 2.5 CLI flags and environment variables
  - 2.6 Structural and migration history, traced through `changelog.md`
- 3. OpenCode
  - 3.1 Config files and merge order
  - 3.2 Major schema keys
  - 3.3 Variable substitution inside config files
  - 3.4 Permission configuration schema
  - 3.5 What the docs page explicitly does not expose
- 4. pi
  - 4.1 Two scopes, no managed/enterprise tier, and a stated recursive-merge rule
  - 4.2 Project trust: a config-loading gate layered in front of the project scope
  - 4.3 Major settings-file key clusters
  - 4.4 CLI flags and environment variables
  - 4.5 Reload semantics
  - 4.6 The worked project-override example, and what it demonstrates about §4.1's merge rule
- 5. Hermes Agent (Nous Research)
  - 5.1 `~/.hermes/` directory layout and the `hermes config` command surface
  - 5.2 Configuration precedence, and a documented inversion at the managed-scope boundary
  - 5.3 Managed scope: filesystem-permission-enforced, leaf-key policy pinning
  - 5.4 Environment-variable substitution inside `config.yaml`, and Cursor/Claude-config interop
  - 5.5 CLI flags, environment-variable overrides, and API-key/model-provider resolution
- 6. Synthesis
- Sources

## references/harnesses/context-compression.md
- 1. Claude Code
  - 1.1 The two-phase mechanism, stated directly
  - 1.2 What the summary keeps and drops
  - 1.3 Trigger thresholds -- what is documented and what is not
  - 1.4 Anti-thrash guard and model-fallback interaction
  - 1.5 Hooks and observability
  - 1.6 Manual levers
- 2. GitHub Copilot CLI
  - 2.1 A visible evolution, not one static mechanism
  - 2.2 What is not documented
  - 2.3 Observability
- 3. OpenCode
  - 3.1 Two implementations exist in this repository -- flagged, not conflated
  - 3.2 Overflow detection: the token budget
  - 3.3 Two independently-scheduled passes, not one
  - 3.4 `prune()`: eviction-only, no LLM call
  - 3.5 `process()`: the summarization pass, in detail
  - 3.6 Config surface -- documented vs. actually consumed
- 4. pi
  - 4.1 Two named mechanisms sharing one summary format, not one mechanism with two names
  - 4.2 Trigger and cut-point selection: turn-boundary-first, with an explicit split-turn fallback
  - 4.3 The summary itself: a fixed template, explicitly *not* stated to be anchored/incremental
  - 4.4 Extension hooks: cancel, replace, or fully author the summary yourself
  - 4.5 Overflow recovery is a *separate* code path from ordinary threshold compaction, and interacts with retries specifically
  - 4.6 Settings surface
- 5. Hermes Agent
  - 5.1 Two independently-thresholded layers, and a pluggable engine underneath the primary one
  - 5.2 Trigger thresholds: a percentage-of-window default, per-model overrides, and a provider-route-specific autoraise
  - 5.3 The built-in engine's four-phase algorithm, and what "iterative" means here
  - 5.4 Tail retention: a `legacy` verbatim mode, and a `lean` default that trades verbatim tail for a denser summary
  - 5.5 Micro-compaction: an opt-in, per-turn, amortized alternative to batch compaction
  - 5.6 Provider-native server-side compaction: a compaction owner outside Hermes' own code, for two specific routes
  - 5.7 No intermediate pressure warnings, by explicit design choice
  - 5.8 Settings surface, and session-identity continuity across a compaction
- 6. DeepSeek Harness
  - 6.1 A capability-seam architecture: compaction is one swappable plugin, not part of the loop spine
  - 6.2 The singleton token meter: one measurement fold prices every decision
  - 6.3 The log-recorded bracket: a transaction, not just a pass
  - 6.4 Tool-result pruning: a separate, optional, deterministic companion that can skip the LLM call entirely
  - 6.5 Range selection: head-anchored, priced-tail retention, and tool-pairing boundaries
  - 6.6 Summarization: a KV-cache-reusing one-shot, with an explicit incremental-update instruction
  - 6.7 Spill storage: proactive oversized-output offloading before compaction is triggered
  - 6.8 Two trigger paths: step-boundary pressure and context-overflow recovery
  - 6.9 The summarize() subclass hook and the summary-failure contract
  - 6.10 Manual compaction: idle-only, queued by the agent loop itself
  - 6.11 Config surface
- 7. Synthesis
- Sources

## references/harnesses/context-retrieval-and-agentic-search.md
- 1. The design space, in general terms
  - 1.1 Two competing retrieval philosophies
  - 1.2 Why this specific debate has a live literature behind it
  - 1.3 A sourcing note on what follows (§1.4-§1.11)
  - 1.4 Naive RAG baseline and the advanced-RAG refinements it is measured against
  - 1.5 Vector-database-specific indexing and retrieval patterns
  - 1.6 Semantic caching as a retrieval-adjacent optimization
  - 1.7 Structured generation as a retrieval-adjacent reliability technique
  - 1.8 Retrieval over unstructured and mixed-format data
  - 1.9 Knowledge-graph RAG: graph traversal as an alternative and complementary retrieval strategy
  - 1.10 A retrieval-agent counter-example, and why it sharpens rather than complicates §1.1's distinction
  - 1.11 RAG evaluation methodology
- 2. Claude Code
  - 2.1 A documented reversal, not a default that was never tried
  - 2.2 What actually ships instead, and where RAG is left as an opt-in seam
- 3. GitHub Copilot CLI
  - 3.1 Copilot CLI's own code-discovery tools are grep/glob-equivalent, not embeddings-based
  - 3.2 A GitHub embeddings feature exists -- for a different product surface
- 4. OpenCode
  - 4.1 The documented and source-confirmed tool surface has no retrieval index
  - 4.2 Repeated, unresolved feature requests -- and the ecosystem filling the gap itself
- 5. pi
  - 5.1 Resolving the package/repo naming question first
  - 5.2 The built-in tool surface: `grep` and `find`, no retrieval index anywhere in it
  - 5.3 No embeddings/vector dependency in either package's own dependency graph, and no such feature in 5,625 lines of changelog
  - 5.4 A stated design philosophy of explicit minimalism, and no MCP seam either
  - 5.5 The maintainer's own on-record rejection of an embeddings/RAG contribution
- 6. Hermes Agent (Nous Research)
  - 6.1 The core code-discovery primitive: one ripgrep-backed tool fusing grep, glob, and `ls`
  - 6.2 Progressive AGENTS.md discovery injected into tool *results*, not the system prompt -- a materially different mechanism from every other harness on this page
  - 6.3 On-demand recursive directory traversal via `@folder:`, sitting beside `@file:`/`@diff:`/`@staged:`/`@url:` as explicit, user-typed context injection
  - 6.4 A deliberately bounded, non-exhaustive workspace snapshot at session start
  - 6.5 Two embeddings-based retrieval mechanisms that exist in Hermes today -- and are, on inspection, scoped away from source-code search, the same pattern Copilot CLI's `dynamicRetrieval` already established for this page
  - 6.6 The LSP tier is a post-write diagnostics gate, not a code-navigation or discovery tool -- a real point of divergence from Claude Code's and OpenCode's own LSP mechanisms
- 7. DeepSeek Harness (DeepSeek AI)
  - 7.1 The code-discovery tool surface: packaged ripgrep behind `glob`/`grep`, no embeddings, no vector index, no shell layer
  - 7.2 The LSP seam: genuine semantic navigation, not just post-write diagnostics
  - 7.3 The filesystem seam is pluggable -- and no code-search embedding is implemented on any provider
  - 7.4 A real, shipped full-text search exists -- over session history, not source code, and off by default
  - 7.5 The "everything is a plugin" architecture creates a first-party hybrid seam that no other harness on this page documents this explicitly
  - 7.6 No trace of embeddings, vector-index, or semantic-code-search in the repository tree, package sources, or dependency declarations
- 8. Synthesis and the hybrid-as-ceiling question
  - 8.1 Convergence, restated precisely
  - 8.2 Is embeddings-for-candidates + agentic-search-for-verification the ceiling nobody built?
- Sources

## references/harnesses/deterministic-orchestration.md
- 1. The general concept: "workflows" vs. "agents" as a deliberate axis, not a spectrum LangGraph merely occupies
  - 1.1 Where Conductor sits on the same axis
- 2. The graph API: `StateGraph`, state/reducers/channels, nodes, edges, `Command`, `Send`
- 3. Persistence and durable execution: checkpointers, threads, time travel, forking
  - 3.1 Cross-reference: how this compares to the three CLI harnesses' own session stores
- 4. Human-in-the-loop: `interrupt()`, `GraphInterrupt`, and resuming via `Command`
- 5. Fault tolerance: per-node retries, timeouts, and error handlers
- 6. Multi-agent patterns: network, supervisor, hierarchical, and swarm
  - 6.1 Cross-reference: mapping LangGraph's four named patterns onto this book's own topology axis
- 7. Synthesis: LangGraph against this book's existing harness pages
- 8. Conductor's authoring surface: a declarative YAML workflow, not a code-built graph
  - 8.1 A genuinely new general concept: the orchestrator as a layer above other harnesses this book documents
  - 8.2 Routing, typed outputs, and structured-output repair
- 9. Conductor's human-in-the-loop surface: four distinct primitives, not one
- 10. Fault tolerance and budget: per-agent retry, timeouts, and two-mode cost enforcement
- 11. Fleet-level supervision: run records, the Fleet Manager TUI, and async mid-run guidance
- 12. Workflow registry, sub-workflows, plugins, and skills
- 13. Cross-instance synthesis: what Conductor adds, and what it just renames
- 14. GitHub Agentic Workflows' authoring surface: Markdown compiled to a hardened GitHub Actions workflow
  - 14.1 The `engine:` property: dispatching a step through another complete harness's own real CLI, extended to a fifth and sixth instance
- 15. Safe outputs: a job/credential-boundary capability separation, not an in-process permission gate
- 16. Third-instance synthesis: what GitHub Agentic Workflows adds beyond LangGraph and Conductor
- Sources
  - Conductor sources (sections 8-13, all fetched this session, 24 August 2026)
  - GitHub Agentic Workflows sources (sections 14-16, all fetched this

## references/harnesses/evals-and-testing-a-harness.md
- 1. General concepts: what "testing a harness" decomposes into
- 2. Claude Code
  - 2.1 Anthropic's published evals guidance for agents built on the Claude Agent SDK
  - 2.2 The evaluator-agent pattern, and why harness design is inseparable from capability evals
  - 2.3 Headless mode as documented scaffolding for building an external eval/CI harness
  - 2.4 The changelog's own "regression" vocabulary, read as proxy evidence
- 3. GitHub Copilot CLI
  - 3.1 Documented non-interactive/programmatic execution
  - 3.2 Changelog-traced scaffolding for external, script-driven verification
  - 3.3 The changelog's own regression vocabulary
- 4. OpenCode
  - 4.1 The record/replay cassette architecture
  - 4.2 The golden-scenario regression matrix: one scenario, run against ~18 provider/model targets
  - 4.3 Unit-level correctness tests on the reassembly algorithm itself
  - 4.4 Event-serialization regression tests, including a schema-backward-compatibility check
  - 4.5 Integration-level tests: the whole session loop against a recorded real transcript
  - 4.6 Route-coverage: a dedicated DSL-driven HTTP API exerciser
  - 4.7 The CI pipeline gluing these layers together
- 5. pi
  - 5.1 Resolving this book's own inconsistent `pi-ai`/`pi-coding-agent` naming: both are correct, for different packages
  - 5.2 The CI-safe deterministic layer: a synthetic "faux" model provider, not recorded real-provider traffic
  - 5.3 Issue-numbered regression tests, and the broader per-provider/per-package test surface
  - 5.4 `packages/evals`: a dedicated, `vitest-evals`-based model-backed behavioral eval package, separate from the CI-safe suite above
  - 5.5 The CI pipeline, and evals' deliberate exclusion from it
  - 5.6 Environment isolation for the test run itself
- 6. Hermes Agent (Nous Research)
  - 6.1 Repository shape and CI orchestration: a single change-classifying gate over several distinct language surfaces
  - 6.2 A hermetic, autouse pytest fixture, and per-file process isolation as the default
  - 6.3 Synthetic model-response fixtures authored inline per test, not a shared cassette or fake-provider package
  - 6.4 Crash-safe transcript-replay regression tests: a different "replay" than OpenCode's or pi's
  - 6.5 The `evals/` directory: a first-party, PR-driven family of A/B benchmark harnesses, and the "hermesbench discipline"
  - 6.6 `scripts/toolperf_abeval`: a trace-scored core-toolset A/B battery, and two honestly-disclosed gaps
- 7. Synthesis
- Sources

## references/harnesses/fan-out.md
- 1. Claude Code
  - 1.1 In-conversation subagent fan-out -- the "Run parallel research" pattern
  - 1.2 A second, coarser layer -- background agents (`claude agents`)
  - 1.3 A third, scripted layer -- the Workflow tool's `pipeline()`
- 2. GitHub Copilot CLI
  - 2.1 The substrate: parallel tool calls within one assistant turn
  - 2.2 Subagent fan-out: custom agents plus numeric depth/concurrency limits
  - 2.3 `/fleet` -- conditional parallel dispatch atop the same substrate
  - 2.4 A third, coarser layer -- multiple concurrent sessions
- 3. OpenCode
  - 3.1 The prompted convention: batch multiple Task calls in one message
  - 3.2 What actually executes concurrently underneath: independent Effect fibers, not a queue
  - 3.3 Depth and permission checks apply per call, not once per batch
- 4. DeepSeek Harness
  - 4.1 Two distinct spawning paths: one-shot delegation vs. continuable children
  - 4.2 Context inheritance is a per-provider descriptor, and it is explicitly not authority inheritance
  - 4.3 Concurrency: a stated qualitative guard, no numeric ceiling
  - 4.4 Using the no-global-cap finding as a reasoning aid for Claude Code's own undocumented ceiling -- BEST CURRENT UNDERSTANDING, UNCONFIRMED
- 5. Hermes Agent (Nous Research)
  - 5.1 `delegate_task`: isolated context, restricted toolset, and a *separate terminal session* per subagent
  - 5.2 Bot Mode: named specialist profiles coordinating in a shared group chat
- 6. pi
  - 6.1 The real finding: no subagent/fan-out mechanism ships in pi's core at all
  - 6.2 The `subagent` example: a first-party reference implementation, not a toy
  - 6.3 Dispatch mechanics: three modes, one OS process per call, a worker-pool limiter
  - 6.4 Context inheritance: none by default -- `--no-session` means a genuinely fresh process
  - 6.5 What is absent: no documented recursion-depth guard
- 7. Synthesis
- Sources

## references/harnesses/handoff-mechanism.md
- 1. Claude Code
  - 1.1 Subagents (the `Agent` tool, née `Task`)
  - 1.2 Resuming a subagent -- a stateful handoff, not a one-shot
  - 1.3 Forks -- the opposite handoff shape
  - 1.4 Concurrency, depth, and session-wide limits
  - 1.5 Agent teams -- peer-to-peer handoff, not parent-to-child
- 2. GitHub Copilot CLI
  - 2.1 Local custom-agent delegation (subagents)
  - 2.2 `/delegate` -- handoff to a different machine entirely
  - 2.3 A genuinely different product's handoff feature -- named `handoffs`, and out of scope here
- 3. OpenCode
  - 3.1 A subagent is a real, persisted child session, not just a context copy
  - 3.2 Permission handoff is a strict subset, not an inheritance
  - 3.3 Foreground vs. background handoff, and what actually returns
- 4. pi
  - 4.0 A naming correction this book can now make with confidence: two real, distinct packages, not an inconsistency to resolve
  - 4.1 The headline finding: no native, built-in subagent or multi-agent handoff mechanism ships in the product at all
  - 4.2 The `subagent/` example: a genuinely separate OS process per delegated task, not an in-process child session
  - 4.3 The `handoff.ts` example: a fundamentally different shape -- a new session, not a spawned agent
  - 4.4 What this leaves out relative to this book's other harness sections, stated plainly
- 5. Hermes Agent (Nous Research)
  - 5.1 `delegate_task`: an in-process child `AIAgent`, not a spawned process -- fresh context, narrowed both ways
  - 5.2 Depth, concurrency, and durability: flat by default, no hard concurrency ceiling, and "durable" describes delivery, not resumable execution
  - 5.3 Compaction is an in-place rewrite by default -- and the one configurable path back to a genuine new session record
  - 5.4 `/compress` vs `/new`: the explicit, human-triggered version of the same question -- and Bot Mode's own carve-out
  - 5.5 `/handoff <platform>`: a literal command sharing this page's own name, but a same-session cross-surface move, not agent-to-agent delegation
- 6. Synthesis
- Sources

## references/harnesses/hooks-lifecycle-extensibility.md
- 1. Claude Code
  - 1.1 What a hook is, and the three firing cadences
  - 1.2 The full event catalogue
  - 1.3 Common input fields and per-event input shape
  - 1.4 Exit-code and JSON-output decision semantics
  - 1.5 Configuration structure, handler types, matchers
  - 1.6 Security posture and documented safeguards against runaway hooks
  - 1.7 Changelog-traced history
- 2. GitHub Copilot CLI
  - 2.1 Three surfaces, one shared hook vocabulary, real behavioral differences
  - 2.2 The 14 documented events, dual-named
  - 2.3 Exit-code semantics, and the one deliberate fail-closed exception
  - 2.4 Configuration file locations and precedence
  - 2.5 Hook entry types
  - 2.6 Matchers, and the Claude-tool-name compatibility layer
  - 2.7 Changelog-traced history
- 3. OpenCode
  - 3.1 No "hooks," a "plugin" that returns a "hooks object" -- and two distinct extension surfaces
  - 3.2 The named hooks, source-verified in full
  - 3.3 A documentation/source naming mismatch, flagged rather than smoothed over
  - 3.4 `tool.execute.before`/`tool.execute.after`, confirmed wired end to end
  - 3.5 Plugin loading: files, npm packages, load order, dependencies
  - 3.6 A structural absence worth stating plainly: no dedicated, blocking session-lifecycle hook
- 4. DeepSeek Harness
  - 4.1 Cordis: registration as a reversible effect, not a fire-and-forget listener
  - 4.2 House rules that read like this book's own grounding discipline, applied to code
  - 4.3 An honest, checked-this-session gap: no confirmed tool-execution hook catalogue
  - 4.4 Using Cordis's disposer pattern as a reasoning aid for the two closed harnesses -- BEST CURRENT UNDERSTANDING, UNCONFIRMED
- 5. pi
  - 5.1 In-process TypeScript modules, not a subprocess contract -- architecturally closer to OpenCode's and DeepSeek's plugins than to Claude Code's or Copilot CLI's hooks
  - 5.2 The fullest documented lifecycle-event diagram of any harness in this book
  - 5.3 The `tool_call` event: mutate-in-place semantics with an explicit no-revalidation guarantee
  - 5.4 `before_agent_start`: the deepest documented system-prompt introspection hook in this book
  - 5.5 Provider-request-layer events: a fourth vantage point on the wire
  - 5.6 Everything else this page's other sections would ask about, briefly
- 6. Hermes Agent (Nous Research)
  - 6.1 Three distinct hook systems under one shared name
  - 6.2 Shell hooks: the exact same wire protocol as Claude Code's, independently arrived at
  - 6.3 `fail_closed`, a persisted consent allowlist, and outbound webhooks
- Synthesis
- Sources

## references/harnesses/instruction-context-budget.md
- 1. Claude Code
  - 1.1 The trap: imports do not save context
  - 1.2 Tier 2a -- `.claude/rules/` with `paths:` frontmatter
  - 1.3 Tier 2b -- nested `CLAUDE.md` in subdirectories
  - 1.4 Tier 3 -- skills, the cheapest place to put procedures
  - 1.5 Trimming levers on the tier-1 file itself
  - 1.6 Measuring what actually loaded
  - 1.7 The cost of laziness
- 2. GitHub Copilot CLI
  - 2.1 What files exist to split into
  - 2.2 The scoping mechanism: `applyTo:` frontmatter
  - 2.3 Tier 3 -- skills
  - 2.4 Measuring and toggling
- 3. OpenCode
  - 3.1 The trap does not apply the same way: tier 1 is re-read every turn, not frozen at session start
  - 3.2 What tier 1 actually contains, and the absence of a path-scoped tier
  - 3.3 A nearby-instruction-file auto-attach mechanism, source-verified, distinct from tier 1 and tier 3
  - 3.4 Tier 3 -- skills
  - 3.5 Measuring and toggling
- 4. pi
  - 4.1 One monorepo, two real packages -- both spellings elsewhere in this book are correct
  - 4.2 Tier 1: the `AGENTS.md`/`CLAUDE.md` context-file hierarchy, read once at session start or on `/reload`
  - 4.3 System prompt shape: a small fixed template, not an embedded corpus
  - 4.4 Tool-schema footprint: four default tools, one-line schema descriptions throughout
  - 4.5 A genuinely distinct lazy/deferred-schema mechanism: `pi.registerTool()` + `pi.setActiveTools()`
  - 4.6 Skills: the same invoke-only tier, an XML index rather than JSON or a truncated string
  - 4.7 No path-scoped tier, and no nearby-file auto-attach on read -- a source-verified negative finding
  - 4.8 Measuring and toggling
- 5. Hermes Agent (Nous Research)
  - 5.1 Three system-prompt cache tiers -- a cache-stability axis, not the lazy-load axis this page's tier-1/2/3 vocabulary otherwise asks about
  - 5.2 Context Files carry a source-verified, dynamically-scaled truncation cap, with the reconstruction instruction delivered directly into the model's own context
  - 5.3 The compression threshold governing when the wider conversation (not the Context File tier specifically) gets summarized -- source-verified, with three independent override layers
  - 5.4 Measuring what actually loaded: `/context`, an explicitly "Claude Code-style" glyph grid across eight budget categories, plus a per-skill/per-toolset drill-down
  - 5.5 Iteration budget: a distinct, non-token axis, worth flagging as a false cognate rather than folding into the token-budget discussion above
- 6. DeepSeek Harness (DeepSeek AI)
  - 6.1 The two kinds of model-facing text -- `PromptSection` vs. `PromptContext` -- and why the distinction matters for budget
  - 6.2 Workspace instructions (`AGENTS.md`/`CLAUDE.md`): a hard byte budget with content-priority truncation, touch-driven discovery of nested files, and no path-scoped tier
  - 6.3 Prompt sections: per-step assembly, scoped shadowing, and the `complete` override
  - 6.4 The compaction budget: a ratio-based trigger against a route-priced token meter, with per-model overrides
  - 6.5 Skills: the catalog is a model-facing `<available_skills>` block with a configurable description cap; the body loads via the `skill` tool
  - 6.6 The scoping and registry layer model -- a shared primitive that governs both prompt assembly and skill tooling
  - 6.7 The doc-budgeting standard -- a wordcount ceiling on the harness's own documentation, not on runtime instruction content
  - 6.8 Measuring what actually loaded
- 7. Synthesis
- Sources

## references/harnesses/inter-agent-messaging.md
- 1. Claude Code
  - 1.1 `SendMessage` is the one tool, used two different ways
  - 1.2 Addressing: agent ID vs. agent name, and the name-collision guard
  - 1.3 The mailbox: file-based, push-delivered, self-healing on malformed entries
  - 1.4 Provenance tagging and the permission-relay firewall
  - 1.5 Structured protocol messages: a second layer above plain-text task direction
  - 1.6 Idle notifications and hooks as the messaging-adjacent extensibility point
- 2. GitHub Copilot CLI
  - 2.1 No documented peer-to-peer channel -- messaging is lifecycle events plus a final result
  - 2.2 `/fleet`: coordination through shared state, not a messaging protocol
- 3. OpenCode
  - 3.1 There is no separate "inter-agent message" type -- agent-to-agent communication is ordinary message writes to a session
  - 3.2 The message/part schema itself, source-verified
  - 3.3 Transport: a real server-sent-events bus, not an abstraction
- 4. pi
  - 4.1 There is no core multi-agent primitive -- "subagents" are a shipped, opt-in reference *example*, not a built-in tool
  - 4.2 The pattern the reference extension actually implements: a spawned OS process, not a session or a mailbox
  - 4.3 Sequencing multiple subagents is client-side string substitution, not a message protocol
  - 4.4 A related-but-distinct mechanism worth naming to avoid confusion: `pi.events` is intra-process, not inter-agent
  - 4.5 The naming question resolved
- 5. Hermes Agent (Nous Research)
  - 5.1 `delegate_task` results: a background handle now, the summary posted back as a new message later
  - 5.2 The `subagent.*` gateway event stream: push-delivered progress telemetry, never the message the parent LLM actually receives
  - 5.3 `message_agent`: a validated, server-attributed send tool that replaced an earlier shell-out protocol
  - 5.4 Local delivery is a full agent turn, not a mailbox write -- and reuses Hermes' own generic background-process primitive
  - 5.5 Cross-connection delivery: a durable file-based envelope queue with TTL expiry and a typed failure-reason taxonomy
  - 5.6 Group chats: voluntary peer participation, not addressed one-to-one messaging
- 6. DeepSeek Harness (DeepSeek AI)
  - 6.1 The `Agent` inbox: two targets, three delivery modes, the shared primitive everything builds on
  - 6.2 Continuable subagents: the parent→child direction is `followup()`, not a mailbox
  - 6.3 The child→parent report direction: `reportFrom()`, a separate tool, a separate delivery mode
  - 6.4 Agent Teams: a durable, log-backed mailbox with de-duplication, replay, and a shared task DAG
  - 6.5 Provenance: three distinct attribution kinds, enforced at the type level
  - 6.6 The event matrix: which packages produce and consume inter-agent messaging events
- 7. Synthesis
- 8. Sources

## references/harnesses/llm-api-contract.md
- 1. The Anthropic Messages API contract
  - 1.1 Request shape
  - 1.2 Roles and the messages array
  - 1.3 The content-block vocabulary
  - 1.4 The response object and the `stop_reason` enumeration
  - 1.5 Streaming: the SSE event sequence
- 2. The OpenAI Responses API contract (and where Chat Completions differs)
  - 2.1 Roles and tool-call shape (Responses API, VERIFIED)
  - 2.2 `finish_reason` (VERIFIED, as documented on this page)
  - 2.3 Streaming (Responses API, VERIFIED)
  - 2.4 Chat Completions' classic shape (BEST CURRENT UNDERSTANDING, UNCONFIRMED)
- 3. How each harness sits on top of this layer
  - 3.1 Claude Code (Claude Agent SDK)
  - 3.2 GitHub Copilot CLI
  - 3.3 OpenCode
  - 3.4 DeepSeek Harness
  - 3.5 pi (`@earendil-works/pi-ai`)
  - 3.6 Hermes Agent (Nous Research)
- 4. Synthesis
- Sources

## references/harnesses/mcp-integration.md
- 1. Claude Code
  - 1.1 Config sources and scopes
  - 1.2 Transports
  - 1.3 Registration CLI
  - 1.4 Environment-variable expansion
  - 1.5 What a stdio server receives at spawn time
  - 1.6 Tool-calling semantics
  - 1.7 Beyond tools
- 2. GitHub Copilot CLI
  - 2.1 Config sources and precedence
  - 2.2 Config format
  - 2.3 Registration CLI and interactive management
  - 2.4 Tool-calling semantics
- 3. OpenCode
  - 3.1 Config, scopes, and the two transport shapes
  - 3.2 OAuth: automatic discovery, dynamic client registration, and a CLI-driven auth flow
  - 3.3 Tool naming, namespacing, and pagination -- source-verified
  - 3.4 Capability negotiation: `roots` enabled, `sampling`/`elicitation` commented out despite closed tracking issues
  - 3.5 Per-tool and per-agent enforcement: config, not a separate MCP-specific permission system
- 4. Hermes Agent (Nous Research)
  - 4.1 Discovery, config, and transports
  - 4.2 Tool namespacing, filtering, and dynamic re-discovery
  - 4.3 Tool-result sanitisation
- 5. pi (Earendil Works)
  - 5.1 Package-name resolution: two real, differently-scoped packages in one monorepo, not an inconsistency
  - 5.2 No built-in MCP client -- an explicit, stated design choice
  - 5.3 The ecosystem's de facto answer: `pi-mcp-adapter` and sibling extension packages
- 6. DeepSeek Harness (DeepSeek AI)
  - 6.1 Architecture: a plugin bridge, not a core feature
  - 6.2 Config format and transport types
  - 6.3 Environment scrubbing for stdio
  - 6.4 Connection lifecycle, reconnection, and `list_changed` re-sync
  - 6.5 Tool naming: `mcp__<serverName>__<rawName>` with collision-safe normalization
  - 6.6 Tool execution semantics
  - 6.7 What is not bridged
- 7. Synthesis -- what actually differs
- Sources

## references/harnesses/mcp-supply-chain-trust.md
- 1. Three separable trust questions, and why "approved once" answers only one of them
- 2. What the MCP specification's own security guidance says
  - 2.1 Local MCP Server Compromise -- the section closest to this page's brief
  - 2.2 Tool annotations: the spec's own admission that trust has to come from somewhere else
  - 2.3 Adjacent, but distinct: OAuth-era risks the spec does cover in depth
  - 2.4 A protocol-level design decision with direct supply-chain consequences: the stdio RCE finding
- 3. Named attack taxonomy: poisoning, shadowing, squatting, and the rug pull
- 4. The registry layer: identity verification is not code vetting
  - 4.1 The official MCP Registry -- what it verifies, and what it explicitly declines to
  - 4.2 GitHub's own registry and custom-registry features: gating, not vetting
- 5. Claude Code
  - 5.1 No built-in registry; a narrower, explicitly-scoped review for connectors specifically
  - 5.2 Administrator-side gating: `managed-mcp.json`, allowlists, and denylists
  - 5.3 The consent event, and what happens to it after the server changes
  - 5.4 The sandbox does not cover MCP servers by default -- a precise, documented boundary
- 6. GitHub Copilot CLI
  - 6.1 "Curated by default" is a context-budget decision, not a security vetting claim
  - 6.2 The registry and custom-registry findings from §4.2, restated in this context
  - 6.3 Where Copilot CLI genuinely differs: sandboxing local MCP servers is on by default
- 7. OpenCode
  - 7.1 No registry, and no MCP-specific trust layer separate from the general permission engine
  - 7.2 The consequence, inherited directly from the general sandboxing finding
- 8. pi
  - 8.1 A naming note this session resolved: `@earendil-works/pi-ai` and `@earendil-works/pi-coding-agent` are both correct
  - 8.2 The finding this page's brief anticipated: pi ships no MCP support at all
  - 8.3 What actually happens when a user adds MCP support anyway: the package-installation trust model, unmodified
  - 8.4 The consequence for blast radius: no sandbox, MCP-bridging extension included
- 9. Hermes Agent (Nous Research)
  - 9.1 A genuine registry-adjacent finding this page had not sourced for any other harness: a PR-reviewed catalog, not merely a curated listing
  - 9.2 Tool-level allowlisting and stdio credential isolation as containment-adjacent, not identity- or code-safety, controls
  - 9.3 Continuity (Q3): two Hermes-specific update pathways, cutting in opposite directions
  - 9.4 Prompt-injection-shaped mitigations layered around, not inside, the MCP client
  - 9.5 No OS-level containment specific to MCP server processes -- confirming the pattern already found for Claude Code, OpenCode, and pi
- 10. DeepSeek Harness
  - 10.1 No registry; `serverName` is local configuration, not a trusted identity
  - 10.2 Tool schemas pass through unmodified: the "garbage-in-garbage-out" boundary
  - 10.3 Continuity (Q3): automatic re-sync on `notifications/tools/list_changed`, with no re-approval
  - 10.4 Environment scrubbing: the one MCP-specific supply-chain mitigation
  - 10.5 The sandbox exists for Bash and FS but does not wrap MCP server processes
- 11. Synthesis
- Sources

## references/harnesses/memory-management.md
- 1. Claude Code
  - 1.1 Two mechanisms, not one
  - 1.2 CLAUDE.md: locations and load order
  - 1.3 Imports and the AGENTS.md question
  - 1.4 `.claude/rules/` -- the path-scoped tier
  - 1.5 Auto memory: the file-based learned-preferences store
  - 1.6 How it actually reaches the model
  - 1.7 Compaction interaction -- the load-bearing table
  - 1.8 Mid-session edits: is an edited CLAUDE.md re-read?
  - 1.9 Session-level persistence (distinct from memory)
- 2. GitHub Copilot CLI
  - 2.1 Instruction files (the file-based tier)
  - 2.2 Copilot Memory: a real, server-side memory service
  - 2.3 Session persistence and resume
  - 2.4 Compaction on Copilot CLI
  - 2.5 Mid-session edits on Copilot CLI
- 3. OpenCode
  - 3.1 No native agent-authored memory tool -- a real, source-verified absence
  - 3.2 The persistent-instruction tier is `AGENTS.md`, purely human-authored -- and re-read from disk every turn
  - 3.3 A nearby-file auto-attach mechanism, distinct from tier 1 and structurally closest to Claude Code's own nested-CLAUDE.md behavior
  - 3.4 Skills, briefly, and what they are not
  - 3.5 Session-level persistence (distinct from memory)
- 4. pi
  - 4.1 No agent-authored memory tool -- a real, source-verified absence, and a resolved naming question
  - 4.2 The persistent-instruction tier: `AGENTS.md`/`CLAUDE.md` discovery, first-match-per-directory precedence, and worktree-shadow dedup
  - 4.3 SDK-level programmatic control over the same tier: `agentsFilesOverride`
  - 4.4 `SYSTEM.md`/`APPEND_SYSTEM.md`: a materially different injection point than `AGENTS.md`/`CLAUDE.md`
  - 4.5 Mid-session edits: `/reload`, a third, distinct answer among the harnesses this page documents
  - 4.6 Session-level persistence (distinct from memory)
- 5. Hermes Agent (Nous Research)
  - 5.1 `MEMORY.md`/`USER.md`: two bounded files, hard caps, no silent truncation
  - 5.2 A closed, post-turn learning loop feeding both memory and skills
  - 5.3 FTS5 cross-session search: a second, independent memory channel
  - 5.4 `SOUL.md`: a persona file pinned to a stated prompt position
  - 5.5 Context-file discovery: naming other harnesses' own conventions directly
- 6. DeepSeek Harness
  - 6.1 No project instruction-file convention at all -- persona is a config string, not a discovered markdown file
  - 6.2 No native agent-authored memory tool -- third-party MCP memory servers, shipped disabled, explicitly not endorsed
  - 6.3 Session-level persistence and instruction-adjacent config -- cross-referenced, not re-derived
- 7. Synthesis
- Sources

## references/harnesses/middleware-composed-agent-harnesses.md
- 1. Verifying the category: three layers, not a LangGraph-alternative
- 2. The general concept: middleware as an agent-loop extension mechanism, distinct from event-dispatch hooks
- 3. Construction vs. execution: what `create_deep_agent()` actually assembles
- 4. The default middleware stack, and a source-verified discrepancy about "planning"
- 5. Virtual filesystem: `BackendProtocol` and six pluggable storage strategies
- 6. Sub-agent-as-tool spawning: `task()`, `CompiledSubAgent`, and async/remote delegation
- 7. Skills: progressive disclosure over `SKILL.md`, and the shared cross-harness convention
- 8. Memory: `AGENTS.md` as writable semantic memory, namespaced across sessions
- 9. Harness profiles: model- and provider-keyed overrides of the default stack
- 10. Permissions and human-in-the-loop: path-level rules with an `interrupt` mode
- 11. Context management: summarization, message eviction, and the `DeltaChannel` reducer
- 12. Stated security posture: "trust the LLM," and a fully source-read threat model
- 13. Adjacent surface named but not investigated: Deep Agents Code
- 14. Synthesis: what Deep Agents adds, and what it renames
- Sources

## references/harnesses/model-routing-and-selection.md
- 1. Claude Code
  - 1.1 Main-session model selection and its precedence stack
  - 1.2 Subagent model overrides
  - 1.3 Dynamic workflows: per-stage model routing in a script
  - 1.4 The advisor tool: a second, typically stronger model consulted mid-task
  - 1.5 Availability-triggered fallback and safety-classifier fallback
  - 1.6 The auto-mode permission classifier's own model
- 2. GitHub Copilot CLI
  - 2.1 Main-session model precedence
  - 2.2 Custom-agent `model` frontmatter
  - 2.3 Auto model selection: task-complexity-based routing
  - 2.4 Bring-your-own-key (BYOK) as a routing-adjacent mechanism
- 3. OpenCode
  - 3.1 Global `model`/`small_model` configuration and startup default resolution
  - 3.2 Per-agent model override
  - 3.3 The hidden title agent: OpenCode's own concrete cheap-model case, source-verified end to end
  - 3.4 A resolved documented-vs-source discrepancy in this exact code path
  - 3.5 No documented availability-triggered model-fallback chain
- 4. pi
  - 4.1 A flat, explicit model catalog rather than a routing algorithm
  - 4.2 Model addressing and thinking-level shorthand
  - 4.3 Custom models and providers as flat configuration, not a routing seam
  - 4.4 Bash-visible model identity, and a documented naming caveat
  - 4.5 No documented model-selection failure fallback
- 5. Hermes Agent (Nous Research)
  - 5.1 Per-task model slots: a flat, explicit list rather than a router
  - 5.2 Fallback chains and credential-pool rotation
  - 5.3 Always-on prompt caching, and inherited-by-default subagent routing
- 6. DeepSeek Harness
  - 6.1 A named-route model, not a precedence stack: `GenerateOptions.provider`/`.model`
  - 6.2 Wire-protocol discriminator and the three-tier catalogue-resolution model
  - 6.3 Two coexisting first-class adapters on one runtime, not one generic layer
  - 6.4 The plugin seam where automatic routing actually lives: `agent/request` and `llm/stream`
  - 6.5 The ecosystem's own worked example: `dsh-model-router` (third-party, not core)
  - 6.6 No documented content-triggered or capability-ranked second-opinion mechanism
- 7. Synthesis
- Sources

## references/harnesses/multi-agent-coordination-design-space.md
- 1. Why a design space, not a checklist
- 2. Topology: centralized, decentralized/flat, hierarchical/layered, and shared-message-pool
  - 2.1 Where the three harnesses land
- 3. Blackboard architectures
  - 3.1 Where the three harnesses land
- 4. Consensus and voting among peers
  - 4.1 Where the three harnesses land -- and one deliberate false friend
- 5. Market-based task allocation
  - 5.1 Where the three harnesses land -- and where none of them do
- 6. Shared-scratchpad vs. message-passing as a spectrum
- 7. Putting the map together
- Sources

## references/harnesses/observability-and-self-diagnostics.md
- 1. Claude Code
  - 1.1 Debug flags, log files, and the debug-log format
  - 1.2 `/doctor` and the other built-in introspection commands
  - 1.3 OpenTelemetry traces (beta) -- structural, not cost-oriented
  - 1.4 Default vendor-side telemetry -- a third, non-customer-configured layer
- 2. GitHub Copilot CLI
  - 2.1 Debug flags and log files
  - 2.2 OpenTelemetry -- genuinely spans, not just cost metrics, and enterprise-managed
  - 2.3 Debugging commands and adjacent tooling
- 3. OpenCode
  - 3.1 Logging flags -- fully documented, source-unverified this session
  - 3.2 No native OpenTelemetry -- a third-party plugin ecosystem fills the gap
  - 3.3 No doctor-equivalent diagnostic command found
- 4. pi
  - 4.1 Debug flags, log files, and an internal render-invariant crash log
  - 4.2 No default OpenTelemetry export -- a vendor-neutral, adapter-only telemetry substrate
- 5. Hermes Agent (Nous Research)
  - 5.1 `hermes doctor`: an extensible, plugin-populated health-check registry, not a fixed checklist
  - 5.2 Redaction as a structural default across every observability surface, not an opt-in
  - 5.3 In-session accounting: the CLI status bar, `turn_summary`, the file-mutation verifier, and the gateway's `runtime_footer`
  - 5.4 Failure visibility as an explicit design principle: subagent failures, gateway circuit breakers, and the stall watchdog
  - 5.5 No native OpenTelemetry; a bundled, fail-open, single-backend Langfuse plugin instead of a vendor-neutral contract
- 6. DeepSeek Harness
  - 6.1 Session telemetry as a capability seam -- OTel logs, not spans, with mandatory deployment redaction
  - 6.2 In-session accounting: the token meter and session-stats projection
  - 6.3 Runtime invariants: package-owned, registry-mediated self-diagnostic checks
  - 6.4 No vendor telemetry: an explicit, default-off stance with acknowledged trade-offs
- 7. Synthesis: instrumenting a from-scratch harness for observability
- 8. Sources

## references/harnesses/orchestration.md
- 0. The general concept: the orchestrator/manager pattern
- 1. Claude Code
  - 1.1 The default case -- Claude itself is the turn-by-turn orchestrator
  - 1.2 Dynamic workflows -- moving the plan into a script
- 2. GitHub Copilot CLI
  - 2.1 Ordinary custom-agent delegation has no orchestrator role
  - 2.2 `/fleet` -- an explicit, named orchestrator agent
- 3. OpenCode
  - 3.1 Primary agents as the orchestrator role, subagents as workers
  - 3.2 `permission.task` -- orchestration boundaries declared in config, not decided per-turn
  - 3.3 Fan-out is a prompted convention, not a scripted runtime
- 4. pi
  - 4.0 Resolving this book's own inconsistent spelling: two real, differently-scoped packages, not an error
  - 4.1 No built-in orchestrator ships in the core product
  - 4.2 Once installed: the top-level session's own model is the (only) orchestrator
  - 4.3 Process-level isolation: a genuinely separate `pi` binary per subagent, not a shared context object
  - 4.4 Agent definitions, discovery, and project-trust gating
  - 4.5 Workflow prompts: canned natural-language chains, not a scripted runtime
- 5. Hermes Agent (Nous Research)
  - 5.1 `delegate_task` as an in-conversation orchestrator -- flat by default, self-nesting behind an explicit `role` flag
  - 5.2 Kanban: a durable, out-of-process task board as the coordination artifact
  - 5.3 `a2a_orchestrate`: capability-based fan-out across process and machine boundaries
  - 5.4 A boundary worth naming: Mixture of Agents is not a task-decomposition orchestrator
- 7. DeepSeek Harness
  - 7.1 The turn-by-turn default: the model itself as orchestrator, via `ctx.subagents`
  - 7.2 Continuable children: moving coordination state into the session log
  - 7.3 Agent Teams: a durable task DAG and peer mailbox over the Lead session
  - 7.4 The workflow seam: a model-written orchestration script, executed in a worker thread
  - 7.5 The Cordis architecture consequence: orchestration is declared in composition, not discovered at runtime
- 8. Synthesis
- Sources

## references/harnesses/packaging-distribution-and-self-update.md
- 1. Claude Code
  - 1.1 Distribution mechanisms
  - 1.2 Cross-platform build considerations
  - 1.3 Binary integrity and code signing
  - 1.4 Auto-update flow
  - 1.5 The VS Code extension as its own distribution channel
- 2. GitHub Copilot CLI
  - 2.1 Distribution mechanisms
  - 2.2 Cross-platform build considerations
  - 2.3 Auto-update flow
  - 2.4 The GitHub Copilot VS Code extension -- a different, older product
- 3. OpenCode
  - 3.1 Distribution mechanisms
  - 3.2 Cross-platform build considerations
  - 3.3 npm package structure
  - 3.4 Auto-update flow
- 4. pi
  - 4.1 One repo, two real npm packages -- resolving this book's own inconsistent citation
  - 4.2 Distribution mechanisms
  - 4.3 Cross-platform build considerations
  - 4.4 Version-number history and the two-hop rename off `@mariozechner/pi-coding-agent`
  - 4.5 Self-update: a single `pi update` command family, plus an experimental staged/managed install
- 5. Hermes Agent (Nous Research)
  - 5.1 Distribution mechanism: a git checkout inside a managed venv, not an npm/pip package
  - 5.2 A named, three-tier platform-support policy -- a documentation pattern this page has not previously sourced
  - 5.3 Versioning: CalVer release tags, no registry dist-tag channel to pin against
  - 5.4 Self-update: `hermes update`, with more layered safety machinery than any other harness on this page
  - 5.5 Docker: image-managed installs refuse `hermes update` by design, verified by an on-disk provenance marker
- 6. Cross-harness synthesis
- Sources

## references/harnesses/permissions-and-sandboxing.md
- 1. Claude Code
  - 1.1 Why an approval-prompt layer exists: the stated threat model
  - 1.2 Permission modes as the enforcement-architecture question
  - 1.3 Approval-prompt UX
  - 1.4 Why a permission classifier exists: auto mode
  - 1.5 Sandboxed command execution
  - 1.6 Sources of escape-hatch risk (Claude Code)
- 2. GitHub Copilot CLI
  - 2.1 Why approval prompts exist: the stated risk framing
  - 2.2 Approval-prompt UX and the two-layer permission architecture
  - 2.3 Local sandbox architecture
  - 2.4 Sources of escape-hatch risk (Copilot CLI)
- 3. OpenCode
  - 3.1 Why an approval layer exists, and what the docs do not claim it is
  - 3.2 Approval-prompt UX
  - 3.3 Enforcement architecture, source-verified
  - 3.4 No OS-level sandbox: a source-verified terminology finding
  - 3.5 Sources of escape-hatch risk (OpenCode)
- 4. DeepSeek Harness
  - 4.1 The sandbox seam: process-level OS confinement, filesystem effects only
  - 4.2 Permission presets: two independent knobs, not one linear scale
  - 4.3 Convergence with Claude Code's own sandbox primitives, and Claude Code's escape hatch naming
  - 4.4 Using DeepSeek's two-axis preset model as a reasoning aid for Claude Code's six permission modes -- BEST CURRENT UNDERSTANDING, UNCONFIRMED
- 5. pi
  - 5.1 No permission system and no sandbox, by explicit design
  - 5.2 Project trust is a config-loading gate, explicitly not a sandbox
  - 5.3 Containerization as the recommended, externally-owned alternative
  - 5.4 Security-report scope: the same boundary stated as a triage policy
- 6. Hermes Agent (Nous Research)
  - 6.1 An explicit, named rejection of "trust the LLM"
  - 6.2 Container isolation as a second, independent layer -- with an explicit trade-off against the approval system
  - 6.3 A named, two-adversary-class threat-model taxonomy, reconfirming a split this page already draws for Claude Code
- 7. Synthesis
- Sources

## references/harnesses/retries.md
- 1. Claude Code
  - 1.1 The documented policy: bounded, category-gated, exponential
  - 1.2 Environment variables
  - 1.3 What the user sees, and how that UX itself changed release to release
  - 1.4 Backoff-minimum and circuit-breaker fixes worth their own note
  - 1.5 `fallbackModel`: a bounded, error-type-gated retry-on-a-different-model
  - 1.6 Retries as a pervasive engineering surface beyond the main API call
  - 1.7 Hook and permission-layer interaction
- 2. GitHub Copilot CLI
  - 2.1 What is documented at the platform level -- and its real scope
  - 2.2 Changelog-traced evidence of the CLI's actual retry behavior
  - 2.3 What is not documented
- 3. OpenCode
  - 3.1 Two distinct, layered retry mechanisms
  - 3.2 The inner layer: `RequestExecutor`'s bounded, jittered transport retry
  - 3.3 The outer layer: `SessionRetry`, wrapping the entire turn
  - 3.4 Corroborating this from a live, fetched GitHub Issue
  - 3.5 A third, unrelated retry utility: `packages/core/src/util/retry.ts`
  - 3.6 Config surface: none found
- 4. pi
  - 4.1 Three layers, not one: transport retry, turn retry, and durable retry state
  - 4.2 The inner, request layer: `retryProviderRequest` -- reimplementing the SDKs' own policy, made abortable
  - 4.3 The outer, turn layer: `retryAssistantCall` and its string-pattern error classifier
  - 4.4 Settings surface, and the documented reason to keep the inner layer off
  - 4.5 Reuse by compaction: the same policy, not a separate hard-coded loop
  - 4.6 A third, structurally distinct layer: durable, crash-recoverable retry state in `pi-agent-core`
- 5. Hermes Agent (Nous Research)
  - 5.1 The loop: `while retry_count < max_retries` in `conversation_loop.py`
  - 5.2 Error classification: `FailoverReason`, a nine-axis taxonomy with per-branch recovery hints
  - 5.3 Backoff: `jittered_backoff()`, a positive-only-jitter exponential with a provider-specific long-tail carve-out
  - 5.4 Disabling the SDK's own retry loop -- and the one path where it stays on
  - 5.5 One-shot recovery guards and the two retry-budget resets
  - 5.6 `fallback_providers`: the alternative-to-retry mitigation, reset-aware and turn-scoped
  - 5.7 Self-reported failure modes
- 6. DeepSeek Harness
  - 6.1 Architecture: provider-owned policy, plugin-owned execution, durable before wait
  - 6.2 Two policy modes: `normal` (bounded, code-gated) and `always` (unbounded, downstream-first)
  - 6.3 Backoff: symmetric jitter around exponential, server `Retry-After` honored exactly when under cap
  - 6.4 The `agent/request-error` waterfall and `RequestErrorAction`
  - 6.5 Retry history: keyed by provider and canonical policy hash
  - 6.6 Error codes and non-retryable carve-outs
  - 6.7 What the model sees: nothing
  - 6.8 Wire-level verification: the transport-recovery integration test
- 7. Synthesis
- Sources

## references/harnesses/session-persistence.md
- 1. Claude Code
  - 1.1 The transcript: one JSONL file per session, on disk from the first turn
  - 1.2 Task-tracking tool persistence: `TodoWrite` vs. the `Task*` family
  - 1.3 Session IDs and what resuming actually restores
  - 1.4 Branching/forking -- a genuinely new session ID, not a pointer
  - 1.5 Checkpointing/`/rewind` -- a parallel, file-snapshot mechanism, not the transcript
  - 1.6 Retention, storage location, and how to make it disappear
  - 1.7 A changelog-traced hardening history
- 2. GitHub Copilot CLI
  - 2.1 Two stores, not one: session files and a derived SQLite index
  - 2.2 Resume mechanics and session identity
  - 2.3 The SDK's more detailed picture of what a session directory holds
  - 2.4 A changelog-traced hardening history
- 3. OpenCode
  - 3.1 A live architecture change the docs and community writeups don't reflect yet
  - 3.2 Session IDs are structured, sortable, and self-timestamping
  - 3.3 Resume, from the CLI's own documented flags
  - 3.4 Fork-from-message: a new session row, truncated at a specific message
  - 3.5 Revert/unrevert: undo in place, not a fork -- and its own shadow-git snapshot store
- 4. DeepSeek Harness
  - 4.1 Turn/step vocabulary and the three-domain session-event model
  - 4.2 A pluggable persistence contract: the framework ships no backend at all
  - 4.3 `fork()`: an inclusive boundary, and a rejected (not clipped) open-turn cut
- 5. pi
  - 5.1 One JSONL file per session, but tree-structured from the format's own design, not bolted on
  - 5.2 Nine entry types, and a session-context builder that walks the tree, not the file
  - 5.3 `/tree`, `/fork`, and `/clone`: three genuinely different operations on the same underlying structure
  - 5.4 Deletion, and a small but genuinely distinctive UX choice
- 6. Hermes Agent (Nous Research)
  - 6.1 One canonical store, `~/.hermes/state.db`: a SQLite database, not a session-per-file format
  - 6.2 Session identity, per-terminal continuity, and workspace-scoped resume
  - 6.3 Compression as lineage-splitting: the only harness on this page where compaction *is* the fork
  - 6.4 Checkpoints & `/rollback`: a separate, opt-in, cross-project shadow-git safety net
  - 6.5 Cross-surface continuity: gateway routing, crash recovery, and `/handoff`
  - 6.6 Export/import interop: a Claude-Code-shaped trace format, and reading rivals' transcripts directly
- 7. Synthesis
- Sources

## references/harnesses/streaming-and-incremental-rendering.md
- 1. Claude Code
  - 1.1 A changelog-traced history of getting streamed text onto a terminal without it flickering or stalling
  - 1.2 Reassembling partial tool-call JSON: concrete failure modes the changelog fixed
  - 1.3 Synthesis for Claude Code
- 2. GitHub Copilot CLI
  - 2.1 Token-by-token streaming, its default, and its off switch
  - 2.2 Flicker, spinner cost, and shell-output tailing
  - 2.3 Adjacent-surface citation: the Copilot SDK's own streaming-events model
- 3. OpenCode
  - 3.1 The republishing layer: one accumulation discipline shared by text, reasoning, and tool input alike
  - 3.2 A genuine divergence: the shared "core" reducer drops tool-input deltas; the TUI's own reducer keeps them
  - 3.3 Incremental parsing of a growing string that is not JSON: the reasoning-title regex
  - 3.4 Incremental Markdown rendering on the web/app surface: tokenize, freeze, heal, and reuse
  - 3.5 Decoupling display pace from delivery cadence: the client-side typewriter pacer
- 4. pi
  - 4.1 The `--mode json` / RPC event stream: a real quadratic-growth bug, fixed by going delta-only
  - 4.2 The TUI's incremental Markdown component: whole-string re-lex plus a targeted partial-fence fix
  - 4.3 A genuine, source-verified exception: live Mermaid-diagram rendering while the diagram is still streaming in
  - 4.4 Render-cost coalescing: a ~60fps floor, and an explicit escape hatch for input latency
  - 4.5 The differential-render/`clearOnShrink` tradeoff, and a still-open scroll-jump bug
  - 4.6 Two negative findings worth stating plainly
  - 4.7 Synthesis for pi
- 5. Hermes Agent (Nous Research)
  - 5.1 The gateway event vocabulary, and a real accumulate-vs-replace regression (`#16391`)
  - 5.2 Fully incremental Markdown: freeze-on-paragraph-boundary scanning, arrived at independently of OpenCode's and pi's own designs
  - 5.3 Context-adaptive render pacing, and a hard tail-cap on the live buffer
  - 5.4 `@hermes/ink`: a cell-level virtual-screen diff engine, hardware scroll regions, and a multiplexer-specific synchronized-output carve-out
  - 5.5 Backpressure-aware frame coalescing (Issue #31486), and off-thread plugin stream-hook dispatch
  - 5.6 Synthesis for Hermes Agent
- 6. Synthesis
- Sources

## references/harnesses/system-prompt-design-as-craft.md
- 1. Anthropic's own published guidance on writing tool-calling instructions
  - 1.1 Phrasing directly steers the tool-call/respond-directly boundary
  - 1.2 Explicit action-language beats implied permission
  - 1.3 Aggressive imperative language has diminishing, then negative, returns
  - 1.4 Parallel tool-call behavior is independently promptable
  - 1.5 Tool descriptions are agent-computer interface (ACI) design, not documentation
  - 1.6 Structuring the prompt itself: sections, examples, XML tags
  - 1.7 pi's own documented micro-style-rule for a flat, multi-contributor bullet list
- 2. Few-shot tool-call examples vs. prose constraints as competing strategies
  - 2.1 The documented case for examples
  - 2.2 The documented risk: examples teach unintended patterns too
  - 2.3 A real, source-verified production example of both strategies coexisting
  - 2.4 Grounding the tradeoff against the wider tool-calling research literature
  - 2.5 pi: a code-assembled template rather than a static prompt file, with tools authoring their own fragments
  - 2.6 OpenCode: the model-family dispatch §2.3 quotes is only the base tier of a per-turn-assembled prompt, sitting under a per-agent override chain
- 3. Phrasing that survives compaction and context pressure
  - 3.1 Front-load the sentence that must not be lost
  - 3.2 Anthropic's own documented technique: tell the model about compaction, don't hide it
  - 3.3 State-externalization phrasing as the durable complement
- 4. Evidence that this is iterated craft, not a solved-once artifact
  - 4.1 Claude Code: a multi-year record of literal prompt-text tuning
  - 4.2 Copilot CLI: the same discipline, independently evidenced
  - 4.3 What is deliberately NOT claimed here: the actual prompt text
  - 4.4 pi: a third craft-maturity model -- the prompt-construction function has its own regression tests
- 5. Resisting prompt injection from the authoring side
  - 5.1 Two threat models, and why authoring technique differs between them
  - 5.2 Documented authoring techniques for indirect injection
  - 5.3 Independent research corroboration, held apart from Anthropic's own guidance
  - 5.4 Changelog evidence that this is a live, ongoing authoring concern on Claude Code
- 6. Hermes Agent (Nous Research)
  - 6.1 Three named cache-priority tiers, and a maintainer-documented fix for exactly the date-in-prompt problem §2.6 leaves open for OpenCode
  - 6.2 A model-family conditional-assembly guidance dial, empirically tuned against named production failure traces -- a third mechanism for §1's "phrasing intensity is tuned per model generation" finding
  - 6.3 The operator-customization surface, stated as an explicit prescriptive boundary between configuration and code
  - 6.4 A documented false-positive-on-legitimate-content injection incident, and the self-describing marker that fixed it -- direct field corroboration of §5.2's provenance-marking guidance and §5.4's Claude Code parallel
  - 6.5 Inline, issue-numbered maintainer comments as a fifth documentary shape for "iterated craft," anchored by one bisection-verified production incident
- 7. DeepSeek Harness (Cordis plugin architecture)
  - 7.1 The system prompt is a Cordis-plugin registry assembled per turn, not a template rendered from one file
  - 7.2 Tool guidance ownership as an explicit, ADR-documented rule -- the structural fix pi's docs only offer as an authoring convention
  - 7.3 Centralized, sparse order allocation: an ADR-governed fourth mechanism for the same ordering-conflict problem OpenCode and Hermes each solve differently
  - 7.4 Strict, fail-loud variable interpolation, and the `complete` flag as DSH's own version of the whole-prompt-replacement lever
  - 7.5 Dated architectural-decision records as a sixth documentary shape for iterated craft, and a 43-case regression suite as further evidence
- 8. Synthesis: what "good" system-prompt authorship actually looks like
- Sources

## references/harnesses/tool-schema-and-interface-design.md
- 1. JSON Schema authoring for tool parameters
  - 1.1 What the schema itself is, and what a harness/API actually requires of it
  - 1.2 Strict mode: schema authoring as a hard guarantee, not just a hint
  - 1.3 `input_examples`: schema-attached demonstration, distinct from prose few-shot
  - 1.4 Anthropic's other stated priorities for schema and response format
  - 1.5 pi: TypeBox schemas, per-field descriptions, an experimental-only strict-sampling switch, and a model-quirk input-coercion shim
  - 1.6 GitHub Copilot CLI: opaque runtime arguments, a documented permission-approval schema, and no published `input_schema` equivalent
  - 1.7 Hermes Agent: an OpenAI-function-calling wire shape, a schema-vs-registry description-precedence quirk, and model-family-conditioned schema variants read directly from source
  - 1.8 DeepSeek Harness: a custom schema DSL (`defineTool`/`ValueSchemaSpec`), a mandatory canonical-output contract, a `finalizeContent` callback, a generated and boot-verified tool catalog, scoped tool registration with `ToolRestriction` filters, and PTC mode as a third tool-presentation axis
- 2. Naming and description conventions that measurably affect tool-selection accuracy
  - 2.1 Anthropic's own naming and namespacing guidance
  - 2.2 What the wider function-calling literature measures, and why it corroborates the naming/description claim
  - 2.3 The hallucinated-argument framing, cross-referenced rather than re-derived
  - 2.4 pi: flat, un-namespaced tool names, and a second, dedicated prompt-guidance channel distinct from `description`
  - 2.5 GitHub Copilot CLI: a retrieval-framed naming rationale, a model-family-conditioned runtime name vocabulary, and an alias layer distinct from either
  - 2.6 Hermes Agent: imperative tool-redirection sentences as a lived negative-boundary convention, a hybrid namespacing scheme, and a corrected MCP-naming finding
  - 2.7 DeepSeek Harness: flat built-in tool names, per-tool system-prompt sections, MCP double-underscore namespacing, config-driven tool names, and enforced parameter-level description discipline
- 3. The few-powerful-tools-vs-many-narrow-tools tradeoff
  - 3.1 Anthropic's stated consolidation guidance, and its own worked example
  - 3.2 Where the three harnesses actually sit on this spectrum -- a real, cross-referenced data point
  - 3.3 Scale changes the calculus: deferred schema loading as a third option
  - 3.4 pi: eight flat, narrow tools -- including a platform-doubled shell pair -- plus in-call batching as a distinct, narrower form of consolidation
  - 3.5 GitHub Copilot CLI: tool search as a model-conditioned deferred-loading mechanism, directly comparable to Claude Code's
  - 3.6 Hermes Agent: the largest built-in surface this page documents, an unevenly-applied consolidation practice, and a three-tier, three-bridge-tool deferred-loading mechanism
  - 3.7 DeepSeek Harness: the second-largest built-in surface this page documents, a `str_replace_editor` consolidation counterpoint, PTC mode as a third tool-presentation axis, scoped `ToolRestriction` filters, and a compartmentalized tool surface by deployment profile
- 4. Idempotency and error-message design
  - 4.1 MCP's tool annotation vocabulary for idempotency, destructiveness, and openness
  - 4.2 MCP's two-tier error taxonomy: what a model can and cannot recover from
  - 4.3 A real, source-verified production example: OpenCode's `edit` tool error catalogue
  - 4.4 Cross-reference: Claude Code's own Edit-tool error design, already documented mechanically
  - 4.5 pi's own `edit` tool: fuzzy-match tolerance before failure, index-qualified batch errors, and a real write-vs-edit idempotency contrast
  - 4.6 GitHub Copilot CLI: a binary success/failure hook channel, an external interception point for refusal text, and no published idempotency-hint vocabulary
  - 4.7 Hermes Agent: a fifth, independently-implemented nine-strategy fuzzy-match cascade with real overlap and real divergence from OpenCode's own, plus a dedicated error-text sanitization layer neither other harness's coverage documents
  - 4.8 DeepSeek Harness: a `remediateFsError` layer appending model-facing recovery instructions, a `finalizeContent` last-mile transform even for pipeline failures, a `ToolArgsError`/`ToolOutputError` typed error taxonomy, an `FS_STALE_VERSION`/`FS_NOT_OBSERVED` read-before-edit gate with model-facing remedy text, and a `ToolGuard` monotonic-deny-only policy with no allow result
- 5. Synthesis
- Sources

## references/harnesses/tui-cli-application-architecture.md
- 1. Claude Code
  - 1.1 Rendering engine
  - 1.2 Component model: contexts as the documented proxy for a component tree
  - 1.3 Input handling
- 2. GitHub Copilot CLI
  - 2.1 Rendering engine
  - 2.2 Component model: modes as the primary modal-dispatch unit, not dialog contexts
  - 2.3 Input handling
- 3. OpenCode
  - 3.1 Rendering engine: OpenTUI, a native Zig core with a SolidJS reconciler
  - 3.2 Component model: a real primitive/composite/dialog hierarchy
  - 3.3 Input handling: `@opentui/keymap`'s mode-stack architecture
  - 3.4 A genuinely remarkable interop finding: OpenCode's external-editor integration reads Claude Code's own IDE lock-file protocol
- 4. pi
  - 4.1 Rendering engine: `pi-tui`, a from-scratch, dependency-free TUI framework
  - 4.2 Component model: a plain-string-array render contract, no virtual DOM
  - 4.3 Input handling: CLI-invocation-time modes, not runtime-cycled ones, plus an overlay-dialog interior
- 5. Hermes Agent (Nous Research)
  - 5.1 Rendering engine: a prompt_toolkit REPL and a forked, in-repo Ink client, bridged to one Python core
  - 5.2 Component model: stacked always-mounted widgets in the base CLI, a real overlay system in the Ink client
  - 5.3 A widget SDK: third-party interactive mini-apps registered into the same Ink tree
  - 5.4 Input handling: `Condition`-filtered keybindings, terminal-quirk shims, and a deliberately mouse-free base CLI
- 6. DeepSeek Harness
  - 6.1 Rendering engine: a browser React application, not a terminal renderer
  - 6.2 Component model: Cordis Slots -- a typed React composition system, not a terminal component tree
  - 6.3 Input handling: the browser DOM is the input layer, not a terminal protocol
- 7. Synthesis
- Sources

## references/inference-engines/batching-and-continuous-batching.md
- 1. How llama-server implements it: slots
- 2. Why this matters more than it might first appear
- 3. Interaction with offloading and quantization
- 4. Why this matters specifically for a multi-agent harness
- Sources

## references/inference-engines/cpu-gpu-heterogeneous-offloading.md
- 1. Layer-granularity CPU+GPU hybrid inference (llama.cpp's model)
- 2. Why heterogeneous offloading is a memory-vs-speed tradeoff, not a free lunch
- 3. Expert offloading: why MoE models need a fundamentally different offloading strategy
- 4. Why this matters for an agent-harness builder
- Sources

## references/inference-engines/ktransformers.md
- 1. What it is, and a documentation-vintage caveat worth stating plainly
- 2. The YAML operator-injection mechanism
- 3. Precision and backend naming
- 4. Supported models and hardware
- 5. Why an agent-harness builder specifically cares about KTransformers
- Sources

## references/inference-engines/kv-cache-and-context-window-management.md
- 1. Why the KV cache is a *second*, session-scoped memory cost
- 2. Context-window sizing as an explicit, engine-facing setting
- 3. KV-cache quantization: a second, independent precision axis
- 4. Why this matters for an agent-harness builder specifically
- Sources

## references/inference-engines/llama-cpp.md
- 1. What it is and its design goals
- 2. Binaries: `llama cli` and `llama serve`
- 3. GGUF quantization type naming: K-quants and I-quants
- 4. Ollama's relationship to llama.cpp
- 5. Why an agent-harness builder specifically cares about llama.cpp
- Sources

## references/inference-engines/memory-mapped-model-loading.md
- 1. Why GGUF was designed to make this possible
- 2. llama.cpp's own load-mode surface
- 3. What memory-mapping actually changes at runtime
- 4. Interaction with quantization and offloading
- 5. Why an agent-harness builder cares
- Sources

## references/inference-engines/model-file-formats.md
- 1. GGUF's predecessors and why they were replaced
- 2. GGUF's on-disk structure
- 3. Alignment and its direct link to memory-mapped loading
- 4. Tensor element types and quantization as a GGUF-native concept
- 5. Why this matters for an agent-harness builder
- Sources

## references/inference-engines/model-management-and-distribution.md
- 1. llama.cpp: direct file paths and Hugging Face references
- 2. Ollama: names, manifests, and a Modelfile-based build layer
- 3. KTransformers: a curated registry for its own launch shortcut
- 4. Why an agent-harness builder cares
- Sources

## references/inference-engines/multi-gpu-and-tensor-parallelism.md
- 1. Layer (pipeline) parallelism -- the default
- 2. Tensor parallelism -- experimental, latency-oriented
- 3. Configuration surface
- 4. Relationship to KTransformers' heterogeneous placement
- 5. Why an agent-harness builder cares
- Sources

## references/inference-engines/ollama.md
- 1. Relationship to llama.cpp: a dependency, not a fork, and now a dual-engine design
- 2. The Modelfile: a declarative model-build format
- 3. GPU support and scheduling
- 4. Dual API surfaces: native REST and OpenAI-compatible
- 5. Why an agent-harness builder specifically cares about Ollama
- Sources

## references/inference-engines/quantization-at-inference-time.md
- 1. The engine consumes, it does not (usually) decide, the scheme
- 2. Dequantize-at-compute-time, not decompress-then-run
- 3. Mixed-precision tensors within one loaded model
- 4. Runtime knobs an engine exposes around a fixed weight quantization
- 5. Why an agent-harness builder cares
- Sources

## references/inference-engines/sampling-and-decoding-parameters.md
- 1. The core sampling knobs
- 2. Grammar- and schema-constrained decoding: a fundamentally different mechanism
- 3. Why grammar-constrained output is the load-bearing mechanism for tool calling
- 4. Why an agent-harness builder cares
- Sources

## references/inference-engines/server-api-modes.md
- 1. What "OpenAI-compatible" concretely means
- 2. llama-server's own native implementation
- 3. Why an OpenAI-shaped API is the load-bearing compatibility layer for agent harnesses
- 4. Why concurrency-aware serving matters more than the API shape alone
- Sources

## references/inference-engines/speculative-decoding.md
- 1. The core mechanism: draft, then verify in one batch
- 2. llama.cpp's family of draft mechanisms
- 3. Why the payoff depends entirely on acceptance rate
- 4. Why an agent-harness builder cares
- Sources

## references/models/mixture-of-experts-and-frankenmerging.md
- 1. What a Mixture of Experts is
- 2. FrankenMoE vs. a native pretrained MoE
- 3. MergeKit's MoE mode: config and gate initialization
- 4. Practical tradeoffs
- 5. Worked example: Beyonder-4x7B-v3
- Sources

## references/models/model-terminology.md
- 1. Learning-paradigm vocabulary
- 2. Pretraining, fine-tuning, and inference
- 3. Encoder, decoder, and encoder-decoder architectures
- 4. Tokenization and model I/O
- 5. Feature extraction and multimodality
- 6. Why this page exists as a separate reference
- Sources

## references/models/parameter-count-and-scale.md
- 1. What a "parameter" is, and what parameter count signals
- 2. Naming conventions: 7B, 13B, 70B
- 3. Memory footprint: the load-bearing rule of thumb
- 4. Why scale interacts with context length: the KV cache
- 5. Latency, cost, and capability tiers in practice
- Sources

## references/models/quantization.md
- 1. Definition and motivation
- 2. Precision formats
- 3. Quantizing to int8: the affine scheme
- 4. Symmetric vs. affine, and per-tensor vs. per-channel granularity
- 5. Calibration: dynamic quantization, static quantization, and QAT
- 6. Practical VRAM impact for LLM deployment
- 7. When to quantize an agentic-pipeline model
- Sources

## references/models/task-and-pipeline-classification.md
- 1. A sourcing note: what `docs/hub/models-tasks` actually documents
- 2. The task taxonomy, top level
- 3. `text-generation`
- 4. `text2text-generation`
- 5. `feature-extraction`
- 6. `sentence-similarity`
- 7. `question-answering`
- 8. `summarization`
- 9. `text-classification`
- 10. `token-classification`
- 11. `fill-mask`
- 12. `translation`
- Sources

## references/rag/advanced-rag-techniques.md
- 1. The retriever half: chunk size, chunking method, and the token-vs-character trap
- 2. Distance metric and index choice
- 3. Visualizing the embedding space with PaCMAP
- 4. The reader half: prompt, and reranking with ColBERTv2
- 5. Levers named but not implemented in this notebook
- 6. Pre-retrieval query transformation: Rewrite-Retrieve-Read and HyDE
  - 6.1 Query Rewriting: the Rewrite-Retrieve-Read framework
  - 6.2 HyDE: Hypothetical Document Embeddings
  - 6.3 Position in the RAG technique taxonomy

## references/rag/agentic-rag-with-llamaindex.md
- 1. The stated goal: a lightweight, fully local ebook librarian
- 2. LlamaIndex's three-phase framing: Loading, Indexing, Querying
  - 2.1 Loading: `SimpleDirectoryReader` and multi-format support for free
  - 2.2 Indexing: `VectorStoreIndex`, and LlamaIndex's OpenAI-by-default trap
  - 2.3 Querying: `as_query_engine`, backed by Ollama-served Llama 2
- 3. Named future work: citations, richer metadata, persistent indexing

## references/rag/basic-rag-pipeline.md
- 1. What the notebook builds, end to end
- 2. Data acquisition: `GitHubIssuesLoader`
- 3. Chunking: `RecursiveCharacterTextSplitter`
- 4. Embedding and vector store: `BAAI/bge-base-en-v1.5` + FAISS
- 5. The generator: quantized Zephyr-7B via `transformers` + LangChain
- 6. Chain assembly with LangChain Expression Language (LCEL)
- 7. The demonstrated payoff: side-by-side comparison

## references/rag/cache-augmented-generation.md
- 1. The tradeoff CAG is built on: retrieval vs. in-context knowledge
- 2. The cost problem CAG solves: prompt caching
- 3. When CAG is viable
- 4. CAG vs. RAG: the architectural tradeoff
- 5. Relationship to the RAG foundations
- 6. Grounding summary

## references/rag/foundations.md
- 1. The problem RAG was built to solve
- 2. The Lewis et al. architecture: parametric + non-parametric memory
- 3. RAG-Sequence vs. RAG-Token
- 4. Results claimed in the abstract
- 5. The agentic reframing: RAG as one tool among several
- 6. What this means for the rest of this reference area

## references/rag/heterogeneous-data-sources.md
- 1. Unstructured documents: partition first, chunk second
- 2. SQL databases: rerank table schemas, generate SQL, then narrate the result
- 3. What both notebooks have in common

## references/rag/rag-evaluation.md
- 1. Why a synthetic dataset, and how it is generated
- 2. Three critique agents, each scoring a distinct failure mode
- 3. The RAG system under test
- 4. Scoring the RAG system's answers with an LLM judge
- 5. RAGAS: reference-free RAG evaluation
  - 5.1 Faithfulness
  - 5.2 Context Precision
  - 5.3 Context Recall
  - 5.4 Response Relevancy (Answer Relevancy)
  - 5.5 How the four metrics compose

## references/rag/semantic-caching.md
- 1. The problem: production RAG has two expensive, repeatable steps
- 2. Where the cache sits: before retrieval, not before generation
- 3. The knowledge base underneath: ChromaDB
- 4. The cache mechanism: FAISS `IndexFlatL2` with a Euclidean threshold
- 5. Index-type choice and eviction policy, named as tunable

## references/rag/structured-generation-for-rag.md
- 1. The target: an answer plus verifiable source snippets
- 2. Naive approach: prompting for JSON, and where it breaks
- 3. Constrained decoding: grammars that make malformed output unreachable
- 4. The mechanism underneath: logit biasing via Outlines
- 5. A second application named in passing: LLM-as-judge scoring

## references/rag/vector-store-integrations.md
- 1. Milvus: a purpose-built vector database, local-first by default
- 2. Elasticsearch: the ES-side-vectorization vs. self-vectorization choice
- 3. MongoDB Atlas: `$vectorSearch` as an aggregation pipeline stage
- 4. What varies and what stays constant across all three

## references/sdlc/04-the-reference-architecture.md
- The wrong unit of architecture
- The three layers (participant structure)
- Mapping the layers across the lifecycle
- The five-layer landscape (technical supply chain)
- What changes about roles
- The architecture decision matrix -- where to start
- Build, buy, or compose
- Start anywhere, expand deliberately -- the phased-adoption timeline
- Source

## references/sdlc/09-10-part-iii-preface-and-practitioners-mindset.md
- Ch. 9 -- A map for Part III
  - Eight terms practitioners cannot avoid
  - The five-layer supply chain, restated
  - Four named composition patterns
- Ch. 10 -- The practitioner's mindset
  - 10.1 The autocomplete trap
  - 10.2 From writing code to engineering context
  - 10.3 Your three roles
  - 10.4 When to use agents and when to code manually
  - 10.5 The cost of over-reliance
  - 10.6 First day: a task from start to finish
  - 10.7 The mindset in practice
- Source

## references/sdlc/11-the-runtime-machine.md
- The problem it addresses
- The four parts of the runtime machine
- The three recurring filename shapes (a 30-second glossary)
- The harness as compiler
- Markdown as code, not documentation
- Inference per-thread; filesystem shared
- Deployment topology variants
- Skills and cross-harness portability
- TL;DR: four parts, one machine
- What this chapter unlocks
- Source

## references/sdlc/12-the-instrumented-codebase.md
- The problem it addresses
- The seven primitive types
  - Instructions
  - Agents
  - Skills
  - Prompts
  - Memory
  - Orchestration
  - Hooks
- Tool support
- Directory structure
- How primitives compose
- The instrumentation audit
- Before and after: a concrete example

## references/sdlc/14-the-load-lifecycle.md
- The problem it addresses
- The four-phase lifecycle: Resolve -> Materialize -> Bind -> Activate
- Cross-harness materialization reference
- The three binding modes
  - Binding-mode timeline
- Determinism vs. probabilism in Activate
- Failure modes / anti-patterns
- The worked example
- Terms of art coined/used
- Checklist: when a primitive is silent
- Source

## references/sdlc/15-attention-and-context-economy.md
- The problem it addresses
- Window vs. attention
- Position-sensitivity: the attention curve
- The three levers of the attention economy
- Diagnosing attention starvation
  - Symptom-to-cause table
- The practitioner's budget table
- The five access mechanisms
- Anti-patterns and failure modes
- Connection back to PROSE (Ch. 13)
- Terms of art coined/used
- Forward references
- Source

## references/sdlc/16-deterministic-probabilistic-boundary.md
- Two computers, one program
- Consequential side effects belong on the deterministic side
  - Named substrate patterns implementing the seam
  - The seam in operation (diagram)
- Property comparison: deterministic side vs. probabilistic side
- Hallucination as a system property
- The four kinds of quality gate
  - Anti-pattern: four common gate mismatches
- The architect's discipline (three habits)
- Compliance and auditability
- How this connects to neighbouring chapters
- Source

## references/sdlc/17-multi-agent-orchestration.md
- When one agent is enough
- Agent specialisation patterns
- Parallelisation strategies
- Conflict resolution
- The human as orchestrator
  - The escalation protocol
- The coordination tax: honest numbers
  - Worked case study -- PR #394: APM Auth + Logging Overhaul
  - The sweet spot
- Session management
- Anti-patterns
- Putting it together (workflow diagram)
- How this connects to neighbouring chapters
- Source

## references/sdlc/18-the-execution-meta-process.md
- The five phases
- The checkpoint: four parts, every wave
- The ADAPT loop
- Wave sizing
- Worked example: PR #394 (APM auth + logging overhaul)
- Scaling the process
- What the meta-process produces
- How this connects to neighbouring chapters
- Source

## references/sdlc/19-architectural-patterns-rosetta-stone.md
- The four-layer substrate
- Composition layer
- Assembly layer
- Dispatch and orchestration layer
- Boundary layer
- Recovery and observability layer
- Decision matrix
- Anti-patterns named explicitly
- Vocabulary
- Reconciling three layered lenses used across the handbook
- Scope: what this chapter deliberately does not catalogue
- Cited sources
- How this connects to neighbouring chapters
- Source

## references/sdlc/20-anti-patterns-and-failure-modes.md
- The problem it addresses
- The taxonomy: 19 anti-patterns mapped to PROSE
- Foundational anti-patterns
- Execution anti-patterns
- Session and resource failure modes
- The silent-failure problem
- Silent-failure detection checklist
- Team-level anti-patterns
- The recovery playbook
  - Worked example: recovering from the "Almost Done" trap
  - The failure-mode decision tree
- Security practices for agent-generated code
- Concluding points
- Source

## references/sdlc/21-primitives-as-code.md
- The problem it addresses
- From file to package
- Modules over monoliths
- Separation of concerns, by dependency
- The lockfile and what it pins
- Overrides without forking
- Versioning: the description is the API
- A walkthrough: from one file to one package
- Three concerns when authoring a skill
- TL;DR

## references/sdlc/22-the-reference-architecture-earned.md
- 22.1 Composition is recursive
- 22.2 What makes the recursion governable
- 22.3 A Panel, walked end to end
- 22.4 What this changes for the architect
- TL;DR -- one rule, applied recursively
- Source

## references/sdlc/23-case-study-apm-overhaul.md
- The problem
- Agentic techniques applied
- Concrete numbers
- Problems encountered and how they were solved
- Lessons learned
- Source

## references/sdlc/24-case-study-handbook-writing.md
- Team topology: 11 personas in four pods
- Execution pipeline: wave-based orchestration
- Concrete numbers
- File and workflow structure
- Problems encountered and how they were solved
- Notable discovery
- Lessons learned
- Source

## references/sdlc/25-case-study-publishing-pipeline.md
- The problem
- Agentic techniques applied
- Concrete numbers
- Lessons learned
- Source

## references/sdlc/26-case-study-growth-engine.md
- The problem
- Agentic techniques applied
- Concrete numbers
- Lessons learned
- Source

## references/sdlc/appendix-a-cross-harness-reference.md
- Master comparison table
- Key observations named in the appendix
- Per-harness technical notes
- Cross-harness convergence
- Source

## references/sdlc/appendix-b-genesis-worked-example.md
- B.1 The anti-pattern -- panel-in-one-thread
- B.2 The corrected design -- fan-out with arbiter
- Source

## references/sdlc/prose-framework.md
- The problem it addresses
- The five constraints
- How the constraints interact
- Applying it: example project layout
- Compliance checklist
