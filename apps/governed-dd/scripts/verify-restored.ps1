param([Parameter(Mandatory)][string]$Prefix,[string]$Context='default')
$ErrorActionPreference='Stop'
if($Prefix -notmatch '^governed-dd-restore-[a-f0-9]{12}$'){throw 'Fresh restore prefix required'}
$taskRoot=Split-Path -Parent $PSScriptRoot;$taskName="$Prefix-verification"
function D([string[]]$Arguments){& docker --context $Context @Arguments;if($LASTEXITCODE -ne 0){throw 'Restored verification failed'}}
$taskArgs=@('create','--name',$taskName,'--user','root','--network',"$Prefix-control-control",'--mount',"type=bind,source=$taskRoot/tests/restored_stack.py,target=/check.py,readonly",'-v',"${Prefix}-configuration:/configuration:ro")
foreach($taskPair in @(@('a','a4e176281f3c47d081b3b623'),@('b','b5e287392a4d58e192c4c734'))){$taskArgs+=@('-v',"${Prefix}-governed-dd-$($taskPair[1])-paperclip:/native/$($taskPair[0]):ro")}
$taskArgs+=@('-v',"${Prefix}-governed-dd-a4e176281f3c47d081b3b623-ontology:/ontology/a:ro",'-v',"${Prefix}-governed-dd-a4e176281f3c47d081b3b623-git:/workspace/a:ro",'--entrypoint','python','governed-dd-governance:0.1.0','/check.py')
D $taskArgs
foreach($taskTenant in @('a4e176281f3c47d081b3b623','b5e287392a4d58e192c4c734')){D @('network','connect',"$Prefix-$taskTenant-ingress",$taskName)}
D @('start','-a',$taskName)
$taskExit=& docker --context $Context inspect $taskName --format '{{.State.ExitCode}}'
if($taskExit -ne '0'){throw 'Restored application check failed'}
foreach($taskTenant in @('a4e176281f3c47d081b3b623','b5e287392a4d58e192c4c734')){
 $taskGov="$Prefix-app-$taskTenant-governance-1"
 D @('cp',"$taskRoot/tests/restored_vectors.py","${taskGov}:/tmp/restored_vectors.py")
 D @('exec','-e','PYTHONPATH=/app',$taskGov,'python','/tmp/restored_vectors.py')
}
Write-Host 'Complete restored-stack checks passed. Test container and volumes retained; stop the restored Compose separately.'
