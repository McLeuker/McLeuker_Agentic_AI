"""
McLeuker AI V5.1 - FastAPI Main Application
============================================
API endpoints with response contract enforcement and file serving.

Key improvements:
1. /api/chat returns ResponseContract (structured JSON)
2. /files/{filename} serves real downloadable files
3. Proper CORS for frontend integration
4. Health check with service status
"""

import os
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn

# Import V5.1 components
from ..core.orchestrator import orchestrator
from ..schemas.response_contract import ResponseContract, IntentType, DomainType
from ..services.file_generator import file_generator
from ..layers.intent.intent_router import intent_router


# === APP SETUP ===
app = FastAPI(
    title="McLeuker AI V5.1",
    description="Fashion Intelligence Platform with Response Contract Architecture",
    version="5.1.0"
)

# CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === REQUEST MODELS ===
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    mode: str = "quick"  # quick or deep
    domain: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    services: dict


# === ENDPOINTS ===

@app.get("/health")
async def health_check() -> HealthResponse:
    """Health check endpoint for Railway deployment"""
    return HealthResponse(
        status="healthy",
        version="5.1.0",
        timestamp=datetime.utcnow().isoformat(),
        services={
            "grok": bool(os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY")),
            "search": bool(os.getenv("SERPER_API_KEY")),
            "file_generation": True,
            "intent_router": True
        }
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "McLeuker AI",
        "version": "5.1.0",
        "architecture": "Response Contract",
        "features": [
            "Structured output (no inline citations)",
            "Real file generation (Excel, PDF, CSV)",
            "Persistent sources",
            "Intent-based routing",
            "Domain-flexible responses"
        ]
    }


@app.post("/api/chat")
async def chat(request: ChatRequest) -> dict:
    """
    Main chat endpoint - returns ResponseContract.
    
    The response follows the contract:
    - main_content: Clean prose WITHOUT citations
    - sources: Persistent array of source objects
    - files: Real downloadable file URLs
    - key_insights: Structured bullet points
    - tables: Structured table data
    """
    try:
        # Process with V5.1 orchestrator
        response = await orchestrator.process(
            message=request.message,
            session_id=request.session_id,
            mode=request.mode
        )
        
        # Convert ResponseContract to dict for JSON response
        return response.dict()
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "session_id": request.session_id,
            "intent": IntentType.GENERAL.value,
            "domain": DomainType.GENERAL.value,
            "summary": "An error occurred",
            "main_content": f"I apologize, but I encountered an error: {str(e)}",
            "sources": [],
            "files": [],
            "key_insights": [],
            "tables": [],
            "action_items": [],
            "follow_up_questions": ["Would you like to try again?"],
            "credits_used": 0
        }


@app.post("/api/classify")
async def classify_intent(request: ChatRequest) -> dict:
    """
    Classify user intent without generating response.
    Useful for frontend to prepare UI before full response.
    """
    classification = intent_router.classify(request.message)
    return {
        "intent": classification['intent'].value,
        "domain": classification['domain'].value,
        "confidence": classification['confidence'],
        "requires_search": classification['requires_search'],
        "requires_file_generation": classification['requires_file_generation'],
        "suggested_mode": classification['suggested_mode']
    }


@app.get("/files/{filename}")
async def download_file(filename: str):
    """
    Serve generated files for download.
    This enables real file downloads instead of text-pretending-to-be-files.
    """
    filepath = file_generator.get_file_path(filename)
    
    if not filepath:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type
    if filename.endswith('.xlsx'):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif filename.endswith('.pdf'):
        media_type = "application/pdf"
    elif filename.endswith('.csv'):
        media_type = "text/csv"
    elif filename.endswith('.pptx'):
        media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    else:
        media_type = "application/octet-stream"
    
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type=media_type
    )


@app.get("/api/sources/{session_id}")
async def get_sources(session_id: str):
    """
    Get sources for a session - enables persistent source display.
    Sources don't disappear on re-render because they're stored server-side.
    """
    # In production, this would fetch from database
    # For now, return empty (sources are included in chat response)
    return {
        "session_id": session_id,
        "sources": [],
        "message": "Sources are included in chat response. This endpoint is for future persistent storage."
    }


# === ERROR HANDLERS ===

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "detail": "Internal server error"
        }
    )


# === MAIN ===

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
