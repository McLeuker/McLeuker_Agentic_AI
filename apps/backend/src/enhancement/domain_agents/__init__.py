"""
Domain-Specific Agents
========================
9 specialized agents for fashion, beauty, and lifestyle domains.
Each agent has deep domain knowledge and specialized analysis capabilities.
"""

from .fashion_agent import FashionAgent
from .beauty_agent import BeautyAgent
from .skincare_agent import SkincareAgent
from .sustainability_agent import SustainabilityAgent
from .tech_agent import TechAgent
from .catwalk_agent import CatwalkAgent
from .culture_agent import CultureAgent
from .textile_agent import TextileAgent
from .lifestyle_agent import LifestyleAgent
from .domain_router import DomainRouter

__all__ = [
    "FashionAgent",
    "BeautyAgent",
    "SkincareAgent",
    "SustainabilityAgent",
    "TechAgent",
    "CatwalkAgent",
    "CultureAgent",
    "TextileAgent",
    "LifestyleAgent",
    "DomainRouter",
]
