param([string]$Context='default')
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
$taskEnv=Join-Path $taskRoot '.env'
$taskValues=@{}
$taskMissing=@()
$taskAdmin=Join-Path $taskRoot 'local/secrets/keycloak-admin'
if(Test-Path -LiteralPath $taskAdmin){
 $taskValues['DD_KEYCLOAK_ADMIN_USERNAME']='governed-dd-admin'
 $taskValues['DD_KEYCLOAK_ADMIN_PASSWORD']=[IO.File]::ReadAllText($taskAdmin).Trim()
}
# Previously verified Alice credentials cached by native browser checks.
$taskAlice=Join-Path $taskRoot 'local/secrets/native-alice-test.json'
if(Test-Path -LiteralPath $taskAlice){
 $taskCached=Get-Content -LiteralPath $taskAlice -Raw | ConvertFrom-Json
 if($taskCached.name -eq 'alice' -and $taskCached.email -and $taskCached.password){
  $taskPrefix='DD_PAPERCLIP_A4E176281F3C47D081B3B623_ALICE'
  $taskValues[$taskPrefix+'_EMAIL']=$taskCached.email
  $taskValues[$taskPrefix+'_PASSWORD']=$taskCached.password
 }
}
$taskSavedPreference=$ErrorActionPreference
$ErrorActionPreference='Continue'
$taskOS=& docker --context $Context info --format '{{.OperatingSystem}}' 2>$null
$taskHostReady=$LASTEXITCODE -eq 0 -and $taskOS -match 'Rancher Desktop'
$taskVMReady=$false
if(-not $taskHostReady){
 $taskEngineSettings=(& rdctl list-settings 2>$null)|ConvertFrom-Json
 $taskVMOS=& rdctl shell docker info --format '{{.OperatingSystem}}' 2>$null
 $taskVMReady=$LASTEXITCODE -eq 0 -and $taskVMOS -match 'Rancher Desktop' -and $taskEngineSettings.containerEngine.name -eq 'moby'
}
$ErrorActionPreference=$taskSavedPreference
if($taskHostReady -or $taskVMReady){
 $taskTenants=@(Get-ChildItem (Join-Path $taskRoot 'local/tenants') -Directory | Where-Object {$_.Name -match '^[a-f0-9]{24}$'})
 # Verify volumes first; never create an empty substitute when a volume is absent.
 $taskVolumes=@('governed-dd-identity-private')+@($taskTenants|ForEach-Object {"governed-dd-$($_.Name)-paperclip"})
 if($taskHostReady){$null=& docker --context $Context volume inspect @taskVolumes 2>$null}else{$null=& rdctl shell docker volume inspect @taskVolumes 2>$null}
 if($LASTEXITCODE -ne 0){throw 'Existing credential volumes unavailable; file unchanged'}
 $taskArguments=@('run','--rm','--user','root','--network','none','-v','governed-dd-identity-private:/identity:ro')
 foreach($taskTenant in $taskTenants){$taskArguments+=@('-v',"governed-dd-$($taskTenant.Name)-paperclip:/native/$($taskTenant.Name):ro")}
 $taskScript=[Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $PSScriptRoot 'read-login-credentials.py')))
 $taskPython="import base64;exec(base64.b64decode('$taskScript'))"
 if($taskHostReady){$taskOutput=& docker --context $Context @taskArguments --entrypoint python governed-dd-governance:0.1.0 -c $taskPython 2>$null}else{$taskOutput=& rdctl shell docker @taskArguments --entrypoint python governed-dd-governance:0.1.0 -c $taskPython 2>$null}
 if($LASTEXITCODE -ne 0){throw 'Private credential-volume export failed; values were not displayed'}
 $taskExport=$taskOutput|ConvertFrom-Json
 foreach($taskProperty in $taskExport.PSObject.Properties){$taskValues[$taskProperty.Name]=[string]$taskProperty.Value}
 if($taskVMReady){Write-Output 'Credential volumes accessed through verified Rancher Moby VM; Windows Docker transport is unavailable.'}
}else{
 $taskMissing+= 'Rancher backend unavailable: portal passwords and remaining native logins still require volume export. Rerun scripts/export-login-env.ps1 when Rancher is ready.'
}
$taskLines=if(Test-Path -LiteralPath $taskEnv){@([IO.File]::ReadAllLines($taskEnv))}else{@()}
# Remove only the previous bounded export block; retain every existing app setting.
$taskStart='# BEGIN GOVERNED DD LOCAL LOGIN CREDENTIALS'
$taskEnd='# END GOVERNED DD LOCAL LOGIN CREDENTIALS'
$taskExisting=@{};$taskKept=[Collections.Generic.List[string]]::new();$taskInside=$false
foreach($taskLine in $taskLines){
 if($taskLine -eq $taskStart){$taskInside=$true;continue}
 if($taskLine -eq $taskEnd){$taskInside=$false;continue}
 if($taskInside){if($taskLine -match '^(DD_[A-Z0-9_]+)=(.*)$'){$taskExisting[$matches[1]]=$matches[2]};continue}
 $taskKept.Add($taskLine)
}
if($taskInside){throw 'Unclosed credential export block; file unchanged'}
$taskKept.Add('');$taskKept.Add($taskStart)
$taskKept.Add('# Private local UI logins. Do not commit or paste into Paperclip tasks.')
$taskKept.Add('# Portal identities are independent of current engagement memberships. Native logins are tenant-specific.')
foreach($taskKey in @($taskExisting.Keys|Sort-Object)){if(-not $taskValues.ContainsKey($taskKey)){$taskKept.Add("$taskKey=$($taskExisting[$taskKey])")}}
foreach($taskKey in @($taskValues.Keys|Sort-Object)){
 $taskValue=[string]$taskValues[$taskKey]
 if($taskValue -match '[\r\n''"\\]'){throw 'Unsupported credential encoding; file unchanged'}
 $taskKept.Add("$taskKey='$taskValue'")
}
foreach($taskNote in $taskMissing){$taskKept.Add('# INCOMPLETE: '+$taskNote)}
$taskKept.Add($taskEnd)
[IO.File]::WriteAllLines($taskEnv,$taskKept,[Text.UTF8Encoding]::new($false))
Write-Output "Private .env updated with $($taskValues.Count) login fields. No credential values displayed."
if($taskMissing){Write-Output 'Export is partial until Rancher is ready.'}
