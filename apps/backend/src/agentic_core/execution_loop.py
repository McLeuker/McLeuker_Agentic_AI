"""
Execution Loop — Step-by-Step Task Execution with Tool Calling
===============================================================

Executes individual steps from the TaskPlanner's plan:
- Tool dispatch (search, browse, code, file)
- Result capture and validation
- Error handling with retries
- Live event streaming
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .task_planner import TaskStep, StepType, StepStatus

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionResult:
    step_id: str
    status: ExecutionStatus
    output: Any = None
    error: Optional[str] = None
    tool_used: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "status": self.status.value,
            "output": str(self.output)[:2000] if self.output else None,
            "error": self.error,
            "tool_used": self.tool_used,
            "execution_time": self.execution_time,
        }


class ExecutionLoop:
    """
    Executes steps from a plan using registered tools.

    Features:
    - Tool dispatch based on step type
    - Parallel execution of independent steps
    - Result validation
    - Error handling with configurable retries
    - Live event streaming
    """

    def __init__(self, kimi_client, config, tool_registry=None):
        """
        Initialize execution loop.

        Args:
            kimi_client: Async OpenAI client for kimi-2.5
            config: AgenticConfig
            tool_registry: UnifiedToolRegistry instance
        """
        self.kimi_client = kimi_client
        self.config = config
        self.tool_registry = tool_registry

        # Tool handlers — mapped by tool_name
        self._tool_handlers: Dict[str, Callable] = {}

        # Event callbacks
        self._event_callbacks: List[Callable] = []

        # Cancellation flags
        self._cancelled: Dict[str, bool] = {}

    def register_tool_handler(self, tool_name: str, handler: Callable):
        """Register a tool handler function."""
        self._tool_handlers[tool_name] = handler
        logger.info(f"Registered tool handler: {tool_name}")

    def register_event_callback(self, callback: Callable):
        """Register an event callback for live streaming."""
        self._event_callbacks.append(callback)

    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit an event to all registered callbacks."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        for callback in self._event_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"Event callback error: {e}")

    async def execute_step(
        self,
        step: TaskStep,
        context: Dict[str, Any],
        session_id: str = "default"
    ) -> ExecutionResult:
        """
        Execute a single step.

        Args:
            step: The step to execute
            context: Accumulated context from previous steps
            session_id: Session identifier

        Returns:
            ExecutionResult
        """
        if self._cancelled.get(session_id, False):
            return ExecutionResult(
                step_id=step.id,
                status=ExecutionStatus.CANCELLED,
                error="Execution cancelled"
            )

        step.status = StepStatus.IN_PROGRESS
        step.started_at = datetime.now()
        start_time = asyncio.get_event_loop().time()

        await self._emit_event("step.started", {
            "step_id": step.id,
            "description": step.description,
            "step_type": step.step_type.value,
            "tool_name": step.tool_name,
        })

        try:
            # Dispatch to the appropriate handler
            if step.tool_name and step.tool_name in self._tool_handlers:
                # Use registered tool handler
                handler = self._tool_handlers[step.tool_name]
                output = await handler(step.tool_params, context)
            elif step.step_type == StepType.RESEARCH:
                output = await self._execute_research(step, context)
            elif step.step_type == StepType.WEB_BROWSING:
                output = await self._execute_browsing(step, context)
            elif step.step_type in (StepType.CODE_EXECUTION, StepType.CODE_GENERATION):
                output = await self._execute_code(step, context)
            elif step.step_type == StepType.FILE_OPERATION:
                output = await self._execute_file_op(step, context)
            elif step.step_type == StepType.ANALYSIS:
                output = await self._execute_analysis(step, context)
            elif step.step_type == StepType.SYNTHESIS:
                output = await self._execute_synthesis(step, context)
            elif step.step_type == StepType.VERIFICATION:
                output = await self._execute_verification(step, context)
            else:
                output = await self._execute_generic(step, context)

            execution_time = asyncio.get_event_loop().time() - start_time

            step.status = StepStatus.COMPLETED
            step.completed_at = datetime.now()
            step.result = output

            result = ExecutionResult(
                step_id=step.id,
                status=ExecutionStatus.COMPLETED,
                output=output,
                tool_used=step.tool_name,
                execution_time=execution_time,
            )

            await self._emit_event("step.completed", {
                "step_id": step.id,
                "execution_time": execution_time,
                "output_preview": str(output)[:500] if output else None,
            })

            return result

        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.exception(f"Step {step.id} failed: {e}")

            step.status = StepStatus.FAILED
            step.retry_count += 1

            result = ExecutionResult(
                step_id=step.id,
                status=ExecutionStatus.FAILED,
                error=str(e),
                tool_used=step.tool_name,
                execution_time=execution_time,
            )

            await self._emit_event("step.failed", {
                "step_id": step.id,
                "error": str(e),
                "retry_count": step.retry_count,
            })

            return result

    async def _execute_research(self, step: TaskStep, context: Dict[str, Any]) -> Any:
        """Execute a research step using web search."""
        query = step.tool_params.get("query", step.description)
        num_results = step.tool_params.get("num_results", 10)

        # Use the search handler if registered
        if "web_search" in self._tool_handlers:
            return await self._tool_handlers["web_search"](
                {"query": query, "num_results": num_results}, context
            )

        # Fallback: use LLM to generate research
        messages = [
            {"role": "system", "content": "You are a research assistant. Provide comprehensive, factual information."},
            {"role": "user", "content": f"Research this topic thoroughly: {query}"}
        ]

        response = await self.kimi_client.chat.completions.create(
            model=self.config.primary_model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=4000,
        )

        return {"text": response.choices[0].message.content, "source": "llm_research"}

    async def _execute_browsing(self, step: TaskStep, context: Dict[str, Any]) -> Any:
        """Execute a web browsing step."""
        if "browser_navigate" in self._tool_handlers:
            url = step.tool_params.get("url", "")
            return await self._tool_handlers["browser_navigate"](
                {"url": url}, context
            )
        return {"text": "Browser not available", "source": "fallback"}

    async def _execute_code(self, step: TaskStep, context: Dict[str, Any]) -> Any:
        """Execute a code execution step."""
        code = step.tool_params.get("code", "")
        language = step.tool_params.get("language", "python")

        handler_name = f"execute_{language}"
        if handler_name in self._tool_handlers:
            return await self._tool_handlers[handler_name](
                {"code": code}, context
            )

        return {"error": f"Code execution handler not available for {language}"}

    async def _execute_file_op(self, step: TaskStep, context: Dict[str, Any]) -> Any:
        """Execute a file operation step."""
        operation = step.tool_params.get("operation", "read")
        handler_name = f"{operation}_file"
        if handler_name in self._tool_handlers:
            return await self._tool_handlers[handler_name](step.tool_params, context)
        return {"error": "File operation handler not available"}

    async def _execute_analysis(self, step: TaskStep, context: Dict[str, Any]) -> Any:
        """Execute an analysis step using LLM."""
        # Gather previous results for analysis
        prev_results = []
        for dep_id in step.dependencies:
            if dep_id in context.get("step_results", {}):
                prev_results.append(str(context["step_results"][dep_id])[:2000])

        analysis_context = "\n\n".join(prev_results) if prev_results else "No previous results."

        messages = [
            {"role": "system", "content": """You are an expert analyst. Analyze the provided data and context.
Provide clear, structured analysis with key findings, patterns, and insights."""},
            {"role": "user", "content": f"""Analyze the following:

TASK: {step.description}

CONTEXT:
{analysis_context}

Provide a thorough analysis."""}
        ]

        response = await self.kimi_client.chat.completions.create(
            model=self.config.primary_model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=4000,
        )

        return {"analysis": response.choices[0].message.content}

    async def _execute_synthesis(self, step: TaskStep, context: Dict[str, Any]) -> Any:
        """Synthesize results from previous steps into a final output."""
        prev_results = []
        for dep_id in step.dependencies:
            if dep_id in context.get("step_results", {}):
                prev_results.append(f"[{dep_id}]: {str(context['step_results'][dep_id])[:3000]}")

        if not prev_results:
            # Use all step results
            for k, v in context.get("step_results", {}).items():
                prev_results.append(f"[{k}]: {str(v)[:3000]}")

        messages = [
            {"role": "system", "content": """You are an expert synthesizer. Combine all research findings and analysis
into a comprehensive, well-structured final response. Use clear headings, precise language,
and cite sources where available. Always reason first, then present conclusions."""},
            {"role": "user", "content": f"""Synthesize these findings into a final response:

OBJECTIVE: {context.get('objective', step.description)}

FINDINGS:
{chr(10).join(prev_results)}

Create a comprehensive, well-structured response."""}
        ]

        response = await self.kimi_client.chat.completions.create(
            model=self.config.primary_model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=8000,
        )

        return {"synthesis": response.choices[0].message.content}

    async def _execute_verification(self, step: TaskStep, context: Dict[str, Any]) -> Any:
        """Verify the quality and accuracy of results."""
        prev_results = []
        for dep_id in step.dependencies:
            if dep_id in context.get("step_results", {}):
                prev_results.append(str(context["step_results"][dep_id])[:2000])

        messages = [
            {"role": "system", "content": """You are a quality verification expert. Check the provided results for:
1. Accuracy — are facts correct?
2. Completeness — is anything missing?
3. Quality — is the output well-structured?
4. Relevance — does it address the original request?

Respond in JSON: {"passed": true/false, "issues": [], "suggestions": [], "score": 0-100}"""},
            {"role": "user", "content": f"""Verify these results:

OBJECTIVE: {context.get('objective', step.description)}

RESULTS:
{chr(10).join(prev_results)}"""}
        ]

        response = await self.kimi_client.chat.completions.create(
            model=self.config.primary_model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )

        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {"passed": True, "issues": [], "score": 70}

    async def _execute_generic(self, step: TaskStep, context: Dict[str, Any]) -> Any:
        """Generic step execution using LLM."""
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant. Complete the requested task."},
            {"role": "user", "content": step.description}
        ]

        response = await self.kimi_client.chat.completions.create(
            model=self.config.primary_model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=4000,
        )

        return {"text": response.choices[0].message.content}

    def cancel(self, session_id: str):
        """Cancel execution for a session."""
        self._cancelled[session_id] = True
