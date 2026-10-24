---
name: opencode-delegate
description: Vendored OpenCode delegate skill (amElnagdy/delegate-skills compatible). Dispatches bounded Core Logic (DeepSeek) or Data (GLM) briefs to the `opencode` CLI, tracks touched files, supports `--read-only` plan mode, and never commits.
---

# OpenCode Delegate (`opencode-delegate`)

Dispatch a bounded task to the `opencode` CLI:

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo [--model <provider/model>] [--read-only]
```
