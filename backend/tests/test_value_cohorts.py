import uuid
from datetime import date
from decimal import Decimal as D
from sqlalchemy import select,text
from sqlalchemy.exc import DBAPIError
import pytest
from app import domain as domain
from app.models import User,PlanPeriod,ValuePeriod
from app.schemas import IdeaCreate,IdeaUpdate,PlanInput,Period,Transition,ResultInput,VerifyInput
from app.queries import value_dashboard
from app.financial import app_today,add_month

def test_snapshot_immutability_matched_cohorts_and_draft_exclusion(db):
    admin=db.scalar(select(User).where(User.role=='Admin'));month=add_month(app_today().replace(day=1),-2);next_month=add_month(month,1)
    ideas=[]
    for index in range(2):
        idea=domain.create_idea(db,admin,IdeaCreate(title='Cohort '+uuid.uuid4().hex,problem='Measured baseline',solution='Pilot',site_id='Tampa',category_id='Energy',expected_start=month,expected_finish=next_month))
        domain.transition(db,admin,idea,Transition(record_version=idea.record_version,action='Screening',reason='Review'))
        fields={k:getattr(idea,k) for k in IdeaUpdate.model_fields if k!='record_version'};fields['screening_note']='Baseline accepted'
        domain.update_idea(db,admin,idea,IdeaUpdate(**fields,record_version=idea.record_version))
        domain.transition(db,admin,idea,Transition(record_version=idea.record_version,action='Analysis',reason='Develop'))
        plan=domain.save_plan(db,admin,idea,PlanInput(record_version=idea.record_version,annual_gross=120000,annual_recurring=12000,upfront=10000,probability=D('.7'),confidence=D('.1'),periods=[Period(month=month,gross=1000,recurring=100,spend=1000),Period(month=next_month,gross=2000,recurring=200,spend=0)]))
        domain.transition(db,admin,idea,Transition(record_version=idea.record_version,action='Approved',reason='Plan reviewed'))
        ideas.append(idea)
    result=domain.save_result(db,admin,ideas[0],month,ResultInput(record_version=ideas[0].record_version,gross=800,recurring=100,spend=1000))
    domain.verify_result(db,admin,ideas[0],month,VerifyInput(record_version=ideas[0].record_version,period_version=result.record_version,gross=750,recurring=100,spend=1000,reason='Meter adjustment'))
    dash=value_dashboard(db,ideas,month,next_month)
    assert dash['planned']['net_benefit']==D(5400)
    assert dash['planned']['risk_adjusted_benefit']==D(3780)
    assert dash['coverage']=={'eligible':4,'reported':1,'verified':1}
    assert dash['actual']['net_benefit']==D(700) and dash['verified']['net_benefit']==D(650)
    assert dash['expected_reported_cohort']==D(900) and dash['expected_verified_cohort']==D(900)
    assert dash['planned']['roi']['value']==D(170)
    assert dash['actual']['roi']['value']==D(-30)
    # A saved revision must not silently replace the approved forecast.
    domain.save_plan(db,admin,ideas[1],PlanInput(record_version=ideas[1].record_version,annual_gross=999999,annual_recurring=0,upfront=0,probability=1,periods=[Period(month=month,gross=999999,recurring=0,spend=0)]))
    assert value_dashboard(db,ideas,month,next_month)['planned']['net_benefit']==D(5400)
    approved=domain.approved_plan(db,ideas[0])
    with pytest.raises(DBAPIError):
        with db.begin_nested():db.execute(text('UPDATE financial_plan SET annual_gross=1 WHERE id=:id'),{'id':approved.id})
    with pytest.raises(DBAPIError):
        with db.begin_nested():db.execute(text('UPDATE financial_plan_period SET gross=1 WHERE plan_id=:id'),{'id':approved.id})
    domain.transition(db,admin,ideas[0],Transition(record_version=ideas[0].record_version,action='Analysis',reason='Revise baseline'))
    dash=value_dashboard(db,ideas,month,next_month)
    assert dash['planned']['net_benefit']==D(2700) and dash['verified']['net_benefit']==D(650)
