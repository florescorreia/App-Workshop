param(
 [Parameter(Position=0)][ValidateSet('init-secrets','deploy','status','start','stop','backup')][string]$Action='status',
 [Parameter(Mandatory=$true)][string]$App,[string]$Release,[string]$Context
)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskRoot
if($App -notmatch '^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$' -or $App.Length -gt 24){throw 'Invalid app slug.'}
$taskCatalog=Get-Content workshop.json -Raw | ConvertFrom-Json
$taskEntry=$taskCatalog.apps.PSObject.Properties[$App]
if(-not $taskEntry -or $taskEntry.Value.kind -ne 'workshop'){throw 'Use scripts/vps.ps1 for existing IdeaFlow. This command manages registered new apps only.'}
$taskPrefix='APPWORKSHOP-'+$App.ToUpperInvariant()+'-VPS'
function New-WorkshopSecret {
 $taskBytes=New-Object byte[] 30
 $taskRng=[Security.Cryptography.RandomNumberGenerator]::Create()
 try{$taskRng.GetBytes($taskBytes)}finally{$taskRng.Dispose()}
 return 'Aa9!'+[Convert]::ToBase64String($taskBytes).Replace('+','-').Replace('/','_')
}
if($Action -eq 'init-secrets'){
 $taskValues=@{
  "$taskPrefix-DB-PASSWORD"=(New-WorkshopSecret)
  "$taskPrefix-ADMIN-PASSWORD"=(New-WorkshopSecret)
  "$taskPrefix-ADMIN-EMAIL"="admin@$App.local"
  "$taskPrefix-COCKPIT-PASSWORD"=(New-WorkshopSecret)
  "$taskPrefix-URL"="https://$($taskCatalog.vps.hostname):$($taskEntry.Value.vps.publicPort)"
 }
 foreach($taskName in $taskValues.Keys){
  if(-not [Environment]::GetEnvironmentVariable($taskName,'User')){[Environment]::SetEnvironmentVariable($taskName,$taskValues[$taskName],'User')}
 }
 Write-Host "Persistent Windows User variables prepared under $taskPrefix. Existing values preserved; no credentials printed."
 return
}
$taskSettings=& rdctl list-settings
if($LASTEXITCODE -ne 0 -or ($taskSettings | ConvertFrom-Json).containerEngine.name -ne 'moby'){throw 'Start Rancher Desktop with Moby. No settings changed.'}
$taskContext=$null
$taskCandidates=if($Context){@($Context)}else{@(& docker context ls --format '{{.Name}}')}
foreach($taskCandidate in $taskCandidates){
 $taskInfo=& docker --context $taskCandidate info --format '{{.OperatingSystem}}' 2>$null
 if($LASTEXITCODE -eq 0 -and $taskInfo -match 'Rancher Desktop'){$taskContext=$taskCandidate;break}
}
if(-not $taskContext){throw 'No reachable Rancher Desktop Moby context.'}
& docker --context $taskContext image inspect ideaflow-vps-tools:1.0.0 --format '{{.Id}}' 2>$null | Out-Null
if($LASTEXITCODE -ne 0){
 & docker --context $taskContext build -t ideaflow-vps-tools:1.0.0 infra/vps-tools
 if($LASTEXITCODE -ne 0){throw 'Tools image build failed.'}
}
$taskNames=@($taskCatalog.vps.credentialPrefix,($taskCatalog.vps.credentialPrefix+'-SSH-KEY-PASSPHRASE'))
$taskNames+=@([Environment]::GetEnvironmentVariables('User').Keys | Where-Object {$_ -like "$taskPrefix-*"})
$taskPrevious=@{}
try{
 $taskDockerEnv=@()
 foreach($taskName in $taskNames){
  $taskPrevious[$taskName]=[Environment]::GetEnvironmentVariable($taskName,'Process')
  $taskValue=[Environment]::GetEnvironmentVariable($taskName,'User')
  if(-not $taskValue){throw "Missing Windows User variable: $taskName"}
  [Environment]::SetEnvironmentVariable($taskName,$taskValue,'Process');$taskDockerEnv+=@('-e',$taskName)
 }
 $taskArguments=@('scripts/workshop_vps.py',$Action,'--app',$App)
 if($Release){$taskArguments+=@('--release',$Release)}
 & docker --context $taskContext run --rm @taskDockerEnv --mount "type=bind,source=$taskRoot,target=/workspace" --mount "type=bind,source=$env:USERPROFILE/.ssh,target=/ssh,readonly" --entrypoint python ideaflow-vps-tools:1.0.0 @taskArguments
 if($LASTEXITCODE -ne 0){throw "VPS app operation failed: $Action"}
}finally{foreach($taskName in $taskPrevious.Keys){[Environment]::SetEnvironmentVariable($taskName,$taskPrevious[$taskName],'Process')}}
