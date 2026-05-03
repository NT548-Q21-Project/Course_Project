from jose import jwt

from app.core.config import settings


class FakeUpstreamResponse:
    def __init__(self, status_code=200, content=b'{"ok":true}', headers=None):
        self.status_code = status_code
        self.content = content
        self.headers = headers or {"content-type": "application/json"}


class FakeAsyncClient:
    def __init__(self, timeout):
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def request(self, method, url, params=None, content=None, headers=None):
        self.last_request = {
            "method": method,
            "url": url,
            "params": params,
            "content": content,
            "headers": headers,
        }
        return FakeUpstreamResponse()


def test_auth_proxy_forwards_request(monkeypatch, client):
    fake_client = FakeAsyncClient(timeout=60.0)
    monkeypatch.setattr("app.main.httpx.AsyncClient", lambda timeout: fake_client)

    response = client.post("/api/auth/login", json={"email": "test@example.com"})

    assert response.status_code == 200
    assert fake_client.last_request["method"] == "POST"
    assert fake_client.last_request["url"] == (
        f"{settings.IDENTITY_SERVICE_URL}/auth/login"
    )
    assert fake_client.last_request["headers"]["content-type"].startswith(
        "application/json"
    )


def test_recruitment_proxy_injects_user_headers(monkeypatch, client):
    fake_client = FakeAsyncClient(timeout=60.0)
    monkeypatch.setattr("app.main.httpx.AsyncClient", lambda timeout: fake_client)

    token = jwt.encode(
        {
            "sub": "11111111-1111-1111-1111-111111111111",
            "auth_id": "22222222-2222-2222-2222-222222222222",
            "email": "candidate@example.com",
            "role": "candidate",
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    response = client.get(
        "/api/recruitment/jobs",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert fake_client.last_request["url"] == (
        f"{settings.RECRUITMENT_SERVICE_URL}/recruitment/jobs"
    )
    assert fake_client.last_request["headers"]["X-User-Id"] == (
        "11111111-1111-1111-1111-111111111111"
    )
    assert fake_client.last_request["headers"]["X-Auth-Id"] == (
        "22222222-2222-2222-2222-222222222222"
    )
    assert fake_client.last_request["headers"]["X-User-Email"] == (
        "candidate@example.com"
    )
    assert fake_client.last_request["headers"]["X-User-Role"] == "candidate"


def test_ai_proxy_injects_user_headers(monkeypatch, client):
    fake_client = FakeAsyncClient(timeout=300.0)
    monkeypatch.setattr("app.main.httpx.AsyncClient", lambda timeout: fake_client)

    token = jwt.encode(
        {
            "sub": "11111111-1111-1111-1111-111111111111",
            "auth_id": "22222222-2222-2222-2222-222222222222",
            "email": "candidate@example.com",
            "role": "candidate",
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    response = client.post(
        "/api/ai/match",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "cv_id": "33333333-3333-3333-3333-333333333333",
            "job_id": "44444444-4444-4444-4444-444444444444",
        },
    )

    assert response.status_code == 200
    assert fake_client.last_request["url"] == f"{settings.AI_SERVICE_URL}/ai/match"
    assert fake_client.last_request["headers"]["X-User-Id"] == (
        "11111111-1111-1111-1111-111111111111"
    )
    assert fake_client.last_request["headers"]["X-Auth-Id"] == (
        "22222222-2222-2222-2222-222222222222"
    )
    assert fake_client.last_request["headers"]["X-User-Email"] == (
        "candidate@example.com"
    )
    assert fake_client.last_request["headers"]["X-User-Role"] == "candidate"
