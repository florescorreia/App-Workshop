import asyncio
import contextlib
import hashlib
import hmac
import json
import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
import jwt
import psycopg
from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form, WebSocket
from fastapi.responses import RedirectResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from psycopg.rows import dict_row
from domain import Domain,Invalid

CONTROL=os.getenv('SERVICE_MODE')=='control'
if os.getenv('PROVIDER_KEYS_FILE'):
    for key,value in json.loads(Path(os.environ['PROVIDER_KEYS_FILE']).read_text()).items():
        if key in (os.getenv('WEB_SEARCH_API_KEY_ENV','DD_SEARCH_API_KEY'),os.getenv('EMBEDDING_API_KEY_ENV','DD_EMBEDDING_API_KEY')):os.environ[key]=value
domain=None if CONTROL else Domain()
COOKIE='governed_dd_session'

def component_origin(component,tenant):
    from urllib.parse import urlsplit
    base=urlsplit(os.getenv('APP_BASE_URL','http://localhost:8081'))
    suffix=os.getenv('COMPONENT_DOMAIN','localhost')
    port=(':'+str(base.port)) if base.port else ''
    return f'{base.scheme}://{component}-{tenant}.{suffix}{port}'

def upstream_endpoint(tenant,component,port):
    """Optional reviewed VPS mTLS transport; local networks remain the default."""
    path=os.getenv('TENANT_UPSTREAMS_FILE')
    if not path:return f'http://{component}-{tenant}:{port}'
    entries=json.loads(Path(path).read_text())
    entry=entries.get(tenant,{}).get(component)
    if not entry or not entry.startswith('https://'):raise HTTPException(503,detail='Tenant transport unavailable')
    return entry.rstrip('/')

def upstream_tls():
    if not os.getenv('TENANT_UPSTREAMS_FILE'):return True
    import ssl
    context=ssl.create_default_context(cafile=os.environ['TENANT_CA_FILE'])
    context.load_cert_chain(os.environ['TENANT_CLIENT_CERT_FILE'],os.environ['TENANT_CLIENT_KEY_FILE'])
    return context


def control_db():
    return psycopg.connect(os.environ['DATABASE_URL'],row_factory=dict_row)


async def worker():
    while True:
        try:
            with domain.connect() as db:
                job=db.execute("UPDATE jobs SET status='running',started_at=now() WHERE id=(SELECT id FROM jobs WHERE status='pending' AND NOT cancelled ORDER BY updated_at LIMIT 1 FOR UPDATE SKIP LOCKED) RETURNING *").fetchone()
            if job: await asyncio.to_thread(domain.process_job,job)
            await asyncio.to_thread(domain.project)
        except Exception:
            pass  # State remains pending/failed; health reports storage availability.
        await asyncio.sleep(3)


@asynccontextmanager
async def lifespan(app):
    if CONTROL:
        with control_db() as db: db.execute(Path('/app/control.sql').read_text())
        yield
    else:
        domain.migrate()
        task=asyncio.create_task(worker())
        async with mcp.router.lifespan_context(mcp):
            yield
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError): await task


app=FastAPI(lifespan=lifespan,docs_url=None,redoc_url=None,openapi_url=None)


@app.middleware('http')
async def mcp_boundary(request,call_next):
    if CONTROL:
        import re
        host=request.url.hostname or ''
        match=re.fullmatch(r'(paperclip|lab)-([a-f0-9]{24})\.'+re.escape(os.getenv('COMPONENT_DOMAIN','localhost')),host)
        if match:
            return await component_proxy(request,match[2],match[1])
        from urllib.parse import urlsplit
        if host not in ('localhost','127.0.0.1','portal','gateway',urlsplit(os.environ['APP_BASE_URL']).hostname):
            return Response('Not found',status_code=404)
    if not CONTROL and request.url.path.startswith('/mcp'):
        token=request.headers.get('authorization','').removeprefix('Bearer ')
        reviewer_file=os.getenv('REVIEWER_KEY_FILE')
        reviewer_ok=bool(reviewer_file and token and hmac.compare_digest(token,Path(reviewer_file).read_text().strip()))
        if not reviewer_ok and (not token or not hmac.compare_digest(token,Path(os.environ['AGENT_KEY_FILE']).read_text().strip())):
            return Response('Not found',status_code=404)
    return await call_next(request)


@app.exception_handler(Invalid)
async def invalid(request,exc):
    return Response(json.dumps({'error':str(exc)}),status_code=422,media_type='application/json')


def hidden():
    raise HTTPException(404,detail='Not found')


def current(request):
    session=request.cookies.get(COOKIE,'')
    with control_db() as db:
        row=db.execute('SELECT * FROM sessions WHERE id=%s AND expires_at>now()',(hashlib.sha256(session.encode()).hexdigest(),)).fetchone()
    if not row: raise HTTPException(401,detail='Sign in required')
    return row


def membership(subject,tenant):
    with control_db() as db:
        return db.execute('SELECT m.role,t.name,t.active FROM memberships m JOIN tenants t ON t.id=m.tenant WHERE m.subject=%s AND m.tenant=%s',(subject,tenant)).fetchone()


def check_origin(request,session):
    if request.headers.get('origin')!=os.environ['APP_BASE_URL'] or not hmac.compare_digest(request.headers.get('x-dd-csrf',''),session['csrf']):
        raise HTTPException(403,detail='Request origin/CSRF validation failed')


def principal(request):
    # Agents never receive the gateway signing secret. Claims are short-lived and tenant-bound.
    token=request.headers.get('authorization','').removeprefix('Bearer ')
    key=Path(os.environ['GATEWAY_KEY_FILE']).read_text().strip()
    agent_key=Path(os.environ['AGENT_KEY_FILE']).read_text().strip()
    if token and hmac.compare_digest(token,agent_key):
        return {'subject':'agent:analyst','role':'agent','tenant':domain.tenant}
    reviewer_file=os.getenv('REVIEWER_KEY_FILE')
    if reviewer_file and token and hmac.compare_digest(token,Path(reviewer_file).read_text().strip()):return {'subject':'agent:reviewer','role':'agent','tenant':domain.tenant}
    try:
        claims=jwt.decode(token,key,algorithms=['HS256'],issuer='governed-dd-gateway',audience=domain.tenant,options={'require':['exp','iss','aud','sub','role']})
    except jwt.PyJWTError:
        hidden()
    if claims.get('tenant')!=domain.tenant: hidden()
    return {'subject':claims['sub'],'role':claims['role'],'tenant':domain.tenant}


@app.get('/health')
def health():
    with (control_db() if CONTROL else domain.connect()) as db:
        db.execute('SELECT 1')
    return {'ok':True,'mode':'control' if CONTROL else 'tenant'}


if CONTROL:
    async def component_proxy(request,tenant,component):
        # Separate origins preserve upstream absolute paths and host-only native cookies.
        origin=component_origin(component,tenant)
        if request.url.path=='/_dd/enter':
            ticket=request.query_params.get('ticket','')
            with control_db() as db:
                row=db.execute('DELETE FROM component_tickets WHERE id=%s AND tenant=%s AND component=%s AND expires_at>now() RETURNING *',(hashlib.sha256(ticket.encode()).hexdigest(),tenant,component)).fetchone()
                session=db.execute('SELECT * FROM sessions WHERE id=%s AND expires_at>now()',(row['session_id'],)).fetchone() if row else None
            if not session or not membership(session['subject'],tenant):return Response('Not found',status_code=404)
            response=RedirectResponse('/auth' if component=='paperclip' else '/')
            # Component cookie stores the existing session hash, never an OIDC/native token.
            response.set_cookie('governed_dd_component',session['id'],httponly=True,samesite='lax',max_age=3600,path='/',secure=origin.startswith('https://'))
            return response
        with control_db() as db:
            session=db.execute('SELECT * FROM sessions WHERE id=%s AND expires_at>now()',(request.cookies.get('governed_dd_component',''),)).fetchone()
        member=membership(session['subject'],tenant) if session else None
        if not member:return Response('Not found',status_code=404)
        if component=='lab' and member['role']!='owner':return Response('Not found',status_code=404)
        if not member['active']:return Response('Engagement is stopped',status_code=503)
        if request.method not in ('GET','HEAD','OPTIONS'):
            if request.headers.get('origin')!=origin:return Response('Forbidden',status_code=403)
            if member['role']=='viewer' and not request.url.path.startswith('/api/auth/'):return Response('Forbidden',status_code=403)
        data=await request.body()
        if len(data)>21*1024*1024:return Response(status_code=413)
        # Gate every upstream path, including aliases, static files and attachment APIs.
        headers={k:v for k,v in request.headers.items() if k.lower() in ('content-type','accept','origin','cookie','referer','authorization')}
        headers['host']=request.headers['host']
        async with httpx.AsyncClient(trust_env=False,timeout=120,follow_redirects=False,verify=upstream_tls()) as client:
            try:upstream=await client.request(request.method,upstream_endpoint(tenant,component,3100 if component=='paperclip' else 3000)+request.url.path,params=request.query_params,headers=headers,content=data)
            except httpx.HTTPError:return Response('Engagement service unavailable',status_code=503)
        with control_db() as db:active=db.execute('SELECT 1 FROM sessions WHERE id=%s AND expires_at>now()',(session['id'],)).fetchone()
        if not active or not membership(session['subject'],tenant):return Response('Not found',status_code=404)
        response=Response(upstream.content,status_code=upstream.status_code,headers={k:v for k,v in upstream.headers.items() if k.lower() in ('content-type','location','content-disposition')})
        for cookie in upstream.headers.get_list('set-cookie'):response.headers.append('set-cookie',cookie)
        return response

    @app.get('/t/{tenant}/open/{component}')
    def open_component(request:Request,tenant:str,component:str):
        session=current(request);member=membership(session['subject'],tenant)
        if not member or component not in ('paperclip','lab') or (component=='lab' and member['role']!='owner'):hidden()
        if not member['active']:raise HTTPException(503,detail='Engagement is stopped')
        ticket=secrets.token_urlsafe(48)
        with control_db() as db:db.execute("INSERT INTO component_tickets(id,session_id,tenant,component,expires_at) VALUES(%s,%s,%s,%s,now()+interval '30 seconds')",(hashlib.sha256(ticket.encode()).hexdigest(),session['id'],tenant,component))
        return RedirectResponse(component_origin(component,tenant)+'/_dd/enter?ticket='+ticket)
    async def oidc_metadata():
        async with httpx.AsyncClient(trust_env=False,timeout=15) as client:
            try:
                response=await client.get(os.environ['OIDC_INTERNAL_URL']+'/.well-known/openid-configuration')
                response.raise_for_status()
            except httpx.HTTPError:
                raise HTTPException(503,detail='Identity service is starting or unavailable. Try again shortly.')
            return response.json()

    @app.get('/auth/login')
    async def login():
        from base64 import urlsafe_b64encode
        state=secrets.token_urlsafe(32); verifier=secrets.token_urlsafe(48);nonce=secrets.token_urlsafe(32)
        with control_db() as db:
            db.execute("INSERT INTO login_states(id,verifier,nonce,expires_at) VALUES(%s,%s,%s,now()+interval '5 minutes')",(state,verifier,nonce))
        metadata=await oidc_metadata()
        from urllib.parse import urlencode
        query=urlencode({'client_id':'dd-portal','response_type':'code','scope':'openid profile','redirect_uri':os.environ['APP_BASE_URL']+'/auth/callback','state':state,'nonce':nonce,'code_challenge':urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('='),'code_challenge_method':'S256'})
        response=RedirectResponse(metadata['authorization_endpoint']+'?'+query)
        response.set_cookie('governed_dd_login',state,httponly=True,samesite='lax',max_age=300,path='/auth',secure=os.environ['APP_BASE_URL'].startswith('https'))
        return response

    @app.get('/auth/callback')
    async def callback(request:Request,state:str='',code:str=''):
        if not state or not hmac.compare_digest(state,request.cookies.get('governed_dd_login','')): hidden()
        with control_db() as db:
            saved=db.execute('DELETE FROM login_states WHERE id=%s AND expires_at>now() RETURNING *',(state,)).fetchone()
        if not saved: hidden()
        internal=os.environ['OIDC_INTERNAL_URL']
        async with httpx.AsyncClient(trust_env=False,timeout=15) as client:
            response=await client.post(internal+'/protocol/openid-connect/token',data={'grant_type':'authorization_code','client_id':'dd-portal','client_secret':Path(os.environ['OIDC_CLIENT_SECRET_FILE']).read_text().strip(),'code':code,'code_verifier':saved['verifier'],'redirect_uri':os.environ['APP_BASE_URL']+'/auth/callback'})
            if response.status_code!=200: raise HTTPException(401,detail='Login could not be completed')
            tokens=response.json()
            jwks=(await client.get(internal+'/protocol/openid-connect/certs')).json()
        header=jwt.get_unverified_header(tokens['id_token'])
        signing=next((k for k in jwks['keys'] if k['kid']==header['kid']),None)
        if not signing: hidden()
        claims=jwt.decode(tokens['id_token'],jwt.PyJWK.from_dict(signing).key,algorithms=['RS256'],issuer=os.environ['OIDC_ISSUER_URL'],audience='dd-portal',options={'require':['exp','iat','iss','aud','sub','nonce']})
        if claims['nonce']!=saved['nonce']: hidden()
        session=secrets.token_urlsafe(48)
        with control_db() as db:
            db.execute("INSERT INTO sessions(id,subject,csrf,expires_at,id_token) VALUES(%s,%s,%s,now()+interval '1 hour',%s)",(hashlib.sha256(session.encode()).hexdigest(),claims['sub'],secrets.token_urlsafe(32),tokens['id_token']))
        response=RedirectResponse('/')
        response.set_cookie(COOKIE,session,httponly=True,samesite='lax',secure=os.environ['APP_BASE_URL'].startswith('https'),path='/',max_age=3600)
        response.delete_cookie('governed_dd_login',path='/auth')
        return response

    @app.post('/auth/logout')
    async def logout(request:Request):
        session=current(request); check_origin(request,session)
        with control_db() as db: db.execute('DELETE FROM sessions WHERE id=%s',(session['id'],))
        from urllib.parse import urlencode
        url=os.environ['OIDC_ISSUER_URL']+'/protocol/openid-connect/logout?'+urlencode({'id_token_hint':session['id_token'],'post_logout_redirect_uri':os.environ['APP_BASE_URL']+'/'})
        response=Response(json.dumps({'url':url}),media_type='application/json')
        response.delete_cookie(COOKIE,path='/')
        return response

    @app.get('/api/me')
    def me(request:Request):
        session=current(request)
        with control_db() as db:
            tenants=db.execute('SELECT t.id,t.name,t.active,m.role FROM tenants t JOIN memberships m ON t.id=m.tenant WHERE m.subject=%s ORDER BY t.name',(session['subject'],)).fetchall()
        return {'subject':session['subject'],'csrf':session['csrf'],'engagements':tenants}

    @app.api_route('/t/{tenant}/{path:path}',methods=['GET','POST','PUT','PATCH','DELETE','HEAD','OPTIONS'])
    async def tenant_proxy(request:Request,tenant:str,path:str):
        session=current(request); member=membership(session['subject'],tenant)
        if not member: hidden()
        if path.startswith(('paperclip','lab','mcp')):hidden()
        if request.method not in ('GET','HEAD','OPTIONS'): check_origin(request,session)
        # Only Explorer and governance HTTP API prefixes; MCP and database endpoints never routed.
        if path.startswith('api/'):
            if request.method!='GET' and member['role']=='viewer': raise HTTPException(403,detail='Viewer permission')
            suffix=path
            base=upstream_endpoint(tenant,'dd',8000)
            from datetime import datetime,timezone,timedelta
            token=jwt.encode({'iss':'governed-dd-gateway','aud':tenant,'sub':session['subject'],'tenant':tenant,'role':member['role'],'exp':datetime.now(timezone.utc)+timedelta(seconds=15)},Path(os.environ['GATEWAY_KEY_FILE']).read_text().strip(),algorithm='HS256')
            headers={'authorization':'Bearer '+token}
        else:
            base=upstream_endpoint(tenant,'explorer',8080);suffix=path;headers={}
        if not member['active']: return Response('Engagement is stopped. Ask your administrator to start it.',status_code=503)
        if request.headers.get('content-length') and int(request.headers['content-length'])>21*1024*1024: raise HTTPException(413)
        data=await request.body()
        if len(data)>21*1024*1024: raise HTTPException(413)
        if request.headers.get('content-type'): headers['content-type']=request.headers['content-type']
        async with httpx.AsyncClient(trust_env=False,timeout=120,follow_redirects=False,verify=upstream_tls()) as client:
            try: upstream=await client.request(request.method,base+'/'+suffix,params=request.query_params,headers=headers,content=data)
            except httpx.HTTPError: return Response('Engagement service unavailable',status_code=503)
        # Recheck after long requests so a revoked user receives no protected response.
        with control_db() as db:active=db.execute('SELECT 1 FROM sessions WHERE id=%s AND expires_at>now()',(session['id'],)).fetchone()
        if not active or not membership(session['subject'],tenant): hidden()
        return Response(upstream.content,status_code=upstream.status_code,headers={k:v for k,v in upstream.headers.items() if k.lower() in ('content-type','content-disposition')})

    @app.websocket('/t/{tenant}/{path:path}')
    async def reject_stream(websocket:WebSocket,tenant:str,path:str):
        # No active streams yet. Fail closed for every upgrade.
        await websocket.close(code=1008)

    @app.websocket('/{path:path}')
    async def component_stream(websocket:WebSocket,path:str):
        import re
        import websockets
        host=websocket.url.hostname or ''
        match=re.fullmatch(r'(paperclip|lab)-([a-f0-9]{24})\.'+re.escape(os.getenv('COMPONENT_DOMAIN','localhost')),host)
        if not match:await websocket.close(code=1008);return
        component,tenant=match[1],match[2]
        with control_db() as db:
            session=db.execute('SELECT * FROM sessions WHERE id=%s AND expires_at>now()',(websocket.cookies.get('governed_dd_component',''),)).fetchone()
        member=membership(session['subject'],tenant) if session else None
        origin=component_origin(component,tenant)
        if not member or not member['active'] or (component=='lab' and member['role']!='owner') or websocket.headers.get('origin')!=origin:
            await websocket.close(code=1008);return
        # Native upstream separately validates its session. Never grant proxy identity headers.
        upstream_url=upstream_endpoint(tenant,component,3100 if component=='paperclip' else 3000).replace('https://','wss://').replace('http://','ws://')+'/'+path
        if websocket.url.query:upstream_url+='?'+websocket.url.query
        try:
            tls={'ssl':upstream_tls()} if upstream_url.startswith('wss://') else {}
            async with websockets.connect(upstream_url,origin=origin,additional_headers={'Cookie':websocket.headers.get('cookie','')},max_size=2*1024*1024,open_timeout=10,**tls) as upstream:
                await websocket.accept()
                async def inbound():
                    while True:
                        message=await websocket.receive()
                        if message['type']=='websocket.disconnect':return
                        await upstream.send(message.get('text') if message.get('text') is not None else message['bytes'])
                async def outbound():
                    async for message in upstream:
                        if not membership(session['subject'],tenant):await websocket.close(code=1008);return
                        if isinstance(message,str):await websocket.send_text(message)
                        else:await websocket.send_bytes(message)
                async def revoked():
                    while True:
                        await asyncio.sleep(1)
                        with control_db() as db:active=db.execute('SELECT 1 FROM sessions WHERE id=%s AND expires_at>now()',(session['id'],)).fetchone()
                        if not active or not membership(session['subject'],tenant):await websocket.close(code=1008);return
                tasks=[asyncio.create_task(f()) for f in (inbound,outbound,revoked)]
                try:await asyncio.wait(tasks,return_when=asyncio.FIRST_COMPLETED)
                finally:
                    for task in tasks:task.cancel()
                    await asyncio.gather(*tasks,return_exceptions=True)
        except Exception:
            with contextlib.suppress(Exception):await websocket.close(code=1008)

    @app.get('/{path:path}')
    def portal(path:str):
        root=Path('/frontend')
        candidate=root/path
        if path and candidate.is_file() and candidate.resolve().is_relative_to(root):
            import mimetypes
            return Response(candidate.read_bytes(),media_type=mimetypes.guess_type(path)[0])
        return Response((root/'index.html').read_bytes(),media_type='text/html')
else:
    from fastmcp import FastMCP
    from fastmcp.server.dependencies import get_http_headers
    tools=FastMCP('Governed DD')

    def agent():
        headers=get_http_headers()
        token=headers.get('authorization','').removeprefix('Bearer ')
        reviewer_file=os.getenv('REVIEWER_KEY_FILE')
        if reviewer_file and hmac.compare_digest(token,Path(reviewer_file).read_text().strip()):return 'agent:reviewer'
        if not hmac.compare_digest(token,Path(os.environ['AGENT_KEY_FILE']).read_text().strip()):
            raise Invalid('Tenant agent authentication required')
        return 'agent:analyst'

    @tools.tool
    def search_knowledge(query:str,limit:int=20,dense:bool|None=None):
        agent(); return domain.search(query,limit,dense=bool(os.getenv('EMBEDDING_MODEL')) if dense is None else dense)

    @tools.tool
    def get_definition(name:str):
        agent(); return [r for r in domain.list('Definition',100) if r['body']['name'].casefold()==name.casefold()]

    @tools.tool
    def register_source(url:str,metadata:dict,key:str):
        actor=agent()
        if os.getenv('PUBLIC_RESEARCH_AUTHORIZED')!='true': raise Invalid('Public research requires engagement authorization')
        from domain import fetch_public
        data,media,resolved=fetch_public(url)
        return domain.upload(data,'capture.html' if media=='text/html' else 'capture.txt',media,{**metadata,'url':resolved},actor,key)

    @tools.tool
    def ingest_source(source:dict):
        agent(); return domain.ingest(source)

    @tools.tool
    def register_artifact(content:str,media_type:str,run:dict,key:str):
        actor=agent();data=content.encode(); digest=domain.storage.put(data)
        return domain.write('Artifact',{'hash':digest,'size':len(data),'media_type':media_type,'run':run},actor,key)

    @tools.tool
    def register_binary_artifact(content_base64:str,media_type:str,run:dict,key:str):
        """Preserve nontext output bytes, bounded to 20 MiB, through shared domain validation."""
        import base64,binascii
        actor=agent()
        if len(content_base64)>28*1024*1024:raise Invalid('Artifact exceeds byte limit')
        try:data=base64.b64decode(content_base64,validate=True)
        except binascii.Error:raise Invalid('Valid base64 artifact bytes required')
        if not data or len(data)>20*1024*1024:raise Invalid('Artifact must be between 1 byte and 20 MiB')
        digest=domain.storage.put(data)
        return domain.write('Artifact',{'hash':digest,'size':len(data),'media_type':media_type,'run':run},actor,key)

    @tools.tool
    def inspect_artifact(reference:dict):
        agent();row=domain.get(reference)
        if row['kind']!='Artifact':raise Invalid('Artifact reference required')
        data=domain.storage.get(row['body']['hash'])
        if len(data)>200000:raise Invalid('Artifact preview limited to 200 KB')
        return {'object':row,'text':data.decode('utf8'),'verified_hash':row['body']['hash']}

    @tools.tool
    def revise_analysis(reference:dict,manifest:dict,key:str):
        """Append a new AnalysisRun revision with exact output references after artifacts exist. Original revision remains intact."""
        return domain.write('AnalysisRun',manifest,agent(),key,reference)

    @tools.tool
    def revise_deliverable(reference:dict,deliverable:dict,key:str):
        return domain.write('Deliverable',deliverable,agent(),key,reference)

    @tools.tool
    def register_reviewer_validation(validation:dict,key:str):
        return domain.write('ReviewerValidation',validation,agent(),key)

    @tools.tool
    def register_analysis(manifest:dict,key:str):
        """Register a run. Required: task_id, paperclip_instance, paperclip_run_id, inputs [{id,version}], code_commit, environment, parameters, seeds, outputs [{id,version}] (empty allowed before artifacts), execution_status. Put numeric results in parameters/results, never outputs."""
        return domain.write('AnalysisRun',manifest,agent(),key)

    @tools.tool
    def propose_assertions(assertions:list[dict],batch_key:str):
        actor=agent();return [domain.write('Assertion',a,actor,f'{batch_key}:{i}') for i,a in enumerate(assertions)]

    @tools.tool
    def propose_definition(definition:dict,key:str):
        return domain.write('Definition',definition,agent(),key)

    @tools.tool
    def propose_ontology(document:dict):
        return domain.ontology(document,agent())

    @tools.tool
    def register_relation(relation:dict,key:str):
        return domain.write('Relation',relation,agent(),key)

    @tools.tool
    def register_finding(finding:dict,key:str):
        return domain.write('Finding',finding,agent(),key)

    @tools.tool
    def trace_provenance(reference:dict):
        agent();row=domain.get(reference)
        result={'object':row,'references':{k:[domain.get(r) for r in row['body'].get(k,[])] for k in ['evidence','inputs','findings','artifacts']}}
        if row['kind']=='Source':
            with domain.connect() as db:result['extractions']=db.execute('SELECT locator,text,hash,extractor FROM chunks WHERE source_id=%s AND source_version=%s ORDER BY id LIMIT 50',(row['id'],row['version'])).fetchall()
        return result

    @tools.tool
    def validate_result(reference:dict):
        agent(); return domain.validation(reference)

    @tools.tool
    def request_publication(deliverable:dict,key:str):
        actor=agent(); row=domain.write('Deliverable',deliverable,actor,key)
        return {'deliverable':row,'validation':domain.validation({'id':str(row['id']),'version':row['version']}),'state':'awaiting human review'}

    @tools.tool
    def web_search(query:str):
        agent();return domain.web_search(query)

    mcp=tools.http_app(path='/')
    app.mount('/mcp',mcp)

    @app.get('/api/records')
    def records(request:Request,kind:str|None=None,limit:int=50,offset:int=0):
        principal(request);return domain.list(kind,limit,offset)

    @app.post('/api/ontology/approve')
    async def approve_ontology(request:Request):
        who=principal(request);data=await request.json()
        return domain.ontology(data['document'],who['subject'],True,who['role'])

    @app.get('/api/records/{ident}/{version}')
    def record(request:Request,ident:str,version:int):
        principal(request);return domain.get({'id':ident,'version':version})

    @app.get('/api/versions/{ident}')
    def versions(request:Request,ident:str):
        principal(request)
        with domain.connect() as db:return db.execute('SELECT id,version,kind,body,actor,created_at FROM records WHERE id=%s AND tenant=%s ORDER BY version DESC LIMIT 100',(ident,domain.tenant)).fetchall()

    @app.get('/api/compare/{ident}/{before}/{after}')
    def compare(request:Request,ident:str,before:int,after:int):
        principal(request);a=domain.get({'id':ident,'version':before});b=domain.get({'id':ident,'version':after})
        def changes(field):
            old={json.dumps(v,sort_keys=True) for v in a['body'].get(field,[])};new={json.dumps(v,sort_keys=True) for v in b['body'].get(field,[])}
            return {'added':[json.loads(v) for v in new-old],'removed':[json.loads(v) for v in old-new]}
        def evidence(record):
            refs=[]
            for finding in record['body'].get('findings',[]):refs.extend(domain.get(finding)['body'].get('evidence',[]))
            return {json.dumps(r,sort_keys=True) for r in refs}
        old=evidence(a);new=evidence(b)
        return {'before':before,'after':after,'findings':changes('findings'),'artifacts':changes('artifacts'),'evidence':{'added':[json.loads(v) for v in new-old],'removed':[json.loads(v) for v in old-new]},'changed_fields':[k for k in set(a['body'])|set(b['body']) if a['body'].get(k)!=b['body'].get(k)]}

    @app.get('/api/preview/{ident}/{version}')
    def preview(request:Request,ident:str,version:int):
        principal(request);row=domain.get({'id':ident,'version':version})
        if row['kind'] not in ('Source','Artifact'):hidden()
        media=row['body']['media_type'];data=domain.storage.get(row['body']['hash'])
        if media=='application/pdf':return Response(data,media_type=media,headers={'Content-Disposition':'inline','X-Content-Type-Options':'nosniff'})
        if media.startswith('text/'):
            # Serve untrusted HTML as plain text, never execute client source markup.
            return Response(data[:200000],media_type='text/plain',headers={'X-Content-Type-Options':'nosniff'})
        hidden()

    @app.post('/api/records')
    async def create(request:Request):
        who=principal(request)
        if who['role']=='viewer': raise HTTPException(403)
        data=await request.json()
        return domain.write(data['kind'],data['body'],who['subject'],data['key'],data.get('previous'))

    @app.post('/api/sources/upload')
    async def upload(request:Request,file:UploadFile=File(),metadata:str=Form('{}'),key:str=Form()):
        who=principal(request)
        if who['role']=='viewer': raise HTTPException(403)
        data=await file.read(20*1024*1024+1)
        row=domain.upload(data,file.filename,file.content_type,json.loads(metadata),who['subject'],key)
        return {'source':row,'job':domain.ingest({'id':str(row['id']),'version':row['version']})}

    @app.get('/api/bytes/{ident}/{version}')
    def download(request:Request,ident:str,version:int):
        principal(request);row=domain.get({'id':ident,'version':version})
        if row['kind'] not in ('Source','Artifact'): hidden()
        data=domain.storage.get(row['body']['hash'])
        return Response(data,media_type=row['body']['media_type'],headers={'Content-Disposition':'attachment; filename="'+row['body'].get('filename','artifact').replace('"','').replace('\r','').replace('\n','')+'"','X-Content-Type-Options':'nosniff'})

    @app.get('/api/chunks/{ident}/{version}')
    def chunks(request:Request,ident:str,version:int,offset:int=0):
        principal(request);domain.get({'id':ident,'version':version})
        with domain.connect() as db: return db.execute('SELECT id,locator,text,extractor,hash FROM chunks WHERE source_id=%s AND source_version=%s ORDER BY id LIMIT 50 OFFSET %s',(ident,version,max(offset,0))).fetchall()

    @app.get('/api/search')
    def search(request:Request,q:str,dense:bool=True):
        principal(request);return domain.search(q,dense=dense)

    @app.get('/api/graph')
    def graph(request:Request,key:str,depth:int=1,limit:int=40,relation:str|None=None):
        principal(request);return domain.graph(key,depth,limit,relation)

    @app.get('/api/status')
    def status(request:Request):
        principal(request)
        with domain.connect() as db:
            return {'jobs':db.execute('SELECT * FROM jobs ORDER BY updated_at DESC LIMIT 50').fetchall(),'projection':db.execute('SELECT state,count(*) FROM outbox GROUP BY state').fetchall(),'dense_configured':bool(os.getenv('EMBEDDING_MODEL')),'agent_execution':'not yet accepted'}

    @app.post('/api/jobs/{ident}/cancel')
    def cancel(request:Request,ident:str):
        who=principal(request)
        if who['role']=='viewer': raise HTTPException(403)
        with domain.connect() as db:
            row=db.execute("UPDATE jobs SET cancelled=true,status=CASE WHEN status='pending' THEN 'cancelled' ELSE status END,updated_at=now() WHERE id=%s RETURNING *",(ident,)).fetchone()
            if not row: hidden()
            domain.audit(db,who['subject'],'cancel-ingestion',{'id':row['source_id'],'version':row['version']})
        return row

    @app.post('/api/reviews')
    async def review(request:Request):
        who=principal(request);data=await request.json()
        return domain.review(data['reference'],data['decision'],who['subject'],who['role'],data['report'])

    @app.get('/api/validate/{ident}/{version}')
    def validate(request:Request,ident:str,version:int):
        principal(request);return domain.validation({'id':ident,'version':version})
