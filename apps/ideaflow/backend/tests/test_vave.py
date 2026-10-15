import base64, copy, uuid
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from app.main import app
from app.models import User
from app.vave import calculations
from app.vave_schemas import Application

P='/api/v1/vave'
def ok(response):
    assert response.status_code<300, response.text
    return response.json()

def setup(clients):
    admin=clients['Admin'];owner=clients['User'];refs=ok(admin.get('/api/v1/references'))
    owner_id=next(u['id'] for u in refs['users'] if u['email']=='user@test.invalid')
    admin_id=next(u['id'] for u in refs['users'] if u['email']=='admin@test.invalid')
    data={'name':'VAVE '+uuid.uuid4().hex,'client':'Private client','objective':'Bracket cost','sponsor':'Sponsor','scope':'Product A','start':'2026-01-01','end':'2026-12-31','recognition_rules':'Comparable baseline, separate volume and price effects','members':[{'user_id':admin_id,'roles':['Manager','Finance','Functional','Authority']},{'user_id':owner_id,'roles':['Contributor','Finance']}],
        'targets':[{'scope':'Program','amount':'100000','start':'2026-01-01','end':'2026-12-31'},{'scope':'Product A','amount':'60000','start':'2026-01-01','end':'2026-12-31'},{'scope':'Workstream','amount':'10000','start':'2026-01-01','end':'2026-12-31','additional':True}]}
    program=ok(admin.post(P+'/programs',json=data))
    return admin,owner,owner_id,admin_id,program

def application(plant='Plant A',id='a'):
    return Application.model_validate({'id':id,'scope':'Bracket','plant':plant,'part':'P1','baseline':'10','proposed':'9','annual_volume':'100000','recurring_per_unit':'0.1','baseline_date':'2026-01-01','effective_date':'2026-01-01','evidence':'Observed baseline and quotation','assumptions':'Comparable eligible bracket quantity','periods':[{'month':'2026-09-01','volume':'40000','spend':'20000'}]}).model_dump(mode='json')

def cmd(client,c,action,target=None,role=None):
    return ok(client.post(P+'/ideas/'+c['id']+'/commands',json={'record_version':c['record_version'],'action':action,'target':target,'role':role,'reason':'Evidence reviewed'}))

def edit(client,c,**changes):
    data=copy.deepcopy(c['data']);data.update(changes)
    return ok(client.put(P+'/ideas/'+c['id'],json={**data,'record_version':c['record_version'],'reason':'Reviewed correction'}))

def gate(admin,c,target):
    for role in {1:['Manager'],2:['Finance'],3:['Functional','Finance'],4:['Authority','Finance'],5:['Manager'],6:['Finance']}[target]: c=cmd(admin,c,'Review',target,role)
    return cmd(admin,c,'Advance',target)

def test_a3_a4_unit_run_rate_timing_cash_and_negative_value():
    calc=calculations(application())
    assert calc['unit_saving']==Decimal('1')
    assert calc['annual_gross_run_rate']==Decimal('100000')
    assert calc['annual_net_run_rate']==Decimal('90000')
    assert calc['periods'][0]['gross']==Decimal('40000')
    assert calc['periods'][0]['net']==Decimal('36000')
    assert calc['cash']['net_cash_flow']==Decimal('16000')
    assert calc['cash']['payback']['month']=='2026-09-01'
    unknown=application();unknown['baseline']=None
    assert calculations(unknown)['annual_gross_run_rate'] is None
    negative=application();negative['proposed']='11'
    assert calculations(negative)['annual_net_run_rate']==Decimal('-110000')

def test_a1_a2_a6_a7_a8_gates_partial_rollout_independence_and_history(clients):
    admin,owner,oid,aid,p=setup(clients)
    c=ok(owner.post(P+'/programs/'+p['id']+'/ideas',json={'title':'Unquantified part','description':'Simplify bracket','scope':'Bracket revision A'}))
    assert c['data']['owner_id'] is None and c['maturity']==0
    c=cmd(owner,c,'Submit')
    failed=admin.post(P+'/ideas/'+c['id']+'/commands',json={'record_version':c['record_version'],'action':'Advance','target':1,'reason':'Try'})
    assert failed.status_code==422 and 'owner' in failed.text
    c=edit(owner,c,owner_id=oid,next_action='Review bracket',due_date='2026-11-01')
    c=gate(admin,c,1)
    aa=application();aa['owner_id']=oid;bb=application('Plant B','b');bb['owner_id']=oid
    c=edit(owner,c,applications=[aa,bb],function='Retain bracket strength',constraints='Quality and safety requirements',actions=[{'id':'task','title':'Production cut-in','owner_id':oid,'due_date':'2026-09-01','required':True}])
    c=gate(admin,c,2)
    failed=admin.post(P+'/ideas/'+c['id']+'/commands',json={'record_version':c['record_version'],'action':'Review','target':3,'role':'Functional','reason':'Try'})
    assert failed.status_code==422 and 'acceptance evidence' in failed.text
    c=ok(admin.post(P+'/ideas/'+c['id']+'/feasibility',json={'record_version':c['record_version'],'evidence':{'Function':'Test passed','Quality':'Accepted','Safety':'Accepted'},'reason':'Functional acceptance evidence'}))
    c=gate(admin,c,3);assert c['approved']
    c=gate(admin,c,4)
    aa['rollout']='In production';aa['implementation_evidence']='Production record';c=edit(owner,c,applications=[aa,bb])
    assert c['partial_rollout']
    report=ok(admin.get(P+'/programs/'+p['id']+'/report'))
    assert Decimal(report['totals']['Cost reduction']['implemented'])==36000
    assert Decimal(report['totals']['Cost reduction']['verified'])==0
    assert Decimal(report['targets']['Cost reduction']['target'])==110000
    failed=admin.post(P+'/ideas/'+c['id']+'/commands',json={'record_version':c['record_version'],'action':'Review','target':5,'role':'Manager','reason':'Try'})
    assert failed.status_code==422 and 'Every selected application' in failed.text
    bb['rollout']='In production';bb['implementation_evidence']='Plant B cut-in'
    c=edit(owner,c,applications=[aa,bb])
    c=ok(owner.post(P+'/ideas/'+c['id']+'/actions/task',json={'record_version':c['record_version'],'status':'Done','evidence':'Both plants live','reason':'Owner records implementation evidence'}))
    c=gate(admin,c,5)
    for a in (aa,bb):
        c=ok(owner.post(P+'/ideas/'+c['id']+'/actuals',json={'record_version':c['record_version'],'application_id':a['id'],'month':'2026-09-01','volume':'40000','actual_cost':'9','recurring':'4000','spend':'20000','evidence':'Invoices','variance_reason':'Matches launch plan','external_effects':'No unrelated price or currency effects','reason':'Observed result'}))
        failed=owner.post(P+'/ideas/'+c['id']+'/actuals/'+a['id']+'/2026-09-01/verify',json={'record_version':c['record_version'],'reason':'My own result'})
        assert failed.status_code==403
        c=ok(admin.post(P+'/ideas/'+c['id']+'/actuals/'+a['id']+'/2026-09-01/verify',json={'record_version':c['record_version'],'reason':'Reconciled independently'}))
    c=gate(admin,c,6);assert c['maturity']==6
    report=ok(admin.get(P+'/programs/'+p['id']+'/report'));assert Decimal(report['totals']['Cost reduction']['verified'])==72000
    old_events=len(c['events']);aa['proposed']='8.9';c=edit(owner,c,applications=[aa,bb])
    assert c['review_required'] and c['approved'] is None and all(not v['verified_at'] for v in c['actuals'].values())
    assert len(c['events'])==old_events+1
    assert any(a.get('proposed')=='9' for e in c['events'] if e['changes'].get('snapshot') for a in e['changes']['snapshot']['applications'])

def test_a5_overlap_alternative_exclusion_and_legacy_api_bypass(clients):
    admin,owner,oid,aid,p=setup(clients);aa=application();aa.update(owner_id=oid,overlap_key='Bracket baseline')
    cases=[]
    for title in ('Concept A','Concept B'):
        c=ok(owner.post(P+'/programs/'+p['id']+'/ideas',json={'title':title,'description':'Change','scope':'Bracket','owner_id':oid,'next_action':'Evaluate','due_date':'2026-11-01','applications':[aa]}));c=cmd(owner,c,'Submit');c=gate(admin,c,1);cases.append(c)
    c=cases[0];failed=admin.post(P+'/ideas/'+c['id']+'/commands',json={'record_version':c['record_version'],'action':'Review','target':2,'role':'Finance','reason':'Try'})
    assert failed.status_code==422 and 'overlapping' in failed.text
    unselected=copy.deepcopy(aa);unselected['selected']=False;cases[1]=edit(owner,cases[1],applications=[unselected])
    c=gate(admin,c,2)
    report=ok(admin.get(P+'/programs/'+p['id']+'/report'))
    assert next(r for r in report['applications'] if r['idea_id']==cases[1]['id'])['excluded']=='Unselected alternative'
    assert Decimal(report['totals']['Cost reduction']['opportunity'])==36000
    assert admin.get('/api/v1/ideas/'+c['id']).status_code==409
    assert c['id'] not in {r['id'] for r in ok(admin.get('/api/v1/ideas?page_size=100'))['items']}

@pytest.mark.parametrize('action',['Reopen','Return'])
def test_rework_cannot_skip_gates_and_failed_decision_is_atomic(clients,action):
    admin,owner,oid,aid,p=setup(clients)
    c=ok(owner.post(P+'/programs/'+p['id']+'/ideas',json={'title':'Guard sequential maturity','description':'Preserve gate review','scope':'Bracket','owner_id':oid,'next_action':'Review','due_date':'2026-11-01'}))
    c=cmd(owner,c,'Submit');c=gate(admin,c,1)
    response=admin.post(P+'/ideas/'+c['id']+'/commands',json={'record_version':c['record_version'],'action':action,'target':6,'reason':'Attempt forward jump'})
    assert response.status_code==422 and 'cannot advance maturity' in response.text
    saved=ok(admin.get(P+'/ideas/'+c['id']))
    for field in ('maturity','status','record_version','events','reviews','approved','data','actuals'):
        assert saved[field]==c[field],field
    # Returning the next gate retains the current maturity; default rework moves back one.
    same=cmd(admin,saved,action,2)
    assert same['maturity']==1 and same['reviews']=={} and len(same['events'])==len(c['events'])+1
    back=cmd(admin,same,action)
    assert back['maturity']==0 and len(back['events'])==len(same['events'])+1

def test_a9_external_boundaries_files_filters_and_controlled_import(clients):
    admin,owner,oid,aid,p=setup(clients)
    ext=ok(admin.post('/api/v1/users',json={'name':'External','email':uuid.uuid4().hex+'@test.invalid','role':'User','password':'test-only-external-123'}))
    program_data=copy.deepcopy(p['data']);program_data['members'].append({'user_id':ext['id'],'roles':['External']})
    p=ok(admin.put(P+'/programs/'+p['id'],json={**program_data,'record_version':p['record_version'],'reason':'Approve external access'}))
    c=ok(owner.post(P+'/programs/'+p['id']+'/ideas',json={'title':'Shared approved concept','description':'Change','scope':'Bracket','shared':True}))
    private=ok(owner.post(P+'/programs/'+p['id']+'/ideas',json={'title':'Commercially sensitive','description':'Secret','scope':'Private'}))
    external=TestClient(app);login=ok(external.post('/api/v1/session/login',json={'email':ext['email'],'password':'test-only-external-123'}));external.headers['X-CSRF-Token']=login['csrf']
    rows=ok(external.get(P+'/programs/'+p['id']+'/ideas'));assert {r['id'] for r in rows}=={c['id']}
    assert external.get(P+'/ideas/'+private['id']).status_code==404
    assert external.get('/api/v1/ideas').status_code==403
    assert external.get('/api/v1/events/export').status_code==403
    assert external.get(P+'/programs/'+p['id']+'/report').status_code==403
    result=ok(external.get(P+'/ideas/'+c['id']));assert 'actuals' not in result and 'applications' not in result['data']
    assert 'Commercially sensitive' not in external.get(P+'/programs/'+p['id']+'/export').text
    c=ok(owner.post(P+'/ideas/'+c['id']+'/evidence',json={'record_version':c['record_version'],'name':'costs.txt','content_base64':base64.b64encode(b'private quotation').decode()}))
    file=c['evidence'][0];assert external.get(P+'/evidence/'+file['id']).status_code==404
    assert owner.get(P+'/evidence/'+file['id']).content==b'private quotation'
    payload={'mapping':{'title':'Name','description':'Change','scope':'Part'},'rows':[{'Name':'Imported concept','Change':'Improve','Part':'P1'}]}
    preview=ok(admin.post(P+'/programs/'+p['id']+'/import',json=payload));assert preview['count']==1
    assert admin.post(P+'/programs/'+p['id']+'/import?dry_run=false',json=payload).status_code==422
    applied=ok(admin.post(P+'/programs/'+p['id']+'/import?dry_run=false',json={**payload,'preview_token':preview['preview_token'],'confirmed':True}));assert len(applied['created'])==1
    again=ok(admin.post(P+'/programs/'+p['id']+'/import?dry_run=false',json={**payload,'preview_token':preview['preview_token'],'confirmed':True}));assert again['already_imported']
    stale=owner.put(P+'/ideas/'+c['id'],json={**c['data'],'record_version':c['record_version']-1,'reason':'Stale'});assert stale.status_code==409
    assert external.get(P+'/programs/'+str(uuid.uuid4())+'/ideas').status_code==404
    other=setup(clients)[-1]
    assert external.get(P+'/programs/'+other['id']+'/ideas').status_code==404
    intake=ok(external.post(P+'/programs/'+p['id']+'/ideas',json={'title':'Supplier proposal','description':'Improve packaging','scope':'Approved intake'}))
    assert ok(external.get(P+'/ideas/'+intake['id']))['data']['title']=='Supplier proposal'
    assert 'applications' not in intake['data']
    intake=ok(external.put(P+'/ideas/'+intake['id'],json={'record_version':intake['record_version'],'title':'Supplier proposal revised','description':'Improve packaging','scope':'Approved intake','reason':'Draft revision'}))
    intake=cmd(external,intake,'Submit');assert intake['status']=='Active'
    external.close()

def test_vave_program_audit_is_append_only(clients,db):
    admin,owner,oid,aid,p=setup(clients)
    import pytest
    from sqlalchemy.exc import DBAPIError
    with pytest.raises(DBAPIError):
        db.execute(text('DELETE FROM vave_program_event WHERE program_id=:id'),{'id':p['id']});db.flush()

def test_existing_idea_adaptation_is_previewed_atomic_and_preserves_legacy_evidence(clients,db):
    admin,owner,oid,aid,p=setup(clients)
    old=ok(owner.post('/api/v1/ideas',json={'title':'Earlier dispatch test','problem':'Existing test problem','solution':'Existing test solution','annual_gross':'1200'}))
    old=ok(owner.get('/api/v1/ideas/'+old['id']))
    sequence=dict(db.execute(text('SELECT last_value,is_called FROM idea_reference_seq')).mappings().one())
    payload={'record_version':old['record_version'],'case':{'title':'Simplify an actuator bracket','description':'Remove redundant machining','scope':'Bracket P1','owner_id':oid},'reason':'Explicitly adapt the existing evaluation record'}
    path=P+'/programs/'+p['id']+'/adopt/'+old['id']
    assert owner.post(path,json=payload).status_code==403
    preview=ok(admin.post(path,json=payload));assert preview['copies_financial_approvals'] is False
    saved=ok(owner.get('/api/v1/ideas/'+old['id']))
    assert {k:v for k,v in saved.items() if k!='financials'}=={k:v for k,v in old.items() if k!='financials'}
    assert admin.post(path+'?dry_run=false',json=payload).status_code==422
    adopted=ok(admin.post(path+'?dry_run=false',json={**payload,'confirmed':True,'preview_token':preview['preview_token']}))
    assert adopted['id']==old['id'] and adopted['reference']==old['reference']
    assert adopted['maturity']==0 and adopted['status']=='Draft' and adopted['approved'] is None and adopted['actuals']=={}
    assert adopted['events'][:-1]==old['events']
    legacy=ok(owner.get(P+'/ideas/'+old['id']+'/legacy'))
    assert legacy['idea']['title']==old['title'] and len(legacy['plans'])==1 and legacy['plans'][0]['annual_gross']=='1200.00'
    assert admin.get('/api/v1/ideas/'+old['id']).status_code==409
    assert dict(db.execute(text('SELECT last_value,is_called FROM idea_reference_seq')).mappings().one())==sequence
    assert admin.post(path,json=payload).status_code==409

def test_notifications_preferences_rework_and_material_change_remain_visible(clients):
    from datetime import timedelta
    from app.financial import app_today
    admin,owner,oid,aid,p=setup(clients)
    c=ok(owner.post(P+'/programs/'+p['id']+'/ideas',json={'title':'Deadline and review test','description':'Improve','scope':'Bracket','owner_id':oid,'next_action':'Review','due_date':(app_today()+timedelta(days=5)).isoformat()}))
    c=cmd(owner,c,'Submit')
    pref=ok(owner.get(P+'/preferences'))
    ok(owner.put(P+'/preferences',json={'record_version':pref['record_version'],'data':{'views':[],'routine_notices':False}}))
    assert not any(n['idea_id']==c['id'] and n['data']['kind']=='Approaching deadline' for n in ok(owner.get(P+'/notices')))
    c=edit(owner,c,due_date=(app_today()-timedelta(days=1)).isoformat())
    assert any(n['idea_id']==c['id'] and n['data']['kind']=='Overdue action' and n['data']['mandatory'] for n in ok(owner.get(P+'/notices')))
    c=cmd(admin,c,'Return')
    assert any(n['idea_id']==c['id'] and n['data']['kind']=='Returned decision' for n in ok(owner.get(P+'/notices')))
    c=edit(owner,c,scope='Revised bracket scope')
    assert any(n['idea_id']==c['id'] and n['data']['kind']=='Material change' for n in ok(owner.get(P+'/notices')))
    assert any(r['id']==c['id'] for r in ok(owner.get(P+'/work'))['owned'])

def test_structured_filters_scoped_reporting_unknowns_and_leadership_read_only(clients):
    admin,owner,oid,aid,p=setup(clients);aa=application();aa.update(owner_id=oid,part='RB-P1',supplier='Supplier A')
    c=ok(owner.post(P+'/programs/'+p['id']+'/ideas',json={'title':'Known application','description':'Improve','scope':'Bracket','product':'Actuator','category':'Design simplification','owner_id':oid,'applications':[aa]}))
    bb=application('Plant B','b');bb.update(baseline=None,owner_id=oid)
    unknown=ok(owner.post(P+'/programs/'+p['id']+'/ideas',json={'title':'Unknown economics','description':'Improve','scope':'Packaging','product':'Packaging','owner_id':oid,'applications':[bb]}))
    rows=ok(admin.get(P+'/programs/'+p['id']+'/ideas?part=RB-P1&supplier=Supplier%20A&sort=title'))
    assert [r['id'] for r in rows]==[c['id']]
    assert [r['id'] for r in ok(admin.get(P+'/programs/'+p['id']+'/ideas?search=RB-P1'))]==[c['id']]
    assert c['reference'] in admin.get(P+'/programs/'+p['id']+'/export?part=RB-P1').text and unknown['reference'] not in admin.get(P+'/programs/'+p['id']+'/export?part=RB-P1').text
    report=ok(admin.get(P+'/programs/'+p['id']+'/report?plant=Plant%20B'))
    assert report['totals']['Cost reduction']['opportunity'] is None and report['totals']['Cost reduction']['unknown_applications']==1
    assert report['targets']['Cost reduction']['target'] is None and report['cohort']['submissions']==1
    report=ok(admin.get(P+'/programs/'+p['id']+'/report?product=Actuator'))
    assert Decimal(report['totals']['Cost reduction']['opportunity'])==36000
    viewer=ok(admin.post('/api/v1/users',json={'name':'Leadership viewer','email':uuid.uuid4().hex+'@test.invalid','role':'User','password':'test-only-viewer-123'}))
    data=copy.deepcopy(p['data']);data['members'].append({'user_id':viewer['id'],'roles':['Viewer']})
    ok(admin.put(P+'/programs/'+p['id'],json={**data,'record_version':p['record_version'],'reason':'Authorize leadership reporting'}))
    with TestClient(app) as client:
        login=ok(client.post('/api/v1/session/login',json={'email':viewer['email'],'password':'test-only-viewer-123'}));client.headers['X-CSRF-Token']=login['csrf']
        assert client.get(P+'/programs/'+p['id']+'/report').status_code==200
        detail=ok(client.get(P+'/ideas/'+c['id']));assert detail['data']['applications'][0]['baseline']=='10'
        assert client.put(P+'/ideas/'+c['id'],json={**detail['data'],'record_version':detail['record_version'],'reason':'Forbidden viewer edit'}).status_code==403

def test_application_owner_cannot_verify_and_actuals_need_approved_period(clients):
    admin,owner,oid,aid,p=setup(clients)
    a=application();a.update(owner_id=aid,rollout='In production',implementation_evidence='Observed production cut-in')
    c=ok(owner.post(P+'/programs/'+p['id']+'/ideas',json={'title':'Independent application verification','description':'Preserve function','scope':'Bracket','owner_id':oid,'next_action':'Review evidence','due_date':'2026-11-01','function':'Bracket support','constraints':'Strength and safety','applications':[a]}))
    c=cmd(owner,c,'Submit')
    c=ok(admin.post(P+'/ideas/'+c['id']+'/feasibility',json={'record_version':c['record_version'],'evidence':{'Function':'Accepted','Quality':'Accepted','Safety':'Accepted'},'reason':'Tests reviewed'}))
    for target in (1,2,3):c=gate(admin,c,target)
    body={'record_version':c['record_version'],'application_id':a['id'],'month':'2026-08-01','volume':'40000','actual_cost':'9','recurring':'4000','spend':'0','evidence':'Invoices','variance_reason':'As planned','external_effects':'None','reason':'Observed result'}
    failed=owner.post(P+'/ideas/'+c['id']+'/actuals',json=body)
    assert failed.status_code==422 and 'observation period' in failed.text
    unchanged=ok(admin.get(P+'/ideas/'+c['id']))
    assert unchanged['record_version']==c['record_version'] and unchanged['actuals']=={}
    c=ok(owner.post(P+'/ideas/'+c['id']+'/actuals',json={**body,'month':'2026-09-01'}))
    failed=admin.post(P+'/ideas/'+c['id']+'/actuals/'+a['id']+'/2026-09-01/verify',json={'record_version':c['record_version'],'reason':'Application owner attempts approval'})
    assert failed.status_code==403 and 'owned application' in failed.text
    unchanged=ok(admin.get(P+'/ideas/'+c['id']))
    assert unchanged['record_version']==c['record_version'] and all(v['verified_at'] is None for v in unchanged['actuals'].values())