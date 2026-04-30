from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user_context
from app.schemas import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationStatusUpdate,
    CVResponse,
    CurrentUserContext,
    JobCreate,
    JobResponse,
    JobUpdate,
    MessageResponse,
)
from app.service import (
    apply_to_job,
    create_cv,
    create_job,
    delete_cv,
    get_job,
    get_job_applications,
    get_my_applications,
    get_my_jobs,
    list_cvs,
    list_jobs,
    update_application_status,
    update_job,
)

router = APIRouter(prefix = "/recruitment", tags=["Recruitment"])


@router.get("/jobs", response_model=list[JobResponse])
def list_public_jobs(
    status: str | None = None,
    location: str | None = None,
    job_type: str | None = None,
    db: Session = Depends(get_db),
):
    return list_jobs(db, status_filter=status, location=location, job_type=job_type)


@router.get("/jobs/my", response_model=list[JobResponse])
def list_my_jobs(
    current_user: CurrentUserContext = Depends(get_current_user_context),
    db: Session = Depends(get_db),
):
    return get_my_jobs(db, current_user)


@router.get("/jobs/{job_id}", response_model=JobResponse)
def read_job(job_id: UUID, db: Session = Depends(get_db)):
    return get_job(db, job_id)


@router.post("/jobs", response_model=JobResponse)
def create_new_job(
    payload: JobCreate,
    current_user: CurrentUserContext = Depends(get_current_user_context),
    db: Session = Depends(get_db),
):
    return create_job(db, current_user, payload)


@router.patch("/jobs/{job_id}", response_model=JobResponse)
def patch_job(
    job_id: UUID,
    payload: JobUpdate,
    current_user: CurrentUserContext = Depends(get_current_user_context),
    db: Session = Depends(get_db),
):
    return update_job(db, current_user, job_id, payload)


@router.get("/cvs", response_model=list[CVResponse])
def read_cvs(
    current_user: CurrentUserContext = Depends(get_current_user_context),
    db: Session = Depends(get_db),
):
    return list_cvs(db, current_user)


@router.post("/cvs/upload", response_model=CVResponse)
async def upload_cv(
    title: str = Form(...),
    file: UploadFile = File(...),
    current_user: CurrentUserContext = Depends(get_current_user_context),
    db: Session = Depends(get_db),
):
    return create_cv(db, current_user, title, file)


@router.delete("/cvs/{cv_id}", response_model=MessageResponse)
def remove_cv(
    cv_id: UUID,
    current_user: CurrentUserContext = Depends(get_current_user_context),
    db: Session = Depends(get_db),
):
    delete_cv(db, current_user, cv_id)
    return {"message": "CV deleted successfully"}


@router.post("/applications", response_model=ApplicationResponse)
def create_application(
    payload: ApplicationCreate,
    current_user: CurrentUserContext = Depends(get_current_user_context),
    db: Session = Depends(get_db),
):
    return apply_to_job(db, current_user, payload)


@router.get("/applications/me", response_model=list[ApplicationResponse])
def read_my_applications(
    current_user: CurrentUserContext = Depends(get_current_user_context),
    db: Session = Depends(get_db),
):
    return get_my_applications(db, current_user)


@router.get("/applications/job/{job_id}", response_model=list[ApplicationResponse])
def read_job_applications(
    job_id: UUID,
    current_user: CurrentUserContext = Depends(get_current_user_context),
    db: Session = Depends(get_db),
):
    return get_job_applications(db, current_user, job_id)


@router.patch("/applications/{application_id}/status", response_model=ApplicationResponse)
def change_application_status(
    application_id: UUID,
    payload: ApplicationStatusUpdate,
    current_user: CurrentUserContext = Depends(get_current_user_context),
    db: Session = Depends(get_db),
):
    return update_application_status(db, current_user, application_id, payload)
