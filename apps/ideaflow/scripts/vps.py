"""Containerized SSH operations with pinned host identity; never print credentials."""
import argparse,json,os,shlex,sys,hashlib,time,http.client,http.cookiejar,base64,socket
from pathlib import Path
import paramiko

HOST='40.160.88.11'
PREFIX='VPS-OVH-US-8104e6c8'

def connect():
    client=paramiko.SSHClient()
    client.load_host_keys('/ssh/vps-8104e6c8_known_hosts')
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    key=paramiko.Ed25519Key.from_private_key_file('/ssh/vps-8104e6c8_ed25519',password=os.environ[PREFIX+'-SSH-KEY-PASSPHRASE'])
    client.connect(HOST,username='ubuntu',pkey=key,allow_agent=False,look_for_keys=False,timeout=20)
    client.get_transport().set_keepalive(30)
    return client

def run(client,command,sudo=False,timeout=300,quiet=False,input_data=''):
    if sudo:command='sudo -S -p "" -- sh -c '+shlex.quote(command)
    stdin,stdout,stderr=client.exec_command(command,timeout=timeout)
    if sudo:stdin.write(os.environ[PREFIX]+'\n')
    if input_data:stdin.write(input_data)
    stdin.flush()
    stdin.channel.shutdown_write()
    channel=stdout.channel;out_parts=[];err_parts=[];deadline=time.monotonic()+timeout
    while True:
        if channel.recv_ready():out_parts.append(channel.recv(65536))
        if channel.recv_stderr_ready():err_parts.append(channel.recv_stderr(65536))
        if channel.exit_status_ready() and not channel.recv_ready() and not channel.recv_stderr_ready():break
        if time.monotonic()>deadline:channel.close();raise TimeoutError('Remote command exceeded its time budget')
        time.sleep(.03)
    out=b''.join(out_parts).decode();err=b''.join(err_parts).decode();code=channel.recv_exit_status()
    for secret in [os.environ.get(k,'') for k in os.environ if k==PREFIX or k.endswith('-PASSWORD') or k.endswith('-PASSPHRASE')]:
        if secret:out=out.replace(secret,'[REDACTED]');err=err.replace(secret,'[REDACTED]')
    if not quiet:
        print(out,end='',flush=True)
        if err:print(err,end='',file=sys.stderr,flush=True)
    if code:raise RuntimeError(f'Remote command failed with status {code}')
    return out

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action');parser.add_argument('--file');parser.add_argument('--command');args=parser.parse_args()
    with connect() as client:
        if args.action=='inspect':
            run(client,'id; uname -m; free -m; df -h /; podman --version; ss -ltn; systemctl --failed --no-pager')
            run(client,'cat /etc/caddy/Caddyfile; ls -l /etc/caddy/apps.d; ufw status verbose; getent passwd ideaflow; loginctl list-users; systemctl status caddy --no-pager',sudo=True)
        elif args.action in ('exec','sudo'):
            if not args.command:parser.error('--command is required')
            run(client,args.command,sudo=args.action=='sudo')
        elif args.action=='upload':
            if not args.file or not args.command:parser.error('--file and --command (remote path) are required')
            local=Path(args.file);size=local.stat().st_size;last=[0]
            def progress(done,total):
                if time.monotonic()-last[0]>20:
                    print(f'Transfer {local.name}: {done*100//max(total,1)}%',flush=True);last[0]=time.monotonic()
            with client.open_sftp() as sftp:sftp.put(str(local),args.command,callback=progress)
            with local.open('rb') as source:checksum=hashlib.file_digest(source,'sha256').hexdigest()
            remote=run(client,'sha256sum '+shlex.quote(args.command),quiet=True).split()[0]
            if remote!=checksum:raise RuntimeError('Transfer checksum mismatch')
            print(f'Uploaded {local.name}: {size} bytes; SHA-256 verified {checksum}')
        elif args.action=='secrets':
            if not args.command:parser.error('--command (protected staging directory) is required')
            base=args.command.rstrip('/')
            run(client,'install -d -m 700 '+shlex.quote(base))
            db=os.environ['IDEAFLOW-VPS-DB-PASSWORD'];app_db=os.environ['IDEAFLOW-VPS-APP-DB-PASSWORD']
            values={
                'postgres.env':{'POSTGRES_DB':'ideaflow','POSTGRES_USER':'ideaflow_migrator','POSTGRES_PASSWORD':db},
                'backend.env':{'DATABASE_ADMIN_URL':f'postgresql+psycopg://ideaflow_migrator:{db}@postgres:5432/ideaflow','DATABASE_URL':f'postgresql+psycopg://ideaflow_app:{app_db}@postgres:5432/ideaflow','APP_DB_PASSWORD':app_db,'ADMIN_EMAIL':os.environ['IDEAFLOW-VPS-ADMIN-EMAIL'],'ADMIN_PASSWORD':os.environ['IDEAFLOW-VPS-ADMIN-PASSWORD'],'APP_TIMEZONE':os.environ['IDEAFLOW-VPS-TIMEZONE'],'APP_ORIGIN':os.environ['IDEAFLOW-VPS-URL'],'SESSION_COOKIE_NAME':'__Host-ideaflow_session','SESSION_COOKIE_SECURE':'true'}
            }
            with client.open_sftp() as sftp:
                for name,env in values.items():
                    if any('\n' in value or '\r' in value for value in env.values()):raise ValueError('Multiline environment values are unsupported')
                    with sftp.open(base+'/'+name,'w') as target:target.write(''.join(f'{key}={value}\n' for key,value in env.items()))
                    sftp.chmod(base+'/'+name,0o600)
            print('Protected VPS environment files written; credential values withheld.')
        elif args.action=='account-password':
            # Password crosses the encrypted channel on stdin, never in argv.
            run(client,'chpasswd',sudo=True,input_data='ideaflow:'+os.environ['IDEAFLOW-VPS-COCKPIT-PASSWORD']+'\n')
            print('Dedicated application Cockpit password installed.')
        elif args.action=='upload-release':
            if not args.command:parser.error('--command (staging directory) is required')
            base=args.command.rstrip('/')
            with client.open_sftp() as sftp:
                for local in sorted(Path('infra/vps').iterdir()):
                    if not local.is_file():continue
                    remote=base+'/'+local.name
                    sftp.put(str(local),remote);sftp.chmod(remote,0o600)
                    checksum=hashlib.sha256(local.read_bytes()).hexdigest()
                    if run(client,'sha256sum '+shlex.quote(remote),quiet=True).split()[0]!=checksum:raise RuntimeError('Release checksum mismatch')
                for local in sorted(Path('demo').glob('*.json')):
                    sftp.put(str(local),base+'/demo-'+local.name)
            print('Release assets and optional demo files transferred; no demo imported.')
        elif args.action=='download':
            if not args.file or not args.command:parser.error('--file and --command (remote path) are required')
            local=Path(args.file);local.parent.mkdir(parents=True,exist_ok=True)
            if local.exists():raise ValueError('Refusing to overwrite an existing local file')
            with client.open_sftp() as sftp:sftp.get(args.command,str(local))
            with local.open('rb') as source:checksum=hashlib.file_digest(source,'sha256').hexdigest()
            remote=run(client,'sha256sum '+shlex.quote(args.command),quiet=True).split()[0]
            if remote!=checksum:raise RuntimeError('Download checksum mismatch')
            print(f'Downloaded {local.name}; SHA-256 verified {checksum}')
        elif args.action=='cockpit-check':
            channel=client.get_transport().open_channel('direct-tcpip',('127.0.0.1',9090),('127.0.0.1',0))
            connection=http.client.HTTPConnection('127.0.0.1',9090,timeout=20);connection.sock=channel
            credentials=os.environ['IDEAFLOW-VPS-COCKPIT-USERNAME']+':'+os.environ['IDEAFLOW-VPS-COCKPIT-PASSWORD']
            authorization='Basic '+base64.b64encode(credentials.encode()).decode()
            connection.request('GET','/cockpit/login',headers={'Authorization':authorization,'Host':'127.0.0.1:9090'})
            response=connection.getresponse();body=response.read()
            if response.status!=200:raise RuntimeError(f'Cockpit authentication failed: HTTP {response.status}')
            result=json.loads(body)
            if not response.getheader('Set-Cookie'):raise RuntimeError('Cockpit did not issue an authenticated session')
            connection.close()
            print('Cockpit application-account authentication through encrypted SSH channel: PASS')
        elif args.action=='ports-check':
            for port in (8443,18081,8000,5432,9090,2019):
                try:
                    with socket.create_connection((HOST,port),timeout=3):reachable=True
                except OSError:reachable=False
                if reachable!=(port==8443):raise RuntimeError(f'Unexpected public reachability: port {port}, reachable={reachable}')
                print(f'Public TCP {port}: '+('reachable' if reachable else 'inaccessible'))
        elif args.action=='stack':
            if args.command not in ('start','stop','status','backup'):parser.error('--command must be start, stop, status or backup')
            command={'start':'systemctl --user start app-ideaflow.target','stop':'systemctl --user stop app-ideaflow.target ideaflow-frontend.service ideaflow-backend.service ideaflow-postgres.service','status':'systemctl --user status app-ideaflow.target --no-pager; podman ps; systemctl --user list-timers ideaflow-backup.timer --no-pager','backup':'systemctl --user start ideaflow-backup.service; ls -lt /home/ideaflow/backups/*.dump'}[args.command]
            run(client,'cd /home/ideaflow; uid=$(id -u ideaflow); runuser -u ideaflow -- env XDG_RUNTIME_DIR=/run/user/$uid sh -c '+shlex.quote(command),sudo=True)
        elif args.action=='app-check':
            import urllib.request
            base=os.environ['IDEAFLOW-VPS-URL']
            jar=http.cookiejar.CookieJar();opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
            data=json.dumps({'email':os.environ['IDEAFLOW-VPS-ADMIN-EMAIL'],'password':os.environ['IDEAFLOW-VPS-ADMIN-PASSWORD']}).encode()
            request=urllib.request.Request(base+'/api/v1/session/login',data=data,headers={'Content-Type':'application/json','Origin':base})
            with opener.open(request,timeout=20) as response:login=json.load(response)
            assert login['user']['role']=='Admin'
            assert any(cookie.name=='__Host-ideaflow_session' and cookie.secure for cookie in jar)
            for path in ('/api/health/ready','/api/v1/session/me','/api/v1/ideas?page_size=100','/api/v1/dashboards/portfolio','/api/v1/dashboards/value','/api/v1/dashboards/process'):
                with opener.open(base+path,timeout=20) as response:result=json.load(response)
                print(f'HTTPS {path}: PASS'+(f" ({result['total']} ideas)" if 'total' in result else ''))
            # Login creates an ordinary expiring session; no business writes.
            print('Existing Admin credentials and Secure session after reboot: PASS')
        else:parser.error('Unknown action')

if __name__=='__main__':main()
