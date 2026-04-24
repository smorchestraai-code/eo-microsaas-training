---
description: Where am I in the build? What command do I run next?
---

# /eo-guide

Activate the **eo-guide** skill in **Mode 1 (Returning Student)**.

Execute the returning-student sequence:
1. Resolve workspace root (worktree-aware: honor `$GIT_WORK_TREE` or `git rev-parse --show-toplevel`, never `pwd`)
2. Read language preference from project `CLAUDE.md` frontmatter, `MENA:` flag, or `.claude/settings.json`
3. Run filesystem scan — collect all 10 signals
4. Evaluate phase detection state machine (first match wins)
5. Trigger safety rail (Mode 3) if state is inconsistent — never recommend `/7-eo-ship` or destructive action
6. Reconcile `_dev-progress.md` + log any diff
7. Print one-screen recommendation: phase + next command + ETA + story + sprint

Output in Arabic-first Gulf tone if `lang: ar` or `MENA: yes`; English otherwise.

Read `skills/eo-guide/SKILL.md` for complete instructions.

## Arguments

None. `/eo-guide` reads filesystem every time.

## When to run

- After opening a fresh Claude Code chat in the project (the whole reason this exists)
- After you've been away for a day or more
- When unsure which command is next
- After any `/eo-*` command that feels like it might have left inconsistent state
