---
description: Systematic root-cause debugging. Hypothesis → evidence → fix → regression test.
---

# /9-eo-debug

**Pillar:** Boris #6 — Autonomous Bug Fixing
**When to run:** Bug report, failing test, production incident.

## What it does

1. Capture the failure: exact error, reproduction steps, environment
2. Run superpowers:systematic-debugging
3. Form hypothesis, gather evidence, confirm/refute
4. Fix at root cause (not symptom)
5. Add a regression test tagged `@AC-N.N` or `@bug-NNN`
6. Run elegance-pause on the fix
7. Append lesson via lessons-manager if pattern

## Workflow

```
1. Capture: user describes bug OR paste error output
2. Reproduce locally (or write test that reproduces)
3. Form ≤3 hypotheses, ranked by likelihood
4. Gather evidence (logs, git blame, recent PRs)
5. Confirm root cause
6. Minimal fix
7. Add regression test
8. Re-run full test suite
9. Elegance pause: "would I write the fix this way again?"
10. Commit with: fix(scope): description + root cause + test ref
11. lessons-manager: append if this is a recurring class
```

## Arguments

`$ARGUMENTS` — bug description, error message, or reproduction URL

## Output

```
## Bug: {short title}

**Reproduction:**
- {steps}

**Root cause:** {1-2 sentences, specific}

**Fix:** {file:line — change summary}

**Regression test:** `tests/…` tagged `@bug-NNN`

**Elegance pause:** {Yes / tweaks}

**Lesson appended?** {Yes → L-NNN / No}
```

## Anti-patterns blocked

- Fixing symptom without understanding root cause → rejected
- Fix without regression test → blocked
- "Works on my machine" without log evidence → blocked
