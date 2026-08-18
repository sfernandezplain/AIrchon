## 2026-08-18 -- `/genesis` review of `airchon-teacher.agent.md` + `airchon/SKILL.md`: five findings, all fixed

At the operator's request ("check the teacher agent and the skill for
coherence, conciseness an compliant of PROSE contrainsts"), ran the
genesis review discipline (classic-principles table, PROSE axes, the
eight durable LLM truths, refactor-pattern triggers R1-R5, and the
MODULE ENTRYPOINT canonical spec) against both files as they stood
after the routed-invocation redesign above, rather than reviewing from
memory -- measured actual line/char/token counts and grepped for
non-ASCII rather than eyeballing. Operator chose to fix everything
immediately rather than leave it as a report.

**HIGH -- missing resume/reload discipline in the routed exam
pipeline.** The routed protocol persists state to disk specifically so
the stateless `grade`/`finalize` calls can recover it, but neither file
said what happens if the ~42-call loop is interrupted mid-exam
(compaction, restart) -- a real gap in the design from the entry
above, not a pre-existing issue. Fixed: both files gained a "resume
after interruption" paragraph -- the skill re-derives position from
its own tasklist's done/pending items; `airchon-teacher` re-derives
state from `qualify-exam.md`'s response block; neither side restarts
or re-grades on resume. Added as a hard rule in Constraints & Scope
too.

**MEDIUM -- `airchon-teacher.agent.md` was 645 lines / ~8.7k tokens,
loaded wholesale on every invocation** including the trivial cached
"what's my tier" lookup (R1 SPLIT's FRAGMENT CALLERS trigger). Fixed
via R3 EXTRACT: the Step 2 exam-file markdown template and the Step
4/5 Python pseudocode moved to two new files --
`.apm/agents/airchon-teacher/resources/exam-file-template.md` and
`resources/scoring-reference.md` -- each with an explicit load-trigger
condition in the body, borrowing the SKILL.md `references/` convention
for a persona file. Net effect: 645 -> 569 lines despite also adding
the resume/cache-discipline prose below.

**MEDIUM -- the routed pipeline's ~42 fresh subagent calls each reload
the full persona body (truth #2) with no cache-prefix discipline
stated (B13).** Fixed: both files now instruct that the per-call
variable payload (`order` + the reader's raw answer) goes at the END
of each `grade` call's prompt, keeping the instructional prefix
byte-identical across the pipeline so the calls can share a cache hit.

**MEDIUM -- `airchon` `SKILL.md`'s `description` was 995/1024
characters (97% of the hard cap),** spanning four fairly distinct
trigger domains. Not a violation yet, but this project already got
burned once by a silent frontmatter failure (see the two authoring
gotchas in `CLAUDE.md`), and the next capability added to this router
would have hit the ceiling with no warning. Fixed: tightened to 694
characters, same four domains still named, imperative phrasing and
indirect triggers preserved.

**LOW -- non-ASCII characters throughout `airchon-teacher.agent.md`**
(em/en-dashes, arrows, checkmarks, one emoji) against genesis's own
step-8 "ASCII only" validate item. Fixed: all replaced with ASCII
equivalents (`--`, `->`, "correct"/"incorrect", emoji removed).
`SKILL.md` was already clean.

**Confirmed compliant, not just findings:** the dual direct-invocation
/ routed-invocation shape in `airchon-teacher.agent.md` reads at first
glance like a MULTI-LENS BODY smell, but maps cleanly onto genesis's
own MODULE ENTRYPOINT BINDING MODES concept -- one primitive, two
binding contexts. Not a SoC violation; left as-is.

Redeployed via `apm install`.

## 2026-08-18 -- Exam administration re-architected around a subagent one-shot-return constraint: the router now paces the exam, `airchon-teacher` grades per question via JSON

At the operator's request ("instead of using taskcreate/tasklist for
task management, return in json all the questions to the skill in
order that the skill uses the tool to render the tasklist to the
user"). Before implementing, asked the operator to resolve a real
architectural fork this implied (see the AskUserQuestion in this
session) and they chose: the `airchon` skill administers the live
exam loop; `airchon-teacher` grades and teaches per question via JSON,
never itself calling `TaskCreate`/`TodoWrite` when reached this way.

**The underlying problem.** `airchon-teacher`'s Steps 1-8 (unchanged,
still the direct-invocation path) assume its own conversation turn IS
the live session with the reader -- it can call `TaskCreate` for
question 1, wait several turns for an answer, then move to question 2,
because it's driving the whole conversation. But when the `airchon`
router dispatches to it via the `Agent` tool (the only path
DISCOVERY/`/airchon` invocation actually takes on Claude Code), that
call is a subagent invocation that runs to completion and returns
exactly once -- it cannot pause mid-exam to show one question, wait an
arbitrary number of reader turns, then resume. The original design
(teacher self-administers via its own `TaskCreate`/`TodoWrite` calls,
one question at a time, all inside one Agent() call) silently cannot
work through the router at all; it only ever worked for direct
invocation.

**Fix: dual invocation paths, single set of rules.**
`.apm/agents/airchon-teacher.agent.md` gained a new
"Routed-Invocation Protocol" section, used only when reached via the
skill: three JSON modes -- `generate` (build+shuffle+write the exam,
return the tier-blind ordered question list), `grade` (given one
question's `order` + the reader's raw answer, grade it, teach the
concept, append the response line to `qualify-exam.md` so state
survives across otherwise-stateless calls, return the explanation),
and `finalize` (tally the score, assign the tier, persist
`~/.airchon/level`, return the Step 8 summary). Every substantive rule
-- Tier Concealment, the new Question Stem Neutrality guardrail
(above), the Harness-Agnostic boundary, the Step 4 rubric, the Step 5
tier table, Self-Assignment, Retake -- applies identically in both
paths; only the transport changes. Steps 1-8 and the tool list
(`Read, Write, TaskCreate, TodoWrite`) are otherwise untouched, since
direct invocation still needs them.

`.apm/skills/airchon/SKILL.md` gained matching pieces: `TaskCreate`
and `TodoWrite` added to its `allowed-tools`, and a new "Exam
Administration" section carving out the one explicit exception to its
"never call more than one agent for one request" rule -- restated more
precisely as "never call more than one agent TYPE," since the exam
flow is now a bounded pipeline of one `generate` + up to 40 `grade` +
one `finalize` call, all against `airchon-teacher` alone, with the
skill never originating exam content itself (only pacing + rendering
the tasklist). `CLAUDE.md`'s `airchon` bullet updated to describe this
exception at a summary level, pointing to both files for the full
contract rather than duplicating it there.

Redeployed via `apm install`.

## 2026-08-18 -- New guardrail: exam question stems must never contain the answer or a hint toward it

At the operator's request. `airchon-teacher.agent.md` already had rules
governing *which* concepts a question can test (Harness-Agnostic
boundary) and *how much context* a reader is owed (the mentoring-voice
"write every question so it teaches" rule in Step 2), but nothing yet
said a question's own stem must not give away its answer -- a gap
distinct from both existing rules, since a stem can be perfectly
harness-agnostic and well-explained while still leaking the answer
through its own wording.

Added three things, all in `.apm/agents/airchon-teacher.agent.md`:

1. A paragraph directly under Step 2's "write every question so it
   teaches, not just tests" rule, warning that the same
   scenario-setting prose that makes a question self-contained must
   not smuggle in the concept being tested.
2. A new named guardrail, **Question Stem Neutrality (No Answer
   Leakage)**, alongside the existing Tier Concealment guardrail --
   four concrete failure modes to check every stem against
   (definitional leakage, behavioural leakage, distractor asymmetry
   for [CHOICE], reasoning-gives-it-away for [ESSAY]), to be run both
   when a question is drafted (Step 2) and again before it's
   administered (Step 3).
3. A matching bullet in Constraints & Scope, so this reads as a hard
   rule on the same footing as tier concealment and the
   harness-agnostic boundary, not just a Step 2 aside.

Redeployed via `apm install`.

## 2026-08-17 -- Second session-pacing file (Gnostic->Demiurge) written; vendor-name leak caught and the harness-agnostic rule tightened

Two things at the operator's request, in sequence.

**`gnostic-to-demiurge-sessions.md` written**, directly to
`.apm/agents/airchon-teacher/resources/` this time (no wiki-book
detour, unlike the Transition-1 file above) -- delegated to
`airchon-author` since designing session count/sizing from a
21-module, 5-cluster band is genuine pedagogical-content authorship,
the same category of work it already does for
`knowledge-path-curriculum.md`, regardless of final file location.
27 sessions: one per module (agenda items from that module's own key
concepts), one synthesis session per cluster (walking that cluster's
comprehension checks plus a representative exercise), and a final
capstone session -- organized around the same five thematic clusters
`knowledge-path-curriculum.md` already uses for this band. Matching
pointer paragraphs added to `knowledge-path-curriculum.md` (under
Transition 2) and `index.md`.

**Vendor-name leak found and fixed.** The operator spotted "Anthropic"
in the output. Both new session files named a specific model vendor in
one agenda item apiece: the Slumberer->Gnostic file's Session 1 item 6
("Anthropic's own narrower usage" vs. "the Hugging Face agents
course's / Lilian Weng's broader ones") and the Gnostic->Demiurge
file's Session 12 items 1-2 ("Anthropic's Messages API" vs. "OpenAI's
Responses API"). Both reworded to describe the underlying
concept/mechanism generically with no company or individual named --
e.g. "one wire protocol's tool-call representation" /  "a second wire
protocol's tool-call representation" in place of naming which vendor
owns which. This happened because the existing Harness-Agnostic
boundary rule in `airchon-teacher.agent.md` only said "never pin the
correct answer to one *harness's* syntax" -- it never said the same
about the model *vendor* underneath the harness, which is a level
these session-breakdown files (and, by the same logic, any future exam
question) can just as easily leak into.

**Rule tightened, not just the two instances fixed.** Added one
sentence to `airchon-teacher.agent.md`'s Harness-Agnostic boundary:
"generic" goes one level deeper than "harness" -- never name the
underlying model vendor either (Anthropic, OpenAI, etc.), only the
three harness names (Claude Code, Copilot CLI, OpenCode) are a
sanctioned exception, since this book's whole cross-harness-comparison
structure depends on naming them. Placed here rather than only in the
two session files, since this is the canonical policy document the
rule already lived in and the one a future author drafting the
Demiurge->Archon session breakdown (or any new exam question) would
need to see it in. Redeployed via `apm install`.

## 2026-08-17 -- New per-agent resource location: `.apm/agents/airchon-teacher/resources/`

At the operator's request ("i want that temary under
airchon-teacher/resources"), relocated the Slumberer->Gnostic
session-breakdown content (written earlier today, see the entry
below) out of the shared wiki-book into a new location scoped to
`airchon-teacher`'s own domain. Treated as a primitive/structure
change I did directly, the same way the rename and router-wiring
entries above were -- not delegated to `airchon-author`, since
relocating already-authored content and adjusting primitive
boundaries is maintainer-level work, not the research-and-write
wiki-book authorship `airchon-author` is chartered for.

- **New file:** `.apm/agents/airchon-teacher/resources/slumberer-to-gnostic-sessions.md`
  -- the session-breakdown content, moved (not duplicated) from
  `knowledge-path-curriculum.md`, now a standalone page with its own
  "what this file is" / "why this lives here, not in the wiki-book"
  framing rather than being a subsection of Transition 1.
- **`knowledge-path-curriculum.md` updated:** the moved subsection
  replaced with a short pointer to the new location and why it moved
  (scoped to one agent's domain and explicitly downstream/course-
  delivery work that agent doesn't do itself, vs. general wiki-book
  research content any reader/agent might need).
- **`index.md` updated:** the Curriculum row's mention of the
  session-pacing layer now points at the new path instead of
  describing content living inline on the curriculum page.
- **`airchon-teacher.agent.md` updated:** Constraints & Scope now
  names the new path for discoverability, explicit that this agent
  neither authors nor reads it as part of its own exam-administration
  flow -- it's there for whatever downstream course-delivery work
  eventually consumes it, consistent with the existing "You do NOT
  create courses" line.
- **`airchon-author.agent.md`'s BOUNDARY updated:** one narrow, named
  exception added -- `.apm/agents/airchon-teacher/resources/` is
  maintainer-level primitive content outside `references/harnesses/`;
  if asked to update it, edit it in place, don't recreate it inside
  the wiki-book. `airchon-author` remains the wiki-book's only writer;
  this is not a general license to write anywhere under `.apm/agents/`.
- **`CLAUDE.md` updated:** file tree gained the new path (explicitly
  noting `apm install` never deploys it -- it isn't an
  `*.agent.md`/`SKILL.md` entrypoint); a new rationale paragraph
  mirrors the existing "why the wiki-book is at the project root"
  one, explaining why this narrow exception exists and that it
  generalizes a possibility this project had previously only
  anticipated hypothetically for the skill, not yet exercised for any
  primitive until now.
- Redeployed via `apm install` (`airchon-teacher`/`airchon-author`
  content changed; the new resources file itself needed no deploy
  step, confirmed by `apm install`'s own output not touching it).

## 2026-08-17 -- `airchon-teacher` redesigned: mentoring voice, one-question-at-a-time, shuffled + tier-hidden, Slumberer-only self-assignment

Ran the `genesis` skill at the operator's request to modify five things
about `.apm/agents/airchon-teacher.agent.md` at once. Treated as a
lightweight redesign (intent + SoC pass + compliance check) rather than
a from-scratch design, since this is a body-only edit to an existing
single-thread persona with no new primitive, tool grant, or dependency.

- **Harness-agnostic grounding made concrete.** "Sourcing Questions"
  now names the actual mechanism categories to draw from (caching,
  tool-calling/tool-schema, determinism, memory/context loading,
  context compression, permissions, retries, orchestration/fan-out,
  hooks), tied to whichever `references/harnesses/*.md` page documents
  each. Also swapped out the Gnostic example question, which asked for
  a specific Claude Code version number -- harness-specific trivia that
  visibly contradicted the rule it sat next to -- for a conceptual
  message-stream-vs-persisted-checklist question any harness with a
  todo/task mechanism can be asked about.
- **Questions must teach, not just test.** New instruction: every
  question is self-contained and carefully set up, because the answer
  explanation (see next point) leans on it.
- **Voice reframed as mentoring, not silent grading.** The persona now
  explains the underlying concept after every answer, right or wrong --
  bounded explicitly against overlap with `airchon-mentor` (stays tied
  to the question just asked; open-ended tangents get redirected to
  the mentor instead of teacher improvising a second Q&A role).
- **Administration restructured: one question at a time via a 40-item
  todo/task list**, never a single 40-question message. Step 3
  rewritten around `TaskCreate`/`TodoWrite` as the per-question
  checklist, citing the same B4 PLAN MEMENTO / B8 ATTENTION ANCHOR
  rationale `genesis` itself uses for its own step-by-step plans.
- **Shuffled presentation, tier concealed.** Questions are randomized
  before administration (scoring is per-question and order-independent,
  so this changes nothing about grading) and no tier label ever
  reaches the todo list, the chat, or any hint about difficulty --
  new "Tier Concealment During Administration" guardrail, justified as
  closing an anchoring/gaming vector the existing Exam Cheating/Gaming
  guardrail already targets. The persisted exam file's tier headers
  stay as private scoring bookkeeping only.
- **New Self-Assignment Policy: skipping the exam caps at Slumberer.**
  A reader may ask to self-declare a tier without taking the exam;
  Teacher may honor skipping the exam but never writes anything above
  `Slumberer` regardless of what tier they named. Justified as a real
  guardrail, not a formality -- `~/.airchon/level` gates tier-specific
  content/courses elsewhere, so an unverified self-assignment would be
  unearned access. Wired through Step 1 (offers the choice), Step 6
  (forces the write), Step 7 (logs it honestly), the mermaid diagram
  (new `OfferMode`/`SelfAssign` states), Constraints & Scope, and
  Invocation Triggers.
- Diagram, Step 1-8 prose, and guardrails all updated together so they
  stay in sync, per this file's own stated convention.
- Redeployed via `apm install`.

## 2026-08-17 -- Renamed `teacher` -> `airchon-teacher`

At the operator's request. Mechanical rename, no behavior change:

- `git mv .apm/agents/teacher.agent.md .apm/agents/airchon-teacher.agent.md`;
  frontmatter `name: teacher` -> `name: airchon-teacher`; the H1
  heading, opening self-reference, and closing line updated from
  "Teacher Persona" to "Airchon Teacher Persona" (interior shorthand
  mentions of "Teacher" left as natural-language shorthand, same as
  how this file's own prose refers to `airchon-mentor` as "the mentor"
  in places).
- Every cross-file reference to the identifier updated to match:
  `.apm/skills/airchon/SKILL.md`'s `allowed-tools` entry and its three
  in-body mentions (`Agent(teacher)` -> `Agent(airchon-teacher)`, and
  the router's dispatch/prose text); `CLAUDE.md`'s primitive bullet,
  file-tree block, "Always edit" list, `apm.lock.yaml`-verified deploy
  paragraph, and the "Two authoring gotchas" section's `allowed-tools`
  example.
- **Not touched:** every entry above this one in this file, which
  correctly describes what was true *as of that entry's own date*
  under the old name -- same precedent as the 2026-07-30
  `airchon-mentor` -> `airchon` rename, whose own prior entries still
  say `airchon-mentor` rather than being rewritten. `references/
  harnesses/*.md` never referenced `teacher` by name (verified via a
  full-repo grep before starting), so the wiki-book needed no edits.
  `README.md` also does not mention `teacher` -- a pre-existing gap
  (it already predates `airchon-author` and `teacher` both) left as
  is, since renaming a name that isn't there is a no-op.
- Redeployed via `apm install`, which reported "Cleaned 2 stale files"
  and removed the old deployed copies
  (`.claude/agents/teacher.md`, `.github/agents/teacher.agent.md`)
  itself -- verified the new `airchon-teacher.*` copies replaced them
  in both `.claude/agents/` and `.github/agents/`, and that
  `airchon-teacher` appears in the deployed `airchon` skill on both
  targets.

## 2026-08-17 -- `airchon` router grows a third branch: teaching/assessment intent -> `teacher`

At the operator's request ("every message whose topic is classes,
courses, formation, current level, continue lesson, correct me
exercise should be redirected to teacher agent"), wired `teacher` into
the existing `.apm/skills/airchon/SKILL.md` router instead of building
it a dedicated skill -- reversing, on reflection, the "deliberately
deferred" call made in an earlier entry above (that entry assumed a
*new*, `teacher`-only skill was the only way to give it Claude-Code
discovery coverage; reusing the already-installed router is simpler
and was not considered at the time).

- **`allowed-tools` grew a third entry**, `Agent(teacher)`, alongside
  the existing `Agent(airchon-mentor)`/`Agent(airchon-author)`.
- **Classification is now 3-way, TEACHING/ASSESSMENT checked
  first**: classes, courses, formation/training, current proficiency
  level/tier, "assess my proficiency", "take/retake the exam",
  continuing a lesson, or getting an exercise corrected -> `teacher`.
  Checked first (not folded into the existing AUTHORING-vs-default
  branch) because its trigger nouns don't overlap either existing
  branch, so it doesn't add real ambiguity to the AUTHORING-vs-default
  call that still defaults to `airchon-mentor`.
- **Frontmatter `description` extended** (855 -> 995 chars, still
  under the 1024-char MODULE ENTRYPOINT cap) to name the new trigger
  nouns for the dispatcher itself.
- **`CLAUDE.md` updated in four places** that had asserted `teacher`
  has no router/skill partner on either harness: the `airchon` and
  `teacher` primitive bullets, the `apm.lock.yaml`-verified deploy
  paragraph, and the "Two authoring gotchas" section's `allowed-tools`
  description (two agents -> three).
- Redeployed via `apm install`; verified `Agent(teacher)` present in
  both deployed copies (`.claude/skills/airchon/SKILL.md`,
  `.agents/skills/airchon/SKILL.md`) and the new description string
  live in the next session's skill-discovery listing.

## 2026-08-17 -- `teacher` reviewed via `genesis` for consistency, conciseness, navigability, coherence

Ran the `genesis` skill's architect lens (SoC pass + compliance check,
scoped to a review of an existing module rather than a new design) over
`.apm/agents/teacher.agent.md` at the operator's request. Findings and
fixes, most severe first:

- **HIGH, coherence -- illustrative exam content pulled from the wrong
  corpus.** All four per-tier essay-question examples in the Step 2
  template, and the Step 7 log's example, tested `genesis`'s own design
  vocabulary (truth #8 "plan before execution", R1 SPLIT/R2 FUSE/R3
  EXTRACT/R4 INLINE, PANEL vs. PIPELINE, FAN-OUT + SYNTHESIZER) instead
  of `references/harnesses/` -- the exact corpus this file's own
  grounding rules (frontmatter, "Before You Start", the
  Harness-Agnostic boundary) say every question must come from. Likely
  origin: `teacher.agent.md` was itself drafted by running `genesis`'s
  own Step 7b (per the original Step 7b commit message), and that
  vocabulary bled into the placeholder examples. Since agents
  pattern-match against concrete examples more than prose rules, a live
  exam would likely have imitated these and drifted off-corpus. Fixed:
  all five examples replaced with ones grounded in real, this-book
  content (the ReAct loop's observation-append step, the documented
  `TodoWrite`->`Task*` v2.1.142 migration, Claude Code's vs. Copilot
  CLI's compaction mechanisms, the advanced-planning gap-analysis
  finding).
- **HIGH, coherence/functionality -- ungranted tools.** Frontmatter
  listed `Task`, `readPage`, `openBrowserPage` -- none of which exist
  anywhere in this book's own `built-in-tools.md` inventory of Claude
  Code, Copilot CLI, or OpenCode (Claude Code's real names are
  `TaskCreate`/`TaskGet`/`TaskList`/`TaskUpdate`/`TaskOutput`/
  `TaskStop`/`TodoWrite`; no bare `Task`) -- while Step 3 instructs
  using `TaskCreate` and `TodoWrite`, neither of which frontmatter
  actually granted. Fixed: `tools: [Read, Write, TaskCreate, TodoWrite]`.
- **MEDIUM, consistency -- contradictory fallback framing.**
  "Multi-Harness Alignment" read as if `TodoWrite` were a fallback for
  when Copilot CLI "lacks `TaskCreate`," contradicting Step 3's
  unconditional one-tool-per-harness split. Fixed: reworded to match
  Step 3 exactly.
- **MEDIUM, prose navigability -- rule after the artifact it
  governs.** "Sourcing Questions" and the Harness-Agnostic boundary
  (added last turn) sat textually after the full Step 2 exam template,
  so a reader met the artifact before the rule shaping it. Fixed:
  moved both under "Step 2," ahead of the template.
- **MEDIUM, coherence -- stale drafting scaffolding shipped in the
  persona body.** An "Integration Notes" section addressed to whoever
  was drafting the file ("after this agent is drafted, deploy it...",
  "pending Step 7a portability review") had no equivalent in
  `airchon-mentor`/`airchon-author`, loaded dead context on every
  invocation, and referenced a decision (the router-skill question)
  already resolved as deferred two entries above. Deleted.
- **LOW, noted but not changed:** the Harness-Agnostic boundary is
  deliberately restated three times across the file (Sourcing
  Questions, Step 8, Constraints & Scope) -- a durability-over-
  conciseness tradeoff already reasoned about when it was added, kept
  as is. Added one clarifying parenthetical where "You do NOT create
  courses" sat in mild tension with Step 8 naming a single next
  exercise.

## 2026-08-17 -- `teacher` grounds Q&A in the source pages; harness-agnostic/specific boundary added

At the operator's request, tightened two things in
`.apm/agents/teacher.agent.md` beyond the review/cleanup above:

- **Grounding widened past the two curriculum meta-pages.** "Before
  You Start" and "Sourcing Questions" now instruct Teacher to follow
  `knowledge-path-curriculum.md`'s own module links out to the actual
  `references/harnesses/*.md` topic pages (`agent-loop.md`,
  `mcp-integration.md`, etc.) and write questions/answer keys from
  what those pages say -- not from the curriculum's one-line "key
  concepts" summary alone. The curriculum page itself already
  disclaims re-verifying anything it cites (its own "What this page
  is, and what it is not" section: factual claims are "inherited from
  that source page's own grounding, not re-verified here"), so Teacher
  citing only the curriculum was one inherited-claim hop further from
  the source than the rest of this book tolerates.
- **New BOUNDARY: exam Q&A and course/reading recommendations are
  HARNESS-AGNOSTIC; exercises are HARNESS-SPECIFIC.** Formalizes a
  distinction `knowledge-path-curriculum.md` already draws implicitly
  (its Slumberer->Gnostic capstone explicitly bars naming a concrete
  harness; its Gnostic->Demiurge band's defining exercise shape is a
  named cross-harness trace) into an explicit rule for Teacher: a
  question's "correct" answer must never collapse onto one harness's
  specific syntax when the source page documents several side by
  side, but a hands-on exercise must name a real harness (asking the
  reader which one they use, if unknown) -- a cross-harness comparison
  exercise still satisfies "harness-specific" since it names concrete
  harnesses, just more than one. Restated in three places (Sourcing
  Questions, Step 8's example output, Constraints & Scope) since this
  is exactly the kind of rule that's easy to violate one tier or one
  example at a time without a durable restatement.
- Alumni Evaluator flow diagram (added in the entry above) and its
  Step 1-8 prose were left factually unchanged by this edit; only the
  grounding and harness-agnostic/specific instructions moved.

## 2026-08-17 -- `teacher` reviewed; genesis handoff packet closed out and deleted

Reviewed `.apm/agents/teacher.agent.md` (drafted earlier today, Step
7b commit) against its own genesis handoff packet
(`TEACHER-HANDOFF.md`, Steps 1-6) at the operator's request, closed
out the documentation gap the Step 7b commit left behind, then
deleted the handoff -- genesis handoff packets are scratch-only in
this project, never committed (same convention already stated for the
mentor/author split's own handoffs, and already exercised once before
for `HANDOFF-missing-topics.md` in the wiki-book's gap-analysis work).
This one reached the repo by mistake, bundled into the Step 7b commit
alongside the agent it was drafted for.

- **All five Step 6 "blocking" open questions verified resolved** in
  the shipped agent -- none needed a code change, only confirmation:
  - Score-boundary overlap at 7.0 / gap at 5-6 -- resolved with
    contiguous, non-overlapping ranges (`0.0-5.99` Slumberer,
    `6.0-7.0` Gnostic, `7.1-8.0` Demiurge, `8.1-10.0` Archon; safe
    because every achievable score is a multiple of 0.25).
  - Free-response scoring strategy -- resolved as an LLM-guided
    rubric (full / half / no credit) with an explicit "err on the
    side of credit" instruction, not pattern-matching or deferred
    human review.
  - Exam-generation approach -- resolved as dynamic per-session
    generation (the handoff's own recommended MVP choice), grounded
    in `knowledge-path-curriculum.md` rather than a pre-authored bank.
  - FORCED-trigger timing -- resolved as a one-time cold-start check
    (`.airchon/` exists, `level` missing), not a periodic re-check.
  - `.airchon/level` file format -- resolved as a single-line tier
    string, no metadata.
- **Documentation close-out (the handoff's own Todo 10, skipped by
  the Step 7b commit):** `CLAUDE.md` now documents `teacher` as this
  project's fourth primitive (source-of-truth file tree, editing
  instructions, `apm.lock.yaml` file-count, and "Running tests"
  section all updated) -- it shipped with no `CLAUDE.md` update
  originally. This entry is the corresponding `CHANGELOG.md` record.
- **Deliberately left undone, not an oversight:** the handoff's Todo
  8 (a Claude-Code-only router skill for `teacher`, mirroring
  `airchon`'s relationship to `airchon-mentor`/`airchon-author`) and
  Todo 9 (a validation/test suite) are net-new feature work outside
  what this review pass was asked to do, and this project still has
  no test harness at all regardless (see `CLAUDE.md`'s "Running
  tests"). `teacher` ships today exactly as the handoff's own Target
  Declaration described it -- "a bare agent, no skill partner on
  Copilot" -- just without a Claude Code-only skill partner either.
- **Current flow materialized as a mermaid diagram, in
  `teacher.agent.md` itself** (its "Core Workflow: User-Classifying
  Flow (Alumni Evaluator)" section), superseding the three draft
  diagrams (component, sequence, state machine) that lived in the
  now-deleted handoff and still showed the score-boundary defect as
  unresolved. Kept alongside the operative instructions rather than
  here, so it stays in sync with the agent it documents; this is the
  first of this project's agent flows documented as a diagram --
  `airchon-mentor`'s and `airchon-author`'s own flows remain
  prose-only for now.

## 2026-08-17 -- `airchon-mentor` gains read-only project-harness review

Ran through the `genesis` design skill (handoff packet in the
session's scratchpad, not committed here) at the operator's request:
"airchon mentor can read project files to respond the user how to do
better and more proper agent harness / railguarding / flow /
performance." This reverses, for `airchon-mentor` only, the
2026-07-30 split's "never audits a user's own skill/persona files"
restriction.

- **R1 SPLIT checked and rejected.** The new capability reuses the
  same grounding corpus (the wiki-book + external harness docs), same
  output shape (conversational prose, no artifacts), same audience
  (a human, directly), and the same read-only tool surface as the
  existing mentor role -- only the TARGET changes (the user's own
  project, in addition to the general case), not a second lens or a
  second side effect. No sibling agent warranted.
- **`.apm/agents/airchon-mentor.agent.md` updated.** Frontmatter
  `description` now also triggers on a request to review or improve
  the user's own project's agent-harness setup (trimmed to 1,013
  chars to stay under the 1024-char cap after the addition). Body
  gained a new PROJECT-HARNESS REVIEW PROCEDURE section (read the
  named files first via Glob/Read/Grep -- a claim about the project
  is VERIFIED only once actually read this session, never inferred;
  map the concern to the relevant wiki-book pages; answer as an
  explicit comparison, tagged throughout). BOUNDARY reworded: still
  no `Write`/`Edit` anywhere, still never touches
  `references/harnesses/**`, and now explicitly never runs `genesis`'s
  own formal design/refactor process (mandatory diagrams,
  severity-rubric findings, a persisted handoff packet) -- flagged as
  a MEDIUM SoC finding (conceptual overlap with `genesis`) during
  design, mitigated by naming `genesis` as the escape hatch for
  redesign-grade requests rather than improvising a lighter version
  of it. Reviewing the user's general application code outside
  agent-harness configuration remains explicitly out of scope.
- **`.apm/agents/airchon-author.agent.md` BOUNDARY line updated**,
  wording only -- it previously claimed "same boundary as
  `airchon-mentor`" on auditing project files, which is now stale;
  reworded to note the asymmetry explicitly. No capability change to
  `airchon-author` itself; it still never reads a project's own
  harness config for advisory purposes, and remains the sole writer
  to the wiki-book.
- **`.apm/skills/airchon/SKILL.md` description updated** to name the
  new trigger for discovery-dispatch accuracy; router classification
  LOGIC unchanged -- a project-review request already fell under the
  existing conversational default branch to `airchon-mentor`.
- **No tool-surface change.** `airchon-mentor` already held
  `Read`/`Glob`/`Grep`; the change is a persona-scoping (prompt)
  boundary shift, not a new tool grant.
- **No evals harness added** for this edit (this project still has
  none, per the "Running tests" section) -- a lightweight evals plan
  (2-3 content evals showing a before/after delta, ~4 trigger evals)
  was recorded in the session's scratchpad handoff packet as design
  rationale only, not shipped as a file.

## 2026-07-30 -- Split `airchon-mentor` into read-only mentor + write-only author

Ran through the `genesis` design skill (handoff packet in the
session's scratchpad, not committed here -- this project has no
`plan.md` convention yet) to split the single combined agent into
two, at the operator's request: "mentor that will answer or explain
any question the user has and author that will populate the book,
mentor can access the book and the sources but cannot modify the
book, if something is not in the book it has to check on the sources
and made a response in situ."

- **R1 SPLIT confirmed structurally**, not just requested: the old
  combined description mixed two verbs ("mentors conversationally"
  AND "writing/updating a shared wiki-book") with two different
  write-permission profiles -- a DESCRIPTION CONJUNCTION / MULTI-LENS
  BODY trigger, not a premature split.
- **`.apm/agents/airchon-mentor.agent.md` narrowed to read-only.**
  Dropped `Write` and `Edit` from `tools:` -- structurally, not just
  by instruction, so the "never modifies the book" constraint holds
  even if the persona body were ignored. Its WIKI-BOOK PROCEDURE now
  reads the book first, and when a topic isn't covered, researches
  the sources live and answers IN SITU (in the conversation) instead
  of persisting anything -- the live research is real, it just never
  reaches `references/harnesses/`.
- **New `.apm/agents/airchon-author.agent.md`.** Carries the
  research-and-write half of the old WIKI-BOOK PROCEDURE verbatim in
  spirit: researches a topic for real, writes/updates exactly the one
  page the request needs, keeps `index.md` current. It is now the
  ONLY agent in this project holding Write/Edit scoped to the
  wiki-book. Its reply to the user is a short confirmation of what it
  wrote and the sources it used -- not a full mentoring-style
  explanation, to avoid overlapping `airchon-mentor`'s job.
- **`.apm/skills/airchon/SKILL.md` router upgraded to a real B2
  CONDITIONAL DISPATCH.** It used to always call `airchon-mentor`;
  it now classifies authoring intent ("write this up", "add this to
  the wiki-book", "update the page on X", ...) vs. the conversational
  default, and calls exactly one of the two agents -- never both.
  `allowed-tools` grew to `Agent(airchon-mentor), Agent(airchon-
  author)`. Defaults to `airchon-mentor` on ambiguity.
- **GROUNDING DISCIPLINE + SOURCE AUTHORITY duplicated verbatim**
  across both new agent files rather than extracted to a shared
  asset (R3 EXTRACT trigger considered and rejected): both personas
  genuinely need the full epistemic contract present in their own
  loaded text with no extra Read-tool round trip on every turn: the
  two files will change together on the rare occasion sourcing rules
  change, which is a small, bounded cost against paying a mandatory
  extra tool call on every single invocation forever.
- **Frontmatter descriptions trimmed post-draft** (mentor 1188 ->
  1003 chars, author -> 906 chars) to stay clear of the 1024-char
  MODULE ENTRYPOINT cap even though that cap is formally an
  agentskills.io SKILL.md rule and these are agent files, not
  SKILL.md containers -- kept as a discipline anyway since these
  descriptions are still dispatcher-preloaded text.
- No `apm.yml`/manifest edit needed: `includes: auto` already
  auto-discovers new files under `.apm/agents/`; verified via
  `apm install` that the new agent deployed to both `.claude/agents/`
  and `.github/agents/` alongside the existing one (4 files = 2
  agents x 2 targets).
- **Known pre-existing IDE lint noise, not a new regression:** the
  editor flags `tools:`/`model:` values on the Copilot-target deploy
  as "unknown" -- this is the same generic tool/model vocabulary the
  combined agent already used before this split; not something this
  change introduced.

## 2026-07-30 -- Split back into agent (`airchon-mentor`) + thin router skill (`airchon`)

- **Restored `.apm/agents/airchon-mentor.agent.md`** at the operator's
  request ("the skill is just a router to several personas, I want
  the agent mentor to exist again") -- the full ROLE/GROUNDING
  DISCIPLINE/SOURCE AUTHORITY/WIKI-BOOK PROCEDURE/BOUNDARY content
  from before the skill conversion, agent-style frontmatter (`model:`,
  `tools: [...]`, `user-invocable:`, `disable-model-invocation:`).
  This agent does the actual mentoring again and deploys to both
  Claude Code and Copilot CLI, restoring the cross-harness coverage
  lost in the previous entry.
- **`references/harnesses/` moved back to the project root** out of
  `.apm/skills/airchon/references/` -- the agent owns the wiki-book
  now, is standalone, and always runs with this repo as its working
  directory, so the fixed root-level path is correct again (same
  reasoning as the original pre-skill design).
- **`.apm/skills/airchon/SKILL.md` shrunk to a thin router**: no
  mentoring content of its own, `allowed-tools: [Agent(airchon-mentor)]`
  only, instructions to call the `airchon-mentor` agent in the
  foreground on every invocation and return its answer verbatim. Kept
  the `airchon` name and its DISCOVERY/`/airchon` invocability so
  Claude Code users get the same entry point as before; it exists
  purely so the mentor is reachable that way on Claude Code, since
  Copilot coverage now comes from the agent directly.
- Framed as a router because the operator described it as one that
  may grow to select between several mentor personas later (different
  tone/audience agents) -- no additional personas were added in this
  pass; the routing/selection step is explicitly not pre-built ahead
  of there being more than one agent to route between.

## 2026-07-30 -- Converted `airchon-mentor` to a skill, renamed to `airchon`

- **Converted from a bare standalone agent to a `SKILL.md`-based
  skill**, at the operator's request, so the wiki-book could deploy
  as part of a bundle instead of relying on `references/harnesses/`
  always being read at the project root. Concretely:
  - `.apm/agents/airchon-mentor.agent.md` removed; replaced by
    `.apm/skills/airchon/SKILL.md` (after the rename below).
  - `references/harnesses/` moved to
    `.apm/skills/airchon/references/harnesses/`.
  - Frontmatter changed from agent-style (`model:`, `tools: [...]`,
    `user-invocable:`, `disable-model-invocation:`) to skill-style
    (`user-invocable:`, `disable-model-invocation:`,
    `allowed-tools:` as a YAML dash list). Skills have no `model:`
    field -- pinning a model tier for this mentor is no longer
    possible; it now inherits whatever model is running the
    conversation.
  - WIKI-BOOK PROCEDURE updated to resolve the deployed-copy path
    (`.claude/skills/<name>/` or `.agents/skills/<name>/`), the same
    approach AgentXRay's `xray-mentor` used before the split.
  - **Verified via `apm.lock.yaml` after running `apm install`:**
    Copilot CLI never receives a deployed copy of this skill --
    `apm.yml`'s `targets: claude, copilot` still lists it, but skills
    have no deploy mechanism on Copilot (only flat `.agent.md` files
    do). This project now effectively only deploys to Claude Code,
    a real behavior change from the original bare-agent setup, which
    deployed to both. This is a known, accepted tradeoff, not an
    oversight.
- **Renamed `airchon-mentor` -> `airchon`** throughout (frontmatter
  `name`, all file/directory paths, self-references in the
  wiki-book's `index.md`, `CLAUDE.md`, `README.md`).

## 2026-07-30 -- Initial creation: `airchon-mentor`, split out of AgentXRay's `xray-mentor`

- **New APM project.** `AIrchon` packages one standalone custom agent,
  `airchon-mentor` (`.apm/agents/airchon-mentor.agent.md`), deployed to
  Claude Code and Copilot CLI (`apm.yml` targets: `claude`, `copilot`).
- **Origin.** `airchon-mentor` is a rename+relocation of AgentXRay's
  `xray-mentor` (that project's 11th agent, `plan.md` v79-v84), moved
  out at the operator's request because its scope -- mentoring on AI
  agent harness internals generally -- was always broader than xray's
  own mission (profiling a real agent execution). Nothing about the
  agent's behavior changed in the move except:
  - Renamed `xray-mentor` -> `airchon-mentor` throughout (frontmatter
    `name`, self-references in the wiki-book's `index.md`).
  - Simplified the WIKI-BOOK PROCEDURE: AgentXRay's version had to
    resolve which of three possible deployed-skill-copy paths
    (`.claude/skills/xray/`, `.agents/skills/xray/`,
    `.github/skills/xray/`) existed at runtime, because the wiki-book
    rode inside a packaged skill. `airchon-mentor` has no packaged
    skill to ride inside of -- it's a bare standalone agent always run
    with this repo as the working directory -- so the wiki-book now
    lives at a fixed path, `references/harnesses/`, with no
    per-harness resolution needed at all.
  - Generalized the BOUNDARY section: removed the reference to xray's
    own 8-lens fan-out / Step 4 synthesis pipeline, since neither
    exists in this repo.
- **Wiki-book carried over verbatim** (6 files: `index.md`,
  `mcp-integration.md`, `memory-management.md`,
  `instruction-context-budget.md`, `agent-loop.md`,
  `agent-loop-implementations.md`), except for the two self-reference
  edits above and one cross-repo pointer fix in `mcp-integration.md`
  (its "related page" note pointed at a file inside the same skill,
  which is no longer true now that the two projects are separate --
  updated to name AgentXRay explicitly as the sibling repo that file
  lives in).
- **No evals/test harness ported.** AgentXRay's `dev/skills/
  xray-maintainer/evals/evals.json` had 5 structural evals
  (`se-96`..`se-100`) asserting `xray-mentor`'s frontmatter shape and
  wiki-book file existence; those were removed from AgentXRay rather
  than copied here, since this project doesn't (yet) have the
  genesis-driven evals convention AgentXRay uses. Revisit if this
  project grows enough surface area to need regression coverage.
