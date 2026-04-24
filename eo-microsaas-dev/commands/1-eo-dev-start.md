---
description: Bootstrap a fresh EO MicroSaaS project from EO-Brain phases 0-4. One-shot, idempotent, plan-mode gated.
---

# /1-eo-dev-start

Activate the **eo-dev-start** skill.

Execute:
1. Resolve workspace root (worktree-aware: honor `$GIT_WORK_TREE` or `git rev-parse --show-toplevel`, never `pwd`)
2. Scan bootstrap signals (EO-Brain reachable? BRD present? scaffold present? first commit present?)
3. Classify state: `empty` | `partial` | `bootstrapped`
4. Route:
   - `empty` → enter plan mode, preview actions from project identity (read from `EO-Brain/1-ProjectBrain/` + `4-Architecture/`), request approval, then invoke `handover-bridge`
   - `partial` → refuse; route to `/8-eo-dev-repair` (it owns triage + silent-repair vs refuse-and-route)
   - `bootstrapped` → refuse; route to `/eo-guide`

Read language from `EO-Brain/_language-pref.md` (Arabic-first Gulf if `ar`, English otherwise).

Read `skills/eo-dev-start/SKILL.md` for the full state machine + plan-mode contract.

## Arguments

None. `/1-eo-dev-start` reads filesystem every time.

## When to run

- First Claude Code session in a fresh project folder, with EO-Brain phases 0-4 complete next to or inside the project
- Never run again after a successful bootstrap — the skill hard-refuses and routes to `/eo-guide` or `/8-eo-dev-repair`

## Contract

| Input state | Output |
|-------------|--------|
| Empty project + complete EO-Brain | Plan mode preview → approval → full bootstrap → evidence table |
| Partial state (any file missing or extra) | No writes. Print classified missing pieces. Route to `/8-eo-dev-repair`. |
| Fully bootstrapped | No writes. Route to `/eo-guide`. |
| EO-Brain missing or incomplete | No writes. Print exact missing files + remediation. Refuse. |
