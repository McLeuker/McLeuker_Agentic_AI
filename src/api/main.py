"""
McLeuker AI V5.1 - FastAPI Main Application
============================================
Structured response endpoints with file serving.

Design Principles:
1. STRUCTURED responses - always return ResponseContract format
2. FILE serving - real downloadable files
3. STREAMING support - for long responses
4. CORS enabled - for frontend access
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

# Use absolute imports
from src.core.orchestrator import orchestrator, OrchestratorResponse
from src.schemas.response_contract import ResponseContract


# FastAPI app
app = FastAPI(
    title="McLeuker AI V5.1",
    description="Agentic AI Platform with Response Contract Architecture",
    version="5.1.0"
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
        "version": "5.1.0",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "grok": bool(os.getenv("XAI_API_KEY")),
            "search": bool(os.getenv("PERPLEXITY_API_KEY") or os.getenv("XAI_API_KEY")),
            "supabase": bool(os.getenv("SUPABASE_URL"))
        },
        "features": {
            "response_contract": True,
            "file_generation": True,
            "intent_routing": True
        }
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "McLeuker AI",
        "version": "5.1.0",
        "description": "Agentic AI Platform with Response Contract Architecture",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "search": "/api/search",
            "files": "/api/files/{file_id}"
        }
    }


# Chat endpoint - main API
@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint with structured response.
    
    Returns ResponseContract format with:
    - summary: Brief overview
    - main_content: Clean prose (no inline citations)
    - sources: Separate source objects
    - files: Generated files (Excel, PDF, etc.)
    - key_insights: Bullet points
    - layout_sections: UI rendering hints
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


# File download endpoint
@app.get("/api/files/{file_id}")
async def get_file(file_id: str):
    """Download generated files"""
    # Files are stored in /tmp/mcleuker_files/
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


# Streaming chat endpoint (for long responses)
@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint for real-time response updates"""
    
    async def generate():
        # Send initial status
        yield json.dumps({"status": "processing", "step": "Analyzing query..."}) + "\n"
        await asyncio.sleep(0.1)
        
        # Process with orchestrator
        result = await orchestrator.process(
            query=request.message,
            session_id=request.session_id,
            mode=request.mode,
            domain_filter=request.domain_filter
        )
        
        # Send reasoning steps
        for step in result.reasoning_steps:
            yield json.dumps({"status": "processing", "step": step}) + "\n"
            await asyncio.sleep(0.1)
        
        # Send final result
        yield json.dumps({"status": "complete", "result": result.to_dict()}) + "\n"
    
    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson"
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
