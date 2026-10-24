# Deep Diagnostics, Low-Level Telemetry & Production Verification Protocol

This reference defines the execution workflow for **Phase 4.5: Deep Release Verification Gate**. While **Phase 4** (governed by [e2e_and_call_chain_testing.md](./e2e_and_call_chain_testing.md)) runs on **every slice** to enforce sequential E2E scenario testing, 3-layer outcome oracles, and call-chain wiring audits, **Phase 4.5** orchestrates heavy low-level hardware/system profiling (ADB Logcat silent error hunting, memory leak detection, Crashlytics telemetry hardening, and full multi-device E2E replay) prior to final production release.

---

## 1. User Consent & Resource Authorization Gate
Heavy memory profiling, device farm runs, and symbol upload audits consume significant machine resources, device time, and AI tokens.
Therefore, **the orchestrator MUST pause and explicitly request user approval before starting Phase 4.5**:
> *"Phase 4 Sequential E2E & Call-Chain Verification passed. Would you like to launch **Phase 4.5: Deep Release Verification & Low-Level Diagnostics Audit** (Logcat silent bug hunt, Android Profiler memory/jank analysis, Firebase Crashlytics verification, and full cached E2E device replay)? [Approve / Skip to Final Commit]"*

---

## 2. Dynamic Testing Tool & E2E Engine Discovery

Before running the audit, the orchestrator inspects the host environment for specialized E2E engines and diagnostic plugins:

| Capability / Target | Primary Plugin / Engine | Fallback / Direct CLI | Purpose |
| :--- | :--- | :--- | :--- |
| **Hybrid Agentic + Deterministic E2E** | `tester-army/e2e` (`@e2e-dev/web`, `@e2e-dev/mobile`) | Playwright / Compose UI Test / Maestro | Sequential longitudinal user journeys, cached action replay, 3-layer outcome assertions |
| **Android Performance & Memory** | `android-profiler` | `adb shell dumpsys meminfo` / `systrace` | Heap dumps, memory leaks, frame drops (Jank), GC thrashing |
| **Android Runtime & Logcat** | `android-cli` | `adb logcat -d` / `adb bugreport` | Fatal crashes, silent exceptions, StrictMode violations |
| **Crashlytics & Telemetry** | `firebase-crashlytics` | `google-services.json` / build scripts | Symbol mapping upload, non-fatal logging, Zero-PII compliance |
| **Test Strategy & Coverage** | `testing-setup` | `./gradlew test jacocoTestReport` | Harness completeness, edge-case coverage, regression suites |
| **Web & Accessibility Auditing** | `a11y-debugging` / `chrome-devtools` | Lighthouse CLI / axe-core | Web DOM traps, tap targets, Core Web Vitals |

---

## 3. The 4-Pillar Deep Audit Breakdown

### Pillar A: Low-Level Runtime & Logcat Silent Error Hunt (`Core Logic Lane - DeepSeek`)
* **Silent Crash & Exception Detection**:
  ```bash
  adb logcat -d *:E | grep -E "(AndroidRuntime|FATAL|Exception|Error|NullPointerException)"
  ```
  Examine stack traces for silent catches (`runCatching { ... }` or empty catch blocks) that logged errors without notifying UI state.
* **StrictMode Violations**:
  Check for disk reads/writes or unoptimized database queries occurring on the Main (UI) thread:
  ```bash
  adb logcat -d | grep -i "StrictMode"
  ```
* **Coroutine Leaks & Thread Starvation**:
  Verify all background jobs are bound to lifecycle scopes (`viewModelScope`, `lifecycleScope`) and properly cancelled on screen navigation.

### Pillar B: Memory Leaks, Frame Drops & Jank (`UI/UX Lane - Claude Sonnet`)
* **Choreographer Jank Analysis**:
  ```bash
  adb logcat -d | grep -E "Choreographer.*Skipped [0-9]+ frames"
  ```
  Pinpoint composables or views causing render stalls (> 16ms per frame) during sequential multi-hour partogram timeline scrolling.
* **Memory Allocation & Leak Inspection**:
  If `android-profiler` is available, trigger a heap snapshot or inspect `dumpsys meminfo <package>` after sequential case entry and handoff flows to verify Bitmaps, ViewModels, and Event Listeners are garbage collected.
* **Narrow-Screen Touch Target Verification**:
  Re-verify that touch targets on 320dp/360dp screens do not overlap and meet the $\ge 48\text{dp}$ medical/bedside standard.

### Pillar C: Cloud Telemetry & Crashlytics Integration (`QA & Audit Lane - Gemini`)
* **ProGuard / R8 De-obfuscation**:
  Ensure release build configurations (`build.gradle.kts`) upload symbol mapping files so production stack traces are human-readable.
* **Zero-PII HIPAA/GDPR Audit**:
  Verify Crashlytics custom keys, user IDs, console logs, and analytics payloads **never contain raw patient identifiers, medical record numbers, passphrases, or sensitive clinical notes**.

### Pillar D: Full Cached E2E Suite Replay & Call-Chain Regression (`Data & QA Lanes`)
* **Full Longitudinal E2E Replay**:
  Re-run all cached `tester-army/e2e` (`.e2e.ts`), Playwright, and Android Instrumented sequential scenarios to confirm zero regression across all previously verified clinical/domain workflows.
* **Assertion & Call-Chain Integrity**:
  Confirm zero mocked internal layers, zero inverted assertions, and 100% round-trip field fidelity from UI entry $\rightarrow$ DB persistence $\rightarrow$ Timeline Matrix $\rightarrow$ Shift Handoff & A4 Export.

---

## 4. Reporting & Verdict Gate
All findings are compiled into `.agents/AI_HANDOFF_LEDGER.md` under section `### Phase 4.5 Deep Diagnostics Report`.
* Any **Silent Crash, Memory Leak, Broken Call-Chain, or StrictMode Blocker** must be resolved before final release tagging.
* Once all pillars pass cleanly, the orchestrator triggers a desktop notification (`./scripts/measure_metrics.py --notify`) and issues the release clearance.
