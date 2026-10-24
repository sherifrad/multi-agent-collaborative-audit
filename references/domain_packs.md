# Dynamic Domain Audit Packs

The orchestrator dynamically selects and applies domain-specific audit rules during **Phase 1 (Zero-Presumption Audit)** and **Phase 4 (Dedicated E2E, Sequential Scenario & Call-Chain Verification)**.

---

## 1. Core Engineering & Fullstack Pack (Default)
*Activated for general web, mobile, desktop, backend, and cloud projects.*

* **UI Lane Focus**:
  * Responsive layout stability (no layout shifts, CWV compliance).
  * WCAG 2.1 AA accessibility (keyboard focus indicators, screen reader labels, contrast ratio >= 4.5:1).
  * Performance: lazy rendering, image optimization, avoid unbounded lists.
* **Core Logic Lane Focus**:
  * Algorithmic time/space complexity (avoid $O(N^2)$ inside loops or hot paths).
  * Concurrency safety (thread locks, race conditions, cancellation tokens).
  * Cross-function call-chain consistency across all callers.
* **Data Lane Focus**:
  * Strict schema types, non-nullable defaults, migration backward-compatibility.
  * Input sanitization, parameter validation, and round-trip persistence fidelity.
  * Internationalization: RTL mirroring, UTF-8 unicode normalization.
* **QA & E2E Audit Lane Focus**:
  * OWASP Top 10 vulnerabilities (SQLi, XSS, SSRF, IDOR).
  * Sequential E2E user journeys and boundary value testing.

---

## 2. Clinical, Healthcare & SaMD Pack
*Activated automatically if keywords like `patient`, `vital`, `dosage`, `clinical`, `partogram`, `labour`, `ehr`, `fhir`, `dicom`, `triage`, `medical`, or `health` are detected in the repository or task description.*

* **Regulatory & Safety Baseline**:
  * **IEC 62304 / ISO 14971**: Software safety classification and risk management.
  * **WHO Clinical Guidelines & Local Protocols (e.g., WHO LCG / EHC / FIGO)**: Verify diagnostic/therapeutic reference values against established medical literature.
  * **FDA SaMD Guidance**: Clinical evaluation, algorithm transparency, and strict separation of reference highlights vs. diagnostic/therapeutic claims.
* **Clinical Lane Mandatory Checks**:
  * **Dosage & Unit Integrity**: Strict scaled-integer unit typing (e.g., `dilatationTenths`, `temperatureTenthsCelsius`, `mg` vs `mcg` vs `mL` with zero implicit `Float.toInt()` truncation or binary float coercion).
  * **Sequential Longitudinal Verification (Anti-Bulk-Mock Rule)**:
    - Clinical rules that depend on time progression (such as cervical arrest lag thresholds, repeat blood pressure confirmation 15–30m apart, or consecutive 10-minute contraction windows) **must never** be verified solely via static pre-built snapshots.
    - Phase 4 tests must fast-forward only the static patient header (`Name`, `Age`, `Parity`, `Admission Time`) and enter time-series observations sequentially step by step ($T_0 \to T_{+1\text{h}} \to T_{+2\text{h}} \to T_{+5\text{h}}$) through the real save and re-evaluation pipeline.
  * **Shift & Case Handoff Integrity (تسليم الحالات - Case Handoff)**:
    - Shared tablet support: Delivery ward tablets and mobile devices are shared across shifts.
    - Structured Handoff Verification: E2E tests must verify that handing off an active case preserves and prominently surfaces: (1) current labour stage and progression clock, (2) latest cervical/fetal/maternal observations, (3) all active or unacknowledged clinical alerts (`IMMEDIATE_SAFETY_ACTION`, `WHO_REFERENCE`, `EHC_SPECIALIST_REVIEW`), (4) next monitoring/reassessment due times (`MONITORING_DUE`), and (5) explicit audit attribution of the outgoing and incoming clinicians.
    - Session vs Account distinction: Clinical session handoff/logout must **never** wipe persisted patient records, audit trails, or offline credential vaults.
  * **Owner Broadcast / Senior Guidance Zone vs. Clinical Alerts Separation**:
    - When the application includes a dedicated zone for Owner/Senior Clinician clarifications, notes, or broadcasts to the medical team, E2E verification must confirm:
      1. **Visual & Semantic Isolation**: Owner announcements render in their dedicated guidance container and never mimic, overwrite, or obscure patient-specific clinical alerts (`ActiveAlertQueue`).
      2. **Zero Bedside Friction**: Viewing or dismissing an owner announcement never blocks or delays the `<15s` rapid bedside observation entry workflow.
  * **Bedside Ergonomics & Narrow Screens**:
    - Glove-friendly inputs: Primary steppers and quick-select chips with $\ge 48\text{dp}$ touch targets.
    - Narrow-screen resilience: Test against $320\text{dp}$ and $360\text{dp}$ viewports to prevent vital sign clipping or horizontal truncation.
  * **HIPAA / GDPR Health Data & Audit Logging**:
    - No PHI/PII in log files, crash reports, or analytics payloads.
    - Immutable, append-only (`CURRENT`, `CORRECTED`, `ENTERED_IN_ERROR`) tamper-evident audit logs for every action affecting patient state.

---

## 3. FinTech, Payments & High-Security Pack
*Activated automatically if keywords like `payment`, `ledger`, `crypto`, `wallet`, `pci`, `stripe`, `plaid`, `bank`, `invoice`, or `transaction` are detected.*

* **Compliance & Financial Safety**:
  * **PCI-DSS & SOC-2**: Tokenization of card data, zero raw card persistence.
  * **Exact Decimal Precision**: Disallow IEEE-754 binary floating-point math for currency (use arbitrary-precision `Decimal` / `BigInt` / cents).
  * **Idempotency**: All payment and transfer mutations must require UUIDv4 idempotency keys.
  * **Double-Entry Bookkeeping**: Sum of debits must equal sum of credits at every transaction boundary.

---

## 4. Systems, Embedded & High-Performance Pack
*Activated automatically for C, C++, Rust, Zig, Go kernel/runtime, and low-level graphics/audio projects.*

* **Memory & Lifecycle Safety**:
  * Zero memory leaks, zero double-free, zero use-after-free.
  * Deterministic destructors / RAII lifecycle enforcement.
  * Allocation bounds: avoid heap allocations in audio threads or render loops.
* **Signal & Thread Safety**:
  * Deadlock avoidance via lock ordering hierarchies.
  * Graceful shutdown on SIGTERM / SIGINT with atomic flag checks.
