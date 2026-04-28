from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    fastapi_env: str = "development"
    fastapi_port: int = 8000
    secret_key: str = "your-secret-key-change-this"
    jwt_secret: str = "your-jwt-secret-change-this"
    
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "stepone_ai"
    redis_url: str = "redis://localhost:6379/0"
    
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
