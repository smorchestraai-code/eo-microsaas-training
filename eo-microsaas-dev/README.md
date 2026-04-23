# eo-microsaas-dev

Claude Code plugin for EO MicroSaaS students. Built for solo founders shipping Arabic-first MENA SaaS.

## What you get

- **12 slash commands** — `/eo-dev-start` (bootstrap), `/eo-dev-repair` (surgical repair), `/eo-guide` + `/eo-status` (cross-session resumability), `/eo-plan`, `/eo-code`, `/eo-review`, `/eo-score`, `/eo-bridge-gaps`, `/eo-ship`, `/eo-debug`, `/eo-retro`
- **10 skills** — `eo-dev-start` (one-shot bootstrap from EO-Brain phases 0-4), `eo-dev-repair` (silent-repair-safe vs refuse-and-route triage), `eo-guide` (phase detector + next-command router), 5-hat scoring (calibrated, honest), lessons manager, elegance pause, Arabic RTL checker, MENA mobile check, BRD traceability, handover bridge
- **150-line CLAUDE.md template** — Boris-discipline, project-specific, no bloat
- **Score gate: 90+ composite or don't ship** — non-negotiable
- **Zero-friction start** — type `/eo-dev-start` in a fresh project. Plan mode previews every action before writing.

## The 7 pillars

1. Plan Mode Default (Boris)
2. Subagent Strategy (Boris)
3. Self-Improvement Loop via `.claude/lessons.md` (Boris — our biggest compounding lever)
4. Verification Before Done (Boris)
5. Demand Elegance (Boris)
6. Autonomous Bug Fixing (Boris)
7. Score + Ship (EO-specific 5-hat gate)

## Works alongside

- **gstack** — keep separately installed (zero maintenance for us)
- **superpowers** — keep separately installed; we orchestrate via `/eo-code` which invokes TDD

We do NOT rebuild what those plugins do well. We orchestrate them + add EO/MENA-specific guardrails.

## Why not smorch-dev-scoring?

This plugin is calibrated for solo founders in MENA, not the SMOrchestra internal team. Scoring examples use real PRs at composite 65-92, not inflated 95+. Rubrics bake in Arabic RTL + 375px mobile + MENA cultural correctness from question 1. Lighter: 5-10 min per score, not 30.

## Install

See `../eo-microsaas-training` repo for install.sh.

## File layout

```
eo-microsaas-dev/
  .claude-plugin/plugin.json
  SKILL.md                        ← plugin overview
  README.md                       ← this file
  CHANGELOG.md
  commands/
    eo-dev-start.md               ← bootstrap (v1.2.0)
    eo-dev-repair.md              ← surgical repair (v1.2.0)
    eo-guide.md                   ← phase detector + next-step router
    eo-status.md                  ← compact dashboard
    eo-plan.md
    eo-code.md
    eo-review.md
    eo-score.md
    eo-bridge-gaps.md
    eo-ship.md
    eo-debug.md
    eo-retro.md
  skills/
    eo-dev-start/SKILL.md         ← one-shot bootstrap from EO-Brain (v1.2.0)
    eo-dev-repair/SKILL.md        ← classify-then-repair-or-refuse (v1.2.0)
    eo-guide/SKILL.md             ← cross-chat continuity
    eo-scorer/                    ← 5-hat scoring
      SKILL.md
      product-hat.md
      architecture-hat.md
      engineering-hat.md
      qa-hat.md
      ux-hat.md
      calibration-examples.md
    lessons-manager/SKILL.md
    elegance-pause/SKILL.md
    arabic-rtl-checker/SKILL.md
    mena-mobile-check/SKILL.md
    brd-traceability/SKILL.md
    handover-bridge/SKILL.md
  templates/
    CLAUDE.md.template
    ci.yml.template
    _dev-progress.md.template
```

## Version

**v1.2.0** (2026-04-23) — adds `/eo-dev-start` (one-shot bootstrap from EO-Brain phases 0-4, plan-mode gated, worktree-aware) and `/eo-dev-repair` (classifies every missing piece as silent-repair-safe or refuse-and-route — rebuilds regeneratable files silently, refuses when core artifacts like BRD or architecture are missing). Updates `/eo-guide` to route `pre-bootstrap` → `/eo-dev-start` and `bootstrap-incomplete` → `/eo-dev-repair`. Simplifies the 5-CodeHandover entry point from a 75-line copy-paste prompt to one command. See `CHANGELOG.md`.

v1.1.0 (2026-04-21) — adds `/eo-guide` + `/eo-status` for cross-session resumability, `_dev-progress.md` dual-writer tracker, hardened `handover-bridge` (HANDOVER READINESS 9/9), native Windows PowerShell hooks, CHANGELOG + rollback runbook.

v1.0.0 (2026-04-19) — first release. Takes students from vanilla Claude Code to a disciplined 7-pillar workflow with a 90+ composite ship gate.
