"""
McLeuker AI V7.0 - Reasoning-First API
======================================
True reasoning-first approach - no preset templates.
Every response is dynamically reasoned by the AI.
"""

import os
import json
import uuid
import asyncio
from datetime import datetime
from typing import Optional, AsyncGenerator
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from pydantic import BaseModel

from src.core.reasoning_orchestrator import reasoning_orchestrator


# FastAPI app
app = FastAPI(
    title="McLeuker AI V7.0",
    description="Reasoning-First AI Platform - Dynamic responses based on actual AI reasoning",
    version="7.0.0"
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
    mode: str = "quick"  # quick, deep


# =============================================================================
# Health check endpoint
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "7.0.0",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "reasoning_first": True,
            "streaming": True,
            "dynamic_responses": True
        }
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "McLeuker AI",
        "version": "7.0.0",
        "description": "Reasoning-First AI Platform",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "chat_stream": "/api/chat/stream"
        }
    }


# =============================================================================
# Main Chat Endpoint (Non-streaming)
# =============================================================================

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint - collects all reasoning and returns final response.
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        # Collect all events from streaming
        reasoning_steps = []
        final_content = ""
        sources = []
        credits_used = 2
        
        async for event in reasoning_orchestrator.process_with_reasoning(
            query=request.message,
            session_id=session_id,
            mode=request.mode
        ):
            event_type = event.get("type")
            event_data = event.get("data", {})
            
            if event_type in ["thinking", "searching", "writing"]:
                reasoning_steps.append({
                    "type": event_type,
                    "title": event_data.get("title", ""),
                    "content": event_data.get("content", ""),
                    "status": event_data.get("status", "")
                })
            elif event_type == "source":
                sources.append(event_data)
            elif event_type == "complete":
                final_content = event_data.get("content", "")
                credits_used = event_data.get("credits_used", 2)
            elif event_type == "error":
                return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "error": event_data.get("message", "Unknown error")
                    }
                )
        
        return {
            "success": True,
            "response": {
                "content": final_content,
                "sources": sources
            },
            "reasoning_steps": reasoning_steps,
            "credits_used": credits_used,
            "session_id": session_id
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


# =============================================================================
# Streaming Chat Endpoint (SSE)
# =============================================================================

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    SSE streaming chat endpoint with real-time reasoning.
    
    Event Types:
    - reasoning_start: Session started
    - thinking: AI reasoning step
    - searching: Searching for information
    - source: Found a source
    - writing: Writing response
    - content: Response content chunk
    - complete: Final response
    - error: Error occurred
    """
    
    async def generate() -> AsyncGenerator[str, None]:
        session_id = request.session_id or str(uuid.uuid4())
        
        try:
            async for event in reasoning_orchestrator.process_with_reasoning(
                query=request.message,
                session_id=session_id,
                mode=request.mode
            ):
                # Format as SSE
                yield f"data: {json.dumps(event)}\n\n"
                
                # Small delay for smoother streaming
                if event.get("type") in ["thinking", "searching", "writing"]:
                    await asyncio.sleep(0.05)
                    
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'data': {'message': str(e)}})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# =============================================================================
# File download endpoint
# =============================================================================

@app.get("/api/files/{file_id}")
async def get_file(file_id: str):
    """Download generated files"""
    file_path = f"/tmp/mcleuker_files/{file_id}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    if file_id.endswith(".xlsx"):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif file_id.endswith(".pdf"):
        media_type = "application/pdf"
    else:
        media_type = "application/octet-stream"
    
    return FileResponse(
        file_path,
        media_type=media_type,
        filename=file_id
    )
