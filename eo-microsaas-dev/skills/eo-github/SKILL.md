---
name: eo-github
description: "GitHub setup for EO MicroSaaS projects. Four modes: create (new repo), point-existing (wire up already-created repo), guided (help confused students pick), audit (drift report for an existing repo). Uses GitHub MCP tools (mcp__github__*) exclusively. Plan-mode gated — never touches a remote without explicit approval. Private by default. Every refuse path names a concrete next door. Triggers on: 'eo github', 'create github repo', 'point github repo', 'promote to github', 'wire up origin', 'اربط جيت هب'."
version: "1.1"
---

# eo-github — GitHub Setup Skill

**Version:** 1.1 (2026-04-23 — stuck-path hardening: slug collision retry, non-empty remote remediation clarity, MCP auth vs missing split, rate-limit / race handling, manual escape hatch, actionable LICENSE guidance)
**Pillar:** EO-specific — owns every remote-touching operation so bootstrap stays local-safe.
**Purpose:** The only skill in the plugin allowed to create or wire up a GitHub remote. `/1-eo-dev-start` routes here when a student explicitly asks for GitHub. Students can also invoke directly after local trial work.

**Hard contracts:**
- Never runs without a GitHub MCP connected. The skill auto-discovers `mcp__Github-*__*` MCPs at Step 4.5 and picks the right one for the founder's account (no `gh auth login` prompt). If zero are connected → refuse with install remediation (Step 2 Case A).
- Never overwrites an existing remote. Once `origin` is set, this skill refuses.
- Never force-pushes. Never writes to a non-empty remote (protects against adopting someone else's repo).
- Private by default. Student flips visibility later via GitHub UI.
- Plan-mode preview before any remote creation or `git remote add`.
- **v1.4.6 — Autonomous push pipeline.** Default path is the MCP-based push (Step 6: `create_or_update_file` to seed → chunked `push_files` → `list_commits` to verify → local refs reset to align). NO `git push -u origin main` from the founder's shell. The shell-based manual runbook (Step 2b) is the **last resort** invoked only when zero `Github-*` MCPs are reachable, never as a workaround for account mismatch.

---

## Why this skill exists

`/1-eo-dev-start` is local-only by design (students trial 3 times before "this is the one" — we don't want three abandoned repos polluting the org). GitHub ops are isolated here so:

1. The bootstrap flow stays cheap to retry.
2. Every remote write is an explicit, reviewed action.
3. MCP dependency lives in one place — if MCP is missing, only this skill refuses, not the whole plugin.

---

## The admin contract

This skill is the student's GitHub admin for EO MicroSaaS repos. That means:

- **It owns repo state.** Settings drift → skill detects → offers correction.
- **It adapts to plan.** Paid org (Team/Enterprise) gets features free orgs can't use.
- **It picks branch strategy.** Solo student = trunk-only. Team = `main` + `dev`.
- **It never assumes.** Plan-mode preview for every change, even updates to existing repos.

The student is the CEO. The skill is the DevOps person who keeps things consistent.

---

## Four modes

### Mode 1 — `create`

Student wants a fresh GitHub repo for this project.

**Inputs:**
- `repo_slug` — sanitized from folder name (e.g., `eo-oasis`). Student can override.
- `visibility` — `private` (default). Always.
- `description` — first sentence of `EO-Brain/1-ProjectBrain/positioning.md` first line, truncated to 350 chars. Optional.

**Sequence:** precheck → plan preview → create repo → apply best-practices settings → `git init` if needed → stage+commit if no prior commit → `git remote add origin` → `git push -u origin main` → create `dev` branch if team strategy.

### Mode 2 — `point-existing`

Student already made the repo on GitHub and wants this local workspace wired to it.

**Inputs:**
- `repo_ref` — either a full URL (`https://github.com/org/repo`) or `owner/repo` shorthand.

**Sequence:** precheck → validate repo exists + student has write → validate repo is empty OR only has a README (no bootstrap collision) → plan preview → `git init` if needed → stage+commit if no prior commit → `git remote add origin` → `git push -u origin main`.

### Mode 3 — `guided`

Triggered when student picked "I don't know" in `/1-eo-dev-start`'s 4-option question AND GitHub MCP is connected. Explains create vs point-existing in one screen, asks the student to pick, then hands off to Mode 1 or Mode 2.

### Mode 4 — `audit` (admin maintenance)

Invokable any time post-setup as `/eo-github audit`. Reads current repo state via MCP, compares to the best-practices matrix, emits a drift report:

- What matches spec (green)
- What drifted (yellow) — with "Fix in plan mode (y/n)?" prompt
- What's unfixable by the skill (red) — e.g., billing plan changes, requires student action

Only writes on explicit `y` per drifted setting. Never batch-fixes without per-item approval when the fix is non-trivial (protected branch rules, collaborator changes).

Runs automatically after the first `/7-eo-ship` to offer branch protection activation (see "Post-first-CI automation" below).

---

## Org type awareness (paid vs free)

On every mode, detect the target org's plan once via MCP (cache in memory for the session):

```
owner_type = user | organization
plan       = free | pro | team | enterprise  (from MCP org/user fetch)
```

### What the skill does differently by plan

| Feature | Free / Pro | Team+ | Enterprise |
|---------|------------|-------|------------|
| Private repos | ✅ unlimited | ✅ | ✅ |
| Branch protection on `main` | ✅ (basic: require PR, no force-push) | ✅ + required reviewers | ✅ + required reviewers + bypass lists |
| Required status checks | ✅ after first CI green | ✅ | ✅ |
| CODEOWNERS enforcement | ❌ (file ignored by GitHub on free/pro) | ✅ applied | ✅ applied |
| Draft PRs | ✅ | ✅ | ✅ |
| Required reviewers | ❌ skip — not honored | ✅ set to 1 for solo, 1-2 for team | ✅ |
| Secret scanning | Push protection only | ✅ full | ✅ full |
| Audit log retrieval | ❌ | ✅ | ✅ |

**Rule:** the skill never offers a setting that the plan can't honor. Free-plan students never see "required reviewers — on/off?" because GitHub would silently ignore it. That teaches the wrong mental model.

Plan detection is non-blocking — if MCP can't resolve the plan, default to `free` and warn in evidence table.

---

## Branch strategy

Detect collaborators via MCP (`list_collaborators` or equivalent):

- **Solo (≤1 collaborator including owner) → trunk-only:** default branch `main`. Feature branches named `feat/*`, `fix/*`, `chore/*`. Merge back to `main` via PR. No long-lived `dev`. This matches the EO `/7-eo-ship` flow — main is always shippable.
- **Team (≥2 collaborators) → dual-branch:** default branch `main` (production), auxiliary branch `dev` (integration). Feature branches merge to `dev`; `dev` merges to `main` on release. CI runs on PRs to both.

### What the skill creates

| Scenario | Branches at creation | Branch protection (deferred until first CI pass) |
|---|---|---|
| Solo, Mode 1 | `main` only | `main`: require PR, disallow force-push, disallow deletion |
| Team, Mode 1 | `main` + `dev` (dev branched from main's first commit) | `main`: require PR + 1 reviewer (Team plan) + required status checks; `dev`: require PR + required status checks |
| Solo, Mode 2 (existing empty repo) | Inherits existing default (usually `main`). Creates `dev` only if student explicitly requests team mode. | Same as above |
| Team, Mode 2 | Verifies `main` exists. Creates `dev` if missing. | Same as above |

The plan-mode preview always shows the branch plan explicitly. If the student is solo now but plans to add collaborators soon, they can flip to team mode via plan preview (`Choose strategy: trunk / dual`).

### Post-first-CI automation

Branch protection can only require status checks that have *actually run at least once*. On first `/7-eo-ship` success:

1. `/7-eo-ship` signals to `eo-github` (via a marker file or direct invocation) that CI has passed.
2. `eo-github audit` runs and offers:
   ```
   ✅ CI passed for the first time.
   
   Ready to lock down main? Proposed protection:
     - Require PRs (no direct pushes to main)
     - Require status check: "CI" (just passed)
     - Disallow force-push
     - Disallow branch deletion
     - Include administrators: yes (protects you from yourself)
   
   Apply? (y/n)
   ```
3. On `y` → applies via MCP. On `n` → leaves main unprotected; prompts again after next 3 ships.

This is how protection gets on without blocking the first-ever push.

---

## Repo creation best practices (applied by Mode 1)

Every repo this skill creates inherits the same shape. Students learn one mental model; future tooling reads a predictable structure.

### Naming rules (enforced at slug sanitization)

| Rule | Why |
|---|---|
| Lowercase only | GitHub URLs are case-insensitive; mixed case causes clone confusion |
| ASCII alphanumeric + hyphen `-` | No underscores (breaks subdomains), no dots (breaks routing), no unicode (breaks tooling) |
| Must start with a letter | Numeric-leading names confuse some build systems |
| 3-60 chars (hard bounds) | Short enough for URL bars, long enough to be specific |
| No consecutive hyphens | Visual noise + typo risk |
| No trailing hyphens | Breaks some CI parsers |
| Reject reserved names | `api`, `www`, `admin`, `test`, `new`, `main`, `master`, `docs`, `blog`, `auth` — too generic, collides with subroutes |
| Prefix `eo-` if `mena_flag` is true | Groups EO MENA projects together in the org listing |
| No version numbers (`-v2`, `-2026`) | Use tags for versioning, not repo names |
| No client names unless intentional | A repo named `acme-microsaas` is a marketing commitment; confirm with student |

Sanitization order: lowercase → strip non-[a-z0-9-] → collapse consecutive `-` → trim edges → check reserved list → check length. If final slug fails any rule → prompt student for a replacement. Never silently rename.

### Repo settings at creation (always applied)

| Setting | Value | Why |
|---|---|---|
| `private` | `true` | Pre-launch default. Student flips public in UI when ready. |
| `default_branch` | `main` | Never `master`. Consistency across the org. |
| `description` | First non-empty line of `EO-Brain/1-ProjectBrain/positioning.md`, ≤350 chars | Empty descriptions make the repo listing useless. If positioning is missing, prompt the student. |
| `auto_init` | `false` | We have scaffold content from `handover-bridge`. Don't let GitHub create a competing README. |
| `has_issues` | `true` | Bug intake surface. Keep on. |
| `has_wiki` | `false` | Docs live in `docs/` inside the repo. Wiki creates drift. |
| `has_projects` | `false` | Tracker is `_dev-progress.md`. GitHub Projects is noise at this stage. |
| `has_discussions` | `false` | Add later if community grows. Empty Discussions tab is worse than none. |
| `allow_squash_merge` | `true` | Default merge strategy for PR flow. |
| `allow_merge_commit` | `false` | Keep history linear. |
| `allow_rebase_merge` | `false` | One default, one mental model. |
| `delete_branch_on_merge` | `true` | Feature branches are ephemeral. Cleans up noise. |

### Topics applied (auto-derived)

Always: `eo-microsaas`
If `mena_flag`: add `mena`, `arabic-rtl`
From `tech-stack-decision.md`: add up to 5 detected tools (e.g., `nextjs`, `supabase`, `tailwindcss`, `typescript`, `stripe`)

Topics help discoverability within the student's own org listing and signal the stack at a glance.

### Issue labels preset (created after repo exists)

| Label | Color | Purpose |
|---|---|---|
| `bug` | `#d73a4a` | Something is broken |
| `enhancement` | `#a2eeef` | New feature or improvement |
| `blocked` | `#b60205` | Waiting on external decision or dep |
| `needs-info` | `#fbca04` | Can't act without more detail from reporter |
| `mena` | `#0e8a16` | MENA-specific (RTL, locale, payment rails) |
| `score-gap` | `#c5def5` | Raised during `/5-eo-score` — track which hat |

Skip labels that already exist (GitHub creates `bug`, `enhancement` by default — don't duplicate; just add the new ones).

### LICENSE handling

If no `LICENSE` file exists in the local scaffold → do NOT auto-create one. Print in the evidence table: *"No LICENSE found. Add one when ready: MIT is the common MicroSaaS default."* Licensing is a business decision, not a bootstrap default — students should choose consciously.

### Things this skill does NOT set (intentionally deferred)

| Deferred setting | Why | When student handles it |
|---|---|---|
| Branch protection on `main` | Requires at least one CI run to define required status checks | After first `/7-eo-ship` succeeds and CI runs once — evidence table prompts the student |
| CODEOWNERS | Needs human judgment on who reviews what | When the project has ≥2 contributors |
| Security policy (`SECURITY.md`) | Template should be chosen by student | After first private beta |
| Environments & secrets | Depend on deploy lane (Vercel vs Contabo) | During `/7-eo-ship` flow (deploy step runs the project's own deploy script) |
| Dependabot | Opinionated | Student enables in GitHub UI if desired |

The evidence table at Step 7 tells the student which of these are worth doing next.

---

## Execution sequence

### Step 1 — Resolve workspace root

Worktree-aware:
```
if [ -n "$GIT_WORK_TREE" ]; then ROOT="$GIT_WORK_TREE"
elif git rev-parse --show-toplevel >/dev/null 2>&1; then ROOT="$(git rev-parse --show-toplevel)"
else ROOT="$PWD"
fi
```

### Step 2 — MCP precheck (two distinct failure paths)

Check for the presence of GitHub MCP tools. The agent runtime exposes MCP tools with the `mcp__github__` prefix.

**Case A — MCP tools absent entirely** (no tool name matches `mcp__github__`):

```
❌ GitHub MCP not connected.

This skill requires the GitHub MCP server. Without it, I can't safely
create or wire up remotes.

Remediation (pick one, most common first):
  1. Install via settings.json — add to ~/.claude/settings.json:
       "mcpServers": {
         "github": {
           "command": "npx",
           "args": ["-y", "@modelcontextprotocol/server-github"],
           "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..." }
         }
       }
     Create the PAT at https://github.com/settings/tokens (classic or
     fine-grained; scopes: repo, read:org). Restart Claude Code.
  2. Install the GitHub MCP CLI globally — follow your installer's docs.
  3. Manual escape hatch (see "Manual fallback" below) — skip MCP entirely
     and wire up via GitHub UI + `git remote add`. You lose the admin
     settings alignment but you get unblocked today.

Sprint work continues either way. /eo-plan, /eo-code, /eo-score, and
/eo-bridge-gaps all work without a remote. Only /eo-ship will refuse.

No writes made.
```

Exit.

**Case B — MCP tools present but auth fails** (tool call returns 401/403 or "bad credentials"):

```
❌ GitHub MCP is connected but authentication failed.

Likely causes:
  1. PAT expired — most common. GitHub PATs expire on a schedule.
     Fix: https://github.com/settings/tokens → regenerate → paste into
     settings.json → restart Claude Code.
  2. PAT missing required scopes — need `repo` and `read:org`
     at minimum. Fine-grained PATs need "Administration: read/write"
     for repo creation.
  3. SSO not approved for this token — if your org uses SSO, approve
     the PAT at https://github.com/settings/tokens under "SSO".
  4. MCP server misconfigured — env var name differs per server
     (some use GITHUB_TOKEN, others GITHUB_PERSONAL_ACCESS_TOKEN).
     Check the server's README.

After fixing, re-run /eo-github. All local state is preserved.

No writes made.
```

Exit.

### Step 2b — Manual fallback (escape hatch when MCP can't be fixed now)

Invoked explicitly by the student saying "manual" / "bypass MCP" in response to either Step 2 refusal. The skill produces an operator runbook — text only, zero writes — that the student executes by hand:

```
📘 Manual GitHub wire-up (no MCP needed)

1. Create the repo in GitHub UI:
   - https://github.com/new
   - Name: {suggested_slug}
   - Private
   - Do NOT initialize with README, .gitignore, or LICENSE
     (we already have scaffold content locally)
   - Create repository

2. In this terminal, from project root:
     git init -b main                       # only if .git is missing
     git add -A
     git commit -m "chore(bootstrap): initial handoff"
     git remote add origin git@github.com:{owner}/{slug}.git
     git push -u origin main

3. Back in GitHub UI → Settings:
   - Options → disable Wiki, Projects, Discussions
   - Options → "Automatically delete head branches" on
   - Options → only "Allow squash merging" checked
   - Collaborators → add anyone who needs write
   - Branches → wait until your first CI runs, then add protection
     requiring a status check named "CI"

4. Back here: /eo-guide will detect the remote on next run.

This skill produces zero writes in manual mode. Everything above is
executed by you.
```

Exit. The student returns when ready (either MCP fixed, or they wire it manually and just keep going).

### Step 3 — Remote precheck (refuse if origin exists)

```
git config --get remote.origin.url 2>/dev/null
```

If output is non-empty → refuse:

```
⚠️ Origin remote already set.

Current origin: {existing_url}

This skill refuses to overwrite an existing remote. Options:
  - If that remote is correct: use normal git commands (git push, /7-eo-ship)
  - If it's wrong: manually `git remote set-url origin <correct>` then
    re-run /eo-github to push your current state.
  - If you need a completely fresh start: see /eo-dev-repair.

No writes made.
```

Exit.

### Step 4 — Determine default owner

Via MCP, fetch the authenticated user (e.g., `mcp__github__get_me` or the equivalent in the connected server). Record `default_owner = login`.

If the MCP call fails with a 401/403 / "bad credentials" signal → jump to **Step 2 Case B** (auth remediation).

If the MCP call fails with a network / 5xx / timeout → print:

```
⚠️ GitHub MCP reachable but returned a server error.

This is almost always a transient GitHub outage. Check:
  - https://www.githubstatus.com/
  - Your network (VPN? corporate proxy blocking api.github.com?)

Options:
  - Wait 2 minutes and re-run /eo-github.
  - Use the manual fallback (Step 2b) if GitHub UI still works.

No writes made.
```

Exit.

### Step 4.5 — GitHub MCP discovery + account selection (v1.4.6, autonomous)

Multiple `mcp__Github-*__*` MCPs may be installed (e.g. `Github-alamouri`, `Github-smo`). Each is pre-authenticated as a different GitHub account. The skill must pick the right one **without asking the founder to run `gh auth login` or `gh auth switch`**.

#### 4.5a — Discover

```
1. Enumerate available MCP servers matching `Github-*`.
2. For each, call mcp__$mcp__search_users(q="me", per_page=1) → returns the
   authenticated user's login (cheap call, no side effects).
3. Build map: { mcp_server_name → github_login }.
```

If zero `Github-*` MCPs are connected → fall through to existing Step 2 Case A (install MCP). The skill DOES NOT ask the founder to run `gh auth login` for account-switching purposes — only for missing-MCP installation.

#### 4.5b — Select (deterministic priority)

```
1. Read EO-Brain/1-ProjectBrain/profile-settings.md for the founder's GitHub
   handle. Match patterns: "github.com/{login}", "GitHub: {login}",
   "@{login}".
2. If found AND matches one of the discovered MCPs → pick that MCP. Done.
3. If profile-settings doesn't name a handle:
   - Default to the MCP whose login matches the project's intended owner per
     `tech-stack-decision.md` (look for "GitHub org/owner: {x}").
   - Otherwise default to the first MCP that's NOT `Github-smo` (preserve
     SMO main-work isolation — student demos should never accidentally push
     to the SMO production org).
4. If multiple `Github-*` MCPs match the founder's handle (shouldn't happen,
   but defensive) → pick the lexicographically-first one and warn.
```

Record the chosen MCP and login in session state for all subsequent calls:

```
$github_mcp     = "Github-alamouri"  (the MCP server to call)
$github_login   = "alamouri99"        (the account doing the work)
$default_owner  = $github_login OR resolved org if BRD names one
```

All subsequent MCP calls in this skill use `mcp__$github_mcp__*` (not `mcp__github__*` — that namespace doesn't exist if the user installed the per-account variant).

#### 4.5c — Show selection to founder (one line, no approval needed)

```
🔑 Using GitHub account: $github_login (via $github_mcp MCP)
```

This is informational. The founder doesn't need to approve — the selection is deterministic from `profile-settings.md`. If they want a different account, they edit `profile-settings.md` and re-run.

### Step 5 — Branch by mode

#### Mode 1 (`create`) — derive slug + show plan

Sanitize folder name to a GitHub-safe slug:
- Lowercase
- Replace non-alphanumeric with `-`
- Collapse consecutive `-`
- Trim leading/trailing `-`
- Truncate to 60 chars (see naming rules table above — not 90)
- Enforce naming rules: must start with letter, reject reserved names, no consecutive/trailing hyphens, no numeric-leading

If sanitization fails any rule → prompt student for a replacement immediately, before any MCP call. Do NOT silently rename.

**Slug collision retry loop** — via MCP, check if `{default_owner}/{slug}` already exists. If yes:

```
⚠️ {default_owner}/{slug} already exists on GitHub.

Suggestions:
  1. {slug}-2
  2. {slug}-{year}   (e.g., {slug}-2026)
  3. eo-{slug}       (if not already prefixed)
  4. Pick your own

Reply with a number, or type a new slug (3-60 chars, lowercase ASCII,
hyphens allowed, must start with a letter), or type "cancel" to exit.
```

Retry up to 3 times. On each retry, re-run sanitization + reserved-name check + existence check. After 3 collisions/invalid replies, refuse:

```
⚠️ Couldn't settle on a slug after 3 tries.

Exit options:
  - Think about naming offline, come back to /eo-github create when ready.
  - Use Mode 2 (point-existing) if you already have a repo.
  - Use the manual fallback (Step 2b) and name the repo in GitHub UI directly.

No writes made.
```

Exit. This avoids an infinite prompt loop; the student owns the decision.

Read description candidate:
- First non-empty line of `$ROOT/../EO-Brain/1-ProjectBrain/positioning.md` (or search paths as in `eo-dev-start` Step 2)
- Strip markdown heading markers, truncate to 350 chars
- If absent → empty description

**Plan mode preview:**

```
📋 Create GitHub repo

  Repo:         {default_owner}/{slug}
  Visibility:   private
  Description:  {description or "—"}
  Default branch: main
  Will push:    {current branch head if git exists, else "first commit of
                 current working tree"}

After creation:
  - Local git initialized (if not already)
  - Single commit: "chore(bootstrap): initial handoff" (only if no prior
    commits exist; otherwise uses existing HEAD)
  - origin wired to git@github.com:{default_owner}/{slug}.git
  - First push: git push -u origin main

Will NOT:
  - Set visibility to public (flip in GitHub UI when ready)
  - Force push
  - Modify any file at {ROOT}
  - Change branch protection (do that in GitHub Settings when ready)

Approve? (y/n)
```

On `n` → exit, no writes.
On `y` → Step 6.

#### Mode 2 (`point-existing`) — validate + show plan

Parse `repo_ref`:
- Full URL `https://github.com/X/Y` → owner=X, repo=Y
- Shorthand `X/Y` → owner=X, repo=Y
- Anything else → ask student to paste a valid ref, no other writes

Via MCP:
1. `get_repository(owner, repo)` — if 404 → refuse with "repo not found on GitHub. Create it first or use mode 1."
2. Check `permissions.push == true` — if false → refuse with "you don't have push access. Fix permissions on GitHub first."
3. List commits or check default branch state — if the repo has commits beyond a single initial README commit → refuse with:

```
❌ Target repo {owner}/{repo} is not empty.

Found: {commit_count} commits, last by {author} on {date}.

This skill refuses to push onto a non-empty remote (protects you from
accidentally adopting someone else's work, and protects them from you
force-pushing over theirs).

Exit options (pick what describes your situation):

  A. Those commits are mine but unrelated to this project.
     → Use Mode 1: `/eo-github create` will make a fresh repo.

  B. Those commits ARE this project's earlier state (you rebuilt locally
     after an abandoned try, or restored from backup).
     → Don't use this skill. Use normal git:
         git remote add origin {html_url}
         git fetch origin
         git merge origin/main --allow-unrelated-histories
         # resolve conflicts, then:
         git push -u origin main
       This skill refuses to guess the merge strategy — wrong guess loses work.

  C. The remote repo was a mistake and you want to start it over.
     → Delete it in GitHub UI (Settings → Delete this repository),
       then re-run `/eo-github create`. Or use Mode 1 with a new slug.

  D. You want to just nuke and re-push.
     → Not supported here. This skill never force-pushes. If you really
       want to overwrite the remote, do it explicitly with `git push --force`
       outside this skill, understanding the risk.

No writes made.
```

Empty repo (or only an auto-generated README from GitHub UI, detected as single commit by `github-actions[bot]` or GitHub's web UI author) → proceed.

Run the best-practices diff against the existing repo:

- Read current `has_wiki`, `has_projects`, `has_discussions`, `allow_*`, `delete_branch_on_merge`, description, topics, labels, default branch
- Compare to best-practices matrix
- Build a drift list (only items that can be safely changed without touching existing content)

**Plan mode preview:**

```
📋 Point to existing GitHub repo

  Repo:         {owner}/{repo}
  URL:          {html_url}
  Plan:         {free|pro|team|enterprise}
  Owner type:   {user|organization}
  Strategy:     {trunk-only | dual-branch}   ← picked based on collaborator count
  Visibility:   {current}  (skill does not change this)
  Empty:        yes (or "README only — will be preserved")
  Will push:    {current branch head if git exists, else "first commit
                 of current working tree"}

Settings to align with best practices (diff):
  has_wiki              {current} → false
  has_projects          {current} → false
  has_discussions       {current} → false
  delete_branch_on_merge {current} → true
  allow_merge_commit    {current} → false
  description           {current or "—"} → "{proposed from positioning.md}"
  topics                {current} → [eo-microsaas, mena?, {stack}...]
  labels                {missing} → add {list}

After wiring:
  - Local git initialized (if not already)
  - Single commit: "chore(bootstrap): initial handoff" (only if no prior
    commits exist; otherwise uses existing HEAD)
  - origin wired to git@github.com:{owner}/{repo}.git
  - First push: git push -u origin main
  - {If dual-branch strategy:} dev branch created from main's HEAD and pushed

Deferred (applied after first CI green — see Post-first-CI automation):
  - Branch protection on main
  - Required status check "CI"

Will NOT:
  - Change the repo's visibility (already set by you)
  - Force push
  - Delete or rewrite existing README or any committed file
  - Delete or rename existing labels (only add missing ones)
  - Touch collaborators or webhooks

Approve? (y/n — or "skip-settings" to wire up origin only, no admin sync)
```

On `n` → exit, no writes.
On `skip-settings` → jump to Step 6 for the push sequence, skip settings alignment.
On `y` → Step 6 (push) + Step 6b (settings alignment).

#### Mode 3 (`guided`) — explain + route

Print:

```
📍 GitHub setup — pick one:

  A. Create a new repo now
     I'll create {default_owner}/{suggested_slug} as private and wire up
     this workspace to it.

  B. Point to a repo I already created
     You've made an empty repo on GitHub (maybe from the web UI or
     another tool). Paste the URL or owner/repo and I'll wire it up.

  C. Not now — keep building locally
     No GitHub actions. Come back to /eo-github later.

(A/B/C):
```

Capture answer:
- `A` → jump to Mode 1
- `B` → ask "Paste the URL or owner/repo:" → Mode 2
- `C` → print the same "build locally, come back later" message as Step 2 refusal case and exit without writes

#### Mode 4 (`audit`) — read current state, diff, fix per-item

Invocation: `/eo-github audit`. Requires an existing origin (refuse if no origin — there's nothing to audit).

**Sequence:**

1. **Read current state via MCP:**
   - `get_repository(owner, repo)` → settings, description, default_branch, visibility, plan (from owner).
   - `list_topics(owner, repo)` → current topics.
   - `list_labels(owner, repo)` → current labels.
   - `list_branches(owner, repo)` → branch set (to decide if `dev` is expected).
   - `get_branch_protection(owner, repo, "main")` → protection state (404 if unprotected).
   - `list_collaborators(owner, repo)` → count → strategy.
   - Last CI run status (to decide whether to offer branch protection).

2. **Compute drift** against the best-practices matrix. For each item:
   - `match` → green, no action.
   - `drift-fixable` → yellow, offer fix.
   - `drift-manual` → red, explain (e.g., plan change required).

3. **Print drift report:**
   ```
   📊 Repo audit — {owner}/{repo}
   
   Plan: {plan}   Strategy: {strategy}   Collaborators: {n}
   Last CI run: {status or "none yet"}
   
   ✅ Matches spec ({n})
     - has_wiki=false
     - delete_branch_on_merge=true
     - ...
   
   ⚠️ Drifted — fixable ({n})
     - has_projects: true → false     Fix? (y/n)
     - allow_merge_commit: true → false   Fix? (y/n)
     - topics: [{current}] → [{proposed}]  Fix? (y/n)
     - labels missing: mena, score-gap    Add? (y/n)
     - dev branch missing (team strategy) Create? (y/n)
   
   🚫 Not fixable by this skill ({n})
     - CODEOWNERS ignored on your plan — upgrade to Team to enforce
     - Required reviewers — upgrade to Team
     - Visibility change — use GitHub UI (business decision)
   
   🛡️ Branch protection on main
     - Currently: {"unprotected" | "protected — status_checks={list}"}
     - Offer activation? {"Yes — CI has passed at least once" | "Not yet — waiting for first green CI"}
   ```

4. **Per-item execute.** For each `y`, apply via MCP, record in manifest. For each `n`, skip and note in evidence table as "declined by student this run."

5. **If branch protection offered and approved:** apply with the proven status-check name from the last green CI run (extracted from checks API). Include administrators. Never override pre-existing protection without explicit diff + approval.

6. **Evidence table** (audit variant):
   ```
   ✅ Audit complete.
   
     Fixes applied:  {count}
     Declined:       {count}
     Manual items:   {count}
     Protection:     {"activated" | "still deferred" | "already active"}
   
   Re-run anytime: /eo-github audit
   ```

### Step 6 — Execute (post-approval)

Run in this exact order. If any sub-step fails, stop and roll back only what this invocation wrote (tracked with a manifest).

**Transient-failure taxonomy** — every MCP call in Step 6 inspects the error shape before escalating:

| Error | Action |
|-------|--------|
| 429 rate limit (Github API) | Read `X-RateLimit-Reset` / `Retry-After` if available. Print: "GitHub rate limit hit. Resets in {N} min. Re-run then." Exit cleanly. No rollback — nothing was written. |
| 422 on `create_repo` (repo appeared between precheck and execute — race) | Re-run Step 5 Mode 1 slug collision retry loop once. The remote `{default_owner}/{slug}` now exists; treat it as a new collision and ask for an alternate slug. Do NOT adopt it silently — we can't tell if it's truly ours. |
| 422 on settings write (invalid config combination, e.g., disabling squash+merge+rebase all at once) | Log the setting in the evidence table as "unapplied — {reason}"; continue with the next setting. Never abort Step 6b on a single 422. |
| 403 with `secondary rate limit` signal | Print: "GitHub secondary rate limit hit (abuse detection). Wait 60 seconds then retry. If repeated, reduce tool parallelism." Exit cleanly. |
| 5xx / timeout | Retry once after 5 seconds. On second failure, print the Step 4 network-error template and exit. |
| All other errors | Refuse with the raw error message + manifest of what was and was not written so far, plus a recovery suggestion. |

1. **Git init if needed:**
   ```
   if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
     git init -b main
   fi
   ```

2. **Ensure main branch:**
   ```
   current=$(git symbolic-ref --short HEAD 2>/dev/null || echo "")
   if [ "$current" != "main" ]; then
     git branch -m main || git checkout -b main
   fi
   ```

3. **First commit if needed:**
   ```
   if ! git rev-parse HEAD >/dev/null 2>&1; then
     git add -A
     git commit -m "chore(bootstrap): initial handoff"
   fi
   ```

4. **Create remote repo (Mode 1 only):** via MCP, `mcp__$github_mcp__create_repository(name=$slug, private=true, description, auto_init=false)`. The `auto_init=false` is critical — we'll seed the repo ourselves at Step 6a (so `push_files` has a base ref of our choosing, and there's no GitHub-generated README to collide with).

   Capture the `html_url` and `clone_url` (HTTPS — `clone_url`, NOT `ssh_url`).

5. **Wire remote (HTTPS, idempotent):**
   ```bash
   cd "$ROOT"
   git remote remove origin 2>/dev/null  # idempotent — clear stale remote
   git remote add origin "$clone_url"     # HTTPS, e.g. https://github.com/owner/slug.git
   ```

   We use HTTPS, NOT SSH, so the remote URL works without local SSH-key auth. The actual push happens via MCP in Step 6 — no `git push` from the founder's shell.

6. **Push files via MCP — autonomous, replaces local `git push` (v1.4.6):**

   This is the autonomous pipeline. NO `git push` from the founder's shell. NO `gh auth login` prompts. Works even when the founder has multiple GitHub accounts and the wrong one is the local-default.

   #### 6a. Bootstrap empty repo via `create_or_update_file`

   The Git Trees API (which `mcp__$github_mcp__push_files` wraps) requires a base ref to update. A freshly-created empty repo has no ref to base on. Seed it with one file via `create_or_update_file` (single-file API, works on empty repos):

   ```
   # Read local README.md, base64-encode the content
   if [[ -f "$ROOT/README.md" ]]; then
     readme_content=$(base64 < "$ROOT/README.md")
   else
     readme_content=$(echo -e "# $project_name\n\nBootstrap seed for push_files." | base64)
   fi

   mcp__$github_mcp__create_or_update_file(
     owner=$default_owner,
     repo=$slug,
     branch="main",
     path="README.md",
     content=$readme_content,
     message="seed: README.md (bootstrap empty repo for push_files)"
   )
   ```

   This creates commit #1 on `main`. From here, `push_files` works.

   #### 6b. Build chunks from local working tree

   Walk `$ROOT` filesystem (respecting `.gitignore`) and produce a list of `(path, content)` tuples. Chunk by **TOTAL DECODED BYTES** per chunk, NOT by file count:

   - Per-chunk byte budget: **200KB** (well under MCP/Read 256KB cap with margin for the API JSON envelope)
   - Per-file byte cap: **1MB** (skip larger; log to warnings — usually binaries or build outputs that shouldn't be in git anyway)
   - Excludes: `node_modules/`, `.next/`, `.env`, `.env.local`, `.git/`, `.DS_Store`, `*.log`
   - Chunk ordering: deterministic — sort paths alphabetically, pack greedily

   For each chunk:

   ```
   mcp__$github_mcp__push_files(
     owner=$default_owner,
     repo=$slug,
     branch="main",
     files=[ {path, content (base64)}, ... ],
     message="chunk N/M: <comma-sep first 3 file paths> + N more"
   )
   ```

   On error, retry once with the chunk split in half. If that fails, surface the specific error + which files were left behind. **Never silently drop files.**

   #### 6c. Verify via `list_commits` + reconcile local refs

   ```
   mcp__$github_mcp__list_commits(owner=$default_owner, repo=$slug, sha="main")
   ```

   Confirm: chunks + seed appear in expected order; final commit count matches expected; HEAD SHA matches the last chunk's commit.

   Then reconcile local with remote so `git status` is clean:

   ```bash
   cd "$ROOT"
   git fetch origin main
   git reset --soft origin/main   # local working-tree files match remote;
                                   # this just aligns the commit-history pointer.
   ```

   Produces clean state: `git status` shows no uncommitted changes; `git log` shows the same commits as `list_commits` returned.

   #### 6d. Print evidence table to founder (CEO-brief format)

   ```
   ✅ /eo-github — autonomous via MCP
   ──────────────────────────────────────────────
   Repo:        https://github.com/$default_owner/$slug   (private)
   Account:     $github_login (selected MCP: $github_mcp)
   Files:       N pushed in M chunks (P kB total)
   Skipped:     X files (>1MB, see warnings) | none
   Local:       remote origin set to HTTPS, working tree clean
   Verified:    M commits on remote (list_commits ✓)

   Next: continue your build. /eo-github does not block /7-eo-ship.
   ```

   **No `gh auth login` prompt to the founder.** Never. Account selection happened in Step 4.5 via MCP discovery.

7. **Create `dev` branch (team strategy only):** via MCP, not `git checkout`:

   ```
   mcp__$github_mcp__create_branch(owner=$default_owner, repo=$slug, branch="dev", from_branch="main")
   ```

### Step 6b — Align settings (Mode 1 always; Mode 2 unless `skip-settings`)

Apply each item from the best-practices matrix via MCP. Idempotent: reading current value first; skip if already correct. Record each write in the execution manifest for rollback.

Order:
1. **Repo settings** (`update_repository` or equivalent): `has_wiki`, `has_projects`, `has_discussions`, `allow_squash_merge`, `allow_merge_commit`, `allow_rebase_merge`, `delete_branch_on_merge`, `description`.
2. **Topics** (`replace_topics` / `set_topics`): merge preset + detected stack, dedupe, apply.
3. **Labels** (`create_label` per missing label): skip any label whose name already exists (case-insensitive).
4. **CODEOWNERS** (Team+/Enterprise only): if a `.github/CODEOWNERS` file exists locally it is already committed; skill does not write one. On free/pro plans, print: *"CODEOWNERS is ignored on your current plan. File retained but not enforced until Team plan."*

Any individual setting write that fails → log the failure in the evidence table, continue with the next. Never abort the whole alignment on a single 422/403 — report at the end.

Branch protection is **never applied at this step**. It is deferred to post-first-CI automation (see the dedicated section above).

### Step 7 — Evidence table

```
✅ GitHub set up.

  Repo:           {owner}/{repo}
  URL:            {html_url}
  Plan:           {free|pro|team|enterprise}
  Visibility:     private
  Default branch: main
  Strategy:       {trunk-only | dual-branch}
  Origin:         {clone_url}
  First push:     {commit_sha_short} "{subject}"
  dev branch:     {created + pushed | N/A (solo)}

Settings aligned:
  has_wiki=false  has_projects=false  has_discussions=false
  delete_branch_on_merge=true  squash-only merge  description set

Topics:           eo-microsaas {mena?} {stack tags}
Labels added:     {list or "none — all already present"}
Label skipped:    {list or "none"}

Deferred (apply later):
  - Branch protection on main (after first /7-eo-ship green CI)
  - CODEOWNERS enforcement ({"enabled on your plan" | "ignored on free/pro"})
  - LICENSE — {status}:
      {if present:}     present ({detected_name}) — no action needed
      {if absent:}      no LICENSE in the repo. Three common MicroSaaS choices:
                          • MIT       — permissive, copy/paste friendly (default pick)
                          • Apache-2  — adds explicit patent grant (B2B SaaS)
                          • Proprietary — add a `LICENSE` file saying
                            "All rights reserved. Contact {owner} for licensing."
                        Create via GitHub UI → Add file → Create new file →
                        name `LICENSE` → "Choose a license template".

Write failures (if any):
  {setting} — {reason} — fix manually in GitHub UI

Next:
  - /eo-guide will now detect your GitHub remote on next run
  - /7-eo-ship will push to this remote from now on
  - /eo-github audit  — re-check settings anytime
  - Flip to public when ready: GitHub UI → Settings → General → Visibility
```

### Step 8 — Failure rollback

If Step 6 fails between sub-steps:
- If step 4 succeeded (remote repo created) but step 5 or 6 failed → print:
  ```
  ⚠️ GitHub repo created at {url} but local wiring failed.
  
  The repo exists on GitHub but your local workspace is not connected.
  To recover:
    - Delete the remote (GitHub UI → Settings → Delete) and re-run
    - OR: manually set the remote: git remote add origin {clone_url} && git push -u origin main
  ```
- If step 5 succeeded but step 6 failed → remote is wired but nothing is pushed. Print remediation, leave state alone (next `git push` will succeed).

Never auto-delete a GitHub repo. That's destructive and the student must confirm.

---

## Anti-patterns

- **Silent remote creation.** Plan-mode preview is not optional. Every creation requires explicit `y`.
- **Force push to match local.** Never. If push is rejected, refuse with merge/rebase guidance.
- **Defaulting to public.** Students are pre-launch, identity is sensitive. Private always.
- **Using `gh` CLI as fallback when MCP is missing.** The contract is MCP-only. Fallbacks create drift between "this skill works" and "this skill works the way the student expects." Refuse cleanly and route to install MCP.
- **Adopting a non-empty remote.** Don't push into a repo with unrelated history. Refuse and let the student decide.
- **Hardcoding an org.** Always use the authenticated user as default owner. Let the student override if they want.
- **Offering plan-locked features.** Never show "required reviewers — on/off?" on a free plan. GitHub would silently ignore it and teach the student the wrong mental model.
- **Batch settings-fix without per-item approval (audit mode).** In Mode 4 every drifted item gets its own `y/n`. Students learn what changed and why. A blanket "apply all" hides the decisions.
- **Applying branch protection on creation.** Protection rules can't require status checks that have never run. Always defer to post-first-CI automation.
- **Renaming existing labels.** Mode 1 creates missing labels. Mode 4 adds missing labels. Neither renames or recolors existing labels — that's student UI drift territory, not bootstrap.
- **Creating `dev` for solo students.** One extra branch = two extra merge decisions per feature for zero benefit. Trunk-only until collaborators appear.
- **Creating a LICENSE for the student.** Licensing is a business decision. Evidence table prompts with MIT / Apache-2 / Proprietary named options + UI path; student chooses.
- **Infinite retry loops.** Slug collision caps at 3 tries; rate limits exit cleanly with wait-time; secondary rate limit exits without thrashing.
- **Silent adoption after 422-race.** If the repo appeared between precheck and create, treat it as a collision — ask for a new slug. Never push into a repo we didn't create this session.
- **Rolling back state we didn't write.** If a call fails before any write, say "no writes made" — don't dramatize rollback theater.
- **Conflating MCP-missing with MCP-auth-failed.** Two different fixes (install vs rotate PAT). Always distinguish before printing remediation.
- **Leaving a refuse path without a door.** Every error has a concrete next command or manual runbook. A student must never see "can't help" with no door.

---

## Integration

| Skill | Relationship |
|-------|--------------|
| `eo-dev-start` | Routes here when student picks option 1, 2, or 4+MCP. Passes mode hint. |
| `eo-guide` | Detects presence of GitHub remote and adjusts phase labels. Never invokes this skill directly. |
| `eo-dev-repair` | Never calls this skill. Remote state is not repairable — student runs `/eo-github` manually when ready. |
| `handover-bridge` | Independent. `handover-bridge` is git-aware but does not assume a remote. If remote exists when it runs, the first commit lands and push is deferred to `/7-eo-ship`. |

---

## Stuck-state exits

Every refuse path above names a concrete next door. Summary for the anxious student:

| Stuck on | Do this |
|----------|---------|
| MCP not installed | Step 2 Case A → install MCP, OR Step 2b manual fallback (text runbook). Sprint work continues meanwhile. |
| MCP auth failed (401/403) | Step 2 Case B → regenerate PAT, re-run. |
| GitHub API 5xx / network | Wait 2 min, re-run. If persistent, check https://www.githubstatus.com/. |
| Slug collision (Mode 1) | 3 retry attempts with suggestions. After 3 fails → pick offline, come back. |
| Non-empty remote (Mode 2) | 4 labeled exits (A/B/C/D). Pick the one that matches your situation. |
| Origin already set | Use normal `git push` or `/eo-ship`. If origin is wrong, `git remote set-url` manually then re-run. |
| Push rejected (non-fast-forward) | `git pull --rebase origin main && git push -u origin main`. No force push. |
| Rate limit 429 | Retry-After time printed. Re-run then. |
| Create race (422) | Slug-collision loop re-fires. Pick another slug. |
| First CI never runs | Branch protection stays deferred. No harm. `/eo-github audit` offers activation after each next ship. |

If none of the above describes the situation → the student should run `/eo-guide` for a state-machine diagnostic, or re-read this section with the error message in hand.

---

## Self-score protocol

| # | Check | Threshold |
|---|-------|-----------|
| 1 | MCP precheck fired and refused when `mcp__github__*` missing (Case A) | must pass |
| 2 | MCP auth-failure routed to Case B with PAT-specific remediation (distinct from Case A) | must pass |
| 3 | Manual fallback offered when student replies "manual" | must pass |
| 4 | Existing-origin precheck refused when origin is already set (Modes 1 & 2) | must pass |
| 5 | Default owner read from MCP (never hardcoded) | must pass |
| 6 | Plan-mode preview shown before any remote creation, `git remote add`, or settings write | must pass |
| 7 | Visibility defaulted to `private` | must pass |
| 8 | Mode 2 refused on non-empty remote with 4 labeled exits (A/B/C/D) | must pass |
| 9 | Git init happened only when `.git` was absent | must pass |
| 10 | First commit created only when no prior commit existed | must pass |
| 11 | No force push anywhere in the path | must pass |
| 12 | Evidence table post-success with repo URL + push sha | must pass |
| 13 | Slug passed all naming rules (lowercase, length, reserved-list, no trailing hyphen) | must pass |
| 14 | Slug collision retry capped at 3 attempts with suggestions | must pass |
| 15 | Plan detected before offering plan-locked features (required reviewers, CODEOWNERS enforcement) | must pass |
| 16 | Branch strategy picked from collaborator count, not assumed | must pass |
| 17 | Branch protection deferred to post-first-CI (not applied at creation) | must pass |
| 18 | Mode 4 audit asked per-item `y/n` on drifted settings (no batch apply) | must pass |
| 19 | Settings write failures logged in evidence table, alignment did not abort on first error | must pass |
| 20 | `dev` branch created only when team strategy (≥2 collaborators) | must pass |
| 21 | No LICENSE auto-created — evidence table prompts with 3 named options + UI path | must pass |
| 22 | 429 / secondary rate limit / 422-race handled with named remediation, no rollback of unwritten state | must pass |
| 23 | Every refuse path names a concrete next door (no terminal "stuck" state) | must pass |

Threshold: 23/23. Below = bug → capture in `.claude/lessons.md`.
