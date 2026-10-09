from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Money = Decimal
Role = Literal['User','Admin']
class Input(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

class Login(Input):
    email: str
    password: str

class UserCreate(Input):
    name: str = Field(min_length=1,max_length=120)
    email: str = Field(min_length=3,max_length=254)
    role: Role
    password: str = Field(min_length=12,max_length=256)

class UserUpdate(Input):
    record_version: int
    name: str = Field(min_length=1,max_length=120)
    role: Role
    active: bool
    password: str | None = Field(default=None,min_length=12,max_length=256)

class AccountCommand(Input):
    record_version: int
    reason: str = Field(min_length=1,max_length=20000)

class IdeaFields(Input):
    title: str = Field(min_length=1,max_length=240)
    problem: str = Field(min_length=1,max_length=20000)
    solution: str = Field(min_length=1,max_length=20000)
    site_id: str | None = None
    category_id: str | None = None
    site_name: str | None = Field(default=None,max_length=120)
    category_name: str | None = Field(default=None,max_length=120)
    owner_id: str | None = None
    expected_start: date | None = None
    expected_finish: date | None = None
    @model_validator(mode='after')
    def date_order(self):
        if self.expected_start and self.expected_finish and self.expected_finish < self.expected_start:
            raise ValueError('Expected finish must follow expected start')
        return self

class IdeaCreate(IdeaFields):
    annual_gross: Decimal | None = Field(default=None,ge=0,max_digits=18,decimal_places=2)
    annual_recurring: Decimal | None = Field(default=None,ge=0,max_digits=18,decimal_places=2)
    upfront: Decimal | None = Field(default=None,ge=0,max_digits=18,decimal_places=2)
    probability: Decimal | None = Field(default=None,ge=0,le=1)
    confidence: Decimal | None = Field(default=None,ge=0,le=1)

class IdeaUpdate(IdeaFields):
    record_version: int
    screening_note: str = Field(default='',max_length=20000)
    evidence_url: str = Field(default='',max_length=2048)
    progress: int = Field(default=0,ge=0,le=100)
    actual_start: date | None = None
    actual_completion: date | None = None
    @field_validator('evidence_url')
    @classmethod
    def url(cls,v):
        if v and not v.startswith(('https://','http://')): raise ValueError('Use an http or https evidence URL')
        return v
    @model_validator(mode='after')
    def actual_order(self):
        if self.actual_start and self.actual_completion and self.actual_completion < self.actual_start:
            raise ValueError('Actual completion must follow actual start')
        return self

class Command(Input):
    record_version: int
    reason: str = Field(min_length=1,max_length=20000)

class IdeaRemovalCommand(Command):
    confirm: Literal[True]

class RestoreIdea(IdeaRemovalCommand):
    owner_id: str | None = None
    reassign_inactive_tasks: bool = False

class Transition(Command):
    action: str
    verification_through: date | None = None
    confirm_completion: bool = False

class TaskInput(Input):
    record_version: int
    title: str = Field(min_length=1,max_length=240)
    assignee_id: str
    due_date: date | None = None
    status: Literal['Open','In progress','Done'] = 'Open'
    required: bool = True

class CommentInput(Input):
    record_version: int
    body: str = Field(min_length=1,max_length=20000)

class Period(Input):
    month: date
    gross: Decimal = Field(ge=0,max_digits=18,decimal_places=2)
    recurring: Decimal = Field(ge=0,max_digits=18,decimal_places=2)
    spend: Decimal = Field(ge=0,max_digits=18,decimal_places=2)
    @field_validator('month')
    @classmethod
    def normalized(cls,v):
        if v.day != 1: raise ValueError('Month must be its first day')
        return v

class PlanInput(Input):
    record_version: int
    annual_gross: Decimal | None = Field(default=None,ge=0,max_digits=18,decimal_places=2)
    annual_recurring: Decimal | None = Field(default=None,ge=0,max_digits=18,decimal_places=2)
    upfront: Decimal | None = Field(default=None,ge=0,max_digits=18,decimal_places=2)
    probability: Decimal | None = Field(default=None,ge=0,le=1)
    confidence: Decimal | None = Field(default=None,ge=0,le=1)
    rationale: str = Field(default='',max_length=20000)
    periods: list[Period] = Field(default_factory=list,max_length=120)
    @field_validator('periods')
    @classmethod
    def unique(cls,v):
        if len({p.month for p in v}) != len(v): raise ValueError('Duplicate plan month')
        return sorted(v,key=lambda p:p.month)

class RampInput(Input):
    start_month: date
    ramp_months: int = Field(ge=1,le=24)
    horizon: int = Field(ge=1,le=120)
    spend_months: int = Field(ge=1,le=24)
    annual_gross: Decimal = Field(ge=0)
    annual_recurring: Decimal = Field(ge=0)
    upfront: Decimal = Field(ge=0)
    @field_validator('start_month')
    @classmethod
    def normalized(cls,v):
        if v.day != 1: raise ValueError('Start month must be its first day')
        return v
    @model_validator(mode='after')
    def allocation(self):
        if self.spend_months > self.horizon: raise ValueError('Spend allocation exceeds horizon')
        return self

class ResultInput(Input):
    record_version: int
    period_version: int = 0
    gross: Decimal | None = Field(default=None,ge=0,max_digits=18,decimal_places=2)
    recurring: Decimal | None = Field(default=None,ge=0,max_digits=18,decimal_places=2)
    spend: Decimal | None = Field(default=None,ge=0,max_digits=18,decimal_places=2)
    reason: str = Field(default='',max_length=20000)

class VerifyInput(Command):
    period_version: int
    gross: Decimal = Field(ge=0,max_digits=18,decimal_places=2)
    recurring: Decimal = Field(ge=0,max_digits=18,decimal_places=2)
    spend: Decimal = Field(ge=0,max_digits=18,decimal_places=2)

class RevokeInput(Command):
    period_version: int

class Assignment(Input):
    record_version: int
    owner_id: str

class ReferenceInput(Input):
    id: str | None = Field(default=None,min_length=1,max_length=80)
    label: str = Field(min_length=1,max_length=120)
    business_unit: str = Field(default='',max_length=120)

class ReferenceUpdate(Input):
    record_version: int
    label: str = Field(min_length=1,max_length=120)
    business_unit: str = Field(default='',max_length=120)
    reason: str = Field(min_length=1,max_length=20000)

class ReferenceMerge(Input):
    record_version: int
    target_id: str
    target_version: int
    reason: str = Field(min_length=1,max_length=20000)
