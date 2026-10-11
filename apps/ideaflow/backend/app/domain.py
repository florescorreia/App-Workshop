from datetime import date
from fastapi import HTTPException
from sqlalchemy import select, func
from .db import now
from .models import Idea, User, Site, Category, FinancialPlan, PlanPeriod, Task, ValuePeriod, IdeaEvent, Comment, reference_seq
from .auth import require
from .schemas import IdeaCreate, PlanInput, Transition
from .financial import app_today

STAGES = ['New','Screening','Analysis','Approved','Implementation','Validation','Realized']
LIFECYCLE = {'CREATED','STAGE_CHANGED','HELD','RESUMED','REJECTED','CANCELLED'}
EDGES = [('New','Screening'),('Screening','Analysis'),('Analysis','Approved'),('Approved','Implementation'),('Implementation','Validation'),('Validation','Realized'),('Analysis','Screening'),('Approved','Analysis'),('Validation','Implementation'),('Realized','Validation')]

def fail(message,status=422): raise HTTPException(status,message)

def lock_idea(db,idea_id,version=None,allow_removed=False):
    from .classifications import lock
    lock(db)
    idea = db.scalar(select(Idea).where(Idea.id == idea_id).with_for_update())
    if not idea: fail('Idea not found',404)
    if version is not None and idea.record_version != version: fail('This idea changed since you opened it. Refresh to see the latest version; your edits were not saved.',409)
    if idea.removed_at and not allow_removed: fail('This idea is removed and read-only. An Admin must restore it before work can continue.',409)
    return idea

def writable(user,idea,mode='edit'):
    require(user,'User','Admin')
    if idea.removed_at: fail('Removed ideas are read-only; restore before editing',409)

def references(db,site_id,category_id,owner_id):
    if (site_id and not db.get(Site,site_id)) or (category_id and not db.get(Category,category_id)): fail('Choose an existing site and category')
    owner = db.get(User,owner_id)
    if not owner or not owner.active or owner.deleted_at: fail('Choose an active owner')

def event(db,idea,user,event_type,activity=None,reason='',changes=None,from_stage=None,from_disposition=None,occurred_at=None,provenance=None):
    db.flush()
    sequence = (db.scalar(select(func.max(IdeaEvent.sequence)).where(IdeaEvent.idea_id == idea.id)) or 0) + 1
    db.add(IdeaEvent(idea_id=idea.id,sequence=sequence,event_type=event_type,activity=activity or event_type.replace('_',' ').title(),
        actor_id=user.id,occurred_at=occurred_at or now(),recorded_at=now(),reason=reason,changes=changes or {},
        from_stage=from_stage,to_stage=idea.stage,from_disposition=from_disposition,to_disposition=idea.disposition,provenance=provenance))
    idea.record_version += 1
    idea.updated_at = now()
    db.flush()

def scalar_json(v):
    if v is None or isinstance(v,(str,int,bool,float)): return v
    if isinstance(v,(dict,list)): return v
    return v.isoformat() if hasattr(v,'isoformat') else str(v)

def changes_for(obj,data):
    return {k:{'old':scalar_json(getattr(obj,k)),'new':scalar_json(v)} for k,v in data.items() if getattr(obj,k) != v}

def create_idea(db,user,data:IdeaCreate,occurred_at=None,provenance=None,external_key=None,batch_id=None):
    owner_id = data.owner_id or user.id
    fields = data.model_dump(exclude={'annual_gross','annual_recurring','upfront','probability','confidence','site_name','category_name'})
    from .classifications import resolve
    fields['site_id']=resolve(db,'sites',data.site_id,data.site_name,legacy=bool(provenance))
    fields['category_id']=resolve(db,'categories',data.category_id,data.category_name,legacy=bool(provenance))
    references(db,fields['site_id'],fields['category_id'],owner_id)
    fields['owner_id'] = owner_id
    timestamp = occurred_at or now()
    idea = Idea(**fields,submitter_id=user.id,reference=f'IF-{db.scalar(reference_seq.next_value()):05d}',created_at=timestamp,
        stage_entered_at=timestamp,external_key=external_key,demo_batch_id=batch_id,record_version=0)
    db.add(idea); db.flush()
    event(db,idea,user,'CREATED','New',changes={k:{'old':None,'new':scalar_json(v)} for k,v in fields.items()},occurred_at=timestamp,provenance=provenance)
    plan = FinancialPlan(idea_id=idea.id,version=1,**data.model_dump(include={'annual_gross','annual_recurring','upfront','probability','confidence'}))
    db.add(plan); db.flush()
    if any(getattr(plan,k) is not None for k in ('annual_gross','annual_recurring','upfront','probability','confidence')):
        event(db,idea,user,'PLAN_REVISED',changes={'plan_version':{'old':None,'new':1}},occurred_at=timestamp,provenance=provenance)
    return idea

def update_idea(db,user,idea,data,occurred_at=None,provenance=None):
    writable(user,idea)
    fields = data.model_dump(exclude={'record_version','site_name','category_name'})
    from .classifications import resolve
    fields['site_id']=resolve(db,'sites',data.site_id,data.site_name,legacy=bool(provenance))
    fields['category_id']=resolve(db,'categories',data.category_id,data.category_name,legacy=bool(provenance))
    fields['owner_id'] = fields['owner_id'] or idea.owner_id
    references(db,fields['site_id'],fields['category_id'],fields['owner_id'])
    for key in ('actual_start','actual_completion'):
        if fields[key] and fields[key] > (occurred_at.date() if occurred_at else app_today()): fail('Actual dates cannot be in the future')
    changes = changes_for(idea,fields)
    if changes:
        for k,v in fields.items(): setattr(idea,k,v)
        event(db,idea,user,'ASSIGNED' if 'owner_id' in changes else 'EDITED',changes=changes,occurred_at=occurred_at,provenance=provenance)
    return idea

def plans(db,idea): return list(db.scalars(select(FinancialPlan).where(FinancialPlan.idea_id==idea.id).order_by(FinancialPlan.version)))
def latest_draft(db,idea): return db.scalar(select(FinancialPlan).where(FinancialPlan.idea_id==idea.id,FinancialPlan.status=='Draft').order_by(FinancialPlan.version.desc()))
def approved_plan(db,idea): return db.scalar(select(FinancialPlan).where(FinancialPlan.idea_id==idea.id,FinancialPlan.status=='Approved').order_by(FinancialPlan.version.desc()))

def save_plan(db,user,idea,data:PlanInput,occurred_at=None,provenance=None):
    writable(user,idea)
    old = latest_draft(db,idea)
    before = old.version if old else None
    if old: old.status = 'Superseded'
    plan = FinancialPlan(idea_id=idea.id,version=max((p.version for p in plans(db,idea)),default=0)+1,
        **data.model_dump(exclude={'record_version','periods'}))
    db.add(plan); db.flush()
    for period in data.periods: db.add(PlanPeriod(plan_id=plan.id,**period.model_dump()))
    event(db,idea,user,'PLAN_REVISED',changes={'plan_version':{'old':before,'new':plan.version},'draft':data.model_dump(mode='json',exclude={'record_version'})},occurred_at=occurred_at,provenance=provenance)
    return plan

def approval_missing(db,idea):
    draft = latest_draft(db,idea)
    missing = []
    if not draft: return ['Save a financial draft first']
    for key,label in [('annual_gross','Annual gross benefit'),('annual_recurring','Annual recurring cost'),('upfront','Upfront cost'),('probability','Probability of success')]:
        if getattr(draft,key) is None: missing.append(label+' must be assessed (zero cost is allowed)')
    if not db.scalar(select(PlanPeriod).where(PlanPeriod.plan_id==draft.id)): missing.append('Add an explicit monthly plan')
    if not idea.expected_start or not idea.expected_finish: missing.append('Expected start and finish dates are required')
    return missing

def approve_plan(db,user,idea,reason,occurred_at=None,provenance=None):
    require(user,'User','Admin')
    if idea.disposition in ('Rejected','Cancelled'): fail('Terminal ideas cannot approve new plans')
    missing = approval_missing(db,idea)
    if missing: fail('; '.join(missing))
    previous = approved_plan(db,idea)
    if previous: previous.status='Superseded'
    plan = latest_draft(db,idea)
    plan.status='Approved'; plan.approved_by=user.id; plan.approved_at=occurred_at or now()
    event(db,idea,user,'PLAN_APPROVED',reason=reason,changes={'plan_version':{'old':previous.version if previous else None,'new':plan.version}},occurred_at=occurred_at,provenance=provenance)
    return plan

def allowed(db,user,idea):
    if idea.removed_at: return []
    permitted = user.role in ('User','Admin')
    result=[]
    for source,target in EDGES:
        if source != idea.stage: continue
        role_ok = permitted
        missing=[]
        if not role_ok: missing.append('Your role cannot make this decision')
        if idea.disposition != 'Active': missing.append('Resume this idea first' if idea.disposition=='On hold' else 'This disposition is terminal')
        if source=='Screening' and target=='Analysis' and not idea.screening_note: missing.append('Record a screening note')
        if target=='Approved': missing+=approval_missing(db,idea)
        if source=='Approved' and target=='Implementation':
            if not idea.actual_start: missing.append('Record actual start')
            if not db.scalar(select(Task).where(Task.idea_id==idea.id)): missing.append('Create at least one implementation task')
            if not approved_plan(db,idea): missing.append('A valid approved plan is required')
        if source=='Implementation' and target=='Validation':
            if not idea.actual_completion: missing.append('Record actual completion')
            if idea.progress != 100: missing.append('Progress must be 100%')
            if db.scalar(select(Task).where(Task.idea_id==idea.id,Task.required==True,Task.status!='Done')): missing.append('Complete all required tasks')
        if target=='Realized':
            if not db.scalar(select(ValuePeriod).where(ValuePeriod.idea_id==idea.id,ValuePeriod.verified_at.is_not(None),ValuePeriod.month < app_today().replace(day=1))): missing.append('Review and verify an elapsed month')
            if not idea.actual_completion or idea.progress!=100: missing.append('Implementation must be complete')
        result.append({'action':target,'allowed':not missing,'missing':missing,'reason_required':True,'role_permitted':role_ok})
    if idea.stage != 'Realized' and idea.disposition not in ('Rejected','Cancelled'):
        for action,ok in [('Resume' if idea.disposition=='On hold' else 'Hold',permitted),('Cancel',permitted)]:
            result.append({'action':action,'allowed':ok,'missing':[] if ok else ['Sign in with an active account'],'reason_required':True,'role_permitted':ok})
        if idea.stage in ('New','Screening','Analysis'):
            result.append({'action':'Reject','allowed':permitted,'missing':[] if permitted else ['An active account is required'],'reason_required':True,'role_permitted':permitted})
    return result

def transition(db,user,idea,data:Transition,occurred_at=None,provenance=None):
    option = next((x for x in allowed(db,user,idea) if x['action']==data.action),None)
    if not option: fail('This transition is not part of the lifecycle')
    if not option['role_permitted']: fail('Your role cannot perform this transition',403)
    if not option['allowed']: fail('; '.join(option['missing']))
    old_stage,old_disposition=idea.stage,idea.disposition
    timestamp = occurred_at or now()
    kind='STAGE_CHANGED'; activity=data.action
    if data.action in ('Hold','Resume','Reject','Cancel'):
        idea.disposition={'Hold':'On hold','Resume':'Active','Reject':'Rejected','Cancel':'Cancelled'}[data.action]
        kind={'Hold':'HELD','Resume':'RESUMED','Reject':'REJECTED','Cancel':'CANCELLED'}[data.action]
        activity={'Hold':'On hold','Resume':'Resumed','Reject':'Rejected','Cancel':'Cancelled'}[data.action]
    else:
        if data.action=='Approved': approve_plan(db,user,idea,data.reason,occurred_at,provenance)
        if old_stage=='Approved' and data.action=='Analysis':
            plan=approved_plan(db,idea)
            if plan:
                plan.status='Invalidated'
                event(db,idea,user,'PLAN_INVALIDATED',reason=data.reason,changes={'status':{'old':'Approved','new':'Invalidated'}},occurred_at=occurred_at,provenance=provenance)
        if old_stage=='Validation' and data.action=='Implementation':
            idea.progress=min(idea.progress,90); idea.actual_completion=None
            for task in db.scalars(select(Task).where(Task.idea_id==idea.id,Task.required==True)):
                task.status='Open'; task.completed_at=None
                event(db,idea,user,'TASK_CHANGED',reason=data.reason,changes={'task_id':task.id,'status':{'old':'Done','new':'Open'}},occurred_at=occurred_at,provenance=provenance)
        if data.action=='Realized':
            month=data.verification_through
            if not data.confirm_completion: fail('Confirm implementation completion')
            if not month or month.day!=1 or month>=app_today().replace(day=1): fail('Choose an elapsed verification-through month')
            period=db.get(ValuePeriod,(idea.id,month))
            if not period or not period.verified_at: fail('Verification-through month must have reviewed results')
            idea.verification_through=month
        idea.stage=data.action; idea.stage_entered_at=timestamp
    event(db,idea,user,kind,activity,reason=data.reason,from_stage=old_stage,from_disposition=old_disposition,
        changes={'stage':{'old':old_stage,'new':idea.stage},'disposition':{'old':old_disposition,'new':idea.disposition}},occurred_at=timestamp,provenance=provenance)
    return idea

def save_task(db,user,idea,data,task_id=None,occurred_at=None,provenance=None):
    task=db.get(Task,task_id) if task_id else None
    if task_id and (not task or task.idea_id!=idea.id): fail('Task not found',404)
    writable(user,idea)
    assignee=db.get(User,data.assignee_id)
    if not assignee or not assignee.active or assignee.deleted_at: fail('Choose an active assignee')
    fields=data.model_dump(exclude={'record_version'})
    changes=changes_for(task,fields) if task else {k:{'old':None,'new':scalar_json(v)} for k,v in fields.items()}
    if not task:
        task=Task(idea_id=idea.id,**fields); db.add(task)
    else:
        for k,v in fields.items(): setattr(task,k,v)
    task.completed_at=(occurred_at or now()) if task.status=='Done' else None
    db.flush()
    event(db,idea,user,'TASK_CHANGED',changes={'task_id':task.id,**changes},occurred_at=occurred_at,provenance=provenance)
    return task

def add_comment(db,user,idea,body,occurred_at=None,provenance=None):
    comment=Comment(idea_id=idea.id,actor_id=user.id,body=body,created_at=occurred_at or now())
    db.add(comment);db.flush()
    event(db,idea,user,'COMMENTED',changes={'comment_id':comment.id,'body':{'old':None,'new':body}},occurred_at=occurred_at,provenance=provenance)
    return comment

def elapsed_month(month):
    if month.day!=1 or month>=app_today().replace(day=1): fail('Results must be for a completed calendar month (first-of-month date)')

def save_result(db,user,idea,month,data,occurred_at=None,provenance=None):
    writable(user,idea,'result'); elapsed_month(month)
    period=db.get(ValuePeriod,(idea.id,month))
    if (period.record_version if period else 0)!=data.period_version: fail('This month changed. Refresh before saving.',409)
    if period and period.verified_at and not data.reason: fail('A reason is required to change a verified result')
    fields=data.model_dump(include={'gross','recurring','spend'})
    changes=changes_for(period,fields) if period else {k:{'old':None,'new':scalar_json(v)} for k,v in fields.items()}
    if not period:
        period=ValuePeriod(idea_id=idea.id,month=month,record_version=0);db.add(period)
    if period.verified_at:
        event(db,idea,user,'VERIFICATION_REVOKED',reason=data.reason,changes={'month':month.isoformat(),'verification':{'old':str(period.verified_at),'new':None}},occurred_at=occurred_at,provenance=provenance)
    for k,v in fields.items(): setattr(period,k,v)
    for k in ('verified_gross','verified_recurring','verified_spend','verified_by','verified_at'): setattr(period,k,None)
    period.reason=data.reason;period.record_version+=1
    event(db,idea,user,'RESULT_UPDATED',reason=data.reason,changes={'month':month.isoformat(),**changes},occurred_at=occurred_at,provenance=provenance)
    return period

def verify_result(db,user,idea,month,data,revoke=False,occurred_at=None,provenance=None):
    require(user,'User','Admin');elapsed_month(month)
    period=db.get(ValuePeriod,(idea.id,month))
    if not period: fail('Record actual results before verification')
    if period.record_version!=data.period_version: fail('This month changed. Refresh before verifying.',409)
    if not revoke and any(getattr(period,k) is None for k in ('gross','recurring','spend')): fail('Assess all three actual components first')
    fields={k:None for k in ('verified_gross','verified_recurring','verified_spend','verified_by','verified_at')} if revoke else {
        'verified_gross':data.gross,'verified_recurring':data.recurring,'verified_spend':data.spend,'verified_by':user.id,'verified_at':occurred_at or now()}
    changes=changes_for(period,fields)
    for k,v in fields.items(): setattr(period,k,v)
    period.reason=data.reason;period.record_version+=1
    event(db,idea,user,'VERIFICATION_REVOKED' if revoke else 'VALUE_VERIFIED',reason=data.reason,changes={'month':month.isoformat(),**changes},occurred_at=occurred_at,provenance=provenance)
    return period
