---
name: claude-delegate
description: Vendored Claude Code delegate skill (amElnagdy/delegate-skills compatible). Dispatches bounded UI/UX mocking and frontend tasks to the `claude` CLI, tracks touched files, supports `--read-only` plan mode, and never commits.
---

# Claude Delegate (`claude-delegate`)

Dispatch a bounded UI/UX or coding task to the `claude` CLI:

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo [--read-only]
```
