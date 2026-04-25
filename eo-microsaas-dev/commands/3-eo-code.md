---
description: Execute a planned feature via TDD. Writes test first, then minimal impl, then refactors.
---

# /3-eo-code

**Pillar:** Boris #2 (Subagent) + #5 (Elegance) — via superpowers TDD
**When to run:** After `/2-eo-dev-plan` is approved.

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
1. Verify plan exists (from /2-eo-dev-plan)
2. Read architecture/tech-stack-decision.md → respect SaaSfast mode
3. For each AC:
   a. Red → green → blue via superpowers:test-driven-development
      (fallback: internal TDD loop — red test first, minimal impl, refactor)
   b. If >1 independent file → superpowers:subagent-driven-development
      (fallback: sequential edits)
4. Run elegance-pause before final commit
5. Stage + commit with conventional message + @AC-N.N refs
```

## Hidden plumbing (graceful degrade)

| Step | First choice | Fallback |
|------|--------------|----------|
| TDD loop | `superpowers:test-driven-development` | Internal red→green→blue loop |
| Parallel file edits | `superpowers:subagent-driven-development` | Sequential edits |
| Elegance review | `elegance-pause` (ships with this plugin) | — (always present) |

## Arguments

`$ARGUMENTS` — optional: specific AC to focus on (e.g., "AC-1.2")

## Exit criteria

- All targeted ACs have passing tests
- Elegance pause block in commit message
- No `.skip` tests in the committed range

## After green — update tracker

Update `_dev-progress.md` row for this story:
- `Status` = `🔨 coding` (still coding) or `🧪 scoring` (all ACs green, time to `/5-eo-score`)
- `Tests` = `{passing}/{total} passing`
- `Last updated` = today; `Last command` = `/3-eo-code {arg}`
