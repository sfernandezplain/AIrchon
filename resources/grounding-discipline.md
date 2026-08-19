# Source Authority & Grounding Rules

Shared by `airchon-mentor` and `airchon-author`. Read when forming any claim about harness behavior.

## Sources and their authority bounds

- `code.claude.com/docs` — Claude Code's documented behavior, configuration, tool names, hooks, MCP support.
- `docs.github.com/copilot` — Copilot CLI's documented behavior, configuration, tool names, MCP support.
- `github.com/anthropics/claude-code` — its own CHANGELOG.md, README, `examples/`, plugin manifests, and Issues. NOT authoritative for internal implementation (this repo ships none).
- `github.com/github/copilot-cli` — same split: CHANGELOG.md, README, install script, Issues are real; no implementation source here either.
- `github.com/anomalyco/opencode` (`dev` branch) + `opencode.ai/docs` — OpenCode's documented behavior AND its real open-source implementation (genuinely inspectable, unlike the two above). The `dev` branch may not reflect the current stable release; flag this when citing source code. Its implementation choices are never assumed to hold for Claude Code or Copilot CLI (AUTHORITY OVERREACH still applies), but it can serve as a general implementation reference for agent-loop / tool / session patterns.
- Anthropic/GitHub engineering blogs, the MCP spec (`modelcontextprotocol.io`), and other named official pages — authoritative for whatever they themselves document; verify each is the actual current page before citing.
- `huggingface.co/learn/agents-course` and `huggingface.co/learn/context-course` — general agent-engineering concepts only (the agent loop, MCP as a concept, multi-agent patterns). Never authoritative for a harness-specific claim -- use for shared conceptual vocabulary only.

No source is authoritative beyond what it itself documents. A mechanism confirmed for one harness is never assumed to hold for another without its own citation (AUTHORITY OVERREACH).

## gh CLI fallback

Check `gh --version` before using `gh api`/`gh repo view`/`gh issue list` for repo metadata, changelogs, or issues -- fall back to fetching the GitHub URL directly if `gh` is not installed. Use web search for anything not covered by the sources above.
