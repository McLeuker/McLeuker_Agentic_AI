"""
McLeuker AI V5.1 - FastAPI Main Application
============================================
API endpoints with structured response format.
"""

import os
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

# Import from orchestrator_v2 which has the fixed ResponseContract field names
from src.core.orchestrator_v2 import orchestrator, OrchestratorResponse

app = FastAPI(
    title="McLeuker AI V5.1",
    description="Agentic AI Platform with Response Contract Architecture",
    version="5.1.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    mode: str = "auto"  # "quick", "deep", "auto"
    domain_filter: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    services: dict
    features: dict


# Health Check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with service status"""
    return HealthResponse(
        status="healthy",
        version="5.1.0",
        timestamp=datetime.utcnow().isoformat(),
        services={
            "grok": bool(os.getenv("XAI_API_KEY")),
            "search": bool(os.getenv("PERPLEXITY_API_KEY") or os.getenv("XAI_API_KEY")),
            "supabase": bool(os.getenv("SUPABASE_URL"))
        },
        features={
            "response_contract": True,
            "file_generation": True,
            "intent_routing": True
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "McLeuker AI",
        "version": "5.1.0",
        "status": "operational",
        "docs": "/docs"
    }


# Chat endpoint
@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Process a chat message and return structured response.
    
    The response follows the ResponseContract schema:
    - summary: Brief overview
    - main_content: Detailed response (no inline citations)
    - sources: Array of source objects
    - key_insights: Array of insight objects
    - files: Array of generated files (if any)
    - action_items: Suggested next steps
    - follow_up_questions: Suggested follow-ups
    """
    try:
        result = await orchestrator.process(
            query=request.message,
            session_id=request.session_id,
            mode=request.mode,
            domain_filter=request.domain_filter
        )
        
        return result.to_dict()
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "reasoning_steps": ["Error occurred during processing"]
            }
        )


# File download endpoint
@app.get("/api/files/{file_id}")
async def download_file(file_id: str):
    """Download a generated file"""
    file_path = f"/tmp/mcleuker_files/{file_id}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="application/octet-stream"
    )


# Legacy endpoint for backward compatibility
@app.post("/chat")
async def chat_legacy(request: ChatRequest):
    """Legacy chat endpoint (redirects to /api/chat)"""
    return await chat(request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
