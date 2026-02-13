"""
Agent Loop V3 - Core Execution Engine for Agentic AI
=====================================================
Implements the main agent loop with:
- Task planning and decomposition (REACT-style)
- Step-by-step execution with tool orchestration
- Error recovery and retry with exponential backoff
- State management and human-in-the-loop support
- Real-time streaming via callbacks

Inspired by Manus AI's execution model and kimi-2.5's capabilities.
Integrates with existing ExecutionOrchestrator as an enhanced layer.
"""

import asyncio
import json
import logging
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ExecutionStatusV3(str, Enum):
    """Execution status for tasks and steps."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class StepTypeV3(str, Enum):
    """Types of execution steps."""
    THOUGHT = "thought"
    ACTION = "action"
    OBSERVATION = "observation"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    ERROR = "error"
    COMPLETION = "completion"
    PLAN = "plan"


class TaskPriority(int, Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ExecutionStepV3:
    """A single step in the execution."""
    id: str = field(default_factory=lambda: str(uuid4()))
    type: StepTypeV3 = StepTypeV3.THOUGHT
    content: str = ""
    tool_name: Optional[str] = None
    tool_input: Optional[Dict] = None
    tool_output: Optional[Any] = None
    status: ExecutionStatusV3 = ExecutionStatusV3.PENDING
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_ms: Optional[int] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    parent_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "tool_name": self.tool_name,
            "tool_input": self.tool_input,
            "tool_output": self.tool_output,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "error": self.error,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "parent_id": self.parent_id,
            "metadata": self.metadata,
        }


@dataclass
class TaskV3:
    """A task that can be executed by the agent."""
    id: str = field(default_factory=lambda: str(uuid4()))
    description: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    status: ExecutionStatusV3 = ExecutionStatusV3.PENDING
    steps: List[ExecutionStepV3] = field(default_factory=list)
    subtasks: List["TaskV3"] = field(default_factory=list)
    parent_id: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    max_iterations: int = 50
    current_iteration: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "steps": [s.to_dict() for s in self.steps],
            "subtasks": [t.to_dict() for t in self.subtasks],
            "parent_id": self.parent_id,
            "dependencies": self.dependencies,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "context": self.context,
            "max_iterations": self.max_iterations,
            "current_iteration": self.current_iteration,
        }


class ExecutionPlanV3(BaseModel):
    """A plan for executing a complex task."""
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    goal: str = ""
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    estimated_duration: Optional[int] = None
    required_tools: List[str] = Field(default_factory=list)
    context_requirements: List[str] = Field(default_factory=list)


class AgentConfigV3(BaseModel):
    """Configuration for the agent loop."""
    max_iterations: int = 50
    max_retries: int = 3
    retry_delay_base: float = 1.0
    enable_human_in_the_loop: bool = False
    human_confirmation_tools: List[str] = Field(default_factory=list)
    parallel_execution: bool = True
    max_parallel_tasks: int = 3
    thought_before_action: bool = True
    observation_after_action: bool = True
    # Model config — uses existing kimi client from main.py
    planning_model: str = "kimi-k2.5"
    reasoning_model: str = "kimi-k2.5"


# ---------------------------------------------------------------------------
# Agent Loop V3
# ---------------------------------------------------------------------------

class AgentLoopV3:
    """
    Main agent execution loop (V3).

    Implements the core agentic AI pattern:
    1. Plan  – Break down the task into steps
    2. Think – Generate reasoning about current state
    3. Act   – Execute tool calls
    4. Observe – Collect results
    5. Decide – Continue, retry, or complete

    Compatible with the existing tool_registry (set_handler / execute style)
    and the existing ExecutionOrchestrator event system.
    """

    def __init__(
        self,
        llm_client: Any,
        tool_registry: Any = None,
        memory_manager: Optional[Any] = None,
        config: Optional[AgentConfigV3] = None,
    ):
        self.llm_client = llm_client
        self.tool_registry = tool_registry
        self.memory_manager = memory_manager
        self.config = config or AgentConfigV3()

        # Execution state
        self.current_task: Optional[TaskV3] = None
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.execution_history: List[TaskV3] = []

        # Callbacks for streaming updates
        self._step_callbacks: List[Callable] = []
        self._task_callbacks: List[Callable] = []

        logger.info("AgentLoopV3 initialized with config: %s", self.config.model_dump())

    # -- Callback registration ------------------------------------------------

    def on_step(self, callback: Callable):
        self._step_callbacks.append(callback)
        return self

    def on_task_update(self, callback: Callable):
        self._task_callbacks.append(callback)
        return self

    async def _notify_step(self, step: ExecutionStepV3):
        for cb in self._step_callbacks:
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(step)
                else:
                    cb(step)
            except Exception as e:
                logger.error(f"Step callback error: {e}")

    async def _notify_task(self, task: TaskV3):
        for cb in self._task_callbacks:
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(task)
                else:
                    cb(task)
            except Exception as e:
                logger.error(f"Task callback error: {e}")

    # -- Planning -------------------------------------------------------------

    async def create_plan(self, goal: str, context: Dict[str, Any]) -> ExecutionPlanV3:
        """Create an execution plan using the LLM."""
        # Gather available tool names from the registry
        tool_names: List[str] = []
        if self.tool_registry:
            try:
                tool_names = list(self.tool_registry.get_tool_names())
            except Exception:
                try:
                    tool_names = [t["name"] for t in self.tool_registry.get_all_tools()]
                except Exception:
                    pass

        plan_prompt = f"""You are an expert task planner for an agentic AI system.
Break down the following goal into clear, actionable steps.

Goal: {goal}

Context: {json.dumps(context, indent=2, default=str)[:3000]}

Available tools: {tool_names}

Create a step-by-step plan. For each step, specify:
1. Step description
2. Required tool (if any)
3. Expected input
4. Success criteria

Respond in JSON format:
{{
    "steps": [
        {{
            "description": "step description",
            "tool": "tool_name or null",
            "input": {{}},
            "success_criteria": "how to verify success"
        }}
    ],
    "estimated_duration": 120,
    "required_tools": ["tool1", "tool2"],
    "context_requirements": ["what context is needed"]
}}"""

        try:
            response = await self.llm_client.chat.completions.create(
                model=self.config.planning_model,
                messages=[{"role": "user", "content": plan_prompt}],
                temperature=0.3,
                response_format={"type": "json_object"},
            )
            raw = response.choices[0].message.content or "{}"
            plan_data = json.loads(raw)
            plan = ExecutionPlanV3(
                goal=goal,
                steps=plan_data.get("steps", []),
                estimated_duration=plan_data.get("estimated_duration"),
                required_tools=plan_data.get("required_tools", []),
                context_requirements=plan_data.get("context_requirements", []),
            )
            logger.info(f"Created plan with {len(plan.steps)} steps")
            return plan
        except Exception as e:
            logger.error(f"Plan creation failed: {e}")
            return ExecutionPlanV3(
                goal=goal,
                steps=[{"description": goal, "tool": None, "input": {}}],
            )

    # -- Step execution -------------------------------------------------------

    async def execute_step(self, step: ExecutionStepV3, task: TaskV3) -> ExecutionStepV3:
        """Execute a single step with tool dispatch."""
        start_time = datetime.utcnow()
        step.status = ExecutionStatusV3.RUNNING
        await self._notify_step(step)

        try:
            if step.type == StepTypeV3.TOOL_CALL and step.tool_name:
                result = await self._execute_tool(step.tool_name, step.tool_input or {})
                step.tool_output = result
                step.status = ExecutionStatusV3.COMPLETED

            elif step.type == StepTypeV3.THOUGHT:
                thought = await self._generate_thought(task)
                step.content = thought
                step.status = ExecutionStatusV3.COMPLETED

            elif step.type == StepTypeV3.ACTION:
                # Action may have a tool attached
                if step.tool_name:
                    result = await self._execute_tool(step.tool_name, step.tool_input or {})
                    step.tool_output = result
                step.status = ExecutionStatusV3.COMPLETED

            else:
                step.status = ExecutionStatusV3.COMPLETED

        except Exception as e:
            step.error = str(e)
            step.status = ExecutionStatusV3.FAILED
            logger.error(f"Step execution failed: {e}")
            logger.debug(traceback.format_exc())

        step.duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        await self._notify_step(step)
        return step

    async def _execute_tool(self, tool_name: str, tool_input: Dict) -> Any:
        """Execute a tool through the registry — compatible with both old and new registry."""
        if not self.tool_registry:
            raise RuntimeError("No tool registry configured")

        # Try new-style registry (get_tool -> execute)
        try:
            tool = self.tool_registry.get_tool(tool_name)
            if tool and hasattr(tool, "execute"):
                return await tool.execute(tool_input)
        except Exception:
            pass

        # Fallback: old-style registry (execute with name)
        try:
            if hasattr(self.tool_registry, "execute"):
                return await self.tool_registry.execute(tool_name, tool_input)
        except Exception:
            pass

        # Fallback: handler-based registry
        try:
            if hasattr(self.tool_registry, "get_handler"):
                handler = self.tool_registry.get_handler(tool_name)
                if handler:
                    if asyncio.iscoroutinefunction(handler):
                        return await handler(**tool_input)
                    return handler(**tool_input)
        except Exception:
            pass

        raise RuntimeError(f"Tool '{tool_name}' not found or not executable")

    async def _generate_thought(self, task: TaskV3) -> str:
        """Generate a thought about the current state and next action."""
        recent_steps = task.steps[-5:] if task.steps else []
        thought_prompt = f"""Based on the current task and execution history, what should be the next step?

Task: {task.description}

Execution history:
{json.dumps([s.to_dict() for s in recent_steps], indent=2, default=str)[:2000]}

Current context:
{json.dumps(task.context, indent=2, default=str)[:1000]}

Provide your reasoning and recommend the next action."""

        try:
            response = await self.llm_client.chat.completions.create(
                model=self.config.reasoning_model,
                messages=[{"role": "user", "content": thought_prompt}],
                temperature=0.7,
                max_tokens=500,
            )
            return response.choices[0].message.content or "Continuing with task execution..."
        except Exception as e:
            logger.error(f"Thought generation failed: {e}")
            return "Continuing with task execution..."

    # -- Retry logic ----------------------------------------------------------

    async def _should_retry(self, step: ExecutionStepV3) -> bool:
        if step.status != ExecutionStatusV3.FAILED:
            return False
        if step.retry_count >= step.max_retries:
            return False
        if step.retry_count >= self.config.max_retries:
            return False
        return True

    async def _retry_step(self, step: ExecutionStepV3) -> ExecutionStepV3:
        step.retry_count += 1
        step.status = ExecutionStatusV3.RETRYING
        await self._notify_step(step)
        delay = self.config.retry_delay_base * (2 ** (step.retry_count - 1))
        logger.info(f"Retrying step {step.id} in {delay}s (attempt {step.retry_count})")
        await asyncio.sleep(delay)
        return step

    # -- Main task runner -----------------------------------------------------

    async def run_task(
        self,
        description: str,
        context: Optional[Dict[str, Any]] = None,
        plan: Optional[ExecutionPlanV3] = None,
    ) -> AsyncGenerator[ExecutionStepV3, None]:
        """Run a task from start to completion, yielding steps for real-time streaming."""
        task = TaskV3(
            description=description,
            context=context or {},
            max_iterations=self.config.max_iterations,
        )
        self.current_task = task
        task.status = ExecutionStatusV3.RUNNING
        await self._notify_task(task)

        # Planning phase
        if not plan:
            plan_step = ExecutionStepV3(type=StepTypeV3.PLAN, content="Creating execution plan...")
            task.steps.append(plan_step)
            await self._notify_step(plan_step)
            yield plan_step

            plan = await self.create_plan(description, task.context)
            plan_step.content = f"Plan created with {len(plan.steps)} steps"
            plan_step.status = ExecutionStatusV3.COMPLETED
            plan_step.metadata["plan"] = plan.model_dump()
            await self._notify_step(plan_step)
            yield plan_step

        # Execute plan steps
        for plan_step_data in plan.steps:
            if task.current_iteration >= task.max_iterations:
                task.error = "Maximum iterations reached"
                task.status = ExecutionStatusV3.FAILED
                break

            task.current_iteration += 1

            # Thought step
            if self.config.thought_before_action:
                thought_step = ExecutionStepV3(type=StepTypeV3.THOUGHT, content="Analyzing current state...")
                task.steps.append(thought_step)
                await self._notify_step(thought_step)
                yield thought_step

                thought = await self._generate_thought(task)
                thought_step.content = thought
                thought_step.status = ExecutionStatusV3.COMPLETED
                await self._notify_step(thought_step)
                yield thought_step

            # Action step
            action_step = ExecutionStepV3(
                type=StepTypeV3.ACTION,
                content=plan_step_data.get("description", ""),
                tool_name=plan_step_data.get("tool"),
                tool_input=plan_step_data.get("input", {}),
            )
            task.steps.append(action_step)

            # Execute with retry
            while True:
                await self.execute_step(action_step, task)
                yield action_step

                if action_step.status == ExecutionStatusV3.COMPLETED:
                    break
                if await self._should_retry(action_step):
                    await self._retry_step(action_step)
                else:
                    break

            # Human-in-the-loop pause
            if (
                self.config.enable_human_in_the_loop
                and action_step.tool_name in self.config.human_confirmation_tools
            ):
                action_step.status = ExecutionStatusV3.PAUSED
                await self._notify_step(action_step)
                yield action_step

            # Observation step
            if self.config.observation_after_action and action_step.status == ExecutionStatusV3.COMPLETED:
                output_preview = ""
                if action_step.tool_output:
                    output_preview = json.dumps(action_step.tool_output, indent=2, default=str)[:500]
                obs_step = ExecutionStepV3(
                    type=StepTypeV3.OBSERVATION,
                    content=f"Result: {output_preview}..." if output_preview else "Action completed successfully",
                    tool_name=action_step.tool_name,
                    tool_output=action_step.tool_output,
                    status=ExecutionStatusV3.COMPLETED,
                )
                task.steps.append(obs_step)
                await self._notify_step(obs_step)
                yield obs_step

        # Completion
        if task.status == ExecutionStatusV3.RUNNING:
            task.status = ExecutionStatusV3.COMPLETED
            task.completed_at = datetime.utcnow()

            completion_step = ExecutionStepV3(
                type=StepTypeV3.COMPLETION,
                content=f"Task completed in {len(task.steps)} steps",
                status=ExecutionStatusV3.COMPLETED,
            )
            task.steps.append(completion_step)
            await self._notify_step(completion_step)
            yield completion_step

        await self._notify_task(task)
        self.execution_history.append(task)
        self.current_task = None

    # -- Parallel execution ---------------------------------------------------

    async def run_parallel_tasks(self, tasks: List[TaskV3]) -> AsyncGenerator[ExecutionStepV3, None]:
        """Run multiple tasks in parallel where possible, respecting dependencies."""
        if not self.config.parallel_execution:
            for task in tasks:
                async for step in self.run_task(task.description, task.context):
                    yield step
            return

        completed_tasks: set = set()
        running_tasks: Dict[str, asyncio.Task] = {}

        async def _run_single(task: TaskV3):
            async for _ in self.run_task(task.description, task.context):
                pass
            completed_tasks.add(task.id)

        remaining = set(t.id for t in tasks)
        while remaining:
            ready = [
                t for t in tasks
                if t.id in remaining
                and all(dep in completed_tasks for dep in t.dependencies)
                and t.id not in running_tasks
            ]
            while len(running_tasks) < self.config.max_parallel_tasks and ready:
                t = ready.pop(0)
                running_tasks[t.id] = asyncio.create_task(_run_single(t))
                remaining.discard(t.id)

            if running_tasks:
                done, _ = await asyncio.wait(running_tasks.values(), return_when=asyncio.FIRST_COMPLETED)
                for d in done:
                    for tid, at in list(running_tasks.items()):
                        if at == d:
                            del running_tasks[tid]
                            break
            else:
                break

    # -- Helpers --------------------------------------------------------------

    def get_execution_history(self, limit: int = 10) -> List[TaskV3]:
        return self.execution_history[-limit:]

    def get_current_task(self) -> Optional[TaskV3]:
        return self.current_task
