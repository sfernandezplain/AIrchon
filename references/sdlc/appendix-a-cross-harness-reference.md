# Appendix A: The cross-harness reference

Source: **The Agentic SDLC Handbook**, Daniel Meppiel, Appendix A --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/appendix-a-cross-harness-reference.html.
See [index.md](index.md) for why this lives here rather than in
`references/harnesses/`. (Note: this page is a standalone digest of
what this handbook's appendix says; it does not read or reference this
project's separate `references/harnesses/` wiki-book.)

The appendix is a single master comparison table mapping ten APM
(Agent Primitives Model) primitive concepts against their concrete
file/config convention in each of five harnesses: **GitHub Copilot,
Claude Code, Cursor, Codex CLI, and OpenCode.**

## Master comparison table

| APM primitive | GitHub Copilot | Claude Code | Cursor | Codex CLI | OpenCode |
|---|---|---|---|---|---|
| Project-wide rules | `.github/copilot-instructions.md` | `CLAUDE.md` (repo root) | `.cursor/rules/*.mdc` (`alwaysApply: true`) | `AGENTS.md` (repo root) | `AGENTS.md` (repo root) |
| Scope-attached rules | `.github/instructions/*.instructions.md` with `applyTo:` glob | Nested `CLAUDE.md` per subtree | `.cursor/rules/*.mdc` with `globs:` | Nested `AGENTS.md` per subtree | Nested `AGENTS.md` per subtree |
| User-scope rules | `~/.copilot/instructions/` (partial) | `~/.claude/CLAUDE.md` | Cursor Settings UI (not file-based) | (no file convention) | `~/.config/opencode/AGENTS.md` |
| Persona / specialist agent | `.github/agents/<name>.agent.md` | `.claude/agents/<name>.md` (Task tool) | `.cursor/agents/<name>.md` (modes) | `.codex/agents/<name>.toml` | `.opencode/agents/<name>.md` |
| Skill (module entrypoint) | `.github/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` | `.cursor/skills/<name>/SKILL.md` (partial) | `.agents/<name>/SKILL.md` (cross-tool dir) | `.opencode/skills/<name>/SKILL.md` |
| Prompt / repeatable workflow | `.github/prompts/*.prompt.md` | (use slash commands) | (none -- partial via rules) | (none) | `.opencode/commands/*.md` |
| Memory (cross-session) | (use scoped instructions) | `CLAUDE.md` + `@path` imports | `.cursor/rules/*.mdc` (`alwaysApply`) | `AGENTS.md` | `AGENTS.md` |
| Hooks (event-driven) | `.github/hooks/*.json` | `.claude/hooks/*.json` (merge into `settings.json`) | `.cursor/hooks/*.json` | `.codex/hooks.json` (single file) | (no native hooks) |
| MCP server config | `.github/mcp.json` or VS Code settings | `.claude/settings.json` (`mcpServers` block) | `.cursor/mcp.json` | `.codex/config.toml` (`[mcp_servers]`) | `.opencode/mcp.json` |
| Session compaction / restart | `/compact` (Copilot CLI session compaction) | `/compact` (Claude Code) | (manual: new chat / "Reset context" in chat header) | `/new` (Codex CLI session refresh) | `/compact` (OpenCode) |

## Key observations named in the appendix

- **"AGENTS.md is one file in two roles"** across Codex CLI and
  OpenCode -- the same file serves both project-wide and
  scope-attached rule purposes through hierarchical nesting.
- **"SKILL.md is the only file name that ports cleanly"** across all
  harnesses that support skills, using "substantially the same
  activation contract."
- **"Persona files are convention, not standard"** -- each harness
  uses a different syntax (markdown, TOML) despite expressing the same
  concept.

## Per-harness technical notes

- **GitHub Copilot.** Load order processes `~/.copilot/` first, then
  `.github/copilot-instructions.md`, then alphabetically-ordered
  `*.instructions.md` files. "Over-eager `applyTo: \"**\"` is the
  single most common Copilot failure," because it consumes attention
  budget before lazy skills load.
- **Claude Code.** Uses "closest-wins" override semantics, where only
  the deepest nested `CLAUDE.md` applies. Supports `@path` import
  syntax for inlining files at load time.
- **Cursor.** User-scope rules exist only in the Settings UI, not the
  filesystem, creating "hidden state in each developer's IDE
  settings."
- **Codex CLI.** Skills materialize to the cross-tool `.agents/`
  directory rather than `.codex/` -- "the cross-tool directory is the
  trap" if installing skills manually.
- **OpenCode.** "Hooks are the missing primitive," with no native
  hooks support; policies must be re-expressed in instructions or
  slash commands.

## Cross-harness convergence

The appendix names **"agentskills.io as the cross-harness
convergence"** -- an open registry standard where descriptions load
eagerly into a small registry and bodies load lazily upon selection.
This standard was adopted by all five harnesses in substantially
compatible form.

## Source

Appendix A: The Cross-Harness Reference --
https://danielmeppiel.github.io/agentic-sdlc-handbook/handbook/appendix-a-cross-harness-reference.html
