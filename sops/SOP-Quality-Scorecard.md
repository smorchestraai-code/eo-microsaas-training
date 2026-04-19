# Student SOP: Quality Scorecard (5 questions)

**Version:** 1.0 (2026-04-19)
**When to use:** Before every PR you open.
**Time:** 5 minutes.

---

## The 5 Questions

Answer each 1-10 honestly. No self-inflation — the whole point is catching what you missed.

### 1. Product (matches intent?)

- Does this code match the BRD / user story you wrote?
- Would a real user from your ICP actually use this?
- Did you accidentally over-build (feature creep)?

**Score 1-10.**

### 2. Architecture (organized?)

- Is the code in logical modules (not one giant file)?
- Can you explain the data flow in 2 sentences?
- Did you separate concerns (UI vs business logic vs API)?

**Score 1-10.**

### 3. Engineering (solid?)

- Are there tests? (Aim for 60%+ coverage on new code)
- Is there error handling for every external call (API, DB, filesystem)?
- Are types strict? (If TypeScript, no implicit `any`)

**Score 1-10.**

### 4. QA (tested?)

- Have you manually clicked through every user flow?
- Did you test empty state (no data)?
- Did you test error state (network fail, bad input)?
- Did you test edge cases (max input length, special chars)?

**Score 1-10.**

### 5. UX / Frontend (polished?)

- Does it work on mobile (375px wide)? (Open Chrome DevTools → device mode)
- If your ICP is MENA: does Arabic RTL render correctly?
- Are there any console errors or warnings?
- Are loading states present?

**Score 1-10.**

---

## Composite

**Composite = average × 10**

| Score | Decision |
|-------|----------|
| 90+ | Ship. You're good. |
| 80-89 | Fix the lowest hat. Re-score. |
| <80 | Don't ship. Iterate. |

---

## Save the score

In your project:

```bash
mkdir -p docs/qa-scores
```

Then save each run as `docs/qa-scores/YYYY-MM-DD.md`:

```markdown
# Score: [feature name] · 2026-04-19

| Hat | Score | Notes |
|-----|:-----:|-------|
| Product | 9 | Matches BRD |
| Architecture | 7 | One file is getting big — will split in next PR |
| Engineering | 8 | Tests at 65%. Need more error handling on the API call |
| QA | 9 | Tested empty + error states |
| UX | 9 | Mobile OK, no console errors |

**Composite:** 84/100 — BORDERLINE SHIP

**Action:** Splitting the big file in next PR. Adding one more error handler before this PR.
```

Track this weekly. Your scores should trend up as you improve.

---

## Common mistakes

1. **Self-inflation** — you score yourself 10 on QA without actually testing edge cases. The whole exercise fails. Be honest.
2. **Skipping saves** — the weekly history is the point. Don't skip writing the score doc.
3. **Ignoring the composite** — "I'm at 78 but it's fine" is how bad code ships.
4. **Only scoring the first PR** — you score every PR. Even a one-line fix gets a mental scorecard.

---

## When you can't get to 90

- Usually tests are missing (QA hat) → write them
- Or mobile is broken (UX hat) → fix the responsive layout
- Or there's no error handling (Engineering hat) → wrap external calls in try/catch

The same 3 issues block most PRs. Fix the pattern, not just this instance.

---

## How this compares to SMOrchestra team's system

SMOrchestra uses the same 5-hat framework but with:
- A skill that generates the score automatically (`/score-project`)
- An independent QA agent on a separate server that re-scores your PR
- CI gates that block the merge

You'll graduate to this over time. For now, the mental model is the point.
