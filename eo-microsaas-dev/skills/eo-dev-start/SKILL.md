---
name: eo-dev-start
description: "First-run bootstrap for a fresh EO MicroSaaS project. Reads EO-Brain phases 0-4 from filesystem, classifies bootstrap state (empty | partial | bootstrapped), enters plan mode with approval gate, and invokes handover-bridge on approval. Never overwrites. Refuses and routes to /eo-dev-repair or /eo-guide when state is not empty. Triggers on: 'eo dev start', 'bootstrap project', 'set up claude code', 'first time', 'ابدأ المشروع'."
version: "1.3"
---

# eo-dev-start — First-Run Bootstrap

**Version:** 1.3 (2026-04-26 — Step 8a adds explicit `SaaSfast yes/no` question, never inferred from BRD; Step 8b heuristic now runs only when 8a returns `yes`. Founder agency comes first.)
**Previous:** 1.2 (2026-04-25 — SaaSfast mode picker M0-M3 added at Step 8b, payment auto-swap, handover-bridge passes mode + payment_provider). 1.1 (2026-04-23 — MCP-absent paths now print a concrete install block and continue as local-only instead of failing silently; invalid replies retry up to 3 times).
**Pillar:** EO-specific — the single entry point from EO-Brain strategy to Claude Code execution.
**Purpose:** Replace the 75-line copy-paste bootstrap prompt from `5-CodeHandover/README.md` with one command that reads EO-Brain output, previews exactly what it will create, waits for approval, then executes `handover-bridge` with parameters extracted from phases 0-4.

**Hard contract:** writes nothing without explicit student approval inside plan mode. Refuses on any non-empty state. Never decides repair (that's `/eo-dev-repair`'s job).

---

## Why this skill exists

The previous flow was: student copy-pastes a 75-line prompt that hardcodes project name, stack, ICP, deploy lane. Three failure modes:

1. **Hardcoded identity** — the template is for EO Oasis, not a reusable command. Every student edits by hand.
2. **No idempotency guard** — re-running overwrites `CLAUDE.md`, `.claude/lessons.md` silently.
3. **No repair vs. bootstrap split** — if something's partially wrong, the student doesn't know which command recovers.

This skill closes all three.

---

## Three states, three routes

### State A — `empty`
- Project folder has **no** `CLAUDE.md`, **no** `.claude/lessons.md`, **no** `architecture/brd.md`, **no** `src/`, **no** `_dev-progress.md`, **no** `.git/` history beyond initial commit.
- EO-Brain phases 0-4 are reachable (via symlink, sibling folder, or subfolder — see Step 2).
- **Route:** enter plan mode → preview → approve → bootstrap.

### State B — `partial`
- Any of the bootstrap files exists, but not all.
- **Route:** refuse. Print classified findings. Tell student to run `/eo-dev-repair`.
- This skill never decides repair. `/eo-dev-repair` owns that.

### State C — `bootstrapped`
- All of: `CLAUDE.md`, `.claude/lessons.md`, `architecture/brd.md`, `_dev-progress.md`, `.github/workflows/ci.yml`, and at least one `feat:` or `chore(bootstrap):` commit on `main` or `dev`.
- **Route:** refuse. Tell student to run `/eo-guide` for next step.

---

## Execution sequence

### Step 1 — Resolve workspace root

Worktree-aware:
```
if [ -n "$GIT_WORK_TREE" ]; then
  ROOT="$GIT_WORK_TREE"
elif git rev-parse --show-toplevel >/dev/null 2>&1; then
  ROOT="$(git rev-parse --show-toplevel)"
else
  ROOT="$PWD"  # greenfield — no git yet
fi
```

Never assume `pwd` is the repo root.

### Step 2 — Locate EO-Brain

Search in order (first match wins):
1. `$ROOT/EO-Brain/` (sibling inside project)
2. `$ROOT/../EO-Brain/` (sibling next to project)
3. `$ROOT/../../EO-MicroSaaS-Training/8-EO-Brain-Starter-Kit/EO-Brain/` (starter kit path)
4. Symlink `$ROOT/eo-brain` or `$ROOT/.eo-brain`

If none found → **refuse with remediation:**
```
❌ EO-Brain not reachable from {ROOT}.

Expected one of:
  {ROOT}/EO-Brain/
  {ROOT}/../EO-Brain/
  symlink {ROOT}/eo-brain

Remediation:
  1. Finish EO-Brain phases 0-4 in Cowork OR
  2. Symlink your existing EO-Brain folder:
       ln -s /path/to/EO-Brain {ROOT}/eo-brain

No writes made. Re-run /1-eo-dev-start after fixing.
```

### Step 3 — Detect language

Read `$EO_BRAIN/_language-pref.md` (set during EO-Brain Phase 0).
- `ar` → Arabic-first Gulf output, English tech terms mixed naturally. Not MSA.
- `en` → Direct English.
- Missing → ask once: "Arabic or English output? (ar/en)" — then write to `$EO_BRAIN/_language-pref.md` so this never asks again.

### Step 4 — Scan bootstrap signals

Collect these 11 signals in one filesystem pass (record `present/absent` + timestamp):

| # | Signal | Path | Meaning if present |
|---|--------|------|--------------------|
| 1 | CLAUDE.md | `$ROOT/CLAUDE.md` | Bootstrap attempted |
| 2 | Lessons | `$ROOT/.claude/lessons.md` | Self-improvement loop seeded |
| 3 | SessionStart hook | `$ROOT/.claude/settings.json` | Lessons auto-load on session |
| 4 | BRD | `$ROOT/architecture/brd.md` | Spec present |
| 5 | Tracker | `$ROOT/_dev-progress.md` | `/eo-guide` can read state |
| 6 | CI | `$ROOT/.github/workflows/ci.yml` | PR quality gate |
| 7 | src/ | `$ROOT/src/` or `$ROOT/app/` | Scaffold present |
| 8 | tests/ | `$ROOT/tests/` | Test skeletons present |
| 9 | UX reference | `$ROOT/docs/ux-reference/` | Artifacts ingested |
| 10 | .env.example | `$ROOT/.env.example` | Env contract present |
| 11 | First commit | `git log --oneline --all \| head -1` | History started |

### Step 5 — Classify state

- **empty** = signals 1, 2, 4, 5, 7, 11 all absent (no bootstrap artifacts at all)
- **bootstrapped** = signals 1, 2, 4, 5, 6 all present AND signal 11 shows a `feat:` or `chore(bootstrap):` commit
- **partial** = anything else

### Step 6 — Route by state

#### State C (bootstrapped) — refuse + route to `/eo-guide`

```
✅ Project is already bootstrapped.

Evidence:
  CLAUDE.md              — {size} bytes, {lines} lines
  architecture/brd.md    — {story_count} stories, {ac_count} ACs
  .claude/lessons.md     — {lesson_count} active lessons
  First commit           — {sha} "{subject}"

Next:
  /eo-guide              ← figures out what command you should run now
```

No writes. Exit.

#### State B (partial) — refuse + route to `/eo-dev-repair`

```
⚠️ Project is partially bootstrapped — /1-eo-dev-start does not handle this.

Signals present:
  {list of present signals with timestamps}

Signals missing:
  {list of absent signals}

Next:
  /eo-dev-repair         ← triages missing pieces and decides silent-repair vs refuse
```

No writes. Exit.

#### State A (empty) — proceed to plan mode

Continue to Step 7.

### Step 7 — Ingest EO-Brain via the resilient parser (NO regex validation)

**v1.4.3 — this step CANNOT FAIL on any legitimate EO-Brain input.** Hardcoded regex validation removed. Replaced with a single call to the `eo-brain-ingester` skill, which produces a structured `BrainStructure` JSON with identity, stack, BRD breakdown, and a `questions[]` array surfacing every blocking gap for founder approval.

#### Step 7a — Run the ingester

```bash
PARSE_OUT=$(python3 ${PLUGIN_PATH}/skills/eo-brain-ingester/parse.py "$EO_BRAIN" --pretty 2>&1)
EXIT=$?
```

#### Step 7b — Hard-refuse only on the two genuine-failure cases

```bash
if [[ $EXIT -eq 2 ]]; then
  reason=$(echo "$PARSE_OUT" | jq -r '.reason')
  remediation=$(echo "$PARSE_OUT" | jq -r '.remediation')
  echo "❌ Cannot bootstrap: $reason"
  echo "   $remediation"
  exit 2
fi
```

The ingester refuses on **only two** conditions (see `skills/eo-brain-ingester/SKILL.md`):
1. EO-Brain directory does not exist
2. BRD has zero `AC-N.N` tags (genuinely empty)

Every other shape — drifted headers, missing `[@WeekendMVP]` tags, prose `profile-settings.md`, missing `_language-pref.md`, partial UX artifacts — proceeds with normalization + blocking questions surfaced to the founder.

#### Step 7c — Surface blocking questions before plan-mode preview

The `BrainStructure` carries a `questions[]` array — every gap that needs founder input before scaffold can run. Iterate them; for each:

```bash
question_count=$(echo "$PARSE_OUT" | jq '.questions | length')
for i in $(seq 0 $((question_count - 1))); do
  prompt=$(echo "$PARSE_OUT" | jq -r ".questions[$i].prompt")
  default=$(echo "$PARSE_OUT" | jq -r ".questions[$i].default_suggestion")
  source=$(echo "$PARSE_OUT" | jq -r ".questions[$i].default_source")

  printf "\n%s\n" "$prompt"
  if [[ "$default" != "null" ]]; then
    printf "  (default: %s — source: %s)\n" "$default" "$source"
    printf "  Press Enter to accept, or type override: "
  else
    printf "  Required (no default): "
  fi
  read answer

  # Store answer keyed by question.key for handover-bridge consumption
  ANSWERS=$(echo "$ANSWERS" | jq --arg k "$(echo "$PARSE_OUT" | jq -r ".questions[$i].key")" \
                                  --arg v "${answer:-$default}" \
                                  '. + {($k): $v}')
done
```

Common question keys:
- `founder_name` — when profile-settings.md absent or unparseable
- `project_name` — when no source has a clean project name
- `carve_approval` — BRD missing `[@WeekendMVP]` / `[@Phase2]` tags; founder approves proposed carve
- `loop_approval` — BRD missing `[loop:X]` tags; founder approves keyword-inferred loops per story
- `mvp_loop_gap` — Weekend MVP slice missing one or more of the 7 loops; founder picks (A) move Phase2 story up, (B) accept gap, (C) return to Cowork

#### Step 7d — Read fields from the BrainStructure for plan-mode preview

```bash
project_name=$(echo "$PARSE_OUT" | jq -r '.identity.project_name')
founder_name=$(echo "$PARSE_OUT" | jq -r '.identity.founder_name')
founder_country=$(echo "$PARSE_OUT" | jq -r '.identity.founder_country')
language=$(echo "$PARSE_OUT" | jq -r '.language.lang')
stack_frontend=$(echo "$PARSE_OUT" | jq -r '.stack.frontend')
payment_primary=$(echo "$PARSE_OUT" | jq -r '.stack.payment_primary')
payment_rationale=$(echo "$PARSE_OUT" | jq -r '.stack.payment_rationale')
deploy_lane=$(echo "$PARSE_OUT" | jq -r '.stack.deploy_lane')
mena_flag=$(echo "$PARSE_OUT" | jq -r '.stack.mena')
story_count=$(echo "$PARSE_OUT" | jq -r '.brd.story_count')
ac_count=$(echo "$PARSE_OUT" | jq -r '.brd.total_acs')
warnings=$(echo "$PARSE_OUT" | jq -r '.warnings[]')
normalization_plan=$(echo "$PARSE_OUT" | jq -r '.brd.normalization_plan[]')

# v1.4.4: multi-hat input score + bridge plan
score_composite=$(echo "$PARSE_OUT" | jq -r '.score.composite')
score_verdict=$(echo "$PARSE_OUT" | jq -r '.score.verdict')
auto_bridges=$(echo "$PARSE_OUT" | jq -c '.score.auto_bridges')
founder_actions=$(echo "$PARSE_OUT" | jq -c '.score.founder_actions')
```

These feed Step 9's plan-mode preview. Founder approves the whole bootstrap (identity + carve + loops + normalization plan + bridge actions) in one gate.

#### Step 7e — Self-score the input + show bridge plan (the v1.4.4 fix)

The parser ALREADY scored the input (5-hat: Identity / Stack / BRD / UX / Compliance, 0-10 each, composite 0-100). The plugin's job in this step is:

1. **Show the score** in plan-mode preview — composite + per-hat breakdown
2. **Apply auto-bridges** automatically — these are safe normalizations (e.g. infer carve tags, infer loops, inject canonical SCOPE block) that the parser flagged as `auto_bridgeable: true`
3. **Surface founder actions** — gaps that require founder decision (move story up, add v2 story, switch deploy lane)
4. **Aim for 10/10 against what the input allows** — composite ≥ 90 is the ship-grade target. If input has unbridgeable gaps (e.g. genuinely missing UX artifacts), composite caps below 90 — that's surfaced honestly, scaffold proceeds anyway.

Print to founder:

```
═══════ INPUT QUALITY SCORE ═══════

  COMPOSITE: 88/100
  Verdict:   🟡 Bridge-grade. Auto-bridges + 1 founder action will lift to 92.

  identity     ██████████ 10/10
  stack        ██████████ 10/10
  brd          ████░░░░░░ 4/10
  ux           ██████████ 10/10
  compliance   ██████████ 10/10

AUTO-BRIDGES (applied automatically):
  • [brd] carve untagged → tag stories [1,2,3,4]=MVP, [5,6]=Phase2
  • [brd] loops untagged → infer from content (founder approves per-story)
  • [brd] SCOPE binary → inject canonical 3-block

FOUNDER ACTIONS (need decision):
  🔴 [brd] Weekend MVP missing loops: [deploy, money, observability]
       → promote Story 6 (covers money) into MVP, or accept partial MVP

After auto-bridges + your decisions, projected composite: 92/100 ✅
```

**Never block on score.** If composite is below 90, surface the gap, apply what's safe, let founder decide on the rest, scaffold proceeds. The goal is "10/10 against what the input allows," not "10/10 absolute."

### Step 8 — (REMOVED in v1.4.3 — identity extraction now lives in the ingester at Step 7a)

The Step 8 identity-extraction logic that lived here in v1.4.2 has moved into `skills/eo-brain-ingester/parse.py`. That parser handles:
- prose `profile-settings.md` ("IDENTITY\nMamoun Alamouri. Founder of EO Oasis MENA...")
- key:value `profile-settings.md`
- YAML frontmatter `profile-settings.md`
- BRD `**Product:**` line as project name source
- `companyprofile.md` h1 as project name source
- `positioning.md` h1 with prefix-strip (e.g. "Positioning — X" → "X")
- bootstrap-prompt.md `Name:` / `Founder:` / `ICP:` fields
- ICP from `icp.md` bullet list with markdown stripped
- voice rules from `brandvoice.md`
- git config `user.name` / `user.email` as fallback for founder identity
- blocking question generation when no source resolves a critical field

### Step 8a — Ask the founder: SaaSfast — yes or no?

**Always ask.** SaaSfast is the EO MicroSaaS starter kit. It is not the default stack. Some founders want to use it; some explicitly don't (learning exercise, different starter, custom build). The founder picks first — only then does the SOP decide *how* to use it.

Print exactly this (English template; Arabic analog when `lang=ar`):

```
🧰 Will this project use SaaSfast (the EO MicroSaaS starter kit)?

  yes — I'll read your BRD and recommend the right subset to pull in
        (auth, payment, landing, dashboard — only what fits).
        You stay in control of the rest.

  no  — Fully custom build. No SaaSfast pieces pulled in.
        I'll scaffold the raw stack from your tech-stack-decision.md.

Reply: yes / no
```

**Recording the answer:**
- `yes` → set `saasfast_used = true`. Continue to Step 8b — heuristic picks `M1` / `M2` / `M3`.
- `no` → set `saasfast_used = false`, `saasfast_mode = M0`. **Skip Step 8b.** Scaffold uses `tech-stack-decision.md` directly with no SaaSfast subset.
- Anything else → re-ask up to 3 times, then default to `yes` (safest — heuristic's `M1` ambiguous default still keeps the founder in control of frontend) and note `saasfast_mode_defaulted=true` in evidence.

The answer is recorded in the plan-mode preview (Step 9) and written to `architecture/tech-stack-decision.md` by `handover-bridge`. This question is **never** skipped, regardless of how clear the BRD signal looks. Founder agency comes first.

### Step 8b — Pick SaaSfast mode (M0–M3)

**Run only when Step 8a returned `yes`.** If Step 8a returned `no`, `saasfast_mode = M0` is already locked — skip this step.

SaaSfast is a toolkit, not a stack. Different products need different subsets. Read `SAASFAST-MODES.md` (side-car to this skill) and pick exactly one mode from M0–M3 based on the BRD + ICP.

**Heuristic (first match wins):**

| Signal in BRD / ICP | Mode |
|---------------------|------|
| Product is not a web app (CLI, internal-only, native mobile) | **M0 — None** |
| Keywords: `directory`, `marketplace`, `content site`, `catalog`, `AppSumo-style`, `landing + browse` | **M1 — Backend-only** |
| Distinct marketing pages + gated product behind auth | **M2 — Gate-only** |
| Standard SaaS loop (login → dashboard → features, tables, admin-heavy) | **M3 — Core stack** |
| Ambiguous | **M1 — Backend-only** (safe default: gets the boring stuff for free without boxing UX) |

**Payment auto-swap:**
- If BRD names a non-Stripe provider (Tap / HyperPay / Moyasar / PayTabs) → record `payment_provider=<name>`.
- If ICP region is MENA and provider is unnamed → record `payment_provider=tap` (default for Gulf).
- Otherwise → `payment_provider=stripe`.

See `PAYMENT-PROVIDER-SWAPS.md` for the per-provider scaffold diff.

**Record the decision** — will be written by `handover-bridge` to `$ROOT/architecture/tech-stack-decision.md` as:

```
SaaSfast mode: M1 — Backend-only
Rationale: BRD describes a directory product (AppSumo-style browse + filter). Frontend is custom; backend pulls auth + payment + email + i18n/RTL from SaaSfast.
Payment provider: tap (Gulf-first; stripe configured as intl fallback per BRD)
```

Every downstream command reads this line and respects the mode.

### Step 9 — Plan-mode preview (the approval gate)

Enter plan mode. Print exactly this (English template shown; Arabic analog when `lang=ar`):

```
📋 Bootstrap plan for: {project_name}

Source of truth: {EO_BRAIN path}

Will create:
  CLAUDE.md                  — ~{estimated_lines} lines, project-calibrated from template
  .claude/lessons.md         — empty, seeded with "First lesson captured on first score <90"
  .claude/settings.json      — SessionStart hook to auto-load lessons
  architecture/brd.md        — copied from EO-Brain
  architecture/*.md          — copied from 4-Architecture/
  docs/ux-reference/         — copied from 5-CodeHandover/artifacts/ ({artifact_count} files)
  docs/qa-scores/            — empty dir (score history)
  docs/handovers/            — empty dir
  docs/retros/               — empty dir
  src/                       — Next.js 14 App Router scaffold (TypeScript + Tailwind + RTL)
  tests/*.test.ts            — {ac_count} placeholder tests tagged @AC-N.N ({story_count} stories)
  .github/workflows/ci.yml   — PR quality gate (lint + test + build + audit)
  _dev-progress.md           — tracker row per story (⬜ not started)
  .env.example               — extracted from tech-stack-decision.md (no real secrets)
  .gitignore                 — .env.local, node_modules/, .next/, docs/secrets/
  README.md                  — project overview linking to EO-Brain
  First commit               — "chore(bootstrap): initial handoff from EO-Brain phases 0-4"

Identity applied:
  Project         {project_name}
  Founder         {founder_name} <{founder_email}>
  Stack           {stack}
  ICP             {icp_summary first 80 chars}
  MENA            {mena_flag}
  Deploy          {deploy_lane}
  Stories         {story_count}
  ACs             {ac_count}
  Language        {lang}
  SaaSfast        {yes | no}                    ← Step 8a answer (founder picked)
  SaaSfast mode   {mode_code} — {mode_name} ({one-line rationale})
                                                ← Step 8b heuristic, only when SaaSfast=yes
                                                ← M0 directly when SaaSfast=no
  Payment         {payment_provider}

Will NOT:
  - Overwrite any existing file at {ROOT}
  - Write real secrets anywhere
  - Skip the score gate (still ≥90 to ship, ≥8 per hat)
  - Run git push (you review + push manually after first commit)

Approve? (y/n)
```

On `n` → exit cleanly, no writes. On `y` → proceed to Step 9b.

### Step 9b — GitHub intent (CONDITIONAL on saasfast_used since v1.4.6)

Before handover-bridge runs, determine whether the bootstrap will include a GitHub remote.

**v1.4.6 conditional logic** — read the founder's `saasfast_used` answer from Step 7c (parser questions[]):

```
if saasfast_used == "yes":
  # GitHub is MANDATORY — SaaSfast-ar must be cloned to founder's repo.
  # Without GitHub at start, the cloned subset has no upstream destination.
  # Skip the 4-option question entirely.
  github_intent = "create"
  Print to founder:
    "🔗 SaaSfast=yes → GitHub repo required at start.
     SaaSfast-ar will be cloned + the right subset extracted into your repo.
     I'll create a private repo via /eo-github create."
  proceed to Step 10 (handover-bridge invocation, then auto-route to /eo-github)

if saasfast_used == "no":
  # Traditional 4-option flow — local-only allowed
  proceed to the precheck + 4-option question below
```

**Precheck (only when saasfast_used == "no"):**
```
git config --get remote.origin.url 2>/dev/null
```

If the output is non-empty → the student already wired a remote. Skip this step, record `github_intent=already-wired` for handover-bridge, proceed to Step 10.

If output is empty AND saasfast_used == "no" → ask one question:

```
📍 No GitHub remote mounted yet. How do you want to handle GitHub?

  1. Create a new private repo now
  2. Point to a repo I already created on GitHub (paste URL/owner/repo)
  3. Continue locally — no GitHub yet
  4. I don't know

(1/2/3/4):
```

**MCP detection:** inspect available tools in the current session for any `mcp__github__*` prefix. Record `github_mcp_present = true|false`.

**Route:**

| Answer | MCP | Next |
|--------|-----|------|
| `1` | present | Record `github_intent=create`. After Step 10 completes handover-bridge, invoke `eo-github` skill in `create` mode. |
| `1` | absent | Print the MCP-install block below, record `github_intent=local-only`, continue. Student can run `/eo-github create` later when MCP is ready. |
| `2` | present | Ask "Paste the URL or owner/repo:" → record `github_intent=point-existing` + `repo_ref`. After Step 10, invoke `eo-github` skill in `point-existing` mode. |
| `2` | absent | Same as 1+absent. |
| `3` | any | Record `github_intent=local-only`. Skip git init in handover-bridge. No remote. |
| `4` | present | Record `github_intent=guided`. After Step 10, invoke `eo-github` in `guided` mode. |
| `4` | absent | Print the MCP-install block below, record `github_intent=local-only`, continue. |
| anything else | any | Print: "Reply 1, 2, 3, or 4." Re-ask up to 3 times; after 3 invalid replies, default to option 3 (local-only) and note in evidence. |

**MCP-install block** (printed when MCP is absent and student picked 1, 2, or 4):

```
⚠️ You picked a GitHub path, but the GitHub MCP server isn't connected
yet. I'll continue locally so your bootstrap isn't blocked.

To enable GitHub later, add to ~/.claude/settings.json:

  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..." }
    }
  }

Create a PAT at https://github.com/settings/tokens (scopes: repo, read:org).
Restart Claude Code. Then run /eo-github when ready.

If you'd rather wire GitHub manually without MCP, /eo-github documents
a manual fallback (create in UI, then `git remote add` yourself).

For now: github_intent=local-only. Bootstrap continues.
```

Writes performed in this step: zero. Everything is just parameter capture for Step 10 and post-Step-10 routing.

### Step 10 — Invoke `handover-bridge`

Pass the identity fields from Step 8, the **`saasfast_used` from Step 8a**, the `saasfast_mode` + `payment_provider` from Step 8b (or the locked `M0` when 8a returned `no`), and `github_intent` from Step 9b to the `handover-bridge` skill. It uses `saasfast_used` + `saasfast_mode` to pick which scaffold subset to install (see `handover-bridge/SKILL.md` Step 4 — `saasfast_used=false` always means "raw stack, no SaaSfast"; `saasfast_used=true` branches on `saasfast_mode`), and `github_intent` to decide whether to `git init` + first commit (for `create`, `point-existing`, `guided`) or skip git entirely (for `local-only`).

Execute its 11-step sequence. If any step fails:
- Log the failure to `$ROOT/.bootstrap-failures.log`
- Attempt to roll back writes in that step only (not earlier steps)
- Exit with clear remediation

### Step 10b — Route to `eo-github` (conditional)

After `handover-bridge` returns success:
- `github_intent=create` → invoke `eo-github` skill, Mode 1. Skill owns plan-preview + approval + push.
- `github_intent=point-existing` → invoke `eo-github` skill, Mode 2 with `repo_ref`.
- `github_intent=guided` → invoke `eo-github` skill, Mode 3.
- `github_intent=local-only` → skip. Evidence table notes "No GitHub remote — run /eo-github later."
- `github_intent=already-wired` → skip. Evidence table shows the existing origin URL.

### Step 11 — Evidence table

After `handover-bridge` returns success, print evidence-based completion (never prose "done"):

```
✅ Bootstrap complete.

Files created:
  CLAUDE.md                  {lines} lines, {bytes} bytes
  .claude/lessons.md         {bytes} bytes (seeded)
  .claude/settings.json      {bytes} bytes (hook active)
  architecture/brd.md        {lines} lines, {story_count} stories, {ac_count} ACs
  _dev-progress.md           {story_count} tracker rows
  tests/*.test.ts            {file_count} files, {ac_count} @AC-N.N tags
  .github/workflows/ci.yml   {bytes} bytes
  docs/ux-reference/         {artifact_count} artifacts
  .env.example               {env_var_count} variables (no values)

Git:
  {if github_intent != local-only:}
  First commit: {sha} "chore(bootstrap): initial handoff from EO-Brain phases 0-4"
  Branch: {branch_name}
  {else:}
  No git repo initialized (github_intent=local-only)

GitHub:
  {if github_intent=create|point-existing|guided:}    eo-github skill completed — origin: {origin_url}
  {if github_intent=already-wired:}                   Existing origin preserved: {origin_url}
  {if github_intent=local-only:}                      No remote. Run /eo-github when your MVP is ready.

Next command:
  /2-eo-dev-plan Story-1-{first_story_slug}

Before you run it:
  - Skim CLAUDE.md (≤150 lines) — make sure it reflects your project
  - Skim architecture/brd.md — confirm all {ac_count} ACs are yours
  {if github_intent != local-only:} - First push happened via eo-github (or skipped if wiring failed — see output above)
```

---

## Anti-patterns

- **Never write outside plan-mode approval.** If the student says `n`, nothing lands.
- **Never overwrite.** If a file exists, refuse and route to `/eo-dev-repair`. Don't merge silently.
- **Never invent identity.** If EO-Brain is missing a required field, refuse with remediation. Don't ask the student to fill in what should have come from phases 0-4.
- **Never decide repair.** Partial state → `/eo-dev-repair`. Period.
- **Never skip language detection.** `lang=ar` students get Arabic output for the plan preview and evidence table.
- **Never create a GitHub repo silently.** The 4-option question in Step 9b is mandatory whenever no origin exists. All actual GitHub operations are delegated to `eo-github`.
- **Never `git init` when `github_intent=local-only`.** Students who choose option 3 stay fully local — no git, no remote. They can still use every other plugin feature.
- **Never `git push` from this skill.** Push is the exclusive responsibility of `eo-github` (on bootstrap) and `/7-eo-ship` (for releases).

---

## Integration

| Skill | Relationship |
|-------|--------------|
| `handover-bridge` | Invoked from Step 10 with `github_intent`. Scaffolds files; only runs `git init` + first commit when `github_intent ≠ local-only`. |
| `eo-github` | Invoked from Step 10b when `github_intent ∈ {create, point-existing, guided}`. Owns every remote-touching operation. |
| `eo-dev-repair` | Routed to when state is `partial`. Never called directly from here. |
| `eo-guide` | Routed to when state is `bootstrapped`. `eo-guide` also routes back here when it detects `pre-bootstrap` phase. Also surfaces `local-only-bootstrapped` state for students who chose option 3. |

---

## Self-score protocol

After every run, verify:

| # | Check | Threshold |
|---|-------|-----------|
| 1 | Workspace root resolved (worktree-aware) | must pass |
| 2 | Language detected from `_language-pref.md` or asked + saved | must pass |
| 3 | All 11 bootstrap signals scanned | must pass |
| 4 | State classified as exactly one of empty/partial/bootstrapped | must pass |
| 5 | EO-Brain completeness verified before plan mode | must pass |
| 6 | Plan-mode preview printed with identity fields | must pass |
| 7 | No writes before student approval | must pass |
| 8 | GitHub-intent question asked when no origin was already set | must pass |
| 9 | MCP presence detected (not assumed) before routing option 1/2/4 | must pass |
| 10 | **SaaSfast yes/no asked explicitly (Step 8a) — never inferred from BRD alone** | **must pass** |
| 11 | SaaSfast mode picked (M0–M3) + one-line rationale recorded — M0 directly when Step 8a returned `no`, otherwise heuristic on BRD | must pass |
| 12 | Payment provider resolved (Stripe or regional swap) from BRD or MENA default | must pass |
| 13 | `handover-bridge` invoked with extracted identity + `saasfast_used` + `saasfast_mode` + `payment_provider` + `github_intent` | must pass |
| 14 | `eo-github` invoked only when `github_intent ∈ {create, point-existing, guided}` | must pass |
| 15 | `local-only` path skipped git init entirely | must pass |
| 16 | Evidence table printed post-success with bytes + line counts | must pass |
| 17 | Next command recommendation cites first Story slug from BRD | must pass |

Threshold: 17/17. Below = bug → capture in `.claude/lessons.md`.
