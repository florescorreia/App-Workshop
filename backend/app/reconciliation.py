import json
from sqlalchemy import select
from .db import SessionLocal,now
from .models import Idea,IdeaEvent,DemoBatch
from .process import discover
from .queries import value_dashboard
from .domain import LIFECYCLE

def main():
    with SessionLocal() as db:
        ideas=list(db.scalars(select(Idea)));events=list(db.scalars(select(IdeaEvent)))
        for idea in ideas:
            trace=sorted([e for e in events if e.idea_id==idea.id and e.event_type in LIFECYCLE],key=lambda e:(e.occurred_at,e.sequence,e.id))
            assert (trace[-1].to_stage,trace[-1].to_disposition)==(idea.stage,idea.disposition)
        value=value_dashboard(db,ideas);process=discover(ideas,events,now())
        for b in db.scalars(select(DemoBatch)):
            selected=[i for i in ideas if i.demo_batch_id==b.id]
            proc=discover(selected,[e for e in events if e.idea_id in {i.id for i in selected}],now())
            print(json.dumps({'batch':b.batch_key,'counts':b.counts,'current_replay':'PASS','rework':proc['rework'],
                'completed_stage_medians':{s['stage']:s['median'] for s in proc['stages']}},default=str))
        print(json.dumps({'ideas':len(ideas),'events':len(events),'coverage':value['coverage'],'planned_net':value['planned']['net_benefit'],
            'actual_net':value['actual']['net_benefit'],'verified_net':value['verified']['net_benefit'],'variants':len(process['variants'])},default=str))
if __name__=='__main__':main()
