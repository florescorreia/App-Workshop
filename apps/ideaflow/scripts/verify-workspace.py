"""Read-only business fingerprints and lifecycle replay for a copied workspace."""
import argparse, json, os
from collections import Counter
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.models import Idea, IdeaEvent
from app.domain import LIFECYCLE, EDGES
from app.restore_check import fingerprints

p=argparse.ArgumentParser()
p.add_argument('--database')
p.add_argument('--expected')
p.add_argument('--output',required=True)
args=p.parse_args()
engine=create_engine(os.environ['DATABASE_ADMIN_URL'])
if args.database:
    if not args.database.startswith('ideaflow_restore_') or not args.database[17:].isalnum():raise ValueError('Expected an isolated restore database')
    engine=create_engine(engine.url.set(database=args.database))
tables=fingerprints(engine)
if args.expected:
    assert json.load(open(args.expected))['tables']==tables,'Copied business data differs from source snapshot'
with Session(engine) as db:
    ideas=list(db.scalars(select(Idea)))
    for idea in ideas:
        events=list(db.scalars(select(IdeaEvent).where(IdeaEvent.idea_id==idea.id).order_by(IdeaEvent.occurred_at,IdeaEvent.sequence,IdeaEvent.id)))
        assert sorted(e.sequence for e in events)==list(range(1,len(events)+1)),idea.reference
        trace=[e for e in events if e.event_type in LIFECYCLE]
        assert trace and trace[0].activity=='New',idea.reference
        assert (trace[-1].to_stage,trace[-1].to_disposition)==(idea.stage,idea.disposition),idea.reference
        state=('New','Active')
        for event in trace[1:]:
            assert (event.from_stage,event.from_disposition)==state,idea.reference
            if event.event_type=='STAGE_CHANGED':assert (event.from_stage,event.to_stage) in EDGES,idea.reference
            state=(event.to_stage,event.to_disposition)
    report={'verification':'PASS','tables':tables,'stage_counts':dict(Counter(i.stage for i in ideas if not i.removed_at)),'ideas':[{'reference':i.reference,'title':i.title,'stage':i.stage,'removed':bool(i.removed_at)} for i in ideas]}
with open(args.output,'w') as target:json.dump(report,target,indent=2)
print(json.dumps(report,indent=2))
