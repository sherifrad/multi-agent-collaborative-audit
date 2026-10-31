#!/usr/bin/env python3
"""MACA project map: how much each path matters, so the router can spend model strength where a mistake costs most.

Deterministic, stdlib only, no model call. Each tracked file gets an aspect and a criticality:
  0 ambient (docs, vendor, generated)    1 low (tests, CI, UI views, config, dependencies)
  2 medium (core logic, API, data access)  3 high (auth/security, money/billing, data schema/migrations)
Signals, strongest first: path and file name, then content patterns, then git history (fix-commit frequency only;
line churn misleads because of formatters and lockfiles). No git or a shallow clone only removes the git layer.
A path that is not in the map is treated as level 2, never lower, so a stale map cannot send risky work to a cheap tier.
The map is advice for the router; the diff can only raise it (see model_router.effective_criticality).

Usage
  project_map.py scan --cwd DIR [--write]    scan (incremental when .agents/PROJECT_MAP.json exists); --write saves it
  project_map.py lookup --cwd DIR PATH...    criticality of paths (unmapped = 2)
  project_map.py summary --cwd DIR           the <=15 line block to paste into AGENTS.md / SKILL.md
  project_map.py --self-test
"""
import argparse, fnmatch, json, os, re, subprocess, sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

RULES_VERSION = 1
UNMAPPED = 2
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".agents", ".idea", ".gradle", "Pods"}
CODE_EXT = {".py", ".js", ".ts", ".tsx", ".jsx", ".kt", ".java", ".go", ".rs", ".swift", ".rb", ".php", ".c", ".cc", ".cpp", ".cs", ".sql", ".sh"}
DOC_EXT = {".md", ".rst", ".txt", ".adoc"}
ASSET_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2", ".ttf", ".css", ".scss", ".html", ".vue", ".svelte"}
CONFIG_EXT = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env"}
MAX_FILES = 20000
MAX_READ = 16384

# (aspect, criticality, directory or file-name words). Matched against path segments / the file stem.
SEGMENT_RULES = [
    ("data_schema", 3, {"migrations", "migration", "migrate", "alembic", "schema", "schemas"}),
    ("auth_security", 3, {"auth", "authentication", "authorization", "oauth", "security", "crypto", "secrets", "permissions", "rbac", "acl", "iam", "sso", "keystore", "keystores", "vault", "biometric", "credentials", "credential", "signing"}),
    ("clinical_safety", 3, {"patient", "patients", "clinical", "dosage", "dose", "medication", "diagnosis", "gestational", "gestation", "obstetric", "pregnancy", "triage", "redating", "dating", "vitals", "emr", "ehr", "phi", "hipaa"}),
    ("money_billing", 3, {"billing", "payments", "payment", "checkout", "invoice", "invoices", "ledger", "stripe", "wallet"}),
    ("api_integration", 2, {"api", "routes", "controllers", "handlers", "endpoints", "clients", "integrations", "webhooks", "rpc"}),
    ("data_access", 2, {"db", "database", "models", "repositories", "repository", "dao", "queries"}),
    ("ci_infra", 1, {".github", ".gitlab", "ci", "deploy", "infra", "terraform", "k8s", "helm"}),
    ("tests", 1, {"tests", "test", "spec", "specs", "__tests__", "e2e", "fixtures"}),
    ("ui_view", 1, {"ui", "views", "templates", "components", "static", "assets", "styles", "public"}),
    ("docs", 0, {"docs", "doc", "documentation", "examples"}),
    ("vendor", 0, {"vendor", "third_party", "thirdparty", "generated", "gen"}),
]
CONTENT_RULES = [
    ("data_schema", 1, re.compile(r"\b(alter\s+table|create\s+table|drop\s+table|create\s+index|add\s+column)\b", re.I)),
    ("auth_security", 2, re.compile(r"\b(jwt|bcrypt|argon2|oauth\w*|passlib|pbkdf2|hmac|encrypt\w*|decrypt\w*|private_key|csrf|api[_ ]?key|client_secret)\b", re.I)),
    ("clinical_safety", 2, re.compile(r"\b(gestational\w*|dosage|medication|trimester|diagnos\w+|obstetric\w*|patient_?id)\b", re.I)),
    ("money_billing", 2, re.compile(r"\b(stripe|paypal|braintree|payment_intent|refund\w*|invoice\w*|billing)\b", re.I)),
]


def stem_last_is_test(spaced: str) -> bool:
    stem = spaced.rsplit("/", 1)[-1].rsplit(".", 1)[0].split()
    return bool(stem) and stem[-1] in ("test", "tests", "spec", "fake", "mock") and len(stem) > 1


def classify_path(rel: str) -> Dict[str, Any]:
    p = rel.replace("\\", "/")
    low = p.lower()
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", p).lower()   # GestationalAgeEngine -> gestational age engine
    name = low.rsplit("/", 1)[-1]
    stem, ext = os.path.splitext(name)
    segs = set(low.split("/")[:-1])
    tokens = set(re.split(r"[/._\- ]", spaced.rsplit(".", 1)[0] if "." in name else spaced))   # auth-service/ and billing_service/ count as auth and billing
    sensitive_words = set().union(*[w for _, c, w in SEGMENT_RULES if c == 3])
    if name.startswith(".env") or ext in (".pem", ".key", ".p12", ".jks", ".keystore") or name in ("id_rsa", "local.properties", "keystore.properties", "google-services.json") or "password" in name:
        return {"aspect": "auth_security", "crit": 3}
    if name.endswith((".lock", ".min.js", ".min.css")) or name in ("package-lock.json", "yarn.lock", "poetry.lock", "go.sum", "cargo.lock", "pnpm-lock.yaml"):
        return {"aspect": "dependencies", "crit": 1}
    if ext in (".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp"):
        return {"aspect": "ui_view", "crit": 1}
    if ext in (".apk", ".aab", ".log", ".zip", ".jar"):
        return {"aspect": "artifact", "crit": 0}
    if name == "androidmanifest.xml":
        return {"aspect": "manifest_permissions", "crit": 2}
    if re.search(r"(^|/)(test_[^/]*|[^/]*_test\.[^/]*|[^/]*\.(test|spec)\.[^/]*)$", low) or stem_last_is_test(spaced):
        return {"aspect": "tests", "crit": 1}
    if name in ("license", "licence", "changelog") or ext in DOC_EXT and not (tokens & sensitive_words):
        return {"aspect": "docs", "crit": 0}
    for aspect, crit, words in SEGMENT_RULES:
        if tokens & words:
            return {"aspect": aspect, "crit": crit}
    if ext in ASSET_EXT:
        return {"aspect": "ui_view", "crit": 1}
    if ext in CONFIG_EXT or name in ("dockerfile", "makefile"):
        return {"aspect": "config", "crit": 1}
    if ext in CODE_EXT:
        return {"aspect": "core_logic", "crit": 2}
    return {"aspect": "other", "crit": 1}


def content_boost(entry: Dict[str, Any], text: str) -> Dict[str, Any]:
    """Raise a code file to level 3 when its content is about schema, auth or money. Never lowers."""
    if entry["crit"] < 2 or entry["crit"] >= 3:
        return entry
    for aspect, need, rx in CONTENT_RULES:
        if len(rx.findall(text)) >= need:
            return {"aspect": aspect, "crit": 3, "by": "content"}
    return entry


def git_out(cwd: Path, *args: str) -> str:
    try:
        return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, timeout=60).stdout
    except Exception:
        return ""


def fix_counts(cwd: Path) -> Optional[Dict[str, int]]:
    """Files touched by fix commits in the last 180 days. None when git history is missing or too shallow to say."""
    if not git_out(cwd, "rev-parse", "--verify", "HEAD").strip():
        return None
    if git_out(cwd, "rev-parse", "--is-shallow-repository").strip() == "true":
        return None
    log = git_out(cwd, "log", "--since=180.days", "--no-merges", "--relative", "--pretty=format:@@%s", "--name-only")
    counts: Counter = Counter()
    fix = False
    for line in log.splitlines():
        if line.startswith("@@"):
            fix = bool(re.match(r"(fix|bugfix|hotfix)\b|fix(es|ed)?[:(]", line[2:].strip(), re.I))
        elif line.strip() and fix:
            counts[line.strip()] += 1
    return dict(counts)


def scan(cwd: Path, previous: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    cached = (previous or {}).get("entries", {}) if (previous or {}).get("rules_version") == RULES_VERSION else {}
    entries: Dict[str, Any] = {}
    n = 0
    for root, dirs, files in os.walk(cwd):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for f in sorted(files):
            if n >= MAX_FILES:
                dirs.clear()
                break
            full = Path(root) / f
            rel = full.relative_to(cwd).as_posix()
            try:
                st = full.stat()
            except OSError:
                continue
            n += 1
            old = cached.get(rel)
            if old and "git" in old:   # a git boost is recomputed each scan, never carried over
                old = {k: v for k, v in old.items() if k != "git"}
                old["crit"] -= 1
            if old and old.get("mtime") == int(st.st_mtime) and old.get("size") == st.st_size:
                entries[rel] = old
                continue
            e = classify_path(rel)
            if Path(f).suffix.lower() in CODE_EXT and st.st_size < 1_000_000:
                try:
                    e = content_boost(e, full.read_text(errors="ignore")[:MAX_READ])
                except OSError:
                    pass
            e.update(mtime=int(st.st_mtime), size=st.st_size)
            entries[rel] = e
    fixes = fix_counts(cwd)
    if fixes is not None:
        for rel, c in fixes.items():
            e = entries.get(rel)
            if e and e["crit"] >= 1 and c >= 3 and e["crit"] < 3 and not e.get("git"):
                e["crit"] += 1; e["git"] = f"{c} fix commits in 180 days"
    crit3 = [p for p, e in entries.items() if e["crit"] == 3]
    return {"version": 1, "rules_version": RULES_VERSION, "unmapped_default": UNMAPPED,
            "git": "ok" if fixes is not None else "unavailable (no history or shallow clone): path and content signals only",
            "summary": {"total_files": len(entries), "level_3_files": len(crit3), "by_level": dict(Counter(e["crit"] for e in entries.values()))},
            "entries": entries}


def load_map(cwd: Path) -> Optional[Dict[str, Any]]:
    p = cwd / ".agents" / "PROJECT_MAP.json"
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return None


def lookup(pmap: Optional[Dict[str, Any]], paths: List[str], risk_paths: Optional[List[str]] = None) -> Dict[str, int]:
    """Criticality per path. Unmapped = 2. A human `Risk paths` glob only ever raises a path to 3."""
    entries = (pmap or {}).get("entries", {})
    out = {}
    for p in paths:
        c = entries[p]["crit"] if p in entries else UNMAPPED
        if any(fnmatch.fnmatch(p, g) for g in (risk_paths or [])):
            c = 3
        out[p] = c
    return out


def summary(pmap: Dict[str, Any]) -> str:
    entries = pmap["entries"]
    dirs: Counter = Counter()
    aspects: Dict[str, set] = {}
    for p, e in entries.items():
        if e["crit"] == 3:
            d = "/".join(p.split("/")[:2]) if p.count("/") >= 2 else (p.rsplit("/", 1)[0] + "/" if "/" in p else p)
            dirs[d] += 1
            aspects.setdefault(d, set()).add(e["aspect"])
    lines = ["## Project risk map (generated by scripts/project_map.py; do not edit by hand)",
             f"- {pmap['summary']['level_3_files']} of {pmap['summary']['total_files']} files are level 3 (auth/security, money/billing, data schema). Full map: .agents/PROJECT_MAP.json (tools only; do not load it).",
             "- Highest-risk areas:"]
    for d, c in dirs.most_common(5):
        lines.append(f"  - `{d}` ({', '.join(sorted(aspects[d]))}, {c} files)")
    if not dirs:
        lines.append("  - none found")
    lines += ["- Rule: an edit to a level-3 path needs a frontier-tier review and an independent test review.",
              "- A path missing from the map counts as level 2. Add `Risk paths` to the profile to raise more paths."]
    return "\n".join(lines)


def self_test() -> None:
    import tempfile
    checks = []
    c = lambda p: classify_path(p)["crit"]
    assert c("src/billing/invoice.py") == 3 and c("db/migrations/001_add.sql") == 3 and c("src/auth/session.py") == 3
    assert c("README.md") == 0 and c("docs/guide.txt") == 0 and c("vendor/x/lib.js") == 0
    assert c("tests/test_a.py") == 1 and c("package-lock.json") == 1 and c("src/ui/button.tsx") == 1 and c("src/core/engine.py") == 2
    checks.append("path rules put schema, auth and billing at 3; docs/vendor at 0; tests/UI/lockfiles at 1; plain code at 2")
    assert c(".env.production") == 3 and c("certs/server.pem") == 3
    checks.append("secret-bearing files are level 3")
    assert c("migrations/README.md") == 3 or classify_path("migrations/README.md")["aspect"] != "docs"
    checks.append("a doc inside migrations/ or auth/ is not demoted to ambient")
    e = content_boost({"aspect": "core_logic", "crit": 2}, "def run(sql):\n  sql('ALTER TABLE users ADD COLUMN x int')")
    assert e["crit"] == 3 and e["aspect"] == "data_schema"
    assert content_boost({"aspect": "core_logic", "crit": 2}, "x = 1")["crit"] == 2
    assert content_boost({"aspect": "docs", "crit": 0}, "ALTER TABLE a")["crit"] == 0
    checks.append("content patterns raise code to 3, never lower, and do not touch docs")
    with tempfile.TemporaryDirectory() as t:
        root = Path(t)
        (root / "src" / "billing").mkdir(parents=True); (root / "docs").mkdir(); (root / "src" / "core").mkdir()
        (root / "src" / "billing" / "charge.py").write_text("x=1")
        (root / "docs" / "a.md").write_text("hi")
        (root / "src" / "core" / "util.py").write_text("import stripe\nrefund(1)\n")
        m = scan(root)
        assert m["entries"]["src/billing/charge.py"]["crit"] == 3 and m["entries"]["docs/a.md"]["crit"] == 0
        assert m["entries"]["src/core/util.py"]["crit"] == 3 and m["entries"]["src/core/util.py"]["by"] == "content"
        assert "unavailable" in m["git"]
        m2 = scan(root, m)
        assert m2["entries"] == m["entries"]
        assert lookup(m, ["src/billing/charge.py", "new/unseen.py"]) == {"src/billing/charge.py": 3, "new/unseen.py": 2}
        assert lookup(m, ["docs/a.md"], ["docs/*"]) == {"docs/a.md": 3}
        assert len(summary(m).splitlines()) <= 15
    checks.append("scan works without git, is incremental, treats unmapped paths as 2, lets Risk paths raise only, and the summary fits 15 lines")
    assert c("services/auth-service/login.py") == 3 and c("src/billing_service/worker.py") == 3
    assert c("docs/security.md") == 3 and c("SECURITY.md") != 0 and c("payments/setup.md") == 3 and c("docs/guide.md") == 0
    assert c("app/src/main/model/GestationalAgeEngine.kt") == 3 and c("storage/PatientAttachmentVault.kt") == 3 and c("keystore/anc.jks") == 3 and c("local.properties") == 3
    assert c("security/AppLockPolicyTest.kt") == 1 and c("evidence/12_security_settings.png") == 1 and c("app/src/main/AndroidManifest.xml") == 2 and c("build/app.apk") == 0
    checks.append("CamelCase names are split; clinical, vault and keystore paths are level 3; Kotlin tests, images and APKs are not inflated; the manifest is level 2")
    checks.append("hyphen/underscore directory names and sensitive docs (security.md, payments/) are not demoted")
    print(json.dumps({"self_test_status": "PASS", "checks_executed": len(checks), "details": checks}, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description="MACA project map")
    ap.add_argument("command", nargs="?", choices=["scan", "lookup", "summary"])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--cwd", default=".")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    cwd = Path(a.cwd).resolve()
    if a.command == "scan":
        m = scan(cwd, load_map(cwd))
        if a.write:
            (cwd / ".agents").mkdir(exist_ok=True)
            (cwd / ".agents" / "PROJECT_MAP.json").write_text(json.dumps(m, indent=1))
        print(json.dumps({k: m[k] for k in ("git", "summary")}, indent=2))
    elif a.command == "lookup":
        print(json.dumps(lookup(load_map(cwd), a.paths), indent=2))
    elif a.command == "summary":
        m = load_map(cwd) or sys.exit("no .agents/PROJECT_MAP.json; run `scan --write` first")
        print(summary(m))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
