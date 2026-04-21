# eo-guide Fixtures

Each fixture is a tarball snapshot of a project in one phase. Used for manual regression testing before releases.

## How to use

```bash
# Extract a fixture into a scratch dir
cd /tmp && mkdir eo-fixture-test && cd eo-fixture-test
tar -xzf ../eo-guide-fixtures/03-ready-to-plan.tar.gz
# Open in Claude Code
claude
# Run /eo-guide
# Compare output against "Expected output" below
```

Each fixture must produce the expected phase and next-command output. Divergence → the skill has regressed.

## Fixture catalog

| # | File | Phase | Expected next command | Expected ETA |
|---|------|-------|------------------------|--------------|
| 01 | `01-pre-bootstrap.tar.gz` | `pre-bootstrap` | Run the bootstrap prompt from `5-CodeHandover/README.md` | 15–20 min |
| 02 | `02-bootstrap-incomplete.tar.gz` | `bootstrap-incomplete` | Re-run `handover-bridge` — `.github/workflows/ci.yml` or `_dev-progress.md` missing | 5 min |
| 03 | `03-ready-to-plan.tar.gz` | `ready-to-plan` | `/eo-plan Story-1-signup` | 15 min |
| 04 | `04-ready-to-code.tar.gz` | `ready-to-code` | `/eo-code` | 45–90 min |
| 05 | `05-ready-to-score.tar.gz` | `ready-to-score` | `/eo-score` | 5 min |
| 06 | `06-bridging-gaps.tar.gz` | `bridging-gaps` | `/eo-bridge-gaps` | 30 min |
| 07 | `07-ready-to-ship.tar.gz` | `ready-to-ship` | `/eo-ship` | 10 min |
| 08 | `08-inconsistent.tar.gz` | `inconsistent` | Mode 3 diagnostic — NO ship recommendation | — |

## Building a fixture

1. Bootstrap a real project to the target phase.
2. Redact secrets from `.env.example` and strip `node_modules/`, `.next/`, `dist/`.
3. `tar -czf NN-<phase>.tar.gz <project-folder>`.
4. Add a row above with the expected output.

## Anti-patterns

- **Don't ship fixtures with real keys.** Use placeholder `.env.example`.
- **Don't check in the `.tar.gz` blobs unreviewed.** Review size + contents.
- **Don't drift fixtures from the skill.** When phase detection changes, update fixtures + expected output in the same PR.

## Not in scope (yet)

Automated test runner. For now: manual. When `tests/` harness exists at plugin level, wire fixtures into it.
