param([Parameter(Position=0)][string]$Action='inspect',[string]$File,[string]$Command)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskRoot
$taskContext=(Get-Content -LiteralPath .env | Where-Object {$_ -match '^DOCKER_CONTEXT='}) -replace '^DOCKER_CONTEXT=',''
$taskEngine=& docker --context $taskContext info --format '{{.OperatingSystem}}'
if($LASTEXITCODE -ne 0 -or $taskEngine -notmatch 'Rancher Desktop'){throw 'Configured Rancher Desktop Moby context is unavailable'}
$taskVars=@('VPS-OVH-US-8104e6c8','VPS-OVH-US-8104e6c8-SSH-KEY-PASSPHRASE')
$taskVars+=@([Environment]::GetEnvironmentVariables('User').Keys | Where-Object {$_ -like 'IDEAFLOW-VPS-*'})
$taskPrevious=@{}
try {
 foreach($taskName in $taskVars){$taskPrevious[$taskName]=[Environment]::GetEnvironmentVariable($taskName,'Process');$taskValue=[Environment]::GetEnvironmentVariable($taskName,'User');if(-not $taskValue){throw "Missing persistent Windows user variable: $taskName"};[Environment]::SetEnvironmentVariable($taskName,$taskValue,'Process')}
 $taskEnvArgs=@();foreach($taskName in $taskVars){$taskEnvArgs+=@('-e',$taskName)}
 $taskArgs=@($Action);if($File){$taskArgs+=@('--file',$File)};if($Command){$taskArgs+=@('--command',$Command)}
 & docker --context $taskContext run --rm @taskEnvArgs --mount "type=bind,source=$taskRoot,target=/workspace" --mount "type=bind,source=$env:USERPROFILE/.ssh,target=/ssh,readonly" ideaflow-vps-tools:1.0.0 @taskArgs
 if($LASTEXITCODE -ne 0){throw "VPS action failed: $Action"}
} finally {foreach($taskName in $taskPrevious.Keys){[Environment]::SetEnvironmentVariable($taskName,$taskPrevious[$taskName],'Process')}}
