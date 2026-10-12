"""Private administrator export; stdout must be captured, never displayed."""
import json,re
from pathlib import Path

values={}
for path in Path('/identity').glob('*.password'):
    name=path.stem
    if not re.fullmatch('[a-z][a-z0-9-]{1,40}',name):
        continue
    prefix='DD_PORTAL_'+name.upper().replace('-','_')
    values[prefix+'_USERNAME']=name
    values[prefix+'_PASSWORD']=path.read_text().strip()
for tenant in Path('/native').iterdir():
    if not tenant.is_dir() or not re.fullmatch('[a-f0-9]{24}',tenant.name):
        continue
    for path in tenant.glob('native-*.json'):
        name=path.stem.removeprefix('native-')
        if not re.fullmatch('[a-z][a-z0-9-]{1,40}',name) or name.endswith('-pending'):
            continue
        credential=json.loads(path.read_text())
        if not credential.get('email') or not credential.get('password'):
            continue
        prefix='DD_PAPERCLIP_'+tenant.name.upper()+'_'+name.upper().replace('-','_')
        values[prefix+'_EMAIL']=credential['email']
        values[prefix+'_PASSWORD']=credential['password']
print(json.dumps(values))
