"""
McLeuker Agentic AI Module
===========================

Manus-style agentic execution system with:
- Kimi 2.5 Client (instant/thinking/agent modes)
- Grok Client (real-time data + verification + fallback)
- Execution Orchestrator V1 (plan → execute → verify → deliver)
- E2B Code Execution sandbox
- Browserless web automation
- WebSocket real-time streaming

V2 Additions:
- ReasoningAgent (reasoning-first, clarification before execution)
- BrowserEngineV2 (fixed Playwright with vision model CUA loop)
- ExecutionOrchestratorV2 (3-mode system: instant/auto/agent)
- API Routes V2 (SSE streaming + WebSocket)
"""

from .kimi25_client import Kimi25Client, KimiMode, KimiModeType, KimiResponse
from .grok_client import GrokClient, GrokResponse, FactCheckResult
from .execution_orchestrator import ExecutionOrchestrator, ExecutionResult, ExecutionStatus
from .e2b_integration import E2BManager, CodeExecutionResult
from .browserless_integration import BrowserlessClient, BrowserResult
from .websocket_handler import ExecutionWebSocketManager, get_websocket_manager

# V2 Agentic AI — Reasoning-first execution
V2_AVAILABLE = False
try:
    from .reasoning_agent import ReasoningAgent, ModeRouter, ReasoningResult
    from .browser_engine_v2 import BrowserEngineV2, PLAYWRIGHT_V2_AVAILABLE
    from .execution_orchestrator_v2 import ExecutionOrchestratorV2, ExecutionStatusV2
    from .api_routes_v2 import create_v2_routes
    V2_AVAILABLE = True
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"V2 agentic modules not available: {e}")

__all__ = [
    "Kimi25Client", "KimiMode", "KimiModeType", "KimiResponse",
    "GrokClient", "GrokResponse", "FactCheckResult",
    "ExecutionOrchestrator", "ExecutionResult", "ExecutionStatus",
    "E2BManager", "CodeExecutionResult",
    "BrowserlessClient", "BrowserResult",
    "ExecutionWebSocketManager", "get_websocket_manager",
    # V2
    "ReasoningAgent", "ModeRouter", "ReasoningResult",
    "BrowserEngineV2", "PLAYWRIGHT_V2_AVAILABLE",
    "ExecutionOrchestratorV2", "ExecutionStatusV2",
    "create_v2_routes", "V2_AVAILABLE",
]
