# eo-microsaas-dev v1.2.0 — Complete Operator's Guide

**For the student or operator opening this plugin for the first time.** Every command, every skill, three real-world scenarios, and the traps new people hit.

**Version:** 1.2.0 (2026-04-23)
**Plugin repo:** https://github.com/smorchestraai-code/eo-microsaas-training
**Applies to:** fresh EO MicroSaaS projects bootstrapped from EO-Brain phases 0-4.

---

## 1. The three-layer model

The plugin is a stack. Each layer hides the next one's complexity. You only ever type into **L1**.

```
┌─────────────────────────────────────────────────────────────────┐
│ L1 — COMMANDS (what you type)                                   │
│   /eo-dev-start   /eo-dev-repair   /eo-guide   /eo-status       │
│   /eo-plan   /eo-code   /eo-review   /eo-score                  │
│   /eo-bridge-gaps   /eo-ship   /eo-debug   /eo-retro            │
└────────────────────────────┬────────────────────────────────────┘
                             │ thin wrappers — activate a skill
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ L2 — EO SKILLS (plugin-specific logic, EO/MENA-aware)           │
│   eo-dev-start   eo-dev-repair   eo-guide   handover-bridge     │
│   eo-scorer (5-hat)   lessons-manager   elegance-pause          │
│   brd-traceability   arabic-rtl-checker   mena-mobile-check     │
└────────────────────────────┬────────────────────────────────────┘
                             │ orchestrate (do not duplicate)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ L3 — EXTERNAL SKILL PACKS (domain-generic, installed once)      │
│   gstack:        /review   /design-review   /ship               │
│   superpowers:   test-driven-development                        │
│                  systematic-debugging                           │
│                  brainstorming                                  │
└─────────────────────────────────────────────────────────────────┘
```

### What each layer encapsulates

| Concern | Handled at | How |
|---|---|---|
| **GitHub = single source of truth** | L2 `handover-bridge` + L1 `/eo-ship` | Bootstrap writes `.github/workflows/ci.yml` (Node 22 + lint + test + build + `npm audit`). `/eo-ship` pushes, opens PR, tags. CI runs on GitHub, not locally — GitHub HEAD is always the authoritative build. L-009 in global CLAUDE.md makes push mandatory at every work unit. |
| **Global `~/.claude/CLAUDE.md`** | L2 `handover-bridge` Step 0 | Bootstrap aborts if global CLAUDE.md or `settings.json` is missing. SessionStart hook (installed at repo-level) auto-loads `.claude/lessons.md` every session. |
| **Project `{project}/CLAUDE.md`** | L2 `handover-bridge` | Written once during bootstrap from EO-Brain identity (founder, tech stack, ICP, MENA flag, deploy lane). Capped at 150 lines by design. Never overwritten after first write. |
| **Global SOPs** | L3 gstack + superpowers (installed in `~/.claude/skills/`) | TDD, `/review`, `/design-review`, `/ship`, `systematic-debugging` live once per machine. Every EO project reuses them. No duplication. |
| **Project SOPs** | L2 `lessons-manager` + `.claude/lessons.md` | Every correction you give Claude becomes one line in `.claude/lessons.md`. SessionStart hook re-loads it. This is the compounding layer — project-specific rules that accumulate. |
| **Project skills** | L2 (the plugin) | You don't author project skills. The plugin is the skill catalog. If you need one, add it to the plugin via PR, tag a new version. |
| **Quality gates** | L2 `eo-scorer` (5-hat) + `brd-traceability` (AC tags) + `arabic-rtl-checker` + `mena-mobile-check` | Composite 90+ to ship, every hat ≥8, every `AC-N.N` has a test, RTL renders, 375px mobile works. Enforced inside `/eo-score`, cannot be bypassed. |
| **Cross-session memory** | L2 `eo-guide` + `_dev-progress.md` | Filesystem is truth. Open a new chat 3 days later, type `/eo-guide`, get the exact next command. No paste. |
| **Recovery** | L2 `eo-dev-repair` | If anything is missing, classify: rebuild silently (CLAUDE.md, hooks, CI) or refuse-and-route (BRD, architecture — finish EO-Brain phase first). |

The key insight: **L2 never duplicates L3**. `/eo-code` calls `superpowers:test-driven-development` — it doesn't re-implement TDD. `/eo-review` calls `gstack:/review` — it doesn't re-implement review. L2 adds EO/MENA-specific guardrails; L3 does the generic work.

---

## 2. Command + skill reference

### L1 — Commands (12)

**Meta — bootstrap & continuity (4)**

| Command | When | What it does |
|---|---|---|
| `/eo-dev-start` | First session in fresh project | Reads EO-Brain phases 0-4, previews bootstrap in plan mode, invokes `handover-bridge` on approval. Routes partial → `/eo-dev-repair`, bootstrapped → `/eo-guide`. |
| `/eo-dev-repair` | Project is partially set up | Triages missing pieces: silent-repair-safe (CLAUDE.md, lessons, hooks, CI) rebuilt from templates; refuse-and-route (BRD, architecture, project-brain) refused with EO-Brain phase to finish. |
| `/eo-guide` | Any returning session | Scans filesystem, tells you exact next command + ETA. Works 3 days after last session, no paste. |
| `/eo-status` | Quick glance | Compact dashboard only. No coaching. |

**Dev chain — daily work (8)**

| Command | Position | What it does |
|---|---|---|
| `/eo-plan` | 1 | Reads a BRD story, produces a plan with `@AC-N.N` tagged test list. Updates `_dev-progress.md` row to `📝 planned`. |
| `/eo-code` | 2 | Invokes `superpowers:test-driven-development`. Writes tests first, code second. Updates row to `🔨 coding`. |
| `/eo-review` | 3 | Invokes `gstack:/review` — 4 dimensions (security, performance, correctness, maintainability). Fix <8/10 before proceeding. |
| `/eo-score` | 4 | 5-hat scorecard (Product, Architecture, Engineering, QA, UX). Composite ≥90 = `🧪 scoring` (ship-ready). 80-89 = route to `/eo-bridge-gaps`. <80 = block. |
| `/eo-bridge-gaps` | 4a | Fixes the lowest hat, re-scores. Logs lesson if the gap recurs. |
| `/eo-ship` | 5 | Final pre-ship gate (score ≥90, tests green, git clean, `npm audit` clean) → commit + push + PR. Sets row to `✅ shipped`. |
| `/eo-debug` | any | Invokes `superpowers:systematic-debugging`. Evidence-based, no guessing. |
| `/eo-retro` | end of sprint | Captures recurring patterns from `.claude/lessons.md` and promotes to global if pattern triggered across 3+ projects. |

### L2 — EO Skills (10)

| Skill | Role | Key contract |
|---|---|---|
| `eo-dev-start` | Bootstrap orchestrator | 11-step. Worktree-aware. Plan-mode gated. Never overwrites. Emits evidence table. |
| `eo-dev-repair` | Triage + surgical rebuild | Classifies every missing signal. Mixed state → refuse ALL repair (don't mask upstream gap). Failure rollback with manifest. |
| `eo-guide` | Phase detector + router | Reads 10 filesystem signals, matches one state, prints next command. Never recommends shipping in inconsistent state. |
| `handover-bridge` | Template application | 11-step scaffolder. Writes CLAUDE.md, `.claude/`, `.github/workflows/ci.yml`, `_dev-progress.md`, placeholder `@AC-N.N` tests, UX reference copy, first commit. Rejects pre-conditions if global CLAUDE.md missing. |
| `eo-scorer` | 5-hat scoring | Product, Architecture, Engineering, QA, UX — each 1-10, composite = avg × 10. Calibrated for solo-founder reality (90+ real, not inflated). |
| `lessons-manager` | Rule capture | Turns every correction into one `trigger → rule → check` entry in `.claude/lessons.md`. |
| `elegance-pause` | Forced simplification check | Before accepting "done," asks: can this be simpler? Catches over-engineering. |
| `brd-traceability` | AC ↔ test mapping | Parses `@AC-N.N` tags in BRD and tests. Flags gaps. Counts tests per story for `/eo-guide`. |
| `arabic-rtl-checker` | MENA UI gate | Runs on every UI change. Catches RTL overflow, mirrored icons, mis-aligned numerals. |
| `mena-mobile-check` | MENA mobile gate | 375px viewport, AED/SAR/QAR/KWD currency, Fri/Sat weekend, DD/MM/YYYY dates. |

### L3 — External packs (kept separately installed)

| Pack | Invoked by | Why keep separate |
|---|---|---|
| `gstack` | `/eo-review`, `/eo-ship` | Domain-generic code review + ship discipline. Not EO-specific. One install, many projects. |
| `superpowers` | `/eo-code`, `/eo-debug` | TDD, systematic debugging, brainstorming. Evergreen techniques. One install, many projects. |

---

## 3. Three real scenarios

### Scenario A — Brand new project (Day 1)

**Pre-conditions:** EO-Brain phases 0-4 complete next to (or inside) the project folder. Global CLAUDE.md + settings.json present. `eo-microsaas-dev` plugin installed.

```
┌─ Day 1 ────────────────────────────────────────────────────────┐
1. cd into empty project folder, open Claude Code
2. /eo-dev-start
   → plan mode: previews CLAUDE.md, tests, CI, hooks, first commit
   → you approve (y)
   → handover-bridge runs, evidence table prints (bytes + lines)
3. /eo-plan Story-1-Registration
   → reads BRD Story 1 + its @AC-1.1 through @AC-1.10
   → writes docs/plans/story-1-signup.md
4. /eo-code
   → superpowers:TDD — test first, code second
   → runs until all @AC-1.N tests pass
5. /eo-review
   → gstack:/review — fix any <8/10
6. /eo-score
   → 5-hat. Target: composite ≥90, every hat ≥8.
   → 80-89 → /eo-bridge-gaps → re-score
   → <80 → back to /eo-code
7. /eo-ship
   → validates gates one more time, commit + push + PR + tag
   → CI runs on GitHub (the source of truth)
   → Status: ✅ shipped in _dev-progress.md
└────────────────────────────────────────────────────────────────┘
```

**What you never do:** paste a 75-line prompt. Hand-write CLAUDE.md. Manually create doc folders. Set up CI. Seed lessons.md. The bootstrap did all of that once.

---

### Scenario B — Existing project, daily dev loop (minor releases, patches, next story)

**Pre-conditions:** Project bootstrapped. You're opening a fresh Claude Code chat — could be same day, could be 3 days later.

```
┌─ Resuming work ───────────────────────────────────────────────┐
1. /eo-guide
   → scans filesystem:
     CLAUDE.md ✅, brd.md ✅, Story 1 shipped, Story 2 mid-code
     tests 3/5 passing on Story 2
   → "📍 You're at: ready-to-code. ⏭️ Next: /eo-code. ⏱️ 30-45 min."
2. /eo-code
   → continues Story 2 in TDD. All 5 tests pass.
3. /eo-review → /eo-score → /eo-bridge-gaps (if 80-89) → /eo-ship
4. /eo-retro   (end of sprint)
   → reads this sprint's lessons from .claude/lessons.md
   → if a pattern hit 3+ projects, promotes to ~/.claude/lessons.md

NEXT MAJOR VERSION (e.g., Story 3 starts):
5. /eo-guide  →  /eo-plan Story-3-whatever  →  /eo-code  →  …

PATCH (bug fix, no new BRD story):
6. /eo-debug → superpowers:systematic-debugging → root cause → fix
7. /eo-review → /eo-score → /eo-ship  (skips /eo-plan, no new AC)
└────────────────────────────────────────────────────────────────┘
```

**Key principle:** `/eo-guide` is the entry point every session after bootstrap. You never guess "where was I" — the filesystem tells you.

---

### Scenario C — QA (pre-ship quality loop)

**Pre-conditions:** You or Claude just finished coding. Tests pass locally. Not shipped yet.

```
┌─ Quality gate ────────────────────────────────────────────────┐
1. /eo-review
   → gstack 4-dim review
   → address every <8/10 finding
2. /eo-score
   → 5 hats, student calibration (no inflation)
   → if MENA user-facing: arabic-rtl-checker + mena-mobile-check
     auto-run inside UX hat
3. Composite decision:
     ≥90 and every hat ≥8 → 🧪 scoring → go to /eo-ship
     80-89              → /eo-bridge-gaps (fix weakest hat, re-score)
     <80                → back to /eo-code (don't ship, don't bridge)
4. If blocked repeatedly on same hat:
   → lessons-manager captures the pattern
   → next time /eo-score can pre-flag it
5. /eo-ship
   → re-runs the gate, then commit + push + PR + CI
   → GitHub CI is the final arbiter. If it fails, nothing deployed.
└────────────────────────────────────────────────────────────────┘
```

**Key principle:** scoring is cheap (5-10 min). Shipping below 90 is the expensive thing — it creates bug debt that shows up 2 weeks later as "why is this broken" at the worst moment.

---

## 4. Questions a new student will ask (and the real answers)

**Q: I opened a new Claude Code chat and typed `/eo-plan`. It's acting confused. What did I do wrong?**
A: You skipped `/eo-guide`. Always start a resumed session with `/eo-guide` (or `/eo-dev-start` if brand new). It reads the filesystem and tells you the real next command. `/eo-plan` works, but only if you're actually at the planning phase — maybe you're really at `/eo-code` or `/eo-score`.

**Q: I deleted `.claude/lessons.md` by accident. Am I cooked?**
A: No. Run `/eo-dev-repair`. `lessons.md` is silent-repair-safe — it regenerates empty. You lose prior accumulated lessons, but the file comes back and the SessionStart hook works again. If you have the file in git history, check out the last good version first.

**Q: `/eo-dev-repair` refused and told me to finish "Phase 4 in Cowork." What does that mean?**
A: Your `architecture/brd.md` or `architecture/tech-stack-decision.md` is missing, and EO-Brain doesn't have a copy either. These come from EO-Brain Phase 4 (the `4-eo-tech-architect` skill in Cowork). There's no shortcut — no template can substitute a BRD written for your specific product. Go finish Phase 4, then re-run `/eo-dev-start`.

**Q: My `/eo-score` keeps landing at 88 on the QA hat. What now?**
A: `/eo-bridge-gaps`. It targets the lowest hat, fixes it, re-scores. If QA keeps recurring as the lowest hat across 3+ stories, `/eo-retro` will surface the pattern and promote the rule to `~/.claude/lessons.md` so you don't keep hitting it.

**Q: Do I need to commit after every command?**
A: Conceptually yes, per L-009 (push discipline). Practically: `/eo-ship` is the command that commits + pushes + PRs. The intermediate commands (`/eo-plan`, `/eo-code`) produce files in your working tree; `/eo-ship` bundles them into the final commit. If you want to checkpoint mid-work, commit manually — the hooks still run.

**Q: Why does `/eo-dev-start` want me to approve in plan mode? Just run it.**
A: Because the only safe default for a bootstrap is "show me what will happen, let me say yes." If the plan is wrong (wrong EO-Brain path, wrong project identity), you catch it in the preview — not after 30 files are written. This is the same reason surgeons don't skip the pre-op checklist.

**Q: I'm on a different branch (worktree). `/eo-guide` looks at `pwd` — will it get confused?**
A: No. All four new commands (`/eo-dev-start`, `/eo-dev-repair`, `/eo-guide`, `/eo-status`) honor `$GIT_WORK_TREE` first, then `git rev-parse --show-toplevel`. They never assume `pwd` is the repo root. This is explicit in every skill's Step 1.

**Q: The plugin wants `~/.claude/CLAUDE.md` to exist. I don't have one. What goes in it?**
A: Global cross-project rules (who you are, what you build, your servers, your SOPs). Everything project-specific lives in `{project}/CLAUDE.md`. If `~/.claude/CLAUDE.md` is missing, `handover-bridge` Step 0 aborts — it won't bootstrap a project when the global context is missing, because every session would run without it.

**Q: What's the difference between `gstack:/review` and `/eo-review`?**
A: `/eo-review` *is* `gstack:/review` with EO-specific guardrails added on top (Arabic RTL, MENA mobile, banned buzzwords). The underlying 4-dimension review is gstack's. L2 adds context, L3 does the generic work.

**Q: `/eo-ship` is refusing because `npm audit` shows a high-severity CVE in a transitive dep. Can I override?**
A: No silent override. Either: (a) update the dep and re-run `/eo-ship`, (b) pin a safe version in package.json + document the reasoning in `docs/handovers/`. The whole point of the gate is that you can't ship at 89 and you can't ship with known CVEs. The gate is the feature.

**Q: I ran `/eo-dev-start` in a folder that already had stuff. It refused and said "route to `/eo-dev-repair`." Did I lose anything?**
A: Nothing. `/eo-dev-start` does not write on refusal — the skill exits before invoking `handover-bridge`. Your files are untouched. Run `/eo-dev-repair` next.

**Q: My GitHub CI is green but my local tests fail. Which one is right?**
A: **GitHub is right.** L-009 names GitHub the single source of truth. If local fails and remote passes, your local state is stale or polluted (uncommitted changes, wrong Node version, dirty cache). Pull, clean install, re-run. If they still disagree, fix local to match remote — never the other way.

**Q: How do I know when to version bump the plugin itself vs. my project?**
A: Different things. **Plugin versioning** (`eo-microsaas-dev` v1.2.0 etc.) is done by the plugin maintainer — you consume it via `claude plugin update`. **Project versioning** (your MicroSaaS v0.1, v0.2…) is yours — tag at `/eo-ship` after each shipped story or sprint.

**Q: I keep getting "banned buzzword" warnings from the scorer. Is this real?**
A: Yes and it's intentional. "Leverage," "synergy," "ecosystem," "holistic," "digital transformation," "cutting-edge," "world-class," "best-in-class" — these are filler. Students use them to sound professional; they hide the actual claim. Rewrite with the concrete noun ("200 Arabic SaaS founders in UAE" instead of "leverage MENA network"). The scorer catches it before the user does.

**Q: What if I hit a bug in the plugin itself?**
A: File an issue at `github.com/smorchestraai-code/eo-microsaas-training/issues`. Don't edit plugin files in place on your machine — they'll be overwritten on next `claude plugin update`. If it's urgent, fork, fix, PR.

---

**TL;DR for a new operator:** `/eo-dev-start` once per project. `/eo-guide` every session after. The chain in between (`/eo-plan → /eo-code → /eo-review → /eo-score → /eo-ship`) is the real work. Everything else is there to catch you when you drift.
