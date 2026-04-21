---
description: Execute a planned feature via TDD. Writes test first, then minimal impl, then refactors.
---

# /eo-code

**Pillar:** Boris #2 (Subagent) + #5 (Elegance) — via superpowers TDD
**When to run:** After `/eo-plan` is approved.

## What it does

1. For each AC in the plan:
   - Un-skip the placeholder test (from handover-bridge)
   - Write the test properly (red)
   - Implement minimal code to pass (green)
   - Refactor with elegance pause (blue)
2. Dispatch subagents for independent work (parallel components)
3. After implementation: run elegance-pause skill
4. Append any corrections to `.claude/lessons.md` via lessons-manager

## Workflow

```
1. Verify plan exists (from /eo-plan)
2. For each AC:
   a. Use superpowers:test-driven-development
   b. If >1 file affected → superpowers:subagent-driven-development
3. Run elegance-pause before final commit
4. Stage + commit with conventional message + @AC-N.N refs
```

## Arguments

`$ARGUMENTS` — optional: specific AC to focus on (e.g., "AC-1.2")

## Exit criteria

- All targeted ACs have passing tests
- Elegance pause block in commit message
- No `.skip` tests in the committed range

## After green — update tracker

Update `_dev-progress.md` row for this story:
- `Status` = `🔨 coding` (still coding) or `🧪 scoring` (all ACs green, time to `/eo-score`)
- `Tests` = `{passing}/{total} passing`
- `Last updated` = today; `Last command` = `/eo-code {arg}`
