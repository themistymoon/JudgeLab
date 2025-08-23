from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from models.submission import SubmissionVerdict, SubmissionLanguage


class SubmissionCreate(BaseModel):
    attempt_id: int
    lang: SubmissionLanguage
    source_code: str = Field(..., min_length=1, max_length=65536)


class TestResult(BaseModel):
    test_id: int
    verdict: str
    time_ms: Optional[int] = None
    memory_kb: Optional[int] = None
    input_preview: Optional[str] = None
    output_preview: Optional[str] = None
    expected_preview: Optional[str] = None


class SubmissionResponse(BaseModel):
    id: int
    attempt_id: int
    user_id: int
    problem_id: int
    lang: SubmissionLanguage
    verdict: SubmissionVerdict
    time_ms: Optional[int]
    memory_kb: Optional[int]
    compile_log: Optional[str]
    first_failed_test: Optional[int]
    test_results: Optional[List[TestResult]]
    integrity_flagged: bool
    created_at: datetime
    judged_at: Optional[datetime]
    
    class Config:
        from_attributes = True