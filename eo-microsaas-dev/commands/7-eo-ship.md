---
description: Ship to production. Final guardrails before merge + deploy.
---

# /7-eo-ship

**Pillar:** EO Pillar #7 — Score+Ship
**When to run:** `/5-eo-score` returned 90+. Ready to merge.

## What it does

1. **Self-score on HEAD** (final gate — re-run `eo-scorer` even if the student just ran `/5-eo-score`; code may have changed)
2. Verify score gate (90+ composite, no hat <8). 80–89 → bounce to `/6-eo-bridge-gaps`. <80 → refuse + route to `/2-eo-dev-plan`.
3. Verify git hygiene (branch up to date, no uncommitted changes)
4. Create PR with score report + review punch list attached
5. Run final checks: `npm run build`, `npm test`, `npm audit --audit-level=high`
6. If all green → merge + deploy per project's deploy script
7. Post-deploy: hit `/api/health` to verify live
8. Push to GitHub remote (auto-invoke `eo-github` when remote exists; ask once if `github_intent=local-only` still active)
9. Update `docs/qa-scores/trend.csv` with deploy marker

## Workflow

```
1. Self-score: dispatch eo-scorer on HEAD → docs/qa-scores/<timestamp>.md
2. Gate:
   - composite ≥ 90 AND no hat < 8 → continue
   - 80–89                         → refuse, route to /6-eo-bridge-gaps
   - < 80                          → refuse, route to /2-eo-dev-plan rework
3. git fetch && git status → clean + up to date with base
4. npm run build → must pass
5. npm test → must pass
6. npm audit --audit-level=high → must be 0 OR documented
7. gh pr create with:
   - Score report body (CEO brief — no 5-hat composite table in PR UI)
   - BRD AC coverage list
   - Screenshots from mena-mobile-check + arabic-rtl-checker
   - Elegance pause block
8. After merge: run deploy script from CLAUDE.md project registry
9. Wait 10s → curl health endpoint → confirm 200
10. If unhealthy → rollback + debug
11. Push to remote:
    - remote exists → `git push origin <branch>`
    - no remote + github_intent≠local-only → invoke eo-github once
    - github_intent=local-only → ask once: "Ready to push to GitHub? (y/n)"
12. Commit score + deploy log to trend.csv
```

## Founder-facing verdict (CEO brief)

One line before the full report:

```
Ship gate: ✅ pass (92) — shipped to {deploy_target}, health 200 OK.
```

No 5-hat composites, no `aria-invalid`, no "setSession fragility" in founder view. Engineering detail stays in `docs/qa-scores/<timestamp>.md`.

## Hidden plumbing (graceful degrade)

| Step | First choice | Fallback |
|------|--------------|----------|
| Canary / gradual rollout | `gstack:canary` | Skip — go straight to deploy (Weekend MVP default) |
| Deploy orchestration | `gstack:land-and-deploy` | Internal: run project `deploy.sh` or `pm2 reload` per `CLAUDE.md` |
| Branch-finish hygiene | `superpowers:finishing-a-development-branch` | Internal: merge + tag + delete branch |
| PR body formatting | `gstack:/ship` PR template | Plugin default PR template |

The founder never sees a "skill not installed" error. If a preferred skill is absent, the fallback path runs silently.

## Arguments

`$ARGUMENTS` — optional: target env (default: production from project registry)

## Blocks

- Score <90 → blocked, go back to /6-eo-bridge-gaps or /3-eo-code
- Uncommitted changes → blocked
- Build/test/audit failure → blocked
- Health check fail post-deploy → auto-rollback + create incident in docs/incidents/

## Output

```
✅ Shipped

**Branch:** {name}
**Composite:** 92
**Deploy target:** {server}
**Health check:** 200 OK
**Commit:** {sha}

Trend.csv updated.
```

## After ship — update tracker

Update `_dev-progress.md` row for this story:
- `Status` = `✅ shipped` (only `/7-eo-ship` can set this)
- `Shipped` = today's date (YYYY-MM-DD)
- `Notes` = commit sha + deploy target (e.g., `a1b2c3d → vercel prod`)
- `Last updated` = today; `Last command` = `/7-eo-ship`

If the deploy or health-check failed → DO NOT set `✅ shipped`. Set `Status` = `⚠️ blocked` and `Notes` = rollback reason. `/eo-guide` will route back to `/eo-debug`.
