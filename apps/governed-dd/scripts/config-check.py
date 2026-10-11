import os
import sys
from pathlib import Path
values={}
for line in Path('/workspace/.env').read_text().splitlines():
 if line and not line.startswith('#') and '=' in line:
  k,v=line.split('=',1);values[k]=v
errors=[]
for k,v in values.items():
 if 'ALLOCATED_' in v or 'GENERATE_' in v:errors.append(k+' contains unresolved placeholder')
if values.get('APP_BASE_URL')!='http://localhost:8081':errors.append('Current local renderer requires exact origin http://localhost:8081')
if values.get('AGENT_MODEL')!='gpt-6.1-sol':errors.append('Requested model must remain gpt-6.1-sol')
if values.get('ALLOW_GENERAL_INTERNET')!='false':errors.append('General egress override requires a reviewed execution configuration')
for field in ['EMBEDDING_BASE_URL','EMBEDDING_MODEL','EMBEDDING_DIMENSIONS','WEB_SEARCH_PROVIDER']:
 if not values.get(field):print('Real integration prerequisite: '+field)
if errors:print('\n'.join(errors));sys.exit(1)
print('Local configuration validation passed; incomplete provider prerequisites reported separately.')
