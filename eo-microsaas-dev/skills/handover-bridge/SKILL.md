# handover-bridge — EO-Brain → Claude Code Handoff

**Purpose:** Convert EO-Brain Phase 5 (Code Handover) output into a Claude Code–ready project with BRD, tests, lessons, and claude.md — the first commit every student makes.

**Pillar:** EO-specific — closes the gap between strategy (EO-Brain) and execution (Claude Code)
**Time cost:** 15-20 minutes one-time per project.

---

## When to run

**Once per project, at project birth.**

The student has completed EO-Brain phases 0-5:
- Phase 0: Scorecards (Triple Assessment, GTM Fitness)
- Phase 1: ProjectBrain (ICP, positioning, voice, thesis)
- Phase 2: GTM (motions, assets)
- Phase 3: Newskills (team/skill map)
- Phase 4: Architecture (tech stack, BRD, diagrams)
- Phase 5: CodeHandover (what this skill consumes)

The student now has a folder `CodingProjects/{ProjectName}/` with loose files. This skill transforms it into a proper dev-ready repo.

---

## The handoff contract

### Input (from EO-Brain Phase 5)

```
{ProjectName}/
  project-brain/
    icp.md
    positioning.md
    brandvoice.md
  architecture/
    tech-stack-decision.md
    brd.md
    architecture-diagram.md
  gtm-assets/
    ... (MD blueprints)
  ux-artifacts/                   ← from 4-eo-code-handover skill
    product-demo.html (or .jsx)   ← interactive product mockup
    onboarding-flow.html (or .jsx)← first-run UX mockup
    admin-dashboard.html (or .jsx)← admin panel layout mockup
```

### Output (Claude Code–ready)

```
{ProjectName}/
  .claude/
    lessons.md              ← NEW (empty, ready to accrue)
    settings.json           ← NEW (SessionStart hook loads lessons)
  .git/                     ← NEW (init + first commit)
  .github/
    workflows/
      ci.yml                ← NEW (PR quality gate)
  CLAUDE.md                 ← NEW (150-line student-calibrated, links to global)
  README.md                 ← NEW (project overview)
  _dev-progress.md          ← NEW (story tracker read by /eo-guide)
  architecture/
    brd.md                  ← copied from EO-Brain
    ... (other EO-Brain docs)
  docs/
    qa-scores/              ← NEW (empty dir for score history)
    handovers/              ← NEW (empty dir)
  src/                      ← NEW (scaffolded per tech stack)
  tests/                    ← NEW (placeholder tests with @AC-N.N stubs)
  docs/ux-reference/        ← NEW (ingested EO-Brain artifacts — ground truth for UI)
    product-demo.html
    onboarding-flow.html
    admin-dashboard.html
    ARTIFACT-INDEX.md       ← what each shows, which BRD stories it covers
  package.json              ← NEW (scaffolded)
  .gitignore                ← NEW
  .env.example              ← NEW (from tech-stack-decision.md)
```

---

## The 11-step handoff

### Step 0 — Precondition: global playbook must be installed

Before anything else, verify the student ran `install.sh`:

```bash
test -f ~/.claude/CLAUDE.md && test -f ~/.claude/settings.json || {
  echo "STOP: Global playbook missing (~/.claude/CLAUDE.md or ~/.claude/settings.json)."
  echo "Re-run install.sh from the EO playbook bundle before continuing."
  exit 1
}
```

This catches the silent-drift failure where a student installs the plugin without the global playbook. Every downstream step assumes global hooks, lessons format, and voice rules are already active.

### Step 1 — Verify EO-Brain output is complete
Check all required files exist:
- [ ] `project-brain/icp.md`
- [ ] `project-brain/positioning.md`
- [ ] `project-brain/brandvoice.md`
- [ ] `architecture/brd.md` with ≥1 user story + numbered ACs (format `AC-N.N`)
- [ ] `architecture/tech-stack-decision.md` naming specific libs/services
- [ ] `ux-artifacts/` containing at least product-demo + onboarding-flow (admin-dashboard optional)

If BRD or project-brain missing → return to EO-Brain, don't bridge yet.
If ux-artifacts missing → bridge proceeds, but UX hat caps at 8 until artifacts land (they are the UX ground truth).

### Step 2 — Generate CLAUDE.md (150 lines max)
Template at `templates/CLAUDE.md.template`. Fill in:
- Project name, domain, ICP (from project-brain)
- Tech stack (from architecture)
- Env vars needed (from architecture)
- Design tokens (colors, fonts) from brandvoice
- MENA flag (yes/no → triggers arabic-rtl-checker + mena-mobile-check)
- Build sequence (standard 6 phases)

Include at the bottom: a precedence note — "Global playbook is at `~/.claude/CLAUDE.md`. Project CLAUDE.md overrides global when they conflict. If a rule is missing here, fall through to global."

### Step 3 — Initialize git
```bash
cd {ProjectName}
git init
git remote add origin git@github.com:{user}/{ProjectName}.git
```

### Step 3b — Ingest UX artifacts
Copy from EO-Brain:
```bash
mkdir -p docs/ux-reference
cp ux-artifacts/*.html docs/ux-reference/ 2>/dev/null || true
cp ux-artifacts/*.jsx  docs/ux-reference/ 2>/dev/null || true
```
Generate `docs/ux-reference/ARTIFACT-INDEX.md` mapping each artifact to the BRD story it visualizes:
```markdown
# UX Reference Artifacts

These are the UX ground truth from EO-Brain Phase 5. Use them as the target
for any UI work. `/eo-plan` reads them when planning visual features.
`/eo-review` UX hat compares rendered components against these.

| Artifact | Covers BRD stories | What to match |
|----------|-------------------|---------------|
| product-demo.html | Story 1, Story 2 | Core workflow layout, primary CTAs, empty states |
| onboarding-flow.html | Story 3 | First-run screens, form fields, progress indicator |
| admin-dashboard.html | Story 5 | Data table layout, filter positions, bulk actions |
```

This is non-negotiable: a component shipped that doesn't match the artifact → UX hat Q1 drops to 6.

### Step 4 — Scaffold src/ per tech stack
If Next.js + Supabase (EO default):
```bash
npx create-next-app@latest src --typescript --tailwind --app --no-src-dir
```
Move generated files into place, don't nest.

### Step 5 — Generate placeholder tests from BRD
For each `AC-N.N` in brd.md, generate:
```ts
// tests/{story-slug}.test.ts
describe.skip('{story title}', () => {
  it('{AC-N.N description} @AC-N.N', async () => {
    // TODO: implement
  });
});
```

### Step 5b — Install CI gate
Copy `templates/ci.yml.template` → `.github/workflows/ci.yml`. The shipped template runs on every PR:
- `actions/checkout@v4` + `actions/setup-node@v4` (Node 22, npm cache)
- `npm ci` (fail if lockfile drift)
- `npm run lint`
- `npm run test` (soft fail until 100% AC coverage — uses `|| echo` on early projects)
- `npm run build`
- `npm audit --audit-level=high` (fail on high+ CVEs)

Without this, the first PR silently skips quality gates and students don't learn CI discipline. Mandatory.

### Step 6 — Seed .claude/lessons.md
```markdown
# Lessons — {ProjectName}

Last pruned: {today}

## Active lessons

None yet. First lesson will be captured on the first score < 90 or first bug.

## Archived lessons

None.
```

### Step 6b — Seed `_dev-progress.md`
Copy `templates/_dev-progress.md.template` → `_dev-progress.md` at project root. Fill one row per BRD story from `architecture/brd.md`; all statuses start `⬜ not started`. This is the tracker `/eo-guide` reads on every session to answer "where am I, what's next?" The filesystem is the source of truth; this file is a view that `/eo-guide` reconciles.

### Step 7 — Install SessionStart hook
Copy `templates/settings.json.template` → `.claude/settings.json` and `templates/lessons.md.template` → `.claude/lessons.md`. Both ship with this plugin.

### Step 8 — Generate .env.example
Extract every env var referenced in `tech-stack-decision.md`. Write to `.env.example` with placeholders, never real values.

### Step 9 — First commit
```bash
git add .
git commit -m "feat: initial handoff from EO-Brain

- CLAUDE.md calibrated for {project}
- BRD with {N} acceptance criteria
- Placeholder tests tagged @AC-N.N
- .claude/lessons.md seeded
"
```

### Step 10 — Print next-step banner
```
✅ Handoff complete. You're Claude Code ready.

Next steps:
  1. cd {ProjectName}
  2. Open in Claude Code: claude
  3. Run: /eo-plan
  4. Start sprint 1 from architecture/technical-roadmap.md

Your first score gate: 90 composite or no ship.
```

---

## Quality checks (before declaring handoff done) — HANDOVER READINESS 9/9

- [ ] Global playbook precondition passed (Step 0)
- [ ] `CLAUDE.md` ≤ 150 lines (Boris discipline) with global-precedence note
- [ ] BRD has ≥3 ACs per user story
- [ ] Every AC has a `.skip` test with matching `@AC-N.N` tag
- [ ] `.github/workflows/ci.yml` present and valid YAML (Step 5b)
- [ ] `_dev-progress.md` present with one row per BRD story (Step 6b)
- [ ] `.gitignore` excludes `.env.local`, `node_modules/`, `.next/`
- [ ] `.env.example` has NO real secrets
- [ ] First commit lands on `main` or `dev`

All 9 checks green = HANDOVER READINESS 9/9. Anything red → fix before handing to student.

---

## Integration

- **Runs after:** EO-Brain Phase 5 complete
- **Runs before:** Any `/eo-*` command
- **Triggers:** Nothing (one-shot at project birth)
- **Consumed by:** every subsequent skill (lessons, scorer, traceability all expect this structure)

---

## Anti-patterns

- **Running without BRD:** Don't bridge a project that doesn't have a BRD. Return to EO-Brain.
- **Skipping placeholder tests:** The `.skip` stubs are the contract. Without them, brd-traceability has nothing to check.
- **Copying smorch-dev-scoring patterns:** This plugin is standalone. Don't pull from smorch-brain.
- **CLAUDE.md bloat:** If you're over 150 lines, remove generic advice. Keep only project-specific rules.
