# Corpus read discipline

Shared RULE for every agent that reads `references/**` (airchon-mentor,
airchon-teacher, airchon-author; airchon-communicator's Stage 1 is
confirmatory). This file is part of your CAG prefix (Rule 0) — it is
loaded at session start via the harness's `instructions:` mechanism,
not retrieved per-question. The rules below are the contract — follow
them in order, stop early when the question is answered.

## Per-area snapshot (measured 2026-09-14 via `resources/scripts/corpus_stats.py`)

| Area | Pages | Approx tokens | Regime |
|---|---|---|---|
| references/harnesses/ | 36 | ~918K | large — ratio strictly |
| references/sdlc/ | 21 | ~61K | large — ratio strictly |
| references/inference-engines/ | 15 | ~34K | small — read on doubt (CAG prefix covers index) |
| references/rag/ | 11 | ~33K | small — read on doubt (CAG prefix covers index) |
| references/models/ | 6 | ~20K | small — read on doubt (CAG prefix covers index) |

Token counts are bytes/4 approximations (labeled by the stats
script). Re-measure only when doubtful (rule 3).

## The rules

0. **CAG prefix (loaded at session start, not per-question).** The
   following files are loaded as a cached prefix via the harness's
   native rules mechanism (CLAUDE.md for Claude Code + Copilot CLI;
   `opencode.json` `instructions:` for OpenCode), not retrieved on
   demand:

   - `resources/corpus-read-discipline.md` (this file) +
     `resources/grounding-discipline.md` (rules — Tier 0, all agents)
   - All five area `index.md` files (topic maps — Tier 1, reading
     agents): `references/harnesses/index.md`, `references/sdlc/index.md`,
     `references/rag/index.md`, `references/models/index.md`,
     `references/inference-engines/index.md`
   - Teacher only: `resources/airchon-teacher/knowledge-path-curriculum.md`
     + `resources/airchon-teacher/reader-proficiency-tiers.md` (Tier 2)

   These are your "what exists" map. They are cached once at session
   start; every subsequent turn reads them at 0.1x. **Do not re-read
   them from disk — they are already in context. Do not `vector_search`
   for them — they are not topic pages, they are the map.**

1. **Retrieve, then read — vector first, heading index as fallback.**
   Rule 0's CAG prefix already gave you the topic-level map (what pages
   exist, what each covers). Now find the right section: call
   `vector_search` (the `airchon-rag` MCP server) with the question,
   `top_k` 3-5. It returns section-level candidates (`page_path`,
   `section`, `score`, `snippet`, `lines`). **If the tool is
   unavailable** (MCP not registered in this harness, venv missing,
   or server error), fall back to `resources/references-index.md`
   (page -> H2/H3 heading map) — keyword/heading match only. The
   fallback is always available: zero dependencies.

   **Do not skip to filename inference.** You may know the file name
   already from the CAG prefix's area indexes, but `vector_search` or
   the heading index confirms *which section* of that file actually
   answers the question. Skipping retrieval to read by filename is
   non-compliant with this rule, even when the outcome would be
   correct — the process exists so the non-obvious cases are caught.

2. **Ratio rule with small-area floor.** Answer from metadata +
   snippets when the question's required claim is already carried by
   them. Read only what the ratio says it needs. **Small-area
   floor:** for the regimes marked *small* above (currently
   models, rag, inference-engines — all under ~40K tokens), call
   `vector_search` (Rule 1 still applies — retrieval is required for
   all areas), but once you have the top-k candidates, read any
   candidate that plausibly answers — don't spend reasoning tokens on
   the cost-benefit analysis. For small areas, the read cost is low
   enough that reading a slightly-wrong section is cheaper than the
   analysis to avoid it. For *large* areas, the ratio is strict:
   "does the question require a claim the snippet does not already
   carry?" — qualitative, not computed.

3. **Ceiling check on doubt only.** When you are about to commit to
   a whole-area read, or the snapshot above feels stale after a
   recent write, run `python resources/scripts/corpus_stats.py` and
   re-measure before reading. Never re-measure as a routine first
   step.

4. **Section-scoped reads for large pages.** When a read is required
   and the target page is large, read the specific section (line
   range) named by the `vector_search` result or the heading index —
   not the whole page. Whole-page reads are reserved for small pages
   (under ~2K tokens) or when the question genuinely spans the page.

5. **Never re-read within a session — unless compacted away.** A
   section already in context is reused, not re-read. **Compaction
   caveat:** long sessions (e.g. the teacher's 40-question exam) may
   evict earlier tool outputs via context compression. A re-read
   *after* compaction is a fresh read, not a duplicate, and is
   necessary — a VERIFIED citation requires the source text to be in
   context at citation time.

6. **Preferred read order — cross-session lever only.** Favor
   index/overview pages before detail pages so the stable prefix
   (agent body + this file + index) is shared across questions and
   sessions. This is a cross-session, TTL-gated best-effort ordering.
   Do not treat it as a within-session cache lever: within a session
   the prompt-cache breakpoint advances automatically with each new
   entry, independent of read order.

7. **Grounding unchanged.** Retrieval surfaces locations; it is a
   retrieval aid, not a truth authority. Read the section for any
   verbatim claim and attach grounding tags as your persona
   requires. A snippet that *seems* to answer but the section does
   not confirm is treated as no-answer.

## Rebuild obligation (airchon-author only)

After writing or editing any `references/*/*.md` page, rebuild the
vector DB: call the `rebuild_index` MCP tool, or run
`python resources/scripts/rag_mcp_server.py build` with the venv
Python (`resources/scripts/.venv/Scripts/python`) if the MCP server
is unavailable. Also rebuild the heading index via the existing
`build_references_index.py update` step — see
`resources/references-index-maintenance.md`.

## Degradation map

- CAG prefix loaded (instructions: configured) → rules + area indexes
  in context at 0.1x cached read; no per-question Read needed for
  Rule 0 files.
- CAG prefix NOT loaded (harness without instructions: support, or
  not yet configured) → Read Rule 0 files from disk on first corpus
  question; they enter context at full price (no caching). Still
  functional, just not optimal.
- MCP server registered, venv healthy → `vector_search` primary.
- MCP server unavailable (harness without registration, missing
  binary, server error) → heading index only (rule 1 fallback).
  This is normal on any harness whose operator has not registered
  the server; it is not an error state.
- venv not bootstrapped (`resources/scripts/.venv/` absent) → same
  fallback; note it for the operator rather than failing.
