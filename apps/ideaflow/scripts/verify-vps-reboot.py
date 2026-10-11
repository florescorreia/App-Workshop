"""Read-only reboot comparison, including sessions and reference sequence."""
import argparse, hashlib, json, os
from sqlalchemy import create_engine, text

p=argparse.ArgumentParser()
p.add_argument('--expected')
p.add_argument('--output',required=True)
args=p.parse_args()
engine=create_engine(os.environ['DATABASE_ADMIN_URL'])
with engine.connect().execution_options(isolation_level='REPEATABLE READ') as connection:
    with connection.begin():
        connection.execute(text('SET TRANSACTION READ ONLY'))
        names=connection.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")).scalars().all()
        tables={}
        for name in names:
            quoted=engine.dialect.identifier_preparer.quote(name)
            rows=connection.execute(text(f'SELECT row_to_json(t)::text FROM {quoted} t')).scalars().all()
            tables[name]={'count':len(rows),'sha256':hashlib.sha256('\n'.join(sorted(rows)).encode()).hexdigest()}
        sequence=dict(connection.execute(text('SELECT last_value,is_called FROM idea_reference_seq')).mappings().one())
        accounts=[dict(row) for row in connection.execute(text('SELECT id,role,active,deleted_at FROM app_user ORDER BY id')).mappings()]
        report={'tables':tables,'reference_sequence':sequence,'accounts':accounts}
if args.expected:
    expected=json.load(open(args.expected))
    assert json.loads(json.dumps(report,default=str))==expected,'Database records, sessions or reference sequence changed across reboot'
with open(args.output,'w') as target:json.dump(report,target,indent=2,default=str)
print(json.dumps({'verification':'PASS','counts':{name:data['count'] for name,data in tables.items()},'reference_sequence':sequence,'compared':bool(args.expected)},indent=2))
