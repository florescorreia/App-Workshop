import os
from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

D=Decimal
def app_today(): return datetime.now(ZoneInfo(os.getenv('APP_TIMEZONE','America/New_York'))).date()
def add_month(month,n):
    total=month.year*12+month.month-1+n
    return date(total//12,total%12+1,1)
def sum_known(values):
    values=list(values)
    return sum(values,D(0)) if values and all(v is not None for v in values) else None
def net(gross,recurring): return gross-recurring if gross is not None and recurring is not None else None
def roi(benefit,spend):
    if benefit is None or spend is None: return {'value':None,'label':'Insufficient data'}
    if spend==0: return {'value':None,'label':'Not applicable'}
    return {'value':(benefit-spend)/spend*100,'label':'ROI'}
def payback(rows):
    if not rows: return {'label':'Insufficient data','month':None,'elapsed_months':None}
    if any(r.get('net') is None or r.get('spend') is None for r in rows): return {'label':'Insufficient data','month':None,'elapsed_months':None}
    if sum(r['spend'] for r in rows)==0: return {'label':'No upfront investment','month':None,'elapsed_months':0}
    cash=D(0); cumulative=[];first_spend=None
    for i,r in enumerate(rows):
        if r['spend']>0 and first_spend is None: first_spend=i
        cash+=r['net']-r['spend'];cumulative.append(cash)
    negative=False
    for i,cash in enumerate(cumulative):
        if cash<0: negative=True
        elif negative and all(v>=0 for v in cumulative[i:]):
            return {'label':'Planned cash payback','month':rows[i]['month'],'elapsed_months':i-first_spend+1}
    if not negative: return {'label':'No upfront investment','month':None,'elapsed_months':0}
    return {'label':'Beyond plan horizon','month':None,'elapsed_months':None}

def schedule_metrics(rows,probability=None):
    rows=sorted(rows,key=lambda r:r['month'])
    benefit=sum_known(r['net'] for r in rows);spend=sum_known(r['spend'] for r in rows)
    return {'net_benefit':benefit,'implementation_spend':spend,'net_cash_flow':net(benefit,spend),
        'risk_adjusted_benefit':benefit*probability if benefit is not None and probability is not None else None,
        'roi':roi(benefit,spend),'payback':payback(rows)}

def ramp(data):
    cents=D('0.01'); spend=(data.upfront/data.spend_months).quantize(cents)
    rows=[]
    for i in range(data.horizon):
        factor=min(D(i+1)/data.ramp_months,D(1))
        allocation=spend if i<data.spend_months else D(0)
        if i==data.spend_months-1: allocation=data.upfront-spend*(data.spend_months-1)
        rows.append({'month':add_month(data.start_month,i),'gross':(data.annual_gross/12*factor).quantize(cents),
            'recurring':(data.annual_recurring/12*factor).quantize(cents),'spend':allocation})
    return rows
