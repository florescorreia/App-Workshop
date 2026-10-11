import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import workshop
import workshop_vps

class VpsTest(unittest.TestCase):
    def app(self):
        slug='sample'
        return {'slug':slug,'title':'Sample','vps':{'account':slug,'target':'app-sample.target','publicPort':8444,'loopbackPort':18082},
                'database':{'name':'sample','user':'sample_owner','volume':'sample_pgdata'},
                'services':{name:{'image':'unused','memoryMiB':128,'cpus':0.5,'healthCommand':'true'} for name in ('postgres','backend','frontend')}}
    def test_generated_install_and_backup_shell_parse(self):
        app=self.app();script=workshop_vps.install_script(app,'/home/ubuntu/workshop-sample-123456789abc')
        self.assertEqual(subprocess.run(['sh','-n'],input=script,text=True,capture_output=True).returncode,0)
        self.assertNotIn('ideaflow',script)
        self.assertNotIn('rm ',script)
        self.assertNotIn('volume rm',script)
        self.assertIn('workshop-owner',script)
        self.assertIn('if [ "$fresh" = 0 ]',script)
        self.assertIn('sport = :8444',script)
        files=workshop.render_release(app,'vps.example.com',{name:'sha256:'+'b'*64 for name in app['services']})
        for name in ('wait-container.sh','backup.sh'):
            self.assertEqual(subprocess.run(['sh','-n'],input=files[name],text=True,capture_output=True).returncode,0)
    def test_injection_and_shared_storage_rejected(self):
        app=self.app();ids={name:'sha256:'+'b'*64 for name in app['services']}
        app['title']='Sample\nExecStart=bad'
        with self.assertRaises(ValueError):workshop.render_release(app,'vps.example.com',ids)
        app=self.app();app['database']['volume']='ideaflow_pgdata'
        with self.assertRaises(ValueError):workshop.render_release(app,'vps.example.com',ids)

if __name__=='__main__':unittest.main()
