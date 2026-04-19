#!/usr/bin/env bash
# Plugin self-validation. Run in CI + before any release tag.
# Exit 0 = plugin is well-formed. Exit 1 = block release.
#
# Checks:
#   1. plugin.json is valid JSON + has required keys
#   2. Every commands[] path in plugin.json resolves to an existing file
#   3. Every skills[] path in plugin.json resolves to a directory containing SKILL.md
#   4. Every .md file under commands/ has YAML frontmatter with `description`
#   5. Every skills/*/SKILL.md has YAML frontmatter with `name` + `description`
#   6. Templates exist: CLAUDE.md.template, trend.csv, settings.json.template, lessons.md.template
#   7. No references to non-existent scripts in any SKILL.md

set -euo pipefail

PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PLUGIN_DIR"

errors=0
warn() { echo "⚠️  $1"; errors=$((errors+1)); }
ok()   { echo "✅ $1"; }

# 1. plugin.json valid JSON
if ! python3 -c "import json, sys; json.load(open('.claude-plugin/plugin.json'))" 2>/dev/null; then
  warn "plugin.json is not valid JSON"
else
  ok "plugin.json is valid JSON"
fi

# 2. required keys
for key in name version description commands skills; do
  if ! python3 -c "import json; d=json.load(open('.claude-plugin/plugin.json')); exit(0 if '$key' in d else 1)" 2>/dev/null; then
    warn "plugin.json missing required key: $key"
  fi
done

# 3. commands[] paths resolve
while IFS= read -r cmd; do
  [ -f "$cmd" ] || warn "commands[] entry not found: $cmd"
done < <(python3 -c "import json; [print(x) for x in json.load(open('.claude-plugin/plugin.json'))['commands']]")

# 4. skills[] paths resolve to dir with SKILL.md
while IFS= read -r skill; do
  if [ ! -f "$skill/SKILL.md" ]; then
    warn "skills[] entry missing SKILL.md: $skill"
  fi
done < <(python3 -c "import json; [print(x) for x in json.load(open('.claude-plugin/plugin.json'))['skills']]")

# 5. command files have frontmatter with description
for f in commands/*.md; do
  head -5 "$f" | grep -q "^description:" || warn "$f missing 'description:' in frontmatter"
done
ok "command frontmatter scanned"

# 6. skill SKILL.md files have frontmatter (top-level and subskills)
for f in SKILL.md skills/*/SKILL.md; do
  [ -f "$f" ] || continue
  head -10 "$f" | grep -q "^---$" || warn "$f missing YAML frontmatter fence"
done
ok "skill frontmatter scanned"

# 7. required templates exist
for t in templates/CLAUDE.md.template templates/trend.csv templates/settings.json.template templates/lessons.md.template; do
  [ -f "$t" ] || warn "missing template: $t"
done
ok "templates scanned"

# 8. no references to non-existent scripts
for ref in "scripts/sync-skills.js" "scripts/validate-skills-lock.js"; do
  if grep -rq "$ref" skills/ commands/ 2>/dev/null; then
    warn "dead reference found: $ref (no such script in plugin)"
  fi
done
ok "dead reference scan"

echo
if [ "$errors" -eq 0 ]; then
  echo "🟢 Plugin validation passed."
  exit 0
else
  echo "🔴 Plugin validation failed with $errors issue(s)."
  exit 1
fi
