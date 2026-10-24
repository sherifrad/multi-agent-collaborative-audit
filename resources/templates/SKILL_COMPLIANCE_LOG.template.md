# 🏛️ MACA Skill Ambassador & Referee Compliance Log (`SKILL_COMPLIANCE_LOG.md`)

* **Feature / Task Under Audit**: `[Feature Name / Task ID from current_task.md]`
* **Skill Ambassador**: `[Independent Procedural Referee — Zero Application Code Authorship]`
* **Audit Mode**: `Live Skill Execution & Meta-Diagnostics`

---

## 1. Pre-Flight Mandatory Gate Charter (Locked at Phase 0)

| Gate ID | Mandatory Skill Rule | Required Artifact / Evidence | Status (`PASS`/`VIOLATION`) | Ambassador Notes |
| :--- | :--- | :--- | :--- | :--- |
| **G-01** | **Phase 0 Bootstrap & Script Health** | `./scripts/bootstrap.sh` & `--self-test` returned `exit code 0` | `PENDING` | - |
| **G-02** | **Phase 1 Spec & Call-Chain Map** | `.agents/SPEC_AND_AUDIT.md` maps all upstream callers & downstream callees | `PENDING` | - |
| **G-03** | **Phase 1.5 Visual Mock Gate** | `.agents/mocks/<feature>.html` or `.svg` signed off by User before logic coding | `PENDING` | - |
| **G-04** | **Phase 3 Tabula Rasa Diff Audit** | Independent peer review in `.agents/AI_HANDOFF_LEDGER.md` (zero fake `[In-Process]`) | `PENDING` | - |
| **G-05** | **Phase 4.1 Scenario Mode Choice** | User offered Mode A (Predefined), Mode B (Imaginary), or Mode C (Custom) | `PENDING` | - |
| **G-06** | **Phase 4.2 Anti-Bulk-Mock Rule** | Fast-forward intake + sequential step-by-step entry ($T_0 \to T_1 \to T_2$) | `PENDING` | - |
| **G-07** | **Phase 4.3 Call-Chain & Zero Mock** | `scenario_and_callchain_engine.py --trace-dir` passed with zero internal mocks | `PENDING` | - |
| **G-08** | **Phase 4.4 3-Layer Outcome Oracle** | Domain + DB Persistence + Visual UI assertions + Negative Control verified | `PENDING` | - |
| **G-09** | **Task Queue Sync (`current_task.md`)** | Completed item updated from `- [ ]` to `- [x]` with inline command/date proof | `PENDING` | - |

---

## 2. Live Agent Evaluation & Skill Friction Log (سجل تقييم أداء الـ Agents وملاحظات تطوير المهارة)

*Record every instance where an agent attempted to cut corners, misunderstood a skill instruction, or hit a tool friction point:*

| Round / Phase | Agent / Lane Evaluated | Behavior Observed | Compliance Verdict | Skill Friction / Root Cause | Proposed Skill Refinement |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Phase 1` | `Antigravity / Planner` | `[Did the agent map all callers before coding?]` | `[PASS / VIOLATION]` | `[Any ambiguity in SKILL.md?]` | `[Exact wording or script tweak]` |
| `Phase 3` | `Implementer Lane` | `[Did the agent obey Ponytail Rungs 1-6?]` | `[PASS / VIOLATION]` | `[Any attempted shortcut?]` | `[Exact wording or script tweak]` |
| `Phase 4` | `QA & E2E Audit Lane` | `[Did it run sequential steps instead of bulk mock?]` | `[PASS / VIOLATION]` | `[Any E2E runner issue?]` | `[Exact wording or script tweak]` |

---

## 3. Final Ambassador Sign-Off & Verdict
* **Deterministic Audit Command**: `python3 scripts/skill_ambassador_auditor.py --audit-workspace .`
* **Overall Skill Compliance Score**: `[0–100%]`
* **Ambassador Clearance**: `[APPROVED FOR COMMIT / BLOCKED — FIX VIOLATIONS FIRST]`
