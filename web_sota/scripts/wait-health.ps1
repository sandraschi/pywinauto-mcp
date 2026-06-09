param(
    [string]$Url = "http://127.0.0.1:10789/api/v1/health",
    [int]$TimeoutSec = 90
)

$deadline = (Get-Date).AddSeconds($TimeoutSec)
while ((Get-Date) -lt $deadline) {
    try {
        $null = Invoke-WebRequest -Uri $Url -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        Write-Host "Health OK: $Url"
        exit 0
    }
    catch {
        Start-Sleep -Seconds 1
    }
}
Write-Error "Timed out waiting for $Url (${TimeoutSec}s)"
