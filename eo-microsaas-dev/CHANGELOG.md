# Changelog — eo-microsaas-dev

All notable changes to this plugin are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/) · versioning: [SemVer](https://semver.org/).

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
