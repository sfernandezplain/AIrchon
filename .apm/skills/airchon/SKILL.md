---
name: airchon
description: Use this skill when the user asks how an AI agent harness actually works internally -- Claude Code, GitHub Copilot CLI, or OpenCode specifically, or agent harnesses generally -- topics like memory management, handoff/compaction, built-in tools, MCP server integration, context compression, prompt caching, orchestration, fan-out, inter-agent messaging, retry behavior, configuration, or built-in skills and how to use them. Also trigger on "how would I build a harness like this", comparisons between harnesses, a request to go deep on one specific mechanism, or a request to write up, add, document, update, or persist a topic into the shared wiki-book at references/harnesses/.
user-invocable: true
disable-model-invocation: false
allowed-tools:
  - Agent(airchon-mentor)
  - Agent(airchon-author)
---

Thin router. This skill does no mentoring or authoring itself -- it
classifies the request, then calls exactly one of two specialist
agents via the Agent tool and returns that agent's answer verbatim.
`airchon-mentor` and `airchon-author` are reachable this way on Claude
Code, and directly (bypassing this router) on both Claude Code and
Copilot CLI, since skills don't deploy to Copilot; the agents do.

**On every invocation:**
1. Classify the request:
   - AUTHORING intent -- the user asks to write up, add, document,
     update, or persist a topic into the wiki-book ("write this up",
     "add this to references/harnesses", "update the page on X",
     "document this in the wiki-book", or names a page that needs
     creating/updating) -> call `airchon-author`.
   - Otherwise (the default) -- the user is asking a question, wants
     something explained, or wants a comparison -> call
     `airchon-mentor`.
2. Call exactly ONE of the two agents via the Agent tool, in the
   foreground (`run_in_background: false`, since this is a live
   conversation, not a background task), passing the user's request
   verbatim as the prompt plus any context already established this
   conversation.
3. Return that agent's answer as your response -- do not paraphrase,
   summarize, or add your own commentary on top of it.

Never call both agents for one request -- they are mutually exclusive
branches, not a pipeline. `airchon-mentor` never writes to the
wiki-book, even when its own live research fills a gap; `airchon-
author` is the only writer. If the intent is ambiguous, default to
`airchon-mentor` -- answering the question in front of you is the
safer default than assuming an authoring intent that was not there.

Currently routes to exactly two personas. If more mentor-style
personas are added later (different tone, different audience), this
is the file that grows another classification branch -- do not
pre-build that now.
