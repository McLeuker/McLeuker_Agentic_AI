"""
Agentic AI API Routes — FastAPI Endpoints for All Agent Capabilities
=====================================================================

Provides REST API endpoints for:
- Computer Use Agent
- Website Builder Agent
- Document Agent
- Slides Generator Agent
- Excel Agent
- Deep Research Agent

All endpoints support streaming responses for real-time updates.
"""

import asyncio
import json
import logging
import os
from typing import AsyncGenerator, Dict, List, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field
import openai

# Import all agent components
from agents.computer_use_agent import ComputerUseAgent, get_computer_use_agent
from agents.website_builder_agent import WebsiteBuilderAgent, get_website_builder
from agents.document_agent import DocumentAgent, get_document_agent
from agents.slides_agent import SlidesAgent, get_slides_agent
from agents.excel_agent import ExcelAgent, get_excel_agent
from agents.deep_research_agent import DeepResearchAgent, get_research_agent

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/agent", tags=["agentic-ai"])

# Initialize LLM client
llm_client = None
if os.getenv("KIMI_API_KEY"):
    llm_client = openai.AsyncOpenAI(
        api_key=os.getenv("KIMI_API_KEY"),
        base_url="https://api.moonshot.cn/v1"
    )
elif os.getenv("GROK_API_KEY"):
    llm_client = openai.AsyncOpenAI(
        api_key=os.getenv("GROK_API_KEY"),
        base_url="https://api.x.ai/v1"
    )


# ============================================================================
# REQUEST MODELS
# ============================================================================

class ComputerUseRequest(BaseModel):
    task: str
    starting_url: Optional[str] = None
    max_steps: int = 30


class WebsiteBuildRequest(BaseModel):
    description: str
    template: Optional[str] = None
    project_id: Optional[str] = None


class WebsiteDeployRequest(BaseModel):
    project_id: str
    platform: str = "vercel"  # vercel, netlify


class DocumentGenerateRequest(BaseModel):
    description: str
    file_type: str = "docx"  # docx, pdf
    template: Optional[str] = None
    title: Optional[str] = None


class SlidesGenerateRequest(BaseModel):
    description: str
    template: Optional[str] = None
    num_slides: Optional[int] = None
    title: Optional[str] = None


class ExcelGenerateRequest(BaseModel):
    description: str
    spreadsheet_type: Optional[str] = None
    title: Optional[str] = None
    data: Optional[Dict] = None


class DeepResearchRequest(BaseModel):
    query: str
    depth: str = "comprehensive"  # quick, standard, comprehensive
    focus_areas: Optional[List[str]] = None
    time_range: Optional[str] = None


# ============================================================================
# STREAMING HELPER
# ============================================================================

async def stream_events(generator: AsyncGenerator[Dict, None]) -> AsyncGenerator[str, None]:
    """Convert event generator to SSE format."""
    async for event in generator:
        yield f"data: {json.dumps(event)}\n\n"
    yield "data: [DONE]\n\n"


# ============================================================================
# COMPUTER USE ENDPOINTS
# ============================================================================

@router.post("/computer-use")
async def computer_use_endpoint(body: ComputerUseRequest):
    """Execute a computer automation task."""
    if not llm_client:
        raise HTTPException(status_code=500, detail="LLM client not configured")
    
    agent = get_computer_use_agent(llm_client)
    if not agent:
        raise HTTPException(status_code=503, detail="Computer Use Agent not available")
    
    import uuid
    execution_id = str(uuid.uuid4())
    
    return StreamingResponse(
        stream_events(agent.execute_task(
            task=body.task,
            execution_id=execution_id,
            max_steps=body.max_steps,
            starting_url=body.starting_url,
        )),
        media_type="text/event-stream",
    )


# ============================================================================
# WEBSITE BUILDER ENDPOINTS
# ============================================================================

@router.post("/website/build")
async def website_build_endpoint(body: WebsiteBuildRequest):
    """Build a website from description."""
    if not llm_client:
        raise HTTPException(status_code=500, detail="LLM client not configured")
    
    agent = get_website_builder(llm_client)
    if not agent:
        raise HTTPException(status_code=503, detail="Website Builder Agent not available")
    
    return StreamingResponse(
        stream_events(agent.build_website(
            description=body.description,
            template=body.template,
            project_id=body.project_id,
        )),
        media_type="text/event-stream",
    )


@router.post("/website/deploy")
async def website_deploy_endpoint(body: WebsiteDeployRequest):
    """Deploy a built website."""
    if not llm_client:
        raise HTTPException(status_code=500, detail="LLM client not configured")
    
    agent = get_website_builder(llm_client)
    if not agent:
        raise HTTPException(status_code=503, detail="Website Builder Agent not available")
    
    return StreamingResponse(
        stream_events(agent.deploy_website(
            project_id=body.project_id,
            platform=body.platform,
        )),
        media_type="text/event-stream",
    )


@router.get("/website/{project_id}")
async def get_website_project(project_id: str):
    """Get website project details."""
    if not llm_client:
        raise HTTPException(status_code=500, detail="LLM client not configured")
    
    agent = get_website_builder(llm_client)
    if not agent:
        raise HTTPException(status_code=503, detail="Website Builder Agent not available")
    
    project = agent.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project.to_dict()


# ============================================================================
# DOCUMENT AGENT ENDPOINTS
# ============================================================================

@router.post("/document/generate")
async def document_generate_endpoint(body: DocumentGenerateRequest):
    """Generate a document from description."""
    if not llm_client:
        raise HTTPException(status_code=500, detail="LLM client not configured")
    
    agent = get_document_agent(llm_client)
    if not agent:
        raise HTTPException(status_code=503, detail="Document Agent not available")
    
    return StreamingResponse(
        stream_events(agent.generate_document(
            description=body.description,
            file_type=body.file_type,
            template=body.template,
            title=body.title,
        )),
        media_type="text/event-stream",
    )


@router.get("/document/templates")
async def list_document_templates():
    """List available document templates."""
    if not llm_client:
        raise HTTPException(status_code=500, detail="LLM client not configured")
    
    agent = get_document_agent(llm_client)
    if not agent:
        raise HTTPException(status_code=503, detail="Document Agent not available")
    
    return {"templates": agent.list_templates()}


@router.get("/document/{document_id}")
async def get_document(document_id: str):
    """Get document details and download."""
    if not llm_client:
        raise HTTPException(status_code=500, detail="LLM client not configured")
    
    agent = get_document_agent(llm_client)
    if not agent:
        raise HTTPException(status_code=503, detail="Document Agent not available")
    
    document = agent.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document.to_dict()


@router.get("/document/{document_id}/download")
async def download_document(document_id: str):
    """Download a generated document."""
    if not llm_client:
        raise HTTPException(status_code=500, detail="LLM client not configured")
    
    agent = get_document_agent(llm_client)
    if not agent:
        raise HTTPException(status_code=503, detail="Document Agent not available")
    
    document = agent.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return FileResponse(
        document.file_path,
        filename=f"{document.title}.{document.file_type}",
        media_type="application/octet-stream",
    )


# ============================================================================
# SLIDES GENERATOR ENDPOINTS
# ============================================================================

@router.post("/slides/generate")
async def slides_generate_endpoint(body: SlidesGenerateRequest):
    """Generate a presentation from description."""
    if not llm_client:
        raise HTTPException(status_code=500, detail="LLM client not configured")
    
    agent = get_slides_agent(llm_client)
    if not agent:
        raise HTTPException(status_code=503, detail="Slides Agent not available")
    
    return StreamingResponse(
        stream_events(agent.generate_presentation(
            description=body.description,
            template=body.template,
            num_slides=body.num_slides,
            title=body.title,
        )),
        media_type="text/event-stream",
    )


@router.get("/slides/templates")
async def list_slides_templates():
    """List available presentation templates."""
    if not llm_client:
        raise HTTPException(status_code=500, detail="LLM client not configured")
    
    agent = get_slides_agent(llm_client)
    if not agent:
        raise HTTPException(status_code=503, detail="Slides Agent not available")
    
    return {"templates": agent.list_templates()}


@router.get("/slides/{presentation_id}/download")
async def download_presentation(presentation_id: str):
    """Download a generated presentation."""
    if not llm_client:
        raise HTTPException(status_code=500, detail="LLM client not configured")
    
    agent = get_slides_agent(llm_client)
    if not agent:
        raise HTTPException(status_code=503, detail="Slides Agent not available")
    
    presentation = agent.get_presentation(presentation_id)
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    return FileResponse(
        presentation.file_path,
        filename=f"{presentation.title}.pptx",
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )


# ============================================================================
# EXCEL AGENT ENDPOINTS
# ============================================================================

@router.post("/excel/generate")
async def excel_generate_endpoint(body: ExcelGenerateRequest):
    """Generate a spreadsheet from description."""
    if not llm_client:
        raise HTTPException(status_code=500, detail="LLM client not configured")
    
    agent = get_excel_agent(llm_client)
    if not agent:
        raise HTTPException(status_code=503, detail="Excel Agent not available")
    
    return StreamingResponse(
        stream_events(agent.generate_spreadsheet(
            description=body.description,
            spreadsheet_type=body.spreadsheet_type,
            title=body.title,
            data=body.data,
        )),
        media_type="text/event-stream",
    )


@router.get("/excel/types")
async def list_excel_types():
    """List available spreadsheet types."""
    if not llm_client:
        raise HTTPException(status_code=500, detail="LLM client not configured")
    
    agent = get_excel_agent(llm_client)
    if not agent:
        raise HTTPException(status_code=503, detail="Excel Agent not available")
    
    return {"types": agent.list_types()}


@router.get("/excel/{spreadsheet_id}/download")
async def download_spreadsheet(spreadsheet_id: str):
    """Download a generated spreadsheet."""
    if not llm_client:
        raise HTTPException(status_code=500, detail="LLM client not configured")
    
    agent = get_excel_agent(llm_client)
    if not agent:
        raise HTTPException(status_code=503, detail="Excel Agent not available")
    
    spreadsheet = agent.get_spreadsheet(spreadsheet_id)
    
    if not spreadsheet:
        raise HTTPException(status_code=404, detail="Spreadsheet not found")
    
    return FileResponse(
        spreadsheet.file_path,
        filename=f"{spreadsheet.title}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# ============================================================================
# DEEP RESEARCH ENDPOINTS
# ============================================================================

@router.post("/research/start")
async def research_start_endpoint(body: DeepResearchRequest):
    """Start a deep research task."""
    if not llm_client:
        raise HTTPException(status_code=500, detail="LLM client not configured")
    
    agent = get_research_agent(llm_client)
    if not agent:
        raise HTTPException(status_code=503, detail="Deep Research Agent not available")
    
    return StreamingResponse(
        stream_events(agent.research(
            query=body.query,
            depth=body.depth,
            focus_areas=body.focus_areas,
            time_range=body.time_range,
        )),
        media_type="text/event-stream",
    )


@router.get("/research/{report_id}")
async def get_research_report(report_id: str):
    """Get a research report."""
    if not llm_client:
        raise HTTPException(status_code=500, detail="LLM client not configured")
    
    agent = get_research_agent(llm_client)
    if not agent:
        raise HTTPException(status_code=503, detail="Deep Research Agent not available")
    
    report = agent.get_report(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report.to_dict()


# ============================================================================
# CAPABILITIES ENDPOINT
# ============================================================================

@router.get("/capabilities")
async def get_capabilities():
    """Get all available agent capabilities."""
    capabilities = {
        "agents": [
            {
                "id": "computer_use",
                "name": "Computer Use Agent",
                "description": "GUI automation and computer control with real-time screenshots",
                "endpoints": [
                    {"path": "/api/v1/agent/computer-use", "method": "POST", "streaming": True}
                ],
                "available": get_computer_use_agent(llm_client) is not None,
            },
            {
                "id": "website_builder",
                "name": "Website Builder Agent",
                "description": "End-to-end website creation and deployment",
                "endpoints": [
                    {"path": "/api/v1/agent/website/build", "method": "POST", "streaming": True},
                    {"path": "/api/v1/agent/website/deploy", "method": "POST", "streaming": True},
                    {"path": "/api/v1/agent/website/{project_id}", "method": "GET", "streaming": False},
                ],
                "available": get_website_builder(llm_client) is not None,
            },
            {
                "id": "document_agent",
                "name": "Document Agent",
                "description": "Professional document generation (DOCX, PDF)",
                "endpoints": [
                    {"path": "/api/v1/agent/document/generate", "method": "POST", "streaming": True},
                    {"path": "/api/v1/agent/document/templates", "method": "GET", "streaming": False},
                    {"path": "/api/v1/agent/document/{document_id}/download", "method": "GET", "streaming": False},
                ],
                "available": get_document_agent(llm_client) is not None,
            },
            {
                "id": "slides_agent",
                "name": "Slides Generator Agent",
                "description": "Professional presentation creation (PPTX)",
                "endpoints": [
                    {"path": "/api/v1/agent/slides/generate", "method": "POST", "streaming": True},
                    {"path": "/api/v1/agent/slides/templates", "method": "GET", "streaming": False},
                    {"path": "/api/v1/agent/slides/{presentation_id}/download", "method": "GET", "streaming": False},
                ],
                "available": get_slides_agent(llm_client) is not None,
            },
            {
                "id": "excel_agent",
                "name": "Excel Agent",
                "description": "Advanced spreadsheet creation and analysis (XLSX)",
                "endpoints": [
                    {"path": "/api/v1/agent/excel/generate", "method": "POST", "streaming": True},
                    {"path": "/api/v1/agent/excel/types", "method": "GET", "streaming": False},
                    {"path": "/api/v1/agent/excel/{spreadsheet_id}/download", "method": "GET", "streaming": False},
                ],
                "available": get_excel_agent(llm_client) is not None,
            },
            {
                "id": "deep_research",
                "name": "Deep Research Agent",
                "description": "Comprehensive multi-source research",
                "endpoints": [
                    {"path": "/api/v1/agent/research/start", "method": "POST", "streaming": True},
                    {"path": "/api/v1/agent/research/{report_id}", "method": "GET", "streaming": False},
                ],
                "available": get_research_agent(llm_client) is not None,
            },
        ],
        "llm_configured": llm_client is not None,
    }
    
    return capabilities


# Export router
__all__ = ["router"]
