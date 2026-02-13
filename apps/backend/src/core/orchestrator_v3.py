"""
Agent Orchestrator V3 - Central Coordination for Agentic AI
=============================================================
Coordinates all agentic components:
- AgentLoopV3 for task execution
- UnifiedToolRegistryV2 for tool management
- RAGSystemV3 for knowledge retrieval
- WebSocket V2 for real-time streaming

Integrates with the existing ExecutionOrchestrator (V1/V2) as an
enhanced layer — does NOT replace it. The existing SSE streaming
in main.py continues to work; this adds structured agent execution.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional
from uuid import uuid4

# V3 imports — all within the repo
from src.agentic.loop_v3 import (
    AgentLoopV3, AgentConfigV3, ExecutionStepV3, StepTypeV3, TaskV3,
)
from src.agentic.memory.rag_v3 import RAGSystemV3, ContextualRAGV3
from src.api.v2.websocket_v2 import ExecutionStreamManagerV2
from src.tools.unified_registry_v2 import UnifiedToolRegistryV2

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@dataclass
class OrchestratorConfigV3:
    """Configuration for the V3 orchestrator."""
    max_iterations: int = 50
    max_retries: int = 3
    enable_human_in_the_loop: bool = False
    enable_rag: bool = True
    rag_top_k: int = 5
    enable_streaming: bool = True
    stream_screenshots: bool = True
    browser_headless: bool = True
    browser_viewport: Dict[str, int] = field(
        default_factory=lambda: {"width": 1280, "height": 720}
    )
    planning_model: str = "kimi-k2.5"
    reasoning_model: str = "kimi-k2.5"


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class AgentOrchestratorV3:
    """
    Central orchestrator for agentic AI execution (V3).

    Usage:
        orchestrator = AgentOrchestratorV3(
            llm_client=kimi_client,
            tool_registry=registry,
            rag_system=rag,
            stream_manager=stream_mgr,
        )
        async for step in orchestrator.execute_task("Search for..."):
            print(step)
    """

    def __init__(
        self,
        llm_client: Any,
        tool_registry: Optional[UnifiedToolRegistryV2] = None,
        rag_system: Optional[RAGSystemV3] = None,
        stream_manager: Optional[ExecutionStreamManagerV2] = None,
        config: Optional[OrchestratorConfigV3] = None,
    ):
        self.llm_client = llm_client
        self.tool_registry = tool_registry or UnifiedToolRegistryV2()
        self.rag_system = rag_system
        self.stream_manager = stream_manager
        self.config = config or OrchestratorConfigV3()

        # Initialize agent loop
        agent_config = AgentConfigV3(
            max_iterations=self.config.max_iterations,
            max_retries=self.config.max_retries,
            enable_human_in_the_loop=self.config.enable_human_in_the_loop,
            parallel_execution=True,
            thought_before_action=True,
            observation_after_action=True,
            planning_model=self.config.planning_model,
            reasoning_model=self.config.reasoning_model,
        )

        self.agent_loop = AgentLoopV3(
            llm_client=llm_client,
            tool_registry=self.tool_registry,
            memory_manager=None,
            config=agent_config,
        )

        # Wire callbacks
        if self.stream_manager:
            self.agent_loop.on_step(self._on_step_update)
            self.agent_loop.on_task_update(self._on_task_update)

        # Active executions
        self._active_executions: Dict[str, str] = {}  # exec_id -> conv_id

        logger.info("AgentOrchestratorV3 initialized")

    # -- Callbacks -------------------------------------------------------------

    async def _on_step_update(self, step: ExecutionStepV3):
        if not self.stream_manager:
            return
        for exec_id in list(self._active_executions):
            await self.stream_manager.stream_step(exec_id, step.to_dict())
            if step.type == StepTypeV3.THOUGHT:
                await self.stream_manager.stream_thought(exec_id, step.content)
            elif step.type == StepTypeV3.TOOL_CALL:
                await self.stream_manager.stream_tool_call(
                    exec_id, step.tool_name or "unknown", step.tool_input or {},
                )
            elif step.type == StepTypeV3.OBSERVATION and step.tool_output:
                await self.stream_manager.stream_tool_result(
                    exec_id, step.tool_name or "unknown", step.tool_output, success=True,
                )
            if step.metadata.get("screenshot"):
                await self.stream_manager.stream_screenshot(
                    exec_id, step.metadata["screenshot"], {"step_type": step.type.value},
                )
            break

    async def _on_task_update(self, task: TaskV3):
        logger.info(f"Task update: {task.id} - {task.status.value}")

    # -- Execution -------------------------------------------------------------

    async def execute_task(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> AsyncGenerator[ExecutionStepV3, None]:
        """Execute a task with full orchestration, yielding steps."""
        execution_id = str(uuid4())
        if conversation_id:
            self._active_executions[execution_id] = conversation_id

        try:
            if self.stream_manager and conversation_id:
                await self.stream_manager.start_execution_stream(
                    execution_id, conversation_id, user_id,
                )

            # Enhance context with RAG
            enhanced_context = dict(context or {})
            if self.config.enable_rag and self.rag_system:
                try:
                    rag_results = await self.rag_system.get_context_for_query(
                        task_description, max_tokens=2000,
                        user_id=user_id, conversation_id=conversation_id,
                    )
                    enhanced_context["retrieved_context"] = rag_results["context"]
                    enhanced_context["sources"] = rag_results["sources"]
                except Exception as e:
                    logger.warning(f"RAG retrieval failed: {e}")

            # Run through agent loop
            async for step in self.agent_loop.run_task(
                description=task_description,
                context=enhanced_context,
            ):
                yield step

            if self.stream_manager and conversation_id:
                await self.stream_manager.end_execution_stream(execution_id, success=True)

        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            if self.stream_manager and conversation_id:
                await self.stream_manager.stream_error(execution_id, str(e))
                await self.stream_manager.end_execution_stream(execution_id, success=False)
            raise
        finally:
            self._active_executions.pop(execution_id, None)

    async def execute_with_planning(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a task with explicit planning phase. Returns full result."""
        execution_id = str(uuid4())
        all_steps = []
        try:
            plan = await self.agent_loop.create_plan(goal, context or {})
            async for step in self.execute_task(
                task_description=goal, context=context, conversation_id=conversation_id,
            ):
                all_steps.append(step.to_dict())
            return {
                "execution_id": execution_id,
                "goal": goal,
                "plan": plan.model_dump(),
                "steps": all_steps,
                "success": True,
            }
        except Exception as e:
            return {
                "execution_id": execution_id,
                "goal": goal,
                "steps": all_steps,
                "success": False,
                "error": str(e),
            }

    async def quick_execute(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Quick execution without streaming. Returns final result only."""
        result = None
        async for step in self.execute_task(task_description, context):
            if step.type == StepTypeV3.COMPLETION:
                result = step.metadata.get("result")
        return result

    # -- Knowledge management --------------------------------------------------

    async def add_knowledge(
        self, content: str, source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> List[str]:
        if not self.rag_system:
            logger.warning("RAG system not configured")
            return []
        return await self.rag_system.add_document(
            content=content, source=source, metadata=metadata, user_id=user_id,
        )

    # -- Introspection ---------------------------------------------------------

    def get_available_tools(self) -> List[Dict[str, Any]]:
        return self.tool_registry.get_openai_schemas()

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        tool = self.tool_registry.get_tool(tool_name)
        if tool:
            return tool.get_definition().model_dump()
        return None

    def get_stats(self) -> Dict[str, Any]:
        return {
            "active_executions": len(self._active_executions),
            "tool_registry": self.tool_registry.get_stats(),
            "config": {
                "max_iterations": self.config.max_iterations,
                "enable_rag": self.config.enable_rag,
                "enable_streaming": self.config.enable_streaming,
            },
        }
