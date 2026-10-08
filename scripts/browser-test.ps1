param([switch]$Verification)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskRoot
$taskContext=(Get-Content -LiteralPath .env | Where-Object {$_ -match '^DOCKER_CONTEXT='}) -replace '^DOCKER_CONTEXT=',''
$taskNetwork=if($Verification){'ideaflow-verification_default'}else{'ideaflow_default'}
New-Item -ItemType Directory -Path artifacts -Force | Out-Null
& docker --context $taskContext run --rm --network $taskNetwork --mount "type=bind,source=$taskRoot/frontend,target=/source,readonly" --mount "type=bind,source=$taskRoot,target=/config,readonly" --mount "type=bind,source=$taskRoot/artifacts,target=/artifacts" -e "VERIFY_DEMO=$($Verification.ToString().ToLower())" -w /tmp/browser mcr.microsoft.com/playwright:v1.55.1-noble sh -c 'cp /source/package*.json /source/playwright.config.ts . && cp -r /source/tests . && npm ci --ignore-scripts && npx playwright test'
if($LASTEXITCODE -ne 0){throw 'Browser verification failed. Review the test output; screenshots are in artifacts/.'}
