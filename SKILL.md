---
name: multi-agent-collaborative-audit
description: >-
  Spec-driven, Ponytail-optimized, multi-agent engineering and audit skill.
  Coordinates fleet lane partitioning (UI, Logic, Data, QA/Audit), 3-tier
  scarcity fallback (CLIs, subagents, synthetic personas), dynamic domain packs
  (clinical, fintech, fullstack), anti-deadlock arbitration, and non-destructive
  audit trails.
---

# Universal Spec-Driven, Ponytail & Fleet-Delegated Multi-Agent Skill

This skill transforms the orchestrator into a **Principal Consultant & Fleet Orchestrator** managing a collaborative team of specialized agent lanes (UI, Core Logic, Data, QA/Audit). It enforces rigorous specification-driven development (SDD), anti-bloat minimalism via the **Ponytail Engine**, strict anti-deadlock review caps, and non-destructive provenance tracking.

---

## Phase 0: Fleet Bootstrap & Governance Setup

### 1. Step 0: Non-Blocking Engine Verification & Fleet Discovery
Before assigning tasks, execute or consult the bootstrap script:

*   **Helper Script**: [bootstrap.sh](./scripts/bootstrap.sh)
*   **Action**: Execute `./scripts/bootstrap.sh` to probe local runtimes, inspect `~/.config/delegate-skills`, and discover available CLIs (`opencode`, `claude`, `codex`, `gemini`, `gh`).
*   **Non-Blocking Guarantee**: If script execution is restricted or if external CLIs are absent, the orchestrator **must not halt**. Instead, it seamlessly activates the **3-Tier Scarcity Cascade**.

### 2. The 3-Tier Scarcity Resolution Cascade
The orchestrator determines the execution engine based on environment capabilities:

```
[Tier 1: Full Fleet Discovery]
Detected external CLIs (e.g., OpenCode, Claude, Codex, Gemini)
       │ (if unavailable)
       ▼
[Tier 2: Native Agent Platform Subagents]
Antigravity subagents invoked with lane-specific role prompts and workspaces
       │ (if subagents restricted)
       ▼
[Tier 3: In-Process Synthetic Multi-Persona Emulation]
Sequential role-based reasoning passes within the single agent context
```

### 3. Governance Artifacts Initialization
Create or verify the governance directory (default: `.agents/`, fallback: workspace root):
*   [AGENTS.template.md](./resources/templates/AGENTS.template.md) $\rightarrow$ `.agents/AGENTS.md`
*   [AI_HANDOFF_LEDGER.template.md](./resources/templates/AI_HANDOFF_LEDGER.template.md) $\rightarrow$ `.agents/AI_HANDOFF_LEDGER.md`

---

## Phase 1: Zero-Presumption Audit & Spec Formulation

Do not write implementation code until the specification and architectural audit are complete.

### 1. Dynamic Domain Pack Selection
Inspect the codebase and task context to activate the corresponding domain pack (see [domain_packs.md](./references/domain_packs.md)):
*   **Clinical / Healthcare / SaMD**: Activated if medical, clinical, patient, dosage, or WHO terminology is present. Enforces IEC 62304, zero unit-coercion, and PHI isolation.
*   **FinTech & Payments**: Activated if payment, ledger, or transaction terms are present. Enforces decimal precision, idempotency, and double-entry rules.
*   **Systems & High-Performance**: Activated for low-level systems (Rust, C++, Go). Enforces RAII, lock hierarchies, and zero-allocation critical loops.
*   **Core Engineering / Fullstack**: Default mode for web, mobile, and backend services. Enforces WCAG 2.1 AA a11y, OWASP security, and responsive layouts.

### 2. Produce `SPEC_AND_AUDIT.md`
Synthesize the audit into `.agents/SPEC_AND_AUDIT.md` using [SPEC_AND_AUDIT.template.md](./resources/templates/SPEC_AND_AUDIT.template.md):
1.  **Existing Codebase Fragilities**: Document exact line numbers of flaws, anti-patterns, and bottlenecks.
2.  **Target Interface Contracts**: Define exact DTOs, function signatures, and state flows.
3.  **Verification Criteria**: Formulate testable pass/fail metrics.

---

## Phase 2: Fleet Lane Partitioning & Work Breakdown

The orchestrator partitions work into atomic, decoupled tasks documented in `.agents/PLAN_TASKS.md`:

```
                 ┌────────────────────────────────┐
                 │ Antigravity Fleet Orchestrator │
                 └───────────────┬────────────────┘
         ┌───────────────┬───────┴───────┬───────────────┐
         ▼               ▼               ▼               ▼
   [ UI Lane ]   [ Core Logic ]    [ Data Lane ]   [ QA / Audit ]
   - Ergonomics   - Algorithms     - Schemas       - Full-Repo
   - A11y / CSS   - Concurrency    - Migrations    - Security
   - Interactions - Room / SQL     - L10n bounds   - Reg. Checks
```

### Lane Assignment Guidelines:
*   **UI Lane**: Focuses on view trees, design systems, responsive layouts, accessibility, and user interaction states.
*   **Core Logic Lane**: Focuses on business rules, algorithms, concurrency, state stores, and computation.
*   **Data Lane**: Focuses on schemas, data serializations, validation boundaries, and migrations. *(Note: RTL/L10n data contracts belong here; visual RTL mirroring belongs to the UI Lane).*
*   **QA & Audit Lane**: Full-repo synthesis, security surface audit, edge-case testing, and domain compliance verification.

---

## Phase 3: Delegated Execution & The Ponytail Engine

### 1. The 7-Rung Ponytail Minimalism Protocol
Every lane must consult [ponytail_ladder.md](./references/ponytail_ladder.md) before writing code:
1.  **YAGNI**: Cut speculative parameters, premature abstractions, and unused flags.
2.  **Existing Helper**: Reuse existing repo functions and styles.
3.  **Standard Library**: Prefer native language primitives over external micro-libraries.
4.  **Native Platform / OS**: Leverage platform APIs (CSS grid, Android insets, native browser events).
5.  **Pre-Installed Dependency**: Do not add new packages if an installed package suffices.
6.  **Atomic Functional Primitive**: Write clean, readable, single-responsibility functions. *Do not write obfuscated one-liners.*
7.  **Minimum High-Performance Custom**: Use bespoke optimizations only when benchmarked bottlenecks require it.

> [!IMPORTANT]
> **Safety Over Minimalism**: The Ponytail Engine strictly forbids cutting input validation, error handling, security checks, accessibility labels, or clinical/financial precision.

### 2. Peer Review & Anti-Infinite-Critique Protocol
To prevent endless review loops:
*   **Capped at 2 Rounds**: A code block or PR may undergo at most **2 review cycles**.
*   **Strict Classification**:
    *   **Hard Blocker**: Security vulnerability, data loss risk, regression, missing validation, or domain hazard. *Must be resolved immediately by the implementing lane.*
    *   **Deferred Shortcut**: Optimization, cosmetic styling, or non-critical refactoring. *Tagged as `// ponytail: <path>` and logged in `.agents/AI_HANDOFF_LEDGER.md` under Ponytail Debt.*
*   **Antigravity Supreme Arbiter Clause**: If lanes disagree after Round 2 (e.g., cross-lane blame), the orchestrator immediately steps in, issues a definitive verdict, and writes the resolving patch directly.

---

## Phase 4 & 5: Platform Stress Testing & Final Commit

### 1. Cross-Platform Stress Verification
1.  Run build and static analyzers:
    *   `dart analyze` / `npm run lint` / `cargo check` / `mvn test`.
2.  Verify edge cases identified in `SPEC_AND_AUDIT.md`.
3.  Ensure zero lint warnings introduced by governance comments.

### 2. Non-Destructive Provenance
*   **Do NOT inject unparsed header comments** (e.g., `// @AI-Implementer`) into source files where it violates project style guides, license header linters, or non-commentable formats (JSON, YAML).
*   **Record all provenance** cleanly in `.agents/AI_HANDOFF_LEDGER.md` and use standard git trailers:
    ```git
    git commit -m "feat(auth): implement token refresh rotation

    Co-authored-by: Core-Logic-Lane <core-logic@agent.local>
    X-AI-Lane: Core-Logic
    X-Audited-By: Antigravity-Orchestrator"
    ```

### 3. Final Verification Checklist
Before concluding, the orchestrator verifies:
- [ ] `./scripts/bootstrap.sh` or fallback was executed.
- [ ] `.agents/SPEC_AND_AUDIT.md` reflects true zero-presumption findings.
- [ ] `.agents/PLAN_TASKS.md` tasks were completed by their designated lanes.
- [ ] Ponytail Ladder was honored; no bloat or obfuscated code introduced.
- [ ] Hard blockers resolved; deferred shortcuts documented in `AI_HANDOFF_LEDGER.md`.
- [ ] All tests and linters pass cleanly.
