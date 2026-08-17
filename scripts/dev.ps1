$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repositoryRoot ".venv\Scripts\python.exe"
$frontendModules = Join-Path $repositoryRoot "frontend\node_modules"

if (-not (Test-Path $python)) {
    throw "Missing .venv. Run: uv sync --locked --extra dev"
}

if (-not (Test-Path $frontendModules)) {
    throw "Missing frontend dependencies. Run: pnpm --dir frontend install --frozen-lockfile"
}

$backend = Start-Process -FilePath $python -ArgumentList "-m", "vocation", "--no-browser" -WorkingDirectory $repositoryRoot -PassThru -WindowStyle Hidden
try {
    Set-Location (Join-Path $repositoryRoot "frontend")
    pnpm dev
}
finally {
    Stop-Process -Id $backend.Id -ErrorAction SilentlyContinue
}
