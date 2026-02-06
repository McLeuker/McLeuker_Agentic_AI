"""
McLeuker AI V5 - Orchestrator
The central controller that coordinates all layers using an agentic approach.

Architecture Layers:
1. Intent Router - Quick classification without asking questions
2. Context Manager - Proper conversation memory
3. Query Planner - Break complex queries into steps
4. Tool Executor - Unified interface for all tools
5. Response Synthesizer - Clean output formatting

Design Principles (Inspired by Manus AI):
- NEVER ask for clarification unless absolutely necessary
- ALWAYS provide a response, even if partial
- Use the brain for reasoning, not classification
- Implement proper streaming for real-time feedback
- Graceful fallbacks on errors
"""

import asyncio
import json
import re
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from src.config.settings import settings
from src.core.brain import brain, BrainResponse
from src.layers.search.search_layer import search_layer, SearchResponse


class QueryIntent(Enum):
    """Types of query intents - determined quickly without LLM."""
    SIMPLE_CHAT = "simple_chat"           # General conversation
    FASHION_QUERY = "fashion_query"       # Fashion-related questions
    BEAUTY_QUERY = "beauty_query"         # Beauty/skincare questions
    TREND_RESEARCH = "trend_research"     # Deep trend analysis
    DATA_REQUEST = "data_request"         # Data/statistics request
    FILE_GENERATION = "file_generation"   # Generate files (Excel, PDF)
    IMAGE_REQUEST = "image_request"       # Generate images
    FOLLOW_UP = "follow_up"               # Follow-up to previous query


class SearchMode(Enum):
    """Search modes for different query types."""
    NONE = "none"           # No search needed
    QUICK = "quick"         # Fast search, fewer results
    DEEP = "deep"           # Comprehensive search


@dataclass
class OrchestratorContext:
    """Context for a single orchestration request."""
    user_id: str
    session_id: str
    query: str
    mode: str = "auto"  # quick, deep, or auto
    conversation_history: List[Dict] = field(default_factory=list)
    intent: QueryIntent = QueryIntent.SIMPLE_CHAT
    search_mode: SearchMode = SearchMode.NONE
    search_results: List[Dict] = field(default_factory=list)
    reasoning_steps: List[str] = field(default_factory=list)
    sources: List[Dict] = field(default_factory=list)


@dataclass
class OrchestratorResponse:
    """Response from the orchestrator."""
    success: bool
    response: str
    session_id: str
    reasoning: List[str] = field(default_factory=list)
    sources: List[Dict] = field(default_factory=list)
    files: List[Dict] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    follow_up_questions: List[str] = field(default_factory=list)
    credits_used: int = 0
    error: Optional[str] = None


class V5Orchestrator:
    """
    The V5 Orchestrator - A robust agentic controller.
    
    Key improvements over V3:
    1. Fast intent detection without LLM calls
    2. Proper search mode selection based on query
    3. No excessive clarification loops
    4. Better error handling with fallbacks
    5. Proper source formatting
    """
    
    # Keywords for intent detection (fast, no LLM needed)
    FASHION_KEYWORDS = [
        "fashion", "style", "outfit", "wear", "clothing", "dress", "designer",
        "runway", "catwalk", "collection", "trend", "wardrobe", "accessory",
        "shoes", "bag", "luxury", "streetwear", "haute couture", "ready-to-wear"
    ]
    
    BEAUTY_KEYWORDS = [
        "beauty", "makeup", "skincare", "cosmetic", "foundation", "lipstick",
        "serum", "moisturizer", "cleanser", "routine", "glow", "anti-aging",
        "sunscreen", "hair", "nail", "fragrance", "perfume"
    ]
    
    RESEARCH_KEYWORDS = [
        "analyze", "research", "compare", "report", "statistics", "data",
        "market", "industry", "forecast", "comprehensive", "in-depth", "deep dive"
    ]
    
    FILE_KEYWORDS = [
        "excel", "spreadsheet", "pdf", "document", "file", "export", "download",
        "generate file", "create report"
    ]
    
    IMAGE_KEYWORDS = [
        "image", "picture", "photo", "visual", "mood board", "generate image",
        "create image", "show me"
    ]
    
    def __init__(self):
        self.brain = brain
        self.search = search_layer
    
    async def process(
        self,
        query: str,
        session_id: str,
        user_id: str = "anonymous",
        mode: str = "auto",
        conversation_history: Optional[List[Dict]] = None
    ) -> OrchestratorResponse:
        """
        Process a user query through the V5 pipeline.
        
        Pipeline:
        1. Detect intent (fast, rule-based)
        2. Determine search mode
        3. Execute search if needed
        4. Generate response with brain
        5. Format and return response
        """
        # Initialize context
        ctx = OrchestratorContext(
            user_id=user_id,
            session_id=session_id,
            query=query,
            mode=mode,
            conversation_history=conversation_history or []
        )
        
        try:
            # Step 1: Detect intent (fast, no LLM)
            ctx.intent = self._detect_intent(query, conversation_history)
            ctx.reasoning_steps.append(f"Intent detected: {ctx.intent.value}")
            
            # Step 2: Determine search mode
            ctx.search_mode = self._determine_search_mode(ctx)
            ctx.reasoning_steps.append(f"Search mode: {ctx.search_mode.value}")
            
            # Step 3: Execute search if needed
            if ctx.search_mode != SearchMode.NONE:
                search_response = await self._execute_search(ctx)
                if search_response.success:
                    ctx.search_results = [
                        {
                            "title": r.title,
                            "url": r.url,
                            "snippet": r.snippet,
                            "source": r.source
                        }
                        for r in search_response.results
                    ]
                    ctx.sources = ctx.search_results
                    ctx.reasoning_steps.append(f"Found {len(ctx.search_results)} search results")
            
            # Step 4: Generate response with brain
            brain_response = await self._generate_response(ctx)
            
            # Step 5: Format and return response
            return self._build_response(ctx, brain_response)
        
        except Exception as e:
            return OrchestratorResponse(
                success=False,
                response=f"I apologize, but I encountered an error processing your request. Please try again.",
                session_id=session_id,
                reasoning=ctx.reasoning_steps + [f"Error: {str(e)}"],
                error=str(e)
            )
    
    async def process_stream(
        self,
        query: str,
        session_id: str,
        user_id: str = "anonymous",
        mode: str = "auto",
        conversation_history: Optional[List[Dict]] = None
    ) -> AsyncGenerator[Dict, None]:
        """
        Process a query with streaming response.
        Yields status updates and response chunks.
        """
        ctx = OrchestratorContext(
            user_id=user_id,
            session_id=session_id,
            query=query,
            mode=mode,
            conversation_history=conversation_history or []
        )
        
        # Yield initial status
        yield {"type": "status", "step": "understanding", "message": "Understanding request"}
        
        # Detect intent
        ctx.intent = self._detect_intent(query, conversation_history)
        yield {"type": "status", "step": "planning", "message": "Planning approach"}
        
        # Determine and execute search
        ctx.search_mode = self._determine_search_mode(ctx)
        
        if ctx.search_mode != SearchMode.NONE:
            yield {"type": "status", "step": "searching", "message": "Gathering information"}
            search_response = await self._execute_search(ctx)
            if search_response.success:
                ctx.search_results = [
                    {"title": r.title, "url": r.url, "snippet": r.snippet, "source": r.source}
                    for r in search_response.results
                ]
                ctx.sources = ctx.search_results
        
        yield {"type": "status", "step": "generating", "message": "Generating answer"}
        
        # Stream the response
        async for chunk in self.brain.think_stream(
            query=query,
            search_results=ctx.search_results if ctx.search_results else None,
            conversation_history=conversation_history
        ):
            yield {"type": "content", "chunk": chunk}
        
        yield {"type": "status", "step": "complete", "message": "Finalizing output"}
        
        # Yield sources at the end
        if ctx.sources:
            yield {"type": "sources", "sources": ctx.sources}
        
        yield {"type": "done"}
    
    def _detect_intent(
        self,
        query: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> QueryIntent:
        """
        Fast intent detection using keyword matching.
        No LLM call needed - this is instant.
        """
        query_lower = query.lower()
        
        # Check for follow-up patterns
        if conversation_history and len(conversation_history) > 0:
            follow_up_patterns = [
                "why", "how", "what about", "tell me more", "explain",
                "can you", "what do you mean", "elaborate", "continue"
            ]
            if any(query_lower.startswith(p) for p in follow_up_patterns):
                return QueryIntent.FOLLOW_UP
        
        # Check for file generation
        if any(kw in query_lower for kw in self.FILE_KEYWORDS):
            return QueryIntent.FILE_GENERATION
        
        # Check for image generation
        if any(kw in query_lower for kw in self.IMAGE_KEYWORDS):
            return QueryIntent.IMAGE_REQUEST
        
        # Check for research/data requests
        if any(kw in query_lower for kw in self.RESEARCH_KEYWORDS):
            return QueryIntent.TREND_RESEARCH
        
        # Check for fashion queries
        if any(kw in query_lower for kw in self.FASHION_KEYWORDS):
            return QueryIntent.FASHION_QUERY
        
        # Check for beauty queries
        if any(kw in query_lower for kw in self.BEAUTY_KEYWORDS):
            return QueryIntent.BEAUTY_QUERY
        
        # Default to simple chat
        return QueryIntent.SIMPLE_CHAT
    
    def _determine_search_mode(self, ctx: OrchestratorContext) -> SearchMode:
        """
        Determine the appropriate search mode based on intent and user preference.
        """
        # User explicitly requested a mode
        if ctx.mode == "quick":
            return SearchMode.QUICK
        elif ctx.mode == "deep":
            return SearchMode.DEEP
        
        # Auto mode - determine based on intent
        if ctx.intent in [QueryIntent.TREND_RESEARCH, QueryIntent.DATA_REQUEST]:
            return SearchMode.DEEP
        elif ctx.intent in [QueryIntent.FASHION_QUERY, QueryIntent.BEAUTY_QUERY]:
            return SearchMode.QUICK
        elif ctx.intent == QueryIntent.FOLLOW_UP:
            # For follow-ups, only search if the original query needed search
            return SearchMode.NONE
        elif ctx.intent in [QueryIntent.FILE_GENERATION, QueryIntent.IMAGE_REQUEST]:
            return SearchMode.NONE
        
        # For simple chat, check if it seems like a factual question
        query_lower = ctx.query.lower()
        question_words = ["what", "who", "when", "where", "which", "how many", "how much"]
        if any(query_lower.startswith(w) for w in question_words):
            return SearchMode.QUICK
        
        return SearchMode.NONE
    
    async def _execute_search(self, ctx: OrchestratorContext) -> SearchResponse:
        """Execute search based on the determined mode."""
        num_results = 5 if ctx.search_mode == SearchMode.QUICK else 10
        return await self.search.search(ctx.query, num_results=num_results)
    
    async def _generate_response(self, ctx: OrchestratorContext) -> BrainResponse:
        """Generate the response using the brain."""
        # Build context from conversation history
        context = None
        if ctx.intent == QueryIntent.FOLLOW_UP and ctx.conversation_history:
            # For follow-ups, include the last exchange as context
            last_messages = ctx.conversation_history[-2:]
            context = "\n".join([f"{m['role']}: {m['content']}" for m in last_messages])
        
        return await self.brain.think(
            query=ctx.query,
            context=context,
            search_results=ctx.search_results if ctx.search_results else None,
            conversation_history=ctx.conversation_history
        )
    
    def _build_response(
        self,
        ctx: OrchestratorContext,
        brain_response: BrainResponse
    ) -> OrchestratorResponse:
        """Build the final orchestrator response."""
        # Format sources for the response
        formatted_sources = []
        for source in ctx.sources:
            formatted_sources.append({
                "title": source.get("title", "Unknown"),
                "url": source.get("url", ""),
                "snippet": source.get("snippet", "")[:200]
            })
        
        # Calculate credits used
        credits = 1  # Base cost
        if ctx.search_mode == SearchMode.DEEP:
            credits = 10
        elif ctx.search_mode == SearchMode.QUICK:
            credits = 2
        
        # Generate follow-up questions based on intent
        follow_ups = self._generate_follow_ups(ctx)
        
        return OrchestratorResponse(
            success=brain_response.success,
            response=brain_response.content,
            session_id=ctx.session_id,
            reasoning=ctx.reasoning_steps + brain_response.reasoning,
            sources=formatted_sources,
            follow_up_questions=follow_ups,
            credits_used=credits,
            error=brain_response.error
        )
    
    def _generate_follow_ups(self, ctx: OrchestratorContext) -> List[str]:
        """Generate relevant follow-up questions based on the query intent."""
        if ctx.intent == QueryIntent.FASHION_QUERY:
            return [
                "What are the key pieces to invest in?",
                "How can I style this trend?",
                "Which brands are leading this trend?"
            ]
        elif ctx.intent == QueryIntent.BEAUTY_QUERY:
            return [
                "What products do you recommend?",
                "How do I incorporate this into my routine?",
                "Are there any budget-friendly alternatives?"
            ]
        elif ctx.intent == QueryIntent.TREND_RESEARCH:
            return [
                "Can you provide more data on this?",
                "What's the market forecast?",
                "Who are the key players?"
            ]
        return []


# Global orchestrator instance
orchestrator = V5Orchestrator()
