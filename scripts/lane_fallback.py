#!/usr/bin/env python3
"""Run one MACA lane through a fallback chain of models so a dead or silent provider never stops the work.

Tries each 'cli:model' in --chain in order. An attempt counts as failed when the relay does not finish with status
'completed', returns no text, or (for a read-only lane) changed source files (app/ or .agents/checks; edits the orchestrator makes elsewhere in the repo meanwhile are ignored). On failure the next model in the chain is tried; the
log of every attempt is written to <out-dir>/fallback.json and the winning text to <out-dir>/final.md.
Exit 0 = some model completed, 3 = whole chain failed (the caller decides; never silently).
"""
import argparse, json, os, subprocess, sys, time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--self-test", action="store_true", help="check the argument gate without running any relay")
ap.add_argument("--write-approved-by", default="", help="a writing lane (no --read-only) needs a person's name here, matching the profile's Write-lane permissions")
ap.add_argument("--brief")
ap.add_argument("--cd")
ap.add_argument("--out-dir")
ap.add_argument("--chain", help="comma list of cli:model, e.g. claude:claude-sonnet-5-5,opencode:openai/gpt-6-luna")
ap.add_argument("--read-only", action="store_true")
ap.add_argument("--timeout-ms", type=int, default=600000, help="per-attempt relay timeout (default 10 min)")
ap.add_argument("--min-chars", type=int, default=400)
ap.add_argument('--no-edits-ok', action='store_true', help='for a writing lane: accept a run that changed no file (default: a writing lane that touches nothing counts as failed, e.g. it only asked for approval)')
a = ap.parse_args()

NON_HUMAN = {"", "ai", "agent", "assistant", "orchestrator", "claude", "auto", "unattended", "assumed", "self", "none"}

def gate_error(args):
    """Return a reason the run must not start, or None. A writing lane is a permission grant, so it must name who granted it."""
    missing = [n for n in ("brief", "cd", "out_dir", "chain") if not getattr(args, n)]
    if missing:
        return "missing required arguments: " + ", ".join("--" + m.replace("_", "-") for m in missing)
    if not args.read_only and args.write_approved_by.strip().lower() in NON_HUMAN:
        return "writing lane needs --write-approved-by <person> (see Write-lane permissions in the profile); otherwise pass --read-only"
    return None

if a.self_test:
    P = ap.parse_args
    ok = gate_error(P(["--brief", "b", "--cd", "c", "--out-dir", "o", "--chain", "claude", "--read-only"])) is None
    no_approval = gate_error(P(["--brief", "b", "--cd", "c", "--out-dir", "o", "--chain", "claude"])) is not None
    ai_approval = gate_error(P(["--brief", "b", "--cd", "c", "--out-dir", "o", "--chain", "claude", "--write-approved-by", "orchestrator"])) is not None
    human = gate_error(P(["--brief", "b", "--cd", "c", "--out-dir", "o", "--chain", "claude", "--write-approved-by", "Dr. Sara"])) is None
    missing = gate_error(P([])) is not None
    assert ok and no_approval and ai_approval and human and missing, (ok, no_approval, ai_approval, human, missing)
    print(json.dumps({"self_test_status": "PASS", "checks_executed": 5}))
    sys.exit(0)

err = gate_error(a)
if err:
    print(json.dumps({"status": "MACA_SCRIPT_ERROR — STOP_AND_FIX", "message": err}), file=sys.stderr)
    sys.exit(2)

def tree_state(cd):
    """Fingerprint of the working tree under cd (git status + diff). Used to tell whether a writing lane really changed anything, even in files that were already modified."""
    try:
        st = subprocess.run(['git', '-C', cd, 'status', '--porcelain'], capture_output=True, text=True).stdout
        df = subprocess.run(['git', '-C', cd, 'diff'], capture_output=True, text=True).stdout
        return hash((st, df))
    except Exception:
        return None

a.brief, a.cd, a.out_dir = (str(Path(x).resolve()) for x in (a.brief, a.cd, a.out_dir))   # relays run with cwd=--cd, so paths must be absolute

SK = Path(__file__).resolve().parent.parent / "vendor/delegate-skills/skills"
out = Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
log = []
for i, spec in enumerate(s for s in a.chain.split(",") if s):
    cli, _, model = spec.partition(":")
    adir = out / f"attempt-{i}-{cli}-{model.replace('/', '_')}"
    cmd = ["node", str(SK / f"{cli}-delegate/scripts/relay.mjs"), "--brief", a.brief, "--cd", a.cd, "--out-dir", str(adir)]
    if model and cli != "claude": cmd += ["--model", model]
    if a.read_only: cmd.append("--read-only")
    env = dict(os.environ, MACA_RELAY_TIMEOUT_MS=str(a.timeout_ms))
    if cli == "claude" and model: env["ANTHROPIC_MODEL"] = model   # claude relay drops --model
    before_state = tree_state(a.cd)
    t = time.time()
    subprocess.run(cmd, env=env, cwd=a.cd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    secs = round(time.time() - t, 1)
    status, text, why, touched = "no-result", "", "", []
    try:
        r = json.loads((adir / "result.json").read_text())
        status, touched = r.get("status"), r.get("touchedFiles") or []
        text = r.get("finalMessage", "")
        why = (r.get("stderrTail") or "")[-200:]
        so = adir / "stdout.txt"
        if so.exists() and len(so.read_text()) > len(text): text = so.read_text()   # relay truncates finalMessage at ~4000 chars
    except Exception as e:
        why = str(e)
    after_state = tree_state(a.cd)
    changed = bool(touched) or (before_state is not None and before_state != after_state)
    wrote_nothing = (not a.read_only) and (not a.no_edits_ok) and not changed
    if wrote_nothing: why = (why + " no file changed").strip()
    ok = status == "completed" and not wrote_nothing and len(text.strip()) >= a.min_chars and not (a.read_only and any(t.startswith('app/') or t.startswith('.agents/checks') for t in touched))
    log.append(dict(spec=spec, status=status, seconds=secs, chars=len(text), ok=ok, why="" if ok else why))
    (out / "fallback.json").write_text(json.dumps(log, indent=1))
    print(f"[fallback] {spec}: {status} {secs}s {len(text)} chars -> {'OK' if ok else 'next'}", flush=True)
    if ok:
        (out / "final.md").write_text(text)
        sys.exit(0)
print("[fallback] whole chain failed", flush=True)
sys.exit(3)
