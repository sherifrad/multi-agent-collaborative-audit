---
name: agy-delegate
description: Vendored Google Antigravity delegate skill (amElnagdy/delegate-skills compatible). Dispatches bounded QA, E2E verification, or read-only audit briefs to the `agy` CLI, tracks touched files, and never commits.
---

# Antigravity Delegate (`agy-delegate`)

Dispatch a bounded QA/audit or coding task to the `agy` CLI:

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo [--read-only]
```
