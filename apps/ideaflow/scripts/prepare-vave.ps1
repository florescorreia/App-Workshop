param()
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskRoot
$taskContext=(Get-Content .env | Where-Object {$_ -match '^DOCKER_CONTEXT='}) -replace '^DOCKER_CONTEXT=',''
$taskEngine=& docker --context $taskContext info --format '{{.OperatingSystem}}'
if($LASTEXITCODE -ne 0 -or $taskEngine -notmatch 'Rancher Desktop'){throw 'Configured Rancher Desktop Moby context unavailable'}
$taskRelease='local/releases/vave-'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
New-Item -ItemType Directory -Path $taskRelease | Out-Null
$taskVersion=(Get-Content frontend/package.json -Raw | ConvertFrom-Json).version
& docker --context $taskContext image save -o "$taskRelease/images.tar" "ideaflow-backend:$taskVersion" "ideaflow-frontend:$taskVersion"
if($LASTEXITCODE -ne 0){throw 'Image export failed'}
& docker --context $taskContext run --rm --mount "type=bind,source=$taskRoot,target=/workspace" --entrypoint python ideaflow-vps-tools:1.0.0 scripts/vave_release.py prepare --archive "$taskRelease/images.tar"
if($LASTEXITCODE -ne 0){throw 'Release digest verification failed'}
Write-Host "Prepared release: $taskRelease"
