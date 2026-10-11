param([Parameter(Mandatory)][string]$Prefix,[string]$Context='default',[string]$SubnetPrefix='10.252')
$ErrorActionPreference='Stop'
if($Prefix -notmatch '^governed-dd-restore-[a-f0-9]{12}$'){throw 'Use an authenticated restore prefix'}
$taskAppRoot=Split-Path -Parent $PSScriptRoot
function D([string[]]$Arguments){& docker --context $Context @Arguments;if($LASTEXITCODE -ne 0){throw 'Full isolated restore failed'}}
# Refuse overlapping requested networks before rendering or starting a copy.
$taskNetworks=@(& docker --context $Context network ls -q)
if($SubnetPrefix -notmatch '^10\.(?:[1-9][0-9]?|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'){throw 'Reviewed private 10.x prefix required'}
if($taskNetworks.Count){$taskKnown=& docker --context $Context network inspect @taskNetworks --format '{{range .IPAM.Config}}{{.Subnet}} {{end}}';if($taskKnown -match ([regex]::Escape($SubnetPrefix)+'\.')){throw '10.252 restore range already in use; retain existing copies and select a reviewed range'}}
$env:RESTORE_SUBNET_PREFIX=$SubnetPrefix
$env:HOST_APP_ROOT=$taskAppRoot
$env:RESTORED_VOLUMES=ConvertTo-Json -Compress -InputObject @(& docker --context $Context volume ls --filter "name=^$Prefix-" --format '{{.Name}}')
D @('run','--rm','--user','root','-e','HOST_APP_ROOT','-e','RESTORED_VOLUMES','-e','RESTORE_SUBNET_PREFIX','--mount',"type=bind,source=$taskAppRoot,target=/workspace",'-v',"${Prefix}-configuration:/configuration:ro",'--entrypoint','python','governed-dd-governance:0.1.0','/workspace/scripts/restore-stack.py',$Prefix)
$taskCompose=Join-Path $taskAppRoot "local/restores/$Prefix/restore.compose.yaml"
D @('compose','-f',$taskCompose,'config','--quiet')
D @('volume','create',"$Prefix-frontend")
D @('run','--rm','--user','root','-v',"${Prefix}-frontend:/target",'--entrypoint','sh','governed-dd-explorer:0.1.0','-c','cp -r /usr/share/nginx/html/. /target/')
D @('compose','-f',$taskCompose,'up','-d')
Write-Host "Isolated full app started without published ports. Test on network $Prefix-control-control; stop with docker --context $Context compose -f $taskCompose stop."
