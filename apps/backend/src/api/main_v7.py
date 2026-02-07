"""
McLeuker AI V7 - Multi-Model FastAPI Application
================================================
Enhanced API with Grok + Kimi K2.5 architecture.

Features:
1. Multi-model orchestration (Grok for reasoning, Kimi for execution)
2. SSE streaming for real-time updates
3. Tool calling and execution framework
4. Agent swarm pattern for parallel task execution
5. Memory-aware conversations
"""

import os
import json
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from pydantic import BaseModel
import asyncio

# Import orchestrators
from src.core.multi_model_orchestrator import get_multi_model_orchestrator
from src.core.orchestrator_v6 import orchestrator as v6_orchestrator, StreamEventType
from src.providers.kimi_provider import get_kimi_provider
from src.core.memory_manager import memory_manager


# FastAPI app
app = FastAPI(
    title="McLeuker AI V7",
    description="Multi-Model AI Platform with Grok + Kimi K2.5 Architecture",
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
    mode: str = "auto"  # quick, deep, auto
    domain_filter: Optional[str] = None
    use_multi_model: bool = True  # Use new multi-model architecture


class SearchRequest(BaseModel):
    query: str
    mode: str = "quick"


class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: dict


class MultiModalRequest(BaseModel):
    prompt: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    
    # Check model availability
    grok_available = bool(os.getenv("XAI_API_KEY"))
    kimi_available = bool(os.getenv("KIMI_API_KEY"))
    perplexity_available = bool(os.getenv("PERPLEXITY_API_KEY"))
    
    return {
        "status": "healthy",
        "version": "7.0.0",
        "timestamp": datetime.now().isoformat(),
        "models": {
            "grok": {
                "available": grok_available,
                "role": "reasoning",
                "model": "grok-4-fast-non-reasoning"
            },
            "kimi": {
                "available": kimi_available,
                "role": "execution",
                "model": "kimi-k2.5"
            },
            "perplexity": {
                "available": perplexity_available,
                "role": "search"
            }
        },
        "features": {
            "multi_model_orchestration": True,
            "tool_calling": kimi_available,
            "multimodal": kimi_available,
            "agent_swarm": True,
            "memory_system": True,
            "sse_streaming": True,
            "response_contract": True
        },
        "architecture": "Grok (reasoning) + Kimi K2.5 (execution)"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "McLeuker AI",
        "version": "7.0.0",
        "description": "Multi-Model AI Platform with Grok + Kimi K2.5",
        "architecture": {
            "reasoning_model": "Grok (xAI)",
            "execution_model": "Kimi K2.5 (Moonshot AI)",
            "pattern": "Agent Swarm with Task Decomposition"
        },
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "chat_stream": "/api/chat/stream",
            "search": "/api/search",
            "tools": "/api/tools",
            "tool_call": "/api/tools/call",
            "multimodal": "/api/multimodal",
            "history": "/api/history/{session_id}"
        }
    }


# Main chat endpoint
@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint with multi-model orchestration.
    
    Uses:
    - Grok for reasoning, planning, and synthesis
    - Kimi K2.5 for tool execution and specialized tasks
    """
    try:
        if request.use_multi_model:
            # Use new multi-model orchestrator
            orchestrator = get_multi_model_orchestrator()
            result = await orchestrator.process(
                query=request.message,
                session_id=request.session_id,
                mode=request.mode
            )
            return result
        else:
            # Fallback to V6 orchestrator
            result = await v6_orchestrator.process(
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
                "error": str(e)
            }
        )


# Streaming chat endpoint
@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint with real-time updates.
    
    Streams events showing:
    - Reasoning process (Grok)
    - Task execution (Kimi)
    - Tool calls and results
    - Final synthesis
    """
    
    async def generate():
        try:
            if request.use_multi_model:
                orchestrator = get_multi_model_orchestrator()
                async for event in orchestrator.process_stream(
                    query=request.message,
                    session_id=request.session_id,
                    mode=request.mode
                ):
                    yield f"data: {json.dumps(event)}\n\n"
                    await asyncio.sleep(0.05)
            else:
                async for event in v6_orchestrator.process_stream(
                    query=request.message,
                    session_id=request.session_id,
                    mode=request.mode,
                    domain_filter=request.domain_filter
                ):
                    yield f"data: {json.dumps(event)}\n\n"
                    await asyncio.sleep(0.05)
                    
        except Exception as e:
            error_event = {
                "type": "error",
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
    """Quick search endpoint"""
    try:
        result = await v6_orchestrator.process(
            query=request.query,
            mode=request.mode
        )
        return result.to_dict()
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


# Tools endpoint - list available tools
@app.get("/api/tools")
async def list_tools():
    """List all available tools for the execution model"""
    orchestrator = get_multi_model_orchestrator()
    
    tools_list = []
    for name, tool_def in orchestrator.tools.items():
        tools_list.append({
            "name": name,
            "description": tool_def["function"]["description"],
            "parameters": tool_def["function"]["parameters"]
        })
    
    return {
        "success": True,
        "tools": tools_list,
        "count": len(tools_list),
        "execution_model": "kimi-k2.5"
    }


# Direct tool call endpoint
@app.post("/api/tools/call")
async def call_tool(request: ToolCallRequest):
    """
    Directly call a tool using Kimi K2.5.
    
    This bypasses the full orchestration for simple tool calls.
    """
    try:
        kimi = get_kimi_provider()
        
        # Create a simple message asking to use the tool
        messages = [
            {
                "role": "system",
                "content": f"You must use the {request.tool_name} tool to complete this request."
            },
            {
                "role": "user",
                "content": f"Execute {request.tool_name} with arguments: {json.dumps(request.arguments)}"
            }
        ]
        
        orchestrator = get_multi_model_orchestrator()
        tools = [orchestrator.tools.get(request.tool_name)]
        
        if not tools[0]:
            raise HTTPException(status_code=404, detail=f"Tool not found: {request.tool_name}")
        
        response = await kimi.complete_with_tools(
            messages=messages,
            tools=tools,
            tool_executor=orchestrator._execute_tool,
            max_iterations=1
        )
        
        return {
            "success": True,
            "tool": request.tool_name,
            "result": response.content,
            "reasoning": response.reasoning_content
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


# Multimodal endpoint
@app.post("/api/multimodal")
async def multimodal_analysis(request: MultiModalRequest):
    """
    Analyze images or videos using Kimi K2.5's multimodal capabilities.
    """
    try:
        kimi = get_kimi_provider()
        
        if request.image_url:
            # For URL-based images, we'd need to download first
            # For now, return a placeholder
            return {
                "success": True,
                "analysis": f"Image analysis for: {request.prompt}",
                "model": "kimi-k2.5",
                "note": "Full multimodal support requires base64 encoded images"
            }
        elif request.video_url:
            return {
                "success": True,
                "analysis": f"Video analysis for: {request.prompt}",
                "model": "kimi-k2.5",
                "note": "Full multimodal support requires base64 encoded videos"
            }
        else:
            # Text-only request
            messages = [{"role": "user", "content": request.prompt}]
            response = await kimi.complete(messages=messages)
            
            return {
                "success": True,
                "response": response.content,
                "reasoning": response.reasoning_content,
                "model": "kimi-k2.5"
            }
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
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
            content={"success": False, "error": str(e)}
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
            content={"success": False, "error": str(e)}
        )


# Model info endpoint
@app.get("/api/models")
async def get_models():
    """Get information about available models"""
    return {
        "models": {
            "grok": {
                "provider": "xAI",
                "model": "grok-4-fast-non-reasoning",
                "role": "reasoning",
                "capabilities": [
                    "Complex reasoning",
                    "Task planning",
                    "Result synthesis",
                    "Creative writing"
                ],
                "available": bool(os.getenv("XAI_API_KEY"))
            },
            "kimi": {
                "provider": "Moonshot AI",
                "model": "kimi-k2.5",
                "role": "execution",
                "capabilities": [
                    "Tool calling (up to 128 tools)",
                    "Code execution",
                    "Multimodal (images, videos)",
                    "256K context window",
                    "Thinking mode"
                ],
                "available": bool(os.getenv("KIMI_API_KEY"))
            },
            "perplexity": {
                "provider": "Perplexity AI",
                "model": "llama-3.1-sonar-small-128k-online",
                "role": "search",
                "capabilities": [
                    "Real-time web search",
                    "Citation extraction"
                ],
                "available": bool(os.getenv("PERPLEXITY_API_KEY"))
            }
        },
        "architecture": "Multi-model orchestration with agent swarm pattern"
    }


# File download endpoint
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
