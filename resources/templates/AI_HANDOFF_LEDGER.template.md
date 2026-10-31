# Handoff ledger

Machine-readable records are single lines starting with the tag. The referee (`skill_ambassador_auditor.py`)
reads these, not the prose around them. Keep one record per line; use `key=value`, quote values with spaces.

## 1. Handoffs

| ID | Time (ISO) | From | To | Artifacts | Status | Summary |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| H-001 | YYYY-MM-DDTHH:MM | orchestrator | test-designer | .agents/SPEC_AND_AUDIT.md | sent | spec and oracles |

## 2. Reviews (max 2 rounds)

Reviewer must differ from author. `independence` is multi-vendor (2+ model families), same-family,
single-model, or same-model (a fresh process of the same model). `evidence` is a file under the repo or `.agents/`,
or the command that was run.

REVIEW: id=R-1 author=<lane/model> reviewer=<lane/model> independence=<level> round=1 evidence=<path or command> verdict=<pass|blockers|deferred>

Findings (file:line, class, why), classified Hard Blocker / Deferred Shortcut / Pass: `[...]`

## 3. Approvals and assumptions

A person must approve these; the orchestrator cannot approve for them. If nobody can answer (unattended), do not
write an APPROVAL: write an ASSUMPTION, take the cautious option, and stop short of the gated action.

APPROVAL: what=<ui-mock | vendor:<name> | tier-ceiling:<n> | write-lane:<name>> by=<person> date=<YYYY-MM-DD>
ASSUMPTION: what="<decision taken without an answer>" default="<option chosen>" needs-confirmation=yes

## 4. Verification

Test results live in `.agents/EVIDENCE.json` (written by `impact_and_cache.py run`). Summary line for the report:
`Ran N | Reused N (identical deps) | Deferred N (not run)`

## 5. Debt and deferred shortcuts

| Item | Why accepted | Revisit by |
| :-- | :-- | :-- |
