# Changelog — eo-microsaas-dev

All notable changes to this plugin are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/) · versioning: [SemVer](https://semver.org/).

---

## [1.4.5] — 2026-04-29

### Added

- **L3 cascade parity** — companion release to `smorch-dev` v1.5.0. Wires two new plan-mode helpers and a debug-time investigator into the existing chain:
  - **`plan-eng-review`** + **`plan-design-review`** added to `/2-eo-dev-plan` (engineering + design pre-review during plan, surfaces architectural risks before TDD starts).
  - **`gstack:investigate`** added to `/eo-debug` (evidence-based root-cause investigation; complements `superpowers:systematic-debugging`).
- v1.4.4's resilient parser, multi-hat scoring, country-aware payment routing, and auto-execute post-scaffold remain unchanged. v1.4.5 is purely additive at L3 (plumbing layer).

### Changed

- `eo-microsaas-dev/.claude-plugin/plugin.json` 1.4.4 → 1.4.5.

### Migration

No breaking changes. `claude plugin update eo-microsaas-dev@eo-microsaas-training` picks up the new plan-mode helpers + investigator. Restart Claude Code.

---

## [1.4.4] — 2026-04-28

Three real fuckups in v1.4.3 named, owned, fixed.

### Fixed

- **(#1) `/1-eo-dev-start` now self-scores the input.** v1.4.3 parsed cleanly but never showed a score. v1.4.4 plan-mode preview shows a 5-hat composite (Identity / Stack / BRD / UX / Compliance, 0-10 each, 0-100 composite) with per-hat bars, auto-bridge plan, and founder-action list. Goal stated explicitly: aim for 10/10 against what the input allows. Auto-bridges (carve tag inference, loop tag inference, SCOPE block injection) apply automatically. Remaining gaps surface as concrete founder actions with severity flags. Never blocks — bootstrap proceeds with what's shippable.
- **(#2) `handover-bridge` Step 10 now auto-executes the post-scaffold dev-environment work.** v1.4.3 ended with a checklist telling the founder to `cd`, `npm install`, edit `.env.local`, run `npm run dev`. That's broken for non-technical founders — defeats the entire purpose of the plugin. v1.4.4 actually runs all of it: `npm install` after scaffold; interactive `.env.local` build (prompts founder for each secret, uses MCPs where available — Supabase MCP fills `NEXT_PUBLIC_SUPABASE_*` automatically, etc.); `npm run db:migrate` if applicable; `npm run dev` in background; HTTP 200 verification on `localhost`; `open` the URL. Founder sees a running dev server URL + the next concrete command (`/2-eo-dev-plan story-1`) — not a TODO list.
- **(#3) Payment default is now Stripe-first for Stripe-supported countries.** v1.4.3 defaulted to Tap for any MENA flag, even for UAE founders where Stripe is supported, ships natively in SaaSfast, and handles subscriptions better than Tap. v1.4.4 extracts founder country from `profile-settings.md` (looks for "Based in Dubai" / "located in Riyadh" / etc.), then picks payment provider:
  - **Stripe-supported countries** (UAE, KSA, Bahrain, Kuwait + global) → **Stripe primary** (SaaSfast-native, best for subscriptions)
  - **Egypt** → PayTabs default
  - **Jordan / Qatar / Oman** → Tap default (Stripe not supported there)
  - **BRD names a single provider** → use it (BRD always wins over default)
  - **BRD names multiple providers** → primary = Stripe if Stripe-supported, fallbacks = the rest

### Added

- `parse_founder_country()` in the ingester — extracts ISO country code (`AE`/`SA`/`BH`/`KW`/`QA`/`OM`/`EG`/`JO`) from `profile-settings.md` + `founderprofile.md`. Pattern matching includes Arabic markers (الإمارات, السعودية, etc.) and English ones, with "Based in {City}" / "Located in {City}" tiebreakers heavily weighted.
- `pick_payment_default()` in the ingester — encapsulates the country-aware payment rule. Returns `(primary, fallbacks, rationale)` tuple. Rationale string is shown to the founder in plan-mode preview so the choice is auditable.
- `score_inputs()` in the ingester — 5-hat scoring with per-hat 0-10, composite 0-100, gap list with `auto_bridgeable` flag, and `verdict` banner (ship-grade / bridge-grade / below-gate / serious-gaps).
- `STRIPE_SUPPORTED_COUNTRIES` constant + `NON_STRIPE_FALLBACK` map at top of `parse.py` — single-source-of-truth for the country routing.

### Verified end-to-end against the real `10-EO-Brain-Starter-Kit Final/EO-Brain/`

```
Project: EO Oasis MENA  ·  Founder: Mamoun Alamouri  ·  Country: AE  ·  Language: ar

PAYMENT (v1.4.4 fix):
  Primary:    Stripe                          ← was Tap in v1.4.3
  Fallbacks:  ['Tap', 'HyperPay']
  Rationale:  founder in AE (Stripe-supported); Stripe primary (SaaSfast-native, best subscriptions)

INPUT QUALITY SCORE:
  COMPOSITE:  88/100
  identity   ██████████ 10/10
  stack      ██████████ 10/10
  brd        ████░░░░░░ 4/10  ← MVP missing 3 loops, surfaced as 1 founder action
  ux         ██████████ 10/10
  compliance ██████████ 10/10

AUTO-BRIDGES (3 — applied automatically): carve tag inference, loop tag inference, SCOPE block injection
FOUNDER ACTIONS (1): MVP missing [deploy, money, observability] — promote Story 6 (covers money), or accept partial MVP
```

Self-score against real EO-Brain: **10/10 gates green**.

### Versions

- `eo-microsaas-dev` 1.4.3 → 1.4.4
- Marketplace `eo-microsaas-training` 1.2.3 → 1.2.4

### Migration

No breaking changes. `claude plugin update eo-microsaas-dev@eo-microsaas-training` picks up the fixes. Restart Claude Code.

---

## [1.4.3] — 2026-04-28

**Resilient Bootstrap.** `/1-eo-dev-start` cannot fail on legitimate EO-Brain input. v1.4.2 had a hardcoded regex (`^## Story` h2-only) at Step 7 that rejected v2.7.0 architect output (which uses `### Story` h3 headers). That's the wrong shape for a tool that runs against 100s of student BRDs. v1.4.3 replaces the build-and-validate-then-reject pattern with parse-and-normalize-and-surface-gaps.

### Added

- **`eo-brain-ingester` skill** — single executable Python parser (`parse.py`, stdlib-only) that ingests any EO-Brain folder shape and returns a canonical `BrainStructure` JSON. Handles:
  - Story headers in any depth (h2, h3, h4) or no header at all
  - Carve tags missing → infers `[@WeekendMVP]` / `[@Phase2]` from story position, surfaces blocking question for founder approval
  - Loop tags missing → infers `[loop:X]` from title + AC content via weighted keyword scoring (title hits 3x, AC hits 1x, threshold ≥3)
  - `profile-settings.md` as prose ("IDENTITY\nMamoun Alamouri. Founder of EO Oasis MENA...") instead of key:value or YAML
  - Project name extraction with prefix-stripping ("Positioning — X" → "X") and multi-source fallback (profile-settings → bootstrap-prompt → companyprofile → BRD → positioning)
  - `_language-pref.md` missing → auto-detects Arabic vs English from BRD content
  - Arabic story headers (`قصَّة N`)
  - Bootstrap prompt as primary identity source when `5-CodeHandover/README.md` is present
  - 5 fixture EO-Brain folders + smoke test (`parse.py --self-test`) shipped under `skills/eo-brain-ingester/fixtures/`
- **`brd-normalizer` skill** — companion contract document for the parser's normalization layer. Defers to `parse.py` for execution.
- **`questions[]` array** in `BrainStructure` — surfaces every blocking gap (missing identity, untagged BRD, MVP loop coverage gap) as a founder-prompt with a sensible default + override hook. Plan-mode preview iterates through these before scaffold runs.
- **Self-test harness** at `skills/eo-brain-ingester/parse.py --self-test` — runs against all fixtures + asserts behavior. Exit 0 = all pass, exit 2 = any fail.

### Changed

- **`eo-dev-start` Step 7 rewritten.** No more rigid `^## Story` regex. Step 7 now invokes `python3 skills/eo-brain-ingester/parse.py "$EO_BRAIN" --pretty`, refuses **only** on the two genuine-failure cases (EO-Brain missing OR BRD zero ACs), surfaces every other gap as a blocking question.
- **`eo-dev-start` Step 8 removed.** Identity extraction logic moved into `parse.py`. Cleaner: one place, one parser, one canonical output.
- **`handover-bridge` Step 4 simplified.** Reads `BrainStructure` JSON + `answers.json` directly. No re-parsing of EO-Brain folder. Single source of truth.
- **Hard-refuse cases narrowed** from ~6 (in v1.4.2) to **2**: `eo-brain-missing` and `brd-empty`. All other shapes proceed with normalization + founder approval.

### Verified

Smoke-tested against the user's actual EO-Brain at `EO-MicroSaaS-Training/10-EO-Brain-Starter-Kit Final/EO-Brain/` (the BRD that v1.4.2 rejected with "0 ## Story headers"):
- ✅ Project name correctly extracted as **"EO Oasis MENA"** (was: "Positioning — EO Oasis" or "Untitled Project")
- ✅ Founder name correctly extracted as **"Mamoun Alamouri"** (was: "alamouri99" git fallback)
- ✅ Email from git config: `mamoun.alamouri99@gmail.com`
- ✅ Language: `ar` from `_language-pref.md`
- ✅ Stack: Next.js + Tailwind + Supabase + Tap + HyperPay + Stripe + Contabo, MENA + RTL flags both true
- ✅ BRD: 6 stories, 60 ACs, all parsed cleanly
- ✅ 3 blocking questions surfaced: carve approval (default `y`: stories 1-4 = MVP, 5-6 = Phase2), loop approval (default `y`: keyword-inferred per story), MVP loop gap (missing money/deploy/observability — option A: promote Story 6 which covers `money`)
- ✅ `refused: false` — bootstrap proceeds with founder review, not skill crash

### Audit findings on `eo-microsaas-os` (upstream architect side)

While shipping the dev plugin's resilient parser, audited the architect + handover skills for similar fragility. **Findings (not fixed in this release — follow-up):**

- `4-eo-tech-architect/references/validate-brd.sh` has **8 hard-refuse exit codes** (5-8 added in v2.7.0 enforce carve + loop coverage). Same brittle build-and-validate pattern that the dev plugin just removed. A founder editing `architecture/brd.md` post-bootstrap (legitimate use case) could trip these refusals.
- `4-eo-code-handover/SKILL.md` line 121: "Story numbers MUST match brd.md Story numbering exactly." Fragile coupling that breaks if founder renumbers stories.

The dev plugin's v1.4.3 parser **neutralizes** the architect's brittleness — whatever shape the architect produces, the dev plugin accepts. The bug-cascade-stops-here. Architect cleanup is a follow-up `eo-microsaas-os` v2.7.1 release.

### Migration

No breaking changes for active projects. Existing v1.4.2 cached BRDs continue to work. `claude plugin update eo-microsaas-dev@eo-microsaas-training` picks up the resilient parser. Restart Claude Code to load.

The 5 fixtures + `--self-test` mode ship with the plugin so future regressions get caught before reaching students.

### Versions

- `eo-microsaas-dev` 1.4.2 → 1.4.3
- Marketplace `eo-microsaas-training` 1.2.2 → 1.2.3

---

## [1.4.2] — 2026-04-27

Architectural cleanup. Numbered chain is now genuinely linear — only commands that fire in sequence carry numeric prefixes. `/8-eo-dev-repair` and `/9-eo-debug` were always lifecycle commands (fire out-of-band, not after `/7-eo-ship`); having them sit in the 1–10 range broke the founder's mental model. Now they live with the other utilities.

### Changed

- **Numbered chain is now 1–8, in order across the weekend.**
  - `/1-eo-dev-start` (Fri eve)
  - `/2-eo-dev-plan` → `/3-eo-code` → `/4-eo-review` → `/5-eo-score` (Sat)
  - `/6-eo-bridge-gaps` (conditional, Sun)
  - `/7-eo-ship` (Sun)
  - `/8-eo-retro` (after ship) — **renamed from `/10-eo-retro`**
- **Demoted to utilities (un-numbered, alphabetical):**
  - `/eo-dev-repair` — was `/8-eo-dev-repair`. Fires when scaffold is partial/drifted, no linear position.
  - `/eo-debug` — was `/9-eo-debug`. Fires when something breaks, no linear position.
- **Utilities now total 7 (alphabetical order in autocomplete):** `/eo-debug`, `/eo-dev-repair`, `/eo-freeze`, `/eo-github`, `/eo-guide`, `/eo-status`, `/eo-unfreeze`.
- **Total command count unchanged:** 15 (8 numbered + 7 utilities). No commands added or removed; only re-organized.
- **Plugin description rewritten** around the linear/utility split.
- **Marketplace bump:** `1.2.1` → `1.2.2`.

### Why

The original v1.4.0 spec called `/8-eo-dev-repair` / `/9-eo-debug` / `/10-eo-retro` "lifecycle, used less" and gave them numeric prefixes as a stable autocomplete sort key. Real-world test surfaced the smell: founders read `/1` → `/10` top-to-bottom and naturally assume "after I run `/7`, I run `/8`." That's wrong — `/8-eo-dev-repair` only fires if the scaffold is broken. The numbering implied a sequence that didn't exist for those two. Fixing it now while training docs are still being authored for v1.4.1 — cheaper than fixing later.

`/8-eo-retro` stays numbered because it genuinely **does** come last in time (after every ship). The `/8` slot is correct for it.

### Migration

- **Existing v1.4.1 projects:** zero code change required. The skill names (`eo-dev-repair`, `eo-debug`, `eo-retro` underneath the numeric command file names) didn't change — only the command file names and how they appear in autocomplete. Users running `claude plugin update eo-microsaas-dev@eo-microsaas-training` get the new layout on next session restart. Existing `_dev-progress.md` rows referencing `/8-eo-dev-repair` or `/10-eo-retro` in `Last command` columns still parse fine — they're just historical strings.
- **Existing scripts / lessons.md / docs that reference the old names:** these become historical. The new commands are just renames; behavior is identical. No re-bootstrap needed.
- **CHANGELOG entries from v1.4.0 / v1.4.1 are NOT rewritten** — they document the names as they existed at those releases (historical accuracy).

---

## [1.4.1] — 2026-04-26

Hotfix on top of 1.4.0. Smoke test surfaced a real gap: the SaaSfast mode picker decided silently from the BRD without asking the founder first. Founder agency comes before the heuristic.

### Fixed
- **`eo-dev-start` Step 8a — explicit `SaaSfast yes/no` question** is now asked on every bootstrap, in all cases. The BRD is no longer the sole input. Two answers:
  - `yes` → Step 8b heuristic picks `M1` / `M2` / `M3` from the BRD as before.
  - `no`  → `saasfast_mode` is locked to `M0`, Step 8b is skipped, and the scaffold uses `tech-stack-decision.md` directly with zero SaaSfast pieces pulled in.
  - Anything else → re-asks up to 3 times, then defaults to `yes` (the safest default — `M1` keeps the founder in control of frontend).
- **Plan-mode preview** now exposes the explicit `SaaSfast: yes | no` line above the mode line, so the founder can confirm both the choice and the recommended mode before scaffolding starts.
- **`handover-bridge` Step 4** now receives `saasfast_used` from `eo-dev-start` Step 8a and treats `saasfast_used=false` as a hard precedence rule — no M1/M2/M3 branch runs even if a stale `saasfast_mode` value is passed.

### Changed
- **`eo-dev-start` self-score: 16 → 17 checks.** New check #10: "SaaSfast yes/no asked explicitly — never inferred from BRD alone." Existing checks renumbered.
- **`eo-dev-start` skill version: 1.2 → 1.3.**
- **Marketplace description (`1.2.0` → `1.2.1`)** — explicitly mentions the `yes/no` question step.

### Migration — 1.4.0 → 1.4.1
No action needed. Existing 1.4.0 installs run `claude plugin update eo-microsaas-dev@eo-microsaas-training` and the next `/1-eo-dev-start` run picks up the explicit question. Projects already bootstrapped in 1.4.0 keep working — the question only fires on fresh bootstraps. If a 1.4.0 project picked the wrong mode silently, run `/8-eo-dev-repair` and the mode-consistency check now reads the recorded `saasfast_used` value instead of inferring.

---

## [1.4.0] — 2026-04-25

Weekend-shipment release. Recalibrates the plugin around one promise: a non-technical founder takes an EO-Brain package on Friday evening, builds through Saturday, and ships to production by Sunday night. Everything in this release supports that promise — visible sequence, hidden plumbing, lean defaults, CEO voice.

### Added
- **Numbered build chain 1–10** — every build command is now prefixed with its sequence number. `/1-eo-dev-start` → `/2-eo-dev-plan` → `/3-eo-code` → `/4-eo-review` → `/5-eo-score` → `/6-eo-bridge-gaps` → `/7-eo-ship`, plus lifecycle `/8-eo-dev-repair`, `/9-eo-debug`, `/10-eo-retro`. Utilities (`/eo-guide`, `/eo-status`, `/eo-github`) stay unnumbered. A non-technical founder can read the command palette top-to-bottom and know what to run next.
- **`/eo-freeze` + `/eo-unfreeze` edit-boundary helpers** — scope Claude's writes to one folder for the rest of the session. Wraps `gstack:freeze` / `gstack:unfreeze` when the `gstack` plugin is present; falls back to a session-local rule otherwise. Kills "Claude rewrote three files while fixing one button."
- **SaaSfast mode picker (M0–M3)** — `/1-eo-dev-start` Step 8b reads the BRD + ICP and picks exactly one mode:
  - **M0 — None** (not a web app)
  - **M1 — Backend-only** (directory / marketplace / content — default for ambiguous cases)
  - **M2 — Gate-only** (marketing + gated app)
  - **M3 — Core stack** (traditional SaaS)
  The decision is recorded at the top of `architecture/tech-stack-decision.md` and every downstream command reads and respects it.
- **Three new side-car SOPs** under `skills/eo-dev-start/`:
  - `SAASFAST-MODES.md` — the four modes, picking heuristic, per-mode scaffold subset, mode-switch discipline.
  - `PAYMENT-PROVIDER-SWAPS.md` — Tap / HyperPay / Moyasar / PayTabs / Stripe scaffold diffs, common interface, MENA defaults (Tap for Gulf, HyperPay for KSA-only, Stripe for global).
  - `EO-SPECIFIC-LAYER.md` — the 5 files scaffolded on top of M1/M2/M3 (founder-profile schema, MENA font + phone defaults, distribution skeletons, Supabase RLS policy templates).
- **`handover-bridge` Step 4b + Step 4c** — mode-aware scaffold and BRD post-process:
  - Step 4 branches on `saasfast_mode` + `payment_provider` passed from `eo-dev-start`. M0 scaffolds per raw stack; M1 is Next.js + backend-only; M2/M3 add SaaSfast frontend layers.
  - Step 4b installs the EO-specific layer on top of M1/M2/M3 from plugin templates.
  - Step 4c parses the copied BRD and injects two framing blocks: **Weekend MVP** (stories 1–4) and **v2 Phase** (stories 5+ with `[@Phase2]` tagging). Idempotent. `brd-traceability` skill honors the tag — Phase 2 ACs don't count against MVP shipment.
- **Self-scoring gates on `/7-eo-ship`, `/8-eo-dev-repair`, `/9-eo-debug`** — every "done" declaration re-invokes `eo-scorer`. No more shipping on a stale score or closing a bug without re-checking the affected AC:
  - `/7-eo-ship` — full 5-hat pass on HEAD. ≥ 90 ship; 80–89 bounce to `/6-eo-bridge-gaps`; < 80 refuse and route to `/2-eo-dev-plan`.
  - `/8-eo-dev-repair` — mode-consistency check + re-score affected story scope. ≥ 80 accepted; < 80 routes to `/3-eo-code`.
  - `/9-eo-debug` — re-score affected AC after fix + tests green. ≥ 80 closed; < 80 keeps bug open + flags follow-up.
- **Hidden plumbing wired into every numbered command** — gstack + superpowers skills preferred, internal fallbacks always present. Founder never sees "skill missing" errors. Per-command mapping documented under each command's "Hidden plumbing" section.
- **GitHub push step in `/7-eo-ship`** — remote-aware. Auto-invokes `eo-github` when no remote exists; asks once if `github_intent=local-only` still active.
- **Weekend cadence in `_dev-progress.md` template** — seeded with 7 rows (4 MVP + 3 v2 🧊 frozen). Phase column shows MVP vs v2 at a glance. Cadence table replaced (5-week sprint plan → Fri/Sat/Sun weekend plan).

### Changed
- **`CLAUDE.md.template`** — Voice § now enforces CEO-brief tone for every founder-facing artifact (`docs/qa-scores/`, `docs/handovers/`, `docs/retros/`, `_dev-progress.md`). No 5-hat composite tables visible, no `aria-invalid`, no "setSession fragility". Engineering detail lives under `docs/engineering/`. The hidden plumbing (gstack / superpowers / subagent names) stays hidden — the founder sees only the numbered chain + utilities.
- **`handover-bridge` quality checks 9/9 → 12/12** — adds mode-line-present, mode-consistent-scaffold, BRD blocks-present-when-story-count-over-4.
- **`eo-dev-start` self-score protocol 14 → 16** — adds mode-picked, payment-resolved.
- **Marketplace description (`1.1.0` → `1.2.0`)** — rewritten around weekend-shipment promise and full numbered chain.

### Migration — 1.3.x → 1.4.0

Existing projects keep working. New projects scaffold with the numbered chain and mode-aware layer.

- **Existing projects built on 1.3.x** continue to work. Their `docs/qa-scores/` / `docs/plans/` / commits reference the un-numbered chain and stay valid as history. Students can switch to numbered commands immediately — behavior is identical.
- **New projects** run `/1-eo-dev-start` — the mode picker runs at Step 8b, the BRD is post-processed at handover-bridge Step 4c, `_dev-progress.md` seeds 7 rows with 4 MVP + 3 v2 frozen.
- **Installing `gstack` or `superpowers` is optional.** If installed, their skills take over the matching steps. If not, internal fallbacks run. Founder never sees the difference.

---

## [1.3.1] — 2026-04-23

### Theme
**No stuck paths.** Every refuse path in the plugin now names a concrete next door. Behavior on happy paths is unchanged.

### Fixed
- **`eo-guide` state-machine short-circuit.** v1.3.0 fired `local-only-bootstrapped` before any sprint-loop phase, so local-only students who had been coding for weeks were perpetually told "keep building locally." v1.3.1 only fires that state when no plan files exist yet. Once `docs/plans/story-*.md` lands, sprint-loop phases advance normally with a `🔒 Still local (no git yet)` banner. Same treatment for `has_git=true AND has_remote=false` → `🔗 Git local, no remote yet` banner.
- **`eo-guide` new phase `ready-to-ship-local-only`.** Local-only students reaching score ≥ 90 now see "🎉 MVP ready to go public. Run `/eo-github` → pick create or point-existing" instead of falling through to inconsistent.
- **`eo-github` MCP-absent vs MCP-auth-failed split.** v1.3.0 refused identically for both. v1.3.1 Case A (absent) shows the install block; Case B (auth 401/403) shows PAT-specific remediation (regenerate, scopes, SSO, env var name). Two problems, two different fixes.
- **`eo-github` manual fallback escape hatch.** Student can reply "manual" to any MCP refuse; skill prints a complete text runbook (UI create → `git init` → `git remote add` → `git push` → Settings checklist) and exits with zero writes. Unblocks anyone whose MCP can't be fixed today.
- **`eo-github` slug collision retry loop (Mode 1).** Now retries up to 3 times with suggestions (`{slug}-2`, `{slug}-{year}`, `eo-{slug}`). After 3 collisions/invalid replies, refuses cleanly — no infinite prompt.
- **`eo-github` non-empty remote remediation clarity (Mode 2).** Now lists 4 labeled exits (A/B/C/D) describing real situations ("mine but unrelated" / "earlier state of this project" / "mistake, start over" / "force-push outside this skill").
- **`eo-github` rate-limit + race-condition handling (Step 6).** 429 reads `Retry-After` and exits cleanly. 422 on `create_repo` (race between precheck and create) re-fires the slug-collision loop instead of silently adopting. 403 secondary rate limit exits with 60-sec guidance.
- **`eo-github` actionable LICENSE guidance.** Evidence table now names MIT / Apache-2 / Proprietary with a one-line rationale each + GitHub UI path, instead of just "add one when ready."
- **`eo-github` 5xx / network-error handling.** Distinct from MCP-missing and MCP-auth-failed; retries once after 5 sec, then prints GitHubStatus / VPN / proxy check guidance.
- **`eo-dev-start` MCP-absent on options 1/2/4.** v1.3.0 refused with a one-line "install MCP first." v1.3.1 prints a full install block (settings.json snippet, PAT link + scopes, restart) and continues the bootstrap as `local-only` so the student isn't blocked.
- **`eo-dev-start` invalid-reply retry.** Anything other than 1/2/3/4 re-asks up to 3 times, then defaults to local-only with a note in evidence.

### Added
- **§10 "Stuck? Here's the exit" in `docs/OPERATOR-GUIDE-v1.3.md`** — 14 sub-sections, one per potential stuck state. Each has symptom → what to check → concrete exit.
- **§11 "What changed in v1.3.1" in operator guide.**
- **Stuck-state exits table in `eo-github` skill** — summary of every refuse path and its named exit.
- **`eo-guide` anti-patterns entry** on short-circuiting sprint-loop rows.
- **`eo-github` anti-patterns entries** on infinite retry loops, silent adoption after 422-race, rollback theater, conflating MCP-missing with MCP-auth-failed, and leaving any refuse path without a door.

### Self-score bumps
- `eo-guide`: 10 checks → 14 checks (adds row-3 guard, banner, ready-to-ship-local-only, exit-named).
- `eo-github`: 18 checks → 23 checks (adds MCP-Case-B, manual fallback, slug retry cap, 4-exit Mode 2, 429/422 taxonomy, exit-named).

### Non-changes (intentional)
- No new commands. No new skills. No new files.
- All v1.3.0 plugin registration stays identical.
- `.claude/project.json` still not created. Git config remains the single source of truth.

### Migration notes
No action needed. `/plugin update eo-microsaas-dev` picks up v1.3.1. Existing projects keep working identically — just with clearer doors when something goes wrong.

---

## [1.3.0] — 2026-04-23

### Added
- **`/eo-github` command + `eo-github` skill** — the only plugin surface allowed to create, wire, or audit a GitHub remote. Four modes:
  - **Mode 1 `create`** — creates a new private repo under the authenticated user, applies best-practices settings (squash-merge only, `has_wiki`/`has_projects`/`has_discussions` off, `delete_branch_on_merge` on, EO topics + labels), wires origin, pushes the first commit.
  - **Mode 2 `point-existing`** — validates an already-created empty repo is writable and empty, shows a settings-drift diff vs the best-practices matrix, wires origin, pushes. Offers `skip-settings` to keep the repo's current config.
  - **Mode 3 `guided`** — A/B/C menu for students who said "I don't know" in `/eo-dev-start`'s 4-option question. Routes into Mode 1 or Mode 2.
  - **Mode 4 `audit`** — reads current repo state via MCP, computes drift vs the best-practices matrix, prints a per-item `y/n` drift report. Runs automatically after first `/eo-ship` green CI to offer branch-protection activation.
- **MCP-only contract** — the skill requires `mcp__github__*` tools. No `gh` CLI fallback. Refuses cleanly with install remediation when MCP is missing. This keeps "the skill works" identical to "the skill works the way the student expects."
- **Plan-aware feature offering** — detects GitHub plan (free/pro/team/enterprise) once per session. Never offers plan-locked features (required reviewers, CODEOWNERS enforcement) on plans that would silently ignore them. Students on free plans see only features their plan can honor.
- **Branch strategy picked from collaborator count** — solo (≤1) → trunk-only (`main` only); team (≥2) → dual-branch (`main` production + `dev` integration). Plan preview shows the choice; student can override in the approval step.
- **Post-first-CI branch protection** — protection rules can't require status checks that have never run. The skill defers protection to after first `/eo-ship` green CI, then offers activation via `/eo-github audit`.
- **Naming rules enforced at slug sanitization** — lowercase-only, ASCII+hyphen, 3-60 chars, reserved-name rejection (`api`, `www`, `admin`, etc.), `eo-` prefix auto-applied when `mena_flag=true`. No silent renames — if a name fails validation, the student is prompted.
- **Issue labels preset** — `bug`, `enhancement`, `blocked`, `needs-info`, `mena`, `score-gap` (skips any already present; never renames existing labels).
- **Failure rollback with manifest** — every write tracked; mid-flight failure → roll back only writes from this invocation. Never auto-deletes a GitHub repo (destructive — student confirms manually).

### Changed
- **`/eo-dev-start` Step 9b** — adds the **one-question-four-options** GitHub intent gate. When no origin is mounted, asks: `1. Create new repo` / `2. Point to existing repo` / `3. Continue locally` / `4. I don't know`. Detects `mcp__github__*` MCP presence. Routes 1/2/4+MCP to `eo-github` after `handover-bridge`; option 3 or 4-without-MCP stays fully local (no git init, no remote). Step 10b wires the post-bridge skill invocation.
- **`handover-bridge` Step 3 + Step 9** — `git init` and first commit are now conditional on `github_intent`. For `local-only`, no git repo is initialized and no commit is made — students who chose option 3 stay fully local. For every other value, git init happens locally but `git remote add origin` is never run (`eo-github` owns that). `git push` is never invoked here.
- **`eo-guide` v1.3** — adds three new phase states:
  - `local-only-bootstrapped` — bootstrap complete, no `.git/` → "Keep building locally. When your MVP works end-to-end, run `/eo-github`."
  - `git-local-no-remote` — git initialized, no `remote.origin.url` → routes to `/eo-github`.
  - `ready-to-ship-but-no-remote` — score ≥ 90 but no remote → routes to `/eo-github` before `/eo-ship`.
  Mode 2 `/eo-status` dashboard now shows a Git row (local/remote/no-git). Two new filesystem signals scanned: `.git/` presence and `remote.origin.url`.
- **Plugin description + README** — command count 12→13, skill count 10→11. File layout updated.

### Architecture notes
- **Isolation of remote operations:** `/eo-dev-start` is cheap to retry; students can trial the bootstrap three times before "this is the one" without polluting GitHub. All remote writes live in one skill (`eo-github`) with one contract (MCP + plan-mode preview).
- **Single source of truth for GitHub status:** `git config --get remote.origin.url`. No new config file introduced — `.claude/project.json` was considered and rejected as unnecessary complexity.
- **The skill is the admin, the student is the CEO:** admin decisions (settings, branches, labels, topics) are made by the skill from best practices; every decision is previewed and approved before writing. Audit mode lets the student correct drift later without re-bootstrapping.

### Migration notes
- **Existing v1.2.0 students with already-wired remotes:** no change. `/eo-dev-start` detects the origin and skips the 4-option question; the existing URL is preserved.
- **Existing v1.2.0 students with local git but no remote:** `/eo-guide` will now surface `git-local-no-remote` and route to `/eo-github`. Run it when ready to push.
- **No breaking changes** for any command or skill. The 4-option question is additive — students with already-wired remotes never see it.

---

## [1.2.0] — 2026-04-23

### Added
- **`/eo-dev-start` command + skill** — one-shot bootstrap for fresh EO MicroSaaS projects.
  - Reads EO-Brain phases 0-4 (`1-ProjectBrain/`, `4-Architecture/`) as source of truth.
  - Worktree-aware workspace root resolution (`$GIT_WORK_TREE` → `git rev-parse --show-toplevel`, never `pwd`).
  - Scans 11 bootstrap signals, classifies state: `empty` | `partial` | `bootstrapped`.
  - Plan-mode gate before any write — previews every file + template source + expected bytes.
  - Routes `partial` → `/eo-dev-repair`, `bootstrapped` → `/eo-guide`. Refuses to re-bootstrap.
  - Invokes `handover-bridge` only on approval. Emits evidence table (bytes + line counts) on completion.
  - Bilingual (Arabic-first Gulf if `EO-Brain/_language-pref.md` = `ar`, English otherwise).
- **`/eo-dev-repair` command + skill** — surgical triage for partially-bootstrapped projects.
  - Classifies every missing signal into one of two classes:
    - **Silent-repair-safe** (regeneratable from templates): `CLAUDE.md`, `.claude/lessons.md`, `.claude/settings.json`, `_dev-progress.md`, `.github/workflows/ci.yml`, `.env.example`, `.gitignore`, placeholder tests, `docs/ux-reference/`, doc subdirs.
    - **Refuse-and-route** (must come from EO-Brain phases 0-4): `architecture/brd.md`, `architecture/tech-stack-decision.md`, `EO-Brain/1-ProjectBrain/{icp,brandvoice,positioning}.md`, EO-Brain itself.
  - **Hard contract:** mixed state (some silent-repair-safe + some refuse-and-route missing) → refuse all repair. Surface the root cause. Partial repair masks upstream gaps.
  - Plan-mode gate shows exact rebuild list before any write. Never overwrites existing files (lessons.md preserved if present).
  - Failure rollback: manifest written before first write; on any mid-flight failure, deletes only files this invocation created.
  - Commit message: `chore(repair): regenerate {list of files} via eo-dev-repair`.
- **`eo-guide` v1.2** — phase detector routes new states to new commands:
  - `pre-bootstrap` (truly empty project) → `/eo-dev-start` (supersedes the old "copy-paste Section 5 prompt" flow).
  - `bootstrap-incomplete` (partial state) → `/eo-dev-repair`.
  - Frontmatter + header version bumped 1.1 → 1.2.
- **Simplified `EO-Brain/5-CodeHandover/README.md` Section 5** — the 75-line bootstrap prompt is replaced with a one-line pointer: `/eo-dev-start`. Zero copy-paste friction.

### Changed
- Plugin description updated to reference 12 commands + 10 skills (was 8 commands + 7 skills).
- README file-layout diagram lists new commands/skills with v1.2.0 annotations.

### Architecture note
The new split cleanly separates concerns:
- `/eo-dev-start` = happy-path bootstrap (empty → ready).
- `/eo-dev-repair` = triage (partial → repaired or refused with remediation).
- `/eo-guide` = router (any state → next correct command).

This mirrors the smorch-dev pattern (`/smo-dev-start` → `/smo-dev-repair` → `/smo-dev-guide`) so engineers moving between EO and SMO see the same mental model.

### Migration notes
- **Existing v1.1.0 students:** `claude plugin update eo-microsaas-dev@eo-microsaas-training`. Bootstrapped projects are unaffected — `/eo-guide` continues to work. New projects use `/eo-dev-start` instead of the old copy-paste prompt.
- **Students mid-bootstrap:** if a previous Section-5-prompt run left the project partial, run `/eo-dev-repair` — it will triage and either silently complete or tell you exactly which EO-Brain phase to finish.
- **No breaking changes.** All prior commands and skills retain behavior.

---

## [1.1.0] — 2026-04-21

### Added
- **`eo-guide` skill** — returning-student phase detector + next-command router. Reads filesystem state (10 signals), infers phase, recommends next `/eo-*` command. Worktree-aware. Bilingual output (Gulf Arabic if `MENA: yes` / `lang: ar` in project CLAUDE.md). Safety rail: never recommends `/eo-ship` when state is inconsistent.
- **`/eo-guide` command** — Mode 1 full recommendation.
- **`/eo-status` command** — Mode 2 compact dashboard (status only, no coaching).
- **handover-bridge hardening**:
  - Step 0 precondition — aborts if `~/.claude/CLAUDE.md` or `~/.claude/settings.json` missing.
  - Step 5b — generates `.github/workflows/ci.yml` from new template.
  - Step 6b — seeds `_dev-progress.md` with one row per BRD story.
  - Quality checks extended to **HANDOVER READINESS 9/9**.
- **Templates:**
  - `templates/ci.yml.template` — Node 22 PR gate (lint + test + build + `npm audit --audit-level=high`).
  - `templates/_dev-progress.md.template` — story tracker with status legend + MVP cadence reference.
- **`_dev-progress.md` dual-writer pattern** — every `/eo-*` command that touches story state now updates its row:
  - `/eo-plan` → status `📝 planned`
  - `/eo-code` → status `🔨 coding` / `🧪 scoring`, tests passing/total
  - `/eo-score` → composite score, status gate
  - `/eo-bridge-gaps` → status `🩹 bridging gaps`, hat bridged
  - `/eo-ship` → status `✅ shipped`, date, commit sha
  - `/eo-retro` → appends retro link to top-of-file metadata
- **`eo-guide/fixtures/README.md`** — 8-fixture catalog (01-pre-bootstrap through 08-inconsistent) for manual regression.

### Changed
- `handover-bridge` Output Contract now requires `.github/workflows/ci.yml` and `_dev-progress.md` at project root.
- Student-facing ship gate clarified: only `/eo-ship` can set `Status = ✅ shipped`. `/eo-score` at 90+ sets `🧪 scoring` (waiting to ship).

### Migration notes
- **Existing v1.0.0 students:** `claude plugin update eo-microsaas-dev@eo-microsaas-training`. No action required on existing projects — `_dev-progress.md` is optional for already-shipped stories; `/eo-guide` will seed it on first invocation if missing.
- **Fresh installs:** `install.sh` at the training-repo root picks up 1.1.0 automatically via marketplace.
- **No breaking changes.** Commands and skills retain prior behavior; new skill + templates are additive.

### Known follow-ups (not in this release)
- Windows PowerShell hooks (`destructive-blocker.ps1`, `secret-scanner.ps1`) — tracked under `templates/hooks-windows/`.
- Automated fixture test harness — fixtures ship as manual-regression only for 1.1.0.

---

## [1.0.0] — 2026-04-19

### Added
- Initial release.
- 8 slash commands: `/eo-plan`, `/eo-code`, `/eo-review`, `/eo-score`, `/eo-bridge-gaps`, `/eo-ship`, `/eo-debug`, `/eo-retro`.
- 7 skills: `eo-scorer`, `lessons-manager`, `brd-traceability`, `elegance-pause`, `arabic-rtl-checker`, `mena-mobile-check`, `handover-bridge`.
- 5-Hat scoring rubric (Product, Architecture, Engineering, QA, UX) with student calibration — 90+ composite ship gate.
- Self-improvement loop via `.claude/lessons.md`.
- MENA-specific checks: Arabic RTL rendering, 375px mobile viewport.
- BRD traceability via `@AC-N.N` tags.
