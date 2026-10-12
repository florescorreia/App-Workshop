param([string]$Context='default')
$ErrorActionPreference='Stop'
$taskRoot=(Resolve-Path (Split-Path -Parent $PSScriptRoot)).Path
$taskKeep='f915add360dbb874d2d47710'
$taskOld=@('a4e176281f3c47d081b3b623','b5e287392a4d58e192c4c734')
function D([string[]]$Arguments){$result=& docker --context $Context @Arguments; if($LASTEXITCODE -ne 0){throw 'Scoped cleanup Docker operation failed'}; return $result}
$taskOS=D @('info','--format','{{.OperatingSystem}}')
if($taskOS -notmatch 'Rancher Desktop'){throw 'Verified Rancher Moby engine required'}
$taskItems=@(D @('ps','-aq'))
$taskContainers=if($taskItems.Count){@(D (@('inspect')+$taskItems)|ConvertFrom-Json)}else{@()}
$taskVolumes=@(D @('volume','ls','--format','{{.Name}}'))
$taskNetworks=@(D @('network','ls','--format','{{.Name}}'))
$taskPattern='^governed-dd-(?:a4e176281f3c47d081b3b623-|b5e287392a4d58e192c4c734-|restore-)'
$taskDeleteContainers=@($taskContainers|Where-Object {$_.Name.TrimStart('/') -match $taskPattern})
if($taskDeleteContainers|Where-Object {$_.State.Running}){throw 'Old engagement containers must be stopped before deletion'}
$taskDeleteVolumes=@($taskVolumes|Where-Object {$_ -match $taskPattern})
$taskDeleteNetworks=@($taskNetworks|Where-Object {$_ -match $taskPattern})
if(@($taskDeleteContainers.Name)+$taskDeleteVolumes+$taskDeleteNetworks | Where-Object {$_ -match $taskKeep}){throw 'Harborlight may not be a deletion target'}
$taskOtherContainers=@($taskContainers|Where-Object {$_.Name -notmatch '^/governed-dd-' }|ForEach-Object Id)
$taskOtherVolumes=@($taskVolumes|Where-Object {$_ -notmatch '^governed-dd-'})
$taskKeepVolumes=@($taskVolumes|Where-Object {$_ -match ('^governed-dd-'+$taskKeep+'-')})
if($taskKeepVolumes.Count -lt 10){throw 'Harborlight storage prerequisite missing'}
# Authoritative membership removal precedes disposal of private backend data.
$taskCode=@'
from main import control_db
old=('a4e176281f3c47d081b3b623','b5e287392a4d58e192c4c734')
with control_db() as db:
    assert db.execute('SELECT 1 FROM tenants WHERE id=%s AND active',('f915add360dbb874d2d47710',)).fetchone()
    for tenant in old:
        db.execute('DELETE FROM component_tickets WHERE tenant=%s',(tenant,))
        db.execute('DELETE FROM memberships WHERE tenant=%s',(tenant,))
        db.execute('DELETE FROM tenants WHERE id=%s',(tenant,))
        db.execute('INSERT INTO control_audit(subject,operation,tenant) VALUES(%s,%s,%s)',('administrator-cli','explicit-delete-engagement',tenant))
print('Old engagements removed from directory; Harborlight preserved.')
'@
D @('exec','governed-dd-control-portal-1','python','-c',$taskCode)
foreach($taskContainer in $taskDeleteContainers){D @('rm',$taskContainer.Id)|Out-Null}
foreach($taskNetwork in $taskDeleteNetworks){
 $taskNetworkInfo=D @('network','inspect',$taskNetwork)|ConvertFrom-Json
 foreach($taskEndpoint in $taskNetworkInfo.Containers.PSObject.Properties){
  if($taskEndpoint.Value.Name -ne 'governed-dd-control-portal-1'){throw 'Unexpected network attachment; refused removal'}
  D @('network','disconnect',$taskNetwork,$taskEndpoint.Name)|Out-Null
 }
 D @('network','rm',$taskNetwork)|Out-Null
}
foreach($taskVolume in $taskDeleteVolumes){D @('volume','rm',$taskVolume)|Out-Null}
# Resolve/check each absolute filesystem target under this app before recursive removal.
function Remove-AppPath([string]$Relative){
 $taskPath=[IO.Path]::GetFullPath((Join-Path $taskRoot $Relative))
 if(-not $taskPath.StartsWith($taskRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Deletion escaped app folder'}
 if($taskPath -match $taskKeep){throw 'Harborlight files must be retained'}
 if(Test-Path -LiteralPath $taskPath){Remove-Item -LiteralPath $taskPath -Recurse -Force}
}
foreach($taskId in $taskOld){Remove-AppPath "local/tenants/$taskId"}
foreach($taskFile in Get-ChildItem -LiteralPath (Join-Path $taskRoot 'local/secrets') -File){
 if($taskFile.Name -match ('^(?:'+($taskOld -join '|')+')-') -or $taskFile.Name -in @('native-alice-test.json','native-test.json')){Remove-AppPath ('local/secrets/'+$taskFile.Name)}
}
# Every existing recovery archive predates Harborlight and contains only old demo tenants.
foreach($taskBackup in Get-ChildItem -LiteralPath (Join-Path $taskRoot 'backups') -Directory){
 $taskFiles=@(Get-ChildItem -LiteralPath $taskBackup.FullName -File)
 if($taskFiles.Name -match $taskKeep){throw 'Harborlight backup must be retained'}
 if($taskFiles.Name -match ('^governed-dd-(?:'+($taskOld -join '|')+')-')){Remove-AppPath ('backups/'+$taskBackup.Name)}
}
foreach($taskFolder in @('local/restores','local/vps-review-tenant-a-20261011','local/vps-tenant-final-review')){Remove-AppPath $taskFolder}
foreach($taskFile in @('local/cancel-task.txt','local/native-attestation.json','local/rancher-restart-containers.txt','local/rancher-restart-volumes.txt','local/vps-tenant-image-map.json')){Remove-AppPath $taskFile}
foreach($taskFile in Get-ChildItem -LiteralPath (Join-Path $taskRoot 'local/evidence') -File){if($taskFile.Name -notlike 'harborlight-*'){Remove-AppPath ('local/evidence/'+$taskFile.Name)}}
# Remove deleted tenant native credentials, including exporter fallback values.
$taskEnv=Join-Path $taskRoot '.env'
$taskLines=@([IO.File]::ReadAllLines($taskEnv)|Where-Object {$_ -notmatch ('^DD_PAPERCLIP_(?:'+(($taskOld|ForEach-Object {$_.ToUpper()}) -join '|')+')_')})
[IO.File]::WriteAllLines($taskEnv,$taskLines,[Text.UTF8Encoding]::new($false))
$taskAfterContainers=@(D @('ps','-aq','--no-trunc'))
$taskAfterVolumes=@(D @('volume','ls','--format','{{.Name}}'))
if($taskOtherContainers|Where-Object {$_ -notin $taskAfterContainers}){throw 'Unrelated container missing'}
if(($taskOtherVolumes+$taskKeepVolumes)|Where-Object {$_ -notin $taskAfterVolumes}){throw 'Protected volume missing'}
Write-Output "Removed $($taskDeleteContainers.Count) containers, $($taskDeleteVolumes.Count) volumes and $($taskDeleteNetworks.Count) networks. Other projects and Harborlight storage preserved."
