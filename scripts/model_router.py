#!/usr/bin/env python3
"""MACA model router: which model tier and which reasoning effort each role gets, decided by rules, not by chance.

Decisions came from a three-adviser discussion (see references/model_routing.md). In short:
  * three tiers (light, standard, frontier); effort (low, medium, high) is a separate dial
  * judging roles (builder, test-designer, reviewer) never use a light model; light only does mechanical work
  * escalate effort first inside standard/frontier, then the tier; a light role escalates straight to standard
  * every routing signal is measured by the orchestrator (git diff, test exit codes), never reported by the routed agent
  * the human sets the call budget in the profile; at the ceiling the run stops, it never raises the ceiling
  * models marked `inferred` never act as the frontier reviewer; free models are preferred for light work

Usage
  model_router.py catalog --cwd DIR [--write]      seed/show the catalog (.agents/model_catalog.json) from discovery + name heuristics
  model_router.py route --role ROLE --cwd DIR [--failures N] [--blockers N] [--full-path] [--builder-family F] [--used-frontier N --used-standard N --rounds N]
  model_router.py risk --cwd DIR                  print the deterministic risk score
  model_router.py --self-test
Read-only except `catalog --write` and the decision log `.agents/ROUTING_LOG.jsonl`. Stdlib only, Python 3.9 compatible.
"""
import argparse, fnmatch, json, re, subprocess, sys, time
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from skill_ambassador_auditor import profile_field, read  # noqa: E402
import fleet_select  # noqa: E402

TIERS = ["light", "standard", "frontier"]
EFFORTS = ["low", "medium", "high"]
JUDGING = {"builder", "test-designer", "reviewer", "second-reviewer"}
SENSITIVE = re.compile(r"\b(auth\w*|token|secret|password|passwd|crypto\w*|payment|charge|refund|balance|invoice|migrat\w+|drop\s+table|permission\w*|session|jwt|exec|eval)\b", re.I)
RISKY_FILES = ("migrations/", "migration", "schema", ".github/workflows/", "package-lock.json", "yarn.lock", "poetry.lock", "Cargo.lock", "go.sum", "Dockerfile", "permissions", "rbac")
CODE_EXT = (".py", ".js", ".ts", ".tsx", ".jsx", ".kt", ".java", ".go", ".rs", ".swift", ".rb", ".php", ".c", ".cc", ".cpp", ".cs", ".sql")


# ------------------------------------------------------------------ catalog
def guess_tier(model_id: str) -> str:
    m = model_id.lower()
    sep = r"(?:^|[-/._])"
    end = r"(?:$|[-/._])"
    if re.search(sep + r"(?:flash|haiku|lite|mini|nano|small|tiny|spark|free)" + end, m):
        return "light"
    if re.search(sep + r"(?:opus|fable|pro|max|ultra|astra|sol|o3)" + end + "|argon-high", m):
        return "frontier"
    return "standard"


def seed_entry(vendor: str, model_id: str) -> Dict[str, Any]:
    fam = fleet_select.family_of(vendor, model_id)
    baked = re.search(r"-(low|medium|high)$", model_id)
    return {"id": model_id, "vendor": vendor, "family": fam, "tier": guess_tier(model_id),
            "efforts": [baked.group(1)] if baked else (["low", "medium", "high"] if vendor in ("claude", "codex", "agy") else []),
            "free": model_id.endswith("-free") or model_id.startswith("opencode/") and "free" in model_id,
            "source": "inferred"}


def seed_catalog(discover: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = [dict(seed_entry("claude", a), source="builtin") for a in ("haiku", "sonnet", "opus", "fable")]   # Claude Code aliases are documented, not guessed
    for d in (discover or {}).get("discovered", []):
        for v in ((d.get("models") or {}).get("values") or []):
            if d["key"] != "claude":
                out.append(seed_entry(d["key"], v))
    return out


def load_catalog(cwd: Path, discover: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    p = cwd / ".agents" / "model_catalog.json"
    if p.exists():
        try:
            return json.loads(p.read_text())["models"]
        except (ValueError, KeyError):
            pass
    return seed_catalog(discover)


# ------------------------------------------------------------------ risk (deterministic, no model call)
def git(cwd: Path, *args: str) -> str:
    try:
        return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, timeout=60).stdout
    except Exception:
        return ""


def risk_from_diff(diff: str, numstat: str, risk_paths: List[str]) -> Dict[str, Any]:
    files, added, removed_tests, added_tests = [], 0, 0, 0
    for line in numstat.splitlines():
        parts = line.split("\t")
        if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
            files.append(parts[2]); added += int(parts[0])
            if re.search(r"(^|/)(tests?|spec|__tests__)/|test_|_test\.|\.test\.|\.spec\.", parts[2]):
                added_tests += int(parts[0]); removed_tests += int(parts[1])
    hits = sorted({m.group(1).lower() for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++") for m in [SENSITIVE.search(l)] if m})
    risky = [f for f in files if any(r.lower() in f.lower() for r in RISKY_FILES) or any(fnmatch.fnmatch(f, g) for g in risk_paths)]
    reasons = []
    if hits: reasons.append(f"sensitive words added: {', '.join(hits[:5])}")
    if risky: reasons.append(f"risky files changed: {', '.join(risky[:3])}")
    if removed_tests > added_tests: reasons.append("tests were removed or weakened")
    cls = "high" if reasons else "medium" if len(files) >= 4 or added >= 150 else "low"
    if cls == "medium": reasons.append(f"{len(files)} files, {added} lines added")
    return {"class": cls, "files": len(files), "lines_added": added, "reasons": reasons}


def measure_risk(cwd: Path, risk_paths: List[str]) -> Dict[str, Any]:
    base = "HEAD" if git(cwd, "rev-parse", "--verify", "HEAD").strip() else ""
    args = ["diff", base] if base else ["diff"]
    r = risk_from_diff(git(cwd, *args, "-U0"), git(cwd, *args, "--numstat"), risk_paths)
    r["source"] = "git diff (measured by the orchestrator)"
    return r


# ------------------------------------------------------------------ routing
def wanted(role: str, risk: str, failures: int, blockers: int, full_path: bool) -> Dict[str, str]:
    """Return {tier, effort, why} using only measured inputs."""
    if role in ("helper", "runner"):
        return {"tier": "light", "effort": "low", "why": "mechanical work stays light"}
    base = {"builder": ("standard", "medium"), "test-designer": ("standard", "medium"),
            "reviewer": ("standard", "medium"), "second-reviewer": ("standard", "high")}[role]
    tier, effort, why = base[0], base[1], [f"{role} baseline"]
    if risk == "medium":
        effort = "high" if role in ("reviewer", "second-reviewer", "test-designer") else effort; why.append("medium risk")
    if risk == "high" or (full_path and role in ("reviewer", "second-reviewer")):
        tier, effort = ("frontier", "high") if role != "builder" else ("standard", "high"); why.append("high risk or Full-path review")
    if failures >= 2 and role == "builder":
        effort = "high"; why.append(f"{failures} failures: effort first")
    if failures >= 3 and role == "builder":
        tier = "frontier"; why.append("still failing: tier")
    if blockers > 0 and role in ("builder", "reviewer", "second-reviewer"):
        tier, effort = "frontier", "high"; why.append("Hard Blocker found in an earlier round")
    return {"tier": tier, "effort": effort, "why": "; ".join(why)}


def eligible(entry: Dict[str, Any], role: str, tier: str, available: Dict[str, str]) -> bool:
    if entry["vendor"] != "claude" and entry["vendor"] not in available:
        return False
    if entry["tier"] != tier:
        return False
    if tier == "frontier" and role in ("reviewer", "second-reviewer") and entry.get("source") == "inferred":
        return False   # an unconfirmed model never acts as the frontier reviewer
    if entry["family"] == "unknown" and role in ("reviewer", "second-reviewer"):
        return False
    return True


def pick(catalog: List[Dict[str, Any]], role: str, want: Dict[str, str], available: Dict[str, str], builder_family: str = "") -> List[Dict[str, Any]]:
    """Ordered candidates: preferred first. Reviewers prefer another family; light work prefers free models."""
    cands = [e for e in catalog if eligible(e, role, want["tier"], available)]
    if role in ("reviewer", "second-reviewer") and builder_family:
        cands.sort(key=lambda e: e["family"] == builder_family)
    elif want["tier"] == "light":
        cands.sort(key=lambda e: not e.get("free"))
    out = []
    for e in cands:
        eff = want["effort"] if (not e["efforts"] or want["effort"] in e["efforts"]) else e["efforts"][0]
        out.append({"vendor": e["vendor"], "model": e["id"], "family": e["family"], "tier": e["tier"], "effort": eff,
                    "source": e.get("source", "confirmed")})
    return out


def fallback_policy(role: str, risk: str, full_path: bool) -> str:
    if role in ("helper", "runner"):
        return "any model may substitute"
    if role in ("reviewer", "second-reviewer") and (risk == "high" or full_path):
        return "same tier, a family other than the builder's; otherwise stop with QUOTA_EXHAUSTED (never a weaker reviewer)"
    if role in ("reviewer", "second-reviewer"):
        return "same tier only; otherwise stop with QUOTA_EXHAUSTED"
    return "same tier on another vendor; one tier down only if a frontier review follows"


def budget_state(profile: str, used: Dict[str, int]) -> Dict[str, Any]:
    def num(name):
        m = re.search(r"\d+", profile_field(profile, name) or "")
        return int(m.group()) if m else None
    lim = {"frontier": num("Max frontier calls"), "standard": num("Max standard calls"), "rounds": num("Max rounds")}
    over = [k for k, v in lim.items() if v is not None and used.get(k, 0) >= v]
    return {"limits": lim, "used": used, "exhausted": over}


def route(role: str, cwd: Path, signals: Dict[str, Any], discover: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    profile = read(cwd / ".agents" / "PROJECT_PROFILE.md")
    risk_paths = [p.strip() for p in re.split(r"[,;]", profile_field(profile, "Risk paths") or "") if p.strip() and "inferred" not in p.lower()]
    risk = signals.get("risk") or measure_risk(cwd, risk_paths)
    want = wanted(role, risk["class"], signals.get("failures", 0), signals.get("blockers", 0), signals.get("full_path", False))
    plan = fleet_select.build_plan(discover, {}, profile)
    available = {k: v["family"] for k, v in plan["usable_external"].items()}
    catalog = load_catalog(cwd, discover)
    bstate = budget_state(profile, signals.get("used", {}))
    stop = None
    if want["tier"] == "frontier" and "frontier" in bstate["exhausted"]:
        stop = "BUDGET_EXHAUSTED: frontier call limit reached; ask the human, report what stays unreviewed"
    if "standard" in bstate["exhausted"] and want["tier"] == "standard":
        stop = "BUDGET_EXHAUSTED: standard call limit reached"
    if "rounds" in bstate["exhausted"]:
        stop = "BUDGET_EXHAUSTED: round limit reached"
    cands = pick(catalog, role, want, available, signals.get("builder_family", ""))
    if role in ("builder", "test-designer") or not cands:
        local = [e for e in pick(catalog, role, want, {}, signals.get("builder_family", "")) if e["vendor"] == "claude"]
        cands = (local + [c for c in cands if c not in local]) if role in ("builder", "test-designer") else (cands or local)
    if not cands and not stop:
        stop = f"NO_ELIGIBLE_MODEL for {role} at tier {want['tier']}: confirm a model in .agents/model_catalog.json or approve a vendor"
    decision = {"role": role, "risk": risk, "want": want, "stop": stop, "choice": cands[0] if cands else None,
                "chain": cands[1:4], "fallback_policy": fallback_policy(role, risk["class"], signals.get("full_path", False)),
                "budget": bstate, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    return decision


def log_decision(cwd: Path, d: Dict[str, Any]) -> None:
    (cwd / ".agents").mkdir(exist_ok=True)
    with open(cwd / ".agents" / "ROUTING_LOG.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({k: d[k] for k in ("ts", "role", "want", "stop")} | {"risk": d["risk"]["class"], "choice": (d["choice"] or {}).get("model")}) + "\n")


# ------------------------------------------------------------------ self test
def self_test() -> None:
    checks = []
    low = risk_from_diff("+x = 1\n", "3\t0\tsrc/a.py\n", [])
    assert low["class"] == "low"
    hi = risk_from_diff("+if token == secret:\n", "3\t0\tsrc/auth.py\n", [])
    assert hi["class"] == "high" and any("sensitive" in r for r in hi["reasons"])
    assert risk_from_diff("", "0\t40\ttests/test_a.py\n", [])["class"] == "high"
    assert risk_from_diff("", "1\t0\tdb/migrations/001.sql\n", [])["class"] == "high"
    assert risk_from_diff("", "1\t0\tweb/x.py\n", ["web/*"])["class"] == "high"
    assert risk_from_diff("", "".join(f"10\t0\tsrc/f{i}.py\n" for i in range(5)), [])["class"] == "medium"
    checks.append("risk is computed from the diff: sensitive words, risky files, weakened tests, profile risk_paths, size")
    assert wanted("helper", "high", 0, 0, True)["tier"] == "light"
    for role in ("builder", "test-designer", "reviewer"):
        assert wanted(role, "low", 0, 0, False)["tier"] != "light", role
    checks.append("judging roles are never light; helpers always are")
    order = lambda w: (TIERS.index(w["tier"]), EFFORTS.index(w["effort"]))
    for role in ("builder", "test-designer", "reviewer"):
        seq = [order(wanted(role, r, 0, 0, False)) for r in ("low", "medium", "high")]
        assert seq == sorted(seq), (role, seq)
    checks.append("cost never goes down as risk goes up")
    assert wanted("builder", "low", 2, 0, False) == {"tier": "standard", "effort": "high", "why": wanted("builder", "low", 2, 0, False)["why"]}
    assert wanted("builder", "low", 3, 0, False)["tier"] == "frontier" and wanted("reviewer", "low", 0, 1, False)["tier"] == "frontier"
    checks.append("escalation: effort first, then tier; a Hard Blocker sends builder and reviewer to frontier")
    cat = [seed_entry("claude", a) for a in ("haiku", "sonnet", "opus")] + [seed_entry("agy", "gemini-3.8-flash-high"), seed_entry("agy", "gemini-4-argon-high")]
    cat[2]["source"] = "confirmed"
    avail = {"agy": "google"}
    rev = pick(cat, "reviewer", {"tier": "frontier", "effort": "high"}, avail, "anthropic")
    assert [c["model"] for c in rev] == ["opus"] or all(c["source"] != "inferred" for c in rev), rev
    assert all(c["source"] == "confirmed" for c in rev)
    checks.append("an inferred model never acts as the frontier reviewer")
    cat.append(seed_entry("agy", "gemini-4-argon-medium"))
    std = pick(cat, "reviewer", {"tier": "standard", "effort": "medium"}, {"agy": "google"}, "anthropic")
    assert std and std[0]["family"] != "anthropic", std
    checks.append("reviewers prefer a family other than the builder's")
    free = pick([seed_entry("opencode", "opencode/beam-free"), seed_entry("claude", "haiku")], "helper", {"tier": "light", "effort": "low"}, {"opencode": "unknown"})
    assert free[0]["model"] == "opencode/beam-free"
    checks.append("free models are preferred for light work")
    b = budget_state("- **Max frontier calls** (x): 2\n", {"frontier": 2})
    assert b["exhausted"] == ["frontier"]
    assert budget_state("", {"frontier": 99})["exhausted"] == []
    checks.append("a human-set call limit stops the run; no limit means no stop")
    assert "never a weaker reviewer" in fallback_policy("reviewer", "high", False) and fallback_policy("helper", "low", False).startswith("any")
    checks.append("fallback policy: no weaker reviewer on risky work, anything for helpers")
    print(json.dumps({"self_test_status": "PASS", "checks_executed": len(checks), "details": checks}, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description="MACA model router")
    ap.add_argument("command", nargs="?", choices=["catalog", "route", "risk"])
    ap.add_argument("--cwd", default=".")
    ap.add_argument("--role")
    ap.add_argument("--failures", type=int, default=0)
    ap.add_argument("--blockers", type=int, default=0)
    ap.add_argument("--full-path", action="store_true")
    ap.add_argument("--builder-family", default="")
    ap.add_argument("--used-frontier", type=int, default=0)
    ap.add_argument("--used-standard", type=int, default=0)
    ap.add_argument("--rounds", type=int, default=0)
    ap.add_argument("--discover-json")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    cwd = Path(a.cwd).resolve()
    discover = json.loads(Path(a.discover_json).read_text()) if a.discover_json else fleet_select.run_node("discover.mjs")
    if a.command == "catalog":
        cat = load_catalog(cwd, discover)
        doc = {"note": "Edit tier/family/efforts, then set source to 'confirmed'. Inferred models never act as the frontier reviewer.", "models": cat}
        if a.write:
            (cwd / ".agents").mkdir(exist_ok=True)
            (cwd / ".agents" / "model_catalog.json").write_text(json.dumps(doc, indent=2))
        print(json.dumps(doc, indent=2))
    elif a.command == "risk":
        profile = read(cwd / ".agents" / "PROJECT_PROFILE.md")
        print(json.dumps(measure_risk(cwd, [p.strip() for p in re.split(r"[,;]", profile_field(profile, "Risk paths") or "") if p.strip()]), indent=2))
    elif a.command == "route":
        if a.role not in ("helper", "runner", "builder", "test-designer", "reviewer", "second-reviewer"):
            sys.exit("--role must be helper|runner|builder|test-designer|reviewer|second-reviewer")
        d = route(a.role, cwd, {"failures": a.failures, "blockers": a.blockers, "full_path": a.full_path, "builder_family": a.builder_family,
                                "used": {"frontier": a.used_frontier, "standard": a.used_standard, "rounds": a.rounds}}, discover)
        log_decision(cwd, d)
        print(json.dumps(d, indent=2))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
