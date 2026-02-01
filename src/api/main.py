"""
McLeuker Fashion AI Platform - V3.1
The Frontier Agentic AI for Fashion, Beauty, Lifestyle, and Culture.

Powered by:
- Grok (Unified Reasoning Brain)
- Parallel Search (Google, Bing, Perplexity, Exa.ai)
- Web Action (Browserless, Firecrawl)
- Analyst (E2B Sandbox)
- Image Generation (Nano Banana)
"""

import asyncio
import json
import uuid
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from src.config.settings import settings
from src.core.orchestrator import V31Orchestrator, orchestrator
from src.layers.search.parallel_search import parallel_search
from src.layers.action.web_action import action_layer
from src.layers.analyst.code_executor import analyst_layer
from src.layers.output.image_generator import output_layer


# ============================================================================
# Pydantic Models
# ============================================================================

class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    user_id: Optional[str] = Field(None, description="User ID for credit tracking")
    conversation_history: Optional[List[ChatMessage]] = Field(default=[], description="Previous messages")
    mode: Optional[str] = Field("auto", description="Mode: 'quick', 'deep', or 'auto'")


class ChatResponse(BaseModel):
    success: bool
    response: str
    session_id: str
    reasoning: List[str] = []
    sources: List[Dict] = []
    files: List[Dict] = []
    images: List[str] = []
    follow_up_questions: List[str] = []
    credits_used: int = 0
    needs_user_input: bool = False
    user_input_prompt: Optional[str] = None
    error: Optional[str] = None


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    providers: Optional[List[str]] = Field(None, description="Specific providers to use")


class FileGenerationRequest(BaseModel):
    type: str = Field(..., description="File type: 'excel', 'pdf', 'word'")
    title: str = Field(..., description="File title")
    data: Dict = Field(..., description="Data to include in the file")


class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Image generation prompt")
    style: Optional[str] = Field("fashion", description="Style: fashion, streetwear, luxury, etc.")
    num_images: Optional[int] = Field(1, description="Number of images to generate")


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    services: Dict[str, bool]


# ============================================================================
# Application Setup
# ============================================================================

# In-memory session storage (use Redis/Supabase in production)
sessions: Dict[str, Dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("🚀 McLeuker Fashion AI Platform V3.1 starting...")
    print(f"✅ Grok configured: {bool(settings.XAI_API_KEY)}")
    print(f"✅ Search configured: {bool(settings.PERPLEXITY_API_KEY or settings.EXA_API_KEY)}")
    print(f"✅ Action configured: {bool(settings.BROWSERLESS_API_KEY)}")
    print(f"✅ Analyst configured: {bool(settings.E2B_API_KEY)}")
    print(f"✅ Image Gen configured: {bool(settings.NANO_BANANA_API_KEY)}")
    
    # Initialize orchestrator with layers
    orchestrator.set_layers(
        search=parallel_search,
        action=action_layer,
        analyst=analyst_layer,
        output=output_layer
    )
    
    yield
    
    # Shutdown
    print("👋 McLeuker Fashion AI Platform shutting down...")


app = FastAPI(
    title="McLeuker Fashion AI Platform",
    description="Frontier Agentic AI for Fashion, Beauty, Lifestyle, and Culture",
    version="3.1.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="3.1.0",
        timestamp=datetime.utcnow().isoformat(),
        services={
            "grok": bool(settings.XAI_API_KEY),
            "perplexity": bool(settings.PERPLEXITY_API_KEY),
            "exa": bool(settings.EXA_API_KEY),
            "browserless": bool(settings.BROWSERLESS_API_KEY),
            "e2b": bool(settings.E2B_API_KEY),
            "nano_banana": bool(settings.NANO_BANANA_API_KEY)
        }
    )


@app.get("/api/status")
async def api_status():
    """Detailed API status."""
    return {
        "platform": "McLeuker Fashion AI",
        "version": "3.1.0",
        "architecture": "V3.1 Killer Blueprint",
        "brain": "Grok (Unified)",
        "layers": {
            "reasoning": "Grok XAI",
            "search": ["Google", "Bing", "Perplexity", "Exa.ai", "Grok Real-time"],
            "action": ["Browserless", "Firecrawl"],
            "analyst": "E2B Sandbox",
            "output": "Nano Banana"
        },
        "focus_areas": [
            "Fashion", "Beauty", "Textile", "Skincare", 
            "Lifestyle", "Tech", "Sustainability", "Culture", "Catwalks"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Main Chat Endpoint
# ============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    Processes user queries through the V3.1 orchestrator.
    """
    
    # Generate or use existing session ID
    session_id = request.session_id or str(uuid.uuid4())
    user_id = request.user_id or "anonymous"
    
    # Get or create session
    if session_id not in sessions:
        sessions[session_id] = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "conversation_history": [],
            "credits_used": 0
        }
    
    session = sessions[session_id]
    
    # Build conversation history
    history = []
    if request.conversation_history:
        history = [{"role": m.role, "content": m.content} for m in request.conversation_history]
    elif session.get("conversation_history"):
        history = session["conversation_history"]
    
    try:
        # Process through orchestrator
        result = await orchestrator.process(
            user_id=user_id,
            session_id=session_id,
            query=request.message,
            conversation_history=history,
            credits_available=100  # TODO: Get from Supabase
        )
        
        # Update session history
        session["conversation_history"].append({"role": "user", "content": request.message})
        if result.success:
            session["conversation_history"].append({"role": "assistant", "content": result.response})
        session["credits_used"] += result.credits_used
        
        # Keep only last 20 messages
        if len(session["conversation_history"]) > 20:
            session["conversation_history"] = session["conversation_history"][-20:]
        
        return ChatResponse(
            success=result.success,
            response=result.response,
            session_id=session_id,
            reasoning=result.reasoning,
            sources=result.sources,
            files=result.files,
            images=result.images,
            follow_up_questions=result.follow_up_questions,
            credits_used=result.credits_used,
            needs_user_input=result.needs_user_input,
            user_input_prompt=result.user_input_prompt,
            error=result.error
        )
        
    except Exception as e:
        return ChatResponse(
            success=False,
            response="I encountered an error processing your request. Please try again.",
            session_id=session_id,
            error=str(e)
        )


# ============================================================================
# Search Endpoint
# ============================================================================

@app.post("/api/search")
async def search(request: SearchRequest):
    """
    Direct search endpoint.
    Executes parallel search across all providers.
    """
    
    try:
        results = await parallel_search.parallel_search(request.query)
        return {
            "success": True,
            "query": request.query,
            "synthesized": results.get("synthesized", ""),
            "sources": results.get("sources", []),
            "providers_used": results.get("providers_used", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# File Generation Endpoint
# ============================================================================

@app.post("/api/generate/file")
async def generate_file(request: FileGenerationRequest):
    """
    File generation endpoint.
    Creates Excel, PDF, or Word files.
    """
    
    try:
        if request.type.lower() == "excel":
            result = await analyst_layer.excel_gen.generate(request.data, request.title)
            
            if result.get("success"):
                return {
                    "success": True,
                    "filename": result["filename"],
                    "content_type": result["content_type"],
                    "data": result["file_data"]
                }
            else:
                raise HTTPException(status_code=500, detail=result.get("error"))
        else:
            raise HTTPException(status_code=400, detail=f"File type '{request.type}' not yet supported")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Image Generation Endpoint
# ============================================================================

@app.post("/api/generate/image")
async def generate_image(request: ImageGenerationRequest):
    """
    Image generation endpoint.
    Creates fashion-focused images using Nano Banana.
    """
    
    try:
        images = await output_layer.generate_images(
            request.prompt, 
            request.num_images, 
            request.style
        )
        
        return {
            "success": True,
            "prompt": request.prompt,
            "style": request.style,
            "images": images,
            "count": len(images)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Session Management
# ============================================================================

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session information."""
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return {
        "session_id": session_id,
        "user_id": session.get("user_id"),
        "created_at": session.get("created_at"),
        "message_count": len(session.get("conversation_history", [])),
        "credits_used": session.get("credits_used", 0)
    }


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    
    if session_id in sessions:
        del sessions[session_id]
    
    return {"success": True, "message": "Session deleted"}


# ============================================================================
# Credits Endpoint (Placeholder for Supabase integration)
# ============================================================================

@app.get("/api/credits/{user_id}")
async def get_credits(user_id: str):
    """Get user credit balance."""
    # TODO: Integrate with Supabase
    return {
        "user_id": user_id,
        "credits_available": 100,
        "credits_used": 0,
        "plan": "free"
    }


# ============================================================================
# Run Application
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
