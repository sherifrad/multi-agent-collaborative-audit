#!/usr/bin/env python3
"""
================================================================================
MACA v2 Automated SaMD Invariant, RBAC & JVM Bytecode Budget Linter
(scripts/lint_samd_invariants.py)
--------------------------------------------------------------------------------
Implements Upgrades 2, 3, and 4 from the MACA Engineering Post-Mortem:
1. Rule SaMD-ZERO-DELETE (Defect D-3 Guard):
   Detects raw SQL `DELETE FROM` or unscoped deletion calls targeting clinical
   entities (`labour_case`, `patient`, `observation_bundle`, `audit_event`,
   `LabourCaseEntity`, `PatientEntity`, `ObservationBundleEntity`, `AuditEventEntity`)
   unless guarded by `@SyntheticMockDataPurgeOnly` or `isMockCaseId`.
2. Rule JVM-PARAM-BUDGET (Defect D-5 Guard):
   Scans Kotlin/TypeScript constructors and functions for parameter sprawl to
   prevent `java.lang.ClassFormatError` (JVM 255-word method descriptor limit).
   - Warning threshold: >= 20 parameters
   - Hard Blocker threshold: >= 35 parameters
3. Rule RBAC-STRING-HEURISTIC (Defect D-2 Guard):
   Flags fragile client-side admin string matching (`username == "dr.` or
   `email == "dr.`) that lacks cryptographic claim verification.
================================================================================
"""

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List


CLINICAL_TABLES_AND_ENTITIES = (
    "labour_case",
    "patient",
    "observation_bundle",
    "audit_event",
    "fhr_sample",
    "LabourCaseEntity",
    "PatientEntity",
    "ObservationBundleEntity",
    "AuditEventEntity",
)

SAFE_DELETE_GUARDS = (
    "@SyntheticMockDataPurgeOnly",
    "isMockCaseId",
    "clearMockCasesInternal",
    "CaseStatus.CLOSED",
)


def emit_fail_closed_error(error_code: str, message: str, remediation: str) -> None:
    payload = {
        "status": "MACA_SCRIPT_ERROR — STOP_AND_FIX",
        "error_code": error_code,
        "message": message,
        "mandatory_agent_action": "DO NOT SKIP OR BYPASS THIS STEP. Fix the error described below and re-run.",
        "remediation": remediation
    }
    print(json.dumps(payload, indent=2), file=sys.stderr)
    sys.exit(2)


def scan_file_for_invariants(file_path: Path, rel_path: str) -> Dict[str, List[Dict[str, Any]]]:
    blockers: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {"blockers": blockers, "warnings": warnings}

    lines = content.splitlines()
    is_test_file = any(tok in rel_path.lower() for tok in ["test", "spec", "mock", "androidtest"])

    # 1. Check SaMD Zero Hard-Delete Rule (skip test files)
    if not is_test_file:
        delete_sql_pattern = re.compile(
            r"DELETE\s+FROM\s+(" + "|".join(CLINICAL_TABLES_AND_ENTITIES) + r")\b",
            re.IGNORECASE
        )
        for idx, line in enumerate(lines, start=1):
            if delete_sql_pattern.search(line):
                # Check surrounding 12-line window for safe guards
                start_w = max(0, idx - 8)
                end_w = min(len(lines), idx + 6)
                window_text = "\n".join(lines[start_w:end_w])
                if not any(guard in window_text for guard in SAFE_DELETE_GUARDS):
                    blockers.append({
                        "rule": "SaMD-ZERO-DELETE (Defect D-3)",
                        "location": f"{rel_path}:{idx}",
                        "line": line.strip(),
                        "remediation": (
                            "Hard-deleting clinical records violates SaMD retention invariants. "
                            "Transition real clinical records to CaseStatus.CLOSED with an AuditEventEntity, "
                            "or guard synthetic deletion with MockCasesCatalog.isMockCaseId(id) / @SyntheticMockDataPurgeOnly."
                        )
                    })

    # 2. Check Fragile RBAC String Heuristics (skip test files)
    if not is_test_file:
        rbac_pattern = re.compile(r"(isSystemAdmin|isAdmin)\s*=.*?\b(username|email)\s*==\s*\"[^\"]+\"")
        for idx, line in enumerate(lines, start=1):
            if rbac_pattern.search(line):
                start_w = max(0, idx - 4)
                end_w = min(len(lines), idx + 4)
                window_text = "\n".join(lines[start_w:end_w])
                if "email_verified" not in window_text and "FirebaseAuthBridge" not in window_text:
                    blockers.append({
                        "rule": "RBAC-STRING-HEURISTIC (Defect D-2)",
                        "location": f"{rel_path}:{idx}",
                        "line": line.strip(),
                        "remediation": (
                            "Do not determine admin rights via raw username/email string equality alone. "
                            "Require verified identity claims (email_verified == true / FirebaseAuthBridge.isCurrentUserAdmin())."
                        )
                    })

    # 3. Check Constructor / Function Parameter Budgeting (JVM 255-word limit guard)
    if file_path.suffix in {".kt", ".ts", ".tsx"}:
        decl_pattern = re.compile(r"\b(data\s+class|class|fun|function)\s+([A-Za-z0-9_]+)\s*\(")
        for match in decl_pattern.finditer(content):
            decl_kind = match.group(1)
            decl_name = match.group(2)
            open_paren_idx = match.end() - 1
            line_no = content[:match.start()].count("\n") + 1

            # Find matching closing parenthesis
            depth = 0
            close_paren_idx = -1
            for i in range(open_paren_idx, min(len(content), open_paren_idx + 12000)):
                ch = content[i]
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        close_paren_idx = i
                        break

            if close_paren_idx != -1:
                params_block = content[open_paren_idx + 1:close_paren_idx].strip()
                if not params_block:
                    continue
                # Count top-level commas inside the parameter list
                param_count = 1
                nested = 0
                for ch in params_block:
                    if ch in "(<[{":
                        nested += 1
                    elif ch in ")>]}":
                        nested = max(0, nested - 1)
                    elif ch == "," and nested == 0:
                        param_count += 1

                # Check for @Suppress annotations on the declaration
                start_w = max(0, line_no - 6)
                end_w = min(len(lines), line_no + 2)
                window_text = "\n".join(lines[start_w:end_w])
                if any(sup in window_text for sup in ("JVM-PARAM-BUDGET", "LongParameterList", "LargeClass")):
                    continue

                if param_count >= 35:
                    blockers.append({
                        "rule": "JVM-PARAM-BUDGET-BLOCKER (Defect D-5)",
                        "location": f"{rel_path}:{line_no}",
                        "symbol": f"{decl_kind} {decl_name} ({param_count} parameters)",
                        "remediation": (
                            f"'{decl_name}' has {param_count} parameters (exceeds hard limit of 35). "
                            "Decompose into nested domain value objects (e.g. GuidanceStrings) to prevent JVM ClassFormatError."
                        )
                    })
                elif param_count >= 20:
                    warnings.append({
                        "rule": "JVM-PARAM-BUDGET-WARNING (Defect D-5)",
                        "location": f"{rel_path}:{line_no}",
                        "symbol": f"{decl_kind} {decl_name} ({param_count} parameters)",
                        "remediation": (
                            f"'{decl_name}' has {param_count} parameters (approaching architectural sprawl threshold of 20). "
                            "Consider grouping related fields into sub-objects."
                        )
                    })

    return {"blockers": blockers, "warnings": warnings}


def scan_directory(root_dir: Path) -> Dict[str, Any]:
    if not root_dir.exists() or not root_dir.is_dir():
        raise FileNotFoundError(f"Scan directory does not exist: {root_dir}")

    exts = {".kt", ".ts", ".tsx", ".sql"}
    ignored = {"node_modules", ".git", "build", "dist", ".gradle", "__pycache__", "vendor"}

    all_blockers: List[Dict[str, Any]] = []
    all_warnings: List[Dict[str, Any]] = []
    files_scanned = 0

    for path in root_dir.rglob("*"):
        if not path.is_file() or path.suffix not in exts:
            continue
        if any(part in ignored for part in path.parts):
            continue
        files_scanned += 1
        rel = str(path.relative_to(root_dir))
        res = scan_file_for_invariants(path, rel)
        all_blockers.extend(res["blockers"])
        all_warnings.extend(res["warnings"])

    return {
        "linter_status": "PASS" if len(all_blockers) == 0 else "FAIL_HARD_BLOCKERS",
        "files_scanned": files_scanned,
        "hard_blockers_count": len(all_blockers),
        "warnings_count": len(all_warnings),
        "hard_blockers": all_blockers,
        "warnings": all_warnings
    }


def run_self_test() -> None:
    checks = []
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp)

        # 1. Inject Defect D-3 (unscoped DELETE FROM labour_case)
        bad_dao = ws / "BadClinicalDao.kt"
        bad_dao.write_text(
            'class BadClinicalDao {\n  fun nuke() { db.execSQL("DELETE FROM labour_case WHERE id = ?") }\n}\n',
            encoding="utf-8"
        )
        # 2. Inject Defect D-5 (36-parameter data class)
        params_36 = ", ".join(f"val p{i}: String" for i in range(1, 37))
        bad_strings = ws / "BloatedStrings.kt"
        bad_strings.write_text(f"data class BloatedStrings({params_36})\n", encoding="utf-8")

        # 3. Inject Defect D-2 (fragile username string check)
        bad_auth = ws / "BadAuth.kt"
        bad_auth.write_text(
            'class BadAuth {\n  val isSystemAdmin = username == "dr.sherif"\n}\n',
            encoding="utf-8"
        )

        fail_report = scan_directory(ws)
        assert fail_report["linter_status"] == "FAIL_HARD_BLOCKERS"
        assert fail_report["hard_blockers_count"] == 3, f"Expected 3 blockers, got {fail_report['hard_blockers_count']}"
        checks.append("Defect D-2 (RBAC String Heuristic) Detection: PASS")
        checks.append("Defect D-3 (SaMD Hard-Delete SQL) Detection: PASS")
        checks.append("Defect D-5 (JVM >=35 Parameter Budget Blocker) Detection: PASS")

        # 4. Now replace with compliant code and verify PASS
        bad_dao.write_text(
            'class SafeClinicalDao {\n  // Guarded by MockCasesCatalog.isMockCaseId(id)\n  fun purgeMock() { db.execSQL("DELETE FROM labour_case WHERE id = ?") }\n}\n',
            encoding="utf-8"
        )
        bad_strings.write_text("data class GuidanceStrings(val title: String, val body: String)\n", encoding="utf-8")
        bad_auth.write_text(
            'class SafeAuth {\n  val isSystemAdmin = FirebaseAuthBridge.isCurrentUserAdmin()\n}\n',
            encoding="utf-8"
        )
        pass_report = scan_directory(ws)
        assert pass_report["linter_status"] == "PASS"
        assert pass_report["hard_blockers_count"] == 0
        checks.append("Compliant SaMD / JVM / RBAC Verification: PASS")

    print(json.dumps({
        "self_test_status": "PASS",
        "checks_executed": len(checks),
        "details": checks
    }, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="MACA v2 Automated SaMD, RBAC & JVM Bytecode Budget Linter")
    parser.add_argument("--self-test", action="store_true", help="Run built-in verification self-tests and exit")
    parser.add_argument("--scan-dir", type=str, metavar="DIR", help="Directory to scan for SaMD, RBAC, and JVM invariants")

    try:
        args = parser.parse_args()
        if args.self_test:
            run_self_test()
            return
        if args.scan_dir:
            report = scan_directory(Path(args.scan_dir).resolve())
            print(json.dumps(report, indent=2))
            sys.exit(0 if report["linter_status"] == "PASS" else 1)
        parser.print_help()
    except Exception as exc:
        emit_fail_closed_error(
            type(exc).__name__,
            str(exc),
            "Run 'python3 scripts/lint_samd_invariants.py --self-test' to verify the SaMD & JVM linter."
        )


if __name__ == "__main__":
    main()
