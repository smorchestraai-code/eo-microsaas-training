---
description: Plan a feature before coding. Reads BRD, past lessons, and drafts an approach.
---

# /2-eo-dev-plan

**Pillar:** Boris #1 — Plan Mode Default
**When to run:** Before writing any code for a new feature.

## What it does

1. **Read context** — `architecture/brd.md`, `.claude/lessons.md`, relevant `project-brain/*.md`, and any matching artifact in `docs/ux-reference/` (the EO-Brain UX ground truth)
2. **Identify ACs** — which BRD acceptance criteria this feature covers
3. **Draft approach** — 3-5 bullets on implementation, in plan mode (no code yet)
4. **Flag risks** — past lessons that apply, deps needed, MENA considerations
5. **Request confirmation** — wait for "go" before leaving plan mode

## Workflow

```
1. Enter plan mode
2. Parse $ARGUMENTS as feature name / BRD story number
3. Cat `.claude/lessons.md` → surface relevant lessons
4. Cat `architecture/brd.md` → extract ACs for this story
5. Read `architecture/tech-stack-decision.md` → respect the recorded SaaSfast mode
6. Read side-car SOPs if present: `skills/eo-dev-start/SAASFAST-MODES.md`, `PAYMENT-PROVIDER-SWAPS.md`
7. If MENA ICP → note arabic-rtl-checker + mena-mobile-check will apply
8. Draft the plan (prefer superpowers:writing-plans if installed; internal drafter otherwise)
9. Optional CEO review pass (gstack:plan-ceo-review if installed) — rewrites plan for founder readability
10. Optional eng review pass (gstack:plan-eng-review if installed) — opinionated architecture/data-flow/edge-case pass
11. Optional design review pass (gstack:plan-design-review if installed AND plan touches UI components) — rates each design dimension 0-10, fixes the plan to get there
12. Present plan, wait for user approval
13. On approval: exit plan mode, begin superpowers:test-driven-development (or /3-eo-code's internal TDD loop if superpowers absent)
```

## Hidden plumbing (graceful degrade)

Skills tried in order, fallback is always local logic — the founder never sees a failure:

| Step | First choice | Fallback |
|------|--------------|----------|
| Draft plan | `superpowers:writing-plans` | Internal plan drafter |
| CEO-review pass | `gstack:plan-ceo-review` | Skip — the plan ships as-is |
| Eng-review pass | `gstack:plan-eng-review` | Skip |
| Design-review pass (UI plans only) | `gstack:plan-design-review` | Skip |
| TDD handoff | `superpowers:test-driven-development` | `/3-eo-code` internal TDD loop |

## Arguments

`$ARGUMENTS` — feature name or BRD story reference (e.g., "password reset" or "Story 1")

## Output

```
## Feature plan: {name}

**BRD ACs:** AC-1.1, AC-1.2, AC-1.3, AC-1.4

**Relevant lessons:**
- L-002: Bundle size check mandatory for new deps

**Approach:**
- …

**Risks / unknowns:**
- …

**MENA checks to run:**
- arabic-rtl-checker (because UI)
- mena-mobile-check (because UI)

**Ready to start TDD?** (y/n)
```

## After approval — update tracker

Before exiting plan mode, update `_dev-progress.md`:
- Find the row for the target story (or add it if missing).
- Set `Status` = `📝 planned`, `Plan` = `✓`, `Notes` = plan filename.
- Set top-level `Last updated` to today, `Last command` to `/2-eo-dev-plan {story}`.

Filesystem is truth — `/eo-guide` will reconcile if you slip.
