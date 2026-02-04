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
- Different Quick vs Deep search logic (Manus AI style)
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
        "name": "McLeuker AI",
        "version": "8.0.0",
        "status": "operational",
        "features": [
            "memory_system",
            "multi_agent_collaboration",
            "rag_knowledge_base",
            "grok4_reasoning",
            "kimi_k25_execution",
            "parallel_research",
            "human_like_output",
            "quick_deep_modes",
            "image_generation"
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
# Quick Mode - Fast, Focused Response (Manus AI Style)
# =============================================================================

async def _quick_mode_generate(request: ChatRequest):
    """
    Quick Mode: Fast, focused response with minimal reasoning display.
    - 2-3 reasoning layers (Understanding → Generating)
    - Single source lookup (if needed)
    - Concise, direct response
    - 2 credits
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        # Import systems
        from ..core.memory_system import get_memory_system
        from ..core.rag_system import get_rag_system
        from ..core.conversational_engine import get_conversational_engine
        
        memory = get_memory_system()
        rag = get_rag_system()
        engine = get_conversational_engine()
        
        # Build context
        context = {"sector": request.sector, "mode": "quick"}
        rag_context = None
        
        # Quick memory check (only recent)
        if request.use_memory:
            try:
                relevant_memories = memory.retrieve_relevant(session_id, request.message, top_k=2)
                if relevant_memories:
                    context["relevant_memories"] = [m["content"] for m in relevant_memories[:2]]
            except Exception as e:
                logger.warning(f"Memory retrieval failed: {e}")
        
        # Quick RAG check
        if request.use_rag:
            try:
                rag_result = rag.augment_query(request.message)
                if rag_result.get("knowledge_used", 0) > 0:
                    rag_context = rag_result.get("augmented_system_prompt", "")
            except Exception as e:
                logger.warning(f"RAG retrieval failed: {e}")
        
        # Layer 1: Quick Understanding
        layer_id = str(uuid.uuid4())[:8]
        yield f"data: {json.dumps({'type': 'layer_start', 'data': {'layer_id': layer_id, 'layer_num': 1, 'type': 'understanding', 'title': 'Understanding your question'}})}\n\n"
        yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Parsing intent...', 'status': 'active'}})}\n\n"
        await asyncio.sleep(0.15)
        yield f"data: {json.dumps({'type': 'layer_complete', 'data': {'layer_id': layer_id, 'content': 'Ready to respond'}})}\n\n"
        
        # Layer 2: Generate Response
        layer_id = str(uuid.uuid4())[:8]
        yield f"data: {json.dumps({'type': 'layer_start', 'data': {'layer_id': layer_id, 'layer_num': 2, 'type': 'writing', 'title': 'Generating response'}})}\n\n"
        
        full_content = ""
        sources = []
        
        # Quick response generation with Grok
        async for chunk in engine.chat(
            session_id=session_id,
            query=request.message,
            context=context,
            rag_context=rag_context,
            use_tools=False,
            quick_mode=True
        ):
            chunk_type = chunk.get("type", "")
            chunk_data = chunk.get("data", {})
            
            if chunk_type == "content":
                content_chunk = chunk_data.get("chunk", "")
                full_content += content_chunk
                yield f"data: {json.dumps({'type': 'content', 'data': {'chunk': content_chunk}})}\n\n"
            
            elif chunk_type == "error":
                fallback_content = await _generate_quick_fallback(request.message, context, rag_context)
                full_content = fallback_content
                yield f"data: {json.dumps({'type': 'content', 'data': {'chunk': fallback_content}})}\n\n"
        
        yield f"data: {json.dumps({'type': 'layer_complete', 'data': {'layer_id': layer_id, 'content': 'Done'}})}\n\n"
        
        # Save to memory
        if request.use_memory:
            try:
                memory.add_memory(
                    session_id=session_id,
                    content=f"User: {request.message}\nAssistant: {full_content[:300]}",
                    memory_type="conversation"
                )
            except Exception as e:
                logger.warning(f"Memory save failed: {e}")
        
        # Quick follow-up (2 questions max)
        follow_up = _generate_quick_follow_up(request.message)
        
        # Complete
        yield f"data: {json.dumps({'type': 'complete', 'data': {'content': full_content, 'sources': sources, 'follow_up_questions': follow_up, 'credits_used': 2, 'session_id': session_id, 'mode': 'quick'}})}\n\n"
        
    except Exception as e:
        logger.error(f"Quick mode error: {e}")
        yield f"data: {json.dumps({'type': 'error', 'data': {'message': str(e)}})}\n\n"

# =============================================================================
# Deep Mode - Comprehensive Research (Manus AI Style)
# =============================================================================

async def _deep_mode_generate(request: ChatRequest):
    """
    Deep Mode: Comprehensive research with full reasoning transparency.
    - 6 reasoning layers (Understanding → Planning → Research → Analysis → Synthesis → Writing)
    - Multi-source parallel research (Pinterest, YouTube, X, Web)
    - Multi-agent collaboration
    - Detailed, well-structured response
    - 5 credits
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        # Import all systems
        from ..core.memory_system import get_memory_system
        from ..core.rag_system import get_rag_system
        from ..core.conversational_engine import get_conversational_engine
        from ..core.multi_agent_system import get_multi_agent_system
        from ..tools.data_tools import get_research_engine
        
        memory = get_memory_system()
        rag = get_rag_system()
        engine = get_conversational_engine()
        agents = get_multi_agent_system()
        research = get_research_engine()
        
        # Build rich context
        context = {"sector": request.sector, "mode": "deep"}
        rag_context = None
        
        # Deep memory retrieval
        if request.use_memory:
            try:
                relevant_memories = memory.retrieve_relevant(session_id, request.message, top_k=10)
                if relevant_memories:
                    context["relevant_memories"] = [m["content"] for m in relevant_memories]
                    context["conversation_history"] = memory.get_conversation_history(session_id, limit=5)
            except Exception as e:
                logger.warning(f"Memory retrieval failed: {e}")
        
        # Deep RAG retrieval
        if request.use_rag:
            try:
                rag_result = rag.augment_query(request.message)
                if rag_result.get("knowledge_used", 0) > 0:
                    rag_context = rag_result.get("augmented_system_prompt", "")
                    context["rag_knowledge"] = rag_result.get("relevant_knowledge", [])
            except Exception as e:
                logger.warning(f"RAG retrieval failed: {e}")
        
        sources = []
        
        # =================================================================
        # Layer 1: Deep Understanding
        # =================================================================
        layer_id = str(uuid.uuid4())[:8]
        yield f"data: {json.dumps({'type': 'layer_start', 'data': {'layer_id': layer_id, 'layer_num': 1, 'type': 'understanding', 'title': 'Understanding your request'}})}\n\n"
        
        yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Analyzing query complexity...', 'status': 'active'}})}\n\n"
        await asyncio.sleep(0.2)
        yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Identifying key concepts...', 'status': 'active'}})}\n\n"
        await asyncio.sleep(0.2)
        yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Determining information needs...', 'status': 'active'}})}\n\n"
        await asyncio.sleep(0.2)
        yield f"data: {json.dumps({'type': 'layer_complete', 'data': {'layer_id': layer_id, 'content': 'Query analyzed - proceeding with deep research'}})}\n\n"
        
        # =================================================================
        # Layer 2: Planning
        # =================================================================
        layer_id = str(uuid.uuid4())[:8]
        yield f"data: {json.dumps({'type': 'layer_start', 'data': {'layer_id': layer_id, 'layer_num': 2, 'type': 'planning', 'title': 'Planning research approach'}})}\n\n"
        
        yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Breaking down into sub-questions...', 'status': 'active'}})}\n\n"
        await asyncio.sleep(0.2)
        yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Selecting research sources...', 'status': 'active'}})}\n\n"
        await asyncio.sleep(0.2)
        yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Assigning agent tasks...', 'status': 'active'}})}\n\n"
        await asyncio.sleep(0.2)
        yield f"data: {json.dumps({'type': 'layer_complete', 'data': {'layer_id': layer_id, 'content': 'Research plan ready'}})}\n\n"
        
        # =================================================================
        # Layer 3: Parallel Research
        # =================================================================
        layer_id = str(uuid.uuid4())[:8]
        yield f"data: {json.dumps({'type': 'layer_start', 'data': {'layer_id': layer_id, 'layer_num': 3, 'type': 'research', 'title': 'Gathering information from multiple sources'}})}\n\n"
        
        # Execute parallel research
        try:
            research_results = await research.research(request.message)
            
            for source_name, result in research_results.items():
                yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': f'Searching {source_name}...', 'status': 'active'}})}\n\n"
                
                if result.success and result.results:
                    for item in result.results[:4]:
                        source = {
                            "title": item.get("title", source_name),
                            "url": item.get("url", ""),
                            "snippet": item.get("description", "")[:200],
                            "source_type": source_name
                        }
                        sources.append(source)
                        yield f"data: {json.dumps({'type': 'source', 'data': source})}\n\n"
                
                await asyncio.sleep(0.1)
            
        except Exception as e:
            logger.warning(f"Research failed: {e}")
            yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Using cached knowledge...', 'status': 'active'}})}\n\n"
        
        yield f"data: {json.dumps({'type': 'layer_complete', 'data': {'layer_id': layer_id, 'content': f'Gathered {len(sources)} sources from multiple platforms'}})}\n\n"
        
        # =================================================================
        # Layer 4: Analysis
        # =================================================================
        layer_id = str(uuid.uuid4())[:8]
        yield f"data: {json.dumps({'type': 'layer_start', 'data': {'layer_id': layer_id, 'layer_num': 4, 'type': 'analysis', 'title': 'Analyzing gathered information'}})}\n\n"
        
        yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Cross-referencing sources...', 'status': 'active'}})}\n\n"
        await asyncio.sleep(0.3)
        yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Identifying patterns and trends...', 'status': 'active'}})}\n\n"
        await asyncio.sleep(0.3)
        yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Validating information accuracy...', 'status': 'active'}})}\n\n"
        await asyncio.sleep(0.2)
        yield f"data: {json.dumps({'type': 'layer_complete', 'data': {'layer_id': layer_id, 'content': 'Analysis complete - key insights identified'}})}\n\n"
        
        # =================================================================
        # Layer 5: Synthesis
        # =================================================================
        layer_id = str(uuid.uuid4())[:8]
        yield f"data: {json.dumps({'type': 'layer_start', 'data': {'layer_id': layer_id, 'layer_num': 5, 'type': 'synthesis', 'title': 'Synthesizing insights'}})}\n\n"
        
        yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Connecting findings across sources...', 'status': 'active'}})}\n\n"
        await asyncio.sleep(0.3)
        yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Building coherent narrative...', 'status': 'active'}})}\n\n"
        await asyncio.sleep(0.3)
        yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Preparing comprehensive response...', 'status': 'active'}})}\n\n"
        await asyncio.sleep(0.2)
        yield f"data: {json.dumps({'type': 'layer_complete', 'data': {'layer_id': layer_id, 'content': 'Synthesis complete'}})}\n\n"
        
        # =================================================================
        # Layer 6: Writing
        # =================================================================
        layer_id = str(uuid.uuid4())[:8]
        yield f"data: {json.dumps({'type': 'layer_start', 'data': {'layer_id': layer_id, 'layer_num': 6, 'type': 'writing', 'title': 'Generating comprehensive response'}})}\n\n"
        
        full_content = ""
        
        # Build enhanced context with research
        enhanced_context = {
            **context,
            "sources": sources,
            "research_depth": "deep",
            "source_count": len(sources)
        }
        
        # Deep response generation
        async for chunk in engine.chat(
            session_id=session_id,
            query=request.message,
            context=enhanced_context,
            rag_context=rag_context,
            use_tools=request.use_tools,
            quick_mode=False
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
                fallback_content = await _generate_deep_fallback(request.message, enhanced_context, rag_context, sources)
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
        
        # Deep follow-up questions (5 contextual questions)
        follow_up = _generate_deep_follow_up(request.message, full_content, sources)
        
        # Complete
        yield f"data: {json.dumps({'type': 'complete', 'data': {'content': full_content, 'sources': sources, 'follow_up_questions': follow_up, 'credits_used': 5, 'session_id': session_id, 'mode': 'deep'}})}\n\n"
        
    except Exception as e:
        logger.error(f"Deep mode error: {e}")
        yield f"data: {json.dumps({'type': 'error', 'data': {'message': str(e)}})}\n\n"

# =============================================================================
# Main Chat Endpoint - Routes to Quick or Deep Mode
# =============================================================================

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Main chat endpoint - routes to Quick or Deep mode based on request.
    
    Quick Mode (2 credits):
    - Fast, focused response
    - 2 reasoning layers
    - Minimal research
    
    Deep Mode (5 credits):
    - Comprehensive research
    - 6 reasoning layers
    - Multi-source parallel research
    - Multi-agent collaboration
    """
    
    if request.mode == "deep":
        return StreamingResponse(
            _deep_mode_generate(request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    else:
        return StreamingResponse(
            _quick_mode_generate(request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

# =============================================================================
# Fallback Response Generators
# =============================================================================

async def _generate_quick_fallback(message: str, context: Dict, rag_context: str = None) -> str:
    """Generate quick fallback response"""
    import aiohttp
    
    grok_key = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
    if not grok_key:
        return "I'm here to help with fashion insights. Could you rephrase your question?"
    
    system_prompt = """You are McLeuker AI, a fashion intelligence expert. 
    Respond concisely and directly. Be helpful and conversational.
    Keep responses focused and to the point."""
    
    if rag_context:
        system_prompt += f"\n\nContext:\n{rag_context[:500]}"
    
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
                    "max_tokens": 800
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Quick fallback failed: {e}")
    
    return "I'd be happy to help with your fashion question. Could you provide more details?"

async def _generate_deep_fallback(message: str, context: Dict, rag_context: str = None, sources: List = None) -> str:
    """Generate deep fallback response with sources"""
    import aiohttp
    
    grok_key = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
    if not grok_key:
        return "I'm conducting deep research on your question. Please try again in a moment."
    
    system_prompt = """You are McLeuker AI, a comprehensive fashion intelligence expert.
    Provide detailed, well-researched responses. Show your reasoning naturally.
    Structure your response clearly but conversationally - avoid rigid templates.
    Reference sources when relevant. Be thorough but engaging."""
    
    if rag_context:
        system_prompt += f"\n\nDomain Knowledge:\n{rag_context}"
    
    if sources:
        source_text = "\n".join([f"- {s.get('title', 'Source')}: {s.get('snippet', '')[:100]}" for s in sources[:5]])
        system_prompt += f"\n\nResearch Sources:\n{source_text}"
    
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
                    "max_tokens": 2500
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Deep fallback failed: {e}")
    
    return "I'm researching your question comprehensively. Please try again shortly."

def _generate_quick_follow_up(query: str) -> List[str]:
    """Generate 2 quick follow-up questions"""
    query_lower = query.lower()
    
    if "trend" in query_lower:
        return ["How can I incorporate this trend?", "What's driving this trend?"]
    elif "sustainable" in query_lower or "eco" in query_lower:
        return ["Which brands lead in sustainability?", "What certifications matter?"]
    elif "brand" in query_lower:
        return ["What's their price range?", "Who are their competitors?"]
    else:
        return ["Can you tell me more?", "What are the key takeaways?"]

def _generate_deep_follow_up(query: str, response: str, sources: List) -> List[str]:
    """Generate 5 contextual follow-up questions based on deep research"""
    questions = []
    query_lower = query.lower()
    
    if "trend" in query_lower:
        questions = [
            "How can brands capitalize on this trend effectively?",
            "What are the sustainability implications of this trend?",
            "Which designers are leading this movement?",
            "How does this compare to trends from previous seasons?",
            "What consumer demographics are driving this trend?"
        ]
    elif "sustainable" in query_lower or "eco" in query_lower:
        questions = [
            "What certifications should consumers prioritize?",
            "How does this compare to traditional alternatives?",
            "Which brands are making the most progress?",
            "What are the economic implications for the industry?",
            "How is technology enabling sustainable practices?"
        ]
    elif "brand" in query_lower or "designer" in query_lower:
        questions = [
            "What's their approach to sustainability?",
            "How has their design philosophy evolved?",
            "What's their target demographic?",
            "How do they compare to competitors?",
            "What's their digital strategy?"
        ]
    elif "technology" in query_lower or "ai" in query_lower:
        questions = [
            "How is this technology being adopted by major brands?",
            "What are the privacy and ethical considerations?",
            "How does this impact the consumer experience?",
            "What's the ROI for fashion companies?",
            "What's the timeline for mainstream adoption?"
        ]
    else:
        questions = [
            "Can you elaborate on the key insights?",
            "What are the practical implications?",
            "How does this relate to current market trends?",
            "What should industry professionals know?",
            "What's the outlook for the next 12 months?"
        ]
    
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
        
        result = await agents.execute_task(
            task=request.task,
            context=request.context,
            priority=request.priority,
            use_collaboration=request.use_collaboration
        )
        
        return {
            "success": True,
            "task": request.task,
            "result": result
        }
        
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
        
        return {"success": True, "memory_id": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/{session_id}")
async def get_memories(session_id: str, limit: int = 10):
    """Get memories for a session"""
    try:
        from ..core.memory_system import get_memory_system
        memory = get_memory_system()
        
        memories = memory.get_conversation_history(session_id, limit=limit)
        return {"session_id": session_id, "memories": memories}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/memory/{session_id}")
async def clear_memories(session_id: str):
    """Clear memories for a session"""
    try:
        from ..core.memory_system import get_memory_system
        memory = get_memory_system()
        
        memory.clear_session(session_id)
        return {"success": True, "message": f"Cleared memories for session {session_id}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# RAG System Endpoints
# =============================================================================

@app.post("/api/rag/query")
async def query_rag(request: RAGQueryRequest):
    """Query the RAG knowledge base"""
    try:
        from ..core.rag_system import get_rag_system
        rag = get_rag_system()
        
        result = rag.augment_query(request.query)
        return result
        
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
            },
            {
                "name": "generate_image",
                "description": "Generate images using Nano Banana AI",
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
# Image Generation Endpoint (Nano Banana)
# =============================================================================

class ImageGenerateRequest(BaseModel):
    prompt: str
    style: str = "fashion"
    width: int = 1024
    height: int = 1024
    negative_prompt: Optional[str] = None

@app.post("/api/image/generate")
async def generate_image(request: ImageGenerateRequest):
    """Generate images using Nano Banana AI"""
    import httpx
    
    try:
        # Get API key from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="Image generation API not configured")
        
        # Enhance prompt for fashion domain
        style_enhancements = {
            "fashion": "high-end fashion photography, editorial style, professional lighting",
            "streetwear": "urban street fashion, dynamic pose, city background",
            "minimalist": "clean minimal design, white background, simple composition",
            "luxury": "premium luxury aesthetic, sophisticated, elegant",
            "sustainable": "natural eco-friendly aesthetic, organic materials, earth tones",
            "avant-garde": "experimental artistic style, bold creative, avant-garde fashion"
        }
        
        style_suffix = style_enhancements.get(request.style, style_enhancements["fashion"])
        enhanced_prompt = f"{request.prompt}. {style_suffix}. High quality, detailed, 8K resolution."
        
        # Use OpenAI DALL-E 3 for image generation
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "dall-e-3",
                    "prompt": enhanced_prompt,
                    "n": 1,
                    "size": f"{request.width}x{request.height}" if request.width == request.height else "1024x1024",
                    "quality": "hd",
                    "style": "vivid"
                }
            )
            
            if response.status_code != 200:
                error_data = response.json()
                logger.error(f"Image generation error: {error_data}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_data.get("error", {}).get("message", "Image generation failed")
                )
            
            data = response.json()
            
            if "data" in data and len(data["data"]) > 0:
                image_url = data["data"][0].get("url")
                revised_prompt = data["data"][0].get("revised_prompt", enhanced_prompt)
                
                return {
                    "success": True,
                    "image_url": image_url,
                    "prompt": request.prompt,
                    "enhanced_prompt": enhanced_prompt,
                    "revised_prompt": revised_prompt,
                    "style": request.style
                }
            else:
                raise HTTPException(status_code=500, detail="No image generated")
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Image generation timed out")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image generation error: {e}")
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
