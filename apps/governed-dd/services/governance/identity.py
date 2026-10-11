"""Keycloak supported administrative REST API; random passwords never printed."""
import os
import secrets
import sys
from pathlib import Path
import httpx

username=sys.argv[2]
base='http://keycloak:8080/identity'
with httpx.Client(trust_env=False,timeout=30) as client:
 password=Path('/run/secrets/keycloak-admin').read_text().strip()
 response=client.post(base+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'governed-dd-admin','password':password})
 response.raise_for_status();headers={'Authorization':'Bearer '+response.json()['access_token']}
 endpoint=base+'/admin/realms/governed-dd/users'
 users=client.get(endpoint,headers=headers,params={'username':username,'exact':'true'}).json()
 if users:
  if not users[0].get('email'):
   client.put(endpoint+'/'+users[0]['id'],headers=headers,json={'email':username+'@example.invalid','emailVerified':True}).raise_for_status()
  print('Existing identity preserved. OIDC subject: '+users[0]['id']);sys.exit(0)
 generated=secrets.token_urlsafe(32)
 result=client.post(endpoint,headers=headers,json={'username':username,'email':username+'@example.invalid','enabled':True,'emailVerified':True,'firstName':username,'lastName':'Consultant','credentials':[{'type':'password','value':generated,'temporary':False}]})
 result.raise_for_status()
 ident=result.headers['location'].split('/')[-1]
 Path('/private/'+username+'.password').write_text(generated)
 print('Identity created; password saved in app private identity volume. OIDC subject: '+ident)
