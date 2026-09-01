param(
    [switch]$Verbose
)

$ErrorActionPreference = 'Stop'
$RepoRoot = $PSScriptRoot

function Log {
    param([string]$Message)
    if ($Verbose) { Write-Host "[+] $Message" }
}

Log "Repo root: $RepoRoot"

# 1. Run apm install --target opencode
Log "Running: apm install --target opencode"
apm install --target opencode
if ($LASTEXITCODE -ne 0) {
    Write-Error "apm install --target opencode failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

# 2. Copy skills from .agents/skills/ to .opencode/skills/
$SrcSkillsDir = Join-Path $RepoRoot '.agents' 'skills'
$DstSkillsDir = Join-Path $RepoRoot '.opencode' 'skills'

if (-not (Test-Path -LiteralPath $SrcSkillsDir)) {
    Write-Error "Source skills directory not found: $SrcSkillsDir"
    exit 1
}

Log "Copying skills from $SrcSkillsDir to $DstSkillsDir"
# Create destination root if needed
if (-not (Test-Path -LiteralPath $DstSkillsDir)) {
    New-Item -ItemType Directory -Path $DstSkillsDir -Force | Out-Null
}

Get-ChildItem -LiteralPath $SrcSkillsDir -Directory | ForEach-Object {
    $SkillName = $_.Name
    $DstSkillDir = Join-Path $DstSkillsDir $SkillName

    # Remove stale copy first so we get a clean deploy
    if (Test-Path -LiteralPath $DstSkillDir) {
        Remove-Item -LiteralPath $DstSkillDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $DstSkillDir -Force | Out-Null

    Copy-Item -LiteralPath $_.FullName -Destination $DstSkillsDir -Recurse -Force
    Log "Copied skill: $SkillName"
}

# 3. Fix frontmatter in .opencode/skills/* and .opencode/agents/*
#    - Remove opencode-incompatible keys: user-invocable, disable-model-invocation, allowed-tools, model
#    - Keep: name, description, license, metadata

function Fix-Frontmatter {
    param([string]$FilePath)

    $content = Get-Content -LiteralPath $FilePath -Raw
    if (-not $content.StartsWith('---')) { return }

    $endMarker = $content.IndexOf('---', 3)
    if ($endMarker -lt 0) { return }

    $frontmatter = $content.Substring(3, $endMarker - 3)
    $body = $content.Substring($endMarker + 3)

    $keysToRemove = @(
        'user-invocable'
        'disable-model-invocation'
        'allowed-tools'
        'model'
    )

    $lines = $frontmatter -split "`n"
    $filtered = [System.Collections.Generic.List[string]]::new()
    $skip = $false

    foreach ($line in $lines) {
        $trimmed = $line.Trim()

        # Skip the value lines of a YAML dash-list key we already matched
        if ($skip) {
            if ($trimmed.StartsWith('- ') -and -not $trimmed.StartsWith('- -')) {
                continue
            }
            $skip = $false
        }

        # Check scalar keys to remove
        $matchedScalar = $false
        foreach ($key in $keysToRemove) {
            if ($trimmed -match "^${key}:\s*" -and -not $trimmed.StartsWith('- ')) {
                $matchedScalar = $true
                $skip = $true
                break
            }
        }
        if ($matchedScalar) { continue }

        # Convert tools: [A, B, C] -> tools: {A: true, B: true, C: true}
        if ($trimmed -match '^tools:\s*\[(.+)\]\s*$') {
            $toolNames = $Matches[1] -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' }
            $toolMap = ($toolNames | ForEach-Object { "${_}: true" }) -join ', '
            $filtered.Add("tools: {${toolMap}}") | Out-Null
            $skip = $false
            continue
        }

        # Convert tools: followed by dash-list (next lines) -> tools: {A: true, ...}
        if ($trimmed -match '^tools:\s*$') {
            $toolList = [System.Collections.Generic.List[string]]::new()
            $lookahead = $filtered.Count
            :scan for ($j = $lines.IndexOf($line) + 1; $j -lt $lines.Count; $j++) {
                $nextTrimmed = $lines[$j].Trim()
                if ($nextTrimmed -match '^\-\s+(.+)$') {
                    $toolList.Add($Matches[1].Trim()) | Out-Null
                } else {
                    break
                }
            }
            if ($toolList.Count -gt 0) {
                $toolMap = ($toolList | ForEach-Object { "${_}: true" }) -join ', '
                $filtered.Add("tools: {${toolMap}}") | Out-Null
                $skip = $true
                continue
            }
        }

        $filtered.Add($line) | Out-Null
    }

    # Remove leading blank lines from frontmatter
    while ($filtered.Count -gt 0 -and [string]::IsNullOrWhiteSpace($filtered[0])) {
        $filtered.RemoveAt(0)
    }
    # Remove trailing blank lines from frontmatter before closing marker
    while ($filtered.Count -gt 0 -and [string]::IsNullOrWhiteSpace($filtered[$filtered.Count - 1])) {
        $filtered.RemoveAt($filtered.Count - 1)
    }

    $newContent = "---`n" + ($filtered -join "`n") + "`n---" + $body
    Set-Content -LiteralPath $FilePath -Value $newContent -NoNewline
    Log "Fixed frontmatter: $FilePath"
}

# Fix all SKILL.md files under .opencode/skills/
Get-ChildItem -LiteralPath $DstSkillsDir -Recurse -Filter 'SKILL.md' -File | ForEach-Object {
    Fix-Frontmatter $_.FullName
}

# Fix all agent .md files under .opencode/agents/
$AgentsDir = Join-Path $RepoRoot '.opencode' 'agents'
if (Test-Path -LiteralPath $AgentsDir) {
    Get-ChildItem -LiteralPath $AgentsDir -Filter '*.md' -File | ForEach-Object {
        Fix-Frontmatter $_.FullName
    }
}

Write-Host "Done. OpenCode deployment complete."
