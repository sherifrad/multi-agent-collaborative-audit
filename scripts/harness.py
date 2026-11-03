#!/usr/bin/env python3
"""MACA harness library: save a script once, reuse it forever (stdlib only).

Why: an agent that rewrites the same helper script on every task pays tokens each time and risks a
slightly different script each time. The "rule of two": the second time the same need appears, the
script is written once, registered here, and from then on called by name. A reused script costs
(almost) zero tokens, and its hash is verified before it runs so a silently edited copy is never trusted.

Two libraries:
  project : <workspace>/.agents/harness/   (scripts specific to this project)
  global  : <skill dir>/harness/           (general-purpose scripts promoted for use in any project)

Commands:
  check    --ws W --need "what the script must do" [--name n]   look before you write
  register --ws W --file F --name N --purpose P [--tags a,b] [--scope project|global] [--self-test-cmd CMD]
  run      --ws W NAME [-- args...]                              verify hash, execute, count the use
  list     --ws W
  find     --ws W keyword [keyword...]
  adopt    --ws W --file DIR [--scope S]                        register every reusable script in an existing folder
  promote  --ws W NAME                                           copy a project script to the global library
  --self-test

`check` prints a first-word verdict an agent can act on:
  FOUND <name>   -> use `run`, do not write a new script
  NEW            -> first time this need appears: write inline, nothing to register yet
  PROMOTE        -> second time: write it once, then `register` it
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
RUNNERS = {".py": [sys.executable], ".sh": ["bash"], ".mjs": ["node"], ".js": ["node"]}
STOP = {"the", "and", "for", "that", "with", "from", "into", "script", "file", "files", "this", "make", "run"}


def fail(code, msg, fix):
    print(json.dumps({"status": "MACA_SCRIPT_ERROR — STOP_AND_FIX", "error_code": code, "message": msg,
                      "remediation": fix}, indent=2), file=sys.stderr)
    sys.exit(2)


def lib_dir(ws, scope):
    d = (Path(ws).resolve() / ".agents" / "harness") if scope == "project" else (SKILL_DIR / "harness")
    d.mkdir(parents=True, exist_ok=True)
    return d


def load(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail("BadJson", f"{path}: {exc}", f"Fix or delete {path}")


def save(path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def words(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 2 and w not in STOP}


def registry(ws, scope):
    return load(lib_dir(ws, scope) / "HARNESS.json", {"scripts": {}})


def entries(ws):
    """All entries, project first so a project script shadows a global one with the same name."""
    seen, out = set(), []
    for scope in ("project", "global"):
        for name, e in registry(ws, scope)["scripts"].items():
            if name not in seen:
                seen.add(name)
                out.append((scope, name, e))
    return out


def match(ws, text):
    q = words(text)
    scored = []
    for scope, name, e in entries(ws):
        hay = words(name.replace("-", " ").replace("_", " ") + " " + e.get("purpose", "") + " " + " ".join(e.get("tags", [])))
        overlap = len(q & hay)
        if overlap >= 2 or (q and q <= hay):
            scored.append((overlap, scope, name, e))
    scored.sort(key=lambda t: -t[0])
    return scored


def cmd_check(ws, need, name):
    hits = match(ws, need + " " + (name or ""))
    if hits:
        _, scope, n, e = hits[0]
        return f"FOUND {n} [{scope}] v{e['version']} used {e['uses']}x: {e['purpose']}  |  usage: {e.get('usage') or 'see --help'}  ->  harness.py run --ws <ws> {n} -- <args>"
    needs_path = lib_dir(ws, "project") / "NEEDS.json"
    needs = load(needs_path, {})
    key = " ".join(sorted(words(need)))[:120] or (name or "unnamed")
    # a repeated need is recognised by overlapping vocabulary with an earlier one
    for k in list(needs):
        if len(set(k.split()) & set(key.split())) >= max(2, min(len(k.split()), len(key.split())) // 2):
            key = k
            break
    rec = needs.setdefault(key, {"count": 0, "first": time.strftime("%Y-%m-%d")})
    rec["count"] += 1
    save(needs_path, needs)
    if rec["count"] >= 2:
        return f"PROMOTE this need has now appeared {rec['count']} times: write the script once, then run `harness.py register`"
    return "NEW first time this need appears: write it inline; it will be promoted if it comes up again"


ABS_PATH_RE = re.compile(r"""["'](/(?:Users|home|private|tmp|var)/[^"'\s]*|[A-Za-z]:\\\\[^"'\s]*)["']""")


def header_field(src, field):
    """Text after `Usage:` / `Purpose:` in the first lines (comment or docstring), else empty."""
    head = "\n".join(src.read_text(encoding="utf-8", errors="replace").splitlines()[:12])
    m = re.search(field + r":\s*(.+)", head)
    return m.group(1).strip().strip('"\'#').strip() if m else ""


def cmd_adopt(ws, directory, scope):
    """Register every reusable script found in an existing folder; report the ones refused and why."""
    done, refused = [], []
    for f in sorted(Path(directory).resolve().iterdir()):
        if not f.is_file() or f.suffix not in RUNNERS or f.name == "harness.py":
            continue
        problems = lint_script(f)
        purpose = header_field(f, "Purpose")
        if problems or not purpose:
            refused.append(f"{f.name}: " + ("; ".join(problems) or "no Purpose: line"))
            continue
        name = re.sub(r"[^a-z0-9-]", "-", f.stem.lower())
        done.append(cmd_register(ws, str(f), name, purpose, "", scope, None))
    return "\n".join(["adopted:"] + ["  " + d for d in done] + ["refused (fix the header/args, then adopt again):"] + ["  " + r for r in refused])


def lint_script(src):
    """Reusable-script contract: self-describing, parameterised, no hardcoded machine paths. Returns problems."""
    text = src.read_text(encoding="utf-8", errors="replace")
    head = "\n".join(text.splitlines()[:12])
    problems = []
    if not (re.search(r"Usage:", head) and re.search(r"Purpose:", head)):
        problems.append("the first lines must state `Usage:` and `Purpose:` so another agent can read them with `head`")
    if src.suffix == ".py" and "argparse" not in text:
        problems.append("a Python script must take its targets from argparse arguments (it must answer --help)")
    hit = ABS_PATH_RE.search(text)
    if hit:
        problems.append(f"hardcoded machine path {hit.group(1)!r}: take it from an argument")
    return problems


def cmd_register(ws, file, name, purpose, tags, scope, self_test_cmd):
    src = Path(file).resolve()
    if not src.is_file():
        fail("NoFile", f"{src} not found", "Pass an existing script with --file")
    if src.suffix not in RUNNERS:
        fail("BadType", f"{src.suffix} not supported", f"Use one of {sorted(RUNNERS)}")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", name):
        fail("BadName", name, "Use lowercase letters, digits, '-' or '_'")
    problems = lint_script(src)
    if problems:
        fail("NotReusable", "; ".join(problems), "Generalise the script (docstring, argparse, no fixed paths), then register again")
    if self_test_cmd:
        proc = subprocess.run(self_test_cmd, shell=True, capture_output=True, text=True, cwd=str(src.parent))
        if proc.returncode != 0:
            fail("SelfTestFailed", (proc.stdout + proc.stderr)[-400:], "Fix the script; a script must pass its own check to be registered")
    d = lib_dir(ws, scope)
    reg_path = d / "HARNESS.json"
    reg = load(reg_path, {"scripts": {}})
    dest = d / (name + src.suffix)
    new_hash = sha(src)
    prev = reg["scripts"].get(name)
    version = 1
    uses = 0
    if prev:
        uses = prev.get("uses", 0)
        version = prev["version"] if prev["sha256"] == new_hash else prev["version"] + 1
    shutil.copyfile(src, dest)
    reg["scripts"][name] = {"file": dest.name, "sha256": new_hash, "version": version, "purpose": purpose,
                            "tags": [t for t in (tags or "").split(",") if t], "uses": uses,
                            "created": (prev or {}).get("created", time.strftime("%Y-%m-%d")),
                            "self_test_cmd": self_test_cmd or "", "usage": header_field(src, "Usage")}
    save(reg_path, reg)
    return f"registered {name} v{version} [{scope}] sha256={new_hash[:12]}"


def locate(ws, name):
    for scope in ("project", "global"):
        reg = registry(ws, scope)
        if name in reg["scripts"]:
            return scope, reg, reg["scripts"][name]
    fail("Unknown", f"No harness script '{name}'", "Use `list` or `find` to see what exists")


def cmd_run(ws, name, args):
    scope, reg, e = locate(ws, name)
    path = lib_dir(ws, scope) / e["file"]
    if not path.is_file() or sha(path) != e["sha256"]:
        fail("HashMismatch", f"{path} changed since it was registered",
             "Do not run it. Review the change, then re-register (version bumps) or restore the file")
    runner = RUNNERS[path.suffix]
    e["uses"] += 1
    e["last_run"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save(lib_dir(ws, scope) / "HARNESS.json", reg)
    return subprocess.call(runner + [str(path)] + list(args))


def cmd_promote(ws, name):
    reg = registry(ws, "project")
    if name not in reg["scripts"]:
        fail("Unknown", f"'{name}' is not a project script", "Register it first")
    e = reg["scripts"][name]
    src = lib_dir(ws, "project") / e["file"]
    if sha(src) != e["sha256"]:
        fail("HashMismatch", "project copy changed since registration", "Re-register before promoting")
    return cmd_register(ws, str(src), name, e["purpose"], ",".join(e.get("tags", [])), "global", e.get("self_test_cmd") or None)


def cmd_list(ws):
    rows = [f"{n:<24} [{s}] v{e['version']} uses={e['uses']}  {e['purpose']}" for s, n, e in entries(ws)]
    return "\n".join(rows) if rows else "(no harness scripts yet)"


def self_test():
    global SKILL_DIR
    real_skill_dir = SKILL_DIR
    with tempfile.TemporaryDirectory() as tmp:
        SKILL_DIR = Path(tmp) / "skill"  # never touch the real global library in a self-test
        ws = Path(tmp) / "ws"
        ws.mkdir()
        s = Path(tmp) / "clean_csv.py"
        hdr = '"""Usage: clean_csv.py FILE...\nPurpose: clean csv files."""\nimport argparse\n'
        s.write_text(hdr + "print('cleaned')\n")
        bad = Path(tmp) / "bad.py"
        bad.write_text("print(open('/Users/someone/data.csv').read())\n")
        try:
            cmd_register(ws, str(bad), "bad", "p", "", "project", None)
            raise AssertionError("non-reusable script must be refused")
        except SystemExit as exc:
            assert exc.code == 2, exc.code
        v = cmd_check(ws, "clean csv files remove blank rows", None)
        assert v.startswith("NEW"), v
        v = cmd_check(ws, "remove blank rows from csv files", None)
        assert v.startswith("PROMOTE"), v
        cmd_register(ws, str(s), "clean-csv", "clean csv files remove blank rows", "csv,clean", "project", "python3 clean_csv.py x")
        v = cmd_check(ws, "need to remove blank rows from a csv", None)
        assert v.startswith("FOUND clean-csv"), v
        assert cmd_run(ws, "clean-csv", ["a.csv"]) == 0
        assert registry(ws, "project")["scripts"]["clean-csv"]["uses"] == 1
        old = Path(tmp) / "oldscripts"
        old.mkdir()
        (old / "count_lines.py").write_text('"""Usage: count_lines.py FILE...\nPurpose: count lines in files."""\nimport argparse\n')
        (old / "legacy.py").write_text("print(1)\n")
        out = cmd_adopt(ws, str(old), "project")
        assert "count-lines" in out and "legacy.py" in out.split("refused")[1], out
        assert "usage: count_lines.py FILE" in cmd_check(ws, "count lines in files", None)
        # same content re-registered keeps the version; changed content bumps it
        cmd_register(ws, str(s), "clean-csv", "p", "csv", "project", None)
        assert registry(ws, "project")["scripts"]["clean-csv"]["version"] == 1
        s.write_text(hdr + "print('changed')\n")
        cmd_register(ws, str(s), "clean-csv", "p", "csv", "project", None)
        assert registry(ws, "project")["scripts"]["clean-csv"]["version"] == 2
        # tamper detection
        (lib_dir(ws, "project") / "clean-csv.py").write_text("print('evil')\n")
        try:
            cmd_run(ws, "clean-csv", [])
            raise AssertionError("tampered script must not run")
        except SystemExit as exc:
            assert exc.code == 2
        # promotion to global requires an untampered copy
        (lib_dir(ws, "project") / "clean-csv.py").write_text(hdr + "print('changed')\n")
        assert "registered" in cmd_promote(ws, "clean-csv")
        assert "clean-csv" in registry(ws, "global")["scripts"]
    SKILL_DIR = real_skill_dir
    print(json.dumps({"status": "PASS", "checks": [
        "check: NEW then PROMOTE on the second similar need", "register + self-test gate",
        "check finds the saved script (FOUND)", "run counts uses", "re-register: same hash keeps version, changed hash bumps it",
        "tampered script refused", "adopt registers an existing folder and refuses non-general scripts", "FOUND shows the usage line", "register refuses scripts without Usage/Purpose, argparse, or with fixed machine paths", "promote project -> global"]}, indent=2))


def main():
    ap = argparse.ArgumentParser(description="MACA harness library")
    ap.add_argument("command", nargs="?", choices=["check", "register", "run", "list", "find", "promote", "adopt"])
    ap.add_argument("rest", nargs="*")
    ap.add_argument("--ws", default=".")
    ap.add_argument("--need")
    ap.add_argument("--name")
    ap.add_argument("--file")
    ap.add_argument("--purpose", default="")
    ap.add_argument("--tags", default="")
    ap.add_argument("--scope", choices=["project", "global"], default="project")
    ap.add_argument("--self-test-cmd")
    ap.add_argument("--self-test", action="store_true")
    a, extra = ap.parse_known_args()
    try:
        if a.self_test:
            return self_test()
        if not a.command:
            return ap.print_help()
        if a.command == "check":
            if not a.need:
                fail("Usage", "--need required", 'check --ws W --need "what the script must do"')
            print(cmd_check(a.ws, a.need, a.name))
        elif a.command == "adopt":
            if not a.file:
                fail("Usage", "--file DIR required", "adopt --ws W --file <folder of scripts> [--scope project|global]")
            print(cmd_adopt(a.ws, a.file, a.scope))
        elif a.command == "register":
            if not (a.file and a.name and a.purpose):
                fail("Usage", "--file, --name and --purpose required", "register --ws W --file F --name N --purpose P")
            print(cmd_register(a.ws, a.file, a.name, a.purpose, a.tags, a.scope, a.self_test_cmd))
        elif a.command == "run":
            if not a.rest:
                fail("Usage", "script name required", "run --ws W NAME -- args")
            args = a.rest[1:] + [x for x in extra if x != "--"]
            sys.exit(cmd_run(a.ws, a.rest[0], args))
        elif a.command == "list":
            print(cmd_list(a.ws))
        elif a.command == "find":
            hits = match(a.ws, " ".join(a.rest))
            print("\n".join(f"{n} [{s}] {e['purpose']}" for _, s, n, e in hits) or "(no match)")
        elif a.command == "promote":
            print(cmd_promote(a.ws, a.rest[0] if a.rest else a.name))
    except SystemExit:
        raise
    except Exception as exc:
        fail(type(exc).__name__, str(exc), "Run harness.py --self-test to diagnose")


if __name__ == "__main__":
    main()
