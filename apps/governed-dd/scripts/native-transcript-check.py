"""Scan native transcripts for concrete injected secrets, reporting counts only."""
import json,os
from pathlib import Path
root=Path('/paperclip');values=[]
for path in Path('/secrets').glob('*'):
 if not path.is_file() or path.name.endswith('.pub'):continue
 try:
  v=path.read_text().strip()
  if 20<=len(v)<500:values.append(v)
 except UnicodeError:pass
for path in root.glob('native-*.json'):
 try:
  data=json.loads(path.read_text());values.append(data['password'])
 except (KeyError,ValueError):pass
files=0;matches=0;tokenfiles=0
for path in root.glob('instances/*/data/run-logs/**/*.ndjson'):
 content=path.read_text();files+=1
 if any(v in content for v in values):matches+=1
 # Managed short-lived upstream MCP tokens are a separate credential class.
 import re
 if re.search(r'eyJ[a-zA-Z0-9_-]{12,}\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+',content):tokenfiles+=1
print({'transcripts':files,'configured_secret_matches':matches,'jwt_containing_files':tokenfiles})
if matches:raise SystemExit(1)
