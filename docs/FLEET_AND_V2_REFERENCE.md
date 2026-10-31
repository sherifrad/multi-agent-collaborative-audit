# 🦅 Multi-Agent Collaborative Audit (MACA)

> **Spec-Driven, Ponytail-Optimized, Dynamic Fleet-Routed & Sequential E2E Intent-Verified Multi-Agent Engineering Skill.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Orchestrator: Antigravity](https://img.shields.io/badge/Orchestrator-Antigravity-4285F4.svg)](https://deepmind.google)
[![Architecture: Spec--Driven](https://img.shields.io/badge/Architecture-SDD-green.svg)](#-the-5-phase-sdd-workflow)
[![Minimalism: Ponytail Engine](https://img.shields.io/badge/Philosophy-Ponytail--Minimalism-ff69b4.svg)](#-the-7-rung-ponytail-minimalism-engine)
[![Verification: 3--Layer E2E Oracle](https://img.shields.io/badge/Verification-Sequential--E2E--Oracle-10b981.svg)](#-phase-4-dedicated-sequential-e2e--call-chain-verification-zone)
[![Fleet: Dynamic Multi--Adapter](https://img.shields.io/badge/Fleet-CLIs%20%7C%20APIs%20%7C%20Ollama%20%7C%20Zero--API-blueviolet.svg)](#-dynamic-multi-adapter-fleet-router--zero-api-resilience)

---

## 📑 Table of Contents

* [🎯 Overview & Mission](#-overview--mission)
  * [The 4 Fatal AI Engineering Failure Modes](#the-4-fatal-ai-engineering-failure-modes)
* [🏛️ Model-Agnostic Fleet Architecture](#-model-agnostic-fleet-architecture)
  * [Lane Competency Contracts](#lane-competency-contracts)
* [🔌 Dynamic Multi-Adapter Fleet Router & Zero-API Resilience](#-dynamic-multi-adapter-fleet-router--zero-api-resilience)
  * [The 4 Execution Adapters](#1-the-4-universal-execution-adapters)
  * [Declarative Fleet Manifest (`.agents/fleet.json`)](#2-declarative-fleet-manifest-agentsfleetjson)
  * [Fail-Safe Cascade & Unreachable Server Resilience](#3-unreachable-server--fail-safe-cascade)
  * [Detection, Self-Repair & Resilience Testing](#4-built-in-detection-self-repair--resilience-testing)
* [🔄 The 5-Phase SDD Engineering Workflow](#-the-5-phase-sdd-workflow)
  * [Detailed Gate Breakdown](#detailed-gate-breakdown)
* [🧪 Phase 4: Dedicated Sequential E2E & Call-Chain Verification Zone](#-phase-4-dedicated-sequential-e2e--call-chain-verification-zone)
  * [The 4 Verification Pillars](#the-4-verification-pillars)
* [✂️ The 7-Rung Ponytail Minimalism Engine](#-the-7-rung-ponytail-minimalism-engine)
* [🏛️ Skill Ambassador & Procedural Compliance Referee](#-skill-ambassador--procedural-compliance-referee)
* [📊 Telemetry, Cockpit Dashboard & Native Notifications](#-telemetry-cockpit-dashboard--native-notifications)
* [🚀 Quickstart & Developer Tracks](#-quickstart--developer-tracks)
  * [Track 1: Solo Developer ($0 Zero-API Mode)](#track-1-solo-developer-0-zero-api-mode)
  * [Track 2: Power User (Local AI CLIs)](#track-2-power-user-local-ai-clis)
  * [Track 3: Custom APIs & Local Models (Ollama / DeepSeek)](#track-3-custom-apis--local-models-ollama--deepseek)
* [🛠️ Engine Script Cheatsheet](#-engine-script-cheatsheet)
* [📜 License & Provenance](#-license--provenance)

---

## 🎯 Overview & Mission

### The 4 Fatal AI Engineering Failure Modes

Modern AI-assisted software engineering suffers from **four fatal failure modes**:

1. **Agent Bloat & Overengineering**: LLMs generate speculative abstractions, inject unneeded dependencies, or compress multi-step logic into brittle one-liners.
2. **Infinite or Fake Review Loops**: Multi-agent setups either loop indefinitely in circular debates or fake independent review using single-turn `[In-Process]` self-approvals.
3. **The Bulk-Mock & Vacuous Test Illusion**: Tests pass with green `exit code 0` because tests feed pre-baked mock payloads directly into state instead of stepping through real time sequences ($T_0 \to T_1 \to T_2$). The app passes tests, but fails when a human clicks it.
4. **Environment Fragility & Delusion**: Agents assume external CLIs or specific API keys exist, crashing or halting when running sandboxed or offline.

**Multi-Agent Collaborative Audit (MACA)** resolves these failure modes deterministically. Led by **Google Antigravity** as the Principal Consultant, MACA enforces a **5-Phase Spec-Driven Workflow**, passes all code through a **7-Rung Ponytail Minimalism Ladder**, bounds adversarial reviews to **2 rounds maximum**, and routes execution through a **Dynamic, Model-Agnostic Multi-Adapter Fleet Router** with automated fail-safe cascade.

---

## 🏛️ Model-Agnostic Fleet Architecture

MACA decouples software delivery into specialized, isolated **Fleet Lanes**. Rather than hardcoding rigid models, each lane is defined by a **Functional Competency Contract** that can be powered by your choice of local CLIs, direct APIs, local LLMs (Ollama), or native zero-cost In-IDE subagents.

```mermaid
flowchart TD
    subgraph Lead["🦅 Principal Consultant & Fleet Orchestrator (Antigravity)"]
        Boot["Phase 0: Engine Bootstrap & Fleet Discovery"]
        Spec["Phase 1: Zero-Presumption Spec & Call-Chain Map"]
        MockGate["Phase 1.5: UI/UX Visual Approval Gate<br/>User Approval Inviolable"]
        Plan["Phase 2: Task Partitioning & Lane Allocation"]
        Arbiter["Supreme Arbiter & Final Commit Authority"]
    end

    Boot --> Spec --> MockGate --> Plan

    subgraph DynamicRouter["⚡ Dynamic Multi-Adapter Fleet Router (scripts/fleet_select.py, model_router.py, fleet_run.py)"]
        direction TB
        UI["🎨 UI/UX Mocking Lane<br/><b>Visual Design Contract</b><br/>• Interactive HTML/SVG Prototypes<br/>• WCAG 2.1 AA a11y & Visual State"]
        Logic["🧠 Core Logic Lane<br/><b>Algorithmic & State Contract</b><br/>• Business Algorithms & State Machines<br/>• Concurrency & Query Optimization"]
        Data["📊 Data Lane<br/><b>Data Integrity Contract</b><br/>• Schema Migrations & DTOs<br/>• Strict Boundary Validation"]
        Audit["🛡️ QA & Audit Referee Lane<br/><b>Adversarial Audit Contract</b><br/>• Rule 6 Tabula Rasa Diff Audit<br/>• Sequential E2E Oracle Verification"]
    end

    Plan --> UI
    Plan --> Logic
    Plan --> Data
    UI --> Audit
    Logic --> Audit
    Data --> Audit
    Audit --> Arbiter
```

### Lane Competency Contracts

| Lane | Competency Contract & Deliverables | Supported Providers (Fully Dynamic) | Strict Boundary |
| :--- | :--- | :--- | :--- |
| **Lead Orchestrator** | Master task charter, preflight verification, arbiter rulings, commit authority | Google Antigravity | Supreme Arbiter; breaks ties after Round 2 |
| **🎨 UI/UX Mocking** | Interactive HTML/SVG prototypes (`.agents/mocks/*.html`), vector rendering, responsive layout, a11y audit | Claude Code CLI, Vision APIs, or In-IDE Subagent | **Visual Gate**: Zero logic coding until user approves mock |
| **🧠 Core Logic** | Domain models, algorithms, state engines, mathematical invariants | OpenCode, Codex CLI, Reasoning APIs, or In-IDE Subagent | Adheres to Ponytail Rungs 1–3 before introducing abstractions |
| **📊 Data** | Migrations, DTOs, boundary parsers, schemas, database persistence | OpenCode, Codex CLI, Schema APIs, or In-IDE Subagent | Type-safe null safety; strict external input sanitization |
| **🛡️ QA & Referee** | Adversarial diff reviews, call-chain tracing, sequential E2E oracle runs | Gemini CLI, Deep-Context APIs, or In-IDE Subagent | **Rule 6 Tabula Rasa**: Independent critique; no assumptions |

---

## Fleet selection, model routing and delegation

MACA keeps no vendor list of its own. Delegation uses the upstream delegate skills (`vendor/delegate-skills/`, pinned in `VENDOR.md`).

| Step | Tool | Decides |
| :-- | :-- | :-- |
| 1. Who is available and allowed | `scripts/fleet_select.py` | archetype (solo / pair / fleet), vendors withheld and why, best independence level |
| 2. Which model and how much reasoning | `scripts/model_router.py route --role R` | tier (light / standard / frontier) and effort per role, from measured signals; call budget |
| 3. Run it, with fallback | `scripts/fleet_run.py` | runs the chain through the upstream relays, read-only unless a person allowed writing |

See `references/fleet_profiles.md` and `references/model_routing.md`. Local models (Ollama and similar) are reached through
opencode providers, not through a MACA adapter.

## 🔄 The 5-Phase SDD Engineering Workflow

Every non-trivial engineering task strictly advances through five sequential gates:

```mermaid
flowchart LR
    P0["Phase 0<br/>Bootstrap & Diagnostics"] --> P1["Phase 1<br/>Spec & Call-Chain Map"]
    P1 --> P15["Phase 1.5<br/>Visual Mock Gate<br/>(User Signs Off)"]
    P15 --> P2["Phase 2<br/>Task Queue Sync"]
    P2 --> P3["Phase 3<br/>Tabula Rasa Diff Audit"]
    P3 --> P4["Phase 4<br/>Sequential E2E Zone"]
    P4 --> P45["Phase 4.5<br/>Deep Diagnostics"]
    P45 --> Final["Phase 5<br/>Telemetry & Release"]
```

### Detailed Gate Breakdown

```
Phase 0: Engine Bootstrap & First-Run Deep Diagnostic
  ├── Run scripts/first_run_preflight.py & scripts/bootstrap.sh
  ├── Verify all 11 external tools and execution engines
  └── Fail-Closed Error Reporting: Never proceed silently with broken tooling

Phase 1: Zero-Presumption Spec & Call-Chain Architecture
  ├── Author .agents/SPEC_AND_AUDIT.md
  ├── Map upstream and downstream call chains: (F_upstream -> F_target -> F_downstream)
  └── Pin failure modes, boundaries, and acceptance criteria

Phase 1.5: Inviolable UI/UX Visual Approval Gate (Mandatory for User-Facing UI)
  ├── UI/UX Lane produces self-contained interactive prototype (.agents/mocks/<feature>.html)
  ├── Embed high-fidelity SVGs, real color tokens, and responsive mobile/desktop containers
  └── 🛑 HARD STOP: Present prototype to User. Zero logic coding allowed until User approves!

Phase 2: Task Partitioning & Queue Synchronization
  ├── Synchronize tasks/current_task.md or .agents/PLAN_TASKS.md
  └── Partition work into independent, non-overlapping atomic subtasks

Phase 3: Tabula Rasa Adversarial Diff Audit (Rule 6)
  ├── QA Lane inspects `git diff` with clean slate (Zero prior knowledge or model bias)
  ├── Document findings in .agents/AI_HANDOFF_LEDGER.md (Banning fake `[In-Process]` badges)
  └── Maximum 2 debate rounds; Antigravity Arbiter rules deterministically on unresolved disputes

Phase 4: Dedicated Sequential E2E & 3-Layer Outcome Oracle Zone
  ├── Execute scripts/scenario_and_callchain_engine.py
  ├── Enforce Anti-Bulk-Mock Progression (T0 -> T1 -> T2 chronological events)
  └── Verify 3-Layer Oracle: Domain Logic + DB Persistence + UI Assertion + Negative Control

Phase 4.5: Deep Diagnostics & Performance Profiling
  ├── Inspect Logcat, memory heap, crashlytics, and system traces
  └── Require explicit User Consent before running heavy instrumentation

Phase 5: Telemetry, Desktop Notification & Final Commit
  ├── Calculate project health and Ponytail index (scripts/measure_metrics.py)
  ├── Send native macOS notification (--notify)
  └── Produce atomic git commit with full Fleet Dispatch attribution badge
```

---

## 🧪 Phase 4: Dedicated Sequential E2E & Call-Chain Verification Zone

To bridge the gap between "green tests" and broken software, MACA bans vacuous tests and bulk mocks through [`references/e2e_and_call_chain_testing.md`](references/e2e_and_call_chain_testing.md) and [`scripts/scenario_and_callchain_engine.py`](scripts/scenario_and_callchain_engine.py).

```mermaid
sequenceDiagram
    autonumber
    actor User as Real User / E2E Runner
    participant UI as Presentation Layer
    participant Upstream as Upstream Caller (F_upstream)
    participant Target as Target Business Logic (F_target)
    participant Downstream as Downstream Consumer (F_downstream)
    participant Storage as Real DB / State Store

    Note over User,Storage: Anti-Bulk-Mock Progression: Step-by-Step Chronological Events (T0 -> T1 -> T2)
    User->>UI: T0: User opens screen (Initial Empty State)
    UI->>Target: Fetch baseline state
    Target->>Storage: Read real record
    Storage-->>Target: Empty / Initial Data
    Target-->>UI: Render baseline UI

    User->>UI: T1: User submits step 1 (Partial Entry)
    UI->>Upstream: Trigger primary action
    Upstream->>Target: Call Target Function with input
    Target->>Storage: Mutate state (DB Layer)
    Target->>Downstream: Fire downstream side-effect

    User->>UI: T2: User finalizes action (Terminal State)
    UI->>Target: Validate completion
    Target->>Storage: Persist final transaction
    
    Note over Target,Storage: 3-Layer Outcome Oracle Verification
    rect rgb(240, 255, 240)
        Note right of Storage: 1. Domain Logic: Result verified<br/>2. DB Persistence: Re-queried from disk<br/>3. Visual UI: Assert element presence<br/>4. Negative Control: Malformed input rejected
    end
```

### The 4 Verification Pillars

1. **User-Selected Scenario Modes**:
   * **Mode A (Predefined)**: Hardcoded deterministic test matrices and compliance fixtures.
   * **Mode B (Imaginary Stress Scenarios)**: Generates high-friction edge cases (e.g., dead battery mid-transaction, double taps, rapid orientation flips).
   * **Mode C (Custom Multi-Step)**: User or agent inputs specific step-by-step real user actions.
2. **The Anti-Bulk-Mock Rule**: Banned from loading pre-baked complete final states. Tests must fast-forward through intake and sequentially apply chronological state transitions ($T_0 \to T_1 \to T_2$).
3. **Multi-Caller Call-Chain Tracing**: Validates upstream callers ($F_{upstream}$) and downstream listeners ($F_{downstream}$) under test, strictly banning internal function mocks.
4. **3-Layer Outcome Oracle**:
   $$\text{Oracle} = \text{Domain Logic Result} \land \text{Storage/DB Persistence} \land \text{Visual UI Confirmation} \land \text{Negative Control}$$

---

## ✂️ The 7-Rung Ponytail Minimalism Engine

AI models tend to generate unnecessary abstractions. MACA forces every architectural decision through the **7-Rung Ponytail Decision Ladder** ([`references/ponytail_ladder.md`](references/ponytail_ladder.md)). Agents must exhaust lower rungs before reaching for higher rungs.

```mermaid
flowchart TD
    R1["Rung 1: YAGNI / Zero Code<br/>Delete unnecessary requirements or dead code"]
    R2["Rung 2: Existing Helper Reuse<br/>Leverage utilities already in codebase"]
    R3["Rung 3: Language Standard Library<br/>Built-in primitives (Kotlin stdlib, Python collections, TS Array)"]
    R4["Rung 4: Single Local Utility Function<br/>Self-contained, pure function in same module"]
    R5["Rung 5: Existing Direct Dependency<br/>Utilize already imported libraries"]
    R6["Rung 6: New Trusted Dependency<br/>Battle-tested, lightweight package (Requires justification)"]
    R7["Rung 7: Custom Architecture / Subsystem<br/>New classes, design patterns, microservices (Supreme Arbiter Approval Required)"]

    R1 -->|If insufficient| R2
    R2 -->|If insufficient| R3
    R3 -->|If insufficient| R4
    R4 -->|If insufficient| R5
    R5 -->|If insufficient| R6
    R6 -->|If unavoidable| R7

    style R1 fill:#dcfce7,stroke:#16a34a,stroke-width:2px
    style R2 fill:#dcfce7,stroke:#16a34a,stroke-width:2px
    style R3 fill:#dcfce7,stroke:#16a34a,stroke-width:2px
    style R4 fill:#fef9c3,stroke:#ca8a04,stroke-width:2px
    style R5 fill:#fef9c3,stroke:#ca8a04,stroke-width:2px
    style R6 fill:#fee2e2,stroke:#dc2626,stroke-width:2px
    style R7 fill:#fecaca,stroke:#b91c1c,stroke-width:3px
```

* **Target Goal**: $\ge 75\%$ of all logic resolved in **Rungs 1–3**.
* **Debt Tagging**: Any code requiring Rung 6 or 7 must be annotated with:
  ```text
  // ponytail: [Rung 6] Justification for new external dependency
  ```

---

## 🏛️ Skill Ambassador & Procedural Compliance Referee

MACA includes a deterministic compliance referee engine ([`scripts/skill_ambassador_auditor.py`](scripts/skill_ambassador_auditor.py)) that acts as an independent procedural auditor.

### Enforced Compliance Gates (v3)

The referee reads structured records, not keywords (`REVIEW:`, `APPROVAL:`, `ASSUMPTION:` in the ledger,
`ORACLE-<id>:` in the spec). Domain gates apply only where `.agents/PROJECT_PROFILE.md` lists the pack.

| Gate | What must be true | Statuses |
| :---: | :--- | :---: |
| **S1** | Spec has a filled call-chain row and at least one `ORACLE-<id>:` line | `PASS` / `VIOLATION` |
| **S2** | A `REVIEW:` record with reviewer != author, an independence level and evidence | `PASS` / `VIOLATION` |
| **S3** | Every test up to the tier ceiling has a passing record with identical deps | `PASS` / `VIOLATION` |
| **S4** | Every ticked task carries a `command` and a date | `PASS` / `VIOLATION` / `NOT_APPLICABLE` |
| **S5** | Every external vendor that ran is approved by profile or a human `APPROVAL:` | `PASS` / `VIOLATION` / `NOT_APPLICABLE` |
| **S6** | UI projects: a mock exists and a person approved it | `PASS` / `VIOLATION` / `NOT_APPLICABLE` |
| **S7/S8** | Clinical / design linters, if the packs call for them; a 0-file scan is not a pass | `PASS` / `NOT_VERIFIED` / `NOT_APPLICABLE` |

Verdicts and exit codes: `APPROVED` 0, `BLOCKED_BY_SKILL_VIOLATIONS` 1, `INCOMPLETE_NOT_VERIFIED` 3.
`NOT_APPLICABLE` gates are excluded from the score and shown with their reason.

---: | :--- | :--- | :---: |
| **G-01** | Phase 0 Bootstrap & Scripts | `./scripts/bootstrap.sh` exit code `0` | `PASS` / `FAIL` |
| **G-02** | Phase 1 Spec & Call-Chain Map | `.agents/SPEC_AND_AUDIT.md` mapped callers | `PASS` / `BLOCKED` |
| **G-03** | Phase 1.5 Visual Mock Gate | `.agents/mocks/*.html` user sign-off | `PASS` / `BLOCKED` |
| **G-04** | Phase 3 Tabula Rasa Diff Audit | Peer critique in `AI_HANDOFF_LEDGER.md` (No fake `[In-Process]`) | `PASS` / `BLOCKED` |
| **G-05** | Phase 4.1 Scenario Mode Choice | Mode A, B, or C explicitly documented | `PASS` / `BLOCKED` |
| **G-06** | Phase 4.2 Anti-Bulk-Mock Rule | Chronological event transitions ($T_0 \to T_1 \to T_2$) | `PASS` / `BLOCKED` |
| **G-07** | Phase 4.3 Call-Chain & Zero Mock | Zero internal function mocks detected | `PASS` / `BLOCKED` |
| **G-08** | Phase 4.4 3-Layer Outcome Oracle | Logic + Storage + UI + Negative Control | `PASS` / `BLOCKED` |
| **G-09** | Task Queue Synchronization | `tasks/current_task.md` marked `- [x]` with date & proof | `PASS` / `BLOCKED` |

---

## 📊 Telemetry, Cockpit Dashboard & Native Notifications

Track project metrics in real time with [`scripts/measure_metrics.py`](scripts/measure_metrics.py).

```bash
# Launch interactive web dashboard (port 8420)
./scripts/measure_metrics.py

# Send native macOS desktop notification upon gate or task completion
./scripts/measure_metrics.py --notify "MACA E2E Complete" "Sequential Oracle & Call-Chain passed!"

# Output structured JSON metrics for CI/CD pipelines
./scripts/measure_metrics.py --json

# Run built-in self-test verification suite
./scripts/measure_metrics.py --self-test
```

---

## 🚀 Quickstart & Developer Tracks

Choose the track that fits your development environment:

### Track 1: Solo Developer ($0 Zero-API Mode)
* **Pre-requisites**: None! No external API keys, zero paid subscriptions.
* **How it works**: Antigravity automatically uses native In-IDE subagents and context-isolated personas.
```bash
# 1. Run bootstrap check
./scripts/bootstrap.sh

# 2. Initialize project governance charter
python3 scripts/skill_ambassador_auditor.py --init-log . --feature "MyFeature"
```

### Track 2: Power User (installed CLIs)
* **Pre-requisites**: one or more installed, signed-in CLIs (`claude`, `codex`, `opencode`, `agy`), listed in the profile's `Approved vendors`.
```bash
python3 scripts/fleet_select.py --cwd .                 # archetype, roles, withheld vendors
python3 scripts/model_router.py route --role reviewer   # tier, effort, candidate chain
python3 scripts/fleet_run.py --brief brief.md --cd . --out-dir .agents/fleet-runs/r1 --chain 'agy:gemini-3.8-flash-high' --read-only
```

### Track 3: Local and free models
* Free models and local servers come through opencode (`opencode/*-free`, or an Ollama provider). The router prefers free models for light work.

---

## 🛠️ Engine Script Cheatsheet

| Script | Primary Command | Key Flags | Role |
| :--- | :--- | :--- | :--- |
| **`bootstrap.sh`** | `./scripts/bootstrap.sh` | `--force-first-run` | Verifies skill integrity & discovers runtime environment |
| **`first_run_preflight.py`** | `python3 scripts/first_run_preflight.py` | `--force`, `--json` | Runs deep 29-item self-test & tool inventory diagnostic |
| **`fleet_select.py` / `model_router.py` / `fleet_run.py`** | `python3 scripts/<name>.py` | `--self-test` | Fleet plan, model and effort per role, relay runner with fallback |
| **`scenario_and_callchain_engine.py`** | `python3 scripts/scenario_and_callchain_engine.py` | `--self-test`, `--mode <A/B/C>`, `--trace-dir <dir>` | Anti-bulk-mock sequential oracle & caller graph tracer |
| **`skill_ambassador_auditor.py`** | `python3 scripts/skill_ambassador_auditor.py` | `--self-test`, `--init-log <dir>`, `--audit-workspace <dir>` | Enforces procedural gates G-01 through G-09 |
| **`measure_metrics.py`** | `python3 scripts/measure_metrics.py` | `--self-test`, `--notify <Title> <Msg>`, `--json`, `--port <n>` | Telemetry cockpit, notifications & Ponytail analytics |

---

## 📜 License & Provenance

Licensed under the [MIT License](LICENSE).

Authored and maintained under the **Multi-Agent Collaborative Audit (MACA)** framework with **Google Antigravity** as Principal Consultant and Lead Orchestrator.
