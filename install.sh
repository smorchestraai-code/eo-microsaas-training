#!/bin/bash
# EO MicroSaaS Student — Claude Code install script
# Standalone setup: free GitHub account, no SMOrchestra infra access.
# Usage: bash install.sh

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  EO MicroSaaS Student — Claude Code Bootstrap              ║"
echo "║  Version: 1.1 · 2026-04-21                                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo

# ──────────────────────────────────────────────────────────────────
# Phase 1: Check OS + prerequisites
# ──────────────────────────────────────────────────────────────────
echo "→ Checking OS..."
OS=$(uname -s)
case "$OS" in
  Darwin) echo "  macOS detected" ;;
  Linux)  echo "  Linux detected" ;;
  *) echo "  ERROR: unsupported OS ($OS). Mac or Linux only." && exit 1 ;;
esac

# ──────────────────────────────────────────────────────────────────
# Phase 2: Install base tools
# ──────────────────────────────────────────────────────────────────
echo
echo "→ [1/6] Installing Homebrew (macOS) / verifying apt (Linux)..."
if [ "$OS" = "Darwin" ] && ! command -v brew >/dev/null 2>&1; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
  echo "  ✓ package manager available"
fi

echo
echo "→ [2/6] Installing Node.js 22..."
if ! command -v node >/dev/null 2>&1 || ! node --version | grep -q "v22"; then
  if [ "$OS" = "Darwin" ]; then
    brew install node@22
    brew link --overwrite node@22 2>/dev/null || true
  else
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
    sudo apt install -y nodejs
  fi
fi
node --version | grep -q "v22" && echo "  ✓ Node 22 ready" || { echo "  ✗ Node 22 install failed"; exit 1; }

echo
echo "→ [3/6] Installing Bun (needed for gstack)..."
if ! command -v bun >/dev/null 2>&1; then
  curl -fsSL https://bun.sh/install | bash
  export BUN_INSTALL=$HOME/.bun
  export PATH=$BUN_INSTALL/bin:$PATH
fi
bun --version 2>/dev/null | head -1 && echo "  ✓ Bun installed" || { echo "  ✗ Bun install failed — add ~/.bun/bin to PATH and re-run"; exit 1; }

echo
echo "→ [4/6] Installing Claude Code..."
if ! command -v claude >/dev/null 2>&1; then
  npm install -g @anthropic-ai/claude-code
fi
claude --version && echo "  ✓ Claude Code ready"

echo
echo "→ [5/6] Installing git + SSH key check..."
git --version >/dev/null 2>&1 || { echo "  ✗ Install git first"; exit 1; }
if [ ! -f ~/.ssh/id_ed25519 ] && [ ! -f ~/.ssh/id_rsa ]; then
  echo "  ⚠ No SSH key found at ~/.ssh/id_ed25519 or id_rsa"
  echo "  Generate one with:"
  echo "    ssh-keygen -t ed25519 -C 'your-email@example.com'"
  echo "  Then add the .pub content to github.com/settings/keys"
else
  echo "  ✓ SSH key present"
fi

echo
echo "→ [6/6] Installing GitHub CLI (gh)..."
if ! command -v gh >/dev/null 2>&1; then
  if [ "$OS" = "Darwin" ]; then brew install gh
  else
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    sudo apt update && sudo apt install -y gh
  fi
fi
gh --version | head -1 && echo "  ✓ gh CLI ready"

# ──────────────────────────────────────────────────────────────────
# Phase 3: Claude Code config + skill suites
# ──────────────────────────────────────────────────────────────────
echo
echo "→ [Phase 3] Setting up Claude Code config + skills..."
mkdir -p ~/.claude/skills

echo
echo "  • Installing gstack (Garry Tan's engineering workflow)..."
if [ ! -d ~/.claude/skills/gstack ]; then
  git clone --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
  cd ~/.claude/skills/gstack && ./setup
  cd - > /dev/null
fi

echo
echo "  • Installing superpowers (TDD, debugging patterns)..."
if [ ! -d ~/.claude/skills/superpowers ]; then
  git clone --depth 1 https://github.com/obra/superpowers.git ~/.claude/skills/superpowers
fi

# Install the eo-microsaas-dev plugin via Claude Code marketplace (proper registration path)
echo
echo "  • Registering eo-microsaas-training marketplace + installing eo-microsaas-dev..."

# Add marketplace (one-time, idempotent)
if claude plugin marketplace list 2>/dev/null | grep -q "eo-microsaas-training"; then
  echo "    marketplace eo-microsaas-training already registered — refreshing"
  claude plugin marketplace update eo-microsaas-training 2>&1 | tail -1
else
  claude plugin marketplace add smorchestraai-code/eo-microsaas-training 2>&1 | tail -1
fi

# Install the plugin
claude plugin install eo-microsaas-dev@eo-microsaas-training 2>&1 | tail -1
echo "    Commands available after Claude Code restart: /eo-guide /eo-status /eo-plan /eo-code /eo-review /eo-score /eo-bridge-gaps /eo-ship /eo-debug /eo-retro"

# Legacy eo-quality-guide shim (kept as fallback for students without the plugin)
echo
echo "  • Installing legacy quality guide (fallback)..."
mkdir -p ~/.claude/skills/eo-quality-guide
cat > ~/.claude/skills/eo-quality-guide/SKILL.md << 'EOSKILL'
# EO Quality Guide — Student Edition

## What this is
A lightweight replacement for SMOrchestra's internal 5-hat scoring system.
Students without access to smorch-brain use this guide for self-review.

## Before every PR, answer these 5 questions honestly (1-10 each):

**Product (1-10)**
- Does this match the BRD / user story you wrote?
- Would a real user from your ICP actually use it?

**Architecture (1-10)**
- Is the code organized into logical modules?
- Can you explain the data flow in 2 sentences?

**Engineering (1-10)**
- Are there tests? (Aim for 60%+ coverage)
- Is error handling present for every external call?

**QA (1-10)**
- Have you clicked through every user flow?
- Tested empty state, error state, and edge cases?

**UX (1-10)**
- Does it work on mobile (375px wide)?
- Arabic RTL if your ICP is MENA?
- Any console errors?

**Composite = average × 10**

| Score | Decision |
|-------|----------|
| 90+ | Ship |
| 80-89 | Fix gaps before ship |
| <80 | Don't ship — address issues |

Save each score to `docs/qa-scores/YYYY-MM-DD.md` in your project.
Track improvement over time.
EOSKILL
echo "  ✓ EO quality guide installed at ~/.claude/skills/eo-quality-guide/"

# ──────────────────────────────────────────────────────────────────
# Phase 4: Claude Code hooks (student-appropriate)
# ──────────────────────────────────────────────────────────────────
echo
echo "→ [Phase 4] Installing Claude Code hooks + CLAUDE.md..."

PLAYBOOK_DIR="$(cd "$(dirname "$0")" && pwd)"

# Deploy the student settings.json (hooks)
# Accepts either new name (settings.json) or legacy (student-settings.json)
SETTINGS_SRC=""
if [ -f "$PLAYBOOK_DIR/settings.json" ]; then
  SETTINGS_SRC="$PLAYBOOK_DIR/settings.json"
elif [ -f "$PLAYBOOK_DIR/student-settings.json" ]; then
  SETTINGS_SRC="$PLAYBOOK_DIR/student-settings.json"
fi
if [ -n "$SETTINGS_SRC" ]; then
  cp "$SETTINGS_SRC" ~/.claude/settings.json
  echo "  ✓ settings.json installed (hooks: destructive-blocker + secret-scanner)"
else
  echo "  ⚠ No settings.json found in playbook dir — skipping"
fi

# Deploy the student CLAUDE.md as their global config
# Accepts either new name (CLAUDE.md) or legacy (CLAUDE-STUDENT-PLAYBOOK.md)
CLAUDE_SRC=""
if [ -f "$PLAYBOOK_DIR/CLAUDE.md" ]; then
  CLAUDE_SRC="$PLAYBOOK_DIR/CLAUDE.md"
elif [ -f "$PLAYBOOK_DIR/CLAUDE-STUDENT-PLAYBOOK.md" ]; then
  CLAUDE_SRC="$PLAYBOOK_DIR/CLAUDE-STUDENT-PLAYBOOK.md"
fi
if [ -n "$CLAUDE_SRC" ]; then
  if [ ! -f ~/.claude/CLAUDE.md ]; then
    cp "$CLAUDE_SRC" ~/.claude/CLAUDE.md
    echo "  ✓ CLAUDE.md (student playbook) installed as global Claude Code instructions"
  else
    echo "  ⚠ ~/.claude/CLAUDE.md already exists — backing up to CLAUDE.md.bak"
    mv ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.bak
    cp "$CLAUDE_SRC" ~/.claude/CLAUDE.md
    echo "  ✓ CLAUDE.md replaced (old saved as CLAUDE.md.bak)"
  fi
fi

# ──────────────────────────────────────────────────────────────────
# Phase 5: Verify
# ──────────────────────────────────────────────────────────────────
echo
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Setup Complete — Verification                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo
echo "  Node:         $(node --version 2>/dev/null || echo MISSING)"
echo "  Bun:          $(bun --version 2>/dev/null || echo 'MISSING — re-source shell profile')"
echo "  Claude Code:  $(claude --version 2>/dev/null || echo MISSING)"
echo "  git:          $(git --version 2>/dev/null || echo MISSING)"
echo "  gh CLI:       $(gh --version 2>/dev/null | head -1 || echo MISSING)"
echo
echo "  ~/.claude/skills/gstack:        $([ -d ~/.claude/skills/gstack ] && echo '✓ installed' || echo '✗ MISSING')"
echo "  ~/.claude/skills/superpowers:   $([ -d ~/.claude/skills/superpowers ] && echo '✓ installed' || echo '✗ MISSING')"
echo "  ~/.claude/skills/eo-quality-guide: $([ -d ~/.claude/skills/eo-quality-guide ] && echo '✓ installed' || echo '✗ MISSING')"
echo "  eo-microsaas-dev plugin: $(claude plugin list 2>/dev/null | grep -q 'eo-microsaas-dev@eo-microsaas-training' && echo '✓ installed (via marketplace)' || echo '✗ MISSING — run claude plugin install eo-microsaas-dev@eo-microsaas-training')"
echo "  ~/.claude/CLAUDE.md:            $([ -f ~/.claude/CLAUDE.md ] && echo '✓ installed' || echo '✗ MISSING')"
echo "  ~/.claude/settings.json:        $([ -f ~/.claude/settings.json ] && echo '✓ installed' || echo '✗ MISSING')"
echo
echo "  Next steps:"
echo "  1. cd to any project directory"
echo "  2. Run: claude"
echo "  3. Read ~/.claude/CLAUDE.md (your student playbook)"
echo "  4. Follow the daily workflow in the playbook"
echo
echo "  Questions? → docs/eo-microsaas-students/FAQ-STUDENTS.md"
echo "  Community → Discord / Telegram (link in your onboarding email)"
echo
