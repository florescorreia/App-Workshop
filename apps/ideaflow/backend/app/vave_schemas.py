from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator

Role = Literal['Contributor','Manager','Functional','Finance','Authority','Viewer','External']
ValueType = Literal['Cost reduction','Cost avoidance','Working capital','Capacity','Revenue','Nonfinancial']

class Model(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True, validate_default=True)

class Member(Model):
    user_id: str
    roles: list[Role] = Field(min_length=1)

class Target(Model):
    scope: str = Field(min_length=1, max_length=200)
    amount: Decimal = Field(ge=0)
    value_type: ValueType = 'Cost reduction'
    metric: str = 'In-year net recurring benefit'
    start: date
    end: date
    additional: bool = False

class ProgramInput(Model):
    name: str = Field(min_length=1, max_length=160)
    client: str = Field(min_length=1, max_length=160)
    objective: str = Field(min_length=1)
    sponsor: str = Field(min_length=1)
    scope: str = Field(min_length=1)
    start: date
    end: date
    currency: str = Field(default='USD', pattern='^[A-Z]{3}$')
    fx_basis: str = 'Native currency; fixed program reporting rates'
    recognition_rules: str = Field(min_length=1)
    cadence_days: int = Field(default=14, ge=1, le=365)
    stale_days: int = Field(default=30, ge=1, le=365)
    approval_threshold: Decimal = Field(default=0, ge=0)
    members: list[Member] = Field(min_length=1)
    mandatory_evidence: list[str] = Field(default_factory=lambda: ['Function','Quality','Safety'])
    targets: list[Target] = Field(default_factory=list)
    record_version: int = 0
    reason: str = ''

    @model_validator(mode='after')
    def valid(self):
        if self.end < self.start: raise ValueError('Reporting end precedes start')
        if len({m.user_id for m in self.members}) != len(self.members): raise ValueError('One membership per account')
        if any('External' in m.roles and m.roles!=['External'] for m in self.members): raise ValueError('External participation cannot be combined with internal decision rights')
        targets=[(t.scope,t.value_type,t.metric,t.start,t.end) for t in self.targets]
        if len(set(targets))!=len(targets): raise ValueError('Targets must have unique scope, metric, type and period')
        for t in self.targets:
            if t.end < t.start or t.start < self.start or t.end > self.end: raise ValueError('Targets must fit the reporting period')
        return self

class Period(Model):
    month: date
    volume: Decimal = Field(ge=0)
    adoption: Decimal = Field(default=1, ge=0, le=1)
    spend: Decimal = Field(default=0, ge=0)
    @model_validator(mode='after')
    def valid(self):
        if self.month.day != 1: raise ValueError('Use first-of-month dates')
        return self

class Application(Model):
    id: str = Field(min_length=1, max_length=80)
    scope: str = Field(min_length=1)
    plant: str = Field(min_length=1)
    supplier: str = ''
    part: str = ''
    revision: str = ''
    owner_id: str | None = None
    value_type: ValueType = 'Cost reduction'
    mechanism: str = ''
    unit: str = 'part'
    usage: Decimal = Field(default=1, gt=0)
    conversion: Decimal = Field(default=1, gt=0)
    baseline: Decimal | None = None
    proposed: Decimal | None = None
    annual_volume: Decimal | None = Field(default=None, ge=0)
    recurring_per_unit: Decimal | None = Field(default=None, ge=0)
    giveback_per_unit: Decimal = Field(default=0, ge=0)
    currency: str = Field(default='USD', pattern='^[A-Z]{3}$')
    fx_rate: Decimal = Field(default=1, gt=0)
    baseline_date: date | None = None
    evidence: str = ''
    source_type: Literal['Quotation','Should-cost','Observed','Estimate'] = 'Estimate'
    assumptions: str = ''
    low: Decimal | None = None
    high: Decimal | None = None
    nonfinancial_metric: str = ''
    overlap_key: str = ''
    selected: bool = True
    effective_date: date | None = None
    implementation_evidence: str = ''
    rollout: Literal['Planned','Released','In production'] = 'Planned'
    periods: list[Period] = Field(default_factory=list, max_length=120)
    @model_validator(mode='after')
    def valid(self):
        if len({p.month for p in self.periods}) != len(self.periods): raise ValueError('Duplicate application months')
        if self.low is not None and self.high is not None and self.low > self.high: raise ValueError('Low estimate exceeds high')
        if self.currency == '' or (self.baseline is not None and self.baseline < 0) or (self.proposed is not None and self.proposed < 0): raise ValueError('Costs must be nonnegative')
        return self

class Risk(Model):
    id: str
    description: str = Field(min_length=1)
    severity: Literal['Low','Medium','High','Critical']
    likelihood: Literal['Low','Medium','High']
    mitigation: str = ''
    owner_id: str
    due_date: date
    disposition: Literal['Open','Accepted','Mitigated'] = 'Open'
    acceptance_evidence: str = ''

class Action(Model):
    id: str
    title: str = Field(min_length=1)
    owner_id: str
    due_date: date
    status: Literal['Open','In progress','Done'] = 'Open'
    dependency: str = ''
    cost: Decimal | None = Field(default=None, ge=0)
    evidence: str = ''
    required: bool = True

class CaseInput(Model):
    title: str = Field(min_length=1, max_length=240)
    description: str = Field(min_length=1)
    scope: str = Field(min_length=1)
    current_condition: str = ''
    future_condition: str = ''
    source: str = ''
    workshop: str = ''
    category: str = ''
    product_family: str = ''
    product: str = ''
    assembly: str = ''
    commodity: str = ''
    region: str = ''
    cost_category: str = ''
    function: str = ''
    customer_benefit: str = ''
    constraints: str = ''
    owner_id: str | None = None
    next_action: str = ''
    due_date: date | None = None
    escalation_contact: str = ''
    priority: Literal['Low','Medium','High'] = 'Medium'
    priority_reason: str = ''
    effort_days: Decimal | None = Field(default=None, ge=0)
    resource_constraints: str = ''
    blocker: str = ''
    schedule_health: Literal['On track','At risk','Late'] = 'On track'
    hold_owner_id: str | None = None
    hold_review_date: date | None = None
    lessons: str = ''
    final_disposition: str = ''
    parent_id: str | None = None
    duplicate_of: str | None = None
    reuse_of: str | None = None
    dependencies: list[str] = Field(default_factory=list)
    shared: bool = False
    feasibility: dict[str,str] = Field(default_factory=dict)
    applications: list[Application] = Field(default_factory=list, max_length=200)
    risks: list[Risk] = Field(default_factory=list)
    actions: list[Action] = Field(default_factory=list)
    record_version: int = 0
    reason: str = ''
    @model_validator(mode='after')
    def valid(self):
        for rows in (self.applications,self.risks,self.actions):
            if len({r.id for r in rows}) != len(rows): raise ValueError('Row IDs must be unique')
        return self

class Command(Model):
    record_version: int = Field(ge=1)
    reason: str = Field(min_length=1)
    action: str = ''
    target: int | None = Field(default=None, ge=1, le=6)
    role: Role | None = None

class ActualInput(Model):
    record_version: int = Field(ge=1)
    month: date
    application_id: str
    volume: Decimal = Field(ge=0)
    actual_cost: Decimal = Field(ge=0)
    recurring: Decimal = Field(ge=0)
    giveback: Decimal = Field(default=0, ge=0)
    spend: Decimal = Field(ge=0)
    evidence: str = Field(min_length=1)
    variance_reason: str = Field(min_length=1)
    external_effects: str = Field(min_length=1)
    reason: str = Field(min_length=1)

class EvidenceInput(Model):
    record_version: int = Field(ge=1)
    name: str = Field(min_length=1, max_length=240)
    content_base64: str = Field(max_length=7_000_000)
    shared: bool = False

class Discussion(Model):
    record_version: int = Field(ge=1)
    body: str = Field(min_length=1)
    mentions: list[str] = Field(default_factory=list)
    shared: bool = False

class FeasibilityInput(Model):
    record_version: int = Field(ge=1)
    evidence: dict[str,str]
    reason: str = Field(min_length=1)

class ActionCommand(Model):
    record_version: int = Field(ge=1)
    status: Literal['Open','In progress','Done']
    evidence: str = Field(min_length=1)
    reason: str = Field(min_length=1)

class AdoptInput(Model):
    record_version: int = Field(ge=1)
    case: CaseInput
    reason: str = Field(min_length=1)
    confirmed: bool = False
    preview_token: str = ''
