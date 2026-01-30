"""
McLeuker Agentic AI Platform - Data Models and Schemas
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import uuid


# ============================================================================
# Enums
# ============================================================================

class DomainType(str, Enum):
    """Supported domains for task classification."""
    FASHION = "fashion"
    BEAUTY = "beauty"
    SKINCARE = "skincare"
    SUSTAINABILITY = "sustainability"
    FASHION_TECH = "fashion_tech"
    CATWALKS = "catwalks"
    CULTURE = "culture"
    TEXTILE = "textile"
    LIFESTYLE = "lifestyle"
    BUSINESS = "business"
    TECHNOLOGY = "technology"
    MARKETING = "marketing"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    OTHER = "other"


class OutputFormat(str, Enum):
    """Supported output formats."""
    EXCEL = "excel"
    CSV = "csv"
    PDF = "pdf"
    WORD = "word"
    PPT = "ppt"
    WEB = "web"
    DASHBOARD = "dashboard"
    CODE = "code"
    TEXT = "text"
    JSON = "json"


class ResearchDepth(str, Enum):
    """Depth of research required."""
    NONE = "none"
    LIGHT = "light"
    MEDIUM = "medium"
    DEEP = "deep"


class ConfidenceLevel(str, Enum):
    """Confidence level of interpretation."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ExecutionStep(str, Enum):
    """Possible execution steps."""
    REASONING = "reasoning"
    WEB_RESEARCH = "web_research"
    DATA_STRUCTURING = "data_structuring"
    ANALYSIS = "analysis"
    EXCEL_GENERATION = "excel_generation"
    PDF_GENERATION = "pdf_generation"
    PPT_GENERATION = "ppt_generation"
    WEB_GENERATION = "web_generation"
    CODE_GENERATION = "code_generation"
    QUALITY_CHECK = "quality_check"


class TaskStatus(str, Enum):
    """Status of a task."""
    PENDING = "pending"
    INTERPRETING = "interpreting"
    REASONING = "reasoning"
    RESEARCHING = "researching"
    STRUCTURING = "structuring"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class DataEntityType(str, Enum):
    """Types of data entities."""
    BRANDS = "brands"
    COMPANIES = "companies"
    PRODUCTS = "products"
    SUPPLIERS = "suppliers"
    MATERIALS = "materials"
    TECHNOLOGIES = "technologies"
    MARKETS = "markets"
    TRENDS = "trends"
    PRICING = "pricing"
    REGULATIONS = "regulations"
    CERTIFICATIONS = "certifications"
    CAMPAIGNS = "campaigns"
    EVENTS = "events"
    STATISTICS = "statistics"
    OTHER = "other"


class RiskFlag(str, Enum):
    """Risk flags for tasks."""
    DATA_FRESHNESS_RISK = "data_freshness_risk"
    SOURCE_RELIABILITY_RISK = "source_reliability_risk"
    AMBIGUOUS_SCOPE = "ambiguous_scope"
    MISSING_INPUTS = "missing_inputs"
    FORMAT_COMPLEXITY = "format_complexity"
    NONE = "none"


# ============================================================================
# Layer 1: Task Interpretation Models
# ============================================================================

class TaskInterpretation(BaseModel):
    """Output schema for the Task Interpretation Layer."""
    intent: str = Field(
        ...,
        description="Clear description of what the user wants to achieve."
    )
    domains: List[DomainType] = Field(
        ...,
        description="Primary and secondary domains involved in the request."
    )
    requires_real_time_research: bool = Field(
        ...,
        description="Whether up-to-date external information is required."
    )
    research_depth: ResearchDepth = Field(
        ...,
        description="Expected depth of research if required."
    )
    geography: Optional[List[str]] = Field(
        default=None,
        description="Relevant regions or markets if mentioned or implied."
    )
    time_horizon: Optional[str] = Field(
        default=None,
        description="Timeframe referenced (e.g., SS26, 2025, next 6 months)."
    )
    outputs: List[OutputFormat] = Field(
        ...,
        description="Requested output formats."
    )
    execution_plan: List[ExecutionStep] = Field(
        ...,
        description="Ordered list of execution steps."
    )
    confidence_level: ConfidenceLevel = Field(
        ...,
        description="How confident the system is about interpreting the request."
    )
    assumptions: Optional[List[str]] = Field(
        default=None,
        description="Explicit assumptions made if the user request was ambiguous."
    )


# ============================================================================
# Layer 2: LLM Reasoning Models
# ============================================================================

class DataStructurePlan(BaseModel):
    """Plan for structuring data outputs."""
    tables: Optional[List[str]] = Field(default=None)
    documents: Optional[List[str]] = Field(default=None)
    presentations: Optional[List[str]] = Field(default=None)
    web_outputs: Optional[List[str]] = Field(default=None)


class ReasoningBlueprint(BaseModel):
    """Output schema for the LLM Reasoning Layer."""
    task_summary: str = Field(
        ...,
        description="Concise restatement of the task in execution-oriented language."
    )
    reasoning_objectives: List[str] = Field(
        ...,
        description="High-level objectives the system must achieve."
    )
    research_questions: Optional[List[str]] = Field(
        default=None,
        description="Specific questions to be answered through real-time research."
    )
    required_data_entities: Optional[List[DataEntityType]] = Field(
        default=None,
        description="Types of structured data required to fulfill the task."
    )
    data_structure_plan: Optional[DataStructurePlan] = Field(
        default=None,
        description="Planned structure of final outputs across formats."
    )
    logic_steps: List[str] = Field(
        ...,
        description="Ordered reasoning steps to transform raw data into final outputs."
    )
    quality_criteria: List[str] = Field(
        ...,
        description="Conditions that must be satisfied for the output to be complete."
    )
    risk_flags: Optional[List[RiskFlag]] = Field(
        default=None,
        description="Potential risks identified during reasoning."
    )


# ============================================================================
# Layer 3: Web Research Models
# ============================================================================

class SearchResult(BaseModel):
    """A single search result."""
    title: str
    url: str
    snippet: str
    source: Optional[str] = None
    published_date: Optional[str] = None


class WebResearchResult(BaseModel):
    """Results from web research."""
    query: str
    results: List[SearchResult]
    summary: Optional[str] = None
    raw_content: Optional[str] = None


class ScrapedContent(BaseModel):
    """Content scraped from a webpage."""
    url: str
    title: Optional[str] = None
    content: str
    extracted_data: Optional[Dict[str, Any]] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)


class ResearchOutput(BaseModel):
    """Complete output from the research layer."""
    search_results: List[WebResearchResult]
    scraped_contents: Optional[List[ScrapedContent]] = None
    synthesized_findings: Optional[str] = None
    data_points: Optional[Dict[str, Any]] = None


# ============================================================================
# Layer 4: Structuring Models
# ============================================================================

class StructuredTable(BaseModel):
    """A structured table for output."""
    name: str
    description: str
    columns: List[str]
    rows: List[Dict[str, Any]]


class StructuredDocument(BaseModel):
    """A structured document for output."""
    title: str
    sections: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None


class StructuredPresentation(BaseModel):
    """A structured presentation for output."""
    title: str
    slides: List[Dict[str, Any]]
    theme: Optional[str] = None


class StructuredOutput(BaseModel):
    """Complete structured output from the structuring layer."""
    tables: Optional[List[StructuredTable]] = None
    documents: Optional[List[StructuredDocument]] = None
    presentations: Optional[List[StructuredPresentation]] = None
    raw_data: Optional[Dict[str, Any]] = None


# ============================================================================
# Layer 5: Execution Models
# ============================================================================

class GeneratedFile(BaseModel):
    """A generated file."""
    filename: str
    format: OutputFormat
    path: str
    size_bytes: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ExecutionResult(BaseModel):
    """Result from the execution layer."""
    files: List[GeneratedFile]
    success: bool
    message: Optional[str] = None
    errors: Optional[List[str]] = None


# ============================================================================
# Task and Session Models
# ============================================================================

class Task(BaseModel):
    """A complete task in the system."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_prompt: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Layer outputs
    interpretation: Optional[TaskInterpretation] = None
    reasoning: Optional[ReasoningBlueprint] = None
    research: Optional[ResearchOutput] = None
    structured_output: Optional[StructuredOutput] = None
    execution_result: Optional[ExecutionResult] = None
    
    # Metadata
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    error_message: Optional[str] = None


class TaskRequest(BaseModel):
    """Request to create a new task."""
    prompt: str = Field(..., description="The user's prompt/request")
    user_id: Optional[str] = None
    preferred_outputs: Optional[List[OutputFormat]] = None
    domain_hint: Optional[DomainType] = None


class TaskResponse(BaseModel):
    """Response for a task."""
    task_id: str
    status: TaskStatus
    message: str
    files: Optional[List[GeneratedFile]] = None
    progress: Optional[Dict[str, Any]] = None


# ============================================================================
# Chat/Conversation Models
# ============================================================================

class Message(BaseModel):
    """A message in a conversation."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


class Conversation(BaseModel):
    """A conversation/chat session."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Message] = Field(default_factory=list)
    task_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
