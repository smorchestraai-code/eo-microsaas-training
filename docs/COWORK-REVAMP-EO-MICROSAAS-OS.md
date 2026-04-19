# Cowork Revamp Guide — eo-microsaas-os Plugin

**For:** Cowork team maintaining the `eo-microsaas-os` plugin (EO-Brain student flow)
**From:** SMOrchestra / EO team
**Date:** 2026-04-19
**Scope:** Two skills — `4-eo-tech-architect` and `4-eo-code-handover`
**Why:** Align EO-Brain Phase 4 output with the new `eo-microsaas-dev` Claude Code plugin. Without this alignment, students hit a dead wall when they switch from EO-Brain → Claude Code.

---

## Context in 60 seconds

We built a new Claude Code plugin (`eo-microsaas-dev`, v1.0.0-pilot) that students install after EO-Brain finishes. It has 8 slash commands (`/eo-plan`, `/eo-code`, `/eo-review`, `/eo-score`, `/eo-bridge-gaps`, `/eo-ship`, `/eo-debug`, `/eo-retro`) and a 5-hat scoring gate (90+ composite to ship).

It expects specific file formats coming out of EO-Brain. Current `eo-microsaas-os` Phase 4 output doesn't match — two small but critical gaps.

**Plugin source:** `github.com/smorchestraai-code/eo-microsaas-training/tree/main/eo-microsaas-dev`

---

## Gap 1 — BRD acceptance criteria must be tagged

### What we need

Every user story in `architecture/brd.md` must have numbered acceptance criteria in this exact format:

```markdown
## Story 1: Password Reset

**As a** logged-out founder
**I want to** reset my password via email
**So that** I can regain access if I forget it

### Acceptance Criteria
- **AC-1.1** User enters email, receives reset link within 60 seconds
- **AC-1.2** Link expires after 1 hour
- **AC-1.3** Password must be ≥8 chars with 1 number
- **AC-1.4** Success page shows login CTA
```

**The tag pattern `AC-{story}.{criterion}` is the contract.** The new plugin greps for `AC-N.N` and expects matching `@AC-N.N` tagged tests later.

### What to change in `skills/4-eo-tech-architect/SKILL.md`

1. **BRD template section:** add a mandatory subsection titled "Acceptance Criteria Format" that enforces the `AC-N.N` pattern and rejects free-text ACs.
2. **BRD validation step:** before writing `brd.md`, validate every story has ≥3 numbered ACs. If not, prompt student to expand.
3. **Add a "traceability contract" note:** "Claude Code's `eo-microsaas-dev` plugin will grep for these AC codes. Shipping without them breaks the handoff."

### Exact text to add to the BRD template

```markdown
### Acceptance Criteria Format (MANDATORY)

Each criterion must be numbered as `AC-{story}.{criterion}`:
- Story 1 criteria: AC-1.1, AC-1.2, AC-1.3, ...
- Story 2 criteria: AC-2.1, AC-2.2, ...

Each criterion must be:
1. **Testable** (observable pass/fail, not "should be fast")
2. **Specific** (includes numbers, timeouts, states — not "works correctly")
3. **Independent** (doesn't require another AC to be true)

Bad: "AC-1.1 Login works"
Good: "AC-1.1 User with valid credentials redirects to /dashboard within 2 seconds"

Why this matters: The `eo-microsaas-dev` Claude Code plugin generates placeholder
tests tagged `@AC-1.1`, `@AC-1.2`, etc. from this document. Each AC = one test.
Without the tag format, test coverage tracking breaks.
```

### Validation check to add before writing `brd.md`

```javascript
// Pseudocode for the skill
const acPattern = /AC-\d+\.\d+/g;
const acsFound = brdDraft.match(acPattern) || [];
if (acsFound.length < 3) {
  ask('BRD has fewer than 3 acceptance criteria. Expand?');
}
// Also verify each story has at least 3 ACs tied to it
```

---

## Gap 2 — Code handover README must bootstrap the new plugin

### What we need

After EO-Brain Phase 4 completes, the student's `5-CodeHandover/README.md` should tell them to:

1. Install the `eo-microsaas-dev` plugin
2. Run the `handover-bridge` skill (packaged in that plugin) to convert EO-Brain output → Claude Code repo
3. Use `/eo-plan` as their first command, not a generic "start building"

Current README bootstrap prompt is too generic. It doesn't mention the plugin, doesn't reference the `handover-bridge` skill, doesn't set up the 5-hat gate expectation.

### What to change in `skills/4-eo-code-handover/SKILL.md`

Replace the bootstrap prompt section with this template:

```markdown
## Bootstrap prompt for Claude Code (first message)

Copy this into your Claude Code session on day 1:

---

I just finished the EO-Brain phases 0-4. My project context is in:
- `1-ProjectBrain/` — ICP, positioning, voice
- `2-GTM/output/` — GTM assets
- `4-Architecture/` — tech-stack-decision.md, brd.md, db-architecture.md, mcp-integration-plan.md

Please run the `handover-bridge` skill from the `eo-microsaas-dev` plugin to:
1. Verify all phase files are present
2. Scaffold the Claude Code project structure (src/, tests/, docs/, .claude/)
3. Generate placeholder tests tagged `@AC-N.N` from my BRD
4. Seed `.claude/lessons.md` and install the SessionStart hook
5. Create the first commit

After the bridge is complete, I'll run `/eo-plan` for my first feature.

My tech stack (from 4-Architecture/tech-stack-decision.md): [Next.js + Supabase + ...]
My ICP (from 1-ProjectBrain/): [MENA solo founders in X vertical]
My language: [Arabic-first / English-first / bilingual]

Non-negotiable quality gate: 5-hat composite score ≥ 90 before any PR merges.
```

### README setup-instructions section update

Replace the current "install Claude Code" paragraph with:

```markdown
## Day 1 setup (15 minutes)

1. Install Claude Code if not installed:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/smorchestraai-code/eo-microsaas-training/main/install.sh | bash
   ```

2. This installs:
   - Claude Code CLI
   - gstack plugin (Garry Tan's engineering workflow)
   - superpowers plugin (TDD, debugging)
   - **eo-microsaas-dev plugin** (7-pillar workflow, 5-hat scoring, MENA checks)

3. Verify commands load:
   ```bash
   cd {your-project-directory}
   claude
   # in Claude Code, type /eo — autocomplete should show /eo-plan, /eo-code, etc.
   ```

4. Copy the bootstrap prompt above into your first Claude message.

5. After handover-bridge completes, run `/eo-plan` with your first feature.
```

---

## Gap 3 (CRITICAL) — UX artifacts must land in a predictable location

### What we need

The `4-eo-code-handover` skill currently produces **3 interactive artifacts**:
- Product Demo (React/HTML mockup of core workflow)
- Onboarding Flow (first-run UX)
- Admin Dashboard (admin panel layout)

These are the **UX ground truth** the new `eo-microsaas-dev` plugin consumes. But there's no contract on WHERE they land. Our `handover-bridge` skill needs a predictable path to ingest them.

### The contract

Artifacts MUST be written to:

```
{ProjectName}/
  5-CodeHandover/
    artifacts/
      product-demo.html         (or .jsx)
      onboarding-flow.html      (or .jsx)
      admin-dashboard.html      (or .jsx — admin optional)
      ARTIFACT-INDEX.md         (maps each file → BRD story it covers)
```

### ARTIFACT-INDEX.md format

Each entry maps the artifact to the BRD stories it visualizes:

```markdown
# UX Artifacts — Index

| Artifact | Covers BRD stories | What it demonstrates |
|----------|-------------------|---------------------|
| product-demo.html | Story 1, Story 2 | Core workflow: form → process → result |
| onboarding-flow.html | Story 3 | First-run screens, 3-step wizard, progress bar |
| admin-dashboard.html | Story 5 | Data table, filters, bulk actions |
```

### What to change in `skills/4-eo-code-handover/SKILL.md`

1. Add a `## Artifact output contract` section with the exact path above
2. After generating each artifact, write it to `5-CodeHandover/artifacts/{kebab-name}.html`
3. After all artifacts written, generate `ARTIFACT-INDEX.md` mapping them to BRD story numbers (must match the `AC-N.N` numbering from the architect's BRD)
4. If student skips an artifact (e.g., no admin dashboard because no admin role), note it in ARTIFACT-INDEX.md as "N/A — rationale"

### Why this matters

Our `handover-bridge` copies these artifacts to `docs/ux-reference/` in the Claude Code project. Then:
- `/eo-plan` reads the artifact matching the feature being planned
- `/eo-review` compares the rendered component to the artifact
- `ux-hat` Q1 drops to 6 if the component doesn't match

Without a predictable path, this chain breaks and students lose the UX ground truth they just generated.

---

## Gap 4 (nice-to-have) — MENA defaults must mention the plugin's auto-checks

In `4-eo-tech-architect/SKILL.md` under "MENA-Specific Defaults", add:

```markdown
### Quality Auto-Checks (via eo-microsaas-dev plugin)

Any stack built for MENA will be auto-checked by the Claude Code plugin:
- `arabic-rtl-checker` — RTL layout, Cairo/Tajawal fonts, BiDi isolation
- `mena-mobile-check` — 375px viewport, AED/SAR/QAR/KWD currency format,
  Fri/Sat weekend, DD/MM/YYYY dates
- `brd-traceability` — every `AC-N.N` must have a tagged test

You don't need to manually list these in tech-stack-decision.md.
The plugin enforces them per-PR via the `/eo-score` UX hat (8 questions)
and Engineering hat (8 questions).
```

---

## Test plan for cowork after the revamp

Before releasing the revamped `eo-microsaas-os`:

1. **Dry run with a test student folder:** Run the full EO-Brain flow (phases 0-4) end-to-end
2. **Verify BRD output:** grep `architecture/brd.md` for `AC-\d+\.\d+` — should find ≥6 ACs across ≥2 stories
3. **Verify README bootstrap:** copy the bootstrap prompt into a Claude Code session, confirm it triggers `handover-bridge` skill correctly
4. **Run `handover-bridge`:** verify Steps 1-10 complete without errors (specifically Step 5 — placeholder test generation)
5. **Run `/eo-plan`** with a dummy feature: confirm BRD is read, ACs surface, plan mode enters

If any step fails, file an issue at `github.com/smorchestraai-code/eo-microsaas-training/issues` with the error + which phase broke.

---

## Versioning

Release the revamped `eo-microsaas-os` as **v2.3** (or whatever matches your semver) with changelog:

```markdown
## v2.3 (2026-MM-DD)

### Changed
- 4-eo-tech-architect: BRD template now enforces `AC-{story}.{criterion}` numbering (required by eo-microsaas-dev Claude Code plugin)
- 4-eo-code-handover: bootstrap prompt now references eo-microsaas-dev plugin + handover-bridge skill

### Added
- BRD validation step (fails if <3 numbered ACs)
- "Quality Auto-Checks" section in tech-stack-decision.md output

### Why
Students were hitting a dead wall when switching from EO-Brain → Claude Code. The new plugin expects specific BRD format; this revamp aligns output.
```

---

## Questions for cowork before starting

1. Is there a shared test-student folder we can use for the dry run? (or should we create one?)
2. Current `eo-microsaas-os` version — what's the latest tag?
3. Any student in a live cohort currently in Phase 4? (we'd want to freeze their flow, ship the revamp, then unfreeze)
4. Who on cowork side owns the BRD template — so we can align voice/tone?

---

## Contact

Ping Mamoun in the EO cowork Slack. Happy to pair-program on any of these changes over screenshare.
