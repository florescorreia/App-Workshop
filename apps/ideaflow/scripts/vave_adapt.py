"""Explicit, previewed adaptation of the two user-authorized evaluation ideas.

Uses authenticated business commands. Never resets storage, copies approvals,
creates accounts or runs at startup. Credentials remain in environment variables.
"""
import argparse,copy,http.cookiejar,json,os,urllib.request,urllib.error
from decimal import Decimal
from pathlib import Path

PROGRAM='Product cost excellence — VAVE evaluation'
SOURCE='User-authorized VAVE evaluation adaptation, 2026-10-15'

class Client:
    def __init__(self):
        self.base=os.getenv('VAVE_ADAPT_URL') or os.environ['IDEAFLOW-VPS-URL']
        self.opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.csrf=''
        login=self.call('POST','/session/login',{'email':os.environ['IDEAFLOW-VPS-ADMIN-EMAIL'],'password':os.environ['IDEAFLOW-VPS-ADMIN-PASSWORD']})
        assert login['user']['role']=='Admin'
        self.csrf=login['csrf'];self.user=login['user']
    def call(self,method,path,data=None):
        request=urllib.request.Request(self.base+'/api/v1'+path,data=json.dumps(data).encode() if data is not None else None,method=method,headers={'Content-Type':'application/json','Origin':self.base,'X-CSRF-Token':self.csrf})
        with self.opener.open(request,timeout=30) as response:return json.load(response)
    def close(self):self.call('POST','/session/logout',{})

def profile(owner):
    def application(id,plant,annual,month,volume,spend,effective):
        return {'id':id,'scope':'Actuator mounting bracket','plant':plant,'part':'ACT-BR-104','revision':'B proposed','owner_id':owner,'value_type':'Cost reduction','unit':'bracket','baseline':'10','proposed':'9','annual_volume':str(annual),'recurring_per_unit':'0.10','giveback_per_unit':'0','currency':'EUR','fx_rate':'1','baseline_date':'2026-10-01','effective_date':effective,'source_type':'Estimate','evidence':'Illustrative evaluation estimate; supplier quotation and observed baseline still require confirmation.','assumptions':'Eligible quantities only; no unrelated currency, mix or market-price benefit. Preserve required load, quality and safety.','low':'0.70','high':'1.30','selected':True,'rollout':'Planned','periods':[{'month':month,'volume':str(volume),'adoption':'1','spend':str(spend)}]}
    a=application('bracket-a','Germany — Plant A',80000,'2026-11-01',16000,20000,'2026-11-01');a['periods'].append({'month':'2026-12-01','volume':'16000','adoption':'1','spend':'0'})
    b=application('bracket-b','Germany — Plant B',20000,'2026-12-01',8000,0,'2026-12-01')
    bracket={'title':'Simplify the actuator mounting bracket','description':'Remove redundant machining features from the mounting bracket while retaining its specified load capacity, interfaces and corrosion protection.','scope':'Actuator mounting bracket ACT-BR-104, two plant applications','source':SOURCE,'workshop':'Internal VAVE evaluation','category':'Design simplification','product_family':'Industrial actuators','product':'Actuator assembly','assembly':'Mounting system','commodity':'Machined metal parts','region':'Germany','cost_category':'Purchased parts','current_condition':'Illustrative machined bracket with redundant secondary operations.','future_condition':'Simplified bracket with the required function and interfaces preserved.','function':'Support the actuator at its specified load and maintain mounting interfaces.','constraints':'Load capacity, fatigue life, quality, safety and corrosion protection must remain compliant.','customer_benefit':'Equivalent performance at lower recurring cost.','owner_id':owner,'next_action':'Confirm comparable baseline and validate bracket function, quality and safety.','due_date':'2026-10-29','priority':'High','priority_reason':'Illustrative retained-cost opportunity with two bounded production applications.','effort_days':'12','resource_constraints':'Engineering validation and purchasing review required.','applications':[a,b],'actions':[{'id':'prototype','title':'Confirm drawing and prototype validation plan','owner_id':owner,'due_date':'2026-10-29','status':'Open','required':True,'cost':'20000'},{'id':'cut-in','title':'Approve production cut-in after validation','owner_id':owner,'due_date':'2026-11-01','status':'Open','dependency':'prototype','required':True}],'risks':[{'id':'load','description':'Simplification may affect bracket fatigue life; the cost estimate is not functional acceptance.','severity':'Critical','likelihood':'Medium','mitigation':'Run agreed load and fatigue validation before M3.','owner_id':owner,'due_date':'2026-10-29','disposition':'Open'}]}
    packaging={'title':'Introduce returnable packaging for actuator deliveries','description':'Evaluate reusable transport packaging to reduce disposable material and handling cost while preserving product protection and delivery performance.','scope':'Actuator outbound packaging; applicability and baseline still under review','source':SOURCE,'workshop':'Internal VAVE evaluation','category':'Packaging','product_family':'Industrial actuators','product':'Actuator packaging','current_condition':'Illustrative single-use outbound packaging.','future_condition':'Returnable packaging with controlled cleaning and reverse logistics.','function':'Protect the actuator during transport and storage.','constraints':'Damage rate, safety, cleanliness, customer acceptance and delivery lead time must be preserved.','next_action':'Establish packaging baseline, return loop and eligible volumes.','due_date':'2026-10-30','priority':'Medium','priority_reason':'Early concept; savings remain unknown until baseline and reverse-logistics costs are quantified.','applications':[{'id':'packaging-a','scope':'Outbound actuator packaging','plant':'Germany — Plant A','supplier':'Packaging supplier — to be confirmed','owner_id':owner,'value_type':'Cost reduction','unit':'shipment','currency':'EUR','baseline':None,'proposed':None,'annual_volume':None,'recurring_per_unit':None,'source_type':'Estimate','assumptions':'Include return freight, loss, cleaning and customer handling; do not assume zero offsets.'}]}
    return {'IF-00205':bracket,'IF-00206':packaging}

def prepare(path):
    c=Client()
    try:
        refs=c.call('GET','/references');ideas=c.call('GET','/ideas?page_size=100')['items']
        selected={i['reference']:i for i in ideas if i['reference'] in ('IF-00205','IF-00206')}
        assert set(selected)=={'IF-00205','IF-00206'},'Expected authorized legacy evaluation records are not both present'
        owners=[u for u in refs['users'] if u['active'] and not u.get('deleted_at') and u['role']=='User']
        assert owners,'Keep an independent existing non-Admin owner for evaluation decisions'
        owner=sorted(owners,key=lambda u:u['id'])[0]['id'];cases=profile(owner)
        members=[{'user_id':u['id'],'roles':['Manager','Contributor','Functional','Finance','Authority'] if u['id']==c.user['id'] else ['Contributor']} for u in refs['users'] if u['active'] and not u.get('deleted_at')]
        program={'name':PROGRAM,'client':'Internal evaluation','objective':'Evaluate product and packaging cost opportunities while preserving required value. All examples and estimates are illustrative.','sponsor':'Internal evaluation team','scope':'Actuator assemblies and transport packaging','start':'2026-01-01','end':'2026-12-31','currency':'EUR','fx_basis':'EUR native estimates; no currency effects counted as initiative benefit','recognition_rules':'Comparable baseline and eligible volume; recurring offsets retained; one-time cash spend separate; independent Finance verification only after actual evidence. Evaluation amounts are not a savings claim.','cadence_days':14,'stale_days':30,'approval_threshold':'50000','members':members,'mandatory_evidence':['Function','Quality','Safety'],'targets':[{'scope':'Program','amount':'50000','value_type':'Cost reduction','metric':'In-year net recurring benefit','start':'2026-01-01','end':'2026-12-31'},{'scope':'Actuator assembly','amount':'40000','value_type':'Cost reduction','metric':'In-year net recurring benefit','start':'2026-01-01','end':'2026-12-31'},{'scope':'Actuator packaging','amount':'10000','value_type':'Cost reduction','metric':'In-year net recurring benefit','start':'2026-01-01','end':'2026-12-31'}]}
        proposal={'source_url':c.base,'program':program,'ideas':[{'original':c.call('GET','/ideas/'+i['id']),'case':cases[ref]} for ref,i in selected.items()],'owner_id':owner}
        path.parent.mkdir(parents=True,exist_ok=True)
        assert not path.exists(),'Retain previous adaptation proposals; choose a new private path'
        path.write_text(json.dumps(proposal,indent=2))
        print(json.dumps({'preview':'PREPARED','records':[{'reference':i['original']['reference'],'from':i['original']['title'],'to':i['case']['title']} for i in proposal['ideas']],'program':PROGRAM,'no_business_changes':True}))
    finally:c.close()

def apply(path):
    proposal=json.loads(path.read_text());c=Client()
    try:
        assert c.base==proposal['source_url'],'Apply only to the workspace inspected in this proposal'
        for item in proposal['ideas']:
            try:existing=c.call('GET','/vave/ideas/'+item['original']['id'])
            except urllib.error.HTTPError as e:
                if e.code!=404:raise
                existing=None
            if existing: assert existing['data']['source']==SOURCE,'Do not overwrite an unrelated VAVE case'
            else:
                original=c.call('GET','/ideas/'+item['original']['id'])
                assert original['record_version']==item['original']['record_version'],'Idea changed since the adaptation proposal'
        programs=c.call('GET','/vave/programs');p=next((p for p in programs if p['name']==PROGRAM),None)
        if p is None:p=c.call('POST','/vave/programs',proposal['program'])
        result=[]
        for item in proposal['ideas']:
            id=item['original']['id']
            try:case=c.call('GET','/vave/ideas/'+id)
            except urllib.error.HTTPError as e:
                if e.code!=404:raise
                body={'record_version':item['original']['record_version'],'case':item['case'],'reason':'User-authorized adaptation of existing evaluation ideas; prior evidence retained without copying approvals.'}
                preview=c.call('POST','/vave/programs/'+p['id']+'/adopt/'+id,body)
                case=c.call('POST','/vave/programs/'+p['id']+'/adopt/'+id+'?dry_run=false',{**body,'confirmed':True,'preview_token':preview['preview_token']})
            assert case['program_id']==p['id']
            if item['original']['reference']=='IF-00205':
                def command(case,action,target=None,role=None):return c.call('POST','/vave/ideas/'+id+'/commands',{'record_version':case['record_version'],'action':action,'target':target,'role':role,'reason':'Illustrative evaluation: review completeness only; functional validation and actual savings are not asserted.'})
                if case['status']=='Draft':case=command(case,'Submit')
                for target,role in [(1,'Manager'),(2,'Finance')]:
                    if case['maturity']<target:case=command(case,'Review',target,role);case=command(case,'Advance',target)
            result.append({'id':id,'reference':case['reference'],'title':case['data']['title'],'maturity':case['maturity'],'status':case['status'],'prior_record_retained':case['legacy_available']})
        report=c.call('GET','/vave/programs/'+p['id']+'/report')
        assert Decimal(str(report['totals']['Cost reduction']['approved_forecast']))==0 and Decimal(str(report['totals']['Cost reduction']['verified']))==0
        evidence={'program_id':p['id'],'cases':result,'report':report,'source_ids_preserved':True,'legacy_approvals_copied':False}
        path.with_name(path.stem+'-applied.json').write_text(json.dumps(evidence,indent=2))
        print(json.dumps({'adaptation':'PASS','program_id':p['id'],'cases':result,'approved_forecast':report['totals']['Cost reduction']['approved_forecast'],'verified':report['totals']['Cost reduction']['verified']}))
    finally:c.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','apply']);parser.add_argument('file',type=Path);args=parser.parse_args()
    (prepare if args.action=='prepare' else apply)(args.file)

def apply_on_vps(ssh,path):
    """Retain and compare live preservation evidence around authorized commands."""
    import hashlib,shlex,time
    from vps import run
    stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
    stage='/home/ubuntu/vave-adaptation-'+stamp
    retained='/home/ideaflow/backups/vave-adaptation-'+stamp
    run(ssh,'install -d -m 700 '+shlex.quote(stage))
    source=Path('scripts/vave-fingerprint.py')
    with ssh.open_sftp() as sftp:
        sftp.put(str(source),stage+'/fingerprint.py');sftp.chmod(stage+'/fingerprint.py',0o600)
    assert run(ssh,'sha256sum '+shlex.quote(stage+'/fingerprint.py'),quiet=True).split()[0]==hashlib.sha256(source.read_bytes()).hexdigest()
    run(ssh,'install -d -o ideaflow -g ideaflow -m 700 '+shlex.quote(retained)+'; install -o ideaflow -g ideaflow -m 600 '+shlex.quote(stage+'/fingerprint.py')+' '+shlex.quote(retained+'/fingerprint.py'),sudo=True)
    def app(command):return run(ssh,'cd /home/ideaflow; runuser -u ideaflow -- env XDG_RUNTIME_DIR=/run/user/1001 sh -c '+shlex.quote(command),sudo=True)
    image=app("podman inspect --format '{{.Image}}' ideaflow-backend").strip()
    assert len(image)==64 and all(c in '0123456789abcdef' for c in image)
    utility='podman run --rm --user 0 --network ideaflow --env-file .config/ideaflow/backend.env -v '+shlex.quote(retained+':/check')+' --entrypoint python '+image
    app('sha256sum .config/ideaflow/*.env > '+shlex.quote(retained+'/credentials-before.sha256'))
    app(utility+' /check/fingerprint.py --adoption --output /check/before.json')
    apply(path)
    app(utility+' /check/fingerprint.py --adoption --output /check/after.json --expected /check/before.json')
    app(utility+' -m app.reconciliation')
    app('sha256sum -c '+shlex.quote(retained+'/credentials-before.sha256'))
    evidence={'preservation':'PASS','retained_evidence':retained,'accounts_password_hashes_and_original_financial_rows':'unchanged','original_events':'all preserved; new VAVE decisions appended','source_ids_and_reference_sequence':'unchanged'}
    path.with_name(path.stem+'-preservation.json').write_text(json.dumps(evidence,indent=2))
    print(json.dumps(evidence))
