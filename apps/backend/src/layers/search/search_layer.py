"""
McLeuker AI V5 - Search Layer
Parallel search across multiple providers with intelligent result aggregation.

Supported Providers:
- Perplexity AI (primary for fashion/beauty)
- Exa.ai (semantic search)
- Google Custom Search
- Bing Web Search
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from src.config.settings import settings


@dataclass
class SearchResult:
    """A single search result."""
    title: str
    url: str
    snippet: str
    source: str
    score: float = 1.0
    published_date: Optional[str] = None


@dataclass
class SearchResponse:
    """Response from the search layer."""
    success: bool
    results: List[SearchResult]
    query: str
    providers_used: List[str]
    error: Optional[str] = None


class SearchLayer:
    """
    Unified search layer that queries multiple providers in parallel.
    Implements intelligent result deduplication and ranking.
    """
    
    def __init__(self):
        self.timeout = settings.SEARCH_TIMEOUT
        self.max_results = settings.MAX_SEARCH_RESULTS
    
    async def search(
        self,
        query: str,
        providers: Optional[List[str]] = None,
        num_results: int = 10
    ) -> SearchResponse:
        """
        Execute a parallel search across configured providers.
        
        Args:
            query: The search query
            providers: Specific providers to use (None = all configured)
            num_results: Maximum number of results to return
        
        Returns:
            SearchResponse with aggregated results
        """
        # Determine which providers to use
        available_providers = self._get_available_providers()
        if providers:
            providers_to_use = [p for p in providers if p in available_providers]
        else:
            providers_to_use = available_providers
        
        if not providers_to_use:
            return SearchResponse(
                success=False,
                results=[],
                query=query,
                providers_used=[],
                error="No search providers configured"
            )
        
        # Execute searches in parallel
        tasks = []
        for provider in providers_to_use:
            if provider == "perplexity":
                tasks.append(self._search_perplexity(query))
            elif provider == "exa":
                tasks.append(self._search_exa(query))
            elif provider == "google":
                tasks.append(self._search_google(query))
            elif provider == "bing":
                tasks.append(self._search_bing(query))
        
        # Wait for all searches to complete
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate and deduplicate results
        all_results = []
        successful_providers = []
        
        for i, results in enumerate(results_lists):
            if isinstance(results, Exception):
                continue
            if results:
                all_results.extend(results)
                successful_providers.append(providers_to_use[i])
        
        # Deduplicate by URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)
        
        # Sort by score and limit results
        unique_results.sort(key=lambda x: x.score, reverse=True)
        final_results = unique_results[:num_results]
        
        return SearchResponse(
            success=len(final_results) > 0,
            results=final_results,
            query=query,
            providers_used=successful_providers
        )
    
    def _get_available_providers(self) -> List[str]:
        """Get list of configured search providers."""
        providers = []
        if settings.PERPLEXITY_API_KEY:
            providers.append("perplexity")
        if settings.EXA_API_KEY:
            providers.append("exa")
        if settings.GOOGLE_SEARCH_API_KEY and settings.GOOGLE_SEARCH_CX:
            providers.append("google")
        if settings.BING_API_KEY:
            providers.append("bing")
        return providers
    
    async def _search_perplexity(self, query: str) -> List[SearchResult]:
        """Search using Perplexity AI."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-sonar-small-128k-online",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a search assistant. Provide factual information with sources."
                            },
                            {
                                "role": "user",
                                "content": f"Search for: {query}. Provide key facts with source URLs."
                            }
                        ],
                        "return_citations": True,
                        "return_related_questions": False
                    },
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status != 200:
                        return []
                    
                    data = await resp.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    citations = data.get("citations", [])
                    
                    results = []
                    for i, citation in enumerate(citations[:5]):
                        results.append(SearchResult(
                            title=citation.get("title", f"Source {i+1}"),
                            url=citation.get("url", ""),
                            snippet=content[:200] if i == 0 else "",
                            source="perplexity",
                            score=1.0 - (i * 0.1)
                        ))
                    
                    return results
        except Exception as e:
            return []
    
    async def _search_exa(self, query: str) -> List[SearchResult]:
        """Search using Exa.ai semantic search."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.exa.ai/search",
                    headers={
                        "x-api-key": settings.EXA_API_KEY,
                        "Content-Type": "application/json"
                    },
                    json={
                        "query": query,
                        "type": "neural",
                        "useAutoprompt": True,
                        "numResults": 5,
                        "contents": {
                            "text": {"maxCharacters": 500}
                        }
                    },
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status != 200:
                        return []
                    
                    data = await resp.json()
                    results = []
                    
                    for i, item in enumerate(data.get("results", [])):
                        results.append(SearchResult(
                            title=item.get("title", "Unknown"),
                            url=item.get("url", ""),
                            snippet=item.get("text", "")[:300],
                            source="exa",
                            score=item.get("score", 1.0 - (i * 0.1)),
                            published_date=item.get("publishedDate")
                        ))
                    
                    return results
        except Exception as e:
            return []
    
    async def _search_google(self, query: str) -> List[SearchResult]:
        """Search using Google Custom Search API."""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "key": settings.GOOGLE_SEARCH_API_KEY,
                    "cx": settings.GOOGLE_SEARCH_CX,
                    "q": query,
                    "num": 5
                }
                async with session.get(
                    "https://www.googleapis.com/customsearch/v1",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status != 200:
                        return []
                    
                    data = await resp.json()
                    results = []
                    
                    for i, item in enumerate(data.get("items", [])):
                        results.append(SearchResult(
                            title=item.get("title", "Unknown"),
                            url=item.get("link", ""),
                            snippet=item.get("snippet", ""),
                            source="google",
                            score=1.0 - (i * 0.1)
                        ))
                    
                    return results
        except Exception as e:
            return []
    
    async def _search_bing(self, query: str) -> List[SearchResult]:
        """Search using Bing Web Search API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.bing.microsoft.com/v7.0/search",
                    headers={"Ocp-Apim-Subscription-Key": settings.BING_API_KEY},
                    params={"q": query, "count": 5},
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status != 200:
                        return []
                    
                    data = await resp.json()
                    results = []
                    
                    for i, item in enumerate(data.get("webPages", {}).get("value", [])):
                        results.append(SearchResult(
                            title=item.get("name", "Unknown"),
                            url=item.get("url", ""),
                            snippet=item.get("snippet", ""),
                            source="bing",
                            score=1.0 - (i * 0.1)
                        ))
                    
                    return results
        except Exception as e:
            return []


# Global search layer instance
search_layer = SearchLayer()
