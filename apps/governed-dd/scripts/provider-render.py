"""Explicitly inject named search/embedding environment keys as scoped private files."""
import os,sys,json
from pathlib import Path
import yaml
root=Path('/workspace');tenant=sys.argv[1]
if len(tenant)!=24 or any(c not in '0123456789abcdef' for c in tenant):raise ValueError('Opaque tenant required')
settings={}
for line in (root/'.env').read_text().splitlines():
 if line and not line.startswith('#') and '=' in line:
  k,v=line.split('=',1);settings[k]=v
path=root/'local/tenants'/tenant/'compose.yaml';c=yaml.safe_load(path.read_text());injected={}
for prefix in ('WEB_SEARCH','EMBEDDING'):
 name=settings.get(prefix+'_API_KEY_ENV')
 configured=settings.get('WEB_SEARCH_PROVIDER' if prefix=='WEB_SEARCH' else 'EMBEDDING_MODEL')
 if prefix=='WEB_SEARCH' and configured=='bing_rss':continue
 if not configured:continue
 if not name or not os.environ.get(name):raise ValueError('Configured provider needs named environment variable '+str(name))
 injected[name]=os.environ[name]
secret=root/'local/secrets'/(tenant+'-providers')
if secret.exists():secret.chmod(0o600)
secret.write_text(json.dumps(injected));os.chown(secret,1101,1101);secret.chmod(0o400)
c['secrets']['providers']={'file':'../../secrets/'+tenant+'-providers'}
if 'providers' not in c['services']['governance']['secrets']:c['services']['governance']['secrets'].append('providers')
c['services']['governance']['environment']['PROVIDER_KEYS_FILE']='/run/secrets/providers'
for field in ('WEB_SEARCH_PROVIDER','WEB_SEARCH_API_KEY_ENV','EMBEDDING_PROVIDER','EMBEDDING_BASE_URL','EMBEDDING_MODEL','EMBEDDING_DIMENSIONS','EMBEDDING_API_KEY_ENV'):
 if field in settings:c['services']['governance']['environment'][field]=settings[field]
path.write_text(yaml.safe_dump(c,sort_keys=False));print('Named provider keys injected privately into tenant governance; '+str(len(injected))+' configured keys.')
