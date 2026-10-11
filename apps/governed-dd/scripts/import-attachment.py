"""Run in tenant governance after explicit administrator native API capture."""
import hashlib,json,sys
from pathlib import Path
from domain import Domain,Invalid
p=Path(sys.argv[1]);m=json.loads((p/'metadata.json').read_text());data=(p/'bytes').read_bytes();d=Domain()
if m['paperclip_instance']!='governed-dd-'+d.tenant or hashlib.sha256(data).hexdigest()!=m['hash'] or len(data)!=m['size']:
    raise Invalid('Native capture binding/checksum failed')
source=d.upload(data,m.pop('filename'),m.pop('media_type'),m,'administrator:attachment-import','native-attachment:'+m['attachment_id'])
job=d.ingest({'id':str(source['id']),'version':source['version']})
print(json.dumps({'source_id':str(source['id']),'version':source['version'],'task_id':m['task_id'],'attachment_id':m['attachment_id'],'job_status':job['status']}))
