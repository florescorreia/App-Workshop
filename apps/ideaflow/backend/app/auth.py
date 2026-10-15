import hashlib, secrets, os
from datetime import timedelta
from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from argon2 import PasswordHasher
from .db import get_db, now
from .models import User, Session

hasher = PasswordHasher()
def digest(token): return hashlib.sha256(token.encode()).hexdigest()

def cookie_name(): return os.getenv('SESSION_COOKIE_NAME','ideaflow_session')

def secure_cookie(request):
    return os.getenv('SESSION_COOKIE_SECURE','').lower()=='true' or request.url.scheme=='https'

def current_user(request: Request, db=Depends(get_db)):
    token = request.cookies.get(cookie_name(),'')
    session = db.get(Session, digest(token))
    if not session or session.expires_at <= now(): raise HTTPException(401,'Sign in to continue')
    user = db.get(User,session.user_id)
    if not user or not user.active or user.deleted_at: raise HTTPException(401,'Account is inactive')
    if request.method not in ('GET','HEAD','OPTIONS'):
        if not secrets.compare_digest(request.headers.get('X-CSRF-Token',''),session.csrf):
            raise HTTPException(403,'Session check failed. Refresh and try again.')
    request.state.session = session
    from .vave import external_only
    if external_only(db,user) and not (request.url.path.startswith('/api/v1/vave/') or request.url.path.startswith('/api/v1/session/') or request.url.path=='/api/v1/references'):
        raise HTTPException(403,'External access is limited to explicitly shared program records')
    return user

def require(user,*roles):
    if user.role not in roles: raise HTTPException(403,'This action requires ' + ' or '.join(roles))

def public_user(user):
    return {k:getattr(user,k) for k in ('id','name','email','role','active','record_version','deleted_at')}
