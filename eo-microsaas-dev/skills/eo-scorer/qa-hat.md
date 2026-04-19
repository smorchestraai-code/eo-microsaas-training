# QA Hat — Scoring Rubric

**Dimension:** Has this been actually tested? Does evidence exist? (Boris pillar 4: verification-before-done)

**Time to score:** 1-2 minutes per PR

---

## 8 Questions (each 1-10)

### 1. Happy path manually tested
- ✅ 10: You clicked through the entire user flow locally, it works end to end
- ⚠️ 7: Tested most of the flow, skipped 1 step
- ❌ 4: Started the flow, assumed rest works
- 💀 1: Never ran the code manually

### 2. Empty state tested
- ✅ 10: First-time user with no data sees sensible state (not a crash or empty void)
- ⚠️ 7: Empty state works but looks ugly
- ❌ 4: Shows blank screen / error when empty
- 💀 1: Empty state not considered

### 3. Error state tested
- ✅ 10: Network fail, 500 response, bad input — all tested + UI shows actionable message
- ⚠️ 7: Most error paths covered
- ❌ 4: Only network-fail tested, not API errors
- 💀 1: Errors crash the app

### 4. Edge cases tested
- ✅ 10: Max input length, zero, negative, special chars, very long strings — all tried
- ⚠️ 7: Most edges covered
- ❌ 4: Boundary values untested
- 💀 1: Only tested with "happy" inputs

### 5. Auth states tested
- ✅ 10: Logged out redirect. Expired session. Role-based access. All verified.
- ⚠️ 7: Most auth paths work
- ❌ 4: Auth tested for happy path only
- 💀 1: No auth testing

### 6. Verification evidence in PR description (Boris pillar 4)
- ✅ 10: Screenshots / test output / commit SHA of passing CI — all in PR body
- ⚠️ 7: Some evidence, not comprehensive
- ❌ 4: "it works on my machine" with no proof
- 💀 1: No evidence, PR body empty

### 7. Regression risk assessed
- ✅ 10: "This change affects X and Y. I tested both."
- ⚠️ 7: Regression considered but not explicitly tested
- ❌ 4: "I think this doesn't affect anything else"
- 💀 1: Broke a feature that worked before this PR

### 8. Autonomous bug fix (if this PR is a bugfix)
- ✅ 10: Fix includes: log pointing at root cause + test preventing regression + minimal code change
- ⚠️ 7: Fix works but no regression test added
- ❌ 4: Patch without root cause analysis
- 💀 1: Fix that masks the bug rather than fixing it

---

## "Would a staff engineer approve?" test (Boris)

**Before scoring the QA hat:** imagine you're handing this to a staff engineer. What would they ask for?

- "Did you run the tests?"
- "Show me the empty state."
- "What happens if the API is down?"
- "Who else uses this? Did you test for them?"

If you can answer all 4 with specifics: QA hat 8+.
If you pause on any: score reflects the gap.

---

## Scoring

**Average of 8 answers × 1.25** = QA hat (capped at 10)

## Red flags that force QA ≤ 6

- Never ran the code manually
- No evidence in PR body
- Known edge case (Arabic text, mobile, error state) untested

## Red flags that force QA ≤ 3

- Feature was broken before your PR and still broken
- Test suite fails, PR opened anyway
- "Works on my machine" is the only evidence

## Calibration examples

See `calibration-examples.md`.
