param([ValidateSet('backup','restore-test')][string]$Action='backup',[string]$Context='default',[string]$Backup)
$ErrorActionPreference='Stop'
$taskAppRoot=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskAppRoot
$taskSettings=& rdctl list-settings
if(($taskSettings|ConvertFrom-Json).containerEngine.name -ne 'moby'){throw 'Rancher Moby required'}
$taskOS=& docker --context $Context info --format '{{.OperatingSystem}}'
if($taskOS -notmatch 'Rancher Desktop'){throw 'Explicit context is not Rancher Desktop'}
$taskVolumes=@(& docker --context $Context volume ls --format '{{.Name}}' | Where-Object {$_ -match '^governed-dd-(control-db|identity-private|[a-f0-9]{24}-(postgres|artifacts|graph|paperclip|git|agent-home|reviewer-git|reviewer-home|run-gate|ontology|lab))$'})
if(-not $taskVolumes){throw 'No Governed DD persistent volumes'}
$taskKey=Join-Path $taskAppRoot 'local/secrets/backup-key'
if(-not (Test-Path $taskKey)){throw 'Run setup first'}
function D([string[]]$Arguments){& docker --context $Context @Arguments;if($LASTEXITCODE -ne 0){throw 'Backup container operation failed'}}
if($Action -eq 'backup'){
 $taskId=(Get-Date -Format 'yyyyMMdd-HHmmss')
 $taskDestination=Join-Path $taskAppRoot "backups/$taskId"
 New-Item -ItemType Directory -Path $taskDestination | Out-Null
 $taskRunning=@(& docker --context $Context ps --filter 'label=com.docker.compose.project' --format '{{.Names}}' | Where-Object {$_ -match '^governed-dd-'})
 try{
  if($taskRunning){D (@('stop','--time','60')+$taskRunning)}
  $taskArgs=@('run','--rm','--user','root','--mount',"type=bind,source=$taskDestination,target=/backup",'--mount',"type=bind,source=$taskAppRoot,target=/configuration,readonly",'--mount',"type=bind,source=$taskKey,target=/key,readonly",'--mount',"type=bind,source=$taskAppRoot/scripts/backup.py,target=/tool.py,readonly")
  foreach($taskVolume in $taskVolumes){$taskArgs+=@('-v',"${taskVolume}:/volumes/${taskVolume}:ro")}
  D ($taskArgs+@('--entrypoint','python','governed-dd-governance:0.1.0','/tool.py','pack'))
 }finally{if($taskRunning){D (@('start')+$taskRunning)}}
 Write-Host "Encrypted backup: apps/governed-dd/backups/$taskId"
}else{
 if(-not $Backup){throw 'Provide -Backup with an existing backup folder'}
 $taskDestination=[IO.Path]::GetFullPath($Backup)
 $taskRestorePrefix='governed-dd-restore-'+[Guid]::NewGuid().ToString('N').Substring(0,12)
 $taskEntries=& docker --context $Context run --rm --user root --mount "type=bind,source=$taskDestination,target=/backup,readonly" --mount "type=bind,source=$taskKey,target=/key,readonly" --mount "type=bind,source=$taskAppRoot/scripts/backup.py,target=/tool.py,readonly" --entrypoint python governed-dd-governance:0.1.0 /tool.py list
 if($LASTEXITCODE -ne 0){throw 'Cannot authenticate backup manifest'}
 $taskVolumes=$taskEntries|ConvertFrom-Json
 foreach($taskEntry in $taskVolumes){if($taskEntry -ne 'configuration' -and $taskEntry -notmatch '^governed-dd-(control-db|identity-private|[a-f0-9]{24}-(postgres|artifacts|graph|paperclip|git|agent-home|reviewer-git|reviewer-home|run-gate|ontology|lab))$'){throw 'Unexpected backup volume name'}}
 $taskArgs=@('run','--rm','--user','root','--mount',"type=bind,source=$taskDestination,target=/backup,readonly",'--mount',"type=bind,source=$taskKey,target=/key,readonly",'--mount',"type=bind,source=$taskAppRoot/scripts/backup.py,target=/tool.py,readonly")
 foreach($taskVolume in $taskVolumes){$taskNew="$taskRestorePrefix-$taskVolume";D @('volume','create',$taskNew);$taskArgs+=@('-v',"${taskNew}:/volumes/${taskVolume}")}
 D ($taskArgs+@('--entrypoint','python','governed-dd-governance:0.1.0','/tool.py','restore'))
 Write-Host "Isolated volume restore completed with prefix $taskRestorePrefix. Volumes retained for database/identity recovery checks. This is not fresh-host application acceptance."
}
