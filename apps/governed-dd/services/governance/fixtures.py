"""Explicit additive fictional evidence. Never a normal startup hook."""
from domain import Domain,Invalid

d=Domain()
source=d.upload(b'FICTIONAL ACCEPTANCE FIXTURE\nNorthstar Components revenue: 2024 USD 100 million; 2025 USD 120 million.\nThis synthetic source is not real research.\n','fictional-assignment.txt','text/plain',{'publisher':'Fictional test author','access_limitations':'Synthetic acceptance fixture','batch':'fictional-v1'},'administrator:demo','fictional-v1-source')
ref={'id':str(source['id']),'version':source['version']}
job=d.ingest(ref)
if job['status'] in ('pending','failed'):d.process_job(job)
definition=d.write('Definition',{'name':'Revenue growth','meaning':'Change in comparable reported revenue','formula':'(current / prior - 1) * 100','units':'percent','scope':'2024–2025; synthetic acceptance data','owner':'human engagement owner'},'administrator:demo','fictional-v1-definition')
run=d.write('AnalysisRun',{'task_id':'explicit-fixture-command','paperclip_instance':'not a Paperclip run','paperclip_run_id':'not applicable','inputs':[ref],'code_commit':'fixture-code-v1','environment':{'type':'deterministic synthetic acceptance command'},'parameters':{'prior':100,'current':120},'seeds':[],'outputs':[],'execution_status':'succeeded','calculation':(120/100-1)*100},'administrator:demo','fictional-v1-run')
runref={'id':str(run['id']),'version':run['version']}
finding=d.write('Finding',{'claim':'Fictional revenue increased 20%','implications':'Synthetic calculation acceptance only','evidence':[dict(ref,locator='section:1')],'assumptions':['Comparable reporting scope'],'uncertainty':'Fictional fixture; no real company conclusion','run':runref,'metrics':[{'value':20,'definition':{'id':str(definition['id']),'version':definition['version']}}]},'administrator:demo','fictional-v1-finding')
data=b'# Fictional acceptance result\nRevenue growth = (120 / 100 - 1) * 100 = 20%.\n';digest=d.storage.put(data)
artifact=d.write('Artifact',{'hash':digest,'size':len(data),'media_type':'text/markdown','run':runref},'administrator:demo','fictional-v1-artifact')
deliverable=d.write('Deliverable',{'title':'Fictional revenue growth review','findings':[{'id':str(finding['id']),'version':1}],'artifacts':[{'id':str(artifact['id']),'version':1}],'run':runref},'administrator:demo','fictional-v1-deliverable')
d.project()
print({'batch':'fictional-v1','validation':d.validation({'id':str(deliverable['id']),'version':1}),'real_agent_run':False})
