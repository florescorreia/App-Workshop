import os, secrets, csv, io
from decimal import Decimal
from datetime import date, datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, Request, Response, Query
from fastapi.responses import StreamingResponse
from fastapi.openapi.docs import get_swagger_ui_html
from sqlalchemy import select, text, func, or_, and_
from sqlalchemy.exc import IntegrityError
from .db import get_db, now
from .models import User, Session, Idea, Site, Category, Task, Comment, IdeaEvent, PlanPeriod, ValuePeriod, DemoBatch
from . import schemas as S, domain as D
from .auth import current_user, require, public_user, hasher, digest
from .queries import serialize, idea_row, selected_ideas, value_dashboard
from .financial import ramp, app_today
from .process import discover

app=FastAPI(title='IdeaFlow',version='1.0.0',docs_url=None,openapi_url='/api/openapi.json',redoc_url=None)
P='/api/v1'

@app.get('/api/docs',include_in_schema=False)
def api_docs():
    return get_swagger_ui_html(openapi_url=app.openapi_url,title='IdeaFlow API',swagger_js_url='/vendor/swagger-ui-bundle.js',swagger_css_url='/vendor/swagger-ui.css',swagger_favicon_url='/vendor/favicon-32x32.png',swagger_ui_parameters={'validatorUrl':None})

@app.middleware('http')
async def origin_defense(request,call_next):
    if request.method not in ('GET','HEAD','OPTIONS'):
        origin=request.headers.get('origin')
        if origin and origin != str(request.base_url).rstrip('/'):
            return __import__('starlette.responses',fromlist=['JSONResponse']).JSONResponse({'detail':'Same-origin requests required'},403)
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Cache-Control']='no-store' if request.url.path.startswith('/api/v1') else 'no-cache'
    return response

@app.exception_handler(IntegrityError)
async def integrity_handler(request,exc):
    return __import__('starlette.responses',fromlist=['JSONResponse']).JSONResponse({'detail':'This change conflicts with an existing record or validation rule. Refresh and check the fields.'},409)

@app.get('/api/health/live')
def live(): return {'status':'live','version':'1.0.0'}
@app.get('/api/health/ready')
def ready(db=Depends(get_db)):
    if db.scalar(text('SELECT version_num FROM alembic_version'))!='0001': raise HTTPException(503,'Migration not ready')
    return {'status':'ready','version':'1.0.0'}

@app.post(P+'/session/login')
def login(data:S.Login,response:Response,request:Request,db=Depends(get_db)):
    user=db.scalar(select(User).where(User.email==data.email.lower()))
    valid=False
    if user and user.active:
        try: valid=hasher.verify(user.password_hash,data.password)
        except Exception: pass
    if not valid: raise HTTPException(401,'Email or password is incorrect')
    token=secrets.token_urlsafe(32);csrf=secrets.token_urlsafe(32)
    db.add(Session(token_hash=digest(token),user_id=user.id,csrf=csrf,expires_at=now()+timedelta(hours=12)))
    response.set_cookie('ideaflow_session',token,httponly=True,samesite='strict',secure=request.url.scheme=='https',max_age=43200,path='/')
    return {'user':public_user(user),'csrf':csrf,'timezone':os.getenv('APP_TIMEZONE','America/New_York')}
@app.get(P+'/session/me')
def me(request:Request,user=Depends(current_user)):
    return {'user':public_user(user),'csrf':request.state.session.csrf,'timezone':os.getenv('APP_TIMEZONE','America/New_York')}
@app.post(P+'/session/logout')
def logout(response:Response,request:Request,user=Depends(current_user),db=Depends(get_db)):
    db.delete(request.state.session);response.delete_cookie('ideaflow_session');return {'ok':True}
@app.post(P+'/users')
def create_user(data:S.UserCreate,user=Depends(current_user),db=Depends(get_db)):
    require(user,'Admin')
    u=User(**data.model_dump(exclude={'password'}),password_hash=hasher.hash(data.password));u.email=u.email.lower()
    db.add(u);db.flush();return public_user(u)
@app.put(P+'/users/{user_id}')
def update_user(user_id:str,data:S.UserUpdate,user=Depends(current_user),db=Depends(get_db)):
    require(user,'Admin');u=db.scalar(select(User).where(User.id==user_id).with_for_update())
    if not u: D.fail('User not found',404)
    if u.record_version!=data.record_version:D.fail('User changed; refresh before saving',409)
    if u.id==user.id and (not data.active or data.role!='Admin'):D.fail('Keep your own Admin account active')
    u.name=data.name;u.role=data.role;u.active=data.active;u.record_version+=1
    if data.password:u.password_hash=hasher.hash(data.password)
    return public_user(u)
@app.get(P+'/references')
def refs(user=Depends(current_user),db=Depends(get_db)):
    return {'sites':[serialize(x) for x in db.scalars(select(Site))],'categories':[serialize(x) for x in db.scalars(select(Category))],
        'users':[public_user(x) for x in db.scalars(select(User).order_by(User.name))],'stages':D.STAGES}
@app.post(P+'/references/{kind}')
def create_reference(kind:str,data:S.ReferenceInput,user=Depends(current_user),db=Depends(get_db)):
    require(user,'Admin');cls={'sites':Site,'categories':Category}.get(kind)
    if not cls:D.fail('Unknown reference type',404)
    obj=cls(**data.model_dump(exclude=set() if kind=='sites' else {'business_unit'}));db.add(obj);db.flush();return serialize(obj)

def filters(request):
    result=dict(request.query_params)
    for k in ('created_from','created_to'):
        if result.get(k):
            try: date.fromisoformat(result[k])
            except ValueError: D.fail('Invalid creation cohort date')
    return result

@app.get(P+'/ideas')
def list_ideas(request:Request,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),user=Depends(current_user),db=Depends(get_db)):
    selected=selected_ideas(db,filters(request));ids=[i.id for i in selected]
    q=select(Idea).where(Idea.id.in_(ids))
    from .models import FinancialPlan
    latest_net=select(FinancialPlan.annual_gross-FinancialPlan.annual_recurring).where(FinancialPlan.idea_id==Idea.id).order_by(FinancialPlan.version.desc()).limit(1).correlate(Idea).scalar_subquery()
    sort=request.query_params.get('sort','updated')
    ordering={'age':Idea.stage_entered_at.asc(),'annual':latest_net.desc().nulls_last(),'finish':Idea.expected_finish.asc().nulls_last(),'updated':Idea.updated_at.desc()}
    rows=db.scalars(q.order_by(ordering.get(sort,ordering['updated']),Idea.id).offset((page-1)*page_size).limit(page_size))
    totals=dict(db.execute(select(Idea.stage,func.sum(latest_net)).where(Idea.id.in_(ids),Idea.disposition.not_in(['Rejected','Cancelled'])).group_by(Idea.stage)).all())
    stage_totals={stage:D.scalar_json(totals.get(stage)) for stage in D.STAGES}
    return {'items':[idea_row(db,i) for i in rows],'total':len(ids),'page':page,'page_size':page_size,'stage_totals':stage_totals}
@app.post(P+'/ideas',status_code=201)
def create_idea(data:S.IdeaCreate,user=Depends(current_user),db=Depends(get_db)):
    return idea_row(db,D.create_idea(db,user,data))

def csv_response(rows,fields,filename):
    output=io.StringIO();writer=csv.DictWriter(output,fieldnames=fields);writer.writeheader()
    for row in rows:
        safe={k:row.get(k) for k in fields}
        for k,v in safe.items():
            if isinstance(v,str) and v.lstrip().startswith(('=','+','-','@','\t','\r')):safe[k]="'"+v
        writer.writerow(safe)
    return Response(output.getvalue(),media_type='text/csv',headers={'Content-Disposition':f'attachment; filename="{filename}"'})
@app.get(P+'/ideas/export')
def export_ideas(request:Request,user=Depends(current_user),db=Depends(get_db)):
    return csv_response([idea_row(db,i) for i in selected_ideas(db,filters(request))],['reference','title','owner_name','site','stage','disposition','annual_net_potential','expected_finish','stage_age_days'],'ideaflow-register.csv')
@app.get(P+'/events/export')
def export_events(request:Request,all_events:bool=False,user=Depends(current_user),db=Depends(get_db)):
    ids=[i.id for i in selected_ideas(db,filters(request))]
    events=db.scalars(select(IdeaEvent).where(IdeaEvent.idea_id.in_(ids)).order_by(IdeaEvent.idea_id,IdeaEvent.occurred_at,IdeaEvent.sequence,IdeaEvent.id))
    rows=[{'case_id':e.idea_id,'activity':e.activity,'timestamp':e.occurred_at.isoformat(),'resource':db.get(User,e.actor_id).name,'sequence':e.sequence,
        'recorded_at':e.recorded_at.isoformat(),'provenance':str(e.provenance or ''),'event_type':e.event_type} for e in events if all_events or e.event_type in D.LIFECYCLE]
    return csv_response(rows,['case_id','activity','timestamp','resource','sequence','recorded_at','provenance','event_type'],'ideaflow-events.csv')

@app.get(P+'/ideas/{idea_id}')
def get_idea(idea_id:str,user=Depends(current_user),db=Depends(get_db)):
    idea=D.lock_idea(db,idea_id)
    ps=D.plans(db,idea)
    return {**idea_row(db,idea),'plans':[{**serialize(p),'periods':[serialize(r) for r in db.scalars(select(PlanPeriod).where(PlanPeriod.plan_id==p.id).order_by(PlanPeriod.month))]} for p in ps],
        'results':[serialize(r) for r in db.scalars(select(ValuePeriod).where(ValuePeriod.idea_id==idea.id).order_by(ValuePeriod.month))],
        'tasks':[serialize(t) for t in db.scalars(select(Task).where(Task.idea_id==idea.id).order_by(Task.due_date))],
        'comments':[{**serialize(c),'actor_name':db.get(User,c.actor_id).name} for c in db.scalars(select(Comment).where(Comment.idea_id==idea.id).order_by(Comment.created_at))],
        'events':[{**serialize(e),'actor_name':db.get(User,e.actor_id).name} for e in db.scalars(select(IdeaEvent).where(IdeaEvent.idea_id==idea.id).order_by(IdeaEvent.occurred_at,IdeaEvent.sequence,IdeaEvent.id))],
        'transitions':D.allowed(db,user,idea),'financials':value_dashboard(db,[idea])}
@app.put(P+'/ideas/{idea_id}')
def edit_idea(idea_id:str,data:S.IdeaUpdate,user=Depends(current_user),db=Depends(get_db)):
    idea=D.lock_idea(db,idea_id,data.record_version);return idea_row(db,D.update_idea(db,user,idea,data))
@app.get(P+'/ideas/{idea_id}/transitions')
def transitions(idea_id:str,user=Depends(current_user),db=Depends(get_db)):
    return D.allowed(db,user,D.lock_idea(db,idea_id))
@app.post(P+'/ideas/{idea_id}/transitions')
def move(idea_id:str,data:S.Transition,user=Depends(current_user),db=Depends(get_db)):
    idea=D.lock_idea(db,idea_id,data.record_version);return idea_row(db,D.transition(db,user,idea,data))
@app.post(P+'/ideas/{idea_id}/assignment')
def assign(idea_id:str,data:S.Assignment,user=Depends(current_user),db=Depends(get_db)):
    require(user,'Manager','Admin');idea=D.lock_idea(db,idea_id,data.record_version)
    D.references(db,idea.site_id,idea.category_id,data.owner_id);old=idea.owner_id;idea.owner_id=data.owner_id
    D.event(db,idea,user,'ASSIGNED',changes={'owner_id':{'old':old,'new':data.owner_id}});return idea_row(db,idea)
@app.post(P+'/ideas/{idea_id}/tasks')
def create_task(idea_id:str,data:S.TaskInput,user=Depends(current_user),db=Depends(get_db)):
    return serialize(D.save_task(db,user,D.lock_idea(db,idea_id,data.record_version),data))
@app.put(P+'/ideas/{idea_id}/tasks/{task_id}')
def edit_task(idea_id:str,task_id:str,data:S.TaskInput,user=Depends(current_user),db=Depends(get_db)):
    return serialize(D.save_task(db,user,D.lock_idea(db,idea_id,data.record_version),data,task_id))
@app.post(P+'/ideas/{idea_id}/comments')
def comment(idea_id:str,data:S.CommentInput,user=Depends(current_user),db=Depends(get_db)):
    return serialize(D.add_comment(db,user,D.lock_idea(db,idea_id,data.record_version),data.body))
@app.post(P+'/financial/ramp')
def generate_ramp(data:S.RampInput,user=Depends(current_user)):
    return {'periods':ramp(data)}
@app.post(P+'/ideas/{idea_id}/plans')
def save_plan(idea_id:str,data:S.PlanInput,user=Depends(current_user),db=Depends(get_db)):
    return serialize(D.save_plan(db,user,D.lock_idea(db,idea_id,data.record_version),data))
@app.post(P+'/ideas/{idea_id}/plans/approve')
def reapprove(idea_id:str,data:S.Command,user=Depends(current_user),db=Depends(get_db)):
    idea=D.lock_idea(db,idea_id,data.record_version)
    if idea.stage in ('New','Screening','Analysis'):D.fail('Advance Analysis to Approved to approve the first plan atomically')
    return serialize(D.approve_plan(db,user,idea,data.reason))
@app.put(P+'/ideas/{idea_id}/results/{month}')
def save_result(idea_id:str,month:date,data:S.ResultInput,user=Depends(current_user),db=Depends(get_db)):
    return serialize(D.save_result(db,user,D.lock_idea(db,idea_id,data.record_version),month,data))
@app.post(P+'/ideas/{idea_id}/results/{month}/verify')
def verify(idea_id:str,month:date,data:S.VerifyInput,user=Depends(current_user),db=Depends(get_db)):
    return serialize(D.verify_result(db,user,D.lock_idea(db,idea_id,data.record_version),month,data))
@app.post(P+'/ideas/{idea_id}/results/{month}/revoke')
def revoke(idea_id:str,month:date,data:S.RevokeInput,user=Depends(current_user),db=Depends(get_db)):
    return serialize(D.verify_result(db,user,D.lock_idea(db,idea_id,data.record_version),month,data,True))

def parse_as_of(value):
    if not value:return now()
    try:
        result=datetime.fromisoformat(value.replace('Z','+00:00'))
        if not result.tzinfo: result=result.replace(tzinfo=timezone.utc)
        if result>now():D.fail('As-of timestamp cannot be in the future')
        return result
    except ValueError:D.fail('Use an ISO as-of timestamp')
@app.get(P+'/dashboards/value')
def value(request:Request,start:date|None=None,end:date|None=None,include_hold:bool=True,as_of:str|None=None,user=Depends(current_user),db=Depends(get_db)):
    return value_dashboard(db,selected_ideas(db,filters(request)),start,end,include_hold,parse_as_of(as_of))
@app.get(P+'/dashboards/portfolio')
def portfolio(request:Request,start:date|None=None,end:date|None=None,include_hold:bool=True,user=Depends(current_user),db=Depends(get_db)):
    ideas=selected_ideas(db,filters(request));rows=[idea_row(db,i) for i in ideas];today=app_today()
    active=[r for r in rows if r['disposition'] in ('Active','On hold') and r['stage']!='Realized']
    overdue=[r for r in active if r['expected_finish'] and r['expected_finish']<today.isoformat()]
    return {'as_of':now(),'stages':[{'stage':s,'count':sum(r['stage']==s for r in rows),'annual_net_potential':sum((Decimal(r['annual_net_potential']) for r in rows if r['stage']==s and r['annual_net_potential'] is not None and r['disposition'] not in ('Rejected','Cancelled')),Decimal(0))} for s in D.STAGES],
        'active_count':len(active),'overdue_count':len(overdue),'open_approvals':sum(i.stage=='Analysis' and i.disposition=='Active' for i in ideas),
        'active_ids':[r['id'] for r in active],'overdue_ids':[r['id'] for r in overdue],'approval_ids':[i.id for i in ideas if i.stage=='Analysis' and i.disposition=='Active'],
        'top_opportunities':sorted(active,key=lambda r:float(r['annual_net_potential'] or -1),reverse=True)[:8],
        'exceptions':overdue+[r for r in active if r['disposition']=='On hold'],'value':value_dashboard(db,ideas,start,end,include_hold)}
@app.get(P+'/dashboards/process')
def process(request:Request,as_of:str|None=None,basis:str=Query('calendar',pattern='^(calendar|active)$'),completed_only:bool=False,user=Depends(current_user),db=Depends(get_db)):
    ideas=selected_ideas(db,filters(request));events=list(db.scalars(select(IdeaEvent).where(IdeaEvent.idea_id.in_([i.id for i in ideas]))))
    return discover(ideas,events,parse_as_of(as_of),basis,completed_only)
@app.get(P+'/my-work')
def my_work(user=Depends(current_user),db=Depends(get_db)):
    ideas=list(db.scalars(select(Idea).where(Idea.owner_id==user.id,Idea.disposition.in_(['Active','On hold']),Idea.stage!='Realized').order_by(Idea.expected_finish)))
    return {'ideas':[idea_row(db,i) for i in ideas],'tasks':[{**serialize(t),'reference':db.get(Idea,t.idea_id).reference} for t in db.scalars(select(Task).where(Task.assignee_id==user.id,Task.status!='Done').order_by(Task.due_date))]}

@app.post(P+'/demo/import')
def demo_import(data:dict,dry_run:bool=True,user=Depends(current_user),db=Depends(get_db)):
    require(user,'Admin')
    from .demo import import_dataset, DemoDataset
    from pydantic import ValidationError
    try: dataset=DemoDataset.model_validate(data)
    except ValidationError as exc: D.fail('; '.join(e['msg'] for e in exc.errors()))
    try: return import_dataset(db,user,dataset,dry_run)
    except ValidationError as exc: D.fail('; '.join(e['msg'] for e in exc.errors()))
    except OSError: D.fail('The private credential handover directory is not writable. Check local folder permissions before retrying.',503)
@app.get(P+'/demo/batches')
def demo_batches(user=Depends(current_user),db=Depends(get_db)):
    require(user,'Admin');return [serialize(b) for b in db.scalars(select(DemoBatch).order_by(DemoBatch.recorded_at))]
