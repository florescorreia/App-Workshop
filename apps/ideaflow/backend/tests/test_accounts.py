import json,uuid
import pytest
from sqlalchemy import select,text
from sqlalchemy.exc import DBAPIError
from fastapi.testclient import TestClient
from app.main import app
from app.models import User,AccountEvent
from test_workflow import make,get,update,P

OLD='test-original-password-123'

def create(admin):
    response=admin.post(P+'/users',json={'name':'Account '+uuid.uuid4().hex[:8],'email':uuid.uuid4().hex+'@test.invalid','role':'User','password':OLD})
    assert response.status_code==200
    return response.json()

def login(client,account,password=OLD):
    r=client.post(P+'/session/login',json={'email':account['email'],'password':password})
    if r.status_code==200:client.headers['X-CSRF-Token']=r.json()['csrf']
    return r

def command(account):return {'record_version':account['record_version'],'reason':'Admin access cleanup'}

def test_delete_unused_account_revokes_sessions_and_records_actor(clients,db):
    admin=clients['Admin'];user=clients['User'];account=create(admin);path=P+'/users/'+account['id']
    assert user.get(path+'/deletion-preview').status_code==403
    assert user.request('DELETE',path,json=command(account)).status_code==403
    assert user.get(P+'/account-events').status_code==403
    with TestClient(app) as target:
        assert login(target,account).status_code==200
        preview=admin.get(path+'/deletion-preview').json();assert preview['allowed'] and preview['mode']=='remove'
        assert admin.request('DELETE',path,json={**command(account),'record_version':0}).status_code==409
        assert target.get(P+'/session/me').status_code==200
        r=admin.request('DELETE',path,json=command(account));assert r.status_code==200 and r.json()['mode']=='remove'
        assert target.get(P+'/session/me').status_code==401
        assert login(target,account).status_code==401
    assert db.get(User,account['id']) is None
    history=admin.get(P+'/account-events').json()
    event=next(e for e in history if e['subject_id']==account['id'] and e['action']=='ACCOUNT_DELETED')
    assert event['actor_id']==admin.get(P+'/session/me').json()['user']['id']
    assert event['subject_name']==account['name'] and event['reason']=='Admin access cleanup'
    assert admin.request('DELETE',path,json=command(account)).status_code==404

def test_delete_old_account_keeps_idea_history_and_blocks_open_work(clients,db):
    admin=clients['Admin'];account=create(admin);path=P+'/users/'+account['id']
    with TestClient(app) as target:
        assert login(target,account).status_code==200
        idea=make(target);id=idea['id']
        before=get(admin,id)
        preview=admin.get(path+'/deletion-preview').json();assert not preview['allowed'] and preview['open_ideas'][0]['id']==id
        assert admin.request('DELETE',path,json=command(account)).status_code==422
        assert get(admin,id)['events']==before['events']
        admin_id=admin.get(P+'/session/me').json()['user']['id']
        assert update(admin,id,owner_id=admin_id).status_code==200
        task=admin.post(P+'/ideas/'+id+'/tasks',json={'record_version':get(admin,id)['record_version'],'title':'Open assigned work','assignee_id':account['id']}).json()
        preview=admin.get(path+'/deletion-preview').json();assert not preview['allowed'] and preview['open_tasks'][0]['id']==task['id']
        assert admin.request('DELETE',path,json=command(account)).status_code==422
        assert admin.put(P+'/ideas/'+id+'/tasks/'+task['id'],json={'record_version':get(admin,id)['record_version'],'title':task['title'],'assignee_id':admin_id}).status_code==200
        before=get(admin,id)
        result=admin.request('DELETE',path,json=command(account));assert result.status_code==200 and result.json()['mode']=='retire'
        assert target.get(P+'/session/me').status_code==401
        assert login(target,account).status_code==401
        after=get(admin,id)
        before['financials'].pop('as_of');after['financials'].pop('as_of')
        assert after==before
        assert after['events'][0]['actor_name']==account['name']
        retired=db.get(User,account['id']);assert retired.deleted_at and not retired.active and retired.password_hash=='!deleted'
        assert next(u for u in admin.get(P+'/references').json()['users'] if u['id']==account['id'])['deleted_at']
        assert admin.put(path,json={k:account[k] for k in ('name','role','active','record_version')}).status_code==409
        assert admin.post(path+'/regenerate-password',json=command(account)).status_code==409
        assert update(admin,id,owner_id=account['id']).status_code==422

def test_regenerate_is_admin_only_one_time_response_no_secret_history(clients,db):
    admin=clients['Admin'];account=create(admin);path=P+'/users/'+account['id']+'/regenerate-password'
    assert clients['User'].post(path,json=command(account)).status_code==403
    assert admin.post(path,json=command(account),headers={'X-CSRF-Token':''}).status_code==403
    with TestClient(app) as target,TestClient(app) as second:
        assert login(target,account).status_code==200;assert login(second,account).status_code==200
        response=admin.post(path,json=command(account));assert response.status_code==200
        data=response.json();password=data['password'];assert len(password)>=24 and password!=OLD
        assert target.get(P+'/session/me').status_code==401 and second.get(P+'/session/me').status_code==401
        assert login(target,account).status_code==401
        assert login(target,account,password).status_code==200
        assert admin.post(path,json=command(account)).status_code==409
        assert target.get(P+'/session/me').status_code==200
        public=admin.get(P+'/references').text;history=admin.get(P+'/account-events').text
        assert password not in public+history and OLD not in history and 'password_hash' not in public
        stored=db.get(User,account['id']);assert password not in stored.password_hash and stored.record_version==account['record_version']+1
        assert admin.post(path,json={**command(account),'record_version':data['record_version']}).status_code==200
        assert target.get(P+'/session/me').status_code==401
    current=next(u for u in admin.get(P+'/references').json()['users'] if u['id']==account['id'])
    inactive=admin.put(P+'/users/'+account['id'],json={k:current[k] for k in ('name','role','active','record_version')}|{'active':False}).json()
    response=admin.post(path,json=command(inactive));assert response.status_code==200
    with TestClient(app) as target:
        assert login(target,account,response.json()['password']).status_code==401
    assert not next(u for u in admin.get(P+'/references').json()['users'] if u['id']==account['id'])['active']

def test_account_audit_immutable_and_own_account_protected(clients,db):
    admin=clients['Admin'];account=create(admin)
    for statement in ['UPDATE account_event SET reason=\'tampered\'','DELETE FROM account_event','TRUNCATE account_event']:
        with pytest.raises(DBAPIError):
            with db.begin_nested():db.execute(text(statement))
    me=admin.get(P+'/session/me').json()['user'];path=P+'/users/'+me['id']
    assert admin.get(path+'/deletion-preview').json()['protected']
    assert admin.request('DELETE',path,json=command(me)).status_code==422
    assert admin.post(path+'/regenerate-password',json=command(me)).status_code==422

def test_bootstrap_protected_and_manual_own_reset_revokes_session(clients,monkeypatch):
    admin=clients['Admin'];account=create(admin);path=P+'/users/'+account['id']
    update={k:account[k] for k in ('name','role','active','record_version')}
    promoted=admin.put(path,json={**update,'role':'Admin'}).json()
    with monkeypatch.context() as patch:
        patch.setenv('ADMIN_EMAIL',account['email'])
        assert admin.get(path+'/deletion-preview').json()['protected']
        assert admin.request('DELETE',path,json=command(promoted)).status_code==422
        assert admin.put(path,json={k:promoted[k] for k in update}|{'active':False}).status_code==422
        assert admin.put(path,json={k:promoted[k] for k in update}|{'role':'User'}).status_code==422
    with TestClient(app) as target:
        assert login(target,account).status_code==200
        replacement='test-manual-own-replacement-123'
        response=target.put(path,json={k:promoted[k] for k in update}|{'password':replacement})
        assert response.status_code==200
        assert target.get(P+'/session/me').status_code==401
        assert login(target,account).status_code==401
        assert login(target,account,replacement).status_code==200
    history=admin.get(P+'/account-events').json()
    event=next(e for e in history if e['subject_id']==account['id'] and e['action']=='PASSWORD_SET')
    assert event['actor_id']==account['id'] and replacement not in json.dumps(history)
