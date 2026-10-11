"""Owner-only whole-origin Lab routing; no native graph RBAC assumed."""
import hashlib,secrets
import httpx
from main import control_db
A='a4e176281f3c47d081b3b623';B='b5e287392a4d58e192c4c734'
users=[('c1491155-4cff-450b-afea-2d4d2fa5c61c',True),('9477ea59-63a6-4f3c-90a0-ee8746e5ebbb',False)]
for subject,owner in users:
 token=secrets.token_urlsafe(32);ident=hashlib.sha256(token.encode()).hexdigest()
 with control_db() as db:db.execute("INSERT INTO sessions(id,subject,csrf,expires_at,id_token) VALUES(%s,%s,'test',now()+interval '2 minutes','test-only')",(ident,subject))
 try:
  with httpx.Client(base_url='http://gateway:8080',cookies={'governed_dd_session':token},timeout=30) as portal:
   entered=portal.get('/t/'+A+'/open/lab');assert entered.status_code==(307 if owner else 404)
   origin='http://lab-'+A+'.localhost:8081'
   with httpx.Client(base_url='http://gateway:8080',headers={'Host':origin.removeprefix('http://'),'Origin':origin},timeout=30) as lab:
    assert lab.get('/').status_code==404
    if owner:
     from urllib.parse import urlsplit
     u=urlsplit(entered.headers['location']);ticket=lab.get(u.path+'?'+u.query)
     lab.cookies.set('governed_dd_component',ticket.cookies.get('governed_dd_component'))
     assert lab.get('/').status_code==200
     assert lab.post('/api/unknown',headers={'Origin':'http://evil.invalid'}).status_code==403
     with control_db() as db:db.execute('DELETE FROM sessions WHERE id=%s',(ident,))
     assert lab.get('/').status_code==404
 finally:
  with control_db() as db:db.execute('DELETE FROM sessions WHERE id=%s',(ident,))
print('Lab owner-only entry, direct denial, whole-origin protection, CSRF and logout revocation passed.')
