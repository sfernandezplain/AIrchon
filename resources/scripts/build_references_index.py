#!/usr/bin/env python3
"""Maintain resources/references-index.md: a machine-generated map of
every references/*/*.md page to its own current H2/H3 headings.

Never hand-edit the output file. Two modes:

  bootstrap   Walk the whole references/ tree and (re)write the full
              index file in one pass. Run once, by hand, to seed or
              fully rebuild the index -- not a recurring agent step.

  update PATH Extract headings from ONE page and print them as
              structured JSON on stdout (diagnostics on stderr).
              airchon-author calls this after writing/editing a page
              and copies the output verbatim into that page's block
              in the index file -- never retyped from memory.

Stdlib only, no third-party dependency to drift out from under itself
(same discipline as .apm/skills/airchon-sync/scripts/check_drift.py).

Examples:
  python resources/scripts/build_references_index.py bootstrap
  python resources/scripts/build_references_index.py update references/harnesses/caching.md
"""
import argparse
import json
import re
import sys
from pathlib import Path

HEADING_RE = re.compile(r"^(#{2,3})\s+(.*\S)\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def extract_headings(text: str) -> list[dict]:
    """Return [{"level": 2|3, "text": ...}, ...] in document order,
    skipping anything inside fenced code blocks (mermaid diagrams use
    '##'-shaped labels that are not real headings)."""
    headings = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING_RE.match(line)
        if m:
            headings.append({"level": len(m.group(1)), "text": m.group(2)})
    return headings


def find_pages(root: Path) -> list[Path]:
    pages = sorted(
        p for p in root.glob("*/*.md") if p.name != "index.md"
    )
    return pages


def render_block(rel_path: str, headings: list[dict]) -> str:
    lines = [f"## {rel_path}"]
    if not headings:
        lines.append("- (no ## headings found)")
    for h in headings:
        prefix = "- " if h["level"] == 2 else "  - "
        lines.append(f"{prefix}{h['text']}")
    return "\n".join(lines)


def cmd_bootstrap(args: argparse.Namespace) -> int:
    root = Path(args.root)
    pages = find_pages(root)
    blocks = []
    for p in pages:
        text = p.read_text(encoding="utf-8")
        rel = p.as_posix()
        blocks.append(render_block(rel, extract_headings(text)))

    header = (
        "# References heading-index\n\n"
        "Machine-maintained by `airchon-author` via "
        "`resources/scripts/build_references_index.py` -- never "
        "hand-edited. Regenerated one page-block at a time on every "
        "references/*/*.md edit (see "
        "`resources/references-index-maintenance.md`); this copy was "
        "last fully rebuilt via `bootstrap` mode.\n\n"
        "Companion to each area's own `index.md` (topic-level summary) "
        "-- this file is section-level (heading text only, no line "
        "numbers: a stale heading fails to match and falls back to a "
        "normal read; a stale line number would silently point at the "
        "wrong content).\n"
    )
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(header + "\n" + "\n\n".join(blocks) + "\n", encoding="utf-8")

    summary = {"pages_indexed": len(pages), "output": str(out_path)}
    print(json.dumps(summary), file=sys.stdout)
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    path = Path(args.page)
    if not path.exists():
        print(json.dumps({"error": f"not found: {path}"}), file=sys.stderr)
        return 1
    text = path.read_text(encoding="utf-8")
    headings = extract_headings(text)
    rel = path.as_posix()
    result = {
        "page": rel,
        "headings": headings,
        "block": render_block(rel, headings),
    }
    print(json.dumps(result, indent=2), file=sys.stdout)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="mode", required=True)

    p_boot = sub.add_parser("bootstrap", help="rebuild the full index from every references/*/*.md page")
    p_boot.add_argument("--root", default="references", help="references/ root (default: references)")
    p_boot.add_argument("--output", default="resources/references-index.md", help="output file (default: resources/references-index.md)")
    p_boot.set_defaults(func=cmd_bootstrap)

    p_upd = sub.add_parser("update", help="extract headings from ONE page, printed as JSON on stdout")
    p_upd.add_argument("page", help="path to the page, e.g. references/harnesses/caching.md")
    p_upd.set_defaults(func=cmd_update)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
