param([ValidateSet('prepare','apply')][string]$Action='prepare',[Parameter(Mandatory=$true)][string]$File,[string]$LocalNetwork)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskRoot
$taskContext=(Get-Content .env | Where-Object {$_ -match '^DOCKER_CONTEXT='}) -replace '^DOCKER_CONTEXT=',''
$taskEngine=& docker --context $taskContext info --format '{{.OperatingSystem}}'
if($LASTEXITCODE -ne 0 -or $taskEngine -notmatch 'Rancher Desktop'){throw 'Configured Rancher Desktop Moby context unavailable'}
$taskPrevious=@{};$taskArgs=@()
try{
 foreach($taskName in @('IDEAFLOW-VPS-URL','IDEAFLOW-VPS-ADMIN-EMAIL','IDEAFLOW-VPS-ADMIN-PASSWORD')){
  $taskPrevious[$taskName]=[Environment]::GetEnvironmentVariable($taskName,'Process')
  $taskValue=[Environment]::GetEnvironmentVariable($taskName,'User')
  if(-not $taskValue){throw 'Missing stored Windows User application credential'}
  [Environment]::SetEnvironmentVariable($taskName,$taskValue,'Process');$taskArgs+=@('-e',$taskName)
 }
 if($LocalNetwork){$taskArgs+=@('--network',$LocalNetwork,'-e','VAVE_ADAPT_URL=http://frontend')}
 & docker --context $taskContext run --rm @taskArgs --mount "type=bind,source=$taskRoot,target=/workspace" --entrypoint python ideaflow-vps-tools:1.0.0 scripts/vave_adapt.py $Action $File
 if($LASTEXITCODE -ne 0){throw 'Previewed VAVE adaptation failed'}
}finally{foreach($taskName in $taskPrevious.Keys){[Environment]::SetEnvironmentVariable($taskName,$taskPrevious[$taskName],'Process')}}
