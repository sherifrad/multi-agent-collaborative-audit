---
tags: [maca]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Use the MACA skill. In src/paginate.js the last page is dropped when item count is an exact multiple of page size (off-by-one in pageCount). Fix it and have someone other than you review it. Keep it light, it's a one-line change.
