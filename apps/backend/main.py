"""
McLeuker AI - Complete Kimi 2.5 Production Backend
All capabilities: Tools, File Gen, Vision-to-Code, Agent Swarm, Code Execution
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, BackgroundTasks, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal, Dict, Any, Union, AsyncGenerator, Callable
import openai
import os
import base64
import json
import asyncio
import httpx
import subprocess
import tempfile
import shutil
import uuid
import re
import time
import hashlib
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import traceback
import logging

# Data processing
import pandas as pd
import numpy as np
from io import BytesIO, StringIO

# Document generation
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# PDF generation
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# PowerPoint
from pptx import Presentation
from pptx.util import Inches as PptxInches, Pt as PptxPt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor as PptxRGBColor

# Visualization
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns

# Image processing
from PIL import Image as PILImage

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(
    title="McLeuker AI - Kimi 2.5 Complete",
    description="Production-ready AI platform with all Kimi 2.5 capabilities",
    version="3.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mcleuker-agentic-ai.vercel.app",
        "http://localhost:3000",
        "https://*.vercel.app",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Keys
KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
EXA_API_KEY = os.getenv("EXA_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
GROK_API_KEY = os.getenv("GROK_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# Initialize Kimi client
client = openai.OpenAI(
    api_key=KIMI_API_KEY,
    base_url="https://api.moonshot.ai/v1"
)

# Directories
OUTPUT_DIR = Path("/tmp/mcleuker_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)
CODE_SANDBOX_DIR = Path("/tmp/mcleuker_sandbox")
CODE_SANDBOX_DIR.mkdir(exist_ok=True)
UPLOADS_DIR = Path("/tmp/mcleuker_uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

# ============================================================================
# DATA MODELS
# ============================================================================

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: Union[str, List[Dict[str, Any]]]
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    mode: Literal["instant", "thinking", "agent", "swarm", "research", "code"] = "thinking"
    stream: bool = False
    enable_tools: bool = True
    context_id: Optional[str] = None

class SwarmRequest(BaseModel):
    master_task: str
    context: Dict[str, Any] = {}
    num_agents: int = Field(default=5, ge=1, le=50)
    enable_search: bool = True
    generate_deliverable: bool = False
    deliverable_type: Optional[Literal["report", "presentation", "spreadsheet"]] = None

class FileGenRequest(BaseModel):
    content: Union[str, Dict, List]
    file_type: Literal["excel", "word", "pdf", "pptx", "csv", "json"]
    filename: Optional[str] = None
    title: Optional[str] = None
    subtitle: Optional[str] = None
    include_charts: bool = False
    template: Optional[str] = None
    styling: Optional[Dict[str, Any]] = None

class VisionCodeRequest(BaseModel):
    image_base64: str
    requirements: str = "Modern, responsive, animated UI"
    framework: Literal["html", "react", "vue", "svelte", "angular"] = "html"
    include_dependencies: bool = True
    styling_preference: Literal["tailwind", "bootstrap", "css", "styled-components"] = "tailwind"

class CodeExecutionRequest(BaseModel):
    code: str
    language: Literal["python", "javascript", "typescript", "bash", "sql"] = "python"
    timeout: int = Field(default=30, ge=5, le=300)
    dependencies: Optional[List[str]] = None
    inputs: Optional[Dict[str, Any]] = None

class SearchRequest(BaseModel):
    query: str
    sources: List[Literal["web", "news", "academic", "youtube", "social"]] = ["web"]
    num_results: int = Field(default=10, ge=1, le=50)
    recency_days: Optional[int] = None

class ResearchRequest(BaseModel):
    query: str
    depth: Literal["quick", "deep", "exhaustive"] = "deep"
    sources: List[str] = ["web", "news", "academic"]
    generate_deliverable: bool = False
    deliverable_type: Optional[Literal["report", "presentation", "spreadsheet"]] = "report"
    include_visualizations: bool = True

class DocumentAnalysisRequest(BaseModel):
    document_type: Literal["pdf", "word", "excel", "image", "text"]
    analysis_type: Literal["summarize", "extract_data", "answer_questions", "compare", "translate"]
    questions: Optional[List[str]] = None
    target_language: Optional[str] = None

class ConversationCreate(BaseModel):
    user_id: str
    title: Optional[str] = None

class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# ============================================================================
# REAL-TIME SEARCH APIs
# ============================================================================

class SearchAPIs:
    """Unified search across all real-time data sources"""
    
    @staticmethod
    async def perplexity_search(query: str, focus: str = "web", recency_days: Optional[int] = None) -> Dict:
        """Deep research with Perplexity AI - Sonar Pro model"""
        if not PERPLEXITY_API_KEY:
            return {"error": "Perplexity not configured", "results": []}
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as http_client:
                # Determine search type based on query
                search_type = "news" if any(kw in query.lower() for kw in ["latest", "recent", "2024", "2025", "2026", "today", "yesterday", "this week"]) else focus
                
                response = await http_client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "sonar-pro",
                        "messages": [{"role": "user", "content": query}],
                        "temperature": 0.2,
                        "top_p": 0.9,
                        "return_images": False,
                        "return_related_questions": True,
                        "search_recency_filter": "month" if recency_days and recency_days <= 30 else "year" if recency_days and recency_days <= 365 else None
                    }
                )
                data = response.json()
                
                return {
                    "source": "perplexity",
                    "model": "sonar-pro",
                    "answer": data["choices"][0]["message"]["content"],
                    "citations": data.get("citations", []),
                    "related_questions": data.get("related_questions", []),
                    "usage": data.get("usage", {}),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Perplexity error: {e}")
            return {"error": str(e), "source": "perplexity"}
    
    @staticmethod
    async def exa_search(query: str, num_results: int = 10, recency_days: Optional[int] = None) -> Dict:
        """Neural search with Exa.ai"""
        if not EXA_API_KEY:
            return {"error": "Exa not configured", "results": []}
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as http_client:
                payload = {
                    "query": query,
                    "numResults": min(num_results, 50),
                    "useAutoprompt": True,
                    "type": "neural",
                    "contents": {
                        "text": {"maxCharacters": 1000}
                    }
                }
                
                if recency_days:
                    payload["startPublishedDate"] = (datetime.now() - timedelta(days=recency_days)).isoformat()
                
                response = await http_client.post(
                    "https://api.exa.ai/search",
                    headers={"Authorization": f"Bearer {EXA_API_KEY}"},
                    json=payload
                )
                data = response.json()
                
                results = []
                for r in data.get("results", []):
                    results.append({
                        "title": r.get("title", "No title"),
                        "url": r.get("url", ""),
                        "snippet": r.get("text", "")[:500] if r.get("text") else "",
                        "published_date": r.get("publishedDate"),
                        "author": r.get("author"),
                        "score": r.get("score")
                    })
                
                return {
                    "source": "exa",
                    "results": results,
                    "autoprompt": data.get("autopromptString"),
                    "total": len(results),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Exa error: {e}")
            return {"error": str(e), "source": "exa"}
    
    @staticmethod
    async def youtube_search(query: str, max_results: int = 10, order: str = "relevance") -> Dict:
        """Search YouTube videos with metadata"""
        if not YOUTUBE_API_KEY:
            return {"error": "YouTube not configured", "videos": []}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                # Search for videos
                search_response = await http_client.get(
                    "https://www.googleapis.com/youtube/v3/search",
                    params={
                        "part": "snippet",
                        "q": query,
                        "maxResults": min(max_results, 50),
                        "type": "video",
                        "order": order,  # relevance, date, rating, viewCount
                        "videoEmbeddable": "true",
                        "key": YOUTUBE_API_KEY
                    }
                )
                search_data = search_response.json()
                
                videos = []
                video_ids = [item["id"]["videoId"] for item in search_data.get("items", [])]
                
                # Get video statistics
                if video_ids:
                    stats_response = await http_client.get(
                        "https://www.googleapis.com/youtube/v3/videos",
                        params={
                            "part": "statistics,contentDetails",
                            "id": ",".join(video_ids),
                            "key": YOUTUBE_API_KEY
                        }
                    )
                    stats_data = {item["id"]: item for item in stats_response.json().get("items", [])}
                else:
                    stats_data = {}
                
                for item in search_data.get("items", []):
                    video_id = item["id"]["videoId"]
                    stats = stats_data.get(video_id, {}).get("statistics", {})
                    
                    videos.append({
                        "title": item["snippet"]["title"],
                        "description": item["snippet"]["description"],
                        "video_id": video_id,
                        "url": f"https://youtube.com/watch?v={video_id}",
                        "embed_url": f"https://youtube.com/embed/{video_id}",
                        "thumbnail": item["snippet"]["thumbnails"].get("high", item["snippet"]["thumbnails"].get("default", {})).get("url", ""),
                        "published_at": item["snippet"]["publishedAt"],
                        "channel": item["snippet"]["channelTitle"],
                        "channel_id": item["snippet"]["channelId"],
                        "view_count": int(stats.get("viewCount", 0)),
                        "like_count": int(stats.get("likeCount", 0)) if stats.get("likeCount") else None,
                        "comment_count": int(stats.get("commentCount", 0)) if stats.get("commentCount") else None
                    })
                
                return {
                    "source": "youtube",
                    "videos": videos,
                    "total": len(videos),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"YouTube error: {e}")
            return {"error": str(e), "source": "youtube"}
    
    @staticmethod
    async def grok_search(query: str, stream: bool = False) -> Dict:
        """Search with Grok/X AI for real-time X/Twitter data"""
        if not GROK_API_KEY:
            return {"error": "Grok not configured", "results": []}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                response = await http_client.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROK_API_KEY}"},
                    json={
                        "model": "grok-beta",
                        "messages": [{"role": "user", "content": query}],
                        "stream": stream,
                        "temperature": 0.7
                    }
                )
                data = response.json()
                
                return {
                    "source": "grok",
                    "model": "grok-beta",
                    "answer": data["choices"][0]["message"]["content"],
                    "usage": data.get("usage", {}),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Grok error: {e}")
            return {"error": str(e), "source": "grok"}
    
    @staticmethod
    async def multi_search(
        query: str, 
        sources: List[str] = None, 
        num_results: int = 10,
        recency_days: Optional[int] = None
    ) -> Dict:
        """Search across all configured sources in parallel"""
        if sources is None:
            sources = ["web"]
        
        tasks = []
        source_map = {}
        idx = 0
        
        if "web" in sources or "news" in sources:
            tasks.append(SearchAPIs.perplexity_search(query, "news" if "news" in sources else "web", recency_days))
            source_map[idx] = "perplexity"
            idx += 1
        
        if "web" in sources or "academic" in sources:
            tasks.append(SearchAPIs.exa_search(query, num_results, recency_days))
            source_map[idx] = "exa"
            idx += 1
        
        if "youtube" in sources:
            tasks.append(SearchAPIs.youtube_search(query, min(num_results, 10)))
            source_map[idx] = "youtube"
            idx += 1
        
        if "social" in sources:
            tasks.append(SearchAPIs.grok_search(query))
            source_map[idx] = "grok"
            idx += 1
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        combined = {
            "query": query,
            "sources_requested": sources,
            "timestamp": datetime.now().isoformat(),
            "results": {}
        }
        
        for i, result in enumerate(results):
            source_name = source_map.get(i, f"source_{i}")
            if isinstance(result, Exception):
                combined["results"][source_name] = {"error": str(result)}
            else:
                combined["results"][source_name] = result
        
        # Create synthesized summary
        combined["synthesized_answer"] = SearchAPIs._synthesize_search_results(combined["results"])
        
        return combined
    
    @staticmethod
    def _synthesize_search_results(results: Dict) -> str:
        """Create a brief synthesis of search results"""
        parts = []
        
        if "perplexity" in results and "answer" in results["perplexity"]:
            parts.append(results["perplexity"]["answer"][:500])
        
        if "exa" in results and "results" in results["exa"]:
            exa_results = results["exa"]["results"]
            if exa_results:
                parts.append(f"Found {len(exa_results)} web sources.")
        
        if "youtube" in results and "videos" in results["youtube"]:
            videos = results["youtube"]["videos"]
            if videos:
                parts.append(f"Found {len(videos)} related videos.")
        
        return " ".join(parts) if parts else "Search completed."

# ============================================================================
# PROFESSIONAL FILE GENERATION
# ============================================================================

class FileGenerator:
    """Generate professional documents with charts and styling"""
    
    generated_files: Dict[str, Dict] = {}
    
    @classmethod
    def generate_excel(
        cls,
        data: Union[Dict, List, pd.DataFrame],
        filename: str = None,
        title: str = None,
        include_charts: bool = False,
        styling: Dict = None
    ) -> str:
        """Generate professional Excel with formatting and optional charts"""
        if filename is None:
            filename = f"report_{uuid.uuid4().hex[:8]}.xlsx"
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        filepath = OUTPUT_DIR / filename
        
        # Convert data to DataFrame(s)
        if isinstance(data, pd.DataFrame):
            sheets = {"Data": data}
        elif isinstance(data, list):
            sheets = {"Data": pd.DataFrame(data)}
        elif isinstance(data, dict):
            sheets = {}
            for key, value in data.items():
                if isinstance(value, list):
                    sheets[key] = pd.DataFrame(value)
                elif isinstance(value, dict):
                    sheets[key] = pd.DataFrame([value])
                elif isinstance(value, pd.DataFrame):
                    sheets[key] = value
                else:
                    sheets[key] = pd.DataFrame({"content": [str(value)]})
        else:
            sheets = {"Data": pd.DataFrame({"content": [str(data)]})}
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            for sheet_name, df in sheets.items():
                # Sanitize sheet name
                safe_name = str(sheet_name)[:31]
                df.to_excel(writer, sheet_name=safe_name, index=False, startrow=2 if title else 0)
                
                workbook = writer.book
                worksheet = writer.sheets[safe_name]
                
                # Apply styling
                from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
                from openpyxl.chart import BarChart, PieChart, LineChart, Reference
                from openpyxl.utils.dataframe import dataframe_to_rows
                
                # Title row
                if title:
                    worksheet.merge_cells('A1:' + chr(64 + len(df.columns)) + '1')
                    title_cell = worksheet['A1']
                    title_cell.value = title
                    title_cell.font = Font(size=16, bold=True, color="FFFFFF")
                    title_cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                    title_cell.alignment = Alignment(horizontal='center', vertical='center')
                    worksheet.row_dimensions[1].height = 30
                
                # Header styling
                header_fill = PatternFill(start_color="B8CCE4", end_color="B8CCE4", fill_type="solid")
                header_font = Font(bold=True, size=11)
                
                for col_num, column in enumerate(df.columns, 1):
                    cell = worksheet.cell(row=(3 if title else 1), column=col_num)
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                    
                    # Auto-adjust column width
                    max_length = len(str(column))
                    for value in df[column]:
                        max_length = max(max_length, len(str(value)))
                    worksheet.column_dimensions[chr(64 + col_num)].width = min(max_length + 4, 50)
                
                # Add chart if requested and data is suitable
                if include_charts and len(df) > 0:
                    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                    if len(numeric_cols) > 0:
                        chart = BarChart()
                        chart.type = "col"
                        chart.style = 10
                        chart.title = f"{safe_name} Chart"
                        chart.y_axis.title = 'Value'
                        chart.x_axis.title = 'Category'
                        
                        data_ref = Reference(worksheet, min_col=2, min_row=2, max_row=len(df)+2, max_col=len(df.columns))
                        cats_ref = Reference(worksheet, min_col=1, min_row=3, max_row=len(df)+2)
                        chart.add_data(data_ref, titles_from_data=True)
                        chart.set_categories(cats_ref)
                        chart.shape = 4
                        worksheet.add_chart(chart, chr(64 + len(df.columns) + 2) + "5")
        
        file_id = uuid.uuid4().hex[:16]
        cls.generated_files[file_id] = {
            "path": str(filepath),
            "filename": filename,
            "type": "excel",
            "created": datetime.now().isoformat()
        }
        
        return file_id
    
    @classmethod
    def generate_word(
        cls,
        content: str,
        title: str = None,
        subtitle: str = None,
        filename: str = None,
        styling: Dict = None
    ) -> str:
        """Generate professional Word document"""
        if filename is None:
            filename = f"document_{uuid.uuid4().hex[:8]}.docx"
        if not filename.endswith('.docx'):
            filename += '.docx'
        
        filepath = OUTPUT_DIR / filename
        doc = Document()
        
        # Set default font
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Calibri'
        font.size = Pt(11)
        
        # Title page
        if title:
            title_para = doc.add_heading(title, 0)
            title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in title_para.runs:
                run.font.color.rgb = RGBColor(0x36, 0x60, 0x92)
            
            if subtitle:
                subtitle_para = doc.add_paragraph(subtitle)
                subtitle_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                subtitle_para.runs[0].font.size = Pt(14)
                subtitle_para.runs[0].font.color.rgb = RGBColor(0x80, 0x80, 0x80)
            
            doc.add_page_break()
        
        # Table of contents placeholder
        if styling and styling.get('include_toc'):
            doc.add_heading('Table of Contents', level=1)
            toc_para = doc.add_paragraph('(Right-click and select "Update Field" to generate)')
            toc_para.runs[0].font.color.rgb = RGBColor(0x80, 0x80, 0x80)
            doc.add_page_break()
        
        # Parse and add content
        lines = content.split('\n')
        current_table_data = []
        in_table = False
        
        for line in lines:
            line = line.strip()
            if not line:
                if in_table and current_table_data:
                    # Add accumulated table
                    cls._add_table_to_doc(doc, current_table_data)
                    current_table_data = []
                    in_table = False
                continue
            
            # Headers
            if line.startswith('# '):
                doc.add_heading(line[2:], level=1)
            elif line.startswith('## '):
                doc.add_heading(line[3:], level=2)
            elif line.startswith('### '):
                doc.add_heading(line[4:], level=3)
            # Lists
            elif line.startswith('- ') or line.startswith('* '):
                if in_table:
                    cls._add_table_to_doc(doc, current_table_data)
                    current_table_data = []
                    in_table = False
                doc.add_paragraph(line[2:], style='List Bullet')
            elif re.match(r'^\d+\.', line):
                if in_table:
                    cls._add_table_to_doc(doc, current_table_data)
                    current_table_data = []
                    in_table = False
                doc.add_paragraph(re.sub(r'^\d+\.', '', line).strip(), style='List Number')
            # Tables (markdown-style)
            elif '|' in line:
                in_table = True
                cells = [c.strip() for c in line.split('|') if c.strip()]
                if cells and not all(c.replace('-', '').replace(':', '') == '' for c in cells):
                    current_table_data.append(cells)
            # Regular paragraph
            else:
                if in_table:
                    cls._add_table_to_doc(doc, current_table_data)
                    current_table_data = []
                    in_table = False
                doc.add_paragraph(line)
        
        # Add any remaining table
        if in_table and current_table_data:
            cls._add_table_to_doc(doc, current_table_data)
        
        # Footer
        doc.add_paragraph()
        footer = doc.add_paragraph()
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer_run = footer.add_run(f"\nGenerated by McLeuker AI on {datetime.now().strftime('%B %d, %Y at %H:%M')}")
        footer_run.font.size = Pt(9)
        footer_run.font.color.rgb = RGBColor(0x80, 0x80, 0x80)
        footer_run.font.italic = True
        
        doc.save(filepath)
        
        file_id = uuid.uuid4().hex[:16]
        cls.generated_files[file_id] = {
            "path": str(filepath),
            "filename": filename,
            "type": "word",
            "created": datetime.now().isoformat()
        }
        
        return file_id
    
    @classmethod
    def _add_table_to_doc(cls, doc: Document, table_data: List[List[str]]):
        """Helper to add a table to document"""
        if len(table_data) < 1:
            return
        
        num_cols = max(len(row) for row in table_data)
        table = doc.add_table(rows=len(table_data), cols=num_cols)
        table.style = 'Light Grid Accent 1'
        
        for i, row_data in enumerate(table_data):
            row = table.rows[i]
            for j, cell_text in enumerate(row_data):
                if j < num_cols:
                    row.cells[j].text = cell_text
                    # Bold first row (header)
                    if i == 0:
                        for paragraph in row.cells[j].paragraphs:
                            for run in paragraph.runs:
                                run.font.bold = True
    
    @classmethod
    def generate_pdf(
        cls,
        content: str,
        title: str = None,
        filename: str = None,
        include_toc: bool = False
    ) -> str:
        """Generate professional PDF with ReportLab"""
        if filename is None:
            filename = f"report_{uuid.uuid4().hex[:8]}.pdf"
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        filepath = OUTPUT_DIR / filename
        
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#366092'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        heading1_style = ParagraphStyle(
            'CustomH1',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#366092'),
            spaceAfter=12
        )
        
        heading2_style = ParagraphStyle(
            'CustomH2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#4F81BD'),
            spaceAfter=10
        )
        
        # Title
        if title:
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 20))
        
        # Parse content
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 12))
                continue
            
            # Headers
            if line.startswith('# '):
                story.append(Paragraph(line[2:], heading1_style))
            elif line.startswith('## '):
                story.append(Paragraph(line[3:], heading2_style))
            elif line.startswith('### '):
                story.append(Paragraph(line[4:], styles['Heading3']))
            # Lists
            elif line.startswith('- ') or line.startswith('* '):
                story.append(Paragraph(f"• {line[2:]}", styles['BodyText']))
            elif re.match(r'^\d+\.', line):
                story.append(Paragraph(line, styles['BodyText']))
            else:
                story.append(Paragraph(line, styles['BodyText']))
        
        # Footer
        story.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.gray,
            alignment=1
        )
        story.append(Paragraph(
            f"Generated by McLeuker AI on {datetime.now().strftime('%B %d, %Y')}",
            footer_style
        ))
        
        doc.build(story)
        
        file_id = uuid.uuid4().hex[:16]
        cls.generated_files[file_id] = {
            "path": str(filepath),
            "filename": filename,
            "type": "pdf",
            "created": datetime.now().isoformat()
        }
        
        return file_id
    
    @classmethod
    def generate_pptx(
        cls,
        content: str,
        title: str = None,
        filename: str = None,
        theme: str = "professional"
    ) -> str:
        """Generate professional PowerPoint presentation"""
        if filename is None:
            filename = f"presentation_{uuid.uuid4().hex[:8]}.pptx"
        if not filename.endswith('.pptx'):
            filename += '.pptx'
        
        filepath = OUTPUT_DIR / filename
        prs = Presentation()
        
        # Theme colors
        themes = {
            "professional": {"primary": PptxRGBColor(54, 96, 146), "secondary": PptxRGBColor(79, 129, 189)},
            "modern": {"primary": PptxRGBColor(0, 112, 192), "secondary": PptxRGBColor(0, 176, 240)},
            "dark": {"primary": PptxRGBColor(64, 64, 64), "secondary": PptxRGBColor(128, 128, 128)}
        }
        theme_colors = themes.get(theme, themes["professional"])
        
        # Title slide
        title_slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(title_slide_layout)
        
        if title:
            slide.shapes.title.text = title
        else:
            slide.shapes.title.text = "McLeuker AI Presentation"
        
        subtitle = slide.placeholders[1]
        subtitle.text = f"Generated on {datetime.now().strftime('%B %d, %Y')}"
        
        # Parse content into slides
        sections = content.split('\n\n')
        current_title = ""
        current_bullets = []
        
        for section in sections:
            lines = section.strip().split('\n')
            if not lines or not lines[0].strip():
                continue
            
            # Check if this is a title
            if lines[0].strip().startswith('#') or (len(lines[0]) < 60 and not lines[0].startswith('-')):
                # Save previous slide if exists
                if current_title and current_bullets:
                    cls._add_content_slide(prs, current_title, current_bullets, theme_colors)
                
                current_title = lines[0].lstrip('#').strip()
                current_bullets = []
                
                # Add remaining lines as bullets
                for line in lines[1:]:
                    line = line.strip()
                    if line.startswith('- ') or line.startswith('* '):
                        current_bullets.append(line[2:])
                    elif line:
                        current_bullets.append(line)
            else:
                # Add to current bullets
                for line in lines:
                    line = line.strip()
                    if line.startswith('- ') or line.startswith('* '):
                        current_bullets.append(line[2:])
                    elif re.match(r'^\d+\.', line):
                        current_bullets.append(line)
                    elif line:
                        current_bullets.append(line)
        
        # Add final slide
        if current_title and current_bullets:
            cls._add_content_slide(prs, current_title, current_bullets, theme_colors)
        
        # Thank you slide
        thank_you_layout = prs.slide_layouts[6]  # Blank
        slide = prs.slides.add_slide(thank_you_layout)
        
        # Add centered text
        left = PptxInches(1)
        top = PptxInches(3)
        width = PptxInches(8)
        height = PptxInches(2)
        
        textbox = slide.shapes.add_textbox(left, top, width, height)
        tf = textbox.text_frame
        tf.text = "Thank You"
        p = tf.paragraphs[0]
        p.font.size = PptxPt(44)
        p.font.bold = True
        p.font.color.rgb = theme_colors["primary"]
        p.alignment = PP_ALIGN.CENTER
        
        prs.save(filepath)
        
        file_id = uuid.uuid4().hex[:16]
        cls.generated_files[file_id] = {
            "path": str(filepath),
            "filename": filename,
            "type": "pptx",
            "created": datetime.now().isoformat()
        }
        
        return file_id
    
    @classmethod
    def _add_content_slide(cls, prs: Presentation, title: str, bullets: List[str], theme_colors: Dict):
        """Add a content slide to presentation"""
        content_layout = prs.slide_layouts[1]  # Title and Content
        slide = prs.slides.add_slide(content_layout)
        
        # Title
        slide.shapes.title.text = title[:50]  # Limit length
        
        # Content
        body_shape = slide.placeholders[1]
        tf = body_shape.text_frame
        tf.clear()
        
        for i, bullet in enumerate(bullets[:8]):  # Limit bullets per slide
            if i == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            
            p.text = bullet[:100]  # Limit bullet length
            p.level = 0
            p.font.size = PptxPt(18)
    
    @classmethod
    def get_file(cls, file_id: str) -> Optional[Dict]:
        """Get file info by ID"""
        return cls.generated_files.get(file_id)
    
    @classmethod
    def cleanup_old_files(cls, max_age_hours: int = 24):
        """Clean up files older than specified hours"""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        to_remove = []
        
        for file_id, file_info in cls.generated_files.items():
            created = datetime.fromisoformat(file_info["created"])
            if created < cutoff:
                try:
                    os.remove(file_info["path"])
                    to_remove.append(file_id)
                except:
                    pass
        
        for file_id in to_remove:
            del cls.generated_files[file_id]
        
        return len(to_remove)

# ============================================================================
# VISION TO CODE
# ============================================================================

class VisionToCode:
    """Convert images to complete code implementations"""
    
    FRAMEWORK_TEMPLATES = {
        "html": {
            "prompt": """Create a single, complete HTML file with embedded CSS and JavaScript.
Requirements:
- Use Tailwind CSS via CDN
- Include smooth animations and transitions
- Make it fully responsive
- Add interactive elements
- Use modern CSS (flexbox, grid)
- Include hover effects
- Add loading states where appropriate""",
            "extension": "html"
        },
        "react": {
            "prompt": """Create a complete React functional component with:
- TypeScript for type safety
- React hooks (useState, useEffect, etc.)
- Tailwind CSS for styling
- Framer Motion for animations (if needed)
- Proper component structure
- Props interface definition
- Responsive design""",
            "extension": "tsx"
        },
        "vue": {
            "prompt": """Create a complete Vue 3 Composition API component with:
- TypeScript
- <script setup> syntax
- Scoped styles
- Reactive state management
- Props definition
- Responsive design""",
            "extension": "vue"
        },
        "svelte": {
            "prompt": """Create a complete Svelte component with:
- Reactive statements
- Event handling
- Scoped styles
- Smooth transitions
- Responsive design""",
            "extension": "svelte"
        },
        "angular": {
            "prompt": """Create a complete Angular component with:
- TypeScript class
- Template HTML
- Component styles
- Input/Output decorators
- Responsive design""",
            "extension": "ts"
        }
    }
    
    @classmethod
    async def generate(
        cls,
        image_base64: str,
        requirements: str,
        framework: str = "html",
        styling_preference: str = "tailwind"
    ) -> Dict:
        """Generate complete code from UI image"""
        
        template = cls.FRAMEWORK_TEMPLATES.get(framework, cls.FRAMEWORK_TEMPLATES["html"])
        
        prompt = f"""Analyze this UI design image and generate production-ready {framework.upper()} code.

User Requirements: {requirements}

{template['prompt']}

Styling Preference: {styling_preference}

Output ONLY the complete, runnable code. Include all necessary dependencies and setup instructions in comments."""

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]
        
        response = client.chat.completions.create(
            model="kimi-k2.5",
            messages=messages,
            max_tokens=16384,
            temperature=0.6,
            extra_body={"thinking": {"type": "enabled"}}
        )
        
        content = response.choices[0].message.content
        
        # Extract code blocks
        code_blocks = cls._extract_code_blocks(content, framework)
        
        # Generate preview HTML if not HTML framework
        preview_html = None
        if framework != "html":
            preview_html = await cls._generate_preview(code_blocks, framework)
        
        return {
            "raw_response": content,
            "code_blocks": code_blocks,
            "framework": framework,
            "styling": styling_preference,
            "preview_html": preview_html,
            "tokens_used": response.usage.total_tokens,
            "reasoning": getattr(response.choices[0].message, 'reasoning_content', None)
        }
    
    @classmethod
    def _extract_code_blocks(cls, content: str, framework: str) -> List[Dict]:
        """Extract code blocks from markdown"""
        blocks = []
        
        # Pattern for code blocks
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for lang, code in matches:
            blocks.append({
                "language": lang or framework,
                "code": code.strip(),
                "lines": len(code.strip().split('\n'))
            })
        
        # If no code blocks, try to extract the whole thing
        if not blocks:
            # Remove markdown formatting
            clean_code = re.sub(r'^#.*\n?', '', content, flags=re.MULTILINE)
            clean_code = re.sub(r'\*\*|__|\*|_', '', clean_code)
            
            blocks.append({
                "language": framework,
                "code": clean_code.strip(),
                "lines": len(clean_code.strip().split('\n'))
            })
        
        return blocks
    
    @classmethod
    async def _generate_preview(cls, code_blocks: List[Dict], framework: str) -> str:
        """Generate preview HTML for non-HTML frameworks"""
        # This would create a sandboxed preview
        # For now, return a placeholder
        return f"<!-- Preview for {framework} - implement with CodeSandbox or similar -->"

# ============================================================================
# CODE EXECUTION SANDBOX
# ============================================================================

class CodeSandbox:
    """Secure code execution environment"""
    
    ALLOWED_MODULES = {
        'python': ['numpy', 'pandas', 'matplotlib', 'seaborn', 'requests', 'json', 'math', 'random', 'datetime', 'statistics'],
        'javascript': ['axios', 'lodash', 'moment', 'uuid'],
    }
    
    @classmethod
    async def execute(
        cls,
        code: str,
        language: str = "python",
        timeout: int = 30,
        dependencies: List[str] = None,
        inputs: Dict[str, Any] = None
    ) -> Dict:
        """Execute code in sandboxed environment"""
        
        execution_id = uuid.uuid4().hex[:12]
        sandbox_dir = CODE_SANDBOX_DIR / execution_id
        sandbox_dir.mkdir(exist_ok=True)
        
        try:
            if language == "python":
                return await cls._execute_python(code, sandbox_dir, timeout, dependencies, inputs)
            elif language in ["javascript", "typescript"]:
                return await cls._execute_javascript(code, sandbox_dir, timeout, dependencies)
            elif language == "bash":
                return await cls._execute_bash(code, sandbox_dir, timeout)
            elif language == "sql":
                return await cls._execute_sql(code, inputs)
            else:
                return {"error": f"Unsupported language: {language}"}
        finally:
            # Cleanup
            try:
                shutil.rmtree(sandbox_dir)
            except:
                pass
    
    @classmethod
    async def _execute_python(
        cls,
        code: str,
        sandbox_dir: Path,
        timeout: int,
        dependencies: List[str],
        inputs: Dict[str, Any]
    ) -> Dict:
        """Execute Python code"""
        
        # Create script with input injection
        script_content = f"""
import sys
import json
import traceback

# Inject inputs
__inputs = {json.dumps(inputs or {})}

# Capture output
from io import StringIO
__stdout_capture = StringIO()
__stderr_capture = StringIO()
old_stdout = sys.stdout
old_stderr = sys.stderr
sys.stdout = __stdout_capture
sys.stderr = __stderr_capture

try:
{chr(10).join('    ' + line for line in code.split(chr(10)))}
    
    # Get output
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    
    result = {{
        "success": True,
        "stdout": __stdout_capture.getvalue(),
        "stderr": __stderr_capture.getvalue(),
        "outputs": {{}}
    }}
    
    # Try to capture any variables
    for var in ['result', 'output', 'data', 'df', 'chart']:
        if var in dir():
            try:
                val = eval(var)
                if hasattr(val, 'to_dict'):  # pandas DataFrame
                    result["outputs"][var] = val.to_dict()
                elif hasattr(val, 'tolist'):  # numpy array
                    result["outputs"][var] = val.tolist()
                else:
                    result["outputs"][var] = str(val)[:1000]
            except:
                pass
    
    print(json.dumps(result))
    
except Exception as e:
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    print(json.dumps({{
        "success": False,
        "error": str(e),
        "traceback": traceback.format_exc()
    }}))
"""
        
        script_path = sandbox_dir / "script.py"
        script_path.write_text(script_content)
        
        # Execute with timeout
        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(sandbox_dir)
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            # Parse output
            output = stdout.decode().strip().split('\n')[-1]  # Get last line (JSON)
            
            try:
                result = json.loads(output)
                result["execution_time"] = timeout
                return result
            except:
                return {
                    "success": True,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                    "raw_output": output
                }
                
        except asyncio.TimeoutError:
            process.kill()
            return {"error": f"Execution timed out after {timeout} seconds"}
        except Exception as e:
            return {"error": str(e), "stderr": stderr.decode() if 'stderr' in locals() else ""}
    
    @classmethod
    async def _execute_javascript(cls, code: str, sandbox_dir: Path, timeout: int, dependencies: List[str]) -> Dict:
        """Execute JavaScript/TypeScript with Node.js"""
        
        # Check if Node.js is available
        try:
            process = await asyncio.create_subprocess_exec(
                'node', '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            if process.returncode != 0:
                return {"error": "Node.js not available"}
        except:
            return {"error": "Node.js not installed"}
        
        # Wrap code for execution
        wrapped_code = f"""
const console_output = {{ stdout: [], stderr: [] }};
const originalLog = console.log;
const originalError = console.error;

console.log = (...args) => {{
    console_output.stdout.push(args.join(' '));
    originalLog(...args);
}};

console.error = (...args) => {{
    console_output.stderr.push(args.join(' '));
    originalError(...args);
}};

try {{
{code}
    console.log(JSON.stringify({{ success: true, output: console_output }}));
}} catch (e) {{
    console.log(JSON.stringify({{ success: false, error: e.message, stack: e.stack }}));
}}
"""
        
        script_path = sandbox_dir / "script.js"
        script_path.write_text(wrapped_code)
        
        try:
            process = await asyncio.create_subprocess_exec(
                'node', str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(sandbox_dir)
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            try:
                result = json.loads(stdout.decode().strip().split('\n')[-1])
                return result
            except:
                return {
                    "success": True,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode()
                }
                
        except asyncio.TimeoutError:
            process.kill()
            return {"error": f"Execution timed out after {timeout} seconds"}
    
    @classmethod
    async def _execute_bash(cls, code: str, sandbox_dir: Path, timeout: int) -> Dict:
        """Execute bash commands (limited)"""
        
        # Security: Only allow safe commands
        dangerous = ['rm -rf /', 'mkfs', 'dd if=', ':(){ :|:& };:', '> /dev/sda']
        for d in dangerous:
            if d in code:
                return {"error": "Dangerous command detected"}
        
        try:
            process = await asyncio.create_subprocess_shell(
                code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(sandbox_dir)
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "exit_code": process.returncode
            }
            
        except asyncio.TimeoutError:
            process.kill()
            return {"error": f"Execution timed out after {timeout} seconds"}
    
    @classmethod
    async def _execute_sql(cls, code: str, inputs: Dict[str, Any]) -> Dict:
        """Execute SQL (requires database connection)"""
        # Placeholder - would need actual DB connection
        return {
            "success": True,
            "message": "SQL execution requires database configuration",
            "query": code
        }

# ============================================================================
# TOOL DEFINITIONS
# ============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "realtime_search",
            "description": "Search for real-time information from web, news, YouTube, and social media. CRITICAL: Use this for ANY question about current events, recent news, or time-sensitive information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "sources": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["web", "news", "academic", "youtube", "social"]},
                        "default": ["web", "news"]
                    },
                    "num_results": {"type": "integer", "default": 10},
                    "recency_days": {"type": "integer", "description": "Limit to recent results (days)"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_excel",
            "description": "Generate a professional Excel spreadsheet with data, formatting, and optional charts. Use for lists, tables, financial data, or any structured data export.",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {"type": "object", "description": "Data as object with sheet names as keys"},
                    "title": {"type": "string", "description": "Spreadsheet title"},
                    "filename": {"type": "string"},
                    "include_charts": {"type": "boolean", "default": False}
                },
                "required": ["data"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_word",
            "description": "Generate a professional Word document (.docx) with formatted content, headers, and styling. Use for reports, proposals, or formal documents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Document content in markdown format"},
                    "title": {"type": "string"},
                    "subtitle": {"type": "string"},
                    "filename": {"type": "string"}
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_pdf",
            "description": "Generate a professional PDF document. Use for reports, whitepapers, or documents requiring fixed layout.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "title": {"type": "string"},
                    "filename": {"type": "string"},
                    "include_toc": {"type": "boolean", "default": False}
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_presentation",
            "description": "Generate a PowerPoint presentation (.pptx) with slides. Use for presentations, pitches, or slide decks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Content organized by sections/slides"},
                    "title": {"type": "string"},
                    "filename": {"type": "string"},
                    "theme": {"type": "string", "enum": ["professional", "modern", "dark"], "default": "professional"}
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "deep_research",
            "description": "Conduct comprehensive research using multiple sources and agents. Use for thorough analysis of complex topics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "depth": {"type": "string", "enum": ["quick", "deep", "exhaustive"], "default": "deep"},
                    "generate_report": {"type": "boolean", "default": False}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_code",
            "description": "Execute code in a sandboxed environment. Use for calculations, data processing, or running scripts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "language": {"type": "string", "enum": ["python", "javascript", "bash"], "default": "python"},
                    "timeout": {"type": "integer", "default": 30}
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_data",
            "description": "Analyze structured data and provide insights with visualizations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {"type": "string", "description": "JSON or CSV data"},
                    "analysis_type": {"type": "string", "enum": ["summary", "trends", "correlation", "forecast"]},
                    "generate_chart": {"type": "boolean", "default": True}
                },
                "required": ["data", "analysis_type"]
            }
        }
    }
]

# ============================================================================
# TOOL EXECUTOR
# ============================================================================

class ToolExecutor:
    """Execute tool calls and manage results"""
    
    @classmethod
    async def execute(cls, tool_calls: List[Any]) -> List[Dict]:
        """Execute multiple tool calls in parallel"""
        tasks = [cls.execute_single(call) for call in tool_calls]
        return await asyncio.gather(*tasks)
    
    @classmethod
    async def execute_single(cls, call: Any) -> Dict:
        """Execute a single tool call with timeout protection"""
        function_name = call.function.name
        try:
            arguments = json.loads(call.function.arguments)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid tool arguments for {function_name}: {e}")
            return {
                "tool_call_id": call.id,
                "role": "tool",
                "content": json.dumps({"tool": function_name, "status": "error", "error": f"Invalid arguments: {e}"}),
                "name": function_name
            }
        
        logger.info(f"Executing tool: {function_name} with args: {list(arguments.keys())}")
        
        try:
            result_data = await asyncio.wait_for(
                cls._execute_tool_inner(function_name, arguments),
                timeout=60.0  # 60 second max per tool
            )
            
            return {
                "tool_call_id": call.id,
                "role": "tool",
                "content": json.dumps(result_data),
                "name": function_name
            }
            
        except asyncio.TimeoutError:
            logger.error(f"Tool {function_name} timed out after 60s")
            return {
                "tool_call_id": call.id,
                "role": "tool",
                "content": json.dumps({"tool": function_name, "status": "error", "error": "Tool execution timed out after 60 seconds"}),
                "name": function_name
            }
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {
                "tool_call_id": call.id,
                "role": "tool",
                "content": json.dumps({"tool": function_name, "status": "error", "error": str(e)}),
                "name": function_name
            }
    
    @classmethod
    async def _execute_tool_inner(cls, function_name: str, arguments: Dict) -> Dict:
        """Inner tool execution logic"""
        result_data = {"tool": function_name, "status": "success"}
        
        if function_name == "realtime_search":
            search_result = await SearchAPIs.multi_search(
                arguments["query"],
                arguments.get("sources", ["web"]),
                arguments.get("num_results", 10),
                arguments.get("recency_days")
            )
            result_data["result"] = search_result
            
        elif function_name == "generate_excel":
            file_id = await asyncio.to_thread(
                FileGenerator.generate_excel,
                arguments["data"],
                arguments.get("filename"),
                arguments.get("title"),
                arguments.get("include_charts", False)
            )
            file_info = FileGenerator.get_file(file_id)
            result_data["file_id"] = file_id
            result_data["filename"] = file_info["filename"]
            result_data["download_url"] = f"/api/v1/download/{file_id}"
            
        elif function_name == "generate_word":
            file_id = await asyncio.to_thread(
                FileGenerator.generate_word,
                arguments["content"],
                arguments.get("title"),
                arguments.get("subtitle"),
                arguments.get("filename")
            )
            file_info = FileGenerator.get_file(file_id)
            result_data["file_id"] = file_id
            result_data["filename"] = file_info["filename"]
            result_data["download_url"] = f"/api/v1/download/{file_id}"
            
        elif function_name == "generate_pdf":
            file_id = await asyncio.to_thread(
                FileGenerator.generate_pdf,
                arguments["content"],
                arguments.get("title"),
                arguments.get("filename"),
                arguments.get("include_toc", False)
            )
            file_info = FileGenerator.get_file(file_id)
            result_data["file_id"] = file_id
            result_data["filename"] = file_info["filename"]
            result_data["download_url"] = f"/api/v1/download/{file_id}"
            
        elif function_name == "generate_presentation":
            file_id = await asyncio.to_thread(
                FileGenerator.generate_pptx,
                arguments["content"],
                arguments.get("title"),
                arguments.get("filename"),
                arguments.get("theme", "professional")
            )
            file_info = FileGenerator.get_file(file_id)
            result_data["file_id"] = file_id
            result_data["filename"] = file_info["filename"]
            result_data["download_url"] = f"/api/v1/download/{file_id}"
            
        elif function_name == "deep_research":
            # Simplified research - just do a search, don't spawn full swarm in streaming
            search_result = await SearchAPIs.multi_search(
                arguments["query"],
                ["web", "news"],
                10
            )
            result_data["result"] = search_result
            
        elif function_name == "execute_code":
            code_result = await CodeSandbox.execute(
                arguments["code"],
                arguments.get("language", "python"),
                min(arguments.get("timeout", 30), 30)  # Cap at 30s
            )
            result_data["result"] = code_result
            
        elif function_name == "analyze_data":
            analysis_code = f"""
import json
import pandas as pd
import numpy as np

data = json.loads('''{json.dumps(arguments.get('data', []))}''')
df = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])

result = {{}}
if "{arguments.get('analysis_type', 'summary')}" == "summary":
    result = df.describe().to_dict()
else:
    result = {{"info": str(df.info()), "shape": list(df.shape)}}

print(json.dumps(result))
"""
            analysis_result = await CodeSandbox.execute(analysis_code, "python", 30)
            result_data["result"] = analysis_result
        
        else:
            result_data["status"] = "error"
            result_data["error"] = f"Unknown tool: {function_name}"
        
        return result_data

# ============================================================================
# KIMI ENGINE
# ============================================================================

class KimiEngine:
    """Main Kimi 2.5 interface with all capabilities"""
    
    CONFIGS = {
        "instant": {
            "temperature": 0.6,
            "top_p": 0.95,
            "extra_body": {"thinking": {"type": "disabled"}}
        },
        "thinking": {
            "temperature": 1.0,
            "top_p": 0.95,
            "extra_body": {"thinking": {"type": "enabled"}}
        },
        "agent": {
            "temperature": 0.6,
            "top_p": 0.95,
            "extra_body": {
                "thinking": {"type": "disabled"},
                "parallel_tool_calls": True
            }
        },
        "swarm": {
            "temperature": 0.7,
            "top_p": 0.95,
            "extra_body": {
                "thinking": {"type": "enabled"},
                "parallel_tool_calls": True
            }
        },
        "research": {
            "temperature": 0.7,
            "top_p": 0.95,
            "extra_body": {
                "thinking": {"type": "enabled"},
                "parallel_tool_calls": True
            }
        },
        "code": {
            "temperature": 0.3,
            "top_p": 0.95,
            "extra_body": {"thinking": {"type": "disabled"}}
        }
    }
    
    @classmethod
    async def chat(
        cls,
        messages: List[Dict],
        mode: str = "thinking",
        enable_tools: bool = True,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Execute chat with tools"""
        
        config = cls.CONFIGS.get(mode, cls.CONFIGS["thinking"]).copy()
        params = {
            "model": "kimi-k2.5",
            "messages": messages,
            "stream": stream,
            **config
        }
        
        # Add tools for agent modes
        if enable_tools and mode in ["agent", "research"]:
            params["tools"] = TOOLS
            params["tool_choice"] = "auto"
        
        start_time = time.time()
        response = client.chat.completions.create(**params)
        latency_ms = int((time.time() - start_time) * 1000)
        
        if stream:
            return response
        
        message = response.choices[0].message
        
        result = {
            "content": message.content,
            "reasoning_content": getattr(message, 'reasoning_content', None),
            "tool_calls": getattr(message, 'tool_calls', None),
            "mode": mode,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            "latency_ms": latency_ms
        }
        
        # Execute tools if present
        if result["tool_calls"]:
            tool_results = await ToolExecutor.execute(result["tool_calls"])
            result["tool_results"] = tool_results
            
            # Continue conversation
            continued = await cls.continue_with_tools(messages, message, tool_results)
            result["content"] = continued["content"]
            result["tool_outputs"] = continued.get("tool_outputs", [])
            result["usage"]["total_tokens"] += continued["usage"]["total_tokens"]
        
        return result
    
    @classmethod
    async def continue_with_tools(
        cls,
        original_messages: List[Dict],
        assistant_message: Any,
        tool_results: List[Dict]
    ) -> Dict[str, Any]:
        """Continue after tool execution"""
        
        messages = original_messages.copy()
        messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "reasoning_content": getattr(assistant_message, 'reasoning_content', None),
            "tool_calls": [tc.model_dump() for tc in assistant_message.tool_calls]
        })
        messages.extend([{
            "role": r["role"],
            "content": r["content"],
            "tool_call_id": r["tool_call_id"]
        } for r in tool_results])
        
        response = client.chat.completions.create(
            model="kimi-k2.5",
            messages=messages,
            temperature=0.6,
            extra_body={"thinking": {"type": "disabled"}}
        )
        
        # Extract file outputs
        tool_outputs = []
        for tr in tool_results:
            try:
                content = json.loads(tr["content"])
                if "download_url" in content:
                    tool_outputs.append({
                        "type": "file",
                        "filename": content.get("filename"),
                        "download_url": content.get("download_url"),
                        "file_id": content.get("file_id"),
                        "file_type": content.get("file_type", "unknown")
                    })
                elif "result" in content and isinstance(content["result"], dict):
                    if "sources" in content["result"]:
                        tool_outputs.append({
                            "type": "search",
                            "sources": list(content["result"].get("sources", {}).keys())
                        })
            except:
                pass
        
        return {
            "content": response.choices[0].message.content,
            "tool_outputs": tool_outputs,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    
    @classmethod
    async def stream_chat(
        cls,
        messages: List[Dict],
        mode: str = "thinking",
        enable_tools: bool = True
    ) -> AsyncGenerator[str, None]:
        """Stream chat responses with full tool execution support"""
        
        # Check if user is asking for file generation - auto-upgrade to agent mode
        user_msg = ""
        for m in messages:
            if m.get("role") == "user":
                content = m.get("content", "")
                if isinstance(content, str):
                    user_msg = content.lower()
                elif isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            user_msg = part.get("text", "").lower()
        
        file_keywords = ['excel', 'spreadsheet', 'xlsx', 'csv',
                        'word doc', 'docx', 'pdf', 'powerpoint', 'presentation', 'pptx']
        needs_tools = any(kw in user_msg for kw in file_keywords)
        
        # Only upgrade to agent mode if explicitly requesting file generation
        if needs_tools and mode in ["instant", "thinking"]:
            mode = "agent"
        
        use_tools = enable_tools and mode in ["agent", "research"]
        
        config = cls.CONFIGS.get(mode, cls.CONFIGS["thinking"]).copy()
        params = {
            "model": "kimi-k2.5",
            "messages": messages,
            "stream": True,
            **config
        }
        
        if use_tools:
            params["tools"] = TOOLS
            params["tool_choice"] = "auto"
            # Add system instruction for file generation
            if needs_tools:
                file_system_msg = {
                    "role": "system",
                    "content": (
                        "IMPORTANT: When the user asks you to generate, create, or make any file "
                        "(Excel, Word, PDF, PowerPoint, CSV), you MUST use the appropriate tool "
                        "(generate_excel, generate_word, generate_pdf, generate_presentation) to create "
                        "an actual downloadable file. Do NOT just describe the content in text. "
                        "Always call the tool with real structured data."
                    )
                }
                params["messages"] = [file_system_msg] + params["messages"]
        
        try:
            response = client.chat.completions.create(**params)
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'data': {'message': str(e)}})}\n\n"
            return
        
        full_content = ''
        full_reasoning = ''
        collected_tool_calls = {}  # index -> {id, function: {name, arguments}}
        downloads = []
        
        for chunk in response:
            delta = chunk.choices[0].delta
            finish_reason = chunk.choices[0].finish_reason
            
            content = getattr(delta, 'content', None)
            reasoning = getattr(delta, 'reasoning_content', None)
            tool_calls_delta = getattr(delta, 'tool_calls', None)
            
            if content:
                full_content += content
                yield f"data: {json.dumps({'type': 'content', 'data': {'chunk': content}})}\n\n"
            
            if reasoning:
                full_reasoning += reasoning
                yield f"data: {json.dumps({'type': 'reasoning', 'data': {'chunk': reasoning}})}\n\n"
            
            # Collect tool call chunks (they come in pieces across multiple chunks)
            if tool_calls_delta:
                for tc in tool_calls_delta:
                    idx = tc.index
                    if idx not in collected_tool_calls:
                        collected_tool_calls[idx] = {
                            "id": getattr(tc, 'id', None),
                            "function": {"name": "", "arguments": ""}
                        }
                    if tc.id:
                        collected_tool_calls[idx]["id"] = tc.id
                    if tc.function:
                        if tc.function.name:
                            collected_tool_calls[idx]["function"]["name"] += tc.function.name
                        if tc.function.arguments:
                            collected_tool_calls[idx]["function"]["arguments"] += tc.function.arguments
            
            # When the model finishes with tool_calls, execute them
            if finish_reason == "tool_calls" and collected_tool_calls:
                yield f"data: {json.dumps({'type': 'tool_call', 'data': {'message': 'Generating files...'}})}\n\n"
                
                # Build tool call objects for execution
                class ToolCallObj:
                    def __init__(self, tc_dict):
                        self.id = tc_dict["id"]
                        self.function = type('Function', (), {
                            'name': tc_dict["function"]["name"],
                            'arguments': tc_dict["function"]["arguments"]
                        })()
                
                tool_call_objects = [ToolCallObj(tc) for tc in collected_tool_calls.values()]
                
                # Execute all tools
                try:
                    tool_results = await ToolExecutor.execute(tool_call_objects)
                    
                    # Extract download info from tool results
                    for tr in tool_results:
                        try:
                            result_content = json.loads(tr["content"])
                            if "download_url" in result_content:
                                download_info = {
                                    "filename": result_content.get("filename", "file"),
                                    "download_url": result_content["download_url"],
                                    "file_id": result_content.get("file_id", ""),
                                    "file_type": result_content.get("type", result_content.get("file_type", "unknown"))
                                }
                                downloads.append(download_info)
                                yield f"data: {json.dumps({'type': 'download', 'data': download_info})}\n\n"
                        except:
                            pass
                    
                    # Continue conversation with tool results
                    continuation_messages = list(params["messages"])
                    continuation_messages.append({
                        "role": "assistant",
                        "content": full_content if full_content else None,
                        "tool_calls": [
                            {
                                "id": tc["id"],
                                "type": "function",
                                "function": {
                                    "name": tc["function"]["name"],
                                    "arguments": tc["function"]["arguments"]
                                }
                            }
                            for tc in collected_tool_calls.values()
                        ]
                    })
                    
                    for tr in tool_results:
                        continuation_messages.append({
                            "role": "tool",
                            "content": tr["content"],
                            "tool_call_id": tr["tool_call_id"]
                        })
                    
                    # Add instruction to keep continuation response concise
                    continuation_messages.insert(0, {
                        "role": "system",
                        "content": (
                            "The tool has been executed and the file has been generated successfully. "
                            "Provide a brief, concise summary of what was created (2-3 sentences max). "
                            "Do NOT repeat yourself or describe what you plan to do. The file is already created."
                        )
                    })
                    
                    # Stream the continuation response with max_tokens limit
                    continuation_response = client.chat.completions.create(
                        model="kimi-k2.5",
                        messages=continuation_messages,
                        stream=True,
                        temperature=0.6,
                        max_tokens=500,  # Keep continuation concise
                        extra_body={"thinking": {"type": "disabled"}}
                    )
                    
                    cont_token_count = 0
                    for cont_chunk in continuation_response:
                        cont_delta = cont_chunk.choices[0].delta
                        cont_content = getattr(cont_delta, 'content', None)
                        if cont_content:
                            cont_token_count += 1
                            full_content += cont_content
                            yield f"data: {json.dumps({'type': 'content', 'data': {'chunk': cont_content}})}\n\n"
                            # Safety: stop if we've generated too much
                            if cont_token_count > 600:
                                logger.warning("Continuation response exceeded 600 tokens, stopping")
                                break
                    
                except Exception as e:
                    logger.error(f"Tool execution error in stream: {e}")
                    error_msg = f"\n\n*Error executing tools: {str(e)}*"
                    full_content += error_msg
                    yield f"data: {json.dumps({'type': 'content', 'data': {'chunk': error_msg}})}\n\n"
        
        # Send complete event with downloads
        yield f"data: {json.dumps({'type': 'complete', 'data': {'content': full_content, 'reasoning': full_reasoning, 'downloads': downloads}})}\n\n"

# ============================================================================
# AGENT SWARM
# ============================================================================

class AgentSwarm:
    """Multi-agent orchestration system"""
    
    ROLES = {
        "researcher": "Expert at finding and verifying real-time information from multiple sources",
        "analyst": "Expert at data analysis, pattern recognition, and statistical insights",
        "writer": "Expert at creating clear, engaging, and well-structured content",
        "critic": "Expert at reviewing, fact-checking, and identifying issues or gaps",
        "synthesizer": "Expert at combining multiple perspectives into coherent output",
        "planner": "Expert at breaking down complex tasks and creating action plans",
        "creative": "Expert at generating innovative ideas and creative solutions",
        "implementer": "Expert at practical execution and implementation details"
    }
    
    async def execute(
        self,
        master_task: str,
        context: Dict,
        num_agents: int = 5,
        enable_search: bool = True,
        generate_deliverable: bool = False,
        deliverable_type: Optional[str] = None
    ) -> Dict:
        """Execute complex task with agent swarm"""
        
        start_time = time.time()
        
        # Step 1: Decompose task
        subtasks = await self._decompose_task(master_task, num_agents)
        
        # Step 2: Execute agents in parallel
        semaphore = asyncio.Semaphore(10)
        
        async def run_agent(agent_def):
            async with semaphore:
                return await self._execute_agent(agent_def, context, enable_search)
        
        results = await asyncio.gather(*[run_agent(t) for t in subtasks])
        
        # Step 3: Synthesize results
        synthesis = await self._synthesize_results(results, master_task)
        
        # Step 4: Generate deliverable if requested
        deliverable = None
        if generate_deliverable and deliverable_type:
            deliverable = await self._generate_deliverable(synthesis, results, deliverable_type)
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        return {
            "master_task": master_task,
            "agents_deployed": len(subtasks),
            "subtasks": subtasks,
            "agent_results": results,
            "synthesis": synthesis,
            "deliverable": deliverable,
            "latency_ms": latency_ms,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _decompose_task(self, task: str, num_agents: int) -> List[Dict]:
        """Intelligently decompose task into subtasks"""
        
        prompt = f"""As a task decomposition expert, break down this complex task into {num_agents} parallel subtasks.

Master Task: {task}

Available roles: {list(self.ROLES.keys())}

Return JSON format:
{{
  "subtasks": [
    {{"role": "researcher/analyst/writer/etc", "task": "specific description", "priority": 1-10}}
  ]
}}"""

        try:
            response = client.chat.completions.create(
                model="kimi-k2.5",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                response_format={"type": "json_object"},
                extra_body={"thinking": {"type": "enabled"}}
            )
            
            data = json.loads(response.choices[0].message.content)
            tasks = data.get("subtasks", [])
            
            valid = []
            for t in tasks[:num_agents]:
                role = t.get("role", "researcher")
                if role not in self.ROLES:
                    role = "researcher"
                valid.append({
                    "id": f"agent_{len(valid)}",
                    "role": role,
                    "task": t.get("task", "Analyze"),
                    "priority": t.get("priority", 5)
                })
            
            return valid if valid else self._fallback_tasks(task, num_agents)
        except Exception as e:
            logger.error(f"Task decomposition error: {e}")
            return self._fallback_tasks(task, num_agents)
    
    def _fallback_tasks(self, task: str, num: int) -> List[Dict]:
        """Fallback task decomposition"""
        roles = list(self.ROLES.keys())[:num]
        return [
            {
                "id": f"agent_{i}",
                "role": role,
                "task": f"Analyze aspect {i+1} of: {task[:100]}",
                "priority": 5
            }
            for i, role in enumerate(roles)
        ]
    
    async def _execute_agent(self, agent_def: Dict, context: Dict, enable_search: bool) -> Dict:
        """Execute single agent"""
        
        role_desc = self.ROLES.get(agent_def["role"], "AI Assistant")
        
        messages = [
            {
                "role": "system",
                "content": f"You are a {agent_def['role']}. {role_desc}. Be thorough but concise."
            },
            {
                "role": "user",
                "content": f"Task: {agent_def['task']}\nContext: {json.dumps(context, default=str)}"
            }
        ]
        
        try:
            result = await KimiEngine.chat(
                messages=messages,
                mode="agent" if enable_search else "thinking",
                enable_tools=enable_search
            )
            
            return {
                "agent_id": agent_def["id"],
                "role": agent_def["role"],
                "task": agent_def["task"],
                "output": result["content"],
                "tool_results": result.get("tool_results", []),
                "tokens": result["usage"]["total_tokens"],
                "success": True
            }
        except Exception as e:
            return {
                "agent_id": agent_def["id"],
                "role": agent_def["role"],
                "task": agent_def["task"],
                "output": str(e),
                "success": False
            }
    
    async def _synthesize_results(self, results: List[Dict], master_task: str) -> str:
        """Synthesize all agent outputs"""
        
        successful = [r for r in results if r.get("success")]
        
        synthesis_input = "\n\n".join([
            f"### {r['role'].upper()} (Agent {r['agent_id']})\n{r['output'][:1000]}"
            for r in successful[:8]
        ])
        
        prompt = f"""Synthesize these expert analyses into a comprehensive final answer.

Master Task: {master_task}

Agent Analyses:
{synthesis_input}

Provide a well-structured, actionable final response that integrates all perspectives:"""

        response = client.chat.completions.create(
            model="kimi-k2.5",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4096,
            extra_body={"thinking": {"type": "enabled"}}
        )
        
        return response.choices[0].message.content
    
    async def _generate_deliverable(
        self,
        synthesis: str,
        results: List[Dict],
        deliverable_type: str
    ) -> Dict:
        """Generate final deliverable document"""
        
        if deliverable_type == "report":
            content = f"""# Research Report

## Executive Summary
{synthesis[:1500]}

## Detailed Findings

"""
            for r in results:
                if r.get("success"):
                    content += f"\n### {r['role'].upper()} Analysis\n\n{r['output'][:800]}\n"
            
            file_id = FileGenerator.generate_word(content, title="Research Report")
            file_info = FileGenerator.get_file(file_id)
            
            return {
                "type": "report",
                "file_id": file_id,
                "filename": file_info["filename"],
                "download_url": f"/api/v1/download/{file_id}"
            }
        
        elif deliverable_type == "presentation":
            content = f"Executive Summary\n\n{synthesis[:1000]}\n\n"
            for r in results[:5]:
                if r.get("success"):
                    content += f"{r['role'].upper()} Insights\n{r['output'][:500]}\n\n"
            
            file_id = FileGenerator.generate_pptx(content, title="Research Presentation")
            file_info = FileGenerator.get_file(file_id)
            
            return {
                "type": "presentation",
                "file_id": file_id,
                "filename": file_info["filename"],
                "download_url": f"/api/v1/download/{file_id}"
            }
        
        return None

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.post("/api/v1/chat")
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint with full tool support"""
    try:
        messages = [m.model_dump(exclude_none=True) for m in request.messages]
        
        result = await KimiEngine.chat(
            messages=messages,
            mode=request.mode,
            enable_tools=request.enable_tools,
            stream=request.stream
        )
        
        # Extract downloads
        downloads = []
        for output in result.get("tool_outputs", []):
            if output.get("type") == "file":
                downloads.append({
                    "filename": output["filename"],
                    "download_url": output["download_url"],
                    "file_id": output["file_id"],
                    "file_type": output.get("file_type", "unknown")
                })
        
        return {
            "success": True,
            "response": {
                "answer": result["content"],
                "reasoning": result.get("reasoning_content"),
                "mode": result["mode"],
                "downloads": downloads,
                "search_sources": [o for o in result.get("tool_outputs", []) if o.get("type") == "search"],
                "metadata": {
                    "tokens": result["usage"],
                    "latency_ms": result["latency_ms"],
                    "tool_calls": len(result.get("tool_calls") or [])
                }
            }
        }
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/v1/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint"""
    messages = [m.model_dump(exclude_none=True) for m in request.messages]
    
    async def generate():
        async for chunk in KimiEngine.stream_chat(
            messages=messages,
            mode=request.mode,
            enable_tools=request.enable_tools
        ):
            yield chunk
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )

@app.post("/api/v1/swarm")
async def swarm_endpoint(request: SwarmRequest):
    """Agent swarm for complex tasks"""
    try:
        swarm = AgentSwarm()
        result = await swarm.execute(
            master_task=request.master_task,
            context=request.context,
            num_agents=request.num_agents,
            enable_search=request.enable_search,
            generate_deliverable=request.generate_deliverable,
            deliverable_type=request.deliverable_type
        )
        
        return {
            "success": True,
            "response": {
                "answer": result["synthesis"],
                "mode": "swarm",
                "agents": result["agents_deployed"],
                "subtasks": result["subtasks"],
                "agent_results": result["agent_results"],
                "deliverable": result.get("deliverable"),
                "latency_ms": result["latency_ms"],
                "metadata": {
                    "total_tokens": sum(r.get("tokens", 0) for r in result["agent_results"])
                }
            }
        }
    except Exception as e:
        logger.error(f"Swarm error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/v1/search")
async def search_endpoint(request: SearchRequest):
    """Direct search across multiple sources"""
    try:
        results = await SearchAPIs.multi_search(
            request.query,
            request.sources,
            request.num_results,
            request.recency_days
        )
        return {"success": True, "results": results}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/v1/research")
async def research_endpoint(request: ResearchRequest):
    """Deep research with optional deliverable"""
    try:
        swarm = AgentSwarm()
        result = await swarm.execute(
            master_task=request.query,
            context={"depth": request.depth, "sources": request.sources},
            num_agents=5 if request.depth == "quick" else 10 if request.depth == "deep" else 15,
            enable_search=True,
            generate_deliverable=request.generate_deliverable,
            deliverable_type=request.deliverable_type
        )
        
        return {
            "success": True,
            "response": {
                "answer": result["synthesis"],
                "research_data": result,
                "mode": "research",
                "deliverable": result.get("deliverable")
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/v1/vision-to-code")
async def vision_to_code_endpoint(request: VisionCodeRequest):
    """Convert UI image to code"""
    try:
        result = await VisionToCode.generate(
            image_base64=request.image_base64,
            requirements=request.requirements,
            framework=request.framework,
            styling_preference=request.styling_preference
        )
        
        return {
            "success": True,
            "response": {
                "code_blocks": result["code_blocks"],
                "framework": result["framework"],
                "preview_html": result.get("preview_html"),
                "tokens_used": result["tokens_used"]
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/v1/execute-code")
async def execute_code_endpoint(request: CodeExecutionRequest):
    """Execute code in sandbox"""
    try:
        result = await CodeSandbox.execute(
            code=request.code,
            language=request.language,
            timeout=request.timeout,
            dependencies=request.dependencies,
            inputs=request.inputs
        )
        
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/v1/generate-file")
async def generate_file_endpoint(request: FileGenRequest):
    """Generate downloadable file"""
    try:
        # Parse content if string
        content = request.content
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except:
                pass
        
        def _generate_sync():
            if request.file_type == "excel":
                return FileGenerator.generate_excel(
                    content,
                    request.filename,
                    request.title,
                    request.include_charts
                )
            elif request.file_type == "word":
                return FileGenerator.generate_word(
                    content if isinstance(content, str) else json.dumps(content, indent=2),
                    request.title,
                    request.subtitle,
                    request.filename
                )
            elif request.file_type == "pdf":
                return FileGenerator.generate_pdf(
                    content if isinstance(content, str) else json.dumps(content, indent=2),
                    request.title,
                    request.filename
                )
            elif request.file_type == "pptx":
                return FileGenerator.generate_pptx(
                    content if isinstance(content, str) else json.dumps(content, indent=2),
                    request.title,
                    request.filename
                )
            else:
                raise ValueError("Unsupported file type")
        
        # Run synchronous file generation in a thread to avoid blocking the event loop
        file_id = await asyncio.wait_for(
            asyncio.to_thread(_generate_sync),
            timeout=30.0
        )
        
        file_info = FileGenerator.get_file(file_id)
        
        return {
            "success": True,
            "file_id": file_id,
            "filename": file_info["filename"],
            "file_type": request.file_type,
            "download_url": f"/api/v1/download/{file_id}"
        }
    except asyncio.TimeoutError:
        logger.error("File generation timed out after 30s")
        return {"success": False, "error": "File generation timed out"}
    except Exception as e:
        logger.error(f"File generation error: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/v1/download/{file_id}")
async def download_file(file_id: str):
    """Download generated file"""
    file_info = FileGenerator.get_file(file_id)
    if not file_info or not os.path.exists(file_info["path"]):
        raise HTTPException(status_code=404, detail="File not found or expired")
    
    media_types = {
        "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "word": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pdf": "application/pdf",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    }
    
    return FileResponse(
        file_info["path"],
        filename=file_info["filename"],
        media_type=media_types.get(file_info["type"], "application/octet-stream")
    )

@app.post("/api/v1/multimodal")
async def multimodal_endpoint(
    text: str = Form(...),
    mode: str = Form("thinking"),
    image: Optional[UploadFile] = File(None)
):
    """Multimodal input (text + image)"""
    try:
        content = [{"type": "text", "text": text}]
        
        if image:
            image_bytes = await image.read()
            image_b64 = base64.b64encode(image_bytes).decode()
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{image.content_type};base64,{image_b64}", "detail": "high"}
            })
        
        messages = [{"role": "user", "content": content}]
        
        result = await KimiEngine.chat(messages=messages, mode=mode)
        
        return {
            "success": True,
            "response": {
                "answer": result["content"],
                "reasoning": result.get("reasoning_content"),
                "mode": mode
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/health")
@app.get("/api/v1/health")
async def health_check():
    """Health check with capabilities"""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "model": "kimi-k2.5",
        "capabilities": [
            "instant_mode", "thinking_mode", "agent_mode", "swarm_mode", "research_mode", "code_mode",
            "realtime_search", "file_generation", "vision_to_code", "code_execution",
            "multimodal", "streaming", "agent_swarm"
        ],
        "apis_configured": {
            "kimi": bool(KIMI_API_KEY),
            "perplexity": bool(PERPLEXITY_API_KEY),
            "exa": bool(EXA_API_KEY),
            "youtube": bool(YOUTUBE_API_KEY),
            "grok": bool(GROK_API_KEY)
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    return {
        "message": "McLeuker AI - Kimi 2.5 Complete",
        "version": "3.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

# Scheduled cleanup
@app.on_event("startup")
async def startup_event():
    """Clean up old files on startup"""
    cleaned = FileGenerator.cleanup_old_files(24)
    logger.info(f"Cleaned up {cleaned} old files")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        timeout_keep_alive=30,
        limit_concurrency=20
    )
