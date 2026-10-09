from decimal import Decimal
from app.financial import app_today,add_month
from test_workflow import make,get,move,update,P

def test_idea_timeline_custom_range_and_unknown_results(clients):
    user=clients['User'];month=add_month(app_today().replace(day=1),-1)
    end=add_month(month,11);idea=make(user,expected_start=month.isoformat(),expected_finish=month.isoformat());id=idea['id']
    assert get(user,id)['financials']['start']==month.isoformat()
    assert move(user,id,'Screening').status_code==200
    assert update(user,id,screening_note='Baseline accepted').status_code==200
    assert move(user,id,'Analysis').status_code==200
    rows=[{'month':add_month(month,n).isoformat(),'gross':'1000','recurring':'100','spend':'3000' if n==0 else '0'} for n in range(12)]
    response=user.post(P+'/ideas/'+id+'/plans',json={'record_version':get(user,id)['record_version'],'annual_gross':'12000','annual_recurring':'1200','upfront':'3000','probability':'0.8','confidence':'0.6','periods':rows})
    assert response.status_code==200,response.text
    draft=get(user,id)['financials']
    assert (draft['start'],draft['end'])==(month.isoformat(),end.isoformat())
    assert len(draft['series'])==12 and all(r['expected'] is None for r in draft['series'])
    assert move(user,id,'Approved').status_code==200
    before=get(user,id);value=before['financials']
    assert Decimal(value['planned']['roi']['value'])==260
    assert Decimal(value['planned']['net_benefit'])==10800
    assert value['coverage']=={'eligible':1,'reported':0,'verified':0}
    assert all(r['actual'] is None and r['verified'] is None for r in value['series'])
    path=P+'/ideas/'+id+'/value'
    custom=user.get(path,params={'start':month.isoformat(),'end':month.isoformat()}).json()
    assert len(custom['series'])==1 and Decimal(custom['planned']['net_benefit'])==900
    assert Decimal(custom['planned']['roi']['value'])==-70
    assert {k:v for k,v in get(user,id).items() if k!='financials'}=={k:v for k,v in before.items() if k!='financials'},'Viewing another range must not change plans/results/history/version'
    for params in ({'start':'bad'},{'start':end.isoformat(),'end':month.isoformat()},{'start':month.replace(day=2).isoformat()},{'start':month.isoformat(),'end':add_month(month,120).isoformat()}):
        assert user.get(path,params=params).status_code==422
    result=user.put(P+'/ideas/'+id+'/results/'+month.isoformat(),json={'record_version':before['record_version'],'period_version':0,'gross':'800','recurring':'100','spend':'3000'}).json()
    unverified=user.get(path).json();assert unverified['coverage']['reported']==1 and unverified['coverage']['verified']==0
    assert Decimal(unverified['series'][0]['actual'])==700 and unverified['series'][0]['verified'] is None
    assert all(r['actual'] is None for r in unverified['series'][1:])
    response=user.post(P+'/ideas/'+id+'/results/'+month.isoformat()+'/verify',json={'record_version':get(user,id)['record_version'],'period_version':result['record_version'],'gross':'800','recurring':'100','spend':'3000','reason':'Reviewed against baseline'})
    assert response.status_code==200,response.text
    verified=user.get(path).json();assert verified['coverage']['verified']==1
    assert Decimal(verified['series'][0]['cumulative_verified'])==700
    assert Decimal(verified['actual']['roi']['value']).quantize(Decimal('.1'))==Decimal('-76.7')
    assert all(r['cumulative_verified'] is None for r in verified['series'][1:])
    # A new draft and an older displayed snapshot must not replace the current approved horizon.
    response=user.post(P+'/ideas/'+id+'/plans',json={'record_version':get(user,id)['record_version'],'annual_gross':'12000','annual_recurring':'1200','upfront':'3000','probability':'0.8','periods':[{'month':add_month(end,1).isoformat(),'gross':'2000','recurring':'100','spend':'3000'}]})
    assert response.status_code==200,response.text
    assert user.get(path).json()['end']==end.isoformat()
    admin=clients['Admin'];current=get(admin,id)
    assert admin.post(P+'/ideas/'+id+'/remove',json={'record_version':current['record_version'],'reason':'Archive isolated fixture','confirm':True}).status_code==200
    assert user.get(path).status_code==403
    assert admin.get(path).json()['end']==end.isoformat()

def test_result_month_extends_idea_timeline_and_empty_fallback(clients):
    user=clients['User'];idea=make(user);id=idea['id'];today=app_today().replace(day=1)
    empty=get(user,id)['financials'];assert empty['start']==empty['end']==today.isoformat()
    month=add_month(today,-15)
    response=user.put(P+'/ideas/'+id+'/results/'+month.isoformat(),json={'record_version':idea['record_version'],'period_version':0,'gross':None,'recurring':'0','spend':'0'})
    assert response.status_code==200,response.text
    value=user.get(P+'/ideas/'+id+'/value').json()
    assert value['start']==value['end']==month.isoformat()
    assert value['series'][0]['actual'] is None and value['actual']['roi']['label']=='Insufficient data'
