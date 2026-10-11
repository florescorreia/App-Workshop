"""Explicit live provider acceptance; fictional/public content only, additive and retryable."""
import hashlib,os
import main  # Load the same scoped provider secret configuration as the serving process.
from domain import Domain,Invalid,fetch_public
d=Domain()
source=d.get({'id':'27595884-10ee-4024-9788-3c7637905369','version':1}) if d.tenant.startswith('a4') else d.list('Source',100)[0]
ref={'id':str(source['id']),'version':source['version']}
before=d.get(ref)['body']['hash']
result=d.reindex(ref['id'],ref['version']);assert result['indexed']>0
vectors=d.embedding(['Revenue increased from one hundred to one hundred twenty million.'])
assert len(vectors[0])==3072
with d.connect() as db:
 rows=db.execute('SELECT source_id,source_version,embedding <=> %s::vector AS distance FROM chunks WHERE source_id=%s AND source_version=%s AND embedding_model=%s ORDER BY distance LIMIT 1',(str(vectors[0]),ref['id'],ref['version'],d.embedding_space())).fetchall()
assert rows and 0<=rows[0]['distance']<2
hybrid=d.search('revenue',dense=True);assert hybrid['ranking_counts']['dense']>0 and hybrid['ranking_counts']['bm25']>0
assert all(d.get({'id':h['source_id'],'version':h['source_version']})['tenant']==d.tenant for h in hybrid['hits'])
assert d.get(ref)['body']['hash']==before
space=d.embedding_space();old=os.environ['EMBEDDING_BASE_URL'];os.environ['EMBEDDING_BASE_URL']=old+'/incompatible'
assert d.embedding_space()!=space
with d.connect() as db:assert db.execute('SELECT count(*) AS n FROM chunks WHERE embedding_model=%s',(d.embedding_space(),)).fetchone()['n']==0
os.environ['EMBEDDING_BASE_URL']=old
print({'tenant':d.tenant,'real_dimensions':3072,'indexed_chunks':result['indexed'],'cosine_distance':round(rows[0]['distance'],6),'hybrid_counts':hybrid['ranking_counts'],'incompatible_space_excluded':True,'source_hash_preserved':True})
if os.getenv('PUBLIC_RESEARCH_AUTHORIZED')=='true':
 results=d.web_search('Python official documentation');assert results['results'] and results['discovery_only']
 candidate=next(r['url'] for r in results['results'] if r['url'].startswith('https://www.python.org/'))
 data,media,resolved=fetch_public(candidate)
 source=d.upload(data,'public-search-capture.html',media,{'url':resolved,'publisher':'Python Software Foundation','access_limitations':'Public documentation; synthetic search acceptance only','search_provider':'bing_rss'},'administrator:provider-test','live-search-capture-v1')
 job=d.ingest({'id':str(source['id']),'version':source['version']})
 if job['status'] in ('pending','failed'):d.process_job(job)
 assert hashlib.sha256(d.storage.get(source['body']['hash'])).hexdigest()==source['body']['hash']
 print({'real_search_results':len(results['results']),'captured_bytes':len(data),'provider':'bing_rss','capture_registered':True})
 authorized=os.environ['PUBLIC_RESEARCH_AUTHORIZED'];os.environ['PUBLIC_RESEARCH_AUTHORIZED']='false'
 try:d.web_search('Python')
 except Invalid:pass
 else:raise AssertionError('Unauthorized public search allowed')
 os.environ['PUBLIC_RESEARCH_AUTHORIZED']=authorized
