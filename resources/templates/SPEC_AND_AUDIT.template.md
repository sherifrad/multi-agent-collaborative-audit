# Specification and audit (SPEC_AND_AUDIT.md)

## 1. Requirement
* **Objective** (the user's words): `[what must be true when this is done]`
* **Scope**: `[in scope / out of scope]`
* **Active packs**: `[from .agents/PROJECT_PROFILE.md]`
* **Task queue item**: `[id in tasks/current_task.md or .agents/PLAN_TASKS.md]`

## 2. Audit of the existing code
* **Reviewed** (file:line): `[...]`
* **Known fragilities**: `[bugs, silent truncation, missing validation]`
* **Hazards** (security, privacy, money, safety): `[...]`

### Call-chain map
Callers and callees of everything that will change. Fill at least one real row; the referee rejects placeholders.

| Target | Upstream callers | Downstream callees | Contract risks (units, types, nulls) |
| :-- | :-- | :-- | :-- |
| `[fn or class]` | `[callers]` | `[callees]` | `[risk]` |

## 3. Target specification
* **Interfaces / signatures**: `[...]`
* **Data and state flow**: `[...]`
* **Failure modes**: `[how every edge case is handled and reported, with no false success]`

## 4. Outcome oracles
One line per observable result that proves success, at the lowest level that can show it (domain value, stored
record, visible output). Tests are written from these. Format is fixed so the referee can count them:

- ORACLE-1: `[exact result, e.g. after add("x"), list() has length 1]`
- ORACLE-2: `[a negative or boundary case, e.g. empty input is rejected and nothing is stored]`

## 5. UI mock (UI work only)
* **Mock path**: `[.agents/mocks/<feature>.html]`
* **Approval**: recorded in the ledger as `APPROVAL: what=ui-mock by=<person> date=<YYYY-MM-DD>`. Without it the UI logic is not built.
