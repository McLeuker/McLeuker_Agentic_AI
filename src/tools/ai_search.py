"""
McLeuker Agentic AI Platform - AI Search Platform

Advanced AI-powered search capability similar to Manus AI.
Provides intelligent search, query expansion, and result synthesis.
"""

import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from src.models.schemas import SearchResult, WebResearchResult
from src.layers.web_research import (
    WebSearchProvider,
    SerperSearchProvider,
    TavilySearchProvider,
    DuckDuckGoSearchProvider,
    WebScraper
)
from src.utils.llm_provider import LLMProvider, LLMFactory
from src.config.settings import get_settings


class SearchType(str, Enum):
    """Types of search."""
    GENERAL = "general"
    NEWS = "news"
    ACADEMIC = "academic"
    IMAGES = "images"
    PRODUCTS = "products"
    LOCAL = "local"


class AISearchPlatform:
    """
    AI-Powered Search Platform
    
    Provides advanced search capabilities with:
    - Multi-source search
    - Query expansion and optimization
    - Result ranking and filtering
    - Content summarization
    - Follow-up question generation
    """
    
    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        search_provider: Optional[WebSearchProvider] = None
    ):
        """Initialize the AI Search Platform."""
        self.llm = llm_provider or LLMFactory.get_default()
        self.search_provider = search_provider or self._get_default_search_provider()
        self.scraper = WebScraper()
        self.settings = get_settings()
    
    def _get_default_search_provider(self) -> WebSearchProvider:
        """Get the default search provider."""
        settings = get_settings()
        if settings.SERPER_API_KEY:
            return SerperSearchProvider()
        elif settings.TAVILY_API_KEY:
            return TavilySearchProvider()
        else:
            return DuckDuckGoSearchProvider()
    
    async def search(
        self,
        query: str,
        search_type: SearchType = SearchType.GENERAL,
        num_results: int = 10,
        expand_query: bool = True,
        summarize: bool = True,
        scrape_top: int = 0
    ) -> Dict[str, Any]:
        """
        Perform an AI-powered search.
        
        Args:
            query: The search query
            search_type: Type of search to perform
            num_results: Number of results to return
            expand_query: Whether to expand the query
            summarize: Whether to summarize results
            scrape_top: Number of top results to scrape (0 = none)
            
        Returns:
            Dict containing search results and analysis
        """
        # Step 1: Analyze and expand query
        query_analysis = await self._analyze_query(query)
        
        expanded_queries = [query]
        if expand_query:
            expanded_queries = await self._expand_query(query, query_analysis)
        
        # Step 2: Perform searches
        all_results = []
        for q in expanded_queries[:3]:  # Limit to 3 query variants
            results = await self.search_provider.search(q, num_results)
            all_results.extend(results)
        
        # Step 3: Deduplicate and rank results
        unique_results = self._deduplicate_results(all_results)
        ranked_results = await self._rank_results(unique_results, query)
        
        # Step 4: Scrape top results if requested
        scraped_content = []
        if scrape_top > 0:
            urls_to_scrape = [r.url for r in ranked_results[:scrape_top]]
            scraped_content = await self.scraper.scrape_multiple(urls_to_scrape)
        
        # Step 5: Generate summary if requested
        summary = None
        if summarize:
            summary = await self._summarize_results(
                query,
                ranked_results[:10],
                scraped_content
            )
        
        # Step 6: Generate follow-up questions
        follow_ups = await self._generate_follow_ups(query, summary or "")
        
        return {
            "query": query,
            "query_analysis": query_analysis,
            "expanded_queries": expanded_queries,
            "results": [r.dict() for r in ranked_results[:num_results]],
            "total_results": len(ranked_results),
            "summary": summary,
            "follow_up_questions": follow_ups,
            "scraped_content": [s.dict() for s in scraped_content] if scraped_content else None,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze the search query to understand intent and context."""
        messages = [
            {
                "role": "system",
                "content": """Analyze the search query and extract:
1. Main intent (what the user wants to find)
2. Key entities (people, places, things, concepts)
3. Query type (informational, navigational, transactional)
4. Domain/topic area
5. Time sensitivity (is recent information important?)

Respond in JSON format."""
            },
            {
                "role": "user",
                "content": f"Analyze this search query: {query}"
            }
        ]
        
        response = await self.llm.complete_with_structured_output(
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        return response.get("content", {})
    
    async def _expand_query(
        self,
        query: str,
        analysis: Dict[str, Any]
    ) -> List[str]:
        """Expand the query into multiple search variants."""
        messages = [
            {
                "role": "system",
                "content": """Generate 3 alternative search queries that will help find comprehensive information.
Each query should approach the topic from a different angle.
Include the original query as the first item.

Respond with a JSON object containing a "queries" array."""
            },
            {
                "role": "user",
                "content": f"""Original query: {query}

Query analysis: {analysis}

Generate alternative search queries."""
            }
        ]
        
        response = await self.llm.complete_with_structured_output(
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.5
        )
        
        content = response.get("content", {})
        queries = content.get("queries", [query])
        
        # Ensure original query is first
        if query not in queries:
            queries.insert(0, query)
        
        return queries[:4]
    
    def _deduplicate_results(
        self,
        results: List[SearchResult]
    ) -> List[SearchResult]:
        """Remove duplicate results based on URL."""
        seen_urls = set()
        unique = []
        
        for result in results:
            # Normalize URL
            url = result.url.rstrip('/').lower()
            if url not in seen_urls:
                seen_urls.add(url)
                unique.append(result)
        
        return unique
    
    async def _rank_results(
        self,
        results: List[SearchResult],
        query: str
    ) -> List[SearchResult]:
        """Rank results by relevance to the query."""
        if len(results) <= 5:
            return results
        
        # Use LLM to rank top results
        results_text = "\n".join([
            f"{i+1}. {r.title}: {r.snippet[:100]}"
            for i, r in enumerate(results[:15])
        ])
        
        messages = [
            {
                "role": "system",
                "content": """Rank the search results by relevance to the query.
Return a JSON object with a "ranking" array containing the result numbers in order of relevance.
Only include the numbers, most relevant first."""
            },
            {
                "role": "user",
                "content": f"""Query: {query}

Results:
{results_text}

Rank these results by relevance."""
            }
        ]
        
        try:
            response = await self.llm.complete_with_structured_output(
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            content = response.get("content", {})
            ranking = content.get("ranking", list(range(1, len(results) + 1)))
            
            # Reorder results based on ranking
            ranked = []
            for idx in ranking:
                if 1 <= idx <= len(results):
                    ranked.append(results[idx - 1])
            
            # Add any results not in ranking
            ranked_urls = {r.url for r in ranked}
            for result in results:
                if result.url not in ranked_urls:
                    ranked.append(result)
            
            return ranked
        except Exception:
            return results
    
    async def _summarize_results(
        self,
        query: str,
        results: List[SearchResult],
        scraped_content: List[Any]
    ) -> str:
        """Generate a summary of the search results."""
        # Build context from results
        context_parts = [f"Query: {query}\n"]
        
        for i, result in enumerate(results[:10], 1):
            context_parts.append(f"{i}. {result.title}")
            context_parts.append(f"   {result.snippet}")
        
        if scraped_content:
            context_parts.append("\n--- Detailed Content ---")
            for content in scraped_content[:3]:
                context_parts.append(f"\nSource: {content.title or content.url}")
                context_parts.append(content.content[:1500])
        
        context = "\n".join(context_parts)
        
        messages = [
            {
                "role": "system",
                "content": """You are an AI search assistant. Provide a comprehensive summary of the search results.

Your summary should:
1. Directly answer the query if possible
2. Highlight key findings from multiple sources
3. Note any conflicting information
4. Be concise but informative
5. Cite sources where appropriate

Format the response in clear paragraphs."""
            },
            {
                "role": "user",
                "content": f"Summarize these search results:\n\n{context}"
            }
        ]
        
        response = await self.llm.complete(
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )
        
        return response.get("content", "")
    
    async def _generate_follow_ups(
        self,
        query: str,
        summary: str
    ) -> List[str]:
        """Generate follow-up questions based on the search."""
        messages = [
            {
                "role": "system",
                "content": """Generate 3 relevant follow-up questions that the user might want to explore next.
Questions should be specific and actionable.

Respond with a JSON object containing a "questions" array."""
            },
            {
                "role": "user",
                "content": f"""Original query: {query}

Summary of findings: {summary[:500]}

Generate follow-up questions."""
            }
        ]
        
        response = await self.llm.complete_with_structured_output(
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.5
        )
        
        content = response.get("content", {})
        return content.get("questions", [])[:3]
    
    async def quick_answer(self, query: str) -> Dict[str, Any]:
        """
        Get a quick answer to a query with minimal latency.
        
        Args:
            query: The question to answer
            
        Returns:
            Dict containing the answer and sources
        """
        # Perform a quick search
        results = await self.search_provider.search(query, num_results=5)
        
        if not results:
            return {
                "query": query,
                "answer": "I couldn't find relevant information for your query.",
                "sources": [],
                "confidence": "low"
            }
        
        # Generate quick answer
        context = "\n".join([
            f"- {r.title}: {r.snippet}"
            for r in results[:5]
        ])
        
        messages = [
            {
                "role": "system",
                "content": """Provide a direct, concise answer to the question based on the search results.
If the answer is uncertain, say so.
Keep the response under 200 words."""
            },
            {
                "role": "user",
                "content": f"""Question: {query}

Search results:
{context}

Provide a direct answer."""
            }
        ]
        
        response = await self.llm.complete(
            messages=messages,
            temperature=0.2,
            max_tokens=300
        )
        
        return {
            "query": query,
            "answer": response.get("content", ""),
            "sources": [{"title": r.title, "url": r.url} for r in results[:3]],
            "confidence": "high" if len(results) >= 3 else "medium"
        }
    
    async def research_topic(
        self,
        topic: str,
        depth: str = "medium"
    ) -> Dict[str, Any]:
        """
        Perform in-depth research on a topic.
        
        Args:
            topic: The topic to research
            depth: Research depth (light, medium, deep)
            
        Returns:
            Comprehensive research results
        """
        # Generate research questions
        questions = await self._generate_research_questions(topic, depth)
        
        # Search for each question
        all_findings = []
        for question in questions:
            result = await self.search(
                question,
                expand_query=False,
                summarize=True,
                scrape_top=1 if depth == "deep" else 0
            )
            all_findings.append({
                "question": question,
                "summary": result.get("summary", ""),
                "sources": result.get("results", [])[:3]
            })
        
        # Synthesize all findings
        synthesis = await self._synthesize_research(topic, all_findings)
        
        return {
            "topic": topic,
            "depth": depth,
            "research_questions": questions,
            "findings": all_findings,
            "synthesis": synthesis,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _generate_research_questions(
        self,
        topic: str,
        depth: str
    ) -> List[str]:
        """Generate research questions for a topic."""
        num_questions = {"light": 2, "medium": 4, "deep": 6}.get(depth, 4)
        
        messages = [
            {
                "role": "system",
                "content": f"""Generate {num_questions} research questions to thoroughly understand the topic.
Questions should cover different aspects: definition, current state, trends, challenges, and future outlook.

Respond with a JSON object containing a "questions" array."""
            },
            {
                "role": "user",
                "content": f"Topic: {topic}"
            }
        ]
        
        response = await self.llm.complete_with_structured_output(
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.5
        )
        
        content = response.get("content", {})
        return content.get("questions", [f"What is {topic}?"])[:num_questions]
    
    async def _synthesize_research(
        self,
        topic: str,
        findings: List[Dict[str, Any]]
    ) -> str:
        """Synthesize all research findings into a coherent summary."""
        findings_text = "\n\n".join([
            f"Q: {f['question']}\nA: {f['summary']}"
            for f in findings
        ])
        
        messages = [
            {
                "role": "system",
                "content": """Synthesize the research findings into a comprehensive overview.
Structure the synthesis with:
1. Overview/Definition
2. Key Points
3. Current Trends
4. Challenges/Considerations
5. Conclusion

Be thorough but concise."""
            },
            {
                "role": "user",
                "content": f"""Topic: {topic}

Research Findings:
{findings_text}

Synthesize these findings."""
            }
        ]
        
        response = await self.llm.complete(
            messages=messages,
            temperature=0.3,
            max_tokens=1500
        )
        
        return response.get("content", "")


# Convenience functions
async def ai_search(
    query: str,
    summarize: bool = True
) -> Dict[str, Any]:
    """Perform an AI-powered search."""
    platform = AISearchPlatform()
    return await platform.search(query, summarize=summarize)


async def quick_answer(query: str) -> Dict[str, Any]:
    """Get a quick answer to a question."""
    platform = AISearchPlatform()
    return await platform.quick_answer(query)


async def research_topic(
    topic: str,
    depth: str = "medium"
) -> Dict[str, Any]:
    """Perform in-depth research on a topic."""
    platform = AISearchPlatform()
    return await platform.research_topic(topic, depth)
