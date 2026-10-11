param([switch]$SkipCreate)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskRoot
$taskContext=(Get-Content .env | Where-Object {$_ -match '^DOCKER_CONTEXT='}) -replace '^DOCKER_CONTEXT=',''
function Verify-Compose {param([string[]]$Arguments); & docker --context $taskContext compose -f compose.yaml -f compose.verify.yaml -p ideaflow-verification @Arguments; if($LASTEXITCODE -ne 0){throw 'Verification Compose command failed'}}
if(-not $SkipCreate){Verify-Compose @('exec','-T','backend','python','-m','app.persistence_probe','create')}
Verify-Compose @('down')
Verify-Compose @('up','-d','--wait','--wait-timeout','120')
Verify-Compose @('exec','-T','backend','python','-m','app.persistence_probe','check')
Verify-Compose @('up','--build','-d','--wait','--wait-timeout','120')
Verify-Compose @('exec','-T','backend','python','-m','app.persistence_probe','check')
New-Item -ItemType Directory -Path backups -Force | Out-Null
Verify-Compose @('exec','-T','postgres','pg_dump','-U','ideaflow_migrator','-d','ideaflow','-Fc','-f','/tmp/verification.dump')
Verify-Compose @('cp','postgres:/tmp/verification.dump','backups/verification.dump')
$taskTemp='ideaflow_restore_'+[Guid]::NewGuid().ToString('N')
try{
 Verify-Compose @('exec','-T','postgres','createdb','-U','ideaflow_migrator',$taskTemp)
 Verify-Compose @('exec','-T','postgres','pg_restore','-U','ideaflow_migrator','--no-owner','--exit-on-error','-d',$taskTemp,'/tmp/verification.dump')
 Verify-Compose @('exec','-T','backend','python','-m','app.restore_check','--database',$taskTemp)
}finally{
 Verify-Compose @('exec','-T','postgres','dropdb','-U','ideaflow_migrator','--if-exists',$taskTemp)
 Verify-Compose @('exec','-T','postgres','rm','/tmp/verification.dump')
}
