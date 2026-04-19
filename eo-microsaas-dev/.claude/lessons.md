# Lessons — eo-microsaas-dev (the plugin itself)

Last pruned: 2026-04-19

## Active lessons

### L-001 — Don't self-score immediately after building
- **Captured:** 2026-04-19
- **Trigger:** Built 13 MD files back-to-back, called it ready. Actual 5-hat score was 60 (QA=3 because never loaded plugin in Claude Code). Classic inflation pattern.
- **Rule:** Any plugin or skill MUST pass a manual smoke test (commands resolve, files load) BEFORE first self-score. Don't score what you haven't run.
- **Check:** QA hat Q1 (happy path manually tested) — auto-fail if "never ran it manually" applies to the artifact being scored.
- **Last triggered:** 2026-04-19

### L-002 — Elegance pause is non-negotiable even on markdown-only PRs
- **Captured:** 2026-04-19
- **Trigger:** Wrote 6 skill SKILL.md files in a row with zero pause. Referenced `scripts/sync-skills.js` and `validate-skills-lock.js` that don't exist. Duplication between arabic-rtl-checker and mena-mobile-check on mobile rules.
- **Rule:** Every session producing >3 new files MUST trigger an elegance pause: "are these files consistent? any dead references? any duplication to collapse?"
- **Check:** Engineering hat Q6 (no dead code) applies to markdown references too.
- **Last triggered:** 2026-04-19

## Archived lessons

None.
