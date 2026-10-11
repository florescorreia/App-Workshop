"""Prepare an isolated complete application from authenticated restored volumes."""
import os,re,sys,shutil,json
from pathlib import Path
import yaml
prefix=sys.argv[1]
if not re.fullmatch(r'governed-dd-restore-[a-f0-9]{12}',prefix):raise ValueError('Invalid restore prefix')
root=Path('/workspace');target=root/'local/restores'/prefix
hostroot=os.environ['HOST_APP_ROOT'].replace('\\','/')
available=set(json.loads(os.environ['RESTORED_VOLUMES']))
def hostpath(p):return str(p).replace(str(root),hostroot,1)
if target.exists():raise ValueError('Fresh restore preparation directory required')
shutil.copytree('/configuration',target)
for secret in (target/'local/secrets').iterdir():
 if not secret.is_file():continue
 secret.chmod(0o600)
 if secret.name in ('gateway-signing','oidc-client') or secret.name.endswith(('-agent','-reviewer','-providers')):
  os.chown(secret,1101,1101);secret.chmod(0o400)
 if secret.name.endswith(('-model','-runtime-agent','-runtime-reviewer')):
  os.chown(secret,1000,1000);secret.chmod(0o400)
config={'name':prefix+'-app','services':{},'networks':{},'volumes':{},'secrets':{}}
files=[('control',target/'local/control.compose.yaml')]+[(p.parent.name,p) for p in sorted((target/'local/tenants').glob('*/compose.yaml'))]
subnet=0
subnet_prefix=os.getenv('RESTORE_SUBNET_PREFIX','10.252')
if not re.fullmatch(r'10\.(?:[1-9][0-9]?|1[0-9]{2}|2[0-4][0-9]|25[0-5])',subnet_prefix):raise ValueError('Reviewed private 10.x prefix required')
for label,path in files:
 c=yaml.safe_load(path.read_text());service_names={name:label+'-'+name for name in c['services']}
 for name,n in c['networks'].items():
  key=label+'-'+name;subnet+=1
  config['networks'][key]={'name':prefix+'-'+key,'internal':True,'ipam':{'config':[{'subnet':f'{subnet_prefix}.{subnet}.0/24'}]}}
 for name,v in c['volumes'].items():
  original=v['name'];restored=prefix+'-'+original
  if restored in available:config['volumes'][label+'-'+name]={'name':restored,'external':True}
 for name,s in c.get('secrets',{}).items():config['secrets'][label+'-'+name]={'file':hostpath((path.parent/s['file']).resolve())}
 for name,s in c['services'].items():
  if any(v.split(':')[0] in c['volumes'] and v.split(':')[0]!='frontend' and prefix+'-'+c['volumes'][v.split(':')[0]]['name'] not in available for v in s.get('volumes',[])):continue
  s.pop('ports',None);s.pop('profiles',None);s.pop('container_name',None)
  # Test containers never initiate model work; all scheduled work already disabled.
  s['restart']='no'
  nets=s.get('networks',[]);nets={n:{} for n in nets} if isinstance(nets,list) else nets
  s['networks']={label+'-'+n:{'aliases':list(set([name]+(options or {}).get('aliases',[])))} for n,options in nets.items()}
  if name=='egress':
   s['networks'][label+'-runtime']['aliases'].append('egress-runtime')
  if 'depends_on' in s:
   deps=s['depends_on'];s['depends_on']={service_names[n]:v for n,v in deps.items()} if isinstance(deps,dict) else [service_names[n] for n in deps]
  s['secrets']=[label+'-'+v if isinstance(v,str) else {**v,'source':label+'-'+v['source']} for v in s.get('secrets',[])]
  # Preserve original secret target filenames after renaming their Compose identifiers.
  s['secrets']=[{'source':v,'target':v.removeprefix(label+'-')} if isinstance(v,str) else v for v in s['secrets']]
  mounts=[]
  for v in s.get('volumes',[]):
   src,dest,*opts=v.split(':')
   if src in c['volumes']:src=label+'-'+src
   else:src=hostpath((path.parent/src).resolve())
   mounts.append(':'.join([src,dest]+opts))
  s['volumes']=mounts
  if 'env_file' in s:s['env_file']=[hostpath((path.parent/p).resolve()) for p in s['env_file']]
  config['services'][service_names[name]]=s
# The immutable frontend and gateway configuration are release assets, not client data.
config['volumes']['control-frontend']={'name':prefix+'-frontend'}
gateway=root/'infra/compose/gateway.conf'
config['services']['control-gateway']['volumes']=[hostpath(gateway)+':/etc/nginx/conf.d/default.conf:ro']
for label,path in files:
 if label!='control':
  ingress=label+'-ingress';config['services']['control-portal']['networks'][ingress]={'aliases':['portal']}
# Fully isolated restore must fit beside the live stack; analytical runtimes remain stopped.
for name in list(config['services']):
 if name.endswith(('-runtime','-runtime-reviewer','-egress','-lab')):config['services'][name]['profiles']=['optional-check']
(target/'restore.compose.yaml').write_text(yaml.safe_dump(config,sort_keys=False))
print('Full isolated restore Compose prepared; no host ports or external egress.')
