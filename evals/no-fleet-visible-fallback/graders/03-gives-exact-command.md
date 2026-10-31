---
type: llm
focus: trace
weight: 1
---

The agent writes one brief file and gives a scripts/fleet_review.sh command with --brief and --lane arguments (a `<skill>` path placeholder is fine, a missing or unrelated command is not), and the brief file holds the spec and diff only, without reviewer findings for the user to run in their own terminal.
