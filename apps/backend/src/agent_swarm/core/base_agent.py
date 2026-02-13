"""
Base Agent Class - Foundation for All 100+ Agents
=================================================

All agents in the swarm inherit from this base class.
Provides:
- Standardized execution interface
- Tool integration
- Memory access
- Communication with coordinator
- State management
- Error handling
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, AsyncGenerator
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class AgentState:
    """State maintained by an agent during execution."""
    session_id: str = field(default_factory=lambda: str(uuid4()))
    memory: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    tools_available: List[str] = field(default_factory=list)
    execution_history: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AgentResult:
    """Result from agent execution."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: Optional[int] = None


class BaseSwarmAgent(ABC):
    """
    Base class for all agents in the swarm.
    
    Agents are specialized AI workers that can:
    - Execute specific types of tasks
    - Use tools to accomplish goals
    - Maintain state across executions
    - Communicate with other agents
    - Stream progress updates
    """
    
    # Agent identification
    name: str = "base_agent"
    description: str = "Base agent class"
    version: str = "1.0.0"
    
    # Capabilities
    supported_task_types: List[str] = []
    required_tools: List[str] = []
    
    # Configuration
    max_execution_time: int = 300  # seconds
    max_retries: int = 3
    stream_updates: bool = True
    
    def __init__(
        self,
        llm_client: Optional[Any] = None,
        tool_registry: Optional[Any] = None,
        memory_manager: Optional[Any] = None,
        coordinator: Optional[Any] = None,
    ):
        self.llm_client = llm_client
        self.tool_registry = tool_registry
        self.memory_manager = memory_manager
        self.coordinator = coordinator
        
        # State
        self.state = AgentState()
        
        # Callbacks for streaming
        self._progress_callbacks: List[Callable[[Dict], None]] = []
        
        # Execution tracking
        self._current_execution: Optional[str] = None
        self._is_running: bool = False
        
        logger.info(f"Initialized agent: {self.name}")

    def on_progress(self, callback: Callable[[Dict], None]):
        """Register a progress callback for streaming updates."""
        self._progress_callbacks.append(callback)
        return self

    async def _notify_progress(self, update: Dict[str, Any]):
        """Notify all progress callbacks."""
        for callback in self._progress_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(update)
                else:
                    callback(update)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")

    @abstractmethod
    async def execute(
        self,
        task_description: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """
        Execute the agent's primary function.
        
        Args:
            task_description: Description of what to do
            input_data: Input parameters
            context: Additional execution context
        
        Returns:
            AgentResult with success/failure and data
        """
        pass

    async def execute_streaming(
        self,
        task_description: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute with streaming progress updates.
        
        Yields progress updates throughout execution.
        """
        yield {"type": "started", "task": task_description, "agent": self.name}
        
        start_time = time.time()
        result = await self.execute(task_description, input_data, context)
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        yield {
            "type": "completed",
            "result": result,
            "execution_time_ms": elapsed_ms,
            "agent": self.name,
        }

    async def plan_execution(
        self,
        task_description: str,
        input_data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Create an execution plan for the task.
        Uses LLM to break down the task into steps.
        """
        if not self.llm_client:
            return [{"action": "execute", "description": task_description}]
        
        prompt = f"""Create a step-by-step plan to accomplish this task.

Task: {task_description}

Input Data: {str(input_data)[:500]}

Available Tools: {self.required_tools}

Create a plan with specific steps. Each step should have:
- action: what to do
- description: detailed description
- tool: tool to use (if any)
- expected_output: what to expect

Respond in JSON format as a list of steps."""

        try:
            import json
            response = self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            
            content = response.choices[0].message.content
            # Try to extract JSON from the response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            plan = json.loads(content)
            
            if isinstance(plan, dict) and "steps" in plan:
                return plan["steps"]
            elif isinstance(plan, list):
                return plan
            else:
                return [{"action": "execute", "description": task_description}]
                
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return [{"action": "execute", "description": task_description}]

    async def use_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
    ) -> Any:
        """Use a tool from the registry."""
        if not self.tool_registry:
            raise RuntimeError("Tool registry not available")
        
        await self._notify_progress({
            "type": "tool_call",
            "tool": tool_name,
            "params": params,
            "agent": self.name,
        })
        
        # Support both execute() and run() methods on the registry
        if hasattr(self.tool_registry, 'execute'):
            result = await self.tool_registry.execute(tool_name, params)
        elif hasattr(self.tool_registry, 'run'):
            result = await self.tool_registry.run(tool_name, params)
        else:
            raise RuntimeError(f"Tool registry has no execute/run method")
        
        await self._notify_progress({
            "type": "tool_result",
            "tool": tool_name,
            "result": str(result)[:500],
            "agent": self.name,
        })
        
        return result

    async def query_memory(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Query the memory system for relevant context."""
        if not self.memory_manager:
            return []
        
        try:
            if hasattr(self.memory_manager, 'search'):
                return await self.memory_manager.search(query, top_k)
            elif hasattr(self.memory_manager, 'query'):
                return await self.memory_manager.query(query, top_k=top_k)
        except Exception as e:
            logger.warning(f"Memory query failed: {e}")
        return []

    async def store_memory(self, key: str, value: Any):
        """Store data in agent memory."""
        self.state.memory[key] = value

    def can_handle(self, task_description: str) -> float:
        """
        Check if this agent can handle a task.
        Returns confidence score (0.0 - 1.0).
        """
        task_lower = task_description.lower()
        
        score = 0.0
        for task_type in self.supported_task_types:
            if task_type.lower() in task_lower:
                score += 0.3
        
        return min(score, 1.0)

    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities."""
        return self.supported_task_types

    def get_state(self) -> Dict[str, Any]:
        """Get current agent state."""
        return {
            "session_id": self.state.session_id,
            "memory_keys": list(self.state.memory.keys()),
            "execution_count": len(self.state.execution_history),
            "created_at": self.state.created_at.isoformat(),
        }

    def reset_state(self):
        """Reset agent state."""
        self.state = AgentState()
        logger.info(f"Reset state for agent: {self.name}")

    async def collaborate(
        self,
        agent_name: str,
        task_description: str,
        input_data: Dict[str, Any],
    ) -> AgentResult:
        """Collaborate with another agent via the coordinator."""
        if not self.coordinator:
            return AgentResult(
                success=False,
                error="Coordinator not available for collaboration",
            )
        
        task_id = await self.coordinator.submit_task(
            description=task_description,
            input_data=input_data,
            preferred_agent=agent_name,
        )
        
        task = await self.coordinator.wait_for_task(task_id)
        
        if not task:
            return AgentResult(success=False, error="Collaboration task timed out")
        
        if task.status == "completed":
            return AgentResult(success=True, data=task.result)
        else:
            return AgentResult(success=False, error=task.error)

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "capabilities": self.supported_task_types,
            "required_tools": self.required_tools,
            "state": self.get_state(),
        }
