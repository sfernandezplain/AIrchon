# Memory management -- Claude Code vs. GitHub Copilot CLI

How each harness persists information across sessions, how that
information gets back into context, and what happens to it when a long
session compacts.

Every claim below is tagged VERIFIED (fetched this session from the
named source) or BEST CURRENT UNDERSTANDING, UNCONFIRMED. Sources and
fetch dates at the bottom. Claude Code and Copilot CLI are separate
products from separate companies -- nothing confirmed for one is
assumed for the other.

**The one-line answer to "is it a memory tool or file convention?":**
Claude Code is entirely file-based and machine-local -- plain markdown
on your disk, written with ordinary file tools, no dedicated memory
tool primitive. Copilot CLI has both: instruction *files* in the repo
**and** a genuine server-side memory service (Copilot Memory) exposed
to the model as tool calls (`store_memory`, `vote_memory`) with
GitHub-account/repository scoping. Both VERIFIED, see below.

```mermaid
flowchart LR
    subgraph CC["Claude Code"]
        CM["CLAUDE.md hierarchy (on disk, human-authored)"] --> Ctx1[Context window]
        AM["Auto memory: MEMORY.md index + topic files (on disk, agent-authored)"] --> Ctx1
    end
    subgraph GH["Copilot CLI"]
        IF["Instruction files: copilot-instructions.md, AGENTS.md, CLAUDE.md (on disk)"] --> Ctx2[Context window]
        SM["Copilot Memory (server-side service)"] -->|"store_memory / vote_memory tool calls"| Ctx2
    end
```

---

## 1. Claude Code

Sources for this section: `code.claude.com/docs/en/memory`,
`code.claude.com/docs/en/context-window`,
`code.claude.com/docs/en/how-claude-code-works`, and
`github.com/anthropics/claude-code` `CHANGELOG.md`, all fetched
2026-07-30. VERIFIED unless a claim is tagged otherwise.

### 1.1 Two mechanisms, not one

The docs are explicit that there are exactly two things carrying
knowledge across a session boundary, and that "each Claude Code session
begins with a fresh context window":

| | CLAUDE.md files | Auto memory |
|---|---|---|
| Who writes it | You | Claude |
| What it contains | Instructions and rules | Learnings and patterns |
| Scope | Project, user, or org | Per repository, shared across worktrees |
| Loaded into | Every session | Every session (first 200 lines or 25KB) |

(That table is reproduced from the docs page.) Critically, the docs
state both "are loaded at the start of every conversation" and that
"Claude treats them as context, not enforced configuration" -- to block
an action regardless of what the model decides, the documented answer
is a `PreToolUse` hook, not a memory file.

### 1.2 CLAUDE.md: locations and load order

```mermaid
flowchart TD
    M["Managed policy CLAUDE.md<br/>(macOS/Linux/WSL/Windows fixed paths)"] --> U["User instructions<br/>~/.claude/CLAUDE.md"]
    U --> P["Project instructions<br/>./CLAUDE.md or ./.claude/CLAUDE.md"]
    P --> L["Local instructions<br/>./CLAUDE.local.md"]
    L --> Ctx["Concatenated into context:<br/>broadest first, nearest-to-launch-dir read last"]
```

Four scopes, listed by the docs in load order, broadest first:

| Scope | Location |
|---|---|
| Managed policy | macOS `/Library/Application Support/ClaudeCode/CLAUDE.md`; Linux/WSL `/etc/claude-code/CLAUDE.md`; Windows `C:\Program Files\ClaudeCode\CLAUDE.md` |
| User instructions | `~/.claude/CLAUDE.md` |
| Project instructions | `./CLAUDE.md` or `./.claude/CLAUDE.md` |
| Local instructions | `./CLAUDE.local.md` (gitignore it) |

Resolution is a walk *up* the directory tree from cwd, checking each
directory for `CLAUDE.md` and `CLAUDE.local.md`. All discovered files
are **concatenated, not overridden** -- ordered filesystem-root-down, so
instructions nearest your launch directory are read last, and within a
directory `CLAUDE.local.md` is appended after `CLAUDE.md`. Files in
*subdirectories* below cwd are discovered but **not** loaded at launch;
they load when Claude reads a file in that subdirectory.

`claudeMdExcludes` (glob patterns against absolute paths, arrays merge
across settings layers) skips ancestor files in monorepos; managed
policy CLAUDE.md cannot be excluded. A managed CLAUDE.md can also be
inlined as a `claudeMd` string key in `managed-settings.json`, honored
only in managed/policy settings.

`--add-dir` directories do **not** contribute memory files unless
`CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` is set.

### 1.3 Imports and the AGENTS.md question

`@path/to/import` inside a CLAUDE.md expands the referenced file into
context **at launch** -- relative paths resolve against the importing
file, recursion is capped at four hops, and import parsing skips code
spans and fenced blocks (so `` `@README` `` in backticks stays
literal). The docs are blunt that this is an organization tool, not a
context-saving one: "imported files still load and enter the context
window at launch."

Imports in a *project* memory file whose path resolves outside the
working directory are "external" and trigger a one-time approval dialog;
imports in user-scope files (`~/.claude/CLAUDE.md`, `~/.claude/rules/`)
load without a dialog.

**Claude Code does not read `AGENTS.md`.** The docs say so directly:
"Claude Code reads `CLAUDE.md`, not `AGENTS.md`." The recommended
bridge is a `CLAUDE.md` containing `@AGENTS.md` (or a symlink, with the
caveat that Windows symlinks need Administrator or Developer Mode).
Separately, `/init` *reads* other agents' rule files -- Cursor
(`.cursor/rules/`, `.cursorrules`) and Copilot
(`.github/copilot-instructions.md`) -- and folds relevant parts into the
CLAUDE.md it generates; with `CLAUDE_CODE_NEW_INIT=1` it also reads
`AGENTS.md`, `.devin/rules/`, `.windsurf/rules/`/`.windsurfrules`, and
`.clinerules`. That is a one-time authoring convenience, not runtime
loading.

### 1.4 `.claude/rules/` -- the path-scoped tier

`.claude/rules/**/*.md` (discovered recursively, symlinks supported and
circular links handled) is the modular alternative to one long
CLAUDE.md. Rules without `paths:` frontmatter load at launch with the
same priority as `.claude/CLAUDE.md`. Rules **with** `paths:` (glob
list) load only when Claude reads a matching file -- "not on every tool
use." `~/.claude/rules/` is the user-level equivalent, loaded before
project rules so project rules win.

Brace expansion in `paths:` shares a budget of 1,000 expanded patterns
and 4 MiB per rule; over-budget patterns are used unexpanded and match
nothing. Project rules are skipped when `project` is excluded from
`--setting-sources` (as of v2.1.211 -- before that, on-demand rules
loaded anyway).

### 1.5 Auto memory: the file-based learned-preferences store

On by default. Storage is `~/.claude/projects/<project>/memory/`, with
`<project>` derived from the **git repository**, so all worktrees and
subdirectories of one repo share a single memory directory. The
directory holds a `MEMORY.md` entrypoint plus arbitrary topic files
Claude creates (`debugging.md`, `api-conventions.md`, ...).

The mechanics that matter for context budgeting:

- **Only `MEMORY.md` loads at session start**, and only its first 200
  lines or 25KB, whichever comes first. Content past that is simply not
  loaded.
- **Topic files are not loaded at startup.** Claude "reads them on
  demand using its standard file tools." That sentence is the whole
  answer to "is there a memory tool?" -- retrieval of the detailed tier
  is ordinary file reading, model-driven, not a special primitive.
- Claude Code enforces the index budget after writes: near a limit it
  reminds Claude to shorten; over a limit the write succeeds but an
  error tells Claude to rewrite the index, because the overflow is
  dropped on next load (v2.1.210; corroborated by CHANGELOG "Memory
  writes that leave a MEMORY.md index over its read limit now produce an
  explicit error instead of silent truncation" and "the agent is now
  reminded to compact its `MEMORY.md` index when nearing the size
  limit"). As of v2.1.211 frontmatter and block-level HTML comments are
  stripped before measuring.
- As of v2.1.214, a memory file that already begins with YAML
  frontmatter gets a `modified` ISO-8601 timestamp written on each save.
  Claude Code never *adds* frontmatter to a file that has none.
- **Machine-local.** Not shared across machines or cloud environments.
- Auto memory is **not** inherited by subagents (the exception is a
  fork, which inherits the parent conversation). A subagent's own auto
  memory, enabled by the subagent `memory` field, is a separate
  directory.

Controls: `/memory`'s toggle writes `autoMemoryEnabled` to
`~/.claude/settings.json`; `autoMemoryEnabled: false` in a project's
settings disables it there; `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` kills it
by env var; `autoMemoryDirectory` (absolute or `~/`-prefixed) relocates
the store and is read from any settings scope -- but when set in a
project's `.claude/settings.json`/`settings.local.json` it is honored
only after you accept the workspace trust dialog, the same gate that
governs hooks.

### 1.6 How it actually reaches the model

One detail worth internalizing, stated in the troubleshooting section:
"CLAUDE.md content is delivered as a **user message after the system
prompt**, not as part of the system prompt itself." If you want
system-prompt-level text you need `--append-system-prompt` on every
invocation. The interactive context-window page's own timeline puts auto
memory (`MEMORY.md`) very early in startup loading, right after the
system prompt and before environment info.

Inspection surfaces: `/context` lists what actually loaded, under a
**Memory files** heading; `/memory` lists and opens CLAUDE.md,
CLAUDE.local.md and the auto memory folder (creating a listed file that
doesn't exist yet if you select it); the `InstructionsLoaded` hook logs
exactly which instruction files loaded, when, and why. "Saved 2
memories" / "Recalled 2 memories" in the UI are auto memory writes and
reads.

### 1.7 Compaction interaction -- the load-bearing table

```mermaid
stateDiagram-v2
    state "Before compaction" as Before
    state "After compaction" as After
    Before --> After: auto-compact or /compact fires

    state After {
        [*] --> Reinjected: "root CLAUDE.md, unscoped rules,<br/>auto memory -- re-read from disk"
        [*] --> Lost: "paths:-scoped rules, nested CLAUDE.md --<br/>lost until a matching file is read again"
        [*] --> Capped: "invoked skill bodies --<br/>5,000 tok/skill, 25,000 total, oldest dropped first"
        [*] --> Unchanged: "system prompt, output style --<br/>not part of message history"
    }
```

From the context-window page, verbatim in substance:

| Mechanism | After compaction |
|---|---|
| System prompt and output style | Unchanged; not part of message history |
| Project-root CLAUDE.md and unscoped rules | Re-injected from disk |
| Auto memory | Re-injected from disk |
| Rules with `paths:` frontmatter | Lost until a matching file is read again |
| Nested CLAUDE.md in subdirectories | Lost until a file in that subdirectory is read again |
| Invoked skill bodies | Re-injected, capped at 5,000 tokens per skill and 25,000 total; oldest dropped first |
| Hooks | Not applicable; hooks run as code, not context |

So the persistence guarantee is asymmetric by *tier*, not by file
format: the launch-loaded tier (project-root CLAUDE.md, unscoped rules,
`MEMORY.md`) is re-read from disk after each compaction; the on-demand
tier (path-scoped rules, nested CLAUDE.md) is summarized away with
everything else and only comes back when its trigger file is read
again. The documented remedy for a rule that must survive is to drop
`paths:` or move it to the project-root CLAUDE.md.

Skill-body truncation "keeps the start of the file," which is a real
authoring constraint: put the most important instructions near the top
of `SKILL.md`.

On the compaction mechanism itself: "It clears older tool outputs
first, then summarizes the conversation if needed. Your requests and key
code snippets are preserved; detailed instructions from early in the
conversation may be lost." You can steer it with a "Compact
Instructions" section in CLAUDE.md or `/compact focus on ...`. As of
v2.1.198 the summarization request inherits the session's extended
thinking configuration. There is a documented anti-thrash guard: after
context refills immediately following three consecutive compactions,
auto-compaction stops with an actionable error rather than looping
(CHANGELOG). A `PreCompact` hook exists and can *block* compaction by
exiting 2 or returning `{"decision":"block"}` (CHANGELOG).

*BEST CURRENT UNDERSTANDING, UNCONFIRMED:* the two-phase behavior
(evict old tool outputs, then summarize) is what the community calls
"microcompaction." The term does not appear in the Claude Code docs
pages fetched here nor anywhere in `CHANGELOG.md` (grepped this
session), so treat the *name* as unofficial while the *behavior* is
verified. Likewise, no exact auto-compaction trigger percentage is
documented on the pages fetched; the only percentage found is a
CHANGELOG entry "Increased auto-compact warning threshold from 60% to
80%," which is a warning threshold, not the compaction trigger.

### 1.8 Mid-session edits: is an edited CLAUDE.md re-read?

Asked directly, and researched directly (docs pages + full `CHANGELOG.md`
grep, 2026-07-30). The honest answer has a verified part and an inferred
part, and they must not be blended.

VERIFIED, and stated repeatedly across the docs: loading is a
**session-start** event. "Each Claude Code session begins with a fresh
context window"; CLAUDE.md files are "loaded into the context window at
the start of every session"; "Claude reads them at the start of every
session"; ancestor CLAUDE.md/CLAUDE.local.md are "loaded in full at
launch"; unscoped `.claude/rules/` are "loaded at launch"; `@` imports
are "expanded and loaded into context at launch." There is **no
documented file watcher, hot-reload, or automatic re-read on edit** for
the launch-loaded tier. Nothing in the memory page, the context-window
page, or the `CHANGELOG.md` (grepped for `reload`/`re-read`/`watch`/
`takes effect`/`mid-session`) describes one. `/memory` opens the file in
your editor and, as of v2.1.216, lets you keep using the session while
the editor window is open -- but the docs do not claim saving it changes
the running session's context.

Three documented paths *do* pull instruction content off disk after
launch, and they are the only levers you have without restarting:

1. **Compaction.** "Project-root CLAUDE.md survives compaction: after
   `/compact`, Claude re-reads it from disk and re-injects it into the
   session." Same for unscoped rules and auto memory (the compaction
   table in 1.7).
2. **Nested CLAUDE.md in a subdirectory.** Loads when Claude reads a
   file in that subdirectory, and reloads the next time it does after a
   compaction. A CHANGELOG entry ("Fixed nested CLAUDE.md files being
   re-injected dozens of times in long sessions that read many files")
   confirms this path fires repeatedly within one session, not once.
3. **Path-scoped rules (`paths:` frontmatter).** Load when a matching
   file is read -- "not on every tool use."

*BEST CURRENT UNDERSTANDING, UNCONFIRMED:* because the docs say
compaction "re-reads it from disk," an edit you made earlier in the
session should appear in its post-compaction form -- i.e. `/compact` is
in practice a manual reload for root CLAUDE.md. The docs never state
this consequence explicitly (they discuss re-reading in the context of
*persistence*, not of *picking up edits*), so treat it as reasoned, not
documented. Likewise UNCONFIRMED: whether a nested CLAUDE.md re-injected
mid-session on a later file read reflects edits made since it first
loaded.

The practical upshot, and the part worth remembering: **for the
launch-loaded tier, edit-then-restart (or `--continue`, which reopens the
session and re-runs startup loading) is the only documented way to be
sure the model sees your change.** `/context` under **Memory files**, and
the `InstructionsLoaded` hook (fires "when CLAUDE.md or
`.claude/rules/*.md` files are loaded into context," CHANGELOG) are how
you verify what a given session actually holds rather than guessing.

### 1.9 Session-level persistence (distinct from memory)

Every message, tool use, and result is written to a plaintext JSONL file
under `~/.claude/projects/`, which is what powers rewind, resume, and
fork. `claude --continue` / `claude --resume` reopen the *same session
ID* and append; `--fork-session` / `/branch` copy history into a new
ID. But the docs draw the line clearly: "Sessions are independent. Each
new session starts with a fresh context window, without the
conversation history from previous sessions." Transcript persistence is
not memory -- it is only reachable by explicitly resuming.

---

## 2. GitHub Copilot CLI

Sources for this section: `docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/overview`,
`docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli`,
`docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference`,
`docs.github.com/en/copilot/concepts/agents/copilot-memory`,
`docs.github.com/en/copilot/how-tos/use-copilot-agents/copilot-memory/manage-for-yourself`,
`docs.github.com/en/copilot/concepts/response-customization`, and
`github.com/github/copilot-cli` `changelog.md` + `README.md`, all
fetched 2026-07-30. VERIFIED unless tagged otherwise.

### 2.1 Instruction files (the file-based tier)

Per the Copilot CLI docs, the CLI "automatically incorporates"
instructions from:

- `.github/copilot-instructions.md` -- repository-wide
- `.github/instructions/**/*.instructions.md` -- path-specific
- `AGENTS.md` -- agent instructions

Two further facts come from the repo's own `changelog.md` (authoritative
for its behavior-change history):

- **Copilot CLI reads `CLAUDE.md` too.** Two independent entries confirm
  it: "Expand @-style imports in AGENTS.md, CLAUDE.md, and Copilot
  instruction files," and "Avoid sending duplicate custom instruction
  files (e.g. copilot-instructions.md and CLAUDE.md with identical
  content) to reduce wasted tokens per turn." So `@`-import expansion
  exists on this harness as well, across all three families.
- **User-level instructions exist outside the repo**:
  "Support `~/.copilot/instructions/*.instructions.md` files for
  user-level instructions across all repositories," and a later entry
  noting `/help` lists `$HOME/.copilot/instructions/**/*.instructions.md`
  among user-level instruction locations.

One context-cost detail from the changelog: "Pattern-specific
instruction files (`.github/instructions/*.instructions.md`) no longer
include their full body in the system prompt on every session" --
i.e. path-specific instruction bodies became lazy rather than always-on,
mirroring (independently) Claude Code's path-scoped-rules design.

`/instructions` views and toggles the loaded instruction files;
`/init` initializes custom instructions and agentic features.

**Precedence caveat (grounding boundary).** `docs.github.com`'s
response-customization page gives a combined-not-overridden precedence
order (personal > path-specific > repository-wide > agent instructions >
organization instructions) but that page enumerates GitHub.com, VS Code,
Visual Studio, JetBrains, Xcode and Eclipse and **does not mention
Copilot CLI at all**. So: instructions are combined rather than
overridden on the surfaces that page covers -- VERIFIED for those; that
the CLI applies the identical ordering is BEST CURRENT UNDERSTANDING,
UNCONFIRMED. I did not find a CLI-specific precedence statement.

### 2.2 Copilot Memory: a real, server-side memory service

```mermaid
sequenceDiagram
    participant Svc as Copilot Memory service
    participant CLI as Copilot CLI
    participant M as Model

    Svc-->>CLI: repo-level facts + user-level preferences (session start, refreshed every 30 min)
    CLI->>M: injected into the prompt
    M->>CLI: store_memory(fact, scope)
    CLI->>M: permission prompt, showing scope (user, or owner/repo)
    M->>Svc: write fact/preference, on approval
    Svc-->>CLI: citation validated against the current branch on later use
    M->>CLI: vote_memory(relevance), throttled per response/interaction
    Note over Svc: unused fact or preference auto-deleted after 28 days;<br/>successful validated use resets the timer
```

This is the genuine architectural difference. Per
`docs.github.com/en/copilot/concepts/agents/copilot-memory` (public
preview at time of fetch): "Copilot Memory helps Copilot become more
effective over time by remembering facts about your repositories and
your personal coding preferences."

Two memory types:

- **Repository-level facts** -- coding conventions, architectural
  decisions, build commands, project-specific rules. Created only in
  response to actions by users **with write access** who have Memory
  enabled. Stored with the repository; available to any user with
  Memory access to that repo; usable only in operations on that same
  repo. Facts carry **citations** to supporting code, and Copilot
  validates citations against the current branch before using a fact.
- **User-level preferences** -- stated or implied personal preferences,
  created only from that user's own interactions and available only in
  that user's later interactions. Citations may include direct user
  quotes. On Business/Enterprise plans the preferences are owned by the
  billing entity.

Other verified properties:

- **Surfaces:** "Copilot Memory is currently used by Copilot cloud
  agent, Copilot code review, and Copilot CLI." Copilot CLI applies
  repository-level facts plus the initiating user's user-level
  preferences. (Code review uses repo facts only.)
- **Retention:** any stored fact or preference that goes unused is
  automatically deleted after **28 days**; successful validation-and-use
  resets the timer.
- **Enablement is per user, not per repository.** Individual plans:
  on by default. Enterprise/org plans: admin must enable it before users
  can opt out. Management UI is profile picture → Copilot settings →
  Features → Copilot Memory (Enabled/Disabled); repository owners
  review and delete repo-level facts under repository Settings →
  Copilot → Memory.
- **Explicitly positioned against instruction files:** the docs frame
  Memory as reducing the "regular, manual maintenance" that custom
  instruction files require, letting Copilot "build its own knowledge."

The CLI-side surface, from `github/copilot-cli` `changelog.md`:

- `/memory on|off|show` -- "enable, disable, or view memory status
  (persistent)" (v1.0.49, 2026-05-18). `/memory show` also surfaces
  documentation links.
- **Model-facing tools**: "Inject repo memories in the prompt and add
  memory storage tool to remember facts across sessions" (v0.0.382 era,
  2026-01-14) -- this is the origin entry, and it names both halves of
  the mechanism: injection at prompt-build time, plus a tool for
  writing. Later entries name the tools directly: "The `store_memory`
  tool is only included when memory is enabled for the user," and
  "`vote_memory` tool calls are throttled per response and per
  interaction to prevent runaway voting bursts." A `vote_memory` tool
  implies a relevance/quality feedback loop on retrieved memories.
- **Permission-gated writes with visible scope**: "Memory tool
  confirmation prompt now shows the scope (repository or user) when
  requesting permission to store a memory," and "Memory permission
  prompts now name who can see a stored memory: user scope or the
  specific `owner/repo` for repository scope. Timeline entries also show
  the scope (`(for user)` / `(shared with repository collaborators)`)."
  Storage is a consented, per-write action, not silent.
- **Timeline visibility**: "Memory storage shows subject, fact, and
  citations in timeline."
- **Backend-dependency failure modes** (further evidence this is a
  service, not a file): "Agent no longer hangs on the first turn when
  the memory backend is unavailable"; "Show warning when repository
  memory fails to load"; "Memory loading no longer warns when outside a
  Git repository"; "Memory storage errors now indicate when repository
  doesn't exist or you lack write access"; "Memory storage correctly
  limits available scopes when no repository context is present."
- **Mid-session refresh**: "Refresh memory context after 30 minutes in
  long-lived sessions." Injection is therefore not purely a
  session-start event on this harness -- it re-hydrates on a timer.
- **Cross-session recall as a separate, experimental feature**: "Add
  cross-session memory: ask about past work, files, and PRs across
  sessions (experimental)" -- i.e. queryable history distinct from
  Copilot Memory's fact/preference store. Related: `/chronicle search`
  "search all session content by keyword or topic."
- SDK-level control: "Allow SDK clients to configure session memory
  through `session.create` and `session.resume`."

### 2.3 Session persistence and resume

`--resume` (or `/resume`) opens a session picker; `--continue` "quickly
resume[s] the most recently closed local session" -- "pick up right
where you left off, with the saved context." `--continue` and
`--resume` are mutually exclusive ("Reject `--continue` when used with
`--resume`", changelog). `--session-id` addresses a specific session;
`/session id` prints and copies the current one.

Config and state live under `~/.copilot/`, relocatable with
`COPILOT_HOME`. Sessions are stored in **session databases** -- the
changelog repeatedly says so ("Improve CLI responsiveness when reading
and writing session databases", "session SQL", "Recover corrupted
session history on load", "Store CLI settings and session state more
reliably"), which is a different storage model from Claude Code's
plaintext JSONL transcripts. The precise on-disk filename/schema is
**not** documented on the pages fetched -- BEST CURRENT UNDERSTANDING,
UNCONFIRMED that it is SQLite specifically, though "session SQL" points
that way. Sessions are also "tied to their working directory across
prompts, restarts, and workspace tools," and the sidebar can restore
remembered sessions across restarts.

### 2.4 Compaction on Copilot CLI

VERIFIED from the CLI docs: the CLI "automatically compresses your
history in the background when your conversation approaches **95% of
the token limit**"; `/compact` compresses manually; `/context` shows a
visual token-usage overview; `/usage` reports credits, duration, lines
edited, and a token breakdown.

From `changelog.md`, the mechanism has more shape than the docs page
gives:

- "Add auto-compaction at 95% token limit and `/compact` command" --
  the origin entry, matching the docs number exactly.
- "Auto-compaction runs in background without blocking the
  conversation" and "Enable infinite sessions with automatic
  long-running context management through **compaction checkpoints**."
  Compaction produces checkpoints with viewable summaries ("Compaction
  messages show clearer command hints to view checkpoint summaries").
- `/compact` "accepts optional focus instructions to shape the
  compaction summary" -- functionally the same affordance as Claude
  Code's `/compact focus on ...`.
- What survives, as far as the changelog states it: "**Skills remain
  effective after conversation history is compacted**" and "Preserve
  extended thinking after compaction." What is deliberately dropped:
  "Reduced memory growth in long sessions by evicting transient events
  after compaction."
- A **`preCompact` hook** exists ("Add preCompact hook to run commands
  before context compaction starts"). *UNCONFIRMED* whether it can
  block compaction the way Claude Code's `PreCompact` can -- no
  changelog or docs statement found either way.
- Context-window tiering interacts with compaction: "Context window
  tier selection (default ~200K vs 1M tokens) is now enforced
  end-to-end, so picking a tier actually constrains compaction,
  truncation, and token display," and tier selection now survives
  SDK-only resume paths.
- Observability hook worth knowing for profiling work: "OpenTelemetry:
  chat spans after a successful compaction carry
  `gen_ai.conversation.compacted=true`, and the summary is emitted as a
  `CompactionPart` in `gen_ai.input.messages`." That gives a
  machine-checkable compaction marker in exported traces.

### 2.5 Mid-session edits on Copilot CLI

Researched the same way (docs pages + full `changelog.md` grep,
2026-07-30). **Not found:** any statement that editing an instruction
file mid-session is or isn't picked up, and no file-watcher/hot-reload
entry for instruction files. The changelog *does* carry explicit reload
primitives for other subsystems -- `/mcp reload`, `/lsp reload`, "Reload
installed plugin extensions without restarting a session" -- and
conspicuously no instruction-file equivalent, which is a weak negative
signal rather than a fact.

Two nearby verified datapoints, neither of which answers the question:
`/instructions` "view and toggle custom instruction files" (so which
files are active is mutable in-session, per the changelog entry adding
the command), and the token-saving entry "Avoid sending duplicate custom
instruction files (e.g. `copilot-instructions.md` and `CLAUDE.md` with
identical content) to reduce wasted tokens **per turn**."

*BEST CURRENT UNDERSTANDING, UNCONFIRMED:* that "per turn" phrasing, plus
the 30-minute memory-context refresh (2.2), hints that Copilot CLI
assembles its prompt per turn rather than freezing instruction text at
launch -- which would make edits visible sooner than on Claude Code. That
is an inference from an incidental word in a changelog entry about
deduplication, not a documented reload guarantee. Do not rely on it.

**Not found:** any statement that Copilot CLI re-injects instruction
files from disk after compaction, the way Claude Code documents for
project-root CLAUDE.md and auto memory. The nearest datapoints are the
skills-survive-compaction entry and the 30-minute memory-context
refresh. Whether `.github/copilot-instructions.md` / `AGENTS.md` bodies
are re-read post-compaction is **UNKNOWN** -- do not assume symmetry
with Claude Code here.

---

## 3. Synthesis

| Dimension | Claude Code | Copilot CLI |
|---|---|---|
| Human-authored persistent instructions | `CLAUDE.md` hierarchy (managed → user → project → local), `.claude/rules/` | `.github/copilot-instructions.md`, `.github/instructions/**/*.instructions.md`, `AGENTS.md`, `~/.copilot/instructions/**/*.instructions.md` |
| Reads the *other* harness's file? | No -- `AGENTS.md` not read at runtime; `/init` only mines it at authoring time | Yes -- `CLAUDE.md` is read and `@`-import-expanded (changelog) |
| Path-scoped instruction tier | `.claude/rules/` with `paths:` frontmatter | `.github/instructions/**/*.instructions.md` (bodies no longer always in system prompt) |
| `@`-import expansion | Yes, 4-hop cap, launch-time | Yes (changelog: AGENTS.md, CLAUDE.md, Copilot instruction files) |
| Agent-authored memory | Auto memory: local markdown at `~/.claude/projects/<project>/memory/`, `MEMORY.md` index (200 lines / 25KB) + on-demand topic files | Copilot Memory: **server-side**, repo-level facts + user-level preferences, citation-validated, 28-day unused-expiry |
| Written how | Ordinary file tools; no dedicated memory tool | Dedicated model-facing tools `store_memory` / `vote_memory`, permission-prompted per write, scope shown |
| Memory sharing | Machine-local; shared across worktrees of one repo; never across machines | Repo facts shared with repo collaborators; user prefs private to the user/billing entity; server-side so cross-machine by construction |
| Enable/disable | `autoMemoryEnabled`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, `/memory` toggle | `/memory on\|off\|show`, GitHub Copilot settings (per user; admin gate on Enterprise) |
| Injection timing | Session start (system prompt then a *user message* carrying CLAUDE.md; `MEMORY.md` early in startup) | Session start prompt injection, **plus refresh after 30 minutes** in long-lived sessions |
| Mid-session re-read of an *edited* instruction file | No documented watcher/hot-reload; launch-loaded tier is a session-start read. Off-disk re-reads happen only at compaction (root CLAUDE.md, unscoped rules, auto memory) and on trigger-file reads (nested CLAUDE.md, `paths:` rules). Restart or `--continue` is the sure path | Undocumented either way; reload primitives exist for MCP/LSP/plugins but not instruction files. `/instructions` can toggle which files are active in-session |
| Auto-compaction trigger | Documented behaviorally (evict tool outputs, then summarize); no % on fetched pages | **95% of token limit**, background, non-blocking |
| Focused manual compaction | `/compact focus on ...`, plus "Compact Instructions" section in CLAUDE.md | `/compact [FOCUS-INSTRUCTIONS]` |
| Post-compaction re-injection | Documented per-mechanism table (root CLAUDE.md + auto memory re-injected; path-scoped rules and nested CLAUDE.md lost until retriggered; skill bodies capped 5K/25K) | Skills survive; instruction-file re-injection **undocumented** |
| Pre-compaction hook | `PreCompact`, can block (exit 2 / `{"decision":"block"}`) | `preCompact` exists; blocking capability unconfirmed |
| Session transcripts | Plaintext JSONL under `~/.claude/projects/` | Session databases under `~/.copilot/` (`COPILOT_HOME`); "session SQL" |
| Resume / continue | `claude --continue`, `--resume`, `--fork-session` / `/branch` | `--continue`, `--resume` / `/resume` (mutually exclusive), `--session-id` |

**The design lesson.** Both harnesses converge on the same *two-tier*
shape -- a small always-loaded index plus a larger lazily-read body --
but diverge completely on where the agent-authored tier lives. Claude
Code keeps it as plain files you own, on your machine, auditable with a
text editor and invisible to your teammates; Copilot puts it in a
GitHub-hosted store with repository scoping, write-access gating,
citation validation against the current branch, and automatic expiry.
That is a governance/reviewability tradeoff, not a feature-count one:
Claude Code's model can be inspected and diffed but never shared;
Copilot's is shared and centrally deletable but not a file you can grep.

**Consequences for anything that must work on both** (directly
relevant to this project's cross-harness requirement):

1. Do not build on "the agent will remember" as a cross-harness
   primitive. The only mechanism with a verified equivalent on both
   sides is **repo instruction files**, and even there the filenames
   differ (Copilot CLI reads `CLAUDE.md`; Claude Code does not read
   `AGENTS.md` or `copilot-instructions.md` at runtime). A single
   `CLAUDE.md` is, per current verified behavior, the *only* one file
   both harnesses read at runtime -- an accident of Copilot CLI's
   compatibility work, not a standard.
2. Anything that must survive a long run should be in the
   always-loaded tier, not conversation. On Claude Code that means
   project-root `CLAUDE.md` or an unscoped rule (both re-injected after
   compaction); path-scoped rules and nested CLAUDE.md are explicitly
   *not* re-injected. On Copilot CLI the equivalent guarantee is not
   documented -- assume conversation-only state is lost at 95%.
3. Instrumentation asymmetry for profiling compaction: Copilot CLI
   emits a machine-checkable OTel marker
   (`gen_ai.conversation.compacted=true` plus a `CompactionPart`);
   Claude Code's documented equivalents are UI/`/context` surfaces and
   the `InstructionsLoaded` hook for load-time visibility. If you need
   a deterministic "did this run compact?" signal, the two harnesses
   need different probes.

---

## Sources

All fetched 2026-07-30.

**Claude Code (authoritative for Claude Code's documented behavior only):**
- `https://code.claude.com/docs/en/memory` -- CLAUDE.md hierarchy, load order, imports, AGENTS.md non-support, `.claude/rules/`, auto memory storage/limits/settings, `/memory`, compaction troubleshooting.
- `https://code.claude.com/docs/en/context-window` -- startup load order timeline, "What survives compaction" table, `/compact` guidance.
- `https://code.claude.com/docs/en/how-claude-code-works` -- "When context fills up", session JSONL storage under `~/.claude/projects/`, resume/fork semantics.
- `https://github.com/anthropics/claude-code` `CHANGELOG.md` (via `gh api repos/anthropics/claude-code/contents/CHANGELOG.md`) -- memory-index error and reminder entries, `autoMemoryDirectory`, worktree sharing, `PreCompact` blocking, autocompact thrash guard, 60%→80% warning threshold. Authoritative for its own behavior-change history; this repo ships no implementation source.

**GitHub Copilot CLI (authoritative for Copilot CLI's documented behavior only):**
- `https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/overview` and `https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli` -- instruction files read by the CLI, `--resume`/`--continue`/`/resume`, 95% auto-compaction, `/compact`, `/context`, `/usage`.
- `https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference` -- slash-command list, `COPILOT_HOME`, `~/.copilot/` config location, session-picker shortcuts.
- `https://docs.github.com/en/copilot/concepts/agents/copilot-memory` -- what Copilot Memory is, repo facts vs. user preferences, citation validation, supported surfaces incl. Copilot CLI, 28-day expiry, per-user enablement, contrast with instruction files.
- `https://docs.github.com/en/copilot/how-tos/use-copilot-agents/copilot-memory/manage-for-yourself` -- enable/disable path in Copilot settings, viewing/deleting repo facts and user preferences.
- `https://docs.github.com/en/copilot/concepts/response-customization` -- instruction-file precedence, explicitly for the GitHub website and IDE surfaces it enumerates; **does not cover Copilot CLI**.
- `https://github.com/github/copilot-cli` `changelog.md` and `README.md` (via `gh api repos/github/copilot-cli/contents/...`) -- `/memory on|off|show`, `store_memory`/`vote_memory`, permission-prompt scoping, timeline citations, memory-backend failure modes, 30-minute memory refresh, cross-session memory (experimental), `CLAUDE.md` reading and `@`-import expansion, `~/.copilot/instructions/`, compaction checkpoints, `preCompact` hook, OTel compaction attributes, session databases. Authoritative for its own behavior-change history; this repo ships no implementation source.
