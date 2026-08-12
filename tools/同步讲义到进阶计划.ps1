#Requires -Version 5.1
# Wrapper: call UTF-8 Python sync (avoid PS Chinese encoding issues)
param(
  [string]$SourceRoot = "D:\浏览器下载文件\【讲义】",
  [string]$DestRoot = "",
  [switch]$Force
)
$py = Join-Path $PSScriptRoot "同步讲义到进阶计划.py"
if (-not $DestRoot) {
  $DestRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}
$argsList = @($py, "--src", $SourceRoot, "--dst", $DestRoot)
if ($Force) { $argsList += "--force" }
python @argsList
exit $LASTEXITCODE
