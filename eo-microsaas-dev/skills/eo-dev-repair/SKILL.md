---
name: eo-dev-repair
description: "Triage a partially-bootstrapped EO MicroSaaS project. Classifies each missing piece as silent-repair-safe (regeneratable from templates/EO-Brain) or refuse-and-route (core artifact that must come from EO-Brain phases 0-4). Silently repairs the former under plan-mode approval. Refuses and prints remediation for the latter. Never decides beyond this boundary. Triggers on: 'eo dev repair', 'fix bootstrap', 'missing CLAUDE.md', 'rebuild lessons', 'project broken', 'أصلح المشروع'."
version: "1.0"
---

# eo-dev-repair — Bootstrap Triage + Surgical Repair

**Version:** 1.0 (2026-04-21)
**Pillar:** EO-specific — the recovery command. Owns the "what's regeneratable vs. what isn't" decision so `/eo-dev-start` stays a pure happy-path bootstrap.
**Purpose:** Students delete files, switch branches, partially ingest EO-Brain, or get halfway through bootstrap and lose context. This skill triages the damage and either repairs surgically or refuses with clear remediation. Never destroys data.

**Hard contract:** mixed state (some silent-repair-safe + some refuse-and-route missing) → refuse all repair. Surface the root cause. Partial repair is worse than no repair because it hides the upstream gap.

---

## The classification table

Every bootstrap signal has exactly one class.

### Silent-repair-safe (regeneratable)

These can be rebuilt from templates or read from EO-Brain without losing student intent:

| Signal | Path | Source |
|--------|------|--------|
| CLAUDE.md | `CLAUDE.md` | `templates/CLAUDE.md.template` + identity from EO-Brain |
| Lessons seed | `.claude/lessons.md` | `templates/lessons.md.template` (empty by design) |
| SessionStart hook | `.claude/settings.json` | `templates/settings.json.template` |
| Tracker | `_dev-progress.md` | `templates/_dev-progress.md.template` + one row per BRD story |
| CI workflow | `.github/workflows/ci.yml` | `templates/ci.yml.template` |
| Env contract | `.env.example` | Extract env vars from `4-Architecture/tech-stack-decision.md` |
| Gitignore | `.gitignore` | `templates/.gitignore.template` |
| Placeholder tests | `tests/*.test.ts` | Generate `.skip` stubs from BRD `AC-N.N` tags |
| UX reference | `docs/ux-reference/` | Copy from `5-CodeHandover/artifacts/` |
| Doc dirs | `docs/qa-scores/`, `docs/handovers/`, `docs/retros/` | `mkdir -p` |

### Refuse-and-route (cannot be regenerated — must come from EO-Brain)

These encode student intent produced in phases 0-4. If missing, the student has either not completed EO-Brain or deleted work. Repair is impossible:

| Signal | Path | EO-Brain phase | Remediation |
|--------|------|----------------|-------------|
| BRD | `architecture/brd.md` | Phase 4 | Finish `4-eo-tech-architect` skill in Cowork |
| Tech stack decision | `architecture/tech-stack-decision.md` | Phase 4 | Same as above |
| ICP | From `EO-Brain/1-ProjectBrain/icp.md` | Phase 1 | Finish `1-eo-brain-ingestion` skill in Cowork |
| Brand voice | From `EO-Brain/1-ProjectBrain/brandvoice.md` | Phase 1 | Same as above |
| Positioning | From `EO-Brain/1-ProjectBrain/positioning.md` | Phase 1 | Same as above |
| EO-Brain itself | `EO-Brain/` reachable | All | Finish phases 0-4 in Cowork |

Note: `architecture/brd.md` and `architecture/tech-stack-decision.md` are **copied** from EO-Brain during bootstrap. If the copies are missing but EO-Brain originals are present, this is silent-repair-safe (Step 7 below). If EO-Brain originals are also missing → refuse-and-route.

---

## Execution sequence

### Step 1 — Resolve workspace root

Same worktree-aware resolution as `eo-dev-start` Step 1.

### Step 2 — Locate EO-Brain

Same as `eo-dev-start` Step 2. If not reachable → refuse with the same remediation.

### Step 3 — Scan the 11 bootstrap signals

Identical scan to `eo-dev-start` Step 4. Record for each: `present | absent`, and if present, `size + mtime`.

### Step 4 — Guard rails (route away if not partial)

| Observed | Route |
|----------|-------|
| All 11 signals absent (empty) | `/eo-dev-start` |
| All 11 signals present + first commit exists | `/eo-guide` |
| Anything between → continue | — |

### Step 5 — Classify each missing signal

For each absent signal, look it up in the table above and tag it `silent-repair-safe` or `refuse-and-route`.

### Step 6 — Decide repair path

- **Any** refuse-and-route tag → **refuse** (skip to Step 8)
- **All** missing are silent-repair-safe → proceed to Step 7

This is a first-match-any, not a majority vote. Mixing a silent repair with an upstream gap masks the gap.

### Step 7 — Silent repair (plan mode + approval)

Enter plan mode. Print:

```
🩹 Surgical repair plan

Missing pieces (all silent-repair-safe):
  {list with source template}

Present and untouched:
  {list — never overwritten}

Will rebuild:
  {file} from {template}  — {expected bytes/lines}
  {file} from {template}  — {expected bytes/lines}
  ...

Will NOT:
  - Overwrite any existing file
  - Rewrite lessons.md if present (your accumulated lessons stay)
  - Modify any file under architecture/ or 1-ProjectBrain/
  - Write to EO-Brain/
  - Run git push

Approve? (y/n)
```

On `n` → exit, no writes.

On `y` → for each missing silent-repair-safe signal, write from template using the same routines `handover-bridge` uses. One commit at the end:

```
chore(repair): regenerate {list of files} via eo-dev-repair

Triggered by /eo-dev-repair. Core artifacts (BRD, architecture, project-brain)
untouched. Accumulated lessons preserved.
```

Print evidence table (same format as `eo-dev-start` Step 11, scoped to the repaired files).

### Step 8 — Refuse-and-route (core artifact missing)

Print:

```
❌ Refusing repair — core artifacts are missing.

Silent-repair-safe (could be rebuilt):
  {list}

Refuse-and-route (must come from EO-Brain, cannot be regenerated):
  {file path}  ← from {EO-Brain phase}
                   Remediation: {exact Cowork skill to run}
  {file path}  ← from {EO-Brain phase}
                   Remediation: {exact Cowork skill to run}

Why this refusal:
  Silent repair here would hide the upstream gap. You would end up with a
  scaffolded project missing its own spec or identity. Fix the root cause
  in EO-Brain, then re-run /eo-dev-start (empty project) or /eo-dev-repair
  (if some files survive).

No writes made.
```

Exit.

### Step 9 — Failure rollback

If any write in Step 7 fails mid-flight:
- Log failure to `.repair-failures.log`
- Delete only files this invocation created (track with a manifest before writing)
- Print rollback evidence
- Exit non-zero

Never leave a half-repaired state.

---

## Anti-patterns

- **Partial repair under mixed state.** If any refuse-and-route item is missing, DO NOT repair the easy pieces. The student needs to see the upstream gap.
- **Overwriting lessons.md.** Lessons accumulate student intent. If present, never touch. Only regenerate if absent.
- **Regenerating BRD from nothing.** BRD comes from EO-Brain Phase 4. If it's missing from both project and EO-Brain, the student has to finish Phase 4. No scaffold substitute.
- **Silent writes before approval.** Plan mode is not optional. The student must see exactly what will change.
- **Running git push.** Student reviews and pushes. Skill writes local commit only.
- **Claiming repair on a no-write exit.** If Step 8 refused, say "no writes made" explicitly. Don't let ambiguity hide inaction.

---

## Integration

| Skill | Relationship |
|-------|--------------|
| `eo-dev-start` | Routes here when state is `partial`. Never runs concurrently. |
| `handover-bridge` | This skill reuses handover-bridge's template-application routines for silent repair. Does not re-run the full 11-step sequence. |
| `eo-guide` | Routes here when it detects missing infrastructure (`bootstrap-incomplete` phase). |
| `lessons-manager` | Lessons file is silent-repair-safe (recreate empty), but **never** overwritten if present. |

---

## Self-score protocol

| # | Check | Threshold |
|---|-------|-----------|
| 1 | Workspace root resolved (worktree-aware) | must pass |
| 2 | Route-away guard fired for empty/bootstrapped (no false repair) | must pass |
| 3 | Every missing signal classified exactly once | must pass |
| 4 | Mixed state refused, not partially repaired | must pass |
| 5 | Plan mode preview shown before any write | must pass |
| 6 | Existing lessons.md preserved if present | must pass |
| 7 | Commit message names every regenerated file | must pass |
| 8 | Rollback manifest written before any Step 7 write | must pass |
| 9 | Evidence table post-success with bytes + line counts | must pass |
| 10 | Refusal output names exact EO-Brain remediation skill | must pass |

Threshold: 10/10. Below = bug → capture in `.claude/lessons.md`.
