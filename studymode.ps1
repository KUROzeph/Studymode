# ==============================
# Study Mode v2.0
# ==============================

$blockedApps = @(
    "steam"
)

$blockedWebsites = @(
    "x.com",
    "www.x.com"
)

$morningStart = "09:00"
$morningEnd   = "12:00"

$afternoonStart = "13:00"
$afternoonEnd   = "17:00"

$hostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"

$startMarker = "# STUDYMODE START"
$endMarker   = "# STUDYMODE END"


function Is-TimeInRange {
    param (
        [string]$Start,
        [string]$End
    )

    $now = (Get-Date).TimeOfDay
    $startTime = [TimeSpan]::Parse($Start)
    $endTime = [TimeSpan]::Parse($End)

    return ($now -ge $startTime -and $now -lt $endTime)
}


function Is-StudyTime {

    return (
        (Is-TimeInRange $morningStart $morningEnd) -or
        (Is-TimeInRange $afternoonStart $afternoonEnd)
    )
}


function Block-Websites {

    $hosts = Get-Content $hostsPath -ErrorAction Stop

    if ($hosts -contains $startMarker) {
        return
    }

    Add-Content -Path $hostsPath -Value ""
    Add-Content -Path $hostsPath -Value $startMarker

    foreach ($site in $blockedWebsites) {
        Add-Content -Path $hostsPath -Value "0.0.0.0 $site"
    }

    Add-Content -Path $hostsPath -Value $endMarker

    ipconfig /flushdns | Out-Null

    Write-Host "$(Get-Date -Format 'HH:mm:ss') - Websites BLOCKED"
}


function Unblock-Websites {

    $hosts = Get-Content $hostsPath -ErrorAction Stop

    $newHosts = @()
    $insideBlock = $false

    foreach ($line in $hosts) {

        if ($line -eq $startMarker) {
            $insideBlock = $true
            continue
        }

        if ($line -eq $endMarker) {
            $insideBlock = $false
            continue
        }

        if (-not $insideBlock) {
            $newHosts += $line
        }
    }

    Set-Content -Path $hostsPath -Value $newHosts

    ipconfig /flushdns | Out-Null

    Write-Host "$(Get-Date -Format 'HH:mm:ss') - Websites UNBLOCKED"
}


while ($true) {

    $blocking = Is-StudyTime

    if ($blocking) {

        foreach ($app in $blockedApps) {

            $process = Get-Process -Name $app -ErrorAction SilentlyContinue

            if ($process) {
                Write-Host "$(Get-Date -Format 'HH:mm:ss') - BLOCKED: $app"
                $process | Stop-Process -Force
            }
        }

        Block-Websites

    }
    else {

        Unblock-Websites

    }

    Start-Sleep -Seconds 5
}