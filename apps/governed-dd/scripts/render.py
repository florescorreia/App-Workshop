"""Container-only setup/render tool. No engine socket is required."""
import argparse
import json
import os
import re
import secrets
from pathlib import Path
import yaml

ROOT=Path('/workspace')
LOCAL=ROOT/'local'
LOCK={
 'postgres':'postgres:17.6-bookworm@sha256:f3bd19c606e442c3d7bdfa8002e03fe260a1023351e0ea4598032022b68dd6e3',
 'paradedb':'paradedb/paradedb:0.26.1-pg17@sha256:c1c147499c6649739d7977f1e47db149578c894f35249953acdd7680ccbae75b',
 'keycloak':'quay.io/keycloak/keycloak:26.4.7@sha256:9409c59bdfb65dbffa20b11e6f18b8abb9281d480c7ca402f51ed3d5977e6007',
 'memgraph':'memgraph/memgraph:3.6.0@sha256:fa51fa1f64bce77fc20fc351632f684fd22afc7916febaba30fc2af24815f5a4',
 'lab':'memgraph/lab:3.6.0@sha256:9b3e22df64ef91e7883737e3be1663bf2b59c8a1c1e19acecded7d2c5ed9e3db',
 'paperclip':'ghcr.io/paperclipai/paperclip:2026.1005.0@sha256:de762433b50d56ed9180fef96a13fa236b37856c5c7a7718e8f19afe3d1e8670',
 'codex':'0.160.1',
}


def secret(name):
 path=LOCAL/'secrets'/name
 if not path.exists():
  path.parent.mkdir(parents=True,exist_ok=True);path.write_text(secrets.token_urlsafe(40));path.chmod(0o600)
 if name in ('gateway-signing','oidc-client') or name.endswith('-agent'):
  os.chown(path,1101,1101);path.chmod(0o400)
 return path.read_text().strip()


def bounded(service,memory='512m',cpu=1):
 return {**service,'mem_limit':memory,'cpus':cpu,'pids_limit':256,'restart':'unless-stopped',
         'security_opt':['no-new-privileges:true'],'logging':{'driver':'json-file','options':{'max-size':'10m','max-file':'3'}}}


def setup():
 LOCAL.mkdir(exist_ok=True)
 for name in ['db-admin','portal-db','keycloak-db','oidc-client','gateway-signing','keycloak-admin','backup-key']:
  secret(name)
 env=ROOT/'.env'
 if not env.exists(): env.write_text((ROOT/'.env.example').read_text())
 control_init=LOCAL/'control-init.sql'
 control_init.write_text(f"CREATE ROLE portal LOGIN PASSWORD '{secret('portal-db')}';\nCREATE DATABASE portal OWNER portal;\nCREATE ROLE keycloak LOGIN PASSWORD '{secret('keycloak-db')}';\nCREATE DATABASE keycloak OWNER keycloak;\nREVOKE ALL ON DATABASE portal FROM PUBLIC;\nREVOKE ALL ON DATABASE keycloak FROM PUBLIC;\n")
 realm={'realm':'governed-dd','enabled':True,'registrationAllowed':False,'resetPasswordAllowed':False,
  'clients':[{'clientId':'dd-portal','enabled':True,'publicClient':False,'secret':secret('oidc-client'),'standardFlowEnabled':True,'directAccessGrantsEnabled':False,'redirectUris':['http://localhost:8081/auth/callback'],'webOrigins':['http://localhost:8081'],'attributes':{'post.logout.redirect.uris':'http://localhost:8081/','pkce.code.challenge.method':'S256'}}]}
 (LOCAL/'realm.json').write_text(json.dumps(realm))
 services={
 'control-postgres':bounded({'image':LOCK['postgres'],'environment':{'POSTGRES_PASSWORD_FILE':'/run/secrets/db-admin'},'secrets':['db-admin'],'volumes':['control-db:/var/lib/postgresql/data','./control-init.sql:/docker-entrypoint-initdb.d/01-control.sql:ro'],'networks':['control'],'healthcheck':{'test':['CMD-SHELL','pg_isready -U postgres'],'interval':'5s','retries':30}}),
 'keycloak':bounded({'image':LOCK['keycloak'],'command':['start-dev','--import-realm'],'environment':{'KC_DB':'postgres','KC_DB_URL':'jdbc:postgresql://control-postgres:5432/keycloak','KC_DB_USERNAME':'keycloak','KC_DB_PASSWORD':secret('keycloak-db'),'KC_BOOTSTRAP_ADMIN_USERNAME':'governed-dd-admin','KC_BOOTSTRAP_ADMIN_PASSWORD':secret('keycloak-admin'),'KC_HOSTNAME':'http://localhost:8081/identity','KC_HTTP_RELATIVE_PATH':'/identity','KC_PROXY_HEADERS':'xforwarded','KC_HEALTH_ENABLED':'true'},'volumes':['./realm.json:/opt/keycloak/data/import/realm.json:ro'],'networks':['control'],'depends_on':{'control-postgres':{'condition':'service_healthy'}}},'1g'),
 'portal':bounded({'image':'governed-dd-governance:0.1.0','environment':{'SERVICE_MODE':'control','DATABASE_URL':f"postgresql://portal:{secret('portal-db')}@control-postgres/portal",'APP_BASE_URL':'http://localhost:8081','OIDC_INTERNAL_URL':'http://keycloak:8080/identity/realms/governed-dd','OIDC_ISSUER_URL':'http://localhost:8081/identity/realms/governed-dd','OIDC_CLIENT_SECRET_FILE':'/run/secrets/oidc-client','GATEWAY_KEY_FILE':'/run/secrets/gateway-signing'},'secrets':['oidc-client','gateway-signing'],'volumes':['frontend:/frontend:ro'],'networks':['control'],'depends_on':{'control-postgres':{'condition':'service_healthy'}}}),
 'gateway':bounded({'image':'nginx:1.28.0-alpine@sha256:30f1c0d78e0ad60901648be663a710bdadf19e4c10ac6782c235200619158284','ports':['127.0.0.1:8081:8080'],'volumes':['../infra/compose/gateway.conf:/etc/nginx/conf.d/default.conf:ro'],'networks':['control','edge'],'depends_on':['portal','keycloak']},'128m',.5),
 }
 config={'name':'governed-dd-control','services':services,'networks':{'control':{'name':'governed-dd-control-v2','internal':True,'ipam':{'config':[{'subnet':'10.253.0.0/24'}]}},'edge':{'name':'governed-dd-edge-v2','ipam':{'config':[{'subnet':'10.253.1.0/24'}]}}},'volumes':{'control-db':{'name':'governed-dd-control-db'},'frontend':{'name':'governed-dd-frontend'},'identity-private':{'name':'governed-dd-identity-private'}},'secrets':{n:{'file':'./secrets/'+n} for n in ['db-admin','oidc-client','gateway-signing','keycloak-admin']}}
 (LOCAL/'control.compose.yaml').write_text(yaml.safe_dump(config,sort_keys=False))
 (LOCAL/'versions.json').write_text(json.dumps(LOCK,indent=2))
 print('Private configuration generated; existing values preserved. No tenants created.')


def tenant(ident,name):
 if not re.fullmatch('[a-f0-9]{24}',ident):raise ValueError('Tenant ID must be 24 opaque hexadecimal characters')
 folder=LOCAL/'tenants'/ident
 folder.mkdir(parents=True,exist_ok=True)
 info=folder/'tenant.json'
 if info.exists() and json.loads(info.read_text())['name']!=name:raise ValueError('Tenant exists with different name')
 if info.exists() and (folder/'compose.yaml').exists():
  print('Existing tenant configuration preserved; no credentials, runtime or storage changes.');return
 creds={n:secret(ident+'-'+n) for n in ['admin','dd','paperclip','agent']}
 (folder/'init.sql').write_text(f"CREATE ROLE dd LOGIN PASSWORD '{creds['dd']}';\nCREATE DATABASE dd OWNER dd;\nCREATE ROLE paperclip LOGIN PASSWORD '{creds['paperclip']}';\nCREATE DATABASE paperclip OWNER paperclip;\nREVOKE ALL ON DATABASE dd FROM PUBLIC;\nREVOKE ALL ON DATABASE paperclip FROM PUBLIC;\n\\connect dd\nCREATE EXTENSION IF NOT EXISTS vector;\nCREATE EXTENSION IF NOT EXISTS pg_search;\n")
 network='governed-dd-'+ident+'-backend'; ingress='governed-dd-'+ident+'-ingress'
 common={'TENANT_ID':ident,'DATABASE_URL':f"postgresql://dd:{creds['dd']}@postgres/dd",'GRAPH_URL':'bolt://graph:7687','GATEWAY_KEY_FILE':'/run/secrets/gateway-signing','AGENT_KEY_FILE':'/run/secrets/agent'}
 envfile='../../../.env'
 services={
 'postgres':bounded({'image':LOCK['paradedb'],'environment':{'POSTGRES_PASSWORD_FILE':'/run/secrets/admin'},'secrets':['admin'],'volumes':['postgres:/var/lib/postgresql/data','./init.sql:/docker-entrypoint-initdb.d/01-tenant.sql:ro'],'networks':['backend'],'healthcheck':{'test':['CMD-SHELL','pg_isready -U postgres'],'interval':'5s','retries':30}},'1g'),
 'graph':bounded({'image':LOCK['memgraph'],'command':['--storage-snapshot-interval-sec=300','--data-recovery-on-startup=true','--storage-wal-enabled=true','--memory-limit=768'],'volumes':['graph:/var/lib/memgraph'],'networks':['backend']},'1g'),
 'governance':bounded({'image':'governed-dd-governance:0.1.0','environment':common,'env_file':[envfile],'secrets':['agent','gateway-signing'],'volumes':['artifacts:/artifacts','ontology:/ontology'],'networks':{'backend':{},'ingress':{'aliases':['dd-'+ident]}},'depends_on':{'postgres':{'condition':'service_healthy'}}},'768m'),
 'explorer':bounded({'image':'governed-dd-explorer:0.1.0','tmpfs':['/var/cache/nginx','/var/run'],'networks':{'ingress':{'aliases':['explorer-'+ident]}}},'128m',.5),
 'paperclip':bounded({'image':LOCK['paperclip'],'environment':{'DATABASE_URL':f"postgresql://paperclip:{creds['paperclip']}@postgres/paperclip",'BETTER_AUTH_SECRET':secret(ident+'-paperclip-auth'),'PAPERCLIP_AGENT_JWT_SECRET':secret(ident+'-paperclip-agent-jwt'),'HEARTBEAT_SCHEDULER_ENABLED':'false','PAPERCLIP_INSTANCE_ID':'governed-dd-'+ident,'PAPERCLIP_DEPLOYMENT_MODE':'authenticated','PAPERCLIP_DEPLOYMENT_EXPOSURE':'private','PAPERCLIP_AUTH_PUBLIC_BASE_URL':f'http://paperclip-{ident}.localhost:8081','PAPERCLIP_ALLOWED_HOSTNAMES':f'paperclip-{ident}.localhost','PAPERCLIP_AUTH_DISABLE_SIGN_UP':'true','PAPERCLIP_ANNOUNCEMENTS_ENABLED':'false','PAPERCLIP_DB_BACKUP_ENABLED':'false'},'volumes':['paperclip:/paperclip','git:/engagement'],'networks':{'backend':{},'ingress':{'aliases':['paperclip-'+ident]}},'depends_on':{'postgres':{'condition':'service_healthy'}}},'2g'),
 'lab':bounded({'image':LOCK['lab'],'profiles':['lab'],'environment':{'QUICK_CONNECT_MG_HOST':'graph','QUICK_CONNECT_MG_PORT':'7687'},'volumes':['lab:/var/lib/memgraph-lab'],'networks':['backend']},'512m'),
 }
 config={'name':'governed-dd-'+ident,'services':services,'networks':{'backend':{'name':network,'internal':True},'ingress':{'name':ingress,'internal':True}},'volumes':{n:{'name':f'governed-dd-{ident}-{n}'} for n in ['postgres','graph','artifacts','ontology','paperclip','git','agent-home','lab']},'secrets':{'admin':{'file':'../../secrets/'+ident+'-admin'},'agent':{'file':'../../secrets/'+ident+'-agent'},'gateway-signing':{'file':'../../secrets/gateway-signing'}}}
 (folder/'compose.yaml').write_text(yaml.safe_dump(config,sort_keys=False))
 info.write_text(json.dumps({'id':ident,'name':name}))
 print('Rendered tenant '+ident+'; no engine access performed.')


if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['setup','tenant']);p.add_argument('--id');p.add_argument('--name');a=p.parse_args()
 if a.action=='setup':setup()
 else:tenant(a.id,a.name)
