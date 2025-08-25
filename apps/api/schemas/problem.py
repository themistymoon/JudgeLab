from datetime import datetime

from pydantic import BaseModel, Field

from models.problem import AvailabilityPolicy, CheckerType, ProblemDifficulty


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
    tags: list[str] = []
    difficulty: ProblemDifficulty = ProblemDifficulty.EASY
    checker_type: CheckerType = CheckerType.DIFF


class ProblemCreate(ProblemBase):
    slug: str = Field(..., pattern=r"^[a-z0-9-]+$", max_length=100)
    time_limit_ms: int = Field(2000, gt=0, le=30000)
    memory_limit_mb: int = Field(256, gt=0, le=2048)
    output_limit_kb: int = Field(64, gt=0, le=1024)
    solve_time_limit_sec: int | None = Field(None, gt=0, le=7200)
    max_attempts: int | None = Field(None, gt=0, le=100)
    visible_from_at: datetime | None = None
    visible_until_at: datetime | None = None
    attempt_open_at: datetime | None = None
    attempt_close_at: datetime | None = None
    availability_policy: AvailabilityPolicy = AvailabilityPolicy.HARD_CLOSE


class ProblemUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    statement_md: str | None = Field(None, min_length=1)
    tags: list[str] | None = None
    difficulty: ProblemDifficulty | None = None
    checker_type: CheckerType | None = None
    time_limit_ms: int | None = Field(None, gt=0, le=30000)
    memory_limit_mb: int | None = Field(None, gt=0, le=2048)
    output_limit_kb: int | None = Field(None, gt=0, le=1024)
    solve_time_limit_sec: int | None = Field(None, gt=0, le=7200)
    max_attempts: int | None = Field(None, gt=0, le=100)
    visible_from_at: datetime | None = None
    visible_until_at: datetime | None = None
    attempt_open_at: datetime | None = None
    attempt_close_at: datetime | None = None
    availability_policy: AvailabilityPolicy | None = None


class ProblemResponse(ProblemBase):
    id: int
    slug: str
    time_limit_ms: int
    memory_limit_mb: int
    output_limit_kb: int
    solve_time_limit_sec: int | None
    max_attempts: int | None
    visible_from_at: datetime | None
    visible_until_at: datetime | None
    attempt_open_at: datetime | None
    attempt_close_at: datetime | None
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
    tags: list[str]
    difficulty: ProblemDifficulty
    created_at: datetime

    class Config:
        from_attributes = True
