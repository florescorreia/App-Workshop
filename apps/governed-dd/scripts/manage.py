"""Container-only portable administrator; the engine socket is transient."""
import argparse,fcntl,json,os,re,subprocess,uuid,datetime
from pathlib import Path
import yaml
p=argparse.ArgumentParser();p.add_argument('action');p.add_argument('--tenant');p.add_argument('--name');p.add_argument('--subject');p.add_argument('--task');p.add_argument('--attachment');p.add_argument('--role',default='viewer',choices=['owner','analyst','reviewer','viewer']);p.add_argument('--backup');p.add_argument('--prefix');p.add_argument('--subnet-prefix',default='10.252');a=p.parse_args()
root=Path('/workspace');os.chdir(root);host=os.environ['HOST_APP_ROOT']
def d(*args,capture=False):
 r=subprocess.run(['docker',*map(str,args)],check=True,text=True,stdout=subprocess.PIPE if capture else None);return r.stdout.strip() if capture else None
info=json.loads(d('info','--format','{{json .}}',capture=True))
if info['ID']!=os.environ['DD_ENGINE_ID'] or 'Rancher Desktop' not in info['OperatingSystem']:raise ValueError('Socket must match explicitly discovered Rancher Moby engine')
def hp(path):return str(path).replace(str(root),host,1)
def t():
 if not a.tenant or not re.fullmatch('[a-f0-9]{24}',a.tenant):raise ValueError('Opaque tenant required')
 return a.tenant
def c(*args,tenant=None,path=None,capture=False):
 path=path or (root/'local/tenants'/tenant/'compose.yaml' if tenant else root/'local/control.compose.yaml');doc=yaml.safe_load(path.read_text())
 for s in doc['services'].values():
  s['volumes']=[hp((path.parent/v.split(':')[0]).resolve())+':'+':'.join(v.split(':')[1:]) if v.split(':')[0] not in doc.get('volumes',{}) else v for v in s.get('volumes',[])]
  if 'env_file' in s:s['env_file']=[str((path.parent/f).resolve()) for f in s['env_file']]
 for secret in doc.get('secrets',{}).values():secret['file']=hp((path.parent/secret['file']).resolve())
 file=root/'local'/('portable-'+doc['name']+'.yaml');file.write_text(yaml.safe_dump(doc,sort_keys=False));file.chmod(0o600)
 return d('compose','-f',file,*args,capture=capture)
def admin(*args):c('exec','-T','portal','python','/app/admin.py',*args)
def capacity(tenant):
 plan=json.loads(c('config','--format','json',tenant=tenant,capture=True));ids=d('ps','-q',capture=True).split();used=0;existing=set()
 for item in json.loads(d('inspect',*ids,capture=True)) if ids else []:
  limit=item['HostConfig']['Memory']
  if not limit:raise ValueError('Existing unlimited container requires reviewed capacity')
  used+=limit;labels=item['Config']['Labels'];existing.add((labels.get('com.docker.compose.project'),labels.get('com.docker.compose.service')))
 for name,s in plan['services'].items():
  if not s.get('profiles') and (plan['name'],name) not in existing:used+=int(s['mem_limit'])
 if used+2*1024**3>info['MemTotal']:raise ValueError(f'Unsafe start: {used/1024**3:.2f} GiB plus 2 GiB headroom exceeds {info["MemTotal"]/1024**3:.2f} GiB engine')
def node(name,tenant,*args):
 container=f'governed-dd-{tenant}-paperclip-1';d('cp',root/'scripts'/name,container+':/tmp/'+name);d('exec',container,'node','/tmp/'+name,*args)
if a.action in ['setup','up','tenant-start','tenant-create','runtime-enable','backup','restore-test','native-bootstrap','native-user']:
 (root/'local').mkdir(exist_ok=True);lock=open(root/'local/administration.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
if a.action=='import-attachment':
 tenant=t()
 if not all(x and re.fullmatch('[a-f0-9-]{36}',x) for x in [a.task,a.attachment]):raise ValueError('Exact task/attachment UUIDs required')
 directory='/tmp/dd-import-'+uuid.uuid4().hex;native=f'governed-dd-{tenant}-paperclip-1';gov=f'governed-dd-{tenant}-governance-1'
 import tempfile,shutil
 temp=Path(tempfile.mkdtemp(prefix='dd-import-'))
 try:
  node('native-attachment.cjs',tenant,a.task,a.attachment,directory)
  d('cp',native+':'+directory+'/.',temp)
  d('cp',str(temp),gov+':'+directory)
  d('exec','--user','root',gov,'chown','-R','1101:1101',directory)
  d('cp',root/'scripts/import-attachment.py',gov+':/tmp/import-attachment.py')
  d('exec','-e','PYTHONPATH=/app',gov,'python','/tmp/import-attachment.py',directory)
 finally:
  for container in [native,gov]:d('exec','--user','root',container,'rm','-rf','--',directory)
  shutil.rmtree(temp)
elif a.action=='doctor':print('Verified Rancher Moby engine:',info['NCPU'],'CPUs',info['MemTotal'],'bytes');d('compose','version')
elif a.action in ['setup','tenant-create']:
 subprocess.run(['python','scripts/render.py','setup'] if a.action=='setup' else ['python','scripts/render.py','tenant','--id',t(),'--name',a.name or ''],check=True)
 c('config','--quiet',tenant=a.tenant if a.action=='tenant-create' else None)
 if a.action=='tenant-create':admin('tenant','--tenant',a.tenant,'--name',a.name)
elif a.action in ['up','tenant-start']:
 tenant=t() if a.action=='tenant-start' else None;capacity(tenant);c('config','--quiet',tenant=tenant);c('up','-d',tenant=tenant)
 if not tenant:d('run','--rm','--user','root','-v','governed-dd-frontend:/target','--entrypoint','sh','governed-dd-explorer:0.1.0','-c','cp -r /usr/share/nginx/html/. /target/')
 portal='governed-dd-control-portal-1';attached=json.loads(d('inspect',portal,'--format','{{json .NetworkSettings.Networks}}',capture=True))
 nets=[f'governed-dd-{tenant}-ingress'] if tenant else [n for n in d('network','ls','--format','{{.Name}}',capture=True).splitlines() if re.fullmatch('governed-dd-[a-f0-9]{24}-ingress',n)]
 for n in nets:
  if n not in attached:d('network','connect',n,portal)
 if tenant:admin('active','--tenant',tenant,'--value','true')
elif a.action in ['down','status','tenant-stop']:
 tenant=t() if a.action=='tenant-stop' else None
 if tenant:admin('active','--tenant',tenant,'--value','false')
 if tenant:c('--profile','*','stop',tenant=tenant)
 else:c('ps' if a.action=='status' else 'stop',tenant=tenant)
elif a.action in ['member-add','member-remove']:
 args=[a.action,'--tenant',t(),'--subject',a.subject]
 if a.action=='member-add':args+=['--role',a.role]
 admin(*args)
elif a.action=='user-create':d('run','--rm','--user','root','--network','governed-dd-control-v2','--mount','type=bind,source='+hp(root/'local/secrets/keycloak-admin')+',target=/run/secrets/keycloak-admin,readonly','-v','governed-dd-identity-private:/private','--entrypoint','python','governed-dd-governance:0.1.0','/app/identity.py','create',a.name)
elif a.action in ['demo-seed','rebuild-graph','reindex']:
 code={'rebuild-graph':'from domain import Domain;print(Domain().project(rebuild=True))','reindex':'from domain import Domain;print(Domain().reindex())'}
 c('exec','-T','governance','python',*(['/app/fixtures.py'] if a.action=='demo-seed' else ['-c',code[a.action]]),tenant=t())
elif a.action in ['config-check','test']:subprocess.run(['python','scripts/config-check.py'] if a.action=='config-check' else ['python','-m','pytest','-q','-p','no:cacheprovider','/app/tests/test_security.py'],check=True)
elif a.action in ['runtime-enable','provider-configure']:subprocess.run(['python','scripts/'+('runtime-render.py' if a.action=='runtime-enable' else 'provider-render.py'),t()],check=True);c('config','--quiet',tenant=a.tenant)
elif a.action=='database-harden':
 tenant=t();d('run','--rm','--user','root','-e','TENANT_ID='+tenant,'--network','governed-dd-'+tenant+'-backend','--mount','type=bind,source='+hp(root/'local/secrets'/f'{tenant}-admin')+',target=/run/secrets/admin,readonly','--mount','type=bind,source='+hp(root/'scripts/database-security.py')+',target=/security.py,readonly','--entrypoint','python','governed-dd-governance:0.1.0','/security.py')
 path=root/'local/tenants'/tenant/'compose.yaml';doc=yaml.safe_load(path.read_text());doc['services']['governance']['environment']['SERVICE_SCHEMA_MANAGED']='true';path.write_text(yaml.safe_dump(doc,sort_keys=False));c('up','-d','--no-deps','governance',tenant=tenant)
elif a.action in ['native-bootstrap','native-user']:
 tenant=t();path=root/'local/tenants'/tenant/'compose.yaml';doc=yaml.safe_load(path.read_text());s=doc['services']['paperclip'];s['environment']['PAPERCLIP_AUTH_DISABLE_SIGN_UP']='false';s['networks'].pop('ingress',None);bootstrap=path.with_name('bootstrap.compose.yaml');bootstrap.write_text(yaml.safe_dump(doc))
 try:
  c('up','-d','--no-deps','paperclip',path=bootstrap);node('native-ready.cjs',tenant)
  node('native-user.cjs',tenant,a.name,a.role) if a.action=='native-user' else node('paperclip-bootstrap.cjs',tenant)
 finally:c('up','-d','--no-deps','paperclip',tenant=tenant)
elif a.action in ['agent-setup','agent-check']:
 tenant=t();container=f'governed-dd-{tenant}-paperclip-1';node('native-ready.cjs',tenant);d('cp',root/'local/secrets'/f'{tenant}-runtime-private',container+':/tmp/runtime-private')
 for name in ['runtime','runtime-reviewer']:
  known=d('exec',container,'ssh-keyscan','-p','2222',name,capture=True);file=root/'local/tenants'/tenant/(name+'-known-hosts');file.write_text(known+'\n');d('cp',file,container+('/tmp/runtime-known-hosts' if name=='runtime' else '/tmp/reviewer-known-hosts'))
 node('paperclip-runtime.cjs',tenant,'setup' if a.action=='agent-setup' else 'smoke')
elif a.action=='restore-stack':
 prefix=a.prefix
 if not prefix or not re.fullmatch('governed-dd-restore-[a-f0-9]{12}',prefix):raise ValueError('--prefix from authenticated restore required')
 if not re.fullmatch(r'10\.(?:[1-9][0-9]?|1[0-9]{2}|2[0-4][0-9]|25[0-5])',a.subnet_prefix):raise ValueError('Reviewed 10.x subnet prefix required')
 ids=d('network','ls','-q',capture=True).split()
 if ids and a.subnet_prefix+'.' in d('network','inspect',*ids,'--format','{{range .IPAM.Config}}{{.Subnet}} {{end}}',capture=True):raise ValueError('Restore subnet prefix already in use')
 volumes=[v for v in d('volume','ls','--format','{{.Name}}',capture=True).splitlines() if v.startswith(prefix+'-')]
 d('run','--rm','--user','root','-e','HOST_APP_ROOT='+host,'-e','RESTORED_VOLUMES='+json.dumps(volumes),'-e','RESTORE_SUBNET_PREFIX='+a.subnet_prefix,'--mount','type=bind,source='+host+',target=/workspace','-v',prefix+'-configuration:/configuration:ro','--entrypoint','python','governed-dd-governance:0.1.0','/workspace/scripts/restore-stack.py',prefix)
 path=root/'local/restores'/prefix/'restore.compose.yaml';d('compose','-f',path,'config','--quiet');d('volume','create',prefix+'-frontend');d('run','--rm','--user','root','-v',prefix+'-frontend:/target','--entrypoint','sh','governed-dd-explorer:0.1.0','-c','cp -r /usr/share/nginx/html/. /target/');d('compose','-f',path,'up','-d')
 print('Isolated complete restore started with no published ports or external egress:',prefix)
elif a.action in ['backup','restore-test']:
 volumes=[v for v in d('volume','ls','--format','{{.Name}}',capture=True).splitlines() if re.fullmatch(r'governed-dd-(control-db|identity-private|[a-f0-9]{24}-(postgres|artifacts|graph|paperclip|git|agent-home|reviewer-git|reviewer-home|run-gate|ontology|lab))',v)]
 destination=Path(a.backup) if a.backup else root/'backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S');prefix='governed-dd-restore-'+uuid.uuid4().hex[:12]
 base=['run','--rm','--user','root','--mount','type=bind,source='+hp(destination)+',target=/backup','--mount','type=bind,source='+hp(root/'local/secrets/backup-key')+',target=/key,readonly','--mount','type=bind,source='+hp(root/'scripts/backup.py')+',target=/tool.py,readonly']
 if a.action=='backup':
  destination.mkdir(parents=True,exist_ok=False);running=[n for n in d('ps','--format','{{.Names}}',capture=True).splitlines() if re.fullmatch(r'governed-dd-(control|[a-f0-9]{24})-.*',n)]
  try:
   if running:d('stop','--time','60',*running)
   args=base+['--mount','type=bind,source='+host+',target=/configuration,readonly']
   for v in volumes:args+=['-v',f'{v}:/volumes/{v}:ro']
   d(*args,'--entrypoint','python','governed-dd-governance:0.1.0','/tool.py','pack')
  finally:
   if running:d('start',*running)
  print('Encrypted backup:',destination)
 else:
  if not a.backup:raise ValueError('--backup required')
  names=json.loads(d(*base,'--entrypoint','python','governed-dd-governance:0.1.0','/tool.py','list',capture=True));args=base[:]
  for v in names:
   if v!='configuration' and v not in volumes:raise ValueError('Unexpected restore volume')
   fresh=prefix+'-'+v;d('volume','create',fresh);args+=['-v',fresh+':/volumes/'+v]
  d(*args,'--entrypoint','python','governed-dd-governance:0.1.0','/tool.py','restore');print('Isolated volumes restored:',prefix)
else:raise ValueError('Unsupported action: '+a.action)
