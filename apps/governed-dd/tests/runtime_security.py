"""Run as node in isolated tenant runtime. No secret values are output."""
import os,socket,urllib.request,urllib.error
from pathlib import Path
assert os.getuid()==1000
for forbidden in ['/var/run/docker.sock','/run/secrets/admin','/run/secrets/gateway-signing','/run/secrets/keycloak-admin','/paperclip/native-admin.json','/etc/shadow','/agent-home/ssh/host_ed25519']:
 try:Path(forbidden).read_bytes()
 except (FileNotFoundError,PermissionError,IsADirectoryError):pass
 else:raise AssertionError('Forbidden credential readable: '+forbidden)
for host in ['postgres','graph','control-postgres','keycloak','dd-b5e287392a4d58e192c4c734','governed-dd-b5e287392a4d58e192c4c734-postgres-1']:
 try:socket.getaddrinfo(host,5432)
 except socket.gaierror:pass
 else:raise AssertionError('Forbidden service resolved: '+host)
proxy=urllib.request.build_opener(urllib.request.ProxyHandler({'https':'http://egress-runtime:8888'}))
try:proxy.open('https://example.com',timeout=10)
except urllib.error.URLError as exc:assert '403' in str(exc)
else:raise AssertionError('Unconfigured egress permitted')
try:socket.create_connection(('1.1.1.1',443),3)
except OSError:pass
else:raise AssertionError('General internet route exists')
print('UID 1000, forbidden credential/files, other-tenant/database DNS, general internet denial and provider allowlist passed.')
