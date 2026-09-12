# Harness Page Template -- The Road to Agentic Archon

Use for `/book/harnesses/{{harness}}.md` (one per harness with at least partial parity in `references/harnesses/index.md`).

```markdown
# {{Harness}} -- Concrete synthesis

**Reading prerequisite:** general-concept chapters that this harness implements (e.g. Ch. Agent Loop before this page).

## At a glance

Two paragraphs: what this harness concretely is (product, owner, distribution channel), and where it sits on the taxonomy this book already taught (agent-topology axes, loop shape, orchestration model). Cite the wiki's own `references/harnesses/{{topic}}.md` § harness section.

## Config and precedence

Table of the harness's own config scopes or precedence chain (e.g. Claude Code's Managed/User/Project/Local vs Copilot's ~/.copilot layout). Name actual file paths and keys. One row per scope.

## Loop, memory, and compression -- how this harness fills the general shape

Three subsections, each mapping the general-concept chapter back onto this harness's documented machinery (with Mermaid `sequenceDiagram` or `stateDiagram-v2` where visual helps). Include actual limit names (`max_turns`, `max_budget_usd`, `CLAUDE_CODE_MAX_RETRIES`, compaction trigger %). 

## Tools, skills, and extensibility

Tool table (permission-required column where the wiki documents it), skill/hook/MCP registration surface for this harness.

## What this harness does differently (honest comparison)

One paragraph per genuine divergence from the other harnesses the book covers, tagged VERIFIED with the wiki source section. One paragraph per honest gap ("not yet in the wiki / not documented -- ask airchon-author").

## Navigation

- Back: [General concept chapters that feed this page](../chapters/...)
- Index: [index.md](../index.md) | Glossary: [../glossary.md]

## Sources

Inherits citations from `references/harnesses/{{topic}}.md` § harness section; no new unverified citation from pretraining.
```
