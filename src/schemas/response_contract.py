"""
McLeuker AI V5.1 - Response Contract Schema
============================================
This is the CORE of the new architecture.

The response contract ensures:
1. Clean prose WITHOUT inline citations
2. Persistent sources as first-class objects
3. Real file generation (Excel, PDF, PPT)
4. Structured layout with hierarchy
5. Separated concerns (content vs metadata)

This fixes ALL root cause issues identified in the ChatGPT diagnosis.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import uuid


class IntentType(str, Enum):
    """User intent classification - prevents domain overfitting"""
    RESEARCH = "research"           # Deep analysis, reports
    ADVICE = "advice"               # Recommendations, suggestions
    SHOPPING = "shopping"           # Product recommendations, where to buy
    DOC_GENERATION = "doc_generation"  # Excel, PDF, PPT requests
    STRATEGY = "strategy"           # Business strategy, planning
    COMPARISON = "comparison"       # Compare products, brands, markets
    NEWS = "news"                   # Current events, what's happening
    GENERAL = "general"             # General questions, chat


class DomainType(str, Enum):
    """Domain classification - flexible, not forced"""
    FASHION = "fashion"
    BEAUTY = "beauty"
    SKINCARE = "skincare"
    SUSTAINABILITY = "sustainability"
    LIFESTYLE = "lifestyle"
    LUXURY = "luxury"
    RETAIL = "retail"
    GENERAL = "general"


class FileType(str, Enum):
    """Supported file types for generation"""
    EXCEL = "xlsx"
    PDF = "pdf"
    POWERPOINT = "pptx"
    MARKDOWN = "md"
    CSV = "csv"


class Source(BaseModel):
    """
    Persistent source object - NEVER inline in prose.
    Sources are first-class citizens, not afterthoughts.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str
    url: str
    publisher: Optional[str] = None
    snippet: Optional[str] = None
    date: Optional[str] = None
    type: str = "article"  # article, report, social, video


class GeneratedFile(BaseModel):
    """
    Real downloadable file - NOT text pretending to be a file.
    Backend generates actual files, frontend shows download button.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    filename: str
    file_type: FileType
    url: str  # Download URL
    size_bytes: Optional[int] = None
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TableData(BaseModel):
    """Structured table data for clean rendering"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: Optional[str] = None
    headers: List[str]
    rows: List[List[str]]
    footer: Optional[str] = None


class KeyInsight(BaseModel):
    """Bullet-point insight for quick scanning"""
    icon: Optional[str] = None  # emoji or icon name
    title: str
    description: str
    importance: str = "medium"  # high, medium, low


class ActionItem(BaseModel):
    """Actionable next step for the user"""
    action: str
    details: Optional[str] = None
    link: Optional[str] = None
    priority: str = "medium"


class LayoutSection(BaseModel):
    """A section in the structured layout"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str
    content: str  # Clean prose, NO citations
    subsections: Optional[List['LayoutSection']] = None


class ResponseContract(BaseModel):
    """
    THE RESPONSE CONTRACT
    =====================
    This is what the backend MUST return for every response.
    Frontend renders these components, never invents structure.
    
    Key principles:
    1. main_content has NO inline citations - clean prose only
    2. sources are persistent objects, never regenerated
    3. files are real downloadable artifacts
    4. layout follows: summary → insights → sections → actions
    """
    
    # === METADATA ===
    session_id: str
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # === INTENT & DOMAIN ===
    intent: IntentType
    domain: DomainType
    confidence: float = Field(ge=0, le=1, default=0.9)
    
    # === MAIN CONTENT (Clean prose, NO citations) ===
    summary: str  # TL;DR - 1-2 sentences max
    main_content: str  # Clean narrative prose, NO [1][2][3]
    
    # === STRUCTURED DATA ===
    key_insights: List[KeyInsight] = Field(default_factory=list)
    tables: List[TableData] = Field(default_factory=list)
    sections: List[LayoutSection] = Field(default_factory=list)
    
    # === SOURCES (Persistent, separate from content) ===
    sources: List[Source] = Field(default_factory=list)
    source_count: int = 0
    
    # === FILES (Real downloadable artifacts) ===
    files: List[GeneratedFile] = Field(default_factory=list)
    
    # === ACTIONS ===
    action_items: List[ActionItem] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)
    
    # === USAGE ===
    credits_used: int = 2
    processing_time_ms: int = 0
    
    # === ERROR HANDLING ===
    success: bool = True
    error: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StreamingChunk(BaseModel):
    """For streaming responses - progressive updates"""
    chunk_type: str  # "status", "content", "source", "file", "complete"
    content: Optional[str] = None
    source: Optional[Source] = None
    file: Optional[GeneratedFile] = None
    progress: Optional[int] = None  # 0-100
    status_message: Optional[str] = None


# === HELPER FUNCTIONS ===

def create_empty_response(session_id: str, error: str = None) -> ResponseContract:
    """Create an empty/error response contract"""
    return ResponseContract(
        session_id=session_id,
        intent=IntentType.GENERAL,
        domain=DomainType.GENERAL,
        summary="Unable to process request" if error else "",
        main_content="",
        success=error is None,
        error=error
    )


def format_sources_for_display(sources: List[Source]) -> str:
    """Format sources for a separate 'Sources' section in UI"""
    if not sources:
        return ""
    
    lines = ["## Sources\n"]
    for i, src in enumerate(sources, 1):
        publisher = f" ({src.publisher})" if src.publisher else ""
        lines.append(f"{i}. [{src.title}]({src.url}){publisher}")
    
    return "\n".join(lines)
