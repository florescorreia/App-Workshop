import os, unittest, uuid
from unittest.mock import patch
import psycopg
from fastapi.testclient import TestClient
from bootstrap import bootstrap
from main import app

class StarterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.live=os.environ['DATABASE_URL'];cls.name='test_'+uuid.uuid4().hex
        with psycopg.connect(cls.live,autocommit=True) as db:db.execute('CREATE DATABASE '+cls.name)
        from urllib.parse import urlsplit,urlunsplit
        parts=urlsplit(cls.live);cls.url=urlunsplit(parts._replace(path='/'+cls.name))
        cls.env=patch.dict(os.environ,{'DATABASE_URL':cls.url});cls.env.start();bootstrap()
    @classmethod
    def tearDownClass(cls):
        cls.env.stop()
        with psycopg.connect(cls.live,autocommit=True) as db:db.execute('DROP DATABASE '+cls.name+' WITH (FORCE)')
    def test_login_transaction_concurrency_and_logout(self):
        with TestClient(app) as client:
            self.assertEqual(client.get('/api/notes').status_code,401)
            login=client.post('/api/session/login',json={'email':os.environ['ADMIN_EMAIL'],'password':os.environ['ADMIN_PASSWORD']})
            self.assertEqual(login.status_code,200)
            self.assertEqual(client.post('/api/session/login',json={'email':os.environ['ADMIN_EMAIL'],'password':os.environ['ADMIN_PASSWORD']},headers={'Origin':'https://other.example'}).status_code,403)
            self.assertEqual(client.get('/api/notes').json(),[])
            self.assertEqual(client.post('/api/notes',json={'body':'hello'}).status_code,403)
            client.headers['X-CSRF-Token']=login.json()['csrf']
            row=client.post('/api/notes',json={'body':'hello'}).json()
            self.assertEqual(client.put('/api/notes/'+row['id'],json={'body':'edited','record_version':1}).status_code,200)
            self.assertEqual(client.put('/api/notes/'+row['id'],json={'body':'stale','record_version':1}).status_code,409)
            with psycopg.connect(self.url) as db:
                self.assertEqual(db.execute('SELECT count(*) FROM note_event').fetchone()[0],2)
                with self.assertRaises(psycopg.errors.RaiseException):db.execute('DELETE FROM note_event')
            self.assertEqual(client.post('/api/session/logout',json={}).status_code,200)
            self.assertEqual(client.get('/api/session/me').status_code,401)
