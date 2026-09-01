# Instruction context budget -- splitting and scoping instruction files

How to stop a single instruction file (`CLAUDE.md`,
`.github/copilot-instructions.md`) from growing without bound, using the
mechanisms each harness actually ships: modular files, path-scoped
loading, on-demand skills, exclusion, and the surfaces that let you
*measure* what loaded.

Every claim below is tagged VERIFIED (fetched this session from the
named source) or BEST CURRENT UNDERSTANDING, UNCONFIRMED. Sources and
fetch dates at the bottom. Claude Code, Copilot CLI, OpenCode, and pi
are separate products from separate organizations -- nothing confirmed
for one is assumed for another. Section 3 (OpenCode) was added
2026-08-24, closing a real gap: this page originally covered only two
of the book's three target harnesses. Section 4 (pi) was added
2026-09-01, extending the same tiered analysis to the fourth harness
this book documents.

**Companion page:** [memory-management.md](memory-management.md) covers
the same file hierarchies from the *persistence* angle (load order,
agent-authored memory, what survives compaction). This page is about
token cost. The one overlap worth restating up front: on Claude Code the
lazily-loaded tier is exactly the tier that does **not** come back after
compaction; OpenCode's own re-read behavior (§3.1) is a genuinely
different shape from either closed-source harness's, source-verified
this session.

**The one-line answer.** All three harnesses have a genuine multi-tier
shape -- (1) always loaded at session start, (2) loaded when a matching
file is touched, (3) loaded only when invoked -- though OpenCode's own
tier 1 is architecturally different from the other two in one important
way (§3.1): it is re-read from disk on every turn, not frozen at session
start. On Claude Code and Copilot CLI, `@`-style imports belong to tier
1, so splitting a big file into imports buys you *organization and
nothing else*; OpenCode has no import-expansion mechanism of its own to
make the same mistake with (§3.2). The real levers on Claude Code and
Copilot CLI are path-scoped instruction files (`.claude/rules/` with
`paths:` on Claude Code, `.github/instructions/*.instructions.md` with
`applyTo:` on Copilot CLI) and skills; OpenCode has no documented
path-scoped instruction tier at all (§3.2), leaving skills as its only
lazy-loading lever.

```mermaid
flowchart TD
    subgraph Tier1["Tier 1 -- always loaded (session start, or every turn on OpenCode)"]
        CC1["Claude Code: CLAUDE.md hierarchy +<br/>unscoped .claude/rules/*.md"]
        GH1["Copilot CLI: copilot-instructions.md,<br/>AGENTS.md, CLAUDE.md"]
        OC1["OpenCode: AGENTS.md hierarchy +<br/>config instructions[] (local + remote)<br/>re-read from disk every turn"]
    end
    subgraph Tier2["Tier 2 -- loaded when a matching file is touched"]
        CC2["Claude Code: .claude/rules/*.md<br/>with paths: glob"]
        GH2["Copilot CLI: .github/instructions/*.instructions.md<br/>with applyTo: glob"]
        OC2["OpenCode: no path-scoped tier found;<br/>nearby-file auto-attach on Read only (§3.3)"]
    end
    subgraph Tier3["Tier 3 -- loaded only when invoked"]
        CC3["Claude Code skills: body loads on use"]
        GH3["Copilot CLI skills: SKILL.md injected on use"]
        OC3["OpenCode skills: skill tool call loads body;<br/>name+description always listed"]
    end
    Tier1 --> Tier2 --> Tier3
```

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

## 3. OpenCode

Sources for this section: `opencode.ai/docs/rules/` (the rendered docs
page) cross-checked against its own Markdown source,
`packages/web/src/content/docs/rules.mdx`, and its skills-tier
counterpart `packages/web/src/content/docs/skills.mdx`, both fetched via
`gh api` from `github.com/anomalyco/opencode`, `dev` branch, 2026-08-24;
deepened with the actual loader source,
`packages/opencode/src/session/instruction.ts` and the calling site in
`packages/opencode/src/session/prompt.ts`, same repo/branch/date. VERIFIED
unless tagged otherwise, with the standing `dev`-branch caveat this book
applies everywhere it cites OpenCode source directly.

### 3.1 The trap does not apply the same way: tier 1 is re-read every turn, not frozen at session start

OpenCode's own instruction-loading module, `Instruction.system()`,
is called once per iteration of the main session loop in
`prompt.ts` -- a `while (true)` turn loop (`let step = 0` before it,
incrementing per iteration) that also drives tool dispatch and the
per-turn system-prompt assembly `[env, instructions, mcpInstructions,
skills]`. `Instruction.system()` itself does a fresh
`fs.readFileString()` of every discovered instruction-file path on each
call, with no caching layer visible in the source read this session.
**This is a materially different architecture from both other harnesses
documented above:** Claude Code's tier 1 is a session-start read with no
documented hot-reload (§1.8, cross-referenced, not repeated), and
Copilot CLI's reload behavior is explicitly undocumented (§2.4). On
OpenCode, editing `AGENTS.md` mid-session takes effect on the *very next
turn* -- a real, source-verified, positive answer to a question the
other two harnesses' own docs leave open. This is a genuinely new
finding for this book, not previously documented in
[memory-management.md](memory-management.md) either.

### 3.2 What tier 1 actually contains, and the absence of a path-scoped tier

Per `rules.mdx` (VERIFIED): OpenCode's tier-1 instruction surface is an
`AGENTS.md` file, initialized via the `/init` slash command (which scans
the repo and writes build/lint/test commands, architecture notes, and
project conventions) or authored by hand. It is discovered from
**multiple locations that serve different purposes**, not merged
arbitrarily:

- **Project**: `AGENTS.md` in the project root, applying only to that
  directory and its subdirectories.
- **Global**: `~/.config/opencode/AGENTS.md`, applied across every
  OpenCode session on the machine, explicitly recommended for personal
  (not team-shared) rules since it is not committed to Git.
- **Claude Code compatibility, as a fallback only**: project-level
  `CLAUDE.md` (used only if no `AGENTS.md` exists) and global
  `~/.claude/CLAUDE.md` (used only if no `~/.config/opencode/AGENTS.md`
  exists), disableable via `OPENCODE_DISABLE_CLAUDE_CODE`,
  `OPENCODE_DISABLE_CLAUDE_CODE_PROMPT`, or
  `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS`.

VERIFIED, docs-stated precedence: "the first matching file wins in each
category" -- if both `AGENTS.md` and `CLAUDE.md` exist at the same
level, only `AGENTS.md` loads; the global `~/.config/opencode/AGENTS.md`
takes precedence over the Claude-compat global fallback. Source-verified
addition not stated on the docs page fetched: the loader
(`instruction.ts`) also recognizes a third, explicitly **deprecated**
filename, `CONTEXT.md`, in the same precedence slot as `AGENTS.md`/
`CLAUDE.md` -- a docs/source gap worth flagging rather than silently
reconciling.

A **separate, additive** mechanism -- not a replacement for the file
hierarchy above -- is the `instructions` array in `opencode.json`
(project) or the global config file, letting a team point at existing
rule files instead of duplicating them into `AGENTS.md`: local paths
(supporting glob patterns, e.g. `"packages/*/AGENTS.md"`) and remote
`https://`/`http://` URLs, source-verified as fetched with a hard
**5-second timeout** (`Effect.timeout(5000)`) and silently degrading to
empty content on failure rather than blocking the turn. VERIFIED (docs):
"All instruction files are combined with your `AGENTS.md` files" -- i.e.
this is an additive tier-1 mechanism, not a per-path-scoped one.

**No path-scoped (tier-2) instruction tier was found.** Neither
`rules.mdx` nor a `search/code` sweep of the docs tree for `applyTo`- or
`paths:`-style scoping syntax this session turned up anything resembling
Claude Code's `.claude/rules/` + `paths:` or Copilot CLI's
`.github/instructions/*.instructions.md` + `applyTo:`. This is UNCONFIRMED-as-absent
(not found in the sources fetched this session), not proven impossible,
but it means OpenCode's own documented answer to "how do I scope
instructions to a subset of files without paying for them everywhere"
is currently just the invoke-only skills tier below, not a middle tier.

### 3.3 A nearby-instruction-file auto-attach mechanism, source-verified, distinct from tier 1 and tier 3

`instruction.ts` exposes a second function, `resolve()`, called when the
model reads a file via the `read` tool: it walks upward from that file's
directory (bounded at the project root) looking for the nearest
`AGENTS.md`/`CLAUDE.md`/`CONTEXT.md` not already surfaced as part of
tier 1 or already attached to that same assistant message (tracked via a
per-message `claims` set, keyed off a helper, `extract()`, that scans
prior completed `read`-tool message parts for a `metadata.loaded` path
list). Any such file found is attached to that turn's context as
`Instructions from: <path>\n<content>`. This is architecturally the
closest OpenCode comes to Claude Code's own **nested-CLAUDE.md-loads-on-
first-read-of-that-subdirectory** behavior (cross-referenced, not
repeated, from Claude Code's own tier documented above) -- a real,
source-verified, per-message-deduplicated auto-attach mechanism, not a
docs-stated feature. BEST CURRENT UNDERSTANDING, UNCONFIRMED: whether
this mechanism is described anywhere in OpenCode's own public docs (it
was not found on `rules.mdx`) -- it currently exists only as a
source-verified implementation detail.

### 3.4 Tier 3 -- skills

VERIFIED (`skills.mdx`): OpenCode's invoke-only tier is the native
`skill` tool. Every discovered `SKILL.md`'s `name` and `description`
(1-1024 characters, frontmatter-only) is always listed in the tool's own
description as an `<available_skills>` block -- structurally the same
"index entry always resident, body loads on demand" shape both Claude
Code's and Copilot CLI's own skills tiers use above -- and the full body
loads only when the model calls `skill({ name: "..." })`. Discovery
walks the same project-root-to-worktree path as `AGENTS.md` (§3.2) for
`.opencode/skills/`, plus Claude-compatible (`.claude/skills/`) and a
third, `agents`-branded (`.agents/skills/`) convention at both project
and global scope, and per-skill/per-agent-pattern `allow`/`ask`/`deny`
permission gating (a `deny`d skill is omitted from `<available_skills>`
entirely, so a denied skill costs nothing, not even its index-entry
tokens -- a stricter budget guarantee than either closed-source
harness's own visibility controls document).

### 3.5 Measuring and toggling

No dedicated context-inspection command (an OpenCode analogue to Claude
Code's `/context` or Copilot CLI's `/context`/`/env`/`/instructions`)
was found in the docs pages fetched this session. This is
UNCONFIRMED-as-absent, not proven absent -- OpenCode's TUI is known
(per [tui-cli-application-architecture.md](tui-cli-application-architecture.md))
to expose a live token/cost footer, but this page found no dedicated
instruction-budget breakdown surface to cite alongside it.

---

## 4. pi

Sources for this section: VERIFIED, fetched 1 September 2026 directly from
`github.com/earendil-works/pi`, `main` branch, both docs and TypeScript source --
`packages/coding-agent/docs/usage.md` (context-file locations and precedence),
`settings.md` (confirmed no context/system-prompt keys live there), `extensions.md`
(Dynamic Tool Loading section, in full) -- cross-checked against
`packages/coding-agent/src/core/system-prompt.ts`, `resource-loader.ts`,
`agent-session.ts`, `agent-session-services.ts`, `skills.ts`, `slash-commands.ts`,
`tools/read.ts`, `tools/tool-definition-wrapper.ts`, and `defaults.ts`. Unlike this
page's Claude Code and Copilot CLI sections (docs-only) this pi section is
source-verified in the same sense §3's OpenCode section is: the claims below are
read off pi's own implementation, not inferred from documentation prose alone.

### 4.1 One monorepo, two real packages -- both spellings elsewhere in this book are correct

This book has cited pi as both `@earendil-works/pi-ai` (in
[llm-api-contract.md](llm-api-contract.md) §3.5) and `@earendil-works/pi-coding-agent`
(in [deterministic-orchestration.md](deterministic-orchestration.md),
[session-persistence.md](session-persistence.md)). Fetched directly this session,
`packages/coding-agent/package.json` and `packages/ai/package.json` in
`github.com/earendil-works/pi` (`main` branch) confirm these are **two distinct,
separately versioned npm packages living side by side in one monorepo**, not a
naming error to reconcile: `@earendil-works/pi-coding-agent` (`"description": "Coding
agent CLI with read, bash, edit, write tools and session management"`, `"bin": {"pi":
"dist/bundle/cli.js"}`) is the harness itself -- the subject of this section --
while `@earendil-works/pi-ai` (`"description": "Unified LLM API with automatic model
discovery and provider configuration"`) is the underlying multi-provider wire-protocol
library the coding agent depends on, documented from the API-shape angle in
[llm-api-contract.md](llm-api-contract.md) §3.5. Both packages currently ship at the
same version number (`0.84.4` as fetched), which is presumably why the book's earlier
pages cite whichever package name was locally relevant without contradiction. One
further, source-only wrinkle worth flagging: `compaction.md`'s own in-repo doc links
still point at `github.com/earendil-works/pi-mono`, an evident holdover from a prior
repository name -- `gh api repos/earendil-works/pi-mono` and `gh api
repos/earendil-works/pi` both resolve to the identical `full_name: "earendil-works/pi"`
this session, confirming `pi-mono` is a stale in-doc link to a renamed repository, not
a second, separate codebase.

### 4.2 Tier 1: the `AGENTS.md`/`CLAUDE.md` context-file hierarchy, read once at session start or on `/reload`

VERIFIED from `resource-loader.ts`'s `loadContextFileFromDir()`/`loadProjectContextFiles()`
functions and `usage.md`: pi discovers, in order, a **global** context file at
`~/.pi/agent/AGENTS.md` (the agent directory, `getAgentDir()`), then walks from the
project root's parent chain down to the current working directory collecting one
context file per directory, unshifting each into an ancestor-ordered list so the
final prompt sees outermost-first, cwd-last. Per directory, the first matching
filename from a fixed candidate list wins: `AGENTS.override.md`, `AGENTS.md`,
`AGENTS.MD`, `CLAUDE.md`, `CLAUDE.MD` -- so, like OpenCode's own precedence rule
(§3.2), an `AGENTS.override.md` or `AGENTS.md` in a directory silently supersedes a
`CLAUDE.md` there rather than both loading. A dedicated `findShadowedContextFile()`
helper additionally suppresses double-loading a linked Git worktree's own copy of the
same logical repository-scoped file when the worktree is nested under its main repo's
root (resolved via realpath, to handle a symlinked `/tmp`-style cwd on macOS
correctly) -- a narrower, more surgical duplicate-prevention rule than either other
harness documents for its own worktree handling.

Two behaviors distinguish this tier from all three other harnesses' own tier 1,
source-verified this session:

- **No stated size guidance was found.** Neither `usage.md` nor any other doc page
  fetched this session states an equivalent of Claude Code's "target under 200 lines"
  (§1.1) for `AGENTS.md`/`CLAUDE.md`.
- **Read once, not per-turn, and not automatically hot-reloaded.** `loadProjectContextFiles()`
  is invoked from `DefaultResourceLoader.reload()`, which the constructor calls once
  during session bootstrap (`agent-session-services.ts`) and which is otherwise only
  re-invoked by an explicit `/reload` slash command -- documented verbatim in
  `slash-commands.ts` as: **"Reload keybindings, extensions, skills, prompts, themes,
  and context files."** This places pi structurally with Claude Code's own
  session-start-read-with-no-documented-hot-reload posture (§1.1), the exact opposite
  of OpenCode's own finding in this page (§3.1) that `Instruction.system()` does a
  fresh disk read on *every* turn with no caching. Editing an `AGENTS.md` mid-session
  on pi therefore has no effect until the user explicitly runs `/reload` (or an
  extension calls the equivalent `ctx.reload()` API, which emits a `session_start`
  event with `reason: "reload"`).
- `--no-context-files` (short flag `-nc`) disables this tier entirely for the session,
  the pi analog of a kill switch rather than a per-directory exclusion glob.

### 4.3 System prompt shape: a small fixed template, not an embedded corpus

VERIFIED directly from `buildSystemPrompt()` in `system-prompt.ts`: absent a full
override (§4.3's next paragraph), pi's default system prompt is a short, fixed
template -- one opening sentence ("You are an expert coding assistant operating inside
pi, a coding agent harness. You help users by reading files, executing commands,
editing code, and writing new files."), an **`Available tools`** section, a
**`Guidelines`** section, a fixed block of pointers to pi's own documentation paths
(read only when the user asks about pi itself), and finally the working directory.
Two things keep this tier lean by construction rather than by editorial discipline
after the fact:

- **A tool only appears in `Available tools` if the caller supplied a one-line
  `toolSnippets` entry for it** -- `visibleTools = tools.filter((name) =>
  !!toolSnippets?.[name])`. A registered, active tool with no snippet is *silently
  omitted from that listing* even though its full JSON-schema definition is still
  sent to the model as a callable tool (§4.4) -- the system-prompt text and the
  tool-schema payload are two independent budgets in pi's own architecture, not one.
- **Guidelines are conditionally assembled and deduplicated** via a `Set`-backed
  `addGuideline()` helper: file-exploration guidance is only added when the active
  tool set actually lacks `grep`/`find`/`ls` (so a project running with those tools
  active never pays for the "use bash for ls/rg/find" bullet), caller-supplied
  `promptGuidelines` are trimmed and deduped against the fixed always-included pair
  ("Be concise in your responses", "Show file paths clearly when working with
  files"), so no guideline line is ever duplicated regardless of how many tools
  contribute one.

**Two escape hatches replace the whole template rather than trimming it.** Source-verified
from `discoverSystemPromptFile()`/`discoverAppendSystemPromptFile()` in
`resource-loader.ts`: a project-level `.pi/SYSTEM.md` (requires
`settingsManager.isProjectTrusted()`, tying full system-prompt replacement to the same
project-trust gate [permissions-and-sandboxing.md](permissions-and-sandboxing.md)
documents for pi's sandboxing posture) or a global `~/.pi/agent/SYSTEM.md` **replaces**
the entire default template above; a sibling `APPEND_SYSTEM.md` at either scope
(same project-trust gate for the project variant) is concatenated onto whichever
system prompt is in effect instead of replacing it. Project takes precedence over
global at each pair. Notably, this same explicit trust gate does **not** appear
anywhere in `loadProjectContextFiles()` itself in the source read this session -- so
an untrusted project's `AGENTS.md`/`CLAUDE.md` content still loads into tier 1 as
ordinary "project context," while only a full or partial *system-prompt replacement*
from that same untrusted project is withheld. That is a real, source-verified
asymmetry worth flagging rather than assuming symmetric trust-gating across every
project-supplied instruction surface.

### 4.4 Tool-schema footprint: four default tools, one-line schema descriptions throughout

VERIFIED from `defaults.ts`, `agent-session.ts`, and the individual tool source files
(`tools/read.ts` inspected directly): pi's **default active tool set is exactly
four tools -- `read`, `bash`, `edit`, `write`** (`defaultActiveToolNames` in
`agent-session.ts`, matching the JSDoc default documented directly in
`BuildSystemPromptOptions`). Additional built-in tools (`find`, `grep`, `ls`,
`powershell`) exist in `src/core/tools/` but are not part of that default set and
must be explicitly activated. Each tool's JSON-schema is built with `typebox`
(`Type.Object({...})`), and the field-level descriptions are terse, one-line strings
-- e.g. `read`'s schema: `path: Type.String({ description: "Path to the file to read
(relative or absolute)" })`, `offset`/`limit` similarly one-clause each -- with the
tool's own system-prompt snippet equally terse (`readToolSystemPromptContribution.snippet
= "Read file contents"`). No MCP (Model Context Protocol) server integration is named
anywhere in the docs or source read this session for pi specifically; this is a
negative finding scoped to the sources fetched this session, not proof MCP support
does not exist elsewhere in the codebase.

### 4.5 A genuinely distinct lazy/deferred-schema mechanism: `pi.registerTool()` + `pi.setActiveTools()`

This is pi's own, source-and-docs-verified answer to "does this harness defer tool
schemas the way a skill defers its body." VERIFIED, quoted verbatim from
`extensions.md`'s "Dynamic Tool Loading" section: an extension can **"register many
tools while keeping only a small initial set active. A tool can then add more tools
with `pi.setActiveTools()` during execution. Pi detects purely additive changes,
records the newly available tool names on that tool result, and applies the updated
active set before the next model request."** Critically, the mechanism branches on
the *provider's own* capability, not just pi's own logic:

```mermaid
flowchart TD
    Reg["pi.registerTool() -- tool exists in\npi.getAllTools(), but inactive"]
    Loader["Loader tool (e.g. search_tools) stays\nactive; searchable tools stay inactive"]
    Call["Loader calls pi.setActiveTools([...current, ...matching])\n(must be purely additive)"]
    Reg --> Loader --> Call
    Call --> Check{"Does the model support\nnative deferred loading?"}
    Check -->|"Anthropic Sonnet/Opus/Fable\n4.5+ (no Haiku)"| Native1["defer_loading definitions;\nload point = tool_reference content.\nStable prompt prefix preserved."]
    Check -->|"OpenAI gpt-5.4+ family"| Native2["tool_search_call / tool_search_output\nitems at the load point.\nStable prompt prefix preserved."]
    Check -->|"Any other model/provider"| Fallback["Fallback: pi resends the COMPLETE\ncurrent active tool list on the next\nrequest -- may invalidate the provider's\ncached prompt prefix"]
```

Per this same source: "This works with every model. Models with native
deferred-loading support preserve the stable prompt prefix and load the new
definitions at the tool-result position. Other models use the fallback described
below." The native path is named precisely for two model families -- **Anthropic**
("Models: Sonnet, Opus, Fable version 4.5 or newer (without Haiku)"; native
representation: "Deferred definitions use `defer_loading`; the load point uses
`tool_reference` content") and **OpenAI** ("Models: `gpt-5.4` and newer family"; "Pi
adds completed client `tool_search_call` and `tool_search_output` items at the load
point") -- with a documented custom-provider escape hatch, `compat.supportsToolReferences:
true` (for `anthropic-messages`) or `compat.supportsToolSearch: true` (for
`openai-responses`/`openai-codex-responses`), left disabled unless the actual
endpoint accepts the corresponding native protocol. The fallback path is explicit
about its own cost: "Pi sends the complete current active tool list normally on the
next request. The model can call the newly activated tools, but adding their
definitions may invalidate the provider's cached prompt prefix" -- the same
prompt-cache-invalidation concern this book's own [caching.md](caching.md) documents
for each harness independently, here tied specifically to tool-set churn rather than
message-history churn. Tool *removals* (a non-additive change, e.g. replacing one
group of tools with another) always take the fallback path regardless of model --
deferred loading is documented as additive-only. One more caveat named directly:
"activating a tool with `promptSnippet` or `promptGuidelines` rebuilds the system
prompt; that system-prompt change can invalidate the prefix even when the provider
supports deferred schemas" -- so a lazily-activated tool that also wants a visible
`Available tools` line (§4.3) trades away part of the very cache benefit deferred
loading exists to preserve; the docs' own guidance is that "lazily loaded tools
should usually rely on their tool `description` and omit active-only prompt
metadata."

### 4.6 Skills: the same invoke-only tier, an XML index rather than JSON or a truncated string

VERIFIED from `skills.ts`'s `formatSkillsForPrompt()`: pi's skills tier follows the
same "index entry always resident, body loads on demand" shape as Claude Code (§1.4),
Copilot CLI (§2.3), and OpenCode (§3.4), but formats the always-resident index as XML
per the `agentskills.io` Agent Skills standard rather than a description-truncated
listing or a JSON tool-schema block: a `<available_skills>` element containing one
`<skill>` per non-`disable-model-invocation`-flagged skill, each with `<name>`,
`<description>`, and `<location>` (the skill's absolute file path) children, with the
model instructed to "Use the read tool to load a skill's file when the task matches
its description" -- i.e. pi's own skill body is not auto-injected on invocation the
way Claude Code's and Copilot CLI's own skill bodies are; the model must issue its
own `read` tool call against the listed `<location>` path, making the skill's body
cost identical to any other file the model chooses to read. Skills flagged
`disable-model-invocation: true` in frontmatter are omitted from `<available_skills>`
entirely (only invocable via an explicit `/skill:name`, cross-referenced from
[built-in-skills.md](built-in-skills.md)'s own deeper pi-skills coverage, not
repeated here) -- the same "denied/disabled costs nothing, not even an index entry"
property OpenCode's own `deny` permission provides (§3.4).

### 4.7 No path-scoped tier, and no nearby-file auto-attach on read -- a source-verified negative finding

Neither `usage.md` nor a review of `resource-loader.ts`/`agent-session.ts` this
session turned up anything resembling Claude Code's `paths:`-scoped rules (§1.2) or
Copilot CLI's `applyTo:`-scoped instruction files (§2.2). `tools/read.ts` does contain
a `COMPACT_RESOURCE_FILE_NAMES` constant listing the same five context-file names
from §4.2 (`AGENTS.override.md`, `AGENTS.md`, `AGENTS.MD`, `CLAUDE.md`, `CLAUDE.MD`),
but reading its actual use this session (`getCompactReadClassification()`) shows it
exists purely to pick a compact TUI display label ("resource" vs. "docs" vs. "skill")
for how a read of one of these files is rendered in the transcript -- it is **not**
a context-injection mechanism. This is the opposite finding from OpenCode's own
source-verified `Instruction.resolve()` (§3.3), which genuinely attaches a nearby
un-surfaced `AGENTS.md`/`CLAUDE.md` to context when the model reads a file in that
subdirectory. On pi, reading a subdirectory's own `AGENTS.md` via the `read` tool
contributes only that tool call's own result to context, exactly like reading any
other file -- there is no separate, silent attach step. Combined with §4.2's
ancestor-walk-only discovery (parent directories and cwd, never *descendant*
subdirectories the agent later navigates into), pi has neither a path-scoped tier nor
a lazy-by-descendant-location tier; skills (§4.6) are its only lever for scoping
instructions to a subset of tasks without paying for them everywhere.

### 4.8 Measuring and toggling

No dedicated context-inspection command comparable to Claude Code's `/context` or
Copilot CLI's `/context`/`/env`/`/instructions` was found in the slash-command list
read directly from `slash-commands.ts` this session. The closest analog is
`/session` (documented inline in source as **"Show session info and stats"**), but
nothing fetched this session confirms it itemizes *which* `AGENTS.md`/`CLAUDE.md`
files loaded the way Claude Code's `/context` **Memory files** list does --
**BEST CURRENT UNDERSTANDING, UNCONFIRMED** that `/session` surfaces per-file
instruction provenance rather than aggregate token/cost stats alone. The TUI's own
footer is documented (per `usage.md`) to display "token/cache usage, cost, context
usage, and current model" live during a session -- the practical, always-visible
substitute for a dedicated breakdown command, structurally similar to OpenCode's own
token-footer fallback (§3.5). `--no-context-files`/`-nc` (§4.2) is the one documented
toggle; no equivalent of Claude Code's `claudeMdExcludes` glob-based partial
exclusion was found. The `reserveTokens`/`keepRecentTokens` compaction budget that
governs how much of the window survives untouched once tier 1 plus conversation
history are loaded is covered in full in
[context-compression.md](context-compression.md) §4.6, not repeated here -- this
section is about what pi puts into context eagerly, not how it evicts what's already
there.

---

## 5. Synthesis

| Concern | Claude Code | Copilot CLI | OpenCode | pi |
|---|---|---|---|---|
| Tier-1 file(s) | `CLAUDE.md` hierarchy (managed → user → project → local), plus `.claude/rules/*.md` **without** `paths:` | `.github/copilot-instructions.md`, `AGENTS.md`, `CLAUDE.md`, `~/.copilot/instructions/**` | `AGENTS.md` (project + global), `CLAUDE.md`/deprecated `CONTEXT.md` as Claude-compat fallbacks, plus config `instructions[]` (local globs + remote URLs) | `AGENTS.md`/`AGENTS.override.md`/`CLAUDE.md` ancestor walk (global `~/.pi/agent/AGENTS.md` + every directory from project root down to cwd), plus a full-replace `SYSTEM.md`/append-only `APPEND_SYSTEM.md` pair (project variant trust-gated) |
| Tier-1 freshness | Session-start read; no documented hot-reload | Undocumented either way | **Re-read from disk every turn** -- source-verified, no caching in `Instruction.system()` | Session-start read (via `resource-loader.ts`'s `reload()` at bootstrap); re-read only on explicit `/reload` -- source-verified, same posture as Claude Code, the opposite of OpenCode |
| Stated size guidance | "target under 200 lines per CLAUDE.md file"; loaded in full regardless of length | None found on the pages fetched | None found on the pages fetched | None found on the pages fetched |
| Do `@` imports save context? | **No** -- stated twice in the docs | UNCONFIRMED; imports exist (v1.0.66), token effect not documented | Not applicable -- no `@`-import-expansion mechanism found in `AGENTS.md`/`instructions[]` loading (the docs instead show a manual, agent-authored "read this file on demand" convention, not a harness-parsed import syntax) | Not applicable -- no `@`-import-expansion mechanism for context files found in the source read this session |
| Path-scoped tier | `.claude/rules/` + `paths:` glob list; triggers on reading a matching file, "not on every tool use" | `.github/instructions/*.instructions.md` + `applyTo:`; body no longer in system prompt every session (v1.0.35), consolidated to a table row (v1.0.26) | **None found** -- UNCONFIRMED-as-absent | **None found** -- source-verified absent this session |
| Lazy-by-location tier | Nested `CLAUDE.md` and nested `.claude/skills/` below cwd load on first read/edit in that subdirectory | Discovery walks working dir → git root (v1.0.11); no documented "load on read of subdirectory file" behavior found | Source-verified nearby-file auto-attach: walking up from a `read`-tool target's directory for the nearest un-surfaced `AGENTS.md`/`CLAUDE.md`/`CONTEXT.md`, deduplicated per assistant message | **None** -- source-verified negative: `read` tool's own `COMPACT_RESOURCE_FILE_NAMES` handling is a TUI display label only, not a context-attach mechanism |
| Tool-schema deferral | Not documented as a distinct mechanism from the skills tier | Experimental embedding-based per-turn retrieval (below) doubles as this | Not documented for OpenCode's own built-in tool set | **Native deferred loading** for Anthropic Sonnet/Opus/Fable 4.5+ (`defer_loading`/`tool_reference`) and OpenAI gpt-5.4+ (`tool_search_call`/`tool_search_output`) via `pi.registerTool()`+`pi.setActiveTools()`; additive-only, falls back to resending the full active tool list (cache-prefix risk) on other models or on non-additive changes |
| Invoke-only tier | Skills: body loads on use; description always in context (1,536-char cap) unless `disable-model-invocation: true`; supports its own `paths:` | Skills: `SKILL.md` "injected in the agent's context" when used; always-on listing cost UNKNOWN | Skills: `name`+`description` (≤1,024 chars) always listed in `<available_skills>`; body loads via `skill({name})` call; a `deny`d skill is omitted from the listing entirely (zero index-entry cost) | Skills: `<available_skills>` XML index (name/description/location) always listed once any skills exist; body is **not** auto-injected on invocation -- the model must issue its own `read` tool call against the listed path; a `disable-model-invocation: true` skill is omitted from the index entirely |
| Exclusion | `claudeMdExcludes` globs, any settings layer, arrays merge | `/instructions` toggle picker | Per-skill/per-agent-pattern `allow`/`ask`/`deny` permissions; no equivalent exclusion lever found for `AGENTS.md`/`instructions[]` itself | `--no-context-files`/`-nc` disables the whole tier-1 context-file mechanism at once; no partial-exclusion glob found |
| Free maintainer notes | Block-level HTML comments stripped before injection | Not documented on pages fetched | Not documented on pages fetched | Not documented on pages fetched |
| Automated trim advice | `/doctor` trim proposal (v2.1.206+) | Not documented on pages fetched | Not documented on pages fetched | Not documented on pages fetched |
| Retrieval-based loading | Not documented | Experimental embedding-based per-turn retrieval of skill/MCP instructions; `dynamicRetrieval` setting | Not documented; remote `instructions[]` URLs are always fully fetched (5s timeout), not retrieved by relevance | Not documented for context files; the closest analog is the provider-capability-gated tool-schema deferral above, which is retrieval-*shaped* but triggered by an extension's own `setActiveTools()` call, not a background relevance search |
| Verify what loaded | `/context` → **Memory files**; `InstructionsLoaded` hook | `/context` (Custom Instructions itemized separately), `/env`, `/instructions` | No dedicated command found in the docs fetched this session | No dedicated command found in the sources fetched this session; `/session` ("session info and stats") is the closest analog, per-file provenance UNCONFIRMED; TUI footer shows live token/cache/cost/context usage |
| Survives compaction? | Tier 1 re-injected; path-scoped and nested lost until retriggered; skills capped 5K/25K | Skills survive; instruction-file re-injection **undocumented** | Not directly investigated here (see [context-compression.md](context-compression.md) §3 for OpenCode's own compaction mechanics); moot in one sense, since tier 1 is rebuilt fresh every turn regardless of compaction state | Not directly investigated here (see [context-compression.md](context-compression.md) §4 for pi's own compaction mechanics); tier 1 is loaded once at session start (§4.2), so it is not literally "re-read" by compaction the way OpenCode's per-turn rebuild makes the question moot, but nothing fetched this session states whether pi's summarization step re-includes or drops the standing context-file content specifically |

**The design lesson.** All four harnesses independently converged on
some version of the same multi-tier answer, and all four make the
*same* thing tier 1 that authors intuitively expect to be cheap: the
imported/split-out file (on the harnesses that have an import
mechanism at all). The distinction that matters is not "one file vs.
many files," it is **"does this text have a trigger?"** A file with no
trigger (`@` import, unscoped rule, plain `copilot-instructions.md`,
OpenCode's own `AGENTS.md`/`instructions[]`, pi's own
`AGENTS.md`/`CLAUDE.md` ancestor walk) costs you tokens on every turn
no matter how many files you split it across. A file with a trigger
(`paths:`, `applyTo:`, a skill name) costs you only its index entry
until the trigger fires -- and on OpenCode specifically, "every turn"
is not a figure of speech: §3.1's re-read finding means the tier-1 cost
is paid, and the tier-1 *content* can change, on every single model
call, not just once at launch. pi sits closer to Claude Code on this
particular axis (§4.2's session-start-or-explicit-`/reload` read) than
to OpenCode, but pi contributes a genuinely new lever the other three
harnesses do not document at all: a *tool-schema* trigger (§4.5) that
is independent of the instruction-file trigger vocabulary above --
provider-native deferred loading keyed off `pi.setActiveTools()` rather
than a glob match or a skill name, which is a lazy-loading axis this
page had not previously found evidence of on any harness for the tool
layer specifically, as opposed to the instruction-file or skill-body
layers all four harnesses share.

**A cross-harness recipe** (relevant to this project's requirement that
everything work across targets):

1. **Tier 1, one small file.** Keep a root `CLAUDE.md` under ~200 lines
   holding only always-true facts. This is close to the one instruction
   file all three harnesses verifiably read at runtime -- Copilot CLI
   reads `CLAUDE.md` directly (its changelog); OpenCode reads it too,
   but only as a fallback when no `AGENTS.md` exists at the same scope
   (§3.2); Claude Code does not read `AGENTS.md` or
   `copilot-instructions.md` (its docs). Practically: an `AGENTS.md`
   with the same content, plus a `CLAUDE.md` for Claude Code, covers all
   three without relying on OpenCode's fallback-only behavior.
2. **Tier 2 has no shared file, and OpenCode has no tier 2 at all.**
   For Claude Code and Copilot CLI you still need two parallel sets:
   `.claude/rules/*.md` with `paths:` for Claude Code and
   `.github/instructions/*.instructions.md` with `applyTo:` for Copilot
   CLI. The glob dialects are similar but not identical (Claude Code
   documents brace expansion with an explicit 1,000-pattern budget;
   Copilot documents comma-separated patterns and a string-or-array
   `applyTo`). Do not generate one from the other without checking the
   pattern semantics, and do not expect OpenCode to honor either --
   its own docs show no scoped-loading equivalent (§3.2), so
   path-conditional guidance either goes in `AGENTS.md` unconditionally
   (paying the token cost everywhere) or is left out for that harness.
3. **Tier 3 can be shared, three ways.** Skills are the one on-demand
   tier where a single directory can serve all three: Copilot CLI's own
   docs list `.claude/skills` among its project skill locations, and
   OpenCode's own skills docs list `.claude/skills/` as a recognized
   discovery path too. Put procedures and long reference material here,
   keep `SKILL.md` bodies short, and push detail into supporting files
   the agent reads only when needed.
4. **Verify per harness, every time.** `/context` on Claude Code and
   Copilot CLI, `InstructionsLoaded` on Claude Code, `/env` and
   `/instructions` on Copilot CLI. OpenCode has no equivalent inspector
   documented -- the practical substitute is reasoning from the source
   behavior in §3.1-§3.3 directly, or watching the TUI's own token
   footer. The cost of a scoped rule on the two closed-source harnesses
   is empirically checkable in under a minute; guessing is not
   necessary there.
5. **Remember the compaction/reload asymmetry, now three-way.** On
   Claude Code, moving text out of tier 1 means it can stop applying
   after a compaction. On Copilot CLI, whether instruction files are
   re-injected post-compaction is undocumented. On OpenCode, the
   question is closer to moot: tier 1 is rebuilt from disk every turn
   regardless of compaction, so an edited `AGENTS.md` is visible on the
   very next turn on OpenCode in a way neither other harness documents
   for itself. Invariants that must never lapse still belong in tier 1
   on all three, even at token cost -- OpenCode just pays that cost with
   a freshness guarantee the other two do not offer.

---

## Sources

All fetched 2026-07-30 unless marked otherwise.

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

**OpenCode (fetched 2026-08-24; authoritative for OpenCode's documented and real-source behavior, with the standing `dev`-branch caveat):**
- `opencode.ai/docs/rules/`, source-checked against `github.com/anomalyco/opencode`'s own `packages/web/src/content/docs/rules.mdx` (`dev` branch, via `gh api`) -- `AGENTS.md` initialization via `/init`, project/global/Claude-compat discovery locations and precedence ("first matching file wins in each category"), the three `OPENCODE_DISABLE_CLAUDE_CODE*` env vars, the `instructions` config array (local globs and remote URLs, "combined with your AGENTS.md files"), the manual `@`-reference convention documented as an *agent*-followed instruction rather than a harness-parsed import.
- `packages/web/src/content/docs/skills.mdx`, same repo/branch/method -- `SKILL.md` frontmatter fields and validation rules, `.opencode/skills/`+Claude-compat+`.agents/skills/` discovery paths at project and global scope, the `<available_skills>` always-listed index block, `skill({name})` invocation, and the `allow`/`ask`/`deny` permission schema including the omitted-from-listing-entirely behavior on `deny`.
- `packages/opencode/src/session/instruction.ts` and `packages/opencode/src/session/prompt.ts`, same repo/branch, fetched via `gh api` -- the `Instruction.system()`/`Instruction.resolve()` implementation: per-turn fresh-disk-read of tier-1 instruction files (no caching), the deprecated `CONTEXT.md` filename not named in the docs page fetched, the `instructions[]` remote-URL fetch's 5-second timeout, and the nearby-instruction-file auto-attach mechanism triggered off `read`-tool calls with a per-assistant-message dedup set. Authoritative for OpenCode's real implementation as of this session's fetch; per this book's standing caveat, `dev` is not a stable release tag and may not match the current stable release.
- A `search/code` sweep of `packages/web/src/content/docs` for `applyTo`/`paths:`-style scoping syntax, same session -- zero hits, grounding the UNCONFIRMED-as-absent finding on a path-scoped instruction tier (§3.2).

**pi (fetched 1 September 2026 from `github.com/earendil-works/pi`, `main` branch; this
section is source-verified, not docs-only -- see §4's own opening note):**
- `packages/coding-agent/package.json` and `packages/ai/package.json` (via `gh api
  repos/earendil-works/pi/contents/...`) -- confirmed live that
  `@earendil-works/pi-coding-agent` and `@earendil-works/pi-ai` are two distinct,
  separately versioned packages in one monorepo (§4.1), resolving the two spellings
  used elsewhere in this book.
- `gh api repos/earendil-works/pi` and `gh api repos/earendil-works/pi-mono`, same
  session -- both resolve to `full_name: "earendil-works/pi"`, confirming `pi-mono` is
  a stale in-doc link to a renamed repository rather than a second codebase (§4.1).
- `packages/coding-agent/docs/usage.md` (fetched via
  `raw.githubusercontent.com/earendil-works/pi/main/...`) -- the `AGENTS.md`/
  `AGENTS.override.md`/`CLAUDE.md` context-file discovery hierarchy and precedence
  (§4.2), the `.pi/SYSTEM.md`/`APPEND_SYSTEM.md` full-replace/append system-prompt
  override pair (§4.3), `--no-context-files`/`-nc` (§4.2, §4.8), and the TUI footer's
  documented token/cache/cost/context display (§4.8).
- `packages/coding-agent/docs/settings.md`, same method -- confirmed no
  context-file/system-prompt/token-budget settings keys live there (a negative result
  established by fetching, cited in §4's opening note).
- `packages/coding-agent/docs/extensions.md` (fetched in full via `gh api
  repos/earendil-works/pi/contents/packages/coding-agent/docs/extensions.md`) -- the
  "Dynamic Tool Loading" section in full: `pi.registerTool()`/`pi.setActiveTools()`,
  the native-deferred-loading model matrix (Anthropic Sonnet/Opus/Fable 4.5+ minus
  Haiku via `defer_loading`/`tool_reference`; OpenAI `gpt-5.4`+ via
  `tool_search_call`/`tool_search_output`), the `compat.supportsToolReferences`/
  `compat.supportsToolSearch` custom-provider escape hatch, the fallback behavior and
  its cache-prefix-invalidation cost, the additive-only constraint, the
  `promptSnippet`/`promptGuidelines`-rebuilds-the-prompt caveat, and the Output
  Truncation section's 50KB/~10k-token/2,000-line limit (§4.5).
- `packages/coding-agent/src/core/system-prompt.ts` (via `gh api`, in full) --
  `buildSystemPrompt()`'s fixed default template, the `toolSnippets`-gated
  `Available tools` listing, and the deduplicated conditional `Guidelines` assembly
  (§4.3).
- `packages/coding-agent/src/core/resource-loader.ts` (via `gh api`, in full) --
  `loadContextFileFromDir()`/`findShadowedContextFile()`/`loadProjectContextFiles()`
  (§4.2's ancestor-walk discovery and worktree-shadowing rule),
  `discoverSystemPromptFile()`/`discoverAppendSystemPromptFile()` (§4.3's
  project-trust-gated `SYSTEM.md`/`APPEND_SYSTEM.md` precedence, and the
  asymmetry with the untrusted-but-still-loaded context-file tier), and the
  `reload()` method that `/reload` and session bootstrap both call (§4.2).
- `packages/coding-agent/src/core/agent-session.ts` and
  `agent-session-services.ts` (via `gh api`, in full) -- `_rebuildSystemPrompt()`
  reading `resourceLoader.getAgentsFiles()`/`getSystemPrompt()` from the cached
  reload state rather than re-reading disk per turn, `defaultActiveToolNames`
  confirming the four-tool default (§4.4), and `session.reload()`'s
  `session_start`/`reason: "reload"` event emission (§4.2).
- `packages/coding-agent/src/core/skills.ts` (via `gh api`, in full) --
  `formatSkillsForPrompt()`'s `<available_skills>` XML index, the
  `disable-model-invocation`-omits-from-index behavior, and the 1,024-character
  `MAX_DESCRIPTION_LENGTH` (§4.6).
- `packages/coding-agent/src/core/slash-commands.ts` (via `gh api`, in full) --
  the full slash-command list, confirming `/reload`'s documented scope and the
  absence of any `/context`-equivalent command (§4.2, §4.8).
- `packages/coding-agent/src/core/tools/read.ts` (via `gh api`, in full) --
  `COMPACT_RESOURCE_FILE_NAMES` and `getCompactReadClassification()`, confirmed to be
  a TUI display-label mechanism rather than a context-injection mechanism (§4.7); the
  `readSchema` typebox definition's one-line field descriptions (§4.4).
- `packages/coding-agent/src/core/tools/tool-definition-wrapper.ts` and
  `defaults.ts` (via `gh api`, in full) -- confirmed no MCP-server integration or
  additional lazy-schema mechanism beyond §4.5's dynamic tool loading (§4.4).
