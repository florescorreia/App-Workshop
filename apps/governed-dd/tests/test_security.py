import hashlib
import socket
import pytest
from domain import FileStorage,Invalid,public_url,Domain


def test_bytes_are_content_addressed_and_immutable(tmp_path):
 storage=FileStorage(tmp_path)
 digest=storage.put(b'original evidence')
 assert storage.put(b'original evidence')==digest
 assert storage.get(digest)==b'original evidence'
 assert len(list(tmp_path.rglob(digest)))==1
 with pytest.raises(Invalid):storage.get('../../outside')
 path=tmp_path/digest[:2]/digest
 path.chmod(0o600);path.write_bytes(b'corruption')
 with pytest.raises(Invalid,match='checksum'):storage.get(digest)


@pytest.mark.parametrize('url',['http://example.com','file:///etc/passwd','https://user:password@example.com','https://example.com:8443'])
def test_fetch_rejects_unsafe_schemes_credentials_and_ports(url):
 with pytest.raises(Invalid):public_url(url)


@pytest.mark.parametrize('address',['127.0.0.1','10.1.2.3','169.254.169.254','::1','192.168.0.1','100.64.0.1'])
def test_fetch_rejects_private_dns(monkeypatch,address):
 monkeypatch.setattr(socket,'getaddrinfo',lambda *a,**k:[(socket.AF_INET,socket.SOCK_STREAM,6,'',(address,443))])
 with pytest.raises(Invalid):public_url('https://documents.example')


def test_mixed_public_private_dns_rejected(monkeypatch):
 monkeypatch.setattr(socket,'getaddrinfo',lambda *a,**k:[(2,1,6,'',('8.8.8.8',443)),(2,1,6,'',('127.0.0.1',443))])
 with pytest.raises(Invalid):public_url('https://documents.example')


def test_agent_cannot_grant_human_acceptance():
 service=Domain('not-connected','a',object())
 with pytest.raises(Invalid,match='Human'):service.review({},'accept','agent:analyst','owner','accept')


def test_incomplete_manifest_rejected_before_database():
 service=Domain('not-connected','a',object())
 with pytest.raises(Invalid,match='Required fields'):service.write('AnalysisRun',{'task_id':'fake'},'agent:analyst','test')
