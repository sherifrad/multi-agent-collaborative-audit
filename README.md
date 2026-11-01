# MACA: Multi-Agent Collaborative Audit

A skill for AI coding agents (Claude Code, Codex, opencode, Antigravity `agy`) that stops one agent from grading its own homework. It separates who builds from who checks, writes down what "done" means before the code exists, and re-runs only the tests that a change could have affected.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## What it does, in plain words

When you ask an agent to change code, the same agent usually writes the tests, reviews the result and says "looks good". Its blind spots are shared across all three steps. MACA changes the process:

1. **Triage first.** A trivial change (a rename, a typo) skips MACA entirely. A small change gets a short *Light* check. Risky or multi-file work gets the *Full* path.
2. **Write the contract first.** The spec lists outcomes that must be true (`ORACLE-1: a user named admin without a verified admin claim is rejected`).
3. **Tests come from the spec, not from the code**, written by a different agent than the builder.
4. **An independent reviewer** audits the change without seeing the author's reasoning. The report says honestly whether the review was by a different model or the same one.
5. **Only affected tests re-run.** Passed tests are reused until something they depend on changes; tests that were not run are reported as *not run*, never as passed.
6. **A referee script checks the paperwork.** It refuses to say `APPROVED` unless the records have real evidence behind them.

Good for: auth, money, personal or regulated data, migrations, safety rules, release checks, second-opinion reviews. Not for: quick questions or small edits with no risk.

## Does it work? (measured, with limits)

Tested by running the same tasks with and without the skill and grading both the same way. Full details: [docs/AB_TEST_RESULTS.md](docs/AB_TEST_RESULTS.md).

| | With MACA | Without |
|---|---|---|
| Share of checks passed (16 task pairs, after slimming) | **0.65** | 0.49 |
| Cost per task (Claude Sonnet) | about $0.23 | about $0.10 |

* It does improve outcomes on risky-change tasks, and the gain is statistically clear in the latest run (+0.16, interval +0.06 to +0.26).
* **It costs about 2.4 times as much per task** in this test. The test does not measure the savings the design aims for (cheaper models for low-risk roles, test reuse over many changes), so do not read this as a proven way to cut cost.
* Small sample, one judge model, and the skill's own test cases. Treat it as evidence, not proof.

## Install

The skill is a folder. Put it where your agent looks for skills (a symlink keeps one copy up to date):

```bash
git clone https://github.com/sherifrad/multi-agent-collaborative-audit.git
SKILL=$PWD/multi-agent-collaborative-audit
ln -s "$SKILL" ~/.claude/skills/multi-agent-collaborative-audit              # Claude Code
ln -s "$SKILL" ~/.codex/skills/multi-agent-collaborative-audit               # Codex
ln -s "$SKILL" ~/.config/opencode/skills/multi-agent-collaborative-audit     # opencode
ln -s "$SKILL" ~/.gemini/antigravity/skills/multi-agent-collaborative-audit  # agy
```

Needs Python 3.9+. Scripts use only the standard library. Node is needed only for dispatching to other agent CLIs. Check your setup:

```bash
python3 scripts/first_run_preflight.py     # expect "internal_health": "PASS"
```

## Use it

Ask your agent in plain words: *"Use MACA to add rate limiting to the login endpoint"*, or *"MACA review of my uncommitted changes"*. On the first Full-path run it asks a few questions (purpose, what a serious failure looks like, build and test commands, which AI vendors may see your code) and saves the answers in `.agents/PROJECT_PROFILE.md`. It does not ask again.

Useful commands:

```bash
python3 scripts/fleet_select.py --cwd .                       # which agents/vendors can fill which roles
python3 scripts/model_router.py route --role reviewer         # model tier and effort for a role, from measured risk
python3 scripts/impact_and_cache.py select --ws . --max-tier 2   # which tests to RUN, REUSE or DEFER
python3 scripts/skill_ambassador_auditor.py --verify . --src-dir src --max-tier 3   # the referee
```

The referee's answer is literal: `APPROVED` is the only pass. `BLOCKED_BY_SKILL_VIOLATIONS` means fix and re-run. `INCOMPLETE_NOT_VERIFIED` means something could not be checked and must be reported as unverified.

## Safety rules it follows

* Your code goes only to AI vendors you list as approved in the profile. Personal data never goes into briefs.
* Text found in the repo (README, comments, issues) is treated as data, not instructions.
* Unattended runs take the cautious default and list their assumptions. They never push, delete, send, widen permissions or approve a UI mock on their own.
* All scripts fail closed: an error stops the run instead of reporting a pass.

## What is in the folder

| Path | What |
|---|---|
| `SKILL.md` | The instructions the agent reads (short: triage, Light path, rules) |
| `references/full_path.md` | The Full path in detail, loaded only when needed |
| `references/` | Roles, test economy, model routing, checklists (core, fintech, systems, data-etl), UI mocking |
| `packs/clinical/` | Extra checks for health and other safety-critical software (directions only, no medical values) |
| `scripts/` | Router, project risk map, fleet selection, test cache, referee, linters, preflight |
| `resources/` | Templates for the profile, spec, ledger and test manifest; subagent definitions |
| `evals/` | 14 test cases with graders, and `evals/tools/ab_run.py` for the before/after comparison |
| `vendor/delegate-skills/` | Upstream relays for Codex, opencode, agy and Claude, vendored unmodified (MIT, see `VENDOR.md`) |
| `docs/` | Test results and the earlier detailed fleet guide |

## Check your changes to the skill

```bash
for f in first_run_preflight fleet_run fleet_select harness impact_and_cache lint_design_and_ux \
         lint_samd_invariants model_router project_map scenario_and_callchain_engine skill_ambassador_auditor; do
  python3 scripts/$f.py --self-test >/dev/null && echo "ok $f" || echo "FAIL $f"
done
```

## License

MIT. See [LICENSE](LICENSE). The vendored relays keep their own MIT license.
