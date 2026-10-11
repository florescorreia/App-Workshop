"""Run inside one dedicated acceptance tenant. Uses real PostgreSQL/Memgraph."""
import hashlib
import socket
import uuid
from domain import Domain,Invalid

d=Domain()
with d.connect() as db:source=d.get(db.execute("SELECT id,version FROM requests WHERE key='fictional-v1-source'").fetchone(),db)
ref={'id':str(source['id']),'version':source['version']}
assert d.storage.get(source['body']['hash'])
hits=d.search('revenue',dense=False)['hits'];assert hits and hits[0]['score']>0
with d.connect() as db:
 before=db.execute('SELECT count(*) AS n FROM records').fetchone()['n']
assert d.upload(d.storage.get(source['body']['hash']),source['body']['filename'],source['body']['media_type'],{},'test','fictional-v1-source')['id']==source['id']
with d.connect() as db:assert db.execute('SELECT count(*) AS n FROM records').fetchone()['n']==before
try:d.write('Finding',{'claim':'unsupported','implications':'test','evidence':[dict(ref,locator='page:999')],'assumptions':[],'uncertainty':'unknown','run':d.list('Finding')[0]['body']['run']},'test',str(uuid.uuid4()))
except Invalid:pass
else:raise AssertionError('Invalid locator accepted')
try:d.review(ref,'accept','agent:analyst','owner','test')
except Invalid:pass
else:raise AssertionError('Agent publication accepted')
bad=d.write('Deliverable',{'title':'Explicit incomplete acceptance output','findings':[],'artifacts':[],'run':d.list('Finding')[0]['body']['run']},'test:acceptance','incomplete-output-v1')
assert not d.validation({'id':str(bad['id']),'version':1})['valid']
d.project(rebuild=True);d.project()
key=str(d.list('Finding')[0]['id'])+':1'
graph=d.graph(key);assert graph['nodes'] and graph['edges']
with d.graph_driver() as driver,driver.session() as session:
 count=session.run('MATCH (n) RETURN count(n) AS n').single()['n']
d.project(rebuild=True)
with d.graph_driver() as driver,driver.session() as session:assert session.run('MATCH (n) RETURN count(n) AS n').single()['n']==count
with d.connect() as db:
 db.execute('INSERT INTO jobs(id,source_id,version,status,cancelled) VALUES(%s,%s,99,%s,true) ON CONFLICT DO NOTHING',(str(uuid.uuid4()),source['id'],'cancelled'))
fixture_run=next(r for r in d.list('AnalysisRun') if 'calculation' in r['body'])
assert abs(fixture_run['body']['calculation']-20)<1e-10
print('Real BM25, byte hashes, duplicate ingestion, locator validation, incomplete rejection, agent publication denial, graph rebuild/idempotence and deterministic calculation passed.')
