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
