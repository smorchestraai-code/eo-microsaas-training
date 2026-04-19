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
