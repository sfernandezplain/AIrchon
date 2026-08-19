---
name: airchon
description: Use this skill when the user asks how an AI agent harness works internally -- Claude Code, GitHub Copilot CLI, or OpenCode, or harnesses generally -- covering memory, compaction, tools, MCP, context compression, caching, orchestration, fan-out, inter-agent messaging, retries, or configuration. Also trigger on harness comparisons, going deep on one mechanism, "how would I build a harness like this", writing or updating a wiki-book page at references/harnesses/, reviewing the user's OWN project agent-harness setup (skills, agent files, hooks, permissions, orchestration), or anything about classes, courses, formation, proficiency level or tier, continuing a lesson, or exercise correction.
user-invocable: true
disable-model-invocation: false
allowed-tools:
  - Agent(airchon-mentor)
  - Agent(airchon-author)
  - Agent(airchon-teacher)
  - TaskCreate
  - TodoWrite
---

Thin router. Classifies the request, dispatches to exactly one of
`airchon-mentor`, `airchon-author`, or `airchon-teacher` via the host's
agent-spawning primitive (`Agent(...)` when available, `TaskCreate`
otherwise), and relays the agent's response verbatim -- no added
judgment, editing, or framing of its own.

**Step 0 -- Dispatch capability check (run before anything else):**
Check whether `Agent(...)` appears in the active tool list for this
invocation. If it does, use it. If it does not, dispatch the matching
agent through `TaskCreate` instead of redirecting the user. The router
should always prefer a real subagent call over a user-facing fallback
when the host gives it one.

**On every invocation:**
1. Classify the request:
   - TEACHING/ASSESSMENT intent -- classes, courses, formation/
     training, the user's current proficiency level or tier, "assess
     my proficiency", "what is my tier", "take the exam", "retake the
     exam", continuing a lesson, or getting an exercise corrected ->
     call `airchon-teacher`. See **Exam Administration** below for the
     one sub-flow ("take/retake the exam") that is a multi-call
     pipeline rather than a single call.
   - AUTHORING intent -- the user asks to write up, add, document,
     update, or persist a topic into the wiki-book ("write this up",
     "add this to references/harnesses", "update the page on X",
     "document this in the wiki-book", or names a page that needs
     creating/updating) -> call `airchon-author`.
   - Otherwise (the default) -- the user is asking a question, wants
     something explained, wants a comparison, or wants their OWN
     project's agent-harness setup reviewed/critiqued -> call
     `airchon-mentor`.
2. For every branch except the exam sub-flow: call exactly one agent
   via the available agent-spawning primitive in the foreground,
   passing the user's request verbatim plus any context established this
   conversation. Relay the returned text verbatim as this skill's own
   response -- no rewording, no framing, no attribution to the
   sub-agent.

**Ambiguity rules:** TEACHING/ASSESSMENT is checked first (trigger
nouns -- classes, courses, level, lesson, exercise, exam, tier --
don't overlap the other two domains). When intent is ambiguous between
AUTHORING and the conversational default, call `airchon-mentor` --
answering the question is the safer default than assuming authoring
intent. The one exception to one call per request is the exam
sub-flow immediately below.

### Exam Administration (multi-call pipeline, `airchon-teacher` only)

`airchon-teacher`'s own persona file (see its Routed-Invocation
Protocol section) explains why this branch alone is a pipeline: a
subagent call made through the available agent-spawning primitive runs
to completion and returns exactly once, so it cannot pause mid-exam to
show one question, wait for the reader's reply, then resume for the
next. Reaching it through this router therefore makes THIS skill
responsible for live pacing and rendering during a "take/retake the
exam" request -- it calls back into `airchon-teacher` once per step of
the exam using that agent's own `generate` / `grade` / `finalize` JSON
contracts:

1. Call `airchon-teacher` once in `generate` mode through the available
   agent-spawning primitive (`Agent(...)` when present, `TaskCreate`
   otherwise). Take the returned ordered, tier-blind question list and
   build the visible tasklist from it using the task list tool -- one
   item per question, titled only "Question N of 40" plus its format
   tag, in the order returned. Never add a tier label to any item's
   title.
2. Present question 1's text in the chat and wait for the reader's
   answer. On each answer, call `airchon-teacher` in `grade` mode
   through the available agent-spawning primitive with that question's
   `order` and the reader's raw answer, show the returned `explanation`
   to the reader verbatim, mark that item's task done, then present the
   next question. Repeat for all 40 -- never present more than one
   question at a time, same discipline `airchon-teacher` itself follows
   in its direct-invocation path.
3. Once all 40 are graded, ask the reader which harness they use
   (Claude Code or Copilot CLI) if it isn't already established, then
   call `airchon-teacher` in `finalize` mode through the available
   agent-spawning primitive with that harness name and show the
   returned `summary` verbatim.

**On resume** (this conversation gets interrupted, compacted, or
restarted mid-exam): do not restart the exam or re-call `generate`.
Re-derive position from the tasklist itself -- whichever items are
still marked pending are the questions left to present; re-enter the
loop at step 2 above from there. `airchon-teacher` independently
re-derives its own state (the answer key and already-graded
questions) from `~/.airchon/qualify-exam.md` on its next `grade` call,
so the two sides re-synchronize from disk, not from either side's
recall.

**Cache discipline:** put the per-call variable payload (the
question's `order` plus the reader's raw answer) at the END of each
`grade` call's prompt, after everything else. That keeps the
instructional prefix identical across all ~42 calls in one exam so
they can share a cache hit instead of re-billing full price on every
call.

This is still a single agent TYPE end to end (`airchon-teacher`), and
this skill originates none of the exam's content at any step -- every
question, explanation, grade, and the final summary come from
`airchon-teacher`'s own JSON. This skill's added work is exclusively
pacing the conversation and rendering the tasklist via the task list tool,
never judging or teaching -- that discipline is what keeps this branch
consistent with the "no mentoring, authoring, or assessment judgment
of its own" rule at the top of this file, despite the extra calls.
Every other TEACHING/ASSESSMENT request (a cached "what is my tier"
lookup, self-assignment without an exam) stays a single `Agent` call,
exactly like the mentor/author branches -- only the full
take/retake-the-exam flow is this multi-call pipeline.
