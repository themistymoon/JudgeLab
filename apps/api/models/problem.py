from enum import Enum as PyEnum

from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


class ProblemDifficulty(PyEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class ProblemStatus(PyEnum):
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CheckerType(PyEnum):
    DIFF = "diff"
    TOKEN = "token"
    FLOAT_EPS = "float_eps"
    CUSTOM = "custom"


class AvailabilityPolicy(PyEnum):
    HARD_CLOSE = "hard_close"
    SOFT_GRACE = "soft_grace"


class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    statement_md = Column(Text, nullable=False)
    tags = Column(JSON, default=[])
    difficulty = Column(Enum(ProblemDifficulty), default=ProblemDifficulty.EASY)
    checker_type = Column(Enum(CheckerType), default=CheckerType.DIFF)

    # Resource limits
    time_limit_ms = Column(Integer, default=2000)
    memory_limit_mb = Column(Integer, default=256)
    output_limit_kb = Column(Integer, default=64)

    # Time controls
    solve_time_limit_sec = Column(Integer, nullable=True)  # Per-attempt time limit
    max_attempts = Column(Integer, nullable=True)

    # Availability windows
    visible_from_at = Column(DateTime(timezone=True), nullable=True)
    visible_until_at = Column(DateTime(timezone=True), nullable=True)
    attempt_open_at = Column(DateTime(timezone=True), nullable=True)
    attempt_close_at = Column(DateTime(timezone=True), nullable=True)
    availability_policy = Column(Enum(AvailabilityPolicy), default=AvailabilityPolicy.HARD_CLOSE)

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    version = Column(Integer, default=1)
    status = Column(Enum(ProblemStatus), default=ProblemStatus.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    testcases = relationship("TestCase", back_populates="problem", cascade="all, delete-orphan")
    attempts = relationship("Attempt", back_populates="problem")
    submissions = relationship("Submission", back_populates="problem")


class TestCase(Base):
    __tablename__ = "testcases"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    group = Column(String, default="main")  # For test groups
    idx = Column(Integer, nullable=False)  # Order within group
    input_blob = Column(Text, nullable=False)
    output_blob = Column(Text, nullable=False)
    points = Column(Integer, default=1)
    is_sample = Column(Integer, default=0)  # Boolean as integer
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    problem = relationship("Problem", back_populates="testcases")
