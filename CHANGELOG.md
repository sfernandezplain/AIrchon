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
