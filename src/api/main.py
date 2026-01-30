"""
McLeuker Agentic AI Platform - FastAPI Backend

Main API server providing endpoints for the agentic AI platform.
"""

import os
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from src.agents.orchestrator import UnifiedAgentOrchestrator, get_orchestrator
from src.models.schemas import (
    Task,
    TaskRequest,
    TaskResponse,
    TaskStatus,
    OutputFormat,
    Message,
    Conversation
)
from src.tools.ai_search import AISearchPlatform
from src.tools.media_services import ElevenLabsService, HuggingFaceService
from src.config.settings import get_settings


# ============================================================================
# Request/Response Models
# ============================================================================

class PromptRequest(BaseModel):
    """Request model for processing a prompt."""
    prompt: str = Field(..., description="The user's prompt/request")
    user_id: Optional[str] = Field(None, description="Optional user ID")
    preferred_outputs: Optional[List[str]] = Field(None, description="Preferred output formats")
    domain_hint: Optional[str] = Field(None, description="Domain hint for the task")


class ChatRequest(BaseModel):
    """Request model for chat interaction."""
    message: str = Field(..., description="The user's message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")


class SearchRequest(BaseModel):
    """Request model for AI search."""
    query: str = Field(..., description="The search query")
    num_results: int = Field(10, description="Number of results to return")
    summarize: bool = Field(True, description="Whether to summarize results")
    scrape_top: int = Field(0, description="Number of top results to scrape")


class ResearchRequest(BaseModel):
    """Request model for topic research."""
    topic: str = Field(..., description="The topic to research")
    depth: str = Field("medium", description="Research depth: light, medium, or deep")


class QuickAnswerRequest(BaseModel):
    """Request model for quick answers."""
    question: str = Field(..., description="The question to answer")


class TTSRequest(BaseModel):
    """Request model for text-to-speech."""
    text: str = Field(..., description="The text to convert to speech")
    voice: str = Field("rachel", description="Voice name to use")


class SummarizeRequest(BaseModel):
    """Request model for text summarization."""
    text: str = Field(..., description="The text to summarize")
    max_length: int = Field(150, description="Maximum summary length")


class TaskStatusResponse(BaseModel):
    """Response model for task status."""
    task_id: str
    status: str
    message: str
    progress: Optional[Dict[str, Any]] = None
    files: Optional[List[Dict[str, Any]]] = None


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str
    timestamp: str


# ============================================================================
# Application Setup
# ============================================================================

# Store for active tasks and conversations
active_tasks: Dict[str, Task] = {}
conversations: Dict[str, Conversation] = {}
websocket_connections: Dict[str, WebSocket] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    settings = get_settings()
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    os.makedirs(settings.TEMP_DIR, exist_ok=True)
    print(f"McLeuker AI Platform starting...")
    print(f"Output directory: {settings.OUTPUT_DIR}")
    
    # Validate API keys
    key_status = settings.validate_required_keys()
    print(f"LLM configured: {key_status['has_llm']}")
    print(f"Search configured: {key_status['has_search']}")
    
    yield
    
    # Shutdown
    print("McLeuker AI Platform shutting down...")


app = FastAPI(
    title="McLeuker Agentic AI Platform",
    description="AI-powered platform for intelligent task execution and research",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for Lovable integration
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/api/status")
async def get_status():
    """Get the current status of the platform."""
    orchestrator = get_orchestrator()
    state = orchestrator.get_state()
    settings = get_settings()
    
    return {
        "status": "operational",
        "agent_state": state,
        "active_tasks": len(active_tasks),
        "supported_outputs": [f.value for f in OutputFormat],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/config/status")
async def get_config_status():
    """Get the configuration status of all API keys and services."""
    settings = get_settings()
    key_status = settings.validate_required_keys()
    
    return {
        "status": "configured" if key_status["has_llm"] else "missing_llm",
        "services": key_status,
        "default_llm": settings.DEFAULT_LLM_PROVIDER,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Task Processing Endpoints
# ============================================================================

@app.post("/api/tasks", response_model=TaskStatusResponse)
async def create_task(
    request: PromptRequest,
    background_tasks: BackgroundTasks
):
    """
    Create and process a new task.
    
    This endpoint accepts a prompt and processes it through all 5 layers:
    1. Task Interpretation
    2. LLM Reasoning
    3. Web Research
    4. Logic & Structuring
    5. Execution
    """
    orchestrator = get_orchestrator()
    
    # Create task request
    task_request = TaskRequest(
        prompt=request.prompt,
        user_id=request.user_id,
        preferred_outputs=[OutputFormat(o) for o in request.preferred_outputs] if request.preferred_outputs else None
    )
    
    # Process task in background
    async def process_task_background():
        task = await orchestrator.process_task(task_request)
        active_tasks[task.id] = task
        
        # Notify via WebSocket if connected
        if request.user_id and request.user_id in websocket_connections:
            ws = websocket_connections[request.user_id]
            try:
                await ws.send_json({
                    "type": "task_complete",
                    "task_id": task.id,
                    "status": task.status.value,
                    "files": [f.dict() for f in task.execution_result.files] if task.execution_result else []
                })
            except Exception:
                pass
    
    # Start processing
    background_tasks.add_task(process_task_background)
    
    # Return immediate response
    task_id = f"task_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    return TaskStatusResponse(
        task_id=task_id,
        status="processing",
        message="Task is being processed. Use the task ID to check status.",
        progress={"phase": 1, "description": "Understanding your request..."}
    )


@app.post("/api/tasks/sync")
async def create_task_sync(request: PromptRequest):
    """
    Create and process a task synchronously.
    
    This endpoint waits for the task to complete before returning.
    Use for simpler integrations or when you need immediate results.
    """
    orchestrator = get_orchestrator()
    
    task_request = TaskRequest(
        prompt=request.prompt,
        user_id=request.user_id
    )
    
    task = await orchestrator.process_task(task_request)
    active_tasks[task.id] = task
    
    return {
        "task_id": task.id,
        "status": task.status.value,
        "interpretation": task.interpretation.dict() if task.interpretation else None,
        "files": [f.dict() for f in task.execution_result.files] if task.execution_result else [],
        "message": task.execution_result.message if task.execution_result else None,
        "error": task.error_message
    }


@app.get("/api/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Get the status of a task."""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = active_tasks[task_id]
    
    files = None
    if task.execution_result and task.execution_result.files:
        files = [f.dict() for f in task.execution_result.files]
    
    return TaskStatusResponse(
        task_id=task_id,
        status=task.status.value,
        message=task.execution_result.message if task.execution_result else "Processing...",
        files=files
    )


@app.get("/api/tasks/{task_id}/files")
async def get_task_files(task_id: str):
    """Get the files generated by a task."""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = active_tasks[task_id]
    
    if not task.execution_result or not task.execution_result.files:
        return {"files": []}
    
    return {
        "files": [f.dict() for f in task.execution_result.files]
    }


@app.get("/api/files/{filename}")
async def download_file(filename: str):
    """Download a generated file."""
    settings = get_settings()
    filepath = os.path.join(settings.OUTPUT_DIR, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        filepath,
        filename=filename,
        media_type="application/octet-stream"
    )


# ============================================================================
# Chat Endpoints
# ============================================================================

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Chat with the AI agent.
    
    The agent will analyze the message and determine whether to:
    - Execute a task
    - Perform a search
    - Answer a question
    - Have a conversation
    """
    orchestrator = get_orchestrator()
    
    # Get or create conversation
    conversation = None
    if request.conversation_id and request.conversation_id in conversations:
        conversation = conversations[request.conversation_id]
    
    # Process the chat
    response = await orchestrator.chat(request.message, conversation)
    
    # Update conversation
    if conversation:
        conversation.messages.append(Message(
            role="user",
            content=request.message
        ))
        conversation.messages.append(Message(
            role="assistant",
            content=response["message"]
        ))
    
    return response


# ============================================================================
# Search Endpoints
# ============================================================================

@app.post("/api/search")
async def ai_search(request: SearchRequest):
    """
    Perform an AI-powered search.
    
    Features:
    - Query expansion
    - Result ranking
    - Content summarization
    - Follow-up question generation
    """
    search_platform = AISearchPlatform()
    
    result = await search_platform.search(
        query=request.query,
        num_results=request.num_results,
        summarize=request.summarize,
        scrape_top=request.scrape_top
    )
    
    return result


@app.post("/api/search/quick")
async def quick_answer(request: QuickAnswerRequest):
    """Get a quick answer to a question."""
    search_platform = AISearchPlatform()
    return await search_platform.quick_answer(request.question)


@app.post("/api/research")
async def research_topic(request: ResearchRequest):
    """
    Perform in-depth research on a topic.
    
    Generates research questions, searches for answers,
    and synthesizes findings into a comprehensive overview.
    """
    search_platform = AISearchPlatform()
    return await search_platform.research_topic(
        topic=request.topic,
        depth=request.depth
    )


# ============================================================================
# Media Services Endpoints
# ============================================================================

@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech using ElevenLabs.
    
    Returns audio as a streaming response.
    """
    settings = get_settings()
    if not settings.ELEVENLABS_API_KEY:
        raise HTTPException(status_code=503, detail="Text-to-speech service not configured")
    
    tts_service = ElevenLabsService()
    audio_bytes = await tts_service.text_to_speech(
        text=request.text,
        voice_name=request.voice
    )
    
    if not audio_bytes:
        raise HTTPException(status_code=500, detail="Failed to generate speech")
    
    return StreamingResponse(
        iter([audio_bytes]),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "attachment; filename=speech.mp3"}
    )


@app.get("/api/tts/voices")
async def get_tts_voices():
    """Get available text-to-speech voices."""
    settings = get_settings()
    if not settings.ELEVENLABS_API_KEY:
        raise HTTPException(status_code=503, detail="Text-to-speech service not configured")
    
    tts_service = ElevenLabsService()
    voices = await tts_service.get_voices()
    
    return {"voices": voices}


@app.post("/api/summarize")
async def summarize_text(request: SummarizeRequest):
    """
    Summarize text using Hugging Face models.
    """
    settings = get_settings()
    if not settings.HUGGINGFACE_API_KEY:
        raise HTTPException(status_code=503, detail="Summarization service not configured")
    
    hf_service = HuggingFaceService()
    summary = await hf_service.summarize(
        text=request.text,
        max_length=request.max_length
    )
    
    if not summary:
        raise HTTPException(status_code=500, detail="Failed to generate summary")
    
    return {"summary": summary}


# ============================================================================
# WebSocket for Real-time Updates
# ============================================================================

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time task updates."""
    await websocket.accept()
    websocket_connections[user_id] = websocket
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            
            # Handle ping/pong
            if data == "ping":
                await websocket.send_text("pong")
            
    except WebSocketDisconnect:
        if user_id in websocket_connections:
            del websocket_connections[user_id]


# ============================================================================
# Interpretation Endpoint (for debugging/testing)
# ============================================================================

@app.post("/api/interpret")
async def interpret_prompt(request: PromptRequest):
    """
    Interpret a prompt without executing the full task.
    
    Useful for testing and debugging the task interpretation layer.
    """
    orchestrator = get_orchestrator()
    interpretation = await orchestrator.interpretation_layer.interpret(request.prompt)
    
    return {
        "interpretation": interpretation.dict(),
        "message": "Prompt interpreted successfully"
    }


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
