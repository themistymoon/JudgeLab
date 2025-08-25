
from datetime import UTC

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.v1.endpoints.auth import get_current_user
from core.database import get_db
from models.attempt import Attempt, AttemptStatus
from models.submission import Submission, SubmissionVerdict
from models.user import User
from schemas.submission import SubmissionCreate, SubmissionResponse
from services.judge import submit_solution

router = APIRouter()


@router.post("", response_model=SubmissionResponse)
async def create_submission(
    submission_data: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a solution for judging."""
    # Get attempt
    attempt = db.query(Attempt).filter(Attempt.id == submission_data.attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    if attempt.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot submit for other users' attempts")

    if attempt.status != AttemptStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Attempt is not active")

    # Check if attempt has expired
    from datetime import datetime
    now = datetime.now(UTC)
    late_by_sec = 0

    if attempt.expires_at and now > attempt.expires_at:
        # Check availability policy
        problem = attempt.problem
        if problem.availability_policy.value == "hard_close":
            raise HTTPException(status_code=410, detail="Submission deadline passed")
        else:  # soft_grace
            late_by_sec = int((now - attempt.expires_at).total_seconds())

    # Create submission record
    submission = Submission(
        attempt_id=attempt.id,
        user_id=current_user.id,
        problem_id=attempt.problem_id,
        lang=submission_data.lang,
        source_ref="",  # Will be set by judge service
        verdict=SubmissionVerdict.PENDING
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    # Update attempt late time if applicable
    if late_by_sec > 0:
        attempt.late_by_sec = max(attempt.late_by_sec, late_by_sec)
        db.commit()

    # Queue for judging
    try:
        submit_solution.delay(submission.id, submission_data.source_code)
    except Exception:
        # If queue fails, mark as system error
        submission.verdict = SubmissionVerdict.RE
        db.commit()
        raise HTTPException(status_code=500, detail="Failed to queue submission for judging")

    return SubmissionResponse.model_validate(submission)


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a submission by ID."""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if submission.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot access other users' submissions")

    return SubmissionResponse.model_validate(submission)


@router.get("/attempt/{attempt_id}", response_model=list[SubmissionResponse])
async def get_attempt_submissions(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all submissions for an attempt."""
    attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    if attempt.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot access other users' attempts")

    submissions = db.query(Submission).filter(Submission.attempt_id == attempt_id).all()
    return [SubmissionResponse.model_validate(s) for s in submissions]


@router.get("/user/{user_id}", response_model=list[SubmissionResponse])
async def get_user_submissions(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get submissions for a user (own submissions only)."""
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot access other users' submissions")

    submissions = db.query(Submission).filter(Submission.user_id == user_id).all()
    return [SubmissionResponse.model_validate(s) for s in submissions]
