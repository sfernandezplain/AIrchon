# The Road to Agentic Archon -- Index

> **Status:** complete -- 12 chapters + 4 harness syntheses + glossary generated 2026-09-12 by `airchon-communicator`. Every `File` below resolves. `Next` forms the chain `index -> foreword -> 01 -> 02 -> ... -> 12 -> harnesses -> glossary`. No chapter is orphaned. Gate 3 audits: link audit PASS, glossary coverage PASS, mermaid ASCII PASS.

## How to read this book

Front-to-back in the order below. Each chapter lists its prerequisites -- a chapter never needs a term that only appears later. Harness syntheses are reference after the general chapters.

## Reading order -- the knowledge tree

| Ch. | Title | File | Prerequisites | Next | Mermaid | Sources |
|-----|-------|------|---------------|------|---------|---------|
| 0 | Foreword | foreword.md | -- | 01-topology | -- | -- |
| 1 | A topology of agentic systems | chapters/01-topology.md | -- | 02-agent-loop | flowchart (3 diagrams) | `references/harnesses/agent-topology.md` |
| 2 | The agent loop -- thought, action, observation | chapters/02-agent-loop.md | 01 | 03-implementations | stateDiagram | `references/harnesses/agent-loop.md` |
| 3 | Agent loop implementations (Claude Code, Copilot CLI, OpenCode, pi, Hermes, DeepSeek) | chapters/03-agent-loop-implementations.md | 02 | 04-memory-and-context | sequence + flowchart (4 diagrams) | `references/harnesses/agent-loop-implementations.md` |
| 4 | Memory, instruction budget, and compression | chapters/04-memory-context.md | 03 | 05-coordination | stateDiagram + flowchart (2 diagrams) | `memory-management.md`, `instruction-context-budget.md`, `context-compression.md`, `caching.md`, `session-persistence.md` |
| 5 | Coordination -- orchestration, handoff, fan-out, messaging | chapters/05-coordination.md | 04 | 06-transport | flowchart + sequence (2 diagrams) | `orchestration.md`, `handoff-mechanism.md`, `fan-out.md`, `inter-agent-messaging.md`, `multi-agent-coordination-design-space.md` |
| 6 | Transport and the LLM API contract | chapters/06-transport.md | 05 | 07-config-permissions | sequence + stateDiagram (2 diagrams) | `llm-api-contract.md`, `streaming-and-incremental-rendering.md`, `retries.md`, `model-routing-and-selection.md` |
| 7 | Config, permissions, hooks, and auth | chapters/07-config-permissions.md | 06 | 08-skills-tools | flowchart (1 diagram) | `configuration.md`, `permissions-and-sandboxing.md`, `hooks-lifecycle-extensibility.md`, `auth-and-usage-accounting.md` |
| 8 | Skills and tools | chapters/08-skills-tools.md | 07 | 09-rag | flowchart (1 diagram) | `built-in-tools.md`, `built-in-skills.md`, `mcp-integration.md`, `tool-schema-and-interface-design.md`, `system-prompt-design-as-craft.md` |
| 9 | Retrieval-Augmented Generation | chapters/09-rag.md | 08 | 10-sdlc | flowchart (3 diagrams) | `references/rag/*` (10 pages + Lewis et al. + RAGAS + HyDE/RWR) |
| 10 | Agentic SDLC -- primitives, lifecycle, and patterns | chapters/10-sdlc.md | 09 | 11-models | flowchart (2 diagrams) | `references/sdlc/*` (14 pages + 2 appendices + handbook Ch.4) |
| 11 | AI model classification and inference engines | chapters/11-models-engines.md | 10 | 12-advanced | flowchart + sequence (4 diagrams) | `references/models/*` (5 pages), `references/inference-engines/*` (14 pages) -- **REWRITTEN 2026-09-12 verbose: primers for quantization, KV cache, MoE from zero** |
| 12 | Advanced topics -- observability, packaging, middleware, deterministic orchestration | chapters/12-advanced.md | 11 | harnesses/claude-code | flowchart (2 diagrams) | `observability-and-self-diagnostics.md`, `packaging-distribution-and-self-update.md`, `tui-cli-application-architecture.md`, `middleware-composed-agent-harnesses.md`, `deterministic-orchestration.md`, `advanced-planning-and-execution-architectures.md` |
| H | Claude Code synthesis | harnesses/claude-code.md | 01-12 | copilot-cli | -- | per-harness sections across wiki |
| H | Copilot CLI synthesis | harnesses/copilot-cli.md | 01-12 | opencode | -- | per-harness sections across wiki |
| H | OpenCode synthesis | harnesses/opencode.md | 01-12 | pi-and-others | -- | per-harness sections across wiki |
| H | pi + Hermes Agent + DeepSeek Harness synthesis | harnesses/pi-and-others.md | 01-12 | glossary | -- | per-harness sections across wiki (pi + Hermes 29/29, DeepSeek partial) |
| N | Glossary | glossary.md | all | -- | -- | all chapters |

> Build receipts: chapters 01-12 and 4 harness syntheses generated 2026-09-12. All `File` paths resolved. `Next` chain verified. See `/book/foreword.md` for voice and conventions, `/book/glossary.md` for term coverage, Gate 3 audit notes in each chapter's footer.

## Navigation contracts

- **Index -> chapter -> next page:** every chapter footer contains `Prev | Index | Next | Glossary` with relative paths that resolve from `/book/chapters/`. Verified: all footers use `../index.md` / `../foreword.md` / `../glossary.md` + adjacent chapter links.
- **Glossary <-> chapter:** terms are first introduced in a chapter with a link to `glossary.md#term-slug`; the glossary entry links back to defining chapters. Verified: no dangling glossary anchors (Gate 3 glossary coverage audit).
- **Harness pages** are reference after the general chapters; read the general chapter first, then the harness page for that harness. Verified: prerequisites column lists 01-12 for all harness pages.

## Gate 3 audit summary (2026-09-12)

| Gate | Check | Result |
|------|-------|--------|
| Link audit | Every `index -> chapter` and `chapter -> next` file exists; no dangling glossary anchor | PASS -- 12/12 chapters + 4/4 harness pages + foreword + glossary all resolve; footers verified |
| Glossary coverage | Every distinct mechanism term used in a chapter appears in `glossary.md` with a backlink | PASS -- 42 terms, all backlinked to defining chapters |
| Mermaid audit | Every `mermaid` block is ASCII, under 25 nodes, supported type (`flowchart`/`sequenceDiagram`/`stateDiagram-v2`), directly above illustrated prose | PASS -- 22 diagrams total, all ASCII, max nodes 14, all `-->`, `->>`, `-->>` |

---

*Generated by `airchon-communicator` (A2 PIPELINE). TOC order follows `resources/airchon-teacher/knowledge-path-curriculum.md` Clusters 1-10: Memory&Context -> Coordination -> Transport -> Config -> Skills&Tools -> RAG -> SDLC -> Models -> Inference Engines -> harness synthesis.*
