from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import MatchResult
from app.services import match_service


def test_match_endpoint_saves_result_to_database(
    integration_client: TestClient,
    db_session: Session,
    auth_headers: dict[str, str],
    sample_match_payload: dict,
    monkeypatch,
):
    async def fake_call_llm(prompt: str) -> str:
        return """
        {
          "fit_level": "strong_fit",
          "strengths": ["Python", "FastAPI", "PostgreSQL"],
          "weaknesses": ["AWS experience is not clearly shown"],
          "suggestions": "Add more detail about cloud deployment experience."
        }
        """

    monkeypatch.setattr(match_service, "call_llm", fake_call_llm)

    response = integration_client.post(
        "/ai/match",
        headers=auth_headers,
        json=sample_match_payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["fit_level"] == "strong_fit"
    assert data["candidate_id"] == auth_headers["X-User-Id"]
    assert data["strengths"] == ["Python", "FastAPI", "PostgreSQL"]

    saved_result = db_session.query(MatchResult).first()

    assert saved_result is not None
    assert str(saved_result.cv_id) == sample_match_payload["cv_id"]
    assert str(saved_result.job_id) == sample_match_payload["job_id"]
    assert saved_result.fit_level == "strong_fit"


def test_match_endpoint_updates_existing_result(
    integration_client: TestClient,
    db_session: Session,
    auth_headers: dict[str, str],
    sample_match_payload: dict,
    monkeypatch,
):
    call_count = {"value": 0}

    async def fake_call_llm(prompt: str) -> str:
        call_count["value"] += 1

        if call_count["value"] == 1:
            return """
            {
              "fit_level": "weak_fit",
              "strengths": ["Python"],
              "weaknesses": ["Missing FastAPI and PostgreSQL details"],
              "suggestions": "Improve backend project details."
            }
            """

        return """
        {
          "fit_level": "fit",
          "strengths": ["Python", "FastAPI"],
          "weaknesses": ["AWS experience is still unclear"],
          "suggestions": "Add cloud deployment examples."
        }
        """

    monkeypatch.setattr(match_service, "call_llm", fake_call_llm)

    first_response = integration_client.post(
        "/ai/match",
        headers=auth_headers,
        json=sample_match_payload,
    )

    second_response = integration_client.post(
        "/ai/match",
        headers=auth_headers,
        json=sample_match_payload,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert second_response.json()["fit_level"] == "fit"

    results = db_session.query(MatchResult).all()

    assert len(results) == 1
    assert results[0].fit_level == "fit"


def test_list_my_match_results(
    integration_client: TestClient,
    auth_headers: dict[str, str],
    sample_match_payload: dict,
    monkeypatch,
):
    async def fake_call_llm(prompt: str) -> str:
        return """
        {
          "fit_level": "fit",
          "strengths": ["Python", "Docker"],
          "weaknesses": ["CI/CD details are limited"],
          "suggestions": "Add CI/CD project examples."
        }
        """

    monkeypatch.setattr(match_service, "call_llm", fake_call_llm)

    create_response = integration_client.post(
        "/ai/match",
        headers=auth_headers,
        json=sample_match_payload,
    )

    assert create_response.status_code == 200

    list_response = integration_client.get(
        "/ai/match-results",
        headers=auth_headers,
    )

    assert list_response.status_code == 200

    data = list_response.json()

    assert len(data["results"]) == 1
    assert data["results"][0]["fit_level"] == "fit"
