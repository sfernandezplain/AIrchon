# CAG/RAG Corpus-Read Discipline — Genesis Handoff Packet

*Packet date: 2026-09-14 (revised: same day, MCP-server-in-venv
architecture per operator decision; 2026-09-14 airchon-mentor plan
review fixes applied)
Authoring model: plainconcepts/qwen-3-8-27b
Reviewer model: airchon-mentor (2026-09-14, verdict: structurally
sound, two rule-fixes mandatory, both applied)
Status: IMPLEMENTED 2026-09-14 (all 13 todos shipped; see the
2026-09-14 `CHANGELOG.md` entry. Deviations from design, measured:
(1) corpus is ~1.07M approx tokens, not the pre-design ~766K
estimate — snapshot in the rule file re-based to live numbers;
(2) small-area floor set at ~40K (not ~20K) per live measurement —
see 2f; (3) fastembed 0.8.0's model ID is
`sentence-transformers/all-MiniLM-L6-v2` (the `BAAI/` spelling is
rejected by this version); (4) model cache lands in
`%LOCALAPPDATA%\Temp\fastembed_cache` on this operator machine, not
next to the DB; (5) Copilot CLI workspace-scope MCP confirmed via
`copilot mcp list` — no degradation needed on any target)
Cost stance: frugal; no cap declared
Deployment targets: claude, copilot, opencode (per `apm.yml`)*

## 1. Problem Statement

The three research agents — `airchon-mentor`, `airchon-teacher`, and
`airchon-author` — currently read `references/**` pages without a
disciplined read strategy. The wiki book has grown to 89 pages /
~1.07M tokens (measured 2026-09-14 via `corpus_stats.py`:
`references/harnesses/` ~918K/36, `references/sdlc/` ~61K/21,
`references/inference-engines/` ~34K/15, `references/rag/` ~33K/11,
`references/models/` ~20K/6 — the pre-design estimate of ~766K/665K
was stale; the live numbers are what the rule snapshot carries).
Reading whole pages
or whole directories without a ratio-based decision burns context
tokens and, more importantly, pushes long conversations (teacher's
40-question exam, multi-session course delivery) into compaction
faster, which destroys the exact grounding the agents need to cite.

A zero-dependency heading index (`references-index.md`) already
solves the "which page?" search problem, but the agents' persona
files do not enforce a reading discipline against it, there is no
semantic (not just keyword/heading) retrieval path, and there is no
mechanical bridge to measure the corpus they are being asked to be
disciplined about. The plan closes all three gaps and does it
without adding a new dispatchable primitive, changing any agent's
model binding or tool list, or loosening the `airchon-author`
write-boundary.

## 2. Design Overview (Steps 1-5)

### 2a — Step 1: Interface Contract

The discipline is delivered as a **shared RULE asset** plus **two
small bridges**:

1. `resources/corpus-read-discipline.md` — the canonical RULE the
   three agents Read on qualifying triggers (mentor: before answering
   a corpus-referencing question; teacher: before Step 2 of the
   classification flow; author: before any reference-area write).
   The rule text itself (7 rules, below) is the contract; the file
   carries the per-area token snapshot at the top as a living,
   operator-readable baseline.
2. `resources/scripts/corpus_stats.py` — a stdlib-only script that
   prints per-area page count, byte count, and an approximate token
   count (bytes/4, documented as an approximation) for every
   `references/*` dir. The rule's "ceiling check" steps call it; it
   is also the source of the per-area snapshot the rule file carries.
3. `resources/scripts/rag_mcp_server.py` — a **minimal
   stdio-over-JSON-RPC MCP server** (hand-rolled, stdlib JSON-RPC
   layer, no `mcp` package dependency) that exposes two tools:
     - `vector_search(query, top_k=5)` — embeds `query` with a local
       ONNX embedding model and returns cosine top-k sections as a
       JSON array: `{page_path, section, score, snippet}`.
     - `rebuild_index()` — rebuilds the vector DB from
       `references/**` (idempotent; the author calls it after
       writes; safe to call at any time — it touches no source
       file).
   **Runs only from a dedicated Python venv** at
   `resources/scripts/.venv` (gitignored): fastembed is installed
   there, never in the operator's global environment. A `build` /
   `query TEXT` subcommand lives in the same file so the index can
   be built and tested directly from a shell without going through
   MCP.
4. **Per-harness MCP registration, operator-local and gitignored**:
   Claude Code via project-level `.mcp.json` (already in
   `.gitignore`), OpenCode via `.opencode/opencode.json`
   (directory already gitignored), Copilot CLI verified live during
   implementation (its MCP config location is confirmed at Step 10;
   if Copilot CLI has no project-local MCP registration, that target
   runs on the heading-index fallback only — acceptable degradation,
   documented).

   No new **dispatchable** primitive (no agent, no skill, no router
   change): an in-venv MCP server is tooling the agents' existing
   harnesses surface to them, not a new APM target.

**No changes to:** `apm.yml` targets/dependencies, any agent's
frontmatter `model` or `tools` (mentor/teacher remain structurally
read-only on `references/**` — the only writer is still
`airchon-author`), grounding-tag discipline, deployed-copy
conventions, or the router skill's classification.

### 2b — Step 2a: Read Path (primary — the hot loop)

```
graph TD
    Q[Question] --> VQ[vector_search MCP tool]
    VQ --> V1[Top-K sections]
    V1 --> SMR{Sufficient with metadata + snippets?}
    SMR -->|Yes| ANS[Answer from context]
    SMR -->|No| R[Read only the listed sections]
    R --> ANS
    VQ -->|MCP unavailable| H[Index RAG fallback via references-index.md]
    H --> R
```

10 nodes. The loop the agent runs on every corpus-referencing
question:

1. **Retrieve via the `vector_search` MCP tool** (semantic, per-
   section, ~zero latency at query time — embeddings are precomputed
   and local). **Fallback:** if the tool is unavailable (MCP not
   registered in this harness, venv missing, or server error), fall
   back to the existing heading index (`references-index.md`) and
   its per-page TOCs. The fallback is always available because it
   is pure static markdown with zero dependencies.
2. **Ratio rule (CAG vs. RAG):** per the reference areas' own
   guidance, use the CAG-lean default — answer from metadata +
   snippets when sufficient; else read. Scale the decision to
   corpus size: **small-area floor** — any area under ~40K tokens
   (at the 2026-09-14 measurement: `references/models/` ~20K/6,
   `references/rag/` ~33K/11, `references/inference-engines/`
   ~34K/15) is always CAG: the
   read-vs-verify ratio there is so favorable that skipping the
   ratio decision and just reading on doubt is cheaper than the
   ceremony. **Large areas** (`harnesses/` ~918K/36 pages) apply the
   ratio strictly: metadata + snippets first, read only the
   specific sections the ratio says it needs. The ratio is
   qualitative — "does the question require a claim the snippet
   does not already carry" — not a number the agent computes.
3. **Ceiling check** (via `corpus_stats.py`): only when the
   per-area snapshot in the rule file is stale or the agent doubts
   it (e.g. a recent large write), re-run the stats bridge to re-
   measure before committing to a whole-area read.
4. **Section-scoped reads for large pages:** when a read is
   required and the target page is large, read the specific
   section by line range (the heading index and the vector result
   both name sections) rather than the whole page.
5. **Never re-read within a session — unless compacted away:** a
   section already in context is reused, not re-read. **Compaction
   caveat (per airchon-mentor review):** long sessions (e.g. the
   teacher's 40-question exam) may push earlier tool outputs out
   via context compression; a re-read *after* compaction is a
   fresh read, not a duplicate, and is necessary — VERIFIED
   citations require the source text to be in context at citation
   time.
6. **Preferred read order (cross-session lever only):** read
   index/overview pages before detail pages so the stable prefix
   (agent body + rule asset + index) is shared across questions.
   **Framing fix (per airchon-mentor review):** this is a
   cross-session TTL-gated best-effort ordering, NOT a within-
   session cache lever — the within-session benefit comes entirely
   from the automatic breakpoint advancing with each new entry,
   which is independent of read order.
7. **Grounding unchanged:** vector search surfaces locations; it is
   a retrieval aid, not a truth authority. The agent still Reads
   the section for any verbatim claim and still attaches grounding
   tags. A snippet that *seems* to answer but the section doesn't
   confirm is treated as no-answer, per existing discipline.

### 2c — Step 2b: Write Path

Unchanged: `airchon-author` is the sole writer of `references/**`.
One addition: after authoring/updating a reference page, the author
runs the vector rebuild (via the `rebuild_index` MCP tool, or
`python rag_mcp_server.py build`) so the semantic index tracks the
new content. The header of the rule asset notes the rebuild
obligation so the author's "after you write" step includes it.

### 2d — Step 2c: State Flow

No new state files for the agents. What *does* get added:
- `resources/vector-index.db` — generated SQLite DB (gitignored),
  rebuilt by the script. Not agent state; a build artifact like
  `references-index.md`.
- `resources/scripts/.venv/` — the Python venv (gitignored) holding
  fastembed + ONNX runtime. Model weights cache to the operator's
  user profile (fastembed's default cache), outside the repo.
- Per-harness MCP registration entries (`.mcp.json`,
  `.opencode/opencode.json`) — operator-local, all already
  gitignored.

### 2e — Step 3: Cost Stance + Frugal Route Decision

**Stance: frugal.** No cap declared.

**Frugal route:**

| Step | Model | Why |
|------|-------|-----|
| Design (this packet) | same session model (Qwen3.8-27B) | operator's choice; no separate design model in scope |
| Plan review | airchon-mentor (its configured model) | read-only structural review; already done 2026-09-14, verdict + fixes incorporated |
| Implementation | caller thread / default | prose-file edits + one small stdlib script + one small MCP server; no novel logic |
| Verification | caller thread | running two scripts, `apm install`, a registration check, and a test query |

**Model binding:** no agent changes its bound model. The only
model in this entire design is the **embedding model**
(`sentence-transformers/all-MiniLM-L6-v2`, 384-dim, ~130MB, ONNX via fastembed) —
it runs locally, never a per-query network cost, and is cached
after first download. It is an infrastructure dependency, not an
agent model.

**Cost projection (implementation, one-time):** *measured at ship
2026-09-14 -- the estimates in parentheses were the pre-implementation
projection.*

- venv bootstrap: one `python -m venv` + one `pip install fastembed`
  (pulled onnxruntime + tokenizers + huggingface_hub + numpy into
  the venv only) + one ~130MB model download to the user-profile
  cache. Operator-time; zero token cost. *Measured: fastembed 0.8.0,
  27 packages into `.venv`; model fetched in ~3s, first embedding
  6.0s including model load.*
- `corpus_stats.py` + first index build: a few lines of script
  each. *Measured: corpus_stats.py ~60 lines; rag_mcp_server.py
  ~300 lines (largest artifact, stdlib JSON-RPC + fastembed glue);
  first build 1,529 sections / 84 pages in 19.7s.*
- Per-harness MCP config: 20-40 lines total across
  `.mcp.json` / `.opencode/opencode.json`. *Shipped: 8-line
  `.mcp.json` + 9-line `.opencode/opencode.json`.*
- Agent-file edits: 4 persona files + 1 flow file + 1 maintenance
  doc, ~15 lines total of actual rule text added across them.
- Query-time cost: **zero tokens** for retrieval (local ONNX,
  sub-second for ~1.5K precomputed chunks); embedding a single
  query is local, sub-second. *Measured: 3 real corpus questions
  answered in <1s each after model warm-up, top hits
  0.46-0.65 cosine.*
- Rebuild cost: ~1.5K small chunks re-embedded locally per rebuild —
  *measured: ~20s, no tokens, no network after first download.*

**Token-cost projection (recurring, per corpus-referencing
question):** unchanged in shape from the CAG/RAG design — a
`vector_search` tool call (tens of tokens: query in, top-K JSON
out, ~5 entries × ~40 tokens ≈ 200-400 tokens) replaces a whole-
page or whole-area read (1-40K+ tokens per page/area). Section-
scoped reads on top. Expected per-question retrieval cost:
~900-2,400 tokens (vector_search result ~200-400 + one section-
scoped read ~500-2,000) vs. thousands-to-tens-of-thousands for a
whole-page read today — a 5-10x reduction, not the "hundreds" the
earlier draft of this projection stated. *Corrected 2026-09-14 after
airchon-mentor grounding review.*

### 2f — Step 4: Architecture + Boundary Statement

| Artifact | Role | New/Modified |
|---|---|---|
| `resources/corpus-read-discipline.md` | shared RULE: 7 reading rules + per-area token snapshot + rebuild note | New |
| `resources/scripts/requirements.txt` | pins `fastembed` (installed only into the venv) | New |
| `resources/scripts/corpus_stats.py` | S7 stats bridge — per-area page/byte/token approx | New |
| `resources/scripts/rag_mcp_server.py` | S7 semantic-retrieval bridge — stdio MCP server (`vector_search`, `rebuild_index`) + `build`/`query` CLI subcommands | New |
| `resources/scripts/.venv/` | Python venv isolating fastembed from the operator's global Python (gitignored) | New |
| `.mcp.json` (Claude Code) | project-local MCP registration (gitignored) | New |
| `.opencode/opencode.json` (OpenCode) | MCP registration entry (dir already gitignored) | Modified if present, else new |
| `resources/vector-index.db` | generated SQLite vector DB (gitignored) | New generated artifact |
| `.gitignore` | add `.venv/` + `resources/vector-index.db` | Modified |
| `.apm/agents/airchon-mentor.agent.md` | inline: load trigger + retrieval note (vector tool, index fallback) | Modified |
| `.apm/agents/airchon-teacher.agent.md` | inline: File Map entry + load trigger (before Step 2; curriculum/tiers stay session-start eager) | Modified |
| `resources/airchon-teacher/classification-flow.md` | "Before Step 2" retrieval + curriculum/tier load order | Modified |
| `.apm/agents/airchon-author.agent.md` | inline: retrieval for grounding + post-write vector rebuild | Modified |
| `resources/references-index-maintenance.md` | add: vector-DB rebuild reminder alongside heading-index rebuild | Modified |
| `.apm/agents/airchon-communicator.agent.md` | inline: confirmatory Stage 1 index-reads-only note | Modified |

**Boundary statement (verbatim):** This design adds a shared RULE
asset, two stdlib/venv bridges (one stats script, one in-venv
stdio-MCP server with a fastembed-backed vector DB behind it), and
one rule file. It does NOT add a new dispatchable primitive: no
new agent, no new skill, no router change. It does NOT change any
agent's model binding or tool list — mentor and teacher remain
structurally read-only on `references/**`; the only writer is still
`airchon-author`. It does NOT change grounding-tag discipline,
the `~/.airchon/` state model, or deployed-copy conventions. The
rule asset is the only new "file agents must Read"; everything
else is either a script, a generated artifact, or a one-sentence
inline pointer. New dependency: `fastembed`, scoped to the venv —
never the operator's global Python. MCP registration is
operator-local (gitignored); a harness without MCP registration
degrades gracefully to the existing heading index.

### 2g — Step 5: Deployment Topology

Per-harness, operator-local, gitignored:
- **Claude Code (`.claude/` targets agents):** project-level
  `.mcp.json` registers `airchon-rag` →
  `resources/scripts/.venv/Scripts/python resources/scripts/rag_mcp_server.py`
  (relative to project root). `.mcp.json` is already gitignored in
  this repo.
- **OpenCode (`.opencode/`):** MCP entry in `.opencode/opencode.json`
  (directory already gitignored), same command/args.
- **Copilot CLI:** project-local MCP config confirmed live at
  validation; if unsupported, the three agents on Copilot use the
  heading-index fallback (rule asset names the fallback path
  explicitly). Documented either way in the rule asset's
  fallback section.

The agents themselves deploy unchanged via `apm install` (the
inline edits are body text, no frontmatter change, so no re-
registration mechanics change — but registration is still
re-verified per the repo's own authoring-gotcha discipline).

### 2h — Step 6: Rationale & Tradeoffs

- **Why a shared RULE file (not per-agent inline bodies):** the
  same 7 rules serve three agents with identical structure; a
  single canonical file means one edit changes all three, and the
  per-area token snapshot has one home. The inline pointers are
  one sentence each ("Read `resources/corpus-read-discipline.md`
  before X") so a persona file stays lean.
- **Why MCP-server-in-a-venv (revised 2026-09-14, operator
  decision):** the earlier revision invoked `build_vector_index.py`
  via Bash. A stdio MCP server is a cleaner contract — the agent
  calls a named `vector_search` tool with a JSON result instead of
  parsing CLI stdout — and it isolates the *only* third-party
  Python this project ever needs (fastembed + ONNX runtime,
  ~100MB of packages) inside `resources/scripts/.venv`, keeping
  the operator's global Python clean. Tradeoff accepted: agents
  can only use vector search if their harness has the server
  registered (operator-local, per-harness) — hence the hard
  fallback to the zero-dependency heading index, which stays the
  guaranteed floor on every harness.
- **Why vector DB *complements* (not replaces) the heading index:**
  `references-index.md` is zero-dependency, always present, and is
  the recovery path when the venv hasn't been bootstrapped, the
  model hasn't been downloaded yet, or a harness lacks MCP
  registration. The vector DB adds semantic recall ("how does
  prompt caching behave under load" → the caching section even
  when the page's headings say nothing about load) and narrows
  reads to section granularity. Per-section chunking (## / ###)
  aligns the retrieval unit with the read unit the rule already
  prescribes.
- **Why frugal and no cap:** design is prose + two small scripts +
  one small server; review is one read-only pass (already
  executed); there is no iterative debugging risk profile that
  justifies a cap. The repo has no test/evals harness, so
  verification is manual: `apm install` + registration check, two
  script runs, a query through the MCP server, and one real-task
  refinement pass.
- **Why no new dispatchable primitive:** the operator asked for a
  discipline, not a new capability surface. Adding an agent/skill
  would create a fourth APM artifact to deploy, register, and
  maintain for behavior that three existing agents can express in
  a file read.
- **Why NOT change tool boundaries:** mentor/teacher have no
  Write/Edit on `references/**` by structural design (the 2026-07-30
  split). This plan's read-side discipline must not quietly relax
  that — so the vector DB is a *read artifact* (gitignored,
  regenerable), and the write-side rebuild is the author's
  existing job plus one command.
- **Known cost of the small-area floor:** areas under ~40K CAG
  unconditionally — slightly less "disciplined" than the large
  areas, deliberately: the ratio ceremony costs more tokens there
  than a direct read would save. (Implemented with the ~40K
  threshold, not ~20K: the live measurement showed rag at ~33K and
  inference-engines at ~34K, and the rationale — ceremony costs
  more than a direct read saves — holds up to that size. The rule
  file carries the live per-area snapshot so the threshold can be
  re-tuned against re-measured numbers without another plan edit.)

### 2i — Step 7a: Handoff Compliance Findings

1. **Plan scope:** prose rules + 3 small Python artifacts (1 stdlib
   stats script, 1 in-venv MCP server, 1 shared rule file) + 6
   agent/doc inline edits + 2 gitignored config files + 1
   gitignore entry. No new dispatchable primitive, no frontmatter
   change, no model binding change.
2. **Boundary integrity:** write boundary untouched (author still
   sole writer of `references/**`; vector DB is generated and
   gitignored). Read boundary untouched (mentor/teacher tool lists
   unchanged). Grounding untouched. `~/.airchon/` untouched. New
   dependency `fastembed` is venv-scoped, not global.
3. **Tradeoff:** frugal, no cap — justified in 2f. Review
   consumed one mentor pass (15-min budget); verdict: structurally
   sound, two mandatory rule fixes (applied: compaction caveat on
   "never re-read"; "fixed read order" reframed as cross-session
   TTL-gated best-effort), plus one design refinement requested
   and applied (preloaded vector DB, delivered per 2026-09-14
   operator decision as the venv MCP architecture).
4. **Implementation risk notes for the caller:**
   - **venv bootstrap is the critical path**: `python -m venv
     resources/scripts/.venv` →
     `.venv/Scripts/python -m pip install -r
     resources/scripts/requirements.txt` → verify the model
     downloads on first `build`. If pip/network is blocked, the
     whole vector path degrades to the heading index — the design
     tolerates that, but the rule asset must say so.
   - **MCP registration is per-harness and operator-local**: each
     harness's config format differs (`.mcp.json` vs
     `.opencode/opencode.json` vs Copilot's — confirmed live); a
     wrong key lands a silently unregistered server, so validation
     is a *tool-availability* check per harness (call
     `vector_search` once) plus grep for the server name in the
     harness's server list, not an exit code.
   - **MCP server must be a minimal, correct stdio JSON-RPC**:
     implement `initialize`, `tools/list`, `tools/call`, `ping`,
     ignore notifications; a protocol bug here is invisible until
     first use — test with a direct stdin/stdout pipe, not just
     "the file exists".
   - **Rebuild must be idempotent and cheap** (~2K chunks, seconds)
     or the author will stop running it.
   - **`corpus_stats.py` token approx (bytes/4) must be labeled**
     as an approximation in output, or the rule's ceiling check
     reads as false precision.
   - **Windows paths:** the MCP command in the gitignored configs
     must use the venv's actual executable
     (`resources/scripts/.venv/Scripts/python.exe` on Windows) —
     forward slashes are fine; a bare `python` resolves to global
     Python and the server dies on `import fastembed`.
5. **SoC check:** `apm.yml` is UNCHANGED. `apm install` re-run once
   at the end. `apm.lock.yaml` should show all 3 agents + skill
   still deployed unchanged.

### 2j — Implementation Todo List (caller executes, in order)

1. Create `resources/scripts/.venv` (venv) + install
   `requirements.txt` into it + verify `all-MiniLM-L6-v2` model
   downloads and a test embedding works offline.
2. Draft `resources/corpus-read-discipline.md` (7 rules + snapshot
   placeholder + rebuild note + harness-fallback note).
3. Write `resources/scripts/corpus_stats.py`; run `--help` and a
   live run; confirm the output matches the 2026-09-14 baseline
   (89 pages, ~766K tokens) and paste that output into the rule
   file's snapshot.
4. Write `resources/scripts/rag_mcp_server.py` (JSON-RPC stdio
   layer + `vector_search`/`rebuild_index` tools +
   `build`/`query` CLI); run `build`; run a `query` test; verify
   the fallback message path (query with the DB absent).
5. Edit `.gitignore`: add `resources/scripts/.venv/` and
   `resources/vector-index.db`.
6. Register the MCP server per harness in the operator-local
   gitignored configs (`.mcp.json` for Claude Code;
   `.opencode/opencode.json` for OpenCode; Copilot CLI — confirm its
   config mechanism live; document degradation if unsupported).
7. Edit `.apm/agents/airchon-mentor.agent.md` (load trigger in
   KNOWLEDGE SOURCE; Retrieval Protocol bullet:
   `vector_search` first, heading-index fallback, section-scoped
   reads, the two review-mandated rule framings).
8. Edit `.apm/agents/airchon-teacher.agent.md` (File Map entry;
   load trigger note: rule file before Step 2; curriculum +
   proficiency-tiers stay eager at session start) and
   `resources/airchon-teacher/classification-flow.md` ("Before
   Step 2" retrieval procedure: `vector_search` → fallback →
   section-scoped read; curriculum/tier load order stated
   verbatim per the plan).
9. Edit `.apm/agents/airchon-author.agent.md` (retrieval for
   write-grounding: `vector_search` with fallback; post-write
   `rebuild_index`, or `python rag_mcp_server.py build` if MCP is
   unavailable) and `resources/references-index-maintenance.md`
   (add the vector-rebuild step after "rebuild the heading index";
   note the venv requirement and the model-download-once fact).
10. Edit `.apm/agents/airchon-communicator.agent.md` (Stage 1 note:
    index-reads-only for book-structure, per the same rule asset —
    confirmatory, one sentence).
11. Run `apm install`; verify registration via the next new-agent-
    types/skills system reminder (or explicit invocation); confirm
    `apm.lock.yaml` shows all 3 agents + skill unchanged.
12. Verify MCP registration per harness (tool-availability check:
    one `vector_search` call per harness; grep the harness's
    server list).
13. Real-task refinement: answer 2-3 actual corpus questions
    end-to-end (e.g. "how does compaction interact with prompt
    caching" — expect vector hit on compression/caching pages; one
    Copilot-fallback case), confirm section-scoped reads fire on a
    large page, and tune rule text only if a rule proved
    unactionable in practice.
14. Update this packet's cost projection with measured numbers;
    write the `CHANGELOG.md` entry (repo convention).

### 2k — Evals

No formal evals harness exists in this repo (no `node:test`, no
evals script — confirmed by the repo's own CLAUDE.md). Verification
is manual and task-shaped:

- **Registration & availability:** after `apm install`, the three
  agents + skill appear in the next harness session (per the
  authoring-gotcha discipline: clean exit code is NOT proof);
  `vector_search` is callable in each MCP-registered harness and
  the fallback is exercised on one harness without it.
- **Read-path behavior:** one corpus question answered via
  `vector_search` → section read, with no whole-area read; the
  grounding tags present; the answer names the section it read.
- **Fallback behavior:** with the MCP server unavailable (test by
  pointing the config at a missing binary, or on a harness
  unregistered), the same question answered via
  `references-index.md` TOCs only.
- **Semantic-mismatch case:** a question whose terms don't match
  any page heading (e.g. "what happens to context when the
  conversation gets too long?" — vector search surfaces
  `context-compression.md` at rank ~6, not the top hit; the returned
  section (a Hermes-specific threshold section) is not the one that
  answers the question, so the agent still needs to read multiple
  sections. The heading-index fallback does indeed fail to surface
  the page by keyword alone — the vector layer's semantic-recall
  advantage is real but smaller than top-hit accuracy; treat it as
  "finds the right page in the top-K, the agent still verifies the
  section" per rule 7's "retrieval aid, not truth authority"
  framing). *Verified live by the 2026-09-14 airchon-mentor review.*
- **Write-path behavior:** author updates one page; rebuild runs;
  a query against the new section surfaces it.
- **Compaction caveat:** in a long session (or by direct
  instruction), confirm the agent re-reads after a stated
  compaction rather than refusing to re-read.

## 3. Grounding

All CAG/RAG claims: `references/rag/cache-augmented-generation.md`
(verified against the source cited there). All vector-DB/
embedding claims: standard local-retrieval practice (fastembed
ONNX inference, cosine similarity, per-section chunking); the
specific model `sentence-transformers/all-MiniLM-L6-v2` and its 384-dim output are
its documented specs (VERIFIED — confirmed by running the build in
Step 1; model ID is in `rag_mcp_server.py` line 30, 384-dim output
confirmed in the stored embeddings). Compaction behavior:
`references/harnesses/context-compression.md`. Cache TTL/breakpoint
mechanics (for the rule 6 framing): `references/harnesses/caching.md`.
Corpus size baseline: measured live 2026-09-14
(`resources/scripts/corpus_stats.py` output, todo #3).

*DESIGN ENDS HERE. Steps 7b-8 (draft the natural-language edits,
deploy, validate) belong to the caller thread.*
