$ErrorActionPreference = "Stop"
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repositoryRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "Missing .venv. Run: py -3.13 -m venv .venv; .\.venv\Scripts\python -m pip install -e '.[test]'"
}

$backend = Start-Process -FilePath $python -ArgumentList "-m", "vocation", "--no-browser" -WorkingDirectory $repositoryRoot -PassThru -WindowStyle Hidden
try {
    Set-Location (Join-Path $repositoryRoot "frontend")
    pnpm dev
}
finally {
    Stop-Process -Id $backend.Id -ErrorAction SilentlyContinue
}
