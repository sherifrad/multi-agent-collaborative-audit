---
name: multi-agent-collaborative-audit
description: >-
  DEFAULT master orchestration, collaborative audit, and E2E intent verification protocol (MACA v2)
  for all coding, software architecture, UI/UX design, debugging, refactoring, and clinical/system
  verification tasks. Automatically triggers on any non-trivial engineering request to coordinate
  delegate-skills (claude-delegate, opencode-delegate, codex-delegate, agy-delegate), enforce the
  5-Phase SDD workflow, Phase 1.5 Visual Approval Gate, 7-Rung Ponytail minimalism, Rule 6 Tabula Rasa
  adversarial diff audits, Phase 4 Sequential E2E, 4-Pillar Design/UX/Geometric Zone & SaMD Invariants,
  and task queue synchronization (current_task.md / PLAN_TASKS.md).
---

# Multi-Agent Collaborative Audit & E2E Intent Verification (MACA v2)

Coordinate specialized agent lanes (`UI/UX`, `Core Logic`, `Data`, `QA & E2E Audit`) plus an independent **Skill Ambassador & Compliance Referee (`سفير وحكم المهارة`)** through a 5-phase Specification-Driven Development (SDD) workflow. Keep this file lean in context and load the linked `references/` files only when entering their respective phase (**Progressive Disclosure**).

## Core Hard Gates (Never Bypass)

1. **Skill Ambassador & Automated Referee Lock (`skill_ambassador_auditor.py`)**:
   * **Role**: The **Skill Ambassador** writes **zero application code**. Its sole mandate is enforcing 100% adherence to this skill across all agents and logging compliance + skill friction in `.agents/SKILL_COMPLIANCE_LOG.md`.
   * **Entry Checkpoint (Phase 0)**: Run `python3 ./scripts/skill_ambassador_auditor.py --init-log <workspace_dir> --feature "<feature_name>"` before planning or coding to lock gates `G-01` to `G-10`.
   * **Exit Checkpoint (Phase 4/5 — Upgrade 5 Auto-Referee)**: Before marking any task `[x]` or concluding the turn, run `python3 ./scripts/skill_ambassador_auditor.py --verify <workspace_dir>` to execute static SaMD/JVM and Design/UX invariants, hash all modified files (`SHA-256`), and auto-append the deterministic compliance proof table to `.agents/SKILL_COMPLIANCE_LOG.md`.
2. **Anti-Fake-Review Lock**: Never mark all lanes `[In-Process]` in a single turn to self-approve your own code. Every review in `.agents/AI_HANDOFF_LEDGER.md` must cite actual CLI, subagent, or deterministic verification command output.
3. **Fail-Closed Script Protocol**: Whenever any script in `./scripts/` returns a non-zero exit code or outputs `MACA_SCRIPT_ERROR`, **STOP IMMEDIATELY**. Run the script with `--self-test`, fix the input or environment issue, and re-run until `PASS` (`exit code 0`).
4. **Task Queue Lock (`current_task.md`)**: Read `tasks/current_task.md` (or `.agents/PLAN_TASKS.md`) before starting. Execute unchecked items (`- [ ]`) in priority order. Update `- [ ]` to `- [x]` with inline command/date evidence only after Phase 4 and `skill_ambassador_auditor.py --verify` pass.

## Phase 0: One-Time First-Run Diagnostic & 3-Tier Scarcity Cascade

1. **One-Time First-Run Deep Diagnostic (`first_run_preflight.py`)**:
   * Execute `./scripts/bootstrap.sh` (which runs `python3 ./scripts/first_run_preflight.py`).
   * **No Silent Fallback on Missing Tools**: If `first_run_preflight.py` reports any missing or broken tool in `missing_external_tools` or `broken_scripts`, you MUST display a concise table of the missing tools, their impact, and their exact copy-paste `remediation` commands to the user before proceeding.
   * **Fast Path on Subsequent Runs**: Once `.first_run_verified.json` is stamped, `bootstrap.sh` runs in `<0.1s` unless `--force-first-run` is passed.
2. Route tasks via the highest available tier:
   * **Tier 1 (Vendored Delegate Relays & External CLIs)**: Dispatch bounded briefs using `node ./vendor/delegate-skills/skills/<skill>-delegate/scripts/relay.mjs --brief <brief.txt> --cd <repo_path>` for `claude-delegate` (UI/UX), `opencode-delegate` (Core Logic / Data), `codex-delegate` (Systems), and `agy-delegate` (QA, E2E & Skill Ambassador Referee).
   * **Tier 2 (Platform Subagents)**: Isolated subagents per lane with clean Tabula Rasa context (e.g., `firestore-rules-author` for Cloud Security rules).
   * **Tier 3 (Two-Step Tabula Rasa Verification)**: Step A writes code and outputs `git diff`; Step B executes deterministic verification commands and audits the raw diff without inheriting Step A's assumptions.

## Phase 1 & 1.5: Zero-Presumption Spec & Visual Approval Gate

1. **Select Domain Pack**: Read [references/domain_packs.md](./references/domain_packs.md) to activate `Clinical/SaMD`, `FinTech`, `Systems`, or `Core Fullstack` rules.
2. **Write `.agents/SPEC_AND_AUDIT.md`**: Using `resources/templates/SPEC_AND_AUDIT.template.md`, document existing fragilities, a **Cross-Function Call-Chain Map** (all upstream callers and downstream callees), and **3-Layer + Geometric + 4-Pillar Design/UX Outcome Oracles**.
3. **Phase 1.5 Visual Gate (UI Tasks Only)**: Read [references/ui_ux_mocking.md](./references/ui_ux_mocking.md). Generate a standalone mock in `.agents/mocks/<feature>.html` or `.svg` (evaluating $360\text{dp}$ Phone and $840\text{dp}$ Tablet in LTR/RTL) and pause for explicit user approval before coding logic.

## Phase 2 & 3: Lane Execution, Ponytail Minimalism & Adversarial Diff Audit

1. **Ponytail Minimalism & Clean Code**: Read [references/ponytail_ladder.md](./references/ponytail_ladder.md) and [references/coding_guidelines.md](./references/coding_guidelines.md). Ascend from Rung 1 (YAGNI) $\rightarrow$ Rung 7 (Custom High-Perf). Keep constructor/method parameter counts $< 20$ (hard ceiling: $< 35$ parameters to prevent JVM 255-word `ClassFormatError`).
2. **Rule 6 Tabula Rasa Diff Audit (Max 2 Rounds)**: Audit `git diff` from scratch and run `python3 ./scripts/lint_samd_invariants.py --scan-dir <workspace_dir>` to enforce:
   * **Zero Hard-Delete (`SaMD-ZERO-DELETE`)**: No unscoped `DELETE FROM` on clinical tables (`labour_case`, `patient`, `observation_bundle`, `audit_event`).
   * **Cryptographic RBAC Claims (`RBAC-STRING-HEURISTIC`)**: No raw `username ==` / `email ==` admin heuristics without verified identity provider claims.
   * **Bytecode Parameter Budget (`JVM-PARAM-BUDGET`)**: Decompose bloated classes into nested value objects before hitting 35 parameters.

## Phase 4: Dedicated E2E, Sequential Scenario, Geometric, Design/UX & Call-Chain Verification Zone

Read [references/e2e_and_call_chain_testing.md](./references/e2e_and_call_chain_testing.md) and [references/ui_ux_mocking.md](./references/ui_ux_mocking.md), and execute all four verification steps before marking any task `[x]`:

1. **Step 4.1 — Interactive Scenario Mode Selector**: Ask the user to choose (unless already specified):
   * **Mode A (`--mode predefined`)**: Run built-in sequential E2E baseline, boundary checks, and negative controls.
   * **Mode B (`--mode imaginary`)**: Run `./scripts/scenario_and_callchain_engine.py --mode imaginary` to propose 3–4 realistic multi-hour domain scenarios in a table for user selection.
   * **Mode C (`--mode custom`)**: Parse the user's custom hourly sequence via `./scripts/scenario_and_callchain_engine.py --mode custom --custom-steps "<steps>"`.
2. **Step 4.2 — Fast-Forward Intake + Strict Incremental Entry (Anti-Bulk-Mock)**: Pre-seed only static verified case header fields (Name, Age, Parity). **Never** inject a complete multi-hour array of observations at once (`Bulk Mock`). Dispatch every time-step observation ($T_0 \to \text{Save/Rehydrate} \to T_{+1\text{h}} \to \text{Save/Rehydrate} \to \text{Reload}$) sequentially through the real save pipeline.
3. **Step 4.3 — Cross-Function Call-Chain & Invariant Audit**: Run `./scripts/scenario_and_callchain_engine.py --trace-dir <dir> --symbol <fn>` and `./scripts/lint_samd_invariants.py --scan-dir <dir>` to verify all production callers and confirm zero internal mocks (`vi.mock`, `mockk`).
4. **Step 4.4 — 3-Layer Outcome Oracle, Geometric Bounds, 4-Pillar Design/UX Audit & Auth Fuzz Matrix**:
   * **Layer 1 (Domain) & Layer 2 (DB Persistence)**: Assert exact signal codes/states (`PROVISIONAL` vs `CONFIRMED`), SQLCipher/Room rows, and immutable `AuditEventEntity` records.
   * **Layer 3 (Visual, Geometric & 4-Pillar Design/UX Oracle — Upgrade 1 & 6)**: For TopBars, Headers, or Action Trays, assert `getUnclippedBoundsInRoot()` non-overlap (`titleBounds.left >= navBounds.right` and `titleBounds.right <= actionsBounds.left`) and minimum title flex width ($\ge 120\text{dp}$ on $320\text{dp}/360\text{dp}$ viewports). Run `python3 ./scripts/lint_design_and_ux.py --scan-dir <dir>` to enforce semantic design tokens (zero hardcoded UI hex colors), SVG/Vector `viewBox` + Arabic RTL `autoMirrored="true"`, WCAG 2.1 AA contrast ($\ge 4.5:1$), the 5 UI states (`Empty`, `Loading`, `Normal`, `Alert`, `200% Font Scale/RTL`), and UX tap budget ($\le 3$ taps, `<15s`, zero IME keyboard occlusion).
   * **Tabula Rasa Auth Fuzz Matrix (Upgrade 2)**: For auth/RBAC flows, run all 6 permutations from `./scripts/scenario_and_callchain_engine.py --auth-fuzz-matrix` (clean match, email-in-username, uppercase/spaces, unverified provider spoof, `+fake` alias spoof, standard clinician).

## Phase 4.5 & 5: Automated Referee Sign-Off, Deep Diagnostics & Notifications

1. **Automated Referee Verification (Upgrade 5)**: Run `python3 ./scripts/skill_ambassador_auditor.py --verify <workspace_dir>` to verify all gates (`G-01`..`G-10`), hash modified files, and append the compliance table to `.agents/SKILL_COMPLIANCE_LOG.md`.
2. **Phase 4.5 On-Demand Profiling**: Read [references/deep_diagnostics.md](./references/deep_diagnostics.md). Ask user permission before running heavy ADB Logcat error hunts, memory/jank profiling, or Crashlytics checks.
3. **Task Check-Off & Notifications**: Check off `- [x]` in `tasks/current_task.md` and run `./scripts/measure_metrics.py --notify "<Title>" "<Message>"` on gate prompts or E2E completion.
4. **Mandatory Fleet Dispatch Badge**: Prepend this exact banner at the top of every response:

```markdown
> 🦅 **MACA v2 Active Fleet Dispatch**
> • **Tier & Phase**: `[Tier 1/2/3]` | `[Phase 1 Spec | 1.5 UI Gate | 3 Build | 4 Sequential, Design/UX & Geometric E2E]`
> • **Lanes & Proof**: `🎨 UI/UX: [Tokens, 5-States & Bounds]` | `🧠 Logic: [Scope & Callers]` | `📊 Data/SaMD: [Zero-Delete & <35 Args]` | `🛡️ QA/E2E: [Mode A/B/C & Auth Fuzz]`
> • **Skill Ambassador (`--verify`)**: `[Gates G-01..G-10 & SHA-256 Proof]` | **Task Queue (`current_task.md`)**: `[Updated [x] / In Progress [/]]`
```
