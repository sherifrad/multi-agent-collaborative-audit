#!/usr/bin/env python3
"""
================================================================================
MACA Skill Ambassador & Compliance Referee Engine
(scripts/skill_ambassador_auditor.py)
--------------------------------------------------------------------------------
Acts as the deterministic enforcement tool for the "Skill Ambassador" role.
Verifies whether the active agents (Antigravity, UI/UX, Core Logic, Data, QA)
actually obeyed every mandatory rule of the MACA skill, or whether they tried
to bypass gates, skip UI mocks, omit call-chain traces, or use bulk mocks.
================================================================================
"""

import argparse
import json
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


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


def init_compliance_log(workspace_dir: Path, feature_name: str) -> Path:
    """Initializes .agents/SKILL_COMPLIANCE_LOG.md at Phase 0 so the Skill Ambassador tracks compliance live."""
    agents_dir = workspace_dir / ".agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    log_path = agents_dir / "SKILL_COMPLIANCE_LOG.md"
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    content = f"""# 🏛️ MACA Skill Ambassador & Referee Compliance Log

* **Feature / Task Under Audit**: `{feature_name}`
* **Initialized At**: `{now_iso}`
* **Skill Ambassador Role**: Independent Procedural Referee (Zero Application Code Authorship)

---

## 1. Pre-Flight Mandatory Gate Charter (Locked at Start of Task)

| Gate ID | Mandatory Skill Rule | Required Artifact / Evidence | Status | Ambassador Verdict & Notes |
| :--- | :--- | :--- | :--- | :--- |
| **G-01** | **Phase 0 Bootstrap & Scripts** | `./scripts/bootstrap.sh` executed with `exit code 0` | `PENDING` | - |
| **G-02** | **Phase 1 Spec & Call-Chain Map** | `.agents/SPEC_AND_AUDIT.md` with upstream/downstream callers mapped | `PENDING` | - |
| **G-03** | **Phase 1.5 Visual Mock Gate** | `.agents/mocks/<feature>.html` or `.svg` approved by User before logic coding | `PENDING` | - |
| **G-04** | **Phase 3 Tabula Rasa Diff Audit** | Independent peer critique in `.agents/AI_HANDOFF_LEDGER.md` (No fake `[In-Process]` rubber-stamp) | `PENDING` | - |
| **G-05** | **Phase 4.1 Scenario Mode Choice** | User presented Mode A (Predefined), Mode B (Imaginary), or Mode C (Custom) | `PENDING` | - |
| **G-06** | **Phase 4.2 Anti-Bulk-Mock Rule** | Fast-forward intake + sequential step-by-step observation/event entry ($T_0 \\to T_1 \\to T_2$) | `PENDING` | - |
| **G-07** | **Phase 4.3 Call-Chain & Zero Mock** | `scenario_and_callchain_engine.py --trace-dir` passed with zero internal mocks | `PENDING` | - |
| **G-08** | **Phase 4.4 3-Layer Outcome Oracle** | Domain + DB Persistence + Visual UI assertions + Negative Control verified | `PENDING` | - |
| **G-09** | **Task Queue Sync (`current_task.md`)** | Completed item updated from `- [ ]` to `- [x]` with inline command/date proof | `PENDING` | - |

---

## 2. Live Agent Evaluation & Skill Friction Log (سجل تقييم أداء الـ Agents ومشاكل المهارة)

| Timestamp | Agent / Lane Evaluated | Rule / Phase Tested | Compliance (`PASS` / `VIOLATION`) | Observed Friction or Defect in Skill Execution | Recommended Skill Adjustment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `{now_iso}` | `Antigravity Orchestrator` | `Phase 0 Init` | `PASS` | Skill Ambassador Charter initialized cleanly. | None |

---

## 3. Final Ambassador Sign-Off & Compliance Score
* **Overall Skill Compliance Score**: `PENDING`
* **Unresolved Procedural Violations**: `NONE YET`
* **Release / Commit Authorization by Ambassador**: `LOCKED UNTIL G-01..G-09 PASS`
"""
    log_path.write_text(content, encoding="utf-8")
    return log_path


def audit_workspace_compliance(workspace_dir: Path, require_ui_mock: bool = True) -> Dict[str, Any]:
    """
    Deterministically audits a workspace directory to check whether the agents
    actually produced the required MACA artifacts and obeyed Phase 0-4 rules.
    """
    if not workspace_dir.exists() or not workspace_dir.is_dir():
        raise FileNotFoundError(f"Workspace directory not found: {workspace_dir}")

    findings: List[Dict[str, str]] = []
    passed_gates = 0
    total_gates = 6 if require_ui_mock else 5

    # 1. Check SPEC_AND_AUDIT.md & Call-Chain Map
    spec_candidates = [workspace_dir / ".agents" / "SPEC_AND_AUDIT.md", workspace_dir / "SPEC_AND_AUDIT.md"]
    spec_file = next((p for p in spec_candidates if p.exists()), None)
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

    # 2. Check UI Mock Artifact (if UI task)
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

    # 3. Check AI_HANDOFF_LEDGER.md for Anti-Bulk-Mock & 3-Layer Oracle proof
    ledger_candidates = [workspace_dir / ".agents" / "AI_HANDOFF_LEDGER.md", workspace_dir / "AI_HANDOFF_LEDGER.md"]
    ledger_file = next((p for p in ledger_candidates if p.exists()), None)
    if ledger_file:
        ledger_text = ledger_file.read_text(encoding="utf-8", errors="ignore")
        has_round1 = "round 1" in ledger_text.lower()
        has_3layer = "3-layer" in ledger_text.lower() or "persistence" in ledger_text.lower()
        if has_round1:
            passed_gates += 1
            findings.append({"gate": "G-04 (Adversarial Diff Audit)", "status": "PASS", "detail": "Round 1 diff audit recorded in ledger."})
        else:
            findings.append({"gate": "G-04 (Adversarial Diff Audit)", "status": "VIOLATION", "detail": "Missing Round 1 diff audit in AI_HANDOFF_LEDGER.md."})

        if has_3layer:
            passed_gates += 1
            findings.append({"gate": "G-08 (3-Layer E2E Oracle)", "status": "PASS", "detail": "3-Layer Outcome Oracle recorded in ledger."})
        else:
            findings.append({"gate": "G-08 (3-Layer E2E Oracle)", "status": "VIOLATION", "detail": "Missing 3-Layer Outcome Oracle evidence in ledger."})
    else:
        findings.append({"gate": "G-04 & G-08 (Handoff Ledger)", "status": "VIOLATION", "detail": "Missing .agents/AI_HANDOFF_LEDGER.md"})

    # 4. Check SKILL_COMPLIANCE_LOG.md presence
    comp_log = workspace_dir / ".agents" / "SKILL_COMPLIANCE_LOG.md"
    if comp_log.exists():
        passed_gates += 1
        findings.append({"gate": "G-01 (Skill Ambassador Log)", "status": "PASS", "detail": "SKILL_COMPLIANCE_LOG.md active."})
    else:
        findings.append({"gate": "G-01 (Skill Ambassador Log)", "status": "VIOLATION", "detail": "Missing .agents/SKILL_COMPLIANCE_LOG.md (Run --init-log first)."})

    # 5. Check Task Queue synchronization (tasks/current_task.md or .agents/PLAN_TASKS.md)
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

    return {
        "ambassador_verdict": "APPROVED" if not violations else "BLOCKED_BY_SKILL_VIOLATIONS",
        "compliance_score_pct": compliance_pct,
        "gates_passed": passed_gates,
        "total_gates_checked": total_gates,
        "violations_count": len(violations),
        "findings": findings
    }


def run_self_test() -> None:
    """Runs deterministic self-tests on Skill Ambassador log initialization and workspace auditing."""
    checks = []
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp)
        # 1. Initialize compliance log
        log_path = init_compliance_log(ws, "Inbox Broadcast Area")
        assert log_path.exists()
        checks.append("Skill Ambassador Charter Initialization (--init-log): PASS")

        # 2. Audit incomplete workspace -> must return BLOCKED_BY_SKILL_VIOLATIONS
        incomplete = audit_workspace_compliance(ws, require_ui_mock=True)
        assert incomplete["ambassador_verdict"] == "BLOCKED_BY_SKILL_VIOLATIONS"
        assert incomplete["violations_count"] > 0
        checks.append("Incomplete Workspace Violation Detection: PASS")

        # 3. Populate required artifacts and verify 100% APPROVED verdict
        (ws / ".agents" / "mocks").mkdir(parents=True, exist_ok=True)
        (ws / ".agents" / "mocks" / "inbox_area.html").write_text("<div>Mock</div>", encoding="utf-8")
        (ws / ".agents" / "SPEC_AND_AUDIT.md").write_text("Call-Chain Map and 3-Layer Outcome Oracle", encoding="utf-8")
        (ws / ".agents" / "AI_HANDOFF_LEDGER.md").write_text("Round 1 Diff Audit + 3-Layer Persistence Oracle", encoding="utf-8")
        (ws / "tasks").mkdir(parents=True, exist_ok=True)
        (ws / "tasks" / "current_task.md").write_text("- [x] Inbox feature verified\n", encoding="utf-8")

        complete = audit_workspace_compliance(ws, require_ui_mock=True)
        assert complete["ambassador_verdict"] == "APPROVED"
        assert complete["compliance_score_pct"] == 100
        checks.append("Compliant Workspace 100% Verification: PASS")

    print(json.dumps({
        "self_test_status": "PASS",
        "checks_executed": len(checks),
        "details": checks
    }, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="MACA Skill Ambassador & Procedural Compliance Referee")
    parser.add_argument("--self-test", action="store_true", help="Run built-in verification self-tests and exit")
    parser.add_argument("--init-log", type=str, metavar="WORKSPACE_DIR", help="Initialize .agents/SKILL_COMPLIANCE_LOG.md in workspace")
    parser.add_argument("--feature", type=str, default="Active Feature Slice", help="Feature name for --init-log")
    parser.add_argument("--audit-workspace", type=str, metavar="WORKSPACE_DIR", help="Audit workspace for MACA skill compliance")
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

        if args.audit_workspace:
            report = audit_workspace_compliance(
                Path(args.audit_workspace).resolve(),
                require_ui_mock=not args.no_ui_mock
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
