#!/usr/bin/env python3
"""
================================================================================
MACA One-Time First-Run Deep Diagnostic & Tooling Remediation Engine
(scripts/first_run_preflight.py)
--------------------------------------------------------------------------------
Executes a comprehensive one-time self-test and tool inventory audit the FIRST
time the skill is used (or whenever skill scripts change / --force is passed).
Unlike a silent fallback scan, if ANY internal file, script, relay, or external
CLI/E2E tool is missing or broken, it generates a mandatory User Alert Report
with exact step-by-step installation and remediation instructions.
================================================================================
"""

import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
STAMP_FILE = SKILL_ROOT / ".first_run_verified.json"

ENHANCED_PATH = (
    f"{os.environ.get('PATH', '')}:/opt/homebrew/bin:/usr/local/bin:"
    f"{Path.home() / '.local/bin'}:{Path.home() / '.antigravity/bin'}:{Path.home() / 'Library/Android/sdk/platform-tools'}"
)

REQUIRED_INTERNAL_FILES = [
    "SKILL.md",
    "README.md",
    "scripts/bootstrap.sh",
    "scripts/measure_metrics.py",
    "scripts/scenario_and_callchain_engine.py",
    "scripts/skill_ambassador_auditor.py",
    "scripts/lint_samd_invariants.py",
    "scripts/lint_design_and_ux.py",
    "scripts/fleet_dispatch.py",
    "references/e2e_and_call_chain_testing.md",
    "references/ponytail_ladder.md",
    "references/domain_packs.md",
    "references/roles_and_modes.md",
    "references/test_economy.md",
    "references/verification_principles.md",
    "references/intake.md",
    "references/token_economy.md",
    "packs/INDEX.md",
    "packs/core.md",
    "packs/fintech.md",
    "packs/systems.md",
    "packs/data-etl.md",
    "packs/clinical/PACK.md",
    "scripts/impact_and_cache.py",
    "scripts/harness.py",
    "resources/templates/PROJECT_PROFILE.template.md",
    "resources/templates/TEST_MANIFEST.template.json",
    "references/ui_ux_mocking.md",
    "references/coding_guidelines.md",
    "references/deep_diagnostics.md",
    "resources/dashboard/index.html",
    "resources/templates/AGENTS.template.md",
    "resources/templates/AI_HANDOFF_LEDGER.template.md",
    "resources/templates/SPEC_AND_AUDIT.template.md",
    "resources/templates/MACA_TOURNAMENT_LEADERBOARD.template.md",
    "resources/templates/SKILL_COMPLIANCE_LOG.template.md",
    "resources/templates/fleet.template.json",
    "vendor/delegate-skills/skills/shared_relay.mjs",
    "vendor/delegate-skills/skills/codex-delegate/SKILL.md",
    "vendor/delegate-skills/skills/codex-delegate/scripts/relay.mjs",
    "vendor/delegate-skills/skills/opencode-delegate/SKILL.md",
    "vendor/delegate-skills/skills/opencode-delegate/scripts/relay.mjs",
    "vendor/delegate-skills/skills/claude-delegate/SKILL.md",
    "vendor/delegate-skills/skills/claude-delegate/scripts/relay.mjs",
    "vendor/delegate-skills/skills/agy-delegate/SKILL.md",
    "vendor/delegate-skills/skills/agy-delegate/scripts/relay.mjs",
]

EXTERNAL_TOOLS_CATALOG = [
    {
        "binary": "node",
        "category": "Core Runtime",
        "role": "Executes vendored delegate-skills relays (relay.mjs) and E2E runners",
        "criticality": "REQUIRED",
        "remediation": "Install Node.js via Homebrew: `brew install node`"
    },
    {
        "binary": "python3",
        "category": "Core Runtime",
        "role": "Executes MACA Phase 4 Scenario Engine, Skill Ambassador Auditor, and Telemetry Cockpit",
        "criticality": "REQUIRED",
        "remediation": "Install Python 3 via Homebrew: `brew install python`"
    },
    {
        "binary": "opencode",
        "category": "AI Fleet CLI (Core Logic & Data Lanes)",
        "role": "Runs DeepSeek / GLM models via opencode-delegate",
        "criticality": "IMPORTANT",
        "remediation": "Install OpenCode CLI: `brew install opencode` or `npm i -g opencode-ai` and authenticate."
    },
    {
        "binary": "codex",
        "category": "AI Fleet CLI (Systems & Algorithmic Lane)",
        "role": "Runs OpenAI Codex via codex-delegate",
        "criticality": "IMPORTANT",
        "remediation": "Install Codex CLI: `npm install -g @openai/codex` and run `codex login`."
    },
    {
        "binary": "claude",
        "category": "AI Fleet CLI (UI/UX & Graphic Mocking Lane)",
        "role": "Runs Claude 3.5 Sonnet / Claude Code via claude-delegate",
        "criticality": "IMPORTANT",
        "remediation": "Install Claude Code CLI: `npm install -g @anthropic-ai/claude-code` and run `claude login`."
    },
    {
        "binary": "agy",
        "category": "AI Fleet CLI (QA, E2E & Skill Ambassador Lane)",
        "role": "Runs Google Antigravity headless CLI via agy-delegate",
        "criticality": "IMPORTANT",
        "remediation": "Open Antigravity IDE -> Command Palette (`Cmd+Shift+P`) -> 'Install agy command in PATH', or add `~/.antigravity/bin` to PATH."
    },
    {
        "binary": "gemini",
        "category": "AI Fleet CLI (QA & Audit Fallback Lane)",
        "role": "Runs Gemini CLI for full-repo audit and review",
        "criticality": "OPTIONAL_LANE",
        "remediation": "Install Gemini CLI: `npm install -g @google/gemini-cli` and authenticate."
    },
    {
        "binary": "playwright",
        "category": "E2E Verification Engine (Web/PWA)",
        "role": "Drives headless/headed browser for Phase 4 sequential E2E tests",
        "criticality": "IMPORTANT",
        "remediation": "Install Playwright: `npm install -g playwright && npx playwright install chromium`"
    },
    {
        "binary": "e2e",
        "category": "E2E Verification Engine (TesterArmy Hybrid AI+Deterministic)",
        "role": "Runs natural-language + deterministic locator E2E tests (`@e2e-dev/web` & `@e2e-dev/mobile`)",
        "criticality": "IMPORTANT",
        "remediation": "Initialize in project: `npx e2e@latest init` or install globally: `npm install -g e2e`"
    },
    {
        "binary": "adb",
        "category": "Mobile Device & Logcat Bridge (Android)",
        "role": "Connects to physical Android phone / emulator for E2E & Phase 4.5 Logcat diagnostics",
        "criticality": "IMPORTANT",
        "remediation": "Install Android Platform Tools: `brew install --cask android-platform-tools` and enable USB Debugging on phone."
    },
    {
        "binary": "maestro",
        "category": "Mobile UI E2E Runner (Android / iOS)",
        "role": "Executes declarative mobile UI flows on Android emulators and physical devices",
        "criticality": "OPTIONAL_E2E",
        "remediation": "Install Maestro CLI: `curl -Ls 'https://get.maestro.mobile.dev' | bash`"
    }
]


def compute_skill_fingerprint() -> str:
    """Computes a combined SHA-256 hash of SKILL.md and all executable scripts so edits re-trigger first-run verification."""
    hasher = hashlib.sha256()
    watched = [
        SKILL_ROOT / "SKILL.md",
        SCRIPT_DIR / "bootstrap.sh",
        SCRIPT_DIR / "measure_metrics.py",
        SCRIPT_DIR / "scenario_and_callchain_engine.py",
        SCRIPT_DIR / "skill_ambassador_auditor.py",
        SCRIPT_DIR / "lint_samd_invariants.py",
        SCRIPT_DIR / "lint_design_and_ux.py",
        SCRIPT_DIR / "fleet_dispatch.py",
        SKILL_ROOT / "resources/templates/fleet.template.json",
        SKILL_ROOT / "vendor/delegate-skills/skills/shared_relay.mjs"
    ]
    for p in watched:
        if p.exists():
            hasher.update(p.read_bytes())
    return hasher.hexdigest()


def verify_internal_files() -> List[Dict[str, str]]:
    missing = []
    for rel in REQUIRED_INTERNAL_FILES:
        target = SKILL_ROOT / rel
        if not target.exists():
            missing.append({
                "file": rel,
                "status": "MISSING",
                "remediation": f"Restore missing skill file '{rel}' from the multi-agent-collaborative-audit repository."
            })
    return missing


def run_internal_script_selftests() -> List[Dict[str, Any]]:
    env = {**os.environ, "PATH": ENHANCED_PATH}
    tasks = []

    py_scripts = [
        ("measure_metrics.py", [sys.executable, str(SCRIPT_DIR / "measure_metrics.py"), "--self-test"]),
        ("scenario_and_callchain_engine.py", [sys.executable, str(SCRIPT_DIR / "scenario_and_callchain_engine.py"), "--self-test"]),
        ("skill_ambassador_auditor.py", [sys.executable, str(SCRIPT_DIR / "skill_ambassador_auditor.py"), "--self-test"]),
        ("lint_samd_invariants.py", [sys.executable, str(SCRIPT_DIR / "lint_samd_invariants.py"), "--self-test"]),
        ("lint_design_and_ux.py", [sys.executable, str(SCRIPT_DIR / "lint_design_and_ux.py"), "--self-test"]),
        ("fleet_dispatch.py", [sys.executable, str(SCRIPT_DIR / "fleet_dispatch.py"), "--self-test"]),
        ("impact_and_cache.py", [sys.executable, str(SCRIPT_DIR / "impact_and_cache.py"), "--self-test"]),
        ("harness.py", [sys.executable, str(SCRIPT_DIR / "harness.py"), "--self-test"]),
    ]
    for name, cmd in py_scripts:
        tasks.append({
            "type": "python",
            "name": name,
            "cmd": cmd
        })

    node_bin = shutil.which("node", path=ENHANCED_PATH)
    for relay in ["codex-delegate", "opencode-delegate", "claude-delegate", "agy-delegate"]:
        relay_path = SKILL_ROOT / "vendor" / "delegate-skills" / "skills" / relay / "scripts" / "relay.mjs"
        tasks.append({
            "type": "node",
            "name": relay,
            "node_bin": node_bin,
            "relay_path": relay_path
        })

    def execute_test(task: Dict[str, Any]) -> Dict[str, Any]:
        if task["type"] == "python":
            name = task["name"]
            proc = subprocess.run(task["cmd"], env=env, capture_output=True, text=True)
            return {
                "component": f"Python Engine: {name}",
                "status": "WORKING" if proc.returncode == 0 else "BROKEN",
                "exit_code": proc.returncode,
                "remediation": None if proc.returncode == 0 else f"Run `python3 scripts/{name} --self-test` and fix syntax/runtime error: {proc.stderr.strip()}"
            }
        else:
            relay = task["name"]
            node_bin = task["node_bin"]
            relay_path = task["relay_path"]
            if not node_bin:
                return {
                    "component": f"Vendored Relay: {relay}",
                    "status": "BROKEN",
                    "exit_code": 127,
                    "remediation": "Install Node.js (`brew install node`) so vendored .mjs relays can execute."
                }
            proc = subprocess.run([node_bin, str(relay_path), "--self-test"], env=env, capture_output=True, text=True)
            return {
                "component": f"Vendored Relay: {relay}",
                "status": "WORKING" if proc.returncode == 0 else "BROKEN",
                "exit_code": proc.returncode,
                "remediation": None if proc.returncode == 0 else f"Fix module import or syntax in {relay_path}: {proc.stderr.strip()}"
            }

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(execute_test, tasks))

    return results


def audit_external_tools() -> List[Dict[str, Any]]:
    inventory = []
    for item in EXTERNAL_TOOLS_CATALOG:
        binary = item["binary"]
        found_path = shutil.which(binary, path=ENHANCED_PATH)
        inventory.append({
            "tool": binary,
            "category": item["category"],
            "role": item["role"],
            "criticality": item["criticality"],
            "status": "WORKING" if found_path else "MISSING",
            "path": found_path,
            "remediation": None if found_path else item["remediation"]
        })
    return inventory


def execute_first_run_diagnostic(force: bool = False) -> Dict[str, Any]:
    current_fp = compute_skill_fingerprint()

    if not force and STAMP_FILE.exists():
        try:
            saved = json.loads(STAMP_FILE.read_text(encoding="utf-8"))
            if saved.get("skill_fingerprint") == current_fp and saved.get("internal_health") == "PASS":
                return {
                    "first_run_executed": False,
                    "mode": "FAST_SUBSEQUENT_RUN (First-Run Already Verified)",
                    "verified_at": saved.get("verified_at"),
                    "internal_health": "PASS",
                    "missing_external_tools": saved.get("missing_external_tools", []),
                    "mandatory_agent_notice": (
                        "First-run verification already passed earlier. However, if any tool in "
                        "'missing_external_tools' is needed for this task, you MUST inform the user "
                        "and show its 'remediation' command rather than silently hiding its absence."
                    )
                }
        except Exception:
            pass

    missing_files = verify_internal_files()
    script_tests = run_internal_script_selftests()
    external_tools = audit_external_tools()

    broken_scripts = [s for s in script_tests if s["status"] != "WORKING"]
    missing_tools = [t for t in external_tools if t["status"] != "WORKING"]
    working_tools = [t for t in external_tools if t["status"] == "WORKING"]

    internal_ok = (len(missing_files) == 0) and (len(broken_scripts) == 0)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    report = {
        "first_run_executed": True,
        "mode": "FIRST_RUN_DEEP_DIAGNOSTIC",
        "verified_at": now_iso,
        "skill_fingerprint": current_fp,
        "internal_health": "PASS" if internal_ok else "FAIL_STOP_AND_FIX",
        "internal_files_checked": len(REQUIRED_INTERNAL_FILES),
        "missing_internal_files": missing_files,
        "internal_script_selftests": script_tests,
        "external_tools_summary": {
            "working_count": len(working_tools),
            "missing_count": len(missing_tools),
            "working_tools": [f"{t['tool']} ({t['path']})" for t in working_tools],
        },
        "missing_external_tools": missing_tools,
        "mandatory_agent_instruction": (
            "MANDATORY FIRST-RUN DISCLOSURE RULE: Do NOT silently ignore missing or broken tools! "
            "You MUST report the 'missing_external_tools' (and any 'broken_scripts') to the user "
            "along with their exact 'remediation' commands, and ask whether the user wants to "
            "install them now or proceed using the available working tools."
        )
    }

    if internal_ok:
        STAMP_FILE.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="MACA One-Time First-Run Diagnostic & Tooling Remediation Engine")
    parser.add_argument("--force", action="store_true", help="Force re-running the deep first-run diagnostic even if already stamped")
    parser.add_argument("--reset", action="store_true", help="Remove .first_run_verified.json stamp so the next run triggers a fresh first-run check")
    parser.add_argument("--self-test", action="store_true", help="Run self-test of the preflight engine")

    args = parser.parse_args()

    if args.reset:
        if STAMP_FILE.exists():
            STAMP_FILE.unlink()
        print(json.dumps({"status": "RESET_COMPLETE", "stamp_removed": str(STAMP_FILE)}, indent=2))
        return

    if args.self_test:
        report = execute_first_run_diagnostic(force=True)
        assert report["internal_health"] == "PASS", "Internal skill files and scripts must pass self-test"
        print(json.dumps({
            "self_test_status": "PASS",
            "internal_files_verified": report["internal_files_checked"],
            "scripts_verified": len(report["internal_script_selftests"]),
            "working_external_tools": report["external_tools_summary"]["working_count"],
            "missing_external_tools_with_remediation": report["external_tools_summary"]["missing_count"]
        }, indent=2))
        return

    report = execute_first_run_diagnostic(force=args.force)
    print(json.dumps(report, indent=2))
    if report["internal_health"] != "PASS":
        sys.exit(2)


if __name__ == "__main__":
    main()
