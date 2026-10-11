"""Read-only restored canonical/file verification in a tooling container."""
import hashlib
from pathlib import Path
import psycopg
from psycopg.rows import dict_row

for host,folder in [('restore-a','a'),('restore-b','b')]:
 with psycopg.connect(f'postgresql://postgres@{host}/dd',row_factory=dict_row) as db:
  records=db.execute("SELECT id,version,kind,body FROM records WHERE kind IN ('Source','Artifact')").fetchall()
  for row in records:
   digest=row['body']['hash'];data=(Path('/volumes')/folder/'data'/digest[:2]/digest).read_bytes()
   assert hashlib.sha256(data).hexdigest()==digest
   assert len(data)==row['body']['size']
  assert db.execute('SELECT count(*) FROM chunks').fetchone()['count']==1
  assert not db.execute('SELECT c.id FROM chunks c LEFT JOIN records r ON r.id=c.source_id AND r.version=c.source_version WHERE r.id IS NULL').fetchall()
 print(host,'source/artifact bytes and canonical extraction lineage verified')
