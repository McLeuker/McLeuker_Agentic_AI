"""
Mode Configuration - Reasoning-First Architecture
==================================================

Defines the 3 main modes (Instant / Auto / Agent) with clear differentiation:

INSTANT MODE (Free/Low Credit)
- Model: grok-4-1-fast-reasoning (fast, cost-effective)
- Reasoning: Internal only (not shown to user)
- Search: Minimal (only time-sensitive queries)
- Output: Concise, 1-3 paragraphs max
- File Gen: No
- Agent Exec: No
- Credit Cost: 1x base

AUTO MODE (Standard Credit)
- Model: kimi-2.5 (balanced quality)
- Reasoning: Shown to user (transparent thinking)
- Search: Full multi-source search
- Output: Comprehensive, well-structured
- File Gen: Yes (PDF, Excel, PPT, Word, CSV)
- Agent Exec: No
- Credit Cost: 3x base

AGENT MODE (Premium Credit)
- Model: kimi-2.5 + grok-4-1-fast-reasoning (dual model)
- Reasoning: Full chain-of-thought shown to user
- Search: Deep research across all sources
- Output: Expert-level analysis with citations
- File Gen: Yes (all formats)
- Agent Exec: Yes (browser, code, GitHub, file ops)
- Credit Cost: 5x base
- Swarm: Can delegate to 124 specialized agents
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class ModeType(str, Enum):
    INSTANT = "instant"
    AUTO = "thinking"       # "thinking" is the internal name for Auto mode
    AGENT = "agent"
    SWARM = "swarm"
    RESEARCH = "research"
    CODE = "code"
    HYBRID = "hybrid"


@dataclass
class ModeCapabilities:
    """What each mode can do."""
    web_search: bool = False
    deep_research: bool = False
    file_generation: bool = False
    browser_execution: bool = False
    code_execution: bool = False
    github_operations: bool = False
    agent_swarm: bool = False
    rag_memory: bool = False
    real_time_data: bool = False
    image_analysis: bool = False
    document_analysis: bool = False


@dataclass
class ModeConfig:
    """Complete configuration for a chat mode."""
    name: str
    display_name: str
    description: str
    
    # Model selection
    primary_model: str          # "grok" or "kimi"
    reasoning_model: str        # Model used for reasoning step
    temperature: float
    max_tokens: int
    
    # Reasoning behavior
    show_reasoning: bool        # Whether to show reasoning to user
    reasoning_depth: str        # "shallow", "standard", "deep"
    
    # Search behavior
    search_enabled: bool
    search_sources: List[str]
    search_results_count: int
    search_only_time_sensitive: bool  # Only search for time-sensitive queries
    
    # Capabilities
    capabilities: ModeCapabilities
    
    # Credit costs
    base_credit_cost: float
    search_credit_multiplier: float
    llm_credit_multiplier: float
    file_gen_credit_multiplier: float
    agent_exec_credit_multiplier: float
    
    # Output formatting
    max_paragraphs: int         # 0 = unlimited
    output_style: str           # "concise", "balanced", "comprehensive"
    enable_citations: bool
    enable_tables: bool
    enable_code_blocks: bool


# ============================================================================
# MODE DEFINITIONS
# ============================================================================

INSTANT_MODE = ModeConfig(
    name="instant",
    display_name="Instant",
    description="Fast, concise answers. Reasoning-first but brief. Best for quick questions.",
    primary_model="grok",
    reasoning_model="grok-4-1-fast-reasoning",
    temperature=0.7,
    max_tokens=16384,
    show_reasoning=False,
    reasoning_depth="shallow",
    search_enabled=True,
    search_sources=["web"],
    search_results_count=5,
    search_only_time_sensitive=True,
    capabilities=ModeCapabilities(
        web_search=True,
        real_time_data=True,
        image_analysis=True,
        document_analysis=True,
    ),
    base_credit_cost=1.0,
    search_credit_multiplier=1.0,
    llm_credit_multiplier=1.0,
    file_gen_credit_multiplier=0.0,  # No file gen in instant
    agent_exec_credit_multiplier=0.0,
    max_paragraphs=3,
    output_style="concise",
    enable_citations=False,
    enable_tables=False,
    enable_code_blocks=True,
)

AUTO_MODE = ModeConfig(
    name="thinking",
    display_name="Auto",
    description="Balanced mode with full search, file generation, and transparent reasoning.",
    primary_model="kimi",
    reasoning_model="kimi-2.5",
    temperature=0.6,
    max_tokens=16384,
    show_reasoning=True,
    reasoning_depth="standard",
    search_enabled=True,
    search_sources=["web", "news", "social"],
    search_results_count=15,
    search_only_time_sensitive=False,
    capabilities=ModeCapabilities(
        web_search=True,
        deep_research=True,
        file_generation=True,
        real_time_data=True,
        image_analysis=True,
        document_analysis=True,
        rag_memory=True,
    ),
    base_credit_cost=3.0,
    search_credit_multiplier=1.5,
    llm_credit_multiplier=2.0,
    file_gen_credit_multiplier=3.0,
    agent_exec_credit_multiplier=0.0,
    max_paragraphs=0,  # Unlimited
    output_style="balanced",
    enable_citations=True,
    enable_tables=True,
    enable_code_blocks=True,
)

AGENT_MODE = ModeConfig(
    name="agent",
    display_name="Agent",
    description="Full agentic AI with browser execution, code running, file ops, and 124 specialized agents.",
    primary_model="kimi",
    reasoning_model="grok-4-1-fast-reasoning",
    temperature=0.5,
    max_tokens=16384,
    show_reasoning=True,
    reasoning_depth="deep",
    search_enabled=True,
    search_sources=["web", "news", "social", "academic"],
    search_results_count=20,
    search_only_time_sensitive=False,
    capabilities=ModeCapabilities(
        web_search=True,
        deep_research=True,
        file_generation=True,
        browser_execution=True,
        code_execution=True,
        github_operations=True,
        agent_swarm=True,
        rag_memory=True,
        real_time_data=True,
        image_analysis=True,
        document_analysis=True,
    ),
    base_credit_cost=5.0,
    search_credit_multiplier=2.0,
    llm_credit_multiplier=3.0,
    file_gen_credit_multiplier=5.0,
    agent_exec_credit_multiplier=10.0,
    max_paragraphs=0,  # Unlimited
    output_style="comprehensive",
    enable_citations=True,
    enable_tables=True,
    enable_code_blocks=True,
)

SWARM_MODE = ModeConfig(
    name="swarm",
    display_name="Swarm",
    description="Multi-agent swarm mode. Delegates tasks to specialized agents for parallel execution.",
    primary_model="kimi",
    reasoning_model="grok-4-1-fast-reasoning",
    temperature=0.5,
    max_tokens=16384,
    show_reasoning=True,
    reasoning_depth="deep",
    search_enabled=True,
    search_sources=["web", "news", "social", "academic"],
    search_results_count=20,
    search_only_time_sensitive=False,
    capabilities=ModeCapabilities(
        web_search=True,
        deep_research=True,
        file_generation=True,
        browser_execution=True,
        code_execution=True,
        github_operations=True,
        agent_swarm=True,
        rag_memory=True,
        real_time_data=True,
        image_analysis=True,
        document_analysis=True,
    ),
    base_credit_cost=8.0,
    search_credit_multiplier=3.0,
    llm_credit_multiplier=5.0,
    file_gen_credit_multiplier=5.0,
    agent_exec_credit_multiplier=15.0,
    max_paragraphs=0,
    output_style="comprehensive",
    enable_citations=True,
    enable_tables=True,
    enable_code_blocks=True,
)

RESEARCH_MODE = ModeConfig(
    name="research",
    display_name="Research",
    description="Deep research mode with academic sources and comprehensive analysis.",
    primary_model="hybrid",
    reasoning_model="grok-4-1-fast-reasoning",
    temperature=0.4,
    max_tokens=16384,
    show_reasoning=True,
    reasoning_depth="deep",
    search_enabled=True,
    search_sources=["web", "news", "social", "academic"],
    search_results_count=25,
    search_only_time_sensitive=False,
    capabilities=ModeCapabilities(
        web_search=True,
        deep_research=True,
        file_generation=True,
        real_time_data=True,
        image_analysis=True,
        document_analysis=True,
        rag_memory=True,
    ),
    base_credit_cost=5.0,
    search_credit_multiplier=3.0,
    llm_credit_multiplier=3.0,
    file_gen_credit_multiplier=5.0,
    agent_exec_credit_multiplier=0.0,
    max_paragraphs=0,
    output_style="comprehensive",
    enable_citations=True,
    enable_tables=True,
    enable_code_blocks=True,
)

CODE_MODE = ModeConfig(
    name="code",
    display_name="Code",
    description="Code-focused mode with execution capabilities.",
    primary_model="kimi",
    reasoning_model="kimi-2.5",
    temperature=0.3,
    max_tokens=16384,
    show_reasoning=False,
    reasoning_depth="standard",
    search_enabled=True,
    search_sources=["web"],
    search_results_count=10,
    search_only_time_sensitive=False,
    capabilities=ModeCapabilities(
        web_search=True,
        file_generation=True,
        code_execution=True,
        github_operations=True,
        document_analysis=True,
    ),
    base_credit_cost=3.0,
    search_credit_multiplier=1.0,
    llm_credit_multiplier=2.0,
    file_gen_credit_multiplier=3.0,
    agent_exec_credit_multiplier=5.0,
    max_paragraphs=0,
    output_style="balanced",
    enable_citations=False,
    enable_tables=True,
    enable_code_blocks=True,
)


# ============================================================================
# MODE REGISTRY
# ============================================================================

MODE_REGISTRY: Dict[str, ModeConfig] = {
    "instant": INSTANT_MODE,
    "thinking": AUTO_MODE,
    "agent": AGENT_MODE,
    "swarm": SWARM_MODE,
    "research": RESEARCH_MODE,
    "code": CODE_MODE,
    "hybrid": AUTO_MODE,  # Hybrid uses Auto config
}


def get_mode_config(mode_name: str) -> ModeConfig:
    """Get the configuration for a mode."""
    return MODE_REGISTRY.get(mode_name, AUTO_MODE)


def get_mode_capabilities(mode_name: str) -> Dict[str, bool]:
    """Get capabilities as a dict for frontend display."""
    config = get_mode_config(mode_name)
    caps = config.capabilities
    return {
        "web_search": caps.web_search,
        "deep_research": caps.deep_research,
        "file_generation": caps.file_generation,
        "browser_execution": caps.browser_execution,
        "code_execution": caps.code_execution,
        "github_operations": caps.github_operations,
        "agent_swarm": caps.agent_swarm,
        "rag_memory": caps.rag_memory,
        "real_time_data": caps.real_time_data,
        "image_analysis": caps.image_analysis,
        "document_analysis": caps.document_analysis,
    }


def get_all_modes_info() -> List[Dict[str, Any]]:
    """Get info for all modes (for frontend mode selector)."""
    modes = []
    seen = set()
    for name, config in MODE_REGISTRY.items():
        if config.name in seen:
            continue
        seen.add(config.name)
        modes.append({
            "name": config.name,
            "display_name": config.display_name,
            "description": config.description,
            "capabilities": get_mode_capabilities(config.name),
            "credit_cost": config.base_credit_cost,
            "reasoning_visible": config.show_reasoning,
            "output_style": config.output_style,
        })
    return modes
