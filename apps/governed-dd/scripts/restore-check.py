"""Read-only recovery checks on restored volumes, never against live volumes."""
import hashlib,json,os,time
from pathlib import Path
import psycopg
from psycopg.rows import dict_row

config=Path('/configuration')
for label,host in [('control','restore-control'),('a','restore-a'),('b','restore-b')]:
    credential='db-admin' if label=='control' else os.environ['TENANT_'+label.upper()]+'-admin'
    password=(config/'local/secrets'/credential).read_text().strip()
    for attempt in range(30):
        try:
            db=psycopg.connect(host=host,user='postgres',password=password,dbname='portal' if label=='control' else 'dd',row_factory=dict_row);break
        except psycopg.OperationalError:time.sleep(2)
    else:raise RuntimeError('Restored database unavailable: '+label)
    with db:
        if label=='control':
            assert db.execute('SELECT count(*) AS n FROM tenants').fetchone()['n']==2
            assert db.execute('SELECT count(*) AS n FROM memberships').fetchone()['n']==4
            with psycopg.connect(host=host,user='postgres',password=password,dbname='keycloak') as identity:
                assert identity.execute("SELECT count(*) FROM user_entity WHERE username IN ('alice','bob','carol')").fetchone()[0]==3
            print('Restored portal tenants/memberships and Keycloak identities verified.');continue
        rows=db.execute("SELECT id,version,body FROM records WHERE kind IN ('Source','Artifact')").fetchall()
        for row in rows:
            digest=row['body']['hash'];data=(Path('/artifacts')/label/digest[:2]/digest).read_bytes()
            assert hashlib.sha256(data).hexdigest()==digest
            assert len(data)==row['body']['size']
        assert db.execute('SELECT count(*) AS n FROM chunks').fetchone()['n']>=1
        assert not db.execute('SELECT c.id FROM chunks c LEFT JOIN records r ON r.id=c.source_id AND r.version=c.source_version WHERE r.id IS NULL').fetchall()
        assert db.execute("SELECT count(*) AS n FROM pg_extension WHERE extname IN ('vector','pg_search')").fetchone()['n']==2
        print('Restored '+label+': '+str(len(rows))+' immutable source/artifact hashes, extraction lineage and required extensions verified.')
