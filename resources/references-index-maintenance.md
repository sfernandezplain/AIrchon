# Maintaining `resources/references-index.md`

Read this whenever `airchon-author`'s REFERENCES PROCEDURE reaches the
"regenerate this page's heading-index block" step. This doc holds the
procedure detail so it doesn't have to live in the always-loaded
persona body -- same reasoning CLAUDE.md already gives for why
`airchon-teacher`'s four procedure files sit outside its own persona
file.

## What this file is

`resources/references-index.md` maps every `references/*/*.md` page to
its own current H2/H3 section headings, so `airchon-mentor` and
`airchon-teacher` can go straight to the right page/section instead of
a blind `Grep` across all five areas. It is a section-level companion
to each area's own `index.md` (which stays topic-level, one line per
page) -- not a replacement for it.

It deliberately records **heading text, not line numbers**. A stale
heading just fails to match on a later lookup and the reader falls
back to a normal read; a stale line number would silently point at
the wrong content after any edit above it. Never add line numbers or
offsets to this file.

## The rule: never hand-transcribed

Heading text is a fact about the current file content -- it must come
from actually reading the file this session, not from your own recall
of what you just wrote. `resources/scripts/build_references_index.py`
exists specifically so you never have to retype a heading from memory.

## Procedure (one page, after you write or edit it)

1. Run:
   ```
   python resources/scripts/build_references_index.py update <page path>
   ```
   e.g. `python resources/scripts/build_references_index.py update references/harnesses/caching.md`

2. The command prints structured JSON on stdout, including a ready-to-
   use `"block"` field -- the exact markdown block for this page
   (`## <page path>` followed by its heading list). Diagnostics (a
   not-found page, etc.) go to stderr.

3. Open `resources/references-index.md` and replace ONLY that page's
   existing block (from its `## <page path>` line up to, but not
   including, the next `## ` line) with the fresh `"block"` value,
   copied verbatim. Do not touch any other page's block. Do not
   regenerate the whole file for a single-page edit.

4. If the page is brand new (no existing block to replace), insert its
   block in the position that keeps blocks sorted by path within their
   area, matching `bootstrap` mode's own ordering (alphabetical by
   filename within `find_pages()`).

## One-time / full-rebuild use (not a per-edit step)

```
python resources/scripts/build_references_index.py bootstrap
```

Walks every `references/*/*.md` page (excluding each area's own
`index.md`) and rewrites the entire index file in one pass. This is
what seeded the file initially; run it again only if the file is
believed to have drifted badly (e.g. after a bulk rename/reorg touched
many pages at once) -- not as routine maintenance. Routine maintenance
is always the single-page `update` step above.

## After any references/** change: also rebuild the vector DB

The heading index and the semantic vector DB are independent artifacts
-- a heading-index `update` does not refresh the vector DB. After
writing or editing any `references/*/*.md` page, also rebuild the
vector DB so `vector_search` (see
`resources/corpus-read-discipline.md`) reflects the new content:

- via MCP: call the `rebuild_index` tool on the `airchon-rag` server, or
- via CLI: `resources/scripts/.venv/Scripts/python resources/scripts/rag_mcp_server.py build`
  (Windows; use `resources/scripts/.venv/bin/python` on POSIX).

Notes:
- Run it with the **venv Python**, never the operator's global Python
  -- fastembed lives only in `resources/scripts/.venv/` (the operator
  may not have global pip installs; the venv keeps the one
  third-party dependency out of the global environment).
- The first-ever build downloads the embedding model
  (~130MB, `sentence-transformers/all-MiniLM-L6-v2`) to the
  operator's user-profile cache, once; every later build is just
  local re-embedding of ~1.5K sections, a few seconds.
- If the venv itself is missing (fresh clone), bootstrap it first:
  `python -m venv resources/scripts/.venv` then
  `resources/scripts/.venv/Scripts/python -m pip install -r resources/scripts/requirements.txt`.
- The DB is a gitignored generated artifact
  (`resources/vector-index.db`) -- never hand-edited, never committed.
- If the rebuild is impossible (no network for the one-time model
  download, venv broken), say so in your reply; the heading index
  above still covers the fallback path, so readers are not stranded.
