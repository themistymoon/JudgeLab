from enum import Enum as PyEnum

from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


class SubmissionVerdict(PyEnum):
    PENDING = "pending"
    JUDGING = "judging"
    AC = "ac"  # Accepted
    WA = "wa"  # Wrong Answer
    TLE = "tle"  # Time Limit Exceeded
    MLE = "mle"  # Memory Limit Exceeded
    RE = "re"  # Runtime Error
    CE = "ce"  # Compilation Error
    OLE = "ole"  # Output Limit Exceeded


class SubmissionLanguage(PyEnum):
    PYTHON = "python"
    CPP = "cpp"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    GO = "go"
    RUST = "rust"


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("attempts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)

    lang = Column(Enum(SubmissionLanguage), nullable=False)
    source_ref = Column(String, nullable=False)  # Reference to stored source code

    # Judging results
    verdict = Column(Enum(SubmissionVerdict), default=SubmissionVerdict.PENDING)
    time_ms = Column(Integer, nullable=True)
    memory_kb = Column(Integer, nullable=True)

    # Additional judge data
    compile_log = Column(Text, nullable=True)
    first_failed_test = Column(Integer, nullable=True)
    test_results = Column(JSON, nullable=True)  # Per-test results

    # Integrity flags
    integrity_flagged = Column(Integer, default=0)  # Boolean as integer

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    judged_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User")
    problem = relationship("Problem", back_populates="submissions")
    attempt = relationship("Attempt", back_populates="submissions")
