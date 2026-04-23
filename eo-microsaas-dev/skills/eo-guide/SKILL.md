---
name: eo-guide
description: "Student-resumption guide for Claude Code build phase. Scans project state, detects current phase of the build loop, and recommends the next /eo-* command. Works in fresh chats — student types /eo-guide after opening Claude Code in the project, gets phase + next command + ETA. Routes to /eo-dev-start for fresh projects and /eo-dev-repair for partially-bootstrapped projects. Triggers on: 'eo guide', 'where am I', 'what's next', 'next step', 'guide me', '/eo-status', 'status', 'check progress'."
version: "1.2"
---

# eo-guide — The Build-Phase Orchestrator

**Version:** 1.2 (2026-04-21 — adds bootstrap-aware routing to /eo-dev-start + /eo-dev-repair)
**Pillar:** EO-specific — cross-chat continuity.
**Purpose:** When a student opens a fresh Claude Code chat in a project — mid-sprint, 3 days after last session, or from a new machine — they type `/eo-guide` and get: where they are, what's next, how long it takes. Zero context-paste. The whole point is resumability.

---

## Why this skill exists

Students leave chats mid-sprint. They lose track of "did I score this story yet?" or "was story 3 planned or just mentioned?" Without a guide:
- They re-plan stories they already planned.
- They ship with scores below 90 because they forgot to re-score.
- They panic at week 3 thinking they should be done when the MVP needs 4–7 sprints.

This skill is the single source of truth that answers "what's the next command to run" from the filesystem alone.

---

## Three modes

### Mode 1 — `/eo-guide` (returning student, default)
Scan → detect phase → recommend one next command → reconcile `_dev-progress.md`.

### Mode 2 — `/eo-status` (compact dashboard, no coaching)
Scan → print status table only. No next-step recommendation. For quick glances.

### Mode 3 — inconsistent-state fallback
Triggered automatically inside Mode 1 when the state machine detects impossible configurations. Outputs a diagnostic, never a destructive or shipping recommendation.

---

## Mode 1 execution sequence (returning student)

### Step 1 — Resolve workspace root

Handle git worktrees explicitly:
- If `$GIT_WORK_TREE` is set, use it as root.
- Else, run `git rev-parse --show-toplevel` and use that.
- Never assume `pwd` is the repo root.

### Step 2 — Read language preference

Look for `lang:` in `CLAUDE.md` frontmatter OR `MENA: yes/no` flag OR `.claude/settings.json` `lang` key. Default to English if unset.

- `lang: ar` → Arabic-first Gulf output, English tech terms mixed naturally. Not MSA.
- `lang: en` → Direct English, MENA context retained when relevant.

### Step 3 — Filesystem scan (source of truth)

Collect these signals in one pass:

| Signal | Check | Meaning |
|--------|-------|---------|
| `CLAUDE.md` at root | `test -f CLAUDE.md` | Bridge ran if present |
| `_dev-progress.md` at root | `test -f _dev-progress.md` | Tracker seeded |
| `architecture/brd.md` | `test -f architecture/brd.md` | BRD present, story count from `## Story N` headers |
| Plan files | `ls docs/plans/story-*.md` | Which stories have plans |
| Test files | `ls tests/*.test.*` | Count `describe.skip` vs `describe` |
| Score files | `ls docs/qa-scores/*.md` | Latest composite + per-hat |
| Recent commits | `git log --oneline -20` | Look for `feat:`, `ship:`, `chore(score):` |
| Retros | `ls docs/retros/*.md` | Sprint close signals |
| Lessons | `wc -l .claude/lessons.md` | Under "Active lessons" section |
| CI | `test -f .github/workflows/ci.yml` | Quality gate installed |

Write observed values into a temp state object — this is what drives the next step.

### Step 4 — Phase detection state machine

Evaluate in order; first match wins:

| Condition | Phase | Next command |
|-----------|-------|--------------|
| No `CLAUDE.md` AND no `architecture/brd.md` AND no `.claude/lessons.md` (truly empty) | `pre-bootstrap` | `/eo-dev-start` — reads EO-Brain, plan-mode gate, invokes handover-bridge. Supersedes the old "copy-paste Section 5 prompt" flow. |
| At least one but not all of: `CLAUDE.md`, `.claude/lessons.md`, `_dev-progress.md`, `.github/workflows/ci.yml`, `.env.example`, `docs/ux-reference/` (partial state) | `bootstrap-incomplete` | `/eo-dev-repair` — triages missing pieces, silently repairs regeneratable files, refuses and routes when core artifacts (BRD, architecture, project-brain) are missing. |
| No plan file for any ⬜ story | `ready-to-plan` | `/eo-plan Story-{N}-{slug}` for the first ⬜ story |
| Plan exists, all tests `.skip` for target story | `ready-to-code` | `/eo-code` |
| Tests pass for target story, no score file today | `ready-to-score` | `/eo-score` |
| Latest score < 80 | `blocked-low-score` | Revisit plan; lesson capture required; do NOT ship |
| Latest score 80–89 | `bridging-gaps` | `/eo-bridge-gaps` then re-score |
| Latest score ≥ 90, no `ship:` commit for this story | `ready-to-ship` | `/eo-ship` |
| `ship:` commit exists, no retro for this sprint | `ready-to-retro` | `/eo-retro` |
| All BRD stories shipped + retros done | `project-complete` | Soft launch + 15 listings |
| None of the above → inconsistent | `inconsistent` | Fall through to Mode 3 diagnostic |

### Step 5 — Safety rail (inconsistent state)

Trigger Mode 3 if ANY of these hold:
- Score file exists but no tests at all.
- Tests pass but no plan file.
- `ship:` commit exists but no score ≥ 90 that day.
- `_dev-progress.md` says "shipped" but no `ship:` commit.
- BRD has stories that `_dev-progress.md` doesn't list, or vice versa.

Output template:

```
⚠️ State inconsistent. Can't safely recommend the next step.

Found:
  - {evidence item 1}
  - {evidence item 2}

Missing or conflicting:
  - {missing item 1}
  - {conflict 1}

Safe next step: {last known-good command, e.g., "re-run /eo-score to resync"}.
Never auto-ship when state is inconsistent.
```

### Step 6 — Reconcile `_dev-progress.md`

Rewrite the file from derived state. Preserve notes column if present. Always update `Last updated`, `Current sprint`, `Last command`.

If the filesystem-derived row differs from what was there: add a one-line diff at the bottom under `## Reconciliation log`.

### Step 7 — Print recommendation

English template:
```
📍 You're at: {phase}
✅ Completed: {list}
⏭️ Next: {exact command}
⏱️ ETA: {minutes}
🧱 Story: {N} — {slug}
📊 Sprint: {sprint number} / MVP has {total} sprints
```

Arabic template:
```
📍 أنت في: {phase — translated}
✅ خلصت: {list}
⏭️ الخطوة الجاية: {command}
⏱️ الوقت المتوقع: {دقايق}
🧱 القصة: {N} — {slug}
📊 السبرنت: {N} من {total}
```

One screen. No explanations unless student asks "why."

---

## Mode 2 — `/eo-status` (compact dashboard)

No coaching. Just the table:

```
EO Build Dashboard — {PROJECT_NAME}
====================================
Bootstrap:   ✅ (CLAUDE.md, CI, tracker all present)
BRD stories: 5 total
Story 1:     ✅ shipped — score 94 — 2026-04-19
Story 2:     🔨 coding — 3/5 tests passing — sprint 2
Story 3:     📝 planned — tests all .skip
Story 4:     ⬜ not started
Story 5:     ⬜ not started
Latest score: 92 (Story 2 draft, 2026-04-21)
Lessons: 4 active
CI: last run green (2h ago)
```

Symbols: ✅ shipped, 🔨 coding, 📝 planned, ⬜ not started, 🩹 bridging, 🧪 scoring, ⚠️ inconsistent.

---

## Mode 3 — Inconsistent state (diagnostic)

Already specified in Step 5 above. Rules of engagement:
- Never recommend `/eo-ship` in Mode 3.
- Never recommend destructive actions (`git reset`, `rm`, `force push`).
- Always offer the safest re-sync command (usually `/eo-score` or re-running `handover-bridge`).
- Log the diagnostic to `docs/retros/_inconsistent-state-{DATE}.md` for later inspection.

---

## Cross-chat continuity contract

This is the core promise of the skill:

> A student who closes Claude Code mid-sprint, walks away for 3 days, opens a new chat in the project, and types `/eo-guide` gets the exact next command to run — without pasting context.

To keep this promise:
- Read the filesystem every time. Never rely on in-conversation state.
- Rewrite `_dev-progress.md` every invocation. Keep it in sync.
- Respect git worktrees.
- Give Arabic output to MENA projects.
- Never lie about ship readiness.

---

## Integration with other skills

| Skill | Relationship |
|-------|--------------|
| `handover-bridge` | Produces the files `/eo-guide` reads. If bootstrap never ran, `/eo-guide` says so. |
| `eo-scorer` | Writes score files that `/eo-guide` parses for phase detection. |
| `brd-traceability` | Defines the `@AC-N.N` tag that `/eo-guide` uses to count tests per story. |
| `lessons-manager` | Surfaces relevant lessons when the state shows repeated failures on the same story. |
| `/eo-plan` through `/eo-retro` | Each writes one row to `_dev-progress.md` at end-of-run. `/eo-guide` reconciles. |

---

## Fixtures (regression harness)

See `fixtures/README.md`. Each fixture is a tarball snapshot of a project in one phase. Expected `/eo-guide` output is documented. Used for manual regression before releases.

| Fixture | Phase expected | Expected next command |
|---------|----------------|----------------------|
| `01-pre-bootstrap.tar.gz` | `pre-bootstrap` | bootstrap prompt |
| `02-bootstrap-incomplete.tar.gz` | `bootstrap-incomplete` | re-run `handover-bridge` |
| `03-ready-to-plan.tar.gz` | `ready-to-plan` | `/eo-plan Story-1-signup` |
| `04-ready-to-code.tar.gz` | `ready-to-code` | `/eo-code` |
| `05-ready-to-score.tar.gz` | `ready-to-score` | `/eo-score` |
| `06-bridging-gaps.tar.gz` | `bridging-gaps` | `/eo-bridge-gaps` |
| `07-ready-to-ship.tar.gz` | `ready-to-ship` | `/eo-ship` |
| `08-inconsistent.tar.gz` | `inconsistent` | Mode 3 diagnostic (no ship) |

---

## Anti-patterns

- **Trusting `_dev-progress.md` blindly.** It's a view. Filesystem wins. Always reconcile.
- **Silently skipping the bootstrap check.** If `CLAUDE.md` is missing, say so — don't guess the phase.
- **Shipping in Mode 3.** Never recommend a merge when state is inconsistent.
- **Hardcoding language.** Always read `CLAUDE.md` frontmatter or settings. Respect `lang: ar`.
- **Ignoring worktrees.** If `$GIT_WORK_TREE` is set, the repo root is NOT `pwd`.

---

## Self-score protocol

After every run, the skill internally verifies:

| # | Check |
|---|-------|
| 1 | Workspace root correctly resolved (worktree-aware) |
| 2 | Language detected and applied |
| 3 | All 10 filesystem signals collected |
| 4 | Phase detection matched exactly one condition |
| 5 | Inconsistent-state rail fired when applicable |
| 6 | `_dev-progress.md` reconciled + diff logged |
| 7 | Recommendation cites one concrete next command |
| 8 | ETA included |
| 9 | Output fits one screen (no essay) |
| 10 | No shipping recommendation in Mode 3 |

Threshold: 10/10. Below = bug. File at `.claude/lessons.md` as a trigger for future hardening.
