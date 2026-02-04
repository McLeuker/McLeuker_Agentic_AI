"""
McLeuker AI V6 - FastAPI Main Application
==========================================
Manus AI-style API with real-time streaming and reasoning display.

Features:
1. SSE streaming for real-time updates
2. Task progress and reasoning visibility
3. Memory-aware conversations
4. Structured response contract
"""

import os
import json
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from pydantic import BaseModel
import asyncio

# Use V6 orchestrator
from src.core.orchestrator_v6 import orchestrator, OrchestratorResponse, StreamEventType
from src.schemas.response_contract import ResponseContract
from src.core.memory_manager import memory_manager


# FastAPI app
app = FastAPI(
    title="McLeuker AI V6",
    description="Manus AI-style Platform with Reasoning Display",
    version="6.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    mode: str = "auto"  # quick, deep, auto
    domain_filter: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    mode: str = "quick"


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    return {
        "status": "healthy",
        "version": "6.0.0",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "grok": bool(os.getenv("XAI_API_KEY")),
            "search": bool(os.getenv("PERPLEXITY_API_KEY") or os.getenv("XAI_API_KEY")),
            "supabase": bool(os.getenv("SUPABASE_URL"))
        },
        "features": {
            "response_contract": True,
            "file_generation": True,
            "intent_routing": True,
            "memory_system": True,
            "reasoning_display": True,
            "sse_streaming": True
        }
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "McLeuker AI",
        "version": "6.0.0",
        "description": "Manus AI-style Platform with Reasoning Display",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "chat_stream": "/api/chat/stream",
            "search": "/api/search",
            "files": "/api/files/{file_id}",
            "history": "/api/history/{session_id}"
        }
    }


# Chat endpoint - main API (non-streaming)
@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint with structured response.
    
    Returns ResponseContract format with:
    - summary: Brief overview
    - main_content: Clean prose (no inline citations)
    - sources: Separate source objects
    - key_insights: Structured insights
    - reasoning_steps: Full reasoning trace
    """
    try:
        # Process with orchestrator
        result = await orchestrator.process(
            query=request.message,
            session_id=request.session_id,
            mode=request.mode,
            domain_filter=request.domain_filter
        )
        
        if not result.success:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": result.error,
                    "reasoning_steps": result.reasoning_steps
                }
            )
        
        return result.to_dict()
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


# Streaming chat endpoint (SSE)
@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint with real-time updates.
    
    Uses Server-Sent Events (SSE) to stream:
    - thinking: AI reasoning process
    - planning: Task breakdown
    - task_update: Individual task status
    - searching: Search progress
    - source: Individual sources found
    - analyzing: Analysis progress
    - insight: Key insights discovered
    - generating: Response generation
    - complete: Final response
    - error: Error messages
    """
    
    async def generate():
        try:
            async for event in orchestrator.process_stream(
                query=request.message,
                session_id=request.session_id,
                mode=request.mode,
                domain_filter=request.domain_filter
            ):
                # Format as SSE
                yield f"data: {json.dumps(event)}\n\n"
                
                # Small delay for smooth streaming
                await asyncio.sleep(0.05)
                
        except Exception as e:
            error_event = {
                "type": StreamEventType.ERROR,
                "data": {"message": str(e)},
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# Search endpoint
@app.post("/api/search")
async def search(request: SearchRequest):
    """Quick search endpoint for simple queries"""
    try:
        result = await orchestrator.process(
            query=request.query,
            mode=request.mode
        )
        
        return result.to_dict()
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


# Conversation history endpoint
@app.get("/api/history/{session_id}")
async def get_history(session_id: str, limit: int = 10):
    """Get conversation history for a session"""
    try:
        history = memory_manager.get_conversation_history(session_id, limit)
        return {
            "success": True,
            "session_id": session_id,
            "messages": history,
            "count": len(history)
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


# Clear session endpoint
@app.delete("/api/history/{session_id}")
async def clear_history(session_id: str):
    """Clear conversation history for a session"""
    try:
        memory_manager.clear_session(session_id)
        return {
            "success": True,
            "message": f"Session {session_id} cleared"
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


# File download endpoint
@app.get("/api/files/{file_id}")
async def get_file(file_id: str):
    """Download generated files"""
    file_path = f"/tmp/mcleuker_files/{file_id}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine content type
    if file_id.endswith(".xlsx"):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif file_id.endswith(".pdf"):
        media_type = "application/pdf"
    elif file_id.endswith(".csv"):
        media_type = "text/csv"
    else:
        media_type = "application/octet-stream"
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=file_id
    )


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "detail": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
