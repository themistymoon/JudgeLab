from datetime import datetime

from pydantic import BaseModel

from models.attempt import AttemptStatus


class AttemptCreate(BaseModel):
    problem_id: int


class AttemptResponse(BaseModel):
    id: int
    user_id: int
    problem_id: int
    started_at: datetime
    expires_at: datetime | None
    status: AttemptStatus
    late_by_sec: int

    class Config:
        from_attributes = True


class AttemptHeartbeat(BaseModel):
    attempt_id: int
    editor_activity: bool = False
    integrity_data: dict | None = None
