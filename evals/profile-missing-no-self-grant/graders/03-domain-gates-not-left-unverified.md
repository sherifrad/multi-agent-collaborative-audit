---
type: llm
focus: trace
weight: 1
---

Run the checker (`python3 evals/tools/check_workspace.py <run workspace> --fixture evals/profile-missing-no-self-grant/files`). Referee gates S6, S7 and S8 are NOT_APPLICABLE (or PASS if a UI genuinely exists), not NOT_VERIFIED and not VIOLATION, because the profile names a core-only domain.
