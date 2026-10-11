import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import String, Text, Date, DateTime, Numeric, ForeignKey, UniqueConstraint, CheckConstraint, Boolean, Integer, JSON, Sequence
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base, now

def uid(): return str(uuid.uuid4())
money = Numeric(18, 2)

class User(Base):
    __tablename__ = 'app_user'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), unique=True)
    role: Mapped[str] = mapped_column(String(20))
    password_hash: Mapped[str] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(default=True)
    record_version: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (CheckConstraint("role IN ('User','Admin')", name='user_role'),)

class AccountEvent(Base):
    __tablename__ = 'account_event'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    actor_id: Mapped[str] = mapped_column(ForeignKey('app_user.id'))
    subject_id: Mapped[str] = mapped_column(String(36))
    subject_name: Mapped[str] = mapped_column(String(120))
    action: Mapped[str] = mapped_column(String(80))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    reason: Mapped[str] = mapped_column(Text, default='')

class Session(Base):
    __tablename__ = 'app_session'
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('app_user.id'))
    csrf: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class Site(Base):
    __tablename__ = 'site'
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    label: Mapped[str] = mapped_column(String(120))
    business_unit: Mapped[str] = mapped_column(String(120))
    active: Mapped[bool] = mapped_column(default=True)
    label_key: Mapped[str] = mapped_column(String(120), unique=True)
    record_version: Mapped[int] = mapped_column(default=1)
    merged_into: Mapped[str | None] = mapped_column(String(80))

class Category(Base):
    __tablename__ = 'category'
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    label: Mapped[str] = mapped_column(String(120))
    active: Mapped[bool] = mapped_column(default=True)
    label_key: Mapped[str] = mapped_column(String(120), unique=True)
    record_version: Mapped[int] = mapped_column(default=1)
    merged_into: Mapped[str | None] = mapped_column(String(80))

class DemoBatch(Base):
    __tablename__ = 'demo_batch'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    batch_key: Mapped[str] = mapped_column(String(120), unique=True)
    seed: Mapped[int] = mapped_column(Integer)
    anchor_date: Mapped[date] = mapped_column(Date)
    importer: Mapped[str] = mapped_column(ForeignKey('app_user.id'))
    counts: Mapped[dict] = mapped_column(JSON, default=dict)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

reference_seq = Sequence('idea_reference_seq')

class Idea(Base):
    __tablename__ = 'idea'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    reference: Mapped[str] = mapped_column(String(30), unique=True)
    title: Mapped[str] = mapped_column(String(240))
    problem: Mapped[str] = mapped_column(Text)
    solution: Mapped[str] = mapped_column(Text)
    submitter_id: Mapped[str] = mapped_column(ForeignKey('app_user.id'))
    owner_id: Mapped[str] = mapped_column(ForeignKey('app_user.id'))
    site_id: Mapped[str | None] = mapped_column(ForeignKey('site.id'))
    category_id: Mapped[str | None] = mapped_column(ForeignKey('category.id'))
    stage: Mapped[str] = mapped_column(String(30), default='New')
    disposition: Mapped[str] = mapped_column(String(30), default='Active')
    progress: Mapped[int] = mapped_column(default=0)
    screening_note: Mapped[str] = mapped_column(Text, default='')
    evidence_url: Mapped[str] = mapped_column(Text, default='')
    expected_start: Mapped[date | None] = mapped_column(Date)
    expected_finish: Mapped[date | None] = mapped_column(Date)
    actual_start: Mapped[date | None] = mapped_column(Date)
    actual_completion: Mapped[date | None] = mapped_column(Date)
    verification_through: Mapped[date | None] = mapped_column(Date)
    record_version: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    stage_entered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    external_key: Mapped[str | None] = mapped_column(String(240), unique=True)
    demo_batch_id: Mapped[str | None] = mapped_column(ForeignKey('demo_batch.id'))
    is_test: Mapped[bool] = mapped_column(Boolean, default=False, server_default='false')
    removed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    removed_by: Mapped[str | None] = mapped_column(ForeignKey('app_user.id'))
    removal_reason: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (
        CheckConstraint('(removed_at IS NULL AND removed_by IS NULL AND removal_reason IS NULL) OR (removed_at IS NOT NULL AND removed_by IS NOT NULL AND removal_reason IS NOT NULL AND length(trim(removal_reason)) > 0)',name='removal_metadata'),
        CheckConstraint('progress BETWEEN 0 AND 100'),
        CheckConstraint("stage IN ('New','Screening','Analysis','Approved','Implementation','Validation','Realized')"),
        CheckConstraint("disposition IN ('Active','On hold','Rejected','Cancelled')"),
        CheckConstraint('expected_finish IS NULL OR expected_start IS NULL OR expected_finish >= expected_start'),
        CheckConstraint('actual_completion IS NULL OR actual_start IS NULL OR actual_completion >= actual_start'),
    )

class FinancialPlan(Base):
    __tablename__ = 'financial_plan'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    idea_id: Mapped[str] = mapped_column(ForeignKey('idea.id'), index=True)
    version: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default='Draft')
    annual_gross: Mapped[Decimal | None] = mapped_column(money)
    annual_recurring: Mapped[Decimal | None] = mapped_column(money)
    upfront: Mapped[Decimal | None] = mapped_column(money)
    probability: Mapped[Decimal | None] = mapped_column(Numeric(6,5))
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(6,5))
    rationale: Mapped[str] = mapped_column(Text, default='')
    approved_by: Mapped[str | None] = mapped_column(ForeignKey('app_user.id'))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    plan_currency: Mapped[str] = mapped_column(String(3), default='USD')
    __table_args__ = (UniqueConstraint('idea_id','version'),
        CheckConstraint("status IN ('Draft','Approved','Superseded','Invalidated')"),
        CheckConstraint("plan_currency = 'USD'"),
        CheckConstraint('annual_gross >= 0 AND annual_recurring >= 0 AND upfront >= 0'),
        CheckConstraint('probability BETWEEN 0 AND 1 AND confidence BETWEEN 0 AND 1'))

class PlanPeriod(Base):
    __tablename__ = 'financial_plan_period'
    plan_id: Mapped[str] = mapped_column(ForeignKey('financial_plan.id'), primary_key=True)
    month: Mapped[date] = mapped_column(Date, primary_key=True)
    gross: Mapped[Decimal] = mapped_column(money)
    recurring: Mapped[Decimal] = mapped_column(money)
    spend: Mapped[Decimal] = mapped_column(money)
    __table_args__ = (CheckConstraint('gross >= 0 AND recurring >= 0 AND spend >= 0'), CheckConstraint('EXTRACT(DAY FROM month) = 1'))

class ValuePeriod(Base):
    __tablename__ = 'value_period'
    idea_id: Mapped[str] = mapped_column(ForeignKey('idea.id'), primary_key=True)
    month: Mapped[date] = mapped_column(Date, primary_key=True)
    gross: Mapped[Decimal | None] = mapped_column(money)
    recurring: Mapped[Decimal | None] = mapped_column(money)
    spend: Mapped[Decimal | None] = mapped_column(money)
    verified_gross: Mapped[Decimal | None] = mapped_column(money)
    verified_recurring: Mapped[Decimal | None] = mapped_column(money)
    verified_spend: Mapped[Decimal | None] = mapped_column(money)
    verified_by: Mapped[str | None] = mapped_column(ForeignKey('app_user.id'))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reason: Mapped[str] = mapped_column(Text, default='')
    record_version: Mapped[int] = mapped_column(default=1)
    __table_args__ = (CheckConstraint('gross >= 0 AND recurring >= 0 AND spend >= 0'),
        CheckConstraint('verified_gross >= 0 AND verified_recurring >= 0 AND verified_spend >= 0'), CheckConstraint('EXTRACT(DAY FROM month) = 1'))

class Task(Base):
    __tablename__ = 'task'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    idea_id: Mapped[str] = mapped_column(ForeignKey('idea.id'), index=True)
    title: Mapped[str] = mapped_column(String(240))
    assignee_id: Mapped[str] = mapped_column(ForeignKey('app_user.id'))
    due_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default='Open')
    required: Mapped[bool] = mapped_column(default=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (CheckConstraint("status IN ('Open','In progress','Done')"),)

class Comment(Base):
    __tablename__ = 'comment'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    idea_id: Mapped[str] = mapped_column(ForeignKey('idea.id'), index=True)
    actor_id: Mapped[str] = mapped_column(ForeignKey('app_user.id'))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class IdeaEvent(Base):
    __tablename__ = 'idea_event'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    idea_id: Mapped[str] = mapped_column(ForeignKey('idea.id'), index=True)
    sequence: Mapped[int] = mapped_column(Integer)
    activity: Mapped[str] = mapped_column(String(80))
    event_type: Mapped[str] = mapped_column(String(80))
    from_stage: Mapped[str | None] = mapped_column(String(30))
    to_stage: Mapped[str | None] = mapped_column(String(30))
    from_disposition: Mapped[str | None] = mapped_column(String(30))
    to_disposition: Mapped[str | None] = mapped_column(String(30))
    actor_id: Mapped[str] = mapped_column(ForeignKey('app_user.id'))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    reason: Mapped[str] = mapped_column(Text, default='')
    changes: Mapped[dict] = mapped_column(JSON, default=dict)
    provenance: Mapped[dict | None] = mapped_column(JSON)
    __table_args__ = (UniqueConstraint('idea_id','sequence'),)
