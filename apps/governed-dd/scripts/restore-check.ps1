param([Parameter(Mandatory)][string]$Prefix,[string]$Context='default')
$ErrorActionPreference='Stop'
if($Prefix -notmatch '^governed-dd-restore-[a-f0-9]{12}$'){throw 'Use a prefix produced by the isolated restore command'}
$taskAppRoot=Split-Path -Parent $PSScriptRoot
$taskA='a4e176281f3c47d081b3b623';$taskB='b5e287392a4d58e192c4c734'
function D([string[]]$Arguments){& docker --context $Context @Arguments;if($LASTEXITCODE -ne 0){throw 'Isolated recovery check failed'}}
$taskNetwork="$Prefix-check"
$taskExists=& docker --context $Context network ls --filter "name=^$taskNetwork$" --format '{{.Name}}'
if(-not $taskExists){D @('network','create','--internal','--subnet','10.253.251.0/24',$taskNetwork)}
$taskContainers=@()
try{
 foreach($taskPair in @(@('control','control-db','postgres:17.6-bookworm'),@('a',"$taskA-postgres",'paradedb/paradedb:0.26.1-pg17'),@('b',"$taskB-postgres",'paradedb/paradedb:0.26.1-pg17'))){
  $taskContainer="$Prefix-check-$($taskPair[0])";$taskContainers+=$taskContainer
  $taskExists=& docker --context $Context ps -a --filter "name=^/$taskContainer$" --format '{{.Names}}'
  if($taskExists){D @('start',$taskContainer)}else{D @('run','-d','--name',$taskContainer,'--network',$taskNetwork,'--network-alias',"restore-$($taskPair[0])",'--memory','1g','-v',"${Prefix}-governed-dd-$($taskPair[1]):/var/lib/postgresql/data",$taskPair[2])}
 }
 D @('run','--rm','--user','root','--network',$taskNetwork,'--mount',"type=bind,source=$taskAppRoot/scripts/restore-check.py,target=/check.py,readonly",'-v',"${Prefix}-configuration:/configuration:ro",'-v',"${Prefix}-governed-dd-$taskA-artifacts:/artifacts/a:ro",'-v',"${Prefix}-governed-dd-$taskB-artifacts:/artifacts/b:ro",'-e',"TENANT_A=$taskA",'-e',"TENANT_B=$taskB",'--entrypoint','python','governed-dd-governance:0.1.0','/check.py')
}finally{foreach($taskContainer in $taskContainers){D @('stop',$taskContainer)}}
Write-Host 'Read-only isolated database/file recovery passed. Test containers stopped; restored volumes retained.'
