# Course Progress Tracker Template

Load-trigger: Read this file when Course-Delivery Flow's CD2 needs to
initialize a fresh `~/.airchon/course-progress.md`, or whenever you need
the exact field layout to update it after any interaction (teaching an
item, presenting or grading an exercise, running a transition-exam
question). Not needed for the classification flow (Steps 1-8) -- that
flow only ever touches `~/.airchon/level` and `~/.airchon/qualify-exam.md`,
never this file.

Added 2026-08-18 alongside Course-Delivery Flow -- see
`airchon-teacher.agent.md`'s Constraints & Scope and `CHANGELOG.md`'s
2026-08-18 entry for why this agent now delivers courses instead of
only classifying into a tier.

```markdown
# Course Progress

**Tier (course):** Gnostic -> Demiurge
**Course file:** resources/airchon-teacher/gnostic-to-demiurge-sessions.md
**Total sessions:** 27
**Next course (after this one):** Demiurge -> Archon
**Harness:** Claude Code
**Last updated:** [auto-filled, every interaction]

## Sessions

- [x] Session 1 -- Memory management
  - Items covered: 1, 2, 3, 4
  - Exercise: passed (2026-08-18) -- "<reader's submission, verbatim>"
  - (or: passed-with-notes (2026-08-18, 3 attempts) -- reader chose to
    stand by their attempt after CD5's three-failure resolution offer;
    "<final submission, verbatim>" -- honestly logged, never silently
    upgraded to a clean pass)
- [ ] Session 2 -- Instruction context budget
  - Items covered: 1, 2
  - Items uncovered: 3, 4
  - Exercise: not yet reached
- [ ] Session 3 -- Context compression
  - Items covered: (none yet)
  - Exercise: not yet reached
- [... one entry per session in the course file, straight through to
  the final capstone session, in that file's own order and numbering ...]

## Current Exercise

**Session:** 2
**Statement:** "<the exact exercise text presented to the reader --
either the session's own named exercise, or the corresponding module's
Exercise field pulled from knowledge-path-curriculum.md>"
**Status:** pending / submitted / passed / failed (N attempts) /
passed-with-notes (offered only after 3 failed attempts, per CD5)
**Reader's submission:** "<raw text, once submitted>"

## Transition Exam (Gnostic -> Demiurge)

**Status:** not started / in progress / passed / failed

### Attempt 1 | Date: [auto-filled]
- Q1: "<response>" -> correct (1)
- Q2: "<response>" -> incorrect (0)
- ...
- Q10: "<response>" -> correct (1)

**Score:** 6 / 10
**Result:** PASSED -- tier updated to Demiurge on [date]
```

**Sessions are listed in the course file's own order and numbering --
never reordered or renumbered here.** Unlike `qualify-exam.md`, there is
no tier-concealment concern for this file: the reader already knows
their current tier and which course they're taking, so there is nothing
here that needs to be withheld from them.

**Update this file after every interaction, not only at session or
exercise boundaries.** Per-item covered/uncovered state, the exact
exercise statement once presented, and each transition-exam
question/answer/outcome must all be persisted as they happen -- CD7
("Resume After Interruption") depends on this file, not on conversation
recall, being the source of truth for where a reader actually is.

**Only one "Current Exercise" block and one course's "Sessions" list
exist at a time.** When a course completes (the transition exam
passes), this file is either reinitialized for the next course (a new
tier/course header, a fresh Sessions list) or, if the reader just
reached Archon, left as a closed record with no next course to start --
Course-Delivery Flow's CD1 returns the Ceiling note in that case rather
than reinitializing this file into a course that doesn't exist.
