"""
McLeuker Agentic AI Platform - Configuration Settings
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Settings
    APP_NAME: str = "McLeuker Agentic AI Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False)
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    GROK_API_KEY: Optional[str] = Field(default=None)
    SERPER_API_KEY: Optional[str] = Field(default=None)  # For web search
    TAVILY_API_KEY: Optional[str] = Field(default=None)  # Alternative search
    
    # LLM Settings
    DEFAULT_LLM_PROVIDER: str = Field(default="openai")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview")
    GROK_MODEL: str = Field(default="grok-2-latest")
    LLM_TEMPERATURE: float = Field(default=0.1)
    LLM_MAX_TOKENS: int = Field(default=4096)
    
    # Database Settings (for future use)
    DATABASE_URL: Optional[str] = Field(default=None)
    
    # Supabase Settings
    SUPABASE_URL: Optional[str] = Field(default=None)
    SUPABASE_ANON_KEY: Optional[str] = Field(default=None)
    SUPABASE_SERVICE_KEY: Optional[str] = Field(default=None)
    
    # File Storage
    OUTPUT_DIR: str = Field(default="./outputs")
    TEMP_DIR: str = Field(default="./temp")
    
    # Web Research Settings
    MAX_SEARCH_RESULTS: int = Field(default=10)
    SCRAPE_TIMEOUT: int = Field(default=30)
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100)
    RATE_LIMIT_PERIOD: int = Field(default=60)  # seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
