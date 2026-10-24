---
name: codex-delegate
description: Vendored Codex delegate skill (amElnagdy/delegate-skills compatible). Dispatches bounded coding or verification briefs to the OpenAI Codex CLI (`codex`), tracks touched files, enforces read-only mode when requested, and never commits.
---

# Codex Delegate (`codex-delegate`)

Dispatch a bounded coding or verification task to the `codex` CLI:

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo [--read-only]
```
