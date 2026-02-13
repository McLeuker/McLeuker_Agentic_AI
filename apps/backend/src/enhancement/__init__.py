"""
McLeuker Enhancement Package
==============================
True agentic AI capabilities built on top of the McLeuker architecture.

Components:
- domain_agents: 9 specialized domain agents with routing
- tool_stability: Workflow orchestration, retry, circuit breaker
- file_analysis: Multimodal file analysis using Kimi 2.5 vision
- execution: End-to-end execution engine for web automation
"""

from .integration import McLeukerEnhancement, EnhancementConfig, create_enhancement

__all__ = [
    "McLeukerEnhancement",
    "EnhancementConfig",
    "create_enhancement",
]
