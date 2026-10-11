"""Explicit additive ontology approval and typed relation acceptance check."""
import copy,uuid
from domain import Domain,Invalid
d=Domain()
with d.connect() as db:original=db.execute('SELECT document FROM ontology_versions ORDER BY version DESC LIMIT 1').fetchone()['document']
document=copy.deepcopy(original);document['relations']['TEST_SUPPORTS']={'from':['Source'],'to':['Finding'],'evidence':True}
proposal=d.ontology(document,'agent:analyst');assert proposal['state']=='proposal'
try:d.ontology(document,'agent:analyst',True,'owner')
except Invalid:pass
else:raise AssertionError('Agent approved ontology')
source=next(r for r in d.list('Source') if r['body']['filename'].endswith('.txt'))
finding=d.list('Finding')[0];run=finding['body']['run']
with d.connect() as db:chunk=db.execute('SELECT locator FROM chunks WHERE source_id=%s AND source_version=%s LIMIT 1',(source['id'],source['version'])).fetchone()
ref=lambda r:{'id':str(r['id']),'version':r['version']}
relation={'relation':'TEST_SUPPORTS','from':ref(source),'to':ref(finding),'evidence':[dict(ref(source),locator=chunk['locator'])],'run':run}
if 'TEST_SUPPORTS' not in original['relations']:
 try:d.write('Relation',relation,'agent:analyst',str(uuid.uuid4()))
 except Invalid:pass
 else:raise AssertionError('Unapproved relation ingested')
approved=d.ontology(document,'test:owner',True,'owner');assert approved['state']=='approved'
assert d.ontology(document,'test:owner',True,'owner')['version']==approved['version']
row=d.write('Relation',relation,'test:acceptance','ontology-typed-relation-v1');d.project()
assert any(e['type']=='TEST_SUPPORTS' for e in d.graph(str(source['id'])+':'+str(source['version']),relation='TEST_SUPPORTS')['edges'])
relation['from']=ref(finding)
try:d.write('Relation',relation,'test:acceptance',str(uuid.uuid4()))
except Invalid:pass
else:raise AssertionError('Invalid endpoint accepted')
from pathlib import Path
assert (Path('/ontology')/('v'+str(approved['version'])+'.yaml')).exists()
print('Proposal persistence, owner approval, agent denial, idempotent approval, typed endpoints, graph filter and tenant Git export passed.')
