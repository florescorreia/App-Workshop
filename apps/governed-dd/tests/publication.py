"""Explicit synthetic human review actions on isolated test deliverables."""
import copy,uuid
from domain import Domain,Invalid
d=Domain();real=d.get({'id':'f1bd2434-5041-4088-b40c-e3ecd95df135','version':5})
# A separate additive copy permits testing human review without accepting the real task result.
body=copy.deepcopy(real['body']);body['title']='Explicit publication acceptance test copy'
test=d.write('Deliverable',body,'test:acceptance','publication-copy-v1');ref={'id':str(test['id']),'version':test['version']}
validation={'reviewed':ref,'report':'Synthetic review of acceptance copy only','checks':{'passed':True},'reviewer_run':'explicit-test-command'}
d.write('ReviewerValidation',validation,'agent:reviewer','publication-copy-reviewer-v1');d.project()
assert d.validation(ref)['valid']
accepted=d.review(ref,'accept','test:human-reviewer','reviewer','Explicit acceptance of synthetic test copy only')
assert accepted['body']['reviewed']==ref
before=d.get(ref);revised=d.write('Deliverable',{**body,'title':'Explicit test correction needs new review'},'test:acceptance','publication-copy-v2',ref)
assert d.get(ref)==before
assert not d.validation({'id':str(revised['id']),'version':revised['version']})['valid']
try:d.review(ref,'accept','agent:analyst','owner','Spoofed role')
except Invalid:pass
else:raise AssertionError('Agent accepted deliverable')
print('Human acceptance of synthetic copy, immutable exact version, revision review gate and agent denial passed.')
