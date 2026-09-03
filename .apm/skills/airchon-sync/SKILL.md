---
name: airchon-sync
description: Use this skill when the operator asks to check whether the wiki-book's cited sources have drifted from what's recorded on disk -- "run the source sync", "check for stale sources", "has anything changed upstream", "refresh sources-of-truth", "audit the sources again", or on a scheduled cadence. Re-fetches every source in resources/sources-of-truth.json, compares its live commit SHA (git sources) or content hash (doc pages) against the recorded value, and for each one that's actionable, hands off to airchon-author with the specific evidence (a GitHub compare diff for a moved commit, a changed-hash note for a doc page) so it can re-verify and update the citing page(s). Recalculates and writes the new baseline back to sources-of-truth.md/.json at the end. Does not judge whether a drift actually broke a cited claim -- that's airchon-author's call. Does not commit git changes itself.
user-invocable: true
disable-model-invocation: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - TodoWrite
  - Agent(airchon-author)
---

# airchon-sync

Reconciliation loop over `resources/sources-of-truth.json`: check every
recorded source against its live current state, hand off what actually
needs a second look to `airchon-author`, then rebaseline the record.
FORCED-only (`disable-model-invocation: true`) -- this makes real
network calls against ~225 external sources and can trigger several
full research-and-rewrite passes; it should never fire from ambient
conversation.

## Genesis design note

This skill's own handoff packet (diagrams, cost projection, evals plan)
was produced via `/genesis` and is scratch-only, per this project's own
precedent that design packets aren't committed (see `CHANGELOG.md`'s
2026-07-30 entries). What follows is the resulting procedure.

## Boundary

- Does NOT judge whether a drift actually broke a cited claim -- that
  stays `airchon-author`'s call, made by reading the new source.
- Does NOT discover new sources -- only re-checks what
  `sources-of-truth.json` already records.
- Does NOT commit git changes itself, per this project's git-safety
  discipline. Leaves the working tree with whatever changed for the
  operator to review and commit.
- Does NOT fire an unbounded fan-out -- a cap (default 8 pages per
  run, see Step 3) bounds worst-case cost; anything past the cap is
  reported as deferred, not dropped, and picked up on the next run.

## Known, confirmed limitation -- read before trusting a "drifted" count

Content-hash checks on SPA-rendered doc sites (`docs.github.com`,
`platform.claude.com` confirmed this session) produce a non-trivial
baseline "drift" rate with NO real content change -- almost certainly a
CDN edge-cache cycle re-baking a build timestamp or nonce into the
response on a roughly hour-scale cycle. Confirmed empirically while
building this skill: two back-to-back fetches of the same page were
byte-identical, but a same-session re-check ~45 minutes later flagged
~30% of non-git sources as drifted, concentrated entirely on those two
domains. **Do not schedule this unattended until you've reviewed at
least two or three manual runs' worth of handoff summaries** and
confirmed the false-positive rate is acceptable at your intended
cadence (a monthly cadence should see far less of this than an hourly
one would, since real content changes accumulate against a roughly
constant noise floor -- but that has not itself been tested yet).
`airchon-author`'s own settled-page short-circuit ("if a page already
covers the ground, say so and stop") is what keeps a false-positive
handoff cheap rather than a wasted full rewrite -- this skill does not
and cannot make that judgment itself.

## Procedure

1. **Check.** Run the bundled script in `check` mode:
   ```
   python .apm/skills/airchon-sync/scripts/check_drift.py check \
     --input resources/sources-of-truth.json \
     --output <a temp path, e.g. via Bash's own temp dir>
   ```
   This is an S7 DETERMINISTIC TOOL BRIDGE crossing -- hashes and
   commit SHAs are facts-that-must-be-true; never approximate or recall
   one yourself. Read the script's stdout summary (`total`,
   `value_changed`, `handoff_needed`, `handoff_urls`, `affected_pages`).
   `value_changed` counts every source whose live value differs from
   the recorded one; `handoff_needed` is the actionable subset (see
   below) -- always report and act on the latter, never the former.

2. **Understand what `handoff_needed` actually means** (the script
   already applies this filter; do not re-derive it):
   - A `git-commit` source with NO specific file path (a bare repo
     citation) that shows a new HEAD commit is NEVER handoff-worthy on
     its own -- an actively-developed repo's HEAD changes constantly
     from unrelated work (confirmed: 10 of this project's own 19 git
     sources are bare-repo citations). Its value still gets rebaselined
     at Step 5, silently.
   - A `git-commit` source with a specific file path (`/blob/` or
     `/tree/` in the URL) that shows a new commit IS handoff-worthy --
     the script already fetched a GitHub compare-diff summary
     (`compare` field: files changed, additions/deletions) for it.
   - A `content-hash` (doc page) source that shows a changed hash IS
     marked handoff-worthy by the script, but per the limitation above,
     treat the count with real skepticism, not as a settled fact.

3. **Group and cap.** From `affected_pages`, build the fan-out list.
   Default cap: 8 pages per invocation. If the operator named a
   different cap when invoking (or said something like "sync
   everything, no cap"), honor that instead. If `affected_pages`
   exceeds the cap, process the first N (stable order -- alphabetical,
   as the script emits them) and record the rest as deferred; do not
   silently drop them and do not exceed the cap without an explicit
   operator override.

4. **Track with TodoWrite.** One item per page in the capped list,
   titled with the page's own path. This is the session's plan memento
   -- if interrupted mid-fan-out, the check script's own `--output`
   JSON (still on disk) is the resumable record; re-read it and the
   `TodoWrite` state to see which pages still need a call, rather than
   re-running the network check from scratch.

5. **Fan out to `airchon-author`, one call per page.** Load
   [references/handoff-prompt-template.md](references/handoff-prompt-template.md)
   for the exact prompt shape -- it puts the page-specific drift
   evidence at the END of the prompt (cache-prefix discipline: keeps
   the instructional framing identical across calls). Mark each
   `TodoWrite` item done as its call returns. `airchon-author`'s own
   reply (already short, by its own persona's design) IS the receipt --
   no separate receipt schema needed.

6. **Render.** Run the bundled script in `render` mode against the SAME
   checked-result JSON from Step 1:
   ```
   python .apm/skills/airchon-sync/scripts/check_drift.py render \
     --checked <the Step 1 output path> \
     --md resources/sources-of-truth.md \
     --json resources/sources-of-truth.json
   ```
   This mechanically regenerates both tracked files from the check
   results -- never hand-edit or hand-transcribe hash/commit values
   into them yourself; that is exactly the LLM-asserted-fact anti-
   pattern this skill exists to avoid.

7. **Report.** One summary to the operator: total sources checked,
   how many values changed vs. how many were actually handoff-worthy
   (name both numbers -- the gap between them IS the noise-floor
   finding above, worth surfacing every run, not just once), how many
   pages were handed off and what each `airchon-author` call concluded
   (updated / no-change-needed), and how many were deferred past the
   cap. Remind the operator that `resources/sources-of-truth.md/.json`
   changed on disk and nothing has been committed.

## Bundled script

`scripts/check_drift.py` -- stdlib-only (no third-party dependency to
drift out from under itself), two modes (`check`, `render`), `--help`
documented, non-interactive, structured JSON on stdout/file, all
diagnostics on stderr. Requires `gh` CLI installed and authenticated
for git-commit sources.
