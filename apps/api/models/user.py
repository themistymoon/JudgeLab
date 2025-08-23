from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from core.database import Base


class UserRole(PyEnum):
    STUDENT = "student"
    AUTHOR = "author" 
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_active = Column(Integer, default=1)  # Using integer for SQLite compatibility
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())