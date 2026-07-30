---
name: airchon
description: Use this skill when the user asks how an AI agent harness actually works internally -- Claude Code, GitHub Copilot CLI, or OpenCode specifically, or agent harnesses generally -- topics like memory management, handoff/compaction, built-in tools, MCP server integration, context compression, prompt caching, orchestration, fan-out, inter-agent messaging, retry behavior, configuration, or built-in skills and how to use them. Also trigger on "how would I build a harness like this", comparisons between harnesses, or a request to go deep on one specific mechanism.
user-invocable: true
disable-model-invocation: false
allowed-tools:
  - Agent(airchon-mentor)
---

Thin router. This skill does no mentoring itself -- it exists only so
`/airchon` and discovery-based invocation both land in one place, and
so the actual mentor is reachable on both Claude Code and Copilot CLI
(skills don't deploy to Copilot; the `airchon-mentor` agent does).

**On every invocation:** call the `airchon-mentor` agent via the Agent
tool, in the foreground (`run_in_background: false`, since this is a
live conversation, not a background task), passing the user's question
verbatim as the prompt plus any context already established this
conversation. Return its answer as your response -- do not paraphrase,
summarize, or add your own commentary on top of it.

Currently routes to a single persona (`airchon-mentor`). If more
persona agents are added later (different tone, different audience),
this is the file that grows a selection step before the Agent call --
do not pre-build that selection now, nothing to route between yet.
