param([switch]$Public,[switch]$Pilot)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskRoot
$taskContext=(Get-Content .env | Where-Object {$_ -match '^DOCKER_CONTEXT='}) -replace '^DOCKER_CONTEXT=',''
$taskEngine=& docker --context $taskContext info --format '{{.OperatingSystem}}'
if($LASTEXITCODE -ne 0 -or $taskEngine -notmatch 'Rancher Desktop'){throw 'Configured Rancher Desktop Moby context unavailable'}
$taskArgs=@();$taskPrevious=@{}
try {
 if($Public -or $Pilot){
  foreach($taskName in @('IDEAFLOW_VPS_ADMIN_EMAIL','IDEAFLOW_VPS_ADMIN_PASSWORD')){
   $taskPrevious[$taskName]=[Environment]::GetEnvironmentVariable($taskName,'Process')
   $taskValue=[Environment]::GetEnvironmentVariable($taskName.Replace('_','-'),'User')
   if(-not $taskValue){throw "Missing Windows User variable: $taskName"}
   [Environment]::SetEnvironmentVariable($taskName,$taskValue,'Process')
   $taskArgs+=@('-e',$taskName)
  }
  $taskArgs+=@('-e','VAVE_PUBLIC=true')
  if($Pilot){$taskArgs+=@('--network','ideaflow-vave-pilot_default','-e','VAVE_PILOT=true','-e','APP_URL=http://frontend')}
  else{$taskArgs+=@('-e',"APP_URL=$([Environment]::GetEnvironmentVariable('IDEAFLOW-VPS-URL','User'))")}
 }else{$taskArgs+=@('--network','ideaflow-verification_default')}
 & docker --context $taskContext run --rm @taskArgs --mount "type=bind,source=$taskRoot/frontend,target=/source,readonly" --mount "type=bind,source=$taskRoot,target=/config,readonly" --mount "type=bind,source=$taskRoot/artifacts,target=/artifacts" -w /tmp/browser mcr.microsoft.com/playwright:v1.55.1-noble sh -c 'cp /source/playwright.config.ts . && cp -r /source/tests . && npm install --ignore-scripts --no-audit --no-fund @playwright/test@1.55.1 && if [ ${VAVE_PUBLIC:-false} = true ]; then npx playwright test vave.spec.ts vps-deployment.spec.ts; else npx playwright test vave.spec.ts; fi'
 if($LASTEXITCODE -ne 0){throw 'VAVE browser verification failed'}
}finally{foreach($taskName in $taskPrevious.Keys){[Environment]::SetEnvironmentVariable($taskName,$taskPrevious[$taskName],'Process')}}
