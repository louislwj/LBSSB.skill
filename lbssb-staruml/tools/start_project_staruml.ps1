param(
  [string]$ProjectRoot = (Get-Location).Path,
  [string]$ConfigPath = "",
  [int]$WaitSeconds = 6,
  [switch]$EnableLogging,
  [string]$OutFile = ""
)

$ErrorActionPreference = "Stop"

function Resolve-AbsolutePath {
  param([string]$PathValue, [string]$BaseDir)
  if ([string]::IsNullOrWhiteSpace($PathValue)) { return $null }
  if ([System.IO.Path]::IsPathRooted($PathValue)) { return $PathValue }
  return [System.IO.Path]::GetFullPath((Join-Path $BaseDir $PathValue))
}

function Test-TcpPort {
  param([string]$HostName, [int]$Port)
  try {
    $client = New-Object System.Net.Sockets.TcpClient
    $async = $client.BeginConnect($HostName, $Port, $null, $null)
    $ok = $async.AsyncWaitHandle.WaitOne(1000, $false)
    if (-not $ok) {
      $client.Close()
      return $false
    }
    $client.EndConnect($async)
    $client.Close()
    return $true
  } catch {
    return $false
  }
}

function Read-RuntimeConfig {
  param([string]$Root, [string]$ExplicitConfig)
  $candidates = @()
  if (-not [string]::IsNullOrWhiteSpace($ExplicitConfig)) {
    $candidates += $ExplicitConfig
  }
  $candidates += (Join-Path $Root ".lbssb\staruml-runtime.json")
  $candidates += (Join-Path $Root "lbssb-staruml\runtime\staruml-runtime.json")

  foreach ($candidate in $candidates) {
    if (Test-Path -LiteralPath $candidate) {
      try {
        $json = Get-Content -LiteralPath $candidate -Raw -Encoding UTF8 | ConvertFrom-Json
        return @{ path = $candidate; data = $json }
      } catch {
        return @{ path = $candidate; data = $null; error = $_.Exception.Message }
      }
    }
  }
  return @{ path = ""; data = $null }
}

function Resolve-StarUML {
  param([string]$Root, [object]$RuntimeConfig)

  $items = @()
  if ($RuntimeConfig.data -and $RuntimeConfig.data.starumlExecutable) {
    $items += @{
      path = (Resolve-AbsolutePath $RuntimeConfig.data.starumlExecutable (Split-Path -Parent $RuntimeConfig.path))
      from = "project-config"
    }
  }
  if ($env:LBSSB_STARUML_EXE) {
    $items += @{ path = $env:LBSSB_STARUML_EXE; from = "env" }
  }

  $items += @{ path = (Join-Path $Root "tools\StarUML\StarUML.exe"); from = "project-local" }
  $items += @{ path = (Join-Path $Root ".lbssb\runtime\StarUML\StarUML.exe"); from = "project-local" }
  $items += @{ path = (Join-Path $Root "mcp\StarUML\StarUML.exe"); from = "project-local" }
  $items += @{ path = "C:\Program Files\StarUML\StarUML.exe"; from = "system" }
  $items += @{ path = "C:\Program Files (x86)\StarUML\StarUML.exe"; from = "system" }

  foreach ($item in $items) {
    if ($item.path -and (Test-Path -LiteralPath $item.path)) {
      return $item
    }
  }

  $cmd = Get-Command "StarUML.exe" -ErrorAction SilentlyContinue
  if ($cmd) {
    return @{ path = $cmd.Source; from = "path" }
  }

  return @{ path = ""; from = "not-found" }
}

$root = [System.IO.Path]::GetFullPath($ProjectRoot)
$runtime = Read-RuntimeConfig $root $ConfigPath
$resolved = Resolve-StarUML $root $runtime

$nodeOptions = [Environment]::GetEnvironmentVariable("NODE_OPTIONS", "Process")
$nodeOptionsDetected = -not [string]::IsNullOrWhiteSpace($nodeOptions)
$nodeOptionsRisky = $false
if ($nodeOptionsDetected) {
  $nodeOptionsRisky = $nodeOptions -match "--use-system-ca|--require|--inspect|--openssl|--tls|--ca|--cert|--experimental"
}

$clearForLaunch = $true
if ($runtime.data -and $null -ne $runtime.data.clearNodeOptionsForStarUMLLaunch) {
  $clearForLaunch = [bool]$runtime.data.clearNodeOptionsForStarUMLLaunch
}
$enableLog = [bool]$EnableLogging
if (-not $enableLog -and $runtime.data -and $null -ne $runtime.data.enableLogging) {
  $enableLog = [bool]$runtime.data.enableLogging
}

$processStarted = $false
$launchError = ""
$nodeCleared = $false
$argsList = @()
if ($enableLog) { $argsList += "--enable-logging" }

if ($resolved.path) {
  $oldNodeOptions = [Environment]::GetEnvironmentVariable("NODE_OPTIONS", "Process")
  try {
    if ($clearForLaunch -and $nodeOptionsDetected) {
      [Environment]::SetEnvironmentVariable("NODE_OPTIONS", $null, "Process")
      $nodeCleared = $true
    }
    $proc = Start-Process -FilePath $resolved.path -ArgumentList $argsList -PassThru
    Start-Sleep -Seconds $WaitSeconds
    $running = Get-Process -Name "StarUML" -ErrorAction SilentlyContinue
    $processStarted = ($null -ne $running) -or ($proc -and -not $proc.HasExited)
  } catch {
    $launchError = $_.Exception.Message
  } finally {
    [Environment]::SetEnvironmentVariable("NODE_OPTIONS", $oldNodeOptions, "Process")
  }
}

$apiPort = 58321
$extensionPort = 58322
if ($runtime.data -and $runtime.data.apiServerPort) { $apiPort = [int]$runtime.data.apiServerPort }
if ($runtime.data -and $runtime.data.extensionPort) { $extensionPort = [int]$runtime.data.extensionPort }

$apiOk = Test-TcpPort "127.0.0.1" $apiPort
$extensionOk = Test-TcpPort "127.0.0.1" $extensionPort

$status = "NotFound"
if ($resolved.path -and -not $processStarted) { $status = "LaunchFailed" }
if ($processStarted -and -not ($apiOk -and $extensionOk)) { $status = "StartedButApiUnavailable" }
if ($processStarted -and $apiOk -and $extensionOk) { $status = "StartedAndPortsAvailable" }

$result = [ordered]@{
  starumlExecutable = $resolved.path
  resolvedFrom = $resolved.from
  runtimeConfig = $runtime.path
  nodeOptionsDetected = $nodeOptionsDetected
  nodeOptionsValue = $nodeOptions
  nodeOptionsRisky = $nodeOptionsRisky
  nodeOptionsClearedForLaunch = $nodeCleared
  processStarted = $processStarted
  launchError = $launchError
  apiServer58321 = $apiOk
  extension58322 = $extensionOk
  status = $status
}

$json = $result | ConvertTo-Json -Depth 6
if ($OutFile) {
  $outDir = Split-Path -Parent $OutFile
  if ($outDir -and -not (Test-Path -LiteralPath $outDir)) {
    New-Item -ItemType Directory -Path $outDir | Out-Null
  }
  Set-Content -LiteralPath $OutFile -Value $json -Encoding UTF8
}
$json

if (-not $resolved.path -or -not $processStarted) { exit 1 }
exit 0
