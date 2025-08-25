from datetime import datetime

from pydantic import BaseModel, Field

from models.submission import SubmissionLanguage, SubmissionVerdict


class SubmissionCreate(BaseModel):
    attempt_id: int
    lang: SubmissionLanguage
    source_code: str = Field(..., min_length=1, max_length=65536)


class TestResult(BaseModel):
    test_id: int
    verdict: str
    time_ms: int | None = None
    memory_kb: int | None = None
    input_preview: str | None = None
    output_preview: str | None = None
    expected_preview: str | None = None


class SubmissionResponse(BaseModel):
    id: int
    attempt_id: int
    user_id: int
    problem_id: int
    lang: SubmissionLanguage
    verdict: SubmissionVerdict
    time_ms: int | None
    memory_kb: int | None
    compile_log: str | None
    first_failed_test: int | None
    test_results: list[TestResult] | None
    integrity_flagged: bool
    created_at: datetime
    judged_at: datetime | None

    class Config:
        from_attributes = True
