# Exam File Template

Load-trigger: Read this file when you reach Step 2 of
`classification-flow.md` (generating a fresh exam, whether direct
or via the routed `generate` mode) and need the exact file structure
to write to `~/.airchon/qualify-exam.md`. Not needed for a cached
tier lookup, a self-assignment, or a retake confirmation prompt --
those paths never touch this file.

```markdown
# Qualification Exam

**Instructions:** Answer all 40 questions. Each correct answer = 0.25 points. Final score determines your tier.

**Test-like questions** are marked [CHOICE] or [SHORT]; **free-response** are marked [ESSAY].

---

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

[... 37 more questions, in the shuffled presentation order, numbered straight through 4-40 with no section breaks or grouping of any kind ...]

---

## User Responses & Scores

*Append response block here after exam completion.*

### Attempt 1 | Date: [auto-filled]
- Q1: [response] -> correct (0.25)
- Q2: [response] -> correct (0.25)
- Q3: [response] -> partial (0.125)
- ...
- Q40: [response] -> incorrect (0.00)

**Raw Score:** 7.5 / 10.0
**Tier:** Demiurge
**Timestamp:** [auto-filled]
```

**Questions are numbered 1-40 by shuffled presentation position only --
never grouped or headed by tier.** Draft the 10 questions per tier as
Step 2's Sourcing Questions section describes, then shuffle across all
40 before writing this file: the question numbering here is the exact
same order and the exact same tier-blind labels ("Question N of 40"
plus format tag) that Step 3 (or the routed `generate` mode's returned
question list) presents to the reader in chat. There is no separate
"private" tier-grouped structure kept on disk -- `~/.airchon/qualify-exam.md`
lives on the reader's own machine and is something they could open and
read directly, so a `## Tier 1: Slumberer` section header here would
leak exactly the difficulty signal the live administration flow is
built to withhold. Tier exists only as an in-memory drafting constraint
while sourcing questions; it is never written down anywhere in this
file.
