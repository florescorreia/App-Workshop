"""Admin account actions preserve all business attribution; never log passwords."""
import os,secrets
from sqlalchemy import select,delete,func
from .models import User,Session,Idea,IdeaEvent,FinancialPlan,ValuePeriod,Task,Comment,DemoBatch,AccountEvent
from .auth import require,hasher
from .domain import fail
from .db import now
from .classifications import lock

def account(db,user,id,version=None):
    require(user,'Admin');lock(db)
    target=db.scalar(select(User).where(User.id==id).with_for_update())
    if not target:fail('Account not found',404)
    if target.deleted_at:fail('This account has been deleted; its history is retained',409)
    if version is not None and target.record_version!=version:fail('Account changed; refresh before continuing',409)
    return target

def audit(db,actor,target,action,reason=''):
    db.add(AccountEvent(actor_id=actor.id,subject_id=target.id,subject_name=target.name,action=action,reason=reason))

def revoke_sessions(db,id):
    db.execute(delete(Session).where(Session.user_id==id))

def deletion_preview(db,user,target):
    from .vave_models import Case, Program, ProgramEvent, Notice, Preference
    owned=list(db.scalars(select(Idea).where(Idea.owner_id==target.id,Idea.removed_at.is_(None),Idea.disposition.in_(['Active','On hold']),Idea.stage!='Realized')))
    tasks=list(db.scalars(select(Task).join(Idea,Task.idea_id==Idea.id).where(Task.assignee_id==target.id,Task.status!='Done',Idea.removed_at.is_(None),Idea.disposition.in_(['Active','On hold']),Idea.stage!='Realized')))
    protected=target.id==user.id or target.email==os.environ['ADMIN_EMAIL'].lower()
    # Any durable FK attribution makes deletion a retirement instead of row removal.
    references=[(Idea,Idea.submitter_id),(Idea,Idea.owner_id),(Idea,Idea.removed_by),(IdeaEvent,IdeaEvent.actor_id),(FinancialPlan,FinancialPlan.approved_by),(ValuePeriod,ValuePeriod.verified_by),(Task,Task.assignee_id),(Comment,Comment.actor_id),(DemoBatch,DemoBatch.importer),(AccountEvent,AccountEvent.actor_id)]
    references.append((ProgramEvent,ProgramEvent.actor_id))
    used=any(db.scalar(select(func.count()).select_from(model).where(column==target.id)) for model,column in references)
    for c in db.scalars(select(Case)):
        if c.status in ('Active','Draft','On hold'):
            if c.data.get('owner_id')==target.id and not any(i.id==c.idea_id for i in owned): owned.append(db.get(Idea,c.idea_id))
            tasks.extend(type('OpenVaveAction',(),{'id':a['id'],'idea_id':c.idea_id,'title':a['title']})() for a in c.data['actions'] if a['owner_id']==target.id and a['status']!='Done')
        if target.id in str(c.data) or target.id in str(c.actuals): used=True
    if any(target.id in str(p.data['members']) for p in db.scalars(select(Program))): used=True
    return {'mode':'retire' if used else 'remove','allowed':not protected and not owned and not tasks,
        'protected':protected,'record_version':target.record_version,
        'open_ideas':[{'id':i.id,'reference':i.reference,'title':i.title} for i in owned],
        'open_tasks':[{'id':t.id,'idea_id':t.idea_id,'title':t.title} for t in tasks]}

def remove(db,user,target,data):
    preview=deletion_preview(db,user,target)
    if preview['protected']:fail('Keep your signed-in account and the bootstrap Admin',422)
    if not preview['allowed']:fail('Reassign this account’s open ideas and tasks before deleting it',422)
    revoke_sessions(db,target.id)
    audit(db,user,target,'ACCOUNT_RETIRED' if preview['mode']=='retire' else 'ACCOUNT_DELETED',data.reason)
    if preview['mode']=='retire':
        target.active=False;target.deleted_at=now();target.password_hash='!deleted';target.record_version+=1
    else:db.delete(target)
    db.flush()
    return {'deleted':True,'mode':preview['mode'],'history_preserved':True}

def regenerate(db,user,target,data):
    if target.id==user.id:fail('Use Set password for your own account; regeneration signs the target out')
    password=secrets.token_urlsafe(24)
    target.password_hash=hasher.hash(password);target.record_version+=1
    revoke_sessions(db,target.id);audit(db,user,target,'PASSWORD_REGENERATED',data.reason);db.flush()
    return {'password':password,'record_version':target.record_version,'sessions_revoked':True}
