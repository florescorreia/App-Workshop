"""Import evidence only: hashed snapshots and read-only checks; run in backend."""
import argparse
import hashlib
import json
import os
from collections import Counter
from decimal import Decimal as D
from sqlalchemy import create_engine, select, text
import httpx
from app.db import Base, SessionLocal, now
from app import models as M
from app.financial import app_today
from app.domain import LIFECYCLE, EDGES
from app.queries import value_dashboard

KEY='harborworks-demo-v2'
TABLES=['idea','idea_event','financial_plan','financial_plan_period','value_period','task','comment','demo_batch','app_user','site','category']

def snapshot():
    engine=create_engine(os.environ['DATABASE_ADMIN_URL']); result={}
    with engine.connect() as c:
        for name in TABLES:
            pk=[col.name for col in Base.metadata.tables[name].primary_key]
            rows=c.execute(text(f'SELECT row_to_json(t)::text FROM {name} t')).scalars()
            result[name]={}
            for raw in rows:
                row=json.loads(raw);key=json.dumps([row[k] for k in pk])
                result[name][key]=hashlib.sha256(raw.encode()).hexdigest()
    engine.dispose();return result

def verify(before,current):
    with SessionLocal() as db, httpx.Client(base_url='http://localhost:8000/api/v1',timeout=30) as c:
        login=c.post('/session/login',json={'email':os.environ['ADMIN_EMAIL'],'password':os.environ['ADMIN_PASSWORD']});login.raise_for_status()
        def get(path):
            r=c.get(path);r.raise_for_status();return r.json()
        batch=db.scalar(select(M.DemoBatch).where(M.DemoBatch.batch_key==KEY))
        assert batch and batch.seed==84
        ideas=list(db.scalars(select(M.Idea).where(M.Idea.demo_batch_id==batch.id)));ids={i.id for i in ideas}
        events=list(db.scalars(select(M.IdeaEvent).where(M.IdeaEvent.idea_id.in_(ids))))
        assert len(ideas)==12
        assert Counter(i.stage for i in ideas)=={'New':6,'Screening':3,'Analysis':2,'Implementation':1}
        assert Counter(i.category_id for i in ideas)=={'Procurement':3,'Freight':3,'Energy':2,'Scrap/Quality':2,'Productivity':2}
        assert Counter(i.site_id for i in ideas)=={'Tampa':4,'Atlanta':4,'Dallas':4}
        assert all(i.disposition=='Active' for i in ideas)
        for idea in ideas:
            trace=sorted([e for e in events if e.idea_id==idea.id],key=lambda e:(e.occurred_at,e.sequence,e.id))
            assert [e.sequence for e in trace]==list(range(1,len(trace)+1))
            assert all(e.occurred_at<=now() and e.provenance['fictional'] and e.provenance['batch_key']==KEY for e in trace)
            life=[e for e in trace if e.event_type in LIFECYCLE]
            assert (life[-1].to_stage,life[-1].to_disposition)==(idea.stage,idea.disposition)
            assert all((e.from_stage,e.to_stage) in EDGES for e in life if e.event_type=='STAGE_CHANGED')
            if idea.stage!='Implementation':
                assert not db.scalar(select(M.FinancialPlan).where(M.FinancialPlan.idea_id==idea.id,M.FinancialPlan.status=='Approved'))
                assert not db.scalar(select(M.ValuePeriod).where(M.ValuePeriod.idea_id==idea.id))
        hero=next(i for i in ideas if i.stage=='Implementation');detail=get('/ideas/'+hero.id)
        approved=next(p for p in detail['plans'] if p['status']=='Approved');periods={p['month']:p for p in approved['periods']}
        assert len(periods)==18 and sum(D(p['spend']) for p in periods.values())==D('12000')
        assert len(detail['tasks'])==2 and detail['progress']==65 and detail['actual_start']=='2026-08-01'
        results=detail['results'];assert len(results)==2
        for r in results:
            assert r['month']<app_today().replace(day=1).isoformat()
            assert D(r['gross'])<D(periods[r['month']]['gross'])
            assert D(r['gross'])-D(r['recurring'])<D(periods[r['month']]['gross'])-D(periods[r['month']]['recurring'])
        assert results[0]['verified_at'] and results[-1]['verified_at'] is None
        portfolio=get('/dashboards/portfolio');value=get('/dashboards/value');process=get('/dashboards/process');register=get('/ideas?page_size=100')
        assert register['total']==len(current['idea'])==len(before['idea'])+12
        assert process['case_count']==register['total'] and sum(v['case_count'] for v in process['variants'])==register['total']
        stage_counts=Counter(i.stage for i in db.scalars(select(M.Idea)))
        assert {s['stage']:s['count'] for s in portfolio['stages']}==dict(stage_counts)
        assert len(get('/ideas?ids='+','.join(ids)+'&page_size=100')['items'])==12
        all_ideas=list(db.scalars(select(M.Idea)));old=[i for i in all_ideas if i.id not in ids]
        oldvalue=value_dashboard(db,old);batchvalue=value_dashboard(db,ideas)
        for label in ('planned','actual','verified'):
            for metric in ('net_benefit','implementation_spend','net_cash_flow'):
                assert abs(D(str(value[label][metric]))-(oldvalue[label][metric] or D(0))-(batchvalue[label][metric] or D(0)))<D('.000001')
        for k in ('eligible','reported','verified'):
            assert value['coverage'][k]==oldvalue['coverage'][k]+batchvalue['coverage'][k]
        assert batchvalue['planned']['net_benefit']==D('46750.00')
        assert batchvalue['actual']['net_benefit']==D('10150.00')
        assert batchvalue['verified']['net_benefit']==D('3700.00')
        assert batchvalue['coverage']=={'eligible':2,'reported':2,'verified':1}
        report={'status':'PASS','batch_key':KEY,'seed':batch.seed,'anchor_date':batch.anchor_date,'counts':batch.counts,
                'total_ideas':register['total'],'total_events':len(current['idea_event']),'stages':dict(Counter(i.stage for i in ideas)),
                'categories':dict(Counter(i.category_id for i in ideas)),'sites':dict(Counter(i.site_id for i in ideas)),
                'records':[{'id':i.id,'reference':i.reference,'title':i.title,'stage':i.stage,'category':i.category_id,'site':i.site_id,'owner_id':i.owner_id} for i in sorted(ideas,key=lambda i:i.reference)],
                'implementation':{'id':hero.id,'reference':hero.reference,'results':results,'periods':list(periods.values()),'tasks':detail['tasks']},
                'batch_value':batchvalue,'portfolio_value':value,'process_cases':process['case_count'],
                'checks':['all existing rows preserved','contiguous event sequences and lifecycle replay','exact category/stage/site mix','only Implementation approved/reported','two below-plan elapsed results/latest unverified','register/board counts','process cases/variants','value additions and coverage']}
        json.dump(report,open('/handover/harborworks-v2-verification.json','w'),default=str,indent=2)
        print(json.dumps({k:report[k] for k in ('status','counts','total_ideas','total_events','checks')},indent=2))

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['snapshot','unchanged','preserved','verify']);p.add_argument('--file',required=True);args=p.parse_args()
    current=snapshot()
    if args.action=='snapshot':
        if os.path.exists(args.file):raise ValueError('Snapshot already exists; preserve evidence')
        json.dump(current,open(args.file,'x'),indent=2);print({k:len(v) for k,v in current.items()});return
    before=json.load(open(args.file))
    if args.action=='unchanged':assert current==before;print('All row fingerprints unchanged: PASS');return
    for table,rows in before.items():
        assert all(current[table].get(key)==digest for key,digest in rows.items()),'Existing rows changed: '+table
    print('Every pre-existing business/reference/user row preserved: PASS')
    if args.action=='verify':verify(before,current)
    assert snapshot()==current,'Verification changed business data'

if __name__=='__main__':main()
