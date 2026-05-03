from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

JobType = Literal["full_time", "part_time", "internship"]
JobStatus = Literal["active", "closed"]
ApplicationStatus = Literal[
    "submitted",
    "rejected",
    "accepted",
]
UserRole = Literal["candidate", "recruiter"]


class CurrentUserContext(BaseModel):
    user_id: UUID
    auth_id: UUID
    email: EmailStr
    role: UserRole


class MessageResponse(BaseModel):
    message: str


class JobBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    responsibilities: str | None = None
    requirements: str | None = None
    nice_to_have: str | None = None
    benefits: str | None = None
    location: str | None = None
    job_type: JobType = "full_time"
    status: JobStatus = "active"
    expired_at: datetime | None = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)
    responsibilities: str | None = None
    requirements: str | None = None
    nice_to_have: str | None = None
    benefits: str | None = None
    location: str | None = None
    job_type: JobType | None = None
    status: JobStatus | None = None
    expired_at: datetime | None = None


class JobResponse(JobBase):
    id: UUID
    recruiter_id: UUID
    created_at: datetime
    applications_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class CVUploadRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class CVResponse(BaseModel):
    id: UUID
    user_id: UUID
    file_name: str
    title: str
    file_url: str | None = None
    content_type: str | None = None
    file_size: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationCreate(BaseModel):
    job_id: UUID
    cv_id: UUID


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


class ApplicationResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    job_id: UUID
    cv_id: UUID
    status: ApplicationStatus
    applied_at: datetime

    model_config = ConfigDict(from_attributes=True)
