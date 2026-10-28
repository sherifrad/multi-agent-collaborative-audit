# Verification Principles (stack-neutral)

Agent-written tests often go green while the real app fails. Five habits cause most of it. For each one,
the fix and the reason.

## 1. Enter state step by step, never in bulk
Seeding a finished multi-step state (all observations, all orders, all edits) skips the transitions where
bugs live: draft clearing, anchor resets, reload/rehydration, ordering. Pre-seed only static, already
verified header data. Then apply each time-step or edit through the real save path, reloading between
steps: `step 0 -> save -> reload -> step 1 -> save -> reload`.

## 2. Assert exact outcomes at three levels
"Did not throw", `defined`, or `status == 200` pass when the code swallows an error and returns nothing.
For each oracle written in Phase 1, assert: (a) **domain**: exact result/state code; (b) **persistence**:
the exact stored rows/values (and audit records where relevant); (c) **visible**: the exact text, badge or
layout the user sees. Include one just-below-boundary case and one invalid-input case that must be rejected.

## 3. Test the wiring, not only the units
A function used from several screens/services can be right in one caller and wrong in another (different
units, defaults, parameters). List every caller (grep, or `scenario_and_callchain_engine.py --trace-dir
<dir> --symbol <fn>`), and run at least one flow per distinct caller with no internal mocks. Mock only
external boundaries (network, clock, hardware).

## 4. Check geometry and states for UI changes
Existence checks pass when a title is crushed to 20px. For headers/trays/dialogs, assert bounding boxes do
not overlap and the main text keeps a usable width at the narrowest supported viewport, in LTR and RTL.
Cover empty, loading, normal, alert/error and large-font states.

## 5. Fuzz identity and permission inputs
Admin or role checks written against one clean fixture break on emails typed into username fields,
case/whitespace variants, unverified providers, and `+alias` spoofs. Run the six-row matrix from
`scenario_and_callchain_engine.py --auth-fuzz-matrix` and require that unverified or aliased identities
are rejected.

## Evidence format for the ledger
For each check, record: command or test name, what it asserted, result, date. A claim without one of
these is not evidence.
