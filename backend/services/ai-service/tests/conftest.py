import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

os.environ.setdefault("APP_NAME", "AIMatch AI Service")
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5433/aimatch_test_db",
)
os.environ.setdefault("LLM_BASE_URL", "https://example.com/v1")
os.environ.setdefault("LLM_API_KEY", "test-key")
os.environ.setdefault("LLM_MODEL", "test-model")
os.environ.setdefault("LLM_TIMEOUT_SECONDS", "10")

from app.db.session import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import MatchResult  # noqa: F401, E402


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides.clear()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {
        "X-User-Id": "11111111-1111-1111-1111-111111111111",
        "X-Auth-Id": "22222222-2222-2222-2222-222222222222",
        "X-User-Email": "candidate@gmail.com",
        "X-User-Role": "candidate",
    }


@pytest.fixture
def recruiter_headers() -> dict[str, str]:
    return {
        "X-User-Id": "11111111-1111-1111-1111-111111111111",
        "X-Auth-Id": "22222222-2222-2222-2222-222222222222",
        "X-User-Email": "recruiter@gmail.com",
        "X-User-Role": "recruiter",
    }


@pytest.fixture
def sample_match_payload() -> dict:
    return {
        "cv_id": "33333333-3333-3333-3333-333333333333",
        "job_id": "44444444-4444-4444-4444-444444444444",
        "cv_text": (
            "I am a backend developer with Python, FastAPI, PostgreSQL, "
            "Docker, REST API development, JWT authentication, and CI/CD."
        ),
        "job_title": "Backend Engineer",
        "job_description": (
            "We need a backend engineer to build REST APIs using FastAPI, "
            "PostgreSQL, Docker, and CI/CD pipelines."
        ),
        "responsibilities": "Build APIs; write tests; integrate services",
        "requirements": "Python; FastAPI; PostgreSQL; Docker; CI/CD; JWT",
        "nice_to_have": "AWS; machine learning",
        "benefits": "Remote work",
    }


@pytest.fixture
def fake_db_dependency():
    def override_get_db():
        yield None

    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    test_database_url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5433/aimatch_test_db",
    )

    engine = create_engine(test_database_url, pool_pre_ping=True)

    try:
        with engine.begin() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS ai_service"))
    except OperationalError as err:
        pytest.skip(f"Test database is not available: {err}")

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
    )

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def integration_client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
