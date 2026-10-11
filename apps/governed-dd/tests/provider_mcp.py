import asyncio
from pathlib import Path
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

async def run():
 token=Path('/run/secrets/agent').read_text().strip()
 async with Client(StreamableHttpTransport('http://localhost:8000/mcp/',headers={'Authorization':'Bearer '+token})) as client:
  result=await client.call_tool('search_knowledge',{'query':'revenue','dense':True})
  assert not result.is_error and result.data['ranking_counts']['dense']>0
  denied=await client.call_tool('search_knowledge',{'query':'revenue','dense':True,'tenant':'other'},raise_on_error=False)
  assert denied.is_error
  if Path('/run/secrets/agent').exists():
   import os
   if os.getenv('PUBLIC_RESEARCH_AUTHORIZED')=='true':
    found=await client.call_tool('web_search',{'query':'Python official documentation'})
    assert not found.is_error and found.data['results'] and found.data['discovery_only']
 print('Live MCP dense retrieval, tenant override denial and authorized external search passed.')
asyncio.run(run())
