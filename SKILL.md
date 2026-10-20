---
name: multi-agent-collaborative-audit
description: >-
  DEFAULT master orchestration and audit protocol for all coding, software architecture,
  UI/UX design, debugging, refactoring, and verification tasks. Automatically triggers on
  any non-trivial engineering request to coordinate delegate-skills (claude-delegate,
  opencode-delegate, codex-delegate, agy-delegate), enforce the 5-Phase SDD workflow,
  Phase 1.5 Visual Approval Gate, 7-Rung Ponytail minimalism, Rule 6 Tabula Rasa adversarial
  diff audits, 3-tier scarcity fallback (including Single-Model Multi-Session isolation),
  and Phase 4.5 deep low-level diagnostics.
---

# Universal Spec-Driven, Ponytail & Fleet-Delegated Multi-Agent Skill

This skill is the **Default Principal Consultant & Fleet Orchestrator** managing a collaborative team of specialized agent lanes (UI/UX, Core Logic, Data, QA/Audit). It enforces specification-driven development (SDD), anti-bloat minimalism via the **Ponytail Engine**, strict anti-deadlock review caps, and non-destructive provenance tracking.

---

## Phase 0: Fleet Bootstrap, Delegate Skills & Scarcity Cascade

### 1. Step 0: Non-Blocking Engine Verification & Fleet Discovery
Before assigning tasks, execute or consult the bootstrap script:

*   **Helper Script**: [bootstrap.sh](./scripts/bootstrap.sh)
*   **Action**: Execute `./scripts/bootstrap.sh` to probe local runtimes, inspect `~/.config/delegate-skills` and `~/.agents/skills/*-delegate`, discover available CLIs (`opencode`, `claude`, `codex`, `gemini`, `gh`), and check diagnostic skills (`android-profiler`, `android-cli`, `firebase-crashlytics`, `testing-setup`).
*   **Non-Blocking Guarantee**: Never assume all external models or CLIs exist. If any CLI or model is missing, seamlessly cascade through the **3-Tier Scarcity Resolution Cascade**.

### 2. The 3-Tier Scarcity Resolution Cascade
The orchestrator dynamically adapts to the host environment without failing:

```
[Tier 1: Delegate-Skills & External CLI Fleet]
Dispatches tasks via file-based relay scripts:
• claude-delegate   ➔ UI/UX & Graphic Mocking Lane
• opencode-delegate ➔ Core Logic (DeepSeek) & Data (GLM) Lanes
• codex-delegate    ➔ Systems / Algorithmic Lane
• agy-delegate      ➔ Independent Read-Only QA & Audit Lane
       │ (if external CLIs or delegate relays are unavailable)
       ▼
[Tier 2: Native Agent Platform Subagents]
Spawns isolated subagents (via invoke_subagent) in separate workspaces/branches,
each bound to a dedicated lane persona and strict Tabula Rasa scope.
       │ (if only a single model is available without subagents)
       ▼
[Tier 3: Single-Model Multi-Session Tabula Rasa Isolation]
Uses the single available model across separate sessions or strict context resets:
• Session A (Implementer): Writes the bounded code slice and outputs raw git diff.
• Session B (Adversarial Auditor): Starts with a clean Tabula Rasa prompt containing
  ONLY the user requirement and the git diff (zero access to Session A's reasoning),
  performing an unbiased Rule 6 bug hunt.
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

### 3. Phase 1.5: UI/UX & Graphic Mocking (User Approval Gate)
Whenever a task introduces or alters user interfaces (Mobile views, Web pages, Dashboards, Vector icons):
1.  **Default Model Routing**: Assigned by default to **Claude Agent / Claude 3.5 Sonnet** for superior spatial reasoning, modern aesthetics, and CSS/Compose ergonomics. If Claude is unavailable, cascades to **Gemini / Antigravity** (`generative_ui` / SVG), then to the best available local model. (See [ui_ux_mocking.md](./references/ui_ux_mocking.md)).
2.  **Mock Artifact Generation**: The UI/UX Lane creates a standalone interactive visual mockup (saved to `.agents/mocks/<feature_slug>.html` or `.svg`).
3.  **User Presentation & Review**: The orchestrator presents the rendered preview and file path to the user for evaluation.
4.  **Mandatory Approval Gate**: The fleet **must not** proceed to Phase 2 task breakdowns or logic implementation until the user explicitly reviews and approves the mock.
5.  **Visual Contract Binding**: The approved mock path is locked into `.agents/SPEC_AND_AUDIT.md` as the definitive visual specification.

---

## Phase 2: Fleet Lane Partitioning & Work Breakdown

The orchestrator partitions work into atomic, decoupled tasks documented in `.agents/PLAN_TASKS.md`, referencing the approved UI/UX mock:

```
                 ┌────────────────────────────────┐
                 │ Antigravity Fleet Orchestrator │
                 └───────────────┬────────────────┘
         ┌───────────────┬───────┴───────┬───────────────┐
         ▼               ▼               ▼               ▼
   [ UI/UX Lane ]  [ Core Logic ]  [ Data Lane ]   [ QA / Audit ]
   - Claude (Def.) - DeepSeek      - GLM           - Gemini
   - Visual Mocks  - Algorithms    - Schemas       - Full-Repo
   - User Sign-Off - Concurrency   - Migrations    - Security
   - Ergonomics    - Room / SQL    - L10n bounds   - Reg. Checks
```

### Lane Assignment Guidelines:
*   **UI/UX & Graphic Design Lane (Claude Sonnet default, fallback: Gemini/Antigravity)**: Focuses on visual mockups, design systems, responsive layouts, accessibility (WCAG 2.1 AA), vector icons, and user interaction states.
*   **Core Logic Lane (OpenCode DeepSeek default)**: Focuses on business rules, algorithms, concurrency, state stores, and computation.
*   **Data Lane (OpenCode GLM default)**: Focuses on schemas, data serializations, validation boundaries, and migrations. *(Note: RTL/L10n data contracts belong here; visual RTL mirroring belongs to the UI Lane).*
*   **QA & Audit Lane (Gemini default)**: Full-repo synthesis, security surface audit, edge-case testing, and domain compliance verification.

---

## Phase 3: Delegated Execution & The Ponytail Engine

### 1. The 7-Rung Ponytail Minimalism Protocol & Coding Guidelines
Every lane must consult both [ponytail_ladder.md](./references/ponytail_ladder.md) and [coding_guidelines.md](./references/coding_guidelines.md) before writing code:
1.  **Idiomatic Code & Clean Architecture**: Follow language conventions (Kotlin/Compose, TypeScript, Python) strictly: UDF state hoisting, immutability, explicit typing, zero empty catches, and clear package boundaries (`ui`, `data`, `domain`).
2.  **YAGNI**: Cut speculative parameters, premature abstractions, and unused flags.
3.  **Existing Helper**: Reuse existing repo functions and styles.
4.  **Standard Library**: Prefer native language primitives over external micro-libraries.
5.  **Native Platform / OS**: Leverage platform APIs (Compose insets, Android Keystore, native browser events).
6.  **Pre-Installed Dependency**: Do not add new packages if an installed package suffices.
7.  **Atomic Functional Primitive**: Write clean, readable, single-responsibility functions. *Do not write obfuscated one-liners.*
8.  **Minimum High-Performance Custom**: Use bespoke optimizations only when benchmarked bottlenecks require it.

> [!IMPORTANT]
> **Safety Over Minimalism**: The Ponytail Engine strictly forbids cutting input validation, error handling, security checks, accessibility labels, or clinical/financial precision.

### 2. Cross-Model Adversarial Diff Audit & Anti-Infinite-Critique Protocol
To ensure rigorous bug hunting while preventing endless review loops:
*   **Zero-Presumption Tabula Rasa**: The reviewing model lane must evaluate the git diff and the original user requirement as if reading them for the very first time. **Do not inherit the implementing model's assumptions or rationales.** Reviewers must first understand *why* the requirement exists, question the fundamental architecture/logic chosen, and actively probe for failure modes.
*   **Mandatory Bug Hunt Scope**:
    1. *Regressions & State Hazards*: Unhandled nulls, concurrency race conditions, memory leaks, or broken component lifecycles.
    2. *Domain & Localization Boundary Leaks*: Untranslated hardcoded strings, broken bidirectional text (RTL/LTR), or accidental corruption of protected domains (e.g. Clinical references, patient names, legal disclaimers, or standardized export formats).
    3. *Visual & Responsive Deficiencies*: Text clipping, truncation, overlapping cards on narrow viewports (320dp/360dp), and missing touch targets (< 48dp).
    4. *Accessibility (a11y) & Usability*: Missing screen-reader semantics, broken keyboard/IME navigation.
*   **Capped at 2 Rounds**: A code block or PR may undergo at most **2 review cycles**.
*   **Strict Classification**:
    *   **Hard Blocker**: Security vulnerability, data loss risk, regression, missing validation, or domain hazard. *Must be resolved immediately by the implementing lane.*
    *   **Deferred Shortcut**: Optimization, cosmetic styling, or non-critical refactoring. *Tagged as `// ponytail: <path>` and logged in `.agents/AI_HANDOFF_LEDGER.md` under Ponytail Debt.*
*   **Antigravity Supreme Arbiter Clause**: If lanes disagree or deadlock after Round 2 (e.g., cross-lane blame), the orchestrator immediately steps in, issues a definitive binding verdict, and writes the resolving patch directly.

### 3. Fast-Path Hotfix Protocol (Trivial Task Bypass)
To avoid unnecessary latency and token expenditure on trivial changes:
*   **Eligibility**: 1-file typo fixes, documentation grammar, single CSS color tweaks, or dependency patch bumps.
*   **Fast-Path Action**: The orchestrator directly implements the patch, skips full multi-lane SDD breakdown, verifies static analysis, and commits with standard audit trailers without generating extensive multi-page specs.

---

## Phase 4 & 5: Platform Stress Testing, Deep Diagnostics & Final Commit

### 1. Cross-Platform Stress Verification
1.  Run build and static analyzers:
    *   `dart analyze` / `npm run lint` / `cargo check` / `mvn test` / `./gradlew test`.
2.  Verify edge cases identified in `SPEC_AND_AUDIT.md`.
3.  **Narrow-Screen & Responsive Guard**: For any UI or mobile alterations, run automated viewport tests or Robolectric suites at $320\text{dp}$ and $360\text{dp}$ to verify zero text clipping, zero button overflow, and proper IME keyboard dismissal.
4.  Ensure zero lint warnings introduced by governance comments.

### 2. Phase 4.5: Deep Release Verification Gate (On-Demand Diagnostics)
Prior to final stable release tagging or production deployment, the fleet can trigger an in-depth low-level audit.
*   **Mandatory User Consent Gate**: Because low-level diagnostics, heap profiling, and exhaustive log audits consume significant resources and tokens, the orchestrator **must ask the user for permission** before running Phase 4.5.
*   **Testing Skills & Plugins Pre-Flight Check**:
    1.  Probe environment for diagnostic skills: `android-profiler`, `android-cli`, `firebase-crashlytics`, `testing-setup`, `a11y-debugging`.
    2.  If missing, prompt the user with recommendations to install or enable the relevant skill/plugin.
    3.  Dynamically discover any project-specific testing tools (Playwright, Cypress, Flutter driver).
*   **Fleet Execution Pillars** (Detailed in [deep_diagnostics.md](./references/deep_diagnostics.md)):
    *   *Pillar A (Core Logic)*: ADB Logcat silent error hunt (`*:E`, `FATAL`, `runCatching` silences, `StrictMode` disk-on-main violations).
    *   *Pillar B (UI/UX)*: Memory leaks, heap allocation stability, `Choreographer` frame drop / jank analysis, touch target sanity.
    *   *Pillar C (QA/Audit)*: Firebase Crashlytics mapping upload, non-fatal exception wiring, zero-PII health data verification.
    *   *Pillar D (Data)*: Deep unit test assertion audit (identifying inverted assertions, test suite blind spots, boundary overflows).

### 3. Non-Destructive Provenance
*   **Do NOT inject unparsed header comments** (e.g., `// @AI-Implementer`) into source files where it violates project style guides, license header linters, or non-commentable formats (JSON, YAML).
*   **Record all provenance** cleanly in `.agents/AI_HANDOFF_LEDGER.md` and use standard git trailers:
    ```git
    git commit -m "feat(auth): implement token refresh rotation

    Co-authored-by: Core-Logic-Lane <core-logic@agent.local>
    X-AI-Lane: Core-Logic
    X-Audited-By: Antigravity-Orchestrator"
    ```

### 4. Telemetry, Competition Leaderboard & Performance Measurement
Run the telemetry engine to measure execution health and launch the evidence dashboard:
*   **Execution**: `./scripts/measure_metrics.py` (launches single-page web cockpit on `127.0.0.1:8420`).
*   **CLI / CI Mode**: `./scripts/measure_metrics.py --json` or `./scripts/measure_metrics.py --export-html report.html`.
*   **Scorecard Targets**: Simplicity Index $\ge 70\%$, Arbiter Escalations $\le 10\%$, First-Turn Pass $\ge 70\%$.
*   **Gamified Championship Leaderboard**: Maintain `.agents/MACA_TOURNAMENT_LEADERBOARD.md` (see [template](./resources/templates/MACA_TOURNAMENT_LEADERBOARD.template.md)) to award points across lanes for critical defect catches (+50 pts), state/concurrency fixes (+30 pts), narrow-screen/a11y catches (+20 pts), and deterministic test cases (+25 pts).

### 5. Final Verification Checklist
Before concluding, the orchestrator verifies:
- [ ] `./scripts/bootstrap.sh` or fallback was executed.
- [ ] `.agents/SPEC_AND_AUDIT.md` reflects true zero-presumption findings and offline-first lifecycle.
- [ ] `.agents/PLAN_TASKS.md` tasks were completed by their designated lanes (or Fast-Path applied).
- [ ] Phase 1.5 UI/UX mock was signed off by the user before coding (for UI tasks).
- [ ] Ponytail Ladder was honored; no bloat or obfuscated code introduced.
- [ ] Narrow-screen ($320\text{dp}$/$360\text{dp}$) responsive tests pass cleanly.
- [ ] Phase 4.5 Deep Diagnostics offered to user (and executed if approved).
- [ ] Hard blockers resolved; deferred shortcuts documented in `AI_HANDOFF_LEDGER.md`.
- [ ] Telemetry measured via `./scripts/measure_metrics.py` and leaderboard updated.
- [ ] All tests and linters pass cleanly.
