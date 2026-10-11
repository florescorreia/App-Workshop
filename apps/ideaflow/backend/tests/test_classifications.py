import uuid
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import select, func
from app.models import Site, Category, IdeaEvent
from test_workflow import make, get, update, move, P

def test_blank_user_start_and_admin_boundary(clients):
    user=clients['User'];admin=clients['Admin']
    response=user.post(P+'/ideas',json={'title':'Start without a taxonomy','problem':'Repeated checks','solution':'One checklist'})
    assert response.status_code==201,response.text
    idea=response.json();assert idea['site_id'] is None and idea['category_id'] is None
    assert user.get(P+'/ideas',params={'ids':idea['id']}).json()['total']==1
    assert user.get(P+'/dashboards/process',params={'ids':idea['id']}).json()['case_count']==1
    assert move(user,idea['id'],'Screening').status_code==200
    account={'name':'Second user','email':uuid.uuid4().hex+'@test.invalid','role':'User','password':'test-only-password-123'}
    assert user.post(P+'/users',json=account).status_code==403
    account['role']='Manager';assert admin.post(P+'/users',json=account).status_code==422
    account['role']='User';assert admin.post(P+'/users',json=account).status_code==200
    owner=admin.get(P+'/session/me').json()['user']['id']
    assert update(user,idea['id'],owner_id=owner).status_code==200

def test_new_labels_deduplicate_and_invalid_save_rolls_back(clients,db):
    user=clients['User'];tag=uuid.uuid4().hex[:8]
    idea=make(user,site_id=None,category_id=None,site_name=' Dock '+tag+'  North ',category_name='Packing '+tag)
    second=make(user,site_id=None,category_id=None,site_name='dock '+tag+' north',category_name='PACKING '+tag)
    assert idea['site_id']==second['site_id'] and idea['category_id']==second['category_id']
    before=db.scalar(select(func.count()).select_from(Site))
    bad=update(user,idea['id'],site_id=None,site_name='Rollback '+tag,actual_start='2099-01-01')
    assert bad.status_code==422
    assert db.scalar(select(func.count()).select_from(Site))==before
    # Concurrent spelling variants must resolve to one durable choice.
    def create(name):return make(user,site_id=None,site_name=name)['site_id']
    with ThreadPoolExecutor(2) as pool:
        ids=list(pool.map(create,['Concurrent '+tag,' concurrent '+tag.upper()+' ']))
    assert ids[0]==ids[1]

def test_shared_rename_merge_history_and_optimistic_conflicts(clients):
    user=clients['User'];tag=uuid.uuid4().hex[:8]
    first=make(user,site_id=None,site_name='Plant A '+tag,category_id=None,category_name='Shipping '+tag)
    second=make(user,site_id=None,site_name='Plant B '+tag,category_id=first['category_id'])
    refs=user.get(P+'/references').json();source=next(r for r in refs['sites'] if r['id']==first['site_id']);target=next(r for r in refs['sites'] if r['id']==second['site_id'])
    source_path=P+'/references/sites/'+source['id']
    rename={'record_version':source['record_version'],'label':'North '+tag,'business_unit':'Operations','reason':'Agreed reporting name'}
    assert user.put(source_path,json=rename).json()['affected_ideas']==1
    assert user.put(source_path,json=rename).status_code==409
    assert get(user,first['id'])['site']=='North '+tag
    current=get(user,first['id']);old_events=current['events']
    merge={'record_version':source['record_version']+1,'target_id':target['id'],'target_version':target['record_version'],'reason':'Combine reporting groups'}
    result=user.post(source_path+'/merge',json=merge);assert result.status_code==200,result.text
    assert result.json()['affected_ideas']==1
    current=get(user,first['id']);assert current['site_id']==target['id']
    assert current['events'][:len(old_events)]==old_events
    assert current['events'][-1]['event_type']=='CLASSIFICATION_MERGED'
    assert user.get(P+'/ideas',params={'site_id':target['id']}).json()['total']==2
    assert source['id'] not in [r['id'] for r in user.get(P+'/references').json()['sites']]
    # Retired spellings and IDs route to the agreed value; never fork the taxonomy.
    third=make(user,site_id=None,site_name='north '+tag)
    assert third['site_id']==target['id']
    # Merge categories has the same audit and aggregation behavior.
    category=user.post(P+'/references/categories',json={'label':'Cost savings '+tag}).json()
    source=user.get(P+'/references').json()['categories'];source=next(r for r in source if r['id']==first['category_id'])
    result=user.post(P+'/references/categories/'+source['id']+'/merge',json={'record_version':source['record_version'],'target_id':category['id'],'target_version':category['record_version'],'reason':'Agreed broader category'})
    assert result.status_code==200 and result.json()['affected_ideas']==2
    assert user.get(P+'/dashboards/portfolio',params={'category_id':category['id']}).json()['active_count']==2

def test_admin_password_reset_and_deactivation(clients,test_engine):
    from fastapi.testclient import TestClient
    from app.main import app
    admin=clients['Admin'];email=uuid.uuid4().hex+'@test.invalid'
    account=admin.post(P+'/users',json={'name':'Account check','email':email,'role':'User','password':'original-test-password-123'}).json()
    with TestClient(app) as other:
        login=other.post(P+'/session/login',json={'email':email,'password':'original-test-password-123'})
        assert login.status_code==200
        update={k:account[k] for k in ('name','role','active','record_version')}
        response=admin.put(P+'/users/'+account['id'],json={**update,'password':'changed-test-password-123'})
        assert response.status_code==200
        assert other.post(P+'/session/login',json={'email':email,'password':'original-test-password-123'}).status_code==401
        assert other.post(P+'/session/login',json={'email':email,'password':'changed-test-password-123'}).status_code==200
        update['record_version']=response.json()['record_version']
        assert admin.put(P+'/users/'+account['id'],json={**update,'active':False}).status_code==200
        assert other.get(P+'/session/me').status_code==401
    current=admin.get(P+'/session/me').json()['user']
    assert admin.put(P+'/users/'+current['id'],json={k:current[k] for k in ('name','role','active','record_version')}|{'active':False}).status_code==422
