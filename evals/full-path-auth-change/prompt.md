---
tags: [maca]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Use MACA. We need to change who counts as an admin in src/auth.js: today anyone whose username is 'admin' is admin. Make it require a verified identity claim (the token's `role` claim must be 'admin' and `verified` must be true). This is the permission check for our billing app.
