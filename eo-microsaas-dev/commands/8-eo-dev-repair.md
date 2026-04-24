---
description: Triage a partially-bootstrapped project. Silently repairs cheap pieces (lessons.md, hooks, CLAUDE.md). Refuses and routes when core artifacts (BRD, architecture, project-brain) are missing.
---

# /8-eo-dev-repair

Activate the **eo-dev-repair** skill.

Execute:
1. Resolve workspace root (worktree-aware)
2. Scan the same 11 bootstrap signals `/1-eo-dev-start` scans
3. Classify each missing piece as:
   - **silent-repair-safe** — regeneratable from templates or EO-Brain (`CLAUDE.md`, `.claude/lessons.md`, `.claude/settings.json`, `_dev-progress.md`, `docs/` subfolders, `.gitignore`, `.github/workflows/ci.yml`, `.env.example`, placeholder tests, `docs/ux-reference/`)
   - **refuse-and-route** — core artifacts from EO-Brain phases 0-4 (`architecture/brd.md`, `architecture/tech-stack-decision.md`, `1-ProjectBrain/icp.md`, `1-ProjectBrain/brandvoice.md`)
4. If **any** refuse-and-route item is missing → print classified findings + remediation, exit without writes
5. If **only** silent-repair-safe items are missing → enter plan mode, show what will be surgically repaired, request approval, execute, print evidence

Read language from project `CLAUDE.md` frontmatter or `EO-Brain/_language-pref.md`.

Read `skills/eo-dev-repair/SKILL.md` for the full classification table + repair contract.

## Arguments

None. `/8-eo-dev-repair` reads filesystem every time.

## When to run

- After `/1-eo-dev-start` classifies state as `partial` and tells you to run this
- After `/eo-guide` detects missing infrastructure (hook missing, tracker missing) and routes here
- Never before `/1-eo-dev-start` — this repairs, it does not create a project from scratch

## Contract

| Missing pieces | Behavior |
|----------------|----------|
| Only silent-repair-safe items | Plan mode → approval → surgical repair → evidence table |
| Any refuse-and-route item (BRD, architecture, project-brain) | Refuse with classified findings. No writes. Remediation = finish EO-Brain phase. |
| All signals present | Route to `/eo-guide`. No writes. |
| No signals present (empty) | Route to `/1-eo-dev-start`. No writes. |
