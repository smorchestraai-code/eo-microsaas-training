# Calibration Examples — Real PR Scores

**Purpose:** Anchor your scoring against known-good examples. Re-read before your first solo score each sprint.

---

## Example 1: `feat: add password reset flow` — Composite 92

**Context:** Solo founder's SaaS, MENA ICP, Next.js + Supabase

| Hat | Score | Why |
|-----|:-----:|-----|
| Product | 9 | BRD existed. All 4 ACs addressed. Out-of-scope noted. MENA-appropriate (Arabic + English emails). |
| Architecture | 9 | Clean separation: `/lib/auth/*` for logic, `/app/(auth)/reset/*` for UI. Supabase RLS policies in place. |
| Engineering | 10 | TDD — tests tagged `@AC-1.1` through `@AC-1.4`. Elegance pause noted in PR: "considered token expiry via cron vs lazy check — went lazy for simplicity." Strict types. |
| QA | 9 | Empty/error/edge all tested. Screenshots in PR. axe scan clean. |
| UX | 10 | Mobile 375px tested. RTL mirrored correctly. Loading states on every async. Axe clean. |

**Composite: (9+9+10+9+10) × 2 = 94** → corrected to 92 after noting 1 missing regression test.

**Decision: Ship.**

---

## Example 2: `feat: export scorecard as PDF` — Composite 78

**Context:** Same founder, month 2

| Hat | Score | Why |
|-----|:-----:|-----|
| Product | 8 | BRD existed. PDF format matches. But added 3 bonus fields not in BRD (feature creep). |
| Architecture | 7 | Used `@react-pdf/renderer` — 300KB added to bundle. Not discussed. Hard-coded font paths. |
| Engineering | 6 | Tests exist but only happy path. Elegance pause NOT honored — PR author admitted "first working version". Types loose on PDF component. |
| QA | 8 | Happy + empty tested. Error path (PDF gen fails) shows generic error. No Arabic test. |
| UX | 10 | PDF renders correctly in English and Arabic. Fonts embedded. Mobile preview works. |

**Composite: (8+7+6+8+10) × 2 = 78**

**Decision: Block. Engineering hat < 8 due to elegance pause skipped. Run bridge-gaps.**

**Lesson added to `.claude/lessons.md`:** "Elegance pause is non-negotiable for any PR with a new third-party dep. Check bundle size impact."

---

## Example 3: `fix: submit button disabled on slow networks` — Composite 88

**Context:** Bugfix PR, 1-line change

| Hat | Score | Why |
|-----|:-----:|-----|
| Product | 10 | Directly fixes BRD AC-3.2 ("submit works on 3G"). In scope. |
| Architecture | 9 | One-line change in loading state logic. No new deps. |
| Engineering | 8 | Added regression test. Elegance pause: "is there a more elegant way?" — considered debouncing but stayed with loading state (correct for this case). No types changed. |
| QA | 9 | Reproduced on throttled Chrome → verified fix. Logs show the race condition gone. |
| UX | 8 | Mobile + desktop tested. Arabic not specifically tested (but translation unchanged). |

**Composite: (10+9+8+9+8) × 2 = 88**

**Decision: Ship (bugfix, 88 acceptable). Note UX 8 — could have tested Arabic; add to next lesson.**

---

## Example 4: `feat: rewrite pricing page` — Composite 65

**Context:** Cosmetic rewrite, no BRD written beforehand

| Hat | Score | Why |
|-----|:-----:|-----|
| Product | 4 | No BRD. Unclear what user problem this solves. Marketing copy is buzzword-heavy ("leverage", "cutting-edge"). |
| Architecture | 7 | Clean component split but introduces 2 new deps (framer-motion, react-icons) without justification. |
| Engineering | 6 | No tests added (cosmetic rewrite). Elegance check skipped. 3 `any` types. |
| QA | 6 | Tested desktop only. No Arabic. Console has React key warnings. |
| UX | 10 | Looks beautiful on desktop. |

**Composite: (4+7+6+6+10) × 2 = 66**

**Decision: Rejected (< 80). Write BRD first. Remove buzzwords. Add tests. Test Arabic + mobile.**

**Lessons added:**
1. Pricing pages for MENA MUST be tested in Arabic before shipping.
2. No PR without a BRD, even "just a cosmetic rewrite."

---

## How to use these

- **Before your first score of the week:** read all 4 examples
- **When a hat score feels off:** compare to the closest example — do the questions match?
- **If your scores are consistently higher than these examples:** you're inflating. Run calibration.

## Your own calibration log

Maintain `docs/qa-scores/calibration.md`:

```markdown
# My Calibration Log

| Date | PR | Self-score | External score (reviewer) | Delta |
|------|-----|:----------:|:-------------------------:|:-----:|
| 2026-04-19 | add-pwd-reset | 92 | 89 | -3 |

## Patterns
- I over-score UX when I spent a lot of time on it
- I under-score Product when I wrote the BRD myself
```

Track delta between your self-score and any external review (reviewer, QA agent, Mamoun). Calibrate monthly.
