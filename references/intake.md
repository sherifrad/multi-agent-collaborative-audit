# Intake: learn the direction of the project once, then reuse it

The skill is neutral. It cannot know whether it is helping a clinic app, a shop, a data pipeline or a game
until someone says so, and the wrong guess means the wrong packs, the wrong strictness and wasted tokens.
So the first time MACA runs in a project, the AI asks; afterwards it reads the answer.

## When to run intake
- No `.agents/PROJECT_PROFILE.md` yet -> run intake before Phase 0.
- Profile exists -> read it, do not re-ask. Re-ask only the item that a new task contradicts (for example a
  new payment feature in a project profiled as "no money handling"), and update the file.
- Unattended or no way to ask: infer from the repo and the task, write the profile with each guess marked
  `(inferred - confirm)`, choose the cautious option wherever risk is unclear, and list the guesses first
  in the report.

## How to ask (one short round, 5-7 questions, multiple choice where possible)
1. What is this project for, and who uses it? (free text)
2. What would a serious failure look like? (nothing important / annoying bug / money or data loss / harm to a person)
3. Which areas does it touch? (web/mobile UI, payments, data pipelines, low-level systems, health, other)
4. How do you build and test it? (commands, or "not set up yet")
5. Cost preference: economy (fewest tokens, lighter checks), balanced, thorough (deepest checks).
6. Who approves designs, thresholds and releases?
7. Which models or CLIs should do planning/review versus routine work? ("session default" is fine)

Offer your own guess in each option when the repo already hints at the answer, so the user can just confirm.

## What the profile drives
| Profile says | MACA does |
|---|---|
| Risk low, economy | Light path, tier ceiling T1, one reviewer, no `.agents/` ceremony |
| Risk medium, balanced | Light or Full by change size, ceiling T2, merged roles allowed |
| Risk high or safety-critical, thorough | Full path, tests-first, fresh-process reviewer, ceiling T3 at close |
| Domains list | Which `packs/*` load (see `packs/INDEX.md`) |
| Model tiers | Which model gets planner/reviewer vs runner roles |
| Approvals | Who is asked at mock, threshold and release gates |

Write the profile from `resources/templates/PROJECT_PROFILE.template.md`. Keep it short and stable; it is
read by every role and sits at the front of every brief (see `references/token_economy.md`).
