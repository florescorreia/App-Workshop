"""Explicit, reversible Admin cleanup; no rows or lifecycle evidence are deleted."""
from sqlalchemy import select,func
from .models import User,Task,IdeaEvent,FinancialPlan,ValuePeriod,Comment
from .auth import require
from .domain import fail,event
from .db import now

def active(db,user_id):
    user=db.get(User,user_id)
    return bool(user and user.active and not user.deleted_at)

def preview(db,user,idea):
    require(user,'Admin')
    tasks=list(db.scalars(select(Task).where(Task.idea_id==idea.id)))
    plans=list(db.scalars(select(FinancialPlan).where(FinancialPlan.idea_id==idea.id)))
    results=list(db.scalars(select(ValuePeriod).where(ValuePeriod.idea_id==idea.id)))
    inactive=[{'id':t.id,'title':t.title,'assignee_id':t.assignee_id} for t in tasks if t.status!='Done' and not active(db,t.assignee_id)]
    return {'id':idea.id,'reference':idea.reference,'title':idea.title,'record_version':idea.record_version,
        'removed_at':idea.removed_at,'stage':idea.stage,'disposition':idea.disposition,
        'owner_name':db.get(User,idea.owner_id).name,'owner_active':active(db,idea.owner_id),'inactive_tasks':inactive,
        'counts':{'tasks':len(tasks),'open_tasks':sum(t.status!='Done' for t in tasks),'plans':len(plans),
            'approved_plans':sum(p.status=='Approved' for p in plans),'results':len(results),
            'verified_results':sum(r.verified_at is not None for r in results),
            'comments':db.scalar(select(func.count()).select_from(Comment).where(Comment.idea_id==idea.id)),
            'events':db.scalar(select(func.count()).select_from(IdeaEvent).where(IdeaEvent.idea_id==idea.id))}}

def remove(db,user,idea,data):
    require(user,'Admin')
    if idea.removed_at:fail('This idea is already removed',409)
    timestamp=now();idea.removed_at=timestamp;idea.removed_by=user.id;idea.removal_reason=data.reason
    event(db,idea,user,'IDEA_REMOVED',reason=data.reason,changes={'removed_at':{'old':None,'new':timestamp.isoformat()},'removed_by':{'old':None,'new':user.id}},occurred_at=timestamp)
    return idea

def restore(db,user,idea,data):
    require(user,'Admin')
    if not idea.removed_at:fail('This idea is not removed',409)
    owner=data.owner_id or idea.owner_id
    if not active(db,owner):fail('Choose an active owner before restoring this idea')
    inactive=[t for t in db.scalars(select(Task).where(Task.idea_id==idea.id,Task.status!='Done')) if not active(db,t.assignee_id)]
    if inactive and not data.reassign_inactive_tasks:fail('Confirm reassignment of open tasks with inactive assignees before restoring')
    old_removed=idea.removed_at;idea.removed_at=None;idea.removed_by=None;idea.removal_reason=None
    if owner!=idea.owner_id:
        old=idea.owner_id;idea.owner_id=owner
        event(db,idea,user,'ASSIGNED',reason=data.reason,changes={'owner_id':{'old':old,'new':owner}})
    for task in inactive:
        old=task.assignee_id;task.assignee_id=owner
        event(db,idea,user,'TASK_CHANGED',reason=data.reason,changes={'task_id':task.id,'assignee_id':{'old':old,'new':owner}})
    event(db,idea,user,'IDEA_RESTORED',reason=data.reason,changes={'removed_at':{'old':old_removed.isoformat(),'new':None}})
    return idea
