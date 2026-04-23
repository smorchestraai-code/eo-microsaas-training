---
name: eo-dev-start
description: "First-run bootstrap for a fresh EO MicroSaaS project. Reads EO-Brain phases 0-4 from filesystem, classifies bootstrap state (empty | partial | bootstrapped), enters plan mode with approval gate, and invokes handover-bridge on approval. Never overwrites. Refuses and routes to /eo-dev-repair or /eo-guide when state is not empty. Triggers on: 'eo dev start', 'bootstrap project', 'set up claude code', 'first time', 'ابدأ المشروع'."
version: "1.0"
---

# eo-dev-start — First-Run Bootstrap

**Version:** 1.0 (2026-04-21)
**Pillar:** EO-specific — the single entry point from EO-Brain strategy to Claude Code execution.
**Purpose:** Replace the 75-line copy-paste bootstrap prompt from `5-CodeHandover/README.md` with one command that reads EO-Brain output, previews exactly what it will create, waits for approval, then executes `handover-bridge` with parameters extracted from phases 0-4.

**Hard contract:** writes nothing without explicit student approval inside plan mode. Refuses on any non-empty state. Never decides repair (that's `/eo-dev-repair`'s job).

---

## Why this skill exists

The previous flow was: student copy-pastes a 75-line prompt that hardcodes project name, stack, ICP, deploy lane. Three failure modes:

1. **Hardcoded identity** — the template is for EO Oasis, not a reusable command. Every student edits by hand.
2. **No idempotency guard** — re-running overwrites `CLAUDE.md`, `.claude/lessons.md` silently.
3. **No repair vs. bootstrap split** — if something's partially wrong, the student doesn't know which command recovers.

This skill closes all three.

---

## Three states, three routes

### State A — `empty`
- Project folder has **no** `CLAUDE.md`, **no** `.claude/lessons.md`, **no** `architecture/brd.md`, **no** `src/`, **no** `_dev-progress.md`, **no** `.git/` history beyond initial commit.
- EO-Brain phases 0-4 are reachable (via symlink, sibling folder, or subfolder — see Step 2).
- **Route:** enter plan mode → preview → approve → bootstrap.

### State B — `partial`
- Any of the bootstrap files exists, but not all.
- **Route:** refuse. Print classified findings. Tell student to run `/eo-dev-repair`.
- This skill never decides repair. `/eo-dev-repair` owns that.

### State C — `bootstrapped`
- All of: `CLAUDE.md`, `.claude/lessons.md`, `architecture/brd.md`, `_dev-progress.md`, `.github/workflows/ci.yml`, and at least one `feat:` or `chore(bootstrap):` commit on `main` or `dev`.
- **Route:** refuse. Tell student to run `/eo-guide` for next step.

---

## Execution sequence

### Step 1 — Resolve workspace root

Worktree-aware:
```
if [ -n "$GIT_WORK_TREE" ]; then
  ROOT="$GIT_WORK_TREE"
elif git rev-parse --show-toplevel >/dev/null 2>&1; then
  ROOT="$(git rev-parse --show-toplevel)"
else
  ROOT="$PWD"  # greenfield — no git yet
fi
```

Never assume `pwd` is the repo root.

### Step 2 — Locate EO-Brain

Search in order (first match wins):
1. `$ROOT/EO-Brain/` (sibling inside project)
2. `$ROOT/../EO-Brain/` (sibling next to project)
3. `$ROOT/../../EO-MicroSaaS-Training/8-EO-Brain-Starter-Kit/EO-Brain/` (starter kit path)
4. Symlink `$ROOT/eo-brain` or `$ROOT/.eo-brain`

If none found → **refuse with remediation:**
```
❌ EO-Brain not reachable from {ROOT}.

Expected one of:
  {ROOT}/EO-Brain/
  {ROOT}/../EO-Brain/
  symlink {ROOT}/eo-brain

Remediation:
  1. Finish EO-Brain phases 0-4 in Cowork OR
  2. Symlink your existing EO-Brain folder:
       ln -s /path/to/EO-Brain {ROOT}/eo-brain

No writes made. Re-run /eo-dev-start after fixing.
```

### Step 3 — Detect language

Read `$EO_BRAIN/_language-pref.md` (set during EO-Brain Phase 0).
- `ar` → Arabic-first Gulf output, English tech terms mixed naturally. Not MSA.
- `en` → Direct English.
- Missing → ask once: "Arabic or English output? (ar/en)" — then write to `$EO_BRAIN/_language-pref.md` so this never asks again.

### Step 4 — Scan bootstrap signals

Collect these 11 signals in one filesystem pass (record `present/absent` + timestamp):

| # | Signal | Path | Meaning if present |
|---|--------|------|--------------------|
| 1 | CLAUDE.md | `$ROOT/CLAUDE.md` | Bootstrap attempted |
| 2 | Lessons | `$ROOT/.claude/lessons.md` | Self-improvement loop seeded |
| 3 | SessionStart hook | `$ROOT/.claude/settings.json` | Lessons auto-load on session |
| 4 | BRD | `$ROOT/architecture/brd.md` | Spec present |
| 5 | Tracker | `$ROOT/_dev-progress.md` | `/eo-guide` can read state |
| 6 | CI | `$ROOT/.github/workflows/ci.yml` | PR quality gate |
| 7 | src/ | `$ROOT/src/` or `$ROOT/app/` | Scaffold present |
| 8 | tests/ | `$ROOT/tests/` | Test skeletons present |
| 9 | UX reference | `$ROOT/docs/ux-reference/` | Artifacts ingested |
| 10 | .env.example | `$ROOT/.env.example` | Env contract present |
| 11 | First commit | `git log --oneline --all \| head -1` | History started |

### Step 5 — Classify state

- **empty** = signals 1, 2, 4, 5, 7, 11 all absent (no bootstrap artifacts at all)
- **bootstrapped** = signals 1, 2, 4, 5, 6 all present AND signal 11 shows a `feat:` or `chore(bootstrap):` commit
- **partial** = anything else

### Step 6 — Route by state

#### State C (bootstrapped) — refuse + route to `/eo-guide`

```
✅ Project is already bootstrapped.

Evidence:
  CLAUDE.md              — {size} bytes, {lines} lines
  architecture/brd.md    — {story_count} stories, {ac_count} ACs
  .claude/lessons.md     — {lesson_count} active lessons
  First commit           — {sha} "{subject}"

Next:
  /eo-guide              ← figures out what command you should run now
```

No writes. Exit.

#### State B (partial) — refuse + route to `/eo-dev-repair`

```
⚠️ Project is partially bootstrapped — /eo-dev-start does not handle this.

Signals present:
  {list of present signals with timestamps}

Signals missing:
  {list of absent signals}

Next:
  /eo-dev-repair         ← triages missing pieces and decides silent-repair vs refuse
```

No writes. Exit.

#### State A (empty) — proceed to plan mode

Continue to Step 7.

### Step 7 — Verify EO-Brain completeness

Required phase files (refuse if any missing):

| Phase | File | Purpose |
|-------|------|---------|
| 0 | `EO-Brain/0-Scorecards/` (any `.md`) | At least one scorecard present |
| 1 | `EO-Brain/1-ProjectBrain/icp.md` | ICP extraction |
| 1 | `EO-Brain/1-ProjectBrain/brandvoice.md` | Voice for CLAUDE.md |
| 1 | `EO-Brain/1-ProjectBrain/profile-settings.md` | Founder identity (optional, warn only) |
| 4 | `EO-Brain/4-Architecture/brd.md` | Spec with AC-N.N tags |
| 4 | `EO-Brain/4-Architecture/tech-stack-decision.md` | Stack identity |
| 5 | `EO-Brain/5-CodeHandover/artifacts/` | UX ground truth (warn only if empty — UX hat caps at 8 until present) |

BRD quality gate:
- Parse `architecture/brd.md` for `## Story` headers → count must be ≥ 1
- Parse for `AC-N.N` tags → count must be ≥ 3 per story

If any **refuse** row missing → print exact list + remediation + exit. No writes.

### Step 8 — Extract project identity from EO-Brain

Read and parse (no writes yet):

| Field | Source | Fallback |
|-------|--------|----------|
| `project_name` | `1-ProjectBrain/positioning.md` or first `# ` header in any phase-1 file | Ask student |
| `founder_name` | `1-ProjectBrain/profile-settings.md` key `founder:` | Git config `user.name` |
| `founder_email` | `1-ProjectBrain/profile-settings.md` key `email:` | Git config `user.email` |
| `stack` | `4-Architecture/tech-stack-decision.md` key `stack:` or first table row | Fail — require it |
| `icp_summary` | `1-ProjectBrain/icp.md` first 3 bullet points | Fail — require it |
| `story_count` | `## Story N` header count in `4-Architecture/brd.md` | Fail — require ≥1 |
| `ac_count` | `AC-N.N` unique tag count in `4-Architecture/brd.md` | Fail — require ≥3 |
| `mena_flag` | `1-ProjectBrain/icp.md` contains any of `Cairo Amman Riyadh Dubai UAE KSA MENA Arabic` → `true` | `false` |
| `deploy_lane` | `4-Architecture/tech-stack-decision.md` key `deploy:` | `vercel` (safe default) |

### Step 9 — Plan-mode preview (the approval gate)

Enter plan mode. Print exactly this (English template shown; Arabic analog when `lang=ar`):

```
📋 Bootstrap plan for: {project_name}

Source of truth: {EO_BRAIN path}

Will create:
  CLAUDE.md                  — ~{estimated_lines} lines, project-calibrated from template
  .claude/lessons.md         — empty, seeded with "First lesson captured on first score <90"
  .claude/settings.json      — SessionStart hook to auto-load lessons
  architecture/brd.md        — copied from EO-Brain
  architecture/*.md          — copied from 4-Architecture/
  docs/ux-reference/         — copied from 5-CodeHandover/artifacts/ ({artifact_count} files)
  docs/qa-scores/            — empty dir (score history)
  docs/handovers/            — empty dir
  docs/retros/               — empty dir
  src/                       — Next.js 14 App Router scaffold (TypeScript + Tailwind + RTL)
  tests/*.test.ts            — {ac_count} placeholder tests tagged @AC-N.N ({story_count} stories)
  .github/workflows/ci.yml   — PR quality gate (lint + test + build + audit)
  _dev-progress.md           — tracker row per story (⬜ not started)
  .env.example               — extracted from tech-stack-decision.md (no real secrets)
  .gitignore                 — .env.local, node_modules/, .next/, docs/secrets/
  README.md                  — project overview linking to EO-Brain
  First commit               — "chore(bootstrap): initial handoff from EO-Brain phases 0-4"

Identity applied:
  Project         {project_name}
  Founder         {founder_name} <{founder_email}>
  Stack           {stack}
  ICP             {icp_summary first 80 chars}
  MENA            {mena_flag}
  Deploy          {deploy_lane}
  Stories         {story_count}
  ACs             {ac_count}
  Language        {lang}

Will NOT:
  - Overwrite any existing file at {ROOT}
  - Write real secrets anywhere
  - Skip the score gate (still ≥90 to ship, ≥8 per hat)
  - Run git push (you review + push manually after first commit)

Approve? (y/n)
```

On `n` → exit cleanly, no writes. On `y` → proceed to Step 10.

### Step 10 — Invoke `handover-bridge`

Pass the identity fields from Step 8 to the `handover-bridge` skill. Execute its 11-step sequence. If any step fails:
- Log the failure to `$ROOT/.bootstrap-failures.log`
- Attempt to roll back writes in that step only (not earlier steps)
- Exit with clear remediation

### Step 11 — Evidence table

After `handover-bridge` returns success, print evidence-based completion (never prose "done"):

```
✅ Bootstrap complete.

Files created:
  CLAUDE.md                  {lines} lines, {bytes} bytes
  .claude/lessons.md         {bytes} bytes (seeded)
  .claude/settings.json      {bytes} bytes (hook active)
  architecture/brd.md        {lines} lines, {story_count} stories, {ac_count} ACs
  _dev-progress.md           {story_count} tracker rows
  tests/*.test.ts            {file_count} files, {ac_count} @AC-N.N tags
  .github/workflows/ci.yml   {bytes} bytes
  docs/ux-reference/         {artifact_count} artifacts
  .env.example               {env_var_count} variables (no values)

Git:
  First commit: {sha} "chore(bootstrap): initial handoff from EO-Brain phases 0-4"
  Branch: {branch_name}

Next command:
  /eo-plan Story-1-{first_story_slug}

Before you run it:
  - Skim CLAUDE.md (≤150 lines) — make sure it reflects your project
  - Skim architecture/brd.md — confirm all {ac_count} ACs are yours
  - git push origin {branch_name} if this is your first commit
```

---

## Anti-patterns

- **Never write outside plan-mode approval.** If the student says `n`, nothing lands.
- **Never overwrite.** If a file exists, refuse and route to `/eo-dev-repair`. Don't merge silently.
- **Never invent identity.** If EO-Brain is missing a required field, refuse with remediation. Don't ask the student to fill in what should have come from phases 0-4.
- **Never decide repair.** Partial state → `/eo-dev-repair`. Period.
- **Never skip language detection.** `lang=ar` students get Arabic output for the plan preview and evidence table.
- **Never run `git push`.** The student reviews + pushes manually. The skill writes the first commit to the local repo only.

---

## Integration

| Skill | Relationship |
|-------|--------------|
| `handover-bridge` | Invoked from Step 10. All heavy lifting (scaffold, tests, CI, lessons seed) happens there. |
| `eo-dev-repair` | Routed to when state is `partial`. Never called directly from here. |
| `eo-guide` | Routed to when state is `bootstrapped`. `eo-guide` also routes back here when it detects `pre-bootstrap` phase. |

---

## Self-score protocol

After every run, verify:

| # | Check | Threshold |
|---|-------|-----------|
| 1 | Workspace root resolved (worktree-aware) | must pass |
| 2 | Language detected from `_language-pref.md` or asked + saved | must pass |
| 3 | All 11 bootstrap signals scanned | must pass |
| 4 | State classified as exactly one of empty/partial/bootstrapped | must pass |
| 5 | EO-Brain completeness verified before plan mode | must pass |
| 6 | Plan-mode preview printed with identity fields | must pass |
| 7 | No writes before student approval | must pass |
| 8 | `handover-bridge` invoked with extracted identity (not defaults) | must pass |
| 9 | Evidence table printed post-success with bytes + line counts | must pass |
| 10 | Next command recommendation cites first Story slug from BRD | must pass |

Threshold: 10/10. Below = bug → capture in `.claude/lessons.md`.
