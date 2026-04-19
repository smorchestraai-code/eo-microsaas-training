---
description: End-of-sprint retro. Score trends, lesson pruning, pattern surfacing.
---

# /eo-retro

**Pillar:** Boris #3 — Self-Improvement Loop
**When to run:** End of sprint (weekly or bi-weekly).

## What it does

1. Read `docs/qa-scores/trend.csv` — last N scores
2. Compute trend per hat (improving / flat / declining)
3. Identify the weakest hat of the sprint
4. Read `.claude/lessons.md` — list lessons triggered this sprint
5. Prune stale lessons (>90 days untriggered)
6. Propose 1-2 rules to add based on repeat issues
7. Output sprint scorecard + next-sprint focus

## Workflow

```
1. Load trend.csv, filter to last 14 days
2. Group by hat, compute avg + trend
3. Find min(avg) hat → "focus hat for next sprint"
4. Parse .claude/lessons.md, check `Last triggered` dates
5. Move >90d lessons to archived section
6. Scan PR history for recurring bug types → propose new lessons
7. Write report to docs/retros/YYYY-MM-DD.md
```

## Arguments

`$ARGUMENTS` — optional: sprint length in days (default: 14)

## Output

```
## Sprint retro — {date range}

**PRs shipped:** N
**Avg composite:** 87
**Trend:** +3 vs prior sprint ✅

### Hat averages
| Hat | Avg | Trend | Status |
|-----|:---:|:-----:|--------|
| Product | 9.2 | +0.4 | ✅ |
| Architecture | 8.1 | -0.2 | 🟡 |
| Engineering | 8.8 | +0.1 | ✅ |
| QA | 7.9 | -0.6 | 🔴 focus |
| UX | 9.1 | +0.5 | ✅ |

### Focus hat: QA
- 3 PRs shipped without empty-state tests
- Propose new lesson: "every component with data must test empty-state"

### Lessons status
- Active: 8 (2 new this sprint)
- Archived: 3 (not triggered in 90d)
- Proposed: "QA empty-state mandatory" — add? (y/n)

### Next sprint focus
- QA discipline: add empty-state requirement to qa-hat Q2
- 1 PR to refactor the 3 files that shipped without the check
```
