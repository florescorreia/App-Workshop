param(
  [Parameter(Position=0)][ValidateSet('doctor','init-env','up','status','logs','down','seed-demo','backup','restore-test','test')][string]$Action='status',
  [string]$Context, [int]$Port=0, [switch]$DryRun, [string]$BatchKey='harborworks-demo-v1', [int]$Seed=42,
  [string]$AnchorDate, [string]$File
)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskRoot
function Read-LocalEnv {
  $taskValues=@{}
  if(Test-Path -LiteralPath '.env') { Get-Content -LiteralPath '.env' | ForEach-Object { if($_ -match '^([^#=]+)=(.*)$'){$taskValues[$matches[1]]=$matches[2]} } }
  return $taskValues
}
function Get-RancherContext {
  $taskSettings=(& rdctl list-settings | ConvertFrom-Json)
  if($LASTEXITCODE -ne 0){throw 'Rancher Desktop is not reachable. Start Rancher Desktop and rerun doctor.'}
  if($taskSettings.containerEngine.name -ne 'moby'){throw 'Select Rancher Desktop > Preferences > Container Engine > General > dockerd (Moby), then apply. No settings were changed.'}
  $taskContexts=@(& docker context ls --format '{{.Name}}')
  $taskCandidate=$Context
  if(-not $taskCandidate){$taskCandidate=(Read-LocalEnv)['DOCKER_CONTEXT']}
  if($taskCandidate){$taskContexts=@($taskCandidate)}
  foreach($taskItem in $taskContexts){
    $taskInfo=& docker --context $taskItem info --format '{{.OperatingSystem}}' 2>$null
    if($LASTEXITCODE -eq 0 -and $taskInfo -match 'Rancher Desktop'){return $taskItem}
  }
  throw 'No reachable Rancher Desktop Docker context was found. Run docker context ls and scripts/ideaflow.ps1 doctor.'
}
function Invoke-Compose {
  param([string[]]$Arguments)
  & docker --context $script:taskContext compose --project-directory $taskRoot @Arguments
  if($LASTEXITCODE -ne 0){throw "Docker Compose failed ($LASTEXITCODE). Check engine, downloads and scripts/ideaflow.ps1 logs."}
}
function New-LocalSecret {
  $taskBytes=New-Object byte[] 24
  $taskRng=[Security.Cryptography.RandomNumberGenerator]::Create()
  try{$taskRng.GetBytes($taskBytes)}finally{$taskRng.Dispose()}
  return [Convert]::ToBase64String($taskBytes).TrimEnd('=').Replace('+','-').Replace('/','_')
}
if($Action -eq 'doctor'){
  & docker version; & docker compose version; & docker context ls
  $taskContext=Get-RancherContext
  Write-Host "Verified Rancher Desktop Moby context: $taskContext"
  & docker --context $taskContext info --format '{{.Name}} | {{.OperatingSystem}}'
  $taskListen=Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue
  Write-Host "Port 8080 occupied: $([bool]$taskListen)"
  exit
}
$script:taskContext=Get-RancherContext
if($Action -eq 'init-env'){
  if(Test-Path -LiteralPath '.env'){Write-Host 'Existing .env preserved.';exit}
  $taskPort=if($Port){$Port}else{8080}
  while(Get-NetTCPConnection -LocalPort $taskPort -State Listen -ErrorAction SilentlyContinue){$taskPort++}
  $taskPassword=New-LocalSecret
  $taskContent=Get-Content -Raw -LiteralPath '.env.example'
  $taskContent=$taskContent.Replace('DOCKER_CONTEXT=default',"DOCKER_CONTEXT=$script:taskContext").Replace('APP_PORT=8080',"APP_PORT=$taskPort")
  $taskContent=$taskContent.Replace('POSTGRES_PASSWORD=GENERATE_LOCALLY',"POSTGRES_PASSWORD=$(New-LocalSecret)").Replace('APP_DB_PASSWORD=GENERATE_LOCALLY',"APP_DB_PASSWORD=$(New-LocalSecret)").Replace('ADMIN_PASSWORD=GENERATE_LOCALLY',"ADMIN_PASSWORD=$taskPassword")
  [IO.File]::WriteAllText((Join-Path $taskRoot '.env'),$taskContent,(New-Object Text.UTF8Encoding $false))
  New-Item -ItemType Directory -Path local -Force | Out-Null
  [IO.File]::WriteAllText((Join-Path $taskRoot 'local/first-login.txt'),"URL: http://localhost:$taskPort`r`nEmail: admin@ideaflow.local`r`nPassword: $taskPassword`r`n",(New-Object Text.UTF8Encoding $false))
  Write-Host "Local secrets generated. First login is in the gitignored local/first-login.txt. Open it privately. Context: $script:taskContext"
  exit
}
if(-not(Test-Path -LiteralPath '.env')){throw 'Run scripts/ideaflow.ps1 init-env first.'}
$taskEnv=Read-LocalEnv
switch($Action){
  'up'{
    New-Item -ItemType Directory -Path local -Force | Out-Null
    Invoke-Compose -Arguments @('up','--build','-d','--wait','--wait-timeout','180')
    $taskUrl="http://localhost:$($taskEnv['APP_PORT'])"
    $taskReady=Invoke-RestMethod -Uri "$taskUrl/api/health/ready"
    if($taskReady.status -ne 'ready'){throw 'Readiness verification failed'}
    Write-Host "IdeaFlow verified ready: $taskUrl | Login: local/first-login.txt"
  }
  'status'{Invoke-Compose -Arguments @('ps')}
  'logs'{Invoke-Compose -Arguments @('logs','--tail','100')}
  'down'{Invoke-Compose -Arguments @('down');Write-Host 'IdeaFlow stopped; named volume preserved.'}
  'seed-demo'{
    $taskArgs=@('exec','-T','backend','python','-m','app.demo','--batch-key',$BatchKey,'--seed',"$Seed")
    if($AnchorDate){$taskArgs+=@('--anchor-date',$AnchorDate)}
    if($DryRun){$taskArgs+='--dry-run'}
    if($File){
      $taskResolved=(Resolve-Path -LiteralPath $File).Path
      $taskName=Split-Path -Leaf $taskResolved
      Invoke-Compose -Arguments @('cp',$taskResolved,"backend:/tmp/$taskName")
      $taskArgs+=@('--file',"/tmp/$taskName")
    }
    Invoke-Compose -Arguments $taskArgs
  }
  'test'{Invoke-Compose -Arguments @('exec','-T','backend','pytest','-q')}
  'backup'{
    New-Item -ItemType Directory -Path backups -Force | Out-Null
    $taskStamp=Get-Date -Format 'yyyyMMdd-HHmmss'
    $taskDump="/tmp/ideaflow-$taskStamp.dump"
    Invoke-Compose -Arguments @('exec','-T','postgres','pg_dump','-U',$taskEnv['POSTGRES_USER'],'-d',$taskEnv['POSTGRES_DB'],'-Fc','-f',$taskDump)
    Invoke-Compose -Arguments @('cp',"postgres:$taskDump",(Join-Path $taskRoot "backups/ideaflow-$taskStamp.dump"))
    Invoke-Compose -Arguments @('exec','-T','postgres','rm',$taskDump)
    Write-Host "Binary-safe custom dump saved: backups/ideaflow-$taskStamp.dump"
  }
  'restore-test'{
    if(-not $File){$File=(Get-ChildItem -LiteralPath backups -Filter '*.dump' | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName}
    if(-not $File){throw 'Create a backup first or specify -File.'}
    $taskResolved=(Resolve-Path -LiteralPath $File).Path
    $taskTemp='ideaflow_restore_'+[Guid]::NewGuid().ToString('N')
    Invoke-Compose -Arguments @('cp',$taskResolved,"postgres:/tmp/$taskTemp.dump")
    try{
      Invoke-Compose -Arguments @('exec','-T','postgres','createdb','-U',$taskEnv['POSTGRES_USER'],$taskTemp)
      Invoke-Compose -Arguments @('exec','-T','postgres','pg_restore','-U',$taskEnv['POSTGRES_USER'],'--exit-on-error','--no-owner','-d',$taskTemp,"/tmp/$taskTemp.dump")
      Invoke-Compose -Arguments @('exec','-T','backend','python','-m','app.restore_check','--database',$taskTemp)
    }finally{
      Invoke-Compose -Arguments @('exec','-T','postgres','dropdb','-U',$taskEnv['POSTGRES_USER'],'--if-exists',$taskTemp)
      Invoke-Compose -Arguments @('exec','-T','postgres','rm',"/tmp/$taskTemp.dump")
    }
  }
}
