"""
McLeuker AI V5 - Configuration Settings
Centralized configuration management with environment variable support.
"""

import os
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings loaded from environment variables."""
    
    # Core AI - Grok (XAI)
    XAI_API_KEY: str = os.getenv("XAI_API_KEY", "")
    GROK_MODEL: str = os.getenv("GROK_MODEL", "grok-4-fast-non-reasoning")
    GROK_API_BASE: str = os.getenv("GROK_API_BASE", "https://api.x.ai/v1")
    
    # Search Providers
    PERPLEXITY_API_KEY: str = os.getenv("PERPLEXITY_API_KEY", "")
    EXA_API_KEY: str = os.getenv("EXA_API_KEY", "")
    GOOGLE_SEARCH_API_KEY: str = os.getenv("GOOGLE_SEARCH_API_KEY", "")
    GOOGLE_SEARCH_CX: str = os.getenv("GOOGLE_SEARCH_CX", "")
    BING_API_KEY: str = os.getenv("BING_API_KEY", "")
    
    # Action Layer
    BROWSERLESS_API_KEY: str = os.getenv("BROWSERLESS_API_KEY", "")
    FIRECRAWL_API_KEY: str = os.getenv("FIRECRAWL_API_KEY", "")
    
    # Output Layer
    NANO_BANANA_API_KEY: str = os.getenv("NANO_BANANA_API_KEY", "")
    
    # Database - Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # Server Configuration
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    # Timeouts
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "120"))
    SEARCH_TIMEOUT: int = int(os.getenv("SEARCH_TIMEOUT", "30"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "4096"))
    
    # V5 Specific Settings
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "10"))
    MAX_CONVERSATION_HISTORY: int = int(os.getenv("MAX_CONVERSATION_HISTORY", "20"))
    ENABLE_STREAMING: bool = os.getenv("ENABLE_STREAMING", "true").lower() == "true"
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    def is_grok_configured(self) -> bool:
        """Check if Grok API is configured."""
        return bool(self.XAI_API_KEY)
    
    def is_search_configured(self) -> bool:
        """Check if any search provider is configured."""
        return bool(self.PERPLEXITY_API_KEY or self.EXA_API_KEY or self.GOOGLE_SEARCH_API_KEY)
    
    def is_supabase_configured(self) -> bool:
        """Check if Supabase is configured."""
        return bool(self.SUPABASE_URL and self.SUPABASE_KEY)


# Global settings instance
settings = Settings()
