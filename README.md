# EO MicroSaaS Student — Claude Code Setup

> **Version:** 2.0 (2026-04-19)
> **Who this is for:** EO MicroSaaS students — solo founders building your first MicroSaaS
> **Status:** standalone (no SMOrchestra infrastructure dependencies)

## What this folder is

A self-contained bundle a student can clone, run `bash install.sh`, and get a Claude Code setup that ships 9.5+ quality code solo.

You are NOT part of the SMOrchestra team. This assumes:
- Your own GitHub account (free tier is fine)
- Your own Supabase / Vercel / Netlify accounts
- Your own API keys for anything you integrate
- No SMOrchestra server access, no Tailscale mesh, no shared credentials

You work solo. Everything runs on your laptop + your own cloud accounts.

---

## One-command install (curl | bash)

```bash
curl -sSL https://raw.githubusercontent.com/smorchestraai-code/eo-microsaas-training/main/install.sh | bash
```

Or clone + run:

```bash
git clone https://github.com/smorchestraai-code/eo-microsaas-training.git
cd eo-microsaas-training
bash install.sh
```

The script installs: Node 22, Bun 1.3+, Claude Code, gh CLI, gstack, superpowers, an eo-quality-guide skill (your 5-question scorecard), the student-tuned hooks, and copies the CLAUDE.md globally.

Run time: ~15 minutes active + ~45 minutes waiting on downloads.

---

## What's in this folder

```
EO-Students/
  README.md             ← You are here
  CLAUDE.md             ← Gets copied to ~/.claude/CLAUDE.md during install
  settings.json         ← Gets copied to ~/.claude/settings.json (2 hooks: destructive + secret-scanner)
  install.sh            ← One-command setup script
  sops/                 ← Lightweight procedures for solo founders
  templates/            ← BRD, scorecard, deploy-checklist
  reference/            ← Extra context: the development workflow doc
```

---

## Verify after install

```bash
node --version      # v22.x
bun --version       # 1.3+
claude --version    # 2.1.100+
gh --version        # 2.x
ls ~/.claude/skills/  # gstack/ superpowers/ eo-quality-guide/
cat ~/.claude/CLAUDE.md | head -5  # should show EO MicroSaaS Student Playbook
```

Test that the hooks fire: open Claude Code, ask it to run a force-push command — it should refuse.

---

## Daily workflow (summary — full detail in CLAUDE.md)

For every feature:

1. **Plan** — write a BRD in `docs/BRD-[feature].md`
2. **TDD** — test first, implement, refactor (`superpowers:test-driven-development`)
3. **Self-review** — `gstack:/review` catches 80% of issues in 2 min
4. **Score** — 5-question scorecard (composite 90+ to ship; save to `docs/qa-scores/YYYY-MM-DD.md`)
5. **Fix gaps** if below 90
6. **PR** — conventional commits, BRD link + score in description
7. **CI** — GitHub Actions runs typecheck + lint + test + build + audit

Full flow and examples in `CLAUDE.md`.

---

## Role comparison (so you know where you fit)

| Aspect | You (student, solo) | SMOrchestra team |
|--------|:-------------------:|:----------------:|
| GitHub | Own free account | SMOrchestra-ai org |
| Infra | Your laptop + Vercel/Netlify | Contabo servers + Tailscale mesh |
| Skill suites | gstack + superpowers + eo-quality-guide (lightweight) | Same 3 + smorch-dev-scoring (internal) |
| Quality gate | 5-question scorecard (mental model) | 5-hat scoring + independent QA agent |
| CI gates | Basic (typecheck, lint, build, audit) | Full (Playwright, axe, Lighthouse, BRD trace) |
| Hooks | 2 (destructive + secret) | 7 (full dev) |

You can level up to SMOrchestra-standard quality over time — the patterns are the same, just scaled up.

---

## Upgrading

- Claude Code: `npm update -g @anthropic-ai/claude-code` monthly
- gstack: `cd ~/.claude/skills/gstack && git pull && ./setup` monthly
- superpowers: `cd ~/.claude/skills/superpowers && git pull` monthly
- This playbook: check `https://github.com/SMOrchestra-ai/eo-mena/releases` for `playbook-v*` tags

---

## Support

- Community: EO Discord / Telegram (link in your onboarding email)
- Stuck > 90 min on a bug → ask in community, not Mamoun directly
- Security question (real — handling money or user PII) → ask directly

---

## Folder version

README: 1.0 · 2026-04-19
Paired with: CLAUDE.md v2.0, install.sh v1.0, settings.json v1.0
