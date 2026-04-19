---
description: Fix the lowest-scoring hat when composite is 80-89. Turns a "blocked" PR into a "ship-ready" one.
---

# /eo-bridge-gaps

**Pillar:** EO Pillar #7 — Score+Ship (recovery arm)
**When to run:** `/eo-score` returned 80-89. Need to lift weakest hat to 8+ to reach ship gate.

## What it does

1. Read latest score report from `docs/qa-scores/`
2. Find hat(s) scoring <8
3. For each low hat, read the rubric (e.g., `eo-scorer/qa-hat.md`)
4. Identify which specific questions dragged the score down
5. Generate fix plan: ordered list of changes to reach ≥8
6. Auto-fix what's safe (missing alt text, missing types, etc.)
7. Flag what needs human judgment (design changes, arch decisions)
8. Re-run `/eo-score` on the target hat after fixes

## Workflow

```
1. Read latest docs/qa-scores/*.md
2. For each hat with score <8:
   a. Open the hat rubric
   b. Match PR evidence to each question
   c. List questions scored ≤6
   d. Propose minimal change per question
3. Categorize fixes:
   - AUTO: safe mechanical fixes (run them)
   - REVIEW: needs human decision (present options)
   - DEFER: too big for this PR (create follow-up issue)
4. Apply AUTO fixes
5. Prompt user for REVIEW items
6. Re-score target hat
7. If ≥8 → return to /eo-score for full recompute
8. If still <8 → loop, or escalate to /eo-plan rework
```

## Arguments

`$ARGUMENTS` — optional: specific hat to target (default: lowest)

## Output

```
## Bridge gaps — targeting {hat} (current: 6)

### Auto-fix (applied)
- Added missing alt="" to 3 images
- Renamed 2 `any` types to explicit interfaces
- Added empty-state test for ProductList

### Needs review
- Q3 (error handling): 2 API calls missing try/catch
  Options: (A) wrap + toast, (B) wrap + silent log
- Q7 (deps justified): framer-motion not justified in BRD
  Options: (A) remove, (B) add comment + bundle size

### Deferred (follow-up issue)
- Q8 (scalability): N+1 query on /api/products — needs pagination refactor

### Re-score prediction
Applying A/A → hat lifts from 6 → 8.5 (ship-ready)
```
