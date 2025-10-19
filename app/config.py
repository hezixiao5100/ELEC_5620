"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External APIs
    STOCK_API_KEY: Optional[str] = Token
    NEWS_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: Optional[str] = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: Optional[float] = 0.7
    OPENAI_MAX_TOKENS: Optional[int] = 1000
    OPENAI_TOP_P: Optional[float] = 1.0
    OPENAI_FREQUENCY_PENALTY: Optional[float] = 0.0
    OPENAI_PRESENCE_PENALTY: Optional[float] = 0.0
    OPENAI_STOP: Optional[str] = None
    OPENAI_N: Optional[int] = 1
    # Application
    DEBUG: bool = False
    APP_NAME: str = "Stock Analysis System"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# TODO: Create global settings instance
# settings = Settings()


