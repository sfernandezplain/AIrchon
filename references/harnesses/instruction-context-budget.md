# Instruction context budget -- splitting and scoping instruction files

How to stop a single instruction file (`CLAUDE.md`,
`.github/copilot-instructions.md`) from growing without bound, using the
mechanisms each harness actually ships: modular files, path-scoped
loading, on-demand skills, exclusion, and the surfaces that let you
*measure* what loaded.

Every claim below is tagged VERIFIED (fetched this session from the
named source) or BEST CURRENT UNDERSTANDING, UNCONFIRMED. Sources and
fetch dates at the bottom. Claude Code and Copilot CLI are separate
products from separate companies -- nothing confirmed for one is assumed
for the other.

**Companion page:** [memory-management.md](memory-management.md) covers
the same file hierarchies from the *persistence* angle (load order,
agent-authored memory, what survives compaction). This page is about
token cost. The one overlap worth restating up front: on Claude Code the
lazily-loaded tier is exactly the tier that does **not** come back after
compaction.

**The one-line answer.** Both harnesses have a genuine three-tier shape
-- (1) always loaded at session start, (2) loaded when a matching file is
touched, (3) loaded only when invoked -- and on both, `@`-style imports
belong to tier 1, so splitting a big file into imports buys you
*organization and nothing else*. The real levers are path-scoped
instruction files (`.claude/rules/` with `paths:` on Claude Code,
`.github/instructions/*.instructions.md` with `applyTo:` on Copilot CLI)
and skills.

---

## 1. Claude Code

Sources for this section: `code.claude.com/docs/en/memory` and
`code.claude.com/docs/en/skills`, both fetched 2026-07-30. VERIFIED
unless a claim is tagged otherwise.

### 1.1 The trap: imports do not save context

The docs say this twice, unambiguously. Under "Write effective
instructions": "You can also split content into imports for
organization, though imported files still load and enter the context
window at launch." And in troubleshooting, under "My CLAUDE.md is too
large": "Splitting into `@path` imports helps organization but doesn't
reduce context, since imported files load at launch."

Related facts that set the budget:

- **Stated size target: "target under 200 lines per CLAUDE.md file.
  Longer files consume more context and reduce adherence."** There is no
  hard limit -- "CLAUDE.md files are loaded in full regardless of
  length, though shorter files produce better adherence." (Contrast the
  auto-memory index `MEMORY.md`, which *is* hard-capped at 200 lines /
  25KB.)
- Every `CLAUDE.md` and `CLAUDE.local.md` in the directory hierarchy
  **above** cwd is "loaded in full at launch," concatenated rather than
  overriding. So in a monorepo your budget is the sum of every ancestor
  file, not just yours.
- Delivery mechanism: "CLAUDE.md content is delivered as a user message
  after the system prompt, not as part of the system prompt itself."

### 1.2 Tier 2a -- `.claude/rules/` with `paths:` frontmatter

This is the primary documented answer to your question. Put topic files
in `.claude/rules/`; all `.md` files are discovered **recursively**, so
`rules/frontend/`, `rules/backend/` etc. work.

- **Without** `paths:` frontmatter, a rule is "loaded at launch with the
  same priority as `.claude/CLAUDE.md`" -- i.e. it is still tier 1. You
  have gained modularity, not context.
- **With** `paths:` (a glob list), the rule "only load[s] into context
  when Claude works with matching files, reducing noise and saving
  context space," and specifically: "Path-scoped rules trigger when
  Claude reads files matching the pattern, **not on every tool use**."

Documented glob semantics and the sharp edges:

| Pattern | Matches |
|---|---|
| `**/*.ts` | All TypeScript files in any directory |
| `src/**/*` | All files under `src/` |
| `*.md` | Markdown files in the project root |
| `src/components/*.tsx` | React components in a specific directory |

- Brace expansion is supported (`"src/**/*.{ts,tsx}"`), but a rule's
  whole `paths` list shares **one budget of 1,000 expanded patterns and
  4 MiB**; patterns without braces don't count. A pattern that would
  exceed the budget is used *unexpanded*, and "its literal braces match
  no files" -- a silently dead rule. (Before v2.1.217 an over-large
  `paths` value "stalled or crashed the CLI at startup.")
- A `[` that can't be parsed as a bracket expression makes the pattern
  invalid: it "matches nothing, and the rule's other patterns keep
  working." Escape a literal one as `photos \[2024/**`. Before v2.1.207
  a single invalid pattern "made the Read tool fail for every file the
  rule was evaluated against."
- Symlinks are supported both ways: `.claude/rules/` entries may be
  symlinks (circular links "detected and handled gracefully"), which is
  the documented way to share one rule set across projects; and as of
  v2.1.198 `paths:` matching also works when Claude reaches a file
  through a symlinked path into the project.
- `~/.claude/rules/` is the user-level equivalent, "loaded before
  project rules, giving project rules higher priority."
- Project rules are skipped if you exclude `project` from
  `--setting-sources`; before v2.1.211, on-demand rules loaded anyway.

### 1.3 Tier 2b -- nested `CLAUDE.md` in subdirectories

"Claude also discovers `CLAUDE.md` and `CLAUDE.local.md` files in
subdirectories under your current working directory. Instead of loading
them at launch, they are included when Claude reads files in those
subdirectories." So a per-package `CLAUDE.md` in a monorepo is already
lazy by construction -- no frontmatter needed. The docs point at
`/docs/en/large-codebases` for the full monorepo layout (not fetched
this session).

### 1.4 Tier 3 -- skills, the cheapest place to put procedures

The skills page states the economics directly: "Unlike CLAUDE.md
content, a skill's body loads only when it's used, so long reference
material costs almost nothing until you need it." And the docs give you
the decision rule for *when* to reach for which tier, in `memory`'s
"When to add to CLAUDE.md": "Keep it to facts Claude should hold in
every session: build commands, conventions, project layout, 'always do
X' rules. If an entry is a multi-step procedure or only matters for one
part of the codebase, move it to a skill or a path-scoped rule
instead." A Note in the rules section draws the same line from the other
end: "Rules load into context every session or when matching files are
opened. For task-specific instructions that don't need to be in context
all the time, use skills instead."

The loading table, verbatim in substance:

| Frontmatter | You can invoke | Claude can invoke | When loaded into context |
|---|---|---|---|
| (default) | Yes | Yes | Description always in context, full skill loads when invoked |
| `disable-model-invocation: true` | Yes | No | **Description not in context**, full skill loads when you invoke |
| `user-invocable: false` | No | Yes | Description always in context, full skill loads when invoked |

Practical consequences for budgeting:

- The recurring always-on cost of a skill is its **description**, and
  "the combined `description` and `when_to_use` text is truncated at
  1,536 characters in the skill listing to reduce context usage." Many
  skills with long descriptions is itself a tier-1 cost.
- `disable-model-invocation: true` removes even that -- the one
  documented way to make a body of instructions cost *zero* until you
  type `/name`.
- Skills also accept a **`paths:` frontmatter field**: "Glob patterns
  that limit when this skill is activated... Claude loads the skill
  automatically only when working with files matching the patterns.
  Uses the same format as path-specific rules."
- Once loaded, a skill's content "stays in context across turns, so
  every line is a recurring token cost." Keep the body short and push
  detail into supporting files: "Large reference docs, API
  specifications, or example collections don't need to load into context
  every time the skill runs." Reference them from `SKILL.md` so Claude
  knows when to read them.
- Re-invoking a skill whose rendered content is unchanged adds "a short
  note that the skill is already loaded rather than a second copy"
  (v2.1.202+).
- Nested `.claude/skills/` below cwd "aren't loaded at startup. They
  load the first time Claude reads or edits a file inside that
  subdirectory" -- the same lazy pattern as nested `CLAUDE.md`.

### 1.5 Trimming levers on the tier-1 file itself

- **`claudeMdExcludes`** -- glob patterns matched against absolute
  paths, configurable at any settings layer (arrays merge across
  layers), for skipping other teams' ancestor files in a monorepo:
  e.g. `["**/monorepo/CLAUDE.md", "/home/user/monorepo/other-team/.claude/rules/**"]`.
  Managed-policy CLAUDE.md cannot be excluded.
- **Block-level HTML comments are free.** "Block-level HTML comments
  (`<!-- maintainer notes -->`) in CLAUDE.md files are stripped before
  the content is injected into Claude's context. Use them to leave notes
  for human maintainers without spending context tokens on them."
  Comments inside code blocks are preserved.
- **`/doctor` proposes trims** (requires v2.1.206+): "it cuts content
  Claude can derive from the codebase, such as directory layouts,
  dependency lists, and architecture overviews, and keeps pitfalls,
  rationale, and conventions that differ from tool defaults." That is a
  useful editorial heuristic even if you never run it: anything the
  agent could read off the filesystem does not need to be in tier 1.
- `--add-dir` directories contribute no memory files unless
  `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`; with it set, that
  directory's `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/*.md` and
  `CLAUDE.local.md` all load. Skills are the documented exception --
  `.claude/skills/` inside an added directory is loaded automatically.

### 1.6 Measuring what actually loaded

- **`/context`** -- the authoritative check: "To confirm the file
  loaded, run `/context` in a session and check the list under **Memory
  files**." Also: "To check which files actually loaded into the current
  session, run `/context`."
- **`InstructionsLoaded` hook** -- "log exactly which instruction files
  are loaded, when they load, and why. This is useful for debugging
  path-specific rules or lazy-loaded files in subdirectories." This is
  the deterministic, machine-readable probe.
- **`/memory`** lists CLAUDE.md / CLAUDE.local.md / auto-memory
  locations (including ones that don't exist yet) -- inventory, not
  proof of loading.

### 1.7 The cost of laziness

Per the compaction table in
[memory-management.md](memory-management.md) §1.7 (sourced from
`code.claude.com/docs/en/context-window`): project-root CLAUDE.md and
unscoped rules are **re-injected from disk** after compaction, while
rules with `paths:` frontmatter and nested subdirectory CLAUDE.md are
**lost until a matching file is read again**. Invoked skill bodies are
re-attached but capped at 5,000 tokens each and 25,000 total, most-recent
first. So every token you move out of tier 1 is also a token that may
silently stop applying mid-session. Budget accordingly: invariants that
must never lapse stay in tier 1 even if they cost tokens.

---

## 2. GitHub Copilot CLI

Sources for this section: `docs.github.com/en/copilot/concepts/response-customization`,
`docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions`,
`docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills`,
`docs.github.com/en/copilot/concepts/agents/about-agent-skills`, and
`github.com/github/copilot-cli` `changelog.md`, all fetched 2026-07-30.
VERIFIED unless tagged otherwise.

### 2.1 What files exist to split into

The CLI reads (per the CLI docs, cited in
[memory-management.md](memory-management.md) §2.1):
`.github/copilot-instructions.md` (repository-wide),
`.github/instructions/**/*.instructions.md` (path-specific), and
`AGENTS.md`. Its own changelog adds `CLAUDE.md` (read and
`@`-import-expanded, v1.0.66) and user-level
`~/.copilot/instructions/**/*.instructions.md` (v1.0.61 `/help` entry).
`COPILOT_CUSTOM_INSTRUCTIONS_DIRS` is a further, changelog-only
mechanism for pointing at instruction directories (v1.0.6 fix entry
naming it).

Discovery is hierarchical like Claude Code's: "Custom instructions, MCP
servers, skills, and agents are now discovered at every directory level
from the working directory up to the git root, enabling full monorepo
support" (v1.0.11). Files are **combined**: "Combine all custom
instruction files instead of using priority-based fallbacks" (v0.0.385)
-- so, as on Claude Code, ancestors add up rather than override.
(Precedence *ordering* for the CLI specifically remains UNCONFIRMED --
see [memory-management.md](memory-management.md) §2.1 for why the
`response-customization` precedence list can't be applied to the CLI.)

Two dedup behaviors reduce accidental double-billing: "Deduplicate
identical model instruction files to save context" (v0.0.394) and "Avoid
sending duplicate custom instruction files (e.g.
copilot-instructions.md and CLAUDE.md with identical content) to reduce
wasted tokens per turn" (v1.0.26). Also, "Custom agent instructions are
no longer duplicated each turn, reducing context window usage"
(v1.0.60).

`@`-style imports exist here too (v1.0.66). BEST CURRENT
UNDERSTANDING, UNCONFIRMED: as on Claude Code they are an organization
mechanism whose expansion still enters context -- the changelog says
"expand," which implies inlining, but no Copilot source I fetched states
the token consequence either way. Do not assume imports save context
here.

### 2.2 The scoping mechanism: `applyTo:` frontmatter

Per `add-repository-instructions`, authoritative for the file format:
path-specific instruction files "must be named `NAME.instructions.md`"
and live in `.github/instructions` or below it, and each needs a
frontmatter block with the `applyTo` keyword using glob syntax:

```markdown
---
applyTo: "app/models/**/*.rb"
---
```

Documented glob semantics: `*` matches files in the current directory;
`**` or `**/*` matches all files in all directories; `*.py` is
current-directory-only; `**/*.py` is recursive; `src/*.py` is direct
children of `src/` only; `src/**/*.py` is recursive within `src/`;
`**/subdir/**/*.py` matches any `subdir` at any depth. "You can specify
multiple patterns by separating them with commas." The purpose sentence
is the same as Claude Code's: "By using path-specific instructions you
can avoid overloading your repository-wide instructions with information
that only applies to files of certain types, or in certain directories."

**Grounding boundary worth knowing.** That same page says "Currently, on
GitHub.com, path-specific custom instructions are only supported for
Copilot cloud agent and Copilot code review." That sentence is scoped to
GitHub.com and does **not** describe the CLI. The CLI's own changelog is
what confirms CLI support, and it also tells you the CLI treats them as
a lazy tier:

- "Pattern-specific instruction files (`.github/instructions/*.instructions.md`)
  no longer include their full body in the system prompt on every
  session" (v1.0.35).
- "Instruction files with specific `applyTo` patterns are consolidated
  into a table instead of inlining full content, reducing context window
  usage" (v1.0.26).

That second entry is the mechanically interesting one: the always-on
cost of a scoped Copilot instruction file is a *table row*, not its
body -- structurally analogous to a Claude Code skill's description, and
it means the model is told the file exists and when it applies before
deciding to pull it in. BEST CURRENT UNDERSTANDING, UNCONFIRMED: what
exactly triggers the full body being loaded (a file read, a model
decision, an embedding match) is not documented on any page I fetched;
the changelog states the consolidation, not the retrieval trigger.

Frontmatter details from the changelog: `applyTo` "accepts both string
and array values" (v1.0.6), and unquoted glob patterns
(`applyTo: **/*.ts`) "are now applied correctly" as of v1.0.48 -- quote
your patterns if you may be on an older build. Instruction files inside
`.gitignore`d directories load correctly as of v1.0.36, and instruction
filenames are "recognized regardless of casing" (v0.0.x era entry).

### 2.3 Tier 3 -- skills

Copilot CLI has an on-demand tier too. Per the CLI's own add-skills
page: "When Copilot chooses to use a skill, the `SKILL.md` file will be
injected in the agent's context" -- i.e. injection at use time, not
session start. Locations, per the same page: project skills in
`.github/skills`, `.claude/skills`, or `.agents/skills`; personal skills
in `~/.copilot/skills` or `~/.agents/skills`. Invocation is by
`/skill-name` in a prompt. The concepts page describes skills as
"folders of instructions, scripts, and resources that Copilot can load
when relevant."

Note that `.claude/skills` in that list is a fact about **Copilot CLI's
own** discovery paths, from GitHub's docs -- not an inference from
Claude Code's docs. It happens to make skills the one tier a single
on-disk location can serve for both harnesses.

Neither Copilot page I fetched states the token cost of the
always-present part of a skill (whether a name/description listing is
injected each session, and how large). That is **UNKNOWN** -- do not
assume Claude Code's "description always in context" model applies.
Two adjacent changelog facts: "Skill content injected to the model no
longer includes YAML frontmatter metadata" (v1.0.48), and there is an
experimental retrieval path -- "Add experimental embedding-based dynamic
retrieval of MCP and skill instructions per turn" (v1.0.5), later
persisted as a `dynamicRetrieval` setting with a
`--dynamic-retrieval skills=<on|off>` flag (v1.0.66). That is a
genuinely different lever from anything documented for Claude Code:
per-turn embedding retrieval of instruction text rather than
glob-triggered loading.

### 2.4 Measuring and toggling

- **`/context`** -- "separates Custom Instructions from the system
  prompt and cross-references per-server MCP tool token costs with
  `/mcp`" (v1.0.60). So instruction cost is itemized separately from the
  system prompt here, which is exactly the number you want when
  trimming.
- **`/env`** -- "show loaded environment details (instructions, MCP
  servers, skills, agents, plugins)" (v1.0.25).
- **`/instructions`** -- "view and toggle custom instruction files"
  (v0.0.x), with "individual instruction file names in `/instructions`
  picker with `[external]` labels for injected files" (v1.0.4).
  Toggling is a real budget lever, not just an inspector.
- `/skills list`, `/skills info`, `/skills reload`, and a `/skills`
  toggle picker (add-skills page).

---

## 3. Synthesis

| Concern | Claude Code | Copilot CLI |
|---|---|---|
| Tier-1 file(s) | `CLAUDE.md` hierarchy (managed → user → project → local), plus `.claude/rules/*.md` **without** `paths:` | `.github/copilot-instructions.md`, `AGENTS.md`, `CLAUDE.md`, `~/.copilot/instructions/**` |
| Stated size guidance | "target under 200 lines per CLAUDE.md file"; loaded in full regardless of length | None found on the pages fetched |
| Do `@` imports save context? | **No** -- stated twice in the docs | UNCONFIRMED; imports exist (v1.0.66), token effect not documented |
| Path-scoped tier | `.claude/rules/` + `paths:` glob list; triggers on reading a matching file, "not on every tool use" | `.github/instructions/*.instructions.md` + `applyTo:`; body no longer in system prompt every session (v1.0.35), consolidated to a table row (v1.0.26) |
| Lazy-by-location tier | Nested `CLAUDE.md` and nested `.claude/skills/` below cwd load on first read/edit in that subdirectory | Discovery walks working dir → git root (v1.0.11); no documented "load on read of subdirectory file" behavior found |
| Invoke-only tier | Skills: body loads on use; description always in context (1,536-char cap) unless `disable-model-invocation: true`; supports its own `paths:` | Skills: `SKILL.md` "injected in the agent's context" when used; always-on listing cost UNKNOWN |
| Exclusion | `claudeMdExcludes` globs, any settings layer, arrays merge | `/instructions` toggle picker |
| Free maintainer notes | Block-level HTML comments stripped before injection | Not documented on pages fetched |
| Automated trim advice | `/doctor` trim proposal (v2.1.206+) | Not documented on pages fetched |
| Retrieval-based loading | Not documented | Experimental embedding-based per-turn retrieval of skill/MCP instructions; `dynamicRetrieval` setting |
| Verify what loaded | `/context` → **Memory files**; `InstructionsLoaded` hook | `/context` (Custom Instructions itemized separately), `/env`, `/instructions` |
| Survives compaction? | Tier 1 re-injected; path-scoped and nested lost until retriggered; skills capped 5K/25K | Skills survive; instruction-file re-injection **undocumented** |

**The design lesson.** Both harnesses independently converged on the
same three-tier answer, and both make the *same* thing tier 1 that
authors intuitively expect to be cheap: the imported/split-out file. The
distinction that matters is not "one file vs. many files," it is
**"does this text have a trigger?"** A file with no trigger (`@`
import, unscoped rule, plain `copilot-instructions.md`) costs you tokens
in every session no matter how many files you split it across. A file
with a trigger (`paths:`, `applyTo:`, a skill name) costs you only its
index entry until the trigger fires.

**A cross-harness recipe** (relevant to this project's requirement that
everything work on both targets):

1. **Tier 1, one small file.** Keep a root `CLAUDE.md` under ~200 lines
   holding only always-true facts. This is the only instruction file
   both harnesses verifiably read at runtime -- Copilot CLI reads
   `CLAUDE.md` (its changelog), Claude Code does not read `AGENTS.md` or
   `copilot-instructions.md` (its docs). That asymmetry is per-harness
   verified, not assumed.
2. **Tier 2 has no shared file.** You need two parallel sets:
   `.claude/rules/*.md` with `paths:` for Claude Code and
   `.github/instructions/*.instructions.md` with `applyTo:` for Copilot
   CLI. The glob dialects are similar but not identical (Claude Code
   documents brace expansion with an explicit 1,000-pattern budget;
   Copilot documents comma-separated patterns and a string-or-array
   `applyTo`). Do not generate one from the other without checking the
   pattern semantics.
3. **Tier 3 can be shared.** Skills are the one on-demand tier where a
   single directory serves both: Copilot CLI's own docs list
   `.claude/skills` among its project skill locations. Put procedures
   and long reference material here, keep `SKILL.md` bodies short, and
   push detail into supporting files the agent reads only when needed.
4. **Verify per harness, every time.** `/context` on both,
   `InstructionsLoaded` on Claude Code, `/env` and `/instructions` on
   Copilot CLI. The cost of a scoped rule is empirically checkable in
   under a minute; guessing is not necessary.
5. **Remember the compaction asymmetry.** On Claude Code, moving text
   out of tier 1 means it can stop applying after a compaction. On
   Copilot CLI, whether instruction files are re-injected post-compaction
   is undocumented. So invariants that must never lapse belong in tier 1
   on both, even at token cost.

---

## Sources

All fetched 2026-07-30.

**Claude Code (authoritative for Claude Code's documented behavior only):**
- `https://code.claude.com/docs/en/memory` -- 200-line size target, "loaded in full regardless of length," imports-don't-save-context (stated twice), when-to-use-CLAUDE.md vs. skill vs. path-scoped rule, `.claude/rules/` setup and recursion, `paths:` frontmatter and glob table, brace-expansion budget (1,000 patterns / 4 MiB), bracket-expression gotcha, rule symlinks, `~/.claude/rules/` ordering, `--setting-sources` interaction, nested-subdirectory lazy loading, `claudeMdExcludes`, HTML-comment stripping, `/doctor` trim proposal, `/context` **Memory files** check, `InstructionsLoaded` hook, `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD`, CLAUDE.md delivered as a user message after the system prompt.
- `https://code.claude.com/docs/en/skills` -- "a skill's body loads only when it's used," invocation/loading table for `disable-model-invocation` and `user-invocable`, 1,536-character `description`+`when_to_use` cap, skill `paths:` frontmatter, skill content stays in context across turns, supporting-files pattern, nested `.claude/skills/` lazy loading, `--add-dir` skills exception, identical-re-invocation dedup (v2.1.202), post-compaction 5,000/25,000-token skill budget.
- Compaction behavior cited via `references/harnesses/memory-management.md` §1.7, which sourced it from `https://code.claude.com/docs/en/context-window` on 2026-07-30.

**GitHub Copilot CLI (authoritative for Copilot CLI's documented behavior only):**
- `https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions` -- `NAME.instructions.md` naming and `.github/instructions` location, `applyTo` frontmatter and glob syntax table, comma-separated multiple patterns, the "avoid overloading your repository-wide instructions" rationale, and the GitHub.com-scoped support caveat.
- `https://docs.github.com/en/copilot/concepts/response-customization` -- path-specific vs. repository-wide framing, precedence list (explicitly enumerating GitHub.com/IDE surfaces, **not** the CLI), `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` as agent-instruction filenames, nearest-`AGENTS.md`-takes-precedence.
- `https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills` -- skill directory locations for the CLI (`.github/skills`, `.claude/skills`, `.agents/skills`, `~/.copilot/skills`, `~/.agents/skills`), `/skill-name` invocation, "When Copilot chooses to use a skill, the `SKILL.md` file will be injected in the agent's context," `/skills list|info|reload`.
- `https://docs.github.com/en/copilot/concepts/agents/about-agent-skills` -- skills definition, supported surfaces including the GitHub Copilot CLI.
- `https://github.com/github/copilot-cli` `changelog.md` (via `gh api repos/github/copilot-cli/contents/changelog.md`) -- v1.0.35 pattern-specific bodies out of the system prompt, v1.0.26 consolidation into a table + duplicate-instruction-file avoidance, v1.0.6 `applyTo` string-or-array, v1.0.48 unquoted-glob fix and skill-frontmatter stripping, v1.0.36 gitignored-directory loading, v1.0.11 monorepo discovery to git root, v0.0.385 combine-all-instruction-files, v0.0.394 identical-file dedup, v1.0.60 `/context` Custom Instructions separation and non-duplicated agent instructions, v1.0.25 `/env`, v1.0.4 `/instructions` picker labels, v1.0.61 `~/.copilot/instructions/**`, v1.0.66 `@`-import expansion and `dynamicRetrieval`, v1.0.5 experimental embedding-based retrieval, v1.0.6-era `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`. Authoritative for its own behavior-change history; this repo ships no implementation source.
