from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str = "mysql://root:password@localhost:3306/stock_analysis"
    
    # JWT Configuration
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External APIs
    STOCK_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: Optional[str] = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: Optional[float] = 0.7
    OPENAI_MAX_TOKENS: Optional[int] = 1000
    OPENAI_TOP_P: Optional[float] = 1.0
    OPENAI_FREQUENCY_PENALTY: Optional[float] = 0.0
    OPENAI_PRESENCE_PENALTY: Optional[float] = 0.0
    OPENAI_STOP: Optional[str] = None
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Application Configuration
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance - automatically loads from .env file
settings = Settings()