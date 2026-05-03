from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import CurrentUserContext, get_current_user_context
from app.schemas import (
    MatchAnalyzeRequest,
    MatchResultListResponse,
    MatchResultResponse,
)
from app.services.match_service import (
    analyze_and_save_match_result,
    get_match_result_by_id,
    list_my_match_results,
)

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/match", response_model=MatchResultResponse)
async def match_cv_with_job(
    payload: MatchAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUserContext = Depends(get_current_user_context),
):
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can analyze CV-job match",
        )

    return await analyze_and_save_match_result(
        db=db,
        payload=payload,
        candidate_id=current_user.user_id,
    )


@router.get("/match-results", response_model=MatchResultListResponse)
def get_my_match_results(
    db: Session = Depends(get_db),
    current_user: CurrentUserContext = Depends(get_current_user_context),
):
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can view their match results",
        )

    results = list_my_match_results(
        db=db,
        candidate_id=current_user.user_id,
    )

    return {
        "results": results,
    }


@router.get("/match-results/{match_result_id}", response_model=MatchResultResponse)
def get_match_result_detail(
    match_result_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUserContext = Depends(get_current_user_context),
):
    match_result = get_match_result_by_id(
        db=db,
        match_result_id=match_result_id,
    )

    if match_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match result not found",
        )

    if (
        current_user.role == "candidate"
        and match_result.candidate_id != current_user.user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this match result",
        )

    return match_result
