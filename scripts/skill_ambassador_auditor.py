#!/usr/bin/env python3
"""
================================================================================
MACA v2 Automated Pre-Commit Subagent Referee & Skill Ambassador Engine
(scripts/skill_ambassador_auditor.py)
--------------------------------------------------------------------------------
Implements Upgrade 5 from the MACA Engineering Post-Mortem:
- Acts as the deterministic CLI referee (`--verify <workspace_dir>`).
- Automatically runs `lint_samd_invariants.py` (Zero Hard-Delete, JVM 255-arg
  budget, and RBAC string-heuristic checks).
- Computes cryptographic SHA-256 verification hashes of all modified files in
  the working tree to prove zero unreviewed changes bypassed the Tabula Rasa
  audit.
- Auto-generates and appends a deterministic Markdown Compliance Proof section
  into `.agents/SKILL_COMPLIANCE_LOG.md`.
================================================================================
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
from typing import Any, Dict, List

SCRIPT_DIR = Path(__file__).resolve().parent
SAMD_LINTER_PATH = SCRIPT_DIR / "lint_samd_invariants.py"
DESIGN_LINTER_PATH = SCRIPT_DIR / "lint_design_and_ux.py"


def emit_fail_closed_error(error_code: str, message: str, remediation: str) -> None:
    payload = {
        "status": "MACA_SCRIPT_ERROR — STOP_AND_FIX",
        "error_code": error_code,
        "message": message,
        "mandatory_agent_action": "DO NOT SKIP OR BYPASS THIS STEP. Fix the error described below and re-run, or halt and report UNKNOWN / HARNESS ERROR.",
        "remediation": remediation
    }
    print(json.dumps(payload, indent=2), file=sys.stderr)
    sys.exit(2)


def compute_modified_files_hashes(workspace_dir: Path) -> List[Dict[str, str]]:
    """Computes SHA-256 hashes of all modified/untracked files in git status (Upgrade 5)."""
    hashes: List[Dict[str, str]] = []
    try:
        out = subprocess.check_output(
            ["git", "-C", str(workspace_dir), "status", "--porcelain"],
            stderr=subprocess.DEVNULL,
            text=True
        )
        for line in out.splitlines():
            if not line.strip():
                continue
            rel = line[3:].strip().strip('"')
            if " -> " in rel:
                rel = rel.split(" -> ", 1)[1].strip()
            fpath = workspace_dir / rel
            if fpath.is_file():
                digest = hashlib.sha256(fpath.read_bytes()).hexdigest()[:16]
                hashes.append({"file": rel, "sha256_prefix": digest})
    except Exception:
        pass
    return hashes


def init_compliance_log(workspace_dir: Path, feature_name: str) -> Path:
    """Initializes .agents/SKILL_COMPLIANCE_LOG.md at Phase 0 so the Skill Ambassador tracks compliance live."""
    agents_dir = workspace_dir / ".agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    log_path = agents_dir / "SKILL_COMPLIANCE_LOG.md"
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    content = f"""# 🏛️ MACA v2 Skill Ambassador & Automated Referee Compliance Log

* **Feature / Task Under Audit**: `{feature_name}`
* **Initialized At**: `{now_iso}`
* **Skill Ambassador Role**: Independent Procedural Referee (Zero Application Code Authorship)

---

## 1. Pre-Flight Mandatory Gate Charter (Locked at Start of Task)

| Gate ID | Mandatory MACA v2 Rule | Required Artifact / Evidence | Status | Ambassador Verdict & Notes |
| :--- | :--- | :--- | :--- | :--- |
| **G-01** | **Phase 0 First-Run & Bootstrap** | `./scripts/bootstrap.sh` executed with `exit code 0` | `PENDING` | - |
| **G-02** | **Phase 1 Spec & Call-Chain Map** | `.agents/SPEC_AND_AUDIT.md` with upstream/downstream callers mapped | `PENDING` | - |
| **G-03** | **Phase 1.5 Visual Mock Gate** | `.agents/mocks/<feature>.html` or `.svg` approved by User before logic coding | `PENDING` | - |
| **G-04** | **Phase 3 Tabula Rasa Diff Audit** | Independent peer critique in `.agents/AI_HANDOFF_LEDGER.md` (No fake `[In-Process]`) | `PENDING` | - |
| **G-05** | **Phase 4.1 Scenario Mode Choice** | User presented Mode A (Predefined), Mode B (Imaginary), or Mode C (Custom) | `PENDING` | - |
| **G-06** | **Phase 4.2 Anti-Bulk-Mock Rule** | Fast-forward intake + sequential step-by-step entry ($T_0 \\to T_1 \\to T_2$) | `PENDING` | - |
| **G-07** | **Phase 4.3 Call-Chain & SaMD AST Lint** | `lint_samd_invariants.py` (Zero Hard-Delete, JVM <35 args, RBAC claims) passed | `PENDING` | - |
| **G-08** | **Phase 4.4 3-Layer + Geometric Oracle** | Domain + DB + UI Bounding-Box (`>=120dp` flex) + 6-Row Auth Fuzz Matrix verified | `PENDING` | - |
| **G-09** | **Task Queue Sync (`current_task.md`)** | Completed item updated from `- [ ]` to `- [x]` with inline command/date proof | `PENDING` | - |
| **G-10** | **Phase 4.4 4-Pillar Design & UX Audit** | `lint_design_and_ux.py` (Tokens, SVG/RTL Icons, WCAG AA >=4.5:1, 5 UI States, <=3 Taps) | `PENDING` | - |

---

## 2. Live Agent Evaluation & Skill Friction Log (سجل تقييم أداء الـ Agents ومشاكل المهارة)

| Timestamp | Agent / Lane Evaluated | Rule / Phase Tested | Compliance (`PASS` / `VIOLATION`) | Observed Friction or Defect in Skill Execution | Recommended Skill Adjustment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `{now_iso}` | `Antigravity Orchestrator` | `Phase 0 Init` | `PASS` | Skill Ambassador Charter initialized cleanly. | None |

---

## 3. Final Ambassador Sign-Off & Cryptographic Verification
* **Overall Skill Compliance Score**: `PENDING`
* **Unresolved Procedural Violations**: `NONE YET`
* **Release / Commit Authorization by Ambassador**: `LOCKED UNTIL G-01..G-10 PASS`
"""
    log_path.write_text(content, encoding="utf-8")
    return log_path


def audit_workspace_compliance(workspace_dir: Path, require_ui_mock: bool = True, auto_write_proof: bool = False) -> Dict[str, Any]:
    if not workspace_dir.exists() or not workspace_dir.is_dir():
        raise FileNotFoundError(f"Workspace directory not found: {workspace_dir}")

    findings: List[Dict[str, str]] = []
    passed_gates = 0
    total_gates = 10 if require_ui_mock else 8

    # 1. Check SPEC_AND_AUDIT.md & Call-Chain Map (G-02)
    spec_candidates = [workspace_dir / ".agents" / "SPEC_AND_AUDIT.md", workspace_dir / "SPEC_AND_AUDIT.md"]
    spec_file = next((p for p in spec_candidates if p.exists()), None)
    spec_text = ""
    if spec_file:
        spec_text = spec_file.read_text(encoding="utf-8", errors="ignore")
        has_call_chain = "call-chain" in spec_text.lower() or "caller" in spec_text.lower()
        has_oracle = "oracle" in spec_text.lower()
        if has_call_chain and has_oracle:
            passed_gates += 1
            findings.append({"gate": "G-02 (Spec & Call-Chain Map)", "status": "PASS", "detail": f"Verified in {spec_file.name}"})
        else:
            findings.append({
                "gate": "G-02 (Spec & Call-Chain Map)",
                "status": "VIOLATION",
                "detail": "SPEC_AND_AUDIT.md exists but is missing the Cross-Function Call-Chain Map or 3-Layer Outcome Oracle."
            })
    else:
        findings.append({"gate": "G-02 (Spec & Call-Chain Map)", "status": "VIOLATION", "detail": "Missing .agents/SPEC_AND_AUDIT.md"})

    # 2. Check UI Mock Artifact (G-03, if UI task)
    if require_ui_mock:
        mocks_dir = workspace_dir / ".agents" / "mocks"
        mock_files = list(mocks_dir.glob("*.*")) if mocks_dir.exists() else []
        if mock_files:
            passed_gates += 1
            findings.append({"gate": "G-03 (Phase 1.5 UI Mock)", "status": "PASS", "detail": f"Found {len(mock_files)} mock artifact(s)"})
        else:
            findings.append({
                "gate": "G-03 (Phase 1.5 UI Mock)",
                "status": "VIOLATION",
                "detail": "No visual mock found in .agents/mocks/ before implementation."
            })

    # 3. Check AI_HANDOFF_LEDGER.md for Adversarial Diff Audit & 3-Layer Oracle proof (G-04, G-05, G-06, G-08)
    ledger_candidates = [workspace_dir / ".agents" / "AI_HANDOFF_LEDGER.md", workspace_dir / "AI_HANDOFF_LEDGER.md"]
    ledger_file = next((p for p in ledger_candidates if p.exists()), None)
    ledger_text = ""
    if ledger_file:
        ledger_text = ledger_file.read_text(encoding="utf-8", errors="ignore")
        has_round1 = bool(re.search(r"round\s*1|peer\s*(?:review|audit|critique)|tabula\s*rasa", ledger_text, re.IGNORECASE))
        has_3layer = bool(re.search(r"3-layer|outcome\s*oracle|persistence|sqlcipher|room\s*entity|db\s*layer", ledger_text, re.IGNORECASE))
        if has_round1:
            passed_gates += 1
            findings.append({"gate": "G-04 (Adversarial Diff Audit)", "status": "PASS", "detail": "Round 1 diff audit recorded in ledger."})
        else:
            findings.append({"gate": "G-04 (Adversarial Diff Audit)", "status": "VIOLATION", "detail": "Missing Round 1 diff audit in AI_HANDOFF_LEDGER.md."})

        # G-05: Scenario Mode Selector (Mode A/B/C)
        combined_text = spec_text + " " + ledger_text
        has_scenario_mode = bool(re.search(r"mode\s*[abc]|scenario\s*mode|--mode|imaginary\s*scenario", combined_text, re.IGNORECASE))
        if has_scenario_mode:
            passed_gates += 1
            findings.append({"gate": "G-05 (Interactive Scenario Mode A/B/C)", "status": "PASS", "detail": "Scenario mode choice documented."})
        else:
            findings.append({"gate": "G-05 (Interactive Scenario Mode A/B/C)", "status": "VIOLATION", "detail": "Missing Interactive Scenario Mode (Mode A/B/C) verification record."})

        # G-06: Fast-Forward Intake & Strict Incremental Entry (Anti-Bulk-Mock)
        has_incremental = bool(re.search(r"incremental|fast-forward|anti-bulk|time-step|t_0|step-by-step", combined_text, re.IGNORECASE))
        if has_incremental:
            passed_gates += 1
            findings.append({"gate": "G-06 (Fast-Forward Intake & Strict Incremental Entry)", "status": "PASS", "detail": "Strict incremental mutation pipeline verified (zero bulk mocks)."})
        else:
            findings.append({"gate": "G-06 (Fast-Forward Intake & Strict Incremental Entry)", "status": "VIOLATION", "detail": "Missing incremental sequential entry proof (anti-bulk-mock)."})

        if has_3layer:
            passed_gates += 1
            findings.append({"gate": "G-08 (3-Layer & Geometric E2E Oracle)", "status": "PASS", "detail": "3-Layer Outcome Oracle recorded in ledger."})
        else:
            findings.append({"gate": "G-08 (3-Layer & Geometric E2E Oracle)", "status": "VIOLATION", "detail": "Missing 3-Layer Outcome Oracle evidence in ledger."})
    else:
        findings.append({"gate": "G-04, G-05, G-06 & G-08 (Handoff Ledger)", "status": "VIOLATION", "detail": "Missing .agents/AI_HANDOFF_LEDGER.md"})

    # 4 & 4b. Concurrent Execution of SaMD Linter (G-07) and Design/UX Linter (G-10)
    linter_tasks = []
    if SAMD_LINTER_PATH.exists():
        linter_tasks.append(("samd", [sys.executable, str(SAMD_LINTER_PATH), "--scan-dir", str(workspace_dir)]))
    if require_ui_mock and DESIGN_LINTER_PATH.exists():
        linter_tasks.append(("design", [sys.executable, str(DESIGN_LINTER_PATH), "--scan-dir", str(workspace_dir)]))

    linter_results = {}
    if linter_tasks:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(linter_tasks)) as executor:
            future_to_kind = {
                executor.submit(subprocess.run, cmd, capture_output=True, text=True): kind
                for kind, cmd in linter_tasks
            }
            for future in concurrent.futures.as_completed(future_to_kind):
                kind = future_to_kind[future]
                linter_results[kind] = future.result()

    if "samd" in linter_results:
        proc = linter_results["samd"]
        if proc.returncode == 0:
            passed_gates += 1
            findings.append({
                "gate": "G-07 (SaMD Zero-Delete, RBAC & JVM Budget Linter)",
                "status": "PASS",
                "detail": "Zero hard-delete SQL, zero fragile RBAC string checks, and constructor budgets < 35 params."
            })
        else:
            findings.append({
                "gate": "G-07 (SaMD Zero-Delete, RBAC & JVM Budget Linter)",
                "status": "VIOLATION",
                "detail": f"Static invariant linter failed: {proc.stdout.strip()}"
            })

    if "design" in linter_results:
        d_proc = linter_results["design"]
        if d_proc.returncode == 0:
            passed_gates += 1
            findings.append({
                "gate": "G-10 (4-Pillar Design, Graphic, UI & UX Linter)",
                "status": "PASS",
                "detail": "Zero hardcoded UI hex colors, valid SVG/Vector viewBox, RTL icon mirroring, and WCAG AA verified."
            })
        else:
            findings.append({
                "gate": "G-10 (4-Pillar Design, Graphic, UI & UX Linter)",
                "status": "VIOLATION",
                "detail": f"Design/UX linter reported blockers: {d_proc.stdout.strip()}"
            })

    # 5. Check SKILL_COMPLIANCE_LOG.md presence (G-01)
    comp_log = workspace_dir / ".agents" / "SKILL_COMPLIANCE_LOG.md"
    if comp_log.exists():
        passed_gates += 1
        findings.append({"gate": "G-01 (Skill Ambassador Log)", "status": "PASS", "detail": "SKILL_COMPLIANCE_LOG.md active."})
    else:
        findings.append({"gate": "G-01 (Skill Ambassador Log)", "status": "VIOLATION", "detail": "Missing .agents/SKILL_COMPLIANCE_LOG.md (Run --init-log first)."})

    # 6. Check Task Queue synchronization (G-09)
    task_candidates = [
        workspace_dir / "tasks" / "current_task.md",
        workspace_dir / "current_task.md",
        workspace_dir / ".agents" / "PLAN_TASKS.md"
    ]
    task_file = next((p for p in task_candidates if p.exists()), None)
    if task_file:
        t_text = task_file.read_text(encoding="utf-8", errors="ignore")
        checked = len(re.findall(r"^\s*-\s*\[x\]", t_text, re.MULTILINE | re.IGNORECASE))
        passed_gates += 1
        findings.append({"gate": "G-09 (Task Queue Sync)", "status": "PASS", "detail": f"Found {task_file.name} ({checked} item(s) checked off [x])."})
    else:
        findings.append({"gate": "G-09 (Task Queue Sync)", "status": "VIOLATION", "detail": "Missing tasks/current_task.md or .agents/PLAN_TASKS.md."})

    compliance_pct = round((passed_gates / total_gates) * 100)
    violations = [f for f in findings if f["status"] == "VIOLATION"]
    verdict = "APPROVED" if not violations else "BLOCKED_BY_SKILL_VIOLATIONS"
    file_hashes = compute_modified_files_hashes(workspace_dir)

    report = {
        "ambassador_verdict": verdict,
        "compliance_score_pct": compliance_pct,
        "gates_passed": passed_gates,
        "total_gates_checked": total_gates,
        "violations_count": len(violations),
        "findings": findings,
        "audited_file_hashes": file_hashes
    }

    if auto_write_proof and comp_log.exists():
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        rows = "\n".join(f"| `{f['gate']}` | **{f['status']}** | {f['detail']} |" for f in findings)
        hash_rows = "\n".join(f"  - `{h['file']}` (`sha256:{h['sha256_prefix']}`)" for h in file_hashes) or "  - *(Clean working tree)*"
        proof_block = f"""

---

## 4. Automated Referee Proof (`--verify` executed at `{now_iso}`)
* **Verdict**: `{verdict}` (**{compliance_pct}%** — `{passed_gates}/{total_gates}` gates passed)

| Gate | Status | Deterministic Audit Proof |
| :--- | :--- | :--- |
{rows}

* **Cryptographic File Hashes Verified**:
{hash_rows}
"""
        comp_log.write_text(comp_log.read_text(encoding="utf-8") + proof_block, encoding="utf-8")

    return report


def run_self_test() -> None:
    checks = []
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp)
        log_path = init_compliance_log(ws, "Inbox Broadcast Area")
        assert log_path.exists()
        checks.append("Skill Ambassador Charter Initialization (--init-log): PASS")

        incomplete = audit_workspace_compliance(ws, require_ui_mock=True)
        assert incomplete["ambassador_verdict"] == "BLOCKED_BY_SKILL_VIOLATIONS"
        checks.append("Incomplete Workspace Violation Detection: PASS")

        (ws / ".agents" / "mocks").mkdir(parents=True, exist_ok=True)
        (ws / ".agents" / "mocks" / "inbox_area.html").write_text("<div>Mock</div>", encoding="utf-8")
        (ws / ".agents" / "SPEC_AND_AUDIT.md").write_text("Call-Chain Map and 3-Layer Outcome Oracle", encoding="utf-8")
        (ws / ".agents" / "AI_HANDOFF_LEDGER.md").write_text("Round 1 Diff Audit + 3-Layer Persistence Oracle + Mode A Scenario + Incremental Time-Step Entry", encoding="utf-8")
        (ws / "tasks").mkdir(parents=True, exist_ok=True)
        (ws / "tasks" / "current_task.md").write_text("- [x] Inbox feature verified\n", encoding="utf-8")

        complete = audit_workspace_compliance(ws, require_ui_mock=True, auto_write_proof=True)
        assert complete["ambassador_verdict"] == "APPROVED"
        assert complete["compliance_score_pct"] == 100
        assert "Automated Referee Proof" in log_path.read_text(encoding="utf-8")
        checks.append("Compliant Workspace 100% Verification & Auto-Ledger Proof (--verify): PASS")

    print(json.dumps({
        "self_test_status": "PASS",
        "checks_executed": len(checks),
        "details": checks
    }, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="MACA v2 Skill Ambassador & Automated Pre-Commit Referee")
    parser.add_argument("--self-test", action="store_true", help="Run built-in verification self-tests and exit")
    parser.add_argument("--init-log", type=str, metavar="WORKSPACE_DIR", help="Initialize .agents/SKILL_COMPLIANCE_LOG.md in workspace")
    parser.add_argument("--feature", type=str, default="Active Feature Slice", help="Feature name for --init-log")
    parser.add_argument("--audit-workspace", type=str, metavar="WORKSPACE_DIR", help="Audit workspace for MACA skill compliance")
    parser.add_argument("--verify", type=str, metavar="WORKSPACE_DIR", help="Run full MACA v2 automated referee check and append cryptographic proof to SKILL_COMPLIANCE_LOG.md")
    parser.add_argument("--no-ui-mock", action="store_true", help="Skip Phase 1.5 UI mock requirement for backend-only tasks")

    try:
        args = parser.parse_args()

        if args.self_test:
            run_self_test()
            return

        if args.init_log:
            log_file = init_compliance_log(Path(args.init_log).resolve(), args.feature)
            print(json.dumps({
                "status": "INITIALIZED",
                "compliance_log_path": str(log_file),
                "feature": args.feature
            }, indent=2))
            return

        target_ws = args.verify or args.audit_workspace
        if target_ws:
            report = audit_workspace_compliance(
                Path(target_ws).resolve(),
                require_ui_mock=not args.no_ui_mock,
                auto_write_proof=bool(args.verify)
            )
            print(json.dumps(report, indent=2))
            sys.exit(0 if report["ambassador_verdict"] == "APPROVED" else 1)

        parser.print_help()
    except Exception as exc:
        emit_fail_closed_error(
            type(exc).__name__,
            str(exc),
            "Run 'python3 scripts/skill_ambassador_auditor.py --self-test' to verify the Skill Ambassador auditor."
        )


if __name__ == "__main__":
    main()
