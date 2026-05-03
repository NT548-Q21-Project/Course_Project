from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

FitLevel = Literal["strong_fit", "fit", "weak_fit", "not_fit"]


class MessageResponse(BaseModel):
    message: str


class MatchAnalyzeRequest(BaseModel):
    cv_id: UUID
    job_id: UUID

    cv_text: str = Field(min_length=20)

    job_title: str = Field(min_length=2)
    job_description: str = Field(min_length=20)
    responsibilities: str | None = None
    requirements: str | None = None
    nice_to_have: str | None = None
    benefits: str | None = None


class MatchAnalyzeResult(BaseModel):
    fit_level: FitLevel
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    suggestions: str | None = None


class MatchResultCreate(BaseModel):
    candidate_id: UUID
    cv_id: UUID
    job_id: UUID
    fit_level: FitLevel
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    suggestions: str | None = None


class MatchResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    candidate_id: UUID
    cv_id: UUID
    job_id: UUID
    fit_level: FitLevel
    strengths: list[str] | None = None
    weaknesses: list[str] | None = None
    suggestions: str | None = None
    created_at: datetime


class MatchResultListResponse(BaseModel):
    results: list[MatchResultResponse]
