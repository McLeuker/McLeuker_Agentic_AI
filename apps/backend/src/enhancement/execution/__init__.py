"""
Execution Engine
==================
True end-to-end execution capabilities for web automation,
credential management, and autonomous task completion.
"""

from .execution_engine import ExecutionEngine, ExecutionTask, ExecutionResult
from .web_executor import WebExecutor
from .credential_manager import CredentialManager
from .task_decomposer import TaskDecomposer

__all__ = [
    "ExecutionEngine",
    "ExecutionTask",
    "ExecutionResult",
    "WebExecutor",
    "CredentialManager",
    "TaskDecomposer",
]
