"""
McLeuker Agentic AI Platform - Layer 3: Real-Time Web Research Layer

This layer gathers up-to-date, domain-relevant information from the web
based on the research questions from the Reasoning Layer.
"""

import asyncio
import json
import re
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx
from bs4 import BeautifulSoup

from src.models.schemas import (
    ReasoningBlueprint,
    SearchResult,
    WebResearchResult,
    ScrapedContent,
    ResearchOutput
)
from src.utils.llm_provider import LLMProvider, LLMFactory
from src.config.settings import get_settings


class WebSearchProvider:
    """Base class for web search providers."""
    
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Perform a web search."""
        raise NotImplementedError


class GoogleSearchProvider(WebSearchProvider):
    """Google Custom Search API provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.GOOGLE_SEARCH_API_KEY
        self.base_url = "https://serpapi.com/search"
    
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Perform a Google search via SerpAPI."""
        if not self.api_key:
            return []
        
        params = {
            "api_key": self.api_key,
            "q": query,
            "engine": "google",
            "num": num_results
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.base_url,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("organic_results", []):
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("link", ""),
                        snippet=item.get("snippet", ""),
                        source=item.get("source", None),
                        published_date=item.get("date", None)
                    ))
                
                return results
            except Exception as e:
                print(f"Google search error: {e}")
                return []


class BingSearchProvider(WebSearchProvider):
    """Bing Search API provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.BING_API_KEY
        self.base_url = "https://api.bing.microsoft.com/v7.0/search"
    
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Perform a Bing search."""
        if not self.api_key:
            return []
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key
        }
        
        params = {
            "q": query,
            "count": num_results,
            "mkt": "en-US"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.base_url,
                    headers=headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("webPages", {}).get("value", []):
                    results.append(SearchResult(
                        title=item.get("name", ""),
                        url=item.get("url", ""),
                        snippet=item.get("snippet", ""),
                        source=item.get("displayUrl", None),
                        published_date=item.get("dateLastCrawled", None)
                    ))
                
                return results
            except Exception as e:
                print(f"Bing search error: {e}")
                return []


class PerplexitySearchProvider(WebSearchProvider):
    """Perplexity AI search provider for AI-powered search with citations."""
    
    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.PERPLEXITY_API_KEY
        self.base_url = "https://api.perplexity.ai/chat/completions"
    
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Perform an AI-powered search via Perplexity."""
        if not self.api_key:
            return []
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful search assistant. Provide factual information with sources."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "return_citations": True
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                
                results = []
                
                # Extract citations as search results
                citations = data.get("citations", [])
                for i, citation in enumerate(citations[:num_results]):
                    results.append(SearchResult(
                        title=f"Source {i+1}",
                        url=citation,
                        snippet=data.get("choices", [{}])[0].get("message", {}).get("content", "")[:200],
                        source="Perplexity AI",
                        published_date=None
                    ))
                
                return results
            except Exception as e:
                print(f"Perplexity search error: {e}")
                return []


class SerperSearchProvider(WebSearchProvider):
    """Serper.dev search provider for Google search results."""
    
    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.SERPER_API_KEY
        self.base_url = "https://google.serper.dev/search"
    
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Perform a Google search via Serper API."""
        if not self.api_key:
            return []
        
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "num": num_results
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("organic", []):
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("link", ""),
                        snippet=item.get("snippet", ""),
                        source=item.get("source", None),
                        published_date=item.get("date", None)
                    ))
                
                return results
            except Exception as e:
                print(f"Serper search error: {e}")
                return []


class TavilySearchProvider(WebSearchProvider):
    """Tavily search provider for AI-optimized search."""
    
    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.TAVILY_API_KEY
        self.base_url = "https://api.tavily.com/search"
    
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Perform a search via Tavily API."""
        if not self.api_key:
            return []
        
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "advanced",
            "max_results": num_results,
            "include_answer": True
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("results", []):
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("content", ""),
                        source=item.get("source", None),
                        published_date=item.get("published_date", None)
                    ))
                
                return results
            except Exception as e:
                print(f"Tavily search error: {e}")
                return []


class DuckDuckGoSearchProvider(WebSearchProvider):
    """DuckDuckGo search provider (no API key required)."""
    
    def __init__(self):
        self.base_url = "https://html.duckduckgo.com/html/"
    
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Perform a DuckDuckGo search."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    data={"q": query},
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                results = []
                
                for result in soup.select(".result")[:num_results]:
                    title_elem = result.select_one(".result__title a")
                    snippet_elem = result.select_one(".result__snippet")
                    
                    if title_elem:
                        url = title_elem.get("href", "")
                        # Extract actual URL from DuckDuckGo redirect
                        if "uddg=" in url:
                            import urllib.parse
                            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                            url = parsed.get("uddg", [url])[0]
                        
                        results.append(SearchResult(
                            title=title_elem.get_text(strip=True),
                            url=url,
                            snippet=snippet_elem.get_text(strip=True) if snippet_elem else "",
                            source=None,
                            published_date=None
                        ))
                
                return results
            except Exception as e:
                print(f"DuckDuckGo search error: {e}")
                return []


class FirecrawlScraper:
    """Firecrawl API for advanced web scraping."""
    
    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.FIRECRAWL_API_KEY
        self.base_url = "https://api.firecrawl.dev/v0/scrape"
    
    async def scrape(self, url: str) -> Optional[ScrapedContent]:
        """Scrape content from a URL using Firecrawl."""
        if not self.api_key:
            return None
        
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
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("success"):
                    content_data = data.get("data", {})
                    return ScrapedContent(
                        url=url,
                        title=content_data.get("metadata", {}).get("title"),
                        content=content_data.get("markdown", content_data.get("content", "")),
                        scraped_at=datetime.utcnow()
                    )
                return None
            except Exception as e:
                print(f"Firecrawl scraping error for {url}: {e}")
                return None


class WebScraper:
    """Web scraper for extracting content from URLs."""
    
    def __init__(self, timeout: int = 30, use_firecrawl: bool = True):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        settings = get_settings()
        self.firecrawl = FirecrawlScraper() if use_firecrawl and settings.FIRECRAWL_API_KEY else None
    
    async def scrape(self, url: str) -> Optional[ScrapedContent]:
        """Scrape content from a URL."""
        # Try Firecrawl first if available
        if self.firecrawl:
            result = await self.firecrawl.scrape(url)
            if result:
                return result
        
        # Fallback to basic scraping
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout,
                    follow_redirects=True
                )
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Remove script and style elements
                for element in soup(["script", "style", "nav", "footer", "header"]):
                    element.decompose()
                
                # Get title
                title = soup.title.string if soup.title else None
                
                # Get main content
                content_selectors = [
                    "article",
                    "main",
                    ".content",
                    ".post-content",
                    ".article-content",
                    "#content",
                    ".entry-content"
                ]
                
                content = ""
                for selector in content_selectors:
                    element = soup.select_one(selector)
                    if element:
                        content = element.get_text(separator="\n", strip=True)
                        break
                
                if not content:
                    body = soup.find("body")
                    if body:
                        content = body.get_text(separator="\n", strip=True)
                
                # Clean up content
                content = re.sub(r'\n\s*\n', '\n\n', content)
                content = content[:10000]
                
                return ScrapedContent(
                    url=url,
                    title=title,
                    content=content,
                    scraped_at=datetime.utcnow()
                )
            except Exception as e:
                print(f"Scraping error for {url}: {e}")
                return None
    
    async def scrape_multiple(self, urls: List[str]) -> List[ScrapedContent]:
        """Scrape content from multiple URLs concurrently."""
        tasks = [self.scrape(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]


class MultiSearchProvider:
    """Aggregates results from multiple search providers."""
    
    def __init__(self):
        settings = get_settings()
        self.providers = []
        
        # Add providers in priority order
        if settings.PERPLEXITY_API_KEY:
            self.providers.append(("perplexity", PerplexitySearchProvider()))
        if settings.GOOGLE_SEARCH_API_KEY:
            self.providers.append(("google", GoogleSearchProvider()))
        if settings.BING_API_KEY:
            self.providers.append(("bing", BingSearchProvider()))
        if settings.SERPER_API_KEY:
            self.providers.append(("serper", SerperSearchProvider()))
        if settings.TAVILY_API_KEY:
            self.providers.append(("tavily", TavilySearchProvider()))
        
        # Always have DuckDuckGo as fallback
        self.providers.append(("duckduckgo", DuckDuckGoSearchProvider()))
    
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Search using the first available provider."""
        for name, provider in self.providers:
            try:
                results = await provider.search(query, num_results)
                if results:
                    return results
            except Exception as e:
                print(f"Search provider {name} failed: {e}")
                continue
        return []
    
    async def search_all(self, query: str, num_results: int = 10) -> Dict[str, List[SearchResult]]:
        """Search using all available providers."""
        results = {}
        for name, provider in self.providers:
            try:
                provider_results = await provider.search(query, num_results)
                if provider_results:
                    results[name] = provider_results
            except Exception as e:
                print(f"Search provider {name} failed: {e}")
        return results


class WebResearchLayer:
    """
    Layer 3: Real-Time Web Research
    
    Gathers up-to-date information from the web based on
    research questions from the Reasoning Layer.
    """
    
    def __init__(
        self,
        search_provider: Optional[WebSearchProvider] = None,
        llm_provider: Optional[LLMProvider] = None
    ):
        """Initialize the Web Research Layer."""
        self.search_provider = search_provider or MultiSearchProvider()
        self.scraper = WebScraper()
        self.llm = llm_provider or LLMFactory.get_default()
        self.settings = get_settings()
    
    async def research(
        self,
        reasoning_blueprint: ReasoningBlueprint,
        scrape_top_results: bool = True,
        max_scrape: int = 3
    ) -> ResearchOutput:
        """
        Perform web research based on the reasoning blueprint.
        
        Args:
            reasoning_blueprint: The reasoning blueprint with research questions
            scrape_top_results: Whether to scrape top search results
            max_scrape: Maximum number of pages to scrape per query
            
        Returns:
            ResearchOutput: Complete research output
        """
        search_results = []
        scraped_contents = []
        
        # Get research questions
        questions = reasoning_blueprint.research_questions or []
        
        # If no questions, generate from objectives
        if not questions:
            questions = [
                f"Latest information about {reasoning_blueprint.task_summary}"
            ]
        
        # Perform searches for each question
        for question in questions:
            results = await self.search_provider.search(
                question,
                num_results=self.settings.MAX_SEARCH_RESULTS
            )
            
            search_results.append(WebResearchResult(
                query=question,
                results=results
            ))
            
            # Scrape top results if enabled
            if scrape_top_results and results:
                urls_to_scrape = [r.url for r in results[:max_scrape]]
                scraped = await self.scraper.scrape_multiple(urls_to_scrape)
                scraped_contents.extend(scraped)
        
        # Synthesize findings using LLM
        synthesized = await self._synthesize_findings(
            reasoning_blueprint,
            search_results,
            scraped_contents
        )
        
        return ResearchOutput(
            search_results=search_results,
            scraped_contents=scraped_contents if scraped_contents else None,
            synthesized_findings=synthesized,
            data_points=None
        )
    
    async def _synthesize_findings(
        self,
        blueprint: ReasoningBlueprint,
        search_results: List[WebResearchResult],
        scraped_contents: List[ScrapedContent]
    ) -> str:
        """Synthesize research findings using LLM."""
        context_parts = [
            f"Task: {blueprint.task_summary}",
            f"Objectives: {', '.join(blueprint.reasoning_objectives)}",
            "\n--- Search Results ---"
        ]
        
        for sr in search_results:
            context_parts.append(f"\nQuery: {sr.query}")
            for i, result in enumerate(sr.results[:5], 1):
                context_parts.append(f"{i}. {result.title}")
                context_parts.append(f"   {result.snippet}")
        
        if scraped_contents:
            context_parts.append("\n--- Scraped Content ---")
            for sc in scraped_contents[:3]:
                context_parts.append(f"\nSource: {sc.title or sc.url}")
                context_parts.append(sc.content[:2000])
        
        context = "\n".join(context_parts)
        
        messages = [
            {
                "role": "system",
                "content": """You are a research synthesis agent. Your job is to:
1. Analyze the search results and scraped content
2. Extract key findings relevant to the task
3. Organize information in a structured way
4. Identify any gaps in the research

Provide a comprehensive synthesis that can be used for creating reports, presentations, or data tables.
Be factual and cite sources where possible."""
            },
            {
                "role": "user",
                "content": f"Synthesize the following research findings:\n\n{context}"
            }
        ]
        
        response = await self.llm.complete(
            messages=messages,
            temperature=0.3,
            max_tokens=2000
        )
        
        return response.get("content", "")
    
    async def search_single_query(self, query: str) -> WebResearchResult:
        """Perform a single search query."""
        results = await self.search_provider.search(
            query,
            num_results=self.settings.MAX_SEARCH_RESULTS
        )
        
        return WebResearchResult(
            query=query,
            results=results
        )
    
    async def scrape_url(self, url: str) -> Optional[ScrapedContent]:
        """Scrape a single URL."""
        return await self.scraper.scrape(url)
    
    async def expand_queries(
        self,
        base_query: str,
        num_expansions: int = 3
    ) -> List[str]:
        """Expand a base query into multiple related queries."""
        messages = [
            {
                "role": "system",
                "content": "You are a search query expansion agent. Generate related search queries that will help gather comprehensive information."
            },
            {
                "role": "user",
                "content": f"Generate {num_expansions} related search queries for: {base_query}\n\nRespond with a JSON array of strings."
            }
        ]
        
        response = await self.llm.complete_with_structured_output(
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.5
        )
        
        content = response.get("content", {})
        if isinstance(content, dict):
            queries = content.get("queries", [base_query])
        else:
            queries = [base_query]
        
        return queries[:num_expansions]


# Convenience function for direct usage
async def perform_research(
    reasoning_blueprint: ReasoningBlueprint,
    search_provider: Optional[WebSearchProvider] = None,
    llm_provider: Optional[LLMProvider] = None
) -> ResearchOutput:
    """
    Convenience function to perform web research.
    
    Args:
        reasoning_blueprint: The reasoning blueprint with research questions
        search_provider: Optional search provider to use
        llm_provider: Optional LLM provider to use
        
    Returns:
        ResearchOutput: Complete research output
    """
    layer = WebResearchLayer(search_provider, llm_provider)
    return await layer.research(reasoning_blueprint)
