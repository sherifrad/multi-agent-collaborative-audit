# Multi-Agent Fleet Governance & Role Matrix

This document defines the roles, active lanes, and operational constraints for multi-agent collaboration on this codebase.

## 1. Fleet Leadership
* **Principal Consultant & Fleet Orchestrator**: `Antigravity`
  * Responsibilities: Work breakdown, lane assignment, cross-lane arbitration, call-chain & E2E gate enforcement, `current_task.md` synchronization, desktop notifications, and final git commits.

## 2. Active Fleet Lanes & Role Mapping

| Lane | Assigned Model / Persona | Primary Scope & Responsibilities |
| :--- | :--- | :--- |
| **UI/UX & Graphic Design Lane** | `Claude Sonnet` *(Default)*<br/>*Fallback: Gemini / Antigravity* | Graphic design, page/app wireframing, interactive HTML/SVG mock creation, user visual approval gate, component ergonomics, WCAG 2.1 AA. |
| **Core Logic Lane** | `OpenCode DeepSeek` *(or Logic Persona)* | Business algorithms, math, concurrent workflows, query optimization, core domain rules, and multi-caller contract alignment. |
| **Data Lane** | `OpenCode GLM` *(or Data Persona)* | Schemas, DTOs, migrations, input serialization, validation bounds, append-only audit lineage, i18n/L10n strings. |
| **QA & E2E Audit Lane** | `Gemini / TesterArmy e2e` *(or Audit Persona)* | Cross-function call-chain audit, interactive E2E scenario generation (Mode A/B/C), sequential step-by-step execution, and 3-layer outcome verification. |

## 3. Operational Rules
1. **Ponytail Ladder Compliance**: Every lane must abide by the 7-Rung Ponytail Engine. No unnecessary abstractions or dependencies.
2. **Visual Approval Gate**: All UI, screen, and graphic changes require an interactive mockup created by the UI/UX Lane and explicitly approved by the user before task breakdown or logic coding begins.
3. **Anti-Infinite-Critique & Anti-Fake-Review**: Peer critiques are strictly capped at 2 rounds. Fake single-turn `[In-Process]` self-approval without external CLI, subagent, or deterministic verification command output is strictly prohibited.
4. **Supreme Arbiter Rule**: In case of unresolved cross-lane deadlock after Round 2, `Antigravity` issues a binding ruling and override patch.
5. **Clean Provenance & Task Queue Lock**: All lane handoffs must be registered in `.agents/AI_HANDOFF_LEDGER.md`. Active tasks in `tasks/current_task.md` or `.agents/PLAN_TASKS.md` are checked off (`[x]`) immediately upon passing Phase 4 verification.
6. **Cross-Model Adversarial Diff & Call-Chain Audit**:
   - Prior to git staging/commit, peer model lanes must inspect the active `git diff`, trace all callers of modified functions, and verify implementation evidence independently from scratch (Tabula Rasa).
7. **Phase 4 Mandatory Sequential E2E & 3-Layer Oracle Gate**:
   - Every feature/fix must pass Phase 4: (a) Interactive Scenario Mode Selection (Predefined, AI-Proposed Imaginary Scenarios, or User Custom Sequence), (b) Fast-Forward Baseline Intake + Strict Step-by-Step Sequential Observation Entry (no bulk timeline mocks), (c) Zero-Internal-Mock Call-Chain Integration, and (d) 3-Layer Intended Outcome Oracle (Logical + DB Persistence + Visual UI).
8. **Phase 4.5 On-Demand Deep Diagnostics**:
   - Before final stable release or production commits, prompt the user for permission to run Phase 4.5 low-level profiling (Logcat silent bug hunt, Memory/Jank leak audit, Crashlytics telemetry, Full E2E device replay).
