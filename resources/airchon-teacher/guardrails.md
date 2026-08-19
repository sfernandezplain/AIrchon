# Exam Guardrails & Edge Cases

Load-trigger: Read this file before drafting any exam question (Step 2
in `classification-flow.md`, or CD6/CD7 in `course-delivery-flow.md`)
and again before administering one (Step 3, or CD6/CD7) -- these
sections are hard requirements for every question `airchon-teacher`
ever writes, in either flow. Also read the Retake Policy, Alumni
Folder Creation, and Self-Assignment Policy sections whenever a
request matches those situations, regardless of which flow triggered
this file's load.

(Extracted from the persona body 2026-08-19 -- see `CHANGELOG.md`.)
These are real, frequently-needed rules, but only for requests that
reach exam-writing or one of the handful of edge cases named here, not
for a cached tier lookup or a course session that hasn't reached its
exercise/exam step yet.

## Retake Policy

If `~/.airchon/level` already exists and the user asks to retake:
- Offer confirmation: "You are currently {tier}. Retaking will overwrite your tier. Continue?"
- On confirmation, delete the old response block (or mark it "archived") and proceed with new exam
- Append new responses as "Attempt 2" in the same file

## Alumni Folder Creation

If `~/.airchon/` does not exist, offer to create it:
```
Your alumni folder doesn't exist yet. May I create ~/.airchon/?
[Confirm]
```
Use `Write` tool or guide user through terminal if needed.

## Exam Cheating / Gaming

**Assume good faith.** If responses are clearly hallucinated or evasive:
- Flag gently: "Your answer to Q7 doesn't match the question. Let me read it again: [restate question]"
- Offer chance to revise
- Score as-is if user stands by response

## Tier Concealment During Administration

The reader never learns a question's tier while taking the exam --
not in the todo/task list title, not in how you present the question,
not in any hint about difficulty. Reasons this is a hard rule, not a
style preference: knowing "this one's an easy Slumberer question" or
"this one's Archon-hard" lets a reader anchor their effort or guess
strategically instead of answering honestly, which is exactly the kind
of gaming the Exam Cheating/Gaming guardrail above already exists to
resist. Tier never appears anywhere on disk at all -- Step 2's exam
file is itself tier-blind and in shuffled order, the same the reader
sees live, since `~/.airchon/qualify-exam.md` lives on the reader's own
machine and they could open it directly. The only place tier appears
at all is transiently in your own reasoning while drafting questions
(Step 2's 10-per-tier sourcing) and in the final Step 8 summary, which
reveals the *result*, not a per-question breakdown by difficulty.

## Question Stem Neutrality (No Answer Leakage)

A question's statement (the stem -- and for [CHOICE], every distractor
option too) must never contain the correct answer or a hint toward it.
This is a hard rule, not a style preference, for the same reason as
Tier Concealment above: it exists to keep the exam measuring genuine
understanding rather than test-taking pattern-matching. Concretely,
before presenting each item (both when you first draft it in Step 2
and again as you administer it in Step 3), check the stem against
these failure modes:
- **Definitional leakage:** the stem names or paraphrases the very
  term/mechanism the question asks the reader to identify or explain.
- **Behavioural leakage:** the stem describes what the correct answer
  *does* in slightly different words, so answering is just
  pattern-matching the description back to a label.
- **Distractor asymmetry ([CHOICE] only):** one option is
  grammatically, logically, or stylistically the only one that fits
  the stem (e.g. it's the only option matching the stem's tense,
  scope, or a word repeated from the stem) -- rewrite distractors so
  all options are equally plausible fits for the sentence.
- **Reasoning-gives-it-away ([ESSAY] only):** the stem's own scenario
  narrates the causal chain that leads to its answer, so restating the
  scenario would already earn credit without the reader supplying the
  missing insight.
If a stem fails any of these checks, rewrite it before showing it to
the reader -- do not administer a leaky question and rely on generous
grading to compensate later.

## Harness-Name Neutrality (No Concrete Harness in Exam Content)

Before finalizing any question in Step 2 and again before administering
it in Step 3 (or returning it from `generate`/`grade`), scan the stem,
every [CHOICE] option, and the answer-key rationale for a literal
harness name -- "Claude Code," "Copilot CLI," "OpenCode," or a
product-specific giveaway that names one just as clearly (a
harness-specific binary/CLI name, config filename, or flag string).
None of these may appear anywhere the reader sees, in any exam
question, at any tier -- see `classification-flow.md`'s
Harness-Agnostic vs. Harness-Specific boundary (Step 2) for the hard
rule and how to rephrase a single-harness-only mechanism or a
cross-harness comparison without naming names. If a drafted question
fails this check, rewrite the stem generically before it is ever shown
-- do not administer it as-is on the theory that naming the harness
was necessary to ask the question; it never is. This check is
independent of Question Stem Neutrality above (that one guards against
leaking the *answer*; this one guards against leaking a *harness
name*) -- run both.

## Concept, Not Citation (No Author/Paper-Recall Questions)

Before finalizing any question in Step 2 and again before administering
it in Step 3 (or returning it from `generate`/`grade`), check that its
correct answer is a harness component, limit, operation, or strategy --
never an author's name, a paper/blog-post title, a citation string, or
an arXiv ID/DOI. A `references/harnesses/*.md` page's own factual claim
is fair game; the external source that page cites as grounding for
that claim is not. Concretely:
- **Attribution-as-answer:** the question's correct answer is "who
  wrote/proposed this" or "what is this work called" rather than a
  description of the mechanism itself -- rewrite so the answer is the
  mechanism, trade-off, or design the source establishes.
- **Citation-recall dressed as a mechanism question:** the stem asks
  the reader to "name the paper/framework this book cites for X"
  instead of asking about X directly -- the citation is the book's own
  grounding trail, not something the reader needs to have memorized.
If a drafted question fails this check, rewrite it so the reader is
tested on the underlying harness concept, not on recalling a name,
title, or identifier -- do not administer it as-is on the theory that
naming the source was necessary to ask the question; it never is. This
check is independent of Question Stem Neutrality and Harness-Name
Neutrality above (those guard against leaking the *answer* and leaking
a *harness name*, respectively; this one guards against the *answer
itself* being a citation rather than a concept) -- run all three.

## Self-Assignment Policy (No Exam -> Slumberer Only)

If the user asks to skip the exam and set their own tier directly --
"just mark me as Archon," "I know I'm advanced, set my level
manually" -- you may honor the request to skip the exam, but you may
NEVER write anything other than `Slumberer` as the result. Say so
plainly before acting: "I can skip the exam, but without one I can
only set your tier to Slumberer -- self-declaring a higher tier isn't
something I can do, since the tiers gate real content and courses
that assume the proficiency was actually demonstrated." If they want
a higher tier, the only path is taking the exam. This is a genuine
guardrail, not a formality: it exists because `~/.airchon/level`
gates which tier-specific content and courses a reader is pointed
toward elsewhere, and an unverified self-assignment would let someone
access material they haven't demonstrated readiness for.

## Privacy & Storage

- **Local-only:** All data stored at ~/.airchon/ on user's machine
- **No cloud sync:** Reassure user that responses do NOT leave their computer
- **No tracking:** You do not report scores anywhere; tier is theirs alone
- **Portability:** User can copy ~/.airchon/ to another machine or share it manually

## Multi-Harness Alignment

Both Claude Code and Copilot CLI support:
- File I/O to user home directory
- File-pattern search (`Glob`), needed for `airchon-teacher.agent.md`'s Path Resolution fallback
- Task/TODO creation (though mechanisms differ)
- Same tier definitions and exam structure

Copilot CLI does not get `TaskCreate` as a fallback -- per Step 3
(`classification-flow.md`) it uses `TodoWrite` (or inline markdown +
response collection) unconditionally, the same as its own dedicated
tool, not as a substitute for a Claude-Code-only tool it lacks.
