# Specification & Zero-Presumption Audit (SPEC_AND_AUDIT.md)

## 1. Executive Summary & Problem Statement
* **Objective**: `[Detailed description of what needs to be implemented or fixed]`
* **Scope**: `[In-scope modules and out-of-scope boundaries]`
* **Active Domain Pack**: `[Core Engineering | Clinical/SaMD | FinTech | Systems]`

---

## 2. Zero-Presumption Architectural Audit
*Conduct a rigorous audit of the existing codebase. Do not assume any component works as intended without verification.*

* **Existing Implementations**: `[List of files and functions reviewed]`
* **Discovered Defects & Fragilities**: `[Bugs, memory leaks, missing validations]`
* **Performance & Hotspots**: `[Bottlenecks, unbounded queries, layout thrashing]`
* **Security & Regulatory Hazards**: `[OWASP risks, PHI/PII leakage, missing auth]`

---

## 3. The Target Specification
* **Component / Interface Contracts**: `[Exact TypeScript / Kotlin / Dart / Python signatures]`
* **State Management & Data Flow**: `[Unidirectional state flow diagram or description]`
* **Error Handling & Failure Modes**: `[How every edge case is handled and reported]`
* **Accessibility & UX Requirements**: `[Focus management, contrast, keyboard traps, tap targets]`

### 3.1 Visual Mockup & UX Contract (Phase 1.5 Approval Gate)
* **Design Lead**: `[Claude 3.5 Sonnet (Default) | Gemini / Antigravity Generative UI | Local/Other]`
* **Mock Artifact Path**: `[docs/mocks/<feature>-mock.html or svg]`
* **User Approval Status**: `[PENDING | APPROVED | REJECTED]`
* **User Feedback / Adjustments**: `[User comments or signed-off state before task breakdown]`

---

## 4. Verification & Testing Matrix
| Test Case ID | Description | Target Lane | Verification Method | Pass Criteria |
| :--- | :--- | :--- | :--- | :--- |
| `TC-01` | Validate empty array input | Data Lane | Unit Test | Returns empty response, status 200 |
| `TC-02` | Screen reader focus announcement | UI Lane | Accessibility Audit | Semantic label read cleanly |
