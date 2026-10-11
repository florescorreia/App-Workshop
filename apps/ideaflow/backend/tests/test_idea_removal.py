import uuid
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor
from app.financial import app_today,add_month
from test_workflow import make,get,move,update,save_plan,P

def command(idea,**extra):return {'record_version':idea['record_version'],'reason':'Practice workspace cleanup','confirm':True,**extra}
def normal_idea(idea):
    return {k:v for k,v in idea.items() if k not in ('events','record_version','updated_at','removed_at','removed_by','removal_reason','financials','transitions')}

def test_unified_ideas_every_view_exports_and_legacy_flags(clients,db):
    from app.models import Idea
    user=clients['User'];admin=clients['Admin'];tag=uuid.uuid4().hex
    business=make(user,title='First '+tag,annual_gross='100',annual_recurring='10')
    practice=make(user,title='Second '+tag,annual_gross='99999',annual_recurring='0')
    # A historical flag survives migration but no longer separates records or metrics.
    db.get(Idea,practice['id']).is_test=True;db.commit()
    ids={business['id'],practice['id']}
    for scope in ('','business','test','all','old-bookmark'):
        params={'search':tag,**({'idea_scope':scope} if scope else {})}
        rows=user.get(P+'/ideas',params=params).json()['items']
        assert {i['id'] for i in rows}==ids and all('is_test' not in i for i in rows)
        portfolio=user.get(P+'/dashboards/portfolio',params=params).json();assert set(portfolio['active_ids'])==ids
        value=user.get(P+'/dashboards/value',params=params).json()
        assert Decimal(value['annual_net_potential'])==Decimal('100089')
        assert {i['idea_id'] for i in value['variance']}==ids
        assert user.get(P+'/dashboards/process',params=params).json()['case_count']==2
        assert {i['id'] for i in user.get(P+'/my-work',params=params).json()['ideas']}==ids
        for endpoint in ('/ideas/export','/events/export'):
            csv=user.get(P+endpoint,params=params).text
            assert 'is_test' not in csv
            assert all((i['reference'] if endpoint=='/ideas/export' else i['id']) in csv for i in (business,practice))
    assert user.post(P+'/ideas',json={'title':'No separate type','problem':'P','solution':'S','is_test':True}).status_code==422
    assert update(user,business['id'],is_test=True).status_code==422
    assert update(user,business['id'],removed_at=app_today().isoformat()).status_code==422
    assert admin.post(P+'/ideas/'+business['id']+'/mark-test',json=command(business)).status_code==404
    path=P+'/ideas/'+business['id']+'/remove'
    assert user.post(path,json=command(business)).status_code==403
    assert admin.post(path,json=command(business,confirm=False)).status_code==422
    assert admin.post(path,json=command(business,reason=' ')).status_code==422
    assert admin.post(path,json=command(business),headers={'X-CSRF-Token':''}).status_code==403
    assert admin.post(path,json=command(business)).status_code==200
    after=get(admin,business['id']);assert after['events'][-1]['event_type']=='IDEA_REMOVED'
    assert after['events'][-1]['actor_name']=='Test Admin'
    assert user.get(P+'/ideas',params={'search':tag}).json()['total']==1
    assert user.get(P+'/ideas',params={'ids':business['id']}).json()['total']==0

def test_removed_developed_idea_retains_all_records_readonly_and_restore(clients):
    admin=clients['Admin'];user=clients['User'];idea=make(user);id=idea['id'];path=P+'/ideas/'+id
    today=app_today();start=today.replace(month=1,day=1)
    assert move(user,id,'Screening').status_code==200
    assert update(user,id,screening_note='Test scope',expected_start=start.isoformat(),expected_finish=today.isoformat()).status_code==200
    assert move(user,id,'Analysis').status_code==200
    assert save_plan(user,id).status_code==200
    assert move(user,id,'Approved').status_code==200
    task=user.post(path+'/tasks',json={'record_version':get(user,id)['record_version'],'title':'Practice task','assignee_id':idea['owner_id']}).json()
    user.post(path+'/comments',json={'record_version':get(user,id)['record_version'],'body':'Retain context'})
    month=add_month(today.replace(day=1),-1).isoformat()
    result=user.put(path+'/results/'+month,json={'record_version':get(user,id)['record_version'],'gross':'900','recurring':'100','spend':'1000'}).json()
    assert user.post(path+'/results/'+month+'/verify',json={'record_version':get(user,id)['record_version'],'period_version':result['record_version'],'gross':'900','recurring':'100','spend':'1000','reason':'Practice review'}).status_code==200
    before=get(admin,id);preview=admin.get(path+'/removal-preview').json()
    assert preview['counts']=={'tasks':1,'open_tasks':1,'plans':2,'approved_plans':1,'results':1,'verified_results':1,'comments':1,'events':len(before['events'])}
    assert user.get(path+'/removal-preview').status_code==403
    assert user.post(path+'/remove',json=command(before)).status_code==403
    assert admin.post(path+'/remove',json=command(before,record_version=0)).status_code==409
    assert admin.post(path+'/remove',json=command(before)).status_code==200
    after=get(admin,id);assert normal_idea(after)==normal_idea(before)
    assert after['transitions']==[]
    for key in ('plans','results','tasks','comments'):
        assert after[key]==before[key]
    assert after['events'][:-1]==before['events'] and after['events'][-1]['event_type']=='IDEA_REMOVED'
    assert user.get(path).status_code==403
    for endpoint in ('/ideas','/my-work','/dashboards/portfolio','/dashboards/value','/dashboards/process','/ideas/export','/events/export'):
        response=admin.get(P+endpoint,params={'ids':id,'idea_scope':'all'});assert response.status_code==200
        assert id not in response.text and idea['reference'] not in response.text
    assert admin.get(P+'/removed-ideas',params={'ids':id,'page_size':1}).json()['total']==1
    assert user.get(P+'/removed-ideas').status_code==403
    for endpoint,method,data in [('', 'PUT', {'title':'wrong'}),('/assignment','POST',{'owner_id':idea['owner_id']}),('/comments','POST',{'body':'wrong'}),('/tasks','POST',{'title':'wrong','assignee_id':idea['owner_id']}),('/tasks/'+task['id'],'PUT',{'title':'wrong','assignee_id':idea['owner_id']}),('/transitions','POST',{'action':'Analysis','reason':'wrong'}),('/plans','POST',{}),('/plans/approve','POST',{'reason':'wrong'}),('/results/'+month,'PUT',{}),('/results/'+month+'/verify','POST',{'period_version':result['record_version'],'gross':'1','recurring':'0','spend':'0','reason':'wrong'}),('/results/'+month+'/revoke','POST',{'period_version':result['record_version'],'reason':'wrong'})]:
        payload={'record_version':after['record_version'],**data}
        if endpoint=='':payload={**{k:before[k] for k in ('title','problem','solution','owner_id','site_id','category_id')},**payload}
        assert admin.request(method,path+endpoint,json=payload).status_code==409,endpoint
    assert get(admin,id)['events']==after['events']
    assert user.post(path+'/restore',json=command(after)).status_code==403
    assert admin.post(path+'/restore',json=command(after)).status_code==200
    restored=get(user,id);assert normal_idea(restored)==normal_idea(before)
    assert restored['transitions']==before['transitions']
    assert restored['events'][:-2]==before['events'] and restored['events'][-1]['event_type']=='IDEA_RESTORED'
    assert restored['removed_at'] is None
    assert user.get(P+'/ideas',params={'ids':id}).json()['total']==1
    assert user.get(P+'/ideas',params={'ids':id,'idea_scope':'test'}).json()['total']==1

def test_shared_classification_changes_retain_archived_evidence(clients):
    admin=clients['Admin'];user=clients['User'];tag=uuid.uuid4().hex
    idea=make(user,site_id=None,category_id=None,site_name='Practice location '+tag)
    path=P+'/ideas/'+idea['id'];assert admin.post(path+'/remove',json=command(idea)).status_code==200
    before=get(admin,idea['id'])
    ref=next(s for s in user.get(P+'/references').json()['sites'] if s['id']==idea['site_id'])
    response=user.put(P+'/references/sites/'+ref['id'],json={'record_version':ref['record_version'],'label':'Agreed location '+tag,'reason':'Shared reporting name'})
    assert response.status_code==200,response.text
    after=get(admin,idea['id']);assert after['removed_at']==before['removed_at']
    assert after['site']=='Agreed location '+tag and after['record_version']==before['record_version']+1
    assert after['events'][-1]['event_type']=='CLASSIFICATION_RENAMED'
    assert after['plans']==before['plans'] and after['results']==before['results'] and after['stage']==before['stage']
    assert user.get(P+'/ideas',params={'ids':idea['id'],'idea_scope':'all'}).json()['total']==0

def test_removal_concurrent_atomic_and_retired_owner_restore(clients):
    admin=clients['Admin'];user=clients['User']
    practice=make(user);path=P+'/ideas/'+practice['id']
    with ThreadPoolExecutor(2) as pool:
        statuses=list(pool.map(lambda _:admin.post(path+'/remove',json=command(practice)).status_code,[1,2]))
    assert sorted(statuses)==[200,409]
    assert len(get(admin,practice['id'])['events'])==2
    account=admin.post(P+'/users',json={'name':'Old practice owner','email':uuid.uuid4().hex+'@test.invalid','role':'User','password':'isolated-owner-password-123'}).json()
    # Restore, assign practice work, remove again, then retire its account.
    assert admin.post(path+'/restore',json=command(get(admin,practice['id']))).status_code==200
    assert update(user,practice['id'],owner_id=account['id']).status_code==200
    task=admin.post(path+'/tasks',json={'record_version':get(user,practice['id'])['record_version'],'title':'Open old-owner task','assignee_id':account['id']}).json()
    assert admin.post(path+'/remove',json=command(get(user,practice['id']))).status_code==200
    assert admin.get(P+'/users/'+account['id']+'/deletion-preview').json()['allowed']
    assert admin.request('DELETE',P+'/users/'+account['id'],json={'record_version':account['record_version'],'reason':'Retire unused training login'}).json()['mode']=='retire'
    removed=get(admin,practice['id']);preview=admin.get(path+'/removal-preview').json();assert not preview['owner_active'] and preview['inactive_tasks'][0]['id']==task['id']
    assert admin.post(path+'/restore',json=command(removed)).status_code==422
    new_owner=admin.get(P+'/session/me').json()['user']['id']
    assert admin.post(path+'/restore',json=command(removed,owner_id=new_owner)).status_code==422
    assert get(admin,practice['id'])['events']==removed['events']
    assert admin.post(path+'/restore',json=command(removed,owner_id=new_owner,reassign_inactive_tasks=True)).status_code==200
    restored=get(admin,practice['id']);assert restored['owner_id']==new_owner and restored['tasks'][0]['assignee_id']==new_owner
    assert [e['event_type'] for e in restored['events'][-3:]]==['ASSIGNED','TASK_CHANGED','IDEA_RESTORED']
