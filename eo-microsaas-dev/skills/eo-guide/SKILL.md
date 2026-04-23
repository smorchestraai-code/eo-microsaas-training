---
name: eo-guide
description: "Student-resumption guide for Claude Code build phase. Scans project state, detects current phase of the build loop, and recommends the next /eo-* command. Works in fresh chats — student types /eo-guide after opening Claude Code in the project, gets phase + next command + ETA. Routes to /eo-dev-start for fresh projects, /eo-dev-repair for partial bootstraps, and /eo-github for local-only projects ready to promote. Triggers on: 'eo guide', 'where am I', 'what's next', 'next step', 'guide me', '/eo-status', 'status', 'check progress'."
version: "1.3.1"
---

# eo-guide — The Build-Phase Orchestrator

**Version:** 1.3.1 (2026-04-23 — hardens local-only path so sprint-loop phases continue to advance; adds explicit exit guidance for stuck states)
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
| Git repo present | `git rev-parse --show-toplevel 2>/dev/null` | Bootstrap happened with git (`github_intent ≠ local-only`) |
| Git remote origin | `git config --get remote.origin.url 2>/dev/null` | GitHub is mounted — `/eo-ship` will push there |

Write observed values into a temp state object — this is what drives the next step.

### Step 4 — Phase detection state machine

Before ordering matches, derive two booleans that ride along every sprint-loop row:

- `has_git` = `git rev-parse --show-toplevel` succeeds
- `has_remote` = `git config --get remote.origin.url` returns non-empty

Evaluate in order; first match wins:

| # | Condition | Phase | Next command |
|---|-----------|-------|--------------|
| 1 | No `CLAUDE.md` AND no `architecture/brd.md` AND no `.claude/lessons.md` (truly empty) | `pre-bootstrap` | `/eo-dev-start` — reads EO-Brain, plan-mode gate, invokes handover-bridge. Supersedes the old "copy-paste Section 5 prompt" flow. |
| 2 | At least one but not all of: `CLAUDE.md`, `.claude/lessons.md`, `_dev-progress.md`, `.github/workflows/ci.yml`, `.env.example`, `docs/ux-reference/` (partial state) | `bootstrap-incomplete` | `/eo-dev-repair` — triages missing pieces, silently repairs regeneratable files, refuses and routes when core artifacts (BRD, architecture, project-brain) are missing. |
| 3 | Bootstrap complete (all of: `CLAUDE.md`, `.claude/lessons.md`, `_dev-progress.md`, `.github/workflows/ci.yml`) **AND** `has_git=false` **AND** no `docs/plans/story-*.md` files yet | `local-only-bootstrapped` | Keep building locally. Your next sprint step is `/eo-plan Story-1-{slug}`. Run it when you're ready to plan Story 1. When your MVP ships end-to-end, run `/eo-github` to push up. No git, no network until then. |
| 4 | No plan file for any ⬜ story | `ready-to-plan` | `/eo-plan Story-{N}-{slug}` for the first ⬜ story |
| 5 | Plan exists, all tests `.skip` for target story | `ready-to-code` | `/eo-code` |
| 6 | Tests pass for target story, no score file today | `ready-to-score` | `/eo-score` |
| 7 | Latest score < 80 | `blocked-low-score` | Revisit plan; lesson capture required; do NOT ship |
| 8 | Latest score 80–89 | `bridging-gaps` | `/eo-bridge-gaps` then re-score |
| 9 | Latest score ≥ 90, no `ship:` commit for this story, `has_git=true`, `has_remote=true` | `ready-to-ship` | `/eo-ship` |
| 10 | Latest score ≥ 90, no `ship:` commit for this story, `has_git=true`, `has_remote=false` | `ready-to-ship-but-no-remote` | Run `/eo-github` first (create or point-existing). `/eo-ship` needs a remote to push to. |
| 11 | Latest score ≥ 90, no `ship:` commit for this story, `has_git=false` (local-only student reached ship-readiness) | `ready-to-ship-local-only` | 🎉 MVP ready to go public. Run `/eo-github` → pick `create` or `point-existing`. That skill does git init + first commit + push in one shot. Then re-run `/eo-ship`. |
| 12 | `ship:` commit exists, no retro for this sprint | `ready-to-retro` | `/eo-retro` |
| 13 | All BRD stories shipped + retros done | `project-complete` | Soft launch + 15 listings |
| 14 | None of the above → inconsistent | `inconsistent` | Fall through to Mode 3 diagnostic |

**Critical ordering rule:** `local-only-bootstrapped` (row 3) only fires when **no plan files exist yet** — i.e., the student just bootstrapped and hasn't started Story 1. Once the first plan file lands, rows 4–13 take over and the student advances through sprint-loop phases normally. This prevents the "perpetually stuck at local-only-bootstrapped" trap where local-only students who have been coding for weeks would never see sprint-loop guidance.

**Still-local banner (rows 4–8 when `has_git=false`):** prepend this line to the Step 7 recommendation:

```
🔒 Still local (no git yet). /eo-github will promote when MVP is ready.
```

**Git-local-no-remote banner (rows 4–8 when `has_git=true` AND `has_remote=false`):** prepend:

```
🔗 Git local, no remote yet. Run /eo-github to mount origin. /eo-ship will refuse until then.
```

Banners are informational — they never block the recommended next command. Sprint work continues whether or not GitHub is wired up.

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
{optional banner: 🔒 Still local... OR 🔗 Git local, no remote...}
📍 You're at: {phase}
✅ Completed: {list}
⏭️ Next: {exact command}
⏱️ ETA: {minutes}
🧱 Story: {N} — {slug}
📊 Sprint: {sprint number} / MVP has {total} sprints
```

Arabic template:
```
{optional banner: 🔒 لسه محلّي... OR 🔗 في git محلي بدون ريموت...}
📍 أنت في: {phase — translated}
✅ خلصت: {list}
⏭️ الخطوة الجاية: {command}
⏱️ الوقت المتوقع: {دقايق}
🧱 القصة: {N} — {slug}
📊 السبرنت: {N} من {total}
```

One screen. No explanations unless student asks "why."

---

## Stuck-state exits (for every refuse path)

A router that refuses must always name the next door the student can open. Every phase in the state machine must resolve to one of: (a) a concrete `/eo-*` command, (b) a Mode 3 diagnostic with a safe re-sync command, or (c) a documented manual exit. There is no terminal "stuck" state.

| Symptom | What to check | Exit |
|---------|---------------|------|
| `/eo-guide` prints "Keep building locally" every time despite progress | You have plan files but chose local-only. Row 3 should yield to sprint-loop rows. | If row 3 still fires after plan files exist → file a lessons.md entry and run the target sprint command directly (`/eo-plan`, `/eo-code`, etc.). |
| "State inconsistent" with no clear diff | Mode 3 diagnostic is running. | Re-run `/eo-score` to regenerate a fresh score file; then `/eo-guide` again. |
| "No `CLAUDE.md` found but `architecture/` exists" | Partial bootstrap. | `/eo-dev-repair` triages. If it refuses, re-run `/eo-dev-start` in a fresh sub-folder and copy `architecture/` across. |
| `/eo-guide` routes to `/eo-github` but MCP is missing | Student picked a GitHub path without MCP connected. | Stay in local-only mode. The sprint loop works end-to-end without GitHub. Install GitHub MCP later; `/eo-github` is idempotent. |
| `ready-to-ship-local-only` but student doesn't want GitHub | `/eo-ship` needs git + remote. | Two doors: (1) run `/eo-github` to promote, (2) keep shipping to your own infra manually — set up an internal `/deploy` path outside this plugin. `/eo-ship` will refuse until git+remote exist. |

---

## Mode 2 — `/eo-status` (compact dashboard)

No coaching. Just the table:

```
EO Build Dashboard — {PROJECT_NAME}
====================================
Bootstrap:   ✅ (CLAUDE.md, CI, tracker all present)
Git:         ✅ local  |  🔗 origin: git@github.com:{owner}/{repo}.git
             ✅ local  |  ⚠️ no remote — run /eo-github
             🚫 no git (local-only bootstrap — run /eo-github when MVP ready)
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
| `eo-github` | `/eo-guide` detects git + remote presence and routes students to `/eo-github` for `local-only-bootstrapped`, `git-local-no-remote`, and `ready-to-ship-but-no-remote` states. Never invokes the skill directly — students always run it explicitly. |
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
- **Short-circuiting sprint-loop rows for local-only students.** Row 3 (`local-only-bootstrapped`) must yield to rows 4–13 once any plan file exists. A local-only student coding for weeks should advance through sprint phases with a banner, not perpetually hear "keep building locally."
- **Leaving a refuse path without an exit.** Every refuse prints a concrete next command, a safe re-sync, or a manual exit. A student must never see "can't help" with no door.

---

## Self-score protocol

After every run, the skill internally verifies:

| # | Check |
|---|-------|
| 1 | Workspace root correctly resolved (worktree-aware) |
| 2 | Language detected and applied |
| 3 | All 12 filesystem signals collected (incl. `has_git` + `has_remote`) |
| 4 | Phase detection matched exactly one condition |
| 5 | Inconsistent-state rail fired when applicable |
| 6 | `_dev-progress.md` reconciled + diff logged |
| 7 | Recommendation cites one concrete next command |
| 8 | ETA included |
| 9 | Output fits one screen (no essay) |
| 10 | No shipping recommendation in Mode 3 |
| 11 | `local-only-bootstrapped` (row 3) only fires when no plan files exist (no sprint-loop short-circuit) |
| 12 | Still-local / no-remote banner prepended on sprint-loop rows 4–8 when appropriate |
| 13 | `ready-to-ship-local-only` routes to `/eo-github` before `/eo-ship` (not directly to `/eo-ship`) |
| 14 | Every refuse path names a concrete next door (no terminal "stuck" state) |

Threshold: 14/14. Below = bug. File at `.claude/lessons.md` as a trigger for future hardening.
