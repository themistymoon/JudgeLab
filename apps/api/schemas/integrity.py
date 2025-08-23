from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class IntegritySource(BaseModel):
    type: str  # "window", "process"  
    name: str
    title_hash: Optional[str] = None
    display_id: Optional[int] = None
    bounds: Optional[Dict[str, int]] = None
    is_foreground: bool = False


class IntegrityHeartbeat(BaseModel):
    session_id: str
    ts: datetime
    ai_detected: bool = False
    multi_display: bool = False
    blocked_events: Dict[str, int] = {"clipboard": 0, "printscreen": 0}
    sources: List[IntegritySource] = []
    app_version: str


class IntegrityEventResponse(BaseModel):
    id: int
    session_id: str
    user_id: Optional[int]
    ts: datetime
    ai_detected: bool
    multi_display: bool
    clipboard_blocked: bool
    screen_capture_blocked: bool
    app_version: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class IntegrityStatusResponse(BaseModel):
    session_id: str
    user_id: Optional[int]
    status: str  # "compliant", "flagged", "disconnected"
    last_heartbeat: Optional[datetime]
    violations: List[str] = []
    grace_period_ends: Optional[datetime] = None