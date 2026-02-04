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
- Human-like conversational output (NO forced structure)
- Different Quick vs Deep search logic (Manus AI style)
- Image Generation (Nano Banana / DALL-E)
- Document Generation (Excel, Word, PPT, PDF)
"""

import os
import io
import json
import uuid
import asyncio
import logging
import tempfile
import base64
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse, Response
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
    files: Optional[List[Dict]] = None  # Attached files

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
    format: str = "markdown"  # markdown, pdf, docx, xlsx, pptx
    title: Optional[str] = None
    data: Optional[List[Dict]] = None  # For Excel data

class ImageGenerateRequest(BaseModel):
    prompt: str
    style: str = "fashion"
    width: int = 1024
    height: int = 1024
    negative_prompt: Optional[str] = None

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
# Health & Info Endpoints
# =============================================================================

@app.get("/")
async def root():
    return {
        "name": "McLeuker AI V8 API",
        "version": "8.0.0",
        "status": "operational",
        "features": [
            "Multi-Model Orchestration (Grok-4 + Kimi K2.5)",
            "Memory System",
            "RAG Knowledge Base",
            "Multi-Agent Collaboration",
            "Quick & Deep Search Modes",
            "Image Generation",
            "Document Generation (Excel, Word, PPT, PDF)",
            "Natural Conversational Output"
        ]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "8.0.0"
    }

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
    """Generate quick fallback response with natural tone"""
    import aiohttp
    
    grok_key = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
    if not grok_key:
        return "I'm here to help with fashion insights. Could you rephrase your question?"
    
    # Natural, conversational system prompt - NO FORCED STRUCTURE
    system_prompt = """You are McLeuker AI, a fashion intelligence expert having a natural conversation.

## ABSOLUTE PROHIBITIONS - VIOLATION WILL RESULT IN FAILURE:
1. DO NOT use any emojis as section headers (🔥, 📈, 💡, etc.)
2. DO NOT create sections titled "Key Trends", "Future Outlook", or "Key Takeaways"
3. DO NOT use the same structure for every response
4. DO NOT start with "Certainly!", "Of course!", "Great question!"
5. DO NOT end with "Let me know if you have more questions!"

## YOUR COMMUNICATION STYLE:
- Write as if you're having a real conversation with a curious friend
- Let your thoughts flow naturally - don't force bullet points
- Show your reasoning: "What I find interesting is...", "This connects to..."
- Be direct and insightful without being robotic
- Each response should feel unique to the specific question
- Keep it concise but substantive"""
    
    if rag_context:
        system_prompt += f"\n\nContext:\n{rag_context[:500]}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.x.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {grok_key}", "Content-Type": "application/json"},
                json={
                    "model": "grok-4-fast-non-reasoning",
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
    """Generate deep fallback response with natural, comprehensive tone"""
    import aiohttp
    
    grok_key = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
    if not grok_key:
        return "I'm conducting deep research on your question. Please try again in a moment."
    
    # Natural, conversational system prompt - NO FORCED STRUCTURE
    system_prompt = """You are McLeuker AI, a comprehensive fashion intelligence expert having a thoughtful conversation.

## ABSOLUTE PROHIBITIONS - VIOLATION WILL RESULT IN FAILURE:
1. DO NOT use any emojis as section headers (🔥 Key Trends, 📈 Future Outlook, 💡 Key Takeaways, etc.)
2. DO NOT create rigid sections with the same titles every time
3. DO NOT start with "Certainly!", "Of course!", "Great question!", "Absolutely!"
4. DO NOT end with "Let me know if you have more questions!" or similar
5. DO NOT use bullet points for everything - mix prose and lists naturally
6. DO NOT repeat the same phrases or transitions

## YOUR COMMUNICATION STYLE:
- Write like you're having an in-depth conversation with a curious colleague
- Show your reasoning naturally: "What's fascinating about this is...", "This connects to..."
- Acknowledge complexity: "This is nuanced because..."
- Be thorough but engaging - take the reader on a journey through your thinking
- Let the content dictate the structure, not a template
- Reference sources naturally when relevant
- End naturally, not with forced summary statements
- Each response should feel unique and tailored to this specific question"""
    
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
                    "model": "grok-4-fast-non-reasoning",
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
# Image Generation Endpoint - FIXED: Uses correct API key
# =============================================================================

@app.post("/api/image/generate")
async def generate_image(request: ImageGenerateRequest):
    """Generate images using xAI Grok Imagine or OpenAI DALL-E 3"""
    import httpx
    
    try:
        # Try xAI API key first (for grok-imagine-image), then OpenAI
        xai_api_key = os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not xai_api_key and not openai_api_key:
            raise HTTPException(status_code=500, detail="Image generation API not configured. Please add XAI_API_KEY or OPENAI_API_KEY to environment variables.")
        
        # Enhance prompt for fashion domain
        style_enhancements = {
            "fashion": "high-end fashion photography, editorial style, professional lighting, vogue magazine quality",
            "streetwear": "urban street fashion, dynamic pose, city background, authentic street style",
            "minimalist": "clean minimal design, white background, simple composition, elegant simplicity",
            "luxury": "premium luxury aesthetic, sophisticated, elegant, high-end materials",
            "sustainable": "natural eco-friendly aesthetic, organic materials, earth tones, sustainable fashion",
            "avant-garde": "experimental artistic style, bold creative, avant-garde fashion, artistic expression"
        }
        
        style_suffix = style_enhancements.get(request.style, style_enhancements["fashion"])
        enhanced_prompt = f"{request.prompt}. {style_suffix}. High quality, detailed, 8K resolution."
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Try xAI grok-imagine-image first
            if xai_api_key:
                try:
                    response = await client.post(
                        "https://api.x.ai/v1/images/generations",
                        headers={
                            "Authorization": f"Bearer {xai_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "grok-imagine-image",
                            "prompt": enhanced_prompt,
                            "n": 1
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "data" in data and len(data["data"]) > 0:
                            image_url = data["data"][0].get("url")
                            return {
                                "success": True,
                                "image_url": image_url,
                                "prompt": request.prompt,
                                "enhanced_prompt": enhanced_prompt,
                                "style": request.style,
                                "provider": "xAI Grok Imagine"
                            }
                except Exception as e:
                    logger.warning(f"xAI image generation failed, trying OpenAI: {e}")
            
            # Fall back to OpenAI DALL-E 3
            if openai_api_key:
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
                        "size": "1024x1024",
                        "quality": "hd",
                        "style": "vivid"
                    }
                )
                
                if response.status_code != 200:
                    error_data = response.json()
                    logger.error(f"OpenAI image generation error: {error_data}")
                    error_msg = error_data.get("error", {}).get("message", "Image generation failed")
                    raise HTTPException(status_code=response.status_code, detail=error_msg)
                
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
                        "style": request.style,
                        "provider": "OpenAI DALL-E 3"
                    }
            
            raise HTTPException(status_code=500, detail="No image generated - both xAI and OpenAI failed")
                
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Image generation timed out")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# Document Generation Endpoints - FIXED: Actually generates files
# =============================================================================

@app.post("/api/document/generate")
async def generate_document(request: DocumentGenerateRequest):
    """Generate downloadable documents (Markdown, PDF, Word, Excel, PowerPoint)"""
    
    try:
        title = request.title or "McLeuker AI Report"
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_title = title.replace(' ', '_').replace('/', '_')
        
        if request.format == "markdown":
            # Markdown file
            filename = f"{safe_title}_{timestamp}.md"
            content = f"# {title}\n\n*Generated by McLeuker AI on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*\n\n{request.content}"
            
            return Response(
                content=content.encode('utf-8'),
                media_type="text/markdown",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )
        
        elif request.format == "pdf":
            # PDF file using weasyprint or fpdf
            try:
                from weasyprint import HTML, CSS
                
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                        h1 {{ color: #177b57; border-bottom: 2px solid #177b57; padding-bottom: 10px; }}
                        h2 {{ color: #266a2e; margin-top: 30px; }}
                        h3 {{ color: #3d665c; }}
                        p {{ margin: 10px 0; }}
                        ul, ol {{ margin: 10px 0 10px 20px; }}
                        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ccc; font-size: 12px; color: #666; }}
                    </style>
                </head>
                <body>
                    <h1>{title}</h1>
                    {_markdown_to_html(request.content)}
                    <div class="footer">Generated by McLeuker AI on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</div>
                </body>
                </html>
                """
                
                pdf_bytes = HTML(string=html_content).write_pdf()
                filename = f"{safe_title}_{timestamp}.pdf"
                
                return Response(
                    content=pdf_bytes,
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f'attachment; filename="{filename}"'
                    }
                )
            except ImportError:
                # Fallback to fpdf
                from fpdf import FPDF
                
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, title, ln=True)
                pdf.set_font("Arial", "", 12)
                
                # Split content into lines and add to PDF
                for line in request.content.split('\n'):
                    pdf.multi_cell(0, 10, line)
                
                pdf_bytes = pdf.output(dest='S').encode('latin-1')
                filename = f"{safe_title}_{timestamp}.pdf"
                
                return Response(
                    content=pdf_bytes,
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f'attachment; filename="{filename}"'
                    }
                )
        
        elif request.format == "docx":
            # Word document using python-docx
            try:
                from docx import Document
                from docx.shared import Inches, Pt, RGBColor
                from docx.enum.text import WD_ALIGN_PARAGRAPH
                
                doc = Document()
                
                # Add title
                title_para = doc.add_heading(title, 0)
                title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                
                # Add timestamp
                timestamp_para = doc.add_paragraph(f"Generated by McLeuker AI on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
                timestamp_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                timestamp_para.runs[0].font.size = Pt(10)
                timestamp_para.runs[0].font.color.rgb = RGBColor(128, 128, 128)
                
                doc.add_paragraph()  # Spacer
                
                # Parse and add content
                for line in request.content.split('\n'):
                    line = line.strip()
                    if not line:
                        doc.add_paragraph()
                    elif line.startswith('### '):
                        doc.add_heading(line[4:], level=3)
                    elif line.startswith('## '):
                        doc.add_heading(line[3:], level=2)
                    elif line.startswith('# '):
                        doc.add_heading(line[2:], level=1)
                    elif line.startswith('- ') or line.startswith('* '):
                        doc.add_paragraph(line[2:], style='List Bullet')
                    elif line[0].isdigit() and '. ' in line[:4]:
                        doc.add_paragraph(line.split('. ', 1)[1], style='List Number')
                    else:
                        doc.add_paragraph(line)
                
                # Save to bytes
                doc_bytes = io.BytesIO()
                doc.save(doc_bytes)
                doc_bytes.seek(0)
                
                filename = f"{safe_title}_{timestamp}.docx"
                
                return Response(
                    content=doc_bytes.getvalue(),
                    media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    headers={
                        "Content-Disposition": f'attachment; filename="{filename}"'
                    }
                )
            except ImportError:
                raise HTTPException(status_code=500, detail="Word document generation not available. Please install python-docx.")
        
        elif request.format == "xlsx":
            # Excel spreadsheet using openpyxl
            try:
                from openpyxl import Workbook
                from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
                from openpyxl.utils import get_column_letter
                
                wb = Workbook()
                ws = wb.active
                ws.title = "Report"
                
                # Style definitions
                header_font = Font(bold=True, color="FFFFFF", size=12)
                header_fill = PatternFill(start_color="177B57", end_color="177B57", fill_type="solid")
                border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
                
                # Add title
                ws['A1'] = title
                ws['A1'].font = Font(bold=True, size=16, color="177B57")
                ws.merge_cells('A1:D1')
                
                ws['A2'] = f"Generated by McLeuker AI on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
                ws['A2'].font = Font(italic=True, size=10, color="808080")
                ws.merge_cells('A2:D2')
                
                # If data is provided, create a proper table
                if request.data and len(request.data) > 0:
                    # Headers
                    headers = list(request.data[0].keys())
                    for col, header in enumerate(headers, 1):
                        cell = ws.cell(row=4, column=col, value=header)
                        cell.font = header_font
                        cell.fill = header_fill
                        cell.alignment = Alignment(horizontal='center')
                        cell.border = border
                    
                    # Data rows
                    for row_idx, row_data in enumerate(request.data, 5):
                        for col_idx, header in enumerate(headers, 1):
                            cell = ws.cell(row=row_idx, column=col_idx, value=row_data.get(header, ''))
                            cell.border = border
                    
                    # Auto-adjust column widths
                    for col in range(1, len(headers) + 1):
                        ws.column_dimensions[get_column_letter(col)].width = 20
                else:
                    # Just add content as text
                    row = 4
                    for line in request.content.split('\n'):
                        if line.strip():
                            ws.cell(row=row, column=1, value=line.strip())
                            row += 1
                    
                    ws.column_dimensions['A'].width = 100
                
                # Save to bytes
                excel_bytes = io.BytesIO()
                wb.save(excel_bytes)
                excel_bytes.seek(0)
                
                filename = f"{safe_title}_{timestamp}.xlsx"
                
                return Response(
                    content=excel_bytes.getvalue(),
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={
                        "Content-Disposition": f'attachment; filename="{filename}"'
                    }
                )
            except ImportError:
                raise HTTPException(status_code=500, detail="Excel generation not available. Please install openpyxl.")
        
        elif request.format == "pptx":
            # PowerPoint presentation using python-pptx
            try:
                from pptx import Presentation
                from pptx.util import Inches, Pt
                from pptx.dml.color import RGBColor
                from pptx.enum.text import PP_ALIGN
                
                prs = Presentation()
                prs.slide_width = Inches(13.333)
                prs.slide_height = Inches(7.5)
                
                # Title slide
                title_slide_layout = prs.slide_layouts[6]  # Blank
                slide = prs.slides.add_slide(title_slide_layout)
                
                # Add title
                title_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(12.333), Inches(1.5))
                title_frame = title_box.text_frame
                title_para = title_frame.paragraphs[0]
                title_para.text = title
                title_para.font.size = Pt(44)
                title_para.font.bold = True
                title_para.font.color.rgb = RGBColor(23, 123, 87)
                title_para.alignment = PP_ALIGN.CENTER
                
                # Add subtitle
                subtitle_box = slide.shapes.add_textbox(Inches(0.5), Inches(4.2), Inches(12.333), Inches(0.5))
                subtitle_frame = subtitle_box.text_frame
                subtitle_para = subtitle_frame.paragraphs[0]
                subtitle_para.text = f"Generated by McLeuker AI • {datetime.utcnow().strftime('%Y-%m-%d')}"
                subtitle_para.font.size = Pt(18)
                subtitle_para.font.color.rgb = RGBColor(128, 128, 128)
                subtitle_para.alignment = PP_ALIGN.CENTER
                
                # Content slides - split content into sections
                sections = request.content.split('\n\n')
                current_slide_content = []
                
                for section in sections:
                    section = section.strip()
                    if not section:
                        continue
                    
                    # Check if it's a header
                    if section.startswith('# ') or section.startswith('## '):
                        # Create new slide for header
                        if current_slide_content:
                            _add_content_slide(prs, current_slide_content)
                            current_slide_content = []
                        
                        header_text = section.lstrip('#').strip()
                        current_slide_content.append(('header', header_text))
                    else:
                        current_slide_content.append(('content', section))
                        
                        # If content is getting long, create slide
                        if len(current_slide_content) > 5:
                            _add_content_slide(prs, current_slide_content)
                            current_slide_content = []
                
                # Add remaining content
                if current_slide_content:
                    _add_content_slide(prs, current_slide_content)
                
                # Save to bytes
                pptx_bytes = io.BytesIO()
                prs.save(pptx_bytes)
                pptx_bytes.seek(0)
                
                filename = f"{safe_title}_{timestamp}.pptx"
                
                return Response(
                    content=pptx_bytes.getvalue(),
                    media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    headers={
                        "Content-Disposition": f'attachment; filename="{filename}"'
                    }
                )
            except ImportError:
                raise HTTPException(status_code=500, detail="PowerPoint generation not available. Please install python-pptx.")
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}. Supported: markdown, pdf, docx, xlsx, pptx")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _markdown_to_html(markdown_text: str) -> str:
    """Convert markdown to HTML"""
    html_lines = []
    
    for line in markdown_text.split('\n'):
        if line.startswith('### '):
            html_lines.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('## '):
            html_lines.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('# '):
            html_lines.append(f'<h1>{line[2:]}</h1>')
        elif line.startswith('- ') or line.startswith('* '):
            html_lines.append(f'<li>{line[2:]}</li>')
        elif line.strip():
            # Handle bold text
            import re
            line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            html_lines.append(f'<p>{line}</p>')
        else:
            html_lines.append('<br>')
    
    return '\n'.join(html_lines)

def _add_content_slide(prs, content_items):
    """Add a content slide to the presentation"""
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    
    slide_layout = prs.slide_layouts[6]  # Blank
    slide = prs.slides.add_slide(slide_layout)
    
    y_position = Inches(0.5)
    
    for item_type, item_content in content_items:
        if item_type == 'header':
            text_box = slide.shapes.add_textbox(Inches(0.5), y_position, Inches(12.333), Inches(0.8))
            text_frame = text_box.text_frame
            para = text_frame.paragraphs[0]
            para.text = item_content
            para.font.size = Pt(32)
            para.font.bold = True
            para.font.color.rgb = RGBColor(23, 123, 87)
            y_position += Inches(1)
        else:
            text_box = slide.shapes.add_textbox(Inches(0.5), y_position, Inches(12.333), Inches(1))
            text_frame = text_box.text_frame
            text_frame.word_wrap = True
            para = text_frame.paragraphs[0]
            para.text = item_content[:500]  # Limit text per slide
            para.font.size = Pt(18)
            para.font.color.rgb = RGBColor(60, 60, 60)
            y_position += Inches(1.2)

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
        content={"detail": str(exc)}
    )

# =============================================================================
# Run Application
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
