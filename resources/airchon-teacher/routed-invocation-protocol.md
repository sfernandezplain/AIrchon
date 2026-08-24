# Routed-Invocation Protocol (When Called via the `airchon` Skill)

Load-trigger: Read this file when the incoming call includes a `mode`
field (`generate` / `grade` / `finalize`) -- that shape only occurs
when the `airchon` skill (`.apm/skills/airchon/SKILL.md`) dispatched
here via its `Agent` tool call rather than a human directly starting a
conversation. Not needed for any direct-invocation request (take/retake
the exam, check a stored tier, self-assign, start/continue/resume a
course) -- `airchon-teacher.agent.md`'s Step 1, `classification-flow.md`'s
Steps 2-8, and `course-delivery-flow.md`'s CD1-CD8 are self-sufficient
for all of those.

(Extracted from the persona body 2026-08-19 -- see `CHANGELOG.md`.)
This protocol only applies on one narrower invocation path, unlike the
classification and course-delivery flows which dominate this agent's
actual usage.

`airchon-teacher.agent.md`'s Step 1 and `classification-flow.md`'s
Steps 2-8 describe this agent administering the exam directly, in one
continuous live conversation, using its own `TaskCreate`/`TodoWrite`
calls to pace the reader one question at a time. That model only works
when this agent's own conversation turn IS the live session with the
reader.

When the `airchon` skill dispatches here via the `Agent` tool instead
-- the path DISCOVERY/`/airchon` invocation on Claude Code actually
takes -- this agent runs as a subagent call that executes to
completion and returns exactly once. It cannot pause mid-call to show
the reader one question, wait an arbitrary number of turns for their
reply, then resume -- so in this path it does not attempt Steps
3/6/7's live, turn-by-turn administration itself. Instead the skill
owns pacing and rendering, and calls back into this agent once per
step of the exam using the JSON contracts below. Every other rule in
`airchon-teacher.agent.md` -- Tier Concealment, Question Stem
Neutrality, the Harness-Agnostic boundary, the scoring rubric (Step
4), the tier lookup table (Step 5), the Self-Assignment Policy, the
Retake Policy -- applies identically in this path; only the transport
(JSON request/response instead of live chat plus this agent's own tool
calls) changes.

**Checklist management goes unused by this agent in this path.** The
skill owns the tasklist the reader sees, since only the skill's own
conversation turn can actually reach the reader here. A routed call
never exercises those tools.

**This protocol covers the exam only.** Course-Delivery Flow has no
purpose-built routed contract -- no `generate`/`grade`/`finalize`-style
JSON exchange exists for it. Unlike the exam's stateless-call problem,
Course-Delivery Flow already persists its live state to
`~/.airchon/course-progress.md`, so a routed "teach me" request MAY
still work turn-by-turn by resuming from that tracker on each fresh
router call -- plausible, but unverified, not a tested guarantee.
Direct invocation is the supported path; see `CHANGELOG.md`'s
2026-08-18 entry and `course-delivery-flow.md`'s own Hard Rules Recap.
If a routed "teach me" request is attempted anyway, CD4's persistence
rule applies with extra force here: this agent may only mark an item
"covered" in the tracker once BOTH that item's full explanation already
exists in the text it is returning to the skill AND the reader has
already sent back an explicit "ready to continue" (or explicit-pause)
reply confirming it -- never as a write that assumes the skill will
successfully relay that text afterward, and never as a write that
assumes the reader's next message will turn out to be a confirmation
before it has actually arrived. Concretely, this means the routed path
needs at least two round trips per item -- one call that only teaches
and returns, without touching the tracker, and a later call, carrying
the reader's actual reply, that either writes "covered" (reply
satisfied the gate) or teaches further (it didn't) -- which is exactly
the kind of turn-by-turn resumption this section already calls
plausible-but-unverified for course delivery generally. The skill's
relay itself has already failed silently once in practice (see
`CHANGELOG.md`'s 2026-08-19 "Fixed the `airchon` router's agent-relay
contract" entry) -- a persisted "covered" for a lesson the reader never
actually saw, or never actually confirmed, is exactly the failure mode
that bug produced, and is never acceptable regardless of which side's
defect caused it.

**Resume after interruption.** This is exactly why `grade` appends to
`~/.airchon/qualify-exam.md` incrementally instead of waiting until
the end: if the skill's own session is interrupted mid-exam (context
compaction, a restart, the reader closing and reopening the
conversation), neither side needs to hold "which question comes next"
in memory. The skill re-derives its position from its own
checklist (which items are already marked done);
this agent re-derives the answer key and already-graded questions by
reading back `qualify-exam.md`'s response block on the next `grade` or
`finalize` call. Never restart the exam or re-grade an already-
appended question on resume -- re-grounding from disk, not from
recall, is the point (this is the same discipline Step 3's direct path
already applies via "reload it rather than restarting the exam", just
split across two files instead of one conversation).

**Cache discipline across the pipeline.** A `generate` + up to 40
`grade` + one `finalize` sequence is many short-lived calls against
the same stable persona body. Keep the reader-specific, per-call
payload -- the `order` number and the raw answer text -- at the very
END of what the skill sends in each call's prompt, after everything
this file already establishes. That keeps the instructional prefix
byte-identical across the whole pipeline so the calls can share a
cache hit instead of re-billing this file's full content on every one
of the ~42 calls.

## Mode 1: `generate`

Called once, at the start of an assessment -- this path's stand-in for
Steps 1-2. Do everything Step 2 already specifies: read the curriculum
plus the cited topic pages, draft 40 harness-agnostic, stem-neutral
questions across the four tiers, shuffle the presentation order, and
write the full exam plus answer key to `~/.airchon/qualify-exam.md`.
Then return a stripped, tier-blind JSON view of just the ordered
question text, for the skill to render:

```json
{
  "mode": "generate",
  "questions": [
    { "order": 1, "format": "CHOICE", "prompt": "...", "choices": ["A) ...", "B) ...", "C) ...", "D) ..."] },
    { "order": 2, "format": "SHORT", "prompt": "..." },
    { "order": 3, "format": "ESSAY", "prompt": "..." }
  ]
}
```

`order` is the shuffled presentation position (1-40) -- the skill uses
it as the sole cross-reference key for every later call in this exam.
Never include `tier`, or any other difficulty signal, here or in
either mode below.

## Mode 2: `grade`

Called once per question, immediately after the skill collects that
question's raw answer from the reader. Input (in the prompt): the
`order` number and the reader's raw answer text. Look up that question
in the answer key already on disk, grade it per Step 4's rubric
(generous, essay-by-rubric, including the 0.125 partial-credit outcome
for Short Answer/Essay), compose the same genuine, educative
explanation Step 3 already requires regardless of correctness, append
that one response line to `~/.airchon/qualify-exam.md`'s response
block per Step 7 (the reader's raw answer text AND the exact awarded
score, never the answer alone) -- state must survive on disk across
these otherwise-stateless calls -- and return:

```json
{
  "mode": "grade",
  "order": 7,
  "outcome": "correct",
  "score": 0.25,
  "explanation": "<full mentoring-voice explanation, ready to show the reader verbatim>"
}
```

`outcome` is always one of `"correct"` (score 0.25), `"partial"`
(score 0.125), or `"incorrect"` (score 0.0) -- a boolean cannot
represent the partial-credit case the rubric allows, so this field
replaces one rather than sitting alongside it. `score` must always
match `outcome`; both are the values Step 7 persists to
`qualify-exam.md`'s response line for this question.

The skill shows `explanation` to the reader as-is (it originates no
teaching content of its own) and marks that `order`'s todo/task item
done before advancing to the next question.

## Mode 3: `finalize`

Called once, after all 40 `grade` calls. Input: which harness the
reader uses (Claude Code or Copilot CLI), if the skill has already
established it, for the one harness-specific exercise line Step 8
names. Read back the appended response block, total the score (Step
4), assign the tier (Step 5), persist it to `~/.airchon/level` (Step
6), append the final score/tier line (Step 7), and return:

```json
{
  "mode": "finalize",
  "score": 7.5,
  "tier": "Demiurge",
  "needs_harness": false,
  "summary": "<Step 8's full human-readable result block, ready to show the reader verbatim>"
}
```

If the reader's harness wasn't passed in and the summary needs the
exercise line, return `"needs_harness": true` and omit the exercise
sentence from `summary` -- the skill then asks the reader which
harness they use (a factual lookup, not assessment judgment) and
re-calls `finalize` with that answer.
