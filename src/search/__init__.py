"""
McLeuker Agentic AI Platform - Search System

Real-time web search with multiple providers.
"""

from src.search.web_search import (
    SearchResult,
    SearchResponse,
    SearchProvider,
    PerplexitySearchProvider,
    GoogleSearchProvider,
    BingSearchProvider,
    FirecrawlProvider,
    MultiProviderSearch,
    get_search_system
)

__all__ = [
    "SearchResult",
    "SearchResponse",
    "SearchProvider",
    "PerplexitySearchProvider",
    "GoogleSearchProvider",
    "BingSearchProvider",
    "FirecrawlProvider",
    "MultiProviderSearch",
    "get_search_system"
]
