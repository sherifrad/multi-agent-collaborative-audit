# Vendored: amElnagdy/delegate-skills

Source: https://github.com/amElnagdy/delegate-skills (MIT, see LICENSE)
Synced commit: 3aa72d6 (2026-10-14, "Merge pull request #145 ... codex-background-delegation")
Copied unmodified: skills/agy-delegate, claude-delegate, codex-delegate, opencode-delegate, delegate-setup.

Rules
- No local edits to these folders. To change behaviour, pass the relay's own flags (`--read-only`, `--model`, `--timeout`, `--out-dir`) or send a fix upstream.
- To update: clone the upstream repo to a scratch dir, copy the same folders over, update the commit above, run `scripts/first_run_preflight.py`.
- The old local `gemini-delegate` and `shared_relay.mjs` were removed: the Gemini CLI no longer signs in for individuals. Reach Gemini models through `agy --model gemini-...`.
