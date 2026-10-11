"""Explicit synthetic ingestion benchmark inside one acceptance tenant."""
import time
from domain import Domain
d=Domain();data=('FICTIONAL ingestion benchmark; revenue reported in USD.\n'*20000).encode()
source=d.upload(data,'fictional-benchmark.txt','text/plain',{'access_limitations':'Synthetic benchmark','batch':'benchmark-v1'},'test:benchmark','benchmark-source-v1')
start=time.monotonic();job=d.ingest({'id':str(source['id']),'version':source['version']})
if job['status'] in ('pending','failed'):d.process_job(job)
with d.connect() as db:
 row=db.execute('SELECT status FROM jobs WHERE id=%s',(job['id'],)).fetchone()
 count=db.execute('SELECT count(*) AS n FROM chunks WHERE source_id=%s',(source['id'],)).fetchone()['n']
assert row['status'] in ('extracted','indexed')
print({'bytes':len(data),'seconds':round(time.monotonic()-start,3),'chunks':count,'dense':False,'first_ingestion':job['status'] in ('pending','failed')})
