# elegance-pause — Boris's Non-Negotiable Quality Check

**Purpose:** Before committing any non-trivial code, pause and ask: "Knowing everything I know now, would I implement this the same way?" If no, refactor before committing.

**Pillar:** Boris #5 — Demand Elegance
**Time cost:** 60-120 seconds per PR. Saves hours of tech debt.

---

## The pause protocol

**MUST run before:**
- Any PR with >50 lines of new code
- Any PR adding a new npm dep
- Any PR touching auth, payments, or data migration
- Any PR that needed >2 iterations to work

**MAY skip for:**
- Typo fixes
- Dependency bumps
- Pure config changes (env vars, etc.)

---

## The 3 questions (answer out loud or in PR description)

### 1. Would I implement this the same way knowing what I know now?
- **Yes, confidently** → elegance check passed, Engineering hat can reach 10
- **Yes with minor tweaks** → list tweaks in PR description, Engineering hat 8-9
- **No or "not sure"** → REFACTOR. Do not commit yet. Engineering hat caps at 7.

### 2. Is there a simpler approach I dismissed too early?
Examples of simpler alternatives to check:
- Standard library fn vs custom util
- Existing component extension vs new component
- Server-side render vs client hydration
- Built-in Supabase RLS vs custom middleware
- Lazy check vs cron job
- Single SQL query vs N+1 API loop

If you find a simpler path → refactor.

### 3. Will the next developer (or future-me in 6 months) understand this without a comment?
- If it needs a comment longer than the code → refactor
- If the var names are cryptic → rename
- If the control flow needs a diagram → restructure

---

## Output format (paste into PR description)

```markdown
## Elegance Pause

**Most complex file:** `src/...`

**Q1 — Same way knowing now?** {Yes / Yes with tweaks / No → refactored}

**Q2 — Simpler approach dismissed?** Considered {X}. Went with {Y} because {reason}.

**Q3 — Next dev will understand?** Yes, because {why}. OR: Added inline comment at line N.

**Tweaks applied after pause:**
- {tweak 1}
- {tweak 2}

**Tweaks noted for follow-up (not blocking this PR):**
- {tweak}
```

---

## When the pause is skipped

If a PR ships without an elegance pause block in the description:

1. **eo-scorer** caps Engineering hat at 7 automatically
2. **lessons-manager** appends a lesson if a bug later surfaces in the unpaused code
3. **/8-eo-retro** surfaces the unpaused PRs for the sprint — compounding signal

---

## Calibration: what "elegant" means in practice

Elegant code is:
- **Short** — fewest lines that express the intent
- **Explicit** — no clever one-liners that obscure meaning
- **Boring** — uses standard patterns the team already knows
- **Local** — changes contained to the smallest blast radius
- **Reversible** — easy to roll back if wrong

Elegant is NOT:
- Shortest possible
- Most abstract
- Most DRY at all costs
- Most clever
- Prematurely optimized

---

## Example pauses

### Example 1 — Pause found improvement
```
Q1: No — I was doing the RLS check in the API route, but Supabase RLS policies already enforce it at the DB layer.
Action: Removed API-layer check. 40 lines → 0 lines. Engineering hat 9.
```

### Example 2 — Pause confirmed elegance
```
Q1: Yes, confidently. Considered debouncing vs loading-state-lock for the submit button race. Loading state is simpler + testable.
Q2: Debouncing adds a timer dep and is harder to test.
Q3: Yes — the useState + disabled={loading} pattern is standard React.
Engineering hat 10.
```

### Example 3 — Pause skipped, lesson captured
```
Shipped PDF export with @react-pdf/renderer (300KB) without pause.
Bundle regression caught next day. Engineering hat rescored 6.
Lesson L-002 appended: "bundle size comment mandatory for any new dep."
```

---

## Integration

- **/3-eo-code:** reminds before commit
- **/4-eo-review:** checks PR description for pause block
- **/5-eo-score:** caps Engineering ≤ 7 if no pause block
- **lessons-manager:** captures skipped-pause bugs
