# Token and Cost Economy

Goal: the same quality for fewer paid tokens. Four levers, in order of payoff.

## 1. Make the provider's prompt cache hit
What the provider documents (Anthropic prompt caching, checked against its docs): a cache **read** costs a
fraction of normal input (0.1x on most models; lower, 0.05x, on some newer ones), a 5-minute **write** costs
1.25x and a 1-hour write 2x; the cache matches an **exact prefix** in the order tools -> system -> messages,
so any change early in the prompt invalidates everything after it; the default lifetime is 5 minutes and is
refreshed each time the entry is used; very short prompts are not cached at all. The skill cannot create
this cache, but the way work is structured decides whether it hits:

- **Stable first, volatile last.** Order every brief as: project profile, then spec/oracles, then role
  instructions, then the task-specific part. Never put timestamps, run ids or changing counters at the top.
- **One shared prefix for all roles.** Build lane briefs from the same leading block
  (`.agents/BRIEF_PREFIX.md` = profile + spec summary + oracle list) followed by a short role-specific
  section. Parallel subagents then reuse the same cached prefix instead of each paying for its own.
- **Do not edit the early part mid-session.** Changing the profile, the tool list or the spec header
  invalidates the cached prefix; put corrections in the ledger or at the end.
- **Keep sessions alive.** A new chat that re-uploads the same files pays full price again; continue the
  session or point to files by path. Gaps longer than the cache lifetime lose the entry, so batch related
  work close together.
- **Do not re-read what has not changed.** Cite the earlier ledger entry or evidence record instead.

## 2. Reuse results instead of recomputing them
- `scripts/impact_and_cache.py` reuses passed tests whose dependency hash is unchanged
  (`references/test_economy.md`). Extend the same idea to reviews: a reviewer verdict on an unchanged diff
  is cited, not repeated.
- Prefer a deterministic script over a model for anything mechanical (hashing, diffing, grepping callers,
  running a test command, formatting a report).

## 3. Save repeated scripts (harness library)
Before writing any helper script run `python3 scripts/harness.py check --ws <ws> --need "<what it does>"`.
- `FOUND`: run it with `harness.py run`; do not rewrite it.
- `NEW`: first time; write it inline.
- `PROMOTE`: second time; write it once, `register` it (with a self-test command), and call it by name from now on.
If the user says the work recurs ("every week", "for each export"), skip the wait: write and register it on
first use. A registered script costs about nothing to reuse and cannot drift, because its hash is verified before each
run. General-purpose scripts can be `promote`d to the global library for use in other projects.

## 4. Put the right model on each job
Strongest model: spec, oracle design, adversarial review. Cheaper model or a plain script: running tests,
collecting evidence, formatting. The profile's "model tiers" line records the choice. The role table in
`references/roles_and_modes.md` says which roles are cheap.

## Measure it
Ask the user for (or read, if available) the cache-read share of tokens and the number of fresh sessions
that re-uploaded the same files. A low cache-read share means prefixes are changing or sessions are being
restarted; fix those first. In reports state: tests ran/reused/deferred, scripts reused from the harness,
and reviews reused.
