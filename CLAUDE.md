# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

An APM (Agent Package Manager) project. It packages four primitives
that work together:

- **`airchon-mentor`** (`.apm/agents/airchon-mentor.agent.md`) -- a
  standalone custom agent that answers/explains: a conversational
  mentor on how AI agent harnesses (Claude Code, GitHub Copilot CLI,
  OpenCode, and agent-harness engineering generally) actually work
  internally. READ-ONLY on the wiki-book (`references/harnesses/`)
  and the sources -- it holds no `Write`/`Edit` tool. When a question
  isn't covered by the book yet, it researches the sources live and
  answers IN SITU (in the conversation), but never persists that
  research to the book. Since 2026-08-17 it may ALSO read (never
  edit) the operator's own project's agent-harness configuration --
  skills, agent/persona files, hooks, permission/sandboxing config,
  orchestration/workflow definitions -- and advise on guardrails,
  control flow, or performance against the same wiki-book/sources
  corpus; it explicitly does not run the separate `genesis` skill's
  formal design/refactor process (diagrams, severity findings) itself
  -- see `CHANGELOG.md`'s 2026-08-17 entry. Deploys to both Claude
  Code and Copilot CLI as a flat `.agent.md` file.
- **`airchon-author`** (`.apm/agents/airchon-author.agent.md`) -- a
  standalone custom agent that populates the book: researches a topic
  for real and writes/updates the one `references/harnesses/*.md`
  page the request needs, keeping `index.md` current. It is the ONLY
  primitive in this project holding `Write`/`Edit` scoped to the
  wiki-book. Its reply to the user is a short confirmation of what it
  wrote, not a full mentoring-style explanation (that's
  `airchon-mentor`'s job). Deploys to both Claude Code and Copilot CLI
  the same way.
- **`airchon`** (`.apm/skills/airchon/SKILL.md`) -- a thin router
  skill with no mentoring, authoring, or assessment logic of its own.
  Its only job is to be DISCOVERY-invocable and `/airchon`-invocable,
  classify teaching/assessment intent vs. authoring intent vs. the
  conversational default (B2 CONDITIONAL DISPATCH), call exactly ONE
  agent TYPE -- `airchon-mentor` / `airchon-author` / `airchon-teacher`
  -- via the Agent tool, and return its answer. The one exception
  (since 2026-08-18): a "take/retake the exam" request against
  `airchon-teacher` is a multi-call pipeline against that single agent
  type (`generate` / `grade`-per-question / `finalize`), because an
  `Agent` call runs to completion and returns once and so cannot pace
  a 40-question exam turn by turn itself -- the router owns pacing and
  `TaskCreate`/`TodoWrite` rendering for that one flow instead, while
  originating none of the exam's content. See `SKILL.md`'s own Exam
  Administration section and `airchon-teacher.agent.md`'s
  Routed-Invocation Protocol for the full contract. Skills only have a deploy
  mechanism on Claude Code (`.claude/skills/<name>/`) -- Copilot CLI
  has no equivalent skill bundle path -- so this router only actually
  reaches Claude Code; the three agents themselves are what keep
  Copilot covered.
- **`airchon-teacher`** (`.apm/agents/airchon-teacher.agent.md`,
  renamed from `teacher` on 2026-08-17 -- see `CHANGELOG.md`) -- a
  standalone custom agent, unrelated to the mentor/author split above,
  that assesses reader proficiency: administers a 40-question exam
  grounded in `references/harnesses/knowledge-path-curriculum.md`,
  scores it, and classifies the reader into one of four tiers
  (Slumberer / Gnostic / Demiurge / Archon, defined in
  `references/harnesses/reader-proficiency-tiers.md`). Persists the
  tier to `~/.airchon/level` and the exam + responses to
  `~/.airchon/qualify-exam.md` -- both on the user's own machine,
  outside this repo, never under `references/harnesses/`. Since
  2026-08-18 it also *delivers* the course behind each tier transition
  (Course-Delivery Flow in its own persona file) -- session by session
  from `resources/airchon-teacher/*-sessions.md`, grading a practical
  exercise every session and a 10-question transition exam at the end,
  tracked in a new `~/.airchon/course-progress.md` (also
  user-machine-local, never under `references/harnesses/`). This reverses an
  earlier revision's explicit "You do NOT create courses"; see
  `CHANGELOG.md`'s 2026-08-18 entry. Still READ-ONLY on the wiki-book
  and on `resources/airchon-teacher/` itself, same structural boundary
  as `airchon-mentor` (no `Write`/`Edit` tool over either -- only over
  files under `~/.airchon/`). Ships as a bare agent, same as
  `airchon-mentor`/`airchon-author`; since 2026-08-17 it is also
  reachable via the `airchon` router's teaching/assessment branch on
  Claude Code (reusing the existing router rather than giving
  `airchon-teacher` a dedicated skill of its own -- see
  `CHANGELOG.md`'s 2026-08-17 entries). Deploys to both Claude Code
  and Copilot CLI the same way as the other two agents.

This split exists because a skill deploying to Copilot at all is not
possible, but a bare agent deploying to Copilot works fine -- so
mentor's, author's, and airchon-teacher's real logic all live on the
agent side, and the skill is purely a discovery/routing convenience
layered on top for Claude Code.

**Mentor vs. author (2026-07-30 split, at the operator's request):**
the original combined agent both answered questions AND wrote to the
wiki-book -- a DESCRIPTION CONJUNCTION / MULTI-LENS BODY smell (R1
SPLIT trigger in genesis terms) once the operator asked for the
read/write boundary to be real. `airchon-mentor` kept the name and
the default/most-invoked conversational role; `airchon-author` is the
new sibling that owns persistence. The single-writer interlock on
`references/harnesses/**` is enforced STRUCTURALLY (mentor's tool
list omits `Write`/`Edit`), not just by instruction in the persona
body -- see `CHANGELOG.md`'s 2026-07-30 "Split `airchon-mentor` into
read-only mentor + write-only author" entry for the full design
rationale (genesis handoff packet was scratch-only, not committed).

**Provenance:** what is now `airchon-mentor` + `airchon` and their
wiki-book were originally built inside the AgentXRay repo as
`xray-mentor`, the 11th agent in that project's `xray` skill family.
They were split out here on 2026-07-30 at the operator's request
because their scope was always broader than xray's own mission
(profiling a real agent execution) -- `xray-mentor` mentored on
harness internals in general, was DISCOVERY-invocable rather than
FORCED-only, and had an external human audience rather than xray's
internal JSON-receipt lens agents. See AgentXRay's own `CHANGELOG.md`
(2026-07-30 entry) for the removal side of this split. This repo
starts its own independent history from here -- do not assume
AgentXRay's `plan.md`/`CHANGELOG.md` conventions (genesis-driven
design log, evals harness, etc.) apply here unless explicitly adopted.

Same day, the shape went through two more revisions -- see
`CHANGELOG.md` for the full blow-by-blow, but in short: it was first
renamed `airchon-mentor` -> `airchon` and fully converted to a
`SKILL.md`-based skill (losing Copilot deployment as a result), then
split back into the current two-primitive shape (agent does the work
and deploys everywhere; skill is a thin discovery/routing wrapper
around it, keeping the `airchon` name) once it was clear the skill
was meant to be a router, not a replacement for the agent. Do not
assume any doc dated before that point still describes the current
shape.

## Source of truth: `.apm/agents/airchon-mentor.agent.md` + `.apm/agents/airchon-author.agent.md` + `.apm/agents/airchon-teacher.agent.md` + `.apm/skills/airchon/SKILL.md`

```
apm.yml                                    APM project manifest (name, targets, dependencies)
apm.lock.yaml                              Resolved/locked dependency versions (generated by `apm install`)
.apm/agents/airchon-mentor.agent.md        Canonical, authored source for the mentor agent -- read-only Q&A
.apm/agents/airchon-author.agent.md        Canonical, authored source for the author agent -- the only writer to the wiki-book
.apm/agents/airchon-teacher.agent.md       Canonical, authored source for the teacher agent -- read-only proficiency-exam administrator; since 2026-08-19 a lean ROUTER body only (routing logic + the one hot-path cached-lookup step) -- see resources/airchon-teacher/ below for where its actual procedures now live
.apm/skills/airchon/SKILL.md               Canonical, authored source for the thin router skill
references/harnesses/                      The wiki-book -- mentor reads it, author writes it -- project root, NOT under .apm/
<deploy-root>/agents/airchon-mentor.*      Deployed copy of the mentor agent -- gitignored, regenerated, NEVER hand-edited
<deploy-root>/agents/airchon-author.*      Deployed copy of the author agent -- gitignored, regenerated, NEVER hand-edited
<deploy-root>/agents/airchon-teacher.*     Deployed copy of the teacher agent -- gitignored, regenerated, NEVER hand-edited
<deploy-root>/skills/airchon/               Deployed copy of the router skill -- gitignored, regenerated, NEVER hand-edited
resources/airchon-teacher/                 airchon-teacher's own content, outside references/harnesses/ on purpose (see below); genuinely NOT deployed anywhere by `apm install` (moved outside `.apm/agents/` on 2026-08-18 specifically so it wouldn't be -- see `CHANGELOG.md`). Two kinds of content live here now, both project-relative and Read directly by the agent, neither deployed: (1) the original session-pacing/scaffolding files (the three `*-sessions.md` files, `course-progress-template.md`, `exam-file-template.md`, `scoring-reference.md`) that the Course-Delivery Flow consumes but does not author; (2) since 2026-08-19, `classification-flow.md`, `course-delivery-flow.md`, `guardrails.md`, and `routed-invocation-protocol.md` -- the actual Steps/CD procedures R3-EXTRACTed out of `airchon-teacher.agent.md`'s own body (see `CHANGELOG.md`'s 2026-08-19 entry). This second kind is canonical, hand-authored source, not reference material -- edit these files directly, the same discipline as the `.agent.md` file itself, never treat them as generated or optional.
~/.airchon/level                           airchon-teacher's own state -- one line, the reader's tier -- user's machine, outside this repo entirely
~/.airchon/qualify-exam.md                 airchon-teacher's own state -- exam + responses + score history -- user's machine, outside this repo entirely
~/.airchon/course-progress.md              airchon-teacher's own state (added 2026-08-18) -- current course, session-by-session progress, the in-flight exercise, and transition-exam Q&A/score -- user's machine, outside this repo entirely
~/.airchon/exercises/<course-slug>-session{N}-exercise/   airchon-teacher's own state (added 2026-08-19) -- a generated starter-file scaffold for one course-delivery session's practical exercise, in the reader's own harness's real conventions -- user's machine, outside this repo entirely
~/.airchon/session-{N}.exam.md             airchon-teacher's own state (added 2026-08-19) -- the 10-question session-exam fallback for a course-delivery session whose exercise has no scaffold-eligible artifact -- user's machine, outside this repo entirely
```

**Always edit `.apm/agents/airchon-mentor.agent.md`,
`.apm/agents/airchon-author.agent.md`,
`.apm/agents/airchon-teacher.agent.md`, `.apm/skills/airchon/SKILL.md`,
`references/harnesses/*.md`, and (since 2026-08-19)
`resources/airchon-teacher/classification-flow.md`,
`course-delivery-flow.md`, `guardrails.md`, and
`routed-invocation-protocol.md` directly.** The last four are as
canonical as `airchon-teacher.agent.md` itself -- only their physical
location changed, to keep the always-loaded router body small; treat
them with the same editing discipline. `.claude/`, `.agents/`,
and `.github/` are gitignored build output -- a plain file copy (not
a symlink; Windows/`core.symlinks=false` makes junctions unsafe).
Only `airchon-author` should ever hand-edit or be instructed to edit
`references/harnesses/*.md` -- `airchon-mentor` and `airchon-teacher`
are read-only there by design (no `Write`/`Edit` tool). After editing
any of the above, run:

```bash
apm install
```

`apm install` (not `apm compile` -- see AgentXRay's own CLAUDE.md for
the live-verified correction on this point, which applies equally
here) is the command that deploys both `.apm/agents/*.agent.md` and
`.apm/skills/*` to each active target's own path.

**Why the wiki-book is back at the project root, not inside the skill
bundle.** The agents (not the skill) own the wiki-book now --
`airchon-author` writes it, `airchon-mentor` reads it -- and both are
bare standalone agents always invoked with this repo as the working
directory -- so, same reasoning as the very first version of this
project, there is no deployed-copy path to resolve; the fixed path
`references/harnesses/` is correct on every invocation, on either
harness, for either agent. If the skill ever needs its own wiki-book
content independent of the agents, that would need to live under
`.apm/skills/airchon/references/` instead and get a deployed-copy
resolution step in the skill's own instructions -- not needed today
since the skill has no content of its own.

**Why `resources/airchon-teacher/` exists outside
`references/harnesses/`.** `references/harnesses/` is general-purpose,
cross-agent wiki-book content; `airchon-teacher` needed a place for
content scoped narrowly to its own tier domain instead (session
pacing/course scaffolding it doesn't itself author or consume -- see
`course-delivery-flow.md`'s own Hard Rules Recap, one of the four
resource files `.apm/agents/airchon-teacher.agent.md` now delegates to
-- see this file's own note below on that 2026-08-19 split) --
something this project only ever
anticipated hypothetically for the skill (previous paragraph) until
the operator actually asked for it for `airchon-teacher`, 2026-08-17
(see `CHANGELOG.md`). It is plain markdown, edited directly the same
way the wiki-book is, not a deployed artifact. This was originally
placed at `.apm/agents/airchon-teacher/resources/` on the assumption
that `apm install` only deploys `*.agent.md` files -- false: `apm`
recursively treats every loose `.md` file anywhere under `.apm/agents/`
as its own deployable agent candidate, with no companion-resource
convention the way skill bundles have `references/`/`assets/`. That
silently deployed this content as junk agents into `.claude/agents/`
and `.github/agents/` (two of the five even broke `apm`'s own YAML
parser outright, since a bare `---` markdown divider followed by a
`**bold**`-led line reads as a second, malformed frontmatter block to
its parser). Fixed 2026-08-18 by moving the whole folder outside
`.apm/` entirely, to `resources/airchon-teacher/` at the project root
-- see `CHANGELOG.md`'s 2026-08-18 entry for the full root-cause
writeup. `apm install` genuinely does not touch this path now.
`airchon-author` remains the wiki-book's only writer; this path is a
narrow, named exception to that scope (see its own BOUNDARY section)
for this one relocated file, not a general license to write anywhere
under `.apm/agents/`.

Verified live via this project's own `apm.lock.yaml` after running
`apm install`: all three agents (mentor, author, airchon-teacher)
deploy to `.claude/agents/` and `.github/agents/` (both targets,
6 files); the skill deploys to `.claude/skills/airchon/` and
`.agents/skills/airchon/` (no `.github/skills/...` entry -- Copilot
never gets a skill copy; `airchon-teacher` still has no skill of its
own, but is reachable via the `airchon` skill's routing on Claude
Code, same as the other two agents). Re-check `apm.lock.yaml` after
any future `apm install` rather than assuming this list is still
current.

## Two authoring gotchas (carried forward from AgentXRay, still apply)

Both were found live while authoring `xray-mentor` before the split
(AgentXRay `plan.md` v79) and silently break registration, with no
error surfaced anywhere:

- In the **agent's** frontmatter (`.apm/agents/airchon-mentor.agent.md`),
  never write `tools: A, B, C` (bare comma-separated words) -- use
  bracket syntax, `tools: [A, B, C]` (or `tools: []` for none). A bare
  list is not valid YAML and the whole agent silently fails to
  register.
- In **either** file's frontmatter, never put an unquoted colon-space
  (`": "`) inside the `description` value -- same silent-failure
  mode, and some toolchains will auto-strip the colon on a later
  write without telling you, which reads as "fixed" while the
  primitive is still unregistered.

The **skill's** frontmatter (`.apm/skills/airchon/SKILL.md`) uses
`allowed-tools:` as a YAML dash list, not the agent-only
`tools: [A, B, C]` bracket syntax -- see the discord `access`/
`configure` skills or `claude-security`'s `SKILL.md` in the official
plugin marketplace for the live-verified format. The router's
`allowed-tools` scopes the Agent tool to the three agents it's allowed
to call: `Agent(airchon-mentor)`, `Agent(airchon-author)`, and
`Agent(airchon-teacher)` -- the router picks exactly one per
invocation, never more than one.

After adding or editing either, always verify it actually appears in
the next "New agent types are now available" / "The following skills
are available" system reminder (or invoke it by name) before assuming
the deploy worked -- a clean `apm install` exit code is not proof of
registration.

## Cross-harness requirement

Whatever either agent asserts -- `airchon-mentor` answering in situ,
`airchon-author` writing to the wiki-book -- must be honest about
which harness(es) a claim actually applies to -- that discipline is
encoded directly (and duplicated verbatim, deliberately -- see
`CHANGELOG.md`) in each agent's own GROUNDING DISCIPLINE and SOURCE
AUTHORITY sections, not restated here. This project's `apm.yml`
declares `targets: claude, copilot` -- both agents genuinely reach
both; the router skill only reaches Claude Code (see above). OpenCode
is a harness the agents research and write about, not a deploy target
of this project either way.

## Running tests

There are none yet -- this project has no scripts, no `node:test`
suite, and no evals harness. `airchon-mentor`, `airchon-author`, and
`airchon-teacher` are all prose/research-driven, not
deterministic-probe-driven the way `xray` is; if that changes, add a
`dev/` maintainer area following AgentXRay's own precedent rather than
putting test/eval assets under `.apm/`.
