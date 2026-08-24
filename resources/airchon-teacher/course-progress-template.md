# Course Progress Tracker Template

Load-trigger: Read this file when Course-Delivery Flow's CD2 needs to
initialize a fresh `~/.airchon/course-progress.md`, or whenever you need
the exact field layout to update it after any interaction (teaching an
item, presenting or grading an exercise, running a transition-exam
question). Not needed for the classification flow (Steps 1-8) -- that
flow only ever touches `~/.airchon/level` and `~/.airchon/qualify-exam.md`,
never this file.

Added 2026-08-18 alongside Course-Delivery Flow -- see
`course-delivery-flow.md`'s own Hard Rules Recap and `CHANGELOG.md`'s
2026-08-18 entry for why this agent now delivers courses instead of
only classifying into a tier.

```markdown
# Course Progress

**Tier (course):** Gnostic -> Demiurge
**Course file:** resources/airchon-teacher/gnostic-to-demiurge-sessions.md
**Total sessions:** 45
**Next course (after this one):** Demiurge -> Archon
**Harness:** Claude Code
**Last updated:** [auto-filled, every interaction]

## Sessions

- [x] Session 1 -- Memory management
  - Items covered: 1 -- What memory means in a harness context;
    2 -- Working vs. persistent memory; 3 -- Injection timing;
    4 -- Eviction/summarization triggers
  - Exercise: passed (2026-08-18) -- scaffold at
    ~/.airchon/exercises/gnostic-to-demiurge-session1-exercise/ --
    "<reader's submission, verbatim>"
  - (or: passed-with-notes (2026-08-18, 3 attempts) -- reader chose to
    stand by their attempt after CD5's three-failure resolution offer;
    "<final submission, verbatim>" -- honestly logged, never silently
    upgraded to a clean pass)
- [ ] Session 2 -- Instruction context budget
  - Items covered: 1 -- What counts against the instruction budget;
    2 -- Static vs. dynamic budget allocation
  - Items uncovered: 3 -- Budget exhaustion failure modes;
    4 -- Trade-offs in reserving headroom
  - Paused: 2026-08-19 -- reader explicitly chose to pause instead of
    continuing right after confirming item 2 was done; resume at item 3
    (see CD8)
  - Exercise: not yet reached
- [x] Session 3 -- Context compression
  - Items covered: 1 -- Summarization vs. eviction; 2 -- Compression
    trigger thresholds; 3 -- What survives a compaction pass
  - Session exam: passed (7/10, 2026-08-19) -- purely conceptual
    session, no scaffold-eligible artifact (CD4 step 4) -- see
    ~/.airchon/session-3.exam.md for the full question/answer record
- [ ] Session 4 -- Tool-result caching
  - Items covered: 1 -- Cache key derivation
  - Items pending confirmation: 2 -- Cache invalidation triggers
    (fully taught -- the conversation ended, e.g. a context compaction,
    before the reader replied to the "ready to continue?" gate CD4
    asks after every item; per CD8, resume by re-asking that same gate,
    never by re-teaching the item from scratch)
  - Items uncovered: 3 -- Stale-cache failure modes;
    4 -- Trade-offs against always-fresh reads
  - Exercise: not yet reached
- [... one entry per session in the course file, straight through to
  the final capstone session, in that file's own order and numbering;
  each one ends in EITHER an "Exercise:" line (scaffold-backed, graded
  via CD5) OR a "Session exam:" line (CD6's fallback), never both ...]

## Current Exercise

**Session:** 2
**Statement:** "<the exact exercise text presented to the reader --
either the session's own named exercise, or the corresponding module's
Exercise field pulled from knowledge-path-curriculum.md>"
**Scaffold:** ~/.airchon/exercises/gnostic-to-demiurge-session2-exercise/
-- "<one-line description of the starting files placed there>"
**Status:** pending / submitted / passed / failed (N attempts) /
passed-with-notes (offered only after 3 failed attempts, per CD5)
**Reader's submission:** "<raw text, once submitted>"

*(This block only exists while a scaffold-backed exercise, per CD4/CD5,
is the session's current practical assessment. A session routed to
CD6 instead has no Current Exercise block -- see Current Session Exam
below.)*

## Current Session Exam

**Session:** 3
**File:** ~/.airchon/session-3.exam.md -- the full 10-question
record (questions, raw answers, per-question outcome) lives there, not
duplicated here; this block is only a pointer plus the outcome CD4/CD6
need to decide what happens next.
**Status:** not started / in progress / passed / failed
**Score:** "<N / 10, once finished>"

*(This block only exists while CD6's session exam, not CD5's
scaffold-backed exercise, is the session's current practical
assessment -- see Current Exercise above for that case instead. Never
both blocks populated for the same session at once.)*

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
exercise boundaries.** Per-item covered/uncovered/pending-confirmation
state, the exact exercise statement once presented, and each
transition-exam question/answer/outcome must all be persisted as they
happen -- CD8 ("Resume After Interruption") depends on this file, not
on conversation recall, being the source of truth for where a reader
actually is.

**Items covered/uncovered/pending-confirmation are recorded by number
AND a short name, never a bare number.** ("1 -- What memory means in a
harness context", not just "1".) An item moves from uncovered to
covered in two gated stages, never in one automatic step (CD4 step 2):
first, its full documented scope must actually be taught through -- not
a first pass or a turn simply ending -- which alone still leaves it
uncovered, not covered; second, and only after CD4 pauses and asks, the
reader must explicitly reply that they're ready to continue (or choose
to pause) before the write to "covered" happens. Teaching-complete with
no reply yet is its own third state, **Items pending confirmation**,
used only when the conversation broke off between finishing the
explanation and the reader's reply (CD8 resumes those by re-asking the
gate, never by re-teaching). This list is therefore the authoritative
record of what has genuinely been taught AND acknowledged, not a
running commentary on what's been touched on or a teacher's own
unilateral judgment that a topic is "done." The name exists so a
resume (same day or days later, per CD8) can name the exact pickup
point at a glance instead of forcing a re-read of the whole session's
agenda in the course file.

**A `Paused:` line records a reader-chosen break, distinct from an
uncontrolled interruption AND distinct from an item sitting in Items
pending confirmation.** CD4 pauses after every item's teaching finishes
and asks the reader directly whether they're ready to continue or
would rather pause for another day; only once that reply lands does
CD4 write the item as covered -- and if the reply was "pause," log the
date and which item they're resuming at here in the same write. Its
absence doesn't mean anything went wrong -- most sessions likely
complete without ever needing it -- it only appears when the reader
explicitly chose not to continue in the same sitting, after having
already confirmed the just-finished item. It never appears together
with that same item still listed under Items pending confirmation --
an item is either confirmed-and-paused-after (a `Paused:` line, item
listed covered) or never got a reply at all (an Items pending
confirmation entry, no `Paused:` line yet), never both at once.

**Every session ends in exactly one practical assessment, never both.**
CD4 decides, per session, whether the exercise task maps to a real
harness artifact: if so, a scaffold is generated and the session's
entry gets an `Exercise:` line, graded via CD5. If not, the session
gets a `Session exam:` line instead, administered and graded via CD6.
Both are equally valid ways for a session to pass -- neither is a lesser
substitute for the other -- and a session's entry only ever carries the
one that actually applied.

**Scaffold paths and session-exam files are pointers, not duplicated
content.** The actual starter files a scaffold-backed exercise created
live under `~/.airchon/exercises/<course-slug>-session{N}-exercise/`;
this tracker only records that path plus a one-line description, never
copies of the files themselves. The actual 10 questions/answers/outcomes
of a session exam live in `~/.airchon/session-{N}.exam.md`; this
tracker only records a pointer to that file plus the final score and
status, the same relationship `qualify-exam.md` has to a cached tier
lookup -- full detail lives in its own file, a summary lives here.

**Only one "Current Exercise" or "Current Session Exam" block, and one
course's "Sessions" list, exist at a time.** Never both blocks
populated together -- a session is either mid-exercise (CD5) or
mid-session-exam (CD6), never both. When a course completes (the
transition exam passes), this file is either reinitialized for the
next course (a new tier/course header, a fresh Sessions list) or, if
the reader just reached Archon, left as a closed record with no next
course to start -- Course-Delivery Flow's CD1 returns the Ceiling note
in that case rather than reinitializing this file into a course that
doesn't exist.
