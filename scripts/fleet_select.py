#!/usr/bin/env python3
"""MACA fleet selection: turn "what is installed, configured and approved" into a role plan.

Inputs (all read-only, nothing is dispatched or written):
  * delegate-setup's discover.mjs      which implementer CLIs exist, authenticated or not, which models
  * delegate-setup's config.mjs load   the user's lanes (global + trusted project), schema delegate-fleet.v1
  * .agents/PROJECT_PROFILE.md         `Approved vendors` and `Write-lane permissions` (inferred values grant nothing)

Output: JSON with the user's archetype (solo | pair | fleet), the best independence level reachable, one
assignment per MACA role, what was withheld and why, and the exact next step for each withheld item.

Rules
  * The orchestrator's own family (claude) and fresh platform subagents need no vendor approval.
  * A vendor is usable only if installed, not known-unauthenticated, and named in `Approved vendors`.
  * Reviewers run read-only. A builder or test-designer may be external only if `Write-lane permissions` names it.
  * A reviewer from the builder's model family is not independent; independence is computed from families, not labels.

Usage: fleet_select.py [--cwd DIR] [--profile FILE] [--discover-json FILE] [--lanes-json FILE] [--self-test]
Stdlib only, Python 3.9 compatible.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from skill_ambassador_auditor import confirmed_names, profile_field, read  # noqa: E402

SETUP = SCRIPT_DIR.parent / "vendor" / "delegate-skills" / "skills" / "delegate-setup" / "scripts"
ORCH_FAMILY = "anthropic"          # the seat MACA is usually driven from; a fresh subagent shares it
LANE_HINTS = {"builder": ("feature", "build", "impl"), "test-designer": ("tests", "test"), "reviewer": ("review", "qa", "audit")}


def family_of(key: str, model: str = "") -> str:
    m = (model or "").lower()
    if key == "claude":
        return "anthropic"
    if key == "codex":
        return "openai"
    if key in ("agy", "opencode", "cline", "aider", "pi", "omp", "cursor", "copilot", "kimi"):
        for needle, fam in (("claude", "anthropic"), ("gemini", "google"), ("gpt-oss", "openai-oss"), ("gpt", "openai"),
                            ("grok", "xai"), ("kimi", "moonshot"), ("deepseek", "deepseek"), ("qwen", "alibaba")):
            if needle in m:
                return fam
        return "unknown"   # unknown never counts as independent
    return {"grok": "xai", "gemini": "google", "kimi": "moonshot"}.get(key, "unknown")


def run_node(script: str, *args: str) -> Optional[Dict[str, Any]]:
    try:
        r = subprocess.run(["node", str(SETUP / script), *args], capture_output=True, text=True, timeout=120)
        return json.loads(r.stdout)
    except Exception:
        return None


def pick_model(item: Dict[str, Any], want_family: Optional[str]) -> str:
    vals = (item.get("models") or {}).get("values") or []
    for v in vals:
        if want_family and family_of(item["key"], v) == want_family:
            return v
    return ""


def parse_write_permissions(raw_w: str) -> set:
    if not raw_w or "inferred" in raw_w.lower():
        return set()
    ok = set()
    for part in re.split(r"[,;/\n]+", raw_w.lower()):
        m = re.match(r"^\s*([a-z][\w.-]*)\s*:\s*(.+?)\s*$", part)
        if not m:
            continue
        name, perm = m.group(1), m.group(2)
        if re.search(r"\b(?:read-only|readonly|none|no)\b", perm):
            continue
        if re.search(r"\b(?:write|rw|read-write)\b|workspace-write", perm):
            ok.add(name)
    return ok


def build_plan(discover: Optional[Dict[str, Any]], lanes: Dict[str, Any], profile: str) -> Dict[str, Any]:
    approved = confirmed_names(profile, "Approved vendors")
    raw_w = profile_field(profile, "Write-lane permissions")
    write_ok = parse_write_permissions(raw_w)
    items = {d["key"]: d for d in (discover or {}).get("discovered", [])}
    withheld: List[Dict[str, str]] = []
    usable: Dict[str, Dict[str, Any]] = {}     # key -> {family, model, lane}

    for key, it in items.items():
        if key == "claude":
            continue   # the orchestrator family; handled as local subagents
        if it.get("authenticated") is False:
            withheld.append({"vendor": key, "why": "installed but not authenticated", "fix": f"sign in to `{it.get('binary', key)}` in your terminal"})
        elif key not in approved:
            withheld.append({"vendor": key, "why": "installed, but not in the profile's `Approved vendors`",
                             "fix": f"add `{key}` to `Approved vendors` in .agents/PROJECT_PROFILE.md (your decision: it receives code and specs)"})
        else:
            lane = next((n for n, l in lanes.items() if l.get("implementer") == key), "")
            model = (lanes.get(lane, {}) or {}).get("model", "") if lane else ""
            fam = family_of(key, model)
            if fam == "unknown" and key == "agy":
                for want in ("google", "openai", "anthropic"):
                    if want != ORCH_FAMILY and pick_model(it, want):
                        model, fam = pick_model(it, want), want
                        break
            usable[key] = {"family": fam, "model": model, "lane": lane, "auth": it.get("authenticated")}
    for name in sorted(approved - set(items) - {"claude"}):
        withheld.append({"vendor": name, "why": "approved in the profile but not installed", "fix": "install it or remove it from `Approved vendors`"})

    ext_families = sorted({u["family"] for u in usable.values() if u["family"] not in ("unknown", ORCH_FAMILY)})
    archetype = "fleet" if len(ext_families) >= 2 else "pair" if ext_families else "solo"

    def lane_for(role: str) -> str:
        return next((n for n in lanes if any(h in n.lower() for h in LANE_HINTS[role])), "")

    def external(role: str, need_other_than: str) -> Optional[Dict[str, Any]]:
        for key, u in sorted(usable.items(), key=lambda kv: kv[1]["family"] == need_other_than):
            if u["family"] not in ("unknown", need_other_than):
                return {"vendor": key, "family": u["family"], "model": u["model"], "lane": lane_for(role) or u["lane"], "mode": "read-only"}
        return None

    local = {"vendor": "claude-subagent", "family": ORCH_FAMILY, "model": "", "mode": "fresh-context"}
    writers = [k for k in usable if k in write_ok]
    builder = dict(local)
    if writers:
        k = writers[0]
        builder = {"vendor": k, "family": usable[k]["family"], "model": usable[k]["model"], "lane": lane_for("builder") or usable[k]["lane"], "mode": "write"}
    test_designer = dict(local)       # tests are written from the spec by a fresh context; external only with write permission
    reviewer = external("reviewer", builder["family"]) or dict(local, note="no approved vendor of another family: same-model review, say so in the report")
    second = None
    if reviewer["vendor"] != "claude-subagent":
        second = external("reviewer", reviewer["family"])
        if second and second["family"] == builder["family"]:
            second = None
    fams = {builder["family"], reviewer["family"]} | ({second["family"]} if second else set())
    independence = "multi-vendor" if len(fams) >= 2 else "same-model"
    if independence == "same-model" and reviewer["vendor"] != "claude-subagent":
        independence = "same-family"
    return {"archetype": archetype, "independence_reachable": independence,
            "roles": {"builder": builder, "test-designer": test_designer, "reviewer": reviewer, "second-reviewer": second},
            "usable_external": usable, "withheld": withheld,
            "lanes_configured": sorted(lanes),
            "notes": ["Reviewers run read-only through the delegate relays (--read-only).",
                      "No lanes configured: run the delegate-setup skill to create them (it writes only after you approve)." if not lanes else "Lane dials come from your delegate-setup config; explicit flags win."]}


def self_test() -> None:
    def d(*items):
        return {"discovered": [dict(key=k, binary=k, authenticated=a, models={"status": "reported", "values": m}) for k, a, m in items]}
    prof = lambda v, w="none": f"- **Approved vendors** (x): {v}\n- **Write-lane permissions** (x): {w}\n"
    checks = []
    solo = build_plan(d(("claude", True, []), ("codex", True, [])), {}, prof("none"))
    assert solo["archetype"] == "solo" and solo["independence_reachable"] == "same-model", solo
    assert any(w["vendor"] == "codex" and "Approved vendors" in w["why"] for w in solo["withheld"])
    checks.append("installed but unapproved vendor is withheld with the fix, archetype solo, same-model only")
    inf = build_plan(d(("claude", True, []), ("codex", True, [])), {}, prof("codex (inferred - confirm)"))
    assert inf["archetype"] == "solo", inf
    checks.append("an inferred approval grants nothing")
    pair = build_plan(d(("claude", True, []), ("codex", True, [])), {}, prof("codex"))
    assert pair["archetype"] == "pair" and pair["roles"]["reviewer"]["vendor"] == "codex" and pair["roles"]["reviewer"]["mode"] == "read-only"
    assert pair["independence_reachable"] == "multi-vendor" and pair["roles"]["builder"]["vendor"] == "claude-subagent"
    checks.append("one approved vendor of another family: pair, read-only reviewer, multi-vendor independence")
    fleet = build_plan(d(("claude", True, []), ("codex", True, []), ("agy", True, ["gemini-3.8-flash-high", "claude-sonnet-5-5-high"])), {}, prof("codex, agy"))
    assert fleet["archetype"] == "fleet" and fleet["roles"]["second-reviewer"] and fleet["roles"]["second-reviewer"]["family"] != fleet["roles"]["reviewer"]["family"], fleet
    checks.append("two external families: fleet with a second reviewer of a different family")
    noauth = build_plan(d(("claude", True, []), ("opencode", False, [])), {}, prof("opencode"))
    assert noauth["archetype"] == "solo" and noauth["withheld"][0]["why"].startswith("installed but not authenticated")
    checks.append("unauthenticated vendor is withheld even when approved")
    same = build_plan(d(("claude", True, []), ("agy", True, ["claude-sonnet-5-5-high"])), {"review": {"implementer": "agy", "model": "claude-sonnet-5-5-high"}}, prof("agy"))
    assert same["independence_reachable"] == "same-model" and same["archetype"] == "solo", same
    checks.append("a vendor serving the orchestrator's own model family is not independent")
    write = build_plan(d(("claude", True, []), ("codex", True, [])), {"feature": {"implementer": "codex"}}, prof("codex", "codex: workspace-write"))
    assert write["roles"]["builder"]["vendor"] == "codex" and write["roles"]["builder"]["mode"] == "write"
    write2 = build_plan(d(("claude", True, []), ("codex", True, [])), {"feature": {"implementer": "codex"}}, prof("codex", "codex: write"))
    assert write2["roles"]["builder"]["vendor"] == "codex" and write2["roles"]["builder"]["mode"] == "write"
    ro = build_plan(d(("claude", True, []), ("codex", True, [])), {"feature": {"implementer": "codex"}}, prof("codex", "codex: read-only"))
    assert ro["roles"]["builder"]["vendor"] == "claude-subagent", ro
    nowrite = build_plan(d(("claude", True, []), ("codex", True, [])), {}, prof("codex", "none"))
    assert nowrite["roles"]["builder"]["vendor"] == "claude-subagent"
    checks.append("an external builder needs a Write-lane permission naming it (codex: write -> write; codex: read-only -> no write)")
    ghost = build_plan(d(("claude", True, [])), {}, prof("gemini"))
    assert any(w["vendor"] == "gemini" and "not installed" in w["why"] for w in ghost["withheld"])
    checks.append("approved but missing vendor is reported")
    print(json.dumps({"self_test_status": "PASS", "checks_executed": len(checks), "details": checks}, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description="MACA fleet selection (read-only)")
    ap.add_argument("--cwd", default=".")
    ap.add_argument("--profile")
    ap.add_argument("--discover-json")
    ap.add_argument("--lanes-json")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    cwd = Path(a.cwd).resolve()
    profile = read(Path(a.profile) if a.profile else cwd / ".agents" / "PROJECT_PROFILE.md")
    discover = json.loads(Path(a.discover_json).read_text()) if a.discover_json else run_node("discover.mjs")
    lanes_doc = json.loads(Path(a.lanes_json).read_text()) if a.lanes_json else (run_node("config.mjs", "load", "--cwd", str(cwd)) or {})
    plan = build_plan(discover, lanes_doc.get("lanes", {}) or {}, profile)
    if discover is None:
        plan["notes"].append("discover.mjs could not run (is Node installed?): no external vendor is assumed.")
    print(json.dumps(plan, indent=2))


if __name__ == "__main__":
    main()
