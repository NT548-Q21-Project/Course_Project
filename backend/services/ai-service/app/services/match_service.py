import json
import re
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import MatchResult
from app.schemas import MatchAnalyzeRequest, MatchAnalyzeResult
from app.services.llm_client import call_llm


def _build_match_prompt(payload: MatchAnalyzeRequest) -> str:
    return f"""
Analyze the candidate CV against the job description.

Return ONLY valid JSON using exactly this schema:
{{
  "fit_level": "strong_fit | fit | weak_fit | not_fit",
  "strengths": ["strength 1", "strength 2"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "suggestions": "short practical suggestions for the candidate"
}}

Rules:
- fit_level must be one of: strong_fit, fit, weak_fit, not_fit.
- strong_fit: candidate clearly matches most important requirements.
- fit: candidate matches the role but may have some gaps.
- weak_fit: candidate has some relevant background but misses key requirements.
- not_fit: candidate is not suitable for this role.
- strengths must be based only on the CV.
- weaknesses must be based on gaps between CV and job.
- suggestions should be concise and actionable.
- Do not invent experience.
- Return JSON only. No markdown.

Candidate CV:
{payload.cv_text}

Job title:
{payload.job_title}

Job description:
{payload.job_description}

Responsibilities:
{payload.responsibilities or "Not provided"}

Requirements:
{payload.requirements or "Not provided"}

Nice to have:
{payload.nice_to_have or "Not provided"}

Benefits:
{payload.benefits or "Not provided"}
"""


def _extract_json(text: str) -> dict:
    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```json", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"^```", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if match is None:
            raise

        return json.loads(match.group(0))


async def analyze_match(payload: MatchAnalyzeRequest) -> MatchAnalyzeResult:
    prompt = _build_match_prompt(payload)
    raw_result = await call_llm(prompt)

    try:
        data = _extract_json(raw_result)
        return MatchAnalyzeResult(**data)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM returned invalid match result format",
        ) from err


async def analyze_and_save_match_result(
    *,
    db: Session,
    payload: MatchAnalyzeRequest,
    candidate_id: UUID,
) -> MatchResult:
    analyze_result = await analyze_match(payload)

    existing_match_result = (
        db.query(MatchResult)
        .filter(
            MatchResult.cv_id == payload.cv_id,
            MatchResult.job_id == payload.job_id,
        )
        .first()
    )

    if existing_match_result is not None:
        existing_match_result.candidate_id = candidate_id
        existing_match_result.fit_level = analyze_result.fit_level
        existing_match_result.strengths = analyze_result.strengths
        existing_match_result.weaknesses = analyze_result.weaknesses
        existing_match_result.suggestions = analyze_result.suggestions

        db.commit()
        db.refresh(existing_match_result)

        return existing_match_result

    match_result = MatchResult(
        candidate_id=candidate_id,
        cv_id=payload.cv_id,
        job_id=payload.job_id,
        fit_level=analyze_result.fit_level,
        strengths=analyze_result.strengths,
        weaknesses=analyze_result.weaknesses,
        suggestions=analyze_result.suggestions,
    )

    db.add(match_result)
    db.commit()
    db.refresh(match_result)

    return match_result


def list_my_match_results(
    *,
    db: Session,
    candidate_id: UUID,
) -> list[MatchResult]:
    return (
        db.query(MatchResult)
        .filter(MatchResult.candidate_id == candidate_id)
        .order_by(MatchResult.created_at.desc())
        .all()
    )


def get_match_result_by_id(
    *,
    db: Session,
    match_result_id: UUID,
) -> MatchResult | None:
    return db.query(MatchResult).filter(MatchResult.id == match_result_id).first()
