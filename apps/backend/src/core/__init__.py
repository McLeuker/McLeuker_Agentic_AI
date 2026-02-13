"""
Core Module — Execution engine and infrastructure
"""

try:
    from .execution_engine import ExecutionEngine, ExecutionState
except ImportError:
    ExecutionEngine = None
    ExecutionState = None

try:
    from .websocket_manager import ExecutionWebSocketManager
except ImportError:
    ExecutionWebSocketManager = None

try:
    from .orchestrator_v3 import AgentOrchestratorV3, OrchestratorConfigV3
except ImportError:
    AgentOrchestratorV3 = None
    OrchestratorConfigV3 = None

__all__ = [
    'ExecutionEngine',
    'ExecutionState',
    'ExecutionWebSocketManager',
    'AgentOrchestratorV3',
    'OrchestratorConfigV3',
]
