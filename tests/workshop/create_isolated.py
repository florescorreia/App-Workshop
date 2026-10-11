"""Create disposable verification sources; never register sample apps live."""
import shutil
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import workshop

root=ROOT/'artifacts/workshop-check'
root.mkdir(parents=True,exist_ok=False)
shutil.copytree(ROOT/'templates',root/'templates')
for folder,names in {'apps/ideaflow/frontend':['package.json','package-lock.json'],
                     'apps/ideaflow/backend':['requirements.lock'],
                     'scripts':['workshop.py','workshop.ps1']}.items():
    (root/folder).mkdir(parents=True)
    for name in names:shutil.copy(ROOT/folder/name,root/folder/name)
shutil.copy(ROOT/'workshop.json',root/'workshop.json')
workshop.new_app('workshop-check-a',root,port=18881)
workshop.new_app('workshop-check-b',root,port=18882)
print('Isolated apps created; production catalog unchanged')
