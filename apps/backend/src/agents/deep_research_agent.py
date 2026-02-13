"""
Deep Research Agent — Comprehensive Multi-Source Research
==========================================================

Performs comprehensive research across multiple sources:
- Web search across multiple providers
- Content extraction and analysis
- Information synthesis
- Source attribution
- Report generation
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional, Set
import openai

logger = logging.getLogger(__name__)


@dataclass
class ResearchSource:
    """A source of research information."""
    title: str
    url: str
    content: str
    source_type: str  # "web", "academic", "news", "social"
    relevance_score: float = 0.0
    date_published: Optional[str] = None
    author: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "url": self.url,
            "content": self.content[:500] + "..." if len(self.content) > 500 else self.content,
            "source_type": self.source_type,
            "relevance_score": self.relevance_score,
            "date_published": self.date_published,
            "author": self.author,
        }


@dataclass
class ResearchFinding:
    """A finding from research."""
    topic: str
    key_points: List[str]
    supporting_sources: List[str]  # source URLs
    confidence: str  # "high", "medium", "low"
    
    def to_dict(self) -> Dict:
        return {
            "topic": self.topic,
            "key_points": self.key_points,
            "supporting_sources": self.supporting_sources,
            "confidence": self.confidence,
        }


@dataclass
class ResearchReport:
    """A comprehensive research report."""
    report_id: str
    query: str
    executive_summary: str
    findings: List[ResearchFinding]
    sources: List[ResearchSource]
    recommendations: List[str]
    gaps: List[str]  # Areas where information was insufficient
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "report_id": self.report_id,
            "query": self.query,
            "executive_summary": self.executive_summary,
            "findings": [f.to_dict() for f in self.findings],
            "sources": [s.to_dict() for s in self.sources],
            "recommendations": self.recommendations,
            "gaps": self.gaps,
            "metadata": self.metadata,
        }


class DeepResearchAgent:
    """
    AI Deep Research Agent for comprehensive research.
    
    Usage:
        agent = DeepResearchAgent(llm_client, search_tools)
        async for event in agent.research("Latest developments in quantum computing"):
            print(event)
    """
    
    def __init__(
        self,
        llm_client: openai.AsyncOpenAI,
        search_tools: Optional[Any] = None,
        model: str = "kimi-k2.5",
        max_sources: int = 20,
    ):
        self.llm_client = llm_client
        self.search_tools = search_tools
        self.model = model
        self.max_sources = max_sources
        
        # Track active research
        self._research_reports: Dict[str, ResearchReport] = {}
    
    async def research(
        self,
        query: str,
        depth: str = "comprehensive",  # "quick", "standard", "comprehensive"
        focus_areas: Optional[List[str]] = None,
        exclude_sources: Optional[List[str]] = None,
        time_range: Optional[str] = None,  # "day", "week", "month", "year", "all"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Perform comprehensive research on a topic.
        
        Args:
            query: Research query/topic
            depth: Research depth level
            focus_areas: Specific areas to focus on
            exclude_sources: Sources to exclude
            time_range: Time range for sources
            
        Yields:
            Progress events and final research report
        """
        import uuid
        report_id = str(uuid.uuid4())
        
        yield {"type": "start", "data": {"report_id": report_id, "query": query, "depth": depth}}
        
        try:
            # Step 1: Analyze query and plan research
            yield {"type": "phase", "data": {"phase": "planning", "status": "started"}}
            
            research_plan = await self._create_research_plan(query, depth, focus_areas)
            
            yield {
                "type": "phase",
                "data": {
                    "phase": "planning",
                    "status": "completed",
                    "sub_queries": len(research_plan.get("sub_queries", [])),
                }
            }
            
            # Step 2: Execute searches
            yield {"type": "phase", "data": {"phase": "searching", "status": "started"}}
            
            all_sources = []
            sub_queries = research_plan.get("sub_queries", [query])
            
            for i, sub_query in enumerate(sub_queries):
                yield {"type": "progress", "data": {"search": i + 1, "total": len(sub_queries), "query": sub_query}}
                
                sources = await self._execute_search(sub_query, time_range)
                all_sources.extend(sources)
                
                # Deduplicate by URL
                seen_urls = set()
                unique_sources = []
                for s in all_sources:
                    if s.url not in seen_urls:
                        seen_urls.add(s.url)
                        unique_sources.append(s)
                all_sources = unique_sources
                
                # Limit sources
                if len(all_sources) >= self.max_sources:
                    all_sources = all_sources[:self.max_sources]
                    break
            
            yield {
                "type": "phase",
                "data": {
                    "phase": "searching",
                    "status": "completed",
                    "sources_found": len(all_sources),
                }
            }
            
            # Step 3: Extract and analyze content
            yield {"type": "phase", "data": {"phase": "analysis", "status": "started"}}
            
            for i, source in enumerate(all_sources):
                yield {"type": "progress", "data": {"analyzing": i + 1, "total": len(all_sources)}}
                
                # Extract and summarize content
                source.content = await self._extract_content(source.url)
                source.relevance_score = await self._calculate_relevance(source, query)
            
            # Sort by relevance
            all_sources.sort(key=lambda s: s.relevance_score, reverse=True)
            
            yield {"type": "phase", "data": {"phase": "analysis", "status": "completed"}}
            
            # Step 4: Synthesize findings
            yield {"type": "phase", "data": {"phase": "synthesis", "status": "started"}}
            
            findings = await self._synthesize_findings(all_sources, query, focus_areas)
            executive_summary = await self._generate_executive_summary(findings, query)
            recommendations = await self._generate_recommendations(findings, query)
            gaps = await self._identify_gaps(findings, query, focus_areas)
            
            yield {"type": "phase", "data": {"phase": "synthesis", "status": "completed"}}
            
            # Step 5: Create research report
            report = ResearchReport(
                report_id=report_id,
                query=query,
                executive_summary=executive_summary,
                findings=findings,
                sources=all_sources,
                recommendations=recommendations,
                gaps=gaps,
                metadata={
                    "depth": depth,
                    "focus_areas": focus_areas or [],
                    "time_range": time_range,
                    "num_sources": len(all_sources),
                },
            )
            self._research_reports[report_id] = report
            
            yield {
                "type": "complete",
                "data": {
                    "report_id": report_id,
                    "query": query,
                    "sources": len(all_sources),
                    "findings": len(findings),
                    "report": report.to_dict(),
                }
            }
            
        except Exception as e:
            logger.error(f"Error performing research: {e}")
            yield {"type": "error", "data": {"message": str(e)}}
    
    async def _create_research_plan(
        self,
        query: str,
        depth: str,
        focus_areas: Optional[List[str]],
    ) -> Dict:
        """Create a research plan with sub-queries."""
        num_queries = {"quick": 2, "standard": 4, "comprehensive": 8}.get(depth, 4)
        
        messages = [
            {
                "role": "system",
                "content": f"""Create a research plan for the query.

Depth: {depth}
Number of sub-queries needed: {num_queries}
Focus areas: {json.dumps(focus_areas or [])}

Break down the main query into {num_queries} specific sub-queries that will help gather comprehensive information.

Respond with JSON:
{{
    "sub_queries": ["query1", "query2", ...],
    "reasoning": "explanation of approach"
}}"""
            },
            {
                "role": "user",
                "content": f"Main query: {query}"
            }
        ]
        
        response = await self.llm_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.5,
            max_tokens=1024,
            response_format={"type": "json_object"},
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _execute_search(
        self,
        query: str,
        time_range: Optional[str],
    ) -> List[ResearchSource]:
        """Execute a search and return sources."""
        sources = []
        
        # If search tools available, use them
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(query)
                for result in search_results:
                    sources.append(ResearchSource(
                        title=result.get("title", ""),
                        url=result.get("url", ""),
                        content="",  # Will be extracted later
                        source_type="web",
                    ))
            except Exception as e:
                logger.warning(f"Search tools error: {e}")
        
        # Fallback: simulate search results for demonstration
        if not sources:
            # This would be replaced with actual search API calls
            sources = [
                ResearchSource(
                    title=f"Search result for: {query}",
                    url=f"https://example.com/search?q={query.replace(' ', '+')}",
                    content="",
                    source_type="web",
                )
            ]
        
        return sources
    
    async def _extract_content(self, url: str) -> str:
        """Extract content from a URL."""
        # If search tools have fetch capability, use it
        if self.search_tools and hasattr(self.search_tools, 'fetch_url'):
            try:
                content = await self.search_tools.fetch_url(url)
                return content
            except Exception as e:
                logger.warning(f"Content extraction error for {url}: {e}")
        
        # Fallback: return placeholder
        return f"[Content from {url}]"
    
    async def _calculate_relevance(self, source: ResearchSource, query: str) -> float:
        """Calculate relevance score for a source."""
        messages = [
            {
                "role": "system",
                "content": """Rate the relevance of this source to the query.

Respond with a number from 0 to 1, where 1 is highly relevant."""
            },
            {
                "role": "user",
                "content": f"Query: {query}\n\nSource title: {source.title}\nSource content: {source.content[:1000]}"
            }
        ]
        
        try:
            response = await self.llm_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=100,
            )
            
            score_text = response.choices[0].message.content.strip()
            # Extract number from response
            import re
            match = re.search(r'[\d.]+', score_text)
            if match:
                return float(match.group())
        except Exception as e:
            logger.warning(f"Relevance calculation error: {e}")
        
        return 0.5  # Default score
    
    async def _synthesize_findings(
        self,
        sources: List[ResearchSource],
        query: str,
        focus_areas: Optional[List[str]],
    ) -> List[ResearchFinding]:
        """Synthesize findings from sources."""
        # Prepare source summaries
        source_summaries = []
        for s in sources[:10]:  # Limit to top 10 sources
            source_summaries.append({
                "title": s.title,
                "url": s.url,
                "content": s.content[:2000],
            })
        
        messages = [
            {
                "role": "system",
                "content": f"""Synthesize findings from the research sources.

Original query: {query}
Focus areas: {json.dumps(focus_areas or [])}

Identify key findings, themes, and insights from the sources.

Respond with JSON:
{{
    "findings": [
        {{
            "topic": "Finding topic",
            "key_points": ["point 1", "point 2", "point 3"],
            "supporting_sources": ["url1", "url2"],
            "confidence": "high|medium|low"
        }}
    ]
}}"""
            },
            {
                "role": "user",
                "content": f"Sources: {json.dumps(source_summaries)}"
            }
        ]
        
        response = await self.llm_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.5,
            max_tokens=4096,
            response_format={"type": "json_object"},
        )
        
        result = json.loads(response.choices[0].message.content)
        findings_data = result.get("findings", [])
        
        findings = []
        for f in findings_data:
            findings.append(ResearchFinding(
                topic=f.get("topic", ""),
                key_points=f.get("key_points", []),
                supporting_sources=f.get("supporting_sources", []),
                confidence=f.get("confidence", "medium"),
            ))
        
        return findings
    
    async def _generate_executive_summary(
        self,
        findings: List[ResearchFinding],
        query: str,
    ) -> str:
        """Generate an executive summary."""
        findings_text = json.dumps([f.to_dict() for f in findings])
        
        messages = [
            {
                "role": "system",
                "content": "Generate a concise executive summary of the research findings."
            },
            {
                "role": "user",
                "content": f"Query: {query}\n\nFindings: {findings_text}"
            }
        ]
        
        response = await self.llm_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        
        return response.choices[0].message.content
    
    async def _generate_recommendations(
        self,
        findings: List[ResearchFinding],
        query: str,
    ) -> List[str]:
        """Generate recommendations based on findings."""
        findings_text = json.dumps([f.to_dict() for f in findings])
        
        messages = [
            {
                "role": "system",
                "content": """Based on the research findings, generate actionable recommendations.

Respond with JSON:
{
    "recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"]
}"""
            },
            {
                "role": "user",
                "content": f"Query: {query}\n\nFindings: {findings_text}"
            }
        ]
        
        response = await self.llm_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            response_format={"type": "json_object"},
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("recommendations", [])
    
    async def _identify_gaps(
        self,
        findings: List[ResearchFinding],
        query: str,
        focus_areas: Optional[List[str]],
    ) -> List[str]:
        """Identify gaps in the research."""
        messages = [
            {
                "role": "system",
                "content": """Identify gaps or areas where more information would be beneficial.

Respond with JSON:
{
    "gaps": ["gap 1", "gap 2"]
}"""
            },
            {
                "role": "user",
                "content": f"Query: {query}\nFocus areas: {json.dumps(focus_areas or [])}\nFindings: {json.dumps([f.to_dict() for f in findings])}"
            }
        ]
        
        response = await self.llm_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.5,
            max_tokens=1024,
            response_format={"type": "json_object"},
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("gaps", [])
    
    def get_report(self, report_id: str) -> Optional[ResearchReport]:
        """Get a research report by ID."""
        return self._research_reports.get(report_id)


# Singleton instance
_research_agent: Optional[DeepResearchAgent] = None


def get_research_agent(
    llm_client: openai.AsyncOpenAI = None,
    search_tools: Any = None,
) -> Optional[DeepResearchAgent]:
    """Get or create the Deep Research Agent singleton."""
    global _research_agent
    if _research_agent is None and llm_client:
        _research_agent = DeepResearchAgent(llm_client, search_tools)
    return _research_agent
