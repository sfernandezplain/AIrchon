#!/usr/bin/env python3
"""check_drift.py -- deterministic source-drift checker for airchon-sync.

S7 DETERMINISTIC TOOL BRIDGE: hashes and commit SHAs are facts-that-
must-be-true. This script computes them by actually fetching each
source; it never asks a model to recall or approximate one.

Modes:
  check   Re-fetch every source recorded in a sources-of-truth JSON
          file, compare each against its recorded value, and write the
          full result to --output. For a drifted git-commit source,
          also fetches a GitHub compare-diff summary (file names +
          insertion/deletion counts) between the recorded and the new
          commit, so the caller doesn't hand airchon-author a bare
          "it changed" with no evidence.
  render  Mechanically regenerate sources-of-truth.md and .json from a
          --checked result. Never hand-transcribe hash/commit values --
          this is the only thing allowed to write those files.

Structured JSON is written to the file arguments; a one-line summary
goes to stdout; diagnostics go to stderr. Non-interactive -- safe for
unattended/scheduled invocation. No third-party dependencies (stdlib
only) so there is nothing here to drift out from under itself; `gh`
CLI must be installed and authenticated for git-commit sources.

Usage:
  check_drift.py check --input resources/sources-of-truth.json --output /tmp/checked.json
  check_drift.py render --checked /tmp/checked.json --md resources/sources-of-truth.md --json resources/sources-of-truth.json
  check_drift.py --help
"""
import argparse
import datetime
import hashlib
import json
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 airchon-sync/1.0"
    )
}
CTX = ssl.create_default_context()
AREA_ORDER = ["harnesses", "sdlc", "rag", "models", "inference-engines"]
AREA_TITLES = {
    "harnesses": "references/harnesses/",
    "sdlc": "references/sdlc/",
    "rag": "references/rag/",
    "models": "references/models/",
    "inference-engines": "references/inference-engines/",
}


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def fetch_bytes(url):
    """GET a URL, following redirects (urllib chokes on 308; curl doesn't)."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12, context=CTX) as resp:
            return resp.read(), resp.status, None
    except (urllib.error.HTTPError, urllib.error.URLError, Exception) as e:  # noqa: BLE001
        code = getattr(e, "code", None)
        if code in (301, 302, 303, 307, 308) or code is None:
            try:
                r = subprocess.run(
                    ["curl", "-sL", "--max-time", "15", url],
                    capture_output=True, timeout=20,
                )
                if r.returncode == 0 and r.stdout:
                    return r.stdout, 200, None
            except Exception as e2:  # noqa: BLE001
                return None, None, f"FAILED: curl fallback: {e2}"
        return None, code, f"FAILED: {type(e).__name__}: {e}"


def fetch_hash(url):
    body, status, err = fetch_bytes(url)
    if err:
        if status == 404:
            return {"status": "DEAD_LINK: HTTP 404", "value": None}
        return {"status": err, "value": None}
    return {"status": "OK", "value": hashlib.sha256(body).hexdigest()}


def parse_github(url):
    p = urlparse(url)
    parts = [x for x in p.path.split("/") if x]
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1]
    if len(parts) >= 3 and parts[2] in ("issues", "pull", "releases", "commit"):
        return {"static": True}
    branch, path = None, None
    if len(parts) >= 4 and parts[2] in ("blob", "tree"):
        branch, path = parts[3], "/".join(parts[4:]) or None
    elif len(parts) >= 3:
        path = "/".join(parts[2:])
    return {"owner": owner, "repo": repo, "branch": branch, "path": path}


def gh_commit(owner, repo, branch, path):
    args = ["gh", "api", f"repos/{owner}/{repo}/commits", "--method", "GET", "-f", "per_page=1"]
    if branch:
        args += ["-f", f"sha={branch}"]
    if path:
        args += ["-f", f"path={path}"]
    args += ["-q", ".[0] | {sha: .sha, date: .commit.committer.date}"]
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=20)
        if r.returncode != 0:
            return {"status": f"FAILED: {r.stderr.strip()[:200]}", "value": None}
        out = json.loads(r.stdout.strip())
        return {"status": "OK", "value": out["sha"][:12], "commit_date": out["date"]}
    except Exception as e:  # noqa: BLE001
        return {"status": f"FAILED: {type(e).__name__}: {e}", "value": None}


def gh_compare(owner, repo, base, head):
    """File-level diff summary between two commits -- evidence for the
    airchon-author handoff, not the full patch (keep it small)."""
    args = ["gh", "api", f"repos/{owner}/{repo}/compare/{base}...{head}",
            "-q", "{files: [.files[] | {filename, status, additions, deletions}], total_commits: .total_commits}"]
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=20)
        if r.returncode != 0:
            return {"status": f"FAILED: {r.stderr.strip()[:200]}"}
        return {"status": "OK", **json.loads(r.stdout.strip())}
    except Exception as e:  # noqa: BLE001
        return {"status": f"FAILED: {type(e).__name__}: {e}"}


def check_one(entry):
    """Sets drifted (value actually changed) and handoff_needed (worth
    an airchon-author pass). These differ for bare-repo git citations:
    a repo's HEAD commit changes on every unrelated commit anywhere in
    it, so for a citation with no specific file path, `drifted` can be
    true constantly while `handoff_needed` stays false -- confirmed
    empirically: 10 of this project's own 19 git sources are bare-repo
    citations (claude-code, opencode, pi, hermes-agent among them, all
    under active development), so treating bare-repo drift as
    handoff-worthy would flood every run with noise and exhaust the
    fan-out cap (see step 3.2's cost-safety design) on irrelevant
    commits before a single real, path-scoped or content change gets a
    look. Only a path-scoped git citation, or a content-hash source (no
    path concept applies there), can set handoff_needed."""
    d = dict(entry)
    old_value = d.get("value")
    if d.get("type") == "static-github-reference":
        d["new_status"] = "STATIC"
        d["drifted"] = False
        d["handoff_needed"] = False
        return d
    if d.get("type") == "git-commit":
        info = parse_github(d["url"])
        if info is None or info.get("static"):
            d["new_status"] = "STATIC"
            d["drifted"] = False
            d["handoff_needed"] = False
            return d
        r = gh_commit(info["owner"], info["repo"], info["branch"], info["path"])
        d["new_status"] = r["status"]
        d["new_value"] = r.get("value")
        d["new_commit_date"] = r.get("commit_date")
        d["drifted"] = r["status"] == "OK" and r["value"] != old_value
        d["handoff_needed"] = d["drifted"] and info.get("path") is not None
        if d["handoff_needed"]:
            d["compare"] = gh_compare(info["owner"], info["repo"], old_value, r["value"])
        return d
    # content-hash (doc page). KNOWN, CONFIRMED-SEVERE LIMITATION, not
    # fixed here: SPA-rendered doc sites (docs.github.com,
    # platform.claude.com -- both React/Next.js-style apps) return
    # byte-different responses on a roughly hour-scale cycle with no
    # underlying content change -- confirmed empirically this session:
    # two back-to-back fetches of the same page are byte-identical
    # (same size, same SHA-256), but re-checking ~45 minutes later
    # against this project's own 225-source set flagged ~30% of non-git
    # sources as "drifted," concentrated entirely on SPA-rendered
    # domains (docs.github.com, platform.claude.com) -- almost
    # certainly a CDN edge-cache cycle re-baking a build timestamp,
    # nonce, or asset hash into the response, not a real content edit.
    # Simpler/static-rendered doc sites were NOT affected at the same
    # rate in this same test run. This is not a rare edge case; treat
    # content-hash "drift" as a noisy, non-trivial-baseline-rate signal
    # on SPA-rendered sources specifically, not proof anything changed.
    # airchon-author's own settled-page short-circuit ("if a page
    # already covers the ground, say so and stop") is what keeps a
    # false-positive handoff cheap rather than a wasted full rewrite --
    # this script does not and cannot make that judgment itself.
    r = fetch_hash(d["url"])
    d["new_status"] = r["status"]
    d["new_value"] = r.get("value")
    d["drifted"] = r["status"] == "OK" and r["value"] != old_value
    d["handoff_needed"] = d["drifted"]
    return d


def cmd_check(args):
    src = json.load(open(args.input, encoding="utf-8"))
    sources = src["sources"]
    git_entries = [d for d in sources if d.get("type") == "git-commit"]
    other_entries = [d for d in sources if d.get("type") != "git-commit"]

    log(f"Checking {len(git_entries)} git sources (sequential, gh api) "
        f"and {len(other_entries)} others (parallel)...")

    results = []
    for d in git_entries:
        r = check_one(d)
        results.append(r)
        log(f"  [git] {r['url']} -> {r['new_status']}"
            + (" DRIFTED" if r["drifted"] else ""))

    with ThreadPoolExecutor(max_workers=16) as ex:
        futs = {ex.submit(check_one, d): d for d in other_entries}
        done = 0
        for fut in as_completed(futs):
            results.append(fut.result())
            done += 1
            if done % 25 == 0:
                log(f"  ...{done}/{len(other_entries)} checked")

    today = datetime.date.today().isoformat()
    for r in results:
        r["checked"] = today

    drifted = [r for r in results if r.get("drifted")]
    actionable = [r for r in results if r.get("handoff_needed")]
    out = {"generated": today, "sources": results}
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    # pages affected, for the caller to group its fan-out by -- only
    # handoff_needed sources drive this, not every value-changed source
    # (see check_one's bare-repo-noise note)
    pages = sorted({p for r in actionable for p in r.get("cited_by", [])})

    summary = {
        "total": len(results),
        "value_changed": len(drifted),
        "handoff_needed": len(actionable),
        "handoff_urls": [r["url"] for r in actionable],
        "affected_pages": pages,
        "output_file": args.output,
    }
    print(json.dumps(summary, indent=2))


def fmt_value(d):
    status = str(d.get("status", ""))
    if status.startswith("OK") and d.get("type") == "git-commit":
        date = (d.get("commit_date") or "")[:10]
        return f"commit `{d['value']}` ({date})"
    if status.startswith("OK") and d.get("type") == "content-hash":
        return f"`sha256:{d['value'][:20]}...`"
    if status == "STATIC":
        return "-- (immutable reference)"
    return "**MISSING**"


def fmt_status(d):
    status = str(d.get("status", ""))
    if status.startswith("OK"):
        return "OK"
    if status == "STATIC":
        return "static"
    if status.startswith("DEAD_LINK"):
        return f"**DEAD LINK** -- {status.split(':', 1)[1].strip()}"
    return f"FAILED -- {status}"


def cmd_render(args):
    checked = json.load(open(args.checked, encoding="utf-8"))["sources"]

    rebased = []
    for d in checked:
        nd = dict(d)
        if d.get("new_status") and d["new_status"] != "STATIC":
            nd["value"] = d.get("new_value", d.get("value"))
            nd["status"] = d["new_status"]
            if "new_commit_date" in d:
                nd["commit_date"] = d["new_commit_date"]
        for k in ("new_status", "new_value", "new_commit_date", "drifted", "handoff_needed", "compare"):
            nd.pop(k, None)
        rebased.append(nd)

    today = datetime.date.today().isoformat()
    ok = sum(1 for d in rebased if str(d.get("status", "")).startswith("OK"))
    static = sum(1 for d in rebased if str(d.get("status", "")).startswith("STATIC"))
    bad = len(rebased) - ok - static

    lines = [
        "# Sources of truth -- live drift detection",
        "",
        f"Generated {today} by `airchon-sync` (re-run of `check_drift.py`),",
        "actually fetching every source, not by describing a mechanism.",
        "",
        f"**Result: {len(rebased)} sources checked, {ok} confirmed live and "
        f"correct right now, {static} static, {bad} need attention.**",
        "",
        "See `resources/sources-of-truth.json` (same directory) for full",
        "unshortened hashes/commit SHAs, and `.apm/skills/airchon-sync/` for",
        "the mechanism that generated this file.",
        "",
        "---",
        "",
    ]
    for area in AREA_ORDER:
        area_data = [d for d in rebased if area in d.get("area", [])]
        if not area_data:
            continue
        lines.append(f"## {AREA_TITLES[area]}")
        lines.append("")
        lines.append("| Source | Cited by | Check | Current value | Status |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for d in sorted(area_data, key=lambda x: x["url"]):
            cited = "<br>".join(f"`{c.split('/')[-1]}`" for c in d.get("cited_by", []))
            check_type = {"git-commit": "commit SHA", "content-hash": "SHA-256",
                          "static-github-reference": "static"}.get(d.get("type"), d.get("type", "?"))
            lines.append(f"| [{d['url']}]({d['url']}) | {cited} | {check_type} | "
                         f"{fmt_value(d)} | {fmt_status(d)} |")
        lines.append("")

    with open(args.md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    with open(args.json, "w", encoding="utf-8") as f:
        json.dump({"generated": today, "sources": rebased}, f, indent=2)

    print(json.dumps({"rendered_md": args.md, "rendered_json": args.json,
                       "total": len(rebased), "ok": ok, "static": static, "bad": bad}))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="mode", required=True)

    pc = sub.add_parser("check", help="Re-fetch every recorded source and diff against it")
    pc.add_argument("--input", required=True, help="path to sources-of-truth.json")
    pc.add_argument("--output", required=True, help="path to write the full checked-result JSON")

    pr = sub.add_parser("render", help="Regenerate sources-of-truth.md/.json from a checked result")
    pr.add_argument("--checked", required=True, help="path to a checked-result JSON from `check`")
    pr.add_argument("--md", required=True, help="path to write sources-of-truth.md")
    pr.add_argument("--json", required=True, help="path to write sources-of-truth.json")

    args = p.parse_args()
    if args.mode == "check":
        cmd_check(args)
    else:
        cmd_render(args)


if __name__ == "__main__":
    main()
