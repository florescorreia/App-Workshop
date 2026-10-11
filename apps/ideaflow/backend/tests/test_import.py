import json, uuid
from sqlalchemy import select, func
from app.demo import built_in, import_dataset, DemoDataset
from app.models import User, Idea, IdeaEvent, DemoBatch, ValuePeriod
from app.financial import app_today
from app.queries import value_dashboard
from app.process import discover
from app.db import now

def test_additive_idempotent_replay_and_coverage(db,tmp_path,monkeypatch):
    monkeypatch.setenv('DEMO_HANDOVER_DIR',str(tmp_path))
    admin=db.scalar(select(User).where(User.role=='Admin'))
    key='test-'+uuid.uuid4().hex;dataset=built_in(key)
    before=db.scalar(select(func.count()).select_from(Idea))
    preview=import_dataset(db,admin,dataset,True)
    assert preview['counts']['ideas']==60
    assert db.scalar(select(func.count()).select_from(Idea))==before
    report=import_dataset(db,admin,dataset,False)
    assert report['counts']['ideas']==60
    repeat=import_dataset(db,admin,built_in(key,42,app_today()),False)
    assert repeat['no_op'] and db.scalar(select(func.count()).select_from(Idea))==before+60
    second=DemoDataset.model_validate_json(open('/demo/example.json',encoding='utf-8').read())
    second.batch_key='test-second-'+uuid.uuid4().hex;second.ideas[0].external_key=second.batch_key+':1'
    import_dataset(db,admin,second,False)
    assert db.scalar(select(func.count()).select_from(Idea))==before+61
    batch=db.scalar(select(DemoBatch).where(DemoBatch.batch_key==key))
    ideas=list(db.scalars(select(Idea).where(Idea.demo_batch_id==batch.id)))
    events=list(db.scalars(select(IdeaEvent).where(IdeaEvent.idea_id.in_([i.id for i in ideas]))))
    for idea in ideas:
        trace=sorted([e for e in events if e.idea_id==idea.id and e.event_type in {'CREATED','STAGE_CHANGED','HELD','RESUMED','REJECTED','CANCELLED'}],key=lambda e:(e.occurred_at,e.sequence,e.id))
        assert (trace[-1].to_stage,trace[-1].to_disposition)==(idea.stage,idea.disposition)
    assert sum(i.stage=='Realized' for i in ideas)==12
    assert sum(i.disposition=='On hold' for i in ideas)>=5
    assert sum(i.disposition=='Rejected' for i in ideas)==6 and sum(i.disposition=='Cancelled' for i in ideas)==3
    process=discover(ideas,events,now())
    assert process['rework']['numerator']>=8
    analysis=next(s for s in process['stages'] if s['stage']=='Analysis')
    assert analysis['count']>=5
    assert analysis['median']>next(s for s in process['stages'] if s['stage']=='Approved')['median']
    assert sum(i.disposition=='Active' and i.stage!='Realized' and i.expected_finish and i.expected_finish<app_today() for i in ideas)>=6
    value=value_dashboard(db,ideas)
    assert value['coverage']['reported']<value['coverage']['eligible']
    assert value['coverage']['verified']<value['coverage']['reported']
    assert value['expected_reported_cohort'] is not None
    assert any(r['actual'] is None for r in value['variance'])
    assert all(e.provenance['fictional'] for e in events)
