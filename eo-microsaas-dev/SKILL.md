---
name: eo-microsaas-dev
description: |
  7-pillar development workflow for EO MicroSaaS students. Wraps Claude Code's plan mode,
  superpowers skills (TDD, debugging, subagents), and gstack engineering tools into a clean
  command surface. Adds what's missing: lessons.md self-improvement loop, MENA-specific
  checks (Arabic RTL, mobile 375px), BRD traceability from EO-Brain Phase 5, and a 5-hat
  quality scorecard calibrated for solo founder reality.

  Commands students call:
  /eo-plan — Start a feature. Write BRD. Create plan in docs/plans/. (3+ step rule)
  /eo-code — Enter TDD mode. Test first, implement, refactor. Read BRD acceptance criteria.
  /eo-review — 4-dim code review + elegance pause + verification-before-done check.
  /eo-score — Run the 5-hat scorecard. Save to docs/qa-scores/. Update trend CSV.
  /eo-debug — Systematic root-cause on a bug. Point at evidence. Resolve without hand-holding.
  /eo-ship — Final gate. Read score, write PR body, push, create PR with BRD link.
  /eo-retro — End-of-sprint. Pull lessons, update .claude/lessons.md for next session.

  Invoke by name OR via slash commands. Students mostly use slash commands directly.
license: MIT
---

# EO MicroSaaS Dev — Plugin Overview

## What this plugin does

Walks a student from feature idea → shipped PR following the 7-pillar workflow extracted from Boris Cherny (Anthropic Claude Code team) + Garry Tan (gstack) + obra (superpowers) + our own MENA + MicroSaaS additions.

## The 7 Pillars

1. **Plan before code** — for 3+ step or architectural work, plan first.
2. **Subagents for breadth** — offload research/exploration to subagents, main context stays clean.
3. **Self-improvement loop** — every user correction → rule in `.claude/lessons.md`. Compounds across sessions.
4. **Verification before done** — "would a staff engineer approve this?" Proof required.
5. **Elegance pause** — non-trivial change? Ask "more elegant way?" before commit.
6. **Autonomous bug fixing** — given a bug, fix it. Don't ask. Point at evidence.
7. **Score + ship** — 5-hat composite ≥ 90 to ship. Track trend weekly.

## Command → internal chain reference

| /eo-* command | What it does | Underlying tools called |
|---------------|--------------|-------------------------|
| /eo-plan | Create BRD + plan doc | plan mode + superpowers:writing-plans |
| /eo-code | TDD cycle + BRD check | superpowers:test-driven-development + brd-traceability skill |
| /eo-review | 4-dim review + elegance pause | gstack:/review + elegance-pause skill + superpowers:verification-before-completion |
| /eo-score | 5-hat quality gate | eo-scorer skill (ours — better than smorch-dev-scoring) |
| /eo-debug | Root-cause bug analysis | superpowers:systematic-debugging |
| /eo-ship | Final gate + PR | gstack:/ship + score validation |
| /eo-retro | Sprint close | lessons-manager skill |

## Skills in this plugin

- `eo-scorer/` — 5-hat scorecard orchestrator (5 hats + composite + bridge-gaps)
- `lessons-manager/` — self-improvement loop (auto-update .claude/lessons.md)
- `arabic-rtl-checker/` — MENA UI compliance
- `mena-mobile-check/` — 375px viewport + Arabic numerals
- `brd-traceability/` — EO-Brain BRD → tagged test mapping
- `handover-bridge/` — Phase 5 (EO-Brain) → first Claude Code commit
- `elegance-pause/` — Boris's "more elegant way?" enforcement

## Prerequisites

- gstack installed at `~/.claude/skills/gstack` (upstream — zero maintenance)
- superpowers installed at `~/.claude/skills/superpowers` (upstream — zero maintenance)
- This plugin at `~/.claude/plugins/eo-microsaas-dev/` OR `~/.claude/skills/eo-microsaas-dev/`

The install.sh in the training repo installs all three.

## When students skip this plugin

They can always fall back to calling gstack and superpowers directly. This plugin is orchestration + EO-specifics. Not a replacement. A student who knows gstack deeply can use `gstack:/review` directly — our `/eo-review` just adds the elegance pause + EO context.

## What makes this better than smorch-dev-scoring

smorch-dev-scoring (SMOrchestra internal) inspired the 5-hat pattern but:
- Calibrated for a professional team, not solo founders
- Heavy (~30 min per full score)
- No MENA specifics
- No self-improvement loop
- No EO-Brain integration

eo-scorer (this plugin, skills/eo-scorer/):
- Calibrated for solo founder reality (5-10 min scoring)
- MENA-baked-in (Arabic RTL, mobile 375px, currency locale)
- Self-improvement loop: low score triggers "write a lesson?" prompt
- EO-Brain aware: reads BRD.md, verifies AC tags in tests
- Trend CSV per project: `docs/qa-scores/trend.csv`

## How to invoke

Direct: `/eo-plan`, `/eo-code`, `/eo-review`, `/eo-score`, `/eo-bridge-gaps`, `/eo-debug`, `/eo-ship`, `/eo-retro`

Or by name: "Use eo-microsaas-dev to start a new feature for password reset."

## Out-of-scope (explicitly NOT this plugin's job)

- **Not a code editor** — we orchestrate TDD via superpowers; we don't write test frameworks
- **Not a deploy tool** — `/eo-ship` calls the project's own deploy script, we don't ship PM2/nginx configs
- **Not a BRD generator** — EO-Brain Phase 4 produces the BRD; we consume it
- **Not a replacement for gstack or superpowers** — we orchestrate both, do not duplicate
- **Not an AI coach** — we are checklists + rubrics + hooks, not a chat coach
- **Not multi-project aware** — each project has its own `.claude/lessons.md`; lessons don't cross-pollinate automatically
- **Not for non-MENA ICPs at full strength** — Arabic/RTL/mobile-375 rules cap ≤6 without explicit MENA ICP; English-only projects skip those questions via N/A

## Manual smoke test (run once after install)

```bash
# 1. Verify plugin files resolve
ls ~/.claude/plugins/eo-microsaas-dev/commands/*.md    # should list 8 files
ls ~/.claude/plugins/eo-microsaas-dev/skills/          # should list 7 directories

# 2. Start Claude Code in any project
cd ~/some-project && claude

# 3. In Claude, type /eo and verify autocomplete shows /eo-plan, /eo-code, etc.

# 4. Run /eo-plan with a dummy feature — verify plan mode entered, BRD referenced

# 5. If step 3 fails → plugin.json commands[] paths wrong; re-check file locations
```

If any step fails, the plugin is not correctly installed — do NOT proceed to score real PRs with it.
