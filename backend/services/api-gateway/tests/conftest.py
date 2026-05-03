import os

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("IDENTITY_SERVICE_URL", "http://identity-service:8001")
os.environ.setdefault("RECRUITMENT_SERVICE_URL", "http://recruitment-service:8002")
os.environ.setdefault("AI_SERVICE_URL", "http://ai-service:8003")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
