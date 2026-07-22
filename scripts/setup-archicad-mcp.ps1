# Configure the optional Archicad MCP runtime on Windows.

[CmdletBinding()]
param(
    [switch]$CheckOnly,
    [switch]$DisableProject,
    [switch]$SkipResolve,
    [switch]$ConfigureUser,
    [switch]$RemoveUser,
    [ValidateSet("all", "claude-desktop", "gemini")]
    [string]$Client = "all"
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$coreScript = Join-Path $scriptDir "setup-archicad-mcp.py"

$pythonArgs = @($coreScript)
if ($CheckOnly) { $pythonArgs += "--check-only" }
if ($DisableProject) { $pythonArgs += "--disable-project" }
if ($SkipResolve) { $pythonArgs += "--skip-resolve" }
if ($ConfigureUser) { $pythonArgs += "--configure-user" }
if ($RemoveUser) { $pythonArgs += "--remove-user" }
if ($ConfigureUser -or $RemoveUser) { $pythonArgs += @("--client", $Client) }

$uvCommand = Get-Command uv -ErrorAction SilentlyContinue
if ($uvCommand) {
    & $uvCommand.Source run --isolated --python 3.12 @pythonArgs
    exit $LASTEXITCODE
}

# Rollback must remain possible even if uv was removed after setup.
if ($DisableProject) {
    $pyCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCommand) {
        & $pyCommand.Source -3 @pythonArgs
        exit $LASTEXITCODE
    }

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        & $pythonCommand.Source @pythonArgs
        exit $LASTEXITCODE
    }
}

Write-Error "uv is required for setup and verification. Install it from https://docs.astral.sh/uv/getting-started/installation/. Rollback without uv also requires py or python."
exit 2
