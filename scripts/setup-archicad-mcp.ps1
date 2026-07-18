# Prepare the optional Archicad MCP runtime on Windows.

[CmdletBinding()]
param(
    [switch]$CheckOnly,
    [switch]$SkipResolve,
    [switch]$ConfigureUser,
    [ValidateSet("all", "claude-desktop", "gemini")]
    [string]$Client = "all"
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$coreScript = Join-Path $scriptDir "setup-archicad-mcp.py"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error "uv is required. Install it from https://docs.astral.sh/uv/getting-started/installation/"
    exit 2
}

$setupArgs = @("run", "--no-project", "--python", "3.12", $coreScript)
if ($CheckOnly) { $setupArgs += "--check-only" }
if ($SkipResolve) { $setupArgs += "--skip-resolve" }
if ($ConfigureUser) {
    $setupArgs += "--configure-user"
    $setupArgs += @("--client", $Client)
}

& uv @setupArgs
exit $LASTEXITCODE
