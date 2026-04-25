---
description: Lift the session edit scope set by /eo-freeze.
---

# /eo-unfreeze

**Purpose:** Remove the edit boundary set by `/eo-freeze` so Claude can write anywhere in the repo again.

## What it does

1. **Tries `gstack:unfreeze` first** if the `gstack` plugin is installed — symmetric to `/eo-freeze`.
2. **Fallback** — clears the session's scoped-path rule. Writes outside the previously frozen path are allowed again.

## Arguments

None. `/eo-unfreeze` always lifts completely. If you want to re-scope, run `/eo-freeze <new-path>` after.

## When to run

- You finished the focused task that `/eo-freeze` was protecting, and the next task legitimately spans more files.
- You hit an "edits restricted to …" refusal and the refusal is wrong — the edit really does need to happen outside the frozen path.

## Output

```
☀️ Freeze lifted. Writes allowed across the repo again.
```

If no freeze was active:
```
No freeze active — nothing to lift.
```

## Integration

- **Pairs with:** `/eo-freeze` (set the boundary)
- **Auto-fires on:** new session start. You never carry a freeze across sessions.
