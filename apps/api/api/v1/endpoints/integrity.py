from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.v1.endpoints.auth import get_current_user
from core.config import settings
from core.database import get_db
from models.integrity import IntegrityEvent
from models.user import User
from schemas.integrity import IntegrityEventResponse, IntegrityHeartbeat, IntegrityStatusResponse

router = APIRouter()


@router.post("/heartbeat")
async def record_heartbeat(
    heartbeat: IntegrityHeartbeat,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record an integrity heartbeat from the lockdown agent."""

    # Create integrity event
    event = IntegrityEvent(
        session_id=heartbeat.session_id,
        user_id=current_user.id if current_user else None,
        ts=heartbeat.ts,
        ai_detected=1 if heartbeat.ai_detected else 0,
        multi_display=1 if heartbeat.multi_display else 0,
        clipboard_blocked=1 if heartbeat.blocked_events.get("clipboard", 0) > 0 else 0,
        screen_capture_blocked=1 if heartbeat.blocked_events.get("printscreen", 0) > 0 else 0,
        sources_json=str(heartbeat.sources) if heartbeat.sources else None,
        app_version=heartbeat.app_version
    )

    db.add(event)
    db.commit()

    # Determine status
    violations = []
    if heartbeat.ai_detected:
        violations.append("ai_tool_detected")
    if heartbeat.multi_display:
        violations.append("multiple_displays")
    if heartbeat.blocked_events.get("clipboard", 0) > 0:
        violations.append("clipboard_blocked")
    if heartbeat.blocked_events.get("printscreen", 0) > 0:
        violations.append("screen_capture_blocked")

    status = "flagged" if violations else "compliant"

    return {
        "status": status,
        "violations": violations,
        "server_time": datetime.utcnow(),
        "grace_period_sec": settings.INTEGRITY_GRACE_PERIOD_SECONDS
    }


@router.get("/status")
async def get_integrity_status(
    session_id: str,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> IntegrityStatusResponse:
    """Get the current integrity status for a session."""

    # Get the latest heartbeat for this session
    latest_event = db.query(IntegrityEvent).filter(
        IntegrityEvent.session_id == session_id
    ).order_by(IntegrityEvent.ts.desc()).first()

    if not latest_event:
        return IntegrityStatusResponse(
            session_id=session_id,
            user_id=current_user.id if current_user else None,
            status="disconnected",
            last_heartbeat=None,
            violations=[],
            grace_period_ends=None
        )

    # Check if session is recent (within grace period)
    now = datetime.utcnow()
    grace_cutoff = now - timedelta(seconds=settings.INTEGRITY_GRACE_PERIOD_SECONDS)

    if latest_event.ts < grace_cutoff:
        status = "disconnected"
    else:
        # Determine violations
        violations = []
        if latest_event.ai_detected:
            violations.append("ai_tool_detected")
        if latest_event.multi_display:
            violations.append("multiple_displays")
        if latest_event.clipboard_blocked:
            violations.append("clipboard_blocked")
        if latest_event.screen_capture_blocked:
            violations.append("screen_capture_blocked")

        status = "flagged" if violations else "compliant"

    return IntegrityStatusResponse(
        session_id=session_id,
        user_id=latest_event.user_id,
        status=status,
        last_heartbeat=latest_event.ts,
        violations=violations,
        grace_period_ends=latest_event.ts + timedelta(seconds=settings.INTEGRITY_GRACE_PERIOD_SECONDS)
    )


@router.get("/events/{session_id}")
async def get_session_events(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get integrity events for a session (admin only)."""
    from models.user import UserRole

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")

    events = db.query(IntegrityEvent).filter(
        IntegrityEvent.session_id == session_id
    ).order_by(IntegrityEvent.ts.desc()).limit(100).all()

    return [IntegrityEventResponse.model_validate(event) for event in events]
