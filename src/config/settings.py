"""
McLeuker Agentic AI Platform - Configuration Settings
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
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS - Using a simple string, we will split it safely in a property
    CORS_ORIGINS: str = "*"
    
    # ============================================
    # LLM PROVIDERS
    # ============================================
    
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    
    GROK_API_KEY: Optional[str] = None
    GROK_MODEL: str = "grok-2-latest"
    GROK_API_BASE: str = "https://api.x.ai/v1"
    
    HUGGINGFACE_API_KEY: Optional[str] = None
    PERPLEXITY_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    
    DEFAULT_LLM_PROVIDER: str = "openai"
    
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 4096
    
    # ============================================
    # SEARCH & RESEARCH APIs
    # ============================================
    
    GOOGLE_SEARCH_API_KEY: Optional[str] = None
    BING_API_KEY: Optional[str] = None
    FIRECRAWL_API_KEY: Optional[str] = None
    SERPER_API_KEY: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None
    
    MAX_SEARCH_RESULTS: int = 10
    SCRAPE_TIMEOUT: int = 30
    
    # ============================================
    # AUTHENTICATION & SUPABASE
    # ============================================
    
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    SUPABASE_REDIRECT_URI: Optional[str] = None
    
    # ============================================
    # PAYMENTS (Stripe)
    # ============================================
    
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_RESTRICTED_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # ============================================
    # MEDIA & VOICE
    # ============================================
    
    ELEVENLABS_API_KEY: Optional[str] = None
    
    # ============================================
    # DIRECTORIES
    # ============================================
    
    OUTPUT_DIR: str = "./outputs"
    TEMP_DIR: str = "./temp"
    
    # ============================================
    # DATABASE
    # ============================================
    
    DATABASE_URL: Optional[str] = None
    
    # ============================================
    # RATE LIMITING
    # ============================================
    
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Safely parse CORS origins."""
        try:
            val = os.getenv("CORS_ORIGINS", "*")
            if not val:
                return ["*"]
            return [origin.strip() for origin in val.split(",")]
        except Exception:
            return ["*"]
    
    def get_llm_config(self, provider: Optional[str] = None) -> dict:
        """Get configuration for the specified LLM provider."""
        provider = provider or self.DEFAULT_LLM_PROVIDER
        
        configs = {
            "openai": {
                "api_key": self.OPENAI_API_KEY,
                "model": self.OPENAI_MODEL,
                "base_url": self.OPENAI_API_BASE,
            },
            "grok": {
                "api_key": self.GROK_API_KEY,
                "model": self.GROK_MODEL,
                "base_url": self.GROK_API_BASE,
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
        return {
            "has_llm": bool(self.OPENAI_API_KEY or self.GROK_API_KEY),
            "has_search": bool(self.GOOGLE_SEARCH_API_KEY or self.FIRECRAWL_API_KEY or self.PERPLEXITY_API_KEY),
            "has_perplexity": bool(self.PERPLEXITY_API_KEY)
        }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
