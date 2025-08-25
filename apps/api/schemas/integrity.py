from datetime import datetime

from pydantic import BaseModel


class IntegritySource(BaseModel):
    type: str  # "window", "process"
    name: str
    title_hash: str | None = None
    display_id: int | None = None
    bounds: dict[str, int] | None = None
    is_foreground: bool = False


class IntegrityHeartbeat(BaseModel):
    session_id: str
    ts: datetime
    ai_detected: bool = False
    multi_display: bool = False
    blocked_events: dict[str, int] = {"clipboard": 0, "printscreen": 0}
    sources: list[IntegritySource] = []
    app_version: str


class IntegrityEventResponse(BaseModel):
    id: int
    session_id: str
    user_id: int | None
    ts: datetime
    ai_detected: bool
    multi_display: bool
    clipboard_blocked: bool
    screen_capture_blocked: bool
    app_version: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class IntegrityStatusResponse(BaseModel):
    session_id: str
    user_id: int | None
    status: str  # "compliant", "flagged", "disconnected"
    last_heartbeat: datetime | None
    violations: list[str] = []
    grace_period_ends: datetime | None = None
