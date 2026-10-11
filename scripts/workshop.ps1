param(
 [Parameter(Position=0)][ValidateSet('list','new','doctor','init-env','up','status','logs','down','test','backup','restore-test','prepare-vps','verify')][string]$Action='list',
 [string]$App,[string]$Context,[int]$Port=0
)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskRoot
function Find-WorkshopContext {
 $taskSettings=& rdctl list-settings
 if($LASTEXITCODE -ne 0){throw 'Start Rancher Desktop before running container operations.'}
 if(($taskSettings | ConvertFrom-Json).containerEngine.name -ne 'moby'){throw 'Rancher Desktop must use dockerd (Moby). No settings were changed.'}
 $taskContexts=if($Context){@($Context)}else{@(& docker context ls --format '{{.Name}}')}
 foreach($taskCandidate in $taskContexts){
  $taskInfo=& docker --context $taskCandidate info --format '{{.OperatingSystem}}' 2>$null
  if($LASTEXITCODE -eq 0 -and $taskInfo -match 'Rancher Desktop'){return $taskCandidate}
 }
 throw 'No reachable Rancher Desktop Moby context. Start Rancher Desktop and retry.'
}
function Read-AppEnv([string]$Path){
 $taskValues=@{}
 if(Test-Path -LiteralPath $Path){Get-Content -LiteralPath $Path | ForEach-Object {if($_ -match '^([^#=]+)=(.*)$'){$taskValues[$matches[1]]=$matches[2]}}}
 return $taskValues
}
function Secret {
 $taskBytes=New-Object byte[] 30
 $taskRng=[Security.Cryptography.RandomNumberGenerator]::Create()
 try{$taskRng.GetBytes($taskBytes)}finally{$taskRng.Dispose()}
 return [Convert]::ToBase64String($taskBytes).Replace('+','-').Replace('/','_')
}
$taskCatalog=Get-Content -LiteralPath workshop.json -Raw | ConvertFrom-Json
if($Action -eq 'list'){
 foreach($taskEntry in $taskCatalog.apps.PSObject.Properties){
  [PSCustomObject]@{App=$taskEntry.Name;Folder=$taskEntry.Value.path;LocalURL="http://localhost:$($taskEntry.Value.localPort)";VPSPort=$taskEntry.Value.vps.publicPort;Type=$taskEntry.Value.kind}
 }
 return
}
$taskContext=Find-WorkshopContext
if($App -and $taskCatalog.apps.PSObject.Properties[$App] -and $taskCatalog.apps.PSObject.Properties[$App].Value.kind -eq 'custom'){
 $taskCustom=$taskCatalog.apps.PSObject.Properties[$App].Value
 $taskCustomScript=[IO.Path]::GetFullPath((Join-Path $taskRoot $taskCustom.managedBy))
 $taskExpectedRoot=[IO.Path]::GetFullPath((Join-Path $taskRoot $taskCustom.path))+[IO.Path]::DirectorySeparatorChar
 if(-not $taskCustomScript.StartsWith($taskExpectedRoot,[StringComparison]::OrdinalIgnoreCase)){throw 'Custom manager must remain in its app folder.'}
 & powershell -NoProfile -ExecutionPolicy Bypass -File $taskCustomScript $Action -Context $taskContext
 if($LASTEXITCODE -ne 0){throw "Custom app operation failed: $Action"}
 return
}
if($Action -in @('new','prepare-vps','verify')){
 & docker --context $taskContext image inspect ideaflow-vps-tools:1.0.0 --format '{{.Id}}' 2>$null | Out-Null
 if($LASTEXITCODE -ne 0){
  & docker --context $taskContext build -t ideaflow-vps-tools:1.0.0 infra/vps-tools
  if($LASTEXITCODE -ne 0){throw 'Could not build the transient workspace tools image.'}
 }
}
if($Action -eq 'doctor'){
 Write-Host "Verified Rancher Desktop Moby context: $taskContext"
 & docker --context $taskContext version
 & docker --context $taskContext compose version
 return
}
if($Action -eq 'verify'){
 & docker --context $taskContext run --rm --mount "type=bind,source=$taskRoot,target=/workspace,readonly" -w /workspace --entrypoint python ideaflow-vps-tools:1.0.0 -B -m unittest discover -s tests/workshop -v
 if($LASTEXITCODE -ne 0){throw 'Workspace verification failed'}
 return
}
if(-not $App -or $App -notmatch '^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$' -or $App.Length -gt 24){throw 'Use a lowercase app slug, at most 24 characters, such as supplier-portal.'}
if($Action -in @('new','prepare-vps')){
 $taskArgs=@('/workspace/scripts/workshop.py',$Action,'--app',$App)
 if($Port){$taskArgs+=@('--port',"$Port")}
 if($Action -eq 'prepare-vps'){
  $taskEntry=$taskCatalog.apps.PSObject.Properties[$App]
  if(-not $taskEntry -or $taskEntry.Value.kind -ne 'workshop'){throw 'Only new workshop apps use prepare-vps; existing IdeaFlow deployment is preserved.'}
  $taskAppConfig=Get-Content (Join-Path $taskRoot "$($taskEntry.Value.path)/app.json") -Raw | ConvertFrom-Json
  $taskReleaseRoot=Join-Path $taskRoot "$($taskEntry.Value.path)/local";New-Item -ItemType Directory -Path $taskReleaseRoot -Force | Out-Null
  $taskArchive=Join-Path $taskReleaseRoot 'release-images.tar'
  if(Test-Path -LiteralPath $taskArchive){throw 'Archive exists. Preserve it or choose an explicit new release; refusing overwrite.'}
  $taskImages=@($taskAppConfig.services.PSObject.Properties | ForEach-Object {$_.Value.image})
  & docker --context $taskContext save -o $taskArchive @taskImages
  if($LASTEXITCODE -ne 0){throw 'Build all app images locally before prepare-vps.'}
  $taskArgs+=@('--images',"/workspace/$($taskEntry.Value.path)/local/release-images.tar")
 }
 & docker --context $taskContext run --rm --mount "type=bind,source=$taskRoot,target=/workspace" -w /workspace --entrypoint python ideaflow-vps-tools:1.0.0 @taskArgs
 if($LASTEXITCODE -ne 0){throw "Workspace operation failed: $Action"}
 return
}
$taskEntry=$taskCatalog.apps.PSObject.Properties[$App]
if(-not $taskEntry){throw "Unknown app: $App. Run list or new first."}
$taskConfig=$taskEntry.Value
if($taskConfig.kind -eq 'existing'){
 # Preserve the established operations and database identities.
 $taskArgs=@('-NoProfile','-ExecutionPolicy','Bypass','-File',(Join-Path $taskRoot "$($taskConfig.path)/scripts/ideaflow.ps1"),$Action,'-Context',$taskContext)
 if($Port){$taskArgs+=@('-Port',"$Port")}
 & powershell @taskArgs
 if($LASTEXITCODE -ne 0){throw "Existing IdeaFlow operation failed: $Action"}
 return
}
$taskAppRoot=[IO.Path]::GetFullPath((Join-Path $taskRoot $taskConfig.path))
$taskAppsRoot=[IO.Path]::GetFullPath((Join-Path $taskRoot 'apps'))+[IO.Path]::DirectorySeparatorChar
if(-not $taskAppRoot.StartsWith($taskAppsRoot,[StringComparison]::OrdinalIgnoreCase)){throw 'Application path must stay inside apps/.'}
$taskEnvFile=Join-Path $taskAppRoot '.env'
$taskEnv=Read-AppEnv $taskEnvFile
if($Action -eq 'init-env'){
 if(Test-Path -LiteralPath $taskEnvFile){Write-Host 'Existing app .env preserved.';return}
 $taskPort=if($Port){$Port}else{[int]$taskConfig.localPort}
 if($taskPort -ne [int]$taskConfig.localPort){throw 'Update the app catalog and app.json together before changing its reserved port.'}
 if(Get-NetTCPConnection -LocalPort $taskPort -State Listen -ErrorAction SilentlyContinue){throw "Port $taskPort is already in use; update app.json and workshop.json to reserve a free port."}
 $taskContent=Get-Content (Join-Path $taskAppRoot '.env.example') -Raw
 $taskContent=$taskContent.Replace('GENERATE_DB_PASSWORD',(Secret)).Replace('GENERATE_ADMIN_PASSWORD',(Secret)).Replace('DETECTED_RANCHER_CONTEXT',$taskContext)
 [IO.File]::WriteAllText($taskEnvFile,$taskContent,(New-Object Text.UTF8Encoding $false))
 Write-Host "Created private $($taskConfig.path)/.env. No credentials printed."
 return
}
if(-not (Test-Path -LiteralPath $taskEnvFile)){throw "Run init-env -App $App first."}
function Compose([string[]]$Arguments){
 & docker --context $taskContext compose --project-directory $taskAppRoot --env-file $taskEnvFile -p $taskConfig.composeProject @Arguments
 if($LASTEXITCODE -ne 0){throw "Compose operation failed for $App"}
}
switch($Action){
 'up'{Compose -Arguments @('up','--build','-d','--wait','--wait-timeout','180');$taskReady=Invoke-RestMethod -Uri "http://localhost:$($taskConfig.localPort)/api/health/ready" -TimeoutSec 15;if($taskReady.status -ne 'ready'){throw 'Application readiness failed'};Write-Host "Ready: http://localhost:$($taskConfig.localPort)"}
 'status'{Compose -Arguments @('ps')}
 'logs'{Compose -Arguments @('logs','--tail','80')}
 'down'{Compose -Arguments @('down');Write-Host 'Stopped this app; volumes preserved.'}
 'test'{Compose -Arguments @('run','--rm','--no-deps','backend','python','-m','unittest','discover','-s','tests','-v')}
 'backup'{
  $taskBackupRoot=Join-Path $taskAppRoot 'backups';New-Item -ItemType Directory -Path $taskBackupRoot -Force | Out-Null
  $taskStamp=Get-Date -Format 'yyyyMMdd-HHmmss'
  $taskDump="/tmp/$App-$taskStamp.dump"
  Compose -Arguments @('exec','-T','postgres','pg_dump','-U',$taskEnv.POSTGRES_USER,'-d',$taskEnv.POSTGRES_DB,'-Fc','-f',$taskDump)
  Compose -Arguments @('cp',"postgres:$taskDump",(Join-Path $taskBackupRoot "$App-$taskStamp.dump"))
  Write-Host "Private backup: $($taskConfig.path)/backups/$App-$taskStamp.dump"
 }
 'restore-test'{
  $taskDatabase='restore_'+[Guid]::NewGuid().ToString('N')
  $taskDump="/tmp/$taskDatabase.dump"
  Compose -Arguments @('exec','-T','postgres','pg_dump','-U',$taskEnv.POSTGRES_USER,'-d',$taskEnv.POSTGRES_DB,'-Fc','-f',$taskDump)
  Compose -Arguments @('exec','-T','postgres','createdb','-U',$taskEnv.POSTGRES_USER,$taskDatabase)
  try{
   Compose -Arguments @('exec','-T','postgres','pg_restore','-U',$taskEnv.POSTGRES_USER,'-d',$taskDatabase,'--exit-on-error',$taskDump)
   Compose -Arguments @('exec','-T','-e',"RESTORE_DATABASE=$taskDatabase",'backend','python','restore_check.py')
  }finally{
   # Only the uniquely generated verification database is removed.
   Compose -Arguments @('exec','-T','postgres','dropdb','-U',$taskEnv.POSTGRES_USER,$taskDatabase)
  }
 }
}
