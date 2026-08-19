# Path Resolution for Project-Relative Paths (Shared by All Three Bare Agents)

Load-trigger: read this before resolving any `Read`/`Glob` of a path
under `references/harnesses/` or `resources/` -- from any of this
project's three standalone agents (`airchon-mentor`, `airchon-author`,
`airchon-teacher`). Added 2026-08-19, at the operator's request, once
`airchon-teacher`'s own genesis conciseness pass first raised the
question for its own file set and it became clear the same gap applies
to `airchon-mentor` and `airchon-author` too -- they name
`references/harnesses/*.md` project-relative paths exactly the same
way. Kept in one shared file, outside `resources/airchon-teacher/`
(which stays scoped to `airchon-teacher`'s own narrow tier domain, per
`CLAUDE.md`'s own rationale for why that directory exists), rather
than duplicated three times across the agent bodies that need it.

**The assumption this corrects.** Every project-relative path any of
these three agents names -- `references/harnesses/knowledge-path-curriculum.md`,
`resources/airchon-teacher/classification-flow.md`, and so on -- is
written as if the session's working directory is the AIrchon repo
itself. That is true whenever a human runs Claude Code or Copilot CLI
directly inside a clone of this repo -- the only way any of these three
agents has ever actually been run so far, and still the overwhelming
common case. It stops being true if this project is ever installed as
an `apm` dependency of another project: `apm install` vendors this
whole repo, unmodified, into that consuming project's
`apm_modules/<owner>/AIrchon/` (confirmed by inspecting how this
project's own `danielmeppiel/genesis` dependency actually lands in its
own `apm_modules/` -- a full clone, not just the declared primitives).
A session running there has the CONSUMING project's root as its
working directory, not the vendored copy's -- the content still
exists, just nested one level down, and the literal path no longer
resolves from cwd.

**The algorithm.** Resolve every such path this way, never assuming in
advance which case applies:

1. **Try the literal path first**, exactly as named (e.g. `Read
   references/harnesses/knowledge-path-curriculum.md`). If it
   resolves, you are running standalone inside this repo -- done; this
   is the expected outcome almost always.
2. **On a not-found result, fall back to a vendored-dependency
   search.** `Glob` for `apm_modules/*/*/<the same literal path>` (e.g.
   `apm_modules/*/*/references/harnesses/knowledge-path-curriculum.md`)
   and `Read` whichever single match comes back. There should be at
   most one -- this repo is a leaf dependency, not itself re-vendored
   recursively.
3. **If step 2 returns more than one match, or neither step resolves
   anything, stop and say so plainly to the user** rather than
   guessing, proceeding without the content, or reconstructing it from
   recalled text -- a missing or ambiguous resource file is a
   fact-that-must-be-true failure, not something to paper over.

**Does not apply to `~/.airchon/*` paths** (`airchon-teacher`'s own
state: `level`, `qualify-exam.md`, `course-progress.md`, the
`exercises/` scaffolds, `session-{N}.exam.md`). Those are already
user-home-absolute, independent of wherever any agent's own definition
happens to be deployed from -- only project-relative
`references/`/`resources/` paths ever need this fallback.

**Not yet exercised in practice.** No project currently depends on
AIrchon via `apm`, so this fallback is unverified against a real
vendored install for any of the three agents -- the same "plausible,
not tested" caveat `airchon-teacher.agent.md` already carries for its
own routed course-delivery pipeline. Revisit if/when this project is
actually published as a dependency for something else to
`apm install`.
