# Deep Diagnostics, Low-Level Telemetry & Production Verification Protocol

This reference defines the execution workflow for Phase 4.5: Deep Release Verification Gate. While Phase 4 runs on every slice to enforce sequential scenario testing, outcome oracles, and call-chain wiring audits, Phase 4.5 orchestrates deep profiling, runtime telemetry hardening, resource regression analysis, and full end-to-end replay prior to final production release.

---

## 1. User Consent & Resource Authorization Gate

Heavy profiling, extended test suites, and diagnostic replays consume significant machine resources, execution time, and AI tokens. Therefore, the orchestrator MUST pause and explicitly request user approval before starting Phase 4.5:

> "Phase 4 sequential verification passed. Would you like to launch Phase 4.5: Deep Release Verification & Low-Level Diagnostics Audit (runtime error log scan, memory/CPU profiling, telemetry hygiene check, and full cached end-to-end replay)? [Approve / Skip to Final Commit]"

---

## 2. Dynamic Testing Tool & Diagnostic Engine Discovery

Before running the audit, inspect the host for the profilers/test engines the profile's stack uses. Dynamically detect available diagnostic tools matching the target runtime:

| Capability / Target | Tool Category | Purpose |
| :--- | :--- | :--- |
| End-to-End Test Engines | Integration test runners, client drivers | Sequential longitudinal user journeys, cached action replay, outcome assertions |
| Performance & Resource Profiling | System profilers, heap analyzers, tracers | Heap inspection, memory leaks, frame drops, CPU latency regressions |
| Runtime & Process Logging | System log collectors, process monitors | Unhandled errors, fatal exceptions, silent failures, event-loop stalls |
| Telemetry & Error Reporting | Error reporting SDKs, symbol upload tools | Symbol/source map uploads, non-fatal event tracking, privacy hygiene |
| Test Strategy & Coverage | Build system test runners, coverage tools | Test harness completeness, edge-case coverage, full regression suites |
| Client & Interface Auditing | Accessibility and client diagnostics | Target sizing, interface responsiveness, input traps |

---

## 3. The 4-Pillar Deep Audit Breakdown

### Pillar A: Runtime Errors and Silent Failures in Logs
* Silent Crash & Exception Detection: Scan runtime logs, stderr, and system diagnostics for unhandled exceptions, panics, and error-level messages. Inspect catch blocks for silent catches that suppress errors without updating UI state or alerting callers.
* Main Thread & Event Loop Hygiene: Check for blocking I/O, heavy computation, or unoptimized database queries on the primary event loop.
* Resource Scope & Asynchronous Leaks: Verify asynchronous jobs, background tasks, and event subscriptions are bound to their respective lifecycles and cancelled on disposal.

### Pillar B: Memory, CPU, and Latency Regressions
* Latency & Frame Drop Analysis: Measure UI render times and backend request latencies against performance thresholds. Identify routines causing render stalls or high p95/p99 tail latency.
* Memory Allocation & Leak Inspection: Take heap snapshots or inspect process memory usage across sequential workflows to verify data structures, controllers, and listeners are properly garbage collected.
* Interface Target Sizing: Verify interactive elements maintain adequate spacing and meet accessibility sizing standards.

### Pillar C: Production Telemetry Hygiene
* Symbol & Source Map De-obfuscation: Ensure release build configurations upload symbol mapping files or source maps so production stack traces are fully readable.
* Privacy & Data Protection Audit: Verify telemetry custom keys, user attributes, log lines, and analytics payloads never contain personal data, credentials, secrets, or sensitive user identifiers.

### Pillar D: Full Cached End-to-End Replay and Call-Chain Regression
* Longitudinal Scenario Replay: Re-run all cached sequential scenarios to confirm zero regression across previously verified system workflows.
* Assertion & Call-Chain Integrity: Confirm zero mocked internal layers, zero inverted assertions, and complete round-trip data fidelity from input entry through persistence and export.

---

## 4. Reporting & Verdict Gate

All findings are compiled into `.agents/AI_HANDOFF_LEDGER.md` under section `### Phase 4.5 Deep Diagnostics Report`.
* The orchestrator MUST block release on any silent crash, leak, broken call chain or privacy leak. All blocking issues must be resolved before tagging a release.
* Once all pillars pass cleanly, write the verification verdict to the ledger and issue release clearance.

---

## 5. Android Deep Diagnostics & Telemetry Verification

When the project targets Android, inspect the host for available Android SDK tools and diagnostic plugins:

| Capability / Target | Primary Plugin / Engine | Direct CLI / Tool | Purpose |
| :--- | :--- | :--- | :--- |
| Hybrid / Native UI E2E | Compose UI Test / Maestro | `@e2e-dev/mobile` | Longitudinal user journeys, cached scenario replay, UI assertions |
| Android Performance & Memory | android-profiler skill | `adb shell dumpsys meminfo` / `systrace` | Heap dumps, memory leaks, frame drops (jank), GC thrashing |
| Android Runtime & Logcat | android-cli skill | `adb logcat -d` / `adb bugreport` | Fatal crashes, silent exceptions, StrictMode violations |
| Crashlytics & Telemetry | firebase-crashlytics skill | `google-services.json` / build scripts | Symbol mapping upload, non-fatal logging |
| Test Strategy & Coverage | testing-setup skill | `./gradlew test jacocoTestReport` | Harness completeness, edge-case coverage, regression suites |

### Pillar A: Low-Level Runtime & Logcat Silent Error Hunt
* Silent Crash & Exception Detection:
  ```bash
  adb logcat -d *:E | grep -E "(AndroidRuntime|FATAL|Exception|Error|NullPointerException)"
  ```
  Examine stack traces for silent catches (`runCatching { ... }` or empty catch blocks) that logged errors without notifying UI state.
* StrictMode Violations:
  Check for disk reads/writes or unoptimized database queries occurring on the Main (UI) thread:
  ```bash
  adb logcat -d | grep -i "StrictMode"
  ```
* Coroutine & Lifecycle Leaks:
  Verify all background coroutines and jobs are bound to lifecycle scopes (`viewModelScope`, `lifecycleScope`) and properly cancelled on screen navigation.

### Pillar B: Memory Leaks, Frame Drops & Jank
* Choreographer Jank Analysis:
  ```bash
  adb logcat -d | grep -E "Choreographer.*Skipped [0-9]+ frames"
  ```
  Pinpoint composables or views causing render stalls (> 16ms per frame).
* Dumpsys Meminfo & Android Profiler:
  If the `android-profiler` skill is available, trigger a heap snapshot or inspect `adb shell dumpsys meminfo <package>` after sequential workflows to verify Bitmaps, ViewModels, and Event Listeners are garbage collected.
* Narrow-Screen Touch Targets:
  Re-verify that touch targets on 320dp/360dp narrow screens do not overlap and meet the >= 48dp touch target standard.

### Pillar C: Cloud Telemetry & Crashlytics Integration
* R8 / ProGuard De-obfuscation:
  Ensure release build configurations (`build.gradle.kts` / `build.gradle`) upload symbol mapping files so production stack traces are human-readable.
* Crashlytics Telemetry Hardening:
  Verify Crashlytics custom keys, user IDs, console logs, and analytics payloads are configured properly and record non-fatal exceptions.

### Pillar D: Full Cached E2E Suite Replay & Call-Chain Regression
* Full Longitudinal E2E Replay:
  Re-run all cached Android instrumented scenarios (Compose UI Test, Maestro) to confirm zero regression across previously verified Android workflows.
* Gradle Test & Jacoco Coverage:
  Execute `./gradlew test jacocoTestReport` to confirm unit test harness completeness, edge-case coverage, and call-chain integrity.

---

## 6. Domain specifics

If the profile lists the clinical pack, also follow `packs/clinical/DIAGNOSTICS.md`; any other domain pack may add `packs/<name>/DIAGNOSTICS.md` in the same shape.
