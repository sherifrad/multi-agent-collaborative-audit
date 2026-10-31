# Clinical pack: extra spec and ledger sections (moved out of the core templates)

Copy these into SPEC_AND_AUDIT.md / the ledger only when the profile loads the clinical pack.

## Spec section: sequential scenario and 3-layer oracle matrix
## 4. Phase 4 Dedicated E2E, Sequential Scenario & 3-Layer Oracle Matrix

* **Selected Scenario Mode**: `[Mode A: Predefined Suite | Mode B: AI-Proposed Imaginary Scenarios | Mode C: User Custom Timeline]`
* **Fast-Forward Baseline Intake Seed**: `[e.g., Patient Name: "Sara", Parity: Nulliparous, Admitted: 10:00 (Pre-seeded to save time)]`
* **Sequential Step-by-Step Verification Matrix (Zero Bulk Mocks Allowed)**:

| Scenario / Step ID | Sequential Stimulus ($T_0 \to T_{+1\text{h}} \to T_{+2\text{h}}$) | Call-Chain Path Exercised (No Internal Mocks) | Logical / Domain Oracle | Persistence (DB) Oracle | Visual (UI / Handoff) Oracle |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `E2E-SEQ-01` | **Step 1 ($10:00$)**: Enter Dilatation `6 cm`, FHR `140`, Contractions `6/10m (45s)` $\rightarrow$ Save.<br/>**Step 2 ($10:30$)**: Enter FHR `105`, Decel `LATE`, Contractions `6/10m (50s)` $\rightarrow$ Save.<br/>**Step 3**: Reload & open Case Handoff. | `BedsideEntryVM` $\rightarrow$ `Validator` $\rightarrow$ `RoomTransaction` $\rightarrow$ `LcgAlertEvaluator` $\rightarrow$ `PartogramVM` & `HandoffVM` | Step 1 emits `PROVISIONAL` contraction recheck; Step 2 transitions to `CONFIRMED` + `WHO-LCG-ALERT-005/006`. | 2 sequential `ObservationBundle` rows committed with exact `observedAt` & `enteredAt`; zero overwrite of Step 1. | Step 1 shows amber recheck badge; Step 2 renders red `105` & `L` badges on matrix + top Handoff alert banner. |
| `NEG-CTRL-01` | Enter out-of-range FHR (`300 bpm`) or non-chronological timestamp. | `BedsideEntryVM` $\rightarrow$ `ClinicalInputValidator` | Returns typed `DATA_QUALITY` validation error; zero signals emitted. | Transaction blocked; database row count unchanged. | Inline validation error displayed; Save button shows no false-success toast. |

## Ledger section: sequential E2E report
## 3. Phase 4 Dedicated Sequential E2E & 3-Layer Outcome Verification Report

* **Scenario Mode Selected**: `[Mode A: Predefined Suite | Mode B: AI-Proposed Imaginary Scenarios | Mode C: User Custom Sequence]`
* **Fast-Forward Baseline Intake Used**: `[YES (Header only) / NO]`
* **Anti-Bulk-Mock Compliance**: `VERIFIED — All time-series observations entered sequentially step by step (T0 -> Save -> T+1h -> Save -> Reload)`
* **Zero-Internal-Mock Call-Chain Path**: `[e.g., UI Action -> ViewModel -> Validator -> Evaluator -> Room/Dexie DB -> Rehydration -> Matrix/Handoff]`
* **3-Layer Intended Outcome Oracle Results**:
  1. *Logical / Domain Oracle*: `[Exact ruleId, signal state, and progression math verified — PASS/FAIL]`
  2. *Persistence / DB Oracle*: `[Exact rows, scaled integers, and audit lineage verified — PASS/FAIL]`
  3. *Visual / UI & Narrow-Screen Oracle*: `[Exact badges, labels, Handoff summary, and 320dp/360dp layout verified — PASS/FAIL]`
  4. *Negative-Control & Boundary Proof*: `[Just-below boundary and invalid input blocked cleanly — PASS/FAIL]`
* **Task Queue Check-Off (`current_task.md`)**: `[Checked off [x] with command & date evidence]`

---

## 4. Phase 4.5 Deep Diagnostics & Production Verification Report (On-Demand)

* **User Consent Granted**: `[YES / NO / SKIPPED]`
* **Available Testing Skills Discovered**: `[e2e, playwright, android-profiler, android-cli, firebase-crashlytics, testing-setup]`
* **Pillar A (Runtime & Logcat)**: `[Silent exceptions, StrictMode, Coroutine lifecycles - PASS/FAIL]`
* **Pillar B (Memory & Jank)**: `[Choreographer frame drops, Heap allocations, Touch targets - PASS/FAIL]`
* **Pillar C (Crashlytics & Telemetry)**: `[Mapping file upload, Non-fatal logging, Zero-PII HIPAA - PASS/FAIL]`
* **Pillar D (Full Cached E2E Replay)**: `[All longitudinal E2E scenarios replayed cleanly - PASS/FAIL]`
* **Production Release Clearance**: `[CLEARED FOR RELEASE / BLOCKED]`

---

## 5. Ponytail Debt & Deferred Shortcuts Ledger

Log all deferred optimizations tagged with `// ponytail: <upgrade path>` here to ensure long-term visibility without blocking immediate delivery:

| Debt ID | File & Line | Ponytail Rung | Description & Justification | Target Milestone |
| :--- | :--- | :--- | :--- | :--- |
| `D-001` | `src/auth/token.ts#L42` | Rung 3 (stdlib) | Basic in-memory token cache used. Deferring Redis client until scale demands it. | v2.1 |
