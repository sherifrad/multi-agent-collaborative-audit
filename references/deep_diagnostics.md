# Deep Diagnostics, Low-Level Telemetry & Production Verification Protocol

This reference defines the execution workflow for **Phase 4.5: Deep Release Verification Gate**. It orchestrates low-level system audits, ADB Logcat silent error hunting, memory leak detection, Crashlytics telemetry hardening, and deep unit testing before approving a stable production release.

---

## 1. User Consent & Resource Authorization Gate
Deep testing, memory profiling, and extensive test coverage audits consume significant machine resources, device time, and AI tokens. 
Therefore, **the orchestrator MUST pause and explicitly request user approval before starting Phase 4.5**:
> *"Implementation and standard builds have succeeded. Would you like to launch the **Deep Release Verification & Low-Level Diagnostics Audit** (Logcat silent bug hunt, Android Profiler memory/jank analysis, Firebase Crashlytics verification, and deep unit test audit)? [Approve / Skip to Final Commit]"*

---

## 2. Dynamic Testing Tool & Plugin Discovery

Before running the audit, the orchestrator inspects the host environment for specialized diagnostic plugins and skills:

| Capability / Target | Primary Plugin / Skill | Fallback / Direct CLI | Purpose |
| :--- | :--- | :--- | :--- |
| **Android Performance & Memory** | `android-profiler` | `adb shell dumpsys meminfo` / `systrace` | Heap dumps, memory leaks, frame drops (Jank), GC thrashing |
| **Android Runtime & Logcat** | `android-cli` | `adb logcat -d` / `adb bugreport` | Fatal crashes, silent exceptions, StrictMode violations |
| **Crashlytics & Telemetry** | `firebase-crashlytics` | `google-services.json` / build scripts | Symbol mapping upload, non-fatal logging, Zero-PII compliance |
| **Test Strategy & Coverage** | `testing-setup` | `./gradlew test jacocoTestReport` | Harness completeness, edge-case coverage, regression suites |
| **Web & Accessibility Auditing** | `a11y-debugging` / `chrome-devtools` | Lighthouse CLI / axe-core | Web DOM traps, tap targets, Core Web Vitals |

### Discovery & Auto-Recommendation Workflow:
1. **Probe Skills**: Check `~/.gemini/config/skills/` and plugin directories.
2. **Surface Missing Tools**: If the project is Android-based and `android-profiler` or `android-cli` is not installed, prompt the user with an actionable recommendation to enable/install it.
3. **Discover Project-Specific Testing Plugins**: Detect any project-specific testing harnesses (e.g. Flutter integration test plugins, Playwright/Cypress for web) and dynamically incorporate them into the audit brief.

---

## 3. The 4-Pillar Deep Audit Breakdown

The fleet orchestrator partitions the deep diagnostic responsibilities across the specialized lanes:

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
  Pinpoint composables or views causing render stalls (> 16ms per frame).
* **Memory Allocation & Leak Inspection**:
  If `android-profiler` is available, trigger a heap snapshot or inspect `dumpsys meminfo <package>` after navigation flows to verify Bitmaps, ViewModels, and Event Listeners are garbage collected.
* **Narrow-Screen Touch Target Verification**:
  Re-verify that touch targets on 320dp/360dp screens do not overlap and meet the $\ge 48\text{dp}$ medical/bedside standard.

### Pillar C: Cloud Telemetry & Crashlytics Integration (`QA & Audit Lane - Gemini`)
* **ProGuard / R8 De-obfuscation**:
  Ensure release build configurations (`build.gradle.kts`) upload symbol mapping files to Firebase so production stack traces are human-readable.
* **Non-Fatal Exception Wiring**:
  Verify critical error paths log to Firebase Crashlytics:
  ```kotlin
  FirebaseCrashlytics.getInstance().recordException(throwable)
  ```
* **Zero-PII HIPAA/GDPR Audit**:
  Verify Crashlytics custom keys, user IDs, and analytics logs **never contain raw patient identifiers, medical record numbers, or sensitive clinical notes**.

### Pillar D: Deep Unit & Boundary Test Integrity (`Data Lane - OpenCode GLM`)
* **Test Coverage & Assertion Rigor**:
  Inspect existing unit test suites for:
  1. *Inverted Assertions*: (e.g. testing for null when an object should exist, formalizing bugs).
  2. *Missing Boundary Conditions*: (empty arrays, max integer limits, network timeouts, offline transitions).
  3. *Pure Bilingual String Completeness*: Verify no English keys leak into RTL mode and no protected clinical reports are mutated.

---

## 4. Reporting & Verdict Gate
All findings are compiled into `.agents/AI_HANDOFF_LEDGER.md` under section `### Phase 4.5 Deep Diagnostics Report`.
* Any **Silent Crash, Memory Leak, or StrictMode Blocker** must be resolved before final release tagging.
* Once all pillars pass cleanly, the orchestrator issues the release clearance for final git tagging and push.
