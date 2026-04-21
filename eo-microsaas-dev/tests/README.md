# eo-microsaas-dev tests

Shell-level regression tests for the plugin. Currently **manual** — run before cutting any release. When a test harness lands at the training-repo level, wire these in.

## Suites

| # | File | What it checks |
|---|------|----------------|
| 1 | `plugin-structure.sh` | `plugin.json` has no `commands[]` / `skills[]` arrays (L-008); all commands have frontmatter `description`; all skills have `SKILL.md`. |
| 2 | `claude-md-budget.sh` | Root `CLAUDE.md` ≤ 200 lines (student-facing, must stay readable). |
| 3 | `eo-guide-fixtures.sh` | For each tarball in `skills/eo-guide/fixtures/`, extract → run phase detector → diff against expected output in `fixtures/README.md`. |
| 4 | `handover-bridge-precondition.sh` | Run bridge in scratch dir with `HOME=/tmp/empty`; expect hard exit. Re-run with synthesized `~/.claude/CLAUDE.md`; expect pass through to Step 1. |

## Running

```bash
cd eo-microsaas-dev/tests
for t in *.sh; do echo "== $t =="; bash "$t" || echo "FAIL: $t"; done
```

All PASS → safe to bump version and publish.

## Not in scope (yet)

- CI automation. Run manually before release; automate when the plugin repo gets a `.github/workflows/plugin-ci.yml`.
- Windows coverage. Tests 1–4 are bash; PowerShell equivalents land with WS3 hooks.
