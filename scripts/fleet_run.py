#!/usr/bin/env python3
"""Run one MACA lane through the upstream delegate relays, with a fallback chain.

This is a thin layer over vendor/delegate-skills/skills/<cli>-delegate/scripts/relay.mjs (unmodified upstream). It adds only
what the relays do not: trying the next candidate, a fingerprint check that a read-only lane changed nothing, and the rule
that a writing lane names the person who allowed it. Who is in the chain, and at which tier, comes from model_router.py
(its `chain` already obeys the rule that a reviewer is never replaced by a weaker model on risky work).

  fleet_run.py --brief B --cd REPO --out-dir O --chain 'agy:gemini-3.8-flash-high,claude:sonnet@high' --read-only
  chain item = cli[:model][@effort]   (effort is passed to relays that support it: claude, codex, agy)

Exit 0 a candidate completed; 3 the whole chain failed or stopped (QUOTA_EXHAUSTED if every failure was a quota/limit error).
Each attempt gets its own folder O/<cli>-<model>/ (the referee reads these names to check vendor approval) and O/dispatch.log.
"""
import argparse, hashlib, json, re, subprocess, sys, time
from pathlib import Path

SK = Path(__file__).resolve().parent.parent / "vendor" / "delegate-skills" / "skills"
NON_HUMAN = {"", "ai", "agent", "assistant", "orchestrator", "claude", "auto", "unattended", "assumed", "self", "none",
             "gemini", "codex", "opencode", "agy", "gpt", "bot", "subagent"}
EFFORT_CLIS = {"claude", "codex", "agy"}
QUOTA = re.compile(r"quota|usage limit|rate.?limit|429|resource_exhausted|free usage limit|exceeded", re.I)


def gate_error(a):
    miss = [n for n in ("brief", "cd", "out_dir", "chain") if not getattr(a, n)]
    if miss:
        return "missing required arguments: " + ", ".join("--" + m.replace("_", "-") for m in miss)
    if not a.read_only and (a.write_approved_by or "").strip().lower() in NON_HUMAN:
        return "a writing lane needs --write-approved-by <person> (the profile's Write-lane permissions); otherwise pass --read-only"
    return None


def tree_state(cd):
    """sha256 of git status + diff: tells whether a lane changed anything, even in files that were already modified."""
    try:
        out = "".join(subprocess.run(["git", "-C", cd, *args], capture_output=True, text=True).stdout for args in (["status", "--porcelain"], ["diff"]))
        return hashlib.sha256(out.encode()).hexdigest()
    except Exception:
        return None


def parse_item(spec):
    m = re.fullmatch(r"([a-z]+)(?::([^@]+))?(?:@(low|medium|high))?", spec.strip())
    if not m:
        raise ValueError(f"bad chain item '{spec}' (use cli[:model][@effort])")
    return m.group(1), m.group(2) or "", m.group(3) or ""


def build_cmd(cli, model, effort, a, adir):
    cmd = ["node", str(SK / f"{cli}-delegate/scripts/relay.mjs"), "--brief", a.brief, "--cd", a.cd, "--out-dir", str(adir),
           "--timeout", f"{max(60, a.timeout_s)}s"]
    if model:
        cmd += ["--model", model]
    if effort and cli in EFFORT_CLIS and not re.search(r"-(low|medium|high)$", model):   # agy ids bake the effort in; --effort then conflicts
        cmd += ["--effort", effort]
    if a.read_only:
        cmd.append("--read-only")
    return cmd


def classify(result, text, changed, a):
    """Return (ok, why, quota)."""
    status = result.get("status")
    blob = " ".join(str(result.get(k, "")) for k in ("stderrTail", "finalMessage")) + text
    if status != "completed":
        return False, f"relay status {status}: {str(result.get('stderrTail', ''))[-160:]}", bool(QUOTA.search(blob))
    if a.read_only and (result.get("readOnlyViolation") or changed):
        return False, "read-only lane changed the working tree", False
    if not a.read_only and not a.no_edits_ok and not changed and not (result.get("touchedFiles") or []):
        return False, "writing lane changed no file", False
    if len(text.strip()) < a.min_chars:
        return False, f"answer shorter than {a.min_chars} chars", False
    return True, "", False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--brief"); ap.add_argument("--cd"); ap.add_argument("--out-dir"); ap.add_argument("--chain")
    ap.add_argument("--read-only", action="store_true")
    ap.add_argument("--write-approved-by", default="")
    ap.add_argument("--no-edits-ok", action="store_true")
    ap.add_argument("--timeout-s", type=int, default=600)
    ap.add_argument("--min-chars", type=int, default=200)
    a = ap.parse_args()
    if a.self_test:
        return self_test(ap)
    err = gate_error(a)
    if err:
        print(json.dumps({"status": "MACA_SCRIPT_ERROR - STOP_AND_FIX", "message": err}), file=sys.stderr)
        sys.exit(2)
    a.brief, a.cd, a.out_dir = (str(Path(x).resolve()) for x in (a.brief, a.cd, a.out_dir))
    out = Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
    log, quota_only = [], True
    for spec in [s for s in a.chain.split(",") if s.strip()]:
        cli, model, effort = parse_item(spec)
        adir = out / f"{cli}-{re.sub(r'[^A-Za-z0-9._-]', '_', model) or 'default'}"
        before, t0 = tree_state(a.cd), time.time()
        subprocess.run(build_cmd(cli, model, effort, a, adir), cwd=a.cd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            r = json.loads((adir / "result.json").read_text())
        except Exception as e:
            r = {"status": "no-result", "stderrTail": str(e)}
        fp = r.get("finalPath")
        text = (Path(fp).read_text() if fp and Path(fp).exists() else "") or r.get("finalMessage", "") or ""
        ok, why, quota = classify(r, text, before is not None and tree_state(a.cd) != before, a)
        log.append({"spec": spec, "status": r.get("status"), "seconds": round(time.time() - t0, 1), "chars": len(text), "ok": ok, "why": why, "quota": quota})
        (out / "dispatch.log").write_text(json.dumps(log, indent=1))
        print(f"[fleet_run] {spec}: {r.get('status')} {len(text)} chars -> {'OK' if ok else 'next'}", flush=True)
        if ok:
            (out / "final.md").write_text(text)
            sys.exit(0)
        quota_only = quota_only and quota
    print("[fleet_run] QUOTA_EXHAUSTED: every candidate hit a quota or limit" if quota_only and log else "[fleet_run] whole chain failed", flush=True)
    sys.exit(3)


def self_test(ap):
    P = ap.parse_args
    base = ["--brief", "b", "--cd", "c", "--out-dir", "o", "--chain", "claude"]
    assert gate_error(P(base + ["--read-only"])) is None
    assert gate_error(P(base)) and gate_error(P(base + ["--write-approved-by", "orchestrator"])) and gate_error(P(base + ["--write-approved-by", "Agy"]))
    assert gate_error(P(base + ["--write-approved-by", "Dr. Sara"])) is None and gate_error(P([]))
    assert parse_item("agy:gemini-3.8-flash-high@medium") == ("agy", "gemini-3.8-flash-high", "medium") and parse_item("claude") == ("claude", "", "")
    a = P(base + ["--read-only"])
    long = "x" * 400
    assert classify({"status": "completed"}, long, False, a)[0]
    assert not classify({"status": "completed", "readOnlyViolation": True}, long, False, a)[0]
    assert not classify({"status": "completed"}, long, True, a)[0]
    assert classify({"status": "failed", "stderrTail": "RESOURCE_EXHAUSTED 429 Individual quota reached"}, "", False, a)[2]
    assert not classify({"status": "failed", "stderrTail": "syntax error"}, "", False, a)[2]
    w = P(base + ["--write-approved-by", "Dr. Sara"])
    assert not classify({"status": "completed"}, long, False, w)[0] and classify({"status": "completed", "touchedFiles": [" M a"]}, long, False, w)[0]
    cmd = build_cmd("agy", "m", "high", a, Path("o"))
    assert "--read-only" in cmd and "--effort" in cmd and "--timeout" in cmd and "opencode" not in " ".join(cmd)
    assert "--effort" not in build_cmd("opencode", "m", "high", a, Path("o"))
    assert "--effort" not in build_cmd("agy", "gemini-3.8-flash-high", "low", a, Path("o")) and "--effort" in build_cmd("claude", "sonnet", "low", a, Path("o"))
    print(json.dumps({"self_test_status": "PASS", "checks_executed": 10}))


if __name__ == "__main__":
    main()
