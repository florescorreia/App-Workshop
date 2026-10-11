"""Explicit isolated runtime enablement. Requires named model key; never prints it."""
import os,sys,subprocess
from pathlib import Path
import yaml
root=Path('/workspace');tenant=sys.argv[1]
if len(tenant)!=24 or any(c not in '0123456789abcdef' for c in tenant):raise ValueError('Invalid tenant')
key=os.environ.get('LITELLM_API_KEY')
if not key:raise ValueError('LITELLM_API_KEY must be explicitly injected')
secrets=root/'local/secrets';private=secrets/(tenant+'-runtime-private')
if not private.exists():
 from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
 from cryptography.hazmat.primitives import serialization
 generated=Ed25519PrivateKey.generate()
 private.write_bytes(generated.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.OpenSSH,serialization.NoEncryption()))
 private.chmod(0o600)
 Path(str(private)+'.pub').write_bytes(generated.public_key().public_bytes(serialization.Encoding.OpenSSH,serialization.PublicFormat.OpenSSH)+b'\n')
model=secrets/(tenant+'-model')
if model.exists():model.chmod(0o600)
model.write_text(key);model.chmod(0o400);os.chown(model,1000,1000)
agent=secrets/(tenant+'-agent');runtimeAgent=secrets/(tenant+'-runtime-agent')
if runtimeAgent.exists():runtimeAgent.chmod(0o600)
runtimeAgent.write_bytes(agent.read_bytes());runtimeAgent.chmod(0o400);os.chown(runtimeAgent,1000,1000)
reviewer=secrets/(tenant+'-reviewer')
if not reviewer.exists():
 import secrets as random
 reviewer.write_text(random.token_urlsafe(40));reviewer.chmod(0o400);os.chown(reviewer,1101,1101)
reviewRuntime=secrets/(tenant+'-runtime-reviewer')
if not reviewRuntime.exists():reviewRuntime.write_bytes(reviewer.read_bytes());reviewRuntime.chmod(0o400);os.chown(reviewRuntime,1000,1000)
folder=root/'local/tenants'/tenant;path=folder/'compose.yaml';c=yaml.safe_load(path.read_text())
for service in c['services'].values():
 if isinstance(service.get('networks'),list):service['networks']={n:{} for n in service['networks']}
c['services']['paperclip']['networks']['ingress']={'aliases':['paperclip-'+tenant]}
c['services']['paperclip']['environment']['PAPERCLIP_AUTH_PUBLIC_BASE_URL']=f'http://paperclip-{tenant}.localhost:8081'
c['services']['paperclip']['environment']['PAPERCLIP_ALLOWED_HOSTNAMES']=f'paperclip-{tenant}.localhost'
c['services']['paperclip']['environment']['PAPERCLIP_AUTH_DISABLE_SIGN_UP']='true'
runtimeNetwork='governed-dd-'+tenant+'-runtime';edgeNetwork='governed-dd-'+tenant+'-provider-edge'
if 'runtime' not in c['networks'] or 'provider-edge' not in c['networks']:
 # Explicit administrator-reviewed allocation; avoid automatic pools overlapping provider routes.
 allocation=os.getenv('DD_RUNTIME_SUBNET')
 edgeAllocation=os.getenv('DD_PROVIDER_EDGE_SUBNET')
 if not allocation or not edgeAllocation:raise ValueError('New execution networks require DD_RUNTIME_SUBNET and DD_PROVIDER_EDGE_SUBNET checked against host/provider routes')
 import ipaddress
 ipaddress.ip_network(allocation);ipaddress.ip_network(edgeAllocation)
 if 'runtime' not in c['networks']:c['networks']['runtime']={'name':runtimeNetwork,'internal':True,'ipam':{'config':[{'subnet':allocation}]}}
 if 'provider-edge' not in c['networks']:c['networks']['provider-edge']={'name':edgeNetwork,'ipam':{'config':[{'subnet':edgeAllocation}]}}
c['services']['paperclip']['image']='governed-dd-paperclip:2026.1005.0'
c['services']['paperclip']['networks']['runtime']={}
c['services']['paperclip']['environment']['PAPERCLIP_PUBLIC_URL']=f'http://paperclip-{tenant}.localhost:8081'
c['services']['governance']['networks']['runtime']={}
c['services']['governance']['networks']['provider-edge']={}
c['services']['governance']['environment']['REVIEWER_KEY_FILE']='/run/secrets/reviewer'
c['services']['governance']['volumes']=[v for v in c['services']['governance']['volumes'] if not v.endswith(':/ontology')]+['ontology:/ontology']
c['volumes']['ontology']={'name':'governed-dd-'+tenant+'-ontology'}
if 'reviewer' not in c['services']['governance']['secrets']:c['services']['governance']['secrets'].append('reviewer')
if (root/'local/workstation-public-ca.pem').exists():
 c['services']['governance']['volumes']=[v for v in c['services']['governance']['volumes'] if '/run/public-fetch-ca.pem' not in v]+['../../workstation-public-ca.pem:/run/public-fetch-ca.pem:ro']
 c['services']['governance']['environment']['PUBLIC_FETCH_CA_FILE']='/run/public-fetch-ca.pem'
c['services']['runtime']={'image':'governed-dd-runtime:2026.1005.0','mem_limit':'2g','cpus':2,'pids_limit':256,'restart':'unless-stopped','security_opt':['no-new-privileges:true'],'networks':['runtime'],'volumes':['git:/engagement','agent-home:/agent-home'],'secrets':['runtime-public','model-key','runtime-agent'],'environment':{'TENANT_ID':tenant}}
c['services']['runtime']['logging']={'driver':'json-file','options':{'max-size':'10m','max-file':'3'}}
# Root SSH listener is infrastructure only; all generated analysis runs as UID 1000.
c['services']['runtime']['secrets']=[{'source':'runtime-public','target':'runtime-public'},{'source':'model-key','target':'model-key'},{'source':'runtime-agent','target':'agent'}]
c['services']['runtime']['volumes'].append('run-gate:/run-gate')
c['services']['runtime-reviewer']={**c['services']['runtime'],'volumes':['reviewer-git:/engagement','reviewer-home:/agent-home','run-gate:/run-gate'],'secrets':[{'source':'runtime-public','target':'runtime-public'},{'source':'model-key','target':'model-key'},{'source':'runtime-reviewer','target':'agent'}]}
c['volumes']['run-gate']={'name':'governed-dd-'+tenant+'-run-gate'}
c['volumes']['reviewer-git']={'name':'governed-dd-'+tenant+'-reviewer-git'}
c['volumes']['reviewer-home']={'name':'governed-dd-'+tenant+'-reviewer-home'}
c['services']['egress']={'image':'governed-dd-governance:0.1.0','command':['python','/app/egress.py'],'environment':{'PROVIDER_HOSTS':'litellm-app.ambitiousground-51296563.westeurope.azurecontainerapps.io'},'mem_limit':'128m','cpus':.25,'pids_limit':64,'restart':'unless-stopped','security_opt':['no-new-privileges:true'],'cap_drop':['ALL'],'networks':{'runtime':{'aliases':['egress-runtime']},'provider-edge':{}}}
c['secrets']['runtime-public']={'file':'../../secrets/'+tenant+'-runtime-private.pub'}
c['secrets']['model-key']={'file':'../../secrets/'+tenant+'-model'}
c['secrets']['runtime-agent']={'file':'../../secrets/'+tenant+'-runtime-agent'}
c['secrets']['reviewer']={'file':'../../secrets/'+tenant+'-reviewer'}
c['secrets']['runtime-reviewer']={'file':'../../secrets/'+tenant+'-runtime-reviewer'}
c['services']['lab']['networks']={'backend':{},'ingress':{'aliases':['lab-'+tenant]}}
path.write_text(yaml.safe_dump(c,sort_keys=False));print('Isolated runtime manifest prepared. Model key stored privately; not emitted.')
