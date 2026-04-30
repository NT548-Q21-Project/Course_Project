from __future__ import annotations

import io
from collections.abc import Iterable
from uuid import UUID

import cloudinary
import cloudinary.uploader
import fitz
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import CV, Application, Job
from app.schemas import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationStatusUpdate,
    CurrentUserContext,
    CVResponse,
    JobCreate,
    JobResponse,
    JobUpdate,
)

# configure cloudinary from env
if (
    settings.CLOUDINARY_CLOUD_NAME
    and settings.CLOUDINARY_API_KEY
    and settings.CLOUDINARY_API_SECRET
):
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
    )


def require_role(current_user: CurrentUserContext, allowed_roles: set[str]) -> None:
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )


def _attach_application_counts(db: Session, jobs: Iterable[Job]) -> list[JobResponse]:
    job_list = list(jobs)
    counts = dict(
        db.query(Application.job_id, func.count(Application.id))
        .filter(Application.job_id.in_([job.id for job in job_list]))
        .group_by(Application.job_id)
        .all()
    )

    responses: list[JobResponse] = []
    for job in job_list:
        job.applications_count = int(counts.get(job.id, 0))
        responses.append(JobResponse.model_validate(job))
    return responses


def list_jobs(
    db: Session,
    status_filter: str | None = None,
    location: str | None = None,
    job_type: str | None = None,
) -> list[JobResponse]:
    query = db.query(Job)

    if status_filter:
        query = query.filter(Job.status == status_filter)
    else:
        query = query.filter(Job.status == "active")

    if location:
        query = query.filter(Job.location == location)

    if job_type:
        query = query.filter(Job.job_type == job_type)

    jobs = query.order_by(Job.created_at.desc()).all()
    return _attach_application_counts(db, jobs)


def get_job(db: Session, job_id: UUID) -> JobResponse:
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )
    return _attach_application_counts(db, [job])[0]


def get_my_jobs(db: Session, current_user: CurrentUserContext) -> list[JobResponse]:
    require_role(current_user, {"recruiter"})
    jobs = (
        db.query(Job)
        .filter(Job.recruiter_id == current_user.user_id)
        .order_by(Job.created_at.desc())
        .all()
    )
    return _attach_application_counts(db, jobs)


def create_job(
    db: Session, current_user: CurrentUserContext, payload: JobCreate
) -> JobResponse:
    require_role(current_user, {"recruiter"})

    job = Job(
        recruiter_id=current_user.user_id,
        **payload.model_dump(),
    )

    db.add(job)
    db.commit()
    db.refresh(job)
    return _attach_application_counts(db, [job])[0]


def update_job(
    db: Session,
    current_user: CurrentUserContext,
    job_id: UUID,
    payload: JobUpdate,
) -> JobResponse:
    require_role(current_user, {"recruiter"})

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )
    if job.recruiter_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not your job"
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    return _attach_application_counts(db, [job])[0]


def create_cv(
    db: Session,
    current_user: CurrentUserContext,
    title: str,
    file: UploadFile,
) -> CVResponse:
    require_role(current_user, {"candidate"})
    # read bytes
    file_bytes = file.file.read()

    # try to extract basic info using PyMuPDF (fitz) when possible
    extracted_title = None
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            meta = doc.metadata or {}
            extracted_title = meta.get("title")
            _page_count = doc.page_count
            # optionally, pull some text from first page (not stored currently)
    except Exception:
        # non-PDF or extraction failed; ignore and continue
        extracted_title = None

    # upload to Cloudinary if configured, otherwise skip upload
    file_url = None
    try:
        if (
            settings.CLOUDINARY_CLOUD_NAME
            and settings.CLOUDINARY_API_KEY
            and settings.CLOUDINARY_API_SECRET
        ):
            # upload as raw so PDFs and docs are preserved
            res = cloudinary.uploader.upload(
                io.BytesIO(file_bytes),
                resource_type="raw",
                folder="cvs",
            )
            file_url = res.get("secure_url") or res.get("url")
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to upload CV: {err}",
        ) from err

    cv = CV(
        user_id=current_user.user_id,
        file_name=file.filename or title,
        title=title or extracted_title or (file.filename or "CV"),
        file_url=file_url,
        content_type=file.content_type,
        file_size=len(file_bytes),
    )

    db.add(cv)
    db.commit()
    db.refresh(cv)

    # optionally attach extracted metadata somewhere (not in DB schema currently)
    return CVResponse.model_validate(cv)


def list_cvs(db: Session, current_user: CurrentUserContext) -> list[CVResponse]:
    require_role(current_user, {"candidate"})
    cvs = (
        db.query(CV)
        .filter(CV.user_id == current_user.user_id)
        .order_by(CV.created_at.desc())
        .all()
    )
    return [CVResponse.model_validate(cv) for cv in cvs]


def delete_cv(db: Session, current_user: CurrentUserContext, cv_id: UUID) -> None:
    require_role(current_user, {"candidate"})
    cv = db.query(CV).filter(CV.id == cv_id).first()
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="CV not found"
        )
    if cv.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your CV")

    db.delete(cv)
    db.commit()


def apply_to_job(
    db: Session,
    current_user: CurrentUserContext,
    payload: ApplicationCreate,
) -> ApplicationResponse:
    require_role(current_user, {"candidate"})

    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    cv = db.query(CV).filter(CV.id == payload.cv_id).first()
    if not cv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="CV not found"
        )
    if cv.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your CV")

    application = Application(
        candidate_id=current_user.user_id,
        job_id=payload.job_id,
        cv_id=payload.cv_id,
        cover_letter=payload.cover_letter,
        status="submitted",
    )

    try:
        db.add(application)
        db.commit()
    except IntegrityError as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Application already exists",
        ) from err

    db.refresh(application)
    return ApplicationResponse.model_validate(application)


def get_my_applications(
    db: Session, current_user: CurrentUserContext
) -> list[ApplicationResponse]:
    require_role(current_user, {"candidate"})
    applications = (
        db.query(Application)
        .filter(Application.candidate_id == current_user.user_id)
        .order_by(Application.applied_at.desc())
        .all()
    )
    return [
        ApplicationResponse.model_validate(application) for application in applications
    ]


def get_job_applications(
    db: Session,
    current_user: CurrentUserContext,
    job_id: UUID,
) -> list[ApplicationResponse]:
    require_role(current_user, {"recruiter"})

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )
    if job.recruiter_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not your job"
        )

    applications = (
        db.query(Application)
        .filter(Application.job_id == job_id)
        .order_by(Application.applied_at.desc())
        .all()
    )
    return [
        ApplicationResponse.model_validate(application) for application in applications
    ]


def update_application_status(
    db: Session,
    current_user: CurrentUserContext,
    application_id: UUID,
    payload: ApplicationStatusUpdate,
) -> ApplicationResponse:
    require_role(current_user, {"recruiter"})

    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    job = db.query(Job).filter(Job.id == application.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )
    if job.recruiter_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not your job"
        )

    application.status = payload.status
    db.commit()
    db.refresh(application)
    return ApplicationResponse.model_validate(application)
