from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID

from fastapi.testclient import TestClient

import app.router as ai_router


def test_match_missing_gateway_headers_returns_401(
    client: TestClient,
    sample_match_payload: dict,
):
    response = client.post("/ai/match", json=sample_match_payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing gateway authentication headers"


def test_match_recruiter_role_returns_403(
    client: TestClient,
    recruiter_headers: dict[str, str],
    sample_match_payload: dict,
    fake_db_dependency,
):
    response = client.post(
        "/ai/match",
        headers=recruiter_headers,
        json=sample_match_payload,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Only candidates can analyze CV-job match"


def test_match_candidate_success_with_mocked_service(
    client: TestClient,
    auth_headers: dict[str, str],
    sample_match_payload: dict,
    fake_db_dependency,
    monkeypatch,
):
    async def fake_analyze_and_save_match_result(*, db, payload, candidate_id):
        return SimpleNamespace(
            id=UUID("55555555-5555-5555-5555-555555555555"),
            candidate_id=candidate_id,
            cv_id=payload.cv_id,
            job_id=payload.job_id,
            fit_level="strong_fit",
            strengths=["Python", "FastAPI"],
            weaknesses=["AWS is unclear"],
            suggestions="Highlight cloud deployment experience.",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

    monkeypatch.setattr(
        ai_router,
        "analyze_and_save_match_result",
        fake_analyze_and_save_match_result,
    )

    response = client.post(
        "/ai/match",
        headers=auth_headers,
        json=sample_match_payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["fit_level"] == "strong_fit"
    assert data["candidate_id"] == auth_headers["X-User-Id"]
    assert data["cv_id"] == sample_match_payload["cv_id"]
    assert data["job_id"] == sample_match_payload["job_id"]
    assert data["strengths"] == ["Python", "FastAPI"]
