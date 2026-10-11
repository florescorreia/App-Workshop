import urllib.request

with urllib.request.urlopen('http://localhost:8000/api/health/ready', timeout=2) as response:
    assert response.status == 200
