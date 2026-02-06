"""
McLeuker AI Backend - Complete Kimi 2.5 Edition
Full tool execution, real-time data, agent swarm, file generation
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any, Union, AsyncGenerator
import openai
import os
import base64
import json
import asyncio
import httpx
from datetime import datetime
from enum import Enum
import re
import uuid
import io
from pathlib import Path

# File generation imports
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Initialize FastAPI
app = FastAPI(
    title="McLeuker AI - Kimi 2.5 Complete",
    description="Advanced Agentic AI with full tool execution and real-time data",
    version="2.5.1"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

# Initialize Kimi client
client = openai.OpenAI(
    api_key=KIMI_API_KEY,
    base_url="https://api.moonshot.cn/v1"
)

# File storage
OUTPUT_DIR = Path("/tmp/mcleuker_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================================
# DATA MODELS
# ============================================================================

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: Union[str, List[Dict[str, Any]]]
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    mode: Literal["instant", "thinking", "agent", "swarm", "research"] = "thinking"
    stream: bool = False
    enable_tools: bool = True

class SwarmRequest(BaseModel):
    master_task: str
    context: Dict[str, Any] = {}
    num_agents: int = Field(default=5, ge=1, le=20)
    enable_search: bool = True

class FileGenRequest(BaseModel):
    content: str
    file_type: Literal["excel", "word", "pdf", "pptx"]
    filename: Optional[str] = None
    title: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    sources: List[Literal["web", "news", "academic", "youtube"]] = ["web"]
    num_results: int = 10

class ResearchRequest(BaseModel):
    query: str
    depth: Literal["quick", "deep", "exhaustive"] = "deep"
    sources: List[str] = ["web", "news"]
    generate_report: bool = False

class V51Response(BaseModel):
    success: bool
    response: Dict[str, Any]
    error: Optional[str] = None

# ============================================================================
# REAL-TIME SEARCH APIs
# ============================================================================

class SearchAPIs:
    """Unified search across multiple real-time data sources"""
    
    @staticmethod
    async def perplexity_search(query: str, focus: str = "web") -> Dict:
        """Deep research with Perplexity AI"""
        if not PERPLEXITY_API_KEY:
            return {"error": "Perplexity API key not configured", "results": []}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                response = await http_client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={"Authorization": f"Bearer {PERPLEXITY_API_KEY}"},
                    json={
                        "model": "sonar-pro",
                        "messages": [{"role": "user", "content": query}],
                        "temperature": 0.2
                    }
                )
                data = response.json()
                return {
                    "source": "perplexity",
                    "answer": data["choices"][0]["message"]["content"],
                    "citations": data.get("citations", []),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {"error": str(e), "source": "perplexity"}
    
    @staticmethod
    async def exa_search(query: str, num_results: int = 10) -> Dict:
        """Web search with Exa.ai"""
        if not EXA_API_KEY:
            return {"error": "Exa API key not configured", "results": []}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                response = await http_client.post(
                    "https://api.exa.ai/search",
                    headers={"Authorization": f"Bearer {EXA_API_KEY}"},
                    json={
                        "query": query,
                        "numResults": num_results,
                        "useAutoprompt": True
                    }
                )
                data = response.json()
                return {
                    "source": "exa",
                    "results": data.get("results", []),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {"error": str(e), "source": "exa"}
    
    @staticmethod
    async def youtube_search(query: str, max_results: int = 5) -> Dict:
        """Search YouTube videos"""
        if not YOUTUBE_API_KEY:
            return {"error": "YouTube API key not configured", "results": []}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                response = await http_client.get(
                    "https://www.googleapis.com/youtube/v3/search",
                    params={
                        "part": "snippet",
                        "q": query,
                        "maxResults": max_results,
                        "type": "video",
                        "order": "relevance",
                        "key": YOUTUBE_API_KEY
                    }
                )
                data = response.json()
                videos = []
                for item in data.get("items", []):
                    videos.append({
                        "title": item["snippet"]["title"],
                        "description": item["snippet"]["description"],
                        "video_id": item["id"]["videoId"],
                        "url": f"https://youtube.com/watch?v={item['id']['videoId']}",
                        "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                        "published_at": item["snippet"]["publishedAt"],
                        "channel": item["snippet"]["channelTitle"]
                    })
                return {
                    "source": "youtube",
                    "videos": videos,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {"error": str(e), "source": "youtube"}
    
    @staticmethod
    async def grok_search(query: str) -> Dict:
        """Search with Grok/X AI"""
        if not GROK_API_KEY:
            return {"error": "Grok API key not configured", "results": []}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                response = await http_client.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROK_API_KEY}"},
                    json={
                        "model": "grok-beta",
                        "messages": [{"role": "user", "content": query}],
                        "stream": False
                    }
                )
                data = response.json()
                return {
                    "source": "grok",
                    "answer": data["choices"][0]["message"]["content"],
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {"error": str(e), "source": "grok"}
    
    @staticmethod
    async def multi_search(query: str, sources: List[str] = None) -> Dict:
        """Search across all available sources"""
        if sources is None:
            sources = ["web"]
        
        tasks = []
        source_map = {}
        
        if "web" in sources or "news" in sources:
            tasks.append(SearchAPIs.perplexity_search(query))
            source_map[len(tasks)-1] = "perplexity"
        
        if "web" in sources:
            tasks.append(SearchAPIs.exa_search(query))
            source_map[len(tasks)-1] = "exa"
        
        if "youtube" in sources:
            tasks.append(SearchAPIs.youtube_search(query))
            source_map[len(tasks)-1] = "youtube"
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        combined = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "sources": {}
        }
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                combined["sources"][source_map[i]] = {"error": str(result)}
            else:
                combined["sources"][result.get("source", source_map[i])] = result
        
        return combined

# ============================================================================
# FILE GENERATION SYSTEM
# ============================================================================

class FileGenerator:
    """Generate downloadable files (Excel, Word, PDF, PPTX)"""
    
    @staticmethod
    def generate_excel(data: Dict, filename: str = None) -> str:
        """Generate Excel file from data"""
        if filename is None:
            filename = f"output_{uuid.uuid4().hex[:8]}.xlsx"
        
        filepath = OUTPUT_DIR / filename
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Handle different data formats
            if isinstance(data, dict):
                for sheet_name, sheet_data in data.items():
                    if isinstance(sheet_data, list):
                        df = pd.DataFrame(sheet_data)
                    elif isinstance(sheet_data, dict):
                        df = pd.DataFrame([sheet_data])
                    else:
                        df = pd.DataFrame({"content": [str(sheet_data)]})
                    df.to_excel(writer, sheet_name=str(sheet_name)[:31], index=False)
            elif isinstance(data, list):
                df = pd.DataFrame(data)
                df.to_excel(writer, sheet_name="Data", index=False)
            else:
                df = pd.DataFrame({"content": [str(data)]})
                df.to_excel(writer, sheet_name="Data", index=False)
        
        return str(filepath)
    
    @staticmethod
    def generate_word(content: str, title: str = None, filename: str = None) -> str:
        """Generate Word document"""
        if filename is None:
            filename = f"report_{uuid.uuid4().hex[:8]}.docx"
        
        filepath = OUTPUT_DIR / filename
        doc = Document()
        
        # Add title
        if title:
            title_para = doc.add_heading(title, 0)
            title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Add content
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip().startswith('#'):
                # Markdown-style headers
                level = len(para.split()[0])
                doc.add_heading(para.lstrip('#').strip(), level=min(level, 3))
            elif para.strip().startswith('- ') or para.strip().startswith('* '):
                # Bullet points
                doc.add_paragraph(para.strip()[2:], style='List Bullet')
            elif re.match(r'^\d+\.', para.strip()):
                # Numbered list
                doc.add_paragraph(re.sub(r'^\d+\.', '', para.strip()).strip(), style='List Number')
            else:
                doc.add_paragraph(para.strip())
        
        # Add footer
        doc.add_paragraph()
        footer = doc.add_paragraph()
        footer_run = footer.add_run(f"Generated by McLeuker AI on {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        footer_run.font.size = Pt(8)
        footer_run.font.color.rgb = RGBColor(128, 128, 128)
        
        doc.save(filepath)
        return str(filepath)
    
    @staticmethod
    def generate_pdf(content: str, title: str = None, filename: str = None) -> str:
        """Generate PDF using matplotlib (lightweight solution)"""
        if filename is None:
            filename = f"report_{uuid.uuid4().hex[:8]}.pdf"
        
        filepath = OUTPUT_DIR / filename
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')
        
        # Title
        y_pos = 0.95
        if title:
            ax.text(0.5, y_pos, title, fontsize=18, weight='bold', 
                   ha='center', transform=ax.transAxes)
            y_pos -= 0.08
        
        # Content
        lines = content.split('\n')
        text_content = []
        for line in lines:
            if len(line) > 100:
                # Wrap long lines
                words = line.split()
                current = ""
                for word in words:
                    if len(current) + len(word) < 95:
                        current += word + " "
                    else:
                        text_content.append(current.strip())
                        current = word + " "
                if current:
                    text_content.append(current.strip())
            else:
                text_content.append(line)
        
        # Display content
        display_text = '\n'.join(text_content[:60])  # Limit pages
        ax.text(0.1, y_pos, display_text, fontsize=10, va='top',
               transform=ax.transAxes, family='monospace')
        
        # Footer
        ax.text(0.5, 0.02, f"Generated by McLeuker AI - {datetime.now().strftime('%Y-%m-%d')}",
               fontsize=8, ha='center', transform=ax.transAxes, style='italic')
        
        plt.savefig(filepath, format='pdf', bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    @staticmethod
    def generate_pptx(content: str, title: str = None, filename: str = None) -> str:
        """Generate PowerPoint presentation"""
        if filename is None:
            filename = f"presentation_{uuid.uuid4().hex[:8]}.pptx"
        
        filepath = OUTPUT_DIR / filename
        
        # Use python-pptx if available, otherwise create a simple HTML-based solution
        try:
            from pptx import Presentation
            from pptx.util import Inches, Pt
            
            prs = Presentation()
            
            # Title slide
            title_slide = prs.slides.add_slide(prs.slide_layouts[0])
            title_slide.shapes.title.text = title or "McLeuker AI Presentation"
            title_slide.placeholders[1].text = f"Generated on {datetime.now().strftime('%Y-%m-%d')}"
            
            # Content slides
            sections = content.split('\n\n')
            for section in sections[:10]:  # Limit slides
                if len(section.strip()) < 10:
                    continue
                    
                slide = prs.slides.add_slide(prs.slide_layouts[1])
                lines = section.split('\n')
                
                if lines:
                    slide.shapes.title.text = lines[0][:50]
                    body = '\n'.join(lines[1:])[:500]
                    slide.placeholders[1].text = body
            
            prs.save(filepath)
        except ImportError:
            # Fallback: create a Word doc with .pptx extension (will need conversion)
            filepath = FileGenerator.generate_word(content, title, filename.replace('.pptx', '.docx'))
        
        return str(filepath)

# ============================================================================
# TOOL DEFINITIONS FOR KIMI
# ============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "realtime_search",
            "description": "Search for real-time information from web, news, YouTube. Use this for ANY question about current events, recent news, or time-sensitive information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "sources": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["web", "news", "youtube"]},
                        "default": ["web"]
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_excel",
            "description": "Generate an Excel file with data. Use for lists, tables, comparisons, or any structured data the user wants to download.",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {"type": "object", "description": "Data to include in Excel - can be a list of objects or dict of sheets"},
                    "filename": {"type": "string", "description": "Optional filename"},
                    "sheet_name": {"type": "string", "default": "Data"}
                },
                "required": ["data"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_word",
            "description": "Generate a Word document (.docx) with formatted content. Use for reports, summaries, or documents the user wants to download.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Document content"},
                    "title": {"type": "string", "description": "Document title"},
                    "filename": {"type": "string", "description": "Optional filename"}
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_pdf",
            "description": "Generate a PDF document. Use for professional reports or documents the user wants to download.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Document content"},
                    "title": {"type": "string", "description": "Document title"},
                    "filename": {"type": "string", "description": "Optional filename"}
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "deep_research",
            "description": "Conduct deep research on a topic using multiple sources. Use for comprehensive analysis or when the user asks for detailed research.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Research topic"},
                    "depth": {"type": "string", "enum": ["quick", "deep", "exhaustive"], "default": "deep"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_image",
            "description": "Analyze an image and provide detailed description. Use when user uploads an image.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_url": {"type": "string", "description": "Base64 or URL of image"}
                },
                "required": ["image_url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_code",
            "description": "Generate code in any programming language. Use when user asks for code examples or implementations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "What the code should do"},
                    "language": {"type": "string", "default": "python"},
                    "framework": {"type": "string", "description": "Optional framework"}
                },
                "required": ["description"]
            }
        }
    }
]

# ============================================================================
# TOOL EXECUTOR
# ============================================================================

class ToolExecutor:
    """Execute tools and return results"""
    
    generated_files: Dict[str, str] = {}
    
    @classmethod
    async def execute(cls, tool_calls: List[Any]) -> List[Dict]:
        """Execute multiple tool calls"""
        results = []
        
        for call in tool_calls:
            try:
                result = await cls.execute_single(call)
                results.append(result)
            except Exception as e:
                results.append({
                    "tool_call_id": call.id,
                    "role": "tool",
                    "content": json.dumps({"error": str(e)}),
                    "name": call.function.name
                })
        
        return results
    
    @classmethod
    async def execute_single(cls, call: Any) -> Dict:
        """Execute a single tool call"""
        function_name = call.function.name
        arguments = json.loads(call.function.arguments)
        
        result_data = {"tool": function_name}
        
        if function_name == "realtime_search":
            search_result = await SearchAPIs.multi_search(
                arguments["query"],
                arguments.get("sources", ["web"])
            )
            result_data["search_results"] = search_result
            
        elif function_name == "deep_research":
            # Use agent swarm for deep research
            swarm = AgentSwarm()
            research_result = await swarm.execute(
                master_task=arguments["query"],
                context={"depth": arguments.get("depth", "deep")},
                num_agents=5,
                enable_search=True
            )
            result_data["research"] = research_result
            
        elif function_name == "generate_excel":
            filepath = FileGenerator.generate_excel(
                arguments["data"],
                arguments.get("filename")
            )
            file_id = uuid.uuid4().hex[:12]
            cls.generated_files[file_id] = filepath
            result_data["file_id"] = file_id
            result_data["filename"] = Path(filepath).name
            result_data["download_url"] = f"/api/v1/download/{file_id}"
            
        elif function_name == "generate_word":
            filepath = FileGenerator.generate_word(
                arguments["content"],
                arguments.get("title"),
                arguments.get("filename")
            )
            file_id = uuid.uuid4().hex[:12]
            cls.generated_files[file_id] = filepath
            result_data["file_id"] = file_id
            result_data["filename"] = Path(filepath).name
            result_data["download_url"] = f"/api/v1/download/{file_id}"
            
        elif function_name == "generate_pdf":
            filepath = FileGenerator.generate_pdf(
                arguments["content"],
                arguments.get("title"),
                arguments.get("filename")
            )
            file_id = uuid.uuid4().hex[:12]
            cls.generated_files[file_id] = filepath
            result_data["file_id"] = file_id
            result_data["filename"] = Path(filepath).name
            result_data["download_url"] = f"/api/v1/download/{file_id}"
            
        elif function_name == "generate_code":
            # Code generation is handled by Kimi itself
            result_data["status"] = "Code generation ready"
            
        elif function_name == "analyze_image":
            result_data["status"] = "Image analysis ready"
            
        else:
            result_data["error"] = f"Unknown tool: {function_name}"
        
        return {
            "tool_call_id": call.id,
            "role": "tool",
            "content": json.dumps(result_data),
            "name": function_name
        }

# ============================================================================
# KIMI ENGINE
# ============================================================================

class KimiEngine:
    """Main Kimi 2.5 interface"""
    
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
        "research": {
            "temperature": 0.7,
            "top_p": 0.95,
            "extra_body": {
                "thinking": {"type": "enabled"},
                "parallel_tool_calls": True
            }
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
        """Execute chat with optional tools"""
        
        config = cls.CONFIGS.get(mode, cls.CONFIGS["thinking"]).copy()
        params = {
            "model": "kimi-k2.5",
            "messages": messages,
            "stream": stream,
            **config
        }
        
        # Add tools for agent/research modes
        if enable_tools and mode in ["agent", "research"]:
            params["tools"] = TOOLS
            params["tool_choice"] = "auto"
        
        start_time = datetime.now()
        response = client.chat.completions.create(**params)
        latency = int((datetime.now() - start_time).total_seconds() * 1000)
        
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
            "latency_ms": latency
        }
        
        # Execute tools if present
        if result["tool_calls"]:
            tool_results = await ToolExecutor.execute(result["tool_calls"])
            result["tool_results"] = tool_results
            
            # Continue conversation with tool results
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
        """Continue conversation after tool execution"""
        
        messages = original_messages.copy()
        messages.append({
            "role": "assistant",
            "content": assistant_message.content,
            "reasoning_content": getattr(assistant_message, 'reasoning_content', None),
            "tool_calls": [tc.model_dump() for tc in assistant_message.tool_calls]
        })
        messages.extend([{"role": r["role"], "content": r["content"], "tool_call_id": r["tool_call_id"]} for r in tool_results])
        
        response = client.chat.completions.create(
            model="kimi-k2.5",
            messages=messages,
            temperature=0.6,
            extra_body={"thinking": {"type": "disabled"}}
        )
        
        # Extract file info from tool results
        tool_outputs = []
        for tr in tool_results:
            try:
                content = json.loads(tr["content"])
                if "download_url" in content:
                    tool_outputs.append({
                        "type": "file",
                        "filename": content.get("filename"),
                        "download_url": content.get("download_url"),
                        "file_id": content.get("file_id")
                    })
                elif "search_results" in content:
                    tool_outputs.append({
                        "type": "search",
                        "results": content["search_results"]
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
        """Stream chat responses"""
        
        config = cls.CONFIGS.get(mode, cls.CONFIGS["thinking"]).copy()
        params = {
            "model": "kimi-k2.5",
            "messages": messages,
            "stream": True,
            **config
        }
        
        if enable_tools and mode in ["agent", "research"]:
            params["tools"] = TOOLS
            params["tool_choice"] = "auto"
        
        response = client.chat.completions.create(**params)
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield f"data: {json.dumps({'type': 'content', 'data': chunk.choices[0].delta.content})}\n\n"
            elif chunk.choices[0].delta.reasoning_content:
                yield f"data: {json.dumps({'type': 'reasoning', 'data': chunk.choices[0].delta.reasoning_content})}\n\n"
        
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

# ============================================================================
# AGENT SWARM
# ============================================================================

class AgentSwarm:
    """Multi-agent orchestration for complex tasks"""
    
    ROLES = {
        "researcher": "Expert at finding and verifying real-time information",
        "analyst": "Expert at data analysis and pattern recognition",
        "writer": "Expert at creating clear, engaging content",
        "critic": "Expert at reviewing and identifying issues",
        "synthesizer": "Expert at combining multiple perspectives into coherent output"
    }
    
    async def execute(
        self,
        master_task: str,
        context: Dict,
        num_agents: int = 5,
        enable_search: bool = True
    ) -> Dict:
        """Execute swarm task"""
        
        start_time = datetime.now()
        
        # Step 1: Decompose task
        subtasks = await self._decompose_task(master_task, num_agents)
        
        # Step 2: Execute in parallel
        semaphore = asyncio.Semaphore(10)
        
        async def run_agent(agent_def):
            async with semaphore:
                return await self._execute_agent(agent_def, context, enable_search)
        
        results = await asyncio.gather(*[run_agent(t) for t in subtasks])
        
        # Step 3: Synthesize
        synthesis = await self._synthesize(results, master_task)
        
        latency = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return {
            "master_task": master_task,
            "agents_deployed": len(subtasks),
            "subtasks": subtasks,
            "agent_results": results,
            "synthesis": synthesis,
            "latency_ms": latency,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _decompose_task(self, task: str, num_agents: int) -> List[Dict]:
        """Decompose task into subtasks"""
        
        prompt = f"""Break this task into {num_agents} parallel subtasks for specialized agents.

Task: {task}
Available roles: {list(self.ROLES.keys())}

Return JSON: {{"subtasks": [{{"role": "role_name", "task": "specific task", "priority": 1-10}}]}}"""

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
                valid.append({
                    "id": f"agent_{len(valid)}",
                    "role": t.get("role", "researcher"),
                    "task": t.get("task", "Analyze"),
                    "priority": t.get("priority", 5)
                })
            return valid
        except:
            return [{"id": f"agent_{i}", "role": "researcher", "task": f"Analyze: {task}", "priority": 5} for i in range(num_agents)]
    
    async def _execute_agent(self, agent_def: Dict, context: Dict, enable_search: bool) -> Dict:
        """Execute single agent"""
        
        role_desc = self.ROLES.get(agent_def["role"], "AI Assistant")
        
        messages = [
            {"role": "system", "content": f"You are a {agent_def['role']}. {role_desc}. Be concise."},
            {"role": "user", "content": f"Task: {agent_def['task']}\nContext: {json.dumps(context)}"}
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
                "output": result["content"],
                "tool_results": result.get("tool_results", []),
                "tokens": result["usage"]["total_tokens"],
                "success": True
            }
        except Exception as e:
            return {
                "agent_id": agent_def["id"],
                "role": agent_def["role"],
                "output": str(e),
                "success": False
            }
    
    async def _synthesize(self, results: List[Dict], master_task: str) -> str:
        """Synthesize agent outputs"""
        
        successful = [r for r in results if r.get("success")]
        
        prompt = f"""Synthesize these agent outputs into a comprehensive answer.

Task: {master_task}

Agent Outputs:
{json.dumps([{"role": r['role'], "output": r['output'][:500]} for r in successful], indent=2)}

Provide a well-structured final response:"""

        response = client.chat.completions.create(
            model="kimi-k2.5",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4096,
            extra_body={"thinking": {"type": "enabled"}}
        )
        
        return response.choices[0].message.content

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.post("/api/v1/chat")
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint with tool execution"""
    try:
        messages = [m.model_dump(exclude_none=True) for m in request.messages]
        
        result = await KimiEngine.chat(
            messages=messages,
            mode=request.mode,
            enable_tools=request.enable_tools,
            stream=request.stream
        )
        
        # Extract downloadable files
        downloads = []
        for output in result.get("tool_outputs", []):
            if output.get("type") == "file":
                downloads.append({
                    "filename": output["filename"],
                    "download_url": output["download_url"],
                    "file_id": output["file_id"]
                })
        
        return {
            "success": True,
            "response": {
                "answer": result["content"],
                "reasoning": result.get("reasoning_content"),
                "mode": result["mode"],
                "downloads": downloads,
                "search_results": [o for o in result.get("tool_outputs", []) if o.get("type") == "search"],
                "metadata": {
                    "tokens": result["usage"],
                    "latency_ms": result["latency_ms"],
                    "tool_calls": len(result.get("tool_calls", []))
                }
            }
        }
    except Exception as e:
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
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
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
            enable_search=request.enable_search
        )
        
        return {
            "success": True,
            "response": {
                "answer": result["synthesis"],
                "mode": "swarm",
                "agents": result["agents_deployed"],
                "subtasks": result["subtasks"],
                "agent_results": result["agent_results"],
                "latency_ms": result["latency_ms"],
                "metadata": {
                    "total_tokens": sum(r.get("tokens", 0) for r in result["agent_results"])
                }
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/v1/search")
async def search_endpoint(request: SearchRequest):
    """Direct search endpoint"""
    try:
        results = await SearchAPIs.multi_search(request.query, request.sources)
        return {"success": True, "results": results}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/v1/research")
async def research_endpoint(request: ResearchRequest):
    """Deep research with report generation"""
    try:
        # Use swarm for comprehensive research
        swarm = AgentSwarm()
        result = await swarm.execute(
            master_task=f"Research: {request.query}",
            context={"depth": request.depth, "sources": request.sources},
            num_agents=5 if request.depth == "deep" else 3,
            enable_search=True
        )
        
        response_data = {
            "success": True,
            "response": {
                "answer": result["synthesis"],
                "research_data": result,
                "mode": "research"
            }
        }
        
        # Generate report file if requested
        if request.generate_report:
            report_content = f"""# Research Report: {request.query}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Executive Summary

{result["synthesis"][:2000]}

## Detailed Findings

"""
            for agent_result in result["agent_results"]:
                report_content += f"\n### {agent_result['role'].upper()} Analysis\n\n"
                report_content += agent_result['output'][:1000] + "\n"
            
            filepath = FileGenerator.generate_word(
                report_content,
                title=f"Research: {request.query[:50]}"
            )
            file_id = uuid.uuid4().hex[:12]
            ToolExecutor.generated_files[file_id] = filepath
            
            response_data["response"]["report_download"] = {
                "file_id": file_id,
                "filename": Path(filepath).name,
                "download_url": f"/api/v1/download/{file_id}"
            }
        
        return response_data
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/v1/generate-file")
async def generate_file_endpoint(request: FileGenRequest):
    """Generate downloadable file"""
    try:
        if request.file_type == "excel":
            filepath = FileGenerator.generate_excel(
                json.loads(request.content) if isinstance(request.content, str) else request.content,
                request.filename
            )
        elif request.file_type == "word":
            filepath = FileGenerator.generate_word(
                request.content,
                request.title,
                request.filename
            )
        elif request.file_type == "pdf":
            filepath = FileGenerator.generate_pdf(
                request.content,
                request.title,
                request.filename
            )
        else:
            return {"success": False, "error": "Unsupported file type"}
        
        file_id = uuid.uuid4().hex[:12]
        ToolExecutor.generated_files[file_id] = filepath
        
        return {
            "success": True,
            "file_id": file_id,
            "filename": Path(filepath).name,
            "download_url": f"/api/v1/download/{file_id}"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/v1/download/{file_id}")
async def download_file(file_id: str):
    """Download generated file"""
    filepath = ToolExecutor.generated_files.get(file_id)
    if not filepath or not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        filepath,
        filename=Path(filepath).name,
        media_type="application/octet-stream"
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

@app.get("/api/v1/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "version": "2.5.1",
        "model": "kimi-k2.5",
        "capabilities": [
            "instant_mode", "thinking_mode", "agent_mode", "swarm_mode", "research_mode",
            "realtime_search", "file_generation", "multimodal", "streaming"
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
        "docs": "/docs",
        "health": "/api/v1/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
