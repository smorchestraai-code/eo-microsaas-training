---
description: Scope edits to a folder for this session — "only touch here, don't wander off".
---

# /eo-freeze

**Purpose:** Non-technical founders hate it when Claude "takes a joyride" — opens a small bug fix and rewrites three other files while it's in there. `/eo-freeze <path>` draws a line: for the rest of this session, edits stay inside `<path>`. Everything outside is off-limits unless you `/eo-unfreeze` first.

## What it does

1. **Tries `gstack:freeze` first.** If the `gstack` plugin is installed, hand off to its `freeze` skill — it already implements path allow-lists the right way.
2. **Fallback — lightweight session rule.** If `gstack` is not installed, set an in-session edit boundary:
   - Record `<path>` as the only writable subtree for the remainder of the session.
   - Before any `Edit` / `Write` / `NotebookEdit` outside `<path>`, refuse with:
     > ❄️ `/eo-freeze` is active — edits restricted to `<path>`. Run `/eo-unfreeze` to lift.
   - Reads are still allowed everywhere. Only writes are scoped.
3. **Auto-lifts on `/eo-unfreeze`** or at the start of a new session.

## Arguments

`<path>` — folder (relative to repo root) to scope edits into. Examples:
- `/eo-freeze src/components/login`
- `/eo-freeze architecture`
- `/eo-freeze docs`

Pass no argument → print whether a freeze is active and on which path.

## When to run

- You told Claude to fix one button, and it's eyeing the whole `components/` tree. Freeze it.
- You're doing a focused bugfix and want to guarantee the blast radius stays small.
- You're handing the session to a teammate and want to lock the edit surface.

## When NOT to run

- Refactors that legitimately span folders — you'll just end up running `/eo-unfreeze` immediately.
- Build / scaffold steps (`/1-eo-dev-start`, `/eo-dev-repair`) — they need broad write access by design.

## Output

```
❄️ Freeze active — edits scoped to src/components/login/
Outside this path, I'll refuse writes until /eo-unfreeze.
```

## Integration

- **Pairs with:** `/eo-unfreeze` (lift the boundary)
- **Bypassed by:** `/1-eo-dev-start`, `/eo-dev-repair` (they scaffold; freeze auto-lifts for these)
- **Hidden dependency:** `gstack:freeze` if installed. Falls back to session-local rule otherwise. The founder sees the same behavior either way.
