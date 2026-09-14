#!/usr/bin/env python3
"""Standalone rebuild script -- run from a REAL terminal, not from
inside opencode's bash tool (which hangs on long CPU runs).

Usage (from the project root):

    resources/scripts/.venv/Scripts/python resources/scripts/rebuild_index.py

Prints progress so you can see it's working.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rag_mcp_server as rag

print(f"Model:   {rag.MODEL_NAME}")
print(f"DB:      {rag.DB_PATH}")
print(f"Corpus:  {rag.REFERENCES}")
print()

t0 = time.time()
rc = rag.build_db(quiet=False)
print(f"\nDone in {time.time() - t0:.1f}s (exit {rc})")
