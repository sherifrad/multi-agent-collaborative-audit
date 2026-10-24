# 🦅 Multi-Agent Collaborative Audit (MACA)

> **Spec-Driven, Ponytail-Optimized, Fleet-Delegated & Sequential E2E Intent-Verified Multi-Agent Engineering Skill.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Orchestrator: Antigravity](https://img.shields.io/badge/Orchestrator-Antigravity-4285F4.svg)](https://deepmind.google)
[![Architecture: Spec--Driven](https://img.shields.io/badge/Architecture-SDD-green.svg)](#-the-5-phase-sdd-workflow)
[![Minimalism: Ponytail Engine](https://img.shields.io/badge/Philosophy-Ponytail--Minimalism-ff69b4.svg)](#-the-7-rung-ponytail-minimalism-engine)
[![Verification: 3--Layer E2E Oracle](https://img.shields.io/badge/Verification-Sequential--E2E--Oracle-10b981.svg)](#-phase-4-dedicated-sequential-e2e--call-chain-verification-zone)
[![Fleet: Multi--Model](https://img.shields.io/badge/Fleet-Claude%20%7C%20OpenCode%20%7C%20Codex%20%7C%20Gemini-orange.svg)](#-fleet-architecture--lane-routing)

---

## 🎯 Overview & Mission

Modern AI-assisted software engineering suffers from **four fatal failure modes**:

1. **Agent Bloat & Overengineering**: LLMs generate speculative abstractions, inject unneeded dependencies, or compress multi-step logic into brittle one-liners.
2. **Infinite or Fake Review Loops**: Multi-agent setups either loop indefinitely in circular debates or fake independent review using single-turn `[In-Process]` self-approvals.
3. **The Bulk-Mock & Vacuous Test Illusion**: Tests pass with green `exit code 0` because tests feed pre-baked mock payloads directly into state instead of stepping through real time sequences ($T_0 \to T_1 \to T_2$). The app passes tests, but fails when a human clicks it.
4. **Environment Fragility & Delusion**: Agents assume external CLIs exist, crashing or hallucinating commands when running sandboxed.

**Multi-Agent Collaborative Audit (MACA)** resolves these failure modes deterministically. Led by **Google Antigravity** as the Principal Consultant, MACA enforces a **5-Phase Spec-Driven Workflow**, passes all code through a **7-Rung Ponytail Minimalism Ladder**, bounds adversarial reviews to **2 rounds maximum**, and gates all releases through a **Dedicated Sequential E2E & 3-Layer Outcome Oracle Zone**.

---

## 🏛️ Fleet Architecture & Lane Routing

MACA decouples software delivery into specialized, isolated **Fleet Lanes**. Each lane operates with strict boundaries and zero presumption of correctness from prior steps.

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

    subgraph FleetLanes["⚡ Specialized Fleet Execution Lanes"]
        direction TB
        UI["🎨 UI/UX & Graphic Mocking Lane<br/>Claude 3.5 Sonnet (claude-delegate)<br/>• Interactive HTML/SVG Prototypes<br/>• WCAG 2.1 AA a11y & Visual State"]
        Logic["🧠 Core Logic Lane<br/>OpenCode DeepSeek / Codex (opencode/codex-delegate)<br/>• Business Algorithms & State Machines<br/>• Concurrency & Query Optimization"]
        Data["📊 Data Lane<br/>OpenCode GLM / GPT-4o (opencode-delegate)<br/>• Schema Migrations & DTOs<br/>• Strict Boundary Validation"]
        Audit["🛡️ QA & Audit Referee Lane<br/>Gemini 1.5 Pro / Flash (agy-delegate / gemini)<br/>• Rule 6 Tabula Rasa Diff Audit<br/>• Sequential E2E Oracle Verification"]
    end

    Plan --> UI
    Plan --> Logic
    Plan --> Data
    UI --> Audit
    Logic --> Audit
    Data --> Audit
    Audit --> Arbiter
```

### Fleet Specialization Matrix

| Lane | Default Engine / Model | Primary Deliverables | Strict Boundary |
| :--- | :--- | :--- | :--- |
| **Lead Orchestrator** | **Google Antigravity** | Master plan, preflight, referee rulings, git commits | Supreme Arbiter; breaks ties after Round 2 |
| **🎨 UI/UX Mocking** | **Claude 3.5 Sonnet** | `.agents/mocks/*.html`, vector SVGs, a11y audit | **Visual Gate**: Zero logic coding until user approves mock |
| **🧠 Core Logic** | **OpenCode (DeepSeek/Codex)** | Domain models, algorithms, state engines | Adheres to Ponytail Rungs 1–3 before introducing abstractions |
| **📊 Data** | **OpenCode (GLM/GPT-4o)** | Migrations, DTOs, boundary parsers, schemas | Type-safe null safety; strict external input sanitization |
| **🛡️ QA & Referee** | **Gemini (Pro / Flash)** | Diff audits, call-chain tracing, E2E oracle runs | **Rule 6 Tabula Rasa**: Independent critique; no assumptions |

---

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
  ├── Verify all 11 external tools (Claude, OpenCode, Codex, Gemini, Playwright, E2E, Maestro)
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

### Enforced Compliance Gates

| Gate ID | Mandatory Rule | Required Evidence | Automatic Verdict |
| :---: | :--- | :--- | :---: |
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

### Key Metrics Monitored

* **Overall Efficacy Score (0–100 & Letter Grade)**: Synthesized from simplicity, test pass rate, and review cycle speed.
* **Ponytail Simplicity Index**: Percentage of architectural solutions resolved in Rungs 1–3 vs Rungs 6–7.
* **First-Turn Pass Rate**: Percentage of code patches approved in Round 1 without rework.
* **Arbiter Escalation Count**: Number of cross-lane disputes escalated to the Antigravity Supreme Arbiter.
* **Git Evidence & Provenance Trail**: Live table displaying commit SHAs, author lanes, verified scopes, and Ponytail debt tags.

---

## 🎛️ Tooling Inventory & Multi-Tier Scarcity Cascade

MACA dynamically adapts to your local machine using a **3-Tier Scarcity Cascade**:

```mermaid
flowchart TD
    Start["Task Initiated"] --> T1Check{"Are External Fleet CLIs<br/>installed in PATH?"}
    
    T1Check -->|Yes| Tier1["Tier 1: Full External Fleet<br/>• Claude Code CLI (@anthropic-ai/claude-code)<br/>• OpenCode CLI (opencode)<br/>• Codex CLI (codex)<br/>• Gemini CLI (@google/gemini-cli)<br/>• E2E Runner (e2e)<br/>• Mobile Runner (maestro)"]
    
    T1Check -->|No| T2Check{"Are Subagents / MCP<br/>available in IDE?"}
    
    T2Check -->|Yes| Tier2["Tier 2: IDE Subagents & MCP<br/>• Delegate via Antigravity Subagents<br/>• Execute tools via local MCP servers"]
    
    T2Check -->|No| Tier3["Tier 3: Single-Model Tabula Rasa<br/>• Antigravity resets context per turn<br/>• Simulates isolated adversarial personas<br/>• Strictly enforces max 2 review rounds"]
```

### Complete Tooling Matrix

| Tool | Category | Installation Command | Purpose |
| :--- | :--- | :--- | :--- |
| **`claude`** | AI Fleet CLI | `npm install -g @anthropic-ai/claude-code` | Claude 3.5 Sonnet UI/UX Mocking Lane |
| **`opencode`** | AI Fleet CLI | `brew install opencode` | Core Logic (DeepSeek) & Data (GLM) Lane |
| **`codex`** | AI Fleet CLI | `brew install codex` | Algorithmic logic & optimization |
| **`gemini`** | AI Fleet CLI | `npm install -g @google/gemini-cli` | Full-repo review & QA fallback lane |
| **`agy`** | AI Fleet CLI | `brew install agy` | Native Antigravity CLI delegation |
| **`e2e`** | E2E Engine | `npm install -g e2e` | Hybrid AI + Deterministic E2E testing |
| **`maestro`** | Mobile E2E | `curl -Ls 'https://get.maestro.mobile.dev' \| bash` | Mobile UI declarative flow automation |
| **`playwright`**| Web E2E | `npm install -g playwright` | Headless browser execution & DOM capture |
| **`adb`** | Mobile Device| Android Platform-Tools | Android emulator & physical device bridge |

---

## 🚀 Quickstart

### 1. Verify Environment & Preflight
Run the one-time deep diagnostic and preflight check:
```bash
# Run first-run preflight
python3 scripts/first_run_preflight.py

# Verify bootstrap readiness
./scripts/bootstrap.sh
```

### 2. Initialize a Task in Your Workspace
To audit an existing project or initialize a new feature with the Skill Ambassador:
```bash
python3 scripts/skill_ambassador_auditor.py --init-log /path/to/project --feature "FeatureName"
```

### 3. Verify Code with the E2E Scenario Engine
```bash
# Run scenario & call-chain verification suite
python3 scripts/scenario_and_callchain_engine.py --self-test
```

---

## 📜 License & Provenance

Licensed under the [MIT License](LICENSE).

Authored and maintained under the **Multi-Agent Collaborative Audit (MACA)** framework with **Google Antigravity** as Principal Consultant and Lead Orchestrator.
