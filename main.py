"""
McLeuker AI V5 - Main API
FastAPI-based REST API with streaming support.

Endpoints:
- POST /api/chat - Main chat endpoint
- POST /api/chat/stream - Streaming chat endpoint
- GET /health - Health check
- GET /api/status - Detailed status
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from src.config.settings import settings
from src.core.orchestrator import orchestrator, OrchestratorResponse
from src.core.hybrid_orchestrator import hybrid_orchestrator


# =============================================================================
# Pydantic Models
# =============================================================================

class ChatMessage(BaseModel):
    """A single chat message."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    user_id: Optional[str] = Field(None, description="User ID for credit tracking")
    conversation_history: Optional[List[ChatMessage]] = Field(default=[], description="Previous messages")
    mode: Optional[str] = Field("auto", description="Mode: 'quick', 'deep', or 'auto'")


class ChatResponse(BaseModel):
    """Response body for chat endpoint."""
    success: bool
    response: str
    session_id: str
    reasoning: List[str] = []
    sources: List[Dict] = []
    files: List[Dict] = []
    images: List[str] = []
    follow_up_questions: List[str] = []
    credits_used: int = 0
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Response body for health check."""
    status: str
    version: str
    timestamp: str
    services: Dict[str, bool]


# =============================================================================
# Application Setup
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("🚀 McLeuker AI V5 starting...")
    print(f"✅ Grok configured: {settings.is_grok_configured()}")
    print(f"✅ Search configured: {settings.is_search_configured()}")
    print(f"✅ Supabase configured: {settings.is_supabase_configured()}")
    print(f"📅 Current date: {datetime.now().strftime('%B %d, %Y')}")
    yield
    # Shutdown
    print("👋 McLeuker AI V5 shutting down...")


app = FastAPI(
    title="McLeuker AI V5",
    description="Frontier Agentic AI for Fashion, Beauty, Lifestyle, and Culture",
    version="5.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Health & Status Endpoints
# =============================================================================

@app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint - basic info."""
    return {
        "name": "McLeuker AI",
        "version": "5.0.0",
        "status": "online",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="5.0.0",
        timestamp=datetime.utcnow().isoformat(),
        services={
            "grok": settings.is_grok_configured(),
            "search": settings.is_search_configured(),
            "supabase": settings.is_supabase_configured()
        }
    )


@app.get("/api/status")
async def api_status():
    """Detailed API status."""
    return {
        "platform": "McLeuker AI",
        "version": "7.0.0",
        "architecture": "V7 Hybrid Agentic",
        "brain": "Dual-Model (Grok + Kimi)",
        "models": {
            "reasoning": {
                "provider": "Grok (xAI)",
                "model": settings.GROK_MODEL,
                "configured": settings.is_grok_configured(),
                "role": "Intent understanding, planning, synthesis"
            },
            "execution": {
                "provider": "Kimi K2.5 (Moonshot AI)",
                "model": settings.KIMI_MODEL,
                "configured": settings.is_kimi_configured(),
                "role": "Code generation, tool calling, agentic workflows"
            },
            "hybrid_enabled": settings.ENABLE_MULTI_MODEL and settings.is_kimi_configured()
        },
        "layers": {
            "intent_router": "Rule-based fast detection",
            "context_manager": "Session-based memory",
            "query_planner": "Automatic mode selection",
            "tool_executor": "Parallel search + Hybrid Brain",
            "response_synthesizer": "Clean formatting with citations"
        },
        "focus_areas": [
            "Fashion", "Beauty", "Textile", "Skincare",
            "Lifestyle", "Tech", "Sustainability", "Culture", "Catwalks"
        ],
        "current_date": datetime.now().strftime("%B %d, %Y"),
        "services": {
            "grok": settings.is_grok_configured(),
            "kimi": settings.is_kimi_configured(),
            "perplexity": bool(settings.PERPLEXITY_API_KEY),
            "exa": bool(settings.EXA_API_KEY),
            "google": bool(settings.GOOGLE_SEARCH_API_KEY),
            "bing": bool(settings.BING_API_KEY)
        }
    }


# =============================================================================
# Chat Endpoints
# =============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - processes user queries.
    
    Modes:
    - quick: Fast response with minimal search
    - deep: Comprehensive research with extensive search
    - auto: Automatically determines the best approach
    """
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    user_id = request.user_id or "anonymous"
    
    # Convert conversation history to dict format
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in (request.conversation_history or [])
    ]
    
    # Process the request through the orchestrator
    result = await orchestrator.process(
        query=request.message,
        session_id=session_id,
        user_id=user_id,
        mode=request.mode or "auto",
        conversation_history=history
    )
    
    return ChatResponse(
        success=result.success,
        response=result.response,
        session_id=result.session_id,
        reasoning=result.reasoning,
        sources=result.sources,
        files=result.files,
        images=result.images,
        follow_up_questions=result.follow_up_questions,
        credits_used=result.credits_used,
        error=result.error
    )


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint - returns Server-Sent Events.
    
    Event types:
    - status: Progress updates (understanding, planning, searching, generating)
    - content: Response text chunks
    - sources: Search sources used
    - done: Stream complete
    """
    session_id = request.session_id or str(uuid.uuid4())
    user_id = request.user_id or "anonymous"
    
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in (request.conversation_history or [])
    ]
    
    async def generate():
        async for event in orchestrator.process_stream(
            query=request.message,
            session_id=session_id,
            user_id=user_id,
            mode=request.mode or "auto",
            conversation_history=history
        ):
            yield f"data: {json.dumps(event)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Session-ID": session_id
        }
    )


# =============================================================================
# Search Endpoint (Direct access)
# =============================================================================

@app.post("/api/search")
async def search(query: str, providers: Optional[List[str]] = None):
    """Direct search endpoint for testing."""
    from src.layers.search.search_layer import search_layer
    
    result = await search_layer.search(query, providers=providers)
    
    return {
        "success": result.success,
        "query": result.query,
        "providers_used": result.providers_used,
        "results": [
            {
                "title": r.title,
                "url": r.url,
                "snippet": r.snippet,
                "source": r.source
            }
            for r in result.results
        ]
    }


# =============================================================================
# Error Handlers
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# =============================================================================
# Run Server
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
