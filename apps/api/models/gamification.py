from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class GamificationProfile(Base):
    __tablename__ = "gamification_profiles"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    streak_days = Column(Integer, default=0)
    last_streak_at = Column(DateTime(timezone=True), nullable=True)
    
    # Statistics
    problems_solved = Column(Integer, default=0)
    total_submissions = Column(Integer, default=0)
    fastest_solve_sec = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    badges = relationship("UserBadge", back_populates="profile")


class Badge(Base):
    __tablename__ = "badges"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)  # e.g., "first_ac", "speed_demon"
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    criteria_json = Column(JSON, nullable=False)  # Criteria for earning
    icon_url = Column(String, nullable=True)
    rarity = Column(String, default="common")  # common, rare, epic, legendary
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user_badges = relationship("UserBadge", back_populates="badge")


class UserBadge(Base):
    __tablename__ = "user_badges"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    badge_id = Column(Integer, ForeignKey("badges.id"), primary_key=True)
    awarded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Context of earning
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=True)
    
    # Relationships
    user = relationship("User")
    badge = relationship("Badge", back_populates="user_badges")
    profile = relationship("GamificationProfile", back_populates="badges")