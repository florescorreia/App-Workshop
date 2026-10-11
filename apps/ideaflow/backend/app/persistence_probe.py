"""Creates/checks a unique verification-only record via authenticated API."""
import argparse,json,os,uuid
from datetime import timedelta
import httpx
from .financial import app_today,add_month
from .restore_check import fingerprints
from sqlalchemy import create_engine

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['create','check']);args=p.parse_args()
    directory='/handover';file=directory+'/persistence-probe.json'
    with httpx.Client(base_url='http://localhost:8000/api/v1') as c:
        login=c.post('/session/login',json={'email':os.environ['ADMIN_EMAIL'],'password':os.environ['ADMIN_PASSWORD']});login.raise_for_status()
        c.headers['X-CSRF-Token']=login.json()['csrf']
        if args.action=='create':
            title='Persistence verification '+uuid.uuid4().hex
            r=c.post('/ideas',json={'title':title,'problem':'Check durable records across restart and rebuild.','solution':'Retain this isolated verification evidence.','site_name':'Persistence location','category_name':'Persistence category'})
            r.raise_for_status();idea=r.json();month=add_month(app_today().replace(day=1),-1).isoformat()
            r=c.put('/ideas/'+idea['id']+'/results/'+month,json={'record_version':idea['record_version'],'period_version':0,'gross':'1234.56','recurring':'34.56','spend':'100','reason':'Unique persisted result'});r.raise_for_status()
            detail=c.get('/ideas/'+idea['id']).json()
            data={'id':idea['id'],'title':title,'month':month,'event_count':len(detail['events']),'version':detail['record_version'],'fingerprints':fingerprints(create_engine(os.environ['DATABASE_ADMIN_URL']))}
            os.makedirs(directory,exist_ok=True)
            with open(file,'w') as f:json.dump(data,f)
            print(json.dumps({'created':idea['reference'],'result':'1234.56','events':data['event_count']}))
        else:
            data=json.load(open(file));r=c.get('/ideas/'+data['id']);r.raise_for_status();idea=r.json()
            assert idea['title']==data['title'] and idea['record_version']==data['version']
            assert len(idea['events'])==data['event_count']
            result=next(r for r in idea['results'] if r['month']==data['month']);assert result['gross']=='1234.56'
            assert fingerprints(create_engine(os.environ['DATABASE_ADMIN_URL']))==data['fingerprints']
            print(json.dumps({'persistence':'PASS','reference':idea['reference'],'result':result['gross'],'events':len(idea['events']),'all_business_fingerprints':'unchanged'}))
if __name__=='__main__':main()
