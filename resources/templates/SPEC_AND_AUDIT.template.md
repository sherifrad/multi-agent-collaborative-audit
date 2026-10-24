# Specification & Zero-Presumption Audit (SPEC_AND_AUDIT.md)

## 1. Executive Summary & Problem Statement
* **Objective**: `[Detailed description of what needs to be implemented or fixed]`
* **Scope**: `[In-scope modules and out-of-scope boundaries]`
* **Active Domain Pack**: `[Core Engineering | Clinical/SaMD | FinTech | Systems]`
* **Linked Task Queue Item**: `[Reference ID in tasks/current_task.md or .agents/PLAN_TASKS.md]`

---

## 2. Zero-Presumption Architectural & Call-Chain Audit
*Conduct a rigorous audit of the existing codebase. Do not assume any component works as intended without verification.*

* **Existing Implementations**: `[List of files and functions reviewed with exact line numbers]`
* **Discovered Defects & Fragilities**: `[Bugs, silent truncation, memory leaks, missing validations]`
* **Cross-Function Call-Chain Map**:
  | Target Function / Method | Upstream Callers (UI / ViewModels / Routes) | Downstream Callees (Validators / Evaluators / DAOs) | Parameter & Unit Contract Risks |
  | :--- | :--- | :--- | :--- |
  | `[e.g., recordObservation()]` | `[BedsideEntrySheet, QuickFhrSheet]` | `[InputValidator, LcgAlertEvaluator, ObservationDao]` | `[Ensure integer tenths used across all callers]` |
* **Security & Regulatory Hazards**: `[OWASP risks, PHI/PII leakage, missing auth]`

---

## 3. The Target Specification
* **Component / Interface Contracts**: `[Exact TypeScript / Kotlin / Dart / Python signatures]`
* **State Management & Data Flow**: `[Unidirectional state flow diagram or description]`
* **Offline-First & Handoff Lifecycle Contract**: `[Differentiate Session Handoff vs Account Wipe; preserve active alerts and due times across shift handoff]`
* **Error Handling & Failure Modes**: `[How every edge case is handled and reported without false-success states]`
* **Accessibility & UX Requirements**: `[Focus management, contrast, keyboard traps, tap targets >= 48dp]`

### 3.1 Visual Mockup & UX Contract (Phase 1.5 Approval Gate)
* **Design Lead**: `[Claude 3.5 Sonnet (Default) | Gemini / Antigravity Generative UI | Local/Other]`
* **Mock Artifact Path**: `[.agents/mocks/<feature>-mock.html or svg]`
* **User Approval Status**: `[PENDING | APPROVED | REJECTED]`
* **Narrow-Screen & Bedside Verification**: `[Verified on 360dp / 320dp widths, glove-friendly touch targets >= 48dp]`

---

## 4. Phase 4 Dedicated E2E, Sequential Scenario & 3-Layer Oracle Matrix

* **Selected Scenario Mode**: `[Mode A: Predefined Suite | Mode B: AI-Proposed Imaginary Scenarios | Mode C: User Custom Timeline]`
* **Fast-Forward Baseline Intake Seed**: `[e.g., Patient Name: "Sara", Parity: Nulliparous, Admitted: 10:00 (Pre-seeded to save time)]`
* **Sequential Step-by-Step Verification Matrix (Zero Bulk Mocks Allowed)**:

| Scenario / Step ID | Sequential Stimulus ($T_0 \to T_{+1\text{h}} \to T_{+2\text{h}}$) | Call-Chain Path Exercised (No Internal Mocks) | Logical / Domain Oracle | Persistence (DB) Oracle | Visual (UI / Handoff) Oracle |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `E2E-SEQ-01` | **Step 1 ($10:00$)**: Enter Dilatation `6 cm`, FHR `140`, Contractions `6/10m (45s)` $\rightarrow$ Save.<br/>**Step 2 ($10:30$)**: Enter FHR `105`, Decel `LATE`, Contractions `6/10m (50s)` $\rightarrow$ Save.<br/>**Step 3**: Reload & open Case Handoff. | `BedsideEntryVM` $\rightarrow$ `Validator` $\rightarrow$ `RoomTransaction` $\rightarrow$ `LcgAlertEvaluator` $\rightarrow$ `PartogramVM` & `HandoffVM` | Step 1 emits `PROVISIONAL` contraction recheck; Step 2 transitions to `CONFIRMED` + `WHO-LCG-ALERT-005/006`. | 2 sequential `ObservationBundle` rows committed with exact `observedAt` & `enteredAt`; zero overwrite of Step 1. | Step 1 shows amber recheck badge; Step 2 renders red `105` & `L` badges on matrix + top Handoff alert banner. |
| `NEG-CTRL-01` | Enter out-of-range FHR (`300 bpm`) or non-chronological timestamp. | `BedsideEntryVM` $\rightarrow$ `ClinicalInputValidator` | Returns typed `DATA_QUALITY` validation error; zero signals emitted. | Transaction blocked; database row count unchanged. | Inline validation error displayed; Save button shows no false-success toast. |
