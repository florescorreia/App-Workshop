import importlib.util, json, shutil, tempfile, unittest, tarfile, io, hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('workshop',ROOT/'scripts/workshop.py')
workshop=importlib.util.module_from_spec(spec);spec.loader.exec_module(workshop)

class WorkshopTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        shutil.copytree(ROOT/'templates',self.root/'templates')
        shutil.copytree(ROOT/'apps/ideaflow/frontend',self.root/'apps/ideaflow/frontend',ignore=shutil.ignore_patterns('node_modules','dist'))
        (self.root/'apps/ideaflow/backend').mkdir();shutil.copy(ROOT/'apps/ideaflow/backend/requirements.lock',self.root/'apps/ideaflow/backend/requirements.lock')
        shutil.copy(ROOT/'workshop.json',self.root/'workshop.json')
        # Production catalog may contain user-created apps. Tests start from
        # the unchanged IdeaFlow reservation only, in an isolated directory.
        data=workshop.catalog(self.root);data['apps']={'ideaflow':data['apps']['ideaflow']}
        (self.root/'workshop.json').write_text(json.dumps(data))
    def tearDown(self):self.temp.cleanup()
    def test_new_apps_are_empty_distinct_and_preserve_existing_identity(self):
        before=workshop.catalog(self.root)['apps']['ideaflow']
        first=workshop.new_app('supplier-portal',self.root)
        second=workshop.new_app('customer-portal',self.root)
        self.assertEqual((first['localPort'],second['localPort']),(8081,8082))
        self.assertEqual((first['vps']['publicPort'],second['vps']['publicPort']),(8444,8445))
        self.assertEqual(workshop.catalog(self.root)['apps']['ideaflow'],before)
        folder=self.root/'apps/supplier-portal'
        self.assertFalse((folder/'.env').exists());self.assertFalse((folder/'.git').exists())
        self.assertEqual(first['database']['volume'],'supplier-portal_pgdata')
        self.assertIn('POSTGRES_DB=supplier_portal',(folder/'.env.example').read_text())
        self.assertIn('POSTGRES_USER=supplier_portal_owner',(folder/'.env.example').read_text())
        self.assertEqual(json.loads((folder/'frontend/package.json').read_text())['name'],'supplier-portal-frontend')
        for file in folder.rglob('*'):
            if file.is_file():self.assertNotIn('{{APP_',file.read_text(),str(file))
        workshop.app_config(self.root,'supplier-portal')
    def test_refuses_duplicate_traversal_collision_and_drift(self):
        before=(self.root/'workshop.json').read_bytes()
        for slug in ('../escape','IdeaFlow','app;rm','a/b','a'*25):
            with self.assertRaises(ValueError):workshop.new_app(slug,self.root)
        with self.assertRaises(ValueError):workshop.new_app('occupied',self.root,port=8080)
        with self.assertRaises(ValueError):workshop.new_app('zero',self.root,port=0)
        self.assertEqual((self.root/'workshop.json').read_bytes(),before)
        workshop.new_app('sample',self.root)
        with self.assertRaises(ValueError):workshop.new_app('sample',self.root)
        file=self.root/'apps/sample/app.json';app=json.loads(file.read_text());app['localPort']=8089;file.write_text(json.dumps(app))
        with self.assertRaises(ValueError):workshop.app_config(self.root,'sample')
    def test_release_keeps_internal_services_private_and_gateway_untouched(self):
        app=workshop.new_app('sample',self.root)
        ids={key:'sha256:'+'a'*64 for key in app['services']}
        files=workshop.render_release(app,'vps.example.com',ids)
        self.assertNotIn('PublishPort=',files['sample-postgres.container'])
        self.assertNotIn('PublishPort=',files['sample-backend.container'])
        self.assertIn('PublishPort=127.0.0.1:18082:80',files['sample-frontend.container'])
        route=files['sample.caddy'];self.assertTrue(route.startswith('vps.example.com:8444 {'))
        self.assertNotIn('redir',route);self.assertNotIn('8443',route)
        self.assertNotIn('ideaflow','\n'.join(files.values()).lower())
        self.assertIn('sample_pgdata',files['sample-postgres.container'])
        self.assertIn('{{.State.Health.Status}}',files['wait-container.sh'])
        app['services']['backend']['healthCommand']='python -c "bad"'
        with self.assertRaises(ValueError):workshop.render_release(app,'vps.example.com',ids)
    def test_image_config_digest_matches_archive_bytes(self):
        app=workshop.new_app('sample',self.root);archive=self.root/'images.tar'
        configs={name:json.dumps({'architecture':'amd64','name':name}).encode() for name in app['services']}
        manifest=[{'Config':name+'.json','RepoTags':[config['image']],'Layers':[]} for name,config in app['services'].items()]
        with tarfile.open(archive,'w') as bundle:
            data=json.dumps(manifest).encode();info=tarfile.TarInfo('manifest.json');info.size=len(data);bundle.addfile(info,io.BytesIO(data))
            for name,data in configs.items():info=tarfile.TarInfo(name+'.json');info.size=len(data);bundle.addfile(info,io.BytesIO(data))
        self.assertEqual(workshop.archive_ids(archive,app),{name:'sha256:'+hashlib.sha256(data).hexdigest() for name,data in configs.items()})

if __name__=='__main__':unittest.main()
