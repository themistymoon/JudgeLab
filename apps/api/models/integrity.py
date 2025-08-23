from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class IntegrityEvent(Base):
    __tablename__ = "integrity_events"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    ts = Column(DateTime(timezone=True), server_default=func.now())
    
    # Detection flags
    ai_detected = Column(Integer, default=0)  # Boolean as integer
    multi_display = Column(Integer, default=0)
    clipboard_blocked = Column(Integer, default=0)
    screen_capture_blocked = Column(Integer, default=0)
    
    # Additional data
    sources_json = Column(Text, nullable=True)  # JSON array of detected sources
    app_version = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")