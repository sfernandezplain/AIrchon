# Exam File Template

Load-trigger: Read this file when you reach Step 2 of
`airchon-teacher.agent.md` (generating a fresh exam, whether direct
or via the routed `generate` mode) and need the exact file structure
to write to `~/.airchon/qualify-exam.md`. Not needed for a cached
tier lookup, a self-assignment, or a retake confirmation prompt --
those paths never touch this file.

```markdown
# Qualification Exam

**Instructions:** Answer all 40 questions. Each correct answer = 0.25 points. Final score determines your tier.

**Test-like questions** are marked [CHOICE] or [SHORT]; **free-response** are marked [ESSAY].

---

## Tier 1: Slumberer (Questions 1-10)

**Question 1** [CHOICE]
What is the primary role of a task() spawn in an agent harness?
A) Delegate work to a background agent
B) Cache API responses
C) Validate input syntax
D) Compile source code

**Question 2** [SHORT]
Name one key difference between DISCOVERY-invocable and FORCED-only skills.

**Question 3** [ESSAY]
Describe, in 2-3 sentences, what happens to a tool's output in the Thought/Action/Observation loop, and why that step has to complete before the model can produce its next Thought.

[... 7 more Slumberer questions ...]

---

## Tier 2: Gnostic (Questions 11-20)

**Question 11** [SHORT]
A harness's checklist/todo tool can either live only in that turn's message stream, or persist to disk across turns. Name one concrete problem this causes for a long, multi-step plan if the checklist is message-stream-only and the session later gets compacted or resumed.

[... 9 more Gnostic questions ...]

---

## Tier 3: Demiurge (Questions 21-30)

**Question 21** [ESSAY]
Compare Claude Code's two-phase evict-then-summarize context-compression mechanism to Copilot CLI's checkpointed background-compaction approach. When would one design be preferable to the other?

[... 9 more Demiurge questions ...]

---

## Tier 4: Archon (Questions 31-40)

**Question 31** [ESSAY]
This book's own gap analysis found that none of Claude Code, Copilot CLI, or OpenCode implement a loop-integrated self-critique or tree-search-style planning mechanism inside their primary task loop. Design a from-scratch mechanism that would close this gap, and explain how it would bridge from model-asserted judgment to a deterministic verification step.

[... 9 more Archon questions ...]

---

## User Responses & Scores

*Append response block here after exam completion.*

### Attempt 1 | Date: [auto-filled]
- Q1: [response] -> correct (0.25)
- Q2: [response] -> correct (0.25)
- ...
- Q40: [response] -> incorrect (0.00)

**Raw Score:** 7.5 / 10.0
**Tier:** Demiurge
**Timestamp:** [auto-filled]
```

This file's tier headers (`## Tier 1: Slumberer`, etc.) are for your
own scoring bookkeeping only -- they organize the answer key so you
can compute the per-tier breakdown in Step 4. They are a private
local artifact; the reader is not shown this file's structure. What
the reader actually sees is built in Step 3 (or the routed `generate`
mode's returned question list), which shuffles the presentation order
and drops every tier label.
