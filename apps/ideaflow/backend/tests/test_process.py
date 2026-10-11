from datetime import datetime,timedelta,timezone,date
from types import SimpleNamespace as NS
from app.process import discover

def test_hold_rework_ties_rejection_and_censoring():
    start=datetime(2026,1,1,tzinfo=timezone.utc);asof=start+timedelta(days=40)
    ideas=[NS(id='a',expected_finish=date(2026,1,20)),NS(id='b',expected_finish=None)]
    rows=[('a',0,'CREATED','New','New','Active',None),('a',2,'STAGE_CHANGED','Screening','Screening','Active','New'),
        ('a',5,'STAGE_CHANGED','Analysis','Analysis','Active','Screening'),('a',8,'HELD','On hold','Analysis','On hold','Analysis'),
        ('a',18,'RESUMED','Resumed','Analysis','Active','Analysis'),('a',25,'STAGE_CHANGED','Screening','Screening','Active','Analysis'),
        ('a',25,'STAGE_CHANGED','Analysis','Analysis','Active','Screening'),('a',26,'COMMENTED','Comment','Analysis','Active',None),
        ('b',1,'CREATED','New','New','Active',None),('b',3,'REJECTED','Rejected','New','Rejected','New')]
    events=[NS(id=str(i),idea_id=id,occurred_at=start+timedelta(days=day),sequence=i,event_type=kind,activity=act,to_stage=stage,to_disposition=disp,from_stage=source) for i,(id,day,kind,act,stage,disp,source) in enumerate(rows)]
    data=discover(ideas,events,asof)
    edge={(e['source'],e['target']):e for e in data['edges']}
    assert edge['Screening','Analysis']['traversals']==2 and edge['Screening','Analysis']['case_count']==1
    assert edge['Analysis','On hold']['median_days']==3
    assert ('Resumed','Screening') in edge and ('New','Rejected') in edge
    assert not any('Comment' in v['path'] for v in data['variants'])
    analysis=[v for v in data['visits'] if v['stage']=='Analysis']
    assert analysis[0]['calendar_days']==20 and analysis[0]['active_days']==10 and analysis[0]['hold_days']==10
    assert analysis[1]['completed'] is False and analysis[1]['calendar_days']==15
    stage=next(s for s in data['stages'] if s['stage']=='Analysis')
    assert stage['count']==1 and stage['median']==20 and stage['open_count']==1 and stage['overdue_count']==1
    assert data['rework']['numerator']==1 and data['rework']['denominator']==2
    assert discover(ideas,events,asof,'active')['stages'][2]['median']==10
    assert discover(ideas,events,asof,completed_only=True)['case_count']==0
