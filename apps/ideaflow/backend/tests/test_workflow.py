import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from sqlalchemy import select, text, func
from sqlalchemy.exc import DBAPIError
import pytest
from app.models import Idea, IdeaEvent, User
from app.financial import app_today, add_month

P='/api/v1'
def get(c,id):return c.get(P+'/ideas/'+id).json()
def make(c,**extra):
    data={'title':'Measured test '+uuid.uuid4().hex[:8],'problem':'A recurring delay is measurable','solution':'Pilot a standard handoff','site_id':'Tampa','category_id':'Energy',**extra}
    response=c.post(P+'/ideas',json=data);assert response.status_code==201,response.text;return response.json()
def update(c,id,**extra):
    idea=get(c,id);fields={k:idea[k] for k in ['title','problem','solution','site_id','category_id','owner_id','expected_start','expected_finish','screening_note','evidence_url','progress','actual_start','actual_completion','record_version']}
    return c.put(P+'/ideas/'+id,json={**fields,**extra})
def move(c,id,action,**extra):return c.post(P+'/ideas/'+id+'/transitions',json={'record_version':get(c,id)['record_version'],'action':action,'reason':'Evidence reviewed',**extra})
def save_plan(c,id):
    year=app_today().year
    rows=[{'month':f'{year}-01-01','gross':'0','recurring':'0','spend':'30000'}]+[{'month':f'{year}-{m:02d}-01','gross':'10000','recurring':'1000','spend':'0'} for m in range(2,13)]
    return c.post(P+'/ideas/'+id+'/plans',json={'record_version':get(c,id)['record_version'],'annual_gross':'120000','annual_recurring':'12000','upfront':'30000','probability':'.7','confidence':'.6','periods':rows,'rationale':'Metered baseline'})

def test_dashboard_drilldowns_pagination_and_decimal_totals(clients):
    a=clients['Admin'];tag='Dashboard '+uuid.uuid4().hex
    first=make(a,title=tag+' first',annual_gross='100.10',annual_recurring='0.01')
    second=make(a,title=tag+' second',annual_gross='200.20',annual_recurring='0.02')
    assert move(a,second['id'],'Screening').status_code==200
    result=a.get(P+'/ideas',params={'search':tag,'page_size':1,'sort':'annual'}).json()
    assert result['total']==2 and result['items'][0]['id']==second['id']
    assert result['stage_totals']['New']=='100.09' and result['stage_totals']['Screening']=='200.18'
    page2=a.get(P+'/ideas',params={'search':tag,'page_size':1,'sort':'annual','page':2}).json()
    assert page2['items'][0]['id']==first['id']
    portfolio=a.get(P+'/dashboards/portfolio',params={'search':tag}).json()
    assert set(portfolio['active_ids'])=={first['id'],second['id']}
    ids=','.join(portfolio['active_ids'])
    assert a.get(P+'/ideas',params={'ids':ids}).json()['total']==portfolio['active_count']

def test_user_end_to_end_results_and_rework(clients):
    a=clients['Admin'];m=f=c=clients['User']
    owner=c.get(P+'/session/me').json()['user']['id']
    idea=make(a,owner_id=owner);id=idea['id']
    assert move(c,id,'Screening').status_code==200
    assert move(c,id,'Analysis').status_code==422
    assert update(c,id,screening_note='Measurable opportunity').status_code==200
    assert move(c,id,'Analysis').status_code==200
    assert move(c,id,'Approved').status_code==422
    today=app_today();start=today.replace(month=1,day=1)
    assert update(m,id,expected_start=start.isoformat(),expected_finish=today.isoformat()).status_code==200
    assert save_plan(m,id).status_code==200
    before=get(a,id)
    assert move(m,id,'Approved').status_code==200
    after=get(a,id);assert len(after['events'])==len(before['events'])+2
    assert after['stage']=='Approved' and after['plans'][-1]['status']=='Approved'
    assert update(m,id,actual_start=start.isoformat()).status_code==200
    task={'record_version':get(a,id)['record_version'],'title':'Complete pilot','assignee_id':owner,'due_date':today.isoformat(),'required':True,'status':'Open'}
    tr=m.post(P+'/ideas/'+id+'/tasks',json=task);assert tr.status_code==200;tid=tr.json()['id']
    assert move(m,id,'Implementation').status_code==200
    task['record_version']=get(a,id)['record_version'];task['status']='Done'
    assert c.put(P+'/ideas/'+id+'/tasks/'+tid,json=task).status_code==200
    assert update(c,id,progress=100,actual_completion=today.isoformat()).status_code==200
    assert move(c,id,'Validation').status_code==200
    month=add_month(today.replace(day=1),-1).isoformat();path=P+'/ideas/'+id+'/results/'+month
    result={'record_version':get(a,id)['record_version'],'period_version':0,'gross':'10000','recurring':'1000','spend':'0'}
    rr=f.put(path,json=result);assert rr.status_code==200
    verify={'record_version':get(a,id)['record_version'],'period_version':rr.json()['record_version'],'gross':'9900','recurring':'1000','spend':'0','reason':'Meter adjustment'}
    assert f.post(path+'/verify',json=verify).status_code==200
    assert move(f,id,'Realized',verification_through=month,confirm_completion=True).status_code==200
    assert move(f,id,'Validation').status_code==200
    period=get(a,id)['results'][0];result.update(record_version=get(a,id)['record_version'],period_version=period['record_version'],gross='9500')
    assert f.put(path,json=result).status_code==422
    result['reason']='Corrected measurement';assert f.put(path,json=result).status_code==200
    assert get(a,id)['results'][0]['verified_at'] is None
    assert move(f,id,'Implementation').status_code==200
    after=get(a,id);assert after['progress']<100 and after['tasks'][0]['status']=='Open'
    assert after['actual_completion'] is None

def test_invalid_atomic_stale_concurrent_and_backdate(clients,db):
    a=clients['Admin'];id=make(a)['id'];before=get(a,id)
    assert move(a,id,'Realized').status_code==422
    assert get(a,id)['record_version']==before['record_version']
    assert len(get(a,id)['events'])==len(before['events'])
    assert update(a,id,occurred_at='2020-01-01T00:00:00Z').status_code==422
    assert update(a,id,stage='Realized').status_code==422
    assert update(a,id,title='First edit').status_code==200
    assert update(a,id,record_version=before['record_version'],title='Stale edit').status_code==409
    current=get(a,id);base={k:current[k] for k in ['title','problem','solution','site_id','category_id','owner_id','expected_start','expected_finish','screening_note','evidence_url','progress','actual_start','actual_completion','record_version']}
    with ThreadPoolExecutor(2) as pool:
        statuses=list(pool.map(lambda title:a.put(P+'/ideas/'+id,json={**base,'title':title}).status_code,['Concurrent A','Concurrent B']))
    assert sorted(statuses)==[200,409]
    after=get(a,id);assert len(after['events'])==len(before['events'])+2
    assert len({e['sequence'] for e in after['events']})==len(after['events'])

def test_audit_permissions_and_csrf(clients,db):
    a=clients['Admin'];id=make(a)['id']
    docs=a.get('/api/docs');assert docs.status_code==200 and '/vendor/swagger-ui-bundle.js' in docs.text and 'cdn.jsdelivr.net' not in docs.text
    for query in ['UPDATE idea_event SET reason=\'tampered\' WHERE idea_id=:id','DELETE FROM idea_event WHERE idea_id=:id','TRUNCATE idea_event']:
        with pytest.raises(DBAPIError):
            with db.begin_nested():db.execute(text(query),{'id':id})
    response=a.post(P+'/ideas',json={'title':'x'},headers={'X-CSRF-Token':''});assert response.status_code==403
    response=a.post(P+'/session/logout',json={},headers={'Origin':'https://evil.invalid'});assert response.status_code==403
    users=a.get(P+'/references').json()['users'];assert all('password_hash' not in u for u in users)

def test_hold_and_terminal_workflow(clients):
    a=clients['Admin'];m=f=c=clients['User']
    id=make(c)['id']
    assert move(c,id,'Hold').status_code==200
    assert move(c,id,'Screening').status_code==422
    assert move(c,id,'Resume').status_code==200
    assert move(m,id,'Reject').status_code==200
    assert move(a,id,'Resume').status_code==422
    assert move(a,id,'Screening').status_code==422

def test_filtered_exports_formula_escape_and_paging(clients):
    a=clients['Admin'];idea=make(a,title='=SUM(A1:A2)')
    response=a.get(P+'/ideas/export',params={'ids':idea['id']})
    assert "'=SUM" in response.text
    assert a.get(P+'/ideas?page=0').status_code==422
    assert a.get(P+'/ideas?stage=New&page_size=1').json()['page_size']==1
