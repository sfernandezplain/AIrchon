#!/usr/bin/env python3
"""Measure references/ corpus size per area: page count, bytes, and an
approximate token count (bytes / 4 -- an approximation, labeled as such
in the output). Feeds the ceiling-check step of
resources/corpus-read-discipline.md and the per-area snapshot that
file carries.

Stdlib only, no third-party dependency (same discipline as
build_references_index.py).

Example:
  python resources/scripts/corpus_stats.py
"""
import argparse
import json
import sys
from pathlib import Path


def measure(root: Path) -> dict:
    areas = {}
    pages = 0
    bytes_total = 0
    for area_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        area_pages = sorted(area_dir.glob("*.md"))
        area_bytes = sum(p.stat().st_size for p in area_pages)
        pages += len(area_pages)
        bytes_total += area_bytes
        areas[area_dir.name] = {
            "pages": len(area_pages),
            "bytes": area_bytes,
            "approx_tokens": round(area_bytes / 4),
        }
    return {
        "areas": areas,
        "total": {
            "pages": pages,
            "bytes": bytes_total,
            "approx_tokens": round(bytes_total / 4),
        },
        "note": "token counts are approximations (bytes/4), not precise",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default="references", help="references/ root (default: references)")
    parser.add_argument("--json", action="store_true", help="print raw JSON instead of the readable table")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        print(f"not found: {root}", file=sys.stderr)
        return 1
    stats = measure(root)

    if args.json:
        print(json.dumps(stats, indent=2), file=sys.stdout)
        return 0

    for name, a in stats["areas"].items():
        print(f"{name:>20}  {a['pages']:>3} pages  {a['bytes']:>9} bytes  ~{a['approx_tokens']:>7} tokens (approx)")
    t = stats["total"]
    print(f"{'TOTAL':>20}  {t['pages']:>3} pages  {t['bytes']:>9} bytes  ~{t['approx_tokens']:>7} tokens (approx)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
