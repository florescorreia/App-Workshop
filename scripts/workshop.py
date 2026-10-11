"""Workspace catalog, clean app creation and reviewable VPS releases.

Runs in a transient container. Never installs or changes a live VPS app.
"""
import argparse, hashlib, json, re, tarfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SLUG=re.compile(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z')

def valid_slug(value):
    if not isinstance(value,str) or not SLUG.fullmatch(value) or len(value)>24:
        raise ValueError('Invalid application slug (lowercase, hyphens, max 24 characters)')
    return value

def catalog(root=ROOT):
    result=json.loads((root/'workshop.json').read_text())
    if result['schemaVersion']!=1:raise ValueError('Unsupported catalog version')
    return result

def app_config(root,slug):
    valid_slug(slug)
    entry=catalog(root)['apps'][slug]
    path=(root/entry['path']).resolve()
    if entry['kind']=='existing':return entry,None,path
    if not path.is_relative_to((root/'apps').resolve()) or path==(root/'apps').resolve():raise ValueError('App path escapes apps/')
    app=json.loads((path/'app.json').read_text())
    if app['slug']!=slug or app['composeProject']!=entry['composeProject'] or app['localPort']!=entry['localPort'] or app['vps']!=entry['vps']:
        raise ValueError('Catalog/app.json identity or port mismatch')
    check_collisions(catalog(root),slug,entry)
    if app['database']!={'name':slug.replace('-','_'),'user':slug.replace('-','_')+'_owner','volume':slug+'_pgdata'}:
        raise ValueError('Unexpected database identity; do not share another app database')
    return entry,app,path

def check_collisions(data,slug,entry):
    for key in ('localPort',):
        value=entry[key]
        if not isinstance(value,int) or isinstance(value,bool) or not 1024<=value<=65535:raise ValueError('Invalid port')
    for key in ('publicPort','loopbackPort'):
        value=entry['vps'][key]
        if not isinstance(value,int) or isinstance(value,bool) or not 1024<=value<=65535:raise ValueError('Invalid VPS port')
    if entry['vps']['publicPort'] in (2019,9090) or entry['vps']['loopbackPort'] in (2019,9090):raise ValueError('Reserved management port')
    if entry['vps']['publicPort']==entry['vps']['loopbackPort']:raise ValueError('Public/private port collision')
    for name,other in data['apps'].items():
        if name==slug:continue
        if entry['composeProject']==other['composeProject'] or entry['path']==other['path']:raise ValueError('Duplicate app identity/path')
        if entry['localPort']==other['localPort']:raise ValueError('Local port collision')
        if entry['vps']['account']==other['vps']['account'] or entry['vps']['target']==other['vps']['target']:raise ValueError('VPS account/target collision')
        if {entry['vps']['publicPort'],entry['vps']['loopbackPort']} & {other['vps']['publicPort'],other['vps']['loopbackPort']}:raise ValueError('VPS port collision')

def next_port(used,start):
    while start in used:start+=1
    if start>65535:raise ValueError('No available catalog port')
    return start

def new_app(slug,root=ROOT,port=None):
    valid_slug(slug);data=catalog(root)
    if slug in data['apps']:raise ValueError('App already registered; refusing overwrite')
    target=root/'apps'/slug
    if target.exists():raise ValueError('App folder already exists; refusing overwrite')
    local=port if port is not None else next_port({v['localPort'] for v in data['apps'].values()},8081)
    used={v['vps'][k] for v in data['apps'].values() for k in ('publicPort','loopbackPort')}
    public=next_port(used,8444);private=next_port(used|{public},18082)
    entry={'path':f'apps/{slug}','kind':'workshop','composeProject':slug,'localPort':local,
           'vps':{'account':slug,'publicPort':public,'loopbackPort':private,'target':f'app-{slug}.target','managedBy':'workshop'}}
    check_collisions(data,slug,entry)
    values={'APP_SLUG':slug,'APP_TITLE':slug.replace('-',' ').title(),'LOCAL_PORT':str(local),'PUBLIC_PORT':str(public),'LOOPBACK_PORT':str(private)}
    values['DB_NAME']=slug.replace('-','_');values['DB_USER']=slug.replace('-','_')+'_owner'
    template=root/'templates'/'three-service'
    # Render into a new directory only. There are no credentials/data/.git in it.
    target.mkdir(parents=True)
    for source in sorted(template.rglob('*')):
        if not source.is_file() or any(part in ('__pycache__','node_modules','dist','local','backups') for part in source.relative_to(template).parts):continue
        dest=target/source.relative_to(template);dest.parent.mkdir(parents=True,exist_ok=True)
        content=source.read_text()
        for key,value in values.items():content=content.replace('{{'+key+'}}',value)
        dest.write_text(content)
    # Reuse the already tested, pinned dependency set without app source/data.
    (target/'backend'/'requirements.lock').write_bytes((root/'backend'/'requirements.lock').read_bytes())
    for name in ('package.json','package-lock.json'):
        (target/'frontend'/name).write_bytes((root/'frontend'/name).read_bytes())
    package=json.loads((target/'frontend'/'package.json').read_text());package['name']=slug+'-frontend';package['version']='0.1.0'
    (target/'frontend'/'package.json').write_text(json.dumps(package,indent=2)+'\n')
    lock=json.loads((target/'frontend'/'package-lock.json').read_text());lock['name']=package['name'];lock['version']=package['version'];lock['packages']['']['name']=package['name'];lock['packages']['']['version']=package['version']
    (target/'frontend'/'package-lock.json').write_text(json.dumps(lock,indent=2)+'\n')
    app={'schemaVersion':1,'slug':slug,'title':values['APP_TITLE'],'composeProject':slug,'localPort':local,'version':'0.1.0','vps':entry['vps'],
         'healthPath':'/api/health/ready','database':{'name':slug.replace('-','_'),'user':slug.replace('-','_')+'_owner','volume':slug+'_pgdata'},
         'services':{'postgres':{'image':'postgres:17.6-bookworm','memoryMiB':512,'cpus':0.5,'healthCommand':f"pg_isready -U {slug.replace('-','_')}_owner -d {slug.replace('-','_')}"},
                     'backend':{'image':f'{slug}-backend:0.1.0','memoryMiB':256,'cpus':0.5,'healthCommand':'python /app/healthcheck.py'},
                     'frontend':{'image':f'{slug}-frontend:0.1.0','memoryMiB':128,'cpus':0.5,'healthCommand':'wget -q --spider http://127.0.0.1/api/health/ready'}}}
    (target/'app.json').write_text(json.dumps(app,indent=2)+'\n')
    data['apps'][slug]=entry
    (root/'workshop.json').write_text(json.dumps(data,indent=2)+'\n')
    return app

def render_release(app,hostname,image_ids):
    slug=valid_slug(app['slug']);account=app['vps']['account']
    if account!=slug or app['vps']['target']!=f'app-{slug}.target':raise ValueError('Deployment identity must equal slug')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9 ._-]{0,79}',app['title']):raise ValueError('Invalid release title')
    if app['database']!={'name':slug.replace('-','_'),'user':slug.replace('-','_')+'_owner','volume':slug+'_pgdata'}:raise ValueError('Invalid database identity')
    for key in ('publicPort','loopbackPort'):
        if type(app['vps'][key]) is not int or not 1024<=app['vps'][key]<=65535:raise ValueError('Invalid VPS port')
    if app['vps']['publicPort']==app['vps']['loopbackPort']:raise ValueError('Public and private port must differ')
    if not re.fullmatch(r'[a-z0-9][a-z0-9.-]+',hostname):raise ValueError('Invalid hostname')
    home=f'/home/{account}';target=f'app-{slug}.target';outputs={}
    outputs[target]=f'[Unit]\nDescription={app["title"]} application\nRequires={slug}-postgres.service {slug}-backend.service {slug}-frontend.service\nAfter={slug}-postgres.service {slug}-backend.service {slug}-frontend.service\n\n[Install]\nWantedBy=default.target\n'
    outputs[f'{slug}.network']=f'[Network]\nNetworkName={slug}\n'
    for service in ('postgres','backend','frontend'):
        config=app['services'][service];image=image_ids[service]
        if not re.fullmatch(r'sha256:[a-f0-9]{64}',image):raise ValueError('Image must be pinned by configuration content ID')
        health=config['healthCommand']
        # Quadlet inline health commands must remain simple; complex scripts go
        # in the built image, avoiding the quote-stripping bug found in IdeaFlow.
        if not re.fullmatch(r'[A-Za-z0-9_ ./:-]+',health):raise ValueError('Use a simple health command or a script in the image')
        memory=config['memoryMiB'];cpus=config['cpus']
        if not isinstance(memory,int) or memory<32 or not isinstance(cpus,(int,float)) or cpus<=0:raise ValueError('Invalid resource budget')
        extra=''
        if service=='postgres':extra=f'EnvironmentFile={home}/.config/{slug}/postgres.env\nVolume={app["database"]["volume"]}:/var/lib/postgresql/data\n'
        if service=='backend':extra=f'EnvironmentFile={home}/.config/{slug}/backend.env\n'
        if service=='frontend':extra=f'PublishPort=127.0.0.1:{app["vps"]["loopbackPort"]}:80\n'
        dependency={'postgres':'','backend':f'Requires={slug}-postgres.service\nAfter={slug}-postgres.service\n','frontend':f'Requires={slug}-backend.service\nAfter={slug}-backend.service\n'}[service]
        outputs[f'{slug}-{service}.container']=f'[Unit]\nDescription={app["title"]} {service}\nPartOf={target}\n{dependency}StartLimitIntervalSec=0\n\n[Container]\nImage={image}\nContainerName={slug}-{service}\nNetwork={slug}.network\nNetworkAlias={service}\n{extra}HealthCmd={health}\nHealthInterval=5s\nHealthTimeout=3s\nHealthRetries=12\nHealthStartPeriod=20s\nPodmanArgs=--memory={memory}m --cpus={cpus} --log-driver=k8s-file --log-opt=max-size=10mb --health-on-failure=kill\n\n[Service]\nRestart=on-failure\nRestartSec=5\nTimeoutStartSec=180\nExecStartPost={home}/bin/wait-container.sh {slug}-{service}\n'
    outputs['wait-container.sh']=f'#!/bin/sh\nset -eu\ncase "$1" in {slug}-postgres|{slug}-backend|{slug}-frontend) ;; *) exit 2 ;; esac\nattempt=0\nwhile [ "$attempt" -lt 80 ]; do\n if [ "$(podman inspect --format \'{{{{.State.Health.Status}}}}\' "$1")" = healthy ]; then exit 0; fi\n attempt=$((attempt + 1)); sleep 2\ndone\nexit 1\n'
    outputs['backup.sh']=f'''#!/bin/sh
set -eu
cd /home/{slug}
umask 077
stamp=$(date -u +%Y%m%dT%H%M%SZ)
name={slug}-$stamp.dump
test ! -e backups/$name
podman exec {slug}-postgres pg_dump -U {app['database']['user']} -d {app['database']['name']} -Fc > backups/$name.partial
podman exec -i {slug}-postgres pg_restore --list < backups/$name.partial > backups/$name.list
test "$(wc -l < backups/$name.list)" -gt 10
mv backups/$name.partial backups/$name
sha256sum backups/$name
'''
    outputs[f'{slug}-backup.service']=f'[Unit]\nDescription={app["title"]} database backup\n\n[Service]\nType=oneshot\nExecStart=/home/{slug}/bin/backup.sh\n'
    outputs[f'{slug}-backup.timer']=f'[Unit]\nDescription={app["title"]} daily backup\n\n[Timer]\nOnCalendar=*-*-* 04:30:00 UTC\nRandomizedDelaySec=1800\nPersistent=true\nUnit={slug}-backup.service\n\n[Install]\nWantedBy=timers.target\n'
    # No standard-port site: IdeaFlow owns the shared 80/443 redirect already.
    outputs[f'{slug}.caddy']=f'{hostname}:{app["vps"]["publicPort"]} {{\n    header {{\n        -Server\n        -Via\n        X-Content-Type-Options nosniff\n        Referrer-Policy same-origin\n        X-Frame-Options DENY\n    }}\n    @private_paths path /api/docs /api/docs/* /api/openapi.json /api/openapi.json/* */.*\n    respond @private_paths "Not found" 404\n    reverse_proxy 127.0.0.1:{app["vps"]["loopbackPort"]} {{\n        header_down -Server\n        header_down -Via\n    }}\n    log {{\n        output file /var/log/caddy/{slug}-access.log {{\n            roll_size 10MiB\n            roll_keep 5\n        }}\n    }}\n}}\n'
    outputs['DEPLOYMENT.md']=f'# {app["title"]} prepared release\n\nThis package has NOT been deployed. Follow docs/APP_WORKSHOP.md in the source repository.\n\nAccount: {account}; target: {target}; volume: {app["database"]["volume"]}.\nPublic URL: https://{hostname}:{app["vps"]["publicPort"]}; private frontend: 127.0.0.1:{app["vps"]["loopbackPort"]}.\nDo not overwrite existing account secrets/volumes or restore local data over live production.\nDatabase copy, backups, restore verification, origin/cookies and browser checks must be completed for this app before publication.\n'
    return outputs

def archive_ids(archive,app):
    with tarfile.open(archive) as bundle:
        manifest=json.load(bundle.extractfile('manifest.json'));ids={}
        for service,config in app['services'].items():
            rows=[row for row in manifest if config['image'] in (row.get('RepoTags') or [])]
            if len(rows)!=1:raise ValueError('Missing or ambiguous image in archive: '+config['image'])
            stream=bundle.extractfile(rows[0]['Config'])
            ids[service]='sha256:'+hashlib.file_digest(stream,'sha256').hexdigest()
    return ids

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=('new','prepare-vps'));p.add_argument('--app',required=True);p.add_argument('--port',type=int);p.add_argument('--images');args=p.parse_args()
    if args.action=='new':
        app=new_app(args.app,port=args.port);print(f'Created apps/{args.app}; local port {app["localPort"]}; no data or credentials copied.')
    else:
        entry,app,path=app_config(ROOT,args.app)
        if entry['kind']=='existing':raise ValueError('Use existing IdeaFlow deployment tools; refusing replacement')
        if not args.images:raise ValueError('Image-ID input required')
        ids=archive_ids(args.images,app);outputs=render_release(app,catalog()['vps']['hostname'],ids)
        checksum=hashlib.sha256(json.dumps(outputs,sort_keys=True).encode()).hexdigest()[:12]
        folder=path/'local'/'releases'/checksum
        if folder.exists():print(f'Release already prepared: {folder.relative_to(ROOT)}');return
        folder.mkdir(parents=True)
        for name,content in outputs.items():(folder/name).write_text(content)
        (folder/'images.json').write_text(json.dumps(ids,indent=2)+'\n')
        with open(args.images,'rb') as source:(folder/'archive.sha256').write_text(hashlib.file_digest(source,'sha256').hexdigest()+'\n')
        print(f'Reviewable VPS release: {folder.relative_to(ROOT)}. No VPS mutation performed.')

if __name__=='__main__':main()
