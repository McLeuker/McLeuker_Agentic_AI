"""
McLeuker Agentic Core — Engine, Planner, Execution Loop, Reflection, State
===========================================================================

The core agentic engine that powers end-to-end task execution:
- AgenticEngine: Main orchestration loop (plan → execute → reflect → revise)
- TaskPlanner: Creates structured execution plans from user requests
- ExecutionLoop: Executes individual steps with tool calling
- ReflectionEngine: Self-correction and learning from results
- StateManager: Session state persistence and checkpointing
"""

from .agentic_engine import AgenticEngine, AgenticConfig, ExecutionContext
from .task_planner import TaskPlanner, ExecutionPlan, TaskStep, StepType, StepStatus
from .execution_loop import ExecutionLoop, ExecutionResult, ExecutionStatus
from .reflection_engine import ReflectionEngine, ReflectionResult, ReflectionAction
from .state_manager import StateManager, SessionState

__all__ = [
    "AgenticEngine", "AgenticConfig", "ExecutionContext",
    "TaskPlanner", "ExecutionPlan", "TaskStep", "StepType", "StepStatus",
    "ExecutionLoop", "ExecutionResult", "ExecutionStatus",
    "ReflectionEngine", "ReflectionResult", "ReflectionAction",
    "StateManager", "SessionState",
]
