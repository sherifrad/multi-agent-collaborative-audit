# Clinical Deep Diagnostics & Safety Verification

This reference defines safety-critical diagnostic checks for clinical applications during Phase 4.5 deep release verification. It supplements `references/deep_diagnostics.md` when the project profile includes the clinical pack.

This pack contains operational directions only. Do not add medical thresholds or values; all specific limits and clinical rules come from the project profile and approved specifications.

---

## 1. Clinical Diagnostics Checks

### Zero Patient Identifiers in Telemetry and Logs
* Audit all error reporting payloads, crash telemetry, analytics events, and console logs.
* Verify custom keys, user identifiers, log lines, and diagnostics never contain raw patient identifiers, medical record numbers, passphrases, patient names, or sensitive clinical notes.
* Test by searching captured diagnostic output against synthetic fixture identifiers.

### Time-Series and Partogram Timeline Scrolling Under Load
* Subject time-series visualizations and partogram timeline interfaces to sequential multi-hour data scrolling under load.
* Verify rendering remains responsive without frame stalls, memory leaks, or progressive UI degradation as data points accumulate across the timeline.

### Shift-Handoff and Report-Export Round-Trip Fidelity
* Verify complete round-trip field fidelity from clinical data entry to database persistence, timeline presentation, shift-handoff summaries, and report generation (such as A4 exports).
* Confirm zero dropped, corrupted, or silently defaulted clinical fields across handoff transitions and external export transformations.

### Bedside Ergonomics
* Inspect user interface components and touch targets under simulated bedside operational conditions.
* Verify controls remain accessible on narrow screens, targets do not overlap, and interactive elements support fast, unambiguous bedside input.
