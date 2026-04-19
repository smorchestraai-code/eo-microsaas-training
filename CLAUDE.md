# EO MicroSaaS Student Playbook — Claude Code Setup v2.0

> Version: 2.0 (2026-04-19)
> Who this is for: EO MicroSaaS students — solo founders building your first MicroSaaS with Claude Code.
> What you get: a setup that ships 9.5+ quality code solo, zero SMOrchestra-infra dependencies.
> Setup time: 60 min active + 90 min for installs.

You are NOT part of the SMOrchestra team. This playbook assumes you have:
- Your own GitHub account (free tier is fine)
- Your own Supabase / Vercel / Netlify accounts
- Your own API keys (Claude, OpenAI, Stripe, whatever you integrate)
- No smorch-brain access, no Tailscale mesh, no shared servers

Solo. Your laptop + your cloud accounts. That's it.

---

## Quick Start

From the folder containing this playbook:

```bash
bash install.sh
```

The script installs Node 22, Bun, Claude Code, gh CLI; clones gstack + superpowers skill suites; writes an eo-quality-guide skill (student 5-question scorecard); installs student-tuned settings.json (destructive-blocker + secret-scanner hooks); installs this playbook as ~/.claude/CLAUDE.md.

---

## Step 1 — Verify install

```bash
node --version     # v22.x
bun --version      # 1.3+
claude --version   # 2.1.100+
gh --version       # 2.x
ls ~/.claude/skills/  # gstack/ superpowers/ eo-quality-guide/
```

---

## Step 2 — Hooks (auto-installed)

| Hook | Blocks | Why |
|------|--------|-----|
| destructive-blocker | perm-delete commands, force push, hard reset, DROP TABLE, TRUNCATE | irreversible damage |
| secret-scanner | real API keys or private keys written to non-env files | leaked keys hijack your accounts |

Test it: in Claude Code ask `git push --force origin main` — refusal expected.

---

## Step 3 — Workflow per feature

### 1. Plan — write a BRD
At `docs/BRD-[feature].md`: problem, ICP, acceptance criteria (numbered AC-1.1 etc. — you'll tag tests with these), 'done when' bullets.

### 2. TDD first
Test file BEFORE source. Failing test → minimum code to pass → refactor. Ask Claude: use `superpowers:test-driven-development`.

### 3. Self-review before commit
Ask Claude: run `gstack:/review`. 4 dimensions scored: security, performance, correctness, maintainability. Fix anything below 8/10 before committing.

### 4. Score before PR — 5-question scorecard

| # | Hat | Questions |
|---|-----|-----------|
| 1 | Product | Matches BRD? Real user would use it? |
| 2 | Architecture | Logical modules? Data flow explainable in 2 sentences? |
| 3 | Engineering | Tests exist? Error handling on every external call? |
| 4 | QA | Every user flow clicked? Empty/error states tested? |
| 5 | UX | Mobile 375px works? Arabic RTL if MENA ICP? Zero console errors? |

Each 1-10. Composite = average × 10.

| Composite | Decision |
|-----------|----------|
| 90+ | Ship |
| 80-89 | Fix lowest hat, re-score |
| <80 | Do not ship |

Save every score to `docs/qa-scores/YYYY-MM-DD.md`. Track weekly.

### 5. Open PR
Conventional commits (`feat:`, `fix:`, `docs:`, `chore:`). PR description: BRD link + score.

### 6. CI — one-time per project

`.github/workflows/pr-quality.yml`:

```yaml
name: PR Quality
on: pull_request
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm run test 2>&1 || echo 'no tests yet'
      - run: npm run build
      - run: npm audit --audit-level=high
```

Ratchet up as you add tests.

---

## Step 4 — Per-project CLAUDE.md template

```markdown
# [Project Name]

## Identity
- Business: [your MicroSaaS]
- Tech: Next.js 14 + Supabase + Tailwind (adjust to your stack)
- Repo: github.com/YOUR-USERNAME/repo-name
- Branch: main (prod), dev (integration), feat/* (work)

## Rules
1. No secrets in code — use .env (gitignored)
2. Arabic RTL if MENA user-facing
3. typecheck + lint + test before every commit
4. Every PR: /review → 5-question scorecard (90+ to ship)

## Dev Tools
| When | Run | Why |
|------|-----|-----|
| Coding | superpowers: test-driven-development | TDD |
| Commit | gstack: /review | 4-dim review |
| Before PR | 5-Q scorecard | 90+ to ship |
| Bug | superpowers: systematic-debugging | Root cause |
| UI changes | gstack: /design-review | Catches slop, RTL bugs |
| Ready to merge | gstack: /ship | Clean PR |
```

Also create `docs/` with `handovers/`, `qa-scores/`, `architecture/` subfolders.

---

## Step 5 — Deploy via Vercel or Netlify

Free tiers are enough for a MicroSaaS MVP.

Vercel: `vercel login` → `cd project && vercel --prod` → env vars in dashboard → git push auto-deploys.

Netlify: connect repo → build `npm run build` → env vars in Site Settings → push auto-deploys.

Do NOT: expose secret keys as NEXT_PUBLIC_* (those reach the browser); commit .env.local; run customer data through free tier without reading privacy terms.

---

## Step 6 — Troubleshooting

Weird bug → ask Claude: use `superpowers:systematic-debugging`. Don't guess. Ruleout via evidence.

Code feels messy → `gstack:/review` and address anything below 8/10.

Decision stuck → `superpowers:brainstorming` to compare options.

Score stuck below 90 — usual culprits: no tests (QA), mobile broken or untested RTL (UX), no error handling on external APIs (Engineering).

---

## Non-Negotiable Rules

1. Every project has `docs/` at root
2. Never commit `.env`; use `.env.example` with fake values
3. Never commit `node_modules/`, `.next/`, build artifacts — use `.gitignore`
4. `/review` before every commit (2 min, catches 80% of issues)
5. 5-Q scorecard before every PR (save to `docs/qa-scores/`)
6. Bugs use `systematic-debugging` — no guessing
7. No hard-coded keys, anywhere. The hook will block you.

---

## Daily Checklist

**Morning**
- [ ] `git pull`
- [ ] `npm install` if deps changed
- [ ] Open Claude Code
- [ ] Confirm AC clear

**Before each commit**
- [ ] Tests pass locally
- [ ] Typecheck clean
- [ ] Lint clean
- [ ] `/review` addressed
- [ ] No secrets in diff

**Before each PR**
- [ ] 5-Q scorecard ≥ 90
- [ ] Score saved to `docs/qa-scores/`
- [ ] PR has BRD + score

**End of day**
- [ ] Everything committed + pushed

---

## Voice for copy

Direct. Specific. Numbers over claims. "200+ Arabic SaaS founders in UAE" not "extensive MENA experience." Trust-first, pitch-second. Gulf Arabic conversational, not MSA.

Never use: leverage, synergy, ecosystem, holistic, digital transformation, innovative, cutting-edge, world-class.

---

## What 9.5 means

- Last 5 PRs pass CI first try
- Last 5 scorecards ≥ 90 without rework
- Zero production bugs reported in 30 days on your code
- You can explain any file in 2 sentences

Below that: more tests, clearer modules, better UX.

---

## Getting help

- Stuck > 90 min → EO community Discord/Telegram
- Approach unclear → community review request
- Security (payments, PII) → ask directly, don't guess

---

## Upgrading

- Claude Code: `npm update -g @anthropic-ai/claude-code` monthly
- gstack: `cd ~/.claude/skills/gstack && git pull && ./setup` monthly
- superpowers: `cd ~/.claude/skills/superpowers && git pull` monthly
- Playbook: pull latest from EO MENA repo release tags (`playbook-v*`)

---

Playbook v2.0 · 2026-04-19
