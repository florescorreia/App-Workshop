"""Read-only whole-stack recovery, real auth/config, graphs and original bytes."""
import time,json,os,hashlib,subprocess
from pathlib import Path
import httpx,psycopg
from psycopg.rows import dict_row
A='a4e176281f3c47d081b3b623';B='b5e287392a4d58e192c4c734'
with httpx.Client(timeout=20) as client:
 for host,port,path in [('portal',8000,'/health'),('keycloak',8080,'/identity/realms/governed-dd/.well-known/openid-configuration')]:
  for attempt in range(60):
   try:
    r=client.get(f'http://{host}:{port}{path}')
    if r.status_code==200:break
   except httpx.HTTPError:pass
   time.sleep(2)
  else:raise AssertionError('Restored health failed '+host)
 print('Restored control database/portal and real Keycloak realm discovery passed.')
 for tenant,label in [(A,'a'),(B,'b')]:
  secret=Path('/configuration/local/secrets/'+tenant+'-agent').read_text().strip()
  for attempt in range(30):
   try:
    r=client.get('http://dd-'+tenant+':8000/api/records',headers={'Authorization':'Bearer '+secret})
    if r.status_code==200:break
   except httpx.HTTPError:pass
   time.sleep(2)
  else:raise AssertionError('Restored governance failed '+label)
  records=r.json();assert records
  sources=[r for r in records if r['kind']=='Source'];assert sources
  row=sources[0]
  bytes_=client.get(f'http://dd-{tenant}:8000/api/bytes/'+row['id']+'/'+str(row['version']),headers={'Authorization':'Bearer '+secret})
  assert bytes_.status_code==200 and hashlib.sha256(bytes_.content).hexdigest()==row['body']['hash']
  search=client.get(f'http://dd-{tenant}:8000/api/search',params={'q':'revenue','dense':'false'},headers={'Authorization':'Bearer '+secret});assert search.status_code==200 and search.json()['hits']
  finding=next(r for r in records if r['kind']=='Finding')
  graph=client.get(f'http://dd-{tenant}:8000/api/graph',params={'key':finding['id']+':'+str(finding['version'])},headers={'Authorization':'Bearer '+secret});assert graph.status_code==200 and graph.json()['edges']
  credential=json.loads(Path('/native/'+label+'/native-'+('alice' if label=='a' else 'bob')+'.json').read_text())
  origin=f'http://paperclip-{tenant}.localhost:8081'
  with httpx.Client(base_url=f'http://paperclip-{tenant}:3100',timeout=20,headers={'Origin':origin,'Host':origin.removeprefix('http://')}) as native:
   login=native.post('/api/auth/sign-in/email',json={'email':credential['email'],'password':credential['password']});assert login.status_code==200
   assert native.get('/api/companies').status_code==200
  print('Restored '+label+': registry, authorized source hash, real BM25, graph paths and native consultant login passed.')
assert (Path('/ontology/a/.git')).exists()
assert list(Path('/workspace/a').rglob('analysis.py'))
print('Restored tenant ontology Git and analytical code/workspace persisted. No real model rerun in restore copy.')
