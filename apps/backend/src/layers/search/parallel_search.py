"""
V3.1 Parallel Search Layer
Executes searches across multiple providers simultaneously for comprehensive results.
Providers: Google, Bing, Perplexity, Exa.ai, and Grok real-time
"""

import asyncio
import aiohttp
import json
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
    timestamp: Optional[str] = None


@dataclass
class SearchResponse:
    """Aggregated search response."""
    query: str
    results: List[SearchResult]
    synthesized: str
    sources: List[Dict]
    providers_used: List[str]


class GoogleSearch:
    """Google Custom Search API integration."""
    
    def __init__(self):
        self.api_key = settings.GOOGLE_SEARCH_API_KEY
        self.enabled = bool(self.api_key)
    
    async def search(self, query: str, num_results: int = 5) -> List[SearchResult]:
        """Execute a Google search."""
        if not self.enabled:
            return []
        
        try:
            # Using SerpAPI-style endpoint for Google search
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": self.api_key,
                "num": num_results,
                "engine": "google"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status != 200:
                        return []
                    
                    data = await resp.json()
                    results = []
                    
                    for item in data.get("organic_results", [])[:num_results]:
                        results.append(SearchResult(
                            title=item.get("title", ""),
                            url=item.get("link", ""),
                            snippet=item.get("snippet", ""),
                            source="Google"
                        ))
                    
                    return results
        except Exception as e:
            print(f"Google search error: {e}")
            return []


class BingSearch:
    """Bing Search API integration."""
    
    def __init__(self):
        self.api_key = settings.BING_API_KEY
        self.enabled = bool(self.api_key)
    
    async def search(self, query: str, num_results: int = 5) -> List[SearchResult]:
        """Execute a Bing search."""
        if not self.enabled:
            return []
        
        try:
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {"Ocp-Apim-Subscription-Key": self.api_key}
            params = {"q": query, "count": num_results}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params, 
                                       timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status != 200:
                        return []
                    
                    data = await resp.json()
                    results = []
                    
                    for item in data.get("webPages", {}).get("value", [])[:num_results]:
                        results.append(SearchResult(
                            title=item.get("name", ""),
                            url=item.get("url", ""),
                            snippet=item.get("snippet", ""),
                            source="Bing"
                        ))
                    
                    return results
        except Exception as e:
            print(f"Bing search error: {e}")
            return []


class PerplexitySearch:
    """Perplexity API integration for conversational search."""
    
    def __init__(self):
        self.api_key = settings.PERPLEXITY_API_KEY
        self.enabled = bool(self.api_key)
    
    async def search(self, query: str) -> Dict:
        """Execute a Perplexity search."""
        if not self.enabled:
            return {"answer": "", "sources": []}
        
        try:
            url = "https://api.perplexity.ai/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.1-sonar-large-128k-online",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful research assistant specializing in fashion, beauty, lifestyle, and related industries. Provide comprehensive, accurate, and up-to-date information with sources."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "temperature": 0.2,
                "max_tokens": 2048,
                "return_citations": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload,
                                        timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status != 200:
                        return {"answer": "", "sources": []}
                    
                    data = await resp.json()
                    answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    citations = data.get("citations", [])
                    
                    return {
                        "answer": answer,
                        "sources": [{"url": c, "source": "Perplexity"} for c in citations]
                    }
        except Exception as e:
            print(f"Perplexity search error: {e}")
            return {"answer": "", "sources": []}


class ExaSearch:
    """Exa.ai neural search integration for deep research."""
    
    def __init__(self):
        self.api_key = settings.EXA_API_KEY
        self.enabled = bool(self.api_key)
    
    async def search(self, query: str, num_results: int = 5) -> List[SearchResult]:
        """Execute an Exa neural search."""
        if not self.enabled:
            return []
        
        try:
            url = "https://api.exa.ai/search"
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "query": query,
                "numResults": num_results,
                "useAutoprompt": True,
                "type": "neural",
                "contents": {
                    "text": True
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload,
                                        timeout=aiohttp.ClientTimeout(total=20)) as resp:
                    if resp.status != 200:
                        return []
                    
                    data = await resp.json()
                    results = []
                    
                    for item in data.get("results", [])[:num_results]:
                        results.append(SearchResult(
                            title=item.get("title", ""),
                            url=item.get("url", ""),
                            snippet=item.get("text", "")[:500] if item.get("text") else "",
                            source="Exa.ai",
                            timestamp=item.get("publishedDate")
                        ))
                    
                    return results
        except Exception as e:
            print(f"Exa search error: {e}")
            return []


class GrokRealTimeSearch:
    """Grok's real-time X (Twitter) search capability."""
    
    def __init__(self):
        self.api_key = settings.XAI_API_KEY
        self.enabled = bool(self.api_key)
    
    async def search(self, query: str) -> Dict:
        """Execute a Grok real-time search focused on social trends."""
        if not self.enabled:
            return {"insights": "", "trending": []}
        
        try:
            url = f"{settings.GROK_API_BASE}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": settings.GROK_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "You have access to real-time information from X (Twitter). Provide the latest trends, discussions, and sentiment about the user's query. Focus on fashion, beauty, lifestyle, and related topics."
                    },
                    {
                        "role": "user",
                        "content": f"What are the latest real-time discussions and trends about: {query}"
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1024
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload,
                                        timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status != 200:
                        return {"insights": "", "trending": []}
                    
                    data = await resp.json()
                    insights = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    
                    return {
                        "insights": insights,
                        "source": "Grok Real-time"
                    }
        except Exception as e:
            print(f"Grok real-time search error: {e}")
            return {"insights": "", "trending": []}


class ParallelSearchLayer:
    """
    The V3.1 Parallel Search Layer
    Executes searches across all providers simultaneously and synthesizes results.
    """
    
    def __init__(self):
        self.google = GoogleSearch()
        self.bing = BingSearch()
        self.perplexity = PerplexitySearch()
        self.exa = ExaSearch()
        self.grok_realtime = GrokRealTimeSearch()
    
    async def parallel_search(self, query: str) -> Dict:
        """
        Execute parallel searches across all providers.
        Returns synthesized results with sources.
        """
        
        # Execute all searches in parallel
        tasks = [
            self.google.search(query),
            self.bing.search(query),
            self.perplexity.search(query),
            self.exa.search(query),
            self.grok_realtime.search(query)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        google_results = results[0] if not isinstance(results[0], Exception) else []
        bing_results = results[1] if not isinstance(results[1], Exception) else []
        perplexity_data = results[2] if not isinstance(results[2], Exception) else {}
        exa_results = results[3] if not isinstance(results[3], Exception) else []
        grok_data = results[4] if not isinstance(results[4], Exception) else {}
        
        # Collect all sources
        all_sources = []
        providers_used = []
        
        if google_results:
            providers_used.append("Google")
            for r in google_results:
                all_sources.append({
                    "title": r.title,
                    "url": r.url,
                    "snippet": r.snippet,
                    "source": "Google"
                })
        
        if bing_results:
            providers_used.append("Bing")
            for r in bing_results:
                all_sources.append({
                    "title": r.title,
                    "url": r.url,
                    "snippet": r.snippet,
                    "source": "Bing"
                })
        
        if perplexity_data.get("answer"):
            providers_used.append("Perplexity")
            for s in perplexity_data.get("sources", []):
                all_sources.append(s)
        
        if exa_results:
            providers_used.append("Exa.ai")
            for r in exa_results:
                all_sources.append({
                    "title": r.title,
                    "url": r.url,
                    "snippet": r.snippet,
                    "source": "Exa.ai"
                })
        
        if grok_data.get("insights"):
            providers_used.append("Grok Real-time")
        
        # Synthesize all information
        synthesized = self._synthesize_results(
            query,
            google_results,
            bing_results,
            perplexity_data,
            exa_results,
            grok_data
        )
        
        # De-duplicate sources by URL
        seen_urls = set()
        unique_sources = []
        for source in all_sources:
            url = source.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_sources.append(source)
        
        return {
            "query": query,
            "synthesized": synthesized,
            "sources": unique_sources[:10],  # Top 10 sources
            "providers_used": providers_used
        }
    
    def _synthesize_results(self, query: str, google: List, bing: List, 
                           perplexity: Dict, exa: List, grok: Dict) -> str:
        """Synthesize all search results into a coherent brief."""
        
        parts = []
        
        # Perplexity answer (usually most comprehensive)
        if perplexity.get("answer"):
            parts.append(f"**Research Summary:**\n{perplexity['answer']}")
        
        # Grok real-time insights
        if grok.get("insights"):
            parts.append(f"\n**Real-time Social Insights:**\n{grok['insights']}")
        
        # Exa deep research
        if exa:
            exa_snippets = "\n".join([f"- {r.title}: {r.snippet[:200]}" for r in exa[:3]])
            parts.append(f"\n**Deep Research Findings:**\n{exa_snippets}")
        
        # Traditional search highlights
        all_traditional = google + bing
        if all_traditional:
            highlights = "\n".join([f"- {r.title}" for r in all_traditional[:5]])
            parts.append(f"\n**Additional Sources:**\n{highlights}")
        
        return "\n".join(parts) if parts else "No search results found."


# Global instance
parallel_search = ParallelSearchLayer()
