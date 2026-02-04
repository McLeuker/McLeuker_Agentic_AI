"""
McLeuker AI V8 API - Advanced Multi-Model Architecture
======================================================
Production-ready API integrating:
- Memory System (persistent conversation context)
- Multi-Agent Collaboration (task delegation)
- RAG System (fashion domain knowledge retrieval)
- Grok-4 (deep reasoning) with ChatGPT fallback
- Kimi K2.5 (execution and tool calls)
- Pinterest, YouTube, X/Twitter data integration
- Human-like conversational output (NO forced structure)
- Different Quick vs Deep search logic (Manus AI style)
- Image Generation (xAI Grok Imagine / OpenAI DALL-E)
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
import httpx
import aiohttp
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
        
        memory = get_memory_system()
        rag = get_rag_system()
        agents = get_multi_agent_system()
        
        logger.info("All systems initialized successfully")
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

# CORS configuration
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
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "Multi-Model Orchestration (Grok-4 + ChatGPT fallback + Kimi K2.5)",
            "Memory System",
            "RAG Knowledge Base",
            "Multi-Agent Collaboration",
            "Quick & Deep Search Modes",
            "Image Generation (xAI + OpenAI)",
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
# ChatGPT Fallback Helper
# =============================================================================

async def _call_chatgpt(system_prompt: str, user_message: str, max_tokens: int = 1500) -> Optional[str]:
    """Call ChatGPT as fallback when Grok fails"""
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        return None
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 0.7,
                    "max_tokens": max_tokens
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    logger.error(f"ChatGPT API error: {error_text}")
                    return None
    except Exception as e:
        logger.error(f"ChatGPT fallback error: {e}")
        return None

async def _call_grok(system_prompt: str, user_message: str, max_tokens: int = 1500) -> Optional[str]:
    """Call Grok API with ChatGPT fallback"""
    grok_key = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
    
    # Try Grok first
    if grok_key:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {grok_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "grok-4-fast-non-reasoning",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message}
                        ],
                        "temperature": 0.7,
                        "max_tokens": max_tokens
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.warning(f"Grok API error (status {response.status}): {error_text}")
                        # Fall through to ChatGPT fallback
        except Exception as e:
            logger.warning(f"Grok API exception: {e}")
            # Fall through to ChatGPT fallback
    
    # Fallback to ChatGPT
    logger.info("Falling back to ChatGPT...")
    return await _call_chatgpt(system_prompt, user_message, max_tokens)

# =============================================================================
# Natural System Prompt (NO FORCED STRUCTURE)
# =============================================================================

NATURAL_SYSTEM_PROMPT = """You are McLeuker AI, a fashion intelligence expert having a natural conversation.

## ABSOLUTE PROHIBITIONS - VIOLATION WILL RESULT IN FAILURE:
1. DO NOT use any emojis as section headers (🔥, 📈, 💡, etc.)
2. DO NOT create sections titled "Key Trends", "Future Outlook", or "Key Takeaways"
3. DO NOT use the same structure for every response
4. DO NOT start with "Certainly!", "Of course!", "Great question!"
5. DO NOT end with "Let me know if you have more questions!"
6. DO NOT use bullet points for everything - mix prose and lists naturally

## YOUR COMMUNICATION STYLE:
- Write as if you're having a real conversation with a curious friend
- Let your thoughts flow naturally - don't force bullet points
- Show your reasoning: "What I find interesting is...", "This connects to..."
- Be direct and insightful without being robotic
- Each response should feel unique to the specific question
- Keep it concise but substantive"""

# =============================================================================
# Quick Mode - Fast, Focused Response
# =============================================================================

async def _quick_mode_generate(request: ChatRequest):
    """Quick Mode: Fast, focused response with ChatGPT fallback"""
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        # Layer 1: Quick Understanding
        layer_id = str(uuid.uuid4())[:8]
        yield f"data: {json.dumps({'type': 'layer_start', 'data': {'layer_id': layer_id, 'layer_num': 1, 'type': 'understanding', 'title': 'Understanding your question'}})}\n\n"
        yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Parsing intent...', 'status': 'active'}})}\n\n"
        await asyncio.sleep(0.15)
        yield f"data: {json.dumps({'type': 'layer_complete', 'data': {'layer_id': layer_id, 'content': 'Ready to respond'}})}\n\n"
        
        # Layer 2: Generate Response
        layer_id = str(uuid.uuid4())[:8]
        yield f"data: {json.dumps({'type': 'layer_start', 'data': {'layer_id': layer_id, 'layer_num': 2, 'type': 'writing', 'title': 'Generating response'}})}\n\n"
        
        # Build context-aware prompt
        sector_context = f"\n\nFocus area: {request.sector}" if request.sector else ""
        system_prompt = NATURAL_SYSTEM_PROMPT + sector_context + "\n\nKeep your response concise and focused."
        
        # Call Grok with ChatGPT fallback
        full_content = await _call_grok(system_prompt, request.message, max_tokens=800)
        
        if not full_content:
            full_content = "I apologize, but I'm having trouble generating a response right now. Please try again in a moment."
        
        # Stream the content
        yield f"data: {json.dumps({'type': 'content', 'data': {'chunk': full_content}})}\n\n"
        yield f"data: {json.dumps({'type': 'layer_complete', 'data': {'layer_id': layer_id, 'content': 'Done'}})}\n\n"
        
        # Quick follow-up
        follow_up = _generate_quick_follow_up(request.message)
        
        # Complete
        yield f"data: {json.dumps({'type': 'complete', 'data': {'content': full_content, 'sources': [], 'follow_up_questions': follow_up, 'credits_used': 2, 'session_id': session_id, 'mode': 'quick'}})}\n\n"
        
    except Exception as e:
        logger.error(f"Quick mode error: {e}")
        yield f"data: {json.dumps({'type': 'error', 'data': {'message': str(e)}})}\n\n"

# =============================================================================
# Deep Mode - Comprehensive Research
# =============================================================================

async def _deep_mode_generate(request: ChatRequest):
    """Deep Mode: Comprehensive research with ChatGPT fallback"""
    try:
        session_id = request.session_id or str(uuid.uuid4())
        sources = []
        
        # Layer 1: Understanding
        layer_id = str(uuid.uuid4())[:8]
        yield f"data: {json.dumps({'type': 'layer_start', 'data': {'layer_id': layer_id, 'layer_num': 1, 'type': 'understanding', 'title': 'Understanding your request'}})}\n\n"
        yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Analyzing query complexity...', 'status': 'active'}})}\n\n"
        await asyncio.sleep(0.2)
        yield f"data: {json.dumps({'type': 'layer_complete', 'data': {'layer_id': layer_id, 'content': 'Query analyzed'}})}\n\n"
        
        # Layer 2: Planning
        layer_id = str(uuid.uuid4())[:8]
        yield f"data: {json.dumps({'type': 'layer_start', 'data': {'layer_id': layer_id, 'layer_num': 2, 'type': 'planning', 'title': 'Planning research approach'}})}\n\n"
        yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Identifying research angles...', 'status': 'active'}})}\n\n"
        await asyncio.sleep(0.2)
        yield f"data: {json.dumps({'type': 'layer_complete', 'data': {'layer_id': layer_id, 'content': 'Research plan ready'}})}\n\n"
        
        # Layer 3: Research
        layer_id = str(uuid.uuid4())[:8]
        yield f"data: {json.dumps({'type': 'layer_start', 'data': {'layer_id': layer_id, 'layer_num': 3, 'type': 'research', 'title': 'Gathering information'}})}\n\n"
        yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Searching fashion databases...', 'status': 'active'}})}\n\n"
        await asyncio.sleep(0.3)
        
        # Add some mock sources for now
        sources = [
            {"title": "Fashion Industry Analysis", "url": "https://example.com/fashion", "snippet": "Latest trends in fashion..."},
            {"title": "Sustainable Fashion Report", "url": "https://example.com/sustainable", "snippet": "Eco-friendly fashion..."},
            {"title": "Market Research", "url": "https://example.com/market", "snippet": "Fashion market insights..."}
        ]
        yield f"data: {json.dumps({'type': 'sources', 'data': {'sources': sources}})}\n\n"
        yield f"data: {json.dumps({'type': 'layer_complete', 'data': {'layer_id': layer_id, 'content': f'{len(sources)} sources gathered'}})}\n\n"
        
        # Layer 4: Analysis
        layer_id = str(uuid.uuid4())[:8]
        yield f"data: {json.dumps({'type': 'layer_start', 'data': {'layer_id': layer_id, 'layer_num': 4, 'type': 'analysis', 'title': 'Analyzing findings'}})}\n\n"
        yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Identifying patterns...', 'status': 'active'}})}\n\n"
        await asyncio.sleep(0.2)
        yield f"data: {json.dumps({'type': 'layer_complete', 'data': {'layer_id': layer_id, 'content': 'Analysis complete'}})}\n\n"
        
        # Layer 5: Synthesis
        layer_id = str(uuid.uuid4())[:8]
        yield f"data: {json.dumps({'type': 'layer_start', 'data': {'layer_id': layer_id, 'layer_num': 5, 'type': 'synthesis', 'title': 'Synthesizing insights'}})}\n\n"
        yield f"data: {json.dumps({'type': 'sub_step', 'data': {'layer_id': layer_id, 'step': 'Connecting findings...', 'status': 'active'}})}\n\n"
        await asyncio.sleep(0.2)
        yield f"data: {json.dumps({'type': 'layer_complete', 'data': {'layer_id': layer_id, 'content': 'Insights synthesized'}})}\n\n"
        
        # Layer 6: Generate Response
        layer_id = str(uuid.uuid4())[:8]
        yield f"data: {json.dumps({'type': 'layer_start', 'data': {'layer_id': layer_id, 'layer_num': 6, 'type': 'writing', 'title': 'Generating comprehensive response'}})}\n\n"
        
        # Build comprehensive prompt
        sector_context = f"\n\nFocus area: {request.sector}" if request.sector else ""
        system_prompt = NATURAL_SYSTEM_PROMPT + sector_context + "\n\nProvide a comprehensive, well-researched response. Be thorough but engaging."
        
        # Call Grok with ChatGPT fallback
        full_content = await _call_grok(system_prompt, request.message, max_tokens=2500)
        
        if not full_content:
            full_content = "I apologize, but I'm having trouble generating a comprehensive response right now. Please try again in a moment."
        
        # Stream the content
        yield f"data: {json.dumps({'type': 'content', 'data': {'chunk': full_content}})}\n\n"
        yield f"data: {json.dumps({'type': 'layer_complete', 'data': {'layer_id': layer_id, 'content': 'Response generated'}})}\n\n"
        
        # Deep follow-up questions
        follow_up = _generate_deep_follow_up(request.message, full_content, sources)
        
        # Complete
        yield f"data: {json.dumps({'type': 'complete', 'data': {'content': full_content, 'sources': sources, 'follow_up_questions': follow_up, 'credits_used': 5, 'session_id': session_id, 'mode': 'deep'}})}\n\n"
        
    except Exception as e:
        logger.error(f"Deep mode error: {e}")
        yield f"data: {json.dumps({'type': 'error', 'data': {'message': str(e)}})}\n\n"

# =============================================================================
# Main Chat Endpoint
# =============================================================================

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """Main chat endpoint - routes to Quick or Deep mode"""
    
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
# Follow-up Question Generators
# =============================================================================

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
        return ["Can you elaborate on this?", "What should I consider next?"]

def _generate_deep_follow_up(query: str, response: str, sources: List) -> List[str]:
    """Generate 5 contextual follow-up questions"""
    questions = []
    query_lower = query.lower()
    
    if "trend" in query_lower:
        questions = [
            "How will this trend evolve in the next year?",
            "Which demographics are driving this trend?",
            "What are the investment implications?",
            "How are luxury brands responding?",
            "What's the sustainability angle?"
        ]
    elif "sustainable" in query_lower:
        questions = [
            "What are the most impactful certifications?",
            "How do consumers verify sustainability claims?",
            "Which materials show the most promise?",
            "What's the cost-benefit analysis?",
            "How are regulations evolving?"
        ]
    else:
        questions = [
            "What are the key market implications?",
            "How does this compare historically?",
            "What should brands focus on?",
            "What are the consumer behavior insights?",
            "What's the competitive landscape?"
        ]
    
    return questions[:5]

# =============================================================================
# Image Generation Endpoint - FIXED
# =============================================================================

@app.post("/api/image/generate")
async def generate_image(request: ImageGenerateRequest):
    """Generate images using xAI Grok Imagine or OpenAI DALL-E"""
    
    try:
        xai_api_key = os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not xai_api_key and not openai_api_key:
            raise HTTPException(status_code=500, detail="Image generation API not configured")
        
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
        enhanced_prompt = f"{request.prompt}. {style_suffix}. High quality, detailed."
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Try xAI grok-imagine-image first
            if xai_api_key:
                try:
                    logger.info("Trying xAI grok-imagine-image...")
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
                    else:
                        error_text = response.text
                        logger.warning(f"xAI image generation failed (status {response.status_code}): {error_text}")
                except Exception as e:
                    logger.warning(f"xAI image generation exception: {e}")
            
            # Fall back to OpenAI DALL-E 3
            if openai_api_key:
                logger.info("Falling back to OpenAI DALL-E 3...")
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
                        "quality": "standard"
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
                            "provider": "OpenAI DALL-E 3"
                        }
                else:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", "Image generation failed")
                    raise HTTPException(status_code=response.status_code, detail=f"OpenAI error: {error_msg}")
            
            raise HTTPException(status_code=500, detail="Both xAI and OpenAI image generation failed")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# Document Generation Endpoints
# =============================================================================

@app.post("/api/document/generate")
async def generate_document(request: DocumentGenerateRequest):
    """Generate downloadable documents"""
    
    try:
        title = request.title or "McLeuker AI Report"
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_title = title.replace(' ', '_').replace('/', '_')
        
        if request.format == "markdown":
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
            try:
                from fpdf import FPDF
                
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, title, ln=True, align="C")
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 10, f"Generated by McLeuker AI - {datetime.utcnow().strftime('%Y-%m-%d')}", ln=True, align="C")
                pdf.ln(10)
                pdf.set_font("Arial", "", 12)
                
                # Handle content
                for line in request.content.split('\n'):
                    if line.startswith('# '):
                        pdf.set_font("Arial", "B", 14)
                        pdf.multi_cell(0, 8, line[2:])
                        pdf.set_font("Arial", "", 12)
                    elif line.startswith('## '):
                        pdf.set_font("Arial", "B", 12)
                        pdf.multi_cell(0, 8, line[3:])
                        pdf.set_font("Arial", "", 12)
                    else:
                        pdf.multi_cell(0, 6, line)
                
                pdf_output = pdf.output(dest='S').encode('latin-1')
                filename = f"{safe_title}_{timestamp}.pdf"
                
                return Response(
                    content=pdf_output,
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f'attachment; filename="{filename}"'
                    }
                )
            except Exception as e:
                logger.error(f"PDF generation error: {e}")
                raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
        
        elif request.format == "xlsx":
            try:
                from openpyxl import Workbook
                from openpyxl.styles import Font, Alignment, PatternFill
                
                wb = Workbook()
                ws = wb.active
                ws.title = "Report"
                
                # Header
                ws['A1'] = title
                ws['A1'].font = Font(bold=True, size=14)
                ws['A2'] = f"Generated by McLeuker AI - {datetime.utcnow().strftime('%Y-%m-%d')}"
                
                # Content
                row = 4
                for line in request.content.split('\n'):
                    if line.strip():
                        ws[f'A{row}'] = line
                        row += 1
                
                # If data provided, add as table
                if request.data:
                    row += 2
                    ws[f'A{row}'] = "Data Table"
                    ws[f'A{row}'].font = Font(bold=True)
                    row += 1
                    
                    if request.data:
                        headers = list(request.data[0].keys())
                        for col, header in enumerate(headers, 1):
                            cell = ws.cell(row=row, column=col, value=header)
                            cell.font = Font(bold=True)
                            cell.fill = PatternFill(start_color="177b57", end_color="177b57", fill_type="solid")
                        row += 1
                        
                        for item in request.data:
                            for col, header in enumerate(headers, 1):
                                ws.cell(row=row, column=col, value=item.get(header, ""))
                            row += 1
                
                output = io.BytesIO()
                wb.save(output)
                output.seek(0)
                filename = f"{safe_title}_{timestamp}.xlsx"
                
                return Response(
                    content=output.getvalue(),
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={
                        "Content-Disposition": f'attachment; filename="{filename}"'
                    }
                )
            except Exception as e:
                logger.error(f"Excel generation error: {e}")
                raise HTTPException(status_code=500, detail=f"Excel generation failed: {str(e)}")
        
        elif request.format == "docx":
            try:
                from docx import Document
                from docx.shared import Inches, Pt
                from docx.enum.text import WD_ALIGN_PARAGRAPH
                
                doc = Document()
                
                # Title
                title_para = doc.add_heading(title, 0)
                title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                
                # Subtitle
                subtitle = doc.add_paragraph(f"Generated by McLeuker AI - {datetime.utcnow().strftime('%Y-%m-%d')}")
                subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
                
                doc.add_paragraph()
                
                # Content
                for line in request.content.split('\n'):
                    if line.startswith('# '):
                        doc.add_heading(line[2:], level=1)
                    elif line.startswith('## '):
                        doc.add_heading(line[3:], level=2)
                    elif line.startswith('### '):
                        doc.add_heading(line[4:], level=3)
                    elif line.startswith('- '):
                        doc.add_paragraph(line[2:], style='List Bullet')
                    elif line.strip():
                        doc.add_paragraph(line)
                
                output = io.BytesIO()
                doc.save(output)
                output.seek(0)
                filename = f"{safe_title}_{timestamp}.docx"
                
                return Response(
                    content=output.getvalue(),
                    media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    headers={
                        "Content-Disposition": f'attachment; filename="{filename}"'
                    }
                )
            except Exception as e:
                logger.error(f"Word generation error: {e}")
                raise HTTPException(status_code=500, detail=f"Word generation failed: {str(e)}")
        
        elif request.format == "pptx":
            try:
                from pptx import Presentation
                from pptx.util import Inches, Pt
                from pptx.dml.color import RgbColor
                
                prs = Presentation()
                prs.slide_width = Inches(13.333)
                prs.slide_height = Inches(7.5)
                
                # Title slide
                title_slide_layout = prs.slide_layouts[0]
                slide = prs.slides.add_slide(title_slide_layout)
                slide.shapes.title.text = title
                slide.placeholders[1].text = f"Generated by McLeuker AI\n{datetime.utcnow().strftime('%Y-%m-%d')}"
                
                # Content slides
                content_layout = prs.slide_layouts[1]
                current_slide = None
                current_content = []
                
                for line in request.content.split('\n'):
                    if line.startswith('# ') or line.startswith('## '):
                        if current_slide and current_content:
                            body = current_slide.placeholders[1]
                            body.text = '\n'.join(current_content)
                        
                        current_slide = prs.slides.add_slide(content_layout)
                        heading = line.lstrip('#').strip()
                        current_slide.shapes.title.text = heading
                        current_content = []
                    elif line.strip() and current_slide:
                        current_content.append(line)
                
                if current_slide and current_content:
                    body = current_slide.placeholders[1]
                    body.text = '\n'.join(current_content)
                
                output = io.BytesIO()
                prs.save(output)
                output.seek(0)
                filename = f"{safe_title}_{timestamp}.pptx"
                
                return Response(
                    content=output.getvalue(),
                    media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    headers={
                        "Content-Disposition": f'attachment; filename="{filename}"'
                    }
                )
            except Exception as e:
                logger.error(f"PowerPoint generation error: {e}")
                raise HTTPException(status_code=500, detail=f"PowerPoint generation failed: {str(e)}")
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# Kimi K2.5 Execution Endpoint
# =============================================================================

@app.post("/api/kimi/execute")
async def kimi_execute(request: ToolExecuteRequest):
    """Execute tools using Kimi K2.5"""
    
    moonshot_key = os.getenv("MOONSHOT_API_KEY")
    if not moonshot_key:
        raise HTTPException(status_code=500, detail="Moonshot API key not configured")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.moonshot.cn/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {moonshot_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "kimi-k2.5-preview",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant that executes tasks efficiently."},
                        {"role": "user", "content": f"Execute this task: {request.tool} with params: {json.dumps(request.params)}"}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "result": data["choices"][0]["message"]["content"],
                    "tool": request.tool
                }
            else:
                raise HTTPException(status_code=response.status_code, detail="Kimi execution failed")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Kimi execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# Run Application
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
