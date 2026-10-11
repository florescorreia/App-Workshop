"""Run in control portal with read-only mounts of explicit acceptance tenant tokens."""
import httpx
from pathlib import Path
A='a4e176281f3c47d081b3b623';B='b5e287392a4d58e192c4c734'
tokens={t:Path('/vector-check/'+t).read_text().strip() for t in (A,B)}
for tenant,other in ((A,B),(B,A)):
 url='http://dd-'+tenant+':8000/api/search'
 with httpx.Client(timeout=60) as client:
  assert client.get(url,params={'q':'revenue','dense':'true'}).status_code==404
  assert client.get(url,params={'q':'revenue','dense':'true'},headers={'Authorization':'Bearer '+tokens[other]}).status_code==404
  r=client.get(url,params={'q':'revenue','dense':'true','tenant':other},headers={'Authorization':'Bearer '+tokens[tenant]})
  assert r.status_code==200 and r.json()['ranking_counts']['dense']>0
  assert r.json()['mode']=='hybrid'
print('Both tenant dense APIs deny missing/other-tenant credentials; supplied tenant override cannot change binding.')
