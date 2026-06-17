param(
  [string]$ProjectRoot = (Get-Location).Path,
  [string]$OutFile = ".lbssb\preflight-report.json",
  [string]$Evidence = "",
  [string]$McpToolsJson = "",
  [switch]$NoLaunch
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonScript = Join-Path $scriptDir "check_staruml_preflight.py"

$python = Get-Command "python" -ErrorAction SilentlyContinue
if (-not $python) {
  $python = Get-Command "py" -ErrorAction SilentlyContinue
}
if (-not $python) {
  Write-Error "Python not found. Install Python or run check_staruml_preflight.py with a known interpreter."
  exit 2
}

$argsList = @($pythonScript, "--project-root", $ProjectRoot, "--out", $OutFile)
if ($Evidence) { $argsList += @("--evidence", $Evidence) }
if ($McpToolsJson) { $argsList += @("--mcp-tools-json", $McpToolsJson) }
if ($NoLaunch) { $argsList += "--no-launch" }

if ($python.Name -eq "py.exe") {
  & $python.Source -3 @argsList
} else {
  & $python.Source @argsList
}
exit $LASTEXITCODE
