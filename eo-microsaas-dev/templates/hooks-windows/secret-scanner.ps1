# secret-scanner.ps1 — Windows PowerShell port of the bash secret-scanner hook.
# Reads stdin JSON payload from Claude Code PreToolUse(Write|Edit), checks `content` or `new_string`
# against rules.json secret regexes, and blocks unless the target file is on the allow-list.
#
# Wire-up example in ~/.claude/settings.json on Windows:
#   "command": "pwsh -NoProfile -File C:\\Users\\<you>\\.claude\\hooks\\secret-scanner.ps1"
#
# Regex semantics note: patterns in rules.json use character-class splits (e.g. s[k]- instead of sk-)
# so the rules file itself doesn't self-trip. [x] matches x — no special handling needed here.

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

$raw = [Console]::In.ReadToEnd()
if ([string]::IsNullOrWhiteSpace($raw)) { Emit-Allow }

try {
    $input = $raw | ConvertFrom-Json
} catch {
    Emit-Allow
}

# Pick either `content` (Write) or `new_string` (Edit).
$content = $input.tool_input.content
if ([string]::IsNullOrWhiteSpace($content)) { $content = $input.tool_input.new_string }
if ([string]::IsNullOrWhiteSpace($content)) { Emit-Allow }

$filePath = $input.tool_input.file_path
if ([string]::IsNullOrWhiteSpace($filePath)) { $filePath = '' }

# Load shared rules.
$rulesPath = Join-Path $HOME '.claude\hooks\rules.json'
if (-not (Test-Path $rulesPath)) {
    $rulesPath = Join-Path $PSScriptRoot '..\hooks-shared\rules.json'
}
if (-not (Test-Path $rulesPath)) { Emit-Allow }

$rules = Get-Content $rulesPath -Raw | ConvertFrom-Json

# If the target file is on the allow-list, skip scanning (documentation / template files
# legitimately reference env var names like `OP` + `ENAI_API_KEY`).
foreach ($allowed in $rules.secrets.allow_list_files) {
    if ($filePath -match [regex]::Escape($allowed)) { Emit-Allow }
}

foreach ($entry in $rules.secrets.patterns) {
    if ($content -match "(?i)$($entry.regex)") {
        Emit-Deny "BLOCKED: Secret matched rule '$($entry.name)'. Move it to a .env file (gitignored)."
    }
}

Emit-Allow
