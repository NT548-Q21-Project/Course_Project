import asyncio

from app.schemas import MatchAnalyzeRequest
from app.services import match_service


def test_extract_json_from_plain_json():
    raw_text = """
    {
      "fit_level": "fit",
      "strengths": ["Python", "FastAPI"],
      "weaknesses": ["AWS is unclear"],
      "suggestions": "Add more cloud deployment experience."
    }
    """

    data = match_service._extract_json(raw_text)

    assert data["fit_level"] == "fit"
    assert data["strengths"] == ["Python", "FastAPI"]
    assert data["weaknesses"] == ["AWS is unclear"]


def test_extract_json_from_markdown_json_block():
    raw_text = """
    ```json
    {
      "fit_level": "strong_fit",
      "strengths": ["Python"],
      "weaknesses": [],
      "suggestions": "Good fit."
    }
    ```
    """

    data = match_service._extract_json(raw_text)

    assert data["fit_level"] == "strong_fit"
    assert data["strengths"] == ["Python"]


def test_analyze_match_returns_valid_result(monkeypatch, sample_match_payload):
    async def fake_call_llm(prompt: str) -> str:
        assert "Analyze the candidate CV" in prompt
        return """
        {
          "fit_level": "strong_fit",
          "strengths": ["Python", "FastAPI", "PostgreSQL"],
          "weaknesses": ["AWS experience is not clear"],
          "suggestions": "Highlight cloud deployment experience."
        }
        """

    monkeypatch.setattr(match_service, "call_llm", fake_call_llm)

    payload = MatchAnalyzeRequest(**sample_match_payload)
    result = asyncio.run(match_service.analyze_match(payload))

    assert result.fit_level == "strong_fit"
    assert "Python" in result.strengths
    assert "AWS experience is not clear" in result.weaknesses
