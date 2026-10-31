# Fleet profiles: who gets which kind of fleet

MACA does not keep its own list of vendors. Three things decide the fleet, and each has one owner:

| Question | Source of truth | Who changes it |
| :-- | :-- | :-- |
| Which CLIs exist and are signed in? | `delegate-setup` discovery (`discover.mjs`) | the machine |
| Which CLI does which kind of work (lanes, model, effort)? | the user's `delegate-fleet.v1` config (global, or project after approval) | the user, via the `delegate-setup` skill |
| May a CLI receive this project's code, or write files? | `.agents/PROJECT_PROFILE.md`: `Approved vendors`, `Write-lane permissions` | a person (inferred values grant nothing) |

`python3 scripts/fleet_select.py --cwd <repo>` combines the three into a plan. It is read-only.

## The three archetypes

| Archetype | What the user has | Plan | Best independence |
| :-- | :-- | :-- | :-- |
| solo | no approved external CLI (new user, locked-down company, offline) | builder, test designer and reviewer are fresh-context Claude subagents | same-model: say so in the report |
| pair | one approved CLI of another model family | Claude builds; that CLI reviews read-only | multi-vendor |
| fleet | two or more approved CLIs of different families | as pair, plus a second reviewer of a third family; findings raised by 2+ families are strong evidence | multi-vendor |

An external CLI serving the same model family as the orchestrator (for example agy running a Claude model) does not
raise independence. Unknown families never count as independent.

## Moving up an archetype

1. Install and sign in to the CLI (the plan lists unauthenticated ones).
2. Run the `delegate-setup` skill to create lanes (it writes only after you approve).
3. Add the vendor to `Approved vendors` in the profile. To let it edit files, also name it in `Write-lane permissions`
   (for example `codex: workspace-write`). Reviewers never need write access.
4. Re-run `fleet_select.py`.

## Roles

| Role | Default | External only if |
| :-- | :-- | :-- |
| builder | fresh Claude subagent | the vendor is approved and named in `Write-lane permissions` |
| test designer | fresh Claude subagent (sees the spec, not the code) | same as builder |
| reviewer | approved vendor of another family, `--read-only` | falls back to a labelled same-model review |
| second reviewer | a third family, `--read-only` | only in the fleet archetype |

Gemini models are reached through `agy --model gemini-...` (upstream ships no separate Gemini relay).
