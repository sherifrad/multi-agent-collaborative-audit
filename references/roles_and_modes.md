# Roles and Modes

## The two modes (complementary, not competing)

| | **Implementation mode** | **Testing mode** |
|---|---|---|
| Question it answers | "Build the change correctly" | "Prove, with evidence, that it works and nothing else broke" |
| Entry | Feature, fix, refactor request | Audit / verify / review request, or after implementation |
| Output | Code + change summary + new `TEST_MANIFEST.json` entries | Verdict + `EVIDENCE.json` + defects as failing tests |
| Cost control | Fast checks only (Tier 0-1) on touched code | Impact-selected tests, cached passes reused (see `test_economy.md`) |
| Who | Builder lanes | Test designer, test runner, adversarial reviewer |

**How they fit together.** The spec's *outcome oracles* are the contract. Testing mode turns each oracle
into tests (before the builders start, on the Full path, so tests cannot be bent to fit the code). Implementation
mode makes them pass. A defect found in testing mode becomes a failing test and goes back to implementation
mode; max 2 rounds, then the user decides. Testing mode also runs alone (audit existing code, pre-release
regression) and implementation mode can run alone on the Light path with one reviewer.

**Choosing the mode.** "build / add / fix / refactor" -> implementation, then a proportionate testing pass.
"audit / verify / review / is this safe / regression" -> testing. State the mode and weight in one line.

## The Orchestrator

The orchestrator is the agent that talks to the user in this session (or the one named in `.agents/fleet.json`
under `orchestrator`). It is a router and record-keeper, not a builder. Duties:

1. Pick mode and weight (Light or Full) and say so.
2. Write or approve the spec and outcome oracles; hold the single source of truth in `.agents/`.
3. Dispatch lanes with bounded briefs and collect results; keep the handoff ledger.
4. Run `impact_and_cache.py select`, show the RUN/REUSE/DEFER plan, and enforce the tier ceiling.
5. Break ties after two review rounds by escalating to the user with both positions, never by overruling silently.
6. Report honestly: what ran, what was reused (and why), what was deferred, what was not verifiable.

It must not: write the app code it later approves (Full path), grade its own tests, mark gates passed
without evidence, or expand scope silently. On the Light path it may do the small build itself, but the
reviewer still cannot be the author.

## Role map

| Role | Mode | Responsibility | Receives | Never does | Model guidance |
|---|---|---|---|---|---|
| **Orchestrator** | both | Routing, spec ownership, ledger, user communication, final report | Everything | Builds Full-path code; approves own work | Strongest available |
| **UI/UX lane** | impl | Mock, screens, states, RTL/a11y | Spec slice, approved mock | Changes logic/data contracts | Design-strong model |
| **Core Logic lane** | impl | Rules, algorithms, call-chain wiring | Spec slice, interfaces | Touches schema without the Data lane | Strong coder |
| **Data lane** | impl | Schema, migrations, serialization, units | Spec slice | Hard-deletes clinical records | Strong coder |
| **Test Designer** | test | Turns oracles into tests and a `TEST_MANIFEST.json`, writes boundary and negative cases | Spec only (not the builders' reasoning) | Reads the implementation before writing tests | Strong reasoning; ideally different from builders |
| **Test Runner** | test | Runs `select`, executes RUN tests, records evidence | Manifest + commands | Judges design; edits code | Cheapest reliable model or plain scripts |
| **Adversarial Reviewer** | test | Audits diff against spec and call-chain map, classifies findings | Spec + diff + impacted-test results | Sees the author's reasoning; fixes code | Different model family from the author when possible |
| **Referee** (Full only) | test | Checks that gates have real evidence, writes the compliance log | Ledger + evidence | Writes app code; accepts keyword-only evidence | Cheap model + `skill_ambassador_auditor.py` |

One model may hold several roles only if the independence pairs hold: Test Designer != Builder,
Reviewer != Author. When that is impossible, use a fresh process for the second role (a new subagent or
`claude -p` with only the allowed inputs) and label the result "same-model review".

## Handoffs (all written to `.agents/AI_HANDOFF_LEDGER.md`)

`Orchestrator -> Test Designer` (spec) -> `Test Designer -> Orchestrator` (manifest, failing tests) ->
`Orchestrator -> Builders` (briefs + manifest) -> `Builders -> Orchestrator` (diff + change summary) ->
`Orchestrator -> Runner + Reviewer` (diff, manifest) -> `Runner/Reviewer -> Orchestrator` (evidence, findings).
Each entry: from, to, artifacts, status, one-line summary.
