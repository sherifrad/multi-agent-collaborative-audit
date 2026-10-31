# Model routing: which model, how much reasoning, for which role

The skill's core job is to spread roles over models on purpose. `scripts/fleet_select.py` decides who is available and allowed
(vendor level); `scripts/model_router.py` decides which model and which reasoning effort each role gets. This page records the
rules and why. They came from a three-model discussion (agy on Gemini 3.8 Flash, a Claude adviser, the orchestrator); the Gemini CLI
was not signed in and opencode's free quota was exhausted, so those two did not take part.

## Tiers and effort (two separate dials)
| Tier | Meaning | Typical models (the user confirms them) |
| :-- | :-- | :-- |
| light | cheap, fast, mechanical work whose result a command checks | haiku, flash, `*-free`, lite, mini |
| standard | the working tier for judging roles | sonnet, mid-size models |
| frontier | high-assurance reasoning, used on risk or after a blocker | opus, fable, pro, argon-high |

Effort is low, medium or high. Some CLIs bake effort into the model id (`gemini-3.8-flash-high`); then the id decides and no
`--effort` flag is sent. Names only suggest a tier: every non-Claude catalog entry from discovery is `source: inferred` (the four Claude aliases are `builtin`) until a person confirms
it in `.agents/model_catalog.json`. An inferred model, or one with an unknown family, never acts as the frontier reviewer.

## Role defaults (rules, in `model_router.py`)
| Role | Default | Risk medium | Risk high / Full-path review | After failures or a Hard Blocker |
| :-- | :-- | :-- | :-- | :-- |
| helper / runner | light, low | same | same | same (mechanical only) |
| builder | standard, medium | standard, medium | standard, high | 2 failures: effort high; 3: frontier; blocker: frontier high |
| test designer | standard, medium | standard, high | frontier, high | same as default (tests are the oracle: never a light model) |
| reviewer | standard, medium | standard, high | frontier, high | frontier, high |
| second reviewer (high risk only) | standard, high | same | frontier, high; a different model, ideally another family | frontier, high |

Judging roles never use a light model. Escalate effort first, then tier; a light role goes straight to standard.

## Risk is measured, not reported
`model_router.py risk` scores the working diff with no model call: sensitive words added (auth, token, secret, payment,
refund, balance, migration, permission, ...), risky files (migrations, schema, CI, lockfiles, permissions), tests removed or
weakened, the profile's `Risk paths`, and size. Failures and blockers also come from what the orchestrator measured (test exit
codes, the ledger), never from the routed agent's own claims, because an agent could use them to keep itself on a cheap tier.

## Criticality: project map, task kind and diff
The router combines three measured signals: `effective criticality = max(task kind, project map, diff risk)`, on a 0-3 scale
(0 docs, 1 low, 2 medium, 3 high). It maps to the risk class the table above uses (docs, low, medium, high).
- **Project map** (`scripts/project_map.py scan --cwd . --write` -> `.agents/PROJECT_MAP.json`): each file gets an aspect and a
  level from its path, then its content (schema, auth and money patterns), then git fix-commit frequency (skipped with no or
  shallow history). Level 3 is auth/security, money/billing, data schema and migrations; 2 is core logic, API, data access;
  1 is tests, CI, UI, config, dependencies; 0 is docs and vendor. A path missing from the map counts as 2, never lower; with no
  map at all the router judges by path name. `project_map.py summary` prints the <=15 line block for AGENTS.md. Tools read the
  map; agents do not load it. `Risk paths` in the profile can only raise a path to 3.
- **Task kind**: inferred from the changed paths and diff (docs-only, tests-only, code, sensitive). The orchestrator may pass
  `--kind` or `--paths` (files about to change); a declared kind can only raise criticality. The diff content always beats a label:
  a change called docs-only that adds `ALTER TABLE` or an API key is routed frontier/high.
- A docs-only change gets a judging role at standard tier with low effort; nothing is ever routed to a light model for judging.

## Fallback when quota runs out
| Role | Fallback |
| :-- | :-- |
| helper / runner | any model |
| builder, test designer | same tier on another vendor; one tier down only if a frontier review follows |
| reviewer on risk or Full path | same tier, a family other than the builder's; otherwise stop with `QUOTA_EXHAUSTED` (never a weaker reviewer) |

## Budget
Counts, not dollars (subscriptions and free tiers have no per-call price): the profile's `Max frontier calls`, `Max standard
calls`, `Max rounds`. A human sets them; at the limit the run stops with `BUDGET_EXHAUSTED` and reports what stayed unreviewed.
Every decision is appended to `.agents/ROUTING_LOG.jsonl` with its reason.

## Solo mode (Claude only)
`resources/subagents/` holds the roster: `maca-builder`, `maca-test-designer`, `maca-reviewer`, `maca-second-reviewer` (high risk
only), `maca-helper`. The referee is a script, not a subagent. The router names the model to pass when spawning
(for example sonnet for a routine review, opus at high effort for a risky one). Every result is labelled same-model review.

## Free models first
For light work the router prefers `opencode/*-free` models. They have a daily limit, so the chain falls back to the next candidate.

## Gemini
The standalone Gemini CLI is no longer supported for Gemini Code Assist for individuals (its sign-in now says to migrate to the Antigravity
products), so MACA does not use it. Reach Gemini models through `agy --model gemini-...`, which the upstream agy relay supports.
