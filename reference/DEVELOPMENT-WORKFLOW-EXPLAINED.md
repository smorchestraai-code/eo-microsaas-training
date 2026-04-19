# The Development Workflow — Explained (Student Edition)

**Version:** 1.0 (2026-04-19)

This is the 7-step flow for every feature. Memorize it. Internalize it. It's what separates shipping from thrashing.

---

## The 7 Steps

```
1. PLAN        Write a BRD before touching code
2. TEST        Write the failing test first (TDD)
3. CODE        Write minimum code to pass the test
4. REVIEW      gstack:/review — 4 dimensions
5. SCORE       5-question scorecard — 90+ to ship
6. PR          Open with BRD link + score + screenshots
7. DEPLOY      After CI passes, deploy and smoke-test
```

Each step has a tool. Use it. Don't improvise — the patterns are battle-tested.

---

## Step 1 — Plan

**Skill:** `superpowers:writing-plans` (for non-trivial features)
**Template:** `templates/BRD-TEMPLATE.md`
**Output:** `docs/BRD-<feature>.md` in your project

### Why planning first

Without a BRD you're guessing what "done" means. You'll build extra things (waste), miss actual requirements (rework), and argue with yourself about scope (thrash).

A good BRD takes 15 minutes. It saves 5 hours of rework.

### What to include

- **Problem:** the user pain in one paragraph
- **User:** specific ICP, not "everyone"
- **Acceptance criteria:** numbered, testable (`AC-1.1`, `AC-1.2` — you'll tag tests with these)
- **Out of scope:** what you're explicitly NOT building in this cycle
- **Done when:** specific criteria for shipping

---

## Step 2 — Test First (TDD)

**Skill:** `superpowers:test-driven-development`
**Output:** Failing test file before any implementation

### The TDD cycle

```
Red    → write a test that fails for the right reason (feature missing)
Green  → write the minimum code that makes the test pass
Refactor → improve structure without changing behavior
```

### Tag tests with BRD IDs

```typescript
test('@AC-1.1 landing page loads 200', async ({ page }) => {
  const response = await page.goto('/');
  expect(response.status()).toBe(200);
});
```

The `@AC-1.1` tag links this test back to your BRD. If CI ever loses track of whether an AC is covered, the BRD traceability script catches it.

### Minimum coverage

Aim for 60%+ on new code. 80%+ on business logic. 100% on anything involving money or credentials.

---

## Step 3 — Code

**Skill:** `superpowers:subagent-driven-development` (for multi-file changes)

### Rules

- Smallest change that makes the next test pass
- Refactor only after tests are green
- Commit logical chunks as you go — don't wait until the end
- Never comment out a failing test. Either fix the test or fix the code.

---

## Step 4 — Self-Review

**Skill:** `gstack:/review`
**Frequency:** Before every commit

### 4 dimensions

| Dimension | What it catches |
|-----------|----------------|
| Security | Secrets, injection vectors, missing auth checks |
| Performance | N+1 queries, unbounded loops, missing pagination |
| Correctness | Edge cases, error paths, spec mismatches |
| Maintainability | Unclear names, magic numbers, single-responsibility violations |

Score each 1-10. If anything is below 8, fix before committing.

### Common `/review` findings

- "Error not handled on line 42 — what if the API returns 500?"
- "Function name `handleData()` is too vague — rename to `parseUserSignup()`"
- "Magic number 86400 should be a named const `SECONDS_PER_DAY`"
- "This could be O(n²) on large inputs — consider indexing"

---

## Step 5 — Score

**Skill:** Mental model (see `sops/SOP-Quality-Scorecard.md`)
**Output:** `docs/qa-scores/YYYY-MM-DD.md` saved in your project

### 5 hats, 5 questions each

Covered in the scorecard SOP. The point:

- **Product** — matches intent?
- **Architecture** — organized?
- **Engineering** — solid?
- **QA** — tested?
- **UX / Frontend** — polished?

### If composite < 90

Fix the lowest hat first. Usually:
- Tests missing (QA) → write them
- Mobile broken or untested RTL (UX) → fix responsive
- No error handling (Engineering) → wrap external calls

Re-score. When you're at 90+, move on.

---

## Step 6 — PR

**Skill:** `gstack:/ship`
**Output:** GitHub PR with structured description

### Required PR content

```markdown
## What this does
[1-2 sentences]

## BRD
Link: docs/BRD-feature-name.md

## Scorecard (composite 91/100)
| Hat | Score |
|-----|:-----:|
| Product | 9 |
| Architecture | 8 |
| Engineering | 9 |
| QA | 9 |
| UX | 9 |

## Screenshots
[before / after for UI changes]

## Out of scope (next PR)
- [what you deferred]
```

### CI will run

- Typecheck
- Lint
- Test suite
- Build
- `npm audit` (blocks on high-severity)

Wait for green before assuming you're done.

---

## Step 7 — Deploy

**Template:** `templates/DEPLOY-CHECKLIST.md`

### Pre-flight
All acceptance criteria pass. Scorecard 90+. Build works locally.

### Deploy
Push to `main` → Vercel/Netlify auto-deploys.

### Post-deploy smoke
- Open production URL
- Walk the main flow
- Mobile check
- Arabic RTL if applicable
- Lighthouse run → Performance 90+, A11y 90+

### Record
Save `docs/deployments/YYYY-MM-DD-v<version>.md` with URL + SHA + what changed.

---

## When to deviate

**Trivial changes** (typo fix, lint fix, comment update): skip steps 1-2, score mentally, still open a PR.

**Urgent hotfix** (production is burning): ship first, score after. Open a retrospective PR with the scorecard and what you skipped.

**Research spike** (you're exploring whether to build X): branch freely, don't PR it. Delete the branch when you decide. Write the decision into a BRD.

Otherwise: follow the 7 steps literally.

---

## What great looks like

- Every PR has a BRD link
- Every PR has a scorecard
- Every PR's tests are tagged with AC IDs
- CI is always green on `main`
- You can roll back to any commit in <30 seconds
- New features ship in ~2 days instead of ~2 weeks because you're not thrashing

---

## Scaling up (when you join SMOrchestra team or similar)

The same 7 steps apply, with more automation:

- `/score-project` replaces the mental 5-question (skill does it for you)
- An independent QA agent re-scores your PR cold
- CI has Playwright E2E + Lighthouse + axe-core blocking
- Deploy has a post-deploy probe validating Sentry + PostHog events

You graduate into those tools over time. The mental model stays the same.
