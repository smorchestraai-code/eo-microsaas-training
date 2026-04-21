# destructive-blocker.ps1 — Windows PowerShell port of the bash destructive-blocker hook.
# Reads stdin JSON payload from Claude Code PreToolUse(Bash), checks the requested command against
# the shared rules.json blocklist, and emits the decision JSON to stdout.
#
# Wire-up example in ~/.claude/settings.json on Windows:
#   "command": "pwsh -NoProfile -File C:\\Users\\<you>\\.claude\\hooks\\destructive-blocker.ps1"
#
# Rules source: eo-microsaas-dev/templates/hooks-shared/rules.json (deployed to ~/.claude/hooks/rules.json by install).

$ErrorActionPreference = 'Stop'

function Emit-Allow {
    '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}' | Write-Output
    exit 0
}

function Emit-Deny([string]$reason) {
    $payload = @{
        hookSpecificOutput = @{
            hookEventName            = 'PreToolUse'
            permissionDecision       = 'deny'
            permissionDecisionReason = $reason
        }
    }
    $payload | ConvertTo-Json -Compress -Depth 5 | Write-Output
    exit 0
}

# Read the full stdin payload.
$raw = [Console]::In.ReadToEnd()
if ([string]::IsNullOrWhiteSpace($raw)) { Emit-Allow }

try {
    $input = $raw | ConvertFrom-Json
} catch {
    Emit-Allow  # Can't parse → don't block the user; fail open with allow, log to stderr.
}

$cmd = $input.tool_input.command
if ([string]::IsNullOrWhiteSpace($cmd)) { Emit-Allow }

# Locate rules.json — prefer the per-user install path, fall back to template location for dev.
$rulesPath = Join-Path $HOME '.claude\hooks\rules.json'
if (-not (Test-Path $rulesPath)) {
    $rulesPath = Join-Path $PSScriptRoot '..\hooks-shared\rules.json'
}
if (-not (Test-Path $rulesPath)) { Emit-Allow }

$rules = Get-Content $rulesPath -Raw | ConvertFrom-Json

foreach ($pattern in $rules.destructive.patterns) {
    if ($cmd -match "(?i)$pattern") {
        Emit-Deny "BLOCKED: Destructive command ($pattern). Double-check what you intend."
    }
}

Emit-Allow
