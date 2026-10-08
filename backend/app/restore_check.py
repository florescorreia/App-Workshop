import argparse, os, hashlib, json
from sqlalchemy import create_engine, text

TABLES=['idea','idea_event','financial_plan','financial_plan_period','value_period','task','comment','demo_batch','app_user']
def fingerprints(engine):
    result={}
    with engine.connect() as c:
        for table in TABLES:
            rows=c.execute(text(f'SELECT row_to_json(t)::text FROM {table} t')).scalars().all()
            result[table]={'count':len(rows),'sha256':hashlib.sha256('\n'.join(sorted(rows)).encode()).hexdigest()}
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument('--database',required=True);args=p.parse_args()
    if not args.database.startswith('ideaflow_restore_') or not args.database[17:].isalnum():raise ValueError('Only isolated restore databases may be checked')
    live=create_engine(os.environ['DATABASE_ADMIN_URL']);restored=create_engine(live.url.set(database=args.database))
    before=fingerprints(live);copy=fingerprints(restored)
    assert before==copy, 'Restored business rows differ from live snapshot (avoid concurrent writes during this check)'
    assert fingerprints(live)==before,'Live database changed during check'
    print(json.dumps({'restore':'PASS','live_unchanged':True,'tables':copy},indent=2))
if __name__=='__main__':main()
