# Dedicated E2E, Sequential Scenario, Geometric Layout & Call-Chain Verification Protocol (MACA v2)

> **Authoritative reference for Phase 4 of the MACA v2 Framework: Interactive Scenario Mode Selection, Fast-Forward Intake + Incremental Time-Series Entry, Cross-Function Call-Chain Auditing, Geometric Bounding-Box Oracles, and Tabula Rasa RBAC Fuzzing.**

---

## 1. Why Traditional AI Unit & Mock Tests Fail in Real Usage

AI coding agents frequently produce tests that pass `npm test` or `./gradlew test` with 100% green checkmarks while the actual application fails when used manually. This happens due to **five classic testing illusions**:

| Testing Illusion | What the AI Does Wrong | Why Manual Testing Breaks | MACA v2 Phase 4 Mandatory Fix |
| :--- | :--- | :--- | :--- |
| **1. The Bulk Mock Illusion (وهم الموك الكامل)** | Constructs a complete multi-hour case snapshot in memory (`observations = [h1, h2, h3, h4]`) and passes it all at once to the evaluator or UI renderer. | Entering `h1`, saving, reopening at `h2`, and saving mutates state incrementally. Bulk mocks completely skip intermediate state transitions, draft clears, lag-anchor resets, and DB rehydration bugs. | **Fast-Forward Intake + Strict Step-by-Step Sequential Entry**: Pre-seed only the static patient header, then dispatch each hourly observation one by one through the real save pipeline. |
| **2. The Vacuous Non-Error Pass (نجاح عدم وجود خطأ)** | Asserts `expect(res).toBeDefined()`, `status === 200`, or `not.toThrow()`. | The function catches or ignores an error and returns an empty/wrong clinical result without crashing. | **3-Layer Intended Outcome Oracle**: Assert exact Domain logic output + exact SQLite/IndexedDB persisted row + exact visible UI text/badge. |
| **3. The Isolated Unit Silo (عزلة الدوال عن بعضها)** | Tests `Function A` in isolation and `Function B` in isolation while mocking the connection between them. | `Function A` is called from 3 different screens (e.g., Bedside Entry, Partogram Matrix, Handoff Summary) with slightly different parameters or units, breaking in 2 of the 3 callers. | **Cross-Function Call-Chain & Multi-Caller Wiring Audit**: Trace every caller of a modified function and run zero-internal-mock integration flows across the full call chain. |
| **4. Semantic Tree Visual Escape (Defect D-1)** | Uses `assertExists()` or `assertIsDisplayed()` on TopBars or cards without checking layout geometry. | Adding an icon expands the action cluster (`~176dp`), choking or shifting the title on $360\text{dp}$ screens while `assertExists()` still passes. | **Upgrade 1 — Geometric & Multi-Viewport Layout Oracle**: Assert `getUnclippedBoundsInRoot()` non-overlap and minimum title flex width ($\ge 120\text{dp}$ on $320\text{dp}/360\text{dp}$). |
| **5. Happy-Path Identity Fragility (Defect D-2)** | Tests admin/clinician login with only one clean fixture (`username = "dr.sherif"`). | Real users enter their email in the username field, use uppercase/spaces, or attackers attempt `+alias` spoofing. | **Upgrade 2 — Tabula Rasa Auth & RBAC Fuzzing Matrix**: Run all 6 identity permutations (`--auth-fuzz-matrix`) against verified provider claims. |

---

## 2. Step 4.1: Interactive Test Scenario Mode Selection Gate

Before generating or running sequential E2E tests for a feature, the Orchestrator / QA Lane presents the user with **three structured options** (or executes the mode already chosen by the user):

```
┌────────────────────────────────────────────────────────────────────────────┐
│ 🧪 MACA v2 Phase 4: Select Your Sequential E2E Testing Mode                │
├────────────────────────────────────────────────────────────────────────────┤
│ [Mode A] Predefined Standard Suite (الاختبارات القياسية المُعدّة مسبقاً)    │
│   • Runs the built-in sequential E2E baseline, boundary thresholds,        │
│     6-row RBAC fuzz matrix, geometric bounds, and negative controls.       │
│                                                                            │
│ [Mode B] AI-Proposed Imaginary Scenarios (سيناريوهات تخيلية تختار منها)    │
│   • The AI proposes 3–4 realistic multi-hour clinical/domain scenarios     │
│     (e.g., Prolonged Labour, Fetal Deceleration, Pre-eclampsia Escalation, │
│     Shift Handoff) as a table of hourly inputs & expected alerts.          │
│   • You pick which scenario(s) to execute (or tweak any value).            │
│                                                                            │
│ [Mode C] User-Defined Custom Timeline (تتابع قراءات وأحداث تحدده بنفسك)    │
│   • You specify the exact sequence (e.g., "At Hour 0 enter X, after 1h     │
│     enter Y, after 2h enter Z") and the AI executes your exact script.     │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Step 4.2: Fast-Forward Intake + Strict Step-by-Step Sequential Execution

* **What MAY Be Fast-Forwarded (Pre-Seeded)**: Static, already-verified case header/intake fields (`Name`, `Age`, `Parity`, `MRN`, `Admission Time`) via a helper fixture (`seedVerifiedActiveCase(...)`).
* **What MUST NEVER Be Fast-Forwarded (Strict Incremental Rule)**: Time-series observations and state transitions. Never pass `listOf(obs1, obs2, obs3)` in a single batch call. Dispatch $T_0 \to \text{Save/Rehydrate} \to T_{+1\text{h}} \to \text{Save/Rehydrate} \to \text{Reload}$ sequentially.

---

## 4. Step 4.3: Cross-Function Call-Chain, SaMD Zero-Delete & JVM Bytecode Audit

1. **Multi-Caller Trace (`scenario_and_callchain_engine.py --trace-dir <dir> --symbol <fn>`)**: Confirm all production callers pass consistent units and zero internal mocks exist in integration tests.
2. **Automated SaMD Static AST & JVM Budget Linter (`lint_samd_invariants.py --scan-dir <dir>`)**:
   * **Rule SaMD-ZERO-DELETE (Defect D-3 Guard)**: Forbids raw SQL `DELETE FROM` on clinical entities (`labour_case`, `patient`, `observation_bundle`, `audit_event`) unless guarded by `MockCasesCatalog.isMockCaseId(id)` or `@SyntheticMockDataPurgeOnly`. Real patient cases must transition to `CaseStatus.CLOSED` with an immutable `AuditEventEntity`.
   * **Rule JVM-PARAM-BUDGET (Defect D-5 Guard)**: Flags any constructor/function with $\ge 20$ parameters (`WARNING`) and blocks builds at $\ge 35$ parameters (`HARD_BLOCKER`) to prevent JVM 255-word `ClassFormatError`.
   * **Rule RBAC-STRING-HEURISTIC (Defect D-2 Guard)**: Blocks unverified string equality admin checks (`username == "..."`).

---

## 5. Step 4.4: 3-Layer Outcome Oracle, Geometric Bounds & Auth Fuzz Matrix

### A. Upgrade 1: Layer 3 Geometric & Multi-Viewport Bounding-Box Oracle
Whenever TopBars, Headers, Dialogs, or Action Trays are modified, semantic `assertExists()` is insufficient. Enforce **Bounding Box Differential Assertions** on $320\text{dp}$ and $360\text{dp}$ viewports (LTR and RTL):

```kotlin
// Run `python3 scripts/scenario_and_callchain_engine.py --geometric-oracle` to emit this template:
val navBounds = composeTestRule.onNodeWithTag("NavIcon").getUnclippedBoundsInRoot()
val titleBounds = composeTestRule.onNodeWithTag("TopBarTitle").getUnclippedBoundsInRoot()
val actionsBounds = composeTestRule.onNodeWithTag("ActionsCluster").getUnclippedBoundsInRoot()

// 1. Assert zero horizontal overlap
assertTrue(titleBounds.left >= navBounds.right, "Geometric Escape: Title overlaps start navigation icon")
assertTrue(titleBounds.right <= actionsBounds.left, "Geometric Escape: Title overlaps end action tray")

// 2. Assert minimum readable title flex budget on 320dp/360dp viewport
val availableTitleWidth = actionsBounds.left - navBounds.right
assertTrue(availableTitleWidth >= 120.dp, "Geometric Escape: Action cluster choked title width below 120.dp")
```

### B. Upgrade 2: Tabula Rasa Auth & RBAC Claim Permutation Matrix
Whenever authentication, clinician registration, or admin authorization (`isSystemAdmin`, `canPublishGuidance`, `canTransferCase`) is touched, execute all 6 rows generated by `python3 scripts/scenario_and_callchain_engine.py --auth-fuzz-matrix`:

| Permutation ID | Username Input | Email Input | Provider & Verification | Expected Role |
| :--- | :--- | :--- | :--- | :--- |
| `AUTH-FUZZ-01` | `dr.sherif1992@gmail.com` | `dr.sherif1992@gmail.com` | Google (`verified=true`) | `ADMIN` |
| `AUTH-FUZZ-02` | `dr.sherif1992@gmail.com` | `null` (Email in username) | Google (`verified=true`) | `ADMIN` |
| `AUTH-FUZZ-03` | `  DR.SHERIF1992@GMAIL.COM ` | ` DR.SHERIF1992@GMAIL.COM ` | Google (`verified=true`) | `ADMIN` |
| `AUTH-FUZZ-04` | `dr.sherif1992@gmail.com` | `dr.sherif1992@gmail.com` | Password (`verified=false`) | `NON_ADMIN_REJECTED` |
| `AUTH-FUZZ-05` | `dr.sherif1992+fake@gmail.com` | `dr.sherif1992+fake@gmail.com` | Google (`verified=true`) | `NON_ADMIN_REJECTED` |
| `AUTH-FUZZ-06` | `dr.ahmed.ali` | `ahmed@hospital.gov.eg` | Password (`verified=true`) | `DOCTOR_NON_ADMIN` |
