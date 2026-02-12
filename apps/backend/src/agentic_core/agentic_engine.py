"""
Agentic Engine — Main Orchestration Loop
==========================================

The central engine that powers end-to-end agentic execution:
  Plan → Execute → Reflect → Revise → Deliver

Integrates:
- TaskPlanner for structured plan generation
- ExecutionLoop for step-by-step execution
- ReflectionEngine for self-correction
- StateManager for session persistence
- EventBus for real-time streaming

Architecture:
  User Request → Mode Router → Reasoning → Plan → [Execute Step → Reflect → (Revise?)] → Synthesize → Deliver
"""

import asyncio
import json
import uuid
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .task_planner import TaskPlanner, ExecutionPlan, TaskStep, StepStatus
from .execution_loop import ExecutionLoop, ExecutionResult, ExecutionStatus
from .reflection_engine import ReflectionEngine, ReflectionResult, ReflectionAction
from .state_manager import StateManager, SessionState

logger = logging.getLogger(__name__)


@dataclass
class AgenticConfig:
    """Configuration for the agentic engine."""
    primary_model: str = "kimi-k2.5"
    reasoning_model: str = "grok-4-1-fast-reasoning"
    fast_model: str = "grok-3-mini"
    temperature: float = 1.0
    max_steps: int = 20
    max_retries_per_step: int = 3
    max_plan_revisions: int = 2
    reflection_enabled: bool = True
    checkpoint_enabled: bool = True
    timeout_seconds: int = 300
    stream_events: bool = True


@dataclass
class ExecutionContext:
    """Context accumulated during execution."""
    session_id: str
    user_id: Optional[str] = None
    objective: str = ""
    mode: str = "auto"
    plan: Optional[ExecutionPlan] = None
    step_results: Dict[str, Any] = field(default_factory=dict)
    accumulated_context: Dict[str, Any] = field(default_factory=dict)
    messages: List[Dict[str, str]] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "objective": self.objective,
            "mode": self.mode,
            "step_count": len(self.step_results),
            "artifact_count": len(self.artifacts),
            "event_count": len(self.events),
        }


class AgenticEngine:
    """
    Main agentic execution engine.

    Orchestrates the full plan → execute → reflect → revise loop.
    Streams events in real-time via SSE/WebSocket.
    """

    def __init__(
        self,
        kimi_client,
        grok_client,
        config: Optional[AgenticConfig] = None,
        search_layer=None,
        browser_engine=None,
    ):
        """
        Initialize the agentic engine.

        Args:
            kimi_client: Async OpenAI client for kimi-2.5
            grok_client: Async OpenAI client for grok
            config: Engine configuration
            search_layer: SearchLayer for web search
            browser_engine: BrowserEngineV2 for web automation
        """
        self.config = config or AgenticConfig()
        self.kimi_client = kimi_client
        self.grok_client = grok_client
        self.search_layer = search_layer
        self.browser_engine = browser_engine

        # Core components
        self.planner = TaskPlanner(kimi_client, self.config)
        self.executor = ExecutionLoop(kimi_client, self.config)
        self.reflector = ReflectionEngine(grok_client, self.config)
        self.state_manager = StateManager()

        # Event subscribers
        self._event_subscribers: List[Callable] = []

        # Active executions
        self._active_executions: Dict[str, ExecutionContext] = {}

        logger.info("AgenticEngine initialized")

    def subscribe_events(self, callback: Callable):
        """Subscribe to execution events."""
        self._event_subscribers.append(callback)

    async def _emit(self, event_type: str, data: Dict[str, Any], session_id: str = ""):
        """Emit an event to all subscribers."""
        event = {
            "type": event_type,
            "data": data,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        for callback in self._event_subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"Event emission error: {e}")

    def register_search_handler(self, search_layer):
        """Register the search layer for web search tool."""
        self.search_layer = search_layer

        async def search_handler(params: Dict, context: Dict) -> Dict:
            query = params.get("query", "")
            num_results = params.get("num_results", 10)
            try:
                results = await search_layer.search(
                    query=query,
                    sources=["web"],
                    num_results=num_results,
                )
                return {
                    "results": results.get("results", []),
                    "text": results.get("combined_text", ""),
                    "sources_count": len(results.get("results", [])),
                    "source": "search_layer"
                }
            except Exception as e:
                logger.error(f"Search handler error: {e}")
                return {"error": str(e), "text": "", "results": []}

        self.executor.register_tool_handler("web_search", search_handler)
        logger.info("Search handler registered with execution loop")

    def register_browser_handler(self, browser_engine):
        """Register the browser engine for web automation tools."""
        self.browser_engine = browser_engine
        engine_ref = self  # Capture reference for closures

        async def navigate_handler(params: Dict, context: Dict) -> Dict:
            url = params.get("url", "")
            try:
                result = await browser_engine.navigate(url)
                # Emit browser.navigated event for LiveScreen.tsx
                await engine_ref._emit("browser.navigated", {
                    "url": result.get("url", url),
                    "title": result.get("title", ""),
                    "screenshot": result.get("screenshot", ""),
                }, context.get("session_id", ""))
                return result
            except Exception as e:
                logger.error(f"Browser navigate error: {e}")
                return {"error": str(e)}

        async def click_handler(params: Dict, context: Dict) -> Dict:
            selector = params.get("selector", "")
            x = params.get("x")
            y = params.get("y")
            try:
                if x is not None and y is not None:
                    result = await browser_engine.click(x=x, y=y)
                else:
                    result = await browser_engine.click(selector=selector)
                # Emit browser.clicked event with screenshot
                await engine_ref._emit("browser.clicked", {
                    "x": x, "y": y, "selector": selector,
                    "screenshot": result.get("screenshot", ""),
                    "url": result.get("url", ""),
                }, context.get("session_id", ""))
                return result
            except Exception as e:
                return {"error": str(e)}

        async def type_handler(params: Dict, context: Dict) -> Dict:
            text = params.get("text", "")
            selector = params.get("selector", "")
            try:
                result = await browser_engine.type_text(selector=selector, text=text)
                # Emit browser.typed event with screenshot
                await engine_ref._emit("browser.typed", {
                    "text": text[:50],
                    "screenshot": result.get("screenshot", ""),
                }, context.get("session_id", ""))
                return result
            except Exception as e:
                return {"error": str(e)}

        async def screenshot_handler(params: Dict, context: Dict) -> Dict:
            try:
                screenshot_b64 = await browser_engine._capture_screenshot()
                # Emit browser.screenshot event for LiveScreen.tsx
                await engine_ref._emit("browser.screenshot", {
                    "screenshot": screenshot_b64,
                    "url": getattr(browser_engine, 'state', None) and browser_engine.state.url or "",
                }, context.get("session_id", ""))
                return {"success": True, "screenshot": screenshot_b64}
            except Exception as e:
                return {"error": str(e)}

        self.executor.register_tool_handler("browser_navigate", navigate_handler)
        self.executor.register_tool_handler("browser_click", click_handler)
        self.executor.register_tool_handler("browser_type", type_handler)
        self.executor.register_tool_handler("browser_screenshot", screenshot_handler)
        logger.info("Browser handlers registered with execution loop (with LiveScreen events)")

    async def execute(
        self,
        user_request: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        mode: str = "auto",
        conversation_history: Optional[List[Dict]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute a user request with full agentic workflow.

        Yields SSE events as the execution progresses.

        Args:
            user_request: The user's request
            session_id: Session identifier
            user_id: User identifier
            mode: Execution mode (instant/auto/agent)
            conversation_history: Previous conversation messages

        Yields:
            Dict events for SSE streaming
        """
        session_id = session_id or str(uuid.uuid4())

        # Create execution context
        ctx = ExecutionContext(
            session_id=session_id,
            user_id=user_id,
            objective=user_request,
            mode=mode,
            started_at=datetime.now(),
        )
        self._active_executions[session_id] = ctx

        # Create session state
        self.state_manager.create_session(
            session_id=session_id,
            user_id=user_id,
            mode=mode,
            objective=user_request,
        )

        try:
            # ── Phase 1: Reasoning ──
            yield {"type": "status", "data": {"phase": "reasoning", "message": "Analyzing your request..."}}
            await self._emit("execution.reasoning", {"objective": user_request}, session_id)

            reasoning_result = await self._reason_about_request(user_request, conversation_history)
            yield {"type": "reasoning", "data": reasoning_result}

            # Check if instant mode is sufficient
            if mode == "instant" or reasoning_result.get("mode_recommendation") == "instant":
                async for event in self._execute_instant(user_request, reasoning_result, ctx):
                    yield event
                return

            # ── Phase 2: Planning ──
            yield {"type": "status", "data": {"phase": "planning", "message": "Creating execution plan..."}}
            await self._emit("execution.planning", {"objective": user_request}, session_id)

            plan = await self.planner.create_plan(
                user_request=user_request,
                context={"reasoning": reasoning_result},
            )
            ctx.plan = plan

            yield {"type": "plan", "data": {
                "plan_id": plan.id,
                "objective": plan.objective,
                "steps": [s.to_dict() for s in plan.steps],
                "step_count": len(plan.steps),
            }}

            # ── Phase 3: Execution Loop ──
            yield {"type": "status", "data": {"phase": "executing", "message": f"Executing {len(plan.steps)} steps..."}}

            revision_count = 0
            current_plan = plan

            while revision_count <= self.config.max_plan_revisions:
                for step in current_plan.steps:
                    if step.status == StepStatus.COMPLETED:
                        continue  # Skip already completed steps

                    # Check dependencies
                    deps_met = all(
                        dep_id in ctx.step_results
                        for dep_id in step.dependencies
                    )
                    if not deps_met:
                        logger.warning(f"Dependencies not met for step {step.id}, skipping")
                        continue

                    # Execute the step
                    yield {"type": "step.start", "data": {
                        "step_id": step.id,
                        "description": step.description,
                        "step_type": step.step_type.value,
                    }}

                    exec_context = {
                        "objective": ctx.objective,
                        "step_results": ctx.step_results,
                        **ctx.accumulated_context,
                    }

                    result = await self.executor.execute_step(step, exec_context, session_id)

                    # Store result
                    ctx.step_results[step.id] = result.output
                    self.state_manager.add_step_result(session_id, step.id, result.output)

                    yield {"type": "step.result", "data": result.to_dict()}

                    # ── Reflection ──
                    if self.config.reflection_enabled and step.requires_reflection:
                        reflection = await self.reflector.reflect(
                            step_id=step.id,
                            step_description=step.description,
                            result=result.output,
                            objective=ctx.objective,
                        )

                        yield {"type": "reflection", "data": reflection.to_dict()}

                        if reflection.action == ReflectionAction.RETRY and step.retry_count < step.max_retries:
                            yield {"type": "step.retry", "data": {"step_id": step.id, "reason": reflection.reflection}}
                            step.status = StepStatus.PENDING
                            # Re-execute (the loop will pick it up again)
                            result = await self.executor.execute_step(step, exec_context, session_id)
                            ctx.step_results[step.id] = result.output
                            yield {"type": "step.result", "data": result.to_dict()}

                        elif reflection.action == ReflectionAction.REVISE_PLAN:
                            yield {"type": "plan.revising", "data": {"reason": reflection.reflection}}
                            current_plan = await self.planner.revise_plan(current_plan, reflection, ctx)
                            revision_count += 1
                            yield {"type": "plan.revised", "data": {
                                "plan_id": current_plan.id,
                                "steps": [s.to_dict() for s in current_plan.steps],
                            }}
                            break  # Restart the step loop with revised plan

                        elif reflection.action == ReflectionAction.ABORT:
                            yield {"type": "execution.aborted", "data": {"reason": reflection.reflection}}
                            return

                    # Checkpoint if configured
                    if self.config.checkpoint_enabled and step.checkpoint:
                        self.state_manager.create_checkpoint(session_id, f"after_{step.id}")

                else:
                    # All steps completed without plan revision
                    break

            # ── Phase 4: Final Reflection ──
            if self.config.reflection_enabled:
                final_reflection = await self.reflector.reflect_on_plan(
                    objective=ctx.objective,
                    all_results=ctx.step_results,
                )
                yield {"type": "final_reflection", "data": final_reflection.to_dict()}

            # ── Phase 5: Synthesis ──
            yield {"type": "status", "data": {"phase": "synthesizing", "message": "Preparing final response..."}}

            final_response = await self._synthesize_final_response(ctx)

            ctx.completed_at = datetime.now()
            execution_time = (ctx.completed_at - ctx.started_at).total_seconds()

            yield {"type": "result", "data": {
                "response": final_response,
                "execution_time": execution_time,
                "steps_completed": len(ctx.step_results),
                "artifacts": ctx.artifacts,
            }}

            yield {"type": "done", "data": {
                "session_id": session_id,
                "execution_time": execution_time,
            }}

        except Exception as e:
            logger.exception(f"Execution failed: {e}")
            yield {"type": "error", "data": {"error": str(e)}}

        finally:
            # Update session state
            self.state_manager.update_session(session_id, status="completed")
            if session_id in self._active_executions:
                del self._active_executions[session_id]

    async def _reason_about_request(
        self,
        user_request: str,
        conversation_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """Use grok reasoning to analyze the request."""
        messages = [
            {"role": "system", "content": """You are an expert reasoning agent. Analyze the user's request and determine:
1. What exactly the user wants
2. What mode is best (instant for simple Q&A, auto for moderate tasks, agent for complex multi-step)
3. What tools/capabilities are needed
4. Any clarifications needed

Respond in JSON:
{
    "understanding": "what the user wants",
    "mode_recommendation": "instant|auto|agent",
    "complexity": "simple|moderate|complex",
    "tools_needed": ["search", "browser", "code", "file"],
    "reasoning": "why this mode and approach",
    "clarification_needed": false,
    "clarification_question": null
}"""},
        ]

        if conversation_history:
            for msg in conversation_history[-5:]:
                messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

        messages.append({"role": "user", "content": user_request})

        try:
            response = await self.grok_client.chat.completions.create(
                model=self.config.reasoning_model,
                messages=messages,
                temperature=0.3,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Reasoning failed: {e}")
            return {
                "understanding": user_request,
                "mode_recommendation": "auto",
                "complexity": "moderate",
                "tools_needed": ["search"],
                "reasoning": "Defaulting to auto mode",
            }

    async def _execute_instant(
        self,
        user_request: str,
        reasoning: Dict[str, Any],
        ctx: ExecutionContext,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute instant mode — fast, direct response."""
        yield {"type": "status", "data": {"phase": "instant", "message": "Generating response..."}}

        messages = [
            {"role": "system", "content": """You are McLeuker AI. Respond concisely and precisely.
Think step-by-step internally, then give a clear, well-structured answer.
Be direct — no filler, no excessive formatting. Quality over quantity."""},
            {"role": "user", "content": user_request}
        ]

        try:
            response = await self.kimi_client.chat.completions.create(
                model=self.config.primary_model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=4000,
            )

            answer = response.choices[0].message.content
            ctx.completed_at = datetime.now()
            execution_time = (ctx.completed_at - ctx.started_at).total_seconds()

            yield {"type": "result", "data": {
                "response": answer,
                "mode": "instant",
                "execution_time": execution_time,
            }}
            yield {"type": "done", "data": {"session_id": ctx.session_id, "execution_time": execution_time}}

        except Exception as e:
            yield {"type": "error", "data": {"error": str(e)}}

    async def _synthesize_final_response(self, ctx: ExecutionContext) -> str:
        """Synthesize all step results into a final response."""
        results_text = []
        for step_id, result in ctx.step_results.items():
            results_text.append(f"[{step_id}]: {str(result)[:3000]}")

        messages = [
            {"role": "system", "content": """You are McLeuker AI. Synthesize all the research and execution results
into a comprehensive, well-structured final response.

Guidelines:
- Start with a brief summary of what was found/done
- Use clear headings and structure
- Cite sources where available
- Be precise and accurate
- Include relevant data, numbers, and facts
- End with key takeaways or next steps if applicable"""},
            {"role": "user", "content": f"""Synthesize these execution results into a final response:

OBJECTIVE: {ctx.objective}

RESULTS:
{chr(10).join(results_text)}

Create a comprehensive, well-structured response."""}
        ]

        try:
            response = await self.kimi_client.chat.completions.create(
                model=self.config.primary_model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=8000,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            # Fallback: concatenate results
            return f"## Results\n\n" + "\n\n".join(
                f"**{k}**: {str(v)[:1000]}" for k, v in ctx.step_results.items()
            )

    def get_active_executions(self) -> List[Dict[str, Any]]:
        """Get all active executions."""
        return [ctx.to_dict() for ctx in self._active_executions.values()]

    def cancel_execution(self, session_id: str):
        """Cancel an active execution."""
        self.executor.cancel(session_id)
        self.state_manager.update_session(session_id, status="cancelled")
