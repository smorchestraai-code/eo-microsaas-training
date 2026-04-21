---
description: Compact build dashboard — status only, no coaching.
---

# /eo-status

Activate the **eo-guide** skill in **Mode 2 (Compact Dashboard)**.

Execute:
1. Resolve workspace root (worktree-aware)
2. Run filesystem scan — same 10 signals as `/eo-guide`
3. Print the status table only. No next-step recommendation. No coaching. No Arabic wrapping (status stays compact across languages).

Use this when you just want a snapshot — not advice.

Output format:
```
EO Build Dashboard — {PROJECT_NAME}
====================================
Bootstrap:   ✅ / ⚠️
BRD stories: {N} total
Story {N}:   {symbol} {state} — {evidence}
Latest score: {composite} ({story draft}, {date})
Lessons: {count} active
CI: last run {status} ({time ago})
```

For coaching + next step, use `/eo-guide`.
