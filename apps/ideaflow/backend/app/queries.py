from datetime import date
from decimal import Decimal
from sqlalchemy import select, or_
from .models import Idea, Site, User, FinancialPlan, PlanPeriod, ValuePeriod, Task
from .domain import plans, approved_plan, scalar_json
from .financial import app_today, add_month, net, sum_known, schedule_metrics, roi

def serialize(obj): return {c.name:scalar_json(getattr(obj,c.name)) for c in obj.__table__.columns if c.name!='is_test'}

def selected_ideas(db,filters,removed=False):
    q=select(Idea).outerjoin(Site,Idea.site_id==Site.id).where(Idea.removed_at.is_not(None) if removed else Idea.removed_at.is_(None))
    for key in ('site_id','category_id','owner_id','stage','disposition'):
        if filters.get(key): q=q.where(getattr(Idea,key)==filters[key])
    if filters.get('business_unit'): q=q.where(Site.business_unit==filters['business_unit'])
    if filters.get('search'):
        term='%'+filters['search']+'%';q=q.where(or_(Idea.title.ilike(term),Idea.problem.ilike(term),Idea.reference.ilike(term)))
    if filters.get('created_from'): q=q.where(Idea.created_at>=filters['created_from'])
    if filters.get('created_to'):
        from datetime import timedelta
        q=q.where(Idea.created_at<(date.fromisoformat(filters['created_to'])+timedelta(days=1)).isoformat())
    if filters.get('ids'): q=q.where(Idea.id.in_(filters['ids'].split(',')))
    return list(db.scalars(q))

def idea_row(db,idea):
    ps=plans(db,idea);latest=ps[-1] if ps else None
    return {**serialize(idea),'owner_name':db.get(User,idea.owner_id).name,'site':db.get(Site,idea.site_id).label if idea.site_id else 'Unassigned',
        'annual_net_potential':scalar_json(net(latest.annual_gross,latest.annual_recurring)) if latest else None,
        'stage_age_days':round((__import__('app.db',fromlist=['now']).now()-idea.stage_entered_at).total_seconds()/86400,1)}

def idea_value_dashboard(db,idea,start=None,end=None):
    """Use the current financial schedule and results, rather than a calendar year."""
    ps=plans(db,idea);plan=approved_plan(db,idea) or (ps[-1] if ps else None)
    months=list(db.scalars(select(PlanPeriod.month).where(PlanPeriod.plan_id==plan.id))) if plan else []
    months+=list(db.scalars(select(ValuePeriod.month).where(ValuePeriod.idea_id==idea.id)))
    if not months:
        months=[d.replace(day=1) for d in (idea.expected_start,idea.expected_finish,idea.actual_start,idea.actual_completion) if d]
    if not months:months=[app_today().replace(day=1)]
    first,last=min(months),max(months)
    clipped=(last.year-first.year)*12+last.month-first.month>119
    if clipped:first=add_month(last,-119)
    result=value_dashboard(db,[idea],start or first,end or last)
    return {**result,'idea_timeline':{'start':first,'end':last,'clipped':clipped}}

def value_dashboard(db,ideas,start=None,end=None,include_hold=True,as_of=None):
    today=app_today();start=start or today.replace(month=1,day=1);end=end or today.replace(month=12,day=1)
    if start.day!=1 or end.day!=1 or end<start: from .domain import fail;fail('Use a valid first-of-month range')
    if (end.year-start.year)*12+end.month-start.month>119: from .domain import fail;fail('Horizon cannot exceed 120 months')
    elapsed=(as_of.date() if as_of else today).replace(day=1)
    if as_of and as_of.date()!=today:
        from .domain import fail
        fail('Historical financial as-of reconstruction is unavailable. Use the current as-of date; historical lifecycle analysis is supported in Process.')
    eligible=reported=verified=0;series=[];variance=[];annual=[];full=[];actual_rows=[];verified_rows=[];actual_cohort=[];verified_cohort=[]
    monthly={};cursor=start
    while cursor<=end:
        monthly[cursor]={'month':cursor,'expected':[],'actual':[],'verified':[],'planned_spend':[],'actual_spend':[],'verified_spend':[],'risk_adjusted':[],
            'expected_reported':[],'expected_verified':[],'eligible':0,'reported':0,'verified_count':0}
        cursor=add_month(cursor,1)
    for idea in ideas:
        ps=plans(db,idea);latest=ps[-1] if ps else None
        if latest and idea.disposition not in ('Rejected','Cancelled') and (include_hold or idea.disposition!='On hold'): annual.append(net(latest.annual_gross,latest.annual_recurring))
        plan=approved_plan(db,idea)
        forecast=bool(plan and idea.disposition not in ('Rejected','Cancelled') and (include_hold or idea.disposition!='On hold'))
        periods={p.month:p for p in db.scalars(select(PlanPeriod).where(PlanPeriod.plan_id==plan.id))} if plan else {}
        values={p.month:p for p in db.scalars(select(ValuePeriod).where(ValuePeriod.idea_id==idea.id))}
        ir=[];iv=[];ip=[];er=[];ev=[]
        for month,m in monthly.items():
            p=periods.get(month);v=values.get(month) if month<elapsed else None
            expected=net(p.gross,p.recurring) if p else None
            if p and forecast:
                m['expected'].append(expected);m['planned_spend'].append(p.spend);ip.append({'month':month,'net':expected,'spend':p.spend})
                m['risk_adjusted'].append(expected*plan.probability if plan.probability is not None else None)
                if month<elapsed: eligible+=1;m['eligible']+=1
            if v:
                actual=net(v.gross,v.recurring)
                if actual is not None:
                    m['actual'].append(actual);m['actual_spend'].append(v.spend);ir.append({'month':month,'net':actual,'spend':v.spend})
                    if p and forecast:
                        reported+=1;m['reported']+=1;er.append(expected);m['expected_reported'].append(expected);actual_cohort.append({'month':month,'net':expected,'spend':p.spend})
                confirmed=net(v.verified_gross,v.verified_recurring)
                if confirmed is not None:
                    m['verified'].append(confirmed);m['verified_spend'].append(v.verified_spend);iv.append({'month':month,'net':confirmed,'spend':v.verified_spend})
                    if p and forecast:
                        verified+=1;m['verified_count']+=1;ev.append(expected);m['expected_verified'].append(expected);verified_cohort.append({'month':month,'net':expected,'spend':p.spend})
        full+=ip;actual_rows+=ir;verified_rows+=iv
        variance.append({'idea_id':idea.id,'reference':idea.reference,'title':idea.title,'disposition':idea.disposition,'plan_version':plan.version if plan else None,
            'expected_horizon':sum_known(r['net'] for r in ip),'expected_reported_cohort':sum_known(er),'actual':sum_known(r['net'] for r in ir),
            'expected_verified_cohort':sum_known(ev),'verified':sum_known(r['net'] for r in iv),
            'variance_reported':net(sum_known(r['net'] for r in ir),sum_known(er)), 'planned':schedule_metrics(ip,plan.probability if plan else None)})
    planned_portfolio=[];cumulative={'expected':Decimal(0),'actual':Decimal(0),'verified':Decimal(0),'planned_cash':Decimal(0),'actual_cash':Decimal(0)}
    for month,m in monthly.items():
        row={k:sum_known(m[k]) for k in ('expected','actual','verified','planned_spend','actual_spend','verified_spend','expected_reported','expected_verified','risk_adjusted')}
        for k in ('expected','actual','verified'):
            if row[k] is not None: cumulative[k]+=row[k]
            row['cumulative_'+k]=cumulative[k] if row[k] is not None else None
        planned_cash=net(row['expected'],row['planned_spend']);actual_cash=net(row['actual'],row['actual_spend'])
        for k,v in [('planned_cash',planned_cash),('actual_cash',actual_cash)]:
            if v is not None: cumulative[k]+=v
            row['cumulative_'+k]=cumulative[k] if v is not None else None
        if row['expected'] is not None: planned_portfolio.append({'month':month,'net':row['expected'],'spend':row['planned_spend']})
        series.append({'month':month,**row,**{k:m[k] for k in ('eligible','reported','verified_count')}})
    return {'as_of':as_of or __import__('app.db',fromlist=['now']).now(),'start':start,'end':end,'include_hold':include_hold,
        'annual_net_potential':sum(v for v in annual if v is not None) if any(v is not None for v in annual) else None,
        'annual_assessed':sum(v is not None for v in annual),'annual_total':len(annual),'coverage':{'eligible':eligible,'reported':reported,'verified':verified},
        'planned':{**schedule_metrics(planned_portfolio),'risk_adjusted_benefit':sum_known(s['risk_adjusted'] for s in series if s['expected'] is not None)},'actual':schedule_metrics(actual_rows),'verified':schedule_metrics(verified_rows),
        'expected_reported_cohort':sum_known(r['net'] for r in actual_cohort),'expected_verified_cohort':sum_known(r['net'] for r in verified_cohort),
        'series':series,'variance':variance,'cohort_note':'Current valid approved plans; rejected/cancelled forecasts excluded. Historical actual and verified value retained. Missing results are unknown. Comparisons use matched idea-months.'}
