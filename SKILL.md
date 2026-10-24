---
name: multi-agent-collaborative-audit
description: >-
  DEFAULT master orchestration, collaborative audit, and E2E intent verification protocol
  for all coding, software architecture, UI/UX design, debugging, refactoring, and clinical/system
  verification tasks. Automatically triggers on any non-trivial engineering request to coordinate
  delegate-skills (claude-delegate, opencode-delegate, codex-delegate, agy-delegate), enforce the
  5-Phase SDD workflow, Phase 1.5 Visual Approval Gate, 7-Rung Ponytail minimalism, Rule 6 Tabula Rasa
  adversarial diff audits, Phase 4 Dedicated Sequential E2E & Call-Chain Verification Zone, and
  task queue synchronization (current_task.md / PLAN_TASKS.md).
---

# Multi-Agent Collaborative Audit & E2E Intent Verification (MACA)

Coordinate specialized agent lanes (`UI/UX`, `Core Logic`, `Data`, `QA & E2E Audit`) plus an independent **Skill Ambassador & Compliance Referee (`سفير وحكم المهارة`)** through a 5-phase Specification-Driven Development (SDD) workflow. Keep this file lean in context and load the linked `references/` files only when entering their respective phase (**Progressive Disclosure**).

## Core Hard Gates (Never Bypass)

1. **Skill Ambassador & Referee Lock (Two-Checkpoint Procedural Gatekeeper)**:
   * **Role**: The **Skill Ambassador** writes **zero application code**. Its sole mandate is enforcing 100% adherence to this skill across all agents and logging agent compliance + skill friction in `.agents/SKILL_COMPLIANCE_LOG.md` (template: `resources/templates/SKILL_COMPLIANCE_LOG.template.md`).
   * **Entry Checkpoint (Phase 0)**: Run `python3 ./scripts/skill_ambassador_auditor.py --init-log <workspace_dir> --feature "<feature_name>"` before planning or coding to lock the 9 mandatory gates (`G-01` to `G-09`).
   * **Exit Checkpoint (Phase 4/5)**: Before marking any task `[x]` or concluding the turn, run `python3 ./scripts/skill_ambassador_auditor.py --audit-workspace <workspace_dir>` and record each agent lane's compliance score and any skill friction in `.agents/SKILL_COMPLIANCE_LOG.md`. If the Ambassador returns `BLOCKED_BY_SKILL_VIOLATIONS`, **halt and remediate the skipped gate immediately**.
2. **Anti-Fake-Review Lock**: Never mark all lanes `[In-Process]` in a single turn to self-approve your own code. Every review in `.agents/AI_HANDOFF_LEDGER.md` must cite actual CLI output, subagent output, or deterministic command evidence.
3. **Fail-Closed Script Protocol**: Whenever `./scripts/bootstrap.sh`, `./scripts/scenario_and_callchain_engine.py`, `./scripts/skill_ambassador_auditor.py`, or `./scripts/measure_metrics.py` returns a non-zero exit code or outputs `MACA_SCRIPT_ERROR`, **STOP IMMEDIATELY**. Run the script with `--self-test`, fix the input or environment issue, and re-run until `PASS` (`exit code 0`).
4. **Task Queue Lock (`current_task.md`)**: Read `tasks/current_task.md` (or `.agents/PLAN_TASKS.md`) before starting. Execute unchecked items (`- [ ]`) in priority order. Update `- [ ]` to `- [x]` with inline command/date evidence only after Phase 4 and the Skill Ambassador Exit Checkpoint pass.

## Phase 0: One-Time First-Run Diagnostic & 3-Tier Scarcity Cascade

1. **One-Time First-Run Deep Diagnostic (`first_run_preflight.py`)**:
   * Execute `./scripts/bootstrap.sh` (which invokes `python3 ./scripts/first_run_preflight.py`).
   * **On First Use (or after any script edit / `--force-first-run`)**: The script verifies that all 25+ internal skill files, Python engines, and vendored Node relays (`vendor/delegate-skills/skills/*-delegate/scripts/relay.mjs`) exist in their exact locations and pass `--self-test`, and audits all external CLIs and E2E tools (`opencode`, `codex`, `claude`, `agy`, `gemini`, `playwright`, `e2e`, `adb`, `maestro`).
   * **No Silent Fallback on Missing Tools (إلزامية إخطار المستخدم بالأدوات الناقصة وطرق حلها)**: If `first_run_preflight.py` reports **any** missing or non-working tool in `missing_external_tools` (or `broken_scripts`), you are **STRICTLY FORBIDDEN from silently ignoring it and working around it without telling the user**. You MUST display a concise table of the missing tools, their impact, and their exact copy-paste installation/fix commands (`remediation`), and ask whether the user wants to fix/install them first or proceed with the available working tools.
   * **On Subsequent Runs**: Once `.first_run_verified.json` is stamped, `bootstrap.sh` automatically uses the fast path (`<0.1s`) unless `--force-first-run` is passed.
2. Initialize `.agents/SKILL_COMPLIANCE_LOG.md` via `skill_ambassador_auditor.py --init-log`, plus `.agents/AGENTS.md` and `.agents/AI_HANDOFF_LEDGER.md` from `resources/templates/`.
3. Route tasks via the highest available tier:
   * **Tier 1 (Vendored Delegate Relays & External CLIs)**: Dispatch bounded briefs using `node ./vendor/delegate-skills/skills/<skill>-delegate/scripts/relay.mjs --brief <brief.txt> --cd <repo_path>` for `claude-delegate` (UI/UX), `opencode-delegate` (Core Logic / Data), `codex-delegate` (Systems), and `agy-delegate` (QA, E2E & Skill Ambassador Referee).
   * **Tier 2 (Platform Subagents)**: Isolated subagents per lane with clean Tabula Rasa context.
   * **Tier 3 (Two-Step Tabula Rasa Verification)**: Step A writes code and outputs `git diff`; Step B executes deterministic verification commands and audits the raw diff without inheriting Step A's assumptions.

## Phase 1 & 1.5: Zero-Presumption Spec & Visual Approval Gate

1. **Select Domain Pack**: Read [references/domain_packs.md](./references/domain_packs.md) to activate `Clinical/SaMD`, `FinTech`, `Systems`, or `Core Fullstack` rules.
2. **Write `.agents/SPEC_AND_AUDIT.md`**: Using `resources/templates/SPEC_AND_AUDIT.template.md`, document existing fragilities, a **Cross-Function Call-Chain Map** (all upstream callers and downstream callees), and **3-Layer Intended Outcome Oracles**.
3. **Phase 1.5 Visual Gate (UI Tasks Only)**: Read [references/ui_ux_mocking.md](./references/ui_ux_mocking.md). Generate a standalone mock in `.agents/mocks/<feature>.html` or `.svg` and pause for explicit user approval before coding logic.

## Phase 2 & 3: Lane Execution, Ponytail Minimalism & Adversarial Diff Audit

1. **Ponytail Minimalism & Clean Code**: Read [references/ponytail_ladder.md](./references/ponytail_ladder.md) and [references/coding_guidelines.md](./references/coding_guidelines.md) before writing code. Ascend from Rung 1 (YAGNI) $\rightarrow$ Rung 2 (Existing Helper) $\rightarrow$ Rung 3 (Stdlib) $\rightarrow$ Rung 4 (Platform API) $\rightarrow$ Rung 5 (Installed Dep) $\rightarrow$ Rung 6 (Readable Atomic Function) $\rightarrow$ Rung 7 (Custom High-Perf). Never cut input validation, error handling, security, accessibility, or clinical precision.
2. **Rule 6 Tabula Rasa Diff Audit (Max 2 Rounds)**: Audit `git diff` from scratch for state hazards, parameter/unit drift across callers, L10n/domain leaks, and $320\text{dp}/360\text{dp}$ clipping. Log `Hard Blocker` vs. `Deferred Shortcut` (`// ponytail:`) in `.agents/AI_HANDOFF_LEDGER.md`.

## Phase 4: Dedicated E2E, Sequential Scenario & Call-Chain Verification Zone

Read [references/e2e_and_call_chain_testing.md](./references/e2e_and_call_chain_testing.md) and execute all four verification steps before marking any task `[x]`:

1. **Step 4.1 — Interactive Scenario Mode Selector**: Ask the user to choose (unless already specified):
   * **Mode A (`--mode predefined`)**: Run built-in sequential E2E baseline and boundary checks.
   * **Mode B (`--mode imaginary`)**: Run `./scripts/scenario_and_callchain_engine.py --mode imaginary` to propose 3–4 realistic multi-hour domain scenarios (e.g., *Prolonged Labour*, *Fetal Late Deceleration*, *Pre-eclampsia BP Escalation*, *Shift Handoff*) in a table for the user to pick from.
   * **Mode C (`--mode custom`)**: Parse the user's custom hourly sequence via `./scripts/scenario_and_callchain_engine.py --mode custom --custom-steps "<steps>"`.
2. **Step 4.2 — Fast-Forward Intake + Strict Incremental Entry (Anti-Bulk-Mock)**: Pre-seed only static verified case header fields (Name, Age, Parity) to save time. **Never** inject a complete multi-hour array of observations at once (`Bulk Mock`). Dispatch every time-step observation ($T_0 \to \text{Save/Rehydrate} \to T_{+1\text{h}} \to \text{Save/Rehydrate} \to \text{Reload}$) sequentially through the real save pipeline.
3. **Step 4.3 — Cross-Function Call-Chain & Multi-Caller Audit**: Run `./scripts/scenario_and_callchain_engine.py --trace-dir <dir> --symbol <fn>` for every modified function to verify all production callers and confirm zero internal mocks (`vi.mock`, `mockk`) in integration/E2E tests.
4. **Step 4.4 — 3-Layer Intended Outcome Oracle & Negative Control**: Reject tests that only check `exit code 0`, `status 200`, or `not.toThrow()`. Assert exact **Logical Domain output** + **Persisted DB row** + **Rendered UI / Handoff state**, plus a just-below-boundary Negative Control.

## Phase 4.5 & 5: Ambassador Sign-Off, Deep Diagnostics, Notifications & Telemetry

1. **Skill Ambassador Exit Audit**: Run `python3 ./scripts/skill_ambassador_auditor.py --audit-workspace <workspace_dir>` and update `.agents/SKILL_COMPLIANCE_LOG.md` with per-agent compliance scores and any skill improvement observations.
2. **Phase 4.5 On-Demand Profiling**: Read [references/deep_diagnostics.md](./references/deep_diagnostics.md). Ask user permission before running heavy ADB Logcat error hunts, memory/jank profiling, or Crashlytics checks.
3. **Task Check-Off & Notifications**: Check off `- [x]` in `tasks/current_task.md` and run `./scripts/measure_metrics.py --notify "<Title>" "<Message>"` on gate prompts or E2E completion.
4. **Mandatory Fleet Dispatch Badge**: Prepend this exact banner at the top of every response:

```markdown
> 🦅 **MACA Active Fleet Dispatch**
> • **Tier & Phase**: `[Tier 1/2/3]` | `[Phase 1 Spec | 1.5 UI Gate | 3 Build | 4 Sequential E2E Gate]`
> • **Lanes & Proof**: `🎨 UI: [Scope]` | `🧠 Logic: [Scope & Callers]` | `📊 Data: [Scope]` | `🛡️ QA/E2E: [Mode A/B/C & 3-Layer Oracle]`
> • **Skill Ambassador Referee**: `[Gates G-01..G-09 Status & Compliance Score %]` | **Task Queue (`current_task.md`)**: `[Updated [x] / In Progress [/]]`
```
