import hashlib, secrets
from datetime import timedelta
from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from argon2 import PasswordHasher
from .db import get_db, now
from .models import User, Session

hasher = PasswordHasher()
def digest(token): return hashlib.sha256(token.encode()).hexdigest()

def current_user(request: Request, db=Depends(get_db)):
    token = request.cookies.get('ideaflow_session','')
    session = db.get(Session, digest(token))
    if not session or session.expires_at <= now(): raise HTTPException(401,'Sign in to continue')
    user = db.get(User,session.user_id)
    if not user or not user.active: raise HTTPException(401,'Account is inactive')
    if request.method not in ('GET','HEAD','OPTIONS'):
        if not secrets.compare_digest(request.headers.get('X-CSRF-Token',''),session.csrf):
            raise HTTPException(403,'Session check failed. Refresh and try again.')
    request.state.session = session
    return user

def require(user,*roles):
    if user.role not in roles: raise HTTPException(403,'This action requires ' + ' or '.join(roles))

def public_user(user):
    return {k:getattr(user,k) for k in ('id','name','email','role','active','record_version')}
