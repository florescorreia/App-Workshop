"""User-defined labels; all changes join the surrounding business transaction."""
import unicodedata
from sqlalchemy import select, text
from .models import Site, Category, Idea, uid
from .domain import fail, event

def key(label):
    return ' '.join(unicodedata.normalize('NFKC', label).casefold().split())

def lock(db):
    # Serializes creation, rename and merge, including concurrent first use.
    db.execute(text('SELECT pg_advisory_xact_lock(18470261)'))

def model(kind):
    cls = {'sites': Site, 'categories': Category}.get(kind)
    if not cls: fail('Unknown classification type')
    return cls

def resolve(db, kind, reference_id=None, label=None, business_unit='', legacy=False):
    cls = model(kind)
    lock(db)
    if label is not None:
        label = ' '.join(unicodedata.normalize('NFKC', label).split())
        if not label: return None
        if len(label)>120 or len(key(label))>120: fail('Use at most 120 characters')
        obj = db.scalar(select(cls).where(cls.label_key==key(label)))
        if not obj:
            fields = {'id': reference_id if legacy and reference_id else uid(), 'label': label, 'label_key': key(label)}
            if kind=='sites': fields['business_unit']=business_unit
            obj=cls(**fields);db.add(obj);db.flush()
    elif reference_id:
        obj=db.get(cls,reference_id)
        if not obj:
            if legacy: return resolve(db,kind,reference_id,reference_id,business_unit,True)
            fail('Choose an existing value or type a new name')
    else: return None
    visited=set()
    while obj.merged_into:
        if obj.id in visited: fail('Invalid classification merge')
        visited.add(obj.id);obj=db.get(cls,obj.merged_into)
    return obj.id

def modify(db,user,kind,reference_id,data,merge=False):
    cls=model(kind);field='site_id' if kind=='sites' else 'category_id'
    lock(db)
    source=db.get(cls,reference_id)
    if not source or not source.active: fail('Classification no longer available; refresh',409)
    if source.record_version!=data.record_version: fail('Classification changed; refresh before saving',409)
    old_label=source.label
    target=None
    if merge:
        target=db.get(cls,data.target_id)
        if not target or not target.active or target.id==source.id: fail('Choose a different active value')
        if target.record_version!=data.target_version: fail('Target changed; refresh',409)
    else:
        label=' '.join(unicodedata.normalize('NFKC',data.label).split())
        if not label or len(key(label))>120: fail('Enter a name of at most 120 characters')
        collision=db.scalar(select(cls).where(cls.label_key==key(label),cls.id!=source.id))
        if collision: fail('That name already exists. Merge these values instead.',409)
    affected=list(db.scalars(select(Idea).where(getattr(Idea,field)==source.id).order_by(Idea.id).with_for_update()))
    old_unit=source.business_unit if kind=='sites' else None
    if merge:
        source.active=False;source.merged_into=target.id;target.record_version+=1
    else:
        source.label=label;source.label_key=key(label)
        if kind=='sites':source.business_unit=data.business_unit
    source.record_version+=1
    for idea in affected:
        changes={kind:{'old':old_label,'new':target.label if merge else source.label}}
        if merge:
            setattr(idea,field,target.id);changes[field]={'old':source.id,'new':target.id}
        if kind=='sites':changes['business_unit']={'old':old_unit,'new':target.business_unit if merge else source.business_unit}
        event(db,idea,user,'CLASSIFICATION_MERGED' if merge else 'CLASSIFICATION_RENAMED',reason=data.reason,changes=changes)
    db.flush()
    return {'affected_ideas':len(affected),'id':target.id if merge else source.id}
