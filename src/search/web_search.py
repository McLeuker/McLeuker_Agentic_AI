"""
McLeuker Agentic AI Platform - Real-Time Web Search System

Multi-provider search system using Perplexity, Google, Bing, and Firecrawl
for comprehensive real-time information retrieval.
"""

import os
import json
import asyncio
import aiohttp
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod

from src.config.settings import get_settings


@dataclass
class SearchResult:
    """A single search result."""
    title: str
    url: str
    snippet: str
    source: str
    published_date: Optional[str] = None
    relevance_score: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "published_date": self.published_date,
            "relevance_score": self.relevance_score
        }


@dataclass
class SearchResponse:
    """Complete search response."""
    query: str
    results: List[SearchResult]
    total_results: int
    provider: str
    summary: Optional[str] = None
    follow_up_questions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "results": [r.to_dict() for r in self.results],
            "total_results": self.total_results,
            "provider": self.provider,
            "summary": self.summary,
            "follow_up_questions": self.follow_up_questions,
            "timestamp": self.timestamp.isoformat()
        }


class SearchProvider(ABC):
    """Abstract base class for search providers."""
    
    @abstractmethod
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Perform a search and return results."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass


class PerplexitySearchProvider(SearchProvider):
    """
    Perplexity AI search provider.
    
    Uses Perplexity's online models for real-time search with AI synthesis.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.PERPLEXITY_API_KEY
        self.base_url = "https://api.perplexity.ai"
    
    @property
    def name(self) -> str:
        return "perplexity"
    
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Search using Perplexity's online model."""
        if not self.api_key:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "llama-3.1-sonar-large-128k-online",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful search assistant. Provide accurate, current information with sources."
                        },
                        {
                            "role": "user",
                            "content": query
                        }
                    ],
                    "temperature": 0.2,
                    "max_tokens": 2000,
                    "return_citations": True
                }
                
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_response(data, query)
                    else:
                        error = await response.text()
                        print(f"Perplexity search error: {error}")
                        return []
        
        except Exception as e:
            print(f"Perplexity search exception: {e}")
            return []
    
    def _parse_response(self, data: Dict, query: str) -> List[SearchResult]:
        """Parse Perplexity response into search results."""
        results = []
        
        try:
            choices = data.get("choices", [])
            if choices:
                message = choices[0].get("message", {})
                content = message.get("content", "")
                
                # Create a result from the synthesized answer
                results.append(SearchResult(
                    title=f"AI Search: {query[:50]}...",
                    url="https://perplexity.ai",
                    snippet=content[:500],
                    source="perplexity",
                    relevance_score=1.0
                ))
                
                # Extract citations if available
                citations = data.get("citations", [])
                for i, citation in enumerate(citations[:5]):
                    if isinstance(citation, str):
                        results.append(SearchResult(
                            title=f"Source {i+1}",
                            url=citation,
                            snippet="",
                            source="perplexity_citation",
                            relevance_score=0.9 - (i * 0.1)
                        ))
        
        except Exception as e:
            print(f"Error parsing Perplexity response: {e}")
        
        return results
    
    async def search_with_synthesis(self, query: str) -> Dict[str, Any]:
        """Search and get synthesized answer with sources."""
        if not self.api_key:
            return {"error": "Perplexity API key not configured"}
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "llama-3.1-sonar-large-128k-online",
                    "messages": [
                        {
                            "role": "system",
                            "content": """You are a knowledgeable search assistant. When answering:
1. Provide accurate, current information
2. Include specific details, names, and data
3. Cite your sources
4. Format your response clearly with sections if needed
5. If the query is about current events, provide the latest information available"""
                        },
                        {
                            "role": "user",
                            "content": query
                        }
                    ],
                    "temperature": 0.2,
                    "max_tokens": 3000,
                    "return_citations": True
                }
                
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        choices = data.get("choices", [])
                        
                        if choices:
                            message = choices[0].get("message", {})
                            return {
                                "answer": message.get("content", ""),
                                "citations": data.get("citations", []),
                                "model": data.get("model", ""),
                                "provider": "perplexity"
                            }
                    
                    return {"error": f"Search failed with status {response.status}"}
        
        except Exception as e:
            return {"error": str(e)}


class GoogleSearchProvider(SearchProvider):
    """Google Custom Search provider."""
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.GOOGLE_SEARCH_API_KEY
        self.cx = getattr(self.settings, 'GOOGLE_SEARCH_CX', None)
    
    @property
    def name(self) -> str:
        return "google"
    
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Search using Google Custom Search API."""
        if not self.api_key:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "key": self.api_key,
                    "q": query,
                    "num": min(num_results, 10)
                }
                
                if self.cx:
                    params["cx"] = self.cx
                
                async with session.get(
                    "https://www.googleapis.com/customsearch/v1",
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_response(data)
                    else:
                        return []
        
        except Exception as e:
            print(f"Google search error: {e}")
            return []
    
    def _parse_response(self, data: Dict) -> List[SearchResult]:
        """Parse Google search response."""
        results = []
        
        items = data.get("items", [])
        for i, item in enumerate(items):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),
                source="google",
                relevance_score=1.0 - (i * 0.05)
            ))
        
        return results


class BingSearchProvider(SearchProvider):
    """Bing Search provider."""
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.BING_API_KEY
    
    @property
    def name(self) -> str:
        return "bing"
    
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Search using Bing Search API."""
        if not self.api_key:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Ocp-Apim-Subscription-Key": self.api_key
                }
                
                params = {
                    "q": query,
                    "count": num_results,
                    "mkt": "en-US"
                }
                
                async with session.get(
                    "https://api.bing.microsoft.com/v7.0/search",
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_response(data)
                    else:
                        return []
        
        except Exception as e:
            print(f"Bing search error: {e}")
            return []
    
    def _parse_response(self, data: Dict) -> List[SearchResult]:
        """Parse Bing search response."""
        results = []
        
        web_pages = data.get("webPages", {}).get("value", [])
        for i, page in enumerate(web_pages):
            results.append(SearchResult(
                title=page.get("name", ""),
                url=page.get("url", ""),
                snippet=page.get("snippet", ""),
                source="bing",
                published_date=page.get("dateLastCrawled"),
                relevance_score=1.0 - (i * 0.05)
            ))
        
        return results


class FirecrawlProvider(SearchProvider):
    """Firecrawl web scraping provider."""
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.FIRECRAWL_API_KEY
        self.base_url = "https://api.firecrawl.dev/v0"
    
    @property
    def name(self) -> str:
        return "firecrawl"
    
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Search using Firecrawl."""
        if not self.api_key:
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "query": query,
                    "limit": num_results
                }
                
                async with session.post(
                    f"{self.base_url}/search",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_response(data)
                    else:
                        return []
        
        except Exception as e:
            print(f"Firecrawl search error: {e}")
            return []
    
    def _parse_response(self, data: Dict) -> List[SearchResult]:
        """Parse Firecrawl response."""
        results = []
        
        items = data.get("data", [])
        for i, item in enumerate(items):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("description", item.get("content", "")[:300]),
                source="firecrawl",
                relevance_score=1.0 - (i * 0.05)
            ))
        
        return results
    
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape a specific URL."""
        if not self.api_key:
            return {"error": "Firecrawl API key not configured"}
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "url": url,
                    "pageOptions": {
                        "onlyMainContent": True
                    }
                }
                
                async with session.post(
                    f"{self.base_url}/scrape",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"Scrape failed with status {response.status}"}
        
        except Exception as e:
            return {"error": str(e)}


class MultiProviderSearch:
    """
    Multi-provider search system.
    
    Combines results from multiple search providers for comprehensive coverage.
    """
    
    def __init__(self, llm_provider=None):
        self.settings = get_settings()
        self.llm = llm_provider
        
        # Initialize providers
        self.providers: List[SearchProvider] = []
        
        # Add Perplexity (primary for AI-powered search)
        if self.settings.PERPLEXITY_API_KEY:
            self.providers.append(PerplexitySearchProvider())
        
        # Add Google
        if self.settings.GOOGLE_SEARCH_API_KEY:
            self.providers.append(GoogleSearchProvider())
        
        # Add Bing
        if self.settings.BING_API_KEY:
            self.providers.append(BingSearchProvider())
        
        # Add Firecrawl
        if self.settings.FIRECRAWL_API_KEY:
            self.providers.append(FirecrawlProvider())
    
    async def search(
        self,
        query: str,
        num_results: int = 10,
        providers: Optional[List[str]] = None
    ) -> SearchResponse:
        """
        Search across multiple providers.
        
        Args:
            query: Search query
            num_results: Number of results to return
            providers: Optional list of provider names to use
            
        Returns:
            Combined search response
        """
        # Filter providers if specified
        active_providers = self.providers
        if providers:
            active_providers = [p for p in self.providers if p.name in providers]
        
        if not active_providers:
            return SearchResponse(
                query=query,
                results=[],
                total_results=0,
                provider="none",
                summary="No search providers available"
            )
        
        # Search all providers concurrently
        tasks = [p.search(query, num_results) for p in active_providers]
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine and deduplicate results
        all_results = []
        seen_urls = set()
        
        for results in results_lists:
            if isinstance(results, list):
                for result in results:
                    if result.url not in seen_urls:
                        seen_urls.add(result.url)
                        all_results.append(result)
        
        # Sort by relevance
        all_results.sort(key=lambda r: r.relevance_score, reverse=True)
        
        # Limit results
        final_results = all_results[:num_results]
        
        # Generate summary if we have an LLM
        summary = None
        if self.llm and final_results:
            summary = await self._generate_summary(query, final_results)
        
        return SearchResponse(
            query=query,
            results=final_results,
            total_results=len(all_results),
            provider=",".join([p.name for p in active_providers]),
            summary=summary
        )
    
    async def smart_search(self, query: str) -> Dict[str, Any]:
        """
        Perform a smart search with AI synthesis.
        
        Uses Perplexity for AI-powered search if available,
        falls back to traditional search with LLM synthesis.
        """
        # Try Perplexity first for best results
        perplexity = next(
            (p for p in self.providers if isinstance(p, PerplexitySearchProvider)),
            None
        )
        
        if perplexity:
            result = await perplexity.search_with_synthesis(query)
            if "error" not in result:
                return {
                    "answer": result.get("answer", ""),
                    "sources": result.get("citations", []),
                    "provider": "perplexity",
                    "is_real_time": True
                }
        
        # Fall back to traditional search
        response = await self.search(query)
        
        return {
            "answer": response.summary or "Search completed",
            "sources": [r.url for r in response.results[:5]],
            "results": [r.to_dict() for r in response.results],
            "provider": response.provider,
            "is_real_time": True
        }
    
    async def _generate_summary(
        self,
        query: str,
        results: List[SearchResult]
    ) -> Optional[str]:
        """Generate a summary of search results using LLM."""
        if not self.llm:
            return None
        
        try:
            # Prepare context from results
            context = "\n\n".join([
                f"Source: {r.title}\nURL: {r.url}\nContent: {r.snippet}"
                for r in results[:5]
            ])
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Summarize the search results to answer the user's query. Be concise but comprehensive."
                },
                {
                    "role": "user",
                    "content": f"Query: {query}\n\nSearch Results:\n{context}\n\nProvide a helpful summary that answers the query."
                }
            ]
            
            response = await self.llm.complete(
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )
            
            return response.get("content", "")
        
        except Exception as e:
            print(f"Error generating summary: {e}")
            return None


# Global search instance
_search_system: Optional[MultiProviderSearch] = None


def get_search_system(llm_provider=None) -> MultiProviderSearch:
    """Get or create the global search system."""
    global _search_system
    if _search_system is None:
        _search_system = MultiProviderSearch(llm_provider)
    return _search_system
