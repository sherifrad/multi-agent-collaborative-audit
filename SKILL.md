---
name: multi-agent-collaborative-audit
description: >-
  Run a team of specialized agents on one engineering task in two complementary modes: IMPLEMENTATION
  (builder lanes build to a written spec) and TESTING (independent test design, impact-selected test runs
  with cached evidence, adversarial diff review). An orchestrator routes the work, learns the project's
  purpose once through an intake profile, and keeps token cost low (cache-friendly briefs, reused test
  results, saved helper scripts). Use when the user asks for multi-agent / multi-lane / team-style work, an
  independent audit or second-opinion review, "MACA", regression or release verification, delegating to
  claude/codex/opencode/agy/gemini CLIs or subagents, or when a change is high-stakes (safety, money,
  security, regulated data, migrations) or spans UI + logic + data where self-review would be unreliable.
  Skip for small single-file edits, quick questions, or routine fixes one agent can build and test alone.
---

# MACA: Multi-Agent Collaborative Audit

MACA exists because one agent reviewing its own work shares its own blind spots: tests it wrote pass, the
spec it assumed looks right, and the real app still breaks. The fix is structural: **separate who builds
from who checks, give every handoff a written contract, verify through the real code path, and spend test
effort only where a change could have altered a result.** If a step doesn't serve one of those, skip it
and say so.

## 0. Intake: learn the direction once

MACA is domain-neutral, so it must learn what the project is for before it can pick rules and strictness.
If `.agents/PROJECT_PROFILE.md` does not exist, run intake (`references/intake.md`): ask the user a short
round of questions (purpose, audience, what a serious failure looks like, areas touched, build/test
commands, cost preference, approvers, model tiers), then write the profile from
`resources/templates/PROJECT_PROFILE.template.md`. If it exists, read it and do not re-ask. If nobody can
answer, infer from the repo, mark each guess `(inferred - confirm)`, choose the cautious option, and list
the guesses first in the report. The profile selects the domain packs, the default weight, tier ceilings
and model tiers.

## 1. Choose mode and weight (state both in one line)

**Mode**
- **Implementation mode**: build, fix, refactor. Output: code + change summary + new test-manifest entries.
- **Testing mode**: audit, verify, review, regression, pre-release. Output: verdict + evidence.
- They are complementary. The spec's *outcome oracles* are the contract between them: testing mode turns
  oracles into tests, implementation mode makes them pass, and a defect found in testing becomes a failing
  test that goes back to implementation (max 2 rounds). Either mode can run alone. Details and the full role
  map: `references/roles_and_modes.md`.

**Weight**

| Path | Use when | What runs |
|---|---|---|
| **Light** | Small or low-risk change, but a second pair of eyes is wanted | See "Light path rules" |
| **Full** | Multi-file or multi-lane feature, or any high-assurance domain | Phases 0-5 |

High-stakes signals (auto-select Full and load the matching pack from `packs/INDEX.md`): harm to a person,
money movement, auth/permissions, regulated data, irreversible data changes, safety-relevant calculations.
The profile's risk level and cost preference set the defaults.

**Light path rules.** Keep the paper trail to `REPORT.md` (3-5 line spec, the reviewer's verdict quoted, the commands you ran)
plus at most one `review.md` holding the diff, the reviewer's brief and its output (no separate diff or
brief files); no `.agents/` files, task queue,
compliance log or referee. Give the reviewer spec + diff inline, never your reasoning. Still required: a reviewer that did
not write the code, and tests you actually ran. Fix real defects it finds, and say if a fix was not
re-reviewed. If scope grows (more files, an auth/data/clinical touch), switch to Full and say why.

## 2. The team and who decides

The **orchestrator** is the agent talking to the user (or the one named in `.agents/fleet.json`). It routes,
owns the spec and the ledger, enforces tier ceilings, and reports honestly. On the Full path it does not
write the code it approves. Everyone else:

| Role | Mode | Job in one line |
|---|---|---|
| UI/UX, Core Logic, Data lanes | implementation | Build their slice from a bounded brief; don't cross interfaces |
| Test Designer | testing | Writes tests and the manifest from the spec only, before looking at the code |
| Test Runner | testing | Runs the selected tests, records evidence (a script or a cheap model is enough) |
| Adversarial Reviewer | testing | Audits spec + diff + test results; never sees the author's reasoning |
| Referee (Full only) | testing | Checks that gates have real evidence; writes no app code |

**Independence rule:** Test Designer != Builder and Reviewer != Author. A review counts only if backed by
evidence you can point to (command output, a different agent's transcript, a failing-then-passing test).
When separation is impossible, launch a **fresh process** for the second role (a new subagent, or
`claude -p` given only the allowed inputs) and label it "same-model review". Re-reading your own work in the
same context is the last resort and must be labelled as such. Full role table, inputs per role, model
guidance and handoff format: `references/roles_and_modes.md`.

**Proportionality (cost guardrail).** Match ceremony to size. For a change to one small function or file,
two fresh-process roles are enough (a tests-first Test Designer and one Reviewer); the orchestrator or a
single builder writes the code, and extra builder/reviewer processes add cost without adding independence.
Test volume follows the oracles: boundary and negative cases plus the identity matrix for auth, not
hundreds of generated permutations. One review round is the default; use the second only if the first found
a blocker. Say in the report which roles were merged and why.

## 3. Dispatch tiers (use the highest available, degrade gracefully)

1. **External CLIs** via vendored relays (`vendor/delegate-skills/skills/<agent>-delegate/scripts/relay.mjs
   --brief <file> --cd <repo>`), configured in `.agents/fleet.json`. Different models give the most
   independent review.
2. **Platform subagents**, one per role, each with a clean context.
3. **Fresh-process fallback**: `claude -p` (or similar) per role with restricted inputs.

Run `bash ./scripts/bootstrap.sh` once per repo to detect what is available (cached afterwards). If it
reports missing tools, show the user a short table (tool, impact, install command) and continue one tier
down; never fail silently.

## 4. Workflow

**Phase 0 - Frame.** Read the task queue (`tasks/current_task.md` or `.agents/PLAN_TASKS.md`) if present.
Seed `.agents/` from `resources/templates/`. Full path: `python3 ./scripts/skill_ambassador_auditor.py
--init-log <ws> --feature "<name>"`.

**Phase 1 - Spec (orchestrator).** Write `.agents/SPEC_AND_AUDIT.md`: the requirement in the user's words,
known fragilities, a **call-chain map** (callers and callees of what will change), and **outcome oracles**
(what exact result proves success at domain, storage and visible-UI level). Apply the packs named in the profile
(`packs/INDEX.md`). UI work: produce a mock in `.agents/mocks/` and get explicit approval before
building logic (`references/ui_ux_mocking.md`).

**Phase 1b - Tests first (testing mode, Full path).** The Test Designer turns each oracle into tests and
registers them in `.agents/TEST_MANIFEST.json` (template in `resources/templates/`), each with a tier and
`deps`. Boundary and invalid-input cases included. Writing them before the code stops tests bending to fit it.

**Phase 2 - Build (implementation mode).** Lanes work from bounded briefs. Prefer the simplest thing that
meets the spec (`references/ponytail_ladder.md`, `references/coding_guidelines.md`); log deliberate shortcuts
in the ledger's debt table. After each lane: Tier 0-1 checks on what it touched. Nothing deeper yet.

**Phase 3 - Independent audit (testing mode, max 2 rounds).** The reviewer audits the diff against the spec
and call-chain map and classifies findings Hard Blocker / Deferred Shortcut / Pass in the ledger. After
round 2, unresolved disagreements go to the user with both positions.

**Phase 4 - Verify, economically (testing mode).** Do not rerun everything. Read
`references/test_economy.md`, then:

```
python3 scripts/impact_and_cache.py select --ws <ws> --max-tier 2     # shows RUN / REUSE / DEFER
# run only RUN lines; after each: impact_and_cache.py record --ws <ws> --id <id> --status pass|fail
```

Passed tests are reused only when a hash of everything they depend on is unchanged; failed tests, tests
marked `always`, and tests with unmatched `deps` always run; tests above the tier ceiling are reported as
*not run*, never as passed. Do not also run the whole suite "to be safe" in the same round: it spends what the cache saved and contradicts
any reuse claim. If you do run extra tests, `record` them and drop the reuse claim for those tests. Show the plan line to the user (`Ran 6 | Reused 14 | Deferred 3`) and raise the
ceiling when risk demands it (changed safety rule, auth, migration). Verification principles, which apply
to every test you do run, are in `references/verification_principles.md`; stack recipes for Android/clinical
are in `references/e2e_and_call_chain_testing.md`. For auth changes only a verified identity claim may grant
admin, so a username-only match must be rejected (`scenario_and_callchain_engine.py --auth-fuzz-matrix`).

**Phase 5 - Close.** Full path: `python3 ./scripts/skill_ambassador_auditor.py --verify <ws>` plus
`python3 ./scripts/lint_samd_invariants.py --scan-dir <source dir>` when the clinical pack or any auth/data
risk applies, and `lint_design_and_ux.py --scan-dir <source dir>` for UI (a result of `files_scanned: 0` or
`NOT_APPLICABLE_NO_SOURCE_FILES` is not evidence; point it at the code). Tick the task queue only after
these pass, with command and date. At a release gate run `impact_and_cache.py invalidate --all` and a full
T3 replay. Deep profiling (T4) only on request: `references/deep_diagnostics.md`.

## 4b. Spending tokens wisely (applies to every phase)

Details in `references/token_economy.md`. In short:
- **Cache-friendly briefs.** Build every role brief as one shared prefix (`.agents/BRIEF_PREFIX.md`: profile,
  spec summary, oracle list) followed by a short role-specific part. Stable material first, changing
  material last, never edit the prefix mid-session, and continue sessions rather than re-uploading files.
- **Reuse results.** Passed tests via `impact_and_cache.py`; reviews of unchanged diffs by citing the
  ledger entry.
- **Harness library.** Before writing a helper script run `python3 scripts/harness.py check --ws <ws> --need
  "<what it does>"`. `FOUND` -> `harness.py run` it. `PROMOTE` (second time the need appears) -> write it
  once, `register` it with a self-test, and call it by name from then on. If the user says the task recurs
  ("every week", "for each export"), write and register the script on first use instead of waiting.
- **Right model per job.** Strong model for spec and adversarial review; cheap model or a script for runs.

## 5. Rules that protect the process

- **Scripts fail closed.** A non-zero exit or `MACA_SCRIPT_ERROR` means stop, run it with `--self-test`, fix
  the cause, re-run. A skipped gate reported as passed is worse than a failed one.
- **Ask when a person is present, assume when not.** Where the process asks the user (mock approval, scenario
  choice, raising a tier ceiling, profiling), ask in interactive sessions. Unattended: take the documented
  default, record the assumption in the ledger, continue.
- **One-line status, not a banner.** At each phase change say the phase, who ran, and the proof. Long tables
  only in the final report.
- **Report what was not verified.** Say what ran, what was reused and why, what was deferred, and what could
  not be checked (for example no repo or device). Never certify beyond the evidence.

## 6. Resource map (load on demand)

| File | Load when |
|---|---|
| `references/roles_and_modes.md` | Choosing mode, assigning roles, writing briefs |
| `references/test_economy.md` | Phase 4, always on the Full path |
| `references/verification_principles.md` | Writing or judging any test |
| `references/intake.md` | First run in a project, or when a task contradicts the profile |
| `packs/INDEX.md` | Phase 1, to load the packs the profile names (core, fintech, systems, data-etl, clinical) |
| `references/token_economy.md` | Writing briefs, choosing models, before writing any helper script |
| `references/e2e_and_call_chain_testing.md` | Android/Kotlin, Compose or clinical stacks (part of the clinical pack) |
| `references/ui_ux_mocking.md` | Any UI change |
| `references/ponytail_ladder.md`, `references/coding_guidelines.md` | Phase 2 |
| `references/deep_diagnostics.md` | Optional T4 profiling |
| `resources/templates/*` | Intake, Phase 0 and 1b, to seed `.agents/` files (PROJECT_PROFILE, SPEC, LEDGER, TEST_MANIFEST) |
