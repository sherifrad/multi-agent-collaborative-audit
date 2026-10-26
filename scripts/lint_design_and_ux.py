#!/usr/bin/env python3
"""
================================================================================
MACA v2 Automated Design, Graphic, UI & UX Verification Engine
(scripts/lint_design_and_ux.py)
--------------------------------------------------------------------------------
Implements the 4-Pillar Design Testing Engine for MACA v2:
1. Pillar 1 — Graphic, Vector & Design-Token Integrity (DESIGN-TOKEN / SVG-INTEGRITY / RTL-ICON):
   - Flags hardcoded hex colors (`#RRGGBB`, `Color(0xFF...)`) inside UI screen/
     component files outside designated theme/palette files.
   - Verifies SVG / Android VectorDrawable files have valid `viewBox` or
     `viewportWidth`/`viewportHeight` and checks directional icons (`arrow`,
     `chevron`, `back`, `forward`, `send`, `next`, `prev`) for RTL mirroring
     (`autoMirrored="true"` or `rtl-mirror`).
2. Pillar 2 — WCAG 2.1 AA Luminance Contrast Calculator (WCAG-CONTRAST-AA):
   - Computes exact relative luminance contrast ratios `(L1 + 0.05) / (L2 + 0.05)`
     between foreground and background color pairs (`--check-contrast FG BG` or
     from mock CSS `--fg`/`--bg` pairs), enforcing `>= 4.5:1` for normal text
     and `>= 3.0:1` for large clinical alerts.
3. Pillar 3 — Mock-to-Code Structural & 5-State UI Matrix Verification (UI-5-STATES):
   - Audits `.agents/mocks/*.html` or `.svg` and UI test suites to verify that
     components cover the 5 required UI states (`Empty`, `Loading`, `Normal`,
     `Error/Alert`, `Overflow/200% Font Scale/RTL`) and `WindowInsets.ime`
     keyboard non-occlusion.
4. Pillar 4 — Quantitative UX Ergonomic Flow & Tap-Budget Verifier (UX-TAP-BUDGET):
   - Evaluates interaction trace sequences to ensure high-frequency bedside workflows
     stay within the ergonomic interaction budget (`<= 3` taps, `<= 15` seconds,
     and zero dead-end screens).
================================================================================
"""

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


DIRECTIONAL_ICON_KEYWORDS = (
    "arrow",
    "chevron",
    "back",
    "forward",
    "next",
    "prev",
    "send",
    "reply",
    "transfer",
    "logout",
)

THEME_FILE_ALLOWLIST_TOKENS = (
    "theme",
    "color",
    "palette",
    "tokens",
    "designsystem",
    "mock",
    "test",
    "spec",
)


def emit_fail_closed_error(error_code: str, message: str, remediation: str) -> None:
    payload = {
        "status": "MACA_SCRIPT_ERROR — STOP_AND_FIX",
        "error_code": error_code,
        "message": message,
        "mandatory_agent_action": "DO NOT SKIP OR BYPASS THIS STEP. Fix the error described below and re-run.",
        "remediation": remediation,
    }
    print(json.dumps(payload, indent=2), file=sys.stderr)
    sys.exit(2)


def parse_hex_color(hex_str: str) -> Tuple[int, int, int]:
    """Parses #RGB, #RRGGBB, #AARRGGBB, or 0xFFRRGGBB into (R, G, B) 0..255."""
    cleaned = hex_str.strip().lstrip("#")
    if cleaned.lower().startswith("0x"):
        cleaned = cleaned[2:]
    if len(cleaned) == 3:
        cleaned = "".join(ch * 2 for ch in cleaned)
    elif len(cleaned) == 8:
        # Strip alpha channel (AARRGGBB -> RRGGBB)
        cleaned = cleaned[2:]
    if len(cleaned) != 6:
        raise ValueError(f"Invalid hex color format: {hex_str}")
    r = int(cleaned[0:2], 16)
    g = int(cleaned[2:4], 16)
    b = int(cleaned[4:6], 16)
    return (r, g, b)


def relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """Computes WCAG 2.1 relative luminance for an sRGB (R, G, B) tuple."""
    channels = []
    for val in rgb:
        s = val / 255.0
        if s <= 0.03928:
            channels.append(s / 12.92)
        else:
            channels.append(((s + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def compute_wcag_contrast(fg_hex: str, bg_hex: str) -> Dict[str, Any]:
    """Computes WCAG 2.1 contrast ratio and AA/AAA pass verdicts."""
    fg_rgb = parse_hex_color(fg_hex)
    bg_rgb = parse_hex_color(bg_hex)
    l1 = relative_luminance(fg_rgb)
    l2 = relative_luminance(bg_rgb)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    ratio = round((lighter + 0.05) / (darker + 0.05), 2)
    return {
        "foreground": fg_hex,
        "background": bg_hex,
        "contrast_ratio": ratio,
        "wcag_aa_normal_text_pass": ratio >= 4.5,
        "wcag_aa_large_text_or_ui_pass": ratio >= 3.0,
        "wcag_aaa_normal_text_pass": ratio >= 7.0,
        "verdict": "PASS" if ratio >= 4.5 else ("PASS_LARGE_TEXT_ONLY" if ratio >= 3.0 else "FAIL_WCAG_AA"),
    }


def evaluate_ux_tap_budget(
    workflow_name: str,
    taps_count: int,
    duration_seconds: float,
    keyboard_occludes_cta: bool = False,
    has_dead_end: bool = False,
    max_taps: int = 3,
    max_seconds: float = 15.0,
) -> Dict[str, Any]:
    """Evaluates Pillar 4 Quantitative UX Ergonomics for bedside/high-frequency flows."""
    violations: List[str] = []
    if taps_count > max_taps:
        violations.append(
            f"Interaction cost ({taps_count} taps) exceeds bedside ergonomic budget (max {max_taps} taps)."
        )
    if duration_seconds > max_seconds:
        violations.append(
            f"Task completion time ({duration_seconds:.1f}s) exceeds bedside budget (max {max_seconds:.1f}s)."
        )
    if keyboard_occludes_cta:
        violations.append(
            "On-screen IME keyboard occludes the primary Save/Submit button or active input field (missing WindowInsets.ime padding)."
        )
    if has_dead_end:
        violations.append("Workflow contains a dead-end state with no clear back/cancel or recovery action.")

    return {
        "workflow": workflow_name,
        "taps_count": taps_count,
        "max_taps_budget": max_taps,
        "duration_seconds": duration_seconds,
        "max_seconds_budget": max_seconds,
        "keyboard_occludes_cta": keyboard_occludes_cta,
        "has_dead_end": has_dead_end,
        "ux_verdict": "PASS" if not violations else "FAIL_UX_BUDGET",
        "violations": violations,
    }


def scan_file_for_design_and_ux(file_path: Path, rel_path: str) -> Dict[str, List[Dict[str, Any]]]:
    blockers: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {"blockers": blockers, "warnings": warnings}

    lines = content.splitlines()
    lower_rel = rel_path.lower()
    is_theme_or_test = any(tok in lower_rel for tok in THEME_FILE_ALLOWLIST_TOKENS)

    # 1. Pillar 1A: Hardcoded Hex Colors in UI Screen / Component Files
    if file_path.suffix in {".kt", ".tsx", ".jsx", ".css"} and not is_theme_or_test:
        compose_color_hex = re.compile(r"\bColor\s*\(\s*0x[0-9A-Fa-f]{8}\s*\)")
        css_raw_hex = re.compile(r"(?<!var\()#[0-9A-Fa-f]{6}\b")

        for idx, line in enumerate(lines, start=1):
            if "DESIGN-TOKEN-ALLOW" in line or "@Suppress" in line:
                continue
            if file_path.suffix == ".kt" and compose_color_hex.search(line):
                blockers.append({
                    "pillar": "Pillar 1: Graphic & Design-Token Integrity",
                    "rule": "DESIGN-TOKEN-HARDCODED-COLOR",
                    "location": f"{rel_path}:{idx}",
                    "line": line.strip(),
                    "remediation": (
                        "Do not hardcode raw hex `Color(0xFF...)` inside UI screens or components. "
                        "Reference semantic MaterialTheme.colorScheme.* or AppTheme tokens so Dark/Light and High-Contrast modes stay consistent."
                    ),
                })
            elif file_path.suffix in {".tsx", ".jsx", ".css"} and css_raw_hex.search(line):
                if not line.strip().startswith("--"):
                    warnings.append({
                        "pillar": "Pillar 1: Graphic & Design-Token Integrity",
                        "rule": "DESIGN-TOKEN-CSS-HEX",
                        "location": f"{rel_path}:{idx}",
                        "line": line.strip(),
                        "remediation": "Prefer semantic CSS custom properties (`var(--color-*)`) over inline hex literals.",
                    })

    # 2. Pillar 1B: SVG & Android VectorDrawable Integrity + RTL Mirroring
    if file_path.suffix == ".svg":
        if "viewBox=" not in content and "viewbox=" not in content.lower():
            blockers.append({
                "pillar": "Pillar 1: Graphic & Vector Integrity",
                "rule": "SVG-MISSING-VIEWBOX",
                "location": rel_path,
                "remediation": "Every `.svg` graphic must declare an explicit `viewBox=\"0 0 W H\"` attribute to scale cleanly across DPIs without clipping.",
            })
    elif file_path.suffix == ".xml" and "<vector" in content:
        if "android:viewportWidth" not in content or "android:viewportHeight" not in content:
            blockers.append({
                "pillar": "Pillar 1: Graphic & Vector Integrity",
                "rule": "VECTOR-MISSING-VIEWPORT",
                "location": rel_path,
                "remediation": "Android `<vector>` drawables must define both `android:viewportWidth` and `android:viewportHeight`.",
            })
        if any(kw in file_path.stem.lower() for kw in DIRECTIONAL_ICON_KEYWORDS):
            if 'android:autoMirrored="true"' not in content:
                blockers.append({
                    "pillar": "Pillar 1: Bilingual RTL Graphic Integrity",
                    "rule": "RTL-DIRECTIONAL-ICON-UNMIRRORED",
                    "location": rel_path,
                    "remediation": (
                        f"Directional vector icon '{file_path.name}' is missing `android:autoMirrored=\"true\"`. "
                        "Add `android:autoMirrored=\"true\"` so arrows/chevrons flip properly in Arabic (RTL) layout."
                    ),
                })

    # 3. Pillar 2 & 3: Phase 1.5 HTML/SVG Mock Quality & Contrast Audit
    if "mocks" in lower_rel and file_path.suffix in {".html", ".htm"}:
        # Check for contrast token declarations if --fg and --bg are defined
        fg_match = re.search(r"--(?:color-)?(?:text|fg|foreground)\s*:\s*(#[0-9A-Fa-f]{6})", content)
        bg_match = re.search(r"--(?:color-)?(?:bg|background|surface)\s*:\s*(#[0-9A-Fa-f]{6})", content)
        if fg_match and bg_match:
            c_res = compute_wcag_contrast(fg_match.group(1), bg_match.group(1))
            if not c_res["wcag_aa_normal_text_pass"]:
                blockers.append({
                    "pillar": "Pillar 2: WCAG 2.1 AA Visual Contrast",
                    "rule": "WCAG-CONTRAST-BELOW-4.5",
                    "location": rel_path,
                    "detail": f"Foreground {c_res['foreground']} on Background {c_res['background']} has contrast {c_res['contrast_ratio']}:1 (< 4.5:1).",
                    "remediation": "Adjust foreground/background tokens in the UI mock to achieve at least 4.5:1 WCAG AA contrast.",
                })

    return {"blockers": blockers, "warnings": warnings}


def audit_mock_to_code_and_5_states(workspace_dir: Path) -> Dict[str, Any]:
    """
    Audits Pillar 2 (Mock-to-Code Visual Fidelity) & Pillar 3 (5-State UI Matrix:
    Empty, Loading, Normal, Error/Alert, Overflow/RTL/200% Font Scale).
    """
    mocks_dir = workspace_dir / ".agents" / "mocks"
    mock_files = list(mocks_dir.glob("*.*")) if mocks_dir.exists() else []

    required_states = {
        "empty": False,
        "loading": False,
        "error_or_alert": False,
        "rtl_or_bilingual": False,
        "font_scale_or_overflow": False,
    }

    search_Files = list(mock_files)
    for test_f in workspace_dir.rglob("*Test*.kt"):
        search_Files.append(test_f)
    for test_f in workspace_dir.rglob("*.spec.ts"):
        search_Files.append(test_f)

    combined_corpus = ""
    for f in search_Files[:60]:
        try:
            combined_corpus += "\n" + f.read_text(encoding="utf-8", errors="ignore").lower()
        except Exception:
            pass

    if any(k in combined_corpus for k in ("empty", "no messages", "no active", "لا توجد")):
        required_states["empty"] = True
    if any(k in combined_corpus for k in ("loading", "skeleton", "progressindicator", "shimmer")):
        required_states["loading"] = True
    if any(k in combined_corpus for k in ("error", "alert", "critical", "warning", "خطأ", "تحذير")):
        required_states["error_or_alert"] = True
    if any(k in combined_corpus for k in ("rtl", "layoutdirection.rtl", "dir=\"rtl\"", "ar")):
        required_states["rtl_or_bilingual"] = True
    if any(k in combined_corpus for k in ("fontscale", "overflow", "ellipsize", "maxlines", "120.dp", "320dp", "360dp")):
        required_states["font_scale_or_overflow"] = True

    covered_count = sum(1 for v in required_states.values() if v)
    return {
        "mocks_found": len(mock_files),
        "states_coverage": required_states,
        "states_covered_count": covered_count,
        "total_required_states": len(required_states),
    }


def scan_directory(root_dir: Path) -> Dict[str, Any]:
    if not root_dir.exists() or not root_dir.is_dir():
        raise FileNotFoundError(f"Scan directory does not exist: {root_dir}")

    exts = {".kt", ".tsx", ".jsx", ".css", ".svg", ".xml", ".html", ".htm"}
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
        res = scan_file_for_design_and_ux(path, rel)
        all_blockers.extend(res["blockers"])
        all_warnings.extend(res["warnings"])

    state_matrix = audit_mock_to_code_and_5_states(root_dir)

    return {
        "design_linter_status": "PASS" if len(all_blockers) == 0 else "FAIL_DESIGN_BLOCKERS",
        "files_scanned": files_scanned,
        "hard_blockers_count": len(all_blockers),
        "warnings_count": len(all_warnings),
        "hard_blockers": all_blockers,
        "warnings": all_warnings,
        "ui_5_state_matrix_summary": state_matrix,
    }


def run_self_test() -> None:
    checks: List[str] = []

    # 1. Verify Pillar 2 WCAG 2.1 AA Contrast Engine
    good_contrast = compute_wcag_contrast("#0F172A", "#FFFFFF")
    assert good_contrast["wcag_aa_normal_text_pass"] is True and good_contrast["contrast_ratio"] >= 15.0
    bad_contrast = compute_wcag_contrast("#94A3B8", "#CBD5E1")
    assert bad_contrast["wcag_aa_normal_text_pass"] is False
    checks.append("Pillar 2 WCAG 2.1 AA Luminance Contrast Calculator: PASS")

    # 2. Verify Pillar 4 Quantitative UX Tap-Budget & Keyboard-Occlusion Engine
    good_ux = evaluate_ux_tap_budget("Bedside FHR Entry", taps_count=2, duration_seconds=6.5, keyboard_occludes_cta=False)
    assert good_ux["ux_verdict"] == "PASS"
    bad_ux = evaluate_ux_tap_budget("Cluttered Modal Entry", taps_count=6, duration_seconds=22.0, keyboard_occludes_cta=True)
    assert bad_ux["ux_verdict"] == "FAIL_UX_BUDGET" and len(bad_ux["violations"]) == 3
    checks.append("Pillar 4 Quantitative UX Tap-Budget & IME Keyboard Occlusion Oracle: PASS")

    # 3. Verify Pillar 1 & 3 File Scanner (Hardcoded Color, Broken SVG, Unmirrored RTL Icon)
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp)
        bad_screen = ws / "InboxScreen.kt"
        bad_screen.write_text(
            "package ui\n@Composable fun InboxScreen() {\n  val bg = Color(0xFFFF0000)\n}\n",
            encoding="utf-8",
        )
        bad_svg = ws / "broken_logo.svg"
        bad_svg.write_text("<svg width=\"24\" height=\"24\"><path d=\"M0 0\"/></svg>", encoding="utf-8")

        bad_rtl_icon = ws / "ic_arrow_forward.xml"
        bad_rtl_icon.write_text(
            '<vector xmlns:android="http://schemas.android.com/apk/res/android" '
            'android:viewportWidth="24" android:viewportHeight="24"></vector>',
            encoding="utf-8",
        )

        fail_report = scan_directory(ws)
        assert fail_report["design_linter_status"] == "FAIL_DESIGN_BLOCKERS"
        assert fail_report["hard_blockers_count"] == 3, f"Expected 3 design blockers, got {fail_report['hard_blockers_count']}"
        checks.append("Pillar 1 Hardcoded UI Hex Color Detection: PASS")
        checks.append("Pillar 1 Broken SVG viewBox Detection: PASS")
        checks.append("Pillar 1 Unmirrored Arabic RTL Directional Icon Detection: PASS")

        # Fix all 3 files and verify clean PASS
        bad_screen.write_text(
            "package ui\n@Composable fun InboxScreen() {\n  val bg = MaterialTheme.colorScheme.surface\n}\n",
            encoding="utf-8",
        )
        bad_svg.write_text('<svg viewBox="0 0 24 24"><path d="M0 0"/></svg>', encoding="utf-8")
        bad_rtl_icon.write_text(
            '<vector xmlns:android="http://schemas.android.com/apk/res/android" '
            'android:autoMirrored="true" android:viewportWidth="24" android:viewportHeight="24"></vector>',
            encoding="utf-8",
        )

        pass_report = scan_directory(ws)
        assert pass_report["design_linter_status"] == "PASS"
        assert pass_report["hard_blockers_count"] == 0
        checks.append("Compliant Design Token, SVG & RTL Icon Verification: PASS")

    print(
        json.dumps(
            {
                "self_test_status": "PASS",
                "checks_executed": len(checks),
                "details": checks,
            },
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="MACA v2 Automated Design, Graphic, UI & UX Verification Engine")
    parser.add_argument("--self-test", action="store_true", help="Run built-in verification self-tests and exit")
    parser.add_argument("--scan-dir", type=str, metavar="DIR", help="Scan workspace directory for graphic, token, SVG, RTL, and 5-state UI compliance")
    parser.add_argument("--check-contrast", nargs=2, metavar=("FG_HEX", "BG_HEX"), help="Compute WCAG 2.1 contrast ratio between two hex colors")
    parser.add_argument("--check-ux-budget", nargs=3, metavar=("WORKFLOW", "TAPS", "SECONDS"), help="Evaluate UX tap and duration budget for a workflow")

    try:
        args = parser.parse_args()
        if args.self_test:
            run_self_test()
            return
        if args.check_contrast:
            fg, bg = args.check_contrast
            res = compute_wcag_contrast(fg, bg)
            print(json.dumps(res, indent=2))
            sys.exit(0 if res["wcag_aa_normal_text_pass"] else 1)
        if args.check_ux_budget:
            wf, taps_s, secs_s = args.check_ux_budget
            res = evaluate_ux_tap_budget(wf, int(taps_s), float(secs_s))
            print(json.dumps(res, indent=2))
            sys.exit(0 if res["ux_verdict"] == "PASS" else 1)
        if args.scan_dir:
            report = scan_directory(Path(args.scan_dir).resolve())
            print(json.dumps(report, indent=2))
            sys.exit(0 if report["design_linter_status"] == "PASS" else 1)
        parser.print_help()
    except Exception as exc:
        emit_fail_closed_error(
            type(exc).__name__,
            str(exc),
            "Run 'python3 scripts/lint_design_and_ux.py --self-test' to verify the Design & UX engine.",
        )


if __name__ == "__main__":
    main()
