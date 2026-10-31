# Android Deep Diagnostics & Telemetry Verification

This reference defines platform-specific diagnostics for Android applications during Phase 4.5 deep release verification. It supplements `references/deep_diagnostics.md` when the project profile includes the android pack.

---

## 1. Android Diagnostic Tools & Engines

Before running Android diagnostics, inspect the host for available Android SDK tools and diagnostic plugins:

| Capability / Target | Primary Plugin / Engine | Direct CLI / Tool | Purpose |
| :--- | :--- | :--- | :--- |
| Hybrid / Native UI E2E | Compose UI Test / Maestro | `@e2e-dev/mobile` | Longitudinal user journeys, cached scenario replay, UI assertions |
| Android Performance & Memory | android-profiler skill | `adb shell dumpsys meminfo` / `systrace` | Heap dumps, memory leaks, frame drops (jank), GC thrashing |
| Android Runtime & Logcat | android-cli skill | `adb logcat -d` / `adb bugreport` | Fatal crashes, silent exceptions, StrictMode violations |
| Crashlytics & Telemetry | firebase-crashlytics skill | `google-services.json` / build scripts | Symbol mapping upload, non-fatal logging |
| Test Strategy & Coverage | testing-setup skill | `./gradlew test jacocoTestReport` | Harness completeness, edge-case coverage, regression suites |

---

## 2. The 4-Pillar Android Audit Breakdown

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
