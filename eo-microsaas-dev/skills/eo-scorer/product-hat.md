# Product Hat — Scoring Rubric

**Dimension:** Does this code serve a real user problem, match the BRD, and stay in scope?

**Time to score:** 1-2 minutes per PR

---

## 8 Questions (each 1-10)

### 1. Does it match the BRD?
- ✅ 10: All acceptance criteria from `docs/BRD-*.md` (or `EO-Brain/4-Architecture/brd.md`) are addressed
- ⚠️ 7: Most ACs addressed, 1 missing or interpreted loosely
- ❌ 4: BRD exists but PR substantially diverges
- 💀 1: No BRD exists or PR has no traceability to it

### 2. Would a real ICP user use this?
- ✅ 10: Solves the exact pain described in the BRD's user section
- ⚠️ 7: Solves something adjacent; user might use it
- ❌ 4: Generic feature not tied to your specific ICP
- 💀 1: Built for yourself, not the ICP

### 3. Scope discipline (no feature creep)
- ✅ 10: PR does exactly what BRD says, nothing extra
- ⚠️ 7: 1-2 minor adjacent improvements snuck in
- ❌ 4: Multiple features bundled, hard to review
- 💀 1: Whole new feature rolled in without BRD

### 4. MENA context addressed (if ICP is MENA)
- ✅ 10: Arabic/English toggle works. Currency/timezone accurate. Ramadan-aware if scheduling.
- ⚠️ 7: English only or Arabic only when both needed
- ❌ 4: Generic Western-default assumptions
- 💀 1: Hardcoded US-centric (USD only, Eastern timezone, Christmas-themed)

### 5. Out-of-scope items deferred explicitly
- ✅ 10: "Not in this PR: X, Y, Z" in PR description
- ⚠️ 7: Most deferrals mentioned, 1 missing
- ❌ 4: Implicit assumptions about what's coming later
- 💀 1: No mention — unclear what's deferred

### 6. Pricing / monetization clarity (if customer-facing)
- ✅ 10: Free vs paid lines are clear to the user
- ⚠️ 7: Lines drawable but not yet documented
- ❌ 4: Confused — you can't explain what's paid
- 💀 1: No monetization model implied

### 7. Success metric is measurable
- ✅ 10: BRD defines "done when" with measurable criteria. PR satisfies them.
- ⚠️ 7: Criteria exist but are fuzzy
- ❌ 4: "Done when it works" — not testable
- 💀 1: No success criteria at all

### 8. Voice / tone consistent
- ✅ 10: All copy uses direct, specific, number-first voice. No buzzwords.
- ⚠️ 7: 90% clean, 1-2 corporate phrases slipped
- ❌ 4: Mixed — some direct, some vague marketing-speak
- 💀 1: Full of "leverage", "synergy", "cutting-edge"

---

## Scoring

**Average of 8 answers × 1.25** = Product hat score (capped at 10)

Example: avg 7.5 → 7.5 × 1.25 = 9.4 → cap at 10 → Product = 9

## Red flags that force Product ≤ 6 regardless of math

- No BRD in the repo
- PR targets a user persona that doesn't exist in your ICP doc
- Arabic support was in the BRD but the PR is English-only

## Red flags that force Product ≤ 3 regardless of math

- You built this for yourself, not the stated ICP
- BRD has explicit "out of scope" items and the PR includes them anyway

## Calibration examples

See `calibration-examples.md` for real score examples from past PRs.
