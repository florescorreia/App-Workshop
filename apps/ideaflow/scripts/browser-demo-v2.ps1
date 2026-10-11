$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskRoot
$taskContext=(Get-Content -LiteralPath .env | Where-Object {$_ -match '^DOCKER_CONTEXT='}) -replace '^DOCKER_CONTEXT=',''
New-Item -ItemType Directory -Path artifacts -Force | Out-Null
& docker --context $taskContext run --rm --network ideaflow_default --mount "type=bind,source=$taskRoot/frontend,target=/source,readonly" --mount "type=bind,source=$taskRoot,target=/config,readonly" --mount "type=bind,source=$taskRoot/artifacts,target=/artifacts" -e DEMO_V2_LIVE=true -w /tmp/browser mcr.microsoft.com/playwright:v1.55.1-noble sh -c 'cp /source/package*.json /source/playwright.config.ts . && cp -r /source/tests . && npm ci --ignore-scripts && npx playwright test demo-v2.spec.ts --timeout=60000'
if($LASTEXITCODE -ne 0){throw 'Read-only v2 browser verification failed.'}
