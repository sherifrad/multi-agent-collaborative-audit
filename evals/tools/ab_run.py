#!/usr/bin/env python3
"""Before/after measurement: does the skill change what the model does, and at what cost?

Usage:
  ab_run.py run [--cases a,b] [--trials 3] [--model sonnet] [--judge-model sonnet]
                [--out DIR] [--budget-usd 2.0] [--timeout 900]
  ab_run.py report <out-dir>        re-render report.md from results.json
  ab_run.py --self-test

Two arms see the SAME prompt in a fresh copy of the same scaffold:
  with     the skill is installed (~/.claude/skills) and may be used
  without  all skills are disabled (--disable-slash-commands), the baseline
Every run is graded by the case's graders/*.md, using one judge that does not know the arm, and is given
the response, the workspace diff and the referee's deterministic facts (check_workspace.py). The report
shows pass rate, cost, turns and time per arm, the paired delta with a bootstrap 95% interval, and the
cases where the skill made things worse. Stdlib only, Python 3.9 compatible.
"""
import argparse, json, os, random, re, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(HERE, "..", ".."))
EVALS = os.path.join(SKILL, "evals")
ARMS = ("with", "without")
TOOLS = ["Read", "Glob", "Grep", "Skill", "Write", "Edit", "Bash"]


def split_front(text):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    return (m.group(1), m.group(2).strip()) if m else ("", text.strip())


def load_case(name):
    d = os.path.join(EVALS, name)
    meta, prompt = split_front(open(os.path.join(d, "prompt.md"), encoding="utf-8").read())
    graders = []
    gdir = os.path.join(d, "graders")
    for f in sorted(os.listdir(gdir)):
        if not f.endswith(".md"):
            continue
        gm, body = split_front(open(os.path.join(gdir, f), encoding="utf-8").read())
        w = re.search(r"^weight:\s*([\d.]+)", gm, re.M)
        graders.append({"id": f[:-3], "text": body, "weight": float(w.group(1)) if w else 1.0})
    return {"name": name, "dir": d, "prompt": prompt, "graders": graders}


def all_cases():
    return sorted(n for n in os.listdir(EVALS)
                  if os.path.isfile(os.path.join(EVALS, n, "prompt.md")) and os.path.isdir(os.path.join(EVALS, n, "graders")))


def claude(prompt, cwd, model, budget, timeout, skills_on, tools=None):
    """Run `claude -p` once; return (parsed json or {'error':..}, wall seconds)."""
    if os.environ.get("AB_STUB"):
        return {"result": os.environ["AB_STUB"], "total_cost_usd": 0.01, "num_turns": 2, "duration_ms": 1000,
                "usage": {"input_tokens": 10, "output_tokens": 5}}, 0.0
    cmd = ["claude", "-p", prompt, "--output-format", "json", "--model", model, "--no-session-persistence",
           "--permission-mode", "acceptEdits", "--max-budget-usd", str(budget)]
    if tools:
        cmd += ["--allowedTools"] + tools
    if not skills_on:
        cmd.append("--disable-slash-commands")
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        out = json.loads(p.stdout) if p.stdout.strip().startswith("{") else {"error": (p.stderr or p.stdout)[-400:]}
    except subprocess.TimeoutExpired:
        out = {"error": "timeout"}
    except (ValueError, OSError) as e:
        out = {"error": str(e)}
    return out, time.time() - t0


def sh(cmd, cwd, timeout=60):
    try:
        p = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        return (p.stdout + p.stderr).strip()
    except (subprocess.TimeoutExpired, OSError):
        return ""


def evidence(work, response):
    """What a grader may look at: the answer, the change, the artifacts, and the referee's facts."""
    status = sh("git status --short | head -40", work)
    diff = sh("git diff HEAD --stat | tail -15", work)
    agents = sh("find .agents tasks -type f 2>/dev/null | head -40", work)
    files = sh("for f in $(find . -type f -not -path './.git/*' -not -path './.agents/*' -size -3k | head -12); do echo \"--- $f\"; head -c 1500 $f; done", work)
    facts = sh("python3 %s %s" % (os.path.join(HERE, "check_workspace.py"), work), work, 120)
    return ("RESPONSE:\n%s\n\nGIT STATUS:\n%s\n\nDIFF STAT:\n%s\n\nFILES IN .agents/ AND tasks/:\n%s\n\nWORKING FILES:\n%s\n\nREFEREE FACTS (deterministic):\n%s"
            % (response[:6000], status, diff, agents, files[:4000], facts[:3000]))


JUDGE = ("You grade one assertion about an AI agent's work. Be strict: pass only if the evidence below shows it. "
         "Do not credit intentions or claims the evidence contradicts. The REFEREE FACTS were produced for you by an "
         "independent script after the run; the agent was not asked to run or cite them, so never penalise the agent for "
         "not citing them, and a missing .agents/ folder is only a failure when the assertion itself requires one.\n\nASSERTION:\n%s\n\n%s\n\n"
         'Reply with ONLY a JSON object: {"passed": true|false, "evidence": "<one sentence citing the evidence>"}')


def judge(assertion, ev, model, budget, timeout):
    out, _ = claude(JUDGE % (assertion, ev), tempfile.gettempdir(), model, budget, timeout, skills_on=False)
    txt = out.get("result", "") if isinstance(out, dict) else ""
    m = re.search(r"\{.*\}", txt, re.S)
    try:
        j = json.loads(m.group(0))
        return bool(j.get("passed")), str(j.get("evidence", ""))[:300], out.get("total_cost_usd", 0) or 0
    except (AttributeError, ValueError):
        return None, "judge returned no verdict: " + (out.get("error") or txt[:120]), out.get("total_cost_usd", 0) or 0


def run_one(case, arm, trial, a):
    base = os.path.join(a.out, case["name"], "%s-%d" % (arm, trial))
    shutil.rmtree(base, ignore_errors=True)
    work = os.path.join(base, "work")
    os.makedirs(work)
    sh("bash %s" % os.path.join(case["dir"], "place-files.sh"), work, 120)
    out, wall = claude(case["prompt"], work, a.model, a.budget_usd, a.timeout, skills_on=(arm == "with"), tools=TOOLS)
    response = out.get("result", "") if isinstance(out, dict) else ""
    ev = evidence(work, response)
    results, jcost, invalid = [], 0.0, bool(out.get("error")) if isinstance(out, dict) else True
    for g in case["graders"]:
        ok, why, c = judge(g["text"], ev, a.judge_model, 0.5, 300)
        jcost += c
        invalid = invalid or ok is None
        if ok is None and LIMIT_RE.search(why):
            raise SystemExit("account usage limit reached: %s\nResults so far are kept; resume after it resets." % why)
        results.append({"id": g["id"], "weight": g["weight"], "passed": bool(ok), "evidence": why})
    total = sum(r["weight"] for r in results) or 1.0
    score = sum(r["weight"] for r in results if r["passed"]) / total
    u = out.get("usage", {}) if isinstance(out, dict) else {}
    rec = {"case": case["name"], "arm": arm, "trial": trial, "score": score, "graders": results, "invalid": invalid,
           "error": out.get("error"), "cost_usd": out.get("total_cost_usd", 0) or 0, "judge_cost_usd": jcost,
           "turns": out.get("num_turns", 0), "wall_s": round(wall, 1),
           "tokens": (u.get("input_tokens", 0) + u.get("output_tokens", 0)
                      + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0))}
    with open(os.path.join(base, "record.json"), "w") as f:
        json.dump(rec, f, indent=1)
    return rec


LIMIT_RE = re.compile(r"hit your .*limit|rate.?limit|usage limit", re.I)


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def bootstrap_ci(diffs, n=4000, seed=7):
    """95% interval of the mean of paired differences."""
    if not diffs:
        return (0.0, 0.0)
    rnd = random.Random(seed)
    ms = sorted(mean([rnd.choice(diffs) for _ in diffs]) for _ in range(n))
    return (ms[int(0.025 * n)], ms[int(0.975 * n) - 1])


def summarize(recs):
    bad = lambda r: r.get("invalid") or any("judge returned no verdict" in g["evidence"] for g in r["graders"])
    skipped = sum(1 for r in recs if bad(r))
    recs = [r for r in recs if not bad(r)]  # a run whose model or judge failed is not a score of 0
    by = {}
    for r in recs:
        by.setdefault(r["case"], {a: {} for a in ARMS})[r["arm"]][r["trial"]] = r
    cases, diffs = [], []
    for name, arms in sorted(by.items()):
        w, wo = arms["with"], arms["without"]
        paired = sorted(set(w) & set(wo))
        d = [w[t]["score"] - wo[t]["score"] for t in paired]
        diffs += d
        cases.append({"case": name, "with": mean([r["score"] for r in w.values()]),
                      "without": mean([r["score"] for r in wo.values()]), "delta": mean(d), "n": len(paired)})
    arm = {}
    for a in ARMS:
        rs = [r for r in recs if r["arm"] == a]
        arm[a] = {"score": mean([r["score"] for r in rs]), "cost": mean([r["cost_usd"] for r in rs]),
                  "turns": mean([r["turns"] for r in rs]), "wall_s": mean([r["wall_s"] for r in rs]),
                  "tokens": mean([r["tokens"] for r in rs]), "errors": sum(1 for r in rs if r["error"]), "runs": len(rs)}
    lo, hi = bootstrap_ci(diffs)
    return {"invalid_runs_excluded": skipped, "cases": cases, "arms": arm, "delta": mean(diffs), "ci": [lo, hi], "pairs": len(diffs),
            "verdict": ("skill helps" if lo > 0 else "skill hurts" if hi < 0 else "no measurable difference")}


def render(s, recs):
    A, B = s["arms"]["with"], s["arms"]["without"]
    L = ["# Skill before/after report", "",
         "Verdict: **%s** (paired score delta %+.2f, 95%% CI [%+.2f, %+.2f], %d pairs)" % (s["verdict"], s["delta"], s["ci"][0], s["ci"][1], s["pairs"]),
         "Invalid runs excluded (model or judge failed): %d" % s.get("invalid_runs_excluded", 0),
         "", "| arm | pass score | cost/run | turns | wall s | tokens | errors | runs |", "|---|---|---|---|---|---|---|---|"]
    for n, x in (("with skill", A), ("without", B)):
        L.append("| %s | %.2f | $%.3f | %.1f | %.0f | %.0f | %d | %d |" % (n, x["score"], x["cost"], x["turns"], x["wall_s"], x["tokens"], x["errors"], x["runs"]))
    L += ["", "| case | with | without | delta | n |", "|---|---|---|---|---|"]
    for c in s["cases"]:
        flag = "  <- REGRESSION" if c["delta"] < 0 else ""
        L.append("| %s | %.2f | %.2f | %+.2f%s | %d |" % (c["case"], c["with"], c["without"], c["delta"], flag, c["n"]))
    fails = [r for r in recs if r["arm"] == "with" and r["score"] < 1 and not r.get("invalid")]
    if fails:
        L += ["", "## Failed assertions with the skill"]
        for r in fails:
            for g in r["graders"]:
                if not g["passed"]:
                    L.append("- %s (trial %d) %s: %s" % (r["case"], r["trial"], g["id"], g["evidence"]))
    L += ["", "Reading it: a delta is only trustworthy when its interval excludes 0. Raise --trials when it does not.",
          "Cost is the model run only; judge cost is in each record.json."]
    return "\n".join(L) + "\n"


def write_report(out):
    recs = [json.load(open(os.path.join(dp, "record.json"))) for dp, _, fs in os.walk(out) if "record.json" in fs]
    if not recs:
        sys.exit("no records in %s" % out)
    s = summarize(recs)
    json.dump({"summary": s, "records": recs}, open(os.path.join(out, "results.json"), "w"), indent=1)
    open(os.path.join(out, "report.md"), "w").write(render(s, recs))
    return s


def self_test():
    assert abs(mean([1, 2, 3]) - 2) < 1e-9
    assert bootstrap_ci([1.0] * 6)[0] > 0 and bootstrap_ci([-1.0] * 6)[1] < 0
    lo, hi = bootstrap_ci([1, -1, 1, -1, 0, 0])
    assert lo < 0 < hi
    assert split_front("---\nweight: 2\n---\nbody")[1] == "body"
    # every real case loads and has graders
    for n in all_cases():
        c = load_case(n)
        assert c["prompt"] and c["graders"], n
    mk = lambda case, arm, t, sc: {"case": case, "arm": arm, "trial": t, "score": sc, "graders": [], "error": None,
                                   "cost_usd": 0.1, "turns": 3, "wall_s": 5, "tokens": 100}
    good = [mk("x", "with", t, 1.0) for t in range(4)] + [mk("x", "without", t, 0.25) for t in range(4)]
    assert summarize(good)["verdict"] == "skill helps"
    bad = [mk("x", "with", t, 0.0) for t in range(4)] + [mk("x", "without", t, 1.0) for t in range(4)]
    s = summarize(bad)
    assert s["verdict"] == "skill hurts" and "REGRESSION" in render(s, bad)
    inv = good + [dict(mk("x", "with", 9, 0.0), invalid=True)]
    assert summarize(inv)["invalid_runs_excluded"] == 1 and summarize(inv)["verdict"] == "skill helps"
    # stubbed end-to-end: no network, judge says pass
    os.environ["AB_STUB"] = '{"passed": true, "evidence": "stub"}'
    tmp = tempfile.mkdtemp()
    try:
        ns = argparse.Namespace(out=tmp, model="m", judge_model="m", budget_usd=1, timeout=30)
        rec = run_one(load_case(all_cases()[0]), "with", 0, ns)
        assert rec["score"] == 1.0 and rec["graders"], rec
        assert os.listdir(os.path.join(tmp, all_cases()[0], "with-0", "work")), "scaffold placed no files"
    finally:
        os.environ.pop("AB_STUB")
        shutil.rmtree(tmp, ignore_errors=True)
    print(json.dumps({"self_test": "PASS"}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", choices=["run", "report"])
    ap.add_argument("path", nargs="?")
    ap.add_argument("--cases", default="")
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--judge-model", default="sonnet")
    ap.add_argument("--out", default=os.path.join(tempfile.gettempdir(), "maca-ab-%d" % int(time.time())))
    ap.add_argument("--budget-usd", type=float, default=2.0, help="cap per model run")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.cmd == "report":
        s = write_report(a.path)
        print(render(s, []))
        return
    if a.cmd != "run":
        ap.error("need run, report or --self-test")
    names = [c for c in a.cases.split(",") if c] or all_cases()
    os.makedirs(a.out, exist_ok=True)
    for n in names:
        case = load_case(n)
        for t in range(a.trials):
            for arm in (ARMS if t % 2 == 0 else ARMS[::-1]):  # alternate order so drift hits both arms equally
                r = run_one(case, arm, t, a)
                print("%-34s %-7s t%d score=%.2f cost=$%.3f%s" % (n, arm, t, r["score"], r["cost_usd"], "  ERROR " + str(r["error"]) if r["error"] else ""), flush=True)
    s = write_report(a.out)
    print("\n" + open(os.path.join(a.out, "report.md")).read())
    print("results:", a.out)


if __name__ == "__main__":
    main()
