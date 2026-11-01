# Does MACA help? Before/after test results

Date: 2026-11-01. This page says what was measured, what it showed, and what it cannot show.

## How it was measured

`evals/tools/ab_run.py` runs each eval case twice with the same prompt on a fresh copy of the same scaffold:

| Arm | What Claude has |
|---|---|
| **with** | the MACA skill installed |
| **without** | all skills disabled (the baseline) |

Every run is graded against the case's `graders/*.md` by one judge model that is not told which arm it is grading. The judge sees the response, the workspace changes, the small working files and the facts printed by `evals/tools/check_workspace.py`. Model for both the agent and the judge: Claude Sonnet. Runs where the model or the judge failed (for example a usage limit) are marked invalid and left out, never counted as a 0.

Run it yourself (spends Claude usage):

```bash
python3 evals/tools/ab_run.py run --trials 2 --out /tmp/maca-ab
python3 evals/tools/ab_run.py report /tmp/maca-ab
```

## Results

| Run | Skill version | Pairs | With skill | Without | Difference (95% interval) | Cost per run (with / without) |
|---|---|---|---|---|---|---|
| [1: first full run](ab_results/01-before-slimming-report.md) | original 20 KB `SKILL.md` | 19 | 0.51 | 0.39 | +0.09 (-0.04 to +0.22): not conclusive | $0.177 / $0.076 |
| [2: after slimming](ab_results/02-after-slimming-report.md) | slim 7.7 KB `SKILL.md` + `references/full_path.md` | 16 | 0.65 | 0.49 | +0.16 (+0.06 to +0.26): skill helps | $0.226 / $0.095 |
| [3: two weak cases repeated](ab_results/03-regression-repeat-report.md) | slim | 8 | 0.62 | 0.50 | +0.12 (-0.06 to +0.31): not conclusive | $0.156 / $0.093 |

Score = share of the case's assertions the judge passed (weighted).

## What this shows

* **The skill improves outcomes on the cases it was designed for.** Biggest gains: tier routing for a risky path (`routes-billing-comment-edit`, +0.50 in run 1), closing a non-clinical task without false clinical failures (`non-clinical-verify-closes`, +0.33 to +0.42), and keeping patient data out of vendor briefs.
* **It costs more per run: about 2.3 to 2.4 times.** The extra spend is the process itself: loading the instructions, a second reviewer, writing evidence files. Slimming `SKILL.md` did not lower the cost in run 2, so the saving the skill aims for (cheaper models for low-risk roles, reused test results) is **not demonstrated by this test**: both arms use the same model, and each case is run once from scratch, so there is nothing to reuse.
* **One real gap:** `repo-text-injection-ignored` sometimes reports the injected comment in the source file but not the one in the README.

## What this cannot show

* Small samples: 2 trials per case, 16 to 19 pairs. Single cases are noise; read the overall difference.
* One judge model and one agent model (Sonnet). A different judge could score differently.
* Run 2 covers 8 of 14 cases. The remaining 6 were not re-run after slimming because the test was stopped.
* Cost savings from routing across several vendors, and from the evidence cache over many changes in a long-lived project, were not measured.
* The cases are the skill's own evals, so they favour what the skill checks for.
