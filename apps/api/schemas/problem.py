from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from models.problem import ProblemDifficulty, CheckerType, AvailabilityPolicy


class TestCaseCreate(BaseModel):
    group: str = "main"
    idx: int
    input_blob: str
    output_blob: str
    points: int = 1
    is_sample: bool = False


class TestCaseResponse(TestCaseCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProblemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    statement_md: str = Field(..., min_length=1)
    tags: List[str] = []
    difficulty: ProblemDifficulty = ProblemDifficulty.EASY
    checker_type: CheckerType = CheckerType.DIFF


class ProblemCreate(ProblemBase):
    slug: str = Field(..., pattern=r"^[a-z0-9-]+$", max_length=100)
    time_limit_ms: int = Field(2000, gt=0, le=30000)
    memory_limit_mb: int = Field(256, gt=0, le=2048)
    output_limit_kb: int = Field(64, gt=0, le=1024)
    solve_time_limit_sec: Optional[int] = Field(None, gt=0, le=7200)
    max_attempts: Optional[int] = Field(None, gt=0, le=100)
    visible_from_at: Optional[datetime] = None
    visible_until_at: Optional[datetime] = None
    attempt_open_at: Optional[datetime] = None
    attempt_close_at: Optional[datetime] = None
    availability_policy: AvailabilityPolicy = AvailabilityPolicy.HARD_CLOSE


class ProblemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    statement_md: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = None
    difficulty: Optional[ProblemDifficulty] = None
    checker_type: Optional[CheckerType] = None
    time_limit_ms: Optional[int] = Field(None, gt=0, le=30000)
    memory_limit_mb: Optional[int] = Field(None, gt=0, le=2048)
    output_limit_kb: Optional[int] = Field(None, gt=0, le=1024)
    solve_time_limit_sec: Optional[int] = Field(None, gt=0, le=7200)
    max_attempts: Optional[int] = Field(None, gt=0, le=100)
    visible_from_at: Optional[datetime] = None
    visible_until_at: Optional[datetime] = None
    attempt_open_at: Optional[datetime] = None
    attempt_close_at: Optional[datetime] = None
    availability_policy: Optional[AvailabilityPolicy] = None


class ProblemResponse(ProblemBase):
    id: int
    slug: str
    time_limit_ms: int
    memory_limit_mb: int
    output_limit_kb: int
    solve_time_limit_sec: Optional[int]
    max_attempts: Optional[int]
    visible_from_at: Optional[datetime]
    visible_until_at: Optional[datetime] 
    attempt_open_at: Optional[datetime]
    attempt_close_at: Optional[datetime]
    availability_policy: AvailabilityPolicy
    created_by: int
    version: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProblemListResponse(BaseModel):
    id: int
    slug: str
    title: str
    tags: List[str]
    difficulty: ProblemDifficulty
    created_at: datetime
    
    class Config:
        from_attributes = True