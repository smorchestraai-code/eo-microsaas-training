---
description: GitHub admin for EO MicroSaaS projects. Creates, wires up, or audits a private repo with EO best practices. MCP-only, plan-mode gated.
---

# /eo-github

Activate the **eo-github** skill.

Execute:
1. Resolve workspace root (worktree-aware: honor `$GIT_WORK_TREE` or `git rev-parse --show-toplevel`, never `pwd`)
2. MCP precheck — refuse if no `mcp__github__*` tool is available in the current session
3. Remote precheck — refuse if `git config --get remote.origin.url` already returns a value (except in `audit` mode, which requires origin)
4. Detect mode from arguments (or pick `guided` if none given):
   - `create` → create a new private repo under the authenticated user, apply best-practices settings, wire origin, push
   - `point-existing <url-or-owner/repo>` → validate empty + writable, align settings with a drift diff, wire origin, push
   - `guided` → show the A/B/C menu for students who said "I don't know" in `/1-eo-dev-start`
   - `audit` → read current repo state, compute drift vs the best-practices matrix, offer per-item fixes
5. Detect GitHub plan (free/pro/team/enterprise) and collaborator count via MCP. Pick branch strategy (trunk for solo, dual-branch for team). Never offer plan-locked features on plans that would silently ignore them.
6. Plan-mode preview for every mode. Student approves (`y`) before anything is written. Mode 2 preview shows the settings drift diff + option to `skip-settings`.
7. Execute + evidence table. Branch protection is deferred until first `/eo-ship` green CI (post-first-CI automation).

Read `skills/eo-github/SKILL.md` for the full four-mode state machine, best-practices matrix, and failure rollback.

## Arguments

| Form | Meaning |
|------|---------|
| `/eo-github` | Defaults to `guided` — shows A/B/C menu |
| `/eo-github create` | Mode 1 — create new repo from folder name |
| `/eo-github point-existing <url-or-owner/repo>` | Mode 2 — wire to an empty repo you already made |
| `/eo-github audit` | Mode 4 — drift report + per-item fix (requires existing origin) |

## When to run

- Student picked option 1, 2, or 4+MCP in `/1-eo-dev-start`'s 4-option question → skill is auto-routed here
- Student finished local MVP and is ready to push to GitHub
- Anytime post-setup for a drift audit (`/eo-github audit`)
- After first `/7-eo-ship` green CI to accept branch-protection activation

## Contract

| Input state | Output |
|-------------|--------|
| No MCP (`mcp__github__*` missing) | No writes. Refuse with install remediation. |
| Origin already set (Modes 1, 2, guided) | No writes. Refuse with existing URL shown. |
| Origin missing (Mode 4 audit) | No writes. Refuse — "nothing to audit yet". |
| Empty workspace + MCP + Mode 1 | Plan preview → y → create repo + settings + first push. |
| Existing empty remote + MCP + Mode 2 | Plan preview with settings diff → y or skip-settings → push + optional alignment. |
| Existing non-empty remote + MCP + Mode 2 | No writes. Refuse with "not empty — resolve manually" remediation. |
| Plan-locked feature requested on free plan | Feature silently omitted from offer; reason printed in evidence table. |

## Guarantees

- **MCP-only.** Never falls back to `gh` CLI or shell `curl`.
- **Private by default.** Student flips to public in GitHub UI later.
- **No force push. Ever.**
- **No auto LICENSE.** Evidence table prompts; student chooses.
- **No renamed labels, no rewritten READMEs.** Adds missing, preserves existing.
- **Idempotent.** Re-running `audit` on a clean repo reports "all matches spec."
