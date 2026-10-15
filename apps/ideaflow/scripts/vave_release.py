"""Reviewed update path for the existing IdeaFlow VPS, without credential/storage changes."""
import argparse, hashlib, json, re, shlex, tarfile, time, uuid
from pathlib import Path
from vps import run

def prepare(archive):
    directory=archive.parent
    version=json.loads(Path('frontend/package.json').read_text())['version']
    assert re.fullmatch(r'\d+\.\d+\.\d+',version)
    with tarfile.open(archive) as tar:
        manifests=json.load(tar.extractfile('manifest.json'))
        images={}
        for role in ('backend','frontend'):
            entry=next(m for m in manifests if f'ideaflow-{role}:{version}' in (m.get('RepoTags') or []))
            images[role]=hashlib.sha256(tar.extractfile(entry['Config']).read()).hexdigest()
    report={'version':version,'schema':'0006','archive':archive.name,'archive_sha256':hashlib.file_digest(archive.open('rb'),'sha256').hexdigest(),'images':images}
    (directory/'release.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

def deploy(client, release_path):
    path=Path(release_path);manifest=json.loads((path/'release.json').read_text());archive=path/manifest['archive']
    assert manifest['version'] in ('1.1.0','1.2.0') and manifest['schema']=='0006'
    assert hashlib.file_digest(archive.open('rb'),'sha256').hexdigest()==manifest['archive_sha256']
    assert all(re.fullmatch('[0-9a-f]{64}',value) for value in manifest['images'].values())
    stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime());remote='/home/ubuntu/ideaflow-vave-'+stamp
    backup='/home/ideaflow/backups/vave-update-'+stamp
    run(client,'install -d -m 700 '+shlex.quote(remote))
    with client.open_sftp() as sftp:
        for local,name in [(archive,'images.tar'),(path/'release.json','release.json'),(Path('scripts/vave-fingerprint.py'),'fingerprint.py')]:
            sftp.put(str(local),remote+'/'+name);sftp.chmod(remote+'/'+name,0o600)
            assert run(client,'sha256sum '+shlex.quote(remote+'/'+name),quiet=True).split()[0]==hashlib.file_digest(local.open('rb'),'sha256').hexdigest()
    print('Release transferred and checksummed; preparing retained rollback assets.',flush=True)
    def app(command,quiet=False,timeout=300):
        return run(client,'cd /home/ideaflow; runuser -u ideaflow -- env XDG_RUNTIME_DIR=/run/user/1001 sh -c '+shlex.quote(command),sudo=True,quiet=quiet,timeout=timeout)
    run(client,'test "$(id -u ideaflow)" = 1001; install -d -o ideaflow -g ideaflow -m 700 '+shlex.quote(backup),sudo=True)
    run(client,'install -o ideaflow -g ideaflow -m 600 '+shlex.quote(remote+'/images.tar')+' '+shlex.quote(backup+'/new-images.tar')+'; install -o ideaflow -g ideaflow -m 644 '+shlex.quote(remote+'/fingerprint.py')+' '+shlex.quote(backup+'/fingerprint.py'),sudo=True)
    app('cp .config/containers/systemd/ideaflow-backend.container '+shlex.quote(backup+'/backend.previous')+'; cp .config/containers/systemd/ideaflow-frontend.container '+shlex.quote(backup+'/frontend.previous')+'; sha256sum .config/ideaflow/*.env > '+shlex.quote(backup+'/credentials.sha256'))
    old={}
    for role in ('backend','frontend'):
        original=app('cat .config/containers/systemd/ideaflow-'+role+'.container',quiet=True)
        old[role]=re.search(r'^Image=([0-9a-f]{64})$',original,re.M).group(1)
        updated=re.sub(r'^Image=.*$', 'Image='+manifest['images'][role],original,flags=re.M)
        with client.open_sftp() as sftp:
            with sftp.open(remote+'/'+role+'.container','w') as f: f.write(updated)
            sftp.chmod(remote+'/'+role+'.container',0o600)
    app('podman save --format docker-archive --multi-image-archive -o '+shlex.quote(backup+'/previous-images.tar')+' '+old['backend']+' '+old['frontend'],timeout=300)
    app('podman load -i '+shlex.quote(backup+'/new-images.tar'),timeout=300)
    for role,digest in manifest['images'].items(): app('podman image exists '+digest)
    network=app("podman inspect --format '{{json .NetworkSettings.Networks}}' ideaflow-backend",quiet=True)
    assert 'ideaflow' in json.loads(network)
    original_schema=app('podman exec ideaflow-postgres psql -U ideaflow_migrator -d ideaflow -Atc "SELECT version_num FROM alembic_version"',quiet=True).strip()
    assert original_schema in ('0005','0006'), 'Unexpected deployed schema'
    def fingerprint(name,expected=None,upgrade=False,database=None):
        command='podman run --rm --user 0 --network ideaflow --env-file .config/ideaflow/backend.env -v '+shlex.quote(backup+':/check')+' --entrypoint python '+manifest['images']['backend']+' /check/fingerprint.py --output /check/'+name
        if expected: command+=' --expected /check/'+expected
        if upgrade: command+=' --upgrade'
        if database: command+=' --database '+database
        return app(command)
    stopped=False;changed=False;paused=None
    try:
        print('Pausing IdeaFlow for a coherent verified backup and image update.',flush=True)
        paused=time.monotonic()
        stopped=True;app('systemctl --user stop app-ideaflow.target ideaflow-frontend.service ideaflow-backend.service ideaflow-postgres.service')
        app('systemctl --user start ideaflow-postgres.service')
        fingerprint('before.json')
        app('podman exec ideaflow-postgres pg_dump -U ideaflow_migrator -d ideaflow -Fc --no-owner --no-acl -f /tmp/vave-'+stamp+'.dump; podman cp ideaflow-postgres:/tmp/vave-'+stamp+'.dump '+shlex.quote(backup+'/production.dump')+'; sha256sum '+shlex.quote(backup+'/production.dump')+' > '+shlex.quote(backup+'/production.dump.sha256'))
        testdb='ideaflow_restore_'+uuid.uuid4().hex
        app('podman exec ideaflow-postgres createdb -U ideaflow_migrator '+testdb)
        try:
            app('podman exec ideaflow-postgres pg_restore -U ideaflow_migrator --exit-on-error --no-owner --no-acl -d '+testdb+' /tmp/vave-'+stamp+'.dump')
            fingerprint('restore.json','before.json',database=testdb)
        finally:
            app('podman exec ideaflow-postgres dropdb -U ideaflow_migrator '+testdb)
        fingerprint('live-after-backup.json','before.json')
        # Download the coherent current production dump, never a local snapshot.
        run(client,'install -o ubuntu -g ubuntu -m 600 '+shlex.quote(backup+'/production.dump')+' '+shlex.quote(remote+'/production.dump'),sudo=True)
        local_backup=Path('backups')/('vps-vave-'+stamp+'.dump');local_backup.parent.mkdir(exist_ok=True)
        assert not local_backup.exists()
        with client.open_sftp() as sftp: sftp.get(remote+'/production.dump',str(local_backup))
        digest=hashlib.file_digest(local_backup.open('rb'),'sha256').hexdigest()
        assert digest==run(client,'sha256sum '+shlex.quote(remote+'/production.dump'),quiet=True).split()[0]
        print('Fresh production backup restored in isolation, compared exactly and downloaded with verified SHA-256 '+digest,flush=True)
        for role in ('backend','frontend'):
            run(client,'install -o ideaflow -g ideaflow -m 600 '+shlex.quote(remote+'/'+role+'.container')+' /home/ideaflow/.config/containers/systemd/ideaflow-'+role+'.container',sudo=True)
        changed=True;app('systemctl --user daemon-reload; systemctl --user start app-ideaflow.target')
        downtime=round(time.monotonic()-paused,1)
        fingerprint('after.json','before.json',upgrade=True)
        app('sha256sum -c '+shlex.quote(backup+'/credentials.sha256')+'; systemctl --user is-active app-ideaflow.target; podman ps; systemctl --user --failed --no-pager')
        for role in ('postgres','backend','frontend'):
            health=app("podman inspect --format '{{.State.Health.Status}}' ideaflow-"+role,quiet=True).strip()
            assert health=='healthy',role+' health failed'
        run(client,'systemctl is-active caddy ufw fail2ban auditd; systemctl --failed --no-pager',sudo=True)
        evidence={'release':manifest,'backup_sha256':digest,'server_rollback':backup,'local_backup':str(local_backup),'timestamp_utc':stamp,'preserved':True,'maintenance_seconds':downtime}
        (path/'deployment.json').write_text(json.dumps(evidence,indent=2));print(json.dumps(evidence,indent=2),flush=True)
    except BaseException:
        print('Update verification failed; restoring the previous image pins without restoring the database.',flush=True)
        if changed:
            app('systemctl --user stop app-ideaflow.target ideaflow-frontend.service ideaflow-backend.service ideaflow-postgres.service; systemctl --user start ideaflow-postgres.service')
            # Retain additive tables and restore the prior release's readiness marker.
            app(f"podman exec ideaflow-postgres psql -U ideaflow_migrator -d ideaflow -c \"UPDATE alembic_version SET version_num='{original_schema}' WHERE version_num='0006'\"")
            app('cp '+shlex.quote(backup+'/backend.previous')+' .config/containers/systemd/ideaflow-backend.container; cp '+shlex.quote(backup+'/frontend.previous')+' .config/containers/systemd/ideaflow-frontend.container; systemctl --user daemon-reload')
        if stopped: app('systemctl --user start app-ideaflow.target')
        raise

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare']);parser.add_argument('--archive',required=True);args=parser.parse_args();prepare(Path(args.archive))
