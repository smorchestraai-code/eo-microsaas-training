# Windows PowerShell hooks

Port of the bash `destructive-blocker` + `secret-scanner` hooks for students on native Windows PowerShell (not WSL2).

## When to use

| Student path | Hooks to deploy |
|---|---|
| macOS | bash (from `settings.json`) |
| WSL2 Ubuntu | bash (runs inside WSL) |
| Native Windows PowerShell | these `.ps1` files |
| Codespaces / Gitpod | bash (devcontainer is Linux) |

## Requirements

- PowerShell 7+ (`pwsh`) — install via `winget install Microsoft.PowerShell`.
- `jq` NOT required — PowerShell has `ConvertFrom-Json` built in.

## Install

```powershell
# One-time setup
mkdir $HOME\.claude\hooks -Force
Copy-Item destructive-blocker.ps1 $HOME\.claude\hooks\
Copy-Item secret-scanner.ps1 $HOME\.claude\hooks\
Copy-Item ..\hooks-shared\rules.json $HOME\.claude\hooks\

# Wire up in ~/.claude/settings.json (Windows path)
#   "command": "pwsh -NoProfile -File C:\\Users\\<you>\\.claude\\hooks\\destructive-blocker.ps1"
#   "command": "pwsh -NoProfile -File C:\\Users\\<you>\\.claude\\hooks\\secret-scanner.ps1"
```

`install.sh` on WSL handles this automatically; for native PowerShell students, `install.ps1` (future) will ship the wiring.

## Smoke test

```powershell
# Should emit permissionDecision=deny
'{"tool_input":{"command":"git push --force origin main"}}' | pwsh -NoProfile -File .\destructive-blocker.ps1

# Should emit permissionDecision=allow
'{"tool_input":{"command":"ls"}}' | pwsh -NoProfile -File .\destructive-blocker.ps1
```

## Single source of truth

Both `.ps1` files read `rules.json` from `..\hooks-shared\rules.json`. Never edit the regex list in the `.ps1` itself — it goes in `rules.json` so bash + PowerShell stay in sync. Bump `rules.json.version` on every change.

## Fail-open policy

If stdin is empty, JSON parse fails, or `rules.json` is missing, the hook emits `allow`. Blocking the user because of a hook bug is worse than missing one destructive command — the student's own eyes are the last line of defense.
