"""
V3.1 Search Layer
Parallel search across Google, Bing, Perplexity, Exa.ai, and Grok real-time.
"""

from src.layers.search.parallel_search import (
    ParallelSearchLayer,
    GoogleSearch,
    BingSearch,
    PerplexitySearch,
    ExaSearch,
    GrokRealTimeSearch,
    SearchResult,
    SearchResponse,
    parallel_search
)

__all__ = [
    "ParallelSearchLayer",
    "GoogleSearch",
    "BingSearch",
    "PerplexitySearch",
    "ExaSearch",
    "GrokRealTimeSearch",
    "SearchResult",
    "SearchResponse",
    "parallel_search"
]
