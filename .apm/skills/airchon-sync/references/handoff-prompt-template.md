# Handoff prompt template (per-page `Agent(airchon-author)` call)

Load this when Step 5 of `SKILL.md` fans out. One call per affected
page. The variable, page-specific content goes at the END, after the
identical instructional framing -- this keeps the framing prefix
stable across all calls in one run so they can share a cache hit
instead of re-billing full price on every call (the same discipline
the `airchon` router documents for its own exam-grading pipeline).

Audience: INTERNAL (`airchon-sync` calling `airchon-author`
programmatically). Brief mode: task-focused, not padded -- state the
page, the drifted source(s), and the evidence; never restate
`airchon-author`'s own role or grounding discipline, it already knows
this from its own persona file.

## Template

```
You are being invoked as the airchon-author agent for the AIrchon
project (working directory: <repo root>). This is an automated
source-drift re-check, not a request for new content -- one of your
own reference pages cites a source whose live state no longer matches
what's recorded in resources/sources-of-truth.json.

Re-fetch the source(s) named below, compare against what the citing
page currently says, and apply your own existing procedure: if the
page still fully and accurately covers the ground, say so and stop --
do not rewrite a settled page without a real reason. If the source
changed in a way that affects a claim on the page, update that page
per your own GROUNDING DISCIPLINE (re-tag VERIFIED with today's date
and the source you actually re-fetched), and note in your reply
exactly what changed and why it mattered.

Reply short, per your own persona's convention: which page you
checked, whether you changed it, and why (or why not).

--- Page to re-check ---
<page path, e.g. references/harnesses/hooks-lifecycle-extensibility.md>

--- Drifted source(s) on this page ---
<for each drifted source citing this page:>

Source: <url>
Type: <git-commit | content-hash>

<if git-commit:>
Recorded commit: <old value> (<old date>)
Live commit: <new value> (<new date>)
Compare diff (files changed): <compare.files -- filename/status/additions/deletions from the check script's output, or "not available" if the compare call failed>

<if content-hash:>
Recorded hash: sha256:<old value, shortened>
Live hash: sha256:<new value, shortened>
Note: content-hash drift on this project has a confirmed non-trivial
false-positive rate on SPA-rendered sites (see SKILL.md) -- re-fetch
and actually compare before assuming the page's claims broke; a hash
difference alone is not evidence of that.
```

## Notes

- If a page has more than one drifted source, list all of them in one
  call (one `Agent()` call per PAGE, not per source) -- `airchon-author`
  can re-verify several citations on the same page in one pass more
  cheaply than N separate calls re-loading the same page N times.
- Never invent the compare-diff content -- if the check script's
  `compare` field is missing or shows a FAILED status, say so plainly
  in the prompt ("not available") rather than fabricating a plausible-
  looking diff.
