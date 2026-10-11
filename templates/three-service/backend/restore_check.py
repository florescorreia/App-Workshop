"""Compare private database fingerprints without printing record contents."""
import hashlib
import json
import os
from urllib.parse import urlsplit,urlunsplit
import psycopg
from psycopg import sql

def fingerprint(url):
    with psycopg.connect(url) as db:
        db.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        names=[row[0] for row in db.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")]
        result={}
        for name in names:
            rows=[row[0] for row in db.execute(sql.SQL('SELECT to_jsonb(t)::text FROM public.{} t').format(sql.Identifier(name)))]
            result[name]={'count':len(rows),'sha256':hashlib.sha256(json.dumps(sorted(rows)).encode()).hexdigest()}
        return result

if __name__=='__main__':
    live=os.environ['DATABASE_URL']
    restored=urlunsplit(urlsplit(live)._replace(path='/'+os.environ['RESTORE_DATABASE']))
    if fingerprint(live)!=fingerprint(restored):raise RuntimeError('Restore mismatch (avoid concurrent writes during this check)')
    print('Isolated backup/restore: all public table fingerprints match; live data preserved.')
