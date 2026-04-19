---
name: eo-scorer
description: |
  5-hat quality scorecard calibrated for EO MicroSaaS solo founders. Orchestrates 5
  dimension scorers (Product, Architecture, Engineering, QA, UX), computes composite,
  saves to docs/qa-scores/, appends to trend CSV, and triggers bridge-gaps if any hat
  below 8 or composite below 90.

  Different from smorch-dev-scoring: calibrated lighter (5-10 min per full score vs 30),
  MENA-baked (Arabic RTL + mobile + currency locale checked in UX hat), integrated with
  lessons-manager (low scores prompt "write a lesson?"), reads EO-Brain BRD for Product
  hat scoring.

  Invoke for: quality gate before PR, weekly self-assessment, or when bug report mentions
  "this code smells wrong."
---

# EO Scorer — 5-Hat Quality Gate

## When to run

- **Before every PR** (non-negotiable for 90+ rule)
- **Weekly** on your active project (track trend)
- **When a feature feels off** but you can't articulate why

## The 5 Hats

Each scored 1-10. Reference the sub-skill for each hat:

1. `product-hat.md` — Does it match the BRD? Would a real ICP user use it?
2. `architecture-hat.md` — Logical modules? Data flow explainable in 2 sentences? Subagents used for parallel work?
3. `engineering-hat.md` — Tests pass? Errors handled? **Elegance pause honored?** Types strict?
4. `qa-hat.md` — Happy + empty + error + edge all tested? **Verification evidence present?**
5. `ux-hat.md` — Mobile 375px? **Arabic RTL (if MENA ICP)?** Zero console errors? axe-core clean?

## Composite calculation

```
composite = (product + architecture + engineering + qa + ux) × 2
```

Each hat 1-10 → composite 10-100.

## Decision gate

| Composite | Any hat < 8? | Decision |
|-----------|:------------:|----------|
| 90+ | No | ✅ Ship |
| 90+ | Yes | ⚠ Ship but fix low hat next PR |
| 80-89 | — | 🔧 Run bridge-gaps on lowest, re-score |
| <80 | — | ❌ Don't ship. Iterate. |

## Workflow this skill executes

1. **Read context**
   - Current branch name
   - Recent commits (last 10)
   - BRD path: `docs/BRD-*.md` or `EO-Brain/4-Architecture/brd.md` if handed off from Phase 5
   - Modified files in working tree
2. **Call each hat scorer in parallel** (subagents for breadth)
   - Each returns: score (1-10), notes, low-confidence flags
3. **Compute composite**
4. **Save to `docs/qa-scores/YYYY-MM-DD-HHMM.md`**
   - Include git SHA, BRD link, 5 scores, composite, decision, gaps identified
5. **Append to `docs/qa-scores/trend.csv`**
   - Columns: date,sha,product,architecture,engineering,qa,ux,composite,decision
6. **If composite < 90 or any hat < 8:**
   - Trigger bridge-gaps output (remediation plan, prioritized)
   - Trigger lessons-manager prompt: "Want me to write a rule in .claude/lessons.md so we don't repeat this?"
7. **Return report to user** — markdown with scores, gaps, next actions

## Output format

```markdown
# EO Score: <feature> · YYYY-MM-DD

**Commit:** <short-sha>
**BRD:** docs/BRD-<feature>.md
**Composite:** XX/100  |  **Decision:** Ship / Fix / Block

| Hat | Score | Notes |
|-----|:-----:|-------|
| Product | X | ... |
| Architecture | X | ... |
| Engineering | X | ... |
| QA | X | ... |
| UX | X | ... |

## Gaps (prioritized)
1. [highest priority — quick fix]
2. [...]

## Lesson candidate
[If score dropped due to a correction from the user, offer to write a rule]

## Next action
[Ship / fix X then re-score / open issue for Y]
```

## Integration with lessons-manager

When a hat scores ≤ 7 due to a pattern the user pointed out in this session:
- Prompt: "This looks like a pattern worth remembering. Add to .claude/lessons.md?"
- If yes → pass the pattern to lessons-manager skill → appended as a rule

This is the **compounding loop** (Boris pillar 3). Every session starts smarter because past mistakes became rules.

## Trend tracking

After 4+ weekly scores:
- Report week-over-week delta per hat
- Flag any hat trending down 2 weeks in a row
- Compare to personal baseline (first score)

## What this skill DOES NOT do

- Test execution (that's CI — we assume tests pass or you'd not be scoring)
- Fix the code (that's bridge-gaps)
- Replace human judgment on shipping (90+ is a gate, not automation)

## References to each hat

Each hat is a standalone file in this skill's folder:
- `product-hat.md`
- `architecture-hat.md`
- `engineering-hat.md`
- `qa-hat.md`
- `ux-hat.md`
- `calibration-examples.md` — reference scores on known projects
