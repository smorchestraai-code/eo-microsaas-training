# eo-microsaas-dev v1.3.0 — Complete Operator's Guide

**For the student or operator opening this plugin for the first time.** Every command, every skill, three real-world scenarios, and the traps new people hit.

**Version:** 1.3.0 (2026-04-23)
**Plugin repo:** https://github.com/smorchestraai-code/eo-microsaas-training
**Applies to:** fresh EO MicroSaaS projects bootstrapped from EO-Brain phases 0-4.

**What changed in v1.3:** a new `/eo-github` command + `eo-github` skill that acts as GitHub admin for your project (create / point to existing / guided / audit). `/eo-dev-start` now asks one 4-option question when no GitHub remote is mounted — so you can bootstrap fully local and push later. See §9 for the v1.3 delta.

---

## 1. The three-layer model

The plugin is a stack. Each layer hides the next one's complexity. You only ever type into **L1**.

```
┌─────────────────────────────────────────────────────────────────┐
│ L1 — COMMANDS (what you type)                                   │
│   /eo-dev-start   /eo-dev-repair   /eo-github                   │
│   /eo-guide   /eo-status                                        │
│   /eo-plan   /eo-code   /eo-review   /eo-score                  │
│   /eo-bridge-gaps   /eo-ship   /eo-debug   /eo-retro            │
└────────────────────────────┬────────────────────────────────────┘
                             │ thin wrappers — activate a skill
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ L2 — EO SKILLS (plugin-specific logic, EO/MENA-aware)           │
│   eo-dev-start   eo-dev-repair   eo-github   eo-guide           │
│   handover-bridge   eo-scorer (5-hat)   lessons-manager         │
│   elegance-pause   brd-traceability                             │
│   arabic-rtl-checker   mena-mobile-check                        │
└────────────────────────────┬────────────────────────────────────┘
                             │ orchestrate (do not duplicate)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ L3 — EXTERNAL SKILL PACKS (domain-generic, installed once)      │
│   gstack:        /review   /design-review   /ship               │
│   superpowers:   test-driven-development                        │
│                  systematic-debugging                           │
│                  brainstorming                                  │
│   MCP:           mcp__github__* (required by eo-github only)    │
└─────────────────────────────────────────────────────────────────┘
```

### What each layer encapsulates

| Concern | Handled at | How |
|---|---|---|
| **GitHub = single source of truth** | L2 `eo-github` (create/point/audit) + `handover-bridge` + L1 `/eo-ship` | `eo-github` is the ONLY skill allowed to touch a remote. Bootstrap writes `.github/workflows/ci.yml` (Node 22 + lint + test + build + `npm audit`). `/eo-ship` pushes, opens PR, tags. CI runs on GitHub, not locally — GitHub HEAD is always the authoritative build. L-009 in global CLAUDE.md makes push mandatory at every work unit. `eo-github` enforces best practices: private by default, squash-merge only, no wikis/projects/discussions, branch protection deferred to post-first-CI (because protection rules can't require status checks that have never run). |
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

### L1 — Commands (13)

**Meta — bootstrap, GitHub & continuity (5)**

| Command | When | What it does |
|---|---|---|
| `/eo-dev-start` | First session in fresh project | Reads EO-Brain phases 0-4, previews bootstrap in plan mode, asks one 4-option question if no GitHub remote is mounted (`create` / `point-existing` / `continue locally` / `I don't know`), invokes `handover-bridge` on approval, then routes to `/eo-github` if you picked option 1/2/4+MCP. Routes partial → `/eo-dev-repair`, bootstrapped → `/eo-guide`. |
| `/eo-dev-repair` | Project is partially set up | Triages missing pieces: silent-repair-safe (CLAUDE.md, lessons, hooks, CI) rebuilt from templates; refuse-and-route (BRD, architecture, project-brain) refused with EO-Brain phase to finish. |
| `/eo-github` | When you want GitHub | **NEW in v1.3.** MCP-only GitHub admin. Four modes: `create` (new private repo with best practices), `point-existing <url-or-owner/repo>` (wire an empty remote you already made), `guided` (A/B/C menu), `audit` (drift report vs best-practices matrix with per-item y/n fix). Plan-aware (free/pro/team/enterprise). Branch strategy: trunk for solo, dual-branch for team. |
| `/eo-guide` | Any returning session | Scans filesystem, tells you exact next command + ETA. Works 3 days after last session, no paste. v1.3 adds `local-only-bootstrapped`, `git-local-no-remote`, `ready-to-ship-but-no-remote` routing. |
| `/eo-status` | Quick glance | Compact dashboard only. No coaching. Now shows Git state (local / remote / no-git). |

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

### L2 — EO Skills (11)

| Skill | Role | Key contract |
|---|---|---|
| `eo-dev-start` | Bootstrap orchestrator | 11-step + Step 9b GitHub-intent question. Worktree-aware. Plan-mode gated. Never overwrites. Never touches remotes (delegates to `eo-github`). Emits evidence table. |
| `eo-dev-repair` | Triage + surgical rebuild | Classifies every missing signal. Mixed state → refuse ALL repair (don't mask upstream gap). Failure rollback with manifest. |
| `eo-github` | **NEW v1.3 — GitHub admin** | MCP-only (`mcp__github__*`). Four modes: create / point-existing / guided / audit. Plan-aware feature set. Picks trunk vs dual-branch from collaborator count. Applies best-practices settings. Defers branch protection to post-first-CI. Private by default. Never force-pushes. |
| `eo-guide` | Phase detector + router | Reads 12 filesystem signals (10 + git + origin), matches one state, prints next command. v1.3 adds 3 GitHub-aware states. Never recommends shipping in inconsistent state. |
| `handover-bridge` | Template application | 11-step scaffolder. Writes CLAUDE.md, `.claude/`, `.github/workflows/ci.yml`, `_dev-progress.md`, placeholder `@AC-N.N` tests, UX reference copy. First commit + `git init` now conditional on `github_intent`. Never adds a remote. Never pushes. |
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
   → Step 9b: "No GitHub remote mounted. 1/2/3/4?"
        1 = create new private repo (if mcp__github__* is connected)
        2 = point to an existing empty repo you already made
        3 = continue locally — no git, no remote
        4 = I don't know (routes to /eo-github guided, or local if no MCP)
   → handover-bridge runs, evidence table prints (bytes + lines)
   → if option 1/2/4+MCP: /eo-github runs next — its own plan preview,
     creates/wires repo with best-practices settings, first push
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
   → first green CI triggers /eo-github audit's protection offer
   → Status: ✅ shipped in _dev-progress.md
└────────────────────────────────────────────────────────────────┘
```

**What you never do:** paste a 75-line prompt. Hand-write CLAUDE.md. Manually create doc folders. Set up CI. Seed lessons.md. Manually configure GitHub settings. Manually add labels. The bootstrap + `eo-github` do all of that once.

**What if you picked option 3 (local-only)?** Your project is fully scaffolded locally without git. Build, test, iterate. When your MVP works end-to-end, run `/eo-github` — it'll ask whether to create a new repo or point to an existing one, then do the first push. `/eo-guide` surfaces this as `local-only-bootstrapped` and tells you exactly when to promote.

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

**Q: `/eo-dev-start` asked me a 4-option question about GitHub. I don't know what to pick.**
A: Pick option 4 (`I don't know`). If GitHub MCP is connected, it'll route you into the guided menu with a plain-English explanation of create vs. point-existing. If MCP isn't connected, it'll tell you to keep building locally and come back when your MVP is real. There is no wrong answer — option 3 (local-only) is completely safe and the plugin works without GitHub.

**Q: I picked option 3 (local) and now I regret it. Did I lose anything?**
A: No. Nothing got pushed because there's no remote. Run `/eo-github` anytime — it'll ask you "create new" or "point to existing" and handle the first push. `handover-bridge` didn't initialize git when you picked option 3, so `/eo-github` will do `git init` as part of its run.

**Q: I created the repo on GitHub manually before running `/eo-dev-start`. Will it overwrite or conflict?**
A: No. If `git config --get remote.origin.url` returns your URL, `/eo-dev-start` skips the 4-option question entirely and just preserves your existing remote. `handover-bridge` writes local files, commits, and hands off to `/eo-ship` for the next push.

**Q: `/eo-github` says my repo isn't empty and refuses to push. Why?**
A: Because blindly pushing onto a non-empty remote is how history gets rewritten and work gets lost. If the existing commits are yours from an earlier session, use `git pull --rebase origin main` and then `git push` manually. If they're someone else's, create a new repo. `/eo-github` will never force-push to "fix" this.

**Q: I'm on a free GitHub plan. Why doesn't `/eo-github` show required reviewers?**
A: Because GitHub silently ignores that setting on free/pro. If the skill offered it, you'd think it was active — and learn the wrong mental model. On Team+/Enterprise plans, the option appears. This is intentional.

**Q: What's the `/eo-github audit` for?**
A: Drift. You (or a collaborator, or GitHub itself through UI changes) might flip `has_wiki` on, forget to enable `delete_branch_on_merge`, or let labels proliferate. `/eo-github audit` reads current repo state, compares to the best-practices matrix, and prints a per-item `y/n` drift report. Nothing batch-fixes without you approving each item.

**Q: When does branch protection on `main` kick in?**
A: After your first `/eo-ship` green CI run. Not before. Branch protection rules can't require a status check that has never run — trying to set it up at repo creation just means you can't push anything without overriding your own rules. Post-first-CI is the clean moment to lock down.

**Q: I added a collaborator. Will the skill change anything?**
A: Run `/eo-github audit`. If collaborators are now ≥2, it'll propose creating a `dev` branch and switching to dual-branch strategy (feature → dev → main). You approve each change; nothing happens silently.

---

## 9. What changed in v1.3 (delta from v1.2)

**One addition, one clarification, three routing updates.**

### 1. New: `/eo-github` command + `eo-github` skill

The only skill in the plugin allowed to touch a GitHub remote. Four modes:

| Mode | When to use |
|---|---|
| `create` | You don't have a GitHub repo yet. Plugin creates one (private), applies best-practices settings, wires origin, pushes. |
| `point-existing <url>` | You made an empty repo on GitHub already. Plugin validates it's empty + writable, shows a settings-drift diff, wires origin, pushes. |
| `guided` | You picked option 4 ("I don't know") in `/eo-dev-start`. Plugin explains create vs. point-existing in one screen and routes. |
| `audit` | Any time post-setup. Plugin reads current repo state, computes drift vs. best practices, prints a per-item `y/n` fix report. |

**Hard contracts:**
- **MCP-only.** Requires `mcp__github__*` tools. No `gh` CLI fallback. Refuses cleanly with install remediation if MCP is missing.
- **Private by default.** Flip to public in GitHub UI when ready.
- **Never force-pushes.** If push is rejected as non-fast-forward, remediation is shown — you resolve manually.
- **Plan-aware.** Free/pro/team/enterprise detection. Never offers settings that your plan would silently ignore (required reviewers, CODEOWNERS enforcement).
- **Strategy-aware.** Solo (≤1 collaborator) → trunk-only. Team (≥2) → `main` + `dev`. Auto-detected from the collaborator list.
- **Post-first-CI protection.** Branch protection is deferred until your first `/eo-ship` green CI run, then offered via `/eo-github audit`.

### 2. Clarification: `/eo-dev-start` now asks one 4-option question

When you run `/eo-dev-start` and no GitHub remote is mounted, you see:

```
📍 No GitHub remote mounted yet. How do you want to handle GitHub?

  1. Create a new private repo now
  2. Point to a repo I already created on GitHub
  3. Continue locally — no GitHub yet
  4. I don't know

(1/2/3/4):
```

| Answer | MCP connected? | What happens |
|---|---|---|
| `1` | yes | After handover-bridge, `/eo-github create` runs. |
| `1` | no | Falls through to local-only with remediation (install MCP, re-run later). |
| `2` | yes | After handover-bridge, `/eo-github point-existing <url>` runs. |
| `2` | no | Same as 1 + no. |
| `3` | any | No git init. No remote. Fully local. Run `/eo-github` later when ready. |
| `4` | yes | After handover-bridge, `/eo-github guided` menu. |
| `4` | no | Local-only with "install MCP when your MVP is ready" remediation. |

If `git config --get remote.origin.url` already returns a value, the question is skipped entirely — the existing remote is preserved.

### 3. Routing updates in `/eo-guide`

Three new phase states (all route to `/eo-github`):

| State | Trigger | What `/eo-guide` says |
|---|---|---|
| `local-only-bootstrapped` | Bootstrap complete, no `.git/` | "Keep building locally. When your MVP works end-to-end, run `/eo-github`." |
| `git-local-no-remote` | `.git/` present, no `remote.origin.url` | "Run `/eo-github` — all other `/eo-*` commands work but `/eo-ship` needs a remote." |
| `ready-to-ship-but-no-remote` | Score ≥ 90, no remote | "Run `/eo-github` first — `/eo-ship` needs somewhere to push." |

### 4. `handover-bridge` is now git-optional

`git init` and the first commit now run **only** when `github_intent ∈ {create, point-existing, guided, already-wired}`. For `local-only`, neither happens — the scaffold stays uncommitted on disk until you decide. `handover-bridge` never adds a remote (that's `eo-github`'s job) and never pushes.

### 5. Self-contained config — no new files

GitHub state lives in `git config --get remote.origin.url`. No `.claude/project.json`. No `.eo-github-state`. The single source of truth is already in git itself.

### Migration from v1.2.0

- **You already have a remote:** no change. `/eo-dev-start` detects it and skips the 4-option question.
- **You have local git, no remote:** `/eo-guide` will surface `git-local-no-remote` and route to `/eo-github` when you're ready.
- **No breaking changes.** Every prior command and skill retains behavior.

---

**TL;DR for a new operator:** `/eo-dev-start` once per project. Answer the 4-option GitHub question (or skip if you already have a remote). `/eo-github` when you want to push and don't have a remote yet, or any time for a drift audit. `/eo-guide` every returning session. The chain in between (`/eo-plan → /eo-code → /eo-review → /eo-score → /eo-ship`) is the real work. Everything else is there to catch you when you drift.
