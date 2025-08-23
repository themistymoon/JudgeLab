"""
Minimal model definitions for the worker.
These should be kept in sync with the main API models.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

Base = declarative_base()


class SubmissionVerdict(PyEnum):
    PENDING = "pending"
    JUDGING = "judging"
    AC = "ac"
    WA = "wa"
    TLE = "tle"
    MLE = "mle"
    RE = "re"
    CE = "ce"
    OLE = "ole"


class SubmissionLanguage(PyEnum):
    PYTHON = "python"
    CPP = "cpp"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    GO = "go"
    RUST = "rust"


class CheckerType(PyEnum):
    DIFF = "diff"
    TOKEN = "token"
    FLOAT_EPS = "float_eps"
    CUSTOM = "custom"


class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    problem_id = Column(Integer, nullable=False)
    
    lang = Column(Enum(SubmissionLanguage), nullable=False)
    source_ref = Column(String, nullable=False)
    
    verdict = Column(Enum(SubmissionVerdict), nullable=True)
    time_ms = Column(Integer, nullable=True)
    memory_kb = Column(Integer, nullable=True)
    
    compile_log = Column(Text, nullable=True)
    first_failed_test = Column(Integer, nullable=True)
    test_results = Column(JSON, nullable=True)
    
    integrity_flagged = Column(Integer, default=0)
    
    created_at = Column(DateTime, nullable=True)
    judged_at = Column(DateTime, nullable=True)


class Problem(Base):
    __tablename__ = "problems"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, nullable=False)
    title = Column(String, nullable=False)
    
    checker_type = Column(Enum(CheckerType), nullable=True)
    time_limit_ms = Column(Integer, nullable=True)
    memory_limit_mb = Column(Integer, nullable=True)
    output_limit_kb = Column(Integer, nullable=True)


class TestCase(Base):
    __tablename__ = "testcases"
    
    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    group = Column(String, nullable=True)
    idx = Column(Integer, nullable=False)
    input_blob = Column(Text, nullable=False)
    output_blob = Column(Text, nullable=False)
    points = Column(Integer, nullable=True)
    is_sample = Column(Integer, nullable=True)