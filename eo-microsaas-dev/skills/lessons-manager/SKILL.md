# lessons-manager — Self-Improvement Loop

**Purpose:** Capture every correction, misstep, and "I should have known" moment into a persistent, per-project lessons file so the same mistake never repeats. This is Boris's compounding lever — the single biggest quality multiplier over time.

**Pillar:** Boris #3 — Self-Improvement Loop
**Time cost:** 30 seconds per lesson. Pays back within the same sprint.

---

## What this skill does

1. **Append** new lessons to `.claude/lessons.md` in the current project
2. **Read** lessons at session start (via SessionStart hook) so they enter context
3. **Surface** relevant lessons when scoring, reviewing, or planning
4. **Prune** stale lessons quarterly (lessons that haven't triggered in 90 days)

---

## The lessons file format

Path: `.claude/lessons.md` (per-project, gitignored by default — solo founder's private memory)

```markdown
# Lessons — {project-name}

Last pruned: YYYY-MM-DD

## Active lessons

### L-001 — Arabic RTL is never optional
- **Captured:** 2026-04-15
- **Trigger:** Shipped pricing page without Arabic test. MENA ICP. Customer complained.
- **Rule:** Any UI component touching MENA users MUST be tested with `dir="rtl"` before scoring UX hat.
- **Check:** UX hat question #2 should auto-fail if RTL untested for MENA ICP.
- **Last triggered:** 2026-04-15

### L-002 — Elegance pause is non-negotiable for new deps
- **Captured:** 2026-04-17
- **Trigger:** Added @react-pdf/renderer (300KB) without bundle check. PR scored 78.
- **Rule:** Any PR adding a new npm dep MUST include bundle size impact in PR description.
- **Check:** Engineering hat question #5 (elegance) auto-caps at 7 if no bundle comment.
- **Last triggered:** 2026-04-17

## Archived lessons (>90 days untriggered)

None yet.
```

---

## When to append a lesson

**Triggers (you MUST append on any of these):**

1. **Score below 80** — the `bridge-gaps` output identified a fixable pattern
2. **Bug in production** — root cause found; write a lesson to prevent recurrence
3. **Code review finds a pattern** — reviewer says "you've done this before"
4. **User correction** — Mamoun / founder says "that's not how we do it here"
5. **Elegance pause retroactive** — you shipped, then realized a better way existed
6. **Boris "knowing now, would I do it again?" — answer is no**

**Do NOT append for:**
- One-off typos
- Tool/library quirks documented in their own README
- Personal preferences without a reusable rule

---

## Lesson quality rubric

A good lesson has 4 parts. Missing any → rewrite before saving.

| Part | Bad | Good |
|------|-----|------|
| Trigger | "Bug in payment flow" | "Stripe webhook retries fired 3x because idempotency key wasn't set. Wed 2026-04-15, cost $180 in duplicate charges." |
| Rule | "Be more careful" | "Every Stripe webhook handler MUST use `Idempotency-Key` header with the event.id." |
| Check | (missing) | "Engineering hat Q3 (error handling) should verify idempotency key on any new webhook." |
| Example | (missing) | "See PR #47 for correct pattern: `src/lib/stripe/webhook.ts:42`" |

---

## Session bootstrap integration

When `SessionStart` fires, the hook should cat `.claude/lessons.md` into the context so Claude reads them automatically. If the file doesn't exist, create it with the header above.

Recommended SessionStart hook (add to `.claude/settings.json`):

```json
{
  "hooks": {
    "SessionStart": [
      {
        "command": "test -f .claude/lessons.md && cat .claude/lessons.md || echo 'No lessons yet for this project.'"
      }
    ]
  }
}
```

---

## Pruning (quarterly)

Every 90 days, for each active lesson:

- If `Last triggered` is within 90 days → keep active
- If `Last triggered` is 90-180 days → move to "Archived" section (still searchable, not loaded at session start)
- If `Last triggered` is >180 days → delete (assume internalized)

Run via `/8-eo-retro` — the retro command prompts a prune pass.

---

## Usage patterns

### Append a lesson (inline)

When triggered, run:

```
eo-scorer detected Engineering hat < 8 because elegance pause skipped.
Appending lesson L-00X to .claude/lessons.md:

### L-00X — {rule title, <10 words}
- **Captured:** {today}
- **Trigger:** {1-2 sentences with specific dollar/hour/bug cost}
- **Rule:** {single imperative sentence}
- **Check:** {which hat question enforces this}
- **Last triggered:** {today}
```

### Surface on demand

When starting a new feature similar to a past lesson, run:

```
grep -l "{topic}" .claude/lessons.md
```

### Read at score time

Before any `/5-eo-score` run, the eo-scorer skill should cat `.claude/lessons.md` and use the rules to calibrate the scoring rubric.

---

## Integration with other skills

| Skill | How it uses lessons |
|-------|---------------------|
| `eo-scorer` | Reads at score time; flags scores that contradict an active lesson |
| `elegance-pause` | Appends lesson when pause is skipped + bug found |
| `brd-traceability` | Appends lesson when a BRD AC ships untested |
| `arabic-rtl-checker` | Appends lesson on any RTL regression |
| `handover-bridge` | Appends lesson on handover gap (EO-Brain → code) |

---

## Anti-patterns

- **Lesson fatigue:** 50+ active lessons = nobody reads them. Prune aggressively.
- **Vague rules:** "Write better code" is not a lesson. Must be checkable.
- **Duplicate lessons:** Before appending, grep for the keyword. If a related lesson exists, extend it instead of adding L-00X.
- **Lessons without checks:** A lesson with no corresponding rubric question is just a note. Tie it to a scoring dimension.
