param(
    [int]$BackendPort = 8765,
    [int]$StartupTimeoutSeconds = 30,
    [switch]$BackendSmokeTest
)

$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repositoryRoot ".venv\Scripts\python.exe"
$frontendPath = Join-Path $repositoryRoot "frontend"
$frontendModules = Join-Path $frontendPath "node_modules"
$backendUrl = "http://127.0.0.1:$BackendPort"
$healthUrl = "$backendUrl/api/health"

function Test-TcpPortInUse {
    param(
        [Parameter(Mandatory)]
        [string]$HostName,
        [Parameter(Mandatory)]
        [int]$Port
    )

    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $task = $client.ConnectAsync($HostName, $Port)
        if (-not $task.Wait(350)) {
            return $false
        }
        return $client.Connected
    }
    catch {
        return $false
    }
    finally {
        $client.Dispose()
    }
}

function Wait-VocationBackend {
    param(
        [Parameter(Mandatory)]
        [System.Diagnostics.Process]$Process,
        [Parameter(Mandatory)]
        [string]$HealthUrl,
        [Parameter(Mandatory)]
        [int]$TimeoutSeconds
    )

    $deadline = [DateTimeOffset]::UtcNow.AddSeconds($TimeoutSeconds)
    while ([DateTimeOffset]::UtcNow -lt $deadline) {
        $Process.Refresh()
        if ($Process.HasExited) {
            throw "Vocation backend exited during startup with code $($Process.ExitCode)."
        }

        try {
            $health = Invoke-RestMethod -Uri $HealthUrl -TimeoutSec 1
            if ($health.status -eq "ok" -and $health.service -eq "vocation") {
                return
            }
        }
        catch {
            # The backend may still be starting or running migrations.
        }

        Start-Sleep -Milliseconds 250
    }

    throw "Vocation backend did not become healthy at $HealthUrl within $TimeoutSeconds seconds."
}

if (-not (Test-Path $python)) {
    throw "Missing .venv. Run: uv sync --locked --extra dev"
}

if (-not $BackendSmokeTest -and -not (Test-Path $frontendModules)) {
    throw "Missing frontend dependencies. Run: pnpm --dir frontend install --frozen-lockfile"
}

if (Test-TcpPortInUse -HostName "127.0.0.1" -Port $BackendPort) {
    throw "Port $BackendPort is already in use. Stop the existing Vocation/backend process or choose another -BackendPort before starting a second development instance."
}

$backend = $null
$frontendLocationPushed = $false
try {
    Write-Host "Starting Vocation backend at $backendUrl ..."
    $backend = Start-Process `
        -FilePath $python `
        -ArgumentList "-m", "vocation", "--no-browser", "--port", "$BackendPort" `
        -WorkingDirectory $repositoryRoot `
        -PassThru `
        -NoNewWindow

    Wait-VocationBackend -Process $backend -HealthUrl $healthUrl -TimeoutSeconds $StartupTimeoutSeconds
    Write-Host "Vocation backend ready (PID $($backend.Id)): $backendUrl"

    if ($BackendSmokeTest) {
        Write-Host "Backend smoke test complete; shutting down the exact child process."
        return
    }

    Push-Location $frontendPath
    $frontendLocationPushed = $true
    Write-Host "Starting Vite frontend: http://127.0.0.1:5173"
    Write-Host "Press Ctrl+C to stop frontend and backend."
    pnpm dev
    if ($LASTEXITCODE -ne 0) {
        throw "Vite exited with code $LASTEXITCODE."
    }
}
finally {
    if ($frontendLocationPushed) {
        Pop-Location
    }

    if ($null -ne $backend) {
        $backend.Refresh()
        if (-not $backend.HasExited) {
            Write-Host "Stopping Vocation backend PID $($backend.Id) ..."
            Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
            [void]$backend.WaitForExit(5000)
        }

        $backend.Refresh()
        if (-not $backend.HasExited) {
            throw "Vocation backend PID $($backend.Id) did not exit cleanly."
        }
        Write-Host "Vocation backend stopped."
    }
}
