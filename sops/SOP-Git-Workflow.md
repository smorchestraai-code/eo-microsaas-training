# Student SOP: Git Workflow

**Version:** 1.0 (2026-04-19)
**When to use:** Every day you code.

---

## Branch strategy

```
main          — production (only merged PRs land here)
dev           — integration branch (optional; some projects skip this)
feat/xyz      — your work branch (one per feature)
fix/xyz       — your bugfix branch (one per bug)
```

---

## Typical flow for a new feature

```bash
# 1. Start clean
git checkout main
git pull origin main

# 2. Branch off
git checkout -b feat/your-feature-name

# 3. Code + commit as you go (don't wait till the end)
# (each logical chunk = one commit)
git add <specific-files>
git commit -m "feat: add user registration form"

git add <next-batch>
git commit -m "feat: validate email on registration"

# 4. Push your branch to GitHub
git push -u origin feat/your-feature-name

# 5. Open a PR targeting main (or dev if your project uses it)
gh pr create --base main --head feat/your-feature-name
```

---

## Commit message format (conventional commits)

```
type: short description

feat: add password reset flow
fix: handle empty email field
docs: update README setup steps
chore: upgrade next to 14.2.35
refactor: extract auth logic into /lib/auth
test: add coverage for edge cases
```

**Types:** `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`, `style`

---

## What to never commit

The hook will block these, but know WHY:

- `.env`, `.env.local` → contains API keys; gets you hacked if pushed
- `node_modules/` → huge, auto-reinstalled
- `.next/`, `dist/`, `build/` → generated; different per machine
- Large binary files → bloats the repo history
- SSH private keys, any `-----BEGIN PRIVATE KEY-----` — self-explanatory

`.gitignore` should cover all of these. Check your project has a good one.

---

## Every commit

Before you commit, in Claude Code ask:

> "Run gstack:/review on the changes I'm about to commit."

If `/review` flags something, fix it before the commit.

---

## Every PR

1. Open PR → conventional title: `feat: add password reset flow`
2. PR description must include:
   - Link to BRD in `docs/BRD-*.md`
   - Your 5-question scorecard composite (save to `docs/qa-scores/` first)
   - Screenshots if UI changed
3. Wait for CI to pass
4. Merge once CI is green + you've addressed any review comments

---

## When things go wrong

### Pushed to wrong branch
```bash
# If you pushed to a feat/* branch by accident and meant a different one:
git checkout correct-branch
git cherry-pick <bad-commit-sha>
git push origin correct-branch
# Then open a PR to delete the wrong branch (or push --force-with-lease if it's your own)
```

### Committed a secret
```bash
# DO NOT just delete the file. The secret is in git history.
# Steps:
# 1. ROTATE the secret at the source (e.g., regenerate the API key)
# 2. Use git-filter-repo or BFG to remove from history
# 3. Force-push
# 4. Ask everyone who cloned to re-clone
```

Better: don't commit secrets. The hook should have stopped you.

### Merge conflict
```bash
git checkout main
git pull origin main
git checkout feat/your-branch
git merge main   # or: git rebase main
# Resolve conflicts in the listed files
git add <resolved-files>
git commit      # or: git rebase --continue
git push
```

---

## When you want to undo

- **Uncommitted changes → trash them:** `git checkout -- <file>` (discards; be sure)
- **Last commit wasn't pushed → amend message:** `git commit --amend`
- **Last commit wasn't pushed → undo:** `git reset HEAD~1` (keeps changes in working dir)
- **Pushed commit → revert:** `git revert <sha>` (creates new commit undoing it)

**NEVER** use `git reset --hard` on a branch others have pulled — it's destructive and the hook will block it.
