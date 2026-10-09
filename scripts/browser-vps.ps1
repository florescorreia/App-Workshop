param()
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskRoot
$taskContext=(Get-Content .env | Where-Object {$_ -match '^DOCKER_CONTEXT='}) -replace '^DOCKER_CONTEXT=',''
$taskEngine=& docker --context $taskContext info --format '{{.OperatingSystem}}'
if($LASTEXITCODE -ne 0 -or $taskEngine -notmatch 'Rancher Desktop'){throw 'Configured Rancher Desktop context is unavailable'}
New-Item -ItemType Directory -Path artifacts -Force | Out-Null
$taskPrevious=@{}
try {
 foreach($taskName in @('IDEAFLOW_VPS_ADMIN_EMAIL','IDEAFLOW_VPS_ADMIN_PASSWORD')){
   $taskPrevious[$taskName]=[Environment]::GetEnvironmentVariable($taskName,'Process')
   $taskValue=[Environment]::GetEnvironmentVariable($taskName.Replace('_','-'),'User')
   if(-not $taskValue){throw "Missing Windows User environment: $taskName"}
   [Environment]::SetEnvironmentVariable($taskName,$taskValue,'Process')
 }
 $taskUrl=[Environment]::GetEnvironmentVariable('IDEAFLOW-VPS-URL','User')
 & docker --context $taskContext run --rm --mount "type=bind,source=$taskRoot/frontend,target=/source,readonly" --mount "type=bind,source=$taskRoot/artifacts,target=/artifacts" -e IDEAFLOW_VPS_ADMIN_EMAIL -e IDEAFLOW_VPS_ADMIN_PASSWORD -e "APP_URL=$taskUrl" -w /tmp/browser mcr.microsoft.com/playwright:v1.55.1-noble sh -c 'cp /source/package*.json /source/playwright.config.ts . && cp -r /source/tests . && npm ci --ignore-scripts && npx playwright test vps-deployment.spec.ts'
 if($LASTEXITCODE -ne 0){throw 'VPS browser verification failed'}
} finally {foreach($taskName in $taskPrevious.Keys){[Environment]::SetEnvironmentVariable($taskName,$taskPrevious[$taskName],'Process')}}
