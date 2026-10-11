param([Parameter(Mandatory)][string]$Tenant,[string]$Name,[ValidateSet('owner','analyst','reviewer','viewer')][string]$Role='viewer',[string]$Context='default')
$ErrorActionPreference='Stop'
$taskAppRoot=Split-Path -Parent $PSScriptRoot
if($Tenant -notmatch '^[a-f0-9]{24}$'){throw 'Opaque tenant required'}
function D([string[]]$Arguments){& docker --context $Context @Arguments;if($LASTEXITCODE -ne 0){throw 'Native provisioning failed'}}
$taskFolder=Join-Path $taskAppRoot "local/tenants/$Tenant"
$taskContainer="governed-dd-$Tenant-paperclip-1"
# Private provisioning disables ingress before enabling native account creation. Always restore original config.
D @('run','--rm','--user','root','--mount',"type=bind,source=$taskAppRoot,target=/workspace",'--entrypoint','python','governed-dd-governance:0.1.0','-c',"import yaml;from pathlib import Path;p=Path('/workspace/local/tenants/$Tenant/compose.yaml');c=yaml.safe_load(p.read_text());s=c['services']['paperclip'];s['environment']['PAPERCLIP_AUTH_DISABLE_SIGN_UP']='false';s['networks']={k:v for k,v in s['networks'].items() if k!='ingress'};p.with_name('bootstrap.compose.yaml').write_text(yaml.safe_dump(c))")
try{
 D @('compose','-f',"$taskFolder/bootstrap.compose.yaml",'config','--quiet')
 D @('compose','-f',"$taskFolder/bootstrap.compose.yaml",'up','-d','paperclip')
 D @('cp',"$taskAppRoot/scripts/paperclip-bootstrap.cjs","${taskContainer}:/tmp/native-bootstrap.cjs")
 D @('cp',"$taskAppRoot/scripts/native-ready.cjs","${taskContainer}:/tmp/native-ready.cjs")
 D @('exec',$taskContainer,'node','/tmp/native-ready.cjs')
 if($Name){
  D @('cp',"$taskAppRoot/scripts/native-user.cjs","${taskContainer}:/tmp/native-user.cjs")
  D @('exec',$taskContainer,'node','/tmp/native-user.cjs',$Name,$Role)
 }else{D @('exec',$taskContainer,'node','/tmp/native-bootstrap.cjs')}
}finally{D @('compose','-f',"$taskFolder/compose.yaml",'up','-d','paperclip')}
Write-Host 'Native provisioning complete; sign-up disabled and protected ingress restored.'
