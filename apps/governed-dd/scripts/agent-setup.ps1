param([Parameter(Mandatory)][string]$Tenant,[ValidateSet('setup','smoke','analysis','review')][string]$Action='setup',[string]$Context='default')
$ErrorActionPreference='Stop'
if($Tenant -notmatch '^[a-f0-9]{24}$'){throw 'Opaque tenant required'}
$taskAppRoot=Split-Path -Parent $PSScriptRoot
$taskContainer="governed-dd-$Tenant-paperclip-1"
function D([string[]]$Arguments){& docker --context $Context @Arguments;if($LASTEXITCODE -ne 0){throw 'Agent integration operation failed'}}
D @('cp',"$taskAppRoot/scripts/native-ready.cjs","${taskContainer}:/tmp/native-ready.cjs")
D @('exec',$taskContainer,'node','/tmp/native-ready.cjs')
D @('cp',"$taskAppRoot/scripts/paperclip-runtime.cjs","${taskContainer}:/tmp/paperclip-runtime.cjs")
D @('cp',"$taskAppRoot/local/secrets/$Tenant-runtime-private","${taskContainer}:/tmp/runtime-private")
# Obtain known-host records inside only the dedicated tenant runtime network.
$taskKnown=& docker --context $Context exec $taskContainer ssh-keyscan -p 2222 runtime 2>$null
if($LASTEXITCODE -ne 0 -or -not $taskKnown){throw 'Analyst runtime unavailable'}
$taskReviewKnown=& docker --context $Context exec $taskContainer ssh-keyscan -p 2222 runtime-reviewer 2>$null
if($LASTEXITCODE -ne 0 -or -not $taskReviewKnown){throw 'Reviewer runtime unavailable'}
$taskPrivateFolder=Join-Path $taskAppRoot "local/tenants/$Tenant"
[IO.File]::WriteAllText((Join-Path $taskPrivateFolder 'runtime-known-hosts'),($taskKnown -join "`n")+"`n")
[IO.File]::WriteAllText((Join-Path $taskPrivateFolder 'reviewer-known-hosts'),($taskReviewKnown -join "`n")+"`n")
D @('cp',"$taskPrivateFolder/runtime-known-hosts","${taskContainer}:/tmp/runtime-known-hosts")
D @('cp',"$taskPrivateFolder/reviewer-known-hosts","${taskContainer}:/tmp/reviewer-known-hosts")
D @('exec',$taskContainer,'node','/tmp/paperclip-runtime.cjs',$Action)
Write-Host 'Native isolated agent configuration applied; only explicitly selected checks start tasks.'
