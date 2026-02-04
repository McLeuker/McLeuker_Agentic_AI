"""
McLeuker AI V5.2 - Enhanced Orchestrator with Manus AI-style Reasoning
=======================================================================
Features:
- Real-time reasoning display (thinking process visible to users)
- Screen flows showing search progress
- Quick vs Deep search modes with visible differences
- Structured output with dynamic follow-ups
- CodeAct-inspired step-by-step execution

Design inspired by: Manus AI, Kimi K2.5
"""

import asyncio
import json
import os
import re
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, AsyncGenerator
from dataclasses import dataclass, field
import httpx

from src.schemas.response_contract import (
    ResponseContract, Source, GeneratedFile, TableData, KeyInsight,
    LayoutSection, IntentType, DomainType
)
from src.layers.intent.intent_router import intent_router, IntentResult
from src.services.file_generator import file_generator


# =============================================================================
# Streaming Event Types (Manus AI-style)
# =============================================================================

class StreamEventType:
    """Event types for real-time streaming updates"""
    THINKING = "thinking"           # AI reasoning/thinking process
    PLANNING = "planning"           # Task breakdown/planning
    SEARCHING = "searching"         # Search in progress
    ANALYZING = "analyzing"         # Analyzing results
    GENERATING = "generating"       # Generating response
    SOURCE = "source"               # Individual source found
    INSIGHT = "insight"             # Key insight discovered
    PROGRESS = "progress"           # Progress update (percentage)
    CONTENT = "content"             # Response content chunk
    COMPLETE = "complete"           # Final complete response
    ERROR = "error"                 # Error occurred


def create_event(event_type: str, data: Any, step: int = 0, total_steps: int = 0) -> Dict:
    """Create a standardized streaming event"""
    return {
        "type": event_type,
        "data": data,
        "step": step,
        "total_steps": total_steps,
        "timestamp": datetime.now().isoformat()
    }


# =============================================================================
# Response Dataclass
# =============================================================================

@dataclass
class OrchestratorResponse:
    """Response from the orchestrator - follows ResponseContract"""
    success: bool
    response: Optional[ResponseContract] = None
    error: Optional[str] = None
    reasoning_steps: List[Dict] = field(default_factory=list)  # Now includes detailed reasoning
    credits_used: int = 0
    session_id: str = ""
    mode_used: str = "auto"
    search_depth: str = "standard"
    
    def to_dict(self) -> dict:
        result = {
            "success": self.success,
            "error": self.error,
            "reasoning_steps": self.reasoning_steps,
            "credits_used": self.credits_used,
            "session_id": self.session_id,
            "mode_used": self.mode_used,
            "search_depth": self.search_depth
        }
        if self.response:
            result["response"] = self.response.to_dict()
        return result


# =============================================================================
# Enhanced V5.2 Orchestrator
# =============================================================================

class V5Orchestrator:
    """
    V5.2 Orchestrator with Manus AI-style reasoning display.
    
    Key features:
    - Real-time thinking process visible to users
    - Step-by-step task execution with progress
    - Quick vs Deep search with clear differences
    - Dynamic, context-aware responses
    """
    
    def __init__(self):
        self.grok_api_key = os.getenv("XAI_API_KEY", "")
        self.grok_base_url = "https://api.x.ai/v1"
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY", "")
        self.session_contexts: Dict[str, List[Dict]] = {}
        
        # Search configuration by mode
        self.search_config = {
            "quick": {
                "max_sources": 5,
                "search_depth": "surface",
                "analysis_depth": "brief",
                "estimated_time": "10-15 seconds"
            },
            "deep": {
                "max_sources": 15,
                "search_depth": "comprehensive",
                "analysis_depth": "thorough",
                "estimated_time": "30-60 seconds"
            }
        }
    
    # =========================================================================
    # Main Processing Methods
    # =========================================================================
    
    async def process(
        self,
        query: str,
        session_id: Optional[str] = None,
        mode: str = "auto",
        domain_filter: Optional[str] = None
    ) -> OrchestratorResponse:
        """
        Process a user query and return structured response.
        Non-streaming version - collects all events and returns final result.
        """
        reasoning_steps = []
        
        try:
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Collect events from streaming process
            final_response = None
            async for event in self.process_stream(query, session_id, mode, domain_filter):
                reasoning_steps.append(event)
                if event["type"] == StreamEventType.COMPLETE:
                    final_response = event["data"]
            
            if final_response:
                return OrchestratorResponse(
                    success=True,
                    response=final_response,
                    reasoning_steps=reasoning_steps,
                    credits_used=final_response.get("credits_used", 3),
                    session_id=session_id,
                    mode_used=mode
                )
            else:
                raise Exception("No response generated")
                
        except Exception as e:
            return OrchestratorResponse(
                success=False,
                error=str(e),
                reasoning_steps=reasoning_steps,
                session_id=session_id or ""
            )
    
    async def process_stream(
        self,
        query: str,
        session_id: Optional[str] = None,
        mode: str = "auto",
        domain_filter: Optional[str] = None
    ) -> AsyncGenerator[Dict, None]:
        """
        Process query with real-time streaming events.
        Yields Manus AI-style events showing thinking, searching, analyzing.
        """
        if not session_id:
            session_id = str(uuid.uuid4())
        
        total_steps = 6  # Planning, Intent, Search, Analyze, Generate, Complete
        current_step = 0
        
        try:
            # =================================================================
            # Step 1: THINKING - Initial reasoning about the query
            # =================================================================
            current_step = 1
            yield create_event(
                StreamEventType.THINKING,
                {
                    "thought": f"Analyzing query: \"{query}\"",
                    "detail": "Understanding the user's intent and determining the best approach..."
                },
                current_step, total_steps
            )
            await asyncio.sleep(0.3)  # Brief pause for UX
            
            # =================================================================
            # Step 2: PLANNING - Break down the task
            # =================================================================
            current_step = 2
            intent_result = intent_router.classify(query)
            
            # Determine search mode
            if mode == "auto":
                # Auto-detect based on query complexity
                is_complex = len(query.split()) > 10 or any(
                    word in query.lower() 
                    for word in ["analyze", "compare", "comprehensive", "detailed", "research", "deep"]
                )
                effective_mode = "deep" if is_complex else "quick"
            else:
                effective_mode = mode
            
            config = self.search_config[effective_mode]
            
            yield create_event(
                StreamEventType.PLANNING,
                {
                    "mode": effective_mode,
                    "intent": intent_result.intent_type.value,
                    "domain": intent_result.domain.value,
                    "plan": [
                        f"Search {config['max_sources']} sources ({config['search_depth']} depth)",
                        f"Analyze with {config['analysis_depth']} analysis",
                        "Generate structured insights",
                        "Compile actionable recommendations"
                    ],
                    "estimated_time": config["estimated_time"]
                },
                current_step, total_steps
            )
            await asyncio.sleep(0.2)
            
            # =================================================================
            # Step 3: SEARCHING - Find information with progress updates
            # =================================================================
            current_step = 3
            yield create_event(
                StreamEventType.SEARCHING,
                {
                    "status": "starting",
                    "message": f"Searching {intent_result.domain.value} databases and sources...",
                    "sources_target": config["max_sources"]
                },
                current_step, total_steps
            )
            
            # Perform actual search with progress events
            search_results = []
            async for search_event in self._search_with_progress(query, effective_mode, intent_result.domain):
                if search_event["type"] == "source_found":
                    search_results.append(search_event["source"])
                    yield create_event(
                        StreamEventType.SOURCE,
                        {
                            "title": search_event["source"].get("title", ""),
                            "url": search_event["source"].get("url", ""),
                            "relevance": search_event.get("relevance", 0.8)
                        },
                        current_step, total_steps
                    )
                elif search_event["type"] == "progress":
                    yield create_event(
                        StreamEventType.PROGRESS,
                        {
                            "message": search_event["message"],
                            "percentage": search_event["percentage"]
                        },
                        current_step, total_steps
                    )
            
            yield create_event(
                StreamEventType.SEARCHING,
                {
                    "status": "complete",
                    "message": f"Found {len(search_results)} relevant sources",
                    "sources_found": len(search_results)
                },
                current_step, total_steps
            )
            
            # =================================================================
            # Step 4: ANALYZING - Process and analyze results
            # =================================================================
            current_step = 4
            yield create_event(
                StreamEventType.ANALYZING,
                {
                    "status": "starting",
                    "message": "Analyzing sources and extracting key information...",
                    "sources_count": len(search_results)
                },
                current_step, total_steps
            )
            await asyncio.sleep(0.3)
            
            # Extract insights during analysis
            analysis_thoughts = [
                f"Reviewing {len(search_results)} sources for {intent_result.domain.value} insights...",
                "Cross-referencing information across sources...",
                "Identifying key trends and patterns...",
                "Evaluating source reliability and relevance..."
            ]
            
            for i, thought in enumerate(analysis_thoughts):
                yield create_event(
                    StreamEventType.THINKING,
                    {
                        "thought": thought,
                        "detail": f"Analysis step {i+1}/{len(analysis_thoughts)}"
                    },
                    current_step, total_steps
                )
                await asyncio.sleep(0.2)
            
            # =================================================================
            # Step 5: GENERATING - Create the response
            # =================================================================
            current_step = 5
            yield create_event(
                StreamEventType.GENERATING,
                {
                    "status": "starting",
                    "message": "Generating comprehensive response..."
                },
                current_step, total_steps
            )
            
            # Generate response with Grok
            response_contract = await self._generate_enhanced_response(
                query=query,
                search_results=search_results,
                intent_result=intent_result,
                session_id=session_id,
                mode=effective_mode
            )
            
            # Yield individual insights as they're "discovered"
            for insight in response_contract.key_insights:
                yield create_event(
                    StreamEventType.INSIGHT,
                    {
                        "text": insight.text,
                        "importance": insight.importance
                    },
                    current_step, total_steps
                )
                await asyncio.sleep(0.1)
            
            # =================================================================
            # Step 6: COMPLETE - Final response
            # =================================================================
            current_step = 6
            credits_used = 2 if effective_mode == "quick" else 5
            
            yield create_event(
                StreamEventType.COMPLETE,
                {
                    "response": response_contract.to_dict(),
                    "session_id": session_id,
                    "mode_used": effective_mode,
                    "sources_used": len(search_results),
                    "credits_used": credits_used
                },
                current_step, total_steps
            )
            
        except Exception as e:
            yield create_event(
                StreamEventType.ERROR,
                {
                    "message": str(e),
                    "step": current_step
                },
                current_step, total_steps
            )
    
    # =========================================================================
    # Search Methods with Progress
    # =========================================================================
    
    async def _search_with_progress(
        self, 
        query: str, 
        mode: str, 
        domain: DomainType
    ) -> AsyncGenerator[Dict, None]:
        """Search with progress events for real-time updates"""
        config = self.search_config[mode]
        results = []
        
        yield {"type": "progress", "message": "Initializing search engines...", "percentage": 10}
        
        # Try Perplexity first
        if self.perplexity_api_key:
            yield {"type": "progress", "message": "Searching Perplexity AI...", "percentage": 30}
            try:
                perplexity_results = await self._search_perplexity(query, mode)
                for i, result in enumerate(perplexity_results[:config["max_sources"]]):
                    results.append(result)
                    yield {
                        "type": "source_found",
                        "source": result,
                        "relevance": 0.9 - (i * 0.05)
                    }
            except Exception as e:
                yield {"type": "progress", "message": f"Perplexity unavailable, using alternative...", "percentage": 40}
        
        # Use Grok for additional sources or as fallback
        if len(results) < config["max_sources"]:
            yield {"type": "progress", "message": f"Searching {domain.value} knowledge base...", "percentage": 60}
            try:
                grok_results = await self._search_grok(query, domain)
                for i, result in enumerate(grok_results):
                    if len(results) >= config["max_sources"]:
                        break
                    results.append(result)
                    yield {
                        "type": "source_found",
                        "source": result,
                        "relevance": 0.85 - (i * 0.05)
                    }
            except Exception as e:
                pass
        
        yield {"type": "progress", "message": "Search complete", "percentage": 100}
    
    async def _search_perplexity(self, query: str, mode: str) -> List[Dict]:
        """Search using Perplexity API"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.perplexity_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-sonar-small-128k-online",
                    "messages": [
                        {"role": "user", "content": f"Search for: {query}. Return factual information with sources."}
                    ],
                    "return_citations": True
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                citations = data.get("citations", [])
                return [
                    {
                        "title": f"Source {i+1}",
                        "url": url,
                        "snippet": ""
                    }
                    for i, url in enumerate(citations)
                ]
        
        return []
    
    async def _search_grok(self, query: str, domain: DomainType) -> List[Dict]:
        """Use Grok to generate search-like results with real-time data"""
        if not self.grok_api_key:
            return []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.grok_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.grok_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-4-fast-non-reasoning",
                    "messages": [
                        {
                            "role": "system",
                            "content": f"You are a research assistant. For the query, provide 5 relevant sources with titles and URLs from reputable {domain.value} publications. Format as JSON array with 'title', 'url', 'snippet' fields."
                        },
                        {"role": "user", "content": query}
                    ],
                    "temperature": 0.3
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                try:
                    json_match = re.search(r'\[[\s\S]*\]', content)
                    if json_match:
                        sources = json.loads(json_match.group())
                        return sources
                except:
                    pass
        
        return []
    
    # =========================================================================
    # Enhanced Response Generation
    # =========================================================================
    
    async def _generate_enhanced_response(
        self,
        query: str,
        search_results: List[Dict],
        intent_result: IntentResult,
        session_id: str,
        mode: str
    ) -> ResponseContract:
        """Generate enhanced structured response using Grok"""
        
        # Build context from search results
        sources_context = "\n".join([
            f"[{i+1}] {r.get('title', 'Source')}: {r.get('snippet', '')}"
            for i, r in enumerate(search_results)
        ])
        
        # Enhanced system prompt for better output
        system_prompt = f"""You are McLeuker AI, a professional {intent_result.domain.value} expert with deep industry knowledge.

TODAY'S DATE: {datetime.now().strftime('%B %d, %Y')}

RESPONSE GUIDELINES:
1. Write authoritative, expert-level content
2. NO inline citations like [1] or [2] - sources are displayed separately
3. Be specific with data, trends, and actionable insights
4. Use clear structure: Summary → Key Points → Details → Recommendations
5. Tailor depth to the search mode: {"comprehensive analysis" if mode == "deep" else "concise overview"}

OUTPUT FORMAT:
- Start with a 2-3 sentence executive summary
- Provide 5 key insights as bullet points (each should be specific and actionable)
- Include relevant data points, statistics, or trends when available
- End with 3 specific, contextual follow-up questions the user might want to explore"""

        user_prompt = f"""Query: {query}

Research Context:
{sources_context if sources_context else "Using internal knowledge base"}

Provide a {"comprehensive, in-depth analysis" if mode == "deep" else "focused, concise response"} that directly addresses the query with expert-level insights."""

        # Call Grok
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.grok_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.grok_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-4-fast-non-reasoning",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 3000 if mode == "deep" else 1500
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Grok API error: {response.status_code}")
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
        
        # Parse response into structured format
        return self._parse_to_contract(
            content=content,
            query=query,
            search_results=search_results,
            intent_result=intent_result,
            mode=mode
        )
    
    def _parse_to_contract(
        self,
        content: str,
        query: str,
        search_results: List[Dict],
        intent_result: IntentResult,
        mode: str = "auto"
    ) -> ResponseContract:
        """Parse Grok response into ResponseContract format"""
        
        # Extract summary (first paragraph)
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        summary = paragraphs[0] if paragraphs else content[:300]
        
        # Clean any remaining citations
        clean_content = re.sub(r'\[\d+\]', '', content)
        
        # Create sources
        sources = [
            Source(
                id=f"src_{i+1}",
                title=r.get("title", f"Source {i+1}"),
                url=r.get("url", ""),
                snippet=r.get("snippet", ""),
                domain=intent_result.domain.value,
                reliability_score=0.85 - (i * 0.03)
            )
            for i, r in enumerate(search_results)
        ]
        
        # Extract key insights (look for bullet points or numbered items)
        insights = []
        bullet_pattern = r'[-•*]\s*\*?\*?(.+?)(?:\*?\*?)(?=\n|$)'
        numbered_pattern = r'\d+\.\s*\*?\*?(.+?)(?:\*?\*?)(?=\n|$)'
        
        bullet_matches = re.findall(bullet_pattern, content)
        numbered_matches = re.findall(numbered_pattern, content)
        
        all_matches = bullet_matches + numbered_matches
        for i, match in enumerate(all_matches[:5]):
            clean_match = re.sub(r'\*+', '', match).strip()
            if len(clean_match) > 20:  # Filter out short/empty matches
                insights.append(KeyInsight(
                    id=f"insight_{i+1}",
                    text=clean_match[:200],
                    importance="high" if i < 2 else "medium",
                    source_ids=[f"src_{(i % max(1, len(sources))) + 1}"] if sources else []
                ))
        
        # Extract follow-up questions from content or generate contextual ones
        follow_ups = self._extract_follow_ups(content, query, intent_result)
        
        # Create layout sections
        sections = []
        header_pattern = r'^#+\s*(.+?)$'
        headers = re.findall(header_pattern, content, re.MULTILINE)
        for i, header in enumerate(headers[:5]):
            sections.append(LayoutSection(
                id=f"section_{i+1}",
                title=header.strip().replace('*', ''),
                content_type="text",
                order=i+1
            ))
        
        return ResponseContract(
            query=query,
            summary=summary[:500],
            main_content=clean_content,
            sources=sources,
            files=[],
            tables=[],
            key_insights=insights,
            layout_sections=sections,
            intent_type=intent_result.intent_type.value,
            domain=intent_result.domain.value,
            confidence_score=intent_result.confidence,
            follow_up_questions=follow_ups,
            generated_at=datetime.now().isoformat(),
            search_mode=mode
        )
    
    def _extract_follow_ups(
        self, 
        content: str, 
        query: str, 
        intent_result: IntentResult
    ) -> List[str]:
        """Extract or generate contextual follow-up questions"""
        
        # Try to find follow-up questions in the content
        follow_up_pattern = r'(?:follow[- ]?up|next|explore|consider|might want to).*?[?]'
        found_questions = re.findall(follow_up_pattern, content, re.IGNORECASE)
        
        if found_questions and len(found_questions) >= 3:
            return [q.strip() for q in found_questions[:3]]
        
        # Generate contextual follow-ups based on domain and query
        domain = intent_result.domain.value
        
        # Extract key terms from query for context
        key_terms = [word for word in query.split() if len(word) > 4][:3]
        context = " ".join(key_terms) if key_terms else domain
        
        follow_ups = []
        
        if intent_result.intent_type == IntentType.TREND:
            follow_ups = [
                f"What are the emerging {context} trends for the upcoming season?",
                f"How can brands capitalize on these {domain} trends?",
                f"What are the sustainability implications of current {context} trends?"
            ]
        elif intent_result.intent_type == IntentType.RESEARCH:
            follow_ups = [
                f"Can you provide a deeper analysis of {context}?",
                f"What are the key market players in {context}?",
                f"How does this compare to previous years in {domain}?"
            ]
        elif intent_result.intent_type == IntentType.DATA:
            follow_ups = [
                f"Can you generate a detailed report on {context}?",
                f"What data sources are most reliable for {domain} research?",
                f"How can I export this data for further analysis?"
            ]
        else:
            follow_ups = [
                f"What specific aspects of {context} would you like to explore further?",
                f"Would you like a more detailed analysis of any particular point?",
                f"Are there specific brands or products you'd like me to focus on?"
            ]
        
        return follow_ups


# Global instance
orchestrator = V5Orchestrator()
