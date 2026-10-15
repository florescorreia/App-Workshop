import json
from sqlalchemy import select
from .db import SessionLocal,now
from .models import Idea,IdeaEvent,DemoBatch
from .process import discover
from .queries import value_dashboard
from .domain import LIFECYCLE
from .vave_models import Case

def main():
    with SessionLocal() as db:
        cases=list(db.scalars(select(Case)));vave_ids={c.idea_id for c in cases}
        ideas=[i for i in db.scalars(select(Idea)) if i.id not in vave_ids];events=list(db.scalars(select(IdeaEvent)))
        for case in cases:
            state=(0,'Draft')
            trace=sorted([e for e in events if e.idea_id==case.idea_id and e.event_type.startswith('VAVE_')],key=lambda e:e.sequence)
            assert trace and trace[0].event_type in ('VAVE_CAPTURED','VAVE_ADOPTED')
            for e in trace:
                after=e.changes.get('after')
                if isinstance(after,dict) and 'maturity' in after and 'status' in after: state=(after['maturity'],after['status'])
            assert state==(case.maturity,case.status),'VAVE maturity/status must match immutable decisions'
        for idea in ideas:
            trace=sorted([e for e in events if e.idea_id==idea.id and e.event_type in LIFECYCLE],key=lambda e:(e.occurred_at,e.sequence,e.id))
            assert (trace[-1].to_stage,trace[-1].to_disposition)==(idea.stage,idea.disposition)
        value=value_dashboard(db,ideas);process=discover(ideas,events,now())
        for b in db.scalars(select(DemoBatch)):
            selected=[i for i in ideas if i.demo_batch_id==b.id]
            proc=discover(selected,[e for e in events if e.idea_id in {i.id for i in selected}],now())
            print(json.dumps({'batch':b.batch_key,'counts':b.counts,'current_replay':'PASS','rework':proc['rework'],
                'completed_stage_medians':{s['stage']:s['median'] for s in proc['stages']}},default=str))
        print(json.dumps({'ideas':len(ideas),'vave_cases':len(cases),'vave_replay':'PASS','events':len(events),'coverage':value['coverage'],'planned_net':value['planned']['net_benefit'],
            'actual_net':value['actual']['net_benefit'],'verified_net':value['verified']['net_benefit'],'variants':len(process['variants'])},default=str))
if __name__=='__main__':main()
