param([Parameter(Position=0)][string]$Action='doctor',[string]$Context,[string]$Tenant,[string]$Name,[string]$Subject,[ValidateSet('owner','analyst','reviewer','viewer')][string]$Role='viewer')
$ErrorActionPreference='Stop'
$taskAppRoot=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskAppRoot
$taskSettings=& rdctl list-settings
if($LASTEXITCODE -ne 0 -or ($taskSettings|ConvertFrom-Json).containerEngine.name -ne 'moby'){throw 'Start Rancher Desktop with Moby. No host settings changed.'}
$taskContext=$null
$taskCandidates=if($Context){@($Context)}else{@(& docker context ls --format '{{.Name}}')}
foreach($taskCandidate in $taskCandidates){$taskOS=& docker --context $taskCandidate info --format '{{.OperatingSystem}}' 2>$null;if($LASTEXITCODE -eq 0 -and $taskOS -match 'Rancher Desktop'){$taskContext=$taskCandidate;break}}
if(-not $taskContext){throw 'No Rancher Desktop Moby context found'}
function Run-Docker([string[]]$Arguments){& docker --context $taskContext @Arguments;if($LASTEXITCODE -ne 0){throw 'Governed DD container operation failed'}}
function Tool([string[]]$Arguments){Run-Docker (@('run','--rm','--user','root','--mount',"type=bind,source=$taskAppRoot,target=/workspace",'-w','/workspace','--entrypoint','python','governed-dd-governance:0.1.0','-B','scripts/render.py')+$Arguments)}
function Control([string[]]$Arguments){Run-Docker (@('compose','-f','local/control.compose.yaml')+$Arguments)}
function Tenant-Compose([string[]]$Arguments){if($Tenant -notmatch '^[a-f0-9]{24}$'){throw 'Use an opaque tenant ID'};Run-Docker (@('compose','-f',"local/tenants/$Tenant/compose.yaml")+$Arguments)}
function Admin([string[]]$Arguments){Run-Docker (@('compose','-f','local/control.compose.yaml','exec','-T','portal','python','/app/admin.py')+$Arguments)}
function Capacity([string]$Manifest){
 $taskMemory=[double](& docker --context $taskContext info --format '{{.MemTotal}}')
 $taskPlan=(& docker --context $taskContext compose -f $Manifest config --format json | ConvertFrom-Json)
 $taskProjects=@{};$taskReservation=0.0
 $taskRunning=@(& docker --context $taskContext ps -q)
 if($taskRunning.Count){$taskContainers=(& docker --context $taskContext inspect @taskRunning|ConvertFrom-Json);foreach($taskContainer in $taskContainers){$taskProject=$taskContainer.Config.Labels.'com.docker.compose.project';$taskService=$taskContainer.Config.Labels.'com.docker.compose.service';$taskProjects["$taskProject/$taskService"]=$true;$taskLimit=[double]$taskContainer.HostConfig.Memory;if($taskLimit -le 0){throw "Unsafe start: existing container $($taskContainer.Name) has no memory reservation. Review host capacity first."};$taskReservation+=$taskLimit}}
 foreach($taskService in $taskPlan.services.PSObject.Properties){if($taskService.Value.profiles){continue};if(-not $taskProjects.ContainsKey("$($taskPlan.name)/$($taskService.Name)")){$taskReservation+=[double]$taskService.Value.mem_limit}}
 if($taskReservation+2GB -gt $taskMemory){throw "Unsafe start: existing and proposed container limits reserve $([Math]::Round($taskReservation/1GB,2)) GiB; engine has $([Math]::Round($taskMemory/1GB,2)) GiB and requires 2 GiB headroom. Stop inactive tenants or increase the reviewed engine budget."}
}
$taskAdminLock=$null
if($Action -in @('up','tenant-start','tenant-create','setup','runtime-enable')){
 New-Item -ItemType Directory -Force -Path (Join-Path $taskAppRoot 'local')|Out-Null
 try{$taskAdminLock=[IO.File]::Open((Join-Path $taskAppRoot 'local/administration.lock'),[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)}catch{throw 'Another Governed DD administration operation is active. Retry after it completes.'}
}
try{
switch($Action){
 'doctor'{Write-Host "Rancher Desktop Moby context: $taskContext";Run-Docker @('compose','version');Run-Docker @('info','--format','CPUs={{.NCPU}} memory={{.MemTotal}}')}
 'build'{Run-Docker @('build','-f','services/governance/Dockerfile','-t','governed-dd-governance:0.1.0','.');Run-Docker @('build','-f','frontend/Dockerfile','-t','governed-dd-explorer:0.1.0','.');Run-Docker @('build','-f','infra/tenant-template/Paperclip.Dockerfile','-t','governed-dd-paperclip:2026.1005.0','.');Run-Docker @('build','-f','infra/tenant-template/Runtime.Dockerfile','-t','governed-dd-runtime:2026.1005.0','.')}
 'setup'{Tool @('setup');Control @('config','--quiet')}
 'init-env'{Tool @('setup');Control @('config','--quiet')}
 'up'{Capacity 'local/control.compose.yaml';Control @('config','--quiet');Control @('up','-d');Run-Docker @('run','--rm','--user','root','-v','governed-dd-frontend:/target','--entrypoint','sh','governed-dd-explorer:0.1.0','-c','cp -r /usr/share/nginx/html/. /target/');$taskPortal=& docker --context $taskContext compose -f local/control.compose.yaml ps -q portal;$taskAttached=& docker --context $taskContext inspect $taskPortal --format '{{json .NetworkSettings.Networks}}';$taskIngress=@(& docker --context $taskContext network ls --format '{{.Name}}' | Where-Object {$_ -match '^governed-dd-[a-f0-9]{24}-ingress$'});foreach($taskNetwork in $taskIngress){if($taskAttached -notmatch $taskNetwork){Run-Docker @('network','connect',$taskNetwork,$taskPortal)}};Write-Host 'Portal: http://localhost:8081 (empty until engagements are assigned)'}
 'down'{Control @('stop')}
 'status'{Control @('ps')}
 'logs'{Control @('logs','--tail','80')}
 'tenant-create'{if(-not $Tenant){$taskBytes=New-Object byte[] 12;[Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($taskBytes);$Tenant=([BitConverter]::ToString($taskBytes)).Replace('-','').ToLower()};if(-not $Name){throw 'Tenant creation requires -Name'};Tool @('tenant','--id',$Tenant,'--name',$Name);Tenant-Compose @('config','--quiet');Admin @('tenant','--tenant',$Tenant,'--name',$Name);Write-Host "Created tenant $Tenant"}
 'tenant-start'{Capacity "local/tenants/$Tenant/compose.yaml";Tenant-Compose @('config','--quiet');Tenant-Compose @('up','-d');$taskPortal=& docker --context $taskContext compose -f local/control.compose.yaml ps -q portal;$taskAttached=& docker --context $taskContext inspect $taskPortal --format '{{json .NetworkSettings.Networks}}';if($taskAttached -notmatch "governed-dd-$Tenant-ingress"){Run-Docker @('network','connect',"governed-dd-$Tenant-ingress",$taskPortal)};Admin @('active','--tenant',$Tenant,'--value','true')}
 'demo-seed'{Tenant-Compose @('exec','-T','governance','python','/app/fixtures.py')}
 'tenant-stop'{Admin @('active','--tenant',$Tenant,'--value','false');Tenant-Compose @('--profile','*','stop')}
 'member-add'{Admin @('member-add','--tenant',$Tenant,'--subject',$Subject,'--role',$Role)}
 'member-remove'{Admin @('member-remove','--tenant',$Tenant,'--subject',$Subject)}
 'user-create'{if(-not $Name -or $Name -notmatch '^[a-z][a-z0-9-]{1,40}$'){throw 'Use -Name for a lowercase login username'};Run-Docker @('run','--rm','--user','root','--network','governed-dd-control-v2','--mount',"type=bind,source=$taskAppRoot/local/secrets/keycloak-admin,target=/run/secrets/keycloak-admin,readonly",'-v','governed-dd-identity-private:/private','--entrypoint','python','governed-dd-governance:0.1.0','/app/identity.py','create',$Name)}
 'test'{Run-Docker @('run','--rm','--entrypoint','python','governed-dd-governance:0.1.0','-m','pytest','-q','-p','no:cacheprovider','/app/tests/test_security.py')}
 'database-harden'{if($Tenant -notmatch '^[a-f0-9]{24}$'){throw 'Opaque tenant required'};Run-Docker @('run','--rm','--user','root','-e',"TENANT_ID=$Tenant",'--network',"governed-dd-$Tenant-backend",'--mount',"type=bind,source=$taskAppRoot/local/secrets/$Tenant-admin,target=/run/secrets/admin,readonly",'--mount',"type=bind,source=$taskAppRoot/scripts/database-security.py,target=/security.py,readonly",'--entrypoint','python','governed-dd-governance:0.1.0','/security.py');Run-Docker @('run','--rm','--user','root','--mount',"type=bind,source=$taskAppRoot,target=/workspace",'--entrypoint','python','governed-dd-governance:0.1.0','-c',"from pathlib import Path;import yaml;p=Path('/workspace/local/tenants/$Tenant/compose.yaml');c=yaml.safe_load(p.read_text());c['services']['governance']['environment']['SERVICE_SCHEMA_MANAGED']='true';p.write_text(yaml.safe_dump(c,sort_keys=False))");Tenant-Compose @('config','--quiet');Tenant-Compose @('up','-d','--no-deps','governance')}
 'provider-configure'{if($Tenant -notmatch '^[a-f0-9]{24}$'){throw 'Opaque tenant required'};$taskProviderArguments=@('run','--rm','--user','root');foreach($taskLine in Get-Content .env){if($taskLine -match '^(WEB_SEARCH|EMBEDDING)_API_KEY_ENV=([A-Za-z_][A-Za-z0-9_]*)$'){$taskKeyName=$matches[2];if(-not [Environment]::GetEnvironmentVariable($taskKeyName,'Process')){[Environment]::SetEnvironmentVariable($taskKeyName,[Environment]::GetEnvironmentVariable($taskKeyName,'User'),'Process')};$taskProviderArguments+=@('-e',$taskKeyName)}};Run-Docker ($taskProviderArguments+@('--mount',"type=bind,source=$taskAppRoot,target=/workspace",'--entrypoint','python','governed-dd-governance:0.1.0','/workspace/scripts/provider-render.py',$Tenant));Tenant-Compose @('config','--quiet');Write-Host 'Private provider injection prepared; recreate governance when no active jobs or agent runs.'}
 'config-check'{Run-Docker @('run','--rm','--mount',"type=bind,source=$taskAppRoot,target=/workspace,readonly",'--entrypoint','python','governed-dd-governance:0.1.0','/workspace/scripts/config-check.py')}
 'agent-setup'{& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'agent-setup.ps1') -Tenant $Tenant -Context $taskContext;if($LASTEXITCODE -ne 0){throw 'Agent setup failed'}}
 'agent-check'{& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'agent-setup.ps1') -Tenant $Tenant -Action smoke -Context $taskContext;if($LASTEXITCODE -ne 0){throw 'Agent check failed'}}
 'native-bootstrap'{& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'native-provision.ps1') -Tenant $Tenant -Context $taskContext;if($LASTEXITCODE -ne 0){throw 'Native bootstrap failed'}}
 'native-user'{& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'native-provision.ps1') -Tenant $Tenant -Name $Name -Role $Role -Context $taskContext;if($LASTEXITCODE -ne 0){throw 'Native user failed'}}
 'runtime-enable'{if($Tenant -notmatch '^[a-f0-9]{24}$'){throw 'Opaque tenant required'};if(-not $env:LITELLM_API_KEY){$env:LITELLM_API_KEY=[Environment]::GetEnvironmentVariable('LITELLM_API_KEY','User')};if(-not $env:LITELLM_API_KEY){throw 'Configure named LITELLM_API_KEY environment variable first'};Run-Docker @('run','--rm','--user','root','-e','LITELLM_API_KEY','-e','DD_RUNTIME_SUBNET','-e','DD_PROVIDER_EDGE_SUBNET','--mount',"type=bind,source=$taskAppRoot,target=/workspace",'--entrypoint','python','governed-dd-governance:0.1.0','/workspace/scripts/runtime-render.py',$Tenant);Tenant-Compose @('config','--quiet');Write-Host 'Runtime manifest rendered. Run tenant-start after capacity review; provision native agents through supported app scripts.'}
 'backup'{& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'backup.ps1') backup -Context $taskContext;if($LASTEXITCODE -ne 0){throw 'Backup failed'}}
 'restore-test'{throw 'Use scripts/backup.ps1 restore-test -Backup <absolute folder> to select the isolated restore input explicitly.'}
 'prepare-vps'{throw 'The PRD is not fully accepted; review docs/VPS_MIGRATION.md. Generic release rendering is prohibited.'}
 'rebuild-graph'{Tenant-Compose @('exec','-T','governance','python','-c','from domain import Domain; print(Domain().project(rebuild=True))')}
 'reindex'{Tenant-Compose @('exec','-T','governance','python','-c','from domain import Domain; print(Domain().reindex())')}
 default{throw "Unsupported action: $Action. See README.md"}
}

}finally{if($taskAdminLock){$taskAdminLock.Dispose()}}
