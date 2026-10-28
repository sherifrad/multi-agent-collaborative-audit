#!/usr/bin/env python3
"""MACA impact selector + evidence cache (stdlib only).

Purpose: stop re-running deep tests that cannot have been affected by a change, without ever
claiming a pass that was not earned. A test result is reused only when a content hash of everything
it depends on is unchanged since the run that passed.

Files (inside <workspace>/.agents/):
  TEST_MANIFEST.json   what tests exist: id, tier, cmd, deps (globs), always, covers
  EVIDENCE.json        last result per test: status, dep_hash, timestamp, cmd, note

Commands:
  select  --ws W [--max-tier N] [--json]     decide RUN / REUSE / DEFER for every test
  record  --ws W --id ID --status pass|fail [--note TEXT]   store a result against the current hashes
  status  --ws W                              fresh / stale / never-run / failed counts
  invalidate --ws W (--id ID | --all)         force re-run
  deps-suggest --root R --symbol NAME         files that mention a symbol (to build `deps` globs)
  --self-test

Decision rules (in order), per test:
  1. tier > --max-tier            -> DEFER   (reported as NOT RUN; never counts as a pass)
  2. always == true               -> RUN     (e.g. safety boundary tests)
  3. no evidence / last was fail  -> RUN
  4. deps match no files          -> RUN     (fail safe: cannot prove nothing changed)
  5. dep_hash differs             -> RUN     (lists which files changed)
  6. otherwise                    -> REUSE   (prior pass, hash identical)
"""
import argparse
import fnmatch
import glob
import hashlib
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

IGNORED_DIRS = {".git", "node_modules", "build", "dist", ".gradle", "__pycache__", ".agents", "vendor"}
MANIFEST = "TEST_MANIFEST.json"
EVIDENCE = "EVIDENCE.json"


def fail(code, msg, fix):
    print(json.dumps({"status": "MACA_SCRIPT_ERROR — STOP_AND_FIX", "error_code": code, "message": msg,
                      "remediation": fix}, indent=2), file=sys.stderr)
    sys.exit(2)


def agents_dir(ws):
    d = Path(ws).resolve() / ".agents"
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_json(path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail("BadJson", f"{path} is not valid JSON: {exc}", f"Fix or delete {path}")


def expand(ws, patterns):
    """Return sorted relative file paths matched by the glob patterns (ignored dirs excluded)."""
    root = Path(ws).resolve()
    found = set()
    for pat in patterns:
        for hit in glob.glob(str(root / pat), recursive=True):
            p = Path(hit)
            if not p.is_file():
                continue
            rel = p.relative_to(root)
            if any(part in IGNORED_DIRS for part in rel.parts):
                continue
            found.add(rel.as_posix())
    return sorted(found)


def file_hashes(ws, rels):
    root = Path(ws).resolve()
    out = {}
    for rel in rels:
        h = hashlib.sha256()
        h.update((root / rel).read_bytes())
        out[rel] = h.hexdigest()
    return out


def dep_state(ws, test):
    rels = expand(ws, test.get("deps", []))
    hashes = file_hashes(ws, rels)
    combined = hashlib.sha256()
    combined.update(str(test.get("cmd", "")).encode())
    for rel in rels:
        combined.update(rel.encode())
        combined.update(hashes[rel].encode())
    return combined.hexdigest(), hashes


def load_tests(ws):
    manifest = load_json(agents_dir(ws) / MANIFEST)
    if not manifest or not manifest.get("tests"):
        fail("NoManifest", f"No tests in {agents_dir(ws) / MANIFEST}",
             "Create it from resources/templates/TEST_MANIFEST.template.json (one entry per test).")
    seen = set()
    for t in manifest["tests"]:
        for key in ("id", "tier", "cmd", "deps"):
            if key not in t:
                fail("BadManifest", f"Test entry missing '{key}': {t}", "Add the field.")
        if t["id"] in seen:
            fail("BadManifest", f"Duplicate test id {t['id']}", "Ids must be unique.")
        seen.add(t["id"])
    return manifest["tests"]


def select(ws, max_tier):
    tests = load_tests(ws)
    evidence = (load_json(agents_dir(ws) / EVIDENCE, {}) or {}).get("tests", {})
    plan = []
    for t in tests:
        tid = t["id"]
        cur_hash, cur_files = dep_state(ws, t)
        ev = evidence.get(tid)
        row = {"id": tid, "tier": t["tier"], "cmd": t["cmd"], "action": "RUN", "reason": ""}
        if max_tier is not None and t["tier"] > max_tier:
            row.update(action="DEFER", reason=f"tier {t['tier']} above this round's ceiling {max_tier}; NOT RUN, not a pass")
        elif t.get("always"):
            row["reason"] = "always-run (safety/boundary test)"
        elif not ev:
            row["reason"] = "never run"
        elif ev.get("status") != "pass":
            row["reason"] = f"last result was {ev.get('status')}"
        elif not cur_files:
            row["reason"] = "deps match no files; cannot prove nothing changed"
        elif ev.get("dep_hash") != cur_hash:
            old = ev.get("files", {})
            changed = sorted(f for f in set(old) | set(cur_files) if old.get(f) != cur_files.get(f))
            row["reason"] = "deps changed: " + ", ".join(changed[:8]) + (" ..." if len(changed) > 8 else "")
        else:
            row.update(action="REUSE", reason=f"passed at {ev.get('ts')} with identical deps")
        plan.append(row)
    return plan


def cmd_record(ws, tid, status, note):
    tests = {t["id"]: t for t in load_tests(ws)}
    if tid not in tests:
        fail("UnknownTest", f"No test '{tid}' in manifest", "Use an id from TEST_MANIFEST.json")
    t = tests[tid]
    h, files = dep_state(ws, t)
    path = agents_dir(ws) / EVIDENCE
    data = load_json(path, {"tests": {}}) or {"tests": {}}
    data.setdefault("tests", {})[tid] = {
        "status": status, "dep_hash": h, "files": files, "cmd": t["cmd"],
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "note": note or ""}
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return h


def cmd_status(ws):
    plan = select(ws, None)
    counts = {"fresh_pass": 0, "stale": 0, "never_run": 0, "failed": 0}
    for r in plan:
        if r["action"] == "REUSE":
            counts["fresh_pass"] += 1
        elif r["reason"] == "never run":
            counts["never_run"] += 1
        elif r["reason"].startswith("last result"):
            counts["failed"] += 1
        else:
            counts["stale"] += 1
    return counts


def cmd_deps_suggest(root, symbol):
    pat = re.compile(r"\b" + re.escape(symbol) + r"\b")
    hits = []
    for p in Path(root).resolve().rglob("*"):
        if not p.is_file() or any(part in IGNORED_DIRS for part in p.parts):
            continue
        if p.suffix not in {".kt", ".java", ".ts", ".tsx", ".js", ".jsx", ".py", ".sql", ".xml", ".swift", ".go", ".rs"}:
            continue
        try:
            if pat.search(p.read_text(encoding="utf-8", errors="ignore")):
                hits.append(p.relative_to(Path(root).resolve()).as_posix())
        except OSError:
            pass
    return sorted(hits)


def print_plan(plan):
    w = max((len(r["id"]) for r in plan), default=4)
    for r in plan:
        print(f"{r['action']:<6} T{r['tier']}  {r['id']:<{w}}  {r['reason']}")
    run = sum(r["action"] == "RUN" for r in plan)
    reuse = sum(r["action"] == "REUSE" for r in plan)
    defer = sum(r["action"] == "DEFER" for r in plan)
    print(f"\nSummary: RUN {run} | REUSE {reuse} | DEFER {defer} (deferred tests are NOT RUN and must be listed as such in the report)")


def self_test():
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp)
        (ws / "src").mkdir()
        (ws / "src/rule.py").write_text("def rule(x): return x < 16\n")
        (ws / "src/ui.py").write_text("def card(): return 'ok'\n")
        (ws / ".agents").mkdir()
        manifest = {"tests": [
            {"id": "UNIT-rule", "tier": 1, "cmd": "pytest rule", "deps": ["src/rule.py"]},
            {"id": "UI-card", "tier": 2, "cmd": "pytest ui", "deps": ["src/ui.py"]},
            {"id": "BOUNDARY", "tier": 1, "cmd": "pytest boundary", "deps": ["src/rule.py"], "always": True},
            {"id": "DEEP", "tier": 4, "cmd": "replay", "deps": ["src/**/*.py"]},
            {"id": "ORPHAN", "tier": 1, "cmd": "x", "deps": ["nothing/*.py"]}]}
        (ws / ".agents" / MANIFEST).write_text(json.dumps(manifest))
        by = lambda plan: {r["id"]: r for r in plan}
        p = by(select(ws, 2))
        assert p["UNIT-rule"]["action"] == "RUN" and p["UNIT-rule"]["reason"] == "never run"
        assert p["DEEP"]["action"] == "DEFER", "tier above ceiling must be deferred, not passed"
        for tid in ("UNIT-rule", "UI-card", "BOUNDARY", "ORPHAN"):
            cmd_record(ws, tid, "pass", "")
        p = by(select(ws, 2))
        assert p["UNIT-rule"]["action"] == "REUSE" and p["UI-card"]["action"] == "REUSE"
        assert p["BOUNDARY"]["action"] == "RUN", "always-run test must never be reused"
        assert p["ORPHAN"]["action"] == "RUN", "tests with unmatched deps must fail safe"
        (ws / "src/rule.py").write_text("def rule(x): return x < 17\n")  # change rule only
        p = by(select(ws, 2))
        assert p["UNIT-rule"]["action"] == "RUN" and "src/rule.py" in p["UNIT-rule"]["reason"]
        assert p["UI-card"]["action"] == "REUSE", "unrelated UI test must be reused"
        cmd_record(ws, "UNIT-rule", "fail", "boom")
        assert by(select(ws, 2))["UNIT-rule"]["action"] == "RUN", "a failed result is never reused"
        assert cmd_status(ws)["failed"] == 1
        assert cmd_deps_suggest(ws, "rule") == ["src/rule.py"]
    print(json.dumps({"status": "PASS", "checks": [
        "select: never-run, tier deferral, always-run, orphan fail-safe",
        "record + reuse on identical hashes", "change invalidates only dependent tests",
        "failed results never reused", "deps-suggest finds symbol files"]}, indent=2))


def main():
    ap = argparse.ArgumentParser(description="MACA impact selector + evidence cache")
    ap.add_argument("command", nargs="?", choices=["select", "record", "status", "invalidate", "deps-suggest"])
    ap.add_argument("--ws")
    ap.add_argument("--root")
    ap.add_argument("--symbol")
    ap.add_argument("--max-tier", type=int)
    ap.add_argument("--id")
    ap.add_argument("--status", choices=["pass", "fail"])
    ap.add_argument("--note", default="")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    try:
        if a.self_test:
            return self_test()
        if not a.command:
            return ap.print_help()
        if a.command == "deps-suggest":
            if not (a.root and a.symbol):
                fail("Usage", "--root and --symbol required", "deps-suggest --root R --symbol NAME")
            for f in cmd_deps_suggest(a.root, a.symbol):
                print(f)
            return
        if not a.ws:
            fail("Usage", "--ws required", "Pass the workspace directory")
        if a.command == "select":
            plan = select(a.ws, a.max_tier)
            print(json.dumps(plan, indent=2) if a.json else "", end="" if a.json else "")
            if not a.json:
                print_plan(plan)
        elif a.command == "record":
            if not (a.id and a.status):
                fail("Usage", "--id and --status required", "record --ws W --id ID --status pass|fail")
            cmd_record(a.ws, a.id, a.status, a.note)
            print(f"recorded {a.id}: {a.status}")
        elif a.command == "status":
            print(json.dumps(cmd_status(a.ws), indent=2))
        elif a.command == "invalidate":
            path = agents_dir(a.ws) / EVIDENCE
            data = load_json(path, {"tests": {}}) or {"tests": {}}
            if a.all:
                data["tests"] = {}
            elif a.id:
                data["tests"].pop(a.id, None)
            else:
                fail("Usage", "--id or --all required", "invalidate --ws W --id ID | --all")
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            print("invalidated")
    except SystemExit:
        raise
    except Exception as exc:  # fail closed, same convention as the other MACA scripts
        fail(type(exc).__name__, str(exc), "Run with --self-test to diagnose impact_and_cache.py")


if __name__ == "__main__":
    main()
