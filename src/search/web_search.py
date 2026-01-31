"""
McLeuker Agentic AI Platform - Real-Time Web Search System v2.1

Fixed version with proper Perplexity integration and comprehensive fallback.
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
    answer: Optional[str] = None
    follow_up_questions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "results": [r.to_dict() for r in self.results],
            "total_results": self.total_results,
            "provider": self.provider,
            "summary": self.summary,
            "answer": self.answer,
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
    Perplexity AI search provider - PRIMARY SEARCH ENGINE.
    
    Uses Perplexity's online models for real-time search with AI synthesis.
    This is the main search provider that returns comprehensive answers.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.PERPLEXITY_API_KEY
        self.base_url = "https://api.perplexity.ai"
    
    @property
    def name(self) -> str:
        return "perplexity"
    
    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Search using Perplexity's online model."""
        if not self.api_key:
            print("Perplexity API key not configured")
            return []
        
        try:
            result = await self.search_with_synthesis(query)
            if "error" not in result:
                answer = result.get("answer", "")
                citations = result.get("citations", [])
                
                results = []
                
                # Create main result from the answer
                if answer:
                    results.append(SearchResult(
                        title=f"Search Results for: {query[:50]}",
                        url="https://perplexity.ai",
                        snippet=answer,
                        source="perplexity",
                        relevance_score=1.0
                    ))
                
                # Add citations as additional results
                for i, citation in enumerate(citations[:5]):
                    if isinstance(citation, str) and citation.startswith("http"):
                        results.append(SearchResult(
                            title=f"Source {i+1}",
                            url=citation,
                            snippet="",
                            source="perplexity_citation",
                            relevance_score=0.9 - (i * 0.1)
                        ))
                
                return results
            
            return []
        
        except Exception as e:
            print(f"Perplexity search exception: {e}")
            return []
    
    async def search_with_synthesis(self, query: str) -> Dict[str, Any]:
        """
        Search and get synthesized answer with sources.
        This is the main method that returns comprehensive answers.
        """
        if not self.api_key:
            return {"error": "Perplexity API key not configured"}
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                # Use the sonar model for online search
                payload = {
                    "model": "sonar",
                    "messages": [
                        {
                            "role": "system",
                            "content": """You are a knowledgeable research assistant. When answering:
1. Provide accurate, current, and comprehensive information
2. Include specific details, statistics, names, and data points
3. Structure your response with clear sections using markdown headers (##)
4. Use bullet points for lists
5. If discussing trends or news, mention specific examples
6. Always aim to give a complete, helpful answer
7. Format numbers and dates clearly"""
                        },
                        {
                            "role": "user",
                            "content": query
                        }
                    ],
                    "temperature": 0.2,
                    "max_tokens": 4000,
                    "return_citations": True,
                    "search_recency_filter": "month"
                }
                
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        choices = data.get("choices", [])
                        
                        if choices:
                            message = choices[0].get("message", {})
                            content = message.get("content", "")
                            citations = data.get("citations", [])
                            
                            if content:
                                return {
                                    "answer": content,
                                    "citations": citations,
                                    "model": data.get("model", "sonar"),
                                    "provider": "perplexity"
                                }
                    
                    error_text = await response.text()
                    print(f"Perplexity API error: {response.status} - {error_text}")
                    return {"error": f"Search failed with status {response.status}"}
        
        except asyncio.TimeoutError:
            print("Perplexity search timeout")
            return {"error": "Search timeout"}
        except Exception as e:
            print(f"Perplexity search error: {e}")
            return {"error": str(e)}


class MultiProviderSearch:
    """
    Multi-provider search system with intelligent fallback.
    
    Primary: Perplexity (for comprehensive AI-synthesized answers)
    Fallback: OpenAI with context (when Perplexity fails)
    """
    
    def __init__(self, llm_provider=None):
        self.settings = get_settings()
        self.llm = llm_provider
        
        # Initialize Perplexity as primary
        self.perplexity = PerplexitySearchProvider()
        
        print(f"Search system initialized:")
        print(f"  - Perplexity available: {self.perplexity.is_available}")
        print(f"  - LLM fallback available: {self.llm is not None}")
    
    async def smart_search(self, query: str) -> Dict[str, Any]:
        """
        Perform a smart search with AI synthesis.
        
        This is the main search method that:
        1. Tries Perplexity first for real-time web search
        2. Falls back to LLM with knowledge if Perplexity fails
        3. Always returns a comprehensive answer
        """
        print(f"Smart search for: {query}")
        
        # Try Perplexity first (primary search)
        if self.perplexity.is_available:
            print("Trying Perplexity search...")
            result = await self.perplexity.search_with_synthesis(query)
            
            if "error" not in result and result.get("answer"):
                answer = result.get("answer", "")
                citations = result.get("citations", [])
                
                print(f"Perplexity returned {len(answer)} chars, {len(citations)} citations")
                
                return {
                    "answer": answer,
                    "sources": citations,
                    "provider": "perplexity",
                    "is_real_time": True
                }
            else:
                print(f"Perplexity failed: {result.get('error', 'Unknown error')}")
        
        # Fallback to LLM with general knowledge
        if self.llm:
            print("Falling back to LLM...")
            return await self._llm_fallback_search(query)
        
        # Last resort - return error message
        return {
            "answer": "I apologize, but I'm unable to search for real-time information at the moment. Please try again later or rephrase your question.",
            "sources": [],
            "provider": "none",
            "is_real_time": False
        }
    
    async def _llm_fallback_search(self, query: str) -> Dict[str, Any]:
        """
        Fallback search using LLM's knowledge.
        Used when Perplexity is unavailable.
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are a knowledgeable AI assistant. Answer the user's question comprehensively using your training knowledge.

Guidelines:
1. Provide detailed, accurate information
2. Structure your response with clear sections using markdown (## headers)
3. Include specific examples, statistics, and details when relevant
4. Use bullet points for lists
5. If the question is about current events, acknowledge that your information may not be the latest
6. Always aim to be helpful and thorough

Format your response professionally with:
- Clear section headers
- Bullet points for key information
- Bold text for important terms"""
                },
                {
                    "role": "user",
                    "content": query
                }
            ]
            
            response = await self.llm.complete(
                messages=messages,
                temperature=0.5,
                max_tokens=2500
            )
            
            content = response.get("content", "")
            
            if content:
                return {
                    "answer": content,
                    "sources": [],
                    "provider": "llm_knowledge",
                    "is_real_time": False
                }
            
            return {
                "answer": "I couldn't generate a response. Please try again.",
                "sources": [],
                "provider": "error",
                "is_real_time": False
            }
        
        except Exception as e:
            print(f"LLM fallback error: {e}")
            return {
                "answer": f"I encountered an error while processing your request. Please try again.",
                "sources": [],
                "provider": "error",
                "is_real_time": False
            }
    
    async def search(self, query: str, num_results: int = 10) -> SearchResponse:
        """
        Traditional search returning structured results.
        """
        result = await self.smart_search(query)
        
        answer = result.get("answer", "")
        sources = result.get("sources", [])
        
        # Convert to SearchResult objects
        results = []
        if answer:
            results.append(SearchResult(
                title=f"Answer: {query[:50]}",
                url="",
                snippet=answer[:500],
                source=result.get("provider", "unknown"),
                relevance_score=1.0
            ))
        
        for i, source in enumerate(sources[:5]):
            if isinstance(source, str):
                results.append(SearchResult(
                    title=f"Source {i+1}",
                    url=source,
                    snippet="",
                    source="citation",
                    relevance_score=0.9 - (i * 0.1)
                ))
        
        return SearchResponse(
            query=query,
            results=results,
            total_results=len(results),
            provider=result.get("provider", "unknown"),
            summary=answer[:500] if answer else None,
            answer=answer
        )


# Global search instance
_search_system: Optional[MultiProviderSearch] = None


def get_search_system(llm_provider=None) -> MultiProviderSearch:
    """Get or create the global search system."""
    global _search_system
    if _search_system is None:
        _search_system = MultiProviderSearch(llm_provider)
    return _search_system
