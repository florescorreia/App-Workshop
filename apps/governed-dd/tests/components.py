"""Real native Paperclip auth behind tenant membership gateway, no credential output."""
import hashlib,json,secrets
from pathlib import Path
import httpx
from main import control_db
A='a4e176281f3c47d081b3b623';B='b5e287392a4d58e192c4c734';subject='c1491155-4cff-450b-afea-2d4d2fa5c61c'
token=secrets.token_urlsafe(32);ident=hashlib.sha256(token.encode()).hexdigest()
with control_db() as db:db.execute("INSERT INTO sessions(id,subject,csrf,expires_at,id_token) VALUES(%s,%s,'test',now()+interval '2 minutes','test-only')",(ident,subject))
try:
 with httpx.Client(base_url='http://gateway:8080',cookies={'governed_dd_session':token},timeout=30) as portal:
  link=portal.get('/t/'+A+'/open/paperclip').headers['location']
  assert portal.get('/t/'+B+'/open/paperclip').status_code==404
  origin='http://paperclip-'+A+'.localhost:8081'
  headers={'Host':origin.removeprefix('http://'),'Origin':origin}
  with httpx.Client(base_url='http://gateway:8080',headers=headers,timeout=30) as native:
   assert native.get('/api/companies').status_code==404
   from urllib.parse import urlsplit
   entered=native.get(urlsplit(link).path+'?'+urlsplit(link).query)
   assert entered.status_code==307
   # HTTP gateway alias needs explicit test cookie; browser stores it against the tenant origin.
   cookie=entered.cookies.get('governed_dd_component');native.cookies.set('governed_dd_component',cookie)
   assert native.get('/').status_code==200
   unauth=native.get('/api/companies');assert unauth.status_code in (401,403),(unauth.status_code,unauth.text[:250])
   credential=json.loads(Path('/native/native-admin.json').read_text())
   login=native.post('/api/auth/sign-in/email',json={'email':credential['email'],'password':credential['password']})
   assert login.status_code==200,login.status_code
   for key,value in login.cookies.items():native.cookies.set(key,value)
   assert native.get('/api/companies').status_code==200
   company=native.get('/api/companies').json()[0]
   import websockets.sync.client
   cookie_header='; '.join(k+'='+v for k,v in {c.name:c.value for c in native.cookies.jar}.items())
   # Connect gateway TCP using tenant Host header and the actual native session.
   import socket
   ws=websockets.sync.client.connect('ws://paperclip-'+A+'.localhost:8081/api/companies/'+company['id']+'/events/ws',sock=socket.create_connection(('gateway',8080)),origin=origin,additional_headers={'Cookie':cookie_header},open_timeout=15)
   assert native.post('/api/auth/sign-up/email',json={'name':'test','email':'disabled@example.invalid','password':secrets.token_urlsafe(40)}).status_code>=400
   with control_db() as db:db.execute('DELETE FROM memberships WHERE subject=%s AND tenant=%s',(subject,A))
   try:ws.recv(timeout=5)
   except websockets.exceptions.ConnectionClosed:pass
   else:raise AssertionError('Revoked stream remained active')
   ws.close()
   for path in ['/','/api/companies','/api/auth/get-session','/assets/test','/api/attachments/test']:
    assert native.get(path).status_code==404
   print('Real native Paperclip login, disabled sign-up, whole-path gateway, next-request and active-stream revocation passed.')
finally:
 with control_db() as db:
  db.execute('DELETE FROM sessions WHERE id=%s',(ident,))
  db.execute("INSERT INTO memberships(subject,tenant,role) VALUES(%s,%s,'owner') ON CONFLICT DO NOTHING",(subject,A))
