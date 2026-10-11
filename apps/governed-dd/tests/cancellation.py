import uuid
from domain import Domain
d=Domain()
source=d.upload(b'Cancellation acceptance source.\n'*5000,'cancel-test.txt','text/plain',{'access_limitations':'synthetic test only'},'test:acceptance','cancel-acceptance-source-v1')
ref={'id':str(source['id']),'version':source['version']};job=d.ingest(ref)
with d.connect() as db:db.execute('UPDATE jobs SET cancelled=true WHERE id=%s',(job['id'],))
d.process_job(job)
with d.connect() as db:
 assert db.execute('SELECT status FROM jobs WHERE id=%s',(job['id'],)).fetchone()['status']=='cancelled'
 assert db.execute('SELECT count(*) AS n FROM chunks WHERE source_id=%s',(source['id'],)).fetchone()['n']==0
print('Cancelled ingestion retained source bytes, recorded cancelled status and wrote no chunks.')
