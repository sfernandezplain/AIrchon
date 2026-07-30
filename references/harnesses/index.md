# Harness engineering wiki-book -- index

Maintained by `airchon` (`.apm/skills/airchon/SKILL.md`).
Prose-navigable reference on how AI agent harnesses actually work --
Claude Code and GitHub Copilot CLI specifically, agent-harness
engineering generally. Every claim in every page is tagged VERIFIED
(fetched from a named, authoritative source this session or a prior
one) or BEST CURRENT UNDERSTANDING, UNCONFIRMED -- never blended. See
each page's own "Sources" section for what was actually checked and
when.

Written LAZY, on demand, as real questions need each topic -- not
pre-built speculatively. A missing page below is real follow-up work,
not an oversight.

## Topics

| Topic | Status |
|---|---|
| [The agent loop](agent-loop.md) | Written 2026-07-30 -- GENERAL-CONCEPTS page (no harness sections, deliberately): Thought/Action/Observation, ReAct, the while-loop framing, observations appended to the prompt, stop-and-parse, JSON vs. code vs. function-calling agents |
| [Agent loop: Claude Code vs. OpenCode](agent-loop-implementations.md) | Written 2026-07-30 -- harness-specific companion to agent-loop.md: Claude Code's Agent SDK-documented loop (turns, max_turns/max_budget_usd, compaction, parallel tool execution) vs. OpenCode's documented + live-source-verified loop (primary/subagents, step-limit system-prompt injection, `packages/core/src/session/runner/max-steps.ts`), plus exactly where to read OpenCode's real implementation next |
| [MCP integration](mcp-integration.md) | Written 2026-07-30 -- discovery/registration/invocation, config formats, transports, tool-calling semantics, both harnesses |
| [Memory management](memory-management.md) | Written 2026-07-30, updated 2026-07-30 (mid-session edit/reload semantics, §1.8 + §2.5) -- instruction-file hierarchies, Claude Code auto memory vs. server-side Copilot Memory, injection timing, whether an edited CLAUDE.md is re-read, compaction survival, session resume, both harnesses |
| [Instruction context budget](instruction-context-budget.md) | Written 2026-07-30 -- keeping the eagerly-loaded instruction tier small: why `@` imports don't help, path-scoped rules (`paths:`) vs. `applyTo:`, skills as the invoke-only tier, exclusion/trim levers, how to measure what loaded, both harnesses |
| Handoff mechanism (compaction/context handoff) | Not yet written -- partially covered by [memory-management.md](memory-management.md) sections 1.7 / 2.4 (what survives compaction, thresholds); a dedicated page would add handoff-between-agents mechanics |
| Built-in tools | Not yet written |
| Context compression | Not yet written -- the *instruction-loading* half is covered by [instruction-context-budget.md](instruction-context-budget.md); a dedicated page would add mid-run compression (tool-output eviction, summarization quality, token accounting) |
| Caching (prompt/context caching) | Not yet written |
| Orchestration | Not yet written |
| Fan-out (subagent dispatch) | Not yet written |
| Inter-agent messaging | Not yet written |
| Retries | Not yet written |
| Configuration | Not yet written |
| Built-in skills | Not yet written |
