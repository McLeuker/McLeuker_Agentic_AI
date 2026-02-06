"""
McLeuker AI V8.0 - Multi-Layer Agentic Reasoning API
=====================================================
True agentic AI with multi-layer reasoning like Manus AI.
Includes Nano Banana image generation integration.
"""

import os
import json
import uuid
import base64
import asyncio
from datetime import datetime
from typing import Optional, AsyncGenerator, List
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from pydantic import BaseModel

from src.core.reasoning_orchestrator import ReasoningOrchestrator
from src.services.nano_banana import nano_banana_service


# Initialize orchestrator
reasoning_orchestrator = ReasoningOrchestrator()


# FastAPI app
app = FastAPI(
    title="McLeuker AI V8.0",
    description="Multi-Layer Agentic Reasoning AI Platform with Nano Banana Image Generation",
    version="8.0.0"
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
    sector: Optional[str] = None
    attachments: Optional[List[str]] = None  # Base64 encoded files


class ImageGenerateRequest(BaseModel):
    prompt: str
    style: Optional[str] = None
    aspect_ratio: str = "1:1"


class ImageEditRequest(BaseModel):
    image_data: str  # Base64 encoded
    edit_prompt: str
    mime_type: str = "image/png"


class ImageAnalyzeRequest(BaseModel):
    image_data: str  # Base64 encoded
    question: str
    mime_type: str = "image/png"


# =============================================================================
# Health check endpoint
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "8.0.0",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "multi_layer_reasoning": True,
            "streaming": True,
            "realtime_data": True,
            "dynamic_sources": True,
            "nano_banana": True,
            "file_upload": True
        }
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "McLeuker AI",
        "version": "8.0.0",
        "description": "Multi-Layer Agentic Reasoning AI Platform",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "chat_stream": "/api/chat/stream",
            "image_generate": "/api/image/generate",
            "image_edit": "/api/image/edit",
            "image_analyze": "/api/image/analyze",
            "file_upload": "/api/upload"
        }
    }


# =============================================================================
# Main Chat Endpoint (Non-streaming)
# =============================================================================

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint - collects all reasoning layers and returns final response.
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        # Collect all events from streaming
        reasoning_layers = []
        final_content = ""
        sources = []
        credits_used = 2
        
        async for event in reasoning_orchestrator.process_with_reasoning(
            query=request.message,
            session_id=session_id,
            mode=request.mode
        ):
            event_type = event.get("type")
            event_data = event.get("data", {})
            
            if event_type == "layer_start":
                reasoning_layers.append({
                    "id": event_data.get("layer_id"),
                    "layer_num": event_data.get("layer_num"),
                    "type": event_data.get("type"),
                    "title": event_data.get("title"),
                    "sub_steps": [],
                    "status": "active"
                })
            elif event_type == "sub_step":
                layer_id = event_data.get("layer_id")
                for layer in reasoning_layers:
                    if layer["id"] == layer_id:
                        layer["sub_steps"].append({
                            "step": event_data.get("step"),
                            "status": event_data.get("status")
                        })
            elif event_type == "layer_complete":
                layer_id = event_data.get("layer_id")
                for layer in reasoning_layers:
                    if layer["id"] == layer_id:
                        layer["status"] = "complete"
                        layer["content"] = event_data.get("content", "")
            elif event_type == "source":
                sources.append(event_data)
            elif event_type == "content":
                final_content += event_data.get("chunk", "")
            elif event_type == "complete":
                final_content = event_data.get("content", final_content)
                credits_used = event_data.get("credits_used", 2)
            elif event_type == "error":
                return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "error": event_data.get("message", "Unknown error")
                    }
                )
        
        return {
            "success": True,
            "response": {
                "content": final_content,
                "sources": sources
            },
            "reasoning_layers": reasoning_layers,
            "credits_used": credits_used,
            "session_id": session_id
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


# =============================================================================
# Streaming Chat Endpoint (SSE) - Multi-Layer Reasoning
# =============================================================================

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    SSE streaming chat endpoint with multi-layer agentic reasoning.
    
    Event Types:
    - layer_start: New reasoning layer started
    - sub_step: Sub-step within a layer
    - layer_complete: Layer completed
    - source: Found a source
    - content: Response content chunk
    - complete: Final response with all data
    - error: Error occurred
    """
    
    async def generate() -> AsyncGenerator[str, None]:
        session_id = request.session_id or str(uuid.uuid4())
        
        try:
            async for event in reasoning_orchestrator.process_with_reasoning(
                query=request.message,
                session_id=session_id,
                mode=request.mode
            ):
                # Format as SSE
                yield f"data: {json.dumps(event)}\n\n"
                
                # Small delay for smoother streaming
                event_type = event.get("type")
                if event_type in ["layer_start", "layer_complete"]:
                    await asyncio.sleep(0.1)
                elif event_type == "sub_step":
                    await asyncio.sleep(0.05)
                    
        except Exception as e:
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


# =============================================================================
# Nano Banana Image Generation Endpoints
# =============================================================================

@app.post("/api/image/generate")
async def generate_image(request: ImageGenerateRequest):
    """
    Generate an image using Nano Banana (Gemini).
    
    Args:
        prompt: Text description of the image
        style: Optional style modifier
        aspect_ratio: Image aspect ratio
    """
    result = await nano_banana_service.generate_image(
        prompt=request.prompt,
        style=request.style,
        aspect_ratio=request.aspect_ratio
    )
    
    if result["success"]:
        return {
            "success": True,
            "image_data": result["image_data"],
            "mime_type": result["mime_type"],
            "prompt": result["prompt"]
        }
    else:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": result.get("error", "Image generation failed")
            }
        )


@app.post("/api/image/edit")
async def edit_image(request: ImageEditRequest):
    """
    Edit an image using Nano Banana (Gemini).
    
    Args:
        image_data: Base64 encoded image
        edit_prompt: Description of the edit
        mime_type: Image MIME type
    """
    result = await nano_banana_service.edit_image(
        image_data=request.image_data,
        edit_prompt=request.edit_prompt,
        mime_type=request.mime_type
    )
    
    if result["success"]:
        return {
            "success": True,
            "image_data": result["image_data"],
            "mime_type": result["mime_type"],
            "edit_prompt": result["edit_prompt"]
        }
    else:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": result.get("error", "Image editing failed")
            }
        )


@app.post("/api/image/analyze")
async def analyze_image(request: ImageAnalyzeRequest):
    """
    Analyze an image using Nano Banana (Gemini).
    
    Args:
        image_data: Base64 encoded image
        question: Question about the image
        mime_type: Image MIME type
    """
    result = await nano_banana_service.analyze_image(
        image_data=request.image_data,
        question=request.question,
        mime_type=request.mime_type
    )
    
    if result["success"]:
        return {
            "success": True,
            "analysis": result["analysis"],
            "question": result["question"]
        }
    else:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": result.get("error", "Image analysis failed")
            }
        )


# =============================================================================
# File Upload Endpoint
# =============================================================================

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    analyze: bool = Form(default=False)
):
    """
    Upload a file for processing.
    
    Supports:
    - Images (PNG, JPG, WEBP) - can be analyzed with Nano Banana
    - Documents (PDF, DOCX, TXT) - can be processed for context
    """
    try:
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate file size (max 10MB)
        if file_size > 10 * 1024 * 1024:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "File too large. Maximum size is 10MB."
                }
            )
        
        # Generate file ID
        file_id = str(uuid.uuid4())[:8]
        
        # Determine file type
        content_type = file.content_type or "application/octet-stream"
        is_image = content_type.startswith("image/")
        
        # Encode to base64
        base64_content = base64.b64encode(content).decode("utf-8")
        
        response = {
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "content_type": content_type,
            "size": file_size,
            "base64_data": base64_content
        }
        
        # Optionally analyze images
        if analyze and is_image:
            analysis_result = await nano_banana_service.analyze_image(
                image_data=base64_content,
                question="Describe this image in detail. What do you see?",
                mime_type=content_type
            )
            
            if analysis_result["success"]:
                response["analysis"] = analysis_result["analysis"]
        
        return response
        
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
    
    if file_id.endswith(".xlsx"):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif file_id.endswith(".pdf"):
        media_type = "application/pdf"
    elif file_id.endswith(".png"):
        media_type = "image/png"
    elif file_id.endswith(".jpg") or file_id.endswith(".jpeg"):
        media_type = "image/jpeg"
    else:
        media_type = "application/octet-stream"
    
    return FileResponse(
        file_path,
        media_type=media_type,
        filename=file_id
    )


# =============================================================================
# Document Generation Endpoints
# =============================================================================

class DocumentGenerateRequest(BaseModel):
    content: str
    title: str
    format: str  # excel, powerpoint, word, markdown, pdf
    template: Optional[str] = None


@app.post("/api/document/generate")
async def generate_document(request: DocumentGenerateRequest):
    """
    Generate a document from content.
    
    Supported formats:
    - excel: Generate Excel spreadsheet (.xlsx)
    - powerpoint: Generate PowerPoint presentation (.pptx)
    - word: Generate Word document (.docx)
    - markdown: Generate Markdown file (.md)
    - pdf: Generate PDF document (.pdf)
    """
    import tempfile
    
    try:
        # Create temp directory if not exists
        os.makedirs("/tmp/mcleuker_files", exist_ok=True)
        
        file_id = str(uuid.uuid4())[:12]
        
        if request.format == "excel":
            # Generate Excel file
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            
            wb = Workbook()
            ws = wb.active
            ws.title = request.title[:31]  # Excel sheet name limit
            
            # Style header
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="6B21A8", end_color="6B21A8", fill_type="solid")
            
            # Parse content into rows
            lines = request.content.strip().split('\n')
            for row_idx, line in enumerate(lines, 1):
                cells = line.split('\t') if '\t' in line else [line]
                for col_idx, cell in enumerate(cells, 1):
                    ws.cell(row=row_idx, column=col_idx, value=cell.strip())
                    if row_idx == 1:
                        ws.cell(row=row_idx, column=col_idx).font = header_font
                        ws.cell(row=row_idx, column=col_idx).fill = header_fill
            
            # Auto-adjust column widths
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                ws.column_dimensions[column_letter].width = min(max_length + 2, 50)
            
            file_path = f"/tmp/mcleuker_files/{file_id}.xlsx"
            wb.save(file_path)
            filename = f"{request.title}.xlsx"
            
        elif request.format == "powerpoint":
            # Generate PowerPoint file
            from pptx import Presentation
            from pptx.util import Inches, Pt
            from pptx.dml.color import RgbColor
            
            prs = Presentation()
            prs.slide_width = Inches(13.333)
            prs.slide_height = Inches(7.5)
            
            # Parse content into slides
            slides_content = request.content.split('---SLIDE---')
            
            for slide_content in slides_content:
                slide_content = slide_content.strip()
                if not slide_content:
                    continue
                    
                slide_layout = prs.slide_layouts[1]  # Title and Content
                slide = prs.slides.add_slide(slide_layout)
                
                lines = slide_content.split('\n')
                title_text = lines[0] if lines else request.title
                body_text = '\n'.join(lines[1:]) if len(lines) > 1 else ""
                
                slide.shapes.title.text = title_text
                if slide.shapes.placeholders[1]:
                    slide.shapes.placeholders[1].text = body_text
            
            file_path = f"/tmp/mcleuker_files/{file_id}.pptx"
            prs.save(file_path)
            filename = f"{request.title}.pptx"
            
        elif request.format == "word":
            # Generate Word document
            from docx import Document
            from docx.shared import Inches, Pt, RGBColor
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            
            doc = Document()
            
            # Add title
            title = doc.add_heading(request.title, 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Parse content
            paragraphs = request.content.split('\n\n')
            for para in paragraphs:
                para = para.strip()
                if para.startswith('# '):
                    doc.add_heading(para[2:], level=1)
                elif para.startswith('## '):
                    doc.add_heading(para[3:], level=2)
                elif para.startswith('### '):
                    doc.add_heading(para[4:], level=3)
                elif para.startswith('- ') or para.startswith('• '):
                    for item in para.split('\n'):
                        if item.startswith('- ') or item.startswith('• '):
                            doc.add_paragraph(item[2:], style='List Bullet')
                else:
                    doc.add_paragraph(para)
            
            file_path = f"/tmp/mcleuker_files/{file_id}.docx"
            doc.save(file_path)
            filename = f"{request.title}.docx"
            
        elif request.format == "markdown":
            # Generate Markdown file
            content = f"# {request.title}\n\n{request.content}"
            file_path = f"/tmp/mcleuker_files/{file_id}.md"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            filename = f"{request.title}.md"
            
        elif request.format == "pdf":
            # Generate PDF file
            from fpdf import FPDF
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, request.title, ln=True, align="C")
            pdf.ln(10)
            pdf.set_font("Arial", "", 12)
            
            # Handle multi-line content
            for line in request.content.split('\n'):
                pdf.multi_cell(0, 8, line)
            
            file_path = f"/tmp/mcleuker_files/{file_id}.pdf"
            pdf.output(file_path)
            filename = f"{request.title}.pdf"
            
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": f"Unsupported format: {request.format}"
                }
            )
        
        # Return download URL
        return {
            "success": True,
            "file_id": f"{file_id}.{request.format if request.format != 'powerpoint' else 'pptx'}",
            "filename": filename,
            "download_url": f"/api/files/{file_id}.{request.format if request.format != 'powerpoint' else 'pptx'}",
            "format": request.format
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


# =============================================================================
# Export Chat to Document
# =============================================================================

class ExportChatRequest(BaseModel):
    messages: List[dict]
    title: str
    format: str  # excel, word, markdown, pdf


@app.post("/api/export/chat")
async def export_chat(request: ExportChatRequest):
    """
    Export chat conversation to a document.
    """
    try:
        os.makedirs("/tmp/mcleuker_files", exist_ok=True)
        file_id = str(uuid.uuid4())[:12]
        
        # Build content from messages
        content_lines = []
        for msg in request.messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")
            
            if role == "user":
                content_lines.append(f"**User:** {content}")
            else:
                content_lines.append(f"**McLeuker AI:** {content}")
            content_lines.append("")
        
        content = "\n".join(content_lines)
        
        # Reuse document generation
        doc_request = DocumentGenerateRequest(
            content=content,
            title=request.title,
            format=request.format
        )
        
        return await generate_document(doc_request)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )
