"""
McLeuker Agentic AI Platform - FastAPI Backend v2.0

Complete agentic AI platform with:
- 5-layer reasoning system
- Conversation memory
- Real-time web search
- Professional file generation
- Structured output formatting

Similar to Manus AI and ChatGPT capabilities.
"""

import os
import json
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from src.config.settings import get_settings
from src.memory.conversation_memory import (
    Conversation,
    ConversationMemoryStore,
    get_memory_store
)
from src.memory.context_extractor import ContextExtractor
from src.reasoning.reasoning_engine import ReasoningEngine, ReasoningChain
from src.search.web_search import MultiProviderSearch, get_search_system
from src.files.excel_generator import ProfessionalExcelGenerator, ExcelSheet, get_excel_generator
from src.files.pdf_generator import ProfessionalPDFGenerator, PDFSection, get_pdf_generator
from src.files.word_generator import ProfessionalWordGenerator, WordSection, get_word_generator
from src.output.formatter import OutputFormatter, OutputStyle, get_formatter
from src.utils.llm_provider import LLMProvider, LLMFactory


# ============================================================================
# Request/Response Models
# ============================================================================

class ChatRequest(BaseModel):
    """Request model for chat interaction."""
    message: str = Field(..., description="The user's message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    user_id: Optional[str] = Field(None, description="User ID")
    mode: str = Field("quick", description="Chat mode: quick, deep, or auto")


class ChatResponse(BaseModel):
    """Response model for chat."""
    message: str
    conversation_id: str
    reasoning: Optional[str] = None
    sources: Optional[List[Dict[str, str]]] = None
    files: Optional[List[Dict[str, Any]]] = None
    follow_up_questions: Optional[List[str]] = None
    credits_used: int = 5
    mode: str = "quick"


class SearchRequest(BaseModel):
    """Request model for AI search."""
    query: str = Field(..., description="The search query")
    mode: str = Field("quick", description="Search mode: quick or deep")
    num_results: int = Field(10, description="Number of results")


class FileGenerationRequest(BaseModel):
    """Request model for file generation."""
    content: str = Field(..., description="Content to generate file from")
    file_type: str = Field("excel", description="File type: excel, pdf, word")
    title: Optional[str] = Field(None, description="Document title")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="Structured data for Excel")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str
    timestamp: str
    services: Dict[str, bool]


# ============================================================================
# Application Setup
# ============================================================================

# Global instances
memory_store: Optional[ConversationMemoryStore] = None
llm_provider: Optional[LLMProvider] = None
search_system: Optional[MultiProviderSearch] = None
reasoning_engine: Optional[ReasoningEngine] = None
context_extractor: Optional[ContextExtractor] = None
output_formatter: Optional[OutputFormatter] = None
excel_generator: Optional[ProfessionalExcelGenerator] = None
pdf_generator: Optional[ProfessionalPDFGenerator] = None
word_generator: Optional[ProfessionalWordGenerator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global memory_store, llm_provider, search_system, reasoning_engine
    global context_extractor, output_formatter
    global excel_generator, pdf_generator, word_generator
    
    settings = get_settings()
    
    # Create directories
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    os.makedirs(settings.TEMP_DIR, exist_ok=True)
    
    print("🚀 McLeuker AI Platform v2.0 starting...")
    
    # Initialize components
    memory_store = get_memory_store()
    llm_provider = LLMFactory.get_default()
    search_system = get_search_system(llm_provider)
    reasoning_engine = ReasoningEngine(llm_provider)
    context_extractor = ContextExtractor(llm_provider)
    output_formatter = get_formatter()
    excel_generator = get_excel_generator(settings.OUTPUT_DIR)
    pdf_generator = get_pdf_generator(settings.OUTPUT_DIR)
    word_generator = get_word_generator(settings.OUTPUT_DIR)
    
    # Validate API keys
    key_status = settings.validate_required_keys()
    print(f"✅ LLM configured: {key_status['has_llm']}")
    print(f"✅ Search configured: {key_status['has_search']}")
    print(f"✅ Perplexity configured: {key_status.get('has_perplexity', False)}")
    
    yield
    
    print("👋 McLeuker AI Platform shutting down...")


app = FastAPI(
    title="McLeuker Agentic AI Platform",
    description="Frontier-level AI platform with reasoning, memory, and file generation",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
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
    key_status = settings.validate_required_keys()
    
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        timestamp=datetime.utcnow().isoformat(),
        services=key_status
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return await root()


@app.get("/api/status")
async def get_status():
    """Get platform status."""
    settings = get_settings()
    key_status = settings.validate_required_keys()
    
    return {
        "status": "operational",
        "version": "2.0.0",
        "services": key_status,
        "features": {
            "conversation_memory": True,
            "real_time_search": key_status.get("has_perplexity", False) or key_status.get("has_search", False),
            "file_generation": True,
            "reasoning_display": True
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Chat Endpoints - Main Interaction
# ============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint with full agentic capabilities.
    
    Features:
    - Conversation memory (remembers previous messages)
    - Real-time web search when needed
    - File generation on request
    - Structured reasoning display
    """
    global memory_store, llm_provider, search_system, reasoning_engine
    global context_extractor, output_formatter
    
    # Get or create conversation
    conversation = memory_store.get_or_create_conversation(
        request.conversation_id,
        request.user_id
    )
    
    # Add user message to memory
    conversation.add_message("user", request.message)
    
    # Extract and update context
    await context_extractor.extract_context(conversation, request.message)
    
    # Analyze the query with reasoning engine
    reasoning_chain = await reasoning_engine.analyze_query(
        request.message,
        {"topics": conversation.context.topics, "entities": conversation.context.entities}
    )
    
    # Determine credits and mode
    mode = request.mode
    credits_used = 5 if mode == "quick" else 50
    
    # Build response
    response_data = {
        "message": "",
        "conversation_id": conversation.id,
        "reasoning": None,
        "sources": None,
        "files": None,
        "follow_up_questions": [],
        "credits_used": credits_used,
        "mode": mode
    }
    
    try:
        # Check if real-time search is needed
        if reasoning_chain.requires_search:
            # Perform real-time search
            search_result = await search_system.smart_search(request.message)
            
            answer = search_result.get("answer", "")
            sources = search_result.get("sources", [])
            
            # Format response
            formatted = output_formatter.format_search_response(
                request.message,
                answer,
                [{"title": s, "url": s} for s in sources[:5]] if sources else [],
                is_real_time=True
            )
            
            response_data["message"] = formatted.to_markdown()
            response_data["sources"] = formatted.sources
            response_data["follow_up_questions"] = formatted.follow_up_questions
            
            # Show reasoning if deep mode
            if mode == "deep":
                response_data["reasoning"] = reasoning_chain.to_display()
                credits_used = 100
        
        # Check if file generation is needed
        elif reasoning_chain.requires_file_generation:
            # Generate file based on request
            file_result = await _generate_file_from_request(
                request.message,
                reasoning_chain.output_format,
                conversation
            )
            
            if file_result:
                formatted = output_formatter.format_file_generation_response(
                    [file_result],
                    f"I've created the {reasoning_chain.output_format} file based on your request."
                )
                response_data["message"] = formatted.to_markdown()
                response_data["files"] = formatted.files
                credits_used = 50
            else:
                response_data["message"] = "I encountered an issue generating the file. Please try again."
        
        else:
            # Regular conversation with context
            response_text = await _generate_contextual_response(
                request.message,
                conversation,
                mode
            )
            
            formatted = output_formatter.format_response(
                response_text,
                style=OutputStyle.CONVERSATIONAL if mode == "quick" else OutputStyle.DETAILED,
                reasoning=reasoning_chain.to_display() if mode == "deep" else None
            )
            
            response_data["message"] = formatted.to_markdown()
            response_data["follow_up_questions"] = formatted.follow_up_questions
            
            if mode == "deep":
                response_data["reasoning"] = reasoning_chain.to_display()
        
        # Add assistant response to memory
        conversation.add_message("assistant", response_data["message"])
        
        response_data["credits_used"] = credits_used
        
    except Exception as e:
        print(f"Chat error: {e}")
        response_data["message"] = f"I apologize, but I encountered an error processing your request. Please try again."
        conversation.add_message("assistant", response_data["message"])
    
    return ChatResponse(**response_data)


async def _generate_contextual_response(
    message: str,
    conversation: Conversation,
    mode: str
) -> str:
    """Generate a response with full conversation context."""
    global llm_provider, context_extractor
    
    # Build context prompt
    context_prompt = context_extractor.build_context_prompt(conversation)
    
    # Get conversation history
    history_messages = conversation.get_messages_for_llm(max_messages=10)
    
    # Build system prompt
    system_prompt = f"""You are McLeuker AI, an advanced AI assistant with the following capabilities:
- Deep knowledge across many domains
- Real-time information access
- File generation (Excel, PDF, Word)
- Intelligent reasoning and analysis

{context_prompt}

Guidelines:
1. ALWAYS remember and reference previous messages in this conversation
2. Be helpful, accurate, and thorough
3. Use emojis appropriately to make responses engaging
4. Structure responses with clear sections when appropriate
5. If you don't know something current, say so and offer to search
6. Provide specific, actionable information

Current date: {datetime.utcnow().strftime('%B %d, %Y')}"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history_messages)
    messages.append({"role": "user", "content": message})
    
    # Generate response
    response = await llm_provider.complete(
        messages=messages,
        temperature=0.7 if mode == "quick" else 0.5,
        max_tokens=1000 if mode == "quick" else 2000
    )
    
    return response.get("content", "I apologize, I couldn't generate a response.")


async def _generate_file_from_request(
    message: str,
    file_type: str,
    conversation: Conversation
) -> Optional[Dict[str, Any]]:
    """Generate a file based on the user's request."""
    global llm_provider, excel_generator, pdf_generator, word_generator
    
    try:
        # Extract data structure from message using LLM
        extraction_prompt = f"""Extract structured data from this request for generating a {file_type} file:

Request: {message}

Provide the data in JSON format with:
- "title": Document title
- "data": Array of objects for the content
- "columns": Array of column names (for Excel)

Example for Excel:
{{"title": "Top 10 Items", "columns": ["Name", "Description", "Rating"], "data": [{{"Name": "Item 1", "Description": "...", "Rating": 4.5}}]}}

Respond ONLY with valid JSON."""

        messages = [
            {"role": "system", "content": "You are a data extraction assistant. Extract structured data from requests."},
            {"role": "user", "content": extraction_prompt}
        ]
        
        response = await llm_provider.complete(
            messages=messages,
            temperature=0.1,
            max_tokens=2000
        )
        
        content = response.get("content", "{}")
        
        # Parse JSON
        try:
            # Find JSON in response
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = {"title": "Generated Document", "data": []}
        except json.JSONDecodeError:
            data = {"title": "Generated Document", "data": []}
        
        title = data.get("title", "Generated Document")
        
        # Generate file based on type
        if file_type == "excel":
            sheet = ExcelSheet(
                name="Data",
                data=data.get("data", []),
                title=title
            )
            result = await excel_generator.generate([sheet])
            
            return {
                "filename": result.filename,
                "filepath": result.filepath,
                "type": "Excel",
                "size": f"{result.size_bytes} bytes"
            }
        
        elif file_type == "pdf":
            sections = [PDFSection(
                title="Overview",
                content=json.dumps(data.get("data", []), indent=2),
                level=1
            )]
            result = await pdf_generator.generate(title, sections)
            
            return {
                "filename": result.filename,
                "filepath": result.filepath,
                "type": "PDF",
                "size": f"{result.size_bytes} bytes"
            }
        
        elif file_type == "word":
            sections = [WordSection(
                title="Overview",
                content=json.dumps(data.get("data", []), indent=2),
                level=1
            )]
            result = await word_generator.generate(title, sections)
            
            return {
                "filename": result.filename,
                "filepath": result.filepath,
                "type": "Word",
                "size": f"{result.size_bytes} bytes"
            }
        
    except Exception as e:
        print(f"File generation error: {e}")
        return None


# ============================================================================
# Search Endpoints
# ============================================================================

@app.post("/api/search")
async def ai_search(request: SearchRequest):
    """
    AI-powered search with real-time results.
    
    Uses Perplexity for AI synthesis or falls back to traditional search.
    """
    global search_system, output_formatter
    
    result = await search_system.smart_search(request.query)
    
    formatted = output_formatter.format_search_response(
        request.query,
        result.get("answer", ""),
        [{"title": s, "url": s} for s in result.get("sources", [])[:5]],
        is_real_time=result.get("is_real_time", False)
    )
    
    return {
        "query": request.query,
        "answer": result.get("answer", ""),
        "sources": result.get("sources", []),
        "results": result.get("results", []),
        "formatted": formatted.to_dict(),
        "credits_used": 10 if request.mode == "quick" else 100
    }


# ============================================================================
# File Generation Endpoints
# ============================================================================

@app.post("/api/files/generate")
async def generate_file(request: FileGenerationRequest):
    """Generate a file from content or data."""
    global excel_generator, pdf_generator, word_generator
    
    title = request.title or "Generated Document"
    
    try:
        if request.file_type == "excel":
            if request.data:
                result = await excel_generator.generate_from_data(
                    request.data,
                    sheet_name="Data",
                    title=title
                )
            else:
                # Parse content into data
                result = await excel_generator.generate_from_data(
                    [{"Content": request.content}],
                    sheet_name="Data",
                    title=title
                )
            
            return {
                "success": True,
                "file": result.to_dict(),
                "download_url": f"/api/files/{result.filename}"
            }
        
        elif request.file_type == "pdf":
            result = await pdf_generator.generate_from_text(title, request.content)
            
            return {
                "success": True,
                "file": result.to_dict(),
                "download_url": f"/api/files/{result.filename}"
            }
        
        elif request.file_type == "word":
            result = await word_generator.generate_from_text(title, request.content)
            
            return {
                "success": True,
                "file": result.to_dict(),
                "download_url": f"/api/files/{result.filename}"
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {request.file_type}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
# Conversation Management Endpoints
# ============================================================================

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history."""
    global memory_store
    
    conversation = memory_store.get_conversation(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation.to_dict()


@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    global memory_store
    
    success = memory_store.delete_conversation(conversation_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"success": True, "message": "Conversation deleted"}


@app.get("/api/users/{user_id}/conversations")
async def get_user_conversations(user_id: str, limit: int = 50):
    """Get all conversations for a user."""
    global memory_store
    
    conversations = memory_store.get_user_conversations(user_id, limit)
    
    return {
        "user_id": user_id,
        "conversations": [c.to_dict() for c in conversations],
        "count": len(conversations)
    }


# ============================================================================
# Legacy Endpoints (for backward compatibility)
# ============================================================================

@app.post("/api/tasks/sync")
async def create_task_sync(request: Dict[str, Any]):
    """Legacy task endpoint - redirects to chat."""
    prompt = request.get("prompt", "")
    
    chat_request = ChatRequest(
        message=prompt,
        mode="deep"
    )
    
    return await chat(chat_request)


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
