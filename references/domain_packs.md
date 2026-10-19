# Dynamic Domain Audit Packs

The orchestrator dynamically selects and applies domain-specific audit rules during **Phase 1 (Zero-Presumption Audit)** and **Phase 4 (Specialist Audit & Verification)**.

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
  * Resource cleanup (streams, listeners, database handles, sockets).
* **Data Lane Focus**:
  * Strict schema types, non-nullable defaults, migration backward-compatibility.
  * Input sanitization, parameter validation.
  * Internationalization: RTL mirroring, UTF-8 unicode normalization.
* **QA & Security Lane Focus**:
  * OWASP Top 10 vulnerabilities (SQLi, XSS, SSRF, IDOR).
  * Boundary value testing (empty arrays, integer overflow, extreme string lengths).

---

## 2. Clinical, Healthcare & SaMD Pack
*Activated automatically if keywords like `patient`, `vital`, `dosage`, `clinical`, `ehr`, `fhir`, `dicom`, `triage`, `medical`, or `health` are detected in the repository or task description.*

* **Regulatory & Safety Baseline**:
  * **IEC 62304 / ISO 14971**: Software safety classification and risk management.
  * **WHO Clinical Guidelines & Protocols**: Verify diagnostic/therapeutic reference values against established medical literature.
  * **FDA SaMD Guidance**: Clinical evaluation, algorithm transparency, and verification of non-diagnostic vs diagnostic claims.
* **Clinical Lane Mandatory Checks**:
  * **Dosage & Unit Integrity**: Strict unit typing (e.g., `mg` vs `mcg` vs `mL` with no implicit float coercion).
  * **Fail-Safe Fallbacks**: If network or sensor data drops, clinical UI must display explicit "STALE DATA" warnings rather than caching old vitals without timestamps.
  * **Offline-First Authentication & Shift Handovers**: 
    - Shared tablet support: Delivery ward tablets are shared by multiple clinicians across shifts.
    - Session vs Account distinction: Clinical logout (`clearSession`) must **never** wipe offline doctor credential vaults (`AccountStore`), preventing shift lockout during emergency power or internet outages.
    - Zero plain-text credentials in logs or Firestore documents.
  * **Bedside Ergonomics & Narrow Screens**:
    - Glove-friendly inputs: Primary steppers and presets with $\ge 48\text{dp}$ touch targets.
    - Narrow-screen resilience: Test against $320\text{dp}$ and $360\text{dp}$ viewports to prevent vital sign clipping or horizontal truncation.
    - Anti-Aesthetic Inflation: Avoid high-CPU animated blurs, pulsing waves, or glassmorphism that drain battery or distract under surgical lights.
  * **HIPAA / GDPR Health Data**: No PHI/PII in log files, crash reports, or analytics payloads. Encryption at rest and in transit (TLS 1.3).
  * **Audit Logging**: Immutable, tamper-evident audit logs for every user action affecting patient state or medical orders.

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
