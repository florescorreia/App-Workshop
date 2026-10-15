"""Private repeatable-read snapshot; compare preexisting rows after additive upgrade."""
import argparse, hashlib, json, os
from sqlalchemy import create_engine, text
parser=argparse.ArgumentParser()
parser.add_argument('--output',required=True)
parser.add_argument('--expected')
parser.add_argument('--database')
parser.add_argument('--upgrade',action='store_true')
parser.add_argument('--adoption',action='store_true')
args=parser.parse_args()
engine=create_engine(os.environ['DATABASE_ADMIN_URL'])
if args.database: engine=create_engine(engine.url.set(database=args.database))
with engine.connect().execution_options(isolation_level='REPEATABLE READ') as c:
    with c.begin():
        c.execute(text('SET TRANSACTION READ ONLY'))
        names=c.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")).scalars().all()
        tables={}
        for name in names:
            quote=engine.dialect.identifier_preparer.quote(name)
            rows=c.execute(text(f'SELECT row_to_json(t)::text FROM {quote} t')).scalars().all()
            tables[name]={'count':len(rows),'sha256':hashlib.sha256('\n'.join(sorted(rows)).encode()).hexdigest()}
        report={'tables':tables,'sequence':dict(c.execute(text('SELECT last_value,is_called FROM idea_reference_seq')).mappings().one())}
        if args.adoption:
            def digest(row): return hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest()
            permitted={'title','problem','solution','owner_id','record_version','updated_at'}
            ideas=c.execute(text('SELECT row_to_json(t)::text FROM idea t')).scalars().all()
            events=c.execute(text('SELECT row_to_json(t)::text FROM idea_event t')).scalars().all()
            report['adoption']={'ideas':{r['id']:digest({k:v for k,v in r.items() if k not in permitted}) for r in map(json.loads,ideas)},'events':{r['id']:digest(r) for r in map(json.loads,events)}}
if args.expected:
    expected=json.load(open(args.expected))
    for name,value in expected['tables'].items():
        if args.adoption and (name.startswith('vave_') or name in ('idea','idea_event','app_session')): continue
        if args.upgrade and name=='alembic_version': continue
        assert report['tables'][name]==value, 'Preservation mismatch: '+name
    assert report['sequence']==expected['sequence'],'Readable sequence changed'
    if args.adoption:
        assert report['adoption']['ideas']==expected['adoption']['ideas'],'Existing identity/lifecycle fields changed'
        for id,digest in expected['adoption']['events'].items(): assert report['adoption']['events'].get(id)==digest,'Original event changed'
    if not args.upgrade: assert set(report['tables'])==set(expected['tables'])
    else:
        for name in set(report['tables'])-set(expected['tables']): assert report['tables'][name]['count']==0,'Unexpected automatic data creation: '+name
with open(args.output,'w') as f: json.dump(report,f,indent=2)
print(json.dumps({'verification':'PASS','counts':{k:v['count'] for k,v in tables.items()},'compared':bool(args.expected),'additive_upgrade':args.upgrade}))
