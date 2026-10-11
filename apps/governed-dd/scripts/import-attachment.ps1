param([Parameter(Mandatory)][string]$Tenant,[Parameter(Mandatory)][string]$Task,[Parameter(Mandatory)][string]$Attachment,[string]$Context='default')
$ErrorActionPreference='Stop'
if($Tenant -notmatch '^[a-f0-9]{24}$' -or $Task -notmatch '^[a-f0-9-]{36}$' -or $Attachment -notmatch '^[a-f0-9-]{36}$'){throw 'Exact tenant/task/attachment IDs required'}
$taskRoot=Split-Path -Parent $PSScriptRoot;$taskId='dd-import-'+[Guid]::NewGuid().ToString('N');$taskNative="governed-dd-$Tenant-paperclip-1";$taskGov="governed-dd-$Tenant-governance-1"
function D([string[]]$Arguments){& docker --context $Context @Arguments;if($LASTEXITCODE -ne 0){throw 'Native attachment import failed'}}
$taskLocal=Join-Path $taskRoot "local/$taskId"
try{
 D @('cp',"$PSScriptRoot/native-attachment.cjs","${taskNative}:/tmp/native-attachment.cjs")
 D @('exec',$taskNative,'node','/tmp/native-attachment.cjs',$Task,$Attachment,"/tmp/$taskId")
 D @('cp',"${taskNative}:/tmp/$taskId",$taskLocal)
 D @('cp',$taskLocal,"${taskGov}:/tmp/$taskId")
 D @('exec','--user','root',$taskGov,'chown','-R','1101:1101',"/tmp/$taskId")
 D @('cp',"$PSScriptRoot/import-attachment.py","${taskGov}:/tmp/import-attachment.py")
 D @('exec','-e','PYTHONPATH=/app',$taskGov,'python','/tmp/import-attachment.py',"/tmp/$taskId")
}finally{
 foreach($taskContainer in @($taskNative,$taskGov)){& docker --context $Context exec --user root $taskContainer rm -rf -- "/tmp/$taskId" | Out-Null}
 if(Test-Path -LiteralPath $taskLocal){$taskResolved=[IO.Path]::GetFullPath($taskLocal);$taskAllowed=[IO.Path]::GetFullPath((Join-Path $taskRoot 'local'))+[IO.Path]::DirectorySeparatorChar;if(-not $taskResolved.StartsWith($taskAllowed)){throw 'Unsafe temporary path'};Remove-Item -LiteralPath $taskResolved -Recurse -Force}
}
