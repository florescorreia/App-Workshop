import asyncio
from pathlib import Path
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from domain import Domain

async def run():
 token=Path('/run/secrets/agent').read_text().strip()
 async with Client(StreamableHttpTransport('http://localhost:8000/mcp/',headers={'Authorization':'Bearer '+token})) as client:
  tools=await client.list_tools()
  required={'search_knowledge','get_definition','register_source','ingest_source','register_artifact','register_analysis','propose_assertions','propose_definition','register_finding','trace_provenance','validate_result','request_publication'}
  assert required.issubset({t.name for t in tools})
  d=Domain();source=d.list('Source')[0]
  result=await client.call_tool('trace_provenance',{'reference':{'id':str(source['id']),'version':1}})
  assert not result.is_error
  denied=await client.call_tool('get_definition',{'name':'Revenue growth','tenant':'other'},raise_on_error=False)
  assert denied.is_error
 print('Real FastMCP discovery/provenance and tenant-parameter rejection passed.')

asyncio.run(run())
