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
#
# Skills (SKILL.md): OpenCode only recognizes name, description, license,
#   compatibility, metadata. All other keys are ignored. We strip
#   Claude-Code-specific keys for cleanliness.
#
# Agents (*.md): OpenCode derives the agent name from the filename, not
#   frontmatter. Recognized keys are description, mode, model, temperature,
#   permission, tools (deprecated), steps, disable, hidden, color, top_p, etc.
#   Unknown keys are passed through to the provider as model options -- junk.
#   We strip: name, user-invocable, disable-model-invocation, allowed-tools,
#   targets, model (invalid format without provider/ prefix).
#   We convert: tools: [A, B, C] -> permission: block with deny-all default
#   + allow for each mapped tool, using OpenCode's lowercase tool names.

# Map Claude Code tool names to OpenCode permission keys
# OpenCode permission keys: read, edit, glob, grep, list, bash, task,
#   external_directory, todowrite, webfetch, websearch, lsp, skill, question
$script:ToolNameMap = [System.Collections.Generic.Dictionary[string,string]]::new()
$script:ToolNameMap['Read'] = 'read'
$script:ToolNameMap['Write'] = 'edit'
$script:ToolNameMap['Edit'] = 'edit'
$script:ToolNameMap['Glob'] = 'glob'
$script:ToolNameMap['Grep'] = 'grep'
$script:ToolNameMap['Bash'] = 'bash'
$script:ToolNameMap['WebFetch'] = 'webfetch'
$script:ToolNameMap['WebSearch'] = 'websearch'
$script:ToolNameMap['TaskCreate'] = 'task'
$script:ToolNameMap['TodoWrite'] = 'todowrite'
$script:ToolNameMap['List'] = 'list'
$script:ToolNameMap['task'] = 'task'
$script:ToolNameMap['read'] = 'read'
$script:ToolNameMap['edit'] = 'edit'
$script:ToolNameMap['write'] = 'edit'
$script:ToolNameMap['glob'] = 'glob'
$script:ToolNameMap['grep'] = 'grep'
$script:ToolNameMap['bash'] = 'bash'
$script:ToolNameMap['webfetch'] = 'webfetch'
$script:ToolNameMap['websearch'] = 'websearch'
$script:ToolNameMap['todowrite'] = 'todowrite'
$script:ToolNameMap['execute'] = 'bash'
$script:ToolNameMap['search'] = 'grep'
$script:ToolNameMap['web'] = 'webfetch'
$script:ToolNameMap['agent'] = 'task'
$script:ToolNameMap['todo'] = 'todowrite'

function Convert-ToolsToPermission {
    param([string[]]$ToolNames)

    $permKeys = [System.Collections.Generic.List[string]]::new()
    $seen = @{}
    foreach ($t in $ToolNames) {
        $mapped = $null
        if ($script:ToolNameMap.ContainsKey($t)) {
            $mapped = $script:ToolNameMap[$t]
        }
        if ($mapped -and -not $seen.ContainsKey($mapped)) {
            $permKeys.Add($mapped) | Out-Null
            $seen[$mapped] = $true
        }
    }

    if ($permKeys.Count -eq 0) { return $null }

    # Build permission block: deny everything by default, allow mapped tools
    $lines = @('permission:')
    $lines += "  `"*`": deny"
    foreach ($k in $permKeys) {
        $lines += "  ${k}: allow"
    }
    return ($lines -join "`n")
}

function Fix-SkillFrontmatter {
    param([string]$FilePath)

    $content = Get-Content -LiteralPath $FilePath -Raw
    if (-not $content.StartsWith('---')) { return }

    $endMarker = $content.IndexOf('---', 3)
    if ($endMarker -lt 0) { return }

    $frontmatter = $content.Substring(3, $endMarker - 3)
    $body = $content.Substring($endMarker + 3)

    # Keys to strip (Claude-Code-specific, not recognized by OpenCode skills)
    $keysToRemove = @(
        'user-invocable'
        'disable-model-invocation'
        'allowed-tools'
    )

    $lines = $frontmatter -split "`n"
    $filtered = [System.Collections.Generic.List[string]]::new()
    $skip = $false
    $lineIndex = 0

    while ($lineIndex -lt $lines.Count) {
        $line = $lines[$lineIndex]
        $trimmed = $line.Trim()
        $lineIndex++

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
    Log "Fixed skill frontmatter: $FilePath"
}

function Fix-AgentFrontmatter {
    param([string]$FilePath)

    $content = Get-Content -LiteralPath $FilePath -Raw
    if (-not $content.StartsWith('---')) { return }

    $endMarker = $content.IndexOf('---', 3)
    if ($endMarker -lt 0) { return }

    $frontmatter = $content.Substring(3, $endMarker - 3)
    $body = $content.Substring($endMarker + 3)

    # Keys to strip entirely (unknown to OpenCode, would be passed as junk
    # to the provider). model is stripped because the source value
    # (e.g. "claude-sonnet-5") lacks the required provider/ prefix.
    $keysToRemove = @(
        'name'
        'user-invocable'
        'disable-model-invocation'
        'allowed-tools'
        'model'
        'targets'
    )

    $lines = $frontmatter -split "`n"
    $filtered = [System.Collections.Generic.List[string]]::new()
    $skip = $false
    $lineIndex = 0

    while ($lineIndex -lt $lines.Count) {
        $line = $lines[$lineIndex]
        $trimmed = $line.Trim()
        $lineIndex++

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

        # Convert tools: [A, B, C] -> permission block
        if ($trimmed -match '^tools:\s*\[(.+)\]\s*$') {
            $toolNames = $Matches[1] -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' }
            $permBlock = Convert-ToolsToPermission $toolNames
            if ($permBlock) {
                $filtered.Add($permBlock) | Out-Null
            }
            $skip = $false
            continue
        }

        # Convert tools: followed by dash-list -> permission block
        if ($trimmed -match '^tools:\s*$') {
            $toolList = [System.Collections.Generic.List[string]]::new()
            while ($lineIndex -lt $lines.Count) {
                $nextTrimmed = $lines[$lineIndex].Trim()
                if ($nextTrimmed -match '^\-\s+(.+)$') {
                    $toolList.Add($Matches[1].Trim()) | Out-Null
                    $lineIndex++
                } else {
                    break
                }
            }
            if ($toolList.Count -gt 0) {
                $permBlock = Convert-ToolsToPermission $toolList
                if ($permBlock) {
                    $filtered.Add($permBlock) | Out-Null
                }
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
    Log "Fixed agent frontmatter: $FilePath"
}

# Fix all SKILL.md files under .opencode/skills/
Get-ChildItem -LiteralPath $DstSkillsDir -Recurse -Filter 'SKILL.md' -File | ForEach-Object {
    Fix-SkillFrontmatter $_.FullName
}

# Fix all agent .md files under .opencode/agents/
$AgentsDir = Join-Path $RepoRoot '.opencode' 'agents'
if (Test-Path -LiteralPath $AgentsDir) {
    Get-ChildItem -LiteralPath $AgentsDir -Filter '*.md' -File | ForEach-Object {
        Fix-AgentFrontmatter $_.FullName
    }
}

Write-Host "Done. OpenCode deployment complete."
