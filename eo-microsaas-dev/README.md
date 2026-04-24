# eo-microsaas-dev

Claude Code plugin for EO MicroSaaS founders — weekend-ship MVP chain. Built for non-technical solo founders shipping Arabic-first MENA SaaS.

## What you get

- **15 slash commands** — numbered build chain `/1-eo-dev-start` → `/2-eo-dev-plan` → `/3-eo-code` → `/4-eo-review` → `/5-eo-score` → `/6-eo-bridge-gaps` → `/7-eo-ship`, plus lifecycle `/8-eo-dev-repair`, `/9-eo-debug`, `/10-eo-retro`, plus utilities `/eo-status`, `/eo-guide`, `/eo-github`, `/eo-freeze`, `/eo-unfreeze`
- **11 skills** — `eo-dev-start` (SaaSfast-mode picker M0-M3 + one-shot bootstrap from EO-Brain phases 0-4), `handover-bridge` (mode-aware scaffolder + BRD post-process for Weekend MVP + v2 roadmap blocks), `eo-dev-repair` (silent-repair-safe vs refuse-and-route triage), `eo-github` (MCP-only GitHub admin, plan-aware), `eo-guide` (phase detector + next-command router), 5-hat scoring (calibrated, honest), lessons manager, elegance pause, Arabic RTL checker, MENA mobile check, BRD traceability
- **150-line CLAUDE.md template** — CEO voice, project-specific, no engineering jargon surfaced
- **Score gate: 90+ composite or don't ship** — non-negotiable. Self-scoring on `/7-eo-ship`, `/8-eo-dev-repair`, `/9-eo-debug`.
- **Zero-friction start** — type `/1-eo-dev-start` in a fresh project. Plan mode previews every action before writing. GitHub only touched after explicit choice.

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
- **superpowers** — keep separately installed; we orchestrate via `/3-eo-code` which invokes TDD

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
    1-eo-dev-start.md             ← bootstrap + SaaSfast-mode picker (v1.4.0)
    2-eo-dev-plan.md              ← plan a feature (plan-mode gated)
    3-eo-code.md                  ← TDD via superpowers
    4-eo-review.md                ← self-review + Arabic/mobile checks
    5-eo-score.md                 ← 5-hat composite (ship gate 90+)
    6-eo-bridge-gaps.md           ← lift weakest hat (80-89 band)
    7-eo-ship.md                  ← self-score + PR + deploy (v1.4.0 adds self-score gate)
    8-eo-dev-repair.md            ← surgical repair + self-score (v1.4.0)
    9-eo-debug.md                 ← root-cause + self-score after fix (v1.4.0)
    10-eo-retro.md                ← sprint close + lesson pruning
    eo-github.md                  ← GitHub admin (v1.3.0 — create/point/guided/audit)
    eo-guide.md                   ← phase detector + next-step router
    eo-status.md                  ← compact dashboard
    eo-freeze.md                  ← lock edits to one directory (v1.4.0)
    eo-unfreeze.md                ← clear the edit boundary (v1.4.0)
  skills/
    eo-dev-start/SKILL.md         ← one-shot bootstrap + 4-option GitHub intent (v1.2.0 → v1.3.0)
    eo-dev-repair/SKILL.md        ← classify-then-repair-or-refuse (v1.2.0)
    eo-github/SKILL.md            ← GitHub admin, MCP-only, plan-aware (v1.3.0)
    eo-guide/SKILL.md              ← cross-chat continuity (v1.3.0 adds local-only + no-remote states)
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
    handover-bridge/SKILL.md      ← git init + first commit now conditional on github_intent (v1.3.0)
  templates/
    CLAUDE.md.template
    ci.yml.template
    _dev-progress.md.template
```

## Version

**v1.3.0** (2026-04-23) — adds `/eo-github` skill + command (four modes: `create`, `point-existing`, `guided`, `audit`). `mcp__github__*` MCP-only — no `gh` CLI fallback. Plan-aware: free/pro/team/enterprise detection omits plan-locked features so students never see settings GitHub would silently ignore. Branch strategy picked from collaborator count (solo → trunk-only; ≥2 → main + dev). Best-practices settings applied on creation: private, squash-merge only, `has_wiki`/`has_projects`/`has_discussions` off, `delete_branch_on_merge` on, EO topics and labels. Branch protection deferred to post-first-CI automation. `/eo-dev-start` now asks one 4-option question when no origin exists (create / point-existing / local-only / I-don't-know) and routes accordingly. `handover-bridge` makes `git init` + first commit conditional on `github_intent`. `/eo-guide` detects `local-only-bootstrapped`, `git-local-no-remote`, and `ready-to-ship-but-no-remote` states and routes to `/eo-github`. See `CHANGELOG.md`.

v1.2.0 (2026-04-23) — adds `/eo-dev-start` (one-shot bootstrap from EO-Brain phases 0-4, plan-mode gated, worktree-aware) and `/eo-dev-repair` (classifies every missing piece as silent-repair-safe or refuse-and-route — rebuilds regeneratable files silently, refuses when core artifacts like BRD or architecture are missing). Updates `/eo-guide` to route `pre-bootstrap` → `/eo-dev-start` and `bootstrap-incomplete` → `/eo-dev-repair`. Simplifies the 5-CodeHandover entry point from a 75-line copy-paste prompt to one command. See `CHANGELOG.md`.

v1.1.0 (2026-04-21) — adds `/eo-guide` + `/eo-status` for cross-session resumability, `_dev-progress.md` dual-writer tracker, hardened `handover-bridge` (HANDOVER READINESS 9/9), native Windows PowerShell hooks, CHANGELOG + rollback runbook.

v1.0.0 (2026-04-19) — first release. Takes students from vanilla Claude Code to a disciplined 7-pillar workflow with a 90+ composite ship gate.
