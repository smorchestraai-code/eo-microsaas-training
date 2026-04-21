---
description: Run 5-hat composite score. Non-negotiable gate — 90+ to ship.
---

# /eo-score

**Pillar:** EO Pillar #7 — Score+Ship
**When to run:** After `/eo-review` is clean. Before merge.

## What it does

1. Invoke `eo-scorer` skill
2. Score all 5 hats (Product, Architecture, Engineering, QA, UX)
3. Compute composite = sum × 2 (10-100 scale)
4. Decision gate:
   - **90+** → ship (run `/eo-ship`)
   - **80-89** → run bridge-gaps to fix the lowest hat
   - **<80** → don't ship. Major rework needed.
5. Save report to `docs/qa-scores/YYYY-MM-DD-HHMM.md`
6. Append row to `docs/qa-scores/trend.csv`
7. If patterns emerge → prompt lessons-manager to append a lesson

## Workflow

```
1. Read BRD + project-brain for context
2. Dispatch parallel subagents (Boris #2):
   - Agent 1: product-hat scoring
   - Agent 2: architecture-hat scoring
   - Agent 3: engineering-hat scoring
   - Agent 4: qa-hat scoring
   - Agent 5: ux-hat scoring
3. Aggregate scores, compute composite
4. Read `.claude/lessons.md` → adjust any hat caps per lesson rules
5. Generate report
6. Decide gate
```

## Arguments

`$ARGUMENTS` — optional: single hat to score (product/architecture/engineering/qa/ux)

## Output

```
## Score — {branch} — {date}

| Hat | Score | Notes |
|-----|:-----:|-------|
| Product | 9 | … |
| Architecture | 8 | … |
| Engineering | 9 | … |
| QA | 9 | … |
| UX | 10 | … |

**Composite: (9+8+9+9+10) × 2 = 90 ✅**

**Decision: Ship**

Run /eo-ship when ready.
```

## After scoring — update tracker

Update `_dev-progress.md` row for this story:
- `Score` = composite (e.g., `90`)
- `Status` = `✅ shipped` only if decision was Ship AND `/eo-ship` has been run; else `🧪 scoring` (90+ waiting to ship) or `🩹 bridging gaps` (80–89) or `⚠️ blocked` (<80)
- `Last updated` = today; `Last command` = `/eo-score`

Never set `Status` = `shipped` from this command — only `/eo-ship` moves it there.
