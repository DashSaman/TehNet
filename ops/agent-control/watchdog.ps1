# TEHNET local watchdog - deterministic checks only, no AI, no retries, no repairs.
# Appends one line per run to %USERPROFILE%\.zcode\tehnet-watchdog.log (rotated at ~2 MB).
# Checks: site HTTP status + robots meta presence, last checkpoint freshness, disk free (C:).
# NEVER: launches Z Code, retries destructive ops, touches services or credentials.

$ErrorActionPreference = 'Continue'
$log = Join-Path $env:USERPROFILE '.zcode\tehnet-watchdog.log'
$repo = 'D:\Codex-Projects\Codex\2026-10-15\referenced-chatgpt-conversation-this-is-an\work\TehNet-growth-20261031'

function Log([string]$line) {
    try {
        $dir = Split-Path $log -Parent
        if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
        if ((Test-Path $log) -and ((Get-Item $log).Length -gt 2MB)) {
            Move-Item -Force $log ($log + '.1')
        }
        $stamp = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        Add-Content -Path $log -Value ("{0} {1}" -f $stamp, $line) -Encoding UTF8
    } catch { }
}

# 1) Site health (single GET, 15s timeout)
try {
    $resp = Invoke-WebRequest -Uri 'https://tehnet.ir/' -Method GET -TimeoutSec 15 -UseBasicParsing -UserAgent 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) TehNet-Watchdog/1.0'
    $meta = ''
    if ($resp.Content -match "<meta name='robots' content='([^']*)'") { $meta = $Matches[1] }
    Log ("SITE status={0} robotsMeta='{1}'" -f [int]$resp.StatusCode, $meta)
} catch {
    Log ("SITE ERROR {0}" -f $_.Exception.Message.Split("`n")[0])
}

# 2) Checkpoint freshness (RUN_HISTORY.md age)
try {
    $rh = Join-Path $repo 'ops\agent-control\RUN_HISTORY.md'
    if (Test-Path $rh) {
        $ageH = [math]::Round(((Get-Date) - (Get-Item $rh).LastWriteTimeUtc).TotalHours, 1)
        Log ("CHECKPOINT ageHours={0}" -f $ageH)
    } else {
        Log 'CHECKPOINT missing'
    }
} catch { Log ('CHECKPOINT ERROR ' + $_.Exception.Message.Split("`n")[0]) }

# 3) Local disk free
try {
    $c = Get-PSDrive C
    Log ("DISK freeGB={0}" -f [math]::Round($c.Free / 1GB, 1))
} catch { Log ('DISK ERROR ' + $_.Exception.Message.Split("`n")[0]) }
