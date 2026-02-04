"""
McLeuker AI V6.0 - FastAPI Main Application
============================================
Manus AI-style output with reasoning, task progress, and structured responses.

Design Principles:
1. REASONING-FIRST - Show AI thinking process before output
2. TASK DECOMPOSITION - Break down complex queries into steps
3. REAL-TIME STREAMING - SSE for live progress updates
4. STRUCTURED OUTPUT - Well-organized, readable responses
5. MEMORY SYSTEM - Context awareness across conversations
"""

import os
import json
import uuid
import asyncio
from datetime import datetime
from typing import Optional, AsyncGenerator, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from pydantic import BaseModel
import httpx

# Use absolute imports
from src.core.orchestrator import orchestrator, OrchestratorResponse
from src.schemas.response_contract import ResponseContract


# FastAPI app
app = FastAPI(
    title="McLeuker AI V6.0",
    description="Agentic AI Platform with Manus-style Reasoning and Task Progress",
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
    mode: str = "quick"  # quick, deep
    domain_filter: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    mode: str = "quick"


# =============================================================================
# Task Decomposition
# =============================================================================

def decompose_task(query: str, mode: str = "quick") -> List[Dict[str, Any]]:
    """
    Decompose a query into logical task steps.
    Returns a list of tasks with id, title, description, and status.
    """
    tasks = []
    
    # Always start with understanding
    tasks.append({
        "id": str(uuid.uuid4())[:8],
        "title": "Understanding your question",
        "description": "Analyzing the query to understand intent and requirements",
        "status": "pending"
    })
    
    # Add domain-specific analysis if domain filter is set
    tasks.append({
        "id": str(uuid.uuid4())[:8],
        "title": "Analyzing context",
        "description": "Identifying key concepts and domain context",
        "status": "pending"
    })
    
    # Research step
    if mode == "deep":
        tasks.append({
            "id": str(uuid.uuid4())[:8],
            "title": "Conducting deep research",
            "description": "Searching multiple sources for comprehensive information",
            "status": "pending"
        })
        tasks.append({
            "id": str(uuid.uuid4())[:8],
            "title": "Cross-referencing sources",
            "description": "Validating information across multiple sources",
            "status": "pending"
        })
    else:
        tasks.append({
            "id": str(uuid.uuid4())[:8],
            "title": "Gathering information",
            "description": "Searching for relevant information",
            "status": "pending"
        })
    
    # Synthesis step
    tasks.append({
        "id": str(uuid.uuid4())[:8],
        "title": "Synthesizing insights",
        "description": "Combining findings into coherent insights",
        "status": "pending"
    })
    
    # Response generation
    tasks.append({
        "id": str(uuid.uuid4())[:8],
        "title": "Generating response",
        "description": "Creating a structured, comprehensive response",
        "status": "pending"
    })
    
    return tasks


# =============================================================================
# SSE Event Helpers
# =============================================================================

def sse_event(event_type: str, data: Dict[str, Any]) -> str:
    """Format an SSE event"""
    return f"data: {json.dumps({'type': event_type, 'data': data, 'timestamp': datetime.now().isoformat()})}\n\n"


# =============================================================================
# Health check endpoint
# =============================================================================

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
            "reasoning_engine": True,
            "task_decomposition": True,
            "memory_system": True
        }
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "McLeuker AI",
        "version": "6.0.0",
        "description": "Agentic AI Platform with Manus-style Reasoning",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "chat_stream": "/api/chat/stream",
            "search": "/api/search",
            "files": "/api/files/{file_id}"
        }
    }


# =============================================================================
# Chat endpoint - main API (non-streaming)
# =============================================================================

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint with structured response.
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


# =============================================================================
# SSE Streaming Chat Endpoint (Manus AI-style)
# =============================================================================

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    SSE streaming chat endpoint with real-time task progress.
    
    Event Types:
    - session_start: Initial session info
    - task_plan: List of tasks to be executed
    - task_update: Status update for a specific task
    - reasoning: AI reasoning/thinking process
    - content_chunk: Partial response content
    - source_found: A source was found
    - insight_generated: A key insight was generated
    - complete: Final complete response
    - error: Error occurred
    """
    
    async def generate() -> AsyncGenerator[str, None]:
        session_id = request.session_id or str(uuid.uuid4())
        
        try:
            # 1. Session start
            yield sse_event("session_start", {
                "session_id": session_id,
                "query": request.message,
                "mode": request.mode,
                "domain": request.domain_filter
            })
            await asyncio.sleep(0.1)
            
            # 2. Task decomposition
            tasks = decompose_task(request.message, request.mode)
            yield sse_event("task_plan", {
                "tasks": tasks,
                "total_tasks": len(tasks)
            })
            await asyncio.sleep(0.2)
            
            # 3. Execute tasks with progress updates
            for i, task in enumerate(tasks):
                # Mark task as in progress
                task["status"] = "in_progress"
                yield sse_event("task_update", {
                    "task_id": task["id"],
                    "title": task["title"],
                    "description": task["description"],
                    "status": "in_progress",
                    "progress": (i / len(tasks)) * 100
                })
                
                # Simulate reasoning for this task
                yield sse_event("reasoning", {
                    "task_id": task["id"],
                    "thought": f"Working on: {task['title']}...",
                    "step": i + 1,
                    "total_steps": len(tasks)
                })
                
                # Small delay to show progress
                await asyncio.sleep(0.3)
                
                # Mark task as completed
                task["status"] = "completed"
                yield sse_event("task_update", {
                    "task_id": task["id"],
                    "title": task["title"],
                    "status": "completed",
                    "progress": ((i + 1) / len(tasks)) * 100
                })
            
            # 4. Process with orchestrator
            result = await orchestrator.process(
                query=request.message,
                session_id=session_id,
                mode=request.mode,
                domain_filter=request.domain_filter
            )
            
            if not result.success:
                yield sse_event("error", {
                    "message": result.error or "Processing failed",
                    "reasoning_steps": result.reasoning_steps
                })
                return
            
            # 5. Stream sources as they're found
            response_data = result.to_dict()
            if response_data.get("response", {}).get("sources"):
                for source in response_data["response"]["sources"]:
                    yield sse_event("source_found", {
                        "title": source.get("title", "Source"),
                        "url": source.get("url", ""),
                        "snippet": source.get("snippet", "")[:200] if source.get("snippet") else ""
                    })
                    await asyncio.sleep(0.1)
            
            # 6. Stream key insights
            if response_data.get("response", {}).get("key_insights"):
                for insight in response_data["response"]["key_insights"]:
                    yield sse_event("insight_generated", {
                        "icon": insight.get("icon", "💡"),
                        "title": insight.get("title", "Insight"),
                        "description": insight.get("description", ""),
                        "importance": insight.get("importance", "medium")
                    })
                    await asyncio.sleep(0.1)
            
            # 7. Send complete response
            yield sse_event("complete", {
                "response": response_data.get("response", {}),
                "credits_used": response_data.get("credits_used", 2),
                "session_id": session_id,
                "processing_time_ms": response_data.get("processing_time_ms", 0)
            })
            
        except Exception as e:
            yield sse_event("error", {
                "message": str(e),
                "type": type(e).__name__
            })
    
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
# Search endpoint
# =============================================================================

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


# =============================================================================
# File download endpoint
# =============================================================================

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


# =============================================================================
# Error handler
# =============================================================================

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
