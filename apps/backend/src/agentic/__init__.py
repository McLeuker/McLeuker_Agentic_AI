"""
McLeuker Agentic AI Module
===========================

Manus-style agentic execution system with:
- Kimi 2.5 Client (instant/thinking/agent modes)
- Grok Client (real-time data + verification + fallback)
- Execution Orchestrator (plan → execute → verify → deliver)
- E2B Code Execution sandbox
- Browserless web automation
- WebSocket real-time streaming
"""

from .kimi25_client import Kimi25Client, KimiMode, KimiModeType, KimiResponse
from .grok_client import GrokClient, GrokResponse, FactCheckResult
from .execution_orchestrator import ExecutionOrchestrator, ExecutionResult, ExecutionStatus
from .e2b_integration import E2BManager, CodeExecutionResult
from .browserless_integration import BrowserlessClient, BrowserResult
from .websocket_handler import ExecutionWebSocketManager, get_websocket_manager

__all__ = [
    "Kimi25Client", "KimiMode", "KimiModeType", "KimiResponse",
    "GrokClient", "GrokResponse", "FactCheckResult",
    "ExecutionOrchestrator", "ExecutionResult", "ExecutionStatus",
    "E2BManager", "CodeExecutionResult",
    "BrowserlessClient", "BrowserResult",
    "ExecutionWebSocketManager", "get_websocket_manager",
]
