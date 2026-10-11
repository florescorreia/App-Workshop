import socket
from pathlib import Path
import httpx
from domain import Domain
d=Domain()
token=Path('/run/secrets/agent').read_text().strip()
with httpx.Client(base_url='http://localhost:8000') as client:
 assert client.get('/api/records').status_code==404
 assert client.get('/api/records',headers={'Authorization':'Bearer '+token}).status_code==200
 assert client.post('/api/reviews',headers={'Authorization':'Bearer '+token},json={'reference':{'id':str(d.list('Source')[0]['id']),'version':1},'decision':'accept','report':'test'}).status_code==422
other='b5e287392a4d58e192c4c734' if d.tenant.startswith('a') else 'a4e176281f3c47d081b3b623'
for name in [f'governed-dd-{other}-postgres-1',f'dd-{other}',f'governed-dd-{other}-graph-1']:
 try:socket.getaddrinfo(name,5432)
 except socket.gaierror:pass
 else:raise AssertionError('Other tenant DNS resolved')
assert not Path('/var/run/docker.sock').exists()
print('Service token authorization, agent publication rejection, other-tenant DNS denial and absent engine socket passed.')
