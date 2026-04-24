---
description: Self-review a PR or working branch. Catches bugs, security, Arabic RTL, mobile issues.
---

# /4-eo-review

**Pillar:** Boris #4 — Verification Before Done
**When to run:** After `/3-eo-code`, before `/5-eo-score`.

## What it does

1. Diff the branch against `main` (or target base)
2. Run superpowers:verification-before-completion
3. For UI changes → run arabic-rtl-checker + mena-mobile-check + compare rendered component against `docs/ux-reference/*.html` artifact for the BRD story
4. Scan for secrets, hardcoded keys, `any` types
5. Check BRD traceability (brd-traceability skill)
6. Verify elegance-pause block in recent commits
7. Output a punch list: must-fix / nice-to-fix

## Workflow

```
1. git diff main...HEAD
2. For each changed file:
   - If .tsx/.jsx → queue arabic-rtl-checker + mena-mobile-check
   - If .ts/.js → queue secret scan + type strictness check
   - If test file → queue @AC tag verification
3. Run brd-traceability coverage check
4. Grep last commit for "## Elegance Pause" block
5. Verify SaaSfast-mode consistency (no cross-mode leakage in changed files)
6. Optional deep review pass: gstack:/review if installed (adds security + perf lens)
7. Output punch list with severity (🔴 must / 🟡 should / 🟢 nice)
```

## Hidden plumbing (graceful degrade)

| Step | First choice | Fallback |
|------|--------------|----------|
| Verification contract | `superpowers:verification-before-completion` | Internal punch-list generator |
| Deep review pass | `gstack:/review` | Skip — the 5-hat review runs anyway |
| Secret scan | global `secret-scanner` hook (repo setting) | Inline grep for `sk_live_`, `SECRET`, etc. |

## Arguments

`$ARGUMENTS` — optional base branch (default: `main`)

## Output

```
## Review — {branch}

**Changed files:** N
**BRD coverage:** X/Y ACs tested (Z%)
**Elegance pause:** {present/missing}

### 🔴 Must fix
- …

### 🟡 Should fix
- …

### 🟢 Nice to have
- …

**Ready for /5-eo-score?** (fix 🔴 first)
```
