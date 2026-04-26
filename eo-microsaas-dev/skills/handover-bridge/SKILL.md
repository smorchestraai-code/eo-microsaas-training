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

### Step 3 — Initialize git (conditional on `github_intent`)

`handover-bridge` accepts a `github_intent` parameter from `/1-eo-dev-start` Step 9b. Values:

| `github_intent` | Git init? | Remote? | First commit? |
|-----------------|-----------|---------|---------------|
| `create` | Yes | No (added later by `eo-github`) | Yes (see Step 9) |
| `point-existing` | Yes | No (added later by `eo-github`) | Yes |
| `guided` | Yes | No (added later by `eo-github`) | Yes |
| `already-wired` | Skip if `.git` exists; otherwise yes | Already present — do not touch | Yes |
| `local-only` | **No** | No | No — all scaffold stays uncommitted until student decides |

```bash
case "$github_intent" in
  create|point-existing|guided)
    if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
      cd {ProjectName}
      git init -b main
    fi
    ;;
  already-wired)
    # Remote is already set — leave remote alone.
    # If somehow no .git exists despite `already-wired` (shouldn't happen), init.
    git rev-parse --show-toplevel >/dev/null 2>&1 || git init -b main
    ;;
  local-only)
    # Do not initialize git. Skip the first-commit step too.
    ;;
esac
```

**Never** `git remote add origin` in this skill. That is `eo-github`'s job — it runs after handover-bridge completes when `github_intent ≠ local-only`. This keeps remote wiring plan-mode gated and MCP-verified.

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
for any UI work. `/2-eo-dev-plan` reads them when planning visual features.
`/4-eo-review` UX hat compares rendered components against these.

| Artifact | Covers BRD stories | What to match |
|----------|-------------------|---------------|
| product-demo.html | Story 1, Story 2 | Core workflow layout, primary CTAs, empty states |
| onboarding-flow.html | Story 3 | First-run screens, form fields, progress indicator |
| admin-dashboard.html | Story 5 | Data table layout, filter positions, bulk actions |
```

This is non-negotiable: a component shipped that doesn't match the artifact → UX hat Q1 drops to 6.

### Step 4 — Scaffold src/ per SaaSfast mode + tech stack

**Inputs (passed from `eo-dev-start` Step 10):** `saasfast_used` (true/false from Step 8a), `saasfast_mode` (M0/M1/M2/M3 from Step 8b), `payment_provider`, `stack`, `mena_flag`.

**Hard precedence rule:** `saasfast_used=false` always means M0 — scaffold raw stack from `tech-stack-decision.md`, pull in zero SaaSfast pieces. Do not run any M1/M2/M3 branch even if a stale `saasfast_mode` value was passed. The founder said no in Step 8a; respect it.

**Branch on mode** (only when `saasfast_used=true`) — see `../eo-dev-start/SAASFAST-MODES.md` for the full per-mode subset table.

#### M0 — No SaaSfast
Scaffold per `stack` only:
- CLI → `npx create-node-cli@latest` or minimal `package.json` + `src/index.ts`
- Static site → `npx create-astro@latest` or `src/` with HTML
- API-only → minimal Express/Fastify setup
- No payment, no email, no auth unless BRD calls for them

#### M1 — Backend-only (default for directory/marketplace/content)
```bash
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir
```
Then install only the backend subset of SaaSfast:
- `src/lib/supabase/` — auth + RLS helpers (copied from SaaSfast-ar source, never edited in-place there)
- `src/lib/payment/<provider>/` — per `payment_provider`, see `../eo-dev-start/PAYMENT-PROVIDER-SWAPS.md`
- `src/lib/email/` — Resend wrapper + SendGrid fallback
- `src/lib/i18n/` + `src/app/layout.tsx` RTL wiring when `mena_flag=true`

**Do NOT scaffold** SaaSfast's marketing pages, auth UI pages, or dashboard. Founder builds custom frontend.

#### M2 — Gate-only
Everything from M1, plus:
- `src/app/(marketing)/` — SaaSfast landing + pricing pages (edit in place, not upstream)
- `src/app/(auth)/` — SaaSfast auth pages
- `src/app/(app)/` — empty shell for custom app, middleware-gated

#### M3 — Core stack
Everything from M2, plus:
- `src/app/(app)/dashboard/` — SaaSfast dashboard shell
- `src/app/(app)/admin/` — SaaSfast admin shell
- `src/components/ui/` — full SaaSfast component library

**Record the decision** at the top of `$ROOT/architecture/tech-stack-decision.md`:

```
---
SaaSfast mode: {M0|M1|M2|M3} — {mode name}
Rationale: {one-line — why this mode for this product}
Payment provider: {provider}
Recorded: {date}
---
```

Every downstream command (`/2-eo-dev-plan`, `/3-eo-code`, `/8-eo-dev-repair`) reads this block.

### Step 4b — Install the EO-specific layer (M1/M2/M3 only; skip for M0)

See `../eo-dev-start/EO-SPECIFIC-LAYER.md` for the full contract. Copy the 5 template sets:

| Template source (inside this plugin) | Destination |
|--------------------------------------|-------------|
| `skills/eo-dev-start/eo-layer/founder-profile/` | `$ROOT/src/lib/founder-profile/` |
| `skills/eo-dev-start/eo-layer/mena-defaults/` | `$ROOT/src/lib/mena-defaults/` |
| `skills/eo-dev-start/eo-layer/distribution/` | `$ROOT/src/lib/distribution/` |
| `skills/eo-dev-start/eo-layer/supabase-policies/` | `$ROOT/supabase/policies/` |
| `skills/eo-dev-start/eo-layer/supabase-migrations/` | `$ROOT/supabase/migrations/` |

If a destination file already exists → refuse; exit; route to `/8-eo-dev-repair`. Never overwrite silently.

If the template directories don't yet exist in the plugin (early v1.4.0), degrade gracefully: print one line noting the layer will be added in a later release, continue scaffold. Do not block on missing EO-layer templates.

### Step 4c — BRD post-process: Weekend MVP + v2 roadmap blocks

After copying `architecture/brd.md` into the project, inject two framing blocks at the top if they are not already present.

**Parse** the BRD for stories:
- Count `## Story N` or `### Story N` headers → `story_count`.
- Identify stories tagged `[@Phase2]` in their header → `phase2_stories`.
- If no stories are tagged, heuristically mark stories 5+ as `phase2_stories` (and stories 1–4 as MVP).

**Prepend (only if not already present — idempotent):**

```markdown
> **Weekend MVP — Stories 1–{min(story_count, 4)}.**
> Ship the first {min(story_count, 4)} stories in one weekend. Email auth + one payment provider from this BRD. No SMS 2FA. No multi-tier pricing. No admin dashboard (Supabase Studio + Google Sheet until 50 customers).

> **v2 Phase — Stories {phase2_range}.**
> Everything tagged `[@Phase2]` in AC headers below is deferred. v2 entry point: `/2-eo-dev-plan story-{phase2_first}` after the MVP is live. The numbered chain continues without another bootstrap.
```

If `story_count ≤ 4` → inject only the Weekend MVP block; skip v2 block.
If the BRD already has either marker verbatim → do not duplicate. Idempotent re-runs are fine (handover-bridge is one-shot, but `/8-eo-dev-repair` re-runs this post-process).

**Tag ACs** deferred to v2: for each `phase2_stories`, append ` [@Phase2]` to every `AC-N.N` in that story if not already tagged. `brd-traceability` skill honors this tag when computing coverage — Phase 2 ACs don't count against MVP shipment.

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

### Step 9 — First commit (conditional on `github_intent`)

Skip entirely when `github_intent=local-only` (there's no git repo to commit to).

For every other value:
```bash
if git rev-parse --show-toplevel >/dev/null 2>&1; then
  git add .
  git commit -m "feat: initial handoff from EO-Brain

- CLAUDE.md calibrated for {project}
- BRD with {N} acceptance criteria
- Placeholder tests tagged @AC-N.N
- .claude/lessons.md seeded
"
fi
```

**Never push.** If the student chose `create` / `point-existing` / `guided`, `eo-github` will be invoked next (by `/1-eo-dev-start` Step 10b) and it owns the push. If the student chose `already-wired`, `/7-eo-ship` handles the first release push.

### Step 10 — Print next-step banner
```
✅ Handoff complete. You're Claude Code ready.

Next steps:
  1. cd {ProjectName}
  2. Open in Claude Code: claude
  3. Run: /2-eo-dev-plan
  4. Start sprint 1 from architecture/technical-roadmap.md

Your first score gate: 90 composite or no ship.
```

---

## Quality checks (before declaring handoff done) — HANDOVER READINESS 12/12

- [ ] Global playbook precondition passed (Step 0)
- [ ] `CLAUDE.md` ≤ 150 lines (Boris discipline) with global-precedence note
- [ ] BRD has ≥3 ACs per user story
- [ ] Every AC has a `.skip` test with matching `@AC-N.N` tag
- [ ] `.github/workflows/ci.yml` present and valid YAML (Step 5b)
- [ ] `_dev-progress.md` present with one row per BRD story (Step 6b)
- [ ] `.gitignore` excludes `.env.local`, `node_modules/`, `.next/`
- [ ] `.env.example` has NO real secrets
- [ ] First commit lands on `main` or `dev` **(skipped when `github_intent=local-only` — counts as pass)**
- [ ] `SaaSfast mode:` line present at top of `architecture/tech-stack-decision.md` (Step 4)
- [ ] Scaffolded subset matches the recorded mode (no cross-mode leakage — e.g. no dashboard shell in an M1 project)
- [ ] BRD has Weekend MVP block + v2 block (when `story_count > 4`) — Step 4c

All 12 checks green = HANDOVER READINESS 12/12. Anything red → fix before handing to student.

**Note:** for `github_intent=local-only` runs, the "first commit" check passes by virtue of the contract (no git repo → no commit required). All other 8 checks still apply.

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
- **Adding a remote here:** `git remote add origin` is `eo-github`'s exclusive responsibility. Never set it in handover-bridge — that bypasses the plan-mode gate.
- **Committing when `github_intent=local-only`:** No git repo exists. Creating one without the student asking undermines the "continue locally" choice.
- **Pushing anything:** handover-bridge makes the first **local** commit only. Network operations belong to `eo-github` and `/7-eo-ship`.
- **Scaffolding across modes:** An M1 project never gets SaaSfast's dashboard shell. Mode is the contract. Break it only via explicit `/8-eo-dev-repair` after the mode line in `tech-stack-decision.md` is updated.
- **Editing SaaSfast-ar source:** Never. Copy the subset per mode into the project. Upstream stays pristine.
- **Duplicating the BRD blocks:** Step 4c is idempotent. If the Weekend MVP / v2 markers are already present (student may have hand-authored them in EO-Brain), do not duplicate.
