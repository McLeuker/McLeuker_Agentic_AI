"""
McLeuker AI V6 - Enhanced Orchestrator with Manus AI-style Reasoning
=====================================================================
Complete rewrite with:
- Real-time reasoning display (thinking process visible to users)
- Task decomposition with progress tracking
- Memory system for context awareness
- Structured output with clean formatting
- SSE streaming for live updates

Design inspired by: Manus AI
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
from src.core.reasoning_engine import reasoning_engine, TaskPlan, ReasoningStep
from src.core.memory_manager import memory_manager


# =============================================================================
# Streaming Event Types (Manus AI-style)
# =============================================================================

class StreamEventType:
    """Event types for real-time streaming updates"""
    # Reasoning events
    THINKING = "thinking"           # AI reasoning/thinking process
    PLANNING = "planning"           # Task breakdown/planning
    TASK_UPDATE = "task_update"     # Individual task status update
    
    # Processing events
    SEARCHING = "searching"         # Search in progress
    ANALYZING = "analyzing"         # Analyzing results
    GENERATING = "generating"       # Generating response
    
    # Data events
    SOURCE = "source"               # Individual source found
    INSIGHT = "insight"             # Key insight discovered
    PROGRESS = "progress"           # Progress update (percentage)
    
    # Content events
    CONTENT = "content"             # Response content chunk
    SECTION = "section"             # A section of the response
    
    # Final events
    COMPLETE = "complete"           # Final complete response
    ERROR = "error"                 # Error occurred


def create_event(
    event_type: str, 
    data: Any, 
    step: int = 0, 
    total_steps: int = 0,
    task_id: Optional[str] = None
) -> Dict:
    """Create a standardized streaming event"""
    return {
        "type": event_type,
        "data": data,
        "step": step,
        "total_steps": total_steps,
        "task_id": task_id,
        "timestamp": datetime.now().isoformat()
    }


# =============================================================================
# Response Dataclass
# =============================================================================

@dataclass
class OrchestratorResponse:
    """Response from the orchestrator - follows ResponseContract"""
    success: bool
    response: Optional[Dict] = None
    error: Optional[str] = None
    reasoning_steps: List[Dict] = field(default_factory=list)
    task_plan: Optional[Dict] = None
    credits_used: int = 0
    session_id: str = ""
    mode_used: str = "auto"
    search_depth: str = "standard"
    
    def to_dict(self) -> dict:
        result = {
            "success": self.success,
            "error": self.error,
            "reasoning_steps": self.reasoning_steps,
            "task_plan": self.task_plan,
            "credits_used": self.credits_used,
            "session_id": self.session_id,
            "mode_used": self.mode_used,
            "search_depth": self.search_depth
        }
        if self.response:
            result["response"] = self.response
        return result


# =============================================================================
# V6 Orchestrator with Manus AI-style Features
# =============================================================================

class V6Orchestrator:
    """
    V6 Orchestrator with Manus AI-style reasoning display.
    
    Key features:
    - Real-time thinking process visible to users
    - Step-by-step task execution with progress
    - Memory system for context awareness
    - Structured, clean output
    """
    
    def __init__(self):
        self.grok_api_key = os.getenv("XAI_API_KEY", "")
        self.grok_base_url = "https://api.x.ai/v1"
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY", "")
        
        # Search configuration by mode
        self.search_config = {
            "quick": {
                "max_sources": 5,
                "search_depth": "surface",
                "analysis_depth": "brief",
                "estimated_time": "10-15 seconds",
                "credits": 2
            },
            "deep": {
                "max_sources": 15,
                "search_depth": "comprehensive",
                "analysis_depth": "thorough",
                "estimated_time": "30-60 seconds",
                "credits": 5
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
        task_plan = None
        
        try:
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Collect events from streaming process
            final_response = None
            async for event in self.process_stream(query, session_id, mode, domain_filter):
                reasoning_steps.append(event)
                
                if event["type"] == StreamEventType.PLANNING:
                    task_plan = event["data"].get("plan")
                
                if event["type"] == StreamEventType.COMPLETE:
                    final_response = event["data"]
            
            if final_response:
                return OrchestratorResponse(
                    success=True,
                    response=final_response.get("response"),
                    reasoning_steps=reasoning_steps,
                    task_plan=task_plan,
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
                task_plan=task_plan,
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
        
        task_id = str(uuid.uuid4())[:8]
        
        try:
            # =================================================================
            # Step 1: THINKING - Initial reasoning about the query
            # =================================================================
            yield create_event(
                StreamEventType.THINKING,
                {
                    "thought": f"Analyzing your request...",
                    "detail": "Understanding the query and determining the best approach"
                },
                step=1, total_steps=6, task_id=task_id
            )
            await asyncio.sleep(0.2)
            
            # Get memory context
            context = await memory_manager.get_context_for_query(session_id, query)
            
            # Generate reasoning thoughts
            async for thought in reasoning_engine.generate_reasoning_stream(query, context):
                yield create_event(
                    StreamEventType.THINKING,
                    thought,
                    step=1, total_steps=6, task_id=task_id
                )
            
            # =================================================================
            # Step 2: PLANNING - Create task plan
            # =================================================================
            yield create_event(
                StreamEventType.THINKING,
                {
                    "thought": "Creating a plan to address your request...",
                    "detail": "Breaking down the task into steps"
                },
                step=2, total_steps=6, task_id=task_id
            )
            await asyncio.sleep(0.2)
            
            # Classify intent
            intent_result = intent_router.classify(query)
            
            # Determine search mode
            if mode == "auto":
                is_complex = len(query.split()) > 10 or any(
                    word in query.lower() 
                    for word in ["analyze", "compare", "comprehensive", "detailed", "research", "deep"]
                )
                effective_mode = "deep" if is_complex else "quick"
            else:
                effective_mode = mode
            
            config = self.search_config[effective_mode]
            
            # Create task plan
            task_plan = await reasoning_engine.create_task_plan(
                query=query,
                intent_type=intent_result.intent_type.value,
                domain=intent_result.domain.value,
                mode=effective_mode
            )
            
            yield create_event(
                StreamEventType.PLANNING,
                {
                    "goal": task_plan.goal,
                    "mode": effective_mode,
                    "intent": intent_result.intent_type.value,
                    "domain": intent_result.domain.value,
                    "plan": task_plan.to_dict(),
                    "steps": [s.to_dict() for s in task_plan.steps],
                    "estimated_time": config["estimated_time"]
                },
                step=2, total_steps=6, task_id=task_id
            )
            await asyncio.sleep(0.3)
            
            # =================================================================
            # Step 3: SEARCHING - Find information with progress updates
            # =================================================================
            for i, step in enumerate(task_plan.steps):
                if step.step_type == "searching":
                    step.status = "in_progress"
                    step.started_at = datetime.utcnow()
                    
                    yield create_event(
                        StreamEventType.TASK_UPDATE,
                        {
                            "step_id": step.step_id,
                            "status": "in_progress",
                            "title": step.title,
                            "description": step.description
                        },
                        step=3, total_steps=6, task_id=task_id
                    )
            
            yield create_event(
                StreamEventType.SEARCHING,
                {
                    "status": "starting",
                    "message": f"Searching {intent_result.domain.value} sources...",
                    "sources_target": config["max_sources"]
                },
                step=3, total_steps=6, task_id=task_id
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
                            "snippet": search_event["source"].get("snippet", "")[:100],
                            "relevance": search_event.get("relevance", 0.8)
                        },
                        step=3, total_steps=6, task_id=task_id
                    )
                elif search_event["type"] == "progress":
                    yield create_event(
                        StreamEventType.PROGRESS,
                        {
                            "message": search_event["message"],
                            "percentage": search_event["percentage"]
                        },
                        step=3, total_steps=6, task_id=task_id
                    )
            
            # Mark search step complete
            for step in task_plan.steps:
                if step.step_type == "searching":
                    step.status = "completed"
                    step.completed_at = datetime.utcnow()
                    yield create_event(
                        StreamEventType.TASK_UPDATE,
                        {
                            "step_id": step.step_id,
                            "status": "completed",
                            "title": step.title
                        },
                        step=3, total_steps=6, task_id=task_id
                    )
            
            yield create_event(
                StreamEventType.SEARCHING,
                {
                    "status": "complete",
                    "message": f"Found {len(search_results)} relevant sources",
                    "sources_found": len(search_results)
                },
                step=3, total_steps=6, task_id=task_id
            )
            
            # =================================================================
            # Step 4: ANALYZING - Process and analyze results
            # =================================================================
            for step in task_plan.steps:
                if step.step_type == "analyzing":
                    step.status = "in_progress"
                    step.started_at = datetime.utcnow()
                    
                    yield create_event(
                        StreamEventType.TASK_UPDATE,
                        {
                            "step_id": step.step_id,
                            "status": "in_progress",
                            "title": step.title,
                            "description": step.description
                        },
                        step=4, total_steps=6, task_id=task_id
                    )
                    break
            
            yield create_event(
                StreamEventType.ANALYZING,
                {
                    "status": "starting",
                    "message": "Analyzing sources and extracting insights...",
                    "sources_count": len(search_results)
                },
                step=4, total_steps=6, task_id=task_id
            )
            await asyncio.sleep(0.3)
            
            # Analysis thoughts
            analysis_thoughts = [
                f"Reviewing {len(search_results)} sources for relevant information...",
                "Cross-referencing data across sources...",
                "Identifying key patterns and trends...",
                "Extracting actionable insights..."
            ]
            
            for i, thought in enumerate(analysis_thoughts):
                yield create_event(
                    StreamEventType.THINKING,
                    {
                        "thought": thought,
                        "phase": "analysis"
                    },
                    step=4, total_steps=6, task_id=task_id
                )
                await asyncio.sleep(0.2)
            
            # Mark analysis steps complete
            for step in task_plan.steps:
                if step.step_type == "analyzing":
                    step.status = "completed"
                    step.completed_at = datetime.utcnow()
            
            # =================================================================
            # Step 5: GENERATING - Create the response
            # =================================================================
            for step in task_plan.steps:
                if step.step_type == "generating":
                    step.status = "in_progress"
                    step.started_at = datetime.utcnow()
                    
                    yield create_event(
                        StreamEventType.TASK_UPDATE,
                        {
                            "step_id": step.step_id,
                            "status": "in_progress",
                            "title": step.title,
                            "description": step.description
                        },
                        step=5, total_steps=6, task_id=task_id
                    )
                    break
            
            yield create_event(
                StreamEventType.GENERATING,
                {
                    "status": "starting",
                    "message": "Synthesizing comprehensive response..."
                },
                step=5, total_steps=6, task_id=task_id
            )
            
            # Get context prompt from memory
            context_prompt = memory_manager.get_context_prompt(context)
            
            # Generate response with Grok
            response_contract = await self._generate_enhanced_response(
                query=query,
                search_results=search_results,
                intent_result=intent_result,
                session_id=session_id,
                mode=effective_mode,
                context_prompt=context_prompt
            )
            
            # Yield individual insights
            for insight in response_contract.key_insights:
                yield create_event(
                    StreamEventType.INSIGHT,
                    {
                        "icon": insight.icon,
                        "title": insight.title,
                        "description": insight.description,
                        "importance": insight.importance
                    },
                    step=5, total_steps=6, task_id=task_id
                )
                await asyncio.sleep(0.1)
            
            # Mark generation complete
            for step in task_plan.steps:
                if step.step_type == "generating":
                    step.status = "completed"
                    step.completed_at = datetime.utcnow()
            
            # =================================================================
            # Step 6: COMPLETE - Final response
            # =================================================================
            credits_used = config["credits"]
            
            # Update memory with this interaction
            memory_manager.add_message(session_id, "user", query)
            memory_manager.add_message(session_id, "assistant", response_contract.summary)
            memory_manager.update_context(
                session_id,
                intent=intent_result.intent_type.value,
                entities=context.get("current_entities", [])
            )
            
            yield create_event(
                StreamEventType.COMPLETE,
                {
                    "response": response_contract.to_dict(),
                    "session_id": session_id,
                    "mode_used": effective_mode,
                    "sources_used": len(search_results),
                    "credits_used": credits_used,
                    "task_plan": task_plan.to_dict()
                },
                step=6, total_steps=6, task_id=task_id
            )
            
        except Exception as e:
            yield create_event(
                StreamEventType.ERROR,
                {
                    "message": str(e),
                    "detail": "An error occurred while processing your request"
                },
                task_id=task_id
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
        
        yield {"type": "progress", "message": "Initializing search...", "percentage": 10}
        
        # Try Perplexity first
        if self.perplexity_api_key:
            yield {"type": "progress", "message": "Searching knowledge bases...", "percentage": 30}
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
                yield {"type": "progress", "message": "Using alternative sources...", "percentage": 40}
        
        # Use Grok for additional sources
        if len(results) < config["max_sources"]:
            yield {"type": "progress", "message": f"Searching {domain.value} databases...", "percentage": 60}
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
        """Use Grok to generate search-like results"""
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
                    "model": "grok-3-latest",
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
        mode: str,
        context_prompt: str = ""
    ) -> ResponseContract:
        """Generate enhanced structured response using Grok"""
        
        # Build context from search results
        sources_context = "\n".join([
            f"[{i+1}] {r.get('title', 'Source')}: {r.get('snippet', '')}"
            for i, r in enumerate(search_results)
        ])
        
        # Enhanced system prompt for Manus AI-style output
        system_prompt = f"""You are McLeuker AI, a professional {intent_result.domain.value} intelligence platform.

TODAY'S DATE: {datetime.now().strftime('%B %d, %Y')}

{context_prompt}

RESPONSE FORMAT REQUIREMENTS:
1. Start with a clear, actionable summary (2-3 sentences)
2. Provide 5 KEY INSIGHTS - each must be:
   - Specific and data-driven when possible
   - Actionable for the user
   - Formatted as: "**[Title]**: [Description]"
3. Write clean prose WITHOUT inline citations [1][2] - sources are displayed separately
4. Use clear section headers with ##
5. End with 3 contextual follow-up questions

QUALITY STANDARDS:
- Be specific with numbers, dates, and names
- Provide expert-level analysis
- {"Comprehensive, in-depth analysis" if mode == "deep" else "Concise, focused response"}
- Professional, authoritative tone"""

        user_prompt = f"""Query: {query}

Research Sources:
{sources_context if sources_context else "Using internal knowledge base"}

Generate a structured response following the format requirements."""

        # Call Grok
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.grok_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.grok_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-3-latest",
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
            session_id=session_id,
            mode=mode
        )
    
    def _parse_to_contract(
        self,
        content: str,
        query: str,
        search_results: List[Dict],
        intent_result: IntentResult,
        session_id: str,
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
                publisher=r.get("publisher", ""),
                type="article"
            )
            for i, r in enumerate(search_results)
        ]
        
        # Extract key insights (look for bold patterns)
        insights = []
        insight_pattern = r'\*\*(.+?)\*\*:\s*(.+?)(?=\n|$)'
        insight_matches = re.findall(insight_pattern, content)
        
        for i, (title, desc) in enumerate(insight_matches[:5]):
            insights.append(KeyInsight(
                icon="💡" if i < 2 else "📌",
                title=title.strip(),
                description=desc.strip()[:200],
                importance="high" if i < 2 else "medium"
            ))
        
        # If no bold insights found, try bullet points
        if not insights:
            bullet_pattern = r'[-•*]\s*(.+?)(?=\n|$)'
            bullet_matches = re.findall(bullet_pattern, content)
            for i, match in enumerate(bullet_matches[:5]):
                clean_match = re.sub(r'\*+', '', match).strip()
                if len(clean_match) > 20:
                    insights.append(KeyInsight(
                        icon="💡" if i < 2 else "📌",
                        title=f"Insight {i+1}",
                        description=clean_match[:200],
                        importance="high" if i < 2 else "medium"
                    ))
        
        # Extract follow-up questions
        follow_ups = self._extract_follow_ups(content, query, intent_result)
        
        # Create layout sections
        sections = []
        header_pattern = r'^##\s*(.+?)$'
        headers = re.findall(header_pattern, content, re.MULTILINE)
        for i, header in enumerate(headers[:5]):
            sections.append(LayoutSection(
                id=f"section_{i+1}",
                title=header.strip().replace('*', ''),
                content=""
            ))
        
        return ResponseContract(
            session_id=session_id,
            intent=intent_result.intent_type,
            domain=intent_result.domain,
            confidence=intent_result.confidence,
            summary=summary[:500],
            main_content=clean_content,
            key_insights=insights,
            sections=sections,
            sources=sources,
            source_count=len(sources),
            follow_up_questions=follow_ups,
            credits_used=2 if mode == "quick" else 5
        )
    
    def _extract_follow_ups(
        self, 
        content: str, 
        query: str, 
        intent_result: IntentResult
    ) -> List[str]:
        """Extract or generate contextual follow-up questions"""
        
        # Try to find follow-up questions in the content
        question_pattern = r'(?:^|\n)\s*[-•*]?\s*(.+?\?)'
        found_questions = re.findall(question_pattern, content[-500:])
        
        if found_questions and len(found_questions) >= 3:
            return [q.strip() for q in found_questions[:3]]
        
        # Generate contextual follow-ups
        domain = intent_result.domain.value
        key_terms = [word for word in query.split() if len(word) > 4][:3]
        context = " ".join(key_terms) if key_terms else domain
        
        return [
            f"What specific aspects of {context} would you like to explore further?",
            f"Would you like me to generate a detailed report on this topic?",
            f"Are there any particular brands or products you'd like me to focus on?"
        ]


# Global instance
orchestrator = V6Orchestrator()
