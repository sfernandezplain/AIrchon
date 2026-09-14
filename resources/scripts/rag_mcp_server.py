#!/usr/bin/env python3
"""Stdio MCP server + CLI for semantic reference-corpus retrieval.

Exposes two MCP tools (JSON-RPC 2.0 over stdio, newline-delimited):
  vector_search(query, top_k=5)  cosine top-k section candidates
  rebuild_index()                rebuild resources/vector-index.db

CLI subcommands (same file, so the index can be built/tested from a
shell without a harness):
  build                 rebuild the vector DB
  query TEXT [--top-k N]   run a search, print results
  serve                 run as the stdio MCP server

Third-party imports (fastembed, numpy) live in the dedicated venv at
resources/scripts/.venv -- run this file with
resources/scripts/.venv/Scripts/python, never the operator's global
Python. Everything else is stdlib.
"""
import argparse
import json
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent.parent
REFERENCES = ROOT / "references"
DB_PATH = ROOT / "resources" / "vector-index.db"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
SERVER_NAME = "airchon-rag"
SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2025-06-18"

MODELS = None


def _model():
    global MODELS
    if MODELS is None:
        from fastembed import TextEmbedding
        MODELS = TextEmbedding(MODEL_NAME)
    return MODELS


def _log(msg: str) -> None:
    print(msg, file=sys.stderr)


def _embed(texts: list[str]):
    import numpy as np
    return np.asarray(list(_model().embed(texts)), dtype="float32")


def _cosine_topk(query_vec, rows, k):
    import numpy as np
    if not rows:
        return []
    mat = np.vstack([r[6] for r in rows]).astype("float32")
    q = query_vec.astype("float32")
    qn = q / (np.linalg.norm(q) or 1.0)
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    mn = mat / norms
    scores = mn @ qn
    order = np.argsort(-scores)[:k]
    return [(rows[i], float(scores[i])) for i in order]


# ---------------------------------------------------------------- chunks


def section_chunks(path: Path):
    """Return [(section, section_path, body, line_start, line_end)]
    with H2/H3 sections split correctly and fence-aware."""
    lines = path.read_text(encoding="utf-8").splitlines()
    chunks = []
    in_fence = False
    cur = None
    h2 = None

    def flush(end):
        nonlocal cur
        if cur is None:
            return
        body = "\n".join(cur[3]).strip()
        if len(body) >= 20:
            chunks.append((cur[0], cur[1], body, cur[2], end))
        cur = None

    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            if cur:
                cur[3].append(line)
            continue
        if not in_fence and (line.startswith("## ") or line.startswith("### ")):
            flush(i - 1)
            title = line.lstrip("#").strip()
            if line.startswith("## "):
                h2 = title
                cur = [title, title, i, []]
            else:
                sp = f"{h2} > {title}" if h2 else title
                cur = [title, sp, i, []]
        else:
            if cur is None:
                cur = ["(top)", "(top)", 1, []]
            cur[3].append(line)
    flush(len(lines))
    return chunks


def find_pages():
    return sorted(
        p for p in REFERENCES.glob("*/*.md")
        if p.name != "index.md"
    )


def _fingerprint(pages):
    return {p.relative_to(ROOT).as_posix(): f"{p.stat().st_mtime_ns}:{p.stat().st_size}" for p in pages}


def build_db(quiet=False):
    import numpy as np
    import sqlite3

    if not REFERENCES.is_dir():
        _log(f"references/ not found at {REFERENCES}")
        return 1
    pages = find_pages()
    if not pages:
        _log("no reference pages found")
        return 1

    t0 = time.time()
    all_chunks = []
    for p in pages:
        for sec, sp, body, ls, le in section_chunks(p):
            snippet = body[:240].replace("\n", " ").strip()
            all_chunks.append((p.relative_to(ROOT).as_posix(), sec, sp, snippet, body, ls, le))

    texts = [c[4] for c in all_chunks]
    _log(f"embedding {len(texts)} sections with {MODEL_NAME} ...")
    vecs = _embed(texts)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "CREATE TABLE chunks (id INTEGER PRIMARY KEY, page TEXT, section TEXT,"
        " section_path TEXT, snippet TEXT, line_start INT, line_end INT, vec BLOB)"
    )
    con.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
    con.execute("INSERT INTO meta VALUES ('model', ?)", (MODEL_NAME,))
    con.execute("INSERT INTO meta VALUES ('built_at', ?)", (time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),))
    fps = _fingerprint(pages)
    con.executemany("INSERT INTO meta VALUES ('fp:' || ?, ?)", [(k, v) for k, v in fps.items()])
    con.executemany(
        "INSERT INTO chunks (page, section, section_path, snippet, line_start, line_end, vec)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        [(c[0], c[1], c[2], c[3], c[5], c[6], np.asarray(v, dtype="float32").tobytes())
         for c, v in zip(all_chunks, vecs)],
    )
    con.commit()
    con.close()

    if not quiet:
        _log(
            f"built {DB_PATH.name}: {len(all_chunks)} sections from {len(pages)} pages"
            f" in {time.time() - t0:.1f}s"
        )
    return 0


def _load_rows():
    import sqlite3
    import numpy as np
    con = sqlite3.connect(DB_PATH)
    rows = con.execute(
        "SELECT page, section, section_path, snippet, line_start, line_end, vec FROM chunks"
    ).fetchall()
    out = [(r[0], r[1], r[2], r[3], r[4], r[5], np.frombuffer(r[6], dtype="float32")) for r in rows]
    meta = dict(con.execute("SELECT key, value FROM meta WHERE key LIKE 'fp:%'").fetchall())
    meta = {k[3:]: v for k, v in meta.items()}
    model = con.execute("SELECT value FROM meta WHERE key='model'").fetchone()
    model = model[0] if model else "?"
    con.close()
    return out, meta, model


def _stale_note(stored_fps):
    try:
        current = _fingerprint(find_pages())
    except OSError:
        return None
    if current != stored_fps:
        return "stale: references/ changed since last build -- call rebuild_index for authoritative results"
    return None


def vector_search(query: str, top_k: int = 5):
    if not DB_PATH.exists():
        return {
            "error": "vector index not found",
            "db": DB_PATH.as_posix(),
            "fallback": "use resources/references-index.md (heading index) + each area's index.md",
        }
    rows, stored_fps, model = _load_rows()
    qv = _embed([query])[0]
    results = _cosine_topk(qv, rows, max(1, min(int(top_k), 20)))
    entries = [
        {"page_path": r[0], "section": r[1], "section_path": r[2],
         "score": round(s, 4), "snippet": r[3], "lines": f"{r[4]}-{r[5]}"}
        for r, s in results
    ]
    payload = {"model": model, "query": query, "results": entries}
    note = _stale_note(stored_fps)
    if note:
        payload["warning"] = note
    return payload


# ------------------------------------------------------------- MCP layer

TOOL_DEFS = [
    {
        "name": "vector_search",
        "description": (
            "Semantic search over the references/ corpus (per H2/H3 section). "
            "Returns top_k candidates: page_path, section, section_path, score, "
            "snippet, lines. Read the named section for any verbatim claim; "
            "the snippet alone is not a source."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "the question or topic, in natural language"},
                "top_k": {"type": "integer", "default": 5, "minimum": 1, "maximum": 20},
            },
            "required": ["query"],
        },
    },
    {
        "name": "rebuild_index",
        "description": (
            "Rebuild resources/vector-index.db from references/** (idempotent, "
            "seconds, local embeddings). Call after writing/editing a reference page."
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def _rpc_ok(mid, result):
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def _rpc_err(mid, code, message):
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}


def _tool_result(payload):
    return {"content": [{"type": "text", "text": json.dumps(payload, indent=2)}], "isError": False}


def handle_request(msg: dict):
    mid = msg.get("id")
    method = msg.get("method")
    params = msg.get("params") or {}

    if method == "initialize":
        client_pv = (params or {}).get("protocolVersion", PROTOCOL_VERSION)
        return _rpc_ok(mid, {
            "protocolVersion": client_pv,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
        })
    if method == "ping":
        return _rpc_ok(mid, {})
    if method == "tools/list":
        return _rpc_ok(mid, {"tools": TOOL_DEFS})
    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        if name == "vector_search":
            payload = vector_search(str(args.get("query", "")), args.get("top_k", 5))
            return _rpc_ok(mid, _tool_result(payload))
        if name == "rebuild_index":
            rc = build_db(quiet=True)
            payload = {"rebuilt": rc == 0, "db": DB_PATH.as_posix()}
            if rc != 0:
                payload["error"] = "build failed; see server stderr log"
            return _rpc_ok(mid, _tool_result(payload))
        return _rpc_err(mid, -32602, f"unknown tool: {name}")
    return _rpc_err(mid, -32601, f"unknown method: {method}")


def serve():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError as e:
            _log(f"bad json: {e}")
            continue
        if "method" not in msg:
            continue
        if "id" not in msg:
            continue  # notification (e.g. notifications/initialized)
        try:
            resp = handle_request(msg)
        except Exception as e:  # noqa: BLE001 - report, keep server alive
            _log(f"error handling {msg.get('method')}: {e!r}")
            resp = _rpc_err(msg.get("id"), -32603, f"internal error: {e!r}")
        print(json.dumps(resp), flush=True)


# ------------------------------------------------------------------ CLI

def cmd_build(args):
    return build_db(quiet=False)


def cmd_query(args):
    payload = vector_search(args.text, args.top_k)
    print(json.dumps(payload, indent=2))
    return 0 if "error" not in payload else 2


def main():
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd")
    p_build = sub.add_parser("build", help="rebuild the vector DB")
    p_build.set_defaults(func=cmd_build)
    p_q = sub.add_parser("query", help="search the vector DB")
    p_q.add_argument("text", help="query text")
    p_q.add_argument("--top-k", type=int, default=5)
    p_q.set_defaults(func=cmd_query)
    p_serve = sub.add_parser("serve", help="run as the stdio MCP server")
    p_serve.set_defaults(func=lambda a: (serve(), 0)[1])
    args = parser.parse_args()
    if args.cmd is None:
        parser.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
