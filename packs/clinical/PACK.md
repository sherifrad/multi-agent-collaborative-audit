# Health / Safety-Critical Pack (directions only)
*Load when the project profile names a health, patient-data or medical-software purpose. Keywords in the repo are a hint to ask, never a trigger.*

**This pack holds directions, not domain data.** It never states a threshold, dose, unit limit, code list or
guideline value. Every concrete value comes from the project's own files (spec, `.agents/PROJECT_PROFILE.md`,
a `docs/` reference list) with a named source and approver. If a value is missing, the correct move is to ask
or flag it, never to fill it from memory. Example numbers in test prompts or recipes are illustrations only.

## Directions
1. **Every domain value is a claim.** For each threshold, dose, range or rule in the spec, record: source
   (document + version), who approved it, date. No source or approver -> report it as "unverified" and keep it
   out of the "passed" column.
2. **Separate reference from advice.** The UI and docs must not present a displayed reference value as a
   diagnosis or treatment instruction unless the project's regulatory owner has approved that wording.
3. **Typed units, no silent conversion.** Keep quantities in explicit units (scaled integers or typed
   wrappers). Test every unit boundary and every conversion path; fail on implicit truncation or float coercion.
4. **Time-dependent rules are tested in sequence.** Seed only static header data; enter each time step through
   the real save and re-evaluation path, reloading between steps (`references/verification_principles.md`).
5. **Handoff keeps state.** When work passes between users or shifts, check that open alerts, next-due
   actions, current stage and who-did-what survive, and that logout never wipes stored records or audit data.
6. **Alerts stay distinct.** Messages from owners or seniors must not imitate or hide safety alerts, and must
   not slow the fast-entry workflow. Verify both.
7. **Records are append-only.** No hard delete of regulated records; corrections add a new state and keep the
   old one. Every state change has an attributable audit entry.
8. **No personal data in logs, crash reports or analytics.** Test by searching captured output for the
   fixture's identifying values.
9. **Usable under real conditions.** Check the smallest supported screen, large text, RTL if used, and input
   targets suited to the stated user environment (for example gloved hands). Take the sizes from the profile.
10. **Name the applicable standards in the profile**, not here, and map each to a test or document. The skill
    only checks that the mapping exists.

## Scripts and recipes
Run when the profile names this pack, or the work touches auth, schemas or deletions:
- `python3 scripts/lint_samd_invariants.py --scan-dir <source dir>` (hard-delete, identity checks, resource budget)
- `python3 scripts/scenario_and_callchain_engine.py --auth-fuzz-matrix`, and `--mode custom` with scenarios the project supplies
- `references/e2e_and_call_chain_testing.md` (stack recipes; its sample data is illustrative)
