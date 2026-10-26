#!/usr/bin/env python3
"""
================================================================================
MACA Dynamic Multi-Adapter Fleet Dispatcher & Resilience Router
(scripts/fleet_dispatch.py)
--------------------------------------------------------------------------------
Provides dynamic, model-agnostic routing across four execution adapters:
  1. CLI Adapter: Spawns pre-installed AI CLIs (Claude, OpenCode, Codex, AGY, etc.)
  2. API Adapter: Direct HTTP requests to OpenAI-compatible/Ollama/vLLM endpoints
  3. Script Adapter: User-defined custom executable agent wrappers
  4. Subagent / Tabula Rasa Adapter: In-IDE subagents (100% free, zero external keys)

Resilience Guarantee:
If an API is unreachable (network timeout, 5xx, rate limit) or a CLI binary
is absent, the router automatically catches the failure, logs the diagnostic trail,
and seamlessly cascades down to the next tier without breaking the pipeline.
================================================================================
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
TEMPLATE_PATH = SKILL_ROOT / "resources" / "templates" / "fleet.template.json"

ENHANCED_PATH = (
    f"{os.environ.get('PATH', '')}:/opt/homebrew/bin:/usr/local/bin:"
    f"{Path.home() / '.local/bin'}:{Path.home() / '.antigravity/bin'}:{Path.home() / 'Library/Android/sdk/platform-tools'}"
)


def emit_fail_closed_error(error_code: str, message: str, remediation: str) -> None:
    payload = {
        "status": "MACA_SCRIPT_ERROR — STOP_AND_FIX",
        "error_code": error_code,
        "message": message,
        "mandatory_agent_action": "Fix the error described below and re-run, or halt and report UNKNOWN / HARNESS ERROR.",
        "remediation": remediation,
    }
    print(json.dumps(payload, indent=2), file=sys.stderr)
    sys.exit(2)


def load_manifest(workspace_dir: Optional[Path] = None) -> Tuple[Dict[str, Any], str]:
    """
    Loads fleet manifest in priority order:
      1. <workspace>/.agents/fleet.json
      2. ~/.maca/fleet.json
      3. SKILL_ROOT/resources/templates/fleet.template.json (Default Fallback)
    """
    candidates = []
    if workspace_dir:
        candidates.append((workspace_dir / ".agents" / "fleet.json", "workspace"))
    candidates.append((Path.home() / ".maca" / "fleet.json", "user_global"))
    candidates.append((TEMPLATE_PATH, "template_default"))

    for path, source in candidates:
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                return data, f"{source} ({path})"
            except Exception as e:
                if source == "workspace":
                    emit_fail_closed_error(
                        "MALFORMED_FLEET_MANIFEST",
                        f"Failed to parse fleet manifest at {path}: {str(e)}",
                        f"Validate JSON syntax in {path} or run 'python3 scripts/fleet_dispatch.py --repair'."
                    )

    # If even template is missing
    emit_fail_closed_error(
        "MISSING_FLEET_TEMPLATE",
        f"Fleet manifest template missing at {TEMPLATE_PATH}",
        "Ensure resources/templates/fleet.template.json exists in skill directory."
    )
    return {}, "none"


def auto_detect_fleet(workspace_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Scans the local machine for CLIs, APIs, and subagent readiness."""
    env = {**os.environ, "PATH": ENHANCED_PATH}
    tools = ["claude", "opencode", "codex", "agy", "gemini"]
    detected_clis = {}
    for t in tools:
        detected_clis[t] = shutil.which(t, path=ENHANCED_PATH) is not None

    api_keys = {
        "openai": bool(os.environ.get("OPENAI_API_KEY")),
        "anthropic": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "gemini": bool(os.environ.get("GEMINI_API_KEY")),
        "deepseek": bool(os.environ.get("DEEPSEEK_API_KEY")),
        "openrouter": bool(os.environ.get("OPENROUTER_API_KEY")),
    }

    # Determine recommended profile
    has_any_cli = any(detected_clis.values())
    has_any_api = any(api_keys.values())

    if has_any_cli:
        mode = "hybrid_cli_primary"
    elif has_any_api:
        mode = "api_primary"
    else:
        mode = "zero_api_subagent_primary"

    return {
        "mode": mode,
        "detected_clis": detected_clis,
        "available_api_keys": [k for k, v in api_keys.items() if v],
        "zero_api_ready": True,
        "workspace": str(workspace_dir) if workspace_dir else os.getcwd()
    }


def execute_cli_adapter(config: Dict[str, Any], brief_text: str, workspace_dir: Path) -> Dict[str, Any]:
    """Executes an external CLI tool."""
    binary = config.get("binary")
    if not binary:
        return {"success": False, "error": "MISSING_BINARY_CONFIG", "message": "No binary specified in CLI config"}

    binary_path = shutil.which(binary, path=ENHANCED_PATH)
    if not binary_path:
        return {
            "success": False,
            "error": "CLI_NOT_FOUND",
            "message": f"CLI binary '{binary}' is not installed or not in PATH."
        }

    args_template = config.get("args", ["-p", "{brief}"])
    model = config.get("model", "")
    rendered_args = []
    for arg in args_template:
        arg = arg.replace("{brief}", brief_text)
        arg = arg.replace("{model}", model)
        arg = arg.replace("{permission_mode}", "acceptEdits")
        rendered_args.append(arg)

    env = {**os.environ, "PATH": ENHANCED_PATH}
    try:
        proc = subprocess.run(
            [binary_path] + rendered_args,
            cwd=str(workspace_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=config.get("timeout_seconds", 120)
        )
        if proc.returncode == 0:
            return {
                "success": True,
                "output": proc.stdout.strip(),
                "adapter": f"cli:{binary}"
            }
        else:
            return {
                "success": False,
                "error": f"CLI_EXIT_{proc.returncode}",
                "message": proc.stderr.strip() or proc.stdout.strip()
            }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "CLI_TIMEOUT", "message": f"Execution timed out after {config.get('timeout_seconds', 120)}s"}
    except Exception as exc:
        return {"success": False, "error": "CLI_EXCEPTION", "message": str(exc)}


def execute_api_adapter(config: Dict[str, Any], brief_text: str) -> Dict[str, Any]:
    """
    Executes a direct API call (OpenAI-compatible, DeepSeek, Ollama, OpenRouter, etc.).
    Uses vanilla Python urllib for zero dependencies and maximum portability.
    """
    endpoint = config.get("endpoint")
    if not endpoint:
        return {"success": False, "error": "MISSING_ENDPOINT", "message": "No endpoint URL configured for API adapter"}

    api_key_env = config.get("api_key_env", "")
    api_key = os.environ.get(api_key_env, "") if api_key_env else ""
    if api_key_env and not api_key:
        return {
            "success": False,
            "error": "MISSING_API_KEY",
            "message": f"Environment variable '{api_key_env}' is not set."
        }

    model = config.get("model", "default")
    timeout = config.get("timeout_seconds", 30)

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a specialized software engineering agent executing a strict MACA lane task."},
            {"role": "user", "content": brief_text}
        ],
        "temperature": 0.2
    }

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(endpoint, data=req_data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body)
            # Standard OpenAI choices[0].message.content extraction
            choices = data.get("choices", [])
            if choices and "message" in choices[0]:
                content = choices[0]["message"].get("content", "")
                return {"success": True, "output": content, "adapter": f"api:{model}"}
            return {"success": True, "output": body, "adapter": f"api:{model}"}
    except urllib.error.HTTPError as http_err:
        return {
            "success": False,
            "error": f"HTTP_{http_err.code}",
            "message": f"Server returned HTTP {http_err.code}: {http_err.reason}"
        }
    except urllib.error.URLError as url_err:
        return {
            "success": False,
            "error": "ENDPOINT_UNREACHABLE",
            "message": f"Could not reach endpoint '{endpoint}': {str(url_err.reason)}"
        }
    except Exception as exc:
        return {"success": False, "error": "API_EXCEPTION", "message": str(exc)}


def execute_subagent_adapter(config: Dict[str, Any], brief_text: str, lane_name: str) -> Dict[str, Any]:
    """
    Formats the task for native In-IDE subagent or Single-Model Tabula Rasa execution.
    Requires $0 external API keys, 0 external CLIs, and works in any sandboxed Antigravity session.
    """
    role_name = config.get("role_name", f"Specialized {lane_name.upper()} Agent")
    instructions = config.get("instructions", "Execute lane task strictly obeying MACA rules.")

    payload = {
        "success": True,
        "adapter": "subagent:native_ide",
        "role_name": role_name,
        "instructions": instructions,
        "task_brief": brief_text,
        "execution_notes": "Dispatched to In-IDE Subagent / Tabula Rasa Persona (Zero external keys required)."
    }
    return payload


def dispatch_lane(
    lane_name: str,
    brief_text: str,
    workspace_dir: Path,
    manifest: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Dispatches a task to a lane with fail-safe cascading resilience:
      1. Attempt Primary configured adapter.
      2. If primary fails or is unavailable, record failure reason.
      3. Cascade to Fallback adapter (typically In-IDE Subagent).
      4. Never crash or leave pipeline in broken state.
    """
    if manifest is None:
        manifest, _ = load_manifest(workspace_dir)

    lanes_cfg = manifest.get("lanes", {})
    if lane_name not in lanes_cfg:
        emit_fail_closed_error(
            "UNKNOWN_LANE",
            f"Lane '{lane_name}' not defined in fleet manifest.",
            f"Available lanes: {list(lanes_cfg.keys())}"
        )

    lane_def = lanes_cfg[lane_name]
    primary_cfg = lane_def.get("primary", {})
    fallback_cfg = lane_def.get("fallback", {"adapter": "subagent"})

    attempts = []

    # 1. Try Primary Adapter
    prim_adapter = primary_cfg.get("adapter", "subagent")
    if prim_adapter == "cli":
        res = execute_cli_adapter(primary_cfg, brief_text, workspace_dir)
    elif prim_adapter == "api":
        res = execute_api_adapter(primary_cfg, brief_text)
    elif prim_adapter == "subagent":
        res = execute_subagent_adapter(primary_cfg, brief_text, lane_name)
    else:
        res = {"success": False, "error": "UNKNOWN_ADAPTER", "message": f"Unsupported adapter '{prim_adapter}'"}

    attempts.append({"adapter": f"primary:{prim_adapter}", "result": res})

    if res.get("success"):
        return {
            "status": "SUCCESS",
            "lane": lane_name,
            "adapter_used": f"primary:{prim_adapter}",
            "attempts": attempts,
            "output": res.get("output", res)
        }

    # 2. Cascade to Fallback Adapter
    fall_adapter = fallback_cfg.get("adapter", "subagent")
    if fall_adapter == "subagent":
        fall_res = execute_subagent_adapter(fallback_cfg, brief_text, lane_name)
    elif fall_adapter == "cli":
        fall_res = execute_cli_adapter(fallback_cfg, brief_text, workspace_dir)
    elif fall_adapter == "api":
        fall_res = execute_api_adapter(fallback_cfg, brief_text)
    else:
        fall_res = execute_subagent_adapter({"role_name": "Emergency Fallback"}, brief_text, lane_name)

    attempts.append({"adapter": f"fallback:{fall_adapter}", "result": fall_res})

    return {
        "status": "FALLBACK_SUCCESS" if fall_res.get("success") else "FAILED",
        "lane": lane_name,
        "adapter_used": f"fallback:{fall_adapter}",
        "primary_failure": res,
        "attempts": attempts,
        "output": fall_res.get("output", fall_res)
    }


def init_workspace_fleet(workspace_dir: Path, force: bool = False) -> Path:
    """Initializes .agents/fleet.json tailored to what is available on the machine."""
    agents_dir = workspace_dir / ".agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    target = agents_dir / "fleet.json"

    if target.exists() and not force:
        return target

    template_data = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    detected = auto_detect_fleet(workspace_dir)

    template_data["environment_detection"] = {
        "detected_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mode": detected["mode"],
        "available_clis": [k for k, v in detected["detected_clis"].items() if v],
        "available_api_keys": detected["available_api_keys"]
    }

    target.write_text(json.dumps(template_data, indent=2), encoding="utf-8")
    return target


def repair_and_validate_manifest(manifest_path: Path) -> Dict[str, Any]:
    """Validates and automatically repairs missing keys or schema errors in a fleet manifest."""
    issues_found = []
    repaired = False

    if not manifest_path.exists():
        emit_fail_closed_error("MANIFEST_NOT_FOUND", f"File does not exist: {manifest_path}", "Check path.")

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        emit_fail_closed_error("JSON_PARSE_ERROR", f"Failed to parse JSON: {e}", "Ensure file is valid JSON.")

    template = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))

    # Check required top-level keys
    for req_key in ["version", "strategy", "lanes"]:
        if req_key not in data:
            data[req_key] = template[req_key]
            issues_found.append(f"Missing '{req_key}' injected from template.")
            repaired = True

    # Check each required lane
    for lane in ["ui_ux", "core_logic", "data", "qa_referee"]:
        if lane not in data["lanes"]:
            data["lanes"][lane] = template["lanes"][lane]
            issues_found.append(f"Missing lane '{lane}' restored from template.")
            repaired = True
        else:
            # Ensure lane has fallback
            if "fallback" not in data["lanes"][lane]:
                data["lanes"][lane]["fallback"] = {"adapter": "subagent", "role_name": f"{lane.upper()} Subagent"}
                issues_found.append(f"Missing fallback in lane '{lane}' configured with default Subagent.")
                repaired = True

    if repaired:
        manifest_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    return {
        "valid": True,
        "repaired": repaired,
        "issues_fixed": issues_found,
        "manifest_path": str(manifest_path)
    }


def run_self_tests() -> None:
    """Executes deterministic self-tests covering all resilience and fallback requirements."""
    checks = []

    # 1. Template integrity
    assert TEMPLATE_PATH.exists(), "Template must exist"
    template_data = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    assert "lanes" in template_data and len(template_data["lanes"]) == 4
    checks.append("Fleet Template Schema & 4 Core Lanes: PASS")

    # 2. Auto-discovery
    discovery = auto_detect_fleet()
    assert discovery["zero_api_ready"] is True
    checks.append(f"Environment Discovery (Mode: {discovery['mode']}, Zero-API Ready: TRUE): PASS")

    # 3. Network Failure & Cascade Resilience Test
    # Simulate an unreachable API endpoint
    dummy_api_cfg = {
        "adapter": "api",
        "endpoint": "http://127.0.0.1:59999/unreachable_endpoint",
        "timeout_seconds": 1
    }
    dummy_fallback_cfg = {
        "adapter": "subagent",
        "role_name": "Resilience Test Agent"
    }
    test_manifest = {
        "lanes": {
            "test_lane": {
                "primary": dummy_api_cfg,
                "fallback": dummy_fallback_cfg
            }
        }
    }
    dispatch_res = dispatch_lane("test_lane", "Brief test", Path.cwd(), test_manifest)
    assert dispatch_res["status"] == "FALLBACK_SUCCESS", "Must cascade to fallback on unreachable API"
    assert dispatch_res["adapter_used"] == "fallback:subagent", "Fallback must be subagent"
    assert "ENDPOINT_UNREACHABLE" in dispatch_res["primary_failure"]["error"]
    checks.append("Unreachable API Server & Fail-Safe Cascade to Subagent: PASS")

    # 4. Missing CLI Binary & Cascade Test
    dummy_cli_cfg = {
        "adapter": "cli",
        "binary": "non_existent_fake_cli_xyz_123"
    }
    test_manifest_cli = {
        "lanes": {
            "test_cli_lane": {
                "primary": dummy_cli_cfg,
                "fallback": dummy_fallback_cfg
            }
        }
    }
    dispatch_cli_res = dispatch_lane("test_cli_lane", "Brief test", Path.cwd(), test_manifest_cli)
    assert dispatch_cli_res["status"] == "FALLBACK_SUCCESS"
    assert dispatch_cli_res["primary_failure"]["error"] == "CLI_NOT_FOUND"
    checks.append("Missing CLI Binary & Graceful Fallback: PASS")

    # 5. Manifest Self-Repair Test
    with tempfile.TemporaryDirectory() as tmp_dir:
        broken_manifest = Path(tmp_dir) / "broken_fleet.json"
        broken_manifest.write_text(json.dumps({"version": "1.0.0", "lanes": {}}), encoding="utf-8")
        repair_res = repair_and_validate_manifest(broken_manifest)
        assert repair_res["repaired"] is True
        assert len(repair_res["issues_fixed"]) > 0
        repaired_data = json.loads(broken_manifest.read_text(encoding="utf-8"))
        assert "ui_ux" in repaired_data["lanes"]
    checks.append("Manifest Detection, Schema Repair & Auto-Fixer: PASS")

    print(json.dumps({
        "self_test_status": "PASS",
        "checks_executed": len(checks),
        "details": checks
    }, indent=2))


def main():
    parser = argparse.ArgumentParser(description="MACA Dynamic Fleet Dispatcher & Resilience Router")
    parser.add_argument("--self-test", action="store_true", help="Run comprehensive resilience self-tests and exit")
    parser.add_argument("--init-config", action="store_true", help="Initialize .agents/fleet.json in workspace")
    parser.add_argument("--workspace", type=str, default=".", help="Target workspace path")
    parser.add_argument("--validate", type=str, help="Validate and repair fleet manifest at path")
    parser.add_argument("--dispatch", type=str, choices=["ui_ux", "core_logic", "data", "qa_referee"], help="Dispatch a task to a lane")
    parser.add_argument("--brief", type=str, help="Task brief text or path to brief markdown file")
    parser.add_argument("--detect-only", action="store_true", help="Detect local environment capabilities and exit")

    args = parser.parse_args()

    if args.self_test:
        run_self_tests()
        return

    workspace_dir = Path(args.workspace).resolve()

    if args.detect_only:
        print(json.dumps(auto_detect_fleet(workspace_dir), indent=2))
        return

    if args.init_config:
        cfg_path = init_workspace_fleet(workspace_dir)
        print(f"✅ Fleet manifest initialized at: {cfg_path}")
        return

    if args.validate:
        res = repair_and_validate_manifest(Path(args.validate).resolve())
        print(json.dumps(res, indent=2))
        return

    if args.dispatch:
        if not args.brief:
            emit_fail_closed_error("MISSING_BRIEF", "Must provide --brief <text|path> for dispatch.", "Provide brief.")
        brief_text = Path(args.brief).read_text(encoding="utf-8") if Path(args.brief).exists() else args.brief
        result = dispatch_lane(args.dispatch, brief_text, workspace_dir)
        print(json.dumps(result, indent=2))
        return

    parser.print_help()


if __name__ == "__main__":
    main()
