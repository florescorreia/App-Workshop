"""Explicit fictional import, replayed through the same domain commands as live work."""
import argparse, json, os, random, secrets
from datetime import date, datetime, time, timedelta, timezone
from typing import Literal
from pydantic import Field, model_validator
from sqlalchemy import select, text, func
from .schemas import Input, IdeaCreate, IdeaUpdate, Transition, PlanInput, Period, TaskInput, ResultInput, VerifyInput, RevokeInput
from .models import User, DemoBatch, Idea, IdeaEvent, Task, ValuePeriod
from .db import SessionLocal, now
from .auth import hasher
from .financial import app_today, add_month
from . import domain as D

class DemoPerson(Input):
    key: str
    name: str
    email: str
    role: Literal['User','Contributor','Manager','Finance','Admin']

class DemoAction(Input):
    occurred_at: datetime
    actor_key: str
    kind: Literal['edit','transition','plan','task','comment','result','verify','revoke']
    data: dict

class DemoIdea(Input):
    external_key: str
    created_at: datetime
    creator_key: str
    owner_key: str
    fields: dict
    actions: list[DemoAction] = Field(default_factory=list)

class DemoDataset(Input):
    format_version: Literal[1]=1
    batch_key: str = Field(min_length=1,max_length=120)
    seed: int=42
    anchor_date: date
    fictional: Literal[True]=True
    people: list[DemoPerson]
    ideas: list[DemoIdea] = Field(min_length=1,max_length=1000)
    @model_validator(mode='after')
    def validate_history(self):
        if self.anchor_date>app_today(): raise ValueError('Anchor date cannot be in the future')
        if len({p.key for p in self.people})!=len(self.people): raise ValueError('Duplicate person key')
        if len({p.email.lower() for p in self.people})!=len(self.people): raise ValueError('Duplicate fictional email')
        if len({i.external_key for i in self.ideas})!=len(self.ideas): raise ValueError('Duplicate external key')
        keys={p.key for p in self.people}
        for idea in self.ideas:
            if idea.creator_key not in keys or idea.owner_key not in keys: raise ValueError('Unknown person key')
            timestamps=[idea.created_at]+[a.occurred_at for a in idea.actions]
            if any(not t.tzinfo for t in timestamps): raise ValueError('Historical timestamps require a timezone')
            if timestamps != sorted(timestamps): raise ValueError('Actions must be chronological; ties retain array ordering')
            if any(t>now() or t.date()>self.anchor_date for t in timestamps): raise ValueError('Future historical occurrences are invalid')
            if any(a.actor_key not in keys for a in idea.actions): raise ValueError('Unknown action actor')
        return self

def replay(db,user,dataset,credentials):
    people={}
    for p in dataset.people:
        role='Admin' if p.role=='Admin' else 'User'
        existing=db.scalar(select(User).where(User.email==p.email.lower()))
        if existing:
            if existing.deleted_at or not existing.active:D.fail('Fictional account is deleted or inactive; use a distinct email')
            if existing.name!=p.name or existing.role!=role:D.fail('Fictional account collides with an existing user; use a distinct email')
            people[p.key]=existing
        else:
            password=secrets.token_urlsafe(18)
            obj=User(name=p.name,email=p.email.lower(),role=role,password_hash=hasher.hash(password))
            db.add(obj);db.flush();people[p.key]=obj
            credentials.append({'name':p.name,'email':p.email.lower(),'role':role,'password':password})
    batch=DemoBatch(batch_key=dataset.batch_key,seed=dataset.seed,anchor_date=dataset.anchor_date,importer=user.id)
    db.add(batch);db.flush();references=[]
    provenance={'fictional':True,'batch_key':dataset.batch_key,'seed':dataset.seed,'anchor_date':dataset.anchor_date.isoformat()}
    for imported in dataset.ideas:
        if db.scalar(select(Idea).where(Idea.external_key==imported.external_key)):D.fail('External key already exists; imports never overwrite records')
        fields={**imported.fields,'owner_id':people[imported.owner_key].id}
        idea=D.create_idea(db,people[imported.creator_key],IdeaCreate.model_validate(fields),imported.created_at,provenance,imported.external_key,batch.id)
        local_tasks={}
        for action in imported.actions:
            actor=people[action.actor_key];data=dict(action.data);ts=action.occurred_at
            if 'record_version' in data or 'period_version' in data:D.fail('Importer derives record versions; remove client versions')
            if action.kind=='edit':
                allowed={k:getattr(idea,k) for k in IdeaUpdate.model_fields if k not in ('record_version','site_name','category_name')}
                if 'owner_key' in data:data['owner_id']=people[data.pop('owner_key')].id
                D.update_idea(db,actor,idea,IdeaUpdate.model_validate({**allowed,**data,'record_version':idea.record_version}),ts,provenance)
            elif action.kind=='transition':
                D.transition(db,actor,idea,Transition.model_validate({**data,'record_version':idea.record_version}),ts,provenance)
            elif action.kind=='plan':
                D.save_plan(db,actor,idea,PlanInput.model_validate({**data,'record_version':idea.record_version}),ts,provenance)
            elif action.kind=='task':
                key=data.pop('task_key');data['assignee_id']=people[data.pop('assignee_key')].id
                task=D.save_task(db,actor,idea,TaskInput.model_validate({**data,'record_version':idea.record_version}),local_tasks.get(key),ts,provenance)
                local_tasks[key]=task.id
            elif action.kind=='comment':
                if set(data)!={'body'}:D.fail('Comment data must contain only body')
                D.add_comment(db,actor,idea,data['body'],ts,provenance)
            elif action.kind in ('result','verify','revoke'):
                month=date.fromisoformat(data.pop('month'))
                if month>=ts.date().replace(day=1):D.fail('Historical actual or verification cannot precede period completion')
                period=db.get(ValuePeriod,(idea.id,month));version=period.record_version if period else 0
                cls={'result':ResultInput,'verify':VerifyInput,'revoke':RevokeInput}[action.kind]
                command=cls.model_validate({**data,'record_version':idea.record_version,'period_version':version})
                if action.kind=='result':D.save_result(db,actor,idea,month,command,ts,provenance)
                else:D.verify_result(db,actor,idea,month,command,action.kind=='revoke',ts,provenance)
        db.flush()
        events=list(db.scalars(select(IdeaEvent).where(IdeaEvent.idea_id==idea.id).order_by(IdeaEvent.occurred_at,IdeaEvent.sequence,IdeaEvent.id)))
        last=next(e for e in reversed(events) if e.event_type in D.LIFECYCLE)
        if (last.to_stage,last.to_disposition)!=(idea.stage,idea.disposition):D.fail('Replay/current state mismatch')
        references.append({'reference':idea.reference,'title':idea.title,'stage':idea.stage,'disposition':idea.disposition})
    counts={'ideas':len(references),'events':db.scalar(select(func.count()).select_from(IdeaEvent).join(Idea).where(Idea.demo_batch_id==batch.id)),
        'tasks':db.scalar(select(func.count()).select_from(Task).join(Idea).where(Idea.demo_batch_id==batch.id)),
        'value_periods':db.scalar(select(func.count()).select_from(ValuePeriod).join(Idea).where(Idea.demo_batch_id==batch.id))}
    batch.counts=counts
    return {'batch_key':dataset.batch_key,'anchor_date':dataset.anchor_date,'counts':counts,'records':references,'validation':'Chronology, domain prerequisites, roles, elapsed results and current-state replay passed'}

def import_dataset(db,user,dataset,dry_run=True):
    D.require(user,'Admin')
    db.execute(text('SELECT pg_advisory_xact_lock(hashtext(:key))'),{'key':'ideaflow-demo-'+dataset.batch_key})
    existing=db.scalar(select(DemoBatch).where(DemoBatch.batch_key==dataset.batch_key))
    if existing:return {'batch_key':dataset.batch_key,'no_op':True,'counts':existing.counts,'message':'Batch already exists. No records changed.'}
    credentials=[]
    if dry_run:
        savepoint=db.begin_nested()
        try:report=replay(db,user,dataset,credentials)
        finally:savepoint.rollback()
        return {**report,'dry_run':True,'message':'Validated without business writes. Readable reference sequences may have gaps.'}
    report=replay(db,user,dataset,credentials)
    # Credentials never enter API responses or logs. Files are private local handover only.
    directory=os.getenv('DEMO_HANDOVER_DIR','/handover');os.makedirs(directory,exist_ok=True)
    file=os.path.join(directory,dataset.batch_key.replace('/','_').replace('\\','_')+'-credentials.json')
    if credentials:
        with open(file,'x',encoding='utf-8') as stream:json.dump(credentials,stream,indent=2)
    return {**report,'dry_run':False,'credential_file':file if credentials else None}

TITLES=[
 'Consolidate outbound freight into scheduled routes','Repair compressed-air leaks at Tampa','Standardize corrugated packaging across sites',
 'Reduce changeover scrap on assembly line 2','Rationalize slow-moving inventory','Replace emergency courier dispatches with a cutoff window',
 'Negotiate pooled resin purchases','Recover reusable pallets from regional customers','Install occupancy controls in warehouse aisles',
 'Reduce invoice exceptions with receipt matching','Balance kit preparation before the morning shift','Tune oven standby temperatures',
 'Consolidate maintenance spare-part suppliers','Reduce returns from incorrect carton labels','Shorten inspection queue with standard sampling']

def built_in(batch_key='harborworks-demo-v1',seed=42,anchor=None):
    anchor=anchor or app_today();rng=random.Random(seed)
    people=[DemoPerson(key='manager',name='Morgan Ellis',email='morgan@harborworks.example',role='Manager'),
        DemoPerson(key='owner',name='Alex Rivera',email='alex@harborworks.example',role='Contributor'),
        DemoPerson(key='finance',name='Jordan Chen',email='jordan@harborworks.example',role='Finance')]
    ideas=[];anchor_ts=datetime.combine(anchor,time(12),timezone.utc)
    if anchor_ts>now():anchor_ts=now()
    targets=['Implementation','Realized','Analysis','Validation','Analysis']+['Realized']*11+['Rejected']*6+['Cancelled']*3+['Implementation']*7+['Approved']*6+['Validation']*4+['Analysis']*8+['Screening']*5+['New']*5
    categories=['Freight','Energy','Procurement','Scrap/Quality','Inventory']+['Procurement','Freight','Inventory','Energy','Scrap/Quality','Productivity','Working Capital']*8
    for i,target in enumerate(targets):
        elapsed=rng.randint(420,535) if target=='Realized' else (rng.randint(300,420) if target in ('Implementation','Approved','Validation') else rng.randint(100,280))
        created=anchor_ts-timedelta(days=elapsed);current=created;actions=[]
        annual=rng.randrange(35,160)*1000;recurring=round(annual*.08);upfront=rng.randrange(8,40)*1000
        start=add_month(anchor.replace(day=1),-6 if target=='Realized' else -3);finish=add_month(start,2)
        if target in ('New','Screening','Analysis','Rejected','Cancelled'):
            finish=add_month(anchor.replace(day=1),2)
        elif target=='Approved': finish=add_month(anchor.replace(day=1),1)
        fields={'title':TITLES[i] if i<15 else f'{["Reduce","Standardize","Improve","Consolidate"][i%4]} {categories[i].lower()} flow in {['Tampa','Atlanta','Dallas'][i%3]} — initiative {i+1}',
            'problem':'Small batches, inconsistent handoffs and repeated exceptions consume staff time and create avoidable operating cost. Review the last quarter of site records to quantify the opportunity.',
            'solution':'Pilot a standard work routine with the site team, measure the baseline, and validate the sustained result before expanding.',
            'site_id':['Tampa','Atlanta','Dallas'][i%3],'category_id':categories[i],'annual_gross':annual,'annual_recurring':recurring,'upfront':upfront,
            'probability':'.7','confidence':'.65','expected_start':start.isoformat(),'expected_finish':finish.isoformat()}
        if i==1:fields['site_id']='Tampa'
        if i==4:fields['problem']+=' Working capital cash release is supplemental narrative only and is not included in recurring savings.'
        def add(kind,data,actor='manager',advance=0):
            nonlocal current
            current+=timedelta(days=advance)
            actions.append(DemoAction(kind=kind,data=data,actor_key=actor,occurred_at=current))
        def move(stage,advance=0):add('transition',{'action':stage,'reason':'Historical fictional review: evidence and delivery responsibilities confirmed.'},advance=advance)
        if target!='New':
            move('Screening',rng.randint(3,12));add('edit',{'screening_note':'Site review confirms a measurable opportunity and a named pilot owner.'})
        if target=='Rejected':
            add('transition',{'action':'Reject','reason':'No credible incremental benefit after review.'},advance=10)
        elif target not in ('New','Screening'):
            move('Analysis',rng.randint(5,20))
            if i in (0,1,3,5,6,7,8,9):
                move('Screening',10);move('Analysis',5)
            if target=='Cancelled':
                add('transition',{'action':'Cancel','reason':'Operating priorities changed; proposal closed without discarding history.'},advance=20)
            else:
                if target not in ('Analysis',):
                    # Analysis takes longer than other completed stages, with uneven durations.
                    current=max(current+timedelta(days=rng.randint(45,95)),datetime.combine(start,time(12),timezone.utc)-timedelta(days=7))
                    periods=[]
                    for n in range(18):
                        factor=min(n/3,1)
                        periods.append({'month':add_month(start,n).isoformat(),'gross':round(annual/12*factor,2),'recurring':round(recurring/12*factor,2),'spend':upfront if n==0 else 0})
                    add('plan',{'annual_gross':annual,'annual_recurring':recurring,'upfront':upfront,'probability':'.7','confidence':'.65','rationale':'Baseline, staged ramp and implementation costs reviewed. USD only.','periods':periods})
                    move('Approved')
                    if target!='Approved':
                        actual_start=max(current.date(),start)
                        if current.date()<actual_start:current=datetime.combine(actual_start,time(12),timezone.utc)
                        add('edit',{'actual_start':actual_start.isoformat()})
                        task_data={'task_key':'pilot','title':'Complete pilot and document measured baseline','assignee_key':'owner','due_date':finish.isoformat(),'status':'Open','required':True}
                        add('task',task_data);move('Implementation')
                        if target in ('Validation','Realized'):
                            completion=max(current.date()+timedelta(days=20),finish)
                            current=datetime.combine(completion,time(12),timezone.utc)
                            add('task',{**task_data,'status':'Done'});add('edit',{'progress':100,'actual_completion':completion.isoformat()});move('Validation')
                        # Actuals are deliberately lagged; retain at least two months for freight hero.
                        current=max(current,datetime.combine(add_month(start,3),time(12),timezone.utc))
                        number=2 if i==0 else 3
                        for n in range(number+1):
                            month=add_month(start,n)
                            if month>=anchor.replace(day=1):continue
                            current=max(current,datetime.combine(add_month(month,1),time(12),timezone.utc))
                            p=periods[n];factor=.68 if i==0 else rng.choice([.85,1.08,1.12])
                            result={'month':month.isoformat(),'gross':round(p['gross']*factor,2),'recurring':p['recurring'],'spend':upfront if n==0 else 0,'reason':'Fictional monthly metered result.'}
                            add('result',result,actor='finance')
                            if target=='Realized' or n==0:
                                add('verify',result,actor='finance')
                        if target=='Realized':
                            add('transition',{'action':'Realized','reason':'Measured sustained improvement confirmed by Finance.','verification_through':add_month(start,number).isoformat(),'confirm_completion':True},actor='finance')
                if i==4 or i in (42,43,44,45):
                    current=max(current,anchor_ts-timedelta(days=55+i%10))
                    add('transition',{'action':'Hold','reason':'Awaiting supplier quotations and a revised operating schedule.'})
                elif i in (2,46):
                    add('transition',{'action':'Hold','reason':'Supplier review paused.'},advance=7)
                    add('transition',{'action':'Resume','reason':'Supplier response received.'},advance=14)
        add('comment',{'body':'Fictional HarborWorks case. Supporting evidence is illustrative; validate live gains separately.'},actor='owner')
        if any(a.occurred_at>anchor_ts for a in actions):
            raise ValueError('Generator produced a future historical action; adjust the anchor/chronology rather than rewriting timestamps')
        ideas.append(DemoIdea(external_key=f'{batch_key}:{i+1:03d}',created_at=created,creator_key='manager',owner_key='owner',fields=fields,actions=actions))
    return DemoDataset(batch_key=batch_key,seed=seed,anchor_date=anchor,people=people,ideas=ideas)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--batch-key',default='harborworks-demo-v1');parser.add_argument('--seed',type=int,default=42)
    parser.add_argument('--anchor-date',type=date.fromisoformat);parser.add_argument('--file');parser.add_argument('--dry-run',action='store_true');parser.add_argument('--write-json')
    args=parser.parse_args()
    dataset=DemoDataset.model_validate_json(open(args.file,encoding='utf-8').read()) if args.file else built_in(args.batch_key,args.seed,args.anchor_date)
    if args.write_json:
        with open(args.write_json,'w',encoding='utf-8') as f:f.write(dataset.model_dump_json(indent=2))
        return
    with SessionLocal.begin() as db:
        user=db.scalar(select(User).where(User.email==os.environ['ADMIN_EMAIL'].lower()))
        report=import_dataset(db,user,dataset,args.dry_run)
    print(json.dumps(report,default=str,indent=2))
    directory=os.getenv('DEMO_HANDOVER_DIR','/handover');os.makedirs(directory,exist_ok=True)
    with open(os.path.join(directory,'last-import-report.json'),'w',encoding='utf-8') as f:json.dump(report,f,default=str,indent=2)
if __name__=='__main__':main()
