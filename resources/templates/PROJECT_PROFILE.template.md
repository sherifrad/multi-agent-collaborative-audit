# Project Profile

> Seeded by intake (`references/intake.md`), confirmed by the user. Kept stable on purpose: it is the first
> thing every role reads, so it works as a cache-friendly prefix. Edit it deliberately; do not append
> per-task notes here (use the ledger).

- **Purpose** (what the app is for, in the user's words):
- **Users / audience** (who uses it, how many, what environment):
- **Direction** (what "done well" means here; what must never happen):
- **Domains / packs** (core, web-ui, fintech, systems, data-etl, clinical; any name needs an installed pack in packs/):
- **Risk level** (low | medium | high | safety-critical) and why:
- **Stack and commands** (language, build, test, lint; how to run one test):
- **Cost preference** (economy | balanced | thorough): default tier ceilings follow this, see `references/token_economy.md`
- **Model tiers** (planner/reviewer: ___ ; builder: ___ ; runner/cheap tasks: ___ ; or "use session default")
- **Approvals** (who approves UI mocks, thresholds, releases):
- **Approved vendors** (external CLIs/APIs allowed to receive code and specs: opencode, codex, gemini, agy; write `none` if none. A lane listed in fleet.json is NOT an approval):
- **Write-lane permissions** (may an external lane edit files? `none` = read-only review only; or name the vendor and mode, e.g. `codex: workspace-write`):
- **Max tier ceiling without asking** (T1-T4):
- **Unattended policy** (what the AI may decide alone, what must wait for a human; default: see SKILL.md section 5):
- **Known constraints** (deadlines, compliance, offline needs, languages/RTL):
- **Confirmed by / date:**

Items marked `(inferred - confirm)` were guessed from the repo and still need the user's answer.
