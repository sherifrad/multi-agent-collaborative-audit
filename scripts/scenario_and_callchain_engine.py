#!/usr/bin/env python3
"""
================================================================================
MACA v2 Phase 4 Sequential Scenario, Auth Fuzzing & Call-Chain Engine
(scripts/scenario_and_callchain_engine.py)
--------------------------------------------------------------------------------
Provides deterministic CLI tooling for Phase 4 of MACA v2:
1. Interactive / CLI Scenario Mode Generation & Anti-Bulk-Mock Validation:
   - Mode A (predefined): Standard sequential regression & boundary suite.
   - Mode B (imaginary): Realistic multi-hour clinical/domain case progressions
     with fast-forward intake.
   - Mode C (custom): Parses user-supplied step-by-step hourly inputs.
2. Upgrade 1 & 2 Generators (MACA v2 Post-Mortem Enhancements):
   - --auth-fuzz-matrix: Generates the 6-permutation Tabula Rasa RBAC & Identity
     Fuzzing Matrix (email-in-username, casing, whitespace, unverified provider,
     +fake suffix, standard clinician).
   - --geometric-oracle-template: Emits the Compose / Web Bounding-Box
     Differential Assertion snippet for TopBars, Action Trays, and narrow screens.
3. Static Cross-Function Call-Chain & Multi-Caller Wiring Auditor.
================================================================================
"""

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List


IMAGINARY_CLINICAL_SCENARIOS: List[Dict[str, Any]] = [
    {
        "id": "SCENARIO-PROLONGED-LABOUR-01",
        "title": "Prolonged Active First Stage (Cervical Arrest at 6 cm)",
        "fast_forward_intake": {
            "patient_name": "Sara M.",
            "age": 26,
            "parity": "NULLIPAROUS",
            "admitted_at": "10:00",
            "active_first_stage_confirmed_cm": 5.0
        },
        "sequential_steps": [
            {
                "step_order": 1,
                "timestamp": "10:00",
                "elapsed_hours": 0.0,
                "inputs": {"dilatation_cm": 6.0, "descent_fifths": "4/5", "fhr_bpm": 140, "contractions_per_10m": 3, "duration_s": 35},
                "expected_oracle": {
                    "domain": "Anchor set at 6.0 cm (10:00); zero cervical lag alerts emitted.",
                    "persistence": "ObservationBundle #1 committed with dilatationTenths=60.",
                    "ui": "6 cm plotted on X curve at 10:00; no lag alert badge."
                }
            },
            {
                "step_order": 2,
                "timestamp": "12:00",
                "elapsed_hours": 2.0,
                "inputs": {"dilatation_cm": 6.0, "descent_fifths": "4/5", "fhr_bpm": 138, "contractions_per_10m": 3, "duration_s": 35},
                "expected_oracle": {
                    "domain": "Elapsed at 6.0 cm = 2.0h (< 5.0h WHO threshold); zero lag alert (Negative Control).",
                    "persistence": "ObservationBundle #2 appended; #1 preserved unchanged.",
                    "ui": "Second 6 cm X plotted at 12:00; alert queue remains clear."
                }
            },
            {
                "step_order": 3,
                "timestamp": "15:00",
                "elapsed_hours": 5.0,
                "inputs": {"dilatation_cm": 6.0, "descent_fifths": "4/5", "fhr_bpm": 144, "contractions_per_10m": 3, "duration_s": 30},
                "expected_oracle": {
                    "domain": "Elapsed at 6.0 cm = 5.0h (>= 5.0h threshold) -> emits WHO-LCG-ALERT-020 (CONFIRMED).",
                    "persistence": "ObservationBundle #3 committed; 3 sequential rows in DB.",
                    "ui": "WHO-LCG-ALERT-020 badge visible on 15:00 cell and Active Alert Queue."
                }
            }
        ]
    },
    {
        "id": "SCENARIO-FETAL-DECEL-TACHYSYSTOLE-02",
        "title": "Fetal Bradycardia & Late Deceleration with Consecutive Contraction Windows",
        "fast_forward_intake": {
            "patient_name": "Nour A.",
            "age": 31,
            "parity": "MULTIPAROUS",
            "admitted_at": "08:00",
            "active_first_stage_confirmed_cm": 5.0
        },
        "sequential_steps": [
            {
                "step_order": 1,
                "timestamp": "08:00",
                "elapsed_hours": 0.0,
                "inputs": {"fhr_bpm": 142, "deceleration": "NONE", "contractions_per_10m": 6, "duration_s": 45},
                "expected_oracle": {
                    "domain": "First abnormal contraction window (>5/10m) -> emits PROVISIONAL_RECHECK_DUE (not CONFIRMED).",
                    "persistence": "ObservationBundle #1 committed.",
                    "ui": "Provisional recheck prompt displayed; no confirmed tachysystole escalation yet."
                }
            },
            {
                "step_order": 2,
                "timestamp": "08:30",
                "elapsed_hours": 0.5,
                "inputs": {"fhr_bpm": 104, "deceleration": "LATE", "contractions_per_10m": 6, "duration_s": 50},
                "expected_oracle": {
                    "domain": "Second consecutive window confirms contraction alert + emits WHO-LCG-ALERT-005 (FHR < 110) and WHO-LCG-ALERT-006 (Late Deceleration).",
                    "persistence": "ObservationBundle #2 committed with FHR=104, decel=LATE.",
                    "ui": "High-contrast red badges on FHR and Deceleration cells; top priority in Shift Handoff card."
                }
            }
        ]
    },
    {
        "id": "SCENARIO-MATERNAL-PREECLAMPSIA-03",
        "title": "Maternal Moderate BP Repeat Confirmation & Severe BP Escalation",
        "fast_forward_intake": {
            "patient_name": "Heba K.",
            "age": 29,
            "parity": "NULLIPAROUS",
            "admitted_at": "12:00",
            "active_first_stage_confirmed_cm": 5.0
        },
        "sequential_steps": [
            {
                "step_order": 1,
                "timestamp": "12:00",
                "elapsed_hours": 0.0,
                "inputs": {"sbp": 145, "dbp": 92, "pulse": 88, "temp_c": 37.0, "urine_protein": "++"},
                "expected_oracle": {
                    "domain": "Emits WHO SBP/DBP/Protein reference signals + EHC Proteinuria-with-Hypertension warning; moderate BP repeat pending.",
                    "persistence": "MaternalVitalEntity & UrinalysisEntity #1 committed.",
                    "ui": "WHO reference highlights on SBP, DBP, and P++; repeat BP due timer shown."
                }
            },
            {
                "step_order": 2,
                "timestamp": "12:25",
                "elapsed_hours": 0.42,
                "inputs": {"sbp": 148, "dbp": 95, "pulse": 92},
                "expected_oracle": {
                    "domain": "Second reading within 15-30m confirms EHC repeat hypertension specialist review.",
                    "persistence": "MaternalVitalEntity #2 committed.",
                    "ui": "Confirmed EHC specialist review banner active."
                }
            },
            {
                "step_order": 3,
                "timestamp": "13:00",
                "elapsed_hours": 1.0,
                "inputs": {"sbp": 164, "dbp": 112, "pulse": 96},
                "expected_oracle": {
                    "domain": "Single severe reading (SBP >= 160 / DBP >= 110) immediately emits IMMEDIATE_SAFETY_ACTION.",
                    "persistence": "MaternalVitalEntity #3 committed.",
                    "ui": "Immediate safety action card pinned at top of case view and Shift Handoff summary."
                }
            }
        ]
    }
]


def generate_auth_fuzz_matrix(admin_email: str = "dr.sherif1992@gmail.com") -> Dict[str, Any]:
    """Generates the MACA v2 Tabula Rasa Auth & RBAC Permutation Matrix (Upgrade 2)."""
    local_part, domain = admin_email.split("@", 1) if "@" in admin_email else (admin_email, "gmail.com")
    return {
        "upgrade": "MACA v2 Upgrade 2 — Tabula Rasa Auth & RBAC Claim Fuzzing Matrix",
        "target_admin_identity": admin_email,
        "permutations": [
            {
                "id": "AUTH-FUZZ-01 (Clean Match)",
                "username_input": admin_email,
                "email_input": admin_email,
                "provider": "google.com",
                "email_verified": True,
                "expected_role": "ADMIN"
            },
            {
                "id": "AUTH-FUZZ-02 (Email Entered in Legacy Username Field)",
                "username_input": admin_email,
                "email_input": None,
                "provider": "google.com",
                "email_verified": True,
                "expected_role": "ADMIN"
            },
            {
                "id": "AUTH-FUZZ-03 (Case & Whitespace Invariance)",
                "username_input": f"  {admin_email.upper()} ",
                "email_input": f" {admin_email.upper()}  ",
                "provider": "google.com",
                "email_verified": True,
                "expected_role": "ADMIN"
            },
            {
                "id": "AUTH-FUZZ-04 (Unverified Local Password Spoof Attempt)",
                "username_input": admin_email,
                "email_input": admin_email,
                "provider": "password",
                "email_verified": False,
                "expected_role": "NON_ADMIN_REJECTED"
            },
            {
                "id": "AUTH-FUZZ-05 (Malicious Plus-Alias Spoof Attempt)",
                "username_input": f"{local_part}+attacker@{domain}",
                "email_input": f"{local_part}+attacker@{domain}",
                "provider": "google.com",
                "email_verified": True,
                "expected_role": "NON_ADMIN_REJECTED"
            },
            {
                "id": "AUTH-FUZZ-06 (Standard Clinician Account)",
                "username_input": "dr.ahmed.ali",
                "email_input": f"ahmed@{domain}",
                "provider": "password",
                "email_verified": True,
                "expected_role": "DOCTOR_NON_ADMIN"
            }
        ]
    }


GEOMETRIC_ORACLE_TEMPLATE = """// MACA v2 Upgrade 1 — Layer 3 Geometric & Multi-Viewport Bounding-Box Oracle
val navBounds = composeTestRule.onNodeWithTag("NavIcon").getUnclippedBoundsInRoot()
val titleBounds = composeTestRule.onNodeWithTag("TopBarTitle").getUnclippedBoundsInRoot()
val actionsBounds = composeTestRule.onNodeWithTag("ActionsCluster").getUnclippedBoundsInRoot()

// 1. Assert zero horizontal overlap on 320dp / 360dp narrow screens
assertTrue(titleBounds.left >= navBounds.right, "Geometric Escape: Title overlaps start navigation icon")
assertTrue(titleBounds.right <= actionsBounds.left, "Geometric Escape: Title overlaps end action tray")

// 2. Assert minimum readable title flex budget (>= 120.dp)
val availableTitleWidth = actionsBounds.left - navBounds.right
assertTrue(availableTitleWidth >= 120.dp, "Geometric Escape: Action cluster choked title width below 120.dp")
"""


def emit_fail_closed_error(error_code: str, message: str, remediation: str) -> None:
    payload = {
        "status": "MACA_SCRIPT_ERROR — STOP_AND_FIX",
        "error_code": error_code,
        "message": message,
        "mandatory_agent_action": "DO NOT SKIP OR BYPASS THIS STEP. Fix the input/environment as described in 'remediation' and re-run, or halt and report UNKNOWN / HARNESS ERROR.",
        "remediation": remediation
    }
    print(json.dumps(payload, indent=2), file=sys.stderr)
    sys.exit(2)


def parse_custom_sequence(spec_str: str) -> Dict[str, Any]:
    raw_steps = [s.strip() for s in re.split(r"[;\n]+", spec_str) if s.strip()]
    steps = []
    for idx, raw in enumerate(raw_steps, start=1):
        tokens = raw.split()
        timestamp = tokens[0] if tokens and ":" in tokens[0] else f"Step-{idx}"
        kv_tokens = tokens[1:] if ":" in (tokens[0] if tokens else "") else tokens
        inputs: Dict[str, Any] = {}
        for tok in kv_tokens:
            if "=" in tok:
                k, v = tok.split("=", 1)
                v_clean = v.strip().rstrip(",")
                try:
                    inputs[k.strip()] = float(v_clean) if "." in v_clean else int(v_clean)
                except ValueError:
                    inputs[k.strip()] = v_clean
        if not inputs:
            raise ValueError(
                f"Step {idx} ('{raw}') contains no key=value pairs. Format example: '10:00 dilatation=5 fhr=140; 11:00 dilatation=6 fhr=135'"
            )
        steps.append({
            "step_order": idx,
            "timestamp": timestamp,
            "inputs": inputs,
            "execution_rule": "INCREMENTAL_SAVE_AND_REHYDRATE_REQUIRED"
        })

    if len(steps) < 2:
        raise ValueError(
            "Anti-Bulk-Mock Violation: A sequential scenario must contain at least 2 distinct time steps separated by ';' or newline."
        )

    return {
        "mode": "Mode C (User Custom Sequential Timeline)",
        "anti_bulk_mock_enforced": True,
        "fast_forward_intake": {
            "patient_name": "FastForward_Case_01",
            "parity": "NULLIPAROUS",
            "note": "Static intake pre-seeded so test focuses on sequential observation steps."
        },
        "sequential_steps": steps
    }


def trace_call_chain(root_dir: Path, symbol: str) -> Dict[str, Any]:
    if not root_dir.exists() or not root_dir.is_dir():
        raise FileNotFoundError(f"Target trace directory does not exist: {root_dir}")

    exts = {".kt", ".ts", ".tsx", ".js", ".py"}
    ignored = {"node_modules", ".git", "build", "dist", ".gradle", "__pycache__"}

    definitions: List[str] = []
    prod_callers: List[str] = []
    test_callers: List[str] = []
    forbidden_internal_mocks: List[str] = []

    def_pattern = re.compile(rf"\b(fun|function|def|class|object|const)\s+{re.escape(symbol)}\b")
    call_pattern = re.compile(rf"\b{re.escape(symbol)}\s*(\(|\.)")
    mock_pattern = re.compile(
        rf"(vi\.mock|jest\.mock|mockk\s*<\s*{re.escape(symbol)}|every\s*\{{[^}}]*\b{re.escape(symbol)}\b)"
    )

    for path in root_dir.rglob("*"):
        if not path.is_file() or path.suffix not in exts:
            continue
        if any(part in ignored for part in path.parts):
            continue

        rel = str(path.relative_to(root_dir))
        is_test = any(t in rel.lower() for t in ["test", "spec", "__tests__", "androidtest", "e2e"])

        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue

        for line_no, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("#") or stripped.startswith("*"):
                continue
            loc = f"{rel}:{line_no}"
            if def_pattern.search(line):
                definitions.append(loc)
            elif call_pattern.search(line):
                if is_test:
                    test_callers.append(loc)
                else:
                    prod_callers.append(loc)
            if is_test and mock_pattern.search(line):
                forbidden_internal_mocks.append(loc)

    return {
        "symbol": symbol,
        "definitions": definitions,
        "production_call_sites": prod_callers,
        "production_caller_count": len(prod_callers),
        "test_call_sites": test_callers,
        "forbidden_internal_mocks_detected": forbidden_internal_mocks,
        "call_chain_status": "FAIL (Internal Mock Detected)" if forbidden_internal_mocks else "PASS"
    }


def run_self_test() -> None:
    checks = []

    # 1. Test Mode B Imaginary Scenarios structure
    assert len(IMAGINARY_CLINICAL_SCENARIOS) >= 3
    checks.append("Mode B (Imaginary Scenarios): PASS")

    # 2. Test Mode C Custom Sequence parser
    plan = parse_custom_sequence("10:00 dilatation=5 fhr=140; 11:00 dilatation=6.5 fhr=135")
    assert plan["anti_bulk_mock_enforced"] is True and len(plan["sequential_steps"]) == 2
    checks.append("Mode C (Custom Multi-Step Parser): PASS")

    # 3. Test Anti-Bulk-Mock rejection of single-step input
    rejected = False
    try:
        parse_custom_sequence("10:00 dilatation=5 fhr=140")
    except ValueError:
        rejected = True
    assert rejected is True
    checks.append("Anti-Bulk-Mock Single-Step Rejection Guard: PASS")

    # 4. Test MACA v2 Auth Fuzz Matrix generator
    fuzz = generate_auth_fuzz_matrix("dr.sherif1992@gmail.com")
    assert len(fuzz["permutations"]) == 6
    checks.append("Upgrade 2 (Tabula Rasa 6-Permutation Auth Fuzz Matrix): PASS")

    # 5. Test Call-Chain Tracer & Forbidden Internal Mock Detection
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "Evaluator.kt").write_text("object LcgAlertEvaluator {\n  fun evaluateCase(x: Int): Int = x + 1\n}\n", encoding="utf-8")
        (tmp_path / "BedsideViewModel.kt").write_text("class BedsideViewModel {\n  fun save() { val r = LcgAlertEvaluator.evaluateCase(5) }\n}\n", encoding="utf-8")
        clean_trace = trace_call_chain(tmp_path, "evaluateCase")
        assert clean_trace["production_caller_count"] == 1 and clean_trace["call_chain_status"] == "PASS"
    checks.append("Call-Chain Multi-Caller & Forbidden-Mock Detector: PASS")

    print(json.dumps({
        "self_test_status": "PASS",
        "checks_executed": len(checks),
        "details": checks
    }, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="MACA v2 Phase 4 Sequential Scenario, Auth Fuzzing & Call-Chain Engine")
    parser.add_argument("--self-test", action="store_true", help="Run built-in verification self-tests and exit")
    parser.add_argument("--mode", choices=["predefined", "imaginary", "custom"], help="Scenario generation mode")
    parser.add_argument("--custom-steps", type=str, default="", help="Semicolon-separated step sequence for --mode custom")
    parser.add_argument("--auth-fuzz-matrix", nargs="?", const="dr.sherif1992@gmail.com", metavar="ADMIN_EMAIL", help="Generate 6-row Tabula Rasa RBAC & Identity permutation test matrix")
    parser.add_argument("--geometric-oracle", action="store_true", help="Print Layer 3 Bounding-Box Differential Oracle template")
    parser.add_argument("--trace-dir", type=str, default="", help="Directory to scan for cross-function call-chain wiring")
    parser.add_argument("--symbol", type=str, default="", help="Function, method, or class name to trace across all callers")

    try:
        args = parser.parse_args()

        if args.self_test:
            run_self_test()
            return

        if args.auth_fuzz_matrix:
            print(json.dumps(generate_auth_fuzz_matrix(args.auth_fuzz_matrix), indent=2))
            return

        if args.geometric_oracle:
            print(GEOMETRIC_ORACLE_TEMPLATE)
            return

        if args.trace_dir or args.symbol:
            if not (args.trace_dir and args.symbol):
                emit_fail_closed_error(
                    "MISSING_TRACE_ARGS",
                    "Both --trace-dir and --symbol must be provided together.",
                    "Pass --trace-dir <path_to_code> and --symbol <function_or_class_name>."
                )
            report = trace_call_chain(Path(args.trace_dir).resolve(), args.symbol)
            print(json.dumps(report, indent=2))
            sys.exit(0 if report["call_chain_status"] == "PASS" else 1)

        if args.mode == "imaginary":
            print(json.dumps({
                "mode": "Mode B (AI-Proposed Imaginary Clinical Scenarios)",
                "instructions": "Present these scenarios to the user for selection, fast-forward intake, and execute each step sequentially.",
                "scenarios": IMAGINARY_CLINICAL_SCENARIOS
            }, indent=2))
            return

        if args.mode == "custom":
            if not args.custom_steps:
                emit_fail_closed_error(
                    "MISSING_CUSTOM_STEPS",
                    "--custom-steps is required when --mode custom is selected.",
                    "Provide at least 2 semicolon-separated time steps, e.g. --custom-steps '10:00 dilatation=5 fhr=140; 12:00 dilatation=6 fhr=105'."
                )
            plan = parse_custom_sequence(args.custom_steps)
            print(json.dumps(plan, indent=2))
            return

        if args.mode == "predefined":
            print(json.dumps({
                "mode": "Mode A (Predefined Standard Suite)",
                "anti_bulk_mock_enforced": True,
                "required_layers": [
                    "Logical Domain Oracle",
                    "Persistence DB Oracle",
                    "Visual & Geometric Bounding-Box UI Oracle",
                    "Tabula Rasa Auth Fuzz Matrix",
                    "Negative Control"
                ],
                "baseline_scenarios": [s["id"] for s in IMAGINARY_CLINICAL_SCENARIOS]
            }, indent=2))
            return

        parser.print_help()
    except Exception as exc:
        emit_fail_closed_error(
            type(exc).__name__,
            str(exc),
            "Run 'python3 scripts/scenario_and_callchain_engine.py --self-test' to verify script health."
        )


if __name__ == "__main__":
    main()
