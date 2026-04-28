from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Backend
    fastapi_env: str = "development"
    fastapi_port: int = 8000
    secret_key: str = "your-secret-key-change-this"
    jwt_secret: str = "your-jwt-secret-change-this"
    
    # Database
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "stepone_ai"
    redis_url: str = "redis://localhost:6379/0"
    
    # AWS/S3
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    s3_bucket: str = "stepone-media"
    s3_bucket_cdn: str = "stepone-media-cdn"
    
    # AI APIs
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
