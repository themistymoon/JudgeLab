from sqlalchemy import Column, String, Integer, Text
from core.database import Base


class PlatformSettings(Base):
    __tablename__ = "platform_settings"
    
    key = Column(String, primary_key=True)
    value = Column(Text, nullable=False)
    description = Column(String, nullable=True)
    
    # Common settings with defaults
    @classmethod
    def get_defaults(cls):
        return {
            "client_max_cache_size_mb": "100",
            "client_cache_ttl_sec": "3600",
            "client_max_cache_items": "1000",
            "server_api_cache_ttl_sec": "300",
            "artifact_retention_days": "30",
            "max_concurrent_submissions": "10",
            "judge_queue_timeout_sec": "300",
            "heartbeat_interval_sec": "10",
            "integrity_grace_period_sec": "30"
        }