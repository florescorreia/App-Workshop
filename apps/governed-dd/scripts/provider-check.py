"""Read-only live provider probes. Output contains statuses, never keys/responses."""
import os
import httpx
base=os.environ['LLM_BASE_URL'].rstrip('/')
key=os.environ[os.environ.get('LLM_API_KEY_ENV','LITELLM_API_KEY')]
with httpx.Client(timeout=30,trust_env=False) as client:
 response=client.post(base+'/responses',headers={'Authorization':'Bearer '+key},json={'model':'gpt-6.1-sol','reasoning':{'effort':'medium'},'input':'Respond with the single word hello.','max_output_tokens':32})
 print('LiteLLM Responses smoke HTTP',response.status_code)
 if response.status_code==200:
  print('Requested model returned',response.json().get('model'),'usage present',bool(response.json().get('usage')))
 else:
  print('Provider rejected request; response suppressed to protect credentials/upstream diagnostics.')
 if response.status_code!=200:raise SystemExit(1)
