$ErrorActionPreference = "Stop"

$workspaceRoot = Split-Path -Parent $PSScriptRoot
$flutterRoot = Join-Path $workspaceRoot "flutter"
$flutterBat = Join-Path $flutterRoot "bin\\flutter.bat"
$gitConfig = Join-Path $workspaceRoot ".gitconfig-codex"
$appDataRoot = Join-Path $workspaceRoot ".appdata"
$homeRoot = Join-Path $workspaceRoot ".home"
$pubCacheRoot = Join-Path $workspaceRoot ".pub-cache"

foreach ($path in @(
    (Join-Path $appDataRoot "Roaming"),
    (Join-Path $appDataRoot "Local"),
    $homeRoot,
    $pubCacheRoot
)) {
    New-Item -ItemType Directory -Force -Path $path | Out-Null
}

$env:GIT_CONFIG_GLOBAL = $gitConfig
$env:APPDATA = Join-Path $appDataRoot "Roaming"
$env:LOCALAPPDATA = Join-Path $appDataRoot "Local"
$env:HOME = $homeRoot
$env:USERPROFILE = $homeRoot
$env:PUB_CACHE = $pubCacheRoot

& git config --file $gitConfig --replace-all safe.directory $flutterRoot.Replace('\', '/')
& $flutterBat @args
