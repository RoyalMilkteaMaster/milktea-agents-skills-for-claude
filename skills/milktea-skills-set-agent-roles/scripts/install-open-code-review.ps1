[CmdletBinding()]
param(
    [switch]$Confirmed,
    [string]$Repo = (Get-Location).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$node = Get-Command node -CommandType Application -ErrorAction SilentlyContinue |
    Select-Object -First 1
if ($null -eq $node) {
    [ordered]@{
        schema_version = 2
        status = "prerequisites_missing"
        reason_codes = @("node_missing")
    } | ConvertTo-Json -Compress
    exit 20
}

$scriptPath = Join-Path $PSScriptRoot "open-code-review.js"
$arguments = @($scriptPath, "install", "--repo", $Repo)
if ($Confirmed) {
    $arguments += "--confirmed"
}

& $node.Source @arguments
exit $LASTEXITCODE
