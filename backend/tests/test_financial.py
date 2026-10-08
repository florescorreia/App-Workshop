from decimal import Decimal as D
from datetime import date
from app.financial import schedule_metrics, net, roi, payback, ramp, sum_known
from app.schemas import RampInput

def test_contract_example():
    rows=[{'month':date(2026,1,1),'net':D(0),'spend':D(30000)}]+[{'month':date(2026,m,1),'net':D(9000),'spend':D(0)} for m in range(2,13)]
    metrics=schedule_metrics(rows,D('.7'))
    assert net(D(120000),D(12000))==D(108000)
    assert metrics['net_benefit']==D(99000)
    assert metrics['net_cash_flow']==D(69000)
    assert metrics['roi']['value']==D(230)
    assert metrics['payback']=={'label':'Planned cash payback','month':date(2026,5,1),'elapsed_months':5}
    assert metrics['risk_adjusted_benefit']==D(69300)

def test_zero_unknown_and_sustained_payback():
    assert roi(D(20),D(0))['label']=='Not applicable'
    assert roi(D(20),None)['label']=='Insufficient data'
    assert net(None,D(0)) is None
    assert sum_known([None,D(1)]) is None
    assert schedule_metrics([])['net_benefit'] is None
    rows=[{'month':date(2026,m,1),'net':D(n),'spend':D(s)} for m,n,s in [(1,0,10),(2,20,0),(3,0,30),(4,30,0)]]
    assert payback(rows)['month']==date(2026,4,1)
    assert payback(rows[:3])['label']=='Beyond plan horizon'

def test_ramp_rounding_and_allocation():
    data=RampInput(start_month=date(2026,1,1),ramp_months=3,horizon=12,spend_months=3,annual_gross=D(120000),annual_recurring=D(12000),upfront=D('100.01'))
    rows=ramp(data)
    assert sum(r['spend'] for r in rows)==D('100.01')
    assert rows[0]['gross']==D('3333.33') and rows[2]['gross']==D('10000.00')
