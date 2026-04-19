# Framework Analysis + Plugin Architecture Recommendation

**Date:** 2026-04-19
**Purpose:** Consolidate Boris's framework (Anthropic), our current stack (gstack + superpowers + smorch-dev-scoring), and EO-Brain's pre-dev workspace into a 10/10 optimal dev plugin for EO MicroSaaS students.

---

## Part 1 — Boris's Framework (Anthropic, ~2.5k tokens, 100 lines)

Boris Cherny runs Claude Code at Anthropic. His team ships 20-30 PRs/day with a ~100-line CLAUDE.md.

| # | Principle | Why it wins |
|---|-----------|-------------|
| 1 | **Plan Mode Default** | For 3+ step or architectural tasks, start in plan mode. Stop and re-plan if things go sideways. Kills ambiguity upfront. |
| 2 | **Subagent Strategy** | Offload research, exploration, parallel analysis to subagents. One task per subagent. Main context stays clean. |
| 3 | **Self-Improvement Loop** | After ANY user correction, write a rule in `tasks/lessons.md`. Every mistake becomes a rule. Every rule prevents the next mistake. **This is the compounding part.** |
| 4 | **Verification Before Done** | Never mark complete without proof. "Would a staff engineer approve this?" Run tests. Check logs. 2-3x output quality. |
| 5 | **Demand Elegance** | Non-trivial change → pause and ask "is there a more elegant way?" Don't accept hacky. Skip for obvious fixes. |
| 6 | **Autonomous Bug Fixing** | Bug report → fix. Don't ask for hand-holding. Point at logs/errors/failing tests, resolve. Zero context switch. |

**Key insight:** The difference isn't complexity. It's **compounding**. Every correction becomes durable context. 80-90% of Claude Code itself is now written using Claude Code.

---

## Part 2 — Our Current Framework

### gstack (Garry Tan, YC) — Engineering Workflow
30+ slash commands. The relevant ones:
- `/plan-ceo-review`, `/plan-eng-review`, `/plan-design-review` — planning
- `/review` — 4-dimension code review
- `/qa`, `/qa-only` — browser-based QA
- `/investigate` — bug root cause
- `/design-review`, `/design-consultation`, `/design-shotgun` — UI
- `/ship`, `/land-and-deploy`, `/canary` — merge + deploy
- `/retro`, `/document-release` — sprint close
- `/browse`, `/connect-chrome` — web
- `/freeze`, `/guard`, `/unfreeze` — code protection
- `/office-hours`, `/autoplan`, `/careful`, `/codex`, `/cso` — meta

### superpowers (obra) — Dev Methodology
14 individual skills:
- `test-driven-development` — TDD cycle
- `systematic-debugging` — hypothesis → evidence → fix
- `subagent-driven-development` — parallel agents
- `brainstorming` — approach selection
- `dispatching-parallel-agents`
- `verification-before-completion`
- `writing-plans` / `executing-plans`
- `requesting-code-review` / `receiving-code-review`
- `finishing-a-development-branch`
- `using-git-worktrees`
- `using-superpowers`, `writing-skills`

### smorch-dev-scoring (SMOrchestra internal) — Quality Gates
- `/score-project` — 5-hat composite (must be 90+ to ship)
- `/score-hat [dim]` — individual dimension
- `/bridge-gaps` — fix plan
- `/calibrate` — calibrate against reference projects

---

## Part 3 — Comparison Matrix

| Boris principle | Our framework coverage | Gap |
|-----------------|------------------------|-----|
| 1. Plan Mode Default | ✅ gstack:/plan-eng-review + superpowers:writing-plans | None |
| 2. Subagent Strategy | ✅ superpowers:subagent-driven-development + dispatching-parallel-agents | None |
| 3. **Self-Improvement Loop** | ❌ **Not explicit anywhere** | **CRITICAL GAP** — no `lessons.md` auto-update mechanism |
| 4. Verification Before Done | ✅ superpowers:verification-before-completion | None |
| 5. **Demand Elegance** | ⚠️ Partially — gstack:/review covers maintainability but no explicit "elegance pause" | **GAP** |
| 6. Autonomous Bug Fixing | ✅ superpowers:systematic-debugging | None |
| CLAUDE.md under 100 lines | ❌ **Ours are 200-400 lines** | **WE'RE BLOATED** |

### Our extras Boris doesn't formalize
- **5-hat scoring** (quantitative quality gate) — valuable, keep it
- **Independent QA agent** (separate process scoring PRs cold) — Boris doesn't have; we invented
- **BRD traceability** (every AC → tagged test) — specific to our projects
- **Handover brief** (context transfer to QA) — specific to our team structure

### EO-specific concerns Boris doesn't address
- **Arabic RTL correctness** — every UI change needs it
- **MENA market context** — pricing currencies, Ramadan scheduling, Gulf conversational tone
- **Mobile-first** (375px minimum) — MENA is mobile-majority
- **MicroSaaS hand-off from EO-Brain** — Phase 5 outputs a specific artifact set

---

## Part 4 — The 10/10 Optimal Framework

Extracted best-of-both. **7 pillars** instead of 6 or 9. Each pillar has one primary tool + one enforcement mechanism.

### Pillar 1 — Plan before you code (3+ steps)
- **Tool:** Claude plan mode + `superpowers:writing-plans`
- **Enforcement:** Hook that blocks `Write|Edit` in new files if no `docs/plans/*.md` exists for the current feature branch

### Pillar 2 — Subagents for breadth, main context for depth
- **Tool:** `superpowers:subagent-driven-development`
- **Enforcement:** Scorecard dimension "Architecture" asks: "were independent explorations delegated?"

### Pillar 3 — Self-improvement loop (COMPOUNDING)
- **Tool:** Auto-append corrections to `.claude/lessons.md` per-project
- **Enforcement:** SessionStart hook reads lessons.md and includes in additionalContext (so every session starts smarter)
- **NEW for us — biggest lever**

### Pillar 4 — Verification before done
- **Tool:** `superpowers:verification-before-completion`
- **Enforcement:** `/eo-review` refuses to pass without test evidence

### Pillar 5 — Elegance pause
- **Tool:** Explicit "is there a more elegant way?" question in `/eo-review`
- **Enforcement:** Scorecard dimension "Engineering" asks this directly

### Pillar 6 — Autonomous bug fixing
- **Tool:** `superpowers:systematic-debugging`
- **Enforcement:** When given a bug report, `/eo-debug` produces root-cause + fix + test, not questions

### Pillar 7 — Score + ship
- **Tool:** 5-hat scorecard (mental for students, full for team) + conventional `/ship`
- **Enforcement:** Scorecard composite ≥ 90 required before PR. Save to `docs/qa-scores/`. Track trend.

### Meta: Keep CLAUDE.md under 150 lines
Boris does 100. We add some EO-specific rules (Arabic, MENA, mobile) so we get ~130-150. Hard stop — if it grows, move content to referenced files.

---

## Part 5 — Dev Sprint Scoring Framework

Combined from smorch-dev-scoring + our metrics baseline.

### Per-sprint metrics (weekly)
| Metric | Target | Current baseline |
|--------|:------:|:----------------:|
| Total PRs opened | 10+ | 13 |
| PRs with `/score-project` | 90%+ | 0% (critical gap) |
| PRs with handover brief | 80%+ | 15% |
| PRs merged within 48h | 70%+ | 38% |
| Avg composite score | 90+ | not tracked |
| Lessons.md entries/week | 5+ | N/A (missing) |

### Per-PR scorecard
5 hats (Product, Architecture, Engineering, QA, UX). Each 1-10. Composite ≥ 90 to ship.

| Hat | Key questions (Boris-influenced) |
|-----|----------------------------------|
| Product | Matches BRD? Real ICP user would use it? Scope disciplined (no feature creep)? |
| Architecture | Logical modules? Data flow explainable in 2 sentences? Subagents used for parallel work? |
| Engineering | Tests exist + pass? Errors handled? **Elegance pause honored?** Types strict? |
| QA | Every flow tested (happy + empty + error + edge)? Verification evidence present? |
| UX | Mobile 375px works? **Arabic RTL** if MENA? Zero console errors? Accessible (axe clean)? |

---

## Part 6 — Optimal CLAUDE.md Structure (Boris-style, ~130 lines)

Template for the student CLAUDE.md (global at ~/.claude/CLAUDE.md):

```markdown
# [Role] — Context

**Who:** [you / your team]
**What:** [the work — MicroSaaS, infra, etc.]
**Core thesis:** [one line that differentiates your voice]

## The 7 Pillars (memorize)

1. Plan before code (3+ steps → plan mode)
2. Subagents for breadth
3. Self-improvement: write every correction to lessons.md
4. Verification before done: prove it works
5. Elegance pause: "more elegant way?" before commit
6. Autonomous bug fix: point at evidence, resolve
7. Score + ship: 5-hat composite ≥ 90

## Slash commands (EO MicroSaaS Dev plugin)
- /eo-plan       — Start a feature with BRD + plan
- /eo-code       — Enter TDD mode (test first, implement, refactor)
- /eo-review     — 4-dim review + elegance pause
- /eo-score      — Run 5-hat scorecard, save to docs/qa-scores/
- /eo-debug      — Systematic root-cause on a bug
- /eo-ship       — Final checks + PR with score + BRD link
- /eo-retro      — Sprint end: what we learned, update lessons.md

## Non-negotiable rules
1. Every project has docs/ with handovers/, qa-scores/, plans/
2. No secrets in code — use .env (gitignored)
3. Every PR has a score saved to docs/qa-scores/
4. Every correction → write a rule in .claude/lessons.md
5. Bugs: point at evidence, don't guess
6. Arabic RTL if MENA user-facing
7. Mobile 375px works before shipping

## Voice / Words never used
Direct. Numbers. Trust-first. No: leverage, synergy, ecosystem, holistic, cutting-edge, world-class.

## When in doubt
Ask in community. Don't guess on security (payments, PII).
```

**Line count target: under 150.**

---

## Part 7 — Architecture Recommendation

### Your question

> Should we keep superpowers + gstack separate, create our own plugin for missing pieces, and have install.sh amend CLAUDE.md to use them together?
>
> OR build one ultimate plugin combining everything?

### My recommendation: **Option C — Thin Orchestrator Plugin**

Neither of your options is optimal. The right answer:

**Install gstack + superpowers UNCHANGED from upstream. Build a THIN `eo-microsaas-dev` plugin that:**
1. Provides ONE clean command surface students actually call (`/eo-plan`, `/eo-code`, `/eo-review`, `/eo-score`, `/eo-ship`, `/eo-debug`, `/eo-retro`)
2. Each of OUR commands internally chains into gstack/superpowers skills — we orchestrate, don't re-implement
3. ADDS what's missing:
   - Self-improvement loop (lessons.md auto-update — biggest lever)
   - BRD-driven workflow (reads from `EO-Brain/` if handed off from Phase 5)
   - Student-calibrated 5-question scorecard
   - MicroSaaS-specific hooks (Arabic RTL check, mobile viewport check, MENA payment patterns)
   - Handover bridge from EO-Brain Phase 5 output → Claude Code first commit

### Why not ONE ultimate plugin (combining gstack + superpowers into our own)

- **Maintenance burden:** gstack (Garry Tan) and superpowers (obra) are actively maintained upstream. Forking = we inherit their bugs forever.
- **Missed improvements:** When they ship new features, we'd have to manually merge. Students lose free upgrades.
- **Licensing / attribution:** Both are open source; bundling them into ours without clear attribution is sketchy.
- **Trust:** Students who hear about gstack or superpowers externally can verify "yes, that's what you're getting" — credibility.

### Why not A (3 separate plugins, student calls commands from each)

- **Cognitive load:** Student has to remember which command lives in which plugin.
- **No EO-specific enforcement:** gstack doesn't know Arabic RTL matters. superpowers doesn't know to check docs/qa-scores/.
- **No compounding lessons:** Neither has a self-improvement loop.
- **Bloated CLAUDE.md:** To explain the 30+ commands, we'd need a long CLAUDE.md, violating Boris's "under 100 lines" principle.

### Why Option C wins

- Student sees ~7 `/eo-*` commands. Maximum clarity.
- Under the hood, we delegate to upstream — they keep evolving, we keep benefiting.
- Our plugin is THIN (~300-500 lines) and implements the 7 pillars + EO-specifics.
- CLAUDE.md stays short — students read ONE page, follow ONE workflow.
- The self-improvement loop (lessons.md) is ours. That's the compounding lever Boris identified.
- Plugin lives at `eo-microsaas-dev/` in `smorchestraai-code/eo-microsaas-training` repo — same install.sh installs it alongside gstack + superpowers.

### Proposed `eo-microsaas-dev` plugin structure

```
eo-microsaas-dev/
├── .claude-plugin/
│   └── plugin.json                  Plugin metadata
├── commands/
│   ├── eo-plan.md                   /eo-plan — wraps plan-eng-review + writing-plans
│   ├── eo-code.md                   /eo-code — wraps test-driven-development + BRD check
│   ├── eo-review.md                 /eo-review — wraps gstack /review + elegance pause
│   ├── eo-score.md                  /eo-score — 5-hat scorecard + save + track trend
│   ├── eo-debug.md                  /eo-debug — wraps systematic-debugging
│   ├── eo-ship.md                   /eo-ship — wraps gstack /ship + score validation + PR template
│   └── eo-retro.md                  /eo-retro — sprint close + lessons.md update
├── skills/
│   ├── lessons-manager/             NEW — append corrections to .claude/lessons.md
│   ├── arabic-rtl-checker/          NEW — verify RTL layout + font rendering
│   ├── mena-mobile-check/           NEW — 375px viewport + Arabic numeral display
│   ├── brd-traceability/            NEW — read EO-Brain BRD, verify AC → test mapping
│   └── handover-bridge/             NEW — read EO-Brain Phase 5, seed first PR
└── SKILL.md                         How all this fits together
```

### install.sh upgrade (one command, three plugins + config)

```bash
curl -sSL https://raw.githubusercontent.com/smorchestraai-code/eo-microsaas-training/main/install.sh | bash
```

Installs:
1. Node 22, Bun, Claude Code, gh CLI
2. **gstack** (upstream — git clone)
3. **superpowers** (upstream — git clone)
4. **eo-microsaas-dev** (our plugin — git clone from this repo's plugin subfolder)
5. Writes ~/.claude/CLAUDE.md (short, 130-line, 7-pillar style)
6. Writes ~/.claude/settings.json (hooks + pulls in lessons.md at session start)

CLAUDE.md only references `/eo-*` commands. Students never see the gstack or superpowers command lists — those are internal to our orchestrator.

---

## Part 8 — Sequence We Should Build In

1. **Write this architecture doc** ✓ (this file)
2. **Get Mamoun approval** ← we are here
3. **Build `eo-microsaas-dev` plugin skeleton** (folder structure + plugin.json + empty commands)
4. **Implement lessons.md auto-update** (SessionStart reads, /eo-retro writes) — the compounding lever first
5. **Implement /eo-score** (5-hat scorecard + save + trend CSV)
6. **Implement /eo-review** with elegance pause
7. **Implement /eo-plan, /eo-code, /eo-debug, /eo-ship, /eo-retro** (thin wrappers)
8. **Write short CLAUDE.md** (130-line Boris style)
9. **Update install.sh** to install all 3 plugins
10. **Build EO-Brain Phase 5 → Claude Code bridge** (handover-bridge skill)
11. **Ship v1.0.0 of dev plugin** (tag)
12. **Pilot with 2-3 real students** for 2 weeks
13. **Iterate based on their lessons.md entries** (dogfood the compounding loop)

---

## Decision Point

**I need your go/no-go on:**

- [ ] The 7-pillar framework as the 10/10 extraction (not 6 like Boris, not 30+ like gstack)
- [ ] Option C (thin orchestrator plugin) as the architecture
- [ ] The command surface: `/eo-plan /eo-code /eo-review /eo-score /eo-debug /eo-ship /eo-retro`
- [ ] The 5 new skills inside our plugin: lessons-manager, arabic-rtl-checker, mena-mobile-check, brd-traceability, handover-bridge
- [ ] The 150-line CLAUDE.md ceiling

If yes to all, I start building. If any objections, we refine first.
