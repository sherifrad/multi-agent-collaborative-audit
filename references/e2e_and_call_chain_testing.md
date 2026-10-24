# Dedicated E2E, Sequential Scenario & Call-Chain Verification Protocol

> **Authoritative reference for Phase 4 of the MACA Framework: Interactive Scenario Mode Selection, Fast-Forward Intake + Incremental Time-Series Entry, Cross-Function Call-Chain Auditing, and 3-Layer Intended Outcome Oracles.**

---

## 1. Why Traditional AI Unit & Mock Tests Fail in Real Usage

AI coding agents frequently produce tests that pass `npm test` or `./gradlew test` with 100% green checkmarks while the actual application fails when used manually. This happens due to **three classic testing illusions**:

| Testing Illusion | What the AI Does Wrong | Why Manual Testing Breaks | MACA Phase 4 Mandatory Fix |
| :--- | :--- | :--- | :--- |
| **1. The Bulk Mock Illusion (وهم الموك الكامل)** | Constructs a complete multi-hour case snapshot in memory (`observations = [h1, h2, h3, h4]`) and passes it all at once to the evaluator or UI renderer. | Entering `h1`, saving, reopening at `h2`, and saving mutates state incrementally. Bulk mocks completely skip intermediate state transitions, draft clears, lag-anchor resets, and DB rehydration bugs. | **Fast-Forward Intake + Strict Step-by-Step Sequential Entry**: Pre-seed only the static patient header, then dispatch each hourly observation one by one through the real save pipeline. |
| **2. The Vacuous Non-Error Pass (نجاح عدم وجود خطأ)** | Asserts `expect(res).toBeDefined()`, `status === 200`, or `not.toThrow()`. | The function catches or ignores an error and returns an empty/wrong clinical result without crashing. | **3-Layer Intended Outcome Oracle**: Assert exact Domain logic output + exact SQLite/IndexedDB persisted row + exact visible UI text/badge. |
| **3. The Isolated Unit Silo (عزلة الدوال عن بعضها)** | Tests `Function A` in isolation and `Function B` in isolation while mocking the connection between them. | `Function A` is called from 3 different screens (e.g., Bedside Entry, Partogram Matrix, Handoff Summary) with slightly different parameters or units, breaking in 2 of the 3 callers. | **Cross-Function Call-Chain & Multi-Caller Wiring Audit**: Trace every caller of a modified function and run zero-internal-mock integration flows across the full call chain. |

---

## 2. Step 4.1: Interactive Test Scenario Mode Selection Gate

Before generating or running sequential E2E tests for a feature, the Orchestrator / QA Lane presents the user with **three structured options** (or executes the mode already chosen by the user):

```
┌────────────────────────────────────────────────────────────────────────────┐
│ 🧪 MACA Phase 4: Select Your Sequential E2E Testing Mode                   │
├────────────────────────────────────────────────────────────────────────────┤
│ [Mode A] Predefined Standard Suite (الاختبارات القياسية المُعدّة مسبقاً)    │
│   • Runs the built-in sequential E2E baseline, boundary thresholds,        │
│     and unhappy-path negative controls automatically.                      │
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

### Example of Mode B (AI-Proposed Imaginary Scenarios Table for Clinical/Partogram Apps):

When the user selects or requests **Mode B**, present a scannable table like this before running:

| Scenario ID & Name | Fast-Forwarded Case Header (Pre-Seeded) | Step 1 ($T_0$) | Step 2 ($T_{+1\text{h}}$ to $T_{+2\text{h}}$) | Step 3 ($T_{+4\text{h}}$ to $T_{+6\text{h}}$) | Expected 3-Layer Outcome Oracle |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **S1: Prolonged Active First Stage (Cervical Arrest)** | `Sara M.`, Age 26, Nulliparous (`G1P0`), Admitted `10:00`, Active onset `5.0 cm` | `10:00`: Dilatation `6.0 cm`, Descent `4/5`, FHR `140`, Contractions `3/10m (35s)` | `12:00` (+2h): Dilatation still `6.0 cm`, Descent `4/5`, FHR `138`, Contractions `3/10m (30s)` | `15:00` (+5h at 6cm): Dilatation still `6.0 cm`, Descent `4/5`, FHR `144` | **Domain**: `WHO-LCG-ALERT-020` (6cm >= 5h lag) fires at `15:00` (not at `12:00`).<br/>**DB**: 3 sequential `ObservationBundle` rows persisted.<br/>**UI**: Amber/Red lag badge on `6 cm` cell + Active Alert Queue banner. |
| **S2: Fetal Late Deceleration + Tachysystole Confirmation** | `Nour A.`, Age 31, Multiparous (`G3P2`), Admitted `08:00`, Active `5.0 cm` | `08:00`: FHR `142`, Decel `NONE`, Contractions `6/10m (45s)` | `08:30` (+30m): FHR `105 bpm`, Decel `LATE`, Contractions `6/10m (50s)` | `09:00` (+1h): Reload app & open Shift Handoff summary | **Domain**: At `08:00` Contraction signal is `PROVISIONAL`; at `08:30` escalates to `CONFIRMED` + `WHO-LCG-ALERT-005/006` (FHR <110 & Late Decel).<br/>**UI/Handoff**: Unacknowledged immediate safety alert highlighted at top of Handoff card. |
| **S3: Maternal BP Escalation & Proteinuria Combo** | `Heba K.`, Age 29, Nulliparous (`G1P0`), Admitted `12:00`, Active `5.0 cm` | `12:00`: BP `145/92`, Pulse `88`, Temp `37.0`, Urine Protein `++` | `12:25` (+25m): Repeat BP `148/95`, Pulse `92` | `13:00` (+1h): BP `162/112` (Severe range single reading) | **Domain**: `12:00` emits WHO BP/Protein reference + EHC co-timed warning; `12:25` confirms EHC repeat moderate BP; `13:00` triggers immediate severe-range BP action. |

---

## 3. Step 4.2: Fast-Forward Intake + Strict Step-by-Step Sequential Execution

To prevent tests from taking excessive time on repetitive boilerplate while still catching real state-mutation bugs:

### A. What MAY Be Fast-Forwarded (Pre-Seeded)
* **Static Case / Entity Creation**: If patient creation (`Name`, `Age`, `Parity`, `MRN`, `Admission Time`) has already been verified by its own test and is not the subject of the current bug fix, pre-populate the case header via a helper fixture (`seedVerifiedActiveCase(name = "Sara", parity = NULLIPAROUS, admittedAt = t0)`).

### B. What MUST NEVER Be Fast-Forwarded (Strict Incremental Rule)
* **Time-Series Observations & State Transitions**: Never pass `listOf(obs1, obs2, obs3)` in a single batch call.
* **Mandatory Sequential Loop**:
  1. **Step 1 ($T_0$)**: Dispatch the user/UI input action for $T_0$ $\rightarrow$ execute the real save transaction $\rightarrow$ await database commit $\rightarrow$ let the ViewModel/UI state re-collect the flow $\rightarrow$ assert $T_0$ UI and alert state.
  2. **Step 2 ($T_{+1\text{h}}$)**: Advance the injected clock / observation timestamp to $T_{+1\text{h}}$ $\rightarrow$ open the entry state with existing case history loaded from the database $\rightarrow$ enter $T_{+1\text{h}}$ values $\rightarrow$ save $\rightarrow$ assert that $T_0$ was not overwritten and that longitudinal rules (lag, repeat vitals, contraction windows) evaluated the transition from $T_0 \to T_{+1\text{h}}$ accurately.
  3. **Step 3 ($T_{+2\text{h}}$ / Reload / Handoff)**: Enter the third step, simulate process recreation or page reload, and verify that rehydrated state matches the live state 100%.

### C. Example Code Pattern (Hybrid Agentic + Deterministic E2E with `tester-army/e2e`)
```typescript
import { test, expect } from 'e2e';

test('Sequential hourly entry detects cervical arrest only after threshold elapsed', async ({ app, agent, screen }) => {
  // 1. Fast-forward verified baseline case header
  await app.open('/?seedCase=sara-nullip-5cm-1000');
  await expect(screen.getByText('Sara')).toBeVisible();

  // 2. Step 1 (10:00): Record 6 cm dilatation -> Save -> Must NOT trigger 6cm lag alert yet
  await agent.act('Open bedside entry for 10:00, set cervical dilatation to 6 cm, FHR 140, contractions 3 lasting 35s, and save');
  await expect(screen.getByTestId('cell-dilatation-1000')).toContainText('6');
  await expect(screen.queryByTestId('alert-WHO-LCG-ALERT-020')).toBeNull();

  // 3. Step 2 (12:00, +2h): Record 6 cm again -> Save -> Still below 5h threshold for 6cm
  await agent.act('Open bedside entry for 12:00, set cervical dilatation to 6 cm, FHR 138, contractions 3 lasting 35s, and save');
  await expect(screen.getByTestId('cell-dilatation-1200')).toContainText('6');
  await expect(screen.queryByTestId('alert-WHO-LCG-ALERT-020')).toBeNull();

  // 4. Step 3 (15:00, +5h at 6cm): Record 6 cm -> Save -> Exact >=5h threshold met!
  await agent.act('Open bedside entry for 15:00, set cervical dilatation to 6 cm, FHR 142, and save');
  await expect(screen.getByTestId('alert-WHO-LCG-ALERT-020')).toBeVisible();
  await expect(screen.getByTestId('alert-WHO-LCG-ALERT-020')).toContainText('6 cm for >= 5 hours');
});
```

---

## 4. Step 4.3: Cross-Function Call-Chain & Multi-Caller Wiring Audit

When a function works in isolation but fails in the app, the bug almost always lives in **how functions call each other**. Every Phase 4 audit must execute this 3-part check:

### 1. Static Multi-Caller Impact Table
Before testing a modified function `fn`, list every caller across the repository in `.agents/AI_HANDOFF_LEDGER.md`:

| Modified Function / Contract | Caller 1 (Entry Flow) | Caller 2 (Matrix / Timeline) | Caller 3 (Handoff / Export) | Wiring Consistency Check |
| :--- | :--- | :--- | :--- | :--- |
| `LcgAlertEvaluator.evaluate(...)` | `BedsideEntryViewModel` (live preview on draft) | `PartogramViewModel` (persisted case stream) | `HandoffSummaryMapper` & `PdfExportMapper` | Verify all 4 callers pass the same `RuleProfileVersions`, injected `evaluationTime`, and scaled integer units (`dilatationTenths`). |

### 2. Zero-Internal-Mock Call-Chain Integration Test
Write at least one integration test per slice that exercises the **entire vertical call chain without any internal mocks**:
* **Prohibited**: `every { repository.save(any()) } returns Result.success(Unit)` or `vi.mock('../clinical/evaluator')`.
* **Required**: Instantiate the real `ViewModel` + real `Validator` + real `Evaluator` + real `Repository` + real in-memory `RoomDatabase` / `Dexie` instance. Trigger the top-level action (`viewModel.onAction(SubmitObservation(...))`) and assert the resulting state emitted at the bottom of the chain (`partogramViewModel.uiState` and `handoffViewModel.uiState`).

### 3. Orphan & Silent-Drop Detection
Verify that:
* Every validation error or signal returned by a callee is explicitly rendered or handled by the caller (no `.getOrNull()` or ignored return values that silently swallow clinical/data warnings).
* Every field entered in the UI form reaches the database entity and re-emerges in the read-back model (`Round-Trip Field Completeness Assertion`).
