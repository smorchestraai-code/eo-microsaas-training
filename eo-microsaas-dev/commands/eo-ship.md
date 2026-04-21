---
description: Ship to production. Final guardrails before merge + deploy.
---

# /eo-ship

**Pillar:** EO Pillar #7 — Score+Ship
**When to run:** `/eo-score` returned 90+. Ready to merge.

## What it does

1. Verify score gate (90+ composite, no hat <8)
2. Verify git hygiene (branch up to date, no uncommitted changes)
3. Create PR with score report + review punch list attached
4. Run final checks: `npm run build`, `npm test`, `npm audit --audit-level=high`
5. If all green → merge + deploy per project's deploy script
6. Post-deploy: hit `/api/health` to verify live
7. Update `docs/qa-scores/trend.csv` with deploy marker

## Workflow

```
1. Read latest docs/qa-scores/*.md → confirm 90+
2. git fetch && git status → clean + up to date with base
3. npm run build → must pass
4. npm test → must pass
5. npm audit --audit-level=high → must be 0 OR documented
6. gh pr create with:
   - Score report body
   - BRD AC coverage list
   - Screenshots from mena-mobile-check + arabic-rtl-checker
   - Elegance pause block
7. After merge: run deploy script from CLAUDE.md project registry
8. Wait 10s → curl health endpoint → confirm 200
9. If unhealthy → rollback + debug
10. Commit score + deploy log to trend.csv
```

## Arguments

`$ARGUMENTS` — optional: target env (default: production from project registry)

## Blocks

- Score <90 → blocked, go back to bridge-gaps or /eo-code
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
- `Status` = `✅ shipped` (only `/eo-ship` can set this)
- `Shipped` = today's date (YYYY-MM-DD)
- `Notes` = commit sha + deploy target (e.g., `a1b2c3d → vercel prod`)
- `Last updated` = today; `Last command` = `/eo-ship`

If the deploy or health-check failed → DO NOT set `✅ shipped`. Set `Status` = `⚠️ blocked` and `Notes` = rollback reason. `/eo-guide` will route back to debug.
