param([switch]$Verification)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskRoot
$taskContext=(Get-Content -LiteralPath .env | Where-Object {$_ -match '^DOCKER_CONTEXT='}) -replace '^DOCKER_CONTEXT=',''
$taskEngine=& docker --context $taskContext info --format '{{.OperatingSystem}}'
if($LASTEXITCODE -ne 0 -or $taskEngine -notmatch 'Rancher Desktop'){throw 'Configured Rancher Desktop context is unavailable'}
$taskNetwork=if($Verification){'ideaflow-verification_default'}else{'ideaflow_default'}
New-Item -ItemType Directory -Path artifacts -Force | Out-Null
& docker --context $taskContext run --rm --network $taskNetwork --mount "type=bind,source=$taskRoot/frontend,target=/source,readonly" --mount "type=bind,source=$taskRoot,target=/config,readonly" --mount "type=bind,source=$taskRoot/artifacts,target=/artifacts" -e "SHARED_EMPTY=$((-not $Verification).ToString().ToLower())" -e "SHARED_MUTATING=$($Verification.ToString().ToLower())" -w /tmp/browser mcr.microsoft.com/playwright:v1.55.1-noble sh -c 'cp /source/package*.json /source/playwright.config.ts . && cp -r /source/tests . && npm ci --ignore-scripts && npx playwright test shared-workspace.spec.ts'
if($LASTEXITCODE -ne 0){throw 'Shared workspace browser verification failed'}
