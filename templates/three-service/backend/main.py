import hashlib, os, secrets, uuid
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from argon2 import PasswordHasher

app=FastAPI(title='{{APP_TITLE}}',docs_url=None,redoc_url=None,openapi_url=None)
hasher=PasswordHasher()
def digest(value):return hashlib.sha256(value.encode()).hexdigest()
def cookie():return os.getenv('SESSION_COOKIE_NAME',os.getenv('APP_SLUG','app')+'_session')
def secure():return os.getenv('APP_ORIGIN','').startswith('https://')
def database():
    with psycopg.connect(os.environ['DATABASE_URL'],row_factory=dict_row) as db:yield db

@app.middleware('http')
async def origin_guard(request,call_next):
    if request.method not in ('GET','HEAD','OPTIONS') and request.headers.get('origin') not in (None,os.environ.get('APP_ORIGIN')):
        from starlette.responses import JSONResponse
        return JSONResponse({'detail':'Same-origin requests required'},403)
    response=await call_next(request);response.headers['Cache-Control']='no-store';return response

def current(request:Request,db=Depends(database)):
    session=db.execute('SELECT s.*,u.email,u.role FROM app_session s JOIN app_user u ON u.id=s.user_id WHERE token_hash=%s AND expires_at>now()',(digest(request.cookies.get(cookie(),'')),)).fetchone()
    if not session:raise HTTPException(401,'Sign in to continue')
    if request.method not in ('GET','HEAD','OPTIONS') and not secrets.compare_digest(request.headers.get('X-CSRF-Token',''),session['csrf']):raise HTTPException(403,'Refresh and try again')
    return session

@app.get('/api/health/ready')
def ready(db=Depends(database)):
    if not db.execute('SELECT 1 FROM schema_version WHERE version=1').fetchone():raise HTTPException(503,'Schema not ready')
    return {'status':'ready'}

class Login(BaseModel):
    email:str=Field(max_length=254)
    password:str=Field(max_length=1024)

@app.post('/api/session/login')
def login(data:Login,response:Response,db=Depends(database)):
    user=db.execute('SELECT * FROM app_user WHERE email=%s',(data.email.lower(),)).fetchone()
    try:valid=bool(user) and hasher.verify(user['password_hash'],data.password)
    except Exception:valid=False
    if not valid:raise HTTPException(401,'Email or password is incorrect')
    token=secrets.token_urlsafe(32);csrf=secrets.token_urlsafe(32)
    db.execute('INSERT INTO app_session VALUES(%s,%s,%s,%s)',(digest(token),user['id'],csrf,datetime.now(timezone.utc)+timedelta(hours=12)))
    response.set_cookie(cookie(),token,httponly=True,secure=secure(),samesite='strict',max_age=43200,path='/')
    return {'email':user['email'],'role':user['role'],'csrf':csrf,'title':os.getenv('APP_TITLE','{{APP_TITLE}}')}

@app.get('/api/session/me')
def me(user=Depends(current)):return {'email':user['email'],'role':user['role'],'csrf':user['csrf'],'title':os.getenv('APP_TITLE','{{APP_TITLE}}')}

@app.post('/api/session/logout')
def logout(response:Response,user=Depends(current),db=Depends(database)):
    db.execute('DELETE FROM app_session WHERE token_hash=%s',(user['token_hash'],))
    response.delete_cookie(cookie(),secure=secure(),httponly=True,samesite='strict',path='/')
    return {'ok':True}

class NoteInput(BaseModel):
    body:str=Field(min_length=1,max_length=2000)
class NoteEdit(NoteInput):
    record_version:int=Field(ge=1)

@app.get('/api/notes')
def notes(user=Depends(current),db=Depends(database)):
    return db.execute('SELECT id,body,record_version,created_at FROM note ORDER BY created_at,id').fetchall()

@app.post('/api/notes',status_code=201)
def create_note(data:NoteInput,user=Depends(current),db=Depends(database)):
    id=uuid.uuid4()
    row=db.execute('INSERT INTO note(id,body,actor_id) VALUES(%s,%s,%s) RETURNING id,body,record_version,created_at',(id,data.body,user['user_id'])).fetchone()
    db.execute('INSERT INTO note_event(id,note_id,actor_id,activity,changes) VALUES(%s,%s,%s,%s,%s)',(uuid.uuid4(),id,user['user_id'],'CREATED',Jsonb({'body':{'old':None,'new':data.body}})))
    return row

@app.put('/api/notes/{id}')
def edit_note(id:uuid.UUID,data:NoteEdit,user=Depends(current),db=Depends(database)):
    previous=db.execute('SELECT * FROM note WHERE id=%s FOR UPDATE',(id,)).fetchone()
    if not previous:raise HTTPException(404,'Note not found')
    if previous['record_version']!=data.record_version:raise HTTPException(409,'Note changed. Refresh before saving.')
    row=db.execute('UPDATE note SET body=%s,record_version=record_version+1 WHERE id=%s RETURNING id,body,record_version,created_at',(data.body,id)).fetchone()
    db.execute('INSERT INTO note_event(id,note_id,actor_id,activity,changes) VALUES(%s,%s,%s,%s,%s)',(uuid.uuid4(),id,user['user_id'],'EDITED',Jsonb({'body':{'old':previous['body'],'new':data.body}})))
    return row
