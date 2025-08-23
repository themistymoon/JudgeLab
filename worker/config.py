import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379"
    
    # Judge settings
    JUDGE_WORK_DIR: str = "/judge_work"
    ARTIFACT_RETENTION_DAYS: int = 30
    MAX_CONCURRENT_JOBS: int = 2
    DOCKER_TIMEOUT_SEC: int = 60
    
    # Language configurations
    PYTHON_IMAGE: str = "python:3.12-slim"
    CPP_IMAGE: str = "gcc:13"
    
    # Resource limits (per container)
    DEFAULT_TIME_LIMIT_MS: int = 2000
    DEFAULT_MEMORY_LIMIT_MB: int = 256
    DEFAULT_OUTPUT_LIMIT_KB: int = 64
    
    # Security settings
    ENABLE_NETWORK: bool = False
    ENABLE_SECCOMP: bool = True
    ENABLE_APPARMOR: bool = True
    
    class Config:
        env_file = ".env"


settings = Settings()