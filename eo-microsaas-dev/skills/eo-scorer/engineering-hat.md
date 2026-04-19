# Engineering Hat — Scoring Rubric

**Dimension:** Is the code solid, tested, maintainable? **Includes Boris's elegance pause.**

**Time to score:** 2-3 minutes per PR

---

## 8 Questions (each 1-10)

### 1. Tests exist and cover the new code
- ✅ 10: New code has unit + integration tests. Coverage for this PR > 80%.
- ⚠️ 7: Some tests, coverage 60-80%
- ❌ 4: Placeholder tests or coverage < 50%
- 💀 1: No tests written

### 2. Tests tagged with BRD acceptance criteria
- ✅ 10: Every `@AC-N.N` from BRD has a matching test
- ⚠️ 7: 80%+ ACs tagged
- ❌ 4: Tests exist but untagged
- 💀 1: No BRD → no traceability possible

### 3. Error handling on every external call
- ✅ 10: Every fetch / Supabase / Stripe / external has try/catch + user-facing fallback
- ⚠️ 7: Most calls wrapped, 1-2 unhandled
- ❌ 4: Happy path only — errors throw to console
- 💀 1: No error handling anywhere

### 4. Types strict (TypeScript)
- ✅ 10: `tsconfig: strict`. No `any`. No `@ts-ignore` without comment.
- ⚠️ 7: Strict-ish, 1-2 `any` used with comment
- ❌ 4: Several `any`, one `@ts-ignore`
- 💀 1: Strict mode off or types thrown away

### 5. Elegance pause honored (Boris pillar 5)
- ✅ 10: Before committing, you paused and asked "more elegant way?" Found something or confirmed this IS elegant.
- ⚠️ 7: You paused but accepted first solution
- ❌ 4: Didn't pause — shipped first working version
- 💀 1: Code is obviously hacky and you know it

### 6. No dead code / commented-out blocks
- ✅ 10: Every line is live. Dead code removed.
- ⚠️ 7: 1-2 commented lines with "TODO: clean later"
- ❌ 4: Blocks of commented code scattered
- 💀 1: 30%+ of files are dead or commented

### 7. Secrets in .env (never in code)
- ✅ 10: All secrets in `.env.local` (gitignored) + `.env.example` with placeholders
- ⚠️ 7: Mostly clean but 1 "TEMP" hardcoded key
- ❌ 4: Several hardcoded keys "for testing"
- 💀 1: Production keys in repo

### 8. npm audit passes
- ✅ 10: `npm audit --audit-level=high` returns 0
- ⚠️ 7: 1-2 high-severity, documented as "will fix in next PR"
- ❌ 4: Several high, no plan
- 💀 1: Known CVE in production-path dep

---

## Boris Elegance Pause (non-negotiable check)

**Before scoring:** actually pause. Read the PR's most complex file. Ask out loud:

> "Knowing everything I know now, would I implement this the same way?"

If the answer is "no" or "not sure" → the code isn't elegant. Engineering hat caps at 7.

If the answer is "yes with minor tweaks" → note tweaks in PR description. Engineering hat 8-9.

If the answer is "yes, this IS elegant given constraints" → Engineering hat 9-10 possible.

**This check cannot be skipped.** It's the single biggest quality multiplier.

---

## Scoring

**Average of 8 answers × 1.25** = Engineering hat (capped at 10)

**Elegance pause caps the hat at 7 if not honored.**

## Red flags that force Engineering ≤ 6

- No tests for new code
- Types disabled or thrown away
- Error paths not handled for external calls

## Red flags that force Engineering ≤ 3

- Secrets committed (rotate immediately — SEV1)
- Known CVE in production dep
- SQL injection / XSS patterns visible

## Calibration examples

See `calibration-examples.md`.
