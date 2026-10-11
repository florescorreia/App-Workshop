"""Live control-plane authorization requests; test sessions are explicit and short-lived."""
import hashlib
import secrets
import httpx
from main import control_db

A='a4e176281f3c47d081b3b623';B='b5e287392a4d58e192c4c734'
ALICE='c1491155-4cff-450b-afea-2d4d2fa5c61c';BOB='3cc5b72a-2402-4d1d-9161-30da6562abf5';CAROL='9477ea59-63a6-4f3c-90a0-ee8746e5ebbb'
for subject,allowed in [(ALICE,[A]),(BOB,[B]),(CAROL,[A,B])]:
 token=secrets.token_urlsafe(32);ident=hashlib.sha256(token.encode()).hexdigest()
 with control_db() as db:db.execute("INSERT INTO sessions(id,subject,csrf,expires_at,id_token) VALUES(%s,%s,'test',now()+interval '2 minutes','test-only')",(ident,subject))
 try:
  with httpx.Client(base_url='http://gateway:8080',cookies={'governed_dd_session':token},timeout=15) as c:
   assert sorted(t['id'] for t in c.get('/api/me').json()['engagements'])==allowed
   for tenant in [A,B]:
    for path in ['','api/records','api/search?q=revenue&dense=false','api/status','paperclip/api/companies','lab/','mcp/','api/bytes/00000000-0000-0000-0000-000000000000/1']:
     result=c.get('/t/'+tenant+'/'+path)
     if tenant not in allowed:assert result.status_code==404,(subject,path,result.status_code)
   if subject==ALICE:
    assert c.post('/t/'+A+'/api/records',json={}).status_code==403
    with control_db() as db:db.execute('DELETE FROM memberships WHERE subject=%s AND tenant=%s',(ALICE,A))
    assert c.get('/t/'+A+'/api/status').status_code==404
    assert c.get('/api/me').json()['engagements']==[]
    with control_db() as db:db.execute("INSERT INTO memberships(subject,tenant,role) VALUES(%s,%s,'owner')",(ALICE,A))
 finally:
  with control_db() as db:
   db.execute('DELETE FROM sessions WHERE id=%s',(ident,))
   db.execute("INSERT INTO memberships(subject,tenant,role) VALUES(%s,%s,'owner') ON CONFLICT DO NOTHING",(ALICE,A))
print('Alice/Bob/Carol directory filtering, guessed routes, CSRF rejection and next-request membership revocation passed.')
