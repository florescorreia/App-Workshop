"""Independent rootless VPS apps; fresh install and data-preserving updates.

Invoked explicitly through workshop-vps.ps1, with workstation environment
secrets and pinned SSH identity. Never modifies the existing IdeaFlow units.
"""
import argparse
import hashlib
import json
import os
import re
import shlex
import time
import urllib.request
from pathlib import Path
import paramiko
import vps
import workshop

ROOT=Path(__file__).resolve().parents[1]
q=shlex.quote

def install_script(app,stage):
    slug=workshop.valid_slug(app['slug'])
    if app['vps']['account']!=slug:raise ValueError('Account mismatch')
    port=app['vps']['publicPort'];loopback=app['vps']['loopbackPort']
    # Values are validated identifiers, integers or shell-quoted paths. The
    # only replacements in this fixed script cannot contain shell syntax.
    return f'''#!/bin/sh
set -eu
app={q(slug)}
stage={q(stage)}
cd /
home=/home/$app
marker=$home/.config/$app/workshop-owner
fresh=0
if getent passwd "$app" >/dev/null; then
 test "$(getent passwd "$app" | cut -d: -f6)" = "$home"
 test -f "$marker" && test "$(cat "$marker")" = "$app"
else
 test ! -e "$home"
 test ! -e /etc/caddy/apps.d/$app.caddy
 # Refuse occupied ports before creating an account or touching a route.
 test -z "$(ss -H -ltn '( sport = :{port} or sport = :{loopback} )')"
 test ! -e /etc/systemd/system/app-$app.service
 useradd --create-home --shell /bin/bash "$app"
 fresh=1
fi
grep -q "^$app:" /etc/subuid
grep -q "^$app:" /etc/subgid
loginctl enable-linger "$app"
uid=$(id -u "$app")
systemctl start "user@$uid.service"
as_app() {{ runuser -u "$app" -- env XDG_RUNTIME_DIR="/run/user/$uid" "$@"; }}
install -d -o "$app" -g "$app" -m 700 "$home/.config/$app" "$home/.config/containers/systemd" "$home/.config/systemd/user" "$home/releases" "$home/backups" "$home/bin"
if [ "$fresh" = 1 ]; then
 test -z "$(as_app podman ps -aq)"
 test -z "$(as_app podman volume ls -q)"
 for name in postgres backend; do
  install -o "$app" -g "$app" -m 600 "$stage/$name.env" "$home/.config/$app/$name.env"
 done
 printf '%s\\n' "$app" > "$marker"
 chown "$app:$app" "$marker"; chmod 600 "$marker"
else
 test -s "$home/.config/$app/postgres.env"
 test -s "$home/.config/$app/backend.env"
 # Updates preserve the server secrets. Do not re-bootstrap passwords.
 if as_app podman container exists "$app-postgres"; then
  as_app "$home/bin/backup.sh"
 fi
fi
as_app systemctl --user enable --now podman.socket
release=$(basename "$stage")
install -d -o "$app" -g "$app" -m 700 "$home/releases/$release"
install -o "$app" -g "$app" -m 600 "$stage/images.tar" "$home/releases/$release/images.tar"
as_app podman load -i "$home/releases/$release/images.tar"
for image in $(cat "$stage/image-ids.txt"); do as_app podman image exists "$image"; done
if [ "$fresh" = 0 ]; then
 as_app systemctl --user stop "app-$app.target" "$app-frontend.service" "$app-backend.service" "$app-postgres.service"
fi
for file in "$stage"/*.container "$stage"/*.network; do
 if [ -e "$home/.config/containers/systemd/$(basename "$file")" ]; then cp -p "$home/.config/containers/systemd/$(basename "$file")" "$home/releases/$release/previous-$(basename "$file")"; fi
 install -o "$app" -g "$app" -m 600 "$file" "$home/.config/containers/systemd/$(basename "$file")"
done
for file in "$stage"/*.target "$stage"/*.service "$stage"/*.timer; do
 install -o "$app" -g "$app" -m 600 "$file" "$home/.config/systemd/user/$(basename "$file")"
done
for name in wait-container.sh backup.sh; do
 install -o "$app" -g "$app" -m 750 "$stage/$name" "$home/bin/$name"
done
install -d -m 755 /etc/systemd/system/user@$uid.service.d
cat > /etc/systemd/system/user@$uid.service.d/zz-$app.conf <<EOF
[Service]
TimeoutStopSec=180
ExecStop=/usr/bin/env XDG_RUNTIME_DIR=/run/user/$uid /usr/bin/systemctl --user stop app-$app.target $app-frontend.service $app-backend.service $app-postgres.service
EOF
systemctl daemon-reload
as_app systemctl --user daemon-reload
as_app systemctl --user enable "app-$app.target" "$app-backup.timer"
as_app systemctl --user start "app-$app.target" "$app-backup.timer"
curl --fail --silent --max-time 15 http://127.0.0.1:{loopback}/api/health/ready
as_app "$home/bin/backup.sh"
# Validate candidate gateway configuration before activating this route.
# Keep backups of this app's previous route and units; shared files untouched.
if [ -e /etc/caddy/apps.d/$app.caddy ]; then cp -p /etc/caddy/apps.d/$app.caddy "$home/releases/previous.caddy"; fi
install -m 644 "$stage/$app.caddy" /etc/caddy/apps.d/$app.caddy
if ! caddy validate --config /etc/caddy/Caddyfile; then
 if [ -e "$home/releases/previous.caddy" ]; then cp -p "$home/releases/previous.caddy" /etc/caddy/apps.d/$app.caddy; else mv /etc/caddy/apps.d/$app.caddy "$stage/invalid-route.caddy"; fi
 exit 1
fi
systemctl reload caddy
ufw allow {port}/tcp
as_app podman ps --format '{{{{.Names}}}} {{{{.Status}}}}'
'''

def connection(data):
    server=data['vps']
    for name in ('sshKeyFile','knownHostsFile'):
        if Path(server[name]).name!=server[name]:raise ValueError('SSH filename must be a basename')
    vps.PREFIX=server['credentialPrefix']
    client=paramiko.SSHClient()
    client.load_host_keys('/ssh/'+server['knownHostsFile'])
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    key=paramiko.Ed25519Key.from_private_key_file('/ssh/'+server['sshKeyFile'],password=os.environ[vps.PREFIX+'-SSH-KEY-PASSPHRASE'])
    client.connect(server['host'],username=server['sshUser'],pkey=key,allow_agent=False,look_for_keys=False,timeout=20)
    client.get_transport().set_keepalive(30)
    return client

def transfer(client,local,remote):
    last=[0]
    def progress(done,total):
        if time.monotonic()-last[0]>20:
            print(f'Transfer {local.name}: {done*100//max(total,1)}%',flush=True);last[0]=time.monotonic()
    with client.open_sftp() as sftp:
        sftp.put(str(local),remote,callback=progress);sftp.chmod(remote,0o600)
    with local.open('rb') as source:checksum=hashlib.file_digest(source,'sha256').hexdigest()
    if vps.run(client,'sha256sum '+q(remote),quiet=True).split()[0]!=checksum:raise RuntimeError('Transfer checksum mismatch')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['deploy','status','start','stop','backup']);parser.add_argument('--app',required=True);parser.add_argument('--release');args=parser.parse_args()
    entry,app,path=workshop.app_config(ROOT,args.app)
    if entry['kind']!='workshop':raise ValueError('Existing application deployment must use its own established tools')
    data=workshop.catalog();slug=app['slug'];prefix='APPWORKSHOP-'+slug.upper()+'-VPS'
    with connection(data) as client:
        if args.action!='deploy':
            commands={'status':f'systemctl --user status app-{slug}.target --no-pager; podman ps',
                      'start':f'systemctl --user start app-{slug}.target',
                      'stop':f'systemctl --user stop app-{slug}.target {slug}-frontend.service {slug}-backend.service {slug}-postgres.service',
                      'backup':f'/home/{slug}/bin/backup.sh'}
            wrapper=f'cd /home/{slug}; uid=$(id -u {slug}); runuser -u {slug} -- env XDG_RUNTIME_DIR=/run/user/$uid sh -c '+q(commands[args.action])
            vps.run(client,wrapper,sudo=True)
            if args.action=='backup':
                # Download only this app's newest custom-format dump privately.
                remote=vps.run(client,f'find /home/{slug}/backups -maxdepth 1 -name "*.dump" -printf "%f\\n" | sort | tail -1',sudo=True,quiet=True).strip()
                if not re.fullmatch(r'[a-z0-9-]+-[0-9TZ]+\.dump',remote):raise ValueError('Invalid backup name')
                temporary=f'/home/{data["vps"]["sshUser"]}/workshop-{slug}-{remote}'
                vps.run(client,f'install -o {q(data["vps"]["sshUser"])} -m 600 /home/{slug}/backups/{remote} {q(temporary)}',sudo=True)
                destination=path/'backups'/remote;destination.parent.mkdir(parents=True,exist_ok=True)
                if destination.exists():raise ValueError('Local backup exists; refusing overwrite')
                with client.open_sftp() as sftp:sftp.get(temporary,str(destination))
                with destination.open('rb') as source:checksum=hashlib.file_digest(source,'sha256').hexdigest()
                if vps.run(client,'sha256sum '+q(temporary),quiet=True).split()[0]!=checksum:raise RuntimeError('Backup checksum mismatch')
                print('Private off-host backup downloaded; SHA-256 verified.')
            return
        if not args.release or not re.fullmatch(r'[a-f0-9]{12}',args.release):raise ValueError('Supply the prepared 12-character release identifier')
        folder=path/'local/releases'/args.release
        images=path/'local/release-images.tar'
        ids=workshop.archive_ids(images,app)
        if ids!=json.loads((folder/'images.json').read_text()):raise ValueError('Prepared image identity mismatch')
        with images.open('rb') as source:checksum=hashlib.file_digest(source,'sha256').hexdigest()
        if checksum!=(folder/'archive.sha256').read_text().strip():raise ValueError('Archive changed after preparation')
        outputs=workshop.render_release(app,data['vps']['hostname'],ids)
        for name,content in outputs.items():
            if (folder/name).read_text()!=content:raise ValueError('Release changed; prepare again instead of editing deployment assets')
        def secret(name):
            value=os.environ[prefix+'-'+name]
            if any(c in value for c in '\n\r'):raise ValueError('Multiline secret unsupported')
            return value
        db=secret('DB-PASSWORD')
        # URL-safe passwords avoid ambiguous libpq URL / systemd env syntax.
        if not re.fullmatch(r'[A-Za-z0-9_!.-]{24,}',db):raise ValueError('Use generated URL-safe database secret')
        for name in ('ADMIN-PASSWORD','COCKPIT-PASSWORD'):
            if not re.fullmatch(r'[A-Za-z0-9_!.-]{24,}',secret(name)):raise ValueError('Use generated environment-safe credentials')
        base=f'https://{data["vps"]["hostname"]}:{app["vps"]["publicPort"]}'
        if secret('URL')!=base:raise ValueError('Windows URL differs from catalog')
        envs={'postgres.env':{'POSTGRES_DB':app['database']['name'],'POSTGRES_USER':app['database']['user'],'POSTGRES_PASSWORD':db},
              'backend.env':{'DATABASE_URL':f'postgresql://{app["database"]["user"]}:{db}@postgres:5432/{app["database"]["name"]}',
                 'ADMIN_EMAIL':secret('ADMIN-EMAIL'),'ADMIN_PASSWORD':secret('ADMIN-PASSWORD'),'APP_TITLE':app['title'],
                 'APP_SLUG':slug,'APP_ORIGIN':base,'SESSION_COOKIE_NAME':'__Host-'+slug+'_session'}}
        stage=f'/home/{data["vps"]["sshUser"]}/workshop-{slug}-{args.release}'
        # Existing app identity must match before any stop/replacement.
        exists=vps.run(client,f'if getent passwd {slug} >/dev/null; then echo yes; else echo no; fi',quiet=True).strip()=='yes'
        if exists:vps.run(client,f'test "$(cat /home/{slug}/.config/{slug}/workshop-owner)" = {slug}',sudo=True,quiet=True)
        vps.run(client,'install -d -m 700 '+q(stage))
        for name in outputs:transfer(client,folder/name,stage+'/'+name)
        transfer(client,images,stage+'/images.tar')
        with client.open_sftp() as sftp:
            assets={'install.sh':install_script(app,stage),'image-ids.txt':'\n'.join(ids.values())+'\n'}
            if not exists:
                for env in envs.values():
                    if any('\n' in value or '\r' in value or '\x00' in value for value in env.values()):raise ValueError('Invalid environment value')
                assets.update({name:''.join(f'{key}={value}\n' for key,value in env.items()) for name,env in envs.items()})
            for name,content in assets.items():
                with sftp.open(stage+'/'+name,'w') as out:out.write(content)
                sftp.chmod(stage+'/'+name,0o600)
        vps.run(client,'sh '+q(stage+'/install.sh'),sudo=True,timeout=900)
        if not exists:vps.run(client,'chpasswd',sudo=True,input_data=slug+':'+secret('COCKPIT-PASSWORD')+'\n')
        with urllib.request.urlopen(base+'/api/health/ready',timeout=30) as response:
            if json.load(response).get('status')!='ready':raise RuntimeError('Public HTTPS readiness failed')
        print(f'Verified deployment: {base}; account {slug}; volume {app["database"]["volume"]}.')

if __name__=='__main__':main()
