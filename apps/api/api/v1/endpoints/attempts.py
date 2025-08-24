from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.v1.endpoints.auth import get_current_user
from core.database import get_db
from models.attempt import Attempt, AttemptStatus
from models.problem import Problem, ProblemStatus
from models.user import User
from schemas.attempt import AttemptCreate, AttemptHeartbeat, AttemptResponse

router = APIRouter()


@router.post("", response_model=AttemptResponse)
async def start_attempt(
    attempt_data: AttemptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new attempt on a problem."""
    # Get problem
    problem = db.query(Problem).filter(Problem.id == attempt_data.problem_id).first()
    if not problem or problem.status != ProblemStatus.PUBLISHED:
        raise HTTPException(status_code=404, detail="Problem not found")

    # Check availability windows
    now = datetime.utcnow()
    if problem.attempt_open_at and now < problem.attempt_open_at:
        raise HTTPException(status_code=403, detail="Attempt window not yet open")
    if problem.attempt_close_at and now > problem.attempt_close_at:
        raise HTTPException(status_code=403, detail="Attempt window closed")

    # Check max attempts
    if problem.max_attempts:
        existing_attempts = db.query(Attempt).filter(
            Attempt.user_id == current_user.id,
            Attempt.problem_id == problem.id
        ).count()
        if existing_attempts >= problem.max_attempts:
            raise HTTPException(status_code=403, detail="Maximum attempts exceeded")

    # Check for active attempt
    active_attempt = db.query(Attempt).filter(
        Attempt.user_id == current_user.id,
        Attempt.problem_id == problem.id,
        Attempt.status == AttemptStatus.ACTIVE
    ).first()

    if active_attempt:
        return AttemptResponse.model_validate(active_attempt)

    # Create new attempt
    expires_at = None
    if problem.solve_time_limit_sec:
        expires_at = now + timedelta(seconds=problem.solve_time_limit_sec)

    attempt = Attempt(
        user_id=current_user.id,
        problem_id=problem.id,
        expires_at=expires_at
    )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return AttemptResponse.model_validate(attempt)


@router.get("/{attempt_id}", response_model=AttemptResponse)
async def get_attempt(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get an attempt by ID."""
    attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    if attempt.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot access other users' attempts")

    return AttemptResponse.model_validate(attempt)


@router.post("/{attempt_id}/heartbeat")
async def send_heartbeat(
    attempt_id: int,
    heartbeat_data: AttemptHeartbeat,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a heartbeat for an active attempt."""
    attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    if attempt.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot access other users' attempts")

    if attempt.status != AttemptStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Attempt is not active")

    # Check if attempt has expired
    now = datetime.utcnow()
    if attempt.expires_at and now > attempt.expires_at:
        attempt.status = AttemptStatus.EXPIRED
        db.commit()
        raise HTTPException(status_code=410, detail="Attempt has expired")

    # TODO: Process integrity data if provided
    # For now, just acknowledge the heartbeat

    return {"status": "ok", "server_time": now}


@router.get("/user/{user_id}", response_model=list[AttemptResponse])
async def get_user_attempts(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get attempts for a user (own attempts only)."""
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot access other users' attempts")

    attempts = db.query(Attempt).filter(Attempt.user_id == user_id).all()
    return [AttemptResponse.model_validate(a) for a in attempts]
