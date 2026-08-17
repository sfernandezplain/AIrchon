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
