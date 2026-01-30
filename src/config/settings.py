"""
McLeuker Agentic AI Platform - Configuration Settings

This module contains all configuration settings for the platform,
loaded from environment variables.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # ============================================
    # APPLICATION SETTINGS
    # ============================================
    
    APP_NAME: str = "McLeuker Agentic AI Platform"
    APP_VERSION: str = Field(default="1.0.0", alias="APP_VERSION")
    DEBUG: bool = Field(default=False, alias="DEBUG")
    HOST: str = Field(default="0.0.0.0", alias="HOST")
    PORT: int = Field(default=8000, alias="PORT")
    
    # CORS
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,https://mcleukerai.com,https://www.mcleukerai.com",
        alias="CORS_ORIGINS"
    )
    
    # ============================================
    # LLM PROVIDERS
    # ============================================
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview")
    
    # Grok (xAI)
    GROK_API_KEY: Optional[str] = Field(default=None)
    GROK_MODEL: str = Field(default="grok-2-latest")
    
    # Hugging Face
    HUGGINGFACE_API_KEY: Optional[str] = Field(default=None)
    
    # Perplexity AI
    PERPLEXITY_API_KEY: Optional[str] = Field(default=None)
    
    # DeepSeek
    DEEPSEEK_API_KEY: Optional[str] = Field(default=None)
    
    # Default LLM Provider
    DEFAULT_LLM_PROVIDER: str = Field(default="openai")
    
    # LLM Settings
    LLM_TEMPERATURE: float = Field(default=0.1)
    LLM_MAX_TOKENS: int = Field(default=4096)
    
    # ============================================
    # SEARCH & RESEARCH APIs
    # ============================================
    
    # Google Search
    GOOGLE_SEARCH_API_KEY: Optional[str] = Field(default=None)
    
    # Bing Search
    BING_API_KEY: Optional[str] = Field(default=None)
    
    # Firecrawl (Web Scraping)
    FIRECRAWL_API_KEY: Optional[str] = Field(default=None)
    
    # Serper (Google Search API)
    SERPER_API_KEY: Optional[str] = Field(default=None)
    
    # Tavily (AI Search)
    TAVILY_API_KEY: Optional[str] = Field(default=None)
    
    # Web Research Settings
    MAX_SEARCH_RESULTS: int = Field(default=10)
    SCRAPE_TIMEOUT: int = Field(default=30)
    
    # ============================================
    # AUTHENTICATION
    # ============================================
    
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None)
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(default=None)
    
    # Supabase
    SUPABASE_URL: Optional[str] = Field(default=None)
    SUPABASE_ANON_KEY: Optional[str] = Field(default=None)
    SUPABASE_SERVICE_KEY: Optional[str] = Field(default=None)
    SUPABASE_REDIRECT_URI: Optional[str] = Field(default=None)
    
    # ============================================
    # PAYMENTS (Stripe)
    # ============================================
    
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None)
    STRIPE_PUBLISHABLE_KEY: Optional[str] = Field(default=None)
    STRIPE_RESTRICTED_KEY: Optional[str] = Field(default=None)
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(default=None)
    
    # ============================================
    # MEDIA & VOICE
    # ============================================
    
    # ElevenLabs (Text-to-Speech)
    ELEVENLABS_API_KEY: Optional[str] = Field(default=None)
    
    # ============================================
    # DIRECTORIES
    # ============================================
    
    OUTPUT_DIR: str = Field(default="./outputs")
    TEMP_DIR: str = Field(default="./temp")
    
    # ============================================
    # DATABASE
    # ============================================
    
    DATABASE_URL: Optional[str] = Field(default=None)
    
    # ============================================
    # RATE LIMITING
    # ============================================
    
    RATE_LIMIT_REQUESTS: int = Field(default=100)
    RATE_LIMIT_PERIOD: int = Field(default=60)  # seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    def get_llm_config(self, provider: Optional[str] = None) -> dict:
        """Get configuration for the specified LLM provider."""
        provider = provider or self.DEFAULT_LLM_PROVIDER
        
        configs = {
            "openai": {
                "api_key": self.OPENAI_API_KEY,
                "model": self.OPENAI_MODEL,
                "base_url": "https://api.openai.com/v1",
            },
            "grok": {
                "api_key": self.GROK_API_KEY,
                "model": self.GROK_MODEL,
                "base_url": "https://api.x.ai/v1",
            },
            "perplexity": {
                "api_key": self.PERPLEXITY_API_KEY,
                "model": "llama-3.1-sonar-large-128k-online",
                "base_url": "https://api.perplexity.ai",
            },
            "huggingface": {
                "api_key": self.HUGGINGFACE_API_KEY,
                "model": "meta-llama/Meta-Llama-3-8B-Instruct",
                "base_url": "https://api-inference.huggingface.co/models",
            },
        }
        
        return configs.get(provider, configs["openai"])
    
    def get_search_config(self) -> dict:
        """Get configuration for search APIs."""
        return {
            "google": {
                "api_key": self.GOOGLE_SEARCH_API_KEY,
                "enabled": bool(self.GOOGLE_SEARCH_API_KEY),
            },
            "bing": {
                "api_key": self.BING_API_KEY,
                "enabled": bool(self.BING_API_KEY),
            },
            "firecrawl": {
                "api_key": self.FIRECRAWL_API_KEY,
                "enabled": bool(self.FIRECRAWL_API_KEY),
            },
            "serper": {
                "api_key": self.SERPER_API_KEY,
                "enabled": bool(self.SERPER_API_KEY),
            },
            "tavily": {
                "api_key": self.TAVILY_API_KEY,
                "enabled": bool(self.TAVILY_API_KEY),
            },
            "perplexity": {
                "api_key": self.PERPLEXITY_API_KEY,
                "enabled": bool(self.PERPLEXITY_API_KEY),
            },
        }
    
    def validate_required_keys(self) -> dict:
        """Validate that required API keys are present."""
        status = {
            "llm": {
                "openai": bool(self.OPENAI_API_KEY),
                "grok": bool(self.GROK_API_KEY),
                "perplexity": bool(self.PERPLEXITY_API_KEY),
                "huggingface": bool(self.HUGGINGFACE_API_KEY),
            },
            "search": {
                "google": bool(self.GOOGLE_SEARCH_API_KEY),
                "bing": bool(self.BING_API_KEY),
                "firecrawl": bool(self.FIRECRAWL_API_KEY),
            },
            "auth": {
                "google_oauth": bool(self.GOOGLE_CLIENT_ID and self.GOOGLE_CLIENT_SECRET),
            },
            "payments": {
                "stripe": bool(self.STRIPE_SECRET_KEY),
            },
            "media": {
                "elevenlabs": bool(self.ELEVENLABS_API_KEY),
            },
        }
        
        # Check if at least one LLM is configured
        status["has_llm"] = any(status["llm"].values())
        status["has_search"] = any(status["search"].values())
        
        return status


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
