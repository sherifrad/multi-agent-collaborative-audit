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

## 5. Domain and platform specifics

If the profile lists the android or clinical pack, also follow `packs/android/DIAGNOSTICS.md` and/or `packs/clinical/DIAGNOSTICS.md`; any other domain may add `packs/<name>/DIAGNOSTICS.md` in the same shape.
