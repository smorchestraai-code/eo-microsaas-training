# Changelog — eo-microsaas-dev

All notable changes to this plugin are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/) · versioning: [SemVer](https://semver.org/).

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
