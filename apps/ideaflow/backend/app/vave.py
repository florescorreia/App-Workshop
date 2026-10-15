"""VAVE scope, gate and savings integrity. All mutations share the idea transaction."""
import base64, copy, hashlib, json
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, Request, Response, Query
from sqlalchemy import select, func
from .db import get_db, now
from .auth import current_user
from .models import Idea, IdeaEvent, User, reference_seq
from .vave_models import Program, Case, ProgramEvent, Evidence, Notice, Preference
from . import vave_schemas as S
from .domain import fail, event
from .queries import serialize
from .financial import app_today, schedule_metrics

router = APIRouter(prefix='/api/v1/vave')
LEVELS = ['Captured','Screened','Quantified','Validated','Authorized','Implemented','Verified']
FINANCIAL = {'Manager','Finance','Authority'}
REPORTING = FINANCIAL | {'Viewer'}

def roles(program, user):
    if user.role == 'Admin': return {'Manager','Finance','Authority','Functional','Contributor'}
    return set(next((m['roles'] for m in program.data['members'] if m['user_id'] == user.id), []))

def external_only(db, user):
    if user.role == 'Admin': return False
    rs = set()
    for p in db.scalars(select(Program)): rs |= roles(p, user)
    return 'External' in rs

def program(db, user, id, needed=None):
    from .classifications import lock
    lock(db)  # Same transaction lock as legacy mutations and account management.
    p = db.scalar(select(Program).where(Program.id == id).with_for_update())
    rs = roles(p, user) if p else set()
    if not p or not rs: fail('Program not found', 404)
    if needed and not rs.intersection(needed): fail('Your program role cannot perform this decision', 403)
    return p

def case(db, user, id, version=None, needed=None):
    c = db.get(Case, id)
    if not c: fail('VAVE idea not found', 404)
    p = program(db, user, c.program_id, needed)
    i = db.scalar(select(Idea).where(Idea.id == id).with_for_update())
    if roles(p, user) <= {'External'} and not c.data['shared'] and i.submitter_id!=user.id: fail('VAVE idea not found', 404)
    if version is not None and i.record_version != version: fail('This idea changed. Refresh before saving; your edits were not saved.', 409)
    if version is not None and c.status in ('Rejected','Cancelled','Superseded','Closed'): fail('Reopen the archived idea with a reason before editing', 409)
    return p, c, i

def active_member(db, p, id):
    u = db.get(User, id) if id else None
    if not u or not u.active or u.deleted_at or not roles(p, u): fail('Choose an active member of this program')

def notify(db, p, i, ids, kind, message):
    for id in set(ids):
        active_member(db, p, id)
        if roles(p,db.get(User,id)) <= {'External'}: continue
        db.add(Notice(user_id=id, idea_id=i.id, data={'time':now().isoformat(),'kind':kind,'message':message,'mandatory':True}))

def record(db, p, c, i, user, kind, reason, changes):
    event(db, i, user, 'VAVE_'+kind, reason=reason, changes=changes)

def fields(data): return data.model_dump(mode='json', exclude={'record_version','reason'})

def material(data):
    result = {k:data[k] for k in ('scope','product_family','product','assembly','function','constraints','feasibility','parent_id','duplicate_of','dependencies')}
    result['applications'] = [{k:v for k,v in a.items() if k not in ('rollout','implementation_evidence','owner_id')} for a in data['applications']]
    result['critical_risks'] = [r for r in data['risks'] if r['severity'] == 'Critical']
    return result

def signature(c): return hashlib.sha256(json.dumps(material(c.data), sort_keys=True).encode()).hexdigest()

def validate_case(db, p, data, id=None):
    for account in [data.owner_id, data.hold_owner_id]+[a.owner_id for a in data.applications]+[a.owner_id for a in data.actions]+[r.owner_id for r in data.risks]:
        if account: active_member(db, p, account)
    for linked in [data.parent_id, data.duplicate_of, data.reuse_of]+data.dependencies:
        if linked:
            other = db.get(Case, linked)
            if linked == id or not other or other.program_id != p.id: fail('Relationships must refer to a different idea in the same program')
            seen = {id}; cursor = other
            while cursor:
                if cursor.idea_id in seen: fail('Circular parent/dependency relationship')
                seen.add(cursor.idea_id); cursor = db.get(Case, cursor.data.get('parent_id')) if cursor.data.get('parent_id') else None
    action_ids = {a.id for a in data.actions}
    action_by_id = {a.id:a for a in data.actions}
    for a in data.actions:
        if a.dependency and (a.dependency not in action_ids or a.dependency == a.id): fail('Task dependency must refer to another action')
        if a.status == 'Done' and not a.evidence: fail('Completed actions need completion evidence')
        seen={a.id};cursor=a
        while cursor.dependency:
            if cursor.dependency in seen: fail('Circular action dependency')
            seen.add(cursor.dependency);cursor=action_by_id[cursor.dependency]
        if a.status=='Done' and a.dependency and action_by_id[a.dependency].status!='Done': fail('Complete predecessor actions first')
    for r in data.risks:
        if r.disposition != 'Open' and not r.acceptance_evidence: fail('Risk acceptance needs evidence')
    for a in data.applications:
        if a.currency == p.data['currency'] and a.fx_rate != 1: fail('Same-currency applications use exchange rate 1')
        if a.rollout == 'In production' and (not a.effective_date or a.effective_date > app_today() or not a.implementation_evidence): fail('Production rollout needs an elapsed effective date and implementation evidence')
        if a.value_type in ('Capacity','Nonfinancial') and a.selected and not a.nonfinancial_metric: fail('Capacity/nonfinancial applications require their own metric')

def calculations(a, approved=None):
    d = lambda k: Decimal(a[k]) if a.get(k) is not None else None
    unit = None if d('baseline') is None or d('proposed') is None else d('baseline')-d('proposed')
    factor = d('usage')*d('conversion')
    retained = None if unit is None or d('recurring_per_unit') is None else unit-d('recurring_per_unit')-d('giveback_per_unit')
    gross = None if unit is None or d('annual_volume') is None else unit*factor*d('annual_volume')
    net = None if retained is None or d('annual_volume') is None else retained*factor*d('annual_volume')
    periods=[]
    for p in a['periods']:
        volume=Decimal(p['volume'])*Decimal(p['adoption'])*factor
        eligible = bool(a.get('effective_date') and p['month'][:7] >= a['effective_date'][:7])
        periods.append({'month':p['month'],'eligible_volume':volume if eligible else Decimal(0),
            'gross':None if unit is None else unit*volume if eligible else Decimal(0),
            'net':None if retained is None else retained*volume if eligible else Decimal(0), 'spend':Decimal(p['spend'])})
    cash=schedule_metrics([{**r,'month':date.fromisoformat(r['month'])} for r in periods]) if all(r['net'] is not None for r in periods) else None
    if cash and cash['implementation_spend'] and cash['payback']['label']=='No upfront investment':
        first=next(r for r in periods if r['spend']>0)
        cash['payback']={'label':'Recovered within first spending month','month':first['month'],'elapsed_months':1}
    return {'unit_saving':unit,'annual_gross_run_rate':gross,'annual_net_run_rate':net,'periods':periods,
        'cash':cash,
        'formula':'(baseline − proposed − incremental recurring − giveback) × eligible volume × adoption × usage × conversion; spend separate'}

def requirement_roles(p, c, target):
    required = {1:['Manager'],2:['Finance'],3:['Functional','Finance'],4:['Authority'],5:['Manager'],6:['Finance']}[target]
    assessed=sum((calculations(a)['annual_net_run_rate'] or Decimal(0))*Decimal(a['fx_rate']) for a in c.data['applications'] if a['selected'] and a['value_type']=='Cost reduction')
    if target == 4 and assessed >= Decimal(p.data['approval_threshold']): required += ['Finance']
    return required

def missing(db, p, c, target, approvals=True):
    d=c.data; result=[]; apps=[a for a in d['applications'] if a['selected']]
    if not d['owner_id'] or not d['next_action'] or not d['due_date']: result.append('Assign one owner, next action and due date')
    if target >= 2:
        if not apps: result.append('Add a selected benefit application')
        for a in apps:
            if any(a[k] is None for k in ('baseline','proposed','annual_volume','recurring_per_unit','baseline_date','effective_date')) or not a['periods'] or not a['assumptions'] or not a['evidence']:
                result.append(a['scope']+': comparable baseline, costs, volume, dates, assumptions, evidence and monthly schedule required')
            if a['currency'] != p.data['currency'] and not p.data['fx_basis']: result.append('Declare exchange-rate basis')
            if not a['owner_id']: result.append(a['scope']+': application owner required')
        overlaps={}
        for other in db.scalars(select(Case).where(Case.program_id==p.id)):
            if other.status in ('Rejected','Cancelled','Superseded','Closed'): continue
            for a in other.data['applications']:
                if not a['selected'] or not a['overlap_key']: continue
                for r in a['periods']:
                    if Decimal(r['volume'])*Decimal(r['adoption']) <= 0: continue
                    key=(a['overlap_key'].casefold().strip(),a['plant'].casefold().strip(),r['month'],a['value_type'])
                    overlaps[key]=overlaps.get(key,0)+1
        if any(n>1 for n in overlaps.values()): result.append('Resolve overlapping selected applications in this program before approval')
        if apps and any(other.data.get('parent_id')==c.idea_id for other in db.scalars(select(Case).where(Case.program_id==p.id))): result.append('Parent initiatives allocate value to child applications; remove parent financial contribution')
        if d['duplicate_of'] and apps: result.append('Duplicate concepts cannot contribute selected benefits')
    if target >= 3:
        for topic in p.data['mandatory_evidence']:
            if not d['feasibility'].get(topic,'').strip(): result.append(topic+': acceptance evidence required')
        if not d['function'] or not d['constraints']: result.append('Document required function and constraints')
        if any(r['severity']=='Critical' and r['disposition']=='Open' for r in d['risks']): result.append('Resolve critical risks')
    if target >= 4 and not d['actions']: result.append('Create implementation actions with owners and dates')
    if target >= 5:
        if not apps or any(a['rollout']!='In production' or not a['implementation_evidence'] for a in apps): result.append('Every selected application must be in production with evidence')
        if any(a['required'] and a['status']!='Done' for a in d['actions']): result.append('Complete required implementation actions')
    if target >= 6:
        for a in apps:
            periods=[r for r in calculations(a)['periods'] if r['eligible_volume']>0 and p.data['start'][:7]<=r['month'][:7]<=p.data['end'][:7] and r['month']<app_today().replace(day=1).isoformat()]
            if not periods or any(not c.actuals.get(a['id']+'|'+r['month'],{}).get('verified_at') for r in periods): result.append(a['scope']+': verify all eligible elapsed observation periods')
    if approvals:
        for role in requirement_roles(p,c,target):
            review=c.reviews.get(str(target)+'|'+role)
            if not review or review['signature']!=signature(c): result.append(role+' approval required for M'+str(target))
    return list(dict.fromkeys(result))

def view(db, p, c, i, user, detail=False):
    rs=roles(p,user); ext=rs <= {'External'}; cost=bool(rs & REPORTING) or (not ext and user.id in (c.data['owner_id'],i.submitter_id))
    data=copy.deepcopy(c.data)
    if not cost:
        for a in data['applications']:
            for k in ('baseline','proposed','annual_volume','recurring_per_unit','giveback_per_unit','fx_rate','low','high','periods','assumptions','evidence'): a.pop(k,None)
        for a in data['actions']: a.pop('cost',None)
    if ext:
        data={k:data[k] for k in ('title','description','scope','product','category','shared')}
    result={'id':i.id,'reference':i.reference,'program_id':p.id,'record_version':i.record_version,'maturity':c.maturity,'maturity_name':LEVELS[c.maturity],'status':c.status,'updated_at':i.updated_at,'originator_id':i.submitter_id,'data':data,
        'roles':sorted(rs),'partial_rollout':any(a['rollout']=='In production' for a in c.data['applications'] if a['selected']) and any(a['rollout']!='In production' for a in c.data['applications'] if a['selected']),
        'review_required':c.approved is None and c.maturity>=3}
    if detail:
        result['legacy_available']=not ext and bool(db.scalar(select(IdeaEvent.id).where(IdeaEvent.idea_id==i.id,IdeaEvent.event_type=='VAVE_ADOPTED')))
        result['evidence']=[{'id':e.id,'name':e.name,'sha256':e.sha256,'shared':e.shared,'size':len(e.content)} for e in db.scalars(select(Evidence).where(Evidence.idea_id==i.id)) if not ext or e.shared]
        result['events']=[{**serialize(e),'actor_name':db.get(User,e.actor_id).name} if cost else {'id':e.id,'sequence':e.sequence,'event_type':e.event_type,'activity':e.activity,'actor_name':db.get(User,e.actor_id).name,'occurred_at':e.occurred_at,'reason':e.reason if not ext else '', 'changes':e.changes if e.event_type=='VAVE_DISCUSSION' else {}} for e in db.scalars(select(IdeaEvent).where(IdeaEvent.idea_id==i.id).order_by(IdeaEvent.sequence)) if not ext or (e.event_type=='VAVE_DISCUSSION' and e.changes.get('shared'))]
        result['missing']=missing(db,p,c,min(c.maturity+1,6)) if not ext else []
        result['required_roles']=requirement_roles(p,c,min(c.maturity+1,6)) if not ext else []
        if cost:
            result.update(approved=c.approved,actuals=c.actuals,reviews=c.reviews,calculations={a['id']:calculations(a) for a in c.data['applications']})
    return result

@router.get('/programs')
def programs(user=Depends(current_user), db=Depends(get_db)):
    return [{'id':p.id,'record_version':p.record_version,'name':p.data['name'],'client':p.data['client'],'roles':sorted(roles(p,user))} for p in db.scalars(select(Program)) if roles(p,user)]

def save_program(db, user, data, p=None):
    if p:
        if p.record_version != data.record_version: fail('Program changed; refresh before saving',409)
        if not data.reason: fail('Program changes require a reason')
    elif not any(m.user_id==user.id and 'Manager' in m.roles for m in data.members): fail('The creator must be a program Manager')
    for m in data.members:
        u=db.get(User,m.user_id)
        if not u or not u.active or u.deleted_at: fail('Membership requires active accounts')
    if not any('Manager' in m.roles for m in data.members): fail('Keep a program Manager')
    if p:
        member_ids={m.user_id for m in data.members}
        for c in db.scalars(select(Case).where(Case.program_id==p.id)):
            responsible=[c.data['owner_id']]+[a['owner_id'] for a in c.data['actions'] if a['status']!='Done']
            if c.status in ('Active','Draft','On hold') and any(id and id not in member_ids for id in responsible): fail('Reassign open responsibilities before removing program membership')
    before=copy.deepcopy(p.data) if p else None
    if not p: p=Program(data=fields(data));db.add(p);db.flush()
    else:
        p.data=fields(data);p.record_version+=1
        # Changed governance requires fresh review of every current approval.
        if any(before[k]!=p.data[k] for k in ('members','mandatory_evidence','approval_threshold','recognition_rules','fx_basis','currency','start','end')):
            for c in db.scalars(select(Case).where(Case.program_id==p.id)):
                c.reviews={};c.approved=None;i=db.get(Idea,c.idea_id)
                original=copy.deepcopy(c.actuals)
                c.actuals={k:{**v,'verified_at':None,'verified_by':None} for k,v in c.actuals.items()}
                record(db,p,c,i,user,'APPROVAL_INVALIDATED',data.reason,{'program_rules_changed':True,'previous_actuals':original})
    db.add(ProgramEvent(program_id=p.id,actor_id=user.id,data={'time':now().isoformat(),'reason':data.reason,'before':before,'after':p.data}))
    return {'id':p.id,'record_version':p.record_version,'data':p.data}

@router.post('/programs',status_code=201)
def new_program(data:S.ProgramInput,user=Depends(current_user),db=Depends(get_db)):
    if external_only(db,user): fail('External participants cannot establish programs',403)
    return save_program(db,user,data)

@router.get('/programs/{id}')
def get_program(id:str,user=Depends(current_user),db=Depends(get_db)):
    p=program(db,user,id); rs=roles(p,user);cost=bool(rs & REPORTING)
    data=copy.deepcopy(p.data)
    if not cost: data={k:data[k] for k in ('name','client','scope','start','end','currency','objective','mandatory_evidence','cadence_days','stale_days')}
    return {'id':p.id,'record_version':p.record_version,'roles':sorted(rs),'data':data,
        'members':[{'id':u.id,'name':u.name,'roles':m['roles'],'active':u.active and not u.deleted_at} for m in p.data['members'] for u in [db.get(User,m['user_id'])]] if not rs <= {'External'} else [],
        'events':[serialize(e) for e in db.scalars(select(ProgramEvent).where(ProgramEvent.program_id==id))] if 'Manager' in rs else []}

@router.put('/programs/{id}')
def edit_program(id:str,data:S.ProgramInput,user=Depends(current_user),db=Depends(get_db)):
    return save_program(db,user,data,program(db,user,id,{'Manager'}))

@router.get('/programs/{id}/ideas')
def register(id:str,search:str='',maturity:int|None=None,status:str='',product:str='',plant:str='',mine:bool=False,category:str='',owner_id:str='',part:str='',supplier:str='',sort:str='updated',user=Depends(current_user),db=Depends(get_db)):
    p=program(db,user,id);result=[]
    ext=roles(p,user)<={'External'}
    if ext and (plant or mine or owner_id or part or supplier): fail('External filters may use only approved public fields',403)
    if sort not in ('updated','title','maturity','due','priority'): fail('Choose a supported register sort')
    for c in db.scalars(select(Case).where(Case.program_id==id)):
        i=db.get(Idea,c.idea_id)
        if roles(p,user)<={'External'} and not c.data['shared'] and i.submitter_id!=user.id: continue
        if maturity is not None and c.maturity!=maturity: continue
        if status and c.status!=status: continue
        if product and c.data['product']!=product: continue
        if plant and not any(a['plant']==plant for a in c.data['applications']): continue
        if category and c.data['category']!=category: continue
        if owner_id and c.data['owner_id']!=owner_id: continue
        if part and not any(a['part']==part for a in c.data['applications']): continue
        if supplier and not any(a['supplier']==supplier for a in c.data['applications']): continue
        if mine and user.id != c.data['owner_id'] and not any(a['owner_id']==user.id and a['status']!='Done' for a in c.data['actions']): continue
        searchable=[i.reference]+[c.data.get(k,'') for k in ('title','description','scope','product','category')]
        if not ext:
            searchable += [c.data.get(k,'') for k in ('source','workshop','current_condition','future_condition','function','product_family','assembly','commodity','region','cost_category')]
            searchable += [a.get(k,'') for a in c.data['applications'] for k in ('scope','plant','part','revision','supplier')]
        if search and search.casefold() not in ' '.join(searchable).casefold(): continue
        result.append(view(db,p,c,i,user))
    if sort=='updated': result.sort(key=lambda r:r['updated_at'],reverse=True)
    elif sort=='title': result.sort(key=lambda r:r['data']['title'].casefold())
    elif sort=='maturity': result.sort(key=lambda r:(r['maturity'],r['reference']))
    elif sort=='due': result.sort(key=lambda r:(r['data'].get('due_date') or '9999-12-31',r['reference']))
    elif sort=='priority': result.sort(key=lambda r:({'High':0,'Medium':1,'Low':2}.get(r['data'].get('priority'),1),r['reference']))
    return result

@router.post('/programs/{program_id}/adopt/{idea_id}')
def adopt_legacy(program_id:str,idea_id:str,data:S.AdoptInput,dry_run:bool=True,user=Depends(current_user),db=Depends(get_db)):
    if user.role!='Admin': fail('An Admin must authorize adaptation of an existing IdeaFlow record',403)
    p=program(db,user,program_id,{'Manager'})
    from .domain import lock_idea
    i=lock_idea(db,idea_id,data.record_version)
    validate_case(db,p,data.case,idea_id)
    before=serialize(i);after=fields(data.case)
    digest=hashlib.sha256(json.dumps({'id':idea_id,'program':program_id,'version':i.record_version,'case':after},sort_keys=True).encode()).hexdigest()
    preview={'reference':i.reference,'previous_title':i.title,'proposed_title':data.case.title,'maturity':0,'status':'Draft','preview_token':digest,'preserves_legacy_history':True,'copies_financial_approvals':False}
    if dry_run: return preview
    if not data.confirmed or data.preview_token!=digest: fail('Review and confirm this exact adaptation preview')
    c=Case(idea_id=i.id,program_id=p.id,data=after);db.add(c);db.flush()
    i.title=data.case.title;i.problem=data.case.description;i.solution=data.case.future_condition or data.case.description;i.owner_id=data.case.owner_id or i.submitter_id
    record(db,p,c,i,user,'ADOPTED',data.reason,{'legacy_idea':before,'after':{'maturity':0,'status':'Draft'},'case':after,'legacy_financials_retained':True})
    if data.case.owner_id: notify(db,p,i,[data.case.owner_id],'Assignment','You are accountable for '+i.reference)
    return view(db,p,c,i,user,True)

@router.get('/ideas/{id}/legacy')
def legacy_record(id:str,user=Depends(current_user),db=Depends(get_db)):
    p,c,i=case(db,user,id,needed=REPORTING|{'Contributor','Functional'})
    adoption=db.scalar(select(IdeaEvent).where(IdeaEvent.idea_id==id,IdeaEvent.event_type=='VAVE_ADOPTED'))
    if not adoption: fail('This idea has no prior IdeaFlow record',404)
    from .models import FinancialPlan,PlanPeriod,ValuePeriod,Task,Comment
    cost=bool(roles(p,user)&REPORTING) or user.id in (c.data['owner_id'],i.submitter_id)
    result={'idea':adoption.changes['legacy_idea'],'adapted_at':adoption.occurred_at,'reason':adoption.reason,'tasks':[serialize(t) for t in db.scalars(select(Task).where(Task.idea_id==id))],'comments':[serialize(t) for t in db.scalars(select(Comment).where(Comment.idea_id==id))]}
    if cost:
        plans=list(db.scalars(select(FinancialPlan).where(FinancialPlan.idea_id==id)))
        result.update(plans=[serialize(t) for t in plans],periods=[serialize(t) for t in db.scalars(select(PlanPeriod).where(PlanPeriod.plan_id.in_([p.id for p in plans])))],actuals=[serialize(t) for t in db.scalars(select(ValuePeriod).where(ValuePeriod.idea_id==id))])
    return result

def create(db,user,p,data):
    validate_case(db,p,data)
    i=Idea(title=data.title,problem=data.description,solution=data.future_condition or data.description,owner_id=data.owner_id or user.id,submitter_id=user.id,reference=f'IF-{db.scalar(reference_seq.next_value()):05d}',record_version=0)
    db.add(i);db.flush();c=Case(idea_id=i.id,program_id=p.id,data=fields(data));db.add(c);db.flush()
    record(db,p,c,i,user,'CAPTURED','Capture',{'scope':data.scope,'originator_id':user.id})
    return view(db,p,c,i,user,True)

@router.post('/programs/{id}/ideas',status_code=201)
def capture(id:str,data:S.CaseInput,user=Depends(current_user),db=Depends(get_db)):
    p=program(db,user,id,{'Contributor','Manager','External'})
    if roles(p,user)<={'External'}:
        allowed={'title','description','scope','product','category','source','workshop','current_condition','future_condition'}
        if set(data.model_dump(exclude_unset=True))-allowed: fail('External capture is limited to the approved intake fields',403)
    return create(db,user,p,data)

@router.get('/ideas/{id}')
def detail(id:str,user=Depends(current_user),db=Depends(get_db)):
    p,c,i=case(db,user,id);return view(db,p,c,i,user,True)

@router.put('/ideas/{id}')
def edit(id:str,data:S.CaseInput,user=Depends(current_user),db=Depends(get_db)):
    p,c,i=case(db,user,id,data.record_version,{'Contributor','Manager','Finance','Authority','External'})
    if roles(p,user)<={'External'}:
        allowed={'title','description','scope','product','category','source','workshop','current_condition','future_condition','record_version','reason'}
        if c.status!='Draft' or i.submitter_id!=user.id or set(data.model_dump(exclude_unset=True))-allowed: fail('External editing is limited to your own draft intake',403)
        before=copy.deepcopy(c.data);c.data={**c.data,**data.model_dump(mode='json',exclude_unset=True,exclude={'record_version','reason'})}
        i.title=data.title;i.problem=data.description
        record(db,p,c,i,user,'INTAKE_CHANGED',data.reason,{'before':before,'after':c.data})
        return view(db,p,c,i,user,True)
    if user.role!='Admin' and not roles(p,user)&{'Manager','Finance','Authority'} and user.id not in (c.data['owner_id'],i.submitter_id): fail('Only the owner or program decision team may edit this case',403)
    validate_case(db,p,data,id);before=copy.deepcopy(c.data);after=fields(data)
    old_ids={a['id'] for a in before['applications']}
    if c.actuals and any(aid not in {a['id'] for a in after['applications']} for aid in old_ids): fail('Applications with financial history must be retained and excluded explicitly')
    if before['priority']!=after['priority'] and not after['priority_reason']: fail('Priority overrides require a reason')
    material_change=material(before)!=material(after)
    if material_change and (c.approved or c.maturity>=2) and not data.reason: fail('Material changes require a reason and reapproval')
    c.data=after;i.title=data.title;i.problem=data.description;i.owner_id=data.owner_id or i.submitter_id
    if material_change:
        c.reviews={};c.approved=None
        prior_actuals=copy.deepcopy(c.actuals)
        c.actuals={k:{**v,'verified_at':None,'verified_by':None,'verification_invalidated':'Business case changed; reapproval required'} for k,v in c.actuals.items()}
    record(db,p,c,i,user,'CASE_CHANGED',data.reason,{'before':before,'after':after,'approvals_flagged':material_change,'prior_actuals':prior_actuals if material_change else None})
    if material_change:
        notify(db,p,i,[m['user_id'] for m in p.data['members'] if set(m['roles'])&{'Manager','Finance','Functional','Authority'}],'Material change',i.reference+': approvals require review — '+data.reason)
    if data.owner_id and before['owner_id']!=data.owner_id: notify(db,p,i,[data.owner_id],'Assignment','You are accountable for '+i.reference)
    for a in after['actions']:
        old=next((r for r in before['actions'] if r['id']==a['id']),None)
        if not old or old['owner_id']!=a['owner_id']: notify(db,p,i,[a['owner_id']],'Assignment',a['title'])
    return view(db,p,c,i,user,True)

@router.post('/ideas/{id}/commands')
def command(id:str,data:S.Command,user=Depends(current_user),db=Depends(get_db)):
    p,c,i=case(db,user,id,needed={'Manager','Contributor','Functional','Finance','Authority','External'})
    if i.record_version!=data.record_version: fail('Idea changed; refresh before deciding',409)
    if roles(p,user)<={'External'} and (data.action!='Submit' or i.submitter_id!=user.id): fail('External participation is limited to your own draft submission',403)
    before={'maturity':c.maturity,'status':c.status}; rs=roles(p,user)
    if data.action in ('Review','Request review','Advance'):
        target=data.target or min(c.maturity+1,6)
        reapproval=c.approved is None and target<=c.maturity and target>=3
        if target!=c.maturity+1 and not reapproval: fail('Gates are sequential; use a recorded reopening for rework')
        if c.status!='Active': fail('Submit or resume the active idea before gate review')
        if data.action=='Request review':
            notify(db,p,i,[m['user_id'] for m in p.data['members'] if set(m['roles'])&set(requirement_roles(p,c,target))],'Review request','Review '+i.reference+' for M'+str(target))
        elif data.action=='Review':
            role=data.role
            if role not in requirement_roles(p,c,target) or role not in rs: fail('You are not an assigned reviewer for this gate',403)
            if role=='Finance' and user.id==c.data['owner_id']: fail('Financial review requires a person independent of the accountable owner',403)
            unmet=missing(db,p,c,target,False)
            if unmet: fail('; '.join(unmet))
            c.reviews={**c.reviews,str(target)+'|'+role:{'actor_id':user.id,'time':now().isoformat(),'signature':signature(c),'reason':data.reason}}
        else:
            if not rs & {'Manager','Authority'}: fail('A Manager or decision authority must pass the gate',403)
            unmet=missing(db,p,c,target)
            if unmet: fail('; '.join(unmet))
            c.maturity=max(c.maturity,target)
            if target>=3: c.approved={'signature':signature(c),'data':copy.deepcopy(c.data),'time':now().isoformat(),'reviews':copy.deepcopy(c.reviews),'maturity':target}
    elif data.action=='Submit':
        if c.status!='Draft': fail('Only drafts can be submitted')
        c.status='Active'
        notify(db,p,i,[m['user_id'] for m in p.data['members'] if 'Manager' in m['roles']],'Screening','Unassigned submission: '+i.reference)
    elif data.action=='Hold':
        if c.status!='Active' or not c.data['hold_owner_id'] or not c.data['hold_review_date']: fail('Active holds need a responsible owner and review date')
        c.status='On hold'
    elif data.action=='Resume':
        if c.status!='On hold': fail('Only held work can resume')
        c.status='Active'
    elif data.action in ('Reject','Cancel','Supersede','Close'):
        if 'Manager' not in rs: fail('Program Manager decision required',403)
        if not c.data['final_disposition'] or not c.data['lessons']: fail('Record final disposition and lessons learned')
        if data.action=='Supersede' and not c.data['duplicate_of']: fail('Link the surviving idea before superseding')
        c.status={'Reject':'Rejected','Cancel':'Cancelled','Supersede':'Superseded','Close':'Closed'}[data.action]
    elif data.action in ('Reopen','Return'):
        if not rs & {'Manager','Finance','Functional','Authority'}: fail('Review authority required',403)
        maturity=max(0,(data.target if data.target is not None else c.maturity)-1)
        if maturity>c.maturity: fail('Reopen and Return cannot advance maturity; pass sequential gates with the required reviews')
        c.status='Active';c.maturity=maturity;c.reviews={};c.approved=None
        if c.data['owner_id']: notify(db,p,i,[c.data['owner_id']],'Returned decision',i.reference+': '+data.reason)
    else: fail('Unknown VAVE command')
    record(db,p,c,i,user,data.action.upper().replace(' ','_'),data.reason,{'before':before,'after':{'maturity':c.maturity,'status':c.status},'target':data.target,'role':data.role,'snapshot':copy.deepcopy(c.data) if data.action in ('Advance','Review') else None})
    return view(db,p,c,i,user,True)

@router.post('/ideas/{id}/actuals')
def actual(id:str,data:S.ActualInput,user=Depends(current_user),db=Depends(get_db)):
    p,c,i=case(db,user,id,data.record_version,{'Contributor','Manager','Finance'})
    if data.month.day!=1 or data.month>=app_today().replace(day=1): fail('Actuals require a fully elapsed month')
    a=next((a for a in c.data['applications'] if a['id']==data.application_id),None)
    if not a or a['rollout']!='In production' or not a['effective_date'] or data.month.strftime('%Y-%m')<a['effective_date'][:7]: fail('Actuals need an application in production for this month')
    if not p.data['start'][:7]<=data.month.strftime('%Y-%m')<=p.data['end'][:7] or not any(r['month']==data.month.isoformat() for r in a['periods']): fail('Actuals must belong to an approved application observation period within the program horizon')
    if not c.approved: fail('Reapprove the business case before reporting comparable actuals')
    key=a['id']+'|'+data.month.isoformat();old=copy.deepcopy(c.actuals.get(key))
    values=fields(data);gross=(Decimal(a['baseline'])-data.actual_cost)*data.volume*Decimal(a['usage'])*Decimal(a['conversion'])
    values.update(gross=str(gross),net=str(gross-data.recurring-data.giveback),cash=str(gross-data.recurring-data.giveback-data.spend),actor_id=user.id,verified_at=None,verified_by=None,baseline_signature=signature(c))
    c.actuals={**c.actuals,key:values};record(db,p,c,i,user,'ACTUAL_RECORDED',data.reason,{'key':key,'before':old,'after':values})
    return view(db,p,c,i,user,True)

@router.post('/ideas/{id}/feasibility')
def functional_evidence(id:str,data:S.FeasibilityInput,user=Depends(current_user),db=Depends(get_db)):
    p,c,i=case(db,user,id,data.record_version,{'Functional','Manager'})
    before=copy.deepcopy(c.data['feasibility']);after={k:v.strip() for k,v in data.evidence.items()}
    if set(after)-set(p.data['mandatory_evidence']): fail('Use the program mandatory evidence topics')
    c.data={**c.data,'feasibility':after};c.reviews={};c.approved=None
    previous_actuals=copy.deepcopy(c.actuals)
    c.actuals={k:{**v,'verified_at':None,'verified_by':None} for k,v in c.actuals.items()}
    record(db,p,c,i,user,'FUNCTIONAL_EVIDENCE',data.reason,{'before':before,'after':after,'previous_actuals':previous_actuals})
    return view(db,p,c,i,user,True)

@router.post('/ideas/{id}/actions/{action_id}')
def action_update(id:str,action_id:str,data:S.ActionCommand,user=Depends(current_user),db=Depends(get_db)):
    p,c,i=case(db,user,id,data.record_version,{'Contributor','Manager','Functional','Finance','Authority'})
    old=next((a for a in c.data['actions'] if a['id']==action_id),None)
    if not old: fail('Action not found',404)
    if old['owner_id']!=user.id and 'Manager' not in roles(p,user): fail('Only the action owner or Manager can update it',403)
    if data.status=='Done' and old['dependency'] and not any(a['id']==old['dependency'] and a['status']=='Done' for a in c.data['actions']): fail('Complete predecessor actions first')
    after={**old,'status':data.status,'evidence':data.evidence};c.data={**c.data,'actions':[after if a['id']==action_id else a for a in c.data['actions']]}
    record(db,p,c,i,user,'ACTION_CHANGED',data.reason,{'before':old,'after':after})
    return view(db,p,c,i,user,True)

@router.post('/ideas/{id}/actuals/{application_id}/{month}/verify')
def verify(id:str,application_id:str,month:date,data:S.Command,user=Depends(current_user),db=Depends(get_db)):
    p,c,i=case(db,user,id,data.record_version,{'Finance'});key=application_id+'|'+month.isoformat();r=c.actuals.get(key)
    if not r: fail('Record actual quantities, costs and evidence first')
    application=next((a for a in c.data['applications'] if a['id']==application_id),None)
    if user.id in (r['actor_id'],c.data['owner_id'],application['owner_id'] if application else None): fail('You cannot verify your own financial submission, owned idea or owned application',403)
    if not c.approved or r['baseline_signature']!=signature(c): fail('Reapprove the comparable baseline and re-record corrected actuals')
    after={**r,'verified_at':now().isoformat(),'verified_by':user.id,'verification_reason':data.reason}
    if data.action=='Revoke': after.update(verified_at=None,verified_by=None)
    c.actuals={**c.actuals,key:after};record(db,p,c,i,user,'RESULT_VERIFIED' if data.action!='Revoke' else 'VERIFICATION_REVOKED',data.reason,{'key':key,'before':r,'after':after})
    return view(db,p,c,i,user,True)

@router.post('/ideas/{id}/evidence')
def attach(id:str,data:S.EvidenceInput,user=Depends(current_user),db=Depends(get_db)):
    p,c,i=case(db,user,id,data.record_version,{'Contributor','Manager','Functional','Finance','Authority'})
    try: content=base64.b64decode(data.content_base64,validate=True)
    except ValueError: fail('Invalid file encoding')
    if not content or len(content)>5*1024*1024: fail('Files must be between 1 byte and 5 MiB')
    name=data.name.replace('\\','/').split('/')[-1]
    e=Evidence(idea_id=id,name=name,content=content,sha256=hashlib.sha256(content).hexdigest(),shared=data.shared);db.add(e);db.flush()
    record(db,p,c,i,user,'EVIDENCE_ATTACHED','Supporting file',{'id':e.id,'name':name,'sha256':e.sha256,'shared':e.shared})
    return view(db,p,c,i,user,True)

@router.get('/evidence/{id}')
def download(id:str,user=Depends(current_user),db=Depends(get_db)):
    e=db.get(Evidence,id)
    if not e: fail('Evidence not found',404)
    p,c,i=case(db,user,e.idea_id)
    if roles(p,user)<={'External'} and not e.shared: fail('Evidence not found',404)
    return Response(e.content,media_type='application/octet-stream',headers={'Content-Disposition':"attachment; filename*=UTF-8''"+__import__('urllib.parse',fromlist=['quote']).quote(e.name),'Content-Security-Policy':"default-src 'none'; sandbox"})

@router.post('/ideas/{id}/discussion')
def discussion(id:str,data:S.Discussion,user=Depends(current_user),db=Depends(get_db)):
    p,c,i=case(db,user,id,data.record_version,{'Contributor','Manager','Functional','Finance','Authority'})
    notify(db,p,i,data.mentions,'Mention',i.reference+': '+data.body[:240])
    record(db,p,c,i,user,'DISCUSSION','Discussion / meeting decision',{'body':data.body,'mentions':data.mentions,'shared':data.shared})
    return view(db,p,c,i,user,True)

@router.get('/notices')
def notices(user=Depends(current_user),db=Depends(get_db)):
    pref=db.get(Preference,user.id)
    for c in db.scalars(select(Case).where(Case.status.in_(['Active','On hold']))):
        p=db.get(Program,c.program_id)
        if not roles(p,user) or roles(p,user)<={'External'}: continue
        deadlines=[a for a in c.data['actions'] if a['owner_id']==user.id and a['status']!='Done']
        if c.data['owner_id']==user.id and c.data['due_date']:
            deadlines.append({'id':'idea','title':i.reference if (i:=db.get(Idea,c.idea_id)) else 'Idea review','due_date':c.data['due_date'],'owner_id':user.id,'status':'Open'})
        for a in deadlines:
            if a['owner_id']!=user.id or a['status']=='Done': continue
            days=(date.fromisoformat(a['due_date'])-app_today()).days
            if days>7 or (days>=0 and pref and not pref.data.get('routine_notices',True)): continue
            kind='Overdue action' if days<0 else 'Approaching deadline'
            notice_id=hashlib.sha256((c.idea_id+a['id']+a['due_date']+user.id+kind).encode()).hexdigest()[:36]
            if not db.get(Notice,notice_id): db.add(Notice(id=notice_id,user_id=user.id,idea_id=c.idea_id,data={'kind':kind,'message':a['title']+' · Due '+a['due_date'],'time':now().isoformat(),'mandatory':days<0}))
        if 'Manager' in roles(p,user):
            i=db.get(Idea,c.idea_id)
            issue='Unassigned submission' if not c.data['owner_id'] else 'Blocked milestone' if c.data['blocker'] else 'Forecast slippage' if c.data['schedule_health']!='On track' else 'Stale review' if (app_today()-i.updated_at.date()).days>=p.data['stale_days'] else ''
            if issue:
                notice_id=hashlib.sha256((c.idea_id+user.id+issue+str(i.record_version)).encode()).hexdigest()[:36]
                if not db.get(Notice,notice_id): db.add(Notice(id=notice_id,user_id=user.id,idea_id=c.idea_id,data={'kind':issue,'message':i.reference+': '+(c.data['blocker'] or c.data['next_action'] or 'Assign an owner, decision and date'),'time':now().isoformat(),'mandatory':True}))
    db.flush()
    result=[]
    for n in db.scalars(select(Notice).where(Notice.user_id==user.id).order_by(Notice.id)):
        c=db.get(Case,n.idea_id);p=db.get(Program,c.program_id)
        if roles(p,user) and (not roles(p,user)<={'External'} or c.data['shared']): result.append(serialize(n))
    return result

@router.get('/work')
def my_work(user=Depends(current_user),db=Depends(get_db)):
    owned=[];actions=[];reviews=[];screening=[]
    for c in db.scalars(select(Case).where(Case.status.in_(['Draft','Active','On hold']))):
        p=db.get(Program,c.program_id);rs=roles(p,user)
        if not rs or rs<={'External'}: continue
        i=db.get(Idea,c.idea_id);row={'id':i.id,'reference':i.reference,'title':c.data['title'],'program':p.data['name'],'next_action':c.data['next_action'],'due_date':c.data['due_date'],'status':c.status,'maturity':c.maturity}
        if c.data['owner_id']==user.id: owned.append(row)
        if not c.data['owner_id'] and 'Manager' in rs: screening.append(row)
        actions += [{**row,'action':a} for a in c.data['actions'] if a['owner_id']==user.id and a['status']!='Done']
        target=min(c.maturity+1,6)
        for role in requirement_roles(p,c,target):
            if c.status=='Active' and role in rs and str(target)+'|'+role not in c.reviews: reviews.append({**row,'gate':target,'role':role,'missing':missing(db,p,c,target,False)})
    for rows in (owned,screening,reviews): rows.sort(key=lambda r:r['due_date'] or '9999-12-31')
    actions.sort(key=lambda r:r['action']['due_date'])
    return {'owned':owned,'actions':actions,'reviews':reviews,'screening':screening}

@router.post('/notices/{id}/read')
def read_notice(id:str,user=Depends(current_user),db=Depends(get_db)):
    n=db.get(Notice,id)
    if not n or n.user_id!=user.id: fail('Notice not found',404)
    n.read=True;return {'ok':True}

@router.get('/preferences')
def preferences(user=Depends(current_user),db=Depends(get_db)):
    p=db.get(Preference,user.id);return serialize(p) if p else {'record_version':0,'data':{'views':[],'routine_notices':True}}

@router.put('/preferences')
def save_preferences(data:dict,user=Depends(current_user),db=Depends(get_db)):
    p=db.scalar(select(Preference).where(Preference.user_id==user.id).with_for_update())
    if data.get('record_version')!=(p.record_version if p else 0): fail('Preferences changed; refresh',409)
    value=data.get('data',{})
    if set(value)-{'views','routine_notices'} or len(json.dumps(value))>20000: fail('Invalid preferences')
    if not p: p=Preference(user_id=user.id,record_version=1,data=value);db.add(p)
    else: p.record_version+=1;p.data=value
    return serialize(p)

@router.get('/programs/{id}/report')
def report(id:str,request:Request,start:date|None=None,end:date|None=None,product:str='',plant:str='',user=Depends(current_user),db=Depends(get_db)):
    p=program(db,user,id,REPORTING);start=start or date.fromisoformat(p.data['start']);end=end or date.fromisoformat(p.data['end'])
    if end<start or (end.year-start.year)*12+end.month-start.month>119: fail('Select a reporting range of at most 120 months')
    totals={t:{'opportunity':Decimal(0),'approved_forecast':Decimal(0),'implemented':Decimal(0),'verified':Decimal(0),'spend':Decimal(0),'known_applications':0,'unknown_applications':0} for t in ('Cost reduction','Cost avoidance','Working capital','Capacity','Revenue','Nonfinancial')}
    rows=[];all_cases=list(db.scalars(select(Case).where(Case.program_id==id)));cases=[c for c in all_cases if (not product or c.data['product']==product) and (not plant or any(a['plant']==plant for a in c.data['applications']))];today=app_today();exceptions=[]
    for c in cases:
        if product and c.data['product']!=product: continue
        i=db.get(Idea,c.idea_id)
        if not c.data['owner_id'] or (c.data['due_date'] and c.data['due_date']<today.isoformat()) or c.data['blocker'] or (today-i.updated_at.date()).days>=p.data['stale_days'] or any(a['due_date']<today.isoformat() and a['status']!='Done' for a in c.data['actions']):
            exceptions.append({'id':i.id,'reference':i.reference,'owner_id':c.data['owner_id'],'next_action':c.data['next_action'],'due_date':c.data['due_date'],'blocker':c.data['blocker'],'schedule_health':c.data['schedule_health'],'open_actions':[a for a in c.data['actions'] if a['status']!='Done']})
        for a in c.data['applications']:
            if plant and a['plant']!=plant: continue
            calc=calculations(a);native=Decimal(0);forecast=Decimal(0);implemented=Decimal(0);actual_total=Decimal(0);verified_total=Decimal(0);spend=Decimal(0);eligible=reported=verified=0
            parent=any(other.data.get('parent_id')==c.idea_id for other in all_cases)
            excluded= 'Unselected alternative' if not a['selected'] else 'Duplicate concept' if c.data['duplicate_of'] else 'Parent allocation' if parent else 'Archived forecast' if c.status in ('Rejected','Cancelled','Superseded','Closed') else ''
            monetary=a['value_type'] not in ('Capacity','Nonfinancial') or bool(a['mechanism'])
            for r in calc['periods']:
                if not start.strftime('%Y-%m')<=r['month'][:7]<=end.strftime('%Y-%m'): continue
                if r['net'] is not None: native+=r['net']
                if c.approved and not excluded and monetary and r['net'] is not None: forecast+=r['net'];spend+=r['spend']
                if c.approved and not excluded and a['rollout']=='In production' and monetary and r['net'] is not None: implemented+=r['net']
                if r['eligible_volume']>0 and r['month']<today.replace(day=1).isoformat(): eligible+=1
                value=c.actuals.get(a['id']+'|'+r['month'])
                if value:
                    reported+=1;actual_total+=Decimal(value['net'])
                    if value.get('verified_at'): verified+=1;verified_total+=Decimal(value['net'])
            fx=Decimal(a['fx_rate']);t=totals[a['value_type']]
            if not excluded and monetary:
                if any(r['net'] is None for r in calc['periods']) or not calc['periods']: t['unknown_applications']+=1
                else: t['known_applications']+=1
                t['opportunity']+=native*fx
            t['approved_forecast']+=forecast*fx;t['implemented']+=implemented*fx;t['spend']+=spend*fx
            if a['selected'] and not c.data['duplicate_of'] and not parent and monetary: t['verified']+=verified_total*fx
            rows.append({'idea_id':i.id,'reference':i.reference,'application_id':a['id'],'scope':a['scope'],'product':c.data['product'],'part':a['part'],'plant':a['plant'],'value_type':a['value_type'],'currency':a['currency'],'fx_rate':a['fx_rate'],'excluded':excluded,'forecast_version':c.approved['time'] if c.approved else None,'native_opportunity':native,'approved_forecast':forecast*fx,'implemented':implemented*fx,'actual':actual_total*fx if reported else None,'verified':verified_total*fx if verified else None,'eligible_periods':eligible,'reported_periods':reported,'verified_periods':verified,'calculation':calc})
    target_rows=[]
    for t in totals.values():
        if t['unknown_applications'] and not t['known_applications']: t['opportunity']=None
    for target in p.data['targets']:
        if target['start']!=start.isoformat() or target['end']!=end.isoformat() or target['metric']!='In-year net recurring benefit': continue
        target_rows.append(target)
    target_totals={}
    for value_type in totals:
        roots=[Decimal(t['amount']) for t in target_rows if t['scope']=='Program' and t['value_type']==value_type]
        allocated=sum(Decimal(t['amount']) for t in target_rows if t['scope']!='Program' and not t['additional'] and t['value_type']==value_type)
        additional=sum(Decimal(t['amount']) for t in target_rows if t['additional'] and t['scope']!='Program' and t['value_type']==value_type)
        matching=[t for t in target_rows if t['value_type']==value_type]
        scoped=[Decimal(t['amount']) for t in matching if product and t['scope']==product]
        value=None if plant or (product and not scoped) or not matching else sum(scoped) if product else max(roots or [allocated])+additional
        target_totals[value_type]={'target':value,'allocated_child':allocated,'additional':additional}
    distribution=[{'maturity':m,'name':LEVELS[m],'count':sum(c.maturity==m for c in cases)} for m in range(7)]
    gate_times=[]
    for c in cases:
        events=list(db.scalars(select(IdeaEvent).where(IdeaEvent.idea_id==c.idea_id,IdeaEvent.event_type=='VAVE_ADVANCE').order_by(IdeaEvent.sequence)))
        capture=db.scalar(select(IdeaEvent).where(IdeaEvent.idea_id==c.idea_id,IdeaEvent.event_type.in_(['VAVE_CAPTURED','VAVE_ADOPTED'])).order_by(IdeaEvent.sequence))
        previous=capture.occurred_at if capture else db.get(Idea,c.idea_id).created_at
        for e in events:
            gate_times.append({'idea_id':c.idea_id,'maturity':e.changes['after']['maturity'],'days':round((e.occurred_at-previous).total_seconds()/86400,2)});previous=e.occurred_at
    return {'as_of':now(),'currency':p.data['currency'],'fx_basis':p.data['fx_basis'],'start':start,'end':end,'metric':'In-year net recurring benefit; cash spend separate; value types never added together','scope':p.data['scope'],'filters':{'product':product,'plant':plant},'target_scope':'Program targets for the stated metric and period; filtered targets require a matching scoped definition','totals':totals,'applications':rows,'targets':target_totals,'target_definitions':p.data['targets'],'distribution':distribution,'exceptions':exceptions,'gate_times':gate_times,'cohort':{'definition':'Filtered program submissions; cumulative gate attainment from immutable decisions','submissions':len(cases),'attained':[len({e.idea_id for e in db.scalars(select(IdeaEvent).where(IdeaEvent.idea_id.in_([c.idea_id for c in cases]),IdeaEvent.event_type=='VAVE_ADVANCE')) if e.changes['after']['maturity']>=m}) for m in range(1,7)]}}

@router.get('/programs/{id}/export')
def export(id:str,request:Request,search:str='',user=Depends(current_user),db=Depends(get_db)):
    from .main import csv_response
    params=request.query_params
    try: maturity=int(params['maturity']) if params.get('maturity') else None
    except ValueError: fail('Invalid maturity filter')
    rows=register(id,search=search,maturity=maturity,status=params.get('status',''),product=params.get('product',''),plant=params.get('plant',''),mine=params.get('mine')=='true',category=params.get('category',''),owner_id=params.get('owner_id',''),part=params.get('part',''),supplier=params.get('supplier',''),sort=params.get('sort','updated'),user=user,db=db)
    return csv_response([{'reference':r['reference'],'title':r['data']['title'],'scope':r['data']['scope'],'maturity':'M'+str(r['maturity']),'status':r['status']} for r in rows],['reference','title','scope','maturity','status'],'vave-register.csv')

@router.post('/programs/{id}/import')
def import_records(id:str,data:dict,dry_run:bool=True,user=Depends(current_user),db=Depends(get_db)):
    p=program(db,user,id,{'Manager'});mapping=data.get('mapping',{});records=data.get('rows',[])
    if not records or len(records)>500: fail('Supply between 1 and 500 rows')
    allowed={'title','description','scope','product','assembly','category','source','workshop','current_condition','future_condition'}
    if set(mapping)-allowed: fail('Only capture fields can be mapped; approvals and results cannot be imported')
    errors=[];parsed=[];duplicates=[];titles={c.data['title'].casefold() for c in db.scalars(select(Case).where(Case.program_id==id))}
    for n,row in enumerate(records):
        try:
            item=S.CaseInput.model_validate({k:row.get(v,'') for k,v in mapping.items()});parsed.append(item)
            if item.title.casefold() in titles: duplicates.append({'row':n+1,'title':item.title})
            titles.add(item.title.casefold())
        except Exception: errors.append({'row':n+1,'message':'Title, description and affected scope required; review field mapping'})
    digest=hashlib.sha256(json.dumps({'mapping':mapping,'rows':records},sort_keys=True).encode()).hexdigest()
    existing=db.scalar(select(ProgramEvent).where(ProgramEvent.program_id==id,ProgramEvent.data['import_digest'].as_string()==digest))
    preview={'count':len(parsed),'errors':errors,'duplicates':duplicates,'preview_token':digest,'already_imported':bool(existing)}
    if dry_run or errors or existing: return preview
    if data.get('preview_token')!=digest or not data.get('confirmed'): fail('Validate this exact mapping and confirm the preview before applying')
    if duplicates and not data.get('accept_duplicates'): fail('Review possible duplicates and explicitly accept them')
    created=[create(db,user,p,item)['reference'] for item in parsed]
    db.add(ProgramEvent(program_id=id,actor_id=user.id,data={'time':now().isoformat(),'import_digest':digest,'references':created}))
    return {**preview,'created':created}
