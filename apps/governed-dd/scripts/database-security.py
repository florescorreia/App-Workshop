"""Transient administrator migration: isolate database owners from serving roles."""
import os
from pathlib import Path
import psycopg
from psycopg import sql
tenant=os.environ['TENANT_ID'];password=Path('/run/secrets/admin').read_text().strip()
with psycopg.connect(host='postgres',dbname='dd',user='postgres',password=password) as db:
 db.execute("DO $$ BEGIN CREATE ROLE dd_owner NOLOGIN; EXCEPTION WHEN duplicate_object THEN NULL; END $$")
 db.execute('ALTER DATABASE dd OWNER TO dd_owner')
 db.execute('ALTER SCHEMA public OWNER TO dd_owner')
 for row in db.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'").fetchall():db.execute(sql.SQL('ALTER TABLE {} OWNER TO dd_owner').format(sql.Identifier(row[0])))
 for row in db.execute("SELECT sequencename FROM pg_sequences WHERE schemaname='public'").fetchall():db.execute(sql.SQL('ALTER SEQUENCE {} OWNER TO dd_owner').format(sql.Identifier(row[0])))
 db.execute('REVOKE ALL ON SCHEMA public FROM PUBLIC,dd')
 db.execute('GRANT USAGE ON SCHEMA public TO dd')
 db.execute('REVOKE ALL ON ALL TABLES IN SCHEMA public FROM dd')
 db.execute('GRANT SELECT ON ALL TABLES IN SCHEMA public TO dd')
 db.execute('GRANT INSERT ON records,requests,audit,outbox,chunks,jobs,ontology_versions TO dd')
 db.execute('GRANT UPDATE ON jobs,chunks,outbox TO dd')
 db.execute('GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA public TO dd')
 db.execute('REVOKE CREATE ON DATABASE dd FROM dd')
 db.execute('GRANT CONNECT ON DATABASE dd TO dd')
print('Serving DD role can append canonical records/audit; cannot alter schemas or update/delete canonical versions.')
