"""
Specialized Agents — Domain-Specific AI Agents
==============================================

High-capability agents for specific task types:
- ComputerUseAgent: GUI automation and browser control
- DeepResearchAgent: Multi-source research with synthesis
- DocumentAgent: Document generation (PDF, Word, Markdown)
- ExcelAgent: Spreadsheet creation and data analysis
- SlidesAgent: Presentation generation
- WebsiteBuilderAgent: Full-stack website development

Each agent is self-contained and can be used independently or orchestrated
through the AgentSwarm coordinator.
"""

from .computer_use_agent import ComputerUseAgent
from .deep_research_agent import DeepResearchAgent
from .document_agent import DocumentAgent
from .excel_agent import ExcelAgent
from .slides_agent import SlidesAgent
from .website_builder_agent import WebsiteBuilderAgent

__all__ = [
    "ComputerUseAgent",
    "DeepResearchAgent",
    "DocumentAgent",
    "ExcelAgent",
    "SlidesAgent",
    "WebsiteBuilderAgent",
]
