# Changelog

All notable changes to this repo will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this
project follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Planned
- Course 01: MicroSaaS Fundamentals
- Example: mini-scorecard (Next.js + Supabase lead magnet)
- Example: arabic-landing-page (RTL layout reference)

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
