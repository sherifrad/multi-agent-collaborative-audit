#!/usr/bin/env python3
"""
MACA referee (scripts/skill_ambassador_auditor.py), stdlib only.

Checks that a workspace's .agents/ records contain real evidence for the gates SKILL.md requires, instead of
matching keywords. The old v2 referee passed on words like "incremental" or "persistence" appearing anywhere;
this one reads structured records:

  REVIEW:     id=R-1 author=<who> reviewer=<who> independence=<multi-vendor|same-family|single-model|same-model>
              round=1 evidence=<file path or command> verdict=<pass|blockers|deferred>
  APPROVAL:   what=<ui-mock|vendor:codex|tier-ceiling:3|...> by=<a person> date=YYYY-MM-DD
  ASSUMPTION: what=<decision taken in place of an answer> default=<what was chosen>

Gate statuses
  PASS          evidence found and checked
  VIOLATION     evidence missing or contradicted            -> verdict BLOCKED_BY_SKILL_VIOLATIONS, exit 1
  NOT_VERIFIED  the gate applies but could not be checked   -> verdict INCOMPLETE_NOT_VERIFIED,      exit 3
                (a linter that scanned 0 files, an unknown domain, a deferred test above the ceiling)
  NOT_APPLICABLE  the profile/flags say the gate does not apply; excluded from the score, reason shown

Exit 0 only when every applicable gate is PASS. Which domain gates apply comes from `.agents/PROJECT_PROFILE.md`
("Domains / packs") or --domains; with neither, domain gates are NOT_VERIFIED rather than silently skipped.
"""

import argparse
import concurrent.futures
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

SCRIPT_DIR = Path(__file__).resolve().parent
SAMD_LINTER_PATH = SCRIPT_DIR / "lint_samd_invariants.py"
DESIGN_LINTER_PATH = SCRIPT_DIR / "lint_design_and_ux.py"
CACHE_PATH = SCRIPT_DIR / "impact_and_cache.py"

INDEPENDENCE = {"multi-vendor", "same-family", "single-model", "same-model"}
NON_HUMAN = {"ai", "agent", "assistant", "orchestrator", "claude", "unattended", "assumed", "auto", "self", "none", "",
             "gemini", "codex", "opencode", "agy", "gpt", "opus", "sonnet", "haiku", "llm", "bot", "ci", "subagent", "reviewer", "builder", "tester"}
PACKS_DIR = SCRIPT_DIR.parent / "packs"
UI_WORDS = {"ui", "web", "web-app", "web-ui", "mobile", "android", "ios", "frontend", "compose"}
BASE_DOMAINS = {"core", "fintech", "systems", "data-etl", "clinical"}
UI_EXTS = {".html", ".htm", ".css", ".scss", ".vue", ".svelte", ".jsx", ".tsx", ".swift", ".storyboard", ".xib"}
UI_SKIP_DIRS = {".git", ".agents", "node_modules", "build", "dist", ".gradle", "__pycache__", "vendor"}


def load_packs() -> List[Dict[str, Any]]:
    out = []
    if PACKS_DIR.exists():
        for f in sorted(PACKS_DIR.glob("*/pack.json")):
            try:
                out.append(json.loads(f.read_text(encoding="utf-8")))
            except ValueError:
                continue
    return out


def ui_words() -> Set[str]:
    return set(UI_WORDS)


def known_domains() -> Set[str]:
    names = set(BASE_DOMAINS) | set(UI_WORDS)
    for p in load_packs():
        names |= set(p.get("domains", []))
    return names


def is_ui_file(path: Path) -> bool:
    ext = path.suffix.lower()
    if ext in UI_EXTS:
        return True
    if ext == ".xml":
        norm = path.as_posix().lower()
        return "res/layout" in norm or "res/values" in norm or "layout" in norm
    if ext in {".kt", ".java"}:
        return bool(re.search(r"^\s*import\s+(?:androidx\.compose|android\.(?:widget|view))\b", read(path), re.M))
    return False


def has_ui_evidence(scan_dir: Path, modified: List[Dict[str, str]], ws: Path) -> bool:
    if scan_dir.exists():
        for p in scan_dir.rglob("*"):
            if p.is_file() and not any(part in UI_SKIP_DIRS for part in p.parts) and is_ui_file(p):
                return True
    for h in modified:
        fp = ws / h["file"]
        if fp.is_file() and not any(part in UI_SKIP_DIRS for part in fp.parts) and is_ui_file(fp):
            return True
    return False
VENDORS = ("opencode", "codex", "gemini", "agy")  # claude is the local family; it needs no vendor approval


def emit_fail_closed_error(error_code: str, message: str, remediation: str) -> None:
    print(json.dumps({
        "status": "MACA_SCRIPT_ERROR — STOP_AND_FIX",
        "error_code": error_code,
        "message": message,
        "mandatory_agent_action": "DO NOT SKIP OR BYPASS THIS STEP. Fix the error described below and re-run, or halt and report UNKNOWN / HARNESS ERROR.",
        "remediation": remediation,
    }, indent=2), file=sys.stderr)
    sys.exit(2)


# ---------------------------------------------------------------- record parsing

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def records(text: str, tag: str) -> List[Dict[str, str]]:
    """Parse `TAG: k=v k=v ...` lines. Values may be quoted with double quotes to hold spaces."""
    out = []
    for line in text.splitlines():
        m = re.match(r"^\s*(?:[-*]\s*)?`?%s:\s*(.+?)`?\s*$" % tag, line)
        if not m:
            continue
        rec = {k.lower(): (v1 or v2).strip() for k, v1, v2 in re.findall(r'(\w+)=(?:"([^"]*)"|(\S+))', m.group(1))}
        out.append(rec)
    return out


def profile_field(profile: str, name: str) -> str:
    m = re.search(r"\*\*%s\*\*(?:\s*\([^)\n]*\))?[^\n:]*:[ \t]*(.*)" % re.escape(name), profile)
    val = m.group(1).strip() if m else ""
    return "" if is_placeholder(re.sub(r"\(inferred[^)]*\)", "", val)) else val


def confirmed_names(profile: str, name: str) -> Set[str]:
    """Names listed in a profile field. Inferred values grant nothing, so an inferred list is empty."""
    raw = profile_field(profile, name)
    if re.search(r"inferred", raw, re.I):
        return set()
    raw = re.split(r"\b(?:not|no|never|except|without|unless)\b", raw, maxsplit=1, flags=re.I)[0]
    return {t.lower() for t in re.split(r"[,;/\s|]+", re.sub(r"\(.*?\)", "", raw)) if re.fullmatch(r"[A-Za-z][\w.-]*", t)} - {"none", "n", "a", "na"}


def is_placeholder(text: str) -> bool:
    t = text.strip().strip("`*_-| ")
    return (not t) or bool(re.fullmatch(r"[\[<].*[\]>]", t))


# ---------------------------------------------------------------- gates

def gate(findings: List[Dict[str, str]], gid: str, name: str, status: str, detail: str) -> None:
    findings.append({"gate": f"{gid} ({name})", "status": status, "detail": detail})


def check_spec(ws: Path, findings) -> None:
    spec = read(ws / ".agents" / "SPEC_AND_AUDIT.md") or read(ws / "SPEC_AND_AUDIT.md")
    if not spec:
        return gate(findings, "S1", "Spec, call-chain map, oracles", "VIOLATION", "Missing .agents/SPEC_AND_AUDIT.md")
    sections = re.split(r"^#{1,4}\s+", spec, flags=re.M)
    chain_body = next((s for s in sections if re.match(r"[^\n]*call[- ]chain", s, re.I)), "")
    chain_rows = [l for l in chain_body.splitlines()[1:] if l.strip().startswith(("|", "-", "*")) and not re.fullmatch(r"[\s|:\-]+", l)]
    real_rows = [l for l in chain_rows if not re.search(r"\[[^\]]*\]|target function|upstream callers", l, re.I)]
    oracles = [m.group(1) for m in re.finditer(r"^\s*(?:[-*]\s*)?`?ORACLE-\w+`?:\s*(.+)$", spec, re.M) if not is_placeholder(m.group(1))]
    problems = []
    if not real_rows:
        problems.append("call-chain section has no filled-in row (only template placeholders or missing)")
    if not oracles:
        problems.append("no `ORACLE-<id>: <observable result>` lines with real content")
    if problems:
        return gate(findings, "S1", "Spec, call-chain map, oracles", "VIOLATION", "; ".join(problems))
    gate(findings, "S1", "Spec, call-chain map, oracles", "PASS", f"{len(real_rows)} call-chain row(s), {len(oracles)} oracle(s)")


def check_reviews(ws: Path, ledger: str, findings) -> None:
    reviews = records(ledger, "REVIEW")
    if not reviews:
        return gate(findings, "S2", "Independent review", "VIOLATION",
                    "No `REVIEW:` record in the ledger. Prose that mentions a review is not accepted as evidence.")
    problems = []
    for r in reviews:
        rid = r.get("id", "?")
        a, v = r.get("author", "").lower(), r.get("reviewer", "").lower()
        if not a or not v or a == v:
            problems.append(f"{rid}: reviewer must differ from author (author={a or '-'}, reviewer={v or '-'})")
        if r.get("independence", "") not in INDEPENDENCE:
            problems.append(f"{rid}: independence must be one of {sorted(INDEPENDENCE)}")
        ev = r.get("evidence", "")
        if not ev:
            problems.append(f"{rid}: no evidence")
        else:
            cand = [q for q in (ws / ev, ws / ".agents" / ev) if q.is_file()]
            is_cmd = bool(re.match(r"(?:node|python3?|pytest|npm|npx|cargo|go|bash|sh|\./\S+)\s", ev))
            if cand:
                inside = str(cand[0].resolve()).startswith(str(ws.resolve()))
                if not inside or cand[0].stat().st_size < 10:
                    problems.append(f"{rid}: evidence file '{ev}' is outside the workspace or empty")
            elif not is_cmd:
                problems.append(f"{rid}: evidence '{ev[:40]}' is neither an existing file nor a command that was run")
        if r.get("independence", "") == "multi-vendor" and not (ws / ".agents" / "fleet-runs").exists():
            problems.append(f"{rid}: independence=multi-vendor but there is no .agents/fleet-runs/ output")
    last = reviews[-1]
    if last.get("verdict", "") not in {"pass", "deferred"}:
        problems.append(f"latest review {last.get('id','?')} verdict is '{last.get('verdict','?')}', not pass/deferred")
    if problems:
        return gate(findings, "S2", "Independent review", "VIOLATION", "; ".join(problems))
    levels = sorted({r["independence"] for r in reviews})
    gate(findings, "S2", "Independent review", "PASS", f"{len(reviews)} review record(s), independence: {', '.join(levels)}")


def oracles_without_test(ws: Path, deferred_ids: Set[str] = frozenset()) -> List[str]:
    spec = read(ws / ".agents" / "SPEC_AND_AUDIT.md")
    ids = [m.group(1).upper() for m in re.finditer(r"^\s*(?:[-*]\s*)?`?(ORACLE-\w+)`?:\s*(.+)$", spec, re.M) if not is_placeholder(m.group(2))]
    try:
        tests = json.loads(read(ws / ".agents" / "TEST_MANIFEST.json")).get("tests", [])
    except ValueError:
        return []
    covered = {str(c).upper() for t in tests if str(t.get("id")) not in deferred_ids for c in (t.get("covers") or [])}
    return [i for i in dict.fromkeys(ids) if i not in covered]


def check_tests(ws: Path, max_tier: int, findings, not_verified: List[str]) -> None:
    if not (ws / ".agents" / "TEST_MANIFEST.json").exists():
        return gate(findings, "S3", "Tests and evidence cache", "VIOLATION", "Missing .agents/TEST_MANIFEST.json (no tests registered).")
    proc = subprocess.run([sys.executable, str(CACHE_PATH), "select", "--ws", str(ws), "--max-tier", str(max_tier), "--json"],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        return gate(findings, "S3", "Tests and evidence cache", "VIOLATION", f"impact_and_cache.py failed: {(proc.stderr or proc.stdout).strip()[:300]}")
    plan = json.loads(proc.stdout)
    # `always` tests are scheduled every round by design; at close they count as proven if a pass is recorded against the current deps
    pending = [t for t in plan if t["action"] == "RUN" and not (t.get("always") and t.get("proven_now"))]
    deferred = [t for t in plan if t["action"] == "DEFER"]
    for t in deferred:
        not_verified.append(f"{t['id']} (tier {t['tier']} above ceiling {max_tier}): NOT RUN")
    if not plan:
        return gate(findings, "S3", "Tests and evidence cache", "VIOLATION", "Manifest has no tests.")
    if pending:
        ids = ", ".join(f"{t['id']} ({t['reason']})" for t in pending)
        return gate(findings, "S3", "Tests and evidence cache", "VIOLATION", f"Not yet proven fresh: {ids}")
    uncovered = oracles_without_test(ws, {str(t["id"]) for t in deferred})
    if uncovered:
        return gate(findings, "S3", "Tests and evidence cache", "VIOLATION",
                    f"No registered test declares `covers` for: {', '.join(uncovered)}. A passing suite proves nothing about an oracle no test targets.")
    reused = sum(1 for t in plan if t["action"] == "REUSE" or (t.get("always") and t.get("proven_now")))
    if reused == 0:
        return gate(findings, "S3", "Tests and evidence cache", "VIOLATION", "No test has a passing record on the current files.")
    if deferred:
        ids = ", ".join(f"{t['id']} (tier {t['tier']})" for t in deferred)
        return gate(findings, "S3", "Tests and evidence cache", "NOT_VERIFIED",
                    f"{reused} test(s) passed, but {ids} never ran at ceiling tier {max_tier}. Run them at close (--max-tier {max(t['tier'] for t in deferred)}) or report them as not verified.")
    gate(findings, "S3", "Tests and evidence cache", "PASS",
         f"{reused} test(s) have a passing record with identical deps; {len(deferred)} deferred above tier {max_tier} and reported as not run")


def check_task_queue(ws: Path, findings) -> None:
    cands = [ws / "tasks" / "current_task.md", ws / "current_task.md", ws / ".agents" / "PLAN_TASKS.md"]
    f = next((p for p in cands if p.exists()), None)
    if not f:
        return gate(findings, "S4", "Task queue ticks carry proof", "NOT_APPLICABLE", "No task queue file in this workspace")
    ticked = [l for l in read(f).splitlines() if re.match(r"^\s*-\s*\[x\]", l, re.I)]
    bad = [l.strip()[:80] for l in ticked if not (re.search(r"`[^`]+`", l) and re.search(r"\d{4}-\d{2}-\d{2}", l))]
    if bad:
        return gate(findings, "S4", "Task queue ticks carry proof", "VIOLATION", f"Ticked without a `command` and a YYYY-MM-DD date: {bad}")
    gate(findings, "S4", "Task queue ticks carry proof", "PASS", f"{len(ticked)} ticked item(s) in {f.name}, each with command and date")


def check_vendors(ws: Path, profile: str, ledger: str, findings) -> None:
    runs = ws / ".agents" / "fleet-runs"
    used: Set[str] = set()
    if runs.exists():
        for p in runs.rglob("*"):
            for v in VENDORS:
                if p.name.lower().startswith(v):
                    used.add(v)
    if not used:
        return gate(findings, "S5", "Vendor dispatch was approved", "NOT_APPLICABLE", "No external vendor runs recorded under .agents/fleet-runs")
    approved = confirmed_names(profile, "Approved vendors") & set(VENDORS)
    approved |= {r.get("what", "").split(":", 1)[1].lower() for r in records(ledger, "APPROVAL")
                 if r.get("what", "").lower().startswith("vendor:") and r.get("by", "").lower() not in NON_HUMAN}
    missing = sorted(used - approved)
    if missing:
        return gate(findings, "S5", "Vendor dispatch was approved", "VIOLATION",
                    f"Runs exist for {missing} but the profile 'Approved vendors' / a human APPROVAL record does not list them. A lane in fleet.json is not approval.")
    gate(findings, "S5", "Vendor dispatch was approved", "PASS", f"Vendors used {sorted(used)} are all approved")


def check_ui_mock(ws: Path, ledger: str, findings) -> None:
    mocks = [p for p in (ws / ".agents" / "mocks").glob("*.*")] if (ws / ".agents" / "mocks").exists() else []
    allowed = confirmed_names(read(ws / ".agents" / "PROJECT_PROFILE.md"), "Approvals")
    appr = [r for r in records(ledger, "APPROVAL") if r.get("what", "").lower() == "ui-mock" and r.get("by", "").lower() not in NON_HUMAN and r.get("date")
            and (not allowed or r.get("by", "").lower() in allowed)]
    if not mocks:
        return gate(findings, "S6", "UI mock approved by a person", "VIOLATION", "No mock under .agents/mocks/")
    if not appr:
        return gate(findings, "S6", "UI mock approved by a person", "VIOLATION",
                    "A mock exists but there is no `APPROVAL: what=ui-mock by=<person> date=<date>` record. When nobody can approve, stop at the mock and report; do not build the UI logic.")
    gate(findings, "S6", "UI mock approved by a person", "PASS", f"{len(mocks)} mock(s); approved by {appr[0]['by']} on {appr[0]['date']}")


def run_linter(path: Path, scan_dir: Path):
    return subprocess.run([sys.executable, str(path), "--scan-dir", str(scan_dir)], capture_output=True, text=True)


def check_linters(scan_dir: Path, domains: Optional[Set[str]], ui_applies: bool, findings, not_verified: List[str]) -> None:
    pack_gates = [(g["id"], g["name"], SCRIPT_DIR.parent / g["script"], ",".join(g.get("applies_when", [])), set(g.get("applies_when", [])))
                  for p in load_packs() for g in p.get("gates", [])]
    pack_gates.sort(key=lambda n: n[0])
    unknown = sorted(domains - known_domains()) if domains else []
    if unknown:
        gate(findings, "S9", "Unknown domains in the profile", "NOT_VERIFIED",
             f"No pack is installed for: {', '.join(unknown)}. Install the pack or remove the name; its checks cannot run.")
        not_verified.append(f"domain(s) without a pack: {', '.join(unknown)}")
    wanted = []
    for gid, name, path, kind, w in pack_gates:
        if domains is None:
            gate(findings, gid, name, "NOT_VERIFIED", "No project profile and no --domains: cannot tell whether this gate applies. Pass --domains core,clinical,ui or write the profile.")
        elif domains & w:
            wanted.append((gid, name, path))
        else:
            gate(findings, gid, name, "NOT_APPLICABLE", f"Domain '{kind}' is not in the project's packs ({', '.join(sorted(domains)) or 'none'})")
    if ui_applies:
        wanted.append(("S8", "Design and UX linter", DESIGN_LINTER_PATH))
    elif domains is None:
        gate(findings, "S8", "Design and UX linter", "NOT_VERIFIED", "No project profile and no --domains: cannot tell whether this gate applies. Pass --domains core,clinical,ui or write the profile.")
    else:
        gate(findings, "S8", "Design and UX linter", "NOT_APPLICABLE", f"No UI files or UI domain in the project's packs ({', '.join(sorted(domains)) or 'none'})")
    if not wanted:
        return
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(wanted)) as ex:
        futs = {gid: ex.submit(run_linter, path, scan_dir) for gid, _, path in wanted}
    for gid, name, _ in wanted:
        proc = futs[gid].result()
        try:
            data = json.loads(proc.stdout)
        except Exception:
            data = {}
        if proc.returncode != 0:
            gate(findings, gid, name, "VIOLATION", f"Linter failed: {proc.stdout.strip()[:300] or proc.stderr.strip()[:300]}")
        elif not data.get("files_scanned"):
            gate(findings, gid, name, "NOT_VERIFIED", f"Scanned 0 files under {scan_dir}. Point --src-dir at the source; a zero-file scan is not evidence.")
            not_verified.append(f"{name}: scanned 0 files")
        else:
            gate(findings, gid, name, "PASS", f"{data['files_scanned']} file(s) scanned, no blockers")


# ---------------------------------------------------------------- audit

def parse_domains(ws: Path, override: Optional[str]) -> Optional[Set[str]]:
    raw = override if override is not None else profile_field(read(ws / ".agents" / "PROJECT_PROFILE.md"), "Domains / packs")
    if not raw or re.search(r"\binferred\b", raw, re.I):
        return None
    raw = re.sub(r"[`*_]", "", raw)
    # only the leading list counts: stop at the first sentence break or negation ("core only. No UI, no clinical" is just core)
    raw = re.split(r"[.\n]|\s-\s|\b(?:no|not|without|none)\b", raw, maxsplit=1, flags=re.I)[0]
    filler = {"only", "and", "plus", "pack", "packs", "domain", "domains"}
    toks = {t.strip().lower() for t in re.split(r"[,;/\s|]+", raw) if re.fullmatch(r"[a-z][a-z-]*", t.strip().lower())} - filler
    return toks or None


def compute_modified_files_hashes(ws: Path) -> List[Dict[str, str]]:
    hashes = []
    try:
        out = subprocess.check_output(["git", "-C", str(ws), "status", "--porcelain"], stderr=subprocess.DEVNULL, text=True)
        for line in out.splitlines():
            rel = line[3:].strip().strip('"').split(" -> ")[-1]
            fp = ws / rel
            if line.strip() and fp.is_file():
                hashes.append({"file": rel, "sha256_prefix": hashlib.sha256(fp.read_bytes()).hexdigest()[:16]})
    except Exception:
        pass
    return hashes


def audit_workspace_compliance(ws: Path, domains_override: Optional[str] = None, src_dir: Optional[Path] = None,
                               max_tier: int = 2, auto_write_proof: bool = False) -> Dict[str, Any]:
    if not ws.is_dir():
        raise FileNotFoundError(f"Workspace directory not found: {ws}")
    findings: List[Dict[str, str]] = []
    not_verified: List[str] = []
    profile = read(ws / ".agents" / "PROJECT_PROFILE.md")
    ledger = read(ws / ".agents" / "AI_HANDOFF_LEDGER.md") or read(ws / "AI_HANDOFF_LEDGER.md")
    domains = parse_domains(ws, domains_override)
    scan_target = src_dir or ws
    modified_hashes = compute_modified_files_hashes(ws)
    ui_applies = has_ui_evidence(scan_target, modified_hashes, ws) or bool(domains and (domains & UI_WORDS))

    check_spec(ws, findings)
    check_reviews(ws, ledger, findings)
    check_tests(ws, max_tier, findings, not_verified)
    check_task_queue(ws, findings)
    check_vendors(ws, profile, ledger, findings)
    if ui_applies:
        check_ui_mock(ws, ledger, findings)
    elif domains is None:
        gate(findings, "S6", "UI mock approved by a person", "NOT_VERIFIED", "Domains unknown (no profile, no --domains) and no UI files detected, so UI applicability is undecided.")
    else:
        gate(findings, "S6", "UI mock approved by a person", "NOT_APPLICABLE", f"No UI files or UI domain in packs ({', '.join(sorted(domains))})")
    check_linters(scan_target, domains, ui_applies, findings, not_verified)

    applicable = [f for f in findings if f["status"] != "NOT_APPLICABLE"]
    passed = sum(1 for f in applicable if f["status"] == "PASS")
    violations = [f for f in findings if f["status"] == "VIOLATION"]
    unverified = [f for f in findings if f["status"] == "NOT_VERIFIED"]
    verdict = "BLOCKED_BY_SKILL_VIOLATIONS" if violations else ("INCOMPLETE_NOT_VERIFIED" if unverified else "APPROVED")
    assumptions = records(ledger, "ASSUMPTION")
    report = {
        "ambassador_verdict": verdict,
        "compliance_score_pct": round(100 * passed / len(applicable)) if applicable else 0,
        "gates_passed": passed,
        "total_gates_applicable": len(applicable),
        "violations_count": len(violations),
        "not_verified_count": len(unverified),
        "not_run_or_not_verified": not_verified,
        "assumptions_recorded": len(assumptions),
        "findings": findings,
        "audited_file_hashes": modified_hashes,
    }
    log = ws / ".agents" / "SKILL_COMPLIANCE_LOG.md"
    if auto_write_proof and log.exists():
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        rows = "\n".join(f"| `{f['gate']}` | **{f['status']}** | {f['detail']} |" for f in findings)
        hashes = "\n".join(f"  - `{h['file']}` (`sha256:{h['sha256_prefix']}`)" for h in report["audited_file_hashes"]) or "  - *(no changed files visible to git)*"
        log.write_text(read(log) + f"\n---\n\n## Referee proof (`--verify` at `{now}`)\n* **Verdict**: `{verdict}` ({passed}/{len(applicable)} applicable gates passed)\n\n"
                       f"| Gate | Status | Proof |\n| :--- | :--- | :--- |\n{rows}\n\n* **File hashes**:\n{hashes}\n", encoding="utf-8")
    return report


def init_compliance_log(ws: Path, feature: str) -> Path:
    d = ws / ".agents"
    d.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    p = d / "SKILL_COMPLIANCE_LOG.md"
    p.write_text(f"""# MACA Compliance Log

* **Feature**: `{feature}`
* **Initialized**: `{now}`
* The referee (`scripts/skill_ambassador_auditor.py --verify`) appends its proof below. It reads structured
  records (`REVIEW:`, `APPROVAL:`, `ASSUMPTION:` in the ledger, `ORACLE-<id>:` in the spec), not keywords.

| Gate | What must be true |
| :--- | :--- |
| S1 | Spec has a filled call-chain map and at least one `ORACLE-<id>:` line |
| S2 | A `REVIEW:` record exists whose reviewer differs from the author, with independence level and evidence |
| S3 | Every test up to the tier ceiling has a passing record with identical deps (`impact_and_cache.py`) |
| S4 | Every ticked task has a `command` and a date |
| S5 | Every external vendor that ran is approved by the profile or by a human `APPROVAL:` record |
| S6 | UI projects: a mock exists and a person approved it |
| S7 / S8 | Clinical / UI linters, only where the profile's packs call for them; a 0-file scan is NOT_VERIFIED |
""", encoding="utf-8")
    return p


# ---------------------------------------------------------------- self-test

def run_self_test() -> None:
    checks = []

    def seed(ws: Path, domains="core", ledger="", spec=None, task=None):
        a = ws / ".agents"
        a.mkdir(parents=True, exist_ok=True)
        (a / "PROJECT_PROFILE.md").write_text(f"- **Domains / packs** (core, ui, clinical): {domains}\n- **Approved vendors** (names or none): none\n", encoding="utf-8")
        (a / "SPEC_AND_AUDIT.md").write_text(spec if spec is not None else
            "## Call-chain map\n| target | callers |\n| :-- | :-- |\n| add() | cli.main |\n\n## Outcomes\n- ORACLE-1: add('x') then list() has length 1\n", encoding="utf-8")
        (a / "AI_HANDOFF_LEDGER.md").write_text(ledger, encoding="utf-8")
        (ws / "src").mkdir(exist_ok=True)
        (ws / "src" / "t.js").write_text("exports.a = 1\n", encoding="utf-8")
        (ws / "t.test.js").write_text("// t\n", encoding="utf-8")
        (a / "TEST_MANIFEST.json").write_text(json.dumps({"tests": [{"id": "UNIT-t", "tier": 1, "cmd": "python3 -c pass", "deps": ["src/t.js", "t.test.js"], "covers": ["ORACLE-1"]}]}), encoding="utf-8")
        if task:
            (ws / "tasks").mkdir(exist_ok=True)
            (ws / "tasks" / "current_task.md").write_text(task, encoding="utf-8")

    def record_pass(ws: Path):
        subprocess.run([sys.executable, str(CACHE_PATH), "run", "--ws", str(ws), "--id", "UNIT-t"], check=True, capture_output=True)

    good_review = "REVIEW: id=R-1 author=builder-a reviewer=reviewer-b independence=same-family round=1 evidence=review.md verdict=pass\n"

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        ws = root / "empty"; ws.mkdir()
        assert audit_workspace_compliance(ws)["ambassador_verdict"] == "BLOCKED_BY_SKILL_VIOLATIONS"
        checks.append("empty workspace is blocked: PASS")

        ws = root / "keywords"; ws.mkdir(); seed(ws, ledger="Round 1 peer review tabula rasa. Mode A scenario. Incremental step-by-step. Persistence 3-layer outcome oracle.\n"); record_pass(ws)
        r = audit_workspace_compliance(ws)
        assert any(f["gate"].startswith("S2") and f["status"] == "VIOLATION" for f in r["findings"]), r
        checks.append("keyword-stuffed ledger without a REVIEW record is rejected: PASS")

        ws = root / "selfreview"; ws.mkdir(); seed(ws, ledger=good_review.replace("reviewer-b", "builder-a")); (ws / "review.md").write_text("x"); record_pass(ws)
        assert any(f["gate"].startswith("S2") and f["status"] == "VIOLATION" for f in audit_workspace_compliance(ws)["findings"])
        checks.append("reviewer equal to author is rejected: PASS")

        ws = root / "good"; ws.mkdir(); seed(ws, ledger=good_review, task="- [x] add todos `node t.test.js` 2026-10-31\n"); (ws / "review.md").write_text("Reviewed spec, code and tests. No blockers found."); record_pass(ws)
        r = audit_workspace_compliance(ws)
        assert r["ambassador_verdict"] == "APPROVED", r
        assert any(f["status"] == "NOT_APPLICABLE" for f in r["findings"])
        assert r["total_gates_applicable"] < len(r["findings"])
        checks.append("plain project with evidence is APPROVED and clinical/UI gates are NOT_APPLICABLE, not failed: PASS")

        m = json.loads((ws / ".agents" / "TEST_MANIFEST.json").read_text()); m["tests"][0]["always"] = True
        (ws / ".agents" / "TEST_MANIFEST.json").write_text(json.dumps(m)); record_pass(ws)
        assert audit_workspace_compliance(ws)["ambassador_verdict"] == "APPROVED", "always test with a current recorded pass must not block"
        checks.append("always:true test with a pass recorded on current deps does not block close: PASS")
        m["tests"][0]["always"] = False; (ws / ".agents" / "TEST_MANIFEST.json").write_text(json.dumps(m))

        (ws / "src" / "t.js").write_text("exports.a = 2\n", encoding="utf-8")
        r = audit_workspace_compliance(ws)
        assert any(f["gate"].startswith("S3") and f["status"] == "VIOLATION" for f in r["findings"]), r
        checks.append("changed dependency makes the cached test stale again: PASS")

        ws = root / "uncovered"; ws.mkdir(); seed(ws, ledger=good_review, spec=None); (ws / "review.md").write_text("Reviewed spec, code and tests. No blockers found.")
        spec = (ws / ".agents" / "SPEC_AND_AUDIT.md").read_text() + "- ORACLE-2: add('') is rejected and nothing is stored\n"
        (ws / ".agents" / "SPEC_AND_AUDIT.md").write_text(spec); record_pass(ws)
        r = audit_workspace_compliance(ws)
        assert any(f["gate"].startswith("S3") and f["status"] == "VIOLATION" and "ORACLE-2" in f["detail"] for f in r["findings"]), r
        checks.append("an oracle that no registered test covers blocks the test gate: PASS")

        ws = root / "prose"; ws.mkdir(); seed(ws, domains="core only. No clinical data, no UI, no auth", ledger=good_review); (ws / "review.md").write_text("Reviewed spec, code and tests. No blockers found."); record_pass(ws)
        assert parse_domains(ws, None) == {"core"}, parse_domains(ws, None)
        assert audit_workspace_compliance(ws)["ambassador_verdict"] == "APPROVED"
        checks.append("prose after the domain list ('No clinical, no UI') is not read as domains: PASS")

        ws = root / "inferreddom"; ws.mkdir(); seed(ws, domains="core (inferred - confirm)", ledger=good_review); (ws / "review.md").write_text("Reviewed spec, code and tests. No blockers found."); record_pass(ws)
        assert parse_domains(ws, None) is None
        r = audit_workspace_compliance(ws)
        assert r["ambassador_verdict"] == "INCOMPLETE_NOT_VERIFIED" and any(f["status"] == "NOT_VERIFIED" for f in r["findings"]), r
        checks.append("inferred domains return None and keep gates NOT_VERIFIED: PASS")

        ws = root / "unknowndom"; ws.mkdir(); seed(ws, domains="core, medical-imaging", ledger=good_review); (ws / "review.md").write_text("Reviewed spec, code and tests. No blockers found."); record_pass(ws)
        r = audit_workspace_compliance(ws)
        assert any(f["gate"].startswith("S9") and f["status"] == "NOT_VERIFIED" for f in r["findings"]) and r["ambassador_verdict"] != "APPROVED", r
        checks.append("a domain with no installed pack is NOT_VERIFIED, never silently skipped: PASS")

        ws = root / "typodom"; ws.mkdir(); seed(ws, domains="core, clinicl", ledger=good_review); (ws / "review.md").write_text("Reviewed spec, code and tests. No blockers found."); record_pass(ws)
        r = audit_workspace_compliance(ws)
        assert any(f["gate"].startswith("S9") and f["status"] == "NOT_VERIFIED" and "clinicl" in f["detail"] for f in r["findings"]) and r["ambassador_verdict"] != "APPROVED", r
        checks.append("typo 'clinicl' triggers S9 NOT_VERIFIED instead of silently turning S7 off: PASS")

        ws = root / "byhand"; ws.mkdir(); seed(ws, ledger=good_review); (ws / "review.md").write_text("Reviewed spec, code and tests. No blockers found.")
        subprocess.run([sys.executable, str(CACHE_PATH), "record", "--ws", str(ws), "--id", "UNIT-t", "--status", "pass"], check=True, capture_output=True)
        assert any(f["gate"].startswith("S3") and f["status"] == "VIOLATION" for f in audit_workspace_compliance(ws)["findings"])
        checks.append("a test pass typed in by hand (not produced by `run`) is not evidence: PASS")

        ws = root / "deferred"; ws.mkdir(); seed(ws, ledger=good_review); (ws / "review.md").write_text("Reviewed spec, code and tests. No blockers found.")
        m = json.loads((ws / ".agents" / "TEST_MANIFEST.json").read_text()); m["tests"][0]["tier"] = 3
        (ws / ".agents" / "TEST_MANIFEST.json").write_text(json.dumps(m))
        r = audit_workspace_compliance(ws, max_tier=2)
        assert r["ambassador_verdict"] != "APPROVED" and any(f["gate"].startswith("S3") and f["status"] != "PASS" for f in r["findings"]), r
        checks.append("a test that was deferred and never ran can not produce APPROVED: PASS")

        ws = root / "inferredvendor"; ws.mkdir(); seed(ws, ledger=good_review); (ws / "review.md").write_text("Reviewed spec, code and tests. No blockers found."); record_pass(ws)
        (ws / ".agents" / "fleet-runs" / "x" / "codex").mkdir(parents=True)
        (ws / ".agents" / "PROJECT_PROFILE.md").write_text("- **Domains / packs** (x): core\n- **Approved vendors** (x): codex (inferred - confirm)\n")
        assert any(f["gate"].startswith("S5") and f["status"] == "VIOLATION" for f in audit_workspace_compliance(ws)["findings"])
        (ws / ".agents" / "PROJECT_PROFILE.md").write_text("- **Domains / packs** (x): core\n- **Approved vendors** (x): none, except codex\n")
        assert any(f["gate"].startswith("S5") and f["status"] == "VIOLATION" for f in audit_workspace_compliance(ws)["findings"])
        checks.append("an inferred or negated vendor entry grants no approval: PASS")

        ws = root / "fmt"; ws.mkdir(); seed(ws, domains="core, `clinical`", ledger=good_review)
        assert parse_domains(ws, None) == {"core", "clinical"}
        seed(ws, domains="core; clinical", ledger=good_review)
        assert parse_domains(ws, None) == {"core", "clinical"}
        checks.append("backticks and semicolons in the Domains line do not switch gates off: PASS")

        ws = root / "freetext"; ws.mkdir(); seed(ws, ledger=good_review.replace("evidence=review.md", 'evidence="I reviewed it"').replace("same-family", "multi-vendor")); record_pass(ws)
        assert any(f["gate"].startswith("S2") and f["status"] == "VIOLATION" for f in audit_workspace_compliance(ws)["findings"])
        checks.append("free-text review evidence and an unproven multi-vendor claim are rejected: PASS")

        ws = root / "tick"; ws.mkdir(); seed(ws, ledger=good_review, task="- [x] done with no proof\n"); (ws / "review.md").write_text("Reviewed spec, code and tests. No blockers found."); record_pass(ws)
        assert any(f["gate"].startswith("S4") and f["status"] == "VIOLATION" for f in audit_workspace_compliance(ws)["findings"])
        checks.append("task ticked without command and date is rejected: PASS")

        ws = root / "clinical"; ws.mkdir(); seed(ws, domains="core, clinical", ledger=good_review); (ws / "review.md").write_text("Reviewed spec, code and tests. No blockers found."); record_pass(ws)
        (root / "emptydir").mkdir()
        r = audit_workspace_compliance(ws, src_dir=root / "emptydir")
        assert any(f["gate"].startswith("S7") and f["status"] == "NOT_VERIFIED" for f in r["findings"]) and r["ambassador_verdict"] != "APPROVED", r
        checks.append("applicable linter that scanned 0 files is NOT_VERIFIED, never a pass: PASS")

        ws = root / "ui"; ws.mkdir(); seed(ws, domains="web-ui", ledger=good_review); (ws / "review.md").write_text("Reviewed spec, code and tests. No blockers found."); record_pass(ws)
        (ws / ".agents" / "mocks").mkdir(); (ws / ".agents" / "mocks" / "m.html").write_text("<div/>")
        assert any(f["gate"].startswith("S6") and f["status"] == "VIOLATION" for f in audit_workspace_compliance(ws, src_dir=root / "emptydir")["findings"])
        (ws / ".agents" / "AI_HANDOFF_LEDGER.md").write_text(good_review + "APPROVAL: what=ui-mock by=gemini date=2026-10-31\n")
        assert any(f["gate"].startswith("S6") and f["status"] == "VIOLATION" for f in audit_workspace_compliance(ws, src_dir=root / "emptydir")["findings"])
        (ws / ".agents" / "AI_HANDOFF_LEDGER.md").write_text(good_review + "APPROVAL: what=ui-mock by=Dr.Sara date=2026-10-31\n")
        assert any(f["gate"].startswith("S6") and f["status"] == "PASS" for f in audit_workspace_compliance(ws, src_dir=root / "emptydir")["findings"])
        checks.append("UI mock (including 'web-ui' profile) needs approval recorded by a person, not the orchestrator: PASS")

        ws = root / "uitsx"; ws.mkdir(); seed(ws, domains="core", ledger=good_review); (ws / "review.md").write_text("Reviewed spec, code and tests. No blockers found."); record_pass(ws)
        (ws / "src" / "App.tsx").write_text("export const App = () => <div/>;\n", encoding="utf-8")
        r = audit_workspace_compliance(ws)
        assert any(f["gate"].startswith("S6") and f["status"] == "VIOLATION" for f in r["findings"]), r
        assert any(f["gate"].startswith("S8") and f["status"] == "PASS" for f in r["findings"]), r
        checks.append("a .tsx file in src dir with profile 'core' makes S6 and S8 applicable: PASS")

        ws = root / "vendor"; ws.mkdir(); seed(ws, ledger=good_review); (ws / "review.md").write_text("Reviewed spec, code and tests. No blockers found."); record_pass(ws)
        (ws / ".agents" / "fleet-runs" / "x" / "codex").mkdir(parents=True)
        assert any(f["gate"].startswith("S5") and f["status"] == "VIOLATION" for f in audit_workspace_compliance(ws)["findings"])
        (ws / ".agents" / "PROJECT_PROFILE.md").write_text("- **Domains / packs** (x): core\n- **Approved vendors** (x): codex\n")
        assert any(f["gate"].startswith("S5") and f["status"] == "PASS" for f in audit_workspace_compliance(ws)["findings"])
        checks.append("vendor run without approval is a violation; approval in the profile clears it: PASS")

        tpl = (SCRIPT_DIR.parent / "resources" / "templates" / "PROJECT_PROFILE.template.md").read_text(encoding="utf-8")
        assert profile_field(tpl, "Approved vendors") == "" and profile_field(tpl, "Domains / packs") == "", "unedited template must not grant anything"
        checks.append("unedited profile template grants no vendor approval and no domains: PASS")

        ws = root / "noprofile"; ws.mkdir(); seed(ws, ledger=good_review); (ws / "review.md").write_text("Reviewed spec, code and tests. No blockers found."); record_pass(ws)
        (ws / ".agents" / "PROJECT_PROFILE.md").unlink()
        r = audit_workspace_compliance(ws)
        assert r["ambassador_verdict"] == "INCOMPLETE_NOT_VERIFIED", r
        checks.append("missing profile makes domain gates NOT_VERIFIED instead of silently skipped: PASS")

        ws = root / "log"; ws.mkdir(); seed(ws, ledger=good_review); (ws / "review.md").write_text("Reviewed spec, code and tests. No blockers found."); record_pass(ws)
        lp = init_compliance_log(ws, "demo")
        audit_workspace_compliance(ws, auto_write_proof=True)
        assert "Referee proof" in lp.read_text(encoding="utf-8")
        checks.append("compliance log initialisation and proof append: PASS")

    print(json.dumps({"self_test_status": "PASS", "checks_executed": len(checks), "details": checks}, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description="MACA evidence-based referee")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--init-log", metavar="WORKSPACE_DIR")
    ap.add_argument("--feature", default="Active Feature Slice")
    ap.add_argument("--audit-workspace", metavar="WORKSPACE_DIR", help="Audit without writing to the compliance log")
    ap.add_argument("--verify", metavar="WORKSPACE_DIR", help="Audit and append the proof to .agents/SKILL_COMPLIANCE_LOG.md if it exists")
    ap.add_argument("--domains", help="Override the profile, e.g. core,fintech or core,clinical,ui")
    ap.add_argument("--src-dir", help="Directory the linters scan (default: the workspace)")
    ap.add_argument("--max-tier", type=int, default=2, help="Tier ceiling for the test-evidence gate (default 2; use 3 at close)")
    ap.add_argument("--no-ui-mock", action="store_true", help="Deprecated: set the domains instead; kept so old calls do not break")
    try:
        args = ap.parse_args()
        if args.self_test:
            return run_self_test()
        if args.init_log:
            p = init_compliance_log(Path(args.init_log).resolve(), args.feature)
            print(json.dumps({"status": "INITIALIZED", "compliance_log_path": str(p), "feature": args.feature}, indent=2))
            return
        target = args.verify or args.audit_workspace
        if target:
            report = audit_workspace_compliance(Path(target).resolve(), args.domains, Path(args.src_dir).resolve() if args.src_dir else None,
                                                args.max_tier, bool(args.verify))
            print(json.dumps(report, indent=2))
            sys.exit({"APPROVED": 0, "BLOCKED_BY_SKILL_VIOLATIONS": 1}.get(report["ambassador_verdict"], 3))
        ap.print_help()
    except SystemExit:
        raise
    except Exception as exc:
        emit_fail_closed_error(type(exc).__name__, str(exc), "Run 'python3 scripts/skill_ambassador_auditor.py --self-test' to verify the referee.")


if __name__ == "__main__":
    main()
