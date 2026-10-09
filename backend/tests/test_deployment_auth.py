from fastapi.testclient import TestClient
from app.main import app


def test_https_origin_cookie_and_logout(clients, monkeypatch):
    # TLS ends at Caddy, while the upstream connection remains HTTP. Trust the
    # configured public origin, including its port, instead of proxy headers.
    origin='https://ideaflow.test:8443'
    monkeypatch.setenv('APP_ORIGIN',origin)
    monkeypatch.setenv('SESSION_COOKIE_NAME','__Host-ideaflow_session')
    monkeypatch.setenv('SESSION_COOKIE_SECURE','true')
    with TestClient(app,base_url=origin) as c:
        credentials={'email':'user@test.invalid','password':'test-only-password-123'}
        assert c.post('/api/v1/session/login',headers={'Origin':'https://ideaflow.test:8444'},json=credentials).status_code==403
        response=c.post('/api/v1/session/login',headers={'Origin':origin},json=credentials)
        assert response.status_code==200
        cookie=response.headers['set-cookie']
        assert cookie.startswith('__Host-ideaflow_session=')
        assert all(flag in cookie for flag in ('Secure','HttpOnly','SameSite=strict','Path=/'))
        assert 'Domain=' not in cookie
        assert c.get('/api/v1/session/me').status_code==200
        assert c.post('/api/v1/session/logout',headers={'Origin':origin}).status_code==403
        logout=c.post('/api/v1/session/logout',headers={'Origin':origin,'X-CSRF-Token':response.json()['csrf']})
        assert logout.status_code==200
        assert 'Max-Age=0' in logout.headers['set-cookie']
        assert c.get('/api/v1/session/me').status_code==401
