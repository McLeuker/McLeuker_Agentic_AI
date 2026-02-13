"""
McLeuker AI - Specialized Agents
=================================

Production-ready specialized agents for end-to-end task execution:
- ComputerUseAgent: GUI automation and control
- DocumentAgent: Professional document generation (DOCX, PDF)
- SlidesAgent: Presentation creation (PPTX)
- ExcelAgent: Spreadsheet creation and analysis (XLSX)
- DeepResearchAgent: Multi-source research
- WebsiteBuilderAgent: End-to-end website creation
"""

from .computer_use_agent import ComputerUseAgent, get_computer_use_agent
from .document_agent import DocumentAgent, get_document_agent
from .slides_agent import SlidesAgent, get_slides_agent
from .excel_agent import ExcelAgent, get_excel_agent
from .deep_research_agent import DeepResearchAgent, get_research_agent
from .website_builder_agent import WebsiteBuilderAgent, get_website_builder

__all__ = [
    "ComputerUseAgent",
    "DocumentAgent",
    "SlidesAgent",
    "ExcelAgent",
    "DeepResearchAgent",
    "WebsiteBuilderAgent",
    "get_computer_use_agent",
    "get_document_agent",
    "get_slides_agent",
    "get_excel_agent",
    "get_research_agent",
    "get_website_builder",
]
