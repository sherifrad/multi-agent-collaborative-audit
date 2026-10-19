# Multi-Agent Fleet Governance & Role Matrix

This document defines the roles, active lanes, and operational constraints for multi-agent collaboration on this codebase.

## 1. Fleet Leadership
* **Principal Consultant & Fleet Orchestrator**: `Antigravity`
  * Responsibilities: Work breakdown, lane assignment, cross-lane arbitration, final PR/diff verification, and git commits.

## 2. Active Fleet Lanes & Role Mapping

| Lane | Assigned Model / Persona | Primary Scope & Responsibilities |
| :--- | :--- | :--- |
| **UI/UX & Graphic Design Lane** | `Claude Sonnet` *(Default)*<br/>*Fallback: Gemini / Antigravity* | Graphic design, page/app wireframing, interactive HTML/SVG mock creation, user visual approval gate, component ergonomics, WCAG 2.1 AA. |
| **Core Logic Lane** | `OpenCode DeepSeek` *(or Logic Persona)* | Business algorithms, math, concurrent workflows, query optimization, core domain rules. |
| **Data Lane** | `OpenCode GLM` *(or Data Persona)* | Schemas, DTOs, migrations, input serialization, validation bounds, i18n/L10n strings. |
| **QA & Audit Lane** | `Gemini` *(or Audit Persona)* | Cross-cutting regression audit, security threat modeling, domain regulatory verification. |

## 3. Operational Rules
1. **Ponytail Ladder Compliance**: Every lane must abide by the 7-Rung Ponytail Engine. No unnecessary abstractions or dependencies.
2. **Visual Approval Gate**: All UI, screen, and graphic changes require an interactive mockup created by the UI/UX Lane and explicitly approved by the user before task breakdown or logic coding begins.
3. **Anti-Infinite-Critique**: Peer critiques are strictly capped at 2 rounds.
4. **Supreme Arbiter Rule**: In case of unresolved cross-lane deadlock after Round 2, `Antigravity` issues a binding ruling and override patch.
5. **Clean Provenance**: All lane handoffs must be registered in `.agents/AI_HANDOFF_LEDGER.md`. Do not pollute application source files with unparsed comments.
6. **Cross-Model Adversarial Diff Audit & Bug Hunt Protocol**:
   - Prior to git staging/commit, peer model lanes must inspect the active `git diff` and implementation evidence independently.
   - **Zero-Presumption Tabula Rasa**: The reviewer must treat the code and original user requirement as if encountering them for the first time. Do NOT inherit the implementing model's assumptions, rationales, or interpretations. First understand the fundamental *why* of the requirement, critically interrogate whether the underlying logic and architecture are sound, and actively hunt for flaws.
   - **Mandatory Bug Hunt Scope**:
     1. *Regressions & State Hazards*: Unhandled nulls, race conditions, memory leaks, or broken lifecycles.
     2. *Domain & Localization Boundary Leaks*: Untranslated hardcoded strings, broken bidirectional text (RTL/LTR), or accidental mutation of protected domains (e.g. Clinical references, patient names, legal disclaimers, or standard export formats).
     3. *Visual & Responsive Deficiencies*: Text clipping, truncation, overlapping cards on narrow viewports (320dp/360dp), and missing touch targets (< 48dp).
     4. *Accessibility (a11y) & Usability*: Missing screen-reader semantics, broken keyboard/IME navigation.
   - Findings must be recorded in `.agents/AI_HANDOFF_LEDGER.md` with explicit `PASS` or `BLOCKER` designations before commit authorization. A `BLOCKER` halts git commit until patched or arbitrated.
