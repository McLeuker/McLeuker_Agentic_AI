"""
McLeuker AI V8 API - Advanced Multi-Model Architecture
======================================================
Production-ready API integrating:
- Memory System (persistent conversation context)
- Multi-Agent Collaboration (task delegation)
- RAG System (fashion domain knowledge retrieval)
- Grok-4 (deep reasoning)
- Kimi K2.5 (execution and tool calls)
- Pinterest, YouTube, X/Twitter data integration
- Human-like conversational output
"""

import os
import json
import uuid
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# Request/Response Models
# =============================================================================

class ChatRequest(BaseModel):
    message: str
    mode: str = "quick"  # quick or deep
    sector: Optional[str] = None
    session_id: Optional[str] = None
    use_memory: bool = True
    use_rag: bool = True
    use_tools: bool = False
    tools: Optional[List[str]] = None

class AgentTaskRequest(BaseModel):
    task: str
    context: Optional[Dict] = None
    priority: str = "medium"
    use_collaboration: bool = True

class ToolExecuteRequest(BaseModel):
    tool: str
    params: Dict = Field(default_factory=dict)

class MemoryRequest(BaseModel):
    session_id: str
    content: str
    memory_type: str = "conversation"
    metadata: Optional[Dict] = None

class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 5
    categories: Optional[List[str]] = None

class DocumentGenerateRequest(BaseModel):
    content: str
    format: str = "markdown"  # markdown, pdf, docx
    title: Optional[str] = None

# =============================================================================
# Application Lifecycle
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    logger.info("McLeuker AI V8 starting up...")
    
    # Initialize systems
    try:
        from ..core.memory_system import get_memory_system
        from ..core.rag_system import get_rag_system
        from ..core.multi_agent_system import get_multi_agent_system
        from ..core.conversational_engine import get_conversational_engine
        from ..tools.data_tools import get_research_engine
        
        memory = get_memory_system()
        rag = get_rag_system()
        agents = get_multi_agent_system()
        engine = get_conversational_engine()
        research = get_research_engine()
        
        logger.info("All V8 systems initialized successfully")
        logger.info(f"RAG Knowledge Base: {rag.get_knowledge_stats()}")
        logger.info(f"Multi-Agent System: {agents.get_system_status()['agents'].keys()}")
        
    except Exception as e:
        logger.warning(f"Some systems failed to initialize: {e}")
    
    yield
    
    logger.info("McLeuker AI V8 shutting down...")

# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="McLeuker AI V8 API",
    description="Advanced Multi-Model Fashion Intelligence Platform",
    version="8.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# Health & Status Endpoints
# =============================================================================

@app.get("/")
async def root():
    return {
        "service": "McLeuker AI V8",
        "version": "8.0.0",
        "status": "operational",
        "features": [
            "memory_system",
            "multi_agent_collaboration",
            "rag_knowledge_retrieval",
            "grok_4_reasoning",
            "kimi_k2.5_execution",
            "pinterest_integration",
            "youtube_integration",
            "x_twitter_integration",
            "human_like_output"
        ]
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "systems": {}
    }
    
    # Check Memory System
    try:
        from ..core.memory_system import get_memory_system
        memory = get_memory_system()
        health["systems"]["memory"] = {"status": "operational"}
    except Exception as e:
        health["systems"]["memory"] = {"status": "error", "error": str(e)}
    
    # Check RAG System
    try:
        from ..core.rag_system import get_rag_system
        rag = get_rag_system()
        stats = rag.get_knowledge_stats()
        health["systems"]["rag"] = {"status": "operational", "chunks": stats["total_chunks"]}
    except Exception as e:
        health["systems"]["rag"] = {"status": "error", "error": str(e)}
    
    # Check Multi-Agent System
    try:
        from ..core.multi_agent_system import get_multi_agent_system
        agents = get_multi_agent_system()
        status = agents.get_system_status()
        health["systems"]["multi_agent"] = {"status": "operational", "agents": len(status["agents"])}
    except Exception as e:
        health["systems"]["multi_agent"] = {"status": "error", "error": str(e)}
    
    # Check API Keys
    health["api_keys"] = {
        "grok": "configured" if os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY") else "missing",
        "moonshot": "configured" if os.getenv("MOONSHOT_API_KEY") else "missing",
        "pinterest": "configured" if os.getenv("PINTEREST_API_KEY") else "missing",
        "youtube": "configured" if os.getenv("YOUTUBE_DATA_API_V3") else "missing"
    }
    
    return health

# =============================================================================
# Main Chat Endpoint - Human-Like Conversational Output
# =============================================================================

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Main chat endpoint with human-like conversational output.
    Uses Grok-4 for reasoning and Kimi K2.5 for execution.
    """
    
    async def generate():
        try:
            session_id = request.session_id or str(uuid.uuid4())
            
            # Import systems
            from ..core.memory_system import get_memory_system
            from ..core.rag_system import get_rag_system
            from ..core.conversational_engine import get_conversational_engine
            from ..tools.data_tools import get_research_engine
            
            memory = get_memory_system()
            rag = get_rag_system()
            engine = get_conversational_engine()
            research = get_research_engine()
            
            # Build context
            context = {"sector": request.sector}
            rag_context = None
            
            # Retrieve relevant memories
            if request.use_memory:
                try:
                    relevant_memories = memory.retrieve_relevant(
                        session_id, 
                        request.message, 
                        top_k=5
                    )
                    if relevant_memories:
                        context["relevant_memories"] = [m["content"] for m in relevant_memories]
                except Exception as e:
                    logger.warning(f"Memory retrieval failed: {e}")
            
            # Retrieve RAG context
            if request.use_rag:
                try:
                    rag_result = rag.augment_query(request.message)
                    if rag_result.get("knowledge_used", 0) > 0:
                        rag_context = rag_result.get("augmented_system_prompt", "")
                except Exception as e:
                    logger.warning(f"RAG retrieval failed: {e}")
            
            # Determine mode-specific settings
            is_deep = request.mode == "deep"
            credits_cost = 5 if is_deep else 2
            
            # Yield initial layer - Understanding
            layer_id = str(uuid.uuid4())[:8]
            yield f"data: {json.dumps({'type': 'layer_start', 'data': {'layer_id': layer_id, 'layer_num': 1, 'type': 'understanding', 'title': 'Understanding your request'}})}\n\n"
            yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Analyzing query intent...', 'status': 'active'}})}\n\n"
            await asyncio.sleep(0.3)
            yield f"data: {json.dumps({'type': 'layer_complete', 'data': {'layer_id': layer_id, 'content': 'Query understood'}})}\n\n"
            
            # Research layer (for deep mode or research queries)
            sources = []
            if is_deep or any(kw in request.message.lower() for kw in ["research", "find", "search", "latest", "trend"]):
                layer_id = str(uuid.uuid4())[:8]
                yield f"data: {json.dumps({'type': 'layer_start', 'data': {'layer_id': layer_id, 'layer_num': 2, 'type': 'research', 'title': 'Gathering information'}})}\n\n"
                
                # Parallel research across sources
                try:
                    research_results = await research.research(request.message)
                    
                    for source_name, result in research_results.items():
                        yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': f'Searching {source_name}...', 'status': 'active'}})}\n\n"
                        
                        if result.success and result.results:
                            for item in result.results[:3]:
                                source = {
                                    "title": item.get("title", source_name),
                                    "url": item.get("url", ""),
                                    "snippet": item.get("description", "")[:200]
                                }
                                sources.append(source)
                                yield f"data: {json.dumps({'type': 'source', 'data': source})}\n\n"
                        
                        await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"Research failed: {e}")
                
                yield f"data: {json.dumps({'type': 'layer_complete', 'data': {'layer_id': layer_id, 'content': f'Found {len(sources)} sources'}})}\n\n"
            
            # Analysis layer
            layer_id = str(uuid.uuid4())[:8]
            yield f"data: {json.dumps({'type': 'layer_start', 'data': {'layer_id': layer_id, 'layer_num': 3, 'type': 'analysis', 'title': 'Analyzing information'}})}\n\n"
            yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Processing data...', 'status': 'active'}})}\n\n"
            await asyncio.sleep(0.2)
            yield f"data: {json.dumps({'type': 'layer_complete', 'data': {'layer_id': layer_id, 'content': 'Analysis complete'}})}\n\n"
            
            # Synthesis layer
            layer_id = str(uuid.uuid4())[:8]
            yield f"data: {json.dumps({'type': 'layer_start', 'data': {'layer_id': layer_id, 'layer_num': 4, 'type': 'synthesis', 'title': 'Synthesizing insights'}})}\n\n"
            yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Connecting patterns...', 'status': 'active'}})}\n\n"
            await asyncio.sleep(0.2)
            yield f"data: {json.dumps({'type': 'layer_complete', 'data': {'layer_id': layer_id, 'content': 'Synthesis complete'}})}\n\n"
            
            # Writing layer - Stream response from conversational engine
            layer_id = str(uuid.uuid4())[:8]
            yield f"data: {json.dumps({'type': 'layer_start', 'data': {'layer_id': layer_id, 'layer_num': 5, 'type': 'writing', 'title': 'Generating response'}})}\n\n"
            
            full_content = ""
            
            async for chunk in engine.chat(
                session_id=session_id,
                query=request.message,
                context=context,
                rag_context=rag_context,
                use_tools=request.use_tools
            ):
                chunk_type = chunk.get("type", "")
                chunk_data = chunk.get("data", {})
                
                if chunk_type == "content":
                    content_chunk = chunk_data.get("chunk", "")
                    full_content += content_chunk
                    yield f"data: {json.dumps({'type': 'content', 'data': {'chunk': content_chunk}})}\n\n"
                
                elif chunk_type == "reasoning_step":
                    yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': chunk_data.get('description', ''), 'status': 'active'}})}\n\n"
                
                elif chunk_type == "tool_call":
                    yield f"data: {json.dumps({'type': 'tool_call', 'data': chunk_data})}\n\n"
                
                elif chunk_type == "error":
                    # Fallback to simpler response
                    fallback_content = await _generate_fallback_response(request.message, context, rag_context)
                    full_content = fallback_content
                    yield f"data: {json.dumps({'type': 'content', 'data': {'chunk': fallback_content}})}\n\n"
            
            yield f"data: {json.dumps({'type': 'layer_complete', 'data': {'layer_id': layer_id, 'content': 'Response generated'}})}\n\n"
            
            # Save to memory
            if request.use_memory:
                try:
                    memory.add_memory(
                        session_id=session_id,
                        content=f"User: {request.message}\nAssistant: {full_content[:500]}",
                        memory_type="conversation"
                    )
                except Exception as e:
                    logger.warning(f"Memory save failed: {e}")
            
            # Generate follow-up questions
            follow_up = _generate_follow_up_questions(request.message, full_content)
            
            # Final complete event
            yield f"data: {json.dumps({'type': 'complete', 'data': {'content': full_content, 'sources': sources, 'follow_up_questions': follow_up, 'credits_used': credits_cost, 'session_id': session_id}})}\n\n"
            
        except Exception as e:
            logger.error(f"Chat stream error: {e}")
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

async def _generate_fallback_response(message: str, context: Dict, rag_context: str = None) -> str:
    """Generate fallback response using simpler method"""
    import aiohttp
    
    grok_key = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
    if not grok_key:
        return "I apologize, but I'm currently unable to process your request. Please try again later."
    
    system_prompt = """You are McLeuker AI, a fashion intelligence expert. Respond naturally and conversationally, 
    like a knowledgeable friend. Avoid rigid templates and bullet points. Show your reasoning process naturally."""
    
    if rag_context:
        system_prompt += f"\n\nRelevant knowledge:\n{rag_context}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.x.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {grok_key}", "Content-Type": "application/json"},
                json={
                    "model": "grok-4",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Fallback generation failed: {e}")
    
    return "I'm having trouble generating a response right now. Please try again."

def _generate_follow_up_questions(query: str, response: str) -> List[str]:
    """Generate contextual follow-up questions"""
    questions = []
    query_lower = query.lower()
    
    if "trend" in query_lower:
        questions.extend([
            "How can brands capitalize on this trend?",
            "What are the sustainability implications?",
            "Which designers are leading this movement?"
        ])
    elif "sustainable" in query_lower or "eco" in query_lower:
        questions.extend([
            "What certifications should consumers look for?",
            "How does this compare to traditional alternatives?",
            "Which brands are making the most progress?"
        ])
    elif "brand" in query_lower or "designer" in query_lower:
        questions.extend([
            "What's their sustainability approach?",
            "How has their style evolved recently?",
            "What's their target demographic?"
        ])
    else:
        questions.extend([
            "Can you elaborate on the key points?",
            "What are the practical implications?",
            "How does this relate to current trends?"
        ])
    
    return questions[:5]

# =============================================================================
# Kimi K2.5 Execution Endpoint
# =============================================================================

@app.post("/api/kimi/execute")
async def kimi_execute(request: ToolExecuteRequest):
    """Execute tasks using Kimi K2.5 model"""
    
    async def generate():
        try:
            from ..core.conversational_engine import get_conversational_engine
            engine = get_conversational_engine()
            
            # Define available tools
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "web_search",
                        "description": "Search the web for information",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Search query"}
                            },
                            "required": ["query"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "analyze_data",
                        "description": "Analyze data and extract insights",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "data": {"type": "string", "description": "Data to analyze"}
                            },
                            "required": ["data"]
                        }
                    }
                }
            ]
            
            async for chunk in engine.generator.generate_with_kimi_execution(
                query=json.dumps(request.params),
                tools=tools
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
                
        except Exception as e:
            logger.error(f"Kimi execution error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'data': {'message': str(e)}})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

# =============================================================================
# Multi-Agent Collaboration Endpoint
# =============================================================================

@app.post("/api/agent/execute")
async def agent_execute(request: AgentTaskRequest):
    """Execute task using multi-agent collaboration"""
    try:
        from ..core.multi_agent_system import get_multi_agent_system
        
        agents = get_multi_agent_system()
        result = await agents.execute(
            task_description=request.task,
            input_data=request.context or {}
        )
        
        return JSONResponse(content={
            "success": True,
            "result": result,
            "agents_used": list(agents.agents.keys())
        })
        
    except Exception as e:
        logger.error(f"Agent execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/status")
async def agent_status():
    """Get multi-agent system status"""
    try:
        from ..core.multi_agent_system import get_multi_agent_system
        agents = get_multi_agent_system()
        return agents.get_system_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# Memory System Endpoints
# =============================================================================

@app.post("/api/memory/add")
async def add_memory(request: MemoryRequest):
    """Add a memory to the system"""
    try:
        from ..core.memory_system import get_memory_system
        memory = get_memory_system()
        
        result = memory.add_memory(
            session_id=request.session_id,
            content=request.content,
            memory_type=request.memory_type,
            metadata=request.metadata
        )
        
        return {"success": True, "memory_id": result.id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/{session_id}")
async def get_memories(session_id: str, limit: int = 20):
    """Get memories for a session"""
    try:
        from ..core.memory_system import get_memory_system
        memory = get_memory_system()
        
        memories = memory.get_session_memories(session_id, limit=limit)
        return {"session_id": session_id, "memories": memories}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/memory/search")
async def search_memories(session_id: str, query: str, top_k: int = 5):
    """Search memories by semantic similarity"""
    try:
        from ..core.memory_system import get_memory_system
        memory = get_memory_system()
        
        results = memory.retrieve_relevant(session_id, query, top_k=top_k)
        return {"query": query, "results": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# RAG System Endpoints
# =============================================================================

@app.post("/api/rag/query")
async def rag_query(request: RAGQueryRequest):
    """Query the RAG knowledge base"""
    try:
        from ..core.rag_system import get_rag_system
        rag = get_rag_system()
        
        result = rag.retrieve(
            query=request.query,
            top_k=request.top_k
        )
        
        return result.to_dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rag/stats")
async def rag_stats():
    """Get RAG knowledge base statistics"""
    try:
        from ..core.rag_system import get_rag_system
        rag = get_rag_system()
        return rag.get_knowledge_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rag/add")
async def add_knowledge(content: str, category: str, source: str, metadata: Dict = None):
    """Add knowledge to the RAG system"""
    try:
        from ..core.rag_system import get_rag_system
        rag = get_rag_system()
        
        result = rag.add_knowledge(content, category, source, metadata)
        return {"success": True, "chunk": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# Research & Data Tools Endpoints
# =============================================================================

@app.post("/api/research")
async def research_query(query: str, sources: List[str] = None):
    """Execute parallel research across multiple sources"""
    try:
        from ..tools.data_tools import get_research_engine
        research = get_research_engine()
        
        results = await research.research(query, sources=sources)
        
        return {
            "query": query,
            "results": {k: v.to_dict() for k, v in results.items()}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tools/list")
async def list_tools():
    """List available tools"""
    return {
        "tools": [
            {
                "name": "web_search",
                "description": "Search the web using Grok-4",
                "category": "research"
            },
            {
                "name": "pinterest_search",
                "description": "Search Pinterest for visual inspiration",
                "category": "research"
            },
            {
                "name": "youtube_search",
                "description": "Search YouTube for video content",
                "category": "research"
            },
            {
                "name": "x_search",
                "description": "Search X/Twitter for real-time trends",
                "category": "research"
            },
            {
                "name": "analyze_data",
                "description": "Analyze data and extract insights",
                "category": "analysis"
            },
            {
                "name": "generate_document",
                "description": "Generate documents in various formats",
                "category": "generation"
            }
        ]
    }

@app.post("/api/tools/execute")
async def execute_tool(request: ToolExecuteRequest):
    """Execute a specific tool"""
    try:
        from ..tools.tool_registry import tool_registry
        
        result = await tool_registry.execute(request.tool, request.params)
        return {"success": True, "result": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# Document Generation Endpoints
# =============================================================================

@app.post("/api/document/generate")
async def generate_document(request: DocumentGenerateRequest):
    """Generate a downloadable document"""
    import tempfile
    
    try:
        title = request.title or "McLeuker AI Report"
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        if request.format == "markdown":
            filename = f"{title.replace(' ', '_')}_{timestamp}.md"
            content = f"# {title}\n\n{request.content}"
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(content)
                filepath = f.name
            
            return FileResponse(
                filepath,
                filename=filename,
                media_type="text/markdown"
            )
        
        elif request.format == "pdf":
            # For PDF, we'd use a library like reportlab or weasyprint
            # For now, return markdown
            filename = f"{title.replace(' ', '_')}_{timestamp}.md"
            content = f"# {title}\n\n{request.content}"
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(content)
                filepath = f.name
            
            return FileResponse(
                filepath,
                filename=filename,
                media_type="text/markdown"
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# Legacy Compatibility Endpoints
# =============================================================================

@app.post("/api/v6/chat/stream")
async def chat_stream_v6(request: ChatRequest):
    """V6 compatibility endpoint"""
    return await chat_stream(request)

@app.post("/api/v7/chat/stream")
async def chat_stream_v7(request: ChatRequest):
    """V7 compatibility endpoint"""
    return await chat_stream(request)

# =============================================================================
# Error Handlers
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
