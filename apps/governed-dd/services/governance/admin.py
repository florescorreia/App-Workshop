import argparse
import re
from main import control_db

p=argparse.ArgumentParser();p.add_argument('action',choices=['tenant','active','member-add','member-remove']);p.add_argument('--tenant',required=True);p.add_argument('--name');p.add_argument('--value');p.add_argument('--subject');p.add_argument('--role');a=p.parse_args()
if not re.fullmatch('[a-f0-9]{24}',a.tenant):raise ValueError('Invalid opaque tenant ID')
with control_db() as db:
 if a.action=='tenant':db.execute('INSERT INTO tenants(id,name) VALUES(%s,%s) ON CONFLICT(id) DO NOTHING',(a.tenant,a.name))
 elif a.action=='active':db.execute('UPDATE tenants SET active=%s WHERE id=%s',(a.value=='true',a.tenant))
 elif a.action=='member-add':db.execute('INSERT INTO memberships(subject,tenant,role) VALUES(%s,%s,%s) ON CONFLICT(subject,tenant) DO UPDATE SET role=excluded.role',(a.subject,a.tenant,a.role))
 elif a.action=='member-remove':db.execute('DELETE FROM memberships WHERE subject=%s AND tenant=%s',(a.subject,a.tenant))
 db.execute('INSERT INTO control_audit(subject,operation,tenant) VALUES(%s,%s,%s)',('administrator-cli',a.action,a.tenant))
print('Administrative operation completed.')
