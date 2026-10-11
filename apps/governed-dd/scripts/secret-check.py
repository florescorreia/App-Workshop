"""Check actual injected secret values without printing matches or values."""
import os,re,sys,json
from pathlib import Path
root=Path('/workspace');values=[]
for path in (root/'local/secrets').glob('*'):
 if path.is_file() and not path.name.endswith('.pub'):
  try:
   text=path.read_text().strip()
   if path.name.endswith('-providers'):
    values.extend(v for v in json.loads(text).values() if isinstance(v,str) and len(v)>=20)
   elif len(text)>=20 and len(text)<500:values.append(text)
  except UnicodeError:pass
for name in ('LITELLM_API_KEY','DD_SEARCH_API_KEY','DD_EMBEDDING_API_KEY'):
 if os.getenv(name):values.append(os.environ[name])
failures=[];count=0
for directory,folders,files in os.walk(root):
 folders[:]=[f for f in folders if f not in ('local','backups','node_modules','.git')]
 for filename in files:
  path=Path(directory)/filename
  try:content=path.read_text()
  except (UnicodeError,OSError):continue
  count+=1
  if any(value in content for value in values):failures.append(str(path.relative_to(root)))
print('Source secret scan: '+str(count)+' text files; '+str(len(failures))+' files with configured secret values.')
if failures:print('\n'.join(failures));sys.exit(1)
