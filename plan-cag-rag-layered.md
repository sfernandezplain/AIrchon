# CAG/RAG Layered Retrieval Plan — Maximum Speed + Economics

*2026-09-14. Supersedes the retrieval section of corpus-read-discipline.md.
Measured against live file sizes (bytes/4 approximation) and the
VERIFIED prompt-caching economics documented in
references/harnesses/caching.md (0.1x cached read, 1.25x write at 5-min
TTL, 2x at 1-hour TTL, 4-breakpoint max, 20-block lookback).*

## Problem

The current discipline has a gap (confirmed by airchon-mentor
2026-09-14): agents go straight to filename-inference disk reads,
skipping both CAG (no whole-area prefix load) and RAG (no
vector_search call). Rule 1 says "vector first" but nothing actually
enforces it, and the "always CAG" label in the regime table describes
a pattern no rule prescribes. This plan fixes that with a concrete
two-layer architecture: what goes in the CAG prefix (instructions)
and what gets retrieved via RAG (the MCP tool).

## Architecture: two layers, not three

```
Layer 0 — CAG PREFIX (in instructions, loaded at session start)
          Rules + indexes + curriculum/tiers
          Cached once, read at 0.1x on every turn
          NO retrieval cost — it's already in context

Layer 1 — RAG (the airchon-rag MCP server, vector_search tool)
          Called per-question to find the right section
          Returns top-k candidates with snippets + line ranges
          Agent reads only the named section (section-scoped read)
```

There is no "Layer 2 — direct file reads by filename inference."
That was the gap. Filename inference is no longer a permitted
retrieval strategy — it was never named in the rules, and this plan
replaces it with an explicit two-layer discipline that leaves no room
for the unnamed third path.

## What goes in the CAG prefix (Layer 0)

### Tier 0 — All agents (rules + grounding)

| File | ~Tokens | Why it's CAG |
|---|---|---|
| resources/corpus-read-discipline.md | 1,187 | The rules themselves — must be in context before any retrieval decision |
| resources/grounding-discipline.md | 552 | Source authority bounds + gh fallback — must be in context before any source claim |
| **Tier 0 subtotal** | **1,739** | Loaded at session start, always cached, never retrieved |

### Tier 1 — Mentor + Author + Communicator (area indexes)

| File | ~Tokens | Why it's CAG |
|---|---|---|
| references/harnesses/index.md | 24,346 | Topic-level map of the ~918K harnesses area — the agent needs to know what pages exist before it can vector_search for the right one |
| references/sdlc/index.md | 2,078 | Same — topic-level map of the sdlc area |
| references/rag/index.md | 1,221 | Same — topic-level map of the rag area |
| references/models/index.md | 1,447 | Same — topic-level map of the models area |
| references/inference-engines/index.md | 3,128 | Same — topic-level map of the inference-engines area |
| **Tier 1 subtotal** | **32,220** | Loaded at session start, cached as prefix |
| **Mentor/Author CAG total** | **33,959** (~34K) | Tier 0 + Tier 1 |

### Tier 2 — Teacher only (curriculum + tiers)

| File | ~Tokens | Why it's CAG |
|---|---|---|
| resources/airchon-teacher/knowledge-path-curriculum.md | 26,786 | Session-critical: defines learning outcomes per tier, module list, session agenda — the teacher needs this before any question generation or retrieval |
| resources/airchon-teacher/reader-proficiency-tiers.md | 11,543 | Tier structure + descriptions — read eagerly per the existing classification-flow.md "Before Step 2" |
| **Tier 2 subtotal** | **38,329** | |
| **Teacher CAG total** | **72,288** (~72K) | Tier 0 + Tier 1 + Tier 2 |

### What does NOT go in the CAG prefix

- `resources/references-index.md` (24,065 tokens) — the heading
  index. This is the RAG-fallback path (rule 1 fallback when MCP is
  unavailable). Putting it in the CAG prefix would duplicate the
  area indexes' topic-level coverage at 3x the cost. It goes in the
  prefix ONLY when the agent knows MCP is unavailable (degradation
  mode), not by default.
- Any `references/*/*.md` topic page (2K-25K tokens each) — these
  are the RAG layer's job to find and the section-scoped read's job
  to load. CAG-loading even one topic page provisionally would burn
  cache budget without guaranteeing it's the right page.

## What gets retrieved via RAG (Layer 1)

Every corpus-referencing question, after the CAG prefix is in context:

1. **Agent formulates a query** from the user's question + the area
   indexes it already has in context (it knows what pages exist and
   what they cover — that's what the CAG prefix gives it).
2. **Call `vector_search`** with `top_k=3-5`. Returns section-level
   candidates: `{page_path, section, section_path, score, snippet, lines}`.
   Cost: ~200-400 tokens.
3. **Agent decides** from the snippets whether the top candidate's
   snippet already carries the needed claim (ratio rule). For small
   areas, the ratio is liberal — read on doubt. For harnesses (~918K),
   the ratio is strict — read only if the snippet doesn't suffice.
4. **Section-scoped read** of the winning candidate(s) by line range.
   Cost: ~500-2,000 tokens per section, vs. 2K-25K for a whole page.

### What RAG does NOT retrieve

- The rules themselves (they're in the CAG prefix already).
- The area indexes (they're in the CAG prefix already).
- The curriculum or tiers (they're in the teacher's CAG prefix already).
- The heading index (references-index.md) — it's the fallback path,
  not the primary RAG path. RAG's primary path is vector_search.

## Economics (measured)

### CAG prefix cost (write once per session, read at 0.1x per turn)

| Agent | Prefix size | Write cost (1.25x) | Per-turn cached read (0.1x) | Break-even (questions/TTL window) |
|---|---|---|---|---|
| Mentor | ~34K | ~42K | ~3.4K | 2 (pays for itself by the 2nd question) |
| Author | ~34K | ~42K | ~3.4K | 2 |
| Communicator | ~34K | ~42K | ~3.4K | 2 |
| Teacher | ~72K | ~90K | ~7.2K | 2 |

The 5-minute TTL is the binding constraint. For the mentor, a
34K prefix cached at 0.1x saves ~30K tokens per question vs. an
uncached read — the 42K write cost is recouped by the 2nd question
within the same TTL window. Beyond 2 questions in 5 minutes,
every cached read is pure savings.

For the teacher's 40-question exam (~42 calls in one session): the
72K prefix is written once (90K write cost), then read 42 times at
0.1x = 42 x 7.2K = 302K cached-read tokens, vs. 42 x 72K = 3.02M
uncached tokens. **Net saving: ~2.7M tokens per exam.** The write
cost is 0.03x of the uncached total.

### RAG retrieval cost (per question)

| Step | Cost |
|---|---|
| vector_search tool call (query in, top-k JSON out) | ~200-400 tokens |
| Section-scoped read (1-3 sections by line range) | ~500-2,000 tokens |
| **Per-question retrieval total** | ~700-2,400 tokens |

vs. the old path (whole-page read): 2K-25K tokens per page.
vs. the old old path (whole-area read): up to 918K tokens.
**5-100x reduction per question, depending on the page.**

### Combined per-question cost

CAG prefix cached read + RAG retrieval:

| Agent | CAG read (0.1x) | RAG retrieval | Total per question |
|---|---|---|---|
| Mentor | ~3.4K | ~700-2.4K | ~4.1K-5.8K |
| Teacher | ~7.2K | ~700-2.4K | ~7.9K-9.6K |

vs. today (no CAG prefix, whole-page reads): 2K-25K+ per question,
plus the implicit cost of the agent re-reading the same rule files
and indexes from disk every time (which it currently does, paying
full price each time with no caching).

## How to place the CAG prefix in instructions

### Option A: AGENTS.md (project-wide, all agents)

Place the Tier 0 + Tier 1 files as `instructions:` entries in
`opencode.json` (or the equivalent in each harness's config). This
makes them part of the session-start system prompt, cached as prefix.

```jsonc
// .opencode/opencode.json (add or merge)
{
  "instructions": [
    "resources/corpus-read-discipline.md",
    "resources/grounding-discipline.md",
    "references/harnesses/index.md",
    "references/sdlc/index.md",
    "references/rag/index.md",
    "references/models/index.md",
    "references/inference-engines/index.md"
  ]
}
```

For the teacher, add Tier 2 via the teacher agent's own frontmatter
or agent config:

```jsonc
// in opencode.json, under agent.airchon-teacher:
{
  "agent": {
    "airchon-teacher": {
      "instructions": [
        "resources/airchon-teacher/knowledge-path-curriculum.md",
        "resources/airchon-teacher/reader-proficiency-tiers.md"
      ]
    }
  }
}
```

### Option B: Per-agent frontmatter `instructions:` field

If the harness supports per-agent instruction lists (Claude Code
does via the persona body; OpenCode does via `agent.<name>` config),
place the files there. This is more precise — the mentor gets
Tiers 0+1, the teacher gets Tiers 0+1+2, the author gets Tiers 0+1,
and the communicator gets Tiers 0+1.

### Recommendation: Option A (AGENTS.md / instructions)

Simpler, one config change, and the Tier 0+1 files (~34K) are small
enough that all agents benefit from having them. The teacher's Tier 2
files (~38K) are agent-specific and go in the per-agent config.

## Rule text changes to corpus-read-discipline.md

The following fixes resolve the gap airchon-mentor identified:

### Fix 1: Rename the regime column

**Before:**
| Area | Regime |
| references/models/ | small — always CAG |

**After:**
| Area | Regime |
| references/models/ | small — read on doubt (CAG prefix covers index) |

This stops claiming "always CAG" when no whole-area load happens.
The regime now says what's actually true: the area's index is in the
CAG prefix, and topic pages are retrieved via RAG with a liberal
ratio for small areas.

### Fix 2: Add a "CAG Prefix" rule (new Rule 0, before Rule 1)

> **Rule 0 — CAG prefix (loaded at session start, not per-question).**
> The following files are loaded as a cached prefix via the harness's
> instructions mechanism (AGENTS.md / opencode.json `instructions:`
> / per-agent frontmatter), not retrieved on demand:
> - `resources/corpus-read-discipline.md` + `resources/grounding-discipline.md`
>   (rules — Tier 0, all agents)
> - All five area `index.md` files (topic maps — Tier 1, reading agents)
> - Teacher only: `knowledge-path-curriculum.md` +
>   `reader-proficiency-tiers.md` (Tier 2)
> These are your "what exists" map. They are cached once at session
> start; every subsequent turn reads them at 0.1x. Do not re-read
> them from disk — they are already in context. Do not vector_search
> for them — they are not topic pages, they are the map.

### Fix 3: Rewrite Rule 1 to reference Rule 0

**Before:**
> Retrieve, then read — vector first, heading index as fallback.

**After:**
> **Retrieve, then read — vector first, heading index as fallback.
> Rule 0's CAG prefix already gave you the topic-level map (what pages
> exist, what each covers). Now find the right section: call
> `vector_search` with the question, `top_k` 3-5. It returns
> section-level candidates. If the tool is unavailable, fall back to
> the heading index (`resources/references-index.md`) — keyword/heading
> match only. Do not skip to filename inference: you may know the file
> name already, but the vector search or heading index confirms which
> section of that file actually answers the question.**

### Fix 4: Rewrite Rule 2's small-area floor

**Before:**
> skip the ratio ceremony entirely: reading is cheap enough to just do on doubt

**After:**
> skip the ratio ceremony entirely: call `vector_search` (Rule 1
> still applies — retrieval is required for all areas), but once you
> have the top-k candidates, read any candidate that plausibly
> answers — don't spend reasoning tokens on the cost-benefit analysis.
> For small areas, the read cost is low enough that reading a
> slightly-wrong section is cheaper than the analysis to avoid it.

## Implementation todo list

1. Merge the `instructions:` entries into `.opencode/opencode.json`
   (Tier 0 + Tier 1 for all reading agents; Tier 2 for teacher via
   per-agent config).
2. Apply the four rule-text fixes to `resources/corpus-read-discipline.md`
   (rename regime column, add Rule 0, rewrite Rules 1+2).
3. Update the per-agent persona files' load-triggers to reference
   Rule 0 instead of instructing a per-question Read of the rule file
   (the rule file is now in the CAG prefix, not read on demand).
4. Restart opencode to load the new instructions and confirm the
   CAG prefix is in context (check via a test question that names a
   page without reading it, confirming the index is cached).
5. Run a real-task test: ask the mentor a corpus question and
   confirm it calls `vector_search` first (Rule 1), not a direct
   Read by filename.
6. If the mentor still skips vector_search after the prefix is live,
   strengthen the rule text ("MUST call vector_search before any
   Read of a references/*/*.md topic page" — shift from descriptive
   to prescriptive).
7. Update CHANGELOG.md.

*PLAN ENDS HERE — the caller thread implements the config changes and
rule edits, then restarts opencode to validate the CAG prefix is live.*
