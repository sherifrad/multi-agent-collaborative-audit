# Project Profile

> Seeded by intake (`references/intake.md`), confirmed by the user. Kept stable on purpose: it is the first
> thing every role reads, so it works as a cache-friendly prefix. Edit it deliberately; do not append
> per-task notes here (use the ledger).

- **Purpose** (what the app is for, in the user's words):
- **Users / audience** (who uses it, how many, what environment):
- **Direction** (what "done well" means here; what must never happen):
- **Domains / packs** (core, ui, fintech, systems, data-etl, clinical; UI is also auto-detected from changed files):
- **Risk level** (low | medium | high | safety-critical) and why:
- **Stack and commands** (language, build, test, lint; how to run one test):
- **Cost preference** (economy | balanced | thorough): default tier ceilings follow this, see `references/token_economy.md`
- **Model tiers** (confirm models in `.agents/model_catalog.json`; `python3 scripts/model_router.py catalog --write` seeds it as `inferred`; or write "use session default")
- **Max frontier calls** (a human sets this; the router stops at the limit and never raises it; blank = no limit):
- **Max standard calls** (same rule):
- **Max rounds** (review/fix rounds before stopping):
- **Risk paths** (globs or words that always mean high risk, comma separated, e.g. `billing/*, auth/*`):
- **Downgrade paths** (human only; `glob=level` with level 0-2, comma separated, e.g. `evidence/**=0, **/ui/**=1`; lowers criticality for paths that over-escalate; Risk paths still win):
- **Approvals** (who approves UI mocks, thresholds, releases):
- **Human approvers** (optional; people allowed to record APPROVAL lines):
- **Approved vendors** (external CLIs/APIs allowed to receive code and specs: opencode, codex, agy; write `none` if none. A lane in the delegate-setup config is NOT an approval):
- **Write-lane permissions** (may an external lane edit files? `none` = read-only review only; or name the vendor and mode, e.g. `codex: workspace-write`):
- **Max tier ceiling without asking** (T1-T4):
- **Unattended policy** (what the AI may decide alone, what must wait for a human; default: see SKILL.md section 5):
- **Known constraints** (deadlines, compliance, offline needs, languages/RTL):
- **Confirmed by / date:**

Items marked `(inferred - confirm)` were guessed from the repo and still need the user's answer.
