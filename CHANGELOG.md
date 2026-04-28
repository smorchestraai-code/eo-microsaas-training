# Changelog

All notable changes to this repo will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this
project follows [Semantic Versioning](https://semver.org/).

---

## [1.2.4] — 2026-04-28

### Fixed
- **`eo-microsaas-dev` plugin 1.4.4** — three real fuckups in v1.4.3 named + fixed:
  - **(#1) `/1-eo-dev-start` now self-scores the input** in plan-mode preview. Multi-hat (Identity / Stack / BRD / UX / Compliance), 0-100 composite, auto-bridge plan, founder-action list with severity. Aims for 10/10 against what the input allows.
  - **(#2) `handover-bridge` auto-executes the post-scaffold dev environment.** No more "next steps for founder to run." Plugin runs `npm install` + interactive `.env.local` build + `npm run dev` + HTTP 200 verify + opens the URL. Non-technical founders get a running dev server, not a checklist.
  - **(#3) Payment default is Stripe-first for Stripe-supported countries** (UAE, KSA, Bahrain, Kuwait). Was Tap for any MENA flag in v1.4.3 — wrong for UAE/KSA where Stripe is native to SaaSfast and better for subscriptions. New rule: extract founder country from `profile-settings.md`, route accordingly. BRD-explicit always wins.
- **Marketplace bump:** 1.2.3 → 1.2.4.

### Verified
- Real EO-Brain at `10-EO-Brain-Starter-Kit Final/EO-Brain/`: now extracts `AE` country, sets Stripe as primary (was Tap), shows composite 88/100 with 3 auto-bridges + 1 founder action surfaced. 10/10 self-score gates green.

### Migration
`claude plugin update eo-microsaas-dev@eo-microsaas-training`. Restart Claude Code.

---

## [1.2.3] — 2026-04-28

### Changed

- **`eo-microsaas-dev` plugin 1.4.3** — Resilient Bootstrap. `/1-eo-dev-start` cannot fail on legitimate EO-Brain input. v1.4.2's hardcoded `^## Story` regex (which rejected v2.7.0 architect output using `### Story` h3 headers) replaced with `eo-brain-ingester` skill — Python parser handling drifted headers, prose `profile-settings.md`, missing files, partial content, Arabic + English. Hard-refuse only on (a) EO-Brain missing or (b) BRD zero ACs. Every other gap surfaces as a blocking question for founder approval. 5 fixture EO-Brain folders + `--self-test` harness shipped. Verified end-to-end against `10-EO-Brain-Starter-Kit Final/EO-Brain/` (the case v1.4.2 rejected): now extracts "EO Oasis MENA" + "Mamoun Alamouri" cleanly, surfaces 3 blocking questions (carve approval, loop approval, MVP loop gap), proceeds without refusal. Full detail: `eo-microsaas-dev/CHANGELOG.md`.
- **Marketplace bump:** 1.2.2 → 1.2.3.

### Audit (not fixed this release)

- `eo-microsaas-os` (Cowork-side architect) has the **same brittle pattern** in `validate-brd.sh` (8 hard-refuse exit codes). Will be addressed in `eo-microsaas-os` v2.7.1 follow-up. The dev plugin's v1.4.3 parser neutralizes this — whatever the architect produces, the dev plugin accepts.

### Migration

`claude plugin update eo-microsaas-dev@eo-microsaas-training` picks up the resilient parser. Restart Claude Code.

---

## [1.2.2] — 2026-04-27

### Changed
- **`eo-microsaas-dev` plugin 1.4.2** — architectural cleanup. Numbered chain is now linear 1–8 (`/1-eo-dev-start` → `/8-eo-retro`). `/8-eo-dev-repair` + `/9-eo-debug` demoted to utilities and renamed to `/eo-dev-repair` + `/eo-debug` — they fire out-of-band, not in linear sequence. `/10-eo-retro` renamed to `/8-eo-retro` (genuinely last in time after every ship). Total commands unchanged (15 = 8 numbered + 7 utilities); only re-organized. Full detail: `eo-microsaas-dev/CHANGELOG.md`.
- **Marketplace bump:** `.claude-plugin/marketplace.json` metadata.version → 1.2.2. Plugin description rewritten around the linear/utility split.

### Migration
No breaking changes. `claude plugin update eo-microsaas-dev@eo-microsaas-training` picks up the rename. Restart Claude Code to load the new autocomplete layout.

---

## [Unreleased]

### Planned
- Course 01: MicroSaaS Fundamentals
- Example: mini-scorecard (Next.js + Supabase lead magnet)
- Example: arabic-landing-page (RTL layout reference)

---

## [1.2.1] — 2026-04-26

### Added
- **`eo-microsaas-dev` plugin 1.4.1** — hotfix. `/1-eo-dev-start` now asks the founder `SaaSfast: yes / no` explicitly on every bootstrap (Step 8a). The mode heuristic (Step 8b) only runs when the answer is yes; a `no` answer locks `M0` and pulls in zero SaaSfast pieces. Plan-mode preview exposes the answer above the recommended mode. `handover-bridge` honors a hard precedence rule: `saasfast_used=false` always means raw stack, regardless of any stale mode value. Full detail: `eo-microsaas-dev/CHANGELOG.md`.
- **Marketplace bump:** `.claude-plugin/marketplace.json` metadata.version → 1.2.1. Plugin description updated to mention the explicit yes/no question step.

### Changed
- No breaking changes. Existing 1.4.0 projects keep working. Fresh bootstraps in 1.4.1 see the explicit question. `claude plugin update eo-microsaas-dev@eo-microsaas-training` picks up the fix.

---

## [1.2.0] — 2026-04-25

### Added
- **`eo-microsaas-dev` plugin 1.4.0** — weekend-shipment release. Numbered build chain 1–10 (visible sequence for non-technical founders). `/eo-freeze` + `/eo-unfreeze` edit-boundary helpers. SaaSfast mode picker (M0–M3) wired into `/1-eo-dev-start` + `handover-bridge`. BRD post-process injects Weekend MVP + v2 Phase framing. Self-scoring gates on `/7-eo-ship`, `/8-eo-dev-repair`, `/9-eo-debug`. gstack + superpowers wired as invisible plumbing with graceful degrade. CEO-voice enforced in founder-facing artifacts. Full detail: `eo-microsaas-dev/CHANGELOG.md`.
- **Marketplace bump:** `.claude-plugin/marketplace.json` metadata.version → 1.2.0. Plugin description rewritten around the weekend-shipment promise + full numbered chain.

### Changed
- No breaking changes. Existing projects on 1.3.x keep working with the un-numbered chain in their history. New projects scaffold with the numbered chain + mode-aware layer.

---

## [1.1.0] — 2026-04-21

### Added
- **`eo-microsaas-dev` plugin 1.1.0** — adds `/eo-guide` + `/eo-status` for cross-session resumability, hardens `handover-bridge` to HANDOVER READINESS 9/9 (Step 0 precondition + Step 5b CI gate + Step 6b tracker seed), ships `_dev-progress.md` dual-writer pattern across 6 story-state commands, adds native Windows PowerShell hooks (destructive-blocker.ps1 + secret-scanner.ps1) backed by `hooks-shared/rules.json` single-source-of-truth blocklist. Full detail: `eo-microsaas-dev/CHANGELOG.md`.
- **Marketplace bump:** `.claude-plugin/marketplace.json` metadata.version → 1.1.0. Plugin description updated to reflect the 2 new commands.
- **`install.sh`:** banner updated to 1.1, command list now includes `/eo-guide` + `/eo-status`.
- **Pinned-install URL** in `README.md` now points at `v1.1.0` tag.

### Changed
- No breaking changes. Existing v1.0.0 students run `claude plugin update eo-microsaas-dev@eo-microsaas-training`; fresh installs via `install.sh` automatically pick up 1.1.0 via marketplace.

---

## [1.0.0] — 2026-04-19

### Added
- Initial release of the EO MicroSaaS Student setup bundle.
- `install.sh` — one-command bootstrap: installs Node 22, Bun, Claude Code, gh CLI; clones gstack + superpowers skill suites; creates `eo-quality-guide` skill; installs hooks + CLAUDE.md.
- `CLAUDE.md` — student playbook v2.0. Global Claude Code instructions covering workflow, rules, daily checklist.
- `settings.json` — Claude Code hooks (destructive-blocker + secret-scanner + SessionStart bootstrap).
- `sops/SOP-Quality-Scorecard.md` — 5-question self-scoring system.
- `sops/SOP-Git-Workflow.md` — branches, commits, conventional messages.
- `sops/SOP-Deployment.md` — Vercel / Netlify deploy guide.
- `templates/BRD-TEMPLATE.md` — write before coding.
- `templates/QA-SCORECARD-TEMPLATE.md` — save per PR.
- `templates/DEPLOY-CHECKLIST.md` — pre-flight every deploy.
- `reference/DEVELOPMENT-WORKFLOW-EXPLAINED.md` — the 7-step workflow explained.
- `docs/STRUCTURE.md` — how this repo is organized and where to add content.
- `CONTRIBUTING.md` — how to contribute courses, examples, SOPs.
- Placeholder `courses/` and `examples/` folders with READMEs describing planned content.

### Notes
- Standalone: zero SMOrchestra infrastructure dependencies.
- Works with free GitHub + Vercel/Netlify accounts.
- Repository lives at `smorchestraai-code/eo-microsaas-training` (user account, not SMOrchestra-ai org).
