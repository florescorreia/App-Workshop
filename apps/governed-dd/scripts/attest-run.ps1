param([Parameter(Mandatory)][string]$Tenant,[Parameter(Mandatory)][string]$Analysis,[Parameter(Mandatory)][int]$Version,[string]$Context='default')
$ErrorActionPreference='Stop'
if($Tenant -notmatch '^[a-f0-9]{24}$' -or $Analysis -notmatch '^[a-f0-9-]{36}$' -or $Version -lt 1){throw 'Exact tenant and analysis version required'}
$taskRoot=Split-Path -Parent $PSScriptRoot
$taskGov="governed-dd-$Tenant-governance-1";$taskNative="governed-dd-$Tenant-paperclip-1"
function D([string[]]$Arguments){$result=& docker --context $Context @Arguments;if($LASTEXITCODE -ne 0){throw 'Native provenance attestation failed'};return $result}
$taskManifest=(D @('exec',$taskGov,'python','-c',"import json;from domain import Domain;print(json.dumps(Domain().get({'id':'$Analysis','version':$Version})['body']))"))|ConvertFrom-Json
D @('cp',"$taskRoot/scripts/native-attest.cjs","${taskNative}:/tmp/native-attest.cjs")|Out-Null
$taskEvidence=(D @('exec',$taskNative,'node','/tmp/native-attest.cjs',$taskManifest.paperclip_run_id))|ConvertFrom-Json
if($taskEvidence.task_id -ne $taskManifest.task_id -or $taskEvidence.paperclip_instance -ne $taskManifest.paperclip_instance){throw 'Declared task/instance does not match native history'}
if($taskManifest.code_commit -notmatch '^[a-f0-9]{40}$'){throw 'Full code commit required'}
D @('exec','--user','1000',"governed-dd-$Tenant-runtime-1",'git','-C','/engagement','cat-file','-e',"$($taskManifest.code_commit)^{commit}")|Out-Null
$taskEvidence|Add-Member -NotePropertyName analysis -NotePropertyValue @{id=$Analysis;version=$Version}
$taskEvidence|Add-Member -NotePropertyName code_commit -NotePropertyValue $taskManifest.code_commit
$taskEvidence|Add-Member -NotePropertyName limitation -NotePropertyValue 'Native API verifies task/run linkage and successful completion; Git verifies commit exists. Historical image and actual code execution require independent review.'
$taskFile=Join-Path $taskRoot 'local/native-attestation.json'
[IO.File]::WriteAllText($taskFile,($taskEvidence|ConvertTo-Json -Depth 10))
D @('cp',$taskFile,"${taskGov}:/tmp/native-attestation.json")|Out-Null
D @('exec',$taskGov,'python','-c',"import json,uuid;from psycopg.types.json import Jsonb;from domain import Domain;d=Domain();b=json.load(open('/tmp/native-attestation.json'));ident=str(uuid.uuid4());db=d.connect();db.execute('INSERT INTO records(id,version,tenant,kind,status,body,actor) VALUES(%s,1,%s,%s,%s,%s,%s)',(ident,d.tenant,'RunAttestation','verified',Jsonb(b),'administrator:native-api'));db.execute('INSERT INTO outbox(id,version) VALUES(%s,1)',(ident,));db.commit();print('Native run linkage and Git commit verified; attestation persisted.')")
