"""
V3.1 Configuration Settings
Fashion & Lifestyle Frontier - Grok-Powered Agentic AI Platform
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # ============================================
    # APPLICATION SETTINGS
    # ============================================
    APP_NAME: str = "McLeuker Fashion AI"
    APP_VERSION: str = "3.1.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "*"
    
    # ============================================
    # LAYER 1: REASONING (Grok Unified Brain)
    # ============================================
    XAI_API_KEY: Optional[str] = None
    GROK_MODEL: str = "grok-beta"
    GROK_API_BASE: str = "https://api.x.ai/v1"
    
    # Fallback LLM (for specific edge cases)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 8192
    
    # ============================================
    # LAYER 2: PARALLEL SEARCH
    # ============================================
    GOOGLE_SEARCH_API_KEY: Optional[str] = None
    BING_API_KEY: Optional[str] = None
    PERPLEXITY_API_KEY: Optional[str] = None
    EXA_API_KEY: Optional[str] = None
    
    MAX_SEARCH_RESULTS: int = 10
    SEARCH_TIMEOUT: int = 30
    
    # ============================================
    # LAYER 3: ACTION (Web Automation)
    # ============================================
    BROWSERLESS_API_KEY: Optional[str] = None
    FIRECRAWL_API_KEY: Optional[str] = None
    BROWSERLESS_TIMEOUT: int = 60
    
    # ============================================
    # LAYER 4: ANALYST (Code Execution)
    # ============================================
    E2B_API_KEY: Optional[str] = None
    E2B_TIMEOUT: int = 120
    
    # ============================================
    # LAYER 5: OUTPUT (Image Generation)
    # ============================================
    NANO_BANANA_API_KEY: Optional[str] = None
    
    # ============================================
    # DATABASE - SUPABASE
    # ============================================
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    
    # ============================================
    # CREDIT SYSTEM
    # ============================================
    DEFAULT_USER_CREDITS: int = 100
    CREDIT_COST_REASONING: int = 1
    CREDIT_COST_SEARCH: int = 2
    CREDIT_COST_ACTION: int = 5
    CREDIT_COST_ANALYST: int = 5
    CREDIT_COST_IMAGE: int = 3
    
    # ============================================
    # DIRECTORIES
    # ============================================
    OUTPUT_DIR: str = "/tmp/outputs"
    TEMP_DIR: str = "/tmp/temp"
    
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
    
    # ============================================
    # LAYER STATUS CHECKS
    # ============================================
    def is_reasoning_configured(self) -> bool:
        """Check if Grok (core brain) is configured."""
        return bool(self.XAI_API_KEY)
    
    def is_search_configured(self) -> bool:
        """Check if at least one search provider is configured."""
        return any([
            self.GOOGLE_SEARCH_API_KEY,
            self.BING_API_KEY,
            self.PERPLEXITY_API_KEY,
            self.EXA_API_KEY
        ])
    
    def is_action_configured(self) -> bool:
        """Check if action layer is configured."""
        return bool(self.BROWSERLESS_API_KEY or self.FIRECRAWL_API_KEY)
    
    def is_analyst_configured(self) -> bool:
        """Check if analyst layer (E2B) is configured."""
        return bool(self.E2B_API_KEY)
    
    def is_image_configured(self) -> bool:
        """Check if image generation is configured."""
        return bool(self.NANO_BANANA_API_KEY)
    
    def is_database_configured(self) -> bool:
        """Check if Supabase is configured."""
        return bool(self.SUPABASE_URL and self.SUPABASE_KEY)
    
    def get_system_status(self) -> dict:
        """Get the status of all system layers."""
        return {
            "version": self.APP_VERSION,
            "layers": {
                "reasoning": self.is_reasoning_configured(),
                "search": self.is_search_configured(),
                "action": self.is_action_configured(),
                "analyst": self.is_analyst_configured(),
                "image": self.is_image_configured(),
            },
            "database": self.is_database_configured(),
        }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
