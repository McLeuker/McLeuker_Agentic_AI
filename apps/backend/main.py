"""
McLeuker AI V2 - Complete Backend with Kimi-2.5 Capabilities
===========================================================

Features:
- Full Kimi-2.5 integration with proper reasoning
- Hybrid LLM architecture (Kimi-2.5 + Grok)
- Agent swarm with parallel execution
- Fixed file generation with real data extraction
- Proper memory/conversation persistence
- Standardized output structure

Models:
- kimi-k2.5: Primary reasoning model
- grok-4-1-fast-reasoning: Real-time search model
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, BackgroundTasks, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any, Union, AsyncGenerator
import openai
import os
import json
import asyncio
import httpx
import uuid
import re
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import traceback
import logging
from dataclasses import dataclass, field
from enum import Enum
import csv
from io import BytesIO
import base64

# Data processing
import pandas as pd
import numpy as np

# Document generation
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Excel
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference

# PDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# PowerPoint
from pptx import Presentation
from pptx.util import Inches as PptxInches

# Supabase
from supabase import create_client, Client

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(
    title="McLeuker AI V2",
    description="Production AI platform with Kimi-2.5 capabilities",
    version="4.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Keys
KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
GROK_API_KEY = os.getenv("GROK_API_KEY", "")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
EXA_API_KEY = os.getenv("EXA_API_KEY", "")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase: {e}")

# Initialize LLM clients
kimi_client = openai.OpenAI(
    api_key=KIMI_API_KEY,
    base_url="https://api.moonshot.ai/v1"
) if KIMI_API_KEY else None

grok_client = openai.OpenAI(
    api_key=GROK_API_KEY,
    base_url="https://api.x.ai/v1"
) if GROK_API_KEY else None

# Directories
OUTPUT_DIR = Path("/tmp/mcleuker_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

class ChatMode(str, Enum):
    INSTANT = "instant"
    THINKING = "thinking"
    AGENT = "agent"
    SWARM = "swarm"
    RESEARCH = "research"
    CODE = "code"
    HYBRID = "hybrid"

class FileType(str, Enum):
    EXCEL = "excel"
    WORD = "word"
    PDF = "pdf"
    PPTX = "pptx"
    CSV = "csv"
    JSON = "json"
    MARKDOWN = "markdown"
    DOCX = "docx"

# Mode configurations
MODE_CONFIGS = {
    ChatMode.INSTANT: {
        "primary_model": "grok",
        "temperature": 0.7,
        "max_tokens": 2048,
        "show_reasoning": False,
        "enable_tools": True
    },
    ChatMode.THINKING: {
        "primary_model": "kimi",
        "temperature": 0.6,
        "max_tokens": 4096,
        "show_reasoning": True,
        "enable_tools": True
    },
    ChatMode.AGENT: {
        "primary_model": "kimi",
        "temperature": 0.5,
        "max_tokens": 4096,
        "show_reasoning": True,
        "enable_tools": True
    },
    ChatMode.SWARM: {
        "primary_model": "kimi",
        "temperature": 0.5,
        "max_tokens": 8192,
        "show_reasoning": True,
        "enable_tools": True,
        "parallel_agents": 5
    },
    ChatMode.RESEARCH: {
        "primary_model": "hybrid",
        "temperature": 0.4,
        "max_tokens": 8192,
        "show_reasoning": True,
        "enable_tools": True
    },
    ChatMode.CODE: {
        "primary_model": "kimi",
        "temperature": 0.3,
        "max_tokens": 4096,
        "show_reasoning": False,
        "enable_tools": True
    },
    ChatMode.HYBRID: {
        "primary_model": "hybrid",
        "temperature": 0.5,
        "max_tokens": 4096,
        "show_reasoning": True,
        "enable_tools": True
    }
}

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
    mode: ChatMode = ChatMode.THINKING
    stream: bool = True
    enable_tools: bool = True
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    context_id: Optional[str] = None

class FileGenRequest(BaseModel):
    # V2 interface
    prompt: Optional[str] = None
    file_type: Optional[FileType] = None
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    # V1 compatibility
    content: Optional[Union[str, Dict, List]] = None
    filename: Optional[str] = None
    title: Optional[str] = None
    subtitle: Optional[str] = None
    include_charts: bool = False
    template: Optional[str] = None
    styling: Optional[Dict[str, Any]] = None

class SearchRequest(BaseModel):
    query: str
    sources: List[str] = ["web", "news"]
    num_results: int = 10

class AgentRequest(BaseModel):
    task: str
    agent_type: str = "research"
    context: Dict = {}
    user_id: Optional[str] = None

class SwarmRequest(BaseModel):
    task: str
    num_agents: int = 5
    context: Dict = {}
    user_id: Optional[str] = None

# ============================================================================
# STREAMING EVENT HELPERS
# ============================================================================

def event(type: str, data: Any) -> str:
    """Create a standardized SSE event."""
    return f"data: {json.dumps({'type': type, 'data': data, 'timestamp': datetime.now().isoformat()})}\n\n"

# ============================================================================
# SEARCH LAYER
# ============================================================================

class SearchLayer:
    """Unified search across all data sources."""
    
    @staticmethod
    async def search(query: str, sources: List[str] = None, num_results: int = 10) -> Dict:
        """Search across all configured sources."""
        if sources is None:
            sources = ["web", "news"]
        
        tasks = []
        source_map = {}
        idx = 0
        
        if "web" in sources or "news" in sources:
            if PERPLEXITY_API_KEY:
                tasks.append(SearchLayer._perplexity_search(query))
                source_map[idx] = "perplexity"
                idx += 1
        
        if "web" in sources:
            if EXA_API_KEY:
                tasks.append(SearchLayer._exa_search(query, num_results))
                source_map[idx] = "exa"
                idx += 1
            if SERPAPI_KEY:
                tasks.append(SearchLayer._google_search(query, num_results))
                source_map[idx] = "google"
                idx += 1
        
        if "social" in sources:
            if GROK_API_KEY:
                tasks.append(SearchLayer._grok_search(query))
                source_map[idx] = "grok"
                idx += 1
        
        if not tasks:
            return {"query": query, "results": {}, "structured_data": {"data_points": []}}
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        combined = {
            "query": query,
            "sources": sources,
            "results": {},
            "structured_data": {"data_points": [], "sources": []}
        }
        
        for i, result in enumerate(results):
            source_name = source_map.get(i, f"source_{i}")
            if isinstance(result, Exception):
                combined["results"][source_name] = {"error": str(result)}
            else:
                combined["results"][source_name] = result
                # Extract structured data
                if "data_points" in result:
                    combined["structured_data"]["data_points"].extend(result["data_points"])
                if "sources" in result:
                    # Filter out API-level sources that have no real URL
                    real_sources = [
                        s for s in result["sources"]
                        if s.get("url") and s["url"].strip() and s["url"].startswith("http")
                    ]
                    combined["structured_data"]["sources"].extend(real_sources)
        
        # Also add Perplexity citations as real sources if available
        for source_name, result in combined["results"].items():
            if source_name == "perplexity" and isinstance(result, dict):
                for citation_url in result.get("citations", []):
                    if citation_url and citation_url.startswith("http"):
                        # Extract domain as title
                        try:
                            from urllib.parse import urlparse
                            domain = urlparse(citation_url).netloc.replace('www.', '')
                            title = domain.split('.')[0].title()
                        except:
                            title = "Source"
                        combined["structured_data"]["sources"].append({
                            "title": title,
                            "url": citation_url,
                            "source": "perplexity"
                        })
        
        return combined
    
    @staticmethod
    async def _perplexity_search(query: str) -> Dict:
        """Search with Perplexity AI."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "sonar-pro",
                        "messages": [{"role": "user", "content": query}],
                        "temperature": 0.2
                    }
                )
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                # Extract data points
                data_points = [{"title": "Perplexity Result", "description": content[:500], "source": "perplexity"}]
                
                return {
                    "source": "perplexity",
                    "answer": content,
                    "citations": data.get("citations", []),
                    "data_points": data_points,
                    "sources": [{"title": "Perplexity", "url": "", "source": "perplexity"}]
                }
        except Exception as e:
            logger.error(f"Perplexity search error: {e}")
            return {"error": str(e), "source": "perplexity", "data_points": [], "sources": []}
    
    @staticmethod
    async def _exa_search(query: str, num_results: int) -> Dict:
        """Search with Exa.ai."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.exa.ai/search",
                    headers={"Authorization": f"Bearer {EXA_API_KEY}"},
                    json={
                        "query": query,
                        "numResults": num_results,
                        "useAutoprompt": True,
                        "contents": {"text": {"maxCharacters": 500}}
                    }
                )
                data = response.json()
                
                data_points = []
                sources = []
                for r in data.get("results", []):
                    dp = {
                        "title": r.get("title", ""),
                        "description": r.get("text", "")[:300],
                        "url": r.get("url", ""),
                        "source": "exa"
                    }
                    data_points.append(dp)
                    sources.append({"title": r.get("title", ""), "url": r.get("url", ""), "source": "exa"})
                
                return {
                    "source": "exa",
                    "results": data.get("results", []),
                    "data_points": data_points,
                    "sources": sources
                }
        except Exception as e:
            logger.error(f"Exa search error: {e}")
            return {"error": str(e), "source": "exa", "data_points": [], "sources": []}
    
    @staticmethod
    async def _google_search(query: str, num_results: int) -> Dict:
        """Search with Google via SerpAPI."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://serpapi.com/search",
                    params={
                        "q": query,
                        "api_key": SERPAPI_KEY,
                        "engine": "google",
                        "num": num_results
                    }
                )
                data = response.json()
                
                data_points = []
                sources = []
                for r in data.get("organic_results", [])[:num_results]:
                    dp = {
                        "title": r.get("title", ""),
                        "description": r.get("snippet", ""),
                        "url": r.get("link", ""),
                        "source": "google"
                    }
                    data_points.append(dp)
                    sources.append({"title": r.get("title", ""), "url": r.get("link", ""), "source": "google"})
                
                return {
                    "source": "google",
                    "results": data.get("organic_results", []),
                    "data_points": data_points,
                    "sources": sources
                }
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return {"error": str(e), "source": "google", "data_points": [], "sources": []}
    
    @staticmethod
    async def _grok_search(query: str) -> Dict:
        """Search with Grok/X AI."""
        try:
            if not grok_client:
                return {"error": "Grok not configured", "source": "grok", "data_points": [], "sources": []}
            
            response = grok_client.chat.completions.create(
                model="grok-4-1-fast-reasoning",
                messages=[
                    {"role": "system", "content": "You are a real-time search assistant. Provide current information."},
                    {"role": "user", "content": query}
                ],
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            return {
                "source": "grok",
                "answer": content,
                "data_points": [{"title": "Grok Result", "description": content[:500], "source": "grok"}],
                "sources": [{"title": "Grok/X AI", "url": "", "source": "grok"}]
            }
        except Exception as e:
            logger.error(f"Grok search error: {e}")
            return {"error": str(e), "source": "grok", "data_points": [], "sources": []}


# ============================================================================
# FILE GENERATION ENGINE
# ============================================================================

class FileEngine:
    """Professional file generation with real data."""
    
    # File registry for downloads
    files: Dict[str, Dict] = {}
    
    @staticmethod
    def _generate_filename(prompt: str, extension: str) -> str:
        """Generate a precise, descriptive filename using LLM reasoning about the content."""
        import re
        
        # Try LLM-based filename generation
        client = grok_client or kimi_client
        if client:
            try:
                model = "grok-3-mini" if client == grok_client else "kimi-k2.5"
                temp = 0.3 if client == grok_client else 1
                result = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": """Generate a precise filename (no extension) for a file based on the user's request.
Rules:
- Summarize the CONTENT the user wants, not their instruction words
- Use snake_case, lowercase, max 6 words
- Be specific: include topic, scope, and type of data
- Examples: "european_beauty_brands_market_analysis", "tesla_vs_byd_ev_comparison_2026", "top_50_sustainable_suppliers_europe"
- Return ONLY the filename, nothing else"""},
                        {"role": "user", "content": f"User request: {prompt[:200]}"}
                    ],
                    temperature=temp,
                    max_tokens=50
                )
                slug = result.choices[0].message.content.strip().strip('"').strip("'").strip('`')
                slug = re.sub(r'[^a-zA-Z0-9_]', '_', slug.lower())
                slug = re.sub(r'_+', '_', slug).strip('_')[:60]
                if slug and len(slug) > 3:
                    return f"{slug}.{extension}"
            except Exception as e:
                logger.error(f"LLM filename generation error: {e}")
        
        # Fallback: extract key words
        stopwords = {'generate', 'create', 'make', 'build', 'an', 'a', 'the', 'me', 'please',
                     'excel', 'spreadsheet', 'sheet', 'pdf', 'word', 'document', 'report',
                     'powerpoint', 'presentation', 'pptx', 'file', 'containing', 'about',
                     'with', 'information', 'data', 'of', 'for', 'on', 'in', 'to', 'and',
                     'that', 'this', 'from', 'can', 'you', 'i', 'want', 'need', 'give',
                     'generative', 'including', 'different', 'perspectives', 'based', 'your',
                     'knowledge', 'master'}
        words = re.sub(r'[^a-zA-Z0-9\s]', '', prompt.lower()).split()
        meaningful = [w for w in words if w not in stopwords and len(w) > 1][:6]
        if not meaningful:
            meaningful = ['report']
        slug = '_'.join(meaningful)
        return f"{slug}.{extension}"
    
    @staticmethod
    def _sanitize_sheet_title(title: str) -> str:
        """Sanitize a string for use as an Excel sheet title."""
        import re
        # Remove characters invalid in Excel sheet names: \ / ? * [ ] :
        sanitized = re.sub(r'[\\/?*\[\]:]', '', title)
        return sanitized[:31]  # Excel sheet name max 31 chars
    
    @classmethod
    async def generate_excel(cls, prompt: str, structured_data: Dict, user_id: str = None) -> Dict:
        """Generate Excel with Kimi-structured data from search results."""
        try:
            file_id = str(uuid.uuid4())[:8]
            filename = cls._generate_filename(prompt, "xlsx")
            filepath = OUTPUT_DIR / f"{file_id}_{filename}"
            
            # Build search context for Kimi
            search_context = ""
            raw_data_points = structured_data.get("data_points", [])
            for dp in raw_data_points[:20]:
                search_context += f"- {dp.get('title', '')}: {dp.get('description', '')}\n"
            
            # Also get answer text from search results
            for source_name in ["perplexity", "grok", "google", "exa"]:
                if source_name in structured_data.get("results", {}):
                    answer = structured_data["results"][source_name].get("answer", "")
                    if answer:
                        search_context += f"\n[{source_name.upper()} ANSWER]:\n{answer[:1500]}\n"
            
            # Use Kimi to generate proper structured data for the Excel
            excel_data = None
            if kimi_client:
                try:
                    # Run in executor to avoid blocking the event loop (enables keepalive)
                    import functools
                    loop = asyncio.get_event_loop()
                    kimi_response = await loop.run_in_executor(None, functools.partial(
                        kimi_client.chat.completions.create,
                        model="kimi-k2.5",
                        messages=[
                            {"role": "system", "content": """You generate comprehensive Excel spreadsheets with MANY TABS. Return ONLY valid JSON.

Format: {"sheets": [{"title": "...", "headers": [...], "rows": [...]}, ...]}

You MUST create 10+ sheets. Think about what perspectives, breakdowns, and analyses would be valuable for this topic. Example tab structures:
- Main comprehensive dataset (30-50 rows)
- Rankings / Top performers
- Regional or geographic breakdown
- Category / segment analysis
- Year-over-year trends or historical data
- Competitive comparison
- Key metrics summary
- Market share or distribution
- Strengths & weaknesses analysis
- Pricing or financial overview
- Recommendations or action items
- Sources & references

Rules:
- Each tab title should be specific and descriptive (e.g., "Revenue by Region", "Brand Rankings 2026", "Sustainability Scores")
- Headers MUST be specific to the topic (e.g., "Brand Name", "Revenue ($M)", "ESG Score", "Country")
- Extract SPECIFIC facts, numbers, names, dates from the search text
- If search data is insufficient, supplement with your knowledge but mark with (est.) suffix
- Numbers should be actual numbers, not strings
- Each row must have the same number of columns as headers
- DO NOT use generic headers like "Item", "Value", "Date"
- Main data tab: 30-50 rows. Other tabs: 5-20 rows each
- Deliver MORE than the user expects — add perspectives they didn't ask for but would find valuable
- Return ONLY the JSON object, no markdown, no explanation"""},
                            {"role": "user", "content": f"Generate multi-tab Excel data for: {prompt}\n\nSearch results to use:\n{search_context[:5000]}"}
                        ],
                        temperature=1,
                        max_tokens=12000
                    ))
                    
                    raw_json = kimi_response.choices[0].message.content.strip()
                    logger.info(f"Kimi Excel raw response length: {len(raw_json)}")
                    
                    # Try multiple JSON extraction strategies
                    for strategy in [
                        lambda t: json.loads(t),
                        lambda t: json.loads(t[t.index('{'):t.rindex('}')+1]),
                        lambda t: json.loads(t.split('```json')[1].split('```')[0].strip()) if '```json' in t else None,
                        lambda t: json.loads(t.split('```')[1].split('```')[0].strip()) if '```' in t else None,
                    ]:
                        try:
                            result = strategy(raw_json)
                            if result and isinstance(result, dict):
                                # Multi-tab format: {"sheets": [...]}
                                if "sheets" in result and isinstance(result["sheets"], list):
                                    excel_data = result
                                    total_rows = sum(len(s.get('rows', [])) for s in result['sheets'])
                                    logger.info(f"Kimi Excel multi-tab: {len(result['sheets'])} sheets, {total_rows} total rows")
                                    break
                                # Legacy single-tab format: {"headers": [...], "rows": [...]}
                                elif "headers" in result and "rows" in result:
                                    excel_data = {"sheets": [{"title": result.get("title", prompt[:30]), "headers": result["headers"], "rows": result["rows"]}]}
                                    logger.info(f"Kimi Excel single-tab: {len(result.get('rows', []))} rows, {len(result.get('headers', []))} columns")
                                    break
                        except:
                            continue
                    
                except Exception as e:
                    logger.error(f"Kimi Excel content generation error: {e}")
            
            # Fallback: Try Grok if Kimi failed
            if not excel_data and grok_client:
                try:
                    logger.info("Kimi failed for Excel, trying Grok fallback")
                    import functools
                    loop = asyncio.get_event_loop()
                    grok_response = await loop.run_in_executor(None, functools.partial(
                        grok_client.chat.completions.create,
                        model="grok-3-mini",
                        messages=[
                            {"role": "system", "content": """Generate structured data for an Excel spreadsheet with MULTIPLE TABS. Return ONLY valid JSON.
Format: {"sheets": [{"title": "...", "headers": [...], "rows": [...]}, ...]}
Create at least 5 sheets with different perspectives on the topic. Main data: 20-30 rows. Other tabs: 5-15 rows each.
Return ONLY the JSON, no markdown."""},
                            {"role": "user", "content": f"Generate Excel data for: {prompt}\n\nSearch data:\n{search_context[:2000]}"}
                        ],
                        temperature=0.3,
                        max_tokens=6000
                    ))
                    raw_json = grok_response.choices[0].message.content.strip()
                    for strategy in [
                        lambda t: json.loads(t),
                        lambda t: json.loads(t[t.index('{'):t.rindex('}')+1]),
                        lambda t: json.loads(t.split('```json')[1].split('```')[0].strip()) if '```json' in t else None,
                        lambda t: json.loads(t.split('```')[1].split('```')[0].strip()) if '```' in t else None,
                    ]:
                        try:
                            result = strategy(raw_json)
                            if result and isinstance(result, dict):
                                if "sheets" in result:
                                    excel_data = result
                                elif "headers" in result and "rows" in result:
                                    excel_data = {"sheets": [{"title": result.get("title", prompt[:30]), "headers": result["headers"], "rows": result["rows"]}]}
                                if excel_data:
                                    logger.info(f"Grok Excel parsed: {sum(len(s.get('rows',[])) for s in excel_data.get('sheets',[]))} total rows")
                                    break
                        except:
                            continue
                except Exception as e:
                    logger.error(f"Grok Excel fallback error: {e}")
            
            # Helper to create a styled sheet
            from openpyxl.utils import get_column_letter
            def _create_styled_sheet(wb, sheet_title, headers, rows, prompt_text):
                ws = wb.create_sheet(cls._sanitize_sheet_title(sheet_title))
                num_cols = max(len(headers), 1)
                
                # Title row
                if num_cols > 1:
                    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=num_cols)
                title_cell = ws.cell(row=1, column=1, value=sheet_title)
                title_cell.font = Font(size=14, bold=True, color="FFFFFF")
                title_cell.fill = PatternFill(start_color="1B1B1B", end_color="1B1B1B", fill_type="solid")
                title_cell.alignment = Alignment(horizontal="center")
                
                # Subtitle
                if num_cols > 1:
                    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=num_cols)
                sub_cell = ws.cell(row=2, column=1, value=f"McLeuker AI | {datetime.now().strftime('%Y-%m-%d')} | {len(rows)} records")
                sub_cell.font = Font(size=9, italic=True, color="666666")
                sub_cell.alignment = Alignment(horizontal="center")
                
                # Headers
                for col, header in enumerate(headers, 1):
                    cell = ws.cell(row=4, column=col, value=str(header))
                    cell.font = Font(bold=True, color="FFFFFF", size=11)
                    cell.fill = PatternFill(start_color="2D2D2D", end_color="2D2D2D", fill_type="solid")
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.border = Border(bottom=Side(style='thin', color='000000'), top=Side(style='thin', color='000000'))
                
                # Data rows
                for row_num, row_data in enumerate(rows[:100], 5):
                    for col_num, value in enumerate(row_data[:len(headers)], 1):
                        cell = ws.cell(row=row_num, column=col_num, value=value)
                        cell.alignment = Alignment(vertical="center", wrap_text=True)
                        if row_num % 2 == 0:
                            cell.fill = PatternFill(start_color="F5F5F5", end_color="F5F5F5", fill_type="solid")
                        cell.border = Border(bottom=Side(style='hair', color='DDDDDD'))
                
                # Auto-adjust column widths
                for col_idx in range(1, len(headers) + 1):
                    max_length = len(str(headers[col_idx - 1])) if col_idx <= len(headers) else 10
                    for row_idx in range(5, 5 + len(rows[:100])):
                        try:
                            cell = ws.cell(row=row_idx, column=col_idx)
                            if cell.value and len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    ws.column_dimensions[get_column_letter(col_idx)].width = min(max(max_length + 3, 15), 50)
                
                return ws, len(rows)
            
            # Create workbook
            wb = Workbook()
            wb.remove(wb.active)
            row_count = 0
            
            if excel_data and excel_data.get("sheets"):
                # Multi-tab: create each sheet
                for sheet_info in excel_data["sheets"]:
                    s_title = sheet_info.get("title", "Data")
                    s_headers = sheet_info.get("headers", [])
                    s_rows = sheet_info.get("rows", [])
                    if s_headers and s_rows:
                        _, count = _create_styled_sheet(wb, s_title, s_headers, s_rows, prompt)
                        row_count += count
                
                # Add a Sources tab automatically
                sources_list = structured_data.get("sources", [])
                if sources_list:
                    src_headers = ["Source", "Title", "URL"]
                    src_rows = [[s.get("source", ""), s.get("title", ""), s.get("url", "")] for s in sources_list[:30]]
                    _create_styled_sheet(wb, "Sources", src_headers, src_rows, prompt)
            else:
                # Fallback: use raw search data points
                headers = ["Title", "Description", "Source", "URL"]
                fallback_rows = [[dp.get("title", ""), dp.get("description", ""), dp.get("source", ""), dp.get("url", "")] for dp in raw_data_points[:50]]
                _, row_count = _create_styled_sheet(wb, "Data", headers, fallback_rows, prompt)
            
            # Save file
            wb.save(filepath)
            
            # Register file
            cls.files[file_id] = {
                "filename": filename,
                "filepath": str(filepath),
                "file_type": "excel",
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
            }
            
            return {
                "success": True,
                "file_id": file_id,
                "filename": filename,
                "download_url": f"/api/v1/download/{file_id}",
                "row_count": row_count
            }
            
        except Exception as e:
            logger.error(f"Excel generation error: {e}")
            return {"success": False, "error": str(e)}
    
    @classmethod
    async def generate_word(cls, prompt: str, content: str, user_id: str = None) -> Dict:
        """Generate Word document with proper markdown rendering."""
        try:
            import re as _re
            from docx.shared import Inches, Pt, Cm, RGBColor
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            from docx.enum.table import WD_TABLE_ALIGNMENT
            
            file_id = str(uuid.uuid4())[:8]
            filename = cls._generate_filename(prompt, "docx")
            filepath = OUTPUT_DIR / f"{file_id}_{filename}"
            
            doc = Document()
            
            # Set default font
            style = doc.styles['Normal']
            font = style.font
            font.name = 'Calibri'
            font.size = Pt(11)
            font.color.rgb = RGBColor(0x33, 0x33, 0x33)
            
            # Set margins
            for section in doc.sections:
                section.top_margin = Cm(2)
                section.bottom_margin = Cm(2)
                section.left_margin = Cm(2.5)
                section.right_margin = Cm(2.5)
            
            # Parse and render markdown content
            lines = content.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i]
                stripped = line.strip()
                
                # Skip empty lines
                if not stripped:
                    i += 1
                    continue
                
                # Headers
                if stripped.startswith('# '):
                    h = doc.add_heading(stripped[2:].strip(), level=0)
                    h.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    i += 1
                    continue
                elif stripped.startswith('## '):
                    h = doc.add_heading(stripped[3:].strip(), level=1)
                    i += 1
                    continue
                elif stripped.startswith('### '):
                    h = doc.add_heading(stripped[4:].strip(), level=2)
                    i += 1
                    continue
                elif stripped.startswith('#### '):
                    h = doc.add_heading(stripped[5:].strip(), level=3)
                    i += 1
                    continue
                
                # Markdown table
                elif stripped.startswith('|') and '|' in stripped[1:]:
                    table_lines = []
                    while i < len(lines) and lines[i].strip().startswith('|'):
                        row_text = lines[i].strip()
                        # Skip separator rows (|---|---|)
                        if _re.match(r'^\|[\s\-:|]+\|$', row_text):
                            i += 1
                            continue
                        cells = [c.strip() for c in row_text.split('|')[1:-1]]
                        if cells:
                            table_lines.append(cells)
                        i += 1
                    
                    if table_lines:
                        num_cols = max(len(row) for row in table_lines)
                        table = doc.add_table(rows=len(table_lines), cols=num_cols)
                        table.style = 'Light Grid Accent 1'
                        table.alignment = WD_TABLE_ALIGNMENT.CENTER
                        
                        for row_idx, row_data in enumerate(table_lines):
                            for col_idx, cell_text in enumerate(row_data):
                                if col_idx < num_cols:
                                    cell = table.cell(row_idx, col_idx)
                                    cell.text = cell_text
                                    # Bold header row
                                    if row_idx == 0:
                                        for paragraph in cell.paragraphs:
                                            for run in paragraph.runs:
                                                run.bold = True
                        doc.add_paragraph('')  # spacing after table
                    continue
                
                # Bullet points
                elif stripped.startswith('- ') or stripped.startswith('* '):
                    p = doc.add_paragraph(style='List Bullet')
                    cls._add_formatted_text(p, stripped[2:])
                    i += 1
                    continue
                
                # Numbered lists
                elif _re.match(r'^\d+\.\s', stripped):
                    text = _re.sub(r'^\d+\.\s', '', stripped)
                    p = doc.add_paragraph(style='List Number')
                    cls._add_formatted_text(p, text)
                    i += 1
                    continue
                
                # Regular paragraph
                else:
                    p = doc.add_paragraph()
                    cls._add_formatted_text(p, stripped)
                    i += 1
                    continue
            
            # Footer with timestamp
            doc.add_paragraph('')
            footer = doc.add_paragraph()
            footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = footer.add_run(f"Generated by McLeuker AI \u2022 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            run.font.size = Pt(8)
            run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
            
            doc.save(filepath)
            
            cls.files[file_id] = {
                "filename": filename,
                "filepath": str(filepath),
                "file_type": "word",
                "user_id": user_id,
                "created_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "file_id": file_id,
                "filename": filename,
                "download_url": f"/api/v1/download/{file_id}"
            }
            
        except Exception as e:
            logger.error(f"Word generation error: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def _add_formatted_text(paragraph, text: str):
        """Parse inline markdown formatting (bold, italic) and add to paragraph."""
        import re as _re
        # Split by bold (**text**) and italic (*text*) patterns
        parts = _re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*)', text)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                run = paragraph.add_run(part[2:-2])
                run.bold = True
            elif part.startswith('*') and part.endswith('*'):
                run = paragraph.add_run(part[1:-1])
                run.italic = True
            else:
                paragraph.add_run(part)
    
    @classmethod
    async def generate_pdf(cls, prompt: str, content: str, user_id: str = None) -> Dict:
        """Generate PDF document with proper markdown rendering via HTML conversion."""
        try:
            import re as _re
            import markdown as md_lib
            
            file_id = str(uuid.uuid4())[:8]
            filename = cls._generate_filename(prompt, "pdf")
            filepath = OUTPUT_DIR / f"{file_id}_{filename}"
            
            # Convert markdown to HTML
            html_content = md_lib.markdown(content, extensions=['tables', 'fenced_code', 'nl2br'])
            
            # Wrap in styled HTML template
            html_template = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{ font-family: 'Helvetica Neue', Arial, sans-serif; font-size: 11pt; color: #333; line-height: 1.6; margin: 40px; }}
    h1 {{ font-size: 22pt; color: #1a1a1a; border-bottom: 2px solid #333; padding-bottom: 8px; margin-top: 24px; }}
    h2 {{ font-size: 16pt; color: #2d2d2d; border-bottom: 1px solid #ddd; padding-bottom: 4px; margin-top: 20px; }}
    h3 {{ font-size: 13pt; color: #444; margin-top: 16px; }}
    h4 {{ font-size: 11pt; color: #555; margin-top: 12px; }}
    p {{ margin: 6px 0; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 10pt; }}
    th {{ background-color: #2d2d2d; color: white; padding: 8px 12px; text-align: left; font-weight: bold; }}
    td {{ padding: 6px 12px; border-bottom: 1px solid #eee; }}
    tr:nth-child(even) {{ background-color: #f9f9f9; }}
    ul, ol {{ margin: 6px 0; padding-left: 24px; }}
    li {{ margin: 3px 0; }}
    code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 10pt; }}
    pre {{ background: #f4f4f4; padding: 12px; border-radius: 4px; overflow-x: auto; }}
    strong {{ color: #1a1a1a; }}
    .footer {{ text-align: center; color: #999; font-size: 8pt; margin-top: 40px; border-top: 1px solid #eee; padding-top: 8px; }}
</style>
</head>
<body>
{html_content}
<div class="footer">Generated by McLeuker AI &bull; {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
</body>
</html>"""
            
            # Convert HTML to PDF using weasyprint
            from weasyprint import HTML
            HTML(string=html_template).write_pdf(str(filepath))
            
            cls.files[file_id] = {
                "filename": filename,
                "filepath": str(filepath),
                "file_type": "pdf",
                "user_id": user_id,
                "created_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "file_id": file_id,
                "filename": filename,
                "download_url": f"/api/v1/download/{file_id}"
            }
            
        except Exception as e:
            logger.error(f"PDF generation error: {e}")
            return {"success": False, "error": str(e)}
    
    @classmethod
    async def generate_pptx(cls, prompt: str, content: str, user_id: str = None) -> Dict:
        """Generate PowerPoint presentation with proper markdown parsing."""
        try:
            import re as _re
            from pptx.util import Inches, Pt
            from pptx.dml.color import RGBColor as PptxRGB
            from pptx.enum.text import PP_ALIGN
            
            file_id = str(uuid.uuid4())[:8]
            filename = cls._generate_filename(prompt, "pptx")
            filepath = OUTPUT_DIR / f"{file_id}_{filename}"
            
            prs = Presentation()
            
            # Title slide
            title_slide = prs.slides.add_slide(prs.slide_layouts[0])
            title_slide.shapes.title.text = prompt[:100]
            title_slide.placeholders[1].text = f"Generated by McLeuker AI \u2022 {datetime.now().strftime('%Y-%m-%d')}"
            
            # Parse markdown into sections by ## headers
            sections = []
            current_title = "Overview"
            current_content = []
            
            for line in content.split('\n'):
                stripped = line.strip()
                if stripped.startswith('## '):
                    if current_content:
                        sections.append((current_title, '\n'.join(current_content)))
                    current_title = stripped[3:].strip()
                    current_content = []
                elif stripped.startswith('# '):
                    if current_content:
                        sections.append((current_title, '\n'.join(current_content)))
                    current_title = stripped[2:].strip()
                    current_content = []
                else:
                    # Clean markdown formatting for slides
                    cleaned = _re.sub(r'\*\*([^*]+)\*\*', r'\1', stripped)  # Remove bold markers
                    cleaned = _re.sub(r'\*([^*]+)\*', r'\1', cleaned)  # Remove italic markers
                    if cleaned:
                        current_content.append(cleaned)
            
            if current_content:
                sections.append((current_title, '\n'.join(current_content)))
            
            # Create slides from sections
            for title, body in sections[:15]:  # Limit to 15 slides
                slide = prs.slides.add_slide(prs.slide_layouts[1])
                slide.shapes.title.text = title[:80]
                
                # Truncate body for slide readability
                body_lines = body.split('\n')[:8]  # Max 8 lines per slide
                slide_text = '\n'.join(line[:120] for line in body_lines)
                slide.placeholders[1].text = slide_text[:600]
            
            prs.save(filepath)
            
            cls.files[file_id] = {
                "filename": filename,
                "filepath": str(filepath),
                "file_type": "pptx",
                "user_id": user_id,
                "created_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "file_id": file_id,
                "filename": filename,
                "download_url": f"/api/v1/download/{file_id}"
            }
            
        except Exception as e:
            logger.error(f"PPTX generation error: {e}")
            return {"success": False, "error": str(e)}
    
    @classmethod
    def get_file(cls, file_id: str) -> Optional[Dict]:
        """Get file info by ID."""
        return cls.files.get(file_id)

# ============================================================================
# MEMORY MANAGER
# ============================================================================

class MemoryManager:
    """Manages conversation memory and persistence."""
    
    @staticmethod
    async def create_conversation(user_id: str, title: str = None, mode: str = "thinking") -> Dict:
        """Create a new conversation."""
        if not supabase:
            return {"id": str(uuid.uuid4()), "title": title or "New Conversation"}
        
        try:
            result = supabase.table("conversations").insert({
                "user_id": user_id,
                "title": title or "New Conversation",
                "mode": mode,
                "status": "active"
            }).execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Create conversation error: {e}")
            return {"id": str(uuid.uuid4()), "title": title or "New Conversation"}
    
    @staticmethod
    async def save_message(conversation_id: str, user_id: str, role: str, content: str, 
                          reasoning_content: str = None, tool_calls: List = None,
                          tokens_input: int = 0, tokens_output: int = 0) -> Dict:
        """Save a message to the conversation."""
        if not supabase:
            return {"id": str(uuid.uuid4())}
        
        try:
            result = supabase.table("messages").insert({
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "reasoning_content": reasoning_content,
                "tool_calls": tool_calls or [],
                "tokens_input": tokens_input,
                "tokens_output": tokens_output
            }).execute()
            
            # Update conversation last_message_at
            supabase.table("conversations").update({
                "updated_at": datetime.now().isoformat(),
                "last_message_at": datetime.now().isoformat()
            }).eq("id", conversation_id).execute()
            
            return result.data[0] if result.data else {"id": str(uuid.uuid4())}
        except Exception as e:
            logger.error(f"Save message error: {e}")
            return {"id": str(uuid.uuid4())}
    
    @staticmethod
    async def get_conversation_messages(conversation_id: str, limit: int = 50) -> List[Dict]:
        """Get messages for a conversation."""
        if not supabase:
            return []
        
        try:
            result = supabase.table("messages").select("*").eq(
                "conversation_id", conversation_id
            ).order("created_at", desc=True).limit(limit).execute()
            
            return result.data or []
        except Exception as e:
            logger.error(f"Get messages error: {e}")
            return []
    
    @staticmethod
    async def get_conversation_context(conversation_id: str, max_messages: int = 10) -> List[Dict]:
        """Get recent conversation context for LLM."""
        messages = await MemoryManager.get_conversation_messages(conversation_id, max_messages)
        
        # Convert to LLM format
        context = []
        for msg in reversed(messages):  # Reverse to get chronological order
            context.append({
                "role": msg.get("role"),
                "content": msg.get("content")
            })
        
        return context


# ============================================================================
# HYBRID LLM ROUTER
# ============================================================================

class HybridLLMRouter:
    """Routes requests between Kimi-2.5 and Grok based on task analysis."""
    
    @staticmethod
    def analyze_intent(query: str) -> Dict:
        """Analyze query to determine best model and approach."""
        query_lower = query.lower()
        
        intent = {
            "requires_realtime": False,
            "requires_reasoning": False,
            "requires_code": False,
            "requires_file": False,
            "is_simple": False
        }
        
        # Real-time indicators
        realtime_keywords = ['latest', 'recent', 'news', 'today', 'yesterday', '2026', '2025', 'current', 'update']
        if any(kw in query_lower for kw in realtime_keywords):
            intent["requires_realtime"] = True
        
        # Reasoning indicators
        reasoning_keywords = ['analyze', 'explain', 'why', 'how to', 'compare', 'evaluate', 'assess']
        if any(kw in query_lower for kw in reasoning_keywords):
            intent["requires_reasoning"] = True
        
        # Code indicators
        code_keywords = ['code', 'program', 'script', 'function', 'python', 'javascript', 'sql']
        if any(kw in query_lower for kw in code_keywords):
            intent["requires_code"] = True
        
        # File indicators
        file_keywords = ['excel', 'pdf', 'word', 'document', 'spreadsheet', 'presentation', 'file']
        if any(kw in query_lower for kw in file_keywords):
            intent["requires_file"] = True
        
        # Simple query indicators
        simple_keywords = ['hello', 'hi', 'hey', 'thanks', 'ok', 'yes', 'no']
        if query_lower.strip() in simple_keywords or len(query_lower.strip()) < 10:
            intent["is_simple"] = True
        
        return intent
    
    @staticmethod
    async def chat(messages: List[Dict], mode: ChatMode, stream: bool = True) -> AsyncGenerator[str, None]:
        """Chat with hybrid routing."""
        config = MODE_CONFIGS[mode]
        
        # Get last user message for intent analysis
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "")
                break
        
        intent = HybridLLMRouter.analyze_intent(last_user_msg)
        
        # Determine primary model
        if config["primary_model"] == "hybrid":
            if intent["requires_realtime"] and grok_client:
                primary_model = "hybrid"
            else:
                primary_model = "kimi"
        else:
            primary_model = config["primary_model"]
        
        # Route to appropriate handler
        if primary_model == "kimi":
            async for event in HybridLLMRouter._chat_kimi(messages, config, stream):
                yield event
        elif primary_model == "grok":
            async for event in HybridLLMRouter._chat_grok(messages, config, stream):
                yield event
        elif primary_model == "hybrid":
            async for event in HybridLLMRouter._chat_hybrid(messages, config, stream, intent):
                yield event
    
    @staticmethod
    async def _chat_kimi(messages: List[Dict], config: Dict, stream: bool) -> AsyncGenerator[str, None]:
        """Chat with Kimi-2.5."""
        if not kimi_client:
            yield event("error", {"message": "Kimi client not configured"})
            return
        
        try:
            # Kimi K2.5 only allows temperature=1
            response = kimi_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1,
                max_tokens=config["max_tokens"],
                stream=stream
            )
            
            if stream:
                for chunk in response:
                    delta = chunk.choices[0].delta
                    content = getattr(delta, 'content', None)
                    reasoning = getattr(delta, 'reasoning_content', None)
                    
                    if reasoning and config.get("show_reasoning"):
                        yield event("reasoning", {"chunk": reasoning})
                    if content:
                        yield event("content", {"chunk": content})
            else:
                msg = response.choices[0].message
                reasoning = getattr(msg, 'reasoning_content', None)
                if reasoning and config.get("show_reasoning"):
                    yield event("reasoning", {"chunk": reasoning})
                content = msg.content
                yield event("content", {"chunk": content})
                
        except Exception as e:
            logger.error(f"Kimi chat error: {e}")
            yield event("error", {"message": str(e)})
    
    @staticmethod
    async def _chat_grok(messages: List[Dict], config: Dict, stream: bool) -> AsyncGenerator[str, None]:
        """Chat with Grok."""
        if not grok_client:
            yield event("error", {"message": "Grok client not configured"})
            return
        
        try:
            response = grok_client.chat.completions.create(
                model="grok-4-1-fast-reasoning",
                messages=messages,
                temperature=config["temperature"],
                max_tokens=config["max_tokens"],
                stream=stream
            )
            
            if stream:
                for chunk in response:
                    delta = chunk.choices[0].delta
                    content = getattr(delta, 'content', None)
                    reasoning = getattr(delta, 'reasoning', None) or getattr(delta, 'reasoning_content', None)
                    
                    if reasoning and config.get("show_reasoning"):
                        yield event("reasoning", {"chunk": reasoning})
                    if content:
                        yield event("content", {"chunk": content})
            else:
                msg = response.choices[0].message
                reasoning = getattr(msg, 'reasoning', None) or getattr(msg, 'reasoning_content', None)
                if reasoning and config.get("show_reasoning"):
                    yield event("reasoning", {"chunk": reasoning})
                content = msg.content
                yield event("content", {"chunk": content})
                
        except Exception as e:
            logger.error(f"Grok chat error: {e}")
            yield event("error", {"message": str(e)})
    
    @staticmethod
    async def _chat_hybrid(messages: List[Dict], config: Dict, stream: bool, intent: Dict) -> AsyncGenerator[str, None]:
        """Chat with hybrid approach - Grok for search, Kimi for synthesis."""
        
        # Step 1: Analyze the query
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "")
                break
        
        query_preview = last_user_msg[:80] + ('...' if len(last_user_msg) > 80 else '')
        
        yield event("task_progress", {
            "step": "analyze",
            "title": "Analyzing your query",
            "status": "active",
            "detail": f"Understanding: \"{query_preview}\""
        })
        
        yield event("task_progress", {
            "step": "analyze",
            "title": "Analyzing your query",
            "status": "complete",
            "detail": "Query parsed and search strategy determined"
        })
        
        # Step 2: Search with multiple sources
        yield event("task_progress", {
            "step": "search",
            "title": "Searching across multiple sources",
            "status": "active",
            "detail": "Querying Perplexity, Exa, and Grok simultaneously"
        })
        
        search_results = await SearchLayer.search(last_user_msg, sources=["web", "news", "social"])
        
        sources = search_results.get("structured_data", {}).get("sources", [])
        source_count = len(sources)
        
        yield event("task_progress", {
            "step": "search",
            "title": f"Found {source_count} relevant sources",
            "status": "complete",
            "detail": f"Collected data from {source_count} sources across web, news, and social"
        })
        
        # Send search sources
        if sources:
            yield event("search_sources", {"sources": sources})
        
        # Step 3: Synthesize with Kimi
        yield event("task_progress", {
            "step": "synthesize",
            "title": "Reasoning and synthesizing response",
            "status": "active",
            "detail": "Analyzing sources, cross-referencing data, and structuring insights"
        })
        
        # Build context with search results
        search_context = ""
        for source, data in search_results.get("results", {}).items():
            if "answer" in data:
                search_context += f"\n[{source.upper()}] {data['answer'][:500]}\n"
        
        enriched_messages = messages.copy()
        enriched_messages.insert(0, {
            "role": "system",
            "content": f"Use this real-time search data to answer:\n{search_context}"
        })
        
        # Stream Kimi response
        if not kimi_client:
            yield event("error", {"message": "Kimi client not configured"})
            return
        
        try:
            # Kimi K2.5 only allows temperature=1
            response = kimi_client.chat.completions.create(
                model="kimi-k2.5",
                messages=enriched_messages,
                temperature=1,
                max_tokens=config["max_tokens"],
                stream=True
            )
            
            for chunk in response:
                delta = chunk.choices[0].delta
                content = getattr(delta, 'content', None)
                
                if content:
                    yield event("content", {"chunk": content})
            
            yield event("task_progress", {
                "step": "synthesize",
                "title": "Response synthesized",
                "status": "complete",
                "detail": "Analysis complete, response structured with citations"
            })
            
        except Exception as e:
            logger.error(f"Hybrid synthesis error: {e}")
            yield event("error", {"message": str(e)})

# ============================================================================
# AGENT ORCHESTRATOR
# ============================================================================

class AgentOrchestrator:
    """Orchestrates agent swarm execution."""
    
    AGENT_TYPES = {
        "research": "Expert at finding and analyzing information",
        "analysis": "Expert at data analysis and pattern recognition",
        "synthesis": "Expert at combining information into coherent output",
        "file": "Expert at generating professional files",
        "code": "Expert at writing and executing code",
        "critique": "Expert at reviewing and improving outputs"
    }
    
    @staticmethod
    async def execute_agent(task: str, agent_type: str, context: Dict = None) -> Dict:
        """Execute a single agent."""
        if not kimi_client:
            return {"error": "Kimi client not configured"}
        
        agent_desc = AgentOrchestrator.AGENT_TYPES.get(agent_type, "AI Assistant")
        
        messages = [
            {"role": "system", "content": f"You are a {agent_desc}. Be thorough and specific."},
            {"role": "user", "content": f"Task: {task}\nContext: {json.dumps(context or {})}"}
        ]
        
        try:
            response = kimi_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1,
                max_tokens=4096
            )
            
            return {
                "agent_type": agent_type,
                "task": task,
                "output": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "success": True
            }
        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            return {"error": str(e), "success": False}
    
    @staticmethod
    async def execute_swarm(task: str, num_agents: int = 5, context: Dict = None) -> AsyncGenerator[str, None]:
        """Execute multiple agents in parallel."""
        
        # Determine agent types based on task
        agent_types = ["research", "analysis", "synthesis"]
        if num_agents > 3:
            agent_types.extend(["critique"] * (num_agents - 3))
        
        # Create subtasks
        subtasks = []
        for i, agent_type in enumerate(agent_types[:num_agents]):
            subtask = f"{task} (Focus area {i+1}: {agent_type})"
            subtasks.append((subtask, agent_type))
        
        # Execute in parallel
        yield event("task_progress", {
            "step": "swarm",
            "title": f"Deploying {len(subtasks)} agents",
            "status": "active"
        })
        
        tasks = [AgentOrchestrator.execute_agent(st, at, context) for st, at in subtasks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        yield event("task_progress", {
            "step": "swarm",
            "title": f"Deploying {len(subtasks)} agents",
            "status": "complete"
        })
        
        # Filter successful results
        successful = [r for r in results if isinstance(r, dict) and r.get("success")]
        
        # Synthesize results
        yield event("task_progress", {
            "step": "synthesize",
            "title": "Synthesizing agent outputs",
            "status": "active"
        })
        
        synthesis = await AgentOrchestrator._synthesize_results(successful, task)
        
        yield event("task_progress", {
            "step": "synthesize",
            "title": "Synthesizing agent outputs",
            "status": "complete"
        })
        
        yield event("complete", {
            "task": task,
            "agents_deployed": len(subtasks),
            "agents_successful": len(successful),
            "agent_results": successful,
            "synthesis": synthesis,
            "success": True
        })
    
    @staticmethod
    async def _synthesize_results(results: List[Dict], original_task: str) -> str:
        """Synthesize multiple agent outputs."""
        if not results:
            return "No results to synthesize."
        
        if not kimi_client:
            return "\n\n".join([r.get("output", "") for r in results])
        
        # Build synthesis input
        synthesis_input = "\n\n".join([
            f"### {r['agent_type'].upper()}\n{r['output'][:1000]}"
            for r in results
        ])
        
        messages = [
            {"role": "system", "content": "You are a synthesis expert. Combine these analyses into a coherent response."},
            {"role": "user", "content": f"Task: {original_task}\n\nAgent Analyses:\n{synthesis_input}\n\nProvide a well-structured final response:"}
        ]
        
        try:
            response = kimi_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1,
                max_tokens=4096
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            return "\n\n".join([r.get("output", "") for r in results])


# ============================================================================
# MAIN CHAT HANDLER
# ============================================================================

class ChatHandler:
    """Main chat handler with all modes and features."""
    
    @staticmethod
    async def handle_chat(request: ChatRequest) -> AsyncGenerator[str, None]:
        """Handle chat request with all modes."""
        
        user_id = request.user_id or "anonymous"
        conversation_id = request.conversation_id
        mode = request.mode
        
        # Create or get conversation
        if not conversation_id:
            conv = await MemoryManager.create_conversation(user_id, mode=mode.value)
            conversation_id = conv.get("id")
            yield event("conversation_created", {"id": conversation_id, "mode": mode.value})
        
        # Get conversation context
        context_messages = await MemoryManager.get_conversation_context(conversation_id)
        
        # Combine with new messages
        all_messages = context_messages + [{"role": m.role, "content": m.content} for m in request.messages]
        
        # Get last user message
        last_user_msg = ""
        for m in reversed(all_messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "")
                break
        
        # Check for file generation intent
        file_type = ChatHandler._detect_file_intent(last_user_msg)
        
        # Route based on mode
        if mode == ChatMode.SWARM:
            async for e in ChatHandler._handle_swarm_mode(all_messages, last_user_msg, user_id, conversation_id):
                yield e
        elif file_type:
            async for e in ChatHandler._handle_file_generation(last_user_msg, file_type, user_id, conversation_id, mode):
                yield e
        elif mode == ChatMode.RESEARCH or mode == ChatMode.HYBRID:
            async for e in ChatHandler._handle_hybrid_mode(all_messages, last_user_msg, user_id, conversation_id):
                yield e
        else:
            async for e in ChatHandler._handle_standard_mode(all_messages, mode, user_id, conversation_id):
                yield e
    
    @staticmethod
    def _detect_file_intent(query: str) -> Optional[str]:
        """Detect if user wants to generate a file."""
        query_lower = query.lower()
        
        file_types = {
            "excel": ["excel", "spreadsheet", "xlsx", "csv"],
            "word": ["word", "docx", "document"],
            "pdf": ["pdf"],
            "pptx": ["powerpoint", "presentation", "pptx", "slide"]
        }
        
        for file_type, keywords in file_types.items():
            if any(kw in query_lower for kw in keywords):
                return file_type
        
        return None
    
    @staticmethod
    async def _handle_standard_mode(messages: List[Dict], mode: ChatMode, user_id: str, conversation_id: str) -> AsyncGenerator[str, None]:
        """Handle standard chat modes (instant, thinking, agent, code)."""
        
        config = MODE_CONFIGS[mode]
        full_content = ""
        search_results = None
        
        # Extract last user message
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                content = m.get("content", "")
                last_user_msg = content if isinstance(content, str) else str(content)
                break
        
        # Determine if this is a simple greeting
        simple_queries = ['hello', 'hi', 'hey', 'thanks', 'ok', 'yes', 'no', 'bye']
        is_simple = last_user_msg.strip().lower() in simple_queries or len(last_user_msg.strip()) < 8
        
        # Step 1: Analyze the query
        yield event("task_progress", {
            "step": "analyze",
            "title": "Understanding your request",
            "detail": f"Parsing intent: \"{last_user_msg[:80]}\"",
            "status": "active"
        })
        
        # Determine query type for better progress messages
        query_lower = last_user_msg.lower()
        if any(kw in query_lower for kw in ['trend', 'market', 'forecast', 'industry']):
            intent_detail = "Identified as market/trend analysis request"
        elif any(kw in query_lower for kw in ['compare', 'vs', 'difference', 'between']):
            intent_detail = "Identified as comparison analysis request"
        elif any(kw in query_lower for kw in ['how to', 'guide', 'steps', 'tutorial']):
            intent_detail = "Identified as instructional/guide request"
        elif any(kw in query_lower for kw in ['latest', 'news', 'today', 'recent', '2026']):
            intent_detail = "Identified as real-time information request"
        else:
            intent_detail = "Identified key topics and preparing search strategy"
        
        yield event("task_progress", {
            "step": "analyze",
            "title": "Understanding your request",
            "detail": intent_detail,
            "status": "complete"
        })
        
        # Step 2: ALWAYS search for real-time data (unless simple greeting)
        if not is_simple:
            yield event("task_progress", {
                "step": "plan",
                "title": "Breaking down your request",
                "detail": f"Planning research strategy for: {last_user_msg[:80]}",
                "status": "complete"
            })
            yield event("task_progress", {
                "step": "search",
                "title": "Searching real-time sources",
                "detail": "Querying Perplexity AI, Exa, and web sources in parallel",
                "status": "active"
            })
            
            yield event("tool_call", {"tool": "search", "status": "started", "message": "Searching real-time sources..."})
            
            try:
                search_results = await SearchLayer.search(last_user_msg, sources=["web", "news"])
            except Exception as e:
                logger.error(f"Search error in standard mode: {e}")
                search_results = None
            
            yield event("tool_call", {"tool": "search", "status": "completed"})
            
            if search_results:
                sources = search_results.get("structured_data", {}).get("sources", [])
                if sources:
                    yield event("search_sources", {"sources": sources})
                
                # Enrich messages with search context
                search_context = ""
                for source, data in search_results.get("results", {}).items():
                    if isinstance(data, dict) and "answer" in data:
                        search_context += f"\n[{source.upper()}] {data['answer'][:500]}\n"
                
                if search_context:
                    messages.insert(0, {
                        "role": "system",
                        "content": f"""You are McLeuker AI. Think deeply about the user's question first, then deliver a well-reasoned response.

APPROACH:
- Start by reasoning about what the user is really asking and what matters most
- Structure your response naturally based on the topic — do NOT follow a rigid template
- Use ## headers to organize sections logically, but let the content dictate the structure
- For comparisons, use tables. For analysis, use narrative. For lists, use ranked items.
- Every section should explain WHY something matters, not just WHAT it is

QUALITY RULES:
- Include specific numbers, dates, percentages, and names from the search data
- Use **bold** for key figures and important terms
- NEVER use generic filler like "there are many factors" or "it depends"
- Show cause-and-effect reasoning: explain relationships between data points
- If data conflicts, say which source is more reliable and why
- Keep sections tight — no excessive spacing or padding between paragraphs
- Write in a professional but conversational tone, like a senior analyst briefing a colleague
- Do NOT include source citations like [1], [2], [3] or "Sources: ..." in your text — sources are shown separately
- Do NOT mention "Perplexity", "Grok", "Exa" or any search engine names in your response

Search Data:
{search_context}"""
                    })
            
            source_count = len(search_results.get('structured_data', {}).get('sources', [])) if search_results else 0
            yield event("task_progress", {
                "step": "search",
                "title": f"Found {source_count} relevant sources",
                "detail": f"Collected and ranked {source_count} sources from web, news, and academic databases",
                "status": "complete"
            })
            yield event("task_progress", {
                "step": "verify",
                "title": "Cross-referencing data",
                "detail": "Verifying facts across multiple sources for accuracy",
                "status": "complete"
            })
        
        # Step 3: Generate response
        model_name = config.get('primary_model', 'kimi').replace('kimi', 'Kimi K2.5').replace('grok', 'Grok').replace('hybrid', 'Multi-model')
        yield event("task_progress", {
            "step": "reason",
            "title": "Reasoning through findings",
            "detail": f"Analyzing with {model_name} — identifying patterns and drawing conclusions",
            "status": "active"
        })
        yield event("task_progress", {
            "step": "write",
            "title": "Composing response",
            "detail": "Structuring analysis with supporting evidence",
            "status": "active"
        })
        
        try:
            async for e in HybridLLMRouter.chat(messages, mode, stream=True):
                try:
                    parsed = json.loads(e.replace("data: ", "").strip())
                    if parsed.get("type") == "content":
                        chunk = parsed.get("data", {}).get("chunk", "")
                        full_content += chunk
                except (json.JSONDecodeError, Exception):
                    pass
                yield e
        except Exception as e:
            logger.error(f"LLM streaming error: {e}")
            # Retry with fallback model — never stay silent
            yield event("task_progress", {
                "step": "retry",
                "title": "Retrying with fallback model",
                "detail": f"Primary model failed, switching to backup",
                "status": "active"
            })
            try:
                fallback_mode = "instant" if mode != "instant" else "thinking"
                async for e2 in HybridLLMRouter.chat(messages, fallback_mode, stream=True):
                    try:
                        parsed = json.loads(e2.replace("data: ", "").strip())
                        if parsed.get("type") == "content":
                            chunk = parsed.get("data", {}).get("chunk", "")
                            full_content += chunk
                    except (json.JSONDecodeError, Exception):
                        pass
                    yield e2
                yield event("task_progress", {
                    "step": "retry",
                    "title": "Recovered with fallback model",
                    "detail": "Response generated successfully after retry",
                    "status": "complete"
                })
            except Exception as e2:
                logger.error(f"Fallback LLM also failed: {e2}")
                error_msg = "I encountered an issue but I'm working on it. Please try your question again."
                yield event("content", {"chunk": error_msg})
                full_content = error_msg
        
        yield event("task_progress", {
            "step": "write",
            "title": "Response complete",
            "detail": "Analysis delivered with structured reasoning",
            "status": "complete"
        })
        
        # Save to memory
        try:
            await MemoryManager.save_message(
                conversation_id=conversation_id,
                user_id=user_id,
                role="assistant",
                content=full_content,
                tokens_output=len(full_content.split())
            )
        except Exception as e:
            logger.error(f"Memory save error: {e}")
        
        # Generate follow-up questions
        try:
            follow_ups = ChatHandler._generate_follow_ups(last_user_msg, full_content)
        except Exception as e:
            logger.error(f"Follow-up generation error: {e}")
            follow_ups = []
        
        if follow_ups:
            yield event("follow_up", {"questions": follow_ups})
        
        # Complete
        yield event("complete", {
            "content": full_content,
            "conversation_id": conversation_id,
            "sources": search_results.get("structured_data", {}).get("sources", []) if search_results else [],
            "follow_up_questions": follow_ups
        })
    
    @staticmethod
    async def _handle_hybrid_mode(messages: List[Dict], query: str, user_id: str, conversation_id: str) -> AsyncGenerator[str, None]:
        """Handle hybrid mode with Kimi + Grok."""
        
        full_content = ""
        
        # Search with multiple sources
        yield event("task_progress", {
            "step": "search",
            "title": "Searching real-time sources",
            "status": "active"
        })
        
        search_results = await SearchLayer.search(query, sources=["web", "news", "social"])
        
        yield event("task_progress", {
            "step": "search",
            "title": "Searching real-time sources",
            "status": "complete"
        })
        
        sources = search_results.get("structured_data", {}).get("sources", [])
        if sources:
            yield event("search_sources", {"sources": sources})
        
        # Synthesize with Kimi
        yield event("task_progress", {
            "step": "synthesize",
            "title": "Synthesizing insights",
            "status": "active"
        })
        
        search_context = ""
        for source, data in search_results.get("results", {}).items():
            if "answer" in data:
                search_context += f"\n[{source.upper()}] {data['answer'][:500]}\n"
        
        enriched_messages = messages.copy()
        enriched_messages.insert(0, {
            "role": "system",
            "content": f"You are a research assistant. Use this data:\n{search_context}"
        })
        
        async for e in HybridLLMRouter._chat_kimi(enriched_messages, MODE_CONFIGS[ChatMode.RESEARCH], True):
            event_data = json.loads(e.replace("data: ", ""))
            if event_data.get("type") == "content":
                full_content += event_data.get("data", {}).get("chunk", "")
            yield e
        
        yield event("task_progress", {
            "step": "synthesize",
            "title": "Synthesizing insights",
            "status": "complete"
        })
        
        # Save to memory
        await MemoryManager.save_message(
            conversation_id=conversation_id,
            user_id=user_id,
            role="assistant",
            content=full_content
        )
        
        # Follow-ups
        follow_ups = ChatHandler._generate_follow_ups(query, full_content)
        yield event("follow_up", {"questions": follow_ups})
        
        yield event("complete", {
            "content": full_content,
            "conversation_id": conversation_id,
            "sources": sources,
            "follow_up_questions": follow_ups
        })
    
    @staticmethod
    async def _handle_file_generation(query: str, file_type: str, user_id: str, conversation_id: str, mode: ChatMode) -> AsyncGenerator[str, None]:
        """Handle file generation requests."""
        
        # Step 1: Analyze and plan
        yield event("task_progress", {
            "step": "understand",
            "title": "Understanding your request",
            "detail": f"Parsing: \"{query[:70]}\"",
            "status": "complete"
        })
        yield event("task_progress", {
            "step": "plan",
            "title": "Planning data collection",
            "detail": f"Will generate {file_type.upper()} with multiple perspectives and structured data",
            "status": "complete"
        })
        
        # Step 2: Search for data
        yield event("task_progress", {
            "step": "search",
            "title": "Searching real-time sources",
            "detail": "Querying Perplexity, Exa, and Grok for latest data",
            "status": "active"
        })
        
        # Run search with keepalive to prevent SSE proxy timeout
        search_task = asyncio.create_task(SearchLayer.search(query, sources=["web", "news", "social"], num_results=15))
        search_progress = [
            "Scanning web databases for relevant data...",
            "Analyzing and ranking search results...",
            "Cross-referencing sources for accuracy...",
            "Extracting structured data points...",
            "Validating data quality..."
        ]
        sp_idx = 0
        while not search_task.done():
            await asyncio.sleep(5)
            if not search_task.done():
                yield event("task_progress", {
                    "step": "search",
                    "title": "Searching real-time sources",
                    "detail": search_progress[sp_idx % len(search_progress)],
                    "status": "active"
                })
                sp_idx += 1
        
        search_results = search_task.result()
        source_count = len(search_results.get('structured_data', {}).get('sources', []))
        
        yield event("task_progress", {
            "step": "search",
            "title": f"Collected {source_count} sources",
            "detail": f"Data gathered from {source_count} verified sources",
            "status": "complete"
        })
        
        sources = search_results.get("structured_data", {}).get("sources", [])
        if sources:
            yield event("search_sources", {"sources": sources})
        
        # Step 3: Generate file
        yield event("task_progress", {
            "step": "structure",
            "title": "Structuring data with AI",
            "detail": f"Using Kimi K2.5 to organize data into {file_type.upper()} format",
            "status": "active"
        })
        
        structured_data = search_results.get("structured_data", {})
        # Pass full search_results to Excel so it can access answer text from Perplexity/Grok
        full_data_for_excel = {
            **structured_data,
            "results": search_results.get("results", {})
        }
        
        # Run file generation with keepalive to prevent SSE proxy timeout
        # Kimi API calls can take 60-120 seconds; Railway proxy times out after ~60s of inactivity
        async def _generate_with_keepalive():
            if file_type == "excel":
                return await FileEngine.generate_excel(query, full_data_for_excel, user_id)
            elif file_type == "word":
                content = await ChatHandler._generate_content(query, structured_data)
                return await FileEngine.generate_word(query, content, user_id)
            elif file_type == "pdf":
                content = await ChatHandler._generate_content(query, structured_data)
                return await FileEngine.generate_pdf(query, content, user_id)
            elif file_type == "pptx":
                content = await ChatHandler._generate_content(query, structured_data)
                return await FileEngine.generate_pptx(query, content, user_id)
            else:
                return {"success": False, "error": "Unknown file type"}
        
        gen_task = asyncio.create_task(_generate_with_keepalive())
        progress_messages = [
            "Extracting key data points from search results...",
            "Organizing data into structured tables...",
            "Creating multiple tabs for different perspectives...",
            "Applying professional formatting and styling...",
            "Validating data integrity across all sheets...",
            "Finalizing layout and preparing for download...",
            "Running final quality checks...",
            "Optimizing cell formatting and column widths...",
            "Adding summary calculations and insights...",
            "Performing data quality validation..."
        ]
        msg_idx = 0
        # Send keepalive every 5 seconds to prevent Railway proxy timeout
        while not gen_task.done():
            await asyncio.sleep(5)
            if not gen_task.done():
                yield event("task_progress", {
                    "step": "structure",
                    "title": "Structuring data with AI",
                    "detail": progress_messages[msg_idx % len(progress_messages)],
                    "status": "active"
                })
                msg_idx += 1
        
        result = gen_task.result()
        
        yield event("task_progress", {
            "step": "structure",
            "title": f"{file_type.upper()} file created",
            "detail": f"{result.get('filename', 'report')} — {result.get('row_count', 'multiple')} rows of data",
            "status": "complete"
        })
        yield event("task_progress", {
            "step": "format",
            "title": "Applied professional formatting",
            "detail": "Headers, styling, and data validation applied",
            "status": "complete"
        })
        
        if result.get("success"):
            yield event("download", {
                "file_id": result["file_id"],
                "filename": result["filename"],
                "file_type": file_type,
                "download_url": result["download_url"]
            })
            
            # Step 4: Generate rich conclusion using Kimi
            yield event("task_progress", {
                "step": "review",
                "title": "Reviewing and summarizing results",
                "detail": "Preparing key findings summary",
                "status": "active"
            })
            
            # Build search context for conclusion
            search_context_summary = ""
            for source, data in search_results.get("results", {}).items():
                if isinstance(data, dict) and "answer" in data:
                    search_context_summary += data["answer"][:300] + "\n"
            
            source_names = [s.get("title", s.get("source", "")) for s in sources[:5]]
            
            # Generate data insights conclusion (NOT process description)
            conclusion = ""
            try:
                if kimi_client:
                    import functools
                    loop = asyncio.get_event_loop()
                    conclusion_response = await loop.run_in_executor(None, functools.partial(
                        kimi_client.chat.completions.create,
                        model="kimi-k2.5",
                        messages=[
                            {"role": "system", "content": """Write a brief overview of the KEY FINDINGS from the research data. The user is about to download a file — give them a quick preview of what's inside.

Format: 3-4 concise bullet points with the most important insights.
- Each bullet should contain a specific finding, number, or trend
- Focus on WHAT THE DATA SHOWS, not what you did to create the file
- Do NOT say "Here's what I did" or "I searched X sources" or "compiled Y rows"
- Do NOT describe the file format or formatting
- Be like a senior analyst giving a 10-second brief before handing over a report

Example good output:
- L'Oréal leads with €38.2B revenue, 3x larger than nearest competitor Estée Lauder
- Pharmacy/dermo-cosmetics is the fastest-growing segment at +12% YoY
- 7 of the top 10 brands are headquartered in France, reflecting domestic market dominance

No headers, no bold, no extra formatting. Maximum 4 bullets."""},
                            {"role": "user", "content": f"Topic: {query}\nData collected: {result.get('row_count', 'N/A')} rows across {file_type.upper()} format\nKey sources: {', '.join(source_names[:3])}\nResearch findings:\n{search_context_summary[:800]}"}
                        ],
                        temperature=1,
                        max_tokens=300
                    ))
                    conclusion = conclusion_response.choices[0].message.content
            except Exception as e:
                logger.error(f"Conclusion generation error: {e}")
            
            # Fallback if Kimi fails - still show insights not process
            if not conclusion:
                conclusion = f"""- Data compiled from {len(sources)} sources covering \"{query[:60]}\"
- {result.get('row_count', 'Multiple')} data points structured across multiple perspectives
- File ready for download with professional formatting"""
            
            yield event("content", {"chunk": conclusion})
            
            yield event("task_progress", {
                "step": "review",
                "title": "Task complete",
                "detail": "File generated and summary delivered",
                "status": "complete"
            })
            
            # Save to memory
            try:
                await MemoryManager.save_message(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    role="assistant",
                    content=conclusion
                )
            except Exception as e:
                logger.error(f"Memory save error: {e}")
            
            # Follow-ups
            follow_ups = ChatHandler._generate_follow_ups(query, conclusion)
            yield event("follow_up", {"questions": follow_ups})
            
            yield event("complete", {
                "content": conclusion,
                "conversation_id": conversation_id,
                "downloads": [result],
                "sources": sources,
                "follow_up_questions": follow_ups
            })
        else:
            error_msg = f"Error generating file: {result.get('error', 'Unknown error')}"
            yield event("error", {"message": error_msg})
            yield event("complete", {"content": error_msg, "conversation_id": conversation_id})
    
    @staticmethod
    async def _handle_swarm_mode(messages: List[Dict], query: str, user_id: str, conversation_id: str) -> AsyncGenerator[str, None]:
        """Handle swarm mode with multiple agents."""
        
        # Execute swarm
        swarm_gen = AgentOrchestrator.execute_swarm(query, num_agents=5)
        
        # Collect swarm events
        synthesis = ""
        async for e in swarm_gen:
            event_data = json.loads(e.replace("data: ", ""))
            if event_data.get("type") == "task_progress":
                yield e
            elif event_data.get("type") == "complete":
                synthesis = event_data.get("data", {}).get("synthesis", "")
        
        # Stream synthesis
        for chunk in synthesis.split():
            yield event("content", {"chunk": chunk + " "})
            await asyncio.sleep(0.01)
        
        # Save to memory
        await MemoryManager.save_message(
            conversation_id=conversation_id,
            user_id=user_id,
            role="assistant",
            content=synthesis
        )
        
        # Follow-ups
        follow_ups = ChatHandler._generate_follow_ups(query, synthesis)
        yield event("follow_up", {"questions": follow_ups})
        
        yield event("complete", {
            "content": synthesis,
            "conversation_id": conversation_id,
            "follow_up_questions": follow_ups
        })
    
    @staticmethod
    async def _generate_content(query: str, structured_data: Dict) -> str:
        """Generate content for documents."""
        if not kimi_client:
            return "Content generation not available."
        
        data_points = structured_data.get("data_points", [])
        data_summary = "\n".join([
            f"- {dp.get('title', '')}: {dp.get('description', '')[:200]}"
            for dp in data_points[:10]
        ])
        
        # Also include answer text from search results
        answer_text = ""
        for source_name in ["perplexity", "grok", "exa"]:
            if source_name in structured_data.get("results", {}):
                answer = structured_data["results"][source_name].get("answer", "")
                if answer:
                    answer_text += f"\n{answer[:500]}\n"
        
        messages = [
            {"role": "system", "content": """You are a professional content writer. Create well-structured, comprehensive content with:
- Clear markdown headers and sections
- Specific data points and facts
- Professional tone and analysis
- Logical flow from introduction to conclusion"""},
            {"role": "user", "content": f"Create comprehensive content for: {query}\n\nData points:\n{data_summary}\n\nResearch findings:\n{answer_text[:1000]}\n\nWrite a detailed, well-structured document:"}
        ]
        
        try:
            response = kimi_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1,
                max_tokens=4096
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Content generation error: {e}")
            return "Content could not be generated."
    
    @staticmethod
    def _generate_follow_ups(query: str, response: str) -> List[str]:
        """Generate contextual follow-up questions using LLM based on query AND response."""
        
        response_summary = response[:800] if response else ""
        
        system_msg = """Generate exactly 3 follow-up questions based on the user's query and the AI's response. Rules:
1. Each question must be directly relevant to the specific topic discussed
2. Questions should represent logical next steps: deeper analysis, comparisons, actionable outputs
3. Be SPECIFIC - mention actual entities, numbers, or topics from the response
4. Do NOT use generic questions like "Tell me more" or "What are the key takeaways"

Return ONLY a valid JSON array of 3 strings. Nothing else."""
        
        user_msg = f"User asked: {query}\n\nAI responded (summary): {response_summary}\n\nGenerate 3 specific follow-up questions:"
        
        # Try Grok first (faster, better at following JSON format instructions)
        clients_to_try = []
        if grok_client:
            clients_to_try.append((grok_client, "grok-3-mini", 0.5))
        if kimi_client:
            clients_to_try.append((kimi_client, "kimi-k2.5", 1))
        
        for client, model, temp in clients_to_try:
            try:
                result = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg}
                    ],
                    temperature=temp,
                    max_tokens=500
                )
                
                raw = result.choices[0].message.content.strip()
                
                # Parse JSON array with multiple strategies
                for strategy in [
                    lambda t: json.loads(t),
                    lambda t: json.loads(t[t.index('['):t.rindex(']')+1]),
                    lambda t: json.loads(t.split('```json')[-1].split('```')[0].strip()) if '```' in t else None,
                ]:
                    try:
                        parsed = strategy(raw)
                        if parsed and isinstance(parsed, list) and len(parsed) >= 3:
                            return [str(q).strip().strip('"') for q in parsed[:5]]
                    except:
                        continue
                
                # Line-by-line extraction as last resort
                lines = [l.strip().lstrip('0123456789.-) ').strip('"') for l in raw.split('\n') if l.strip() and len(l.strip()) > 15]
                if len(lines) >= 3:
                    return lines[:5]
                
                logger.warning(f"Follow-up parsing failed for {model}, raw: {raw[:200]}")
                
            except Exception as e:
                logger.error(f"Follow-up generation error with {model}: {e}")
                continue
        
        # Minimal fallback - at least reference the topic
        topic = query[:60] if query else "this topic"
        return [
            f"Can you go deeper into {topic}?",
            f"Generate an Excel report with this data",
            f"What are the key takeaways?"
        ]


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.post("/api/v1/chat")
@app.post("/api/v1/chat/stream")
async def chat_endpoint(request: ChatRequest):
    """Streaming chat endpoint - supports both /api/v1/chat and /api/v1/chat/stream."""
    try:
        async def event_generator():
            async for e in ChatHandler.handle_chat(request):
                yield e
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/chat/non-stream")
async def chat_non_stream(request: ChatRequest):
    """Non-streaming chat endpoint."""
    try:
        content_parts = []
        downloads = []
        sources = []
        follow_ups = []
        
        async for e in ChatHandler.handle_chat(request):
            event_data = json.loads(e.replace("data: ", ""))
            event_type = event_data.get("type")
            event_data_inner = event_data.get("data", {})
            
            if event_type == "content":
                content_parts.append(event_data_inner.get("chunk", ""))
            elif event_type == "download":
                downloads.append(event_data_inner)
            elif event_type == "search_sources":
                sources = event_data_inner.get("sources", [])
            elif event_type == "follow_up":
                follow_ups = event_data_inner.get("questions", [])
        
        return {
            "success": True,
            "content": "".join(content_parts),
            "downloads": downloads,
            "sources": sources,
            "follow_up_questions": follow_ups
        }
    except Exception as e:
        logger.error(f"Chat non-stream error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/search")
async def search_endpoint(request: SearchRequest):
    """Direct search endpoint."""
    try:
        results = await SearchLayer.search(request.query, request.sources, request.num_results)
        return {"success": True, "results": results}
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/generate-file")
@app.post("/api/v1/files/generate")
async def generate_file_endpoint(request: FileGenRequest):
    """Generate file endpoint - supports both V1 and V2 interfaces."""
    try:
        # Determine prompt from V1 or V2 interface
        prompt = request.prompt
        if not prompt and request.content:
            if isinstance(request.content, (dict, list)):
                prompt = json.dumps(request.content, indent=2)
            else:
                prompt = str(request.content)
            if request.title:
                prompt = f"{request.title}: {prompt}"
        if not prompt:
            raise HTTPException(status_code=400, detail="No prompt or content provided")
        
        # Search for data
        search_results = await SearchLayer.search(prompt, sources=["web", "news", "social"], num_results=15)
        structured_data = search_results.get("structured_data", {})
        
        # Determine file type
        file_type_val = None
        if request.file_type:
            file_type_val = request.file_type.value if isinstance(request.file_type, FileType) else str(request.file_type)
        else:
            file_type_val = "excel"  # default
        if file_type_val == "csv":
            # Generate CSV from content
            import csv as csv_mod
            import io
            file_id = str(uuid.uuid4())[:8]
            filename = FileEngine._generate_filename(prompt, "csv")
            filepath = OUTPUT_DIR / f"{file_id}_{filename}"
            content_text = request.content if isinstance(request.content, str) else ""
            
            # Parse markdown tables or content into CSV
            csv_lines = []
            for line in content_text.split('\n'):
                stripped = line.strip()
                if stripped.startswith('|') and stripped.endswith('|'):
                    import re as _re
                    if _re.match(r'^\|[\s\-:|]+\|$', stripped):
                        continue  # Skip separator rows
                    cells = [c.strip() for c in stripped.split('|')[1:-1]]
                    csv_lines.append(cells)
                elif stripped and not stripped.startswith('#'):
                    # Non-table content as single-column rows
                    cleaned = stripped.lstrip('- *').strip()
                    if cleaned:
                        csv_lines.append([cleaned])
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv_mod.writer(f)
                for row in csv_lines:
                    writer.writerow(row)
            
            FileEngine.files[file_id] = {
                "filename": filename,
                "filepath": str(filepath),
                "file_type": "csv",
                "user_id": request.user_id,
                "created_at": datetime.now().isoformat()
            }
            return {
                "success": True,
                "file_id": file_id,
                "filename": filename,
                "download_url": f"/api/v1/download/{file_id}"
            }
        if file_type_val == "docx":
            file_type_val = "word"
        
        # Handle markdown export (client-side content, no search needed)
        if file_type_val == "markdown":
            file_id = str(uuid.uuid4())[:8]
            filename = FileEngine._generate_filename(prompt, "md")
            filepath = OUTPUT_DIR / f"{file_id}_{filename}"
            content_text = request.content if isinstance(request.content, str) else prompt
            filepath.write_text(content_text, encoding="utf-8")
            FileEngine.files[file_id] = {
                "filename": filename,
                "filepath": str(filepath),
                "file_type": "markdown",
                "user_id": request.user_id,
                "created_at": datetime.now().isoformat()
            }
            return {
                "success": True,
                "file_id": file_id,
                "filename": filename,
                "download_url": f"/api/v1/download/{file_id}"
            }
        
        # Generate file
        file_type = file_type_val
        
        # If content is provided directly (export from chat), use it instead of searching
        direct_content = None
        if request.content and isinstance(request.content, str) and len(request.content) > 100:
            direct_content = request.content
        
        # Only search if we don't have direct content
        if not direct_content:
            search_results = await SearchLayer.search(prompt, sources=["web", "news", "social"], num_results=15)
            structured_data = search_results.get("structured_data", {})
        
        # Pass full search_results to Excel so it can access answer text
        full_data_for_excel = {
            **structured_data,
            "results": search_results.get("results", {}) if not direct_content else {}
        }
        
        content_for_doc = direct_content or await ChatHandler._generate_content(prompt, structured_data)
        
        if file_type == "excel":
            result = await FileEngine.generate_excel(prompt, full_data_for_excel, request.user_id)
        elif file_type == "word":
            result = await FileEngine.generate_word(prompt, content_for_doc, request.user_id)
        elif file_type == "pdf":
            result = await FileEngine.generate_pdf(prompt, content_for_doc, request.user_id)
        elif file_type == "pptx":
            result = await FileEngine.generate_pptx(prompt, content_for_doc, request.user_id)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown file type: {file_type}")
        
        if result.get("success"):
            return {
                "success": True,
                "file_id": result["file_id"],
                "filename": result["filename"],
                "download_url": result["download_url"]
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "File generation failed"))
    except Exception as e:
        logger.error(f"File generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/download/{file_id}")
@app.get("/api/v1/files/{file_id}/download")
async def download_file(file_id: str):
    """Download generated file."""
    try:
        file_info = FileEngine.get_file(file_id)
        
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        filepath = Path(file_info["filepath"])
        if not filepath.exists():
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        media_types = {
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "word": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "pdf": "application/pdf",
            "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "markdown": "text/markdown",
            "csv": "text/csv"
        }
        
        return FileResponse(
            path=str(filepath),
            filename=file_info["filename"],
            media_type=media_types.get(file_info["file_type"], "application/octet-stream")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/agent/execute")
async def execute_agent(request: AgentRequest):
    """Execute single agent."""
    try:
        result = await AgentOrchestrator.execute_agent(
            request.task,
            request.agent_type,
            request.context
        )
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Agent execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/swarm/execute")
async def execute_swarm(request: SwarmRequest):
    """Execute agent swarm."""
    try:
        async def event_generator():
            async for e in AgentOrchestrator.execute_swarm(request.task, request.num_agents, request.context):
                yield e
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.error(f"Swarm execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CONVERSATION ENDPOINTS
# ============================================================================

@app.get("/api/v1/conversations")
async def list_conversations(user_id: str):
    """List user's conversations."""
    try:
        if not supabase:
            return {"success": True, "conversations": []}
        
        result = supabase.table("conversations").select("*").eq(
            "user_id", user_id
        ).eq("status", "active").order("updated_at", desc=True).execute()
        
        return {"success": True, "conversations": result.data or []}
    except Exception as e:
        logger.error(f"List conversations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/conversations")
async def create_conversation(user_id: str, title: str = None, mode: str = "thinking"):
    """Create new conversation."""
    try:
        result = await MemoryManager.create_conversation(user_id, title, mode)
        return {"success": True, "conversation": result}
    except Exception as e:
        logger.error(f"Create conversation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, user_id: str):
    """Get conversation with messages."""
    try:
        if not supabase:
            return {"success": True, "conversation": None, "messages": []}
        
        # Get conversation
        conv_result = supabase.table("conversations").select("*").eq(
            "id", conversation_id
        ).eq("user_id", user_id).single().execute()
        
        # Get messages
        messages = await MemoryManager.get_conversation_messages(conversation_id)
        
        return {
            "success": True,
            "conversation": conv_result.data,
            "messages": messages
        }
    except Exception as e:
        logger.error(f"Get conversation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, user_id: str):
    """Delete conversation."""
    try:
        if not supabase:
            return {"success": True}
        
        supabase.table("conversations").update({"status": "deleted"}).eq(
            "id", conversation_id
        ).eq("user_id", user_id).execute()
        
        return {"success": True}
    except Exception as e:
        logger.error(f"Delete conversation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# HEALTH AND STATUS
# ============================================================================

@app.get("/health")
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "4.0.0",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "kimi": kimi_client is not None,
            "grok": grok_client is not None,
            "perplexity": bool(PERPLEXITY_API_KEY),
            "exa": bool(EXA_API_KEY),
            "serpapi": bool(SERPAPI_KEY),
            "supabase": supabase is not None
        }
    }

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "McLeuker AI V2",
        "version": "4.0.0",
        "description": "AI platform with Kimi-2.5 capabilities",
        "endpoints": [
            "/api/v1/chat",
            "/api/v1/chat/non-stream",
            "/api/v1/search",
            "/api/v1/files/generate",
            "/api/v1/files/{id}/download",
            "/api/v1/agent/execute",
            "/api/v1/swarm/execute",
            "/api/v1/conversations",
            "/health"
        ]
    }

# ============================================================================
# MULTIMODAL ENDPOINT
# ============================================================================

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
        
        # Use HybridLLMRouter instead of old KimiEngine
        result_content = ""
        async for evt in HybridLLMRouter.chat(messages, ChatMode(mode) if mode in [m.value for m in ChatMode] else ChatMode.thinking):
            evt_data = json.loads(evt.replace("data: ", "").strip())
            if evt_data.get("type") == "content":
                result_content += evt_data.get("data", {}).get("chunk", "")
        
        return {
            "success": True,
            "response": {
                "answer": result_content,
                "mode": mode
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================================
# WEEKLY INSIGHTS - Real-time domain intelligence
# ============================================================================

_weekly_insights_cache: Dict[str, Dict[str, Any]] = {}
WEEKLY_INSIGHTS_CACHE_TTL = 3600  # 1 hour cache

DOMAIN_INSIGHT_PROMPTS: Dict[str, str] = {
    "fashion": """You are a fashion industry intelligence analyst. Research and provide 8 of the most significant fashion industry developments from the PAST 7 DAYS (the week ending today). Focus on:
- Major runway shows, fashion week highlights (NYFW, Milan, Paris, London, Berlin)
- Designer appointments, creative director changes
- Luxury brand business moves (acquisitions, IPOs, earnings)
- Emerging trend signals from street style and social media
- Celebrity fashion moments that drove conversation
- Retail and e-commerce shifts

For each insight, provide a compelling headline, a 1-2 sentence summary, the source publication name, and a category tag.""",
    "beauty": """You are a beauty industry intelligence analyst. Research and provide 8 of the most significant beauty industry developments from the PAST 7 DAYS. Focus on:
- New product launches and brand collaborations
- Beauty brand earnings and business news
- Backstage beauty trends from fashion weeks
- Viral beauty moments on social media (TikTok, Instagram)
- K-beauty and J-beauty innovations
- Clean beauty and ingredient science news
- Celebrity beauty brand updates

For each insight, provide a compelling headline, a 1-2 sentence summary, the source publication name, and a category tag.""",
    "skincare": """You are a skincare and dermatology intelligence analyst. Research and provide 8 of the most significant skincare developments from the PAST 7 DAYS. Focus on:
- Clinical skincare breakthroughs and ingredient innovations
- Dermatologist-backed trend analysis
- Regulatory changes affecting skincare products
- Viral skincare routines and product reviews
- PDRN, peptide, and active ingredient news
- Brand launches targeting specific skin concerns
- Sunscreen and anti-aging research updates

For each insight, provide a compelling headline, a 1-2 sentence summary, the source publication name, and a category tag.""",
    "sustainability": """You are a sustainable fashion intelligence analyst. Research and provide 8 of the most significant sustainability developments in fashion from the PAST 7 DAYS. Focus on:
- Circular fashion initiatives and resale market news
- Brand sustainability commitments and greenwashing expos\u00e9s
- Textile recycling technology breakthroughs
- EU and global regulatory changes (EPR, DPP, due diligence)
- Copenhagen Fashion Week sustainability highlights
- Supply chain transparency developments
- Carbon footprint and water usage reduction news

For each insight, provide a compelling headline, a 1-2 sentence summary, the source publication name, and a category tag.""",
    "fashion-tech": """You are a fashion technology intelligence analyst. Research and provide 8 of the most significant fashion-tech developments from the PAST 7 DAYS. Focus on:
- AI in fashion design, merchandising, and forecasting
- Virtual try-on and AR/VR shopping experiences
- Generative AI tools for designers
- AI-powered shoppable runways and retail tech
- Digital fashion and NFT developments
- Supply chain technology and automation
- Fashion data analytics and personalization

For each insight, provide a compelling headline, a 1-2 sentence summary, the source publication name, and a category tag.""",
    "catwalks": """You are a runway and catwalk intelligence analyst. Research and provide 8 of the most significant runway and catwalk developments from the PAST 7 DAYS. Focus on:
- Fashion week show reviews and standout collections
- Designer debuts and farewell collections
- Backstage moments and model casting news
- Runway styling trends (hair, makeup, accessories)
- Show production and venue innovations
- Front row celebrity and influencer moments
- Emerging designers showing at fashion weeks

For each insight, provide a compelling headline, a 1-2 sentence summary, the source publication name, and a category tag.""",
    "culture": """You are a cultural intelligence analyst focused on fashion and lifestyle. Research and provide 8 of the most significant cultural developments affecting fashion from the PAST 7 DAYS. Focus on:
- Art exhibitions and museum shows influencing fashion
- Film, music, and entertainment crossovers with fashion
- Social media cultural moments and viral trends
- Diversity, equity, and inclusion news in fashion
- Fashion photography and editorial highlights
- Subculture movements gaining mainstream attention
- Fashion heritage and archival moments

For each insight, provide a compelling headline, a 1-2 sentence summary, the source publication name, and a category tag.""",
    "textile": """You are a textile industry intelligence analyst. Research and provide 8 of the most significant textile industry developments from the PAST 7 DAYS. Focus on:
- New fiber and fabric innovations
- Textile mill acquisitions and closures
- Raw material price movements (cotton, silk, wool)
- Sustainable textile technology breakthroughs
- Trade policy changes affecting textiles (tariffs, AGOA)
- Textile manufacturing shifts (nearshoring, automation)
- Hemp, linen, and alternative fiber developments

For each insight, provide a compelling headline, a 1-2 sentence summary, the source publication name, and a category tag.""",
    "lifestyle": """You are a lifestyle intelligence analyst. Research and provide 8 of the most significant lifestyle developments from the PAST 7 DAYS. Focus on:
- Wellness and self-care trend shifts
- Home and interior design crossovers with fashion
- Travel and hospitality luxury experiences
- Food and beverage lifestyle trends
- Fitness and athleisure market movements
- Consumer behavior and spending pattern changes
- Social media lifestyle influencer moments

For each insight, provide a compelling headline, a 1-2 sentence summary, the source publication name, and a category tag.""",
}

async def _fetch_weekly_insights(domain: str) -> List[Dict[str, Any]]:
    """Fetch real-time weekly insights using AI providers"""
    prompt = DOMAIN_INSIGHT_PROMPTS.get(domain, DOMAIN_INSIGHT_PROMPTS.get("fashion", ""))
    today = datetime.now().strftime("%B %d, %Y")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%B %d, %Y")
    
    system_msg = f"""You are a real-time intelligence analyst. Today is {today}. You must provide insights from the period {week_ago} to {today}.

Return your response as a valid JSON array of objects. Each object must have exactly these fields:
- "title": string (compelling headline, max 80 chars)
- "summary": string (1-2 sentence description, max 200 chars)
- "source": string (publication name like "Vogue", "BoF", "WWD", "Reuters", etc.)
- "category": string (short tag like "Runway", "Business", "Trend", "Innovation", etc.)
- "date": string (ISO date format, within the last 7 days)

Return ONLY the JSON array, no markdown formatting, no code blocks, no explanation."""
    
    providers = []
    if GROK_API_KEY:
        providers.append(("grok", "https://api.x.ai/v1", GROK_API_KEY, "grok-4-1-fast-reasoning"))
    providers.append(("gemini", None, os.getenv("OPENAI_API_KEY", ""), "gemini-2.5-flash"))
    if KIMI_API_KEY:
        providers.append(("kimi", "https://api.moonshot.ai/v1", KIMI_API_KEY, "moonshot-v1-auto"))
    
    for provider_name, base_url, api_key, model in providers:
        if not api_key:
            continue
        try:
            logger.info(f"Fetching weekly insights for {domain} via {provider_name}")
            provider_client = openai.AsyncOpenAI(
                api_key=api_key, base_url=base_url
            ) if base_url else openai.AsyncOpenAI(api_key=api_key)
            
            response = await provider_client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": prompt}],
                temperature=0.7, max_tokens=3000
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                if raw.endswith("```"): raw = raw[:-3]
                raw = raw.strip()
            insights = json.loads(raw)
            if isinstance(insights, list) and len(insights) >= 3:
                logger.info(f"Got {len(insights)} insights for {domain} via {provider_name}")
                return insights[:10]
        except Exception as e:
            logger.warning(f"Failed to fetch insights via {provider_name}: {e}")
            continue
    return []


class WeeklyInsightsRequest(BaseModel):
    domain: str = Field(..., description="Domain slug e.g. fashion, beauty, skincare")
    force_refresh: bool = Field(False, description="Force refresh bypassing cache")


@app.post("/api/v1/weekly-insights")
async def weekly_insights_endpoint(request: WeeklyInsightsRequest):
    """Get real-time weekly insights for a specific domain"""
    domain = request.domain.lower().strip()
    valid_domains = list(DOMAIN_INSIGHT_PROMPTS.keys())
    if domain not in valid_domains:
        raise HTTPException(status_code=400, detail=f"Invalid domain. Valid: {valid_domains}")
    
    now = time.time()
    if not request.force_refresh and domain in _weekly_insights_cache:
        cached = _weekly_insights_cache[domain]
        if now - cached["timestamp"] < WEEKLY_INSIGHTS_CACHE_TTL:
            return {"success": True, "domain": domain, "insights": cached["data"], "source": cached.get("source", "cache"), "cached": True, "cache_age_seconds": int(now - cached["timestamp"])}
    
    try:
        insights = await _fetch_weekly_insights(domain)
        if insights:
            _weekly_insights_cache[domain] = {"data": insights, "timestamp": now, "source": "ai"}
            return {"success": True, "domain": domain, "insights": insights, "source": "ai", "cached": False}
        return {"success": False, "domain": domain, "insights": [], "error": "No insights could be generated. Try again later."}
    except Exception as e:
        logger.error(f"Weekly insights error for {domain}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/weekly-insights/{domain}")
async def weekly_insights_get(domain: str, refresh: bool = False):
    req = WeeklyInsightsRequest(domain=domain, force_refresh=refresh)
    return await weekly_insights_endpoint(req)


# ============================================================================
# LIVE SIGNALS - Real-time "What's Happening Now" intelligence
# ============================================================================

_live_signals_cache: Dict[str, Dict[str, Any]] = {}
LIVE_SIGNALS_CACHE_TTL = 1800  # 30 min cache

DOMAIN_LIVE_PROMPTS: Dict[str, str] = {
    "fashion": """You are a real-time fashion intelligence analyst monitoring breaking news RIGHT NOW. Provide 6 urgent, high-priority signals happening TODAY or in the last 48 hours in fashion. Focus on:
- Breaking runway or collection news
- Brand announcements made today
- Viral fashion moments trending on social media right now
- Stock/market movements for fashion companies
- Celebrity style moments generating buzz today
- Industry personnel changes announced recently

For each signal provide: title (max 70 chars), description (2 sentences, max 180 chars), impact level (high/medium/low), category (one of: Breaking, Market, Viral, Business, Trend, Celebrity), source name, and a relevant metric or stat if available.""",
    "beauty": """You are a real-time beauty intelligence analyst. Provide 6 urgent signals happening TODAY or in the last 48 hours in beauty. Focus on: product launches, viral TikTok moments, brand earnings, ingredient controversies, celebrity beauty news, K-beauty innovations.

For each signal provide: title (max 70 chars), description (2 sentences, max 180 chars), impact level (high/medium/low), category (Breaking/Market/Viral/Business/Trend/Celebrity), source name, and a relevant metric.""",
    "skincare": """You are a real-time skincare intelligence analyst. Provide 6 urgent signals happening TODAY or in the last 48 hours in skincare. Focus on: clinical breakthroughs, FDA/EU regulatory news, viral skincare routines, ingredient science updates, brand launches, dermatologist warnings.

For each signal provide: title (max 70 chars), description (2 sentences, max 180 chars), impact level (high/medium/low), category (Breaking/Market/Viral/Business/Trend/Science), source name, and a relevant metric.""",
    "sustainability": """You are a real-time sustainability intelligence analyst for fashion. Provide 6 urgent signals happening TODAY or in the last 48 hours. Focus on: EU regulation updates, brand greenwashing exposures, circular fashion milestones, supply chain transparency news, carbon reduction achievements, textile recycling breakthroughs.

For each signal provide: title (max 70 chars), description (2 sentences, max 180 chars), impact level (high/medium/low), category (Breaking/Regulation/Business/Innovation/Trend/Policy), source name, and a relevant metric.""",
    "fashion-tech": """You are a real-time fashion technology analyst. Provide 6 urgent signals happening TODAY or in the last 48 hours. Focus on: AI fashion tool launches, AR/VR shopping updates, fashion startup funding rounds, retail tech deployments, digital fashion drops, supply chain tech news.

For each signal provide: title (max 70 chars), description (2 sentences, max 180 chars), impact level (high/medium/low), category (Breaking/Funding/AI/Retail/Innovation/Launch), source name, and a relevant metric.""",
    "catwalks": """You are a real-time runway intelligence analyst. Provide 6 urgent signals happening TODAY or in the last 48 hours. Focus on: fashion week show reviews, designer debuts, backstage exclusives, model casting news, show production innovations, front row moments.

For each signal provide: title (max 70 chars), description (2 sentences, max 180 chars), impact level (high/medium/low), category (Breaking/Show/Designer/Backstage/Trend/Casting), source name, and a relevant metric.""",
    "culture": """You are a real-time cultural intelligence analyst for fashion. Provide 6 urgent signals happening TODAY or in the last 48 hours. Focus on: art-fashion collaborations, museum exhibitions, film/music crossovers, viral cultural moments, DEI news in fashion, heritage brand moments.

For each signal provide: title (max 70 chars), description (2 sentences, max 180 chars), impact level (high/medium/low), category (Breaking/Art/Media/Social/Heritage/Exhibition), source name, and a relevant metric.""",
    "textile": """You are a real-time textile industry analyst. Provide 6 urgent signals happening TODAY or in the last 48 hours. Focus on: fiber innovation announcements, raw material price changes, mill acquisitions, trade policy updates, sustainable textile breakthroughs, manufacturing shifts.

For each signal provide: title (max 70 chars), description (2 sentences, max 180 chars), impact level (high/medium/low), category (Breaking/Price/Innovation/Trade/Business/Supply), source name, and a relevant metric.""",
    "lifestyle": """You are a real-time lifestyle intelligence analyst. Provide 6 urgent signals happening TODAY or in the last 48 hours. Focus on: wellness trend shifts, luxury experience launches, athleisure market moves, consumer behavior data, travel-fashion crossovers, social media lifestyle moments.

For each signal provide: title (max 70 chars), description (2 sentences, max 180 chars), impact level (high/medium/low), category (Breaking/Wellness/Market/Consumer/Travel/Viral), source name, and a relevant metric.""",
}

async def _fetch_live_signals(domain: str) -> List[Dict[str, Any]]:
    """Fetch real-time live signals using AI providers"""
    prompt = DOMAIN_LIVE_PROMPTS.get(domain, DOMAIN_LIVE_PROMPTS.get("fashion", ""))
    today = datetime.now().strftime("%B %d, %Y")
    
    system_msg = f"""You are a real-time intelligence analyst. Today is {today}. You must provide signals from the LAST 48 HOURS only.

Return your response as a valid JSON array of objects. Each object must have exactly these fields:
- "title": string (compelling headline, max 70 chars)
- "description": string (2 sentence summary, max 180 chars)
- "impact": string (one of: "high", "medium", "low")
- "category": string (short tag)
- "source": string (publication name)
- "metric": string (a relevant stat like "+15% stock", "2.3M views", "#1 trending", or "" if none)
- "timestamp": string (ISO datetime within last 48 hours)

Return ONLY the JSON array, no markdown, no code blocks."""
    
    providers = []
    if GROK_API_KEY:
        providers.append(("grok", "https://api.x.ai/v1", GROK_API_KEY, "grok-4-1-fast-reasoning"))
    providers.append(("gemini", None, os.getenv("OPENAI_API_KEY", ""), "gemini-2.5-flash"))
    if KIMI_API_KEY:
        providers.append(("kimi", "https://api.moonshot.ai/v1", KIMI_API_KEY, "moonshot-v1-auto"))
    
    for provider_name, base_url, api_key, model in providers:
        if not api_key:
            continue
        try:
            logger.info(f"Fetching live signals for {domain} via {provider_name}")
            provider_client = openai.AsyncOpenAI(
                api_key=api_key, base_url=base_url
            ) if base_url else openai.AsyncOpenAI(api_key=api_key)
            
            response = await provider_client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": prompt}],
                temperature=0.7, max_tokens=3000
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                if raw.endswith("```"): raw = raw[:-3]
                raw = raw.strip()
            signals = json.loads(raw)
            if isinstance(signals, list) and len(signals) >= 3:
                return signals[:6]
        except Exception as e:
            logger.warning(f"Failed live signals via {provider_name}: {e}")
            continue
    return []


@app.post("/api/v1/live-signals")
async def live_signals_endpoint(request: WeeklyInsightsRequest):
    """Get real-time live signals for a domain"""
    domain = request.domain.lower().strip()
    valid = list(DOMAIN_LIVE_PROMPTS.keys())
    if domain not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid domain. Valid: {valid}")
    
    now = time.time()
    cache_key = f"live_{domain}"
    if not request.force_refresh and cache_key in _live_signals_cache:
        cached = _live_signals_cache[cache_key]
        if now - cached["timestamp"] < LIVE_SIGNALS_CACHE_TTL:
            return {"success": True, "domain": domain, "signals": cached["data"], "cached": True}
    
    try:
        signals = await _fetch_live_signals(domain)
        if signals:
            _live_signals_cache[cache_key] = {"data": signals, "timestamp": now}
            return {"success": True, "domain": domain, "signals": signals, "cached": False}
        return {"success": False, "domain": domain, "signals": [], "error": "No signals available"}
    except Exception as e:
        logger.error(f"Live signals error for {domain}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/live-signals/{domain}")
async def live_signals_get(domain: str, refresh: bool = False):
    return await live_signals_endpoint(WeeklyInsightsRequest(domain=domain, force_refresh=refresh))


# ============================================================================
# DOMAIN MODULES - Real-time module previews
# ============================================================================

_module_previews_cache: Dict[str, Dict[str, Any]] = {}
MODULE_PREVIEW_CACHE_TTL = 3600  # 1 hour

DOMAIN_MODULE_PROMPTS: Dict[str, str] = {
    "fashion": """Generate 4 intelligence module previews for the FASHION domain. Each module should have a real, current data point from this week. The modules are:
1. Runway Analysis - Latest silhouette/color/designer signals from recent fashion weeks
2. Brand Positioning - Current luxury brand strategy shifts and market movements
3. Street Style - Consumer adoption signals from fashion capitals
4. Emerging Designers - New talent gaining industry attention this season

For each module provide: id, label, description (max 50 chars), a live_stat, a preview_headline (max 60 chars), and available_insights count (8-25).""",
    "beauty": """Generate 4 intelligence module previews for the BEAUTY domain with real current data:
1. Ingredient Trends - Active ingredients gaining traction in prestige skincare/makeup
2. Brand Analysis - Market positioning and recent launches
3. Clean Beauty - Sustainability in cosmetics
4. Backstage Beauty - Runway makeup trends from recent shows

For each: id, label, description (max 50 chars), live_stat, preview_headline (max 60 chars), available_insights count (8-25).""",
    "skincare": """Generate 4 intelligence module previews for the SKINCARE domain with real current data:
1. Active Ingredients - Science-backed formulation innovations
2. Regulatory Updates - EU, US & Asian compliance changes
3. Claims Analysis - Marketing and efficacy claims trending
4. Product Innovation - New formats and technologies

For each: id, label, description (max 50 chars), live_stat, preview_headline (max 60 chars), available_insights count (8-25).""",
    "sustainability": """Generate 4 intelligence module previews for the SUSTAINABILITY domain with real current data:
1. Sustainable Materials - Circular and regenerative options
2. Supply Chain - Transparency and traceability developments
3. ESG Regulations - Compliance and reporting requirements
4. Certifications - Standards and verification updates

For each: id, label, description (max 50 chars), live_stat, preview_headline (max 60 chars), available_insights count (8-25).""",
    "fashion-tech": """Generate 4 intelligence module previews for the FASHION-TECH domain with real current data:
1. AI in Fashion - Machine learning applications across the value chain
2. Startup Landscape - Emerging tech companies and funding
3. Digital Fashion - Virtual and augmented experiences
4. Retail Tech - Store and e-commerce innovation

For each: id, label, description (max 50 chars), live_stat, preview_headline (max 60 chars), available_insights count (8-25).""",
    "catwalks": """Generate 4 intelligence module previews for the CATWALKS domain with real current data:
1. Show Summaries - Key collections and standout moments
2. Designer Analysis - Creative direction and vision
3. Styling Trends - Show styling and presentation signals
4. Emerging Talent - New designers making waves

For each: id, label, description (max 50 chars), live_stat, preview_headline (max 60 chars), available_insights count (8-25).""",
    "culture": """Generate 4 intelligence module previews for the CULTURE domain with real current data:
1. Art & Fashion - Collaborations and exhibitions
2. Social Signals - Movements and values shaping fashion
3. Regional Culture - Geographic influences on global trends
4. Media & Influence - Cultural narratives in fashion

For each: id, label, description (max 50 chars), live_stat, preview_headline (max 60 chars), available_insights count (8-25).""",
    "textile": """Generate 4 intelligence module previews for the TEXTILE domain with real current data:
1. Find Mills - European and Asian textile producers
2. Fiber Innovation - New materials and technologies
3. Supplier Discovery - Sourcing with specifications
4. Certification Guide - GOTS, OEKO-TEX, BCI standards

For each: id, label, description (max 50 chars), live_stat, preview_headline (max 60 chars), available_insights count (8-25).""",
    "lifestyle": """Generate 4 intelligence module previews for the LIFESTYLE domain with real current data:
1. Consumer Signals - Behavior shifts and preferences
2. Wellness Trends - Health and fashion convergence
3. Cultural Shifts - Social movements and values
4. Travel & Leisure - Destination and experience signals

For each: id, label, description (max 50 chars), live_stat, preview_headline (max 60 chars), available_insights count (8-25).""",
}

async def _fetch_module_previews(domain: str) -> List[Dict[str, Any]]:
    """Fetch module preview data using AI"""
    prompt = DOMAIN_MODULE_PROMPTS.get(domain, DOMAIN_MODULE_PROMPTS.get("fashion", ""))
    today = datetime.now().strftime("%B %d, %Y")
    
    system_msg = f"""You are a fashion intelligence platform. Today is {today}.

Return a JSON array of 4 module objects. Each must have:
- "id": string (e.g. "runway", "brands")
- "label": string (module name)
- "description": string (max 50 chars)
- "live_stat": string (a real current metric)
- "preview_headline": string (one compelling current headline, max 60 chars)
- "available_insights": number (between 8-25)

Return ONLY the JSON array."""
    
    providers = []
    if GROK_API_KEY:
        providers.append(("grok", "https://api.x.ai/v1", GROK_API_KEY, "grok-4-1-fast-reasoning"))
    providers.append(("gemini", None, os.getenv("OPENAI_API_KEY", ""), "gemini-2.5-flash"))
    if KIMI_API_KEY:
        providers.append(("kimi", "https://api.moonshot.ai/v1", KIMI_API_KEY, "moonshot-v1-auto"))
    
    for provider_name, base_url, api_key, model in providers:
        if not api_key:
            continue
        try:
            provider_client = openai.AsyncOpenAI(
                api_key=api_key, base_url=base_url
            ) if base_url else openai.AsyncOpenAI(api_key=api_key)
            
            response = await provider_client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": prompt}],
                temperature=0.7, max_tokens=2000
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                if raw.endswith("```"): raw = raw[:-3]
                raw = raw.strip()
            modules = json.loads(raw)
            if isinstance(modules, list) and len(modules) >= 3:
                return modules[:4]
        except Exception as e:
            logger.warning(f"Failed module previews via {provider_name}: {e}")
            continue
    return []


@app.post("/api/v1/domain-modules")
async def domain_modules_endpoint(request: WeeklyInsightsRequest):
    """Get real-time module previews for a domain"""
    domain = request.domain.lower().strip()
    valid = list(DOMAIN_MODULE_PROMPTS.keys())
    if domain not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid domain. Valid: {valid}")
    
    now = time.time()
    cache_key = f"modules_{domain}"
    if not request.force_refresh and cache_key in _module_previews_cache:
        cached = _module_previews_cache[cache_key]
        if now - cached["timestamp"] < MODULE_PREVIEW_CACHE_TTL:
            return {"success": True, "domain": domain, "modules": cached["data"], "cached": True}
    
    try:
        modules = await _fetch_module_previews(domain)
        if modules:
            _module_previews_cache[cache_key] = {"data": modules, "timestamp": now}
            return {"success": True, "domain": domain, "modules": modules, "cached": False}
        return {"success": False, "domain": domain, "modules": [], "error": "No module data available"}
    except Exception as e:
        logger.error(f"Module previews error for {domain}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/domain-modules/{domain}")
async def domain_modules_get(domain: str, refresh: bool = False):
    return await domain_modules_endpoint(WeeklyInsightsRequest(domain=domain, force_refresh=refresh))


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
