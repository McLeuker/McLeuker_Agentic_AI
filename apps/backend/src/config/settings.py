"""
McLeuker AI V7 - Configuration Settings
Centralized configuration management with environment variable support.

Supports:
- Grok (xAI) for reasoning
- Kimi K2.5 (Moonshot AI) for execution
- Multiple search providers
- Supabase for persistence
"""

import os
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class Settings:
    """Application settings loaded from environment variables."""
    
    # ==========================================================================
    # Core AI Models
    # ==========================================================================
    
    # Grok (xAI) - Primary Reasoning Model
    XAI_API_KEY: str = os.getenv("XAI_API_KEY", "")
    GROK_MODEL: str = os.getenv("GROK_MODEL", "grok-3-latest")
    GROK_API_BASE: str = os.getenv("GROK_API_BASE", "https://api.x.ai/v1")
    GROK_API_KEY: str = os.getenv("GROK_API_KEY", os.getenv("XAI_API_KEY", ""))
    
    # Kimi K2.5 (Moonshot AI) - Execution Model
    MOONSHOT_API_KEY: str = os.getenv("MOONSHOT_API_KEY", "")
    KIMI_MODEL: str = os.getenv("KIMI_MODEL", "kimi-k2.5")
    KIMI_API_BASE: str = os.getenv("KIMI_API_BASE", "https://api.moonshot.ai/v1")
    KIMI_THINKING_ENABLED: bool = os.getenv("KIMI_THINKING_ENABLED", "true").lower() == "true"
    KIMI_MAX_TOKENS: int = int(os.getenv("KIMI_MAX_TOKENS", "32768"))
    
    # OpenAI (Fallback)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    # Default LLM Provider
    DEFAULT_LLM_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "grok")
    
    # ==========================================================================
    # Search Providers
    # ==========================================================================
    
    PERPLEXITY_API_KEY: str = os.getenv("PERPLEXITY_API_KEY", "")
    EXA_API_KEY: str = os.getenv("EXA_API_KEY", "")
    GOOGLE_SEARCH_API_KEY: str = os.getenv("GOOGLE_SEARCH_API_KEY", "")
    GOOGLE_SEARCH_CX: str = os.getenv("GOOGLE_SEARCH_CX", "")
    BING_API_KEY: str = os.getenv("BING_API_KEY", "")
    
    # ==========================================================================
    # Action Layer
    # ==========================================================================
    
    BROWSERLESS_API_KEY: str = os.getenv("BROWSERLESS_API_KEY", "")
    FIRECRAWL_API_KEY: str = os.getenv("FIRECRAWL_API_KEY", "")
    
    # ==========================================================================
    # Output Layer
    # ==========================================================================
    
    NANO_BANANA_API_KEY: str = os.getenv("NANO_BANANA_API_KEY", "")
    
    # ==========================================================================
    # Database - Supabase
    # ==========================================================================
    
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # ==========================================================================
    # Server Configuration
    # ==========================================================================
    
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    # ==========================================================================
    # Timeouts and Limits
    # ==========================================================================
    
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "120"))
    SEARCH_TIMEOUT: int = int(os.getenv("SEARCH_TIMEOUT", "30"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "4096"))
    
    # ==========================================================================
    # V7 Multi-Model Settings
    # ==========================================================================
    
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "10"))
    MAX_CONVERSATION_HISTORY: int = int(os.getenv("MAX_CONVERSATION_HISTORY", "20"))
    ENABLE_STREAMING: bool = os.getenv("ENABLE_STREAMING", "true").lower() == "true"
    
    # Agent Orchestration
    MAX_TOOL_ITERATIONS: int = int(os.getenv("MAX_TOOL_ITERATIONS", "10"))
    MAX_PARALLEL_TASKS: int = int(os.getenv("MAX_PARALLEL_TASKS", "5"))
    ENABLE_MULTI_MODEL: bool = os.getenv("ENABLE_MULTI_MODEL", "true").lower() == "true"
    
    # Safety
    ENABLE_SAFETY_FILTERS: bool = os.getenv("ENABLE_SAFETY_FILTERS", "true").lower() == "true"
    ENABLE_OUTPUT_VALIDATION: bool = os.getenv("ENABLE_OUTPUT_VALIDATION", "true").lower() == "true"
    
    # ==========================================================================
    # Helper Methods
    # ==========================================================================
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    def is_grok_configured(self) -> bool:
        """Check if Grok API is configured."""
        return bool(self.XAI_API_KEY or self.GROK_API_KEY)
    
    def is_kimi_configured(self) -> bool:
        """Check if Kimi/Moonshot API is configured."""
        return bool(self.MOONSHOT_API_KEY)
    
    def is_search_configured(self) -> bool:
        """Check if any search provider is configured."""
        return bool(self.PERPLEXITY_API_KEY or self.EXA_API_KEY or self.GOOGLE_SEARCH_API_KEY)
    
    def is_supabase_configured(self) -> bool:
        """Check if Supabase is configured."""
        return bool(self.SUPABASE_URL and self.SUPABASE_KEY)
    
    def is_multi_model_ready(self) -> bool:
        """Check if multi-model architecture is ready."""
        return self.is_grok_configured() and self.is_kimi_configured()
    
    def get_available_models(self) -> dict:
        """Get dictionary of available models."""
        return {
            "grok": {
                "available": self.is_grok_configured(),
                "model": self.GROK_MODEL,
                "role": "reasoning"
            },
            "kimi": {
                "available": self.is_kimi_configured(),
                "model": self.KIMI_MODEL,
                "role": "execution"
            },
            "openai": {
                "available": bool(self.OPENAI_API_KEY),
                "model": self.OPENAI_MODEL,
                "role": "fallback"
            }
        }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings
