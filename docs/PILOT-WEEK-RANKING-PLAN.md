# Pilot Week Ranking Plan — eo-microsaas-dev v1.0.0-pilot

**Purpose:** After cowork aligns `4-eo-tech-architect` + `4-eo-code-handover`, how do we verify the plugin is 10/10 per hat? This is the concrete evidence required — no hand-waving.

**Timeline:** 1 pilot week, 2-3 students, real projects (not toy examples).

---

## Current score (pre-pilot): 92/100

| Hat | Score | Why |
|-----|:-----:|-----|
| Product | 9.5 | BRD at `architecture/brd.md`, out-of-scope documented, ICP + measurable success metric defined |
| Architecture | 10 | Clean module split, plugin.json validated by CI, no dead refs, trend.csv schema, templates complete |
| Engineering | 9.5 | `validate-plugin.sh` runs in CI, L-001 + L-002 lessons captured, elegance-pause enforced retroactively |
| QA | 7 | **UNVALIDATED in a real Claude Code session with a real project.** This is the only honest floor. |
| UX | 10 | EO-Brain artifacts now land in `docs/ux-reference/`, `/eo-plan` + `/eo-review` both read them, ux-hat Q1 drops to 6 if component doesn't match |

**Composite: (9.5 + 10 + 9.5 + 7 + 10) × 2 = 92**

---

## How each hat gets to 10/10 after pilot

### Product hat: 9.5 → 10

**Missing piece:** real user validation. A student completes EO-Brain → handover-bridge → ships first feature using only the plugin's workflow.

**Evidence required to score 10:**
- [ ] ≥1 pilot student completes `/eo-plan` → `/eo-code` → `/eo-score` loop end-to-end
- [ ] Student's self-reported "did the plugin reduce my ramp-up time?" answer is yes with specifics
- [ ] No student reports "the plugin told me to do something that didn't match my project"
- [ ] BRD from `4-eo-tech-architect` (post-cowork-revamp) parses correctly for `AC-N.N` tags

**How to measure:** pilot exit survey (5 questions), 1:1 debrief with each student.

### Architecture hat: 10 → 10

Already 10. No pilot change expected. Red flag that would drop it: if the plugin collides with gstack or superpowers in a real session (e.g., both try to own `/review`). Unlikely but testable.

**Evidence required to HOLD 10:**
- [ ] No command-name collisions reported during pilot
- [ ] Plugin loads correctly on both macOS and Linux (test both)
- [ ] `validate-plugin.sh` passes on every commit that touches the plugin

### Engineering hat: 9.5 → 10

**Missing piece:** CI on the plugin repo. `validate-plugin.sh` exists but isn't wired to GitHub Actions yet.

**Evidence required to score 10:**
- [ ] `.github/workflows/validate.yml` runs `validate-plugin.sh` on every PR
- [ ] At least one PR during pilot demonstrates the validator catching a regression (proves it's active)
- [ ] Every skill has a 1-line self-test noted in SKILL.md ("how to verify this skill works")

**Effort:** ~30 min to wire CI.

### QA hat: 7 → 10 — **the big lift, requires pilot**

This IS the whole point of pilot week. Four specific evidence items:

**Evidence required to score 10:**

1. **Manual smoke test passes on a fresh machine** (Q1 happy path)
   - Student runs `bash install.sh` on a clean macOS install
   - Types `/eo` in Claude Code, sees all 8 commands autocomplete
   - Runs `/eo-plan "add a testimonial"` in a test project
   - Plan mode engages, BRD is read, artifacts referenced
   - **Pass criterion:** zero errors, plan shows within 10s

2. **All 5 hats score-able from a real PR** (Q2-5 empty/error/edge/auth)
   - Student's first real PR gets scored
   - Every hat's 8 questions answerable from the PR evidence
   - Composite computed correctly
   - **Pass criterion:** score report matches the calibration-examples.md format

3. **Bridge-gaps loop works** (Q6 verification evidence)
   - A PR that scores 82 (intentionally imperfect)
   - `/eo-bridge-gaps` identifies the lowest hat, proposes fixes
   - After applying fixes, re-score lifts the hat ≥8
   - **Pass criterion:** PR goes 82 → 90+ without human intervention on the fixable items

4. **Regression prevention** (Q7)
   - Student ships a PR at 90+
   - Next PR breaks a previously-passing test
   - Plugin surfaces the regression before merge
   - **Pass criterion:** regression caught by `/eo-review` or `/eo-score`

**If all 4 pass:** QA hat = 10. If 3 of 4: QA = 8. If <3: remain at 7 and re-pilot.

### UX hat: 10 → 10

Already 10 post-artifact-ingestion. **But only if the cowork revamp ships.**

**Evidence required to HOLD 10:**
- [ ] Cowork ships revamped `4-eo-code-handover` with `5-CodeHandover/artifacts/` contract
- [ ] Pilot student's artifacts land at expected path
- [ ] `handover-bridge` successfully copies to `docs/ux-reference/`
- [ ] At least 1 PR during pilot has UX hat scored by comparing rendered component to artifact

**Risk:** If cowork revamp slips, UX reverts to 8 (no artifacts = no ground truth).

---

## The pilot execution plan (1 week)

### Day 0 (pre-pilot, you + cowork)
- [ ] Cowork ships `eo-microsaas-os` v2.3 with the 3 gaps fixed (BRD tagging + bootstrap prompt + artifact contract)
- [ ] You push `eo-microsaas-dev` v1.0.0-pilot to GitHub
- [ ] You pick 2-3 pilot students and brief them (15 min each)

### Day 1
- [ ] Each pilot student runs EO-Brain phases 0-4 with cowork's revamped plugin
- [ ] Each student reaches `5-CodeHandover/` with BRD + artifacts generated
- [ ] Each student runs `bash install.sh` and verifies the manual smoke test

### Day 2-3
- [ ] Each student runs `handover-bridge` (via bootstrap prompt in Claude Code)
- [ ] Each student ships first feature using `/eo-plan` → `/eo-code` → `/eo-review` → `/eo-score`
- [ ] You collect score reports + PR links

### Day 4
- [ ] Intentional bridge-gaps test: one student pushes a PR designed to score ~82
- [ ] Verify `/eo-bridge-gaps` lifts it to 90+
- [ ] Collect `.claude/lessons.md` files — are lessons accruing?

### Day 5
- [ ] Regression test: a student's second PR breaks a prior test
- [ ] Verify plugin catches it
- [ ] Exit interviews: 20 min per student

### Day 6-7
- [ ] Score the pilot against the 4 QA evidence criteria above
- [ ] Write `docs/pilot-retro.md` with real scores + lessons for v1.1
- [ ] Decide: ship v1.0.0 (drop -pilot suffix) OR iterate

---

## Red flags during pilot that block 10/10

Any of these during pilot → score stays at 92 or drops, cannot reach 100:

1. **Plugin fails to load for >1 student** — Architecture drops to 7
2. **A hat's 8 questions can't be answered from a real PR** — QA stays at 7, rubric needs rework
3. **Students ignore the plugin and use gstack directly** — Product drops (orchestration failed)
4. **`.claude/lessons.md` stays empty after 5 PRs** — Engineering drops (self-improvement loop dead)
5. **No student's UX hat references the artifact** — UX drops to 8 (artifact ingestion useless in practice)

---

## What I commit to (no sandbagging)

- I will NOT re-score this plugin above 92 until the 4 QA evidence items are demonstrated
- I will score each pilot student's first PR honestly — no "encouragement inflation"
- If pilot reveals a rubric question that's unanswerable, I will rewrite that question, not lower my scoring standard
- If pilot reveals the plugin is duplicating gstack/superpowers work, I will strip the duplication before v1.1

This is the contract. Hold me to it.
