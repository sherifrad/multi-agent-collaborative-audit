# Test Economy: deep verification without re-running everything

Goal: spend tokens and minutes only where a change could have altered a result, while never reporting a
pass that was not earned.

## 1. Tiers

| Tier | What | Typical cost | Default use |
|---|---|---|---|
| T0 | Compile, type-check, lint, static MACA linters on changed files | seconds | Every change |
| T1 | Unit and boundary tests for touched symbols | seconds-minutes | Every change |
| T2 | Integration test per impacted caller (call-chain map) | minutes | Full path, each round |
| T3 | Sequential E2E scenarios touching the change | minutes-tens of minutes | Once at close, only impacted scenarios |
| T4 | Device runs, profiling, full replay, security sweep | long | Release gate, or when the user asks |

Default ceilings: Light = T1. Full per-iteration = T2. Full at close = T3. T4 only on request or release.
Raise the ceiling when risk demands it (safety rule changed, auth/permission touched, migration), and say why.

## 2. Evidence cache

`scripts/impact_and_cache.py` keeps `.agents/EVIDENCE.json`. A test is **reused** only if it passed before
and the SHA-256 of everything in its `deps` (plus its command) is unchanged. Rules, in order:

1. Above the tier ceiling -> DEFER. Listed in the report as *not run*, never counted as a pass.
2. `always: true` -> RUN. Use sparingly, for cheap T1 safety/boundary tests of rules that were edited.
3. Never run, or last result was fail -> RUN. Failures are never cached.
4. `deps` match no files -> RUN (cannot prove nothing changed).
5. Hash differs -> RUN, and the plan names the changed files.
6. Otherwise -> REUSE.

Workflow per round:

```
python3 scripts/impact_and_cache.py select --ws <ws> --max-tier 2     # show plan: RUN / REUSE / DEFER
# run only the RUN lines, then for each result:
python3 scripts/impact_and_cache.py record --ws <ws> --id <id> --status pass|fail --note "<evidence>"
python3 scripts/impact_and_cache.py status --ws <ws>                   # fresh / stale / never / failed
```

Declare `deps` generously: the code under test, **its callers**, fixtures, config, and the test file. A
`deps` list that is too narrow causes false reuse; too wide only costs a rerun. Use
`impact_and_cache.py deps-suggest --root <repo> --symbol <fn>` to list callers.

## 3. Keeping reviewers cheap

- Give the reviewer the diff, the spec's oracle list, and the impacted-test results; not the repo or the
  transcript. Ask for findings only, as `file:line - class - why`.
- Test runner output: keep the summary line for passes, the full trace only for failures.
- Do not re-review code unchanged since a PASS verdict; point at the earlier ledger entry.

## 4. Safety net against stale confidence

- Run `invalidate --all` and a full T3 replay at the release gate or after dependency/config upgrades.
- If the manifest is missing or a test has no `deps`, run it; never skip on a guess.
- Report format: `Ran 6 | Reused 14 (identical deps) | Deferred 3 (T4, not run)`.
