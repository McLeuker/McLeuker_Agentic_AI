"""
McLeuker Agentic AI Platform - FastAPI Backend v2.1

Complete agentic AI platform with:
- 5-layer reasoning system
- Conversation memory
- Real-time web search (fixed)
- Professional file generation
- Structured output formatting

Similar to Manus AI and ChatGPT capabilities.
"""

import os
import json
import asyncio
import traceback
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
    
    print("🚀 McLeuker AI Platform v2.1 starting...")
    
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
    version="2.1.0",
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
        version="2.1.0",
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
        "version": "2.1.0",
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
    
    print(f"Chat request: {request.message[:100]}...")
    
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
        # Check if file generation is needed FIRST (higher priority)
        if reasoning_chain.requires_file_generation:
            print(f"File generation requested: {reasoning_chain.output_format}")
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
                response_data["follow_up_questions"] = ["What other data would you like to export?", "Would you like me to modify this file?", "Need a different format?"]
                credits_used = 50
            else:
                response_data["message"] = "I encountered an issue generating the file. Please try again with more specific data."
        
        # Check if real-time search is needed
        elif reasoning_chain.requires_search or mode == "deep":
            print(f"Search triggered for: {request.message[:50]}...")
            
            # Perform real-time search
            search_result = await search_system.smart_search(request.message)
            
            answer = search_result.get("answer", "")
            sources = search_result.get("sources", [])
            provider = search_result.get("provider", "unknown")
            
            print(f"Search result from {provider}: {len(answer)} chars, {len(sources)} sources")
            
            if answer and len(answer) > 50:
                # We got a good answer - format it properly
                formatted = output_formatter.format_search_response(
                    request.message,
                    answer,
                    [{"title": f"Source {i+1}", "url": s} for i, s in enumerate(sources[:5]) if isinstance(s, str)],
                    is_real_time=search_result.get("is_real_time", True)
                )
                
                response_data["message"] = formatted.to_markdown()
                response_data["sources"] = formatted.sources
                response_data["follow_up_questions"] = formatted.follow_up_questions
            else:
                # Search didn't return good results, fall back to LLM
                print("Search returned insufficient results, falling back to LLM")
                response_text = await _generate_contextual_response(
                    request.message,
                    conversation,
                    mode
                )
                
                formatted = output_formatter.format_response(
                    response_text,
                    style=OutputStyle.DETAILED,
                    reasoning=reasoning_chain.to_display() if mode == "deep" else None
                )
                
                response_data["message"] = formatted.to_markdown()
                response_data["follow_up_questions"] = formatted.follow_up_questions
            
            # Show reasoning if deep mode
            if mode == "deep":
                response_data["reasoning"] = reasoning_chain.to_display()
                credits_used = 100
        
        else:
            # Regular conversation with context
            print("Regular conversation mode")
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
        traceback.print_exc()
        response_data["message"] = f"I apologize, but I encountered an error processing your request. Please try again."
        response_data["follow_up_questions"] = ["Can you rephrase your question?", "Would you like to try a different topic?"]
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
3. Use emojis appropriately to make responses engaging (📌, 💡, ✅, etc.)
4. Structure responses with clear sections using markdown headers (##, ###)
5. Use bullet points (•) for lists
6. If you don't know something current, say so and offer to search
7. Provide specific, actionable information
8. Format your response professionally

Current date: {datetime.utcnow().strftime('%B %d, %Y')}"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history_messages)
    messages.append({"role": "user", "content": message})
    
    # Generate response
    response = await llm_provider.complete(
        messages=messages,
        temperature=0.7 if mode == "quick" else 0.5,
        max_tokens=1500 if mode == "quick" else 2500
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
- "data": Array of objects for the content (at least 5-10 items with realistic data)
- "columns": Array of column names (for Excel)

Example for Excel about fashion:
{{"title": "Fashion Week Highlights 2026", "columns": ["Designer", "Collection", "Key Trend", "Rating"], "data": [{{"Designer": "Chanel", "Collection": "Spring 2026", "Key Trend": "Sustainable Luxury", "Rating": 4.8}}, {{"Designer": "Dior", "Collection": "Spring 2026", "Key Trend": "Neo-Romanticism", "Rating": 4.7}}]}}

Generate realistic, detailed data based on the user's request. Respond ONLY with valid JSON."""

        messages = [
            {"role": "system", "content": "You are a data extraction assistant. Extract and generate structured data from requests. Always provide realistic, detailed data."},
            {"role": "user", "content": extraction_prompt}
        ]
        
        response = await llm_provider.complete(
            messages=messages,
            temperature=0.3,
            max_tokens=2500
        )
        
        content = response.get("content", "{}")
        
        # Parse JSON
        try:
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
                title=title,
                content=json.dumps(data.get("data", []), indent=2)
            )]
            result = await pdf_generator.generate(sections, title)
            
            return {
                "filename": result.filename,
                "filepath": result.filepath,
                "type": "PDF",
                "size": f"{result.size_bytes} bytes"
            }
        
        elif file_type == "word":
            sections = [WordSection(
                title=title,
                content=json.dumps(data.get("data", []), indent=2)
            )]
            result = await word_generator.generate(sections, title)
            
            return {
                "filename": result.filename,
                "filepath": result.filepath,
                "type": "Word",
                "size": f"{result.size_bytes} bytes"
            }
        
        return None
    
    except Exception as e:
        print(f"File generation error: {e}")
        traceback.print_exc()
        return None


# ============================================================================
# Search Endpoints
# ============================================================================

@app.post("/api/search")
async def search(request: SearchRequest):
    """Direct search endpoint."""
    global search_system
    
    result = await search_system.smart_search(request.query)
    
    return {
        "query": request.query,
        "answer": result.get("answer", ""),
        "sources": result.get("sources", []),
        "provider": result.get("provider", "unknown"),
        "is_real_time": result.get("is_real_time", False)
    }


# ============================================================================
# File Generation Endpoints
# ============================================================================

@app.post("/api/files/generate")
async def generate_file(request: FileGenerationRequest):
    """Generate a file from content."""
    global excel_generator, pdf_generator, word_generator
    
    try:
        if request.file_type == "excel":
            if request.data:
                sheet = ExcelSheet(
                    name="Data",
                    data=request.data,
                    title=request.title or "Generated Data"
                )
                result = await excel_generator.generate([sheet])
            else:
                return {"error": "No data provided for Excel generation"}
        
        elif request.file_type == "pdf":
            sections = [PDFSection(
                title=request.title or "Document",
                content=request.content
            )]
            result = await pdf_generator.generate(sections, request.title or "Document")
        
        elif request.file_type == "word":
            sections = [WordSection(
                title=request.title or "Document",
                content=request.content
            )]
            result = await word_generator.generate(sections, request.title or "Document")
        
        else:
            return {"error": f"Unsupported file type: {request.file_type}"}
        
        return {
            "success": True,
            "filename": result.filename,
            "filepath": result.filepath,
            "size": result.size_bytes,
            "download_url": f"/api/files/{result.filename}"
        }
    
    except Exception as e:
        return {"error": str(e)}


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
    """Get a conversation by ID."""
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


@app.get("/api/conversations")
async def list_conversations(user_id: Optional[str] = None, limit: int = 20):
    """List conversations."""
    global memory_store
    
    conversations = memory_store.list_conversations(user_id, limit)
    return {
        "conversations": [c.to_dict() for c in conversations],
        "total": len(conversations)
    }


# ============================================================================
# WebSocket for Streaming (Optional)
# ============================================================================

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for streaming chat."""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Process the message
            request = ChatRequest(**data)
            response = await chat(request)
            
            # Send response
            await websocket.send_json(response.dict())
    
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()
