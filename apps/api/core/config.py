from typing import List, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "JudgeLab"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # Security
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    CORS_ORIGINS: List[AnyHttpUrl] = []
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Judge settings
    WORKER_CONCURRENCY: int = 2
    ARTIFACT_RETENTION_DAYS: int = 30
    MAX_SUBMISSION_SIZE_KB: int = 64
    
    # Lockdown agent
    ALLOWED_DOMAINS: List[str] = []
    HEARTBEAT_INTERVAL_SECONDS: int = 10
    INTEGRITY_GRACE_PERIOD_SECONDS: int = 30
    
    # Problem settings
    DEFAULT_TIME_LIMIT_MS: int = 2000
    DEFAULT_MEMORY_LIMIT_MB: int = 256
    DEFAULT_OUTPUT_LIMIT_KB: int = 64
    MAX_TESTCASES: int = 100
    
    # Gamification
    BASE_XP_PER_PROBLEM: int = 100
    XP_MULTIPLIERS: dict = {
        "easy": 1.0,
        "medium": 1.5,
        "hard": 2.0,
        "expert": 3.0
    }
    STREAK_BONUS_MULTIPLIER: float = 0.1
    SPEED_BONUS_THRESHOLD: float = 0.7  # 70% time remaining
    CLUTCH_TIME_THRESHOLD: int = 30  # seconds
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod 
    def assemble_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @field_validator("ALLOWED_DOMAINS", mode="before")
    @classmethod
    def assemble_allowed_domains(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()