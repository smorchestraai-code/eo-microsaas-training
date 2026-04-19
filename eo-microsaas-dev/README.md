# eo-microsaas-dev

Claude Code plugin for EO MicroSaaS students. Built for solo founders shipping Arabic-first MENA SaaS.

## What you get

- **7 slash commands** — `/eo-plan`, `/eo-code`, `/eo-review`, `/eo-score`, `/eo-bridge-gaps`, `/eo-ship`, `/eo-debug`, `/eo-retro`
- **7 skills** — 5-hat scoring (calibrated, honest), lessons manager, elegance pause, Arabic RTL checker, MENA mobile check, BRD traceability, handover bridge
- **150-line CLAUDE.md template** — Boris-discipline, project-specific, no bloat
- **Score gate: 90+ composite or don't ship** — non-negotiable

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
  commands/
    eo-plan.md
    eo-code.md
    eo-review.md
    eo-score.md
    eo-bridge-gaps.md
    eo-ship.md
    eo-debug.md
    eo-retro.md
  skills/
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
```

## Version

v1.0.0 — first release. Pilot with 2-3 students for 2 weeks before v1.1.
