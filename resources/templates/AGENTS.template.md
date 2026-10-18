# Multi-Agent Fleet Governance & Role Matrix

This document defines the roles, active lanes, and operational constraints for multi-agent collaboration on this codebase.

## 1. Fleet Leadership
* **Principal Consultant & Fleet Orchestrator**: `Antigravity`
  * Responsibilities: Work breakdown, lane assignment, cross-lane arbitration, final PR/diff verification, and git commits.

## 2. Active Fleet Lanes & Role Mapping

| Lane | Assigned Model / Persona | Primary Scope & Responsibilities |
| :--- | :--- | :--- |
| **UI Lane** | `Claude Sonnet` *(or UI Persona)* | Component hierarchy, styling, state binding, responsiveness, WCAG a11y, animations. |
| **Core Logic Lane** | `OpenCode DeepSeek` *(or Logic Persona)* | Business algorithms, math, concurrent workflows, query optimization, core domain rules. |
| **Data Lane** | `OpenCode GLM` *(or Data Persona)* | Schemas, DTOs, migrations, input serialization, validation bounds, i18n/L10n strings. |
| **QA & Audit Lane** | `Gemini` *(or Audit Persona)* | Cross-cutting regression audit, security threat modeling, domain regulatory verification. |

## 3. Operational Rules
1. **Ponytail Ladder Compliance**: Every lane must abide by the 7-Rung Ponytail Engine. No unnecessary abstractions or dependencies.
2. **Anti-Infinite-Critique**: Peer critiques are strictly capped at 2 rounds.
3. **Supreme Arbiter Rule**: In case of unresolved cross-lane deadlock after Round 2, `Antigravity` issues a binding ruling.
4. **Clean Provenance**: All lane handoffs must be registered in `.agents/AI_HANDOFF_LEDGER.md`. Do not pollute application source files with unparsed comments.
