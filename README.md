# EO MicroSaaS Training

> **Version:** 1.1.0 (2026-04-21)
> **Status:** Active — accepting new content (courses, examples, SOPs)
> **License:** MIT
> **Repo:** https://github.com/smorchestraai-code/eo-microsaas-training

A complete Claude Code setup + training library for Entrepreneurs Oasis MicroSaaS students. One command installs everything a solo founder needs to ship production-grade MENA-focused MicroSaaS on their own laptop, using their own GitHub and Vercel/Netlify accounts.

**Standalone:** zero SMOrchestra infrastructure dependencies.

---

## One-command install (curl | bash)

```bash
curl -sSL https://raw.githubusercontent.com/smorchestraai-code/eo-microsaas-training/main/install.sh | bash
```

What gets installed:

- **Node.js 22, Bun, Claude Code, gh CLI** (via Homebrew on macOS, apt on Linux)
- **Skill suites** at `~/.claude/skills/`:
  - `gstack` — engineering workflow (/review, /ship, /qa, /investigate, /design-review)
  - `superpowers` — TDD, systematic debugging, brainstorming
  - `eo-quality-guide` — lightweight 5-question scorecard
- **Claude Code hooks** at `~/.claude/settings.json`:
  - destructive-blocker — prevents `rm -rf /`, force push, hard reset, DROP TABLE
  - secret-scanner — blocks real API keys from being written to non-env files
- **CLAUDE.md** at `~/.claude/CLAUDE.md` — your global playbook

Run time: ~15 min active + ~45 min waiting on downloads.

---

## Or clone + run manually

```bash
git clone https://github.com/smorchestraai-code/eo-microsaas-training.git
cd eo-microsaas-training
bash install.sh
```

---

## What's in this repo

```
eo-microsaas-training/
├── README.md                  ← you are here
├── install.sh                 ← one-command installer
├── CLAUDE.md                  ← student playbook (installed to ~/.claude/CLAUDE.md)
├── settings.json              ← hooks (installed to ~/.claude/settings.json)
├── CHANGELOG.md               ← version history
├── CONTRIBUTING.md            ← how to add courses, examples, SOPs
├── LICENSE                    ← MIT
│
├── sops/                      ← Standard Operating Procedures
│   ├── SOP-Quality-Scorecard.md
│   ├── SOP-Git-Workflow.md
│   └── SOP-Deployment.md
│
├── templates/                 ← fill-in templates
│   ├── BRD-TEMPLATE.md
│   ├── QA-SCORECARD-TEMPLATE.md
│   └── DEPLOY-CHECKLIST.md
│
├── reference/                 ← reference docs
│   └── DEVELOPMENT-WORKFLOW-EXPLAINED.md
│
├── courses/                   ← training modules (growing)
│   └── README.md              ← planned courses
│
├── examples/                  ← reference projects (growing)
│   └── README.md              ← planned examples
│
└── docs/
    └── STRUCTURE.md           ← how this repo is organized
```

---

## Verify after install

```bash
node --version      # v22.x
bun --version       # 1.3+
claude --version    # 2.1.100+
gh --version        # 2.x
ls ~/.claude/skills/  # gstack/ superpowers/ eo-quality-guide/
head -5 ~/.claude/CLAUDE.md  # EO MicroSaaS Student Playbook
```

Test that hooks fire: ask Claude Code to run `git push --force origin main` → expected refusal.

---

## Daily workflow (summary — full detail in CLAUDE.md)

For every feature:

1. **Plan** — write a BRD in `docs/BRD-[feature].md`
2. **TDD** — test first, implement, refactor (`superpowers:test-driven-development`)
3. **Self-review** — `gstack:/review` catches 80% of issues in 2 min
4. **Score** — 5-question scorecard (90+ to ship, save to `docs/qa-scores/YYYY-MM-DD.md`)
5. **Fix gaps** if below 90
6. **PR** — conventional commits, BRD link + score in description
7. **CI** — your own GitHub Actions run typecheck, lint, test, build, audit

Full flow + examples in `CLAUDE.md`.

---

## Role comparison (so you know where you fit)

| Aspect | You (solo student) | SMOrchestra team |
|--------|:-------------------:|:----------------:|
| GitHub | Own free account | SMOrchestra-ai org |
| Infra | Your laptop + Vercel/Netlify | Contabo servers + Tailscale mesh |
| Skill suites | gstack + superpowers + eo-quality-guide | Same 3 + internal `smorch-dev-scoring` |
| Quality gate | 5-question scorecard (mental model) | 5-hat scoring + independent QA agent |
| CI gates | Basic (typecheck, lint, build, audit) | Full (Playwright, axe, Lighthouse, BRD trace) |
| Hooks | 2 (destructive + secret) | 7 (full dev) |

You can level up to SMOrchestra-standard quality over time — the patterns are the same, scaled up.

---

## What's planned next (track in CHANGELOG)

**Courses (planned):**
- 01 MicroSaaS Fundamentals
- 02 Idea → Validated Niche
- 03 Business Brain (positioning, ICP, offer)
- 04 GTM Asset Factory
- 05 Custom Skills for Your Niche
- 06 Architecture + Claude Code Handover

**Examples (planned):**
- mini-scorecard (Next.js + Supabase lead magnet)
- arabic-landing-page (RTL layout reference)
- stripe-one-tier (subscription MVP)

See `courses/README.md` and `examples/README.md` for the full planned list.

---

## Upgrading

```bash
# Main bundle
curl -sSL https://raw.githubusercontent.com/smorchestraai-code/eo-microsaas-training/main/install.sh | bash

# Individual skill suites
cd ~/.claude/skills/gstack && git pull && ./setup
cd ~/.claude/skills/superpowers && git pull

# Claude Code itself
npm update -g @anthropic-ai/claude-code
```

Monthly is enough. Check `CHANGELOG.md` in the repo for what's new.

---

## Versioning

Main branch = latest stable. Tagged releases are frozen versions you can pin to:

```bash
curl -sSL https://raw.githubusercontent.com/smorchestraai-code/eo-microsaas-training/v1.1.0/install.sh | bash
```

`v1.1.0` today · Semantic versioning going forward.

---

## Contributing

See `CONTRIBUTING.md`. Short version:
- Courses + examples welcome via PR (with proposal issue first)
- Typo/doc fixes via PR directly
- Bug reports via issues
- Anything touching `install.sh` / hooks requires Mamoun review

---

## Support

- **Issues:** https://github.com/smorchestraai-code/eo-microsaas-training/issues
- **EO MENA:** https://smorchestra.ai
- **Community:** Discord / Telegram (link in your EO onboarding email)

---

Built by SMOrchestra for Entrepreneurs Oasis MENA.
