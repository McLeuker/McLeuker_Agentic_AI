"""
Execution Engine — Main orchestration loop
=============================================

Ties together PlannerAgent, ExecutorAgent, and BrowserAgent
into a complete execution pipeline:

  User Request → Plan → Execute Steps → Observe → Deliver

Emits real-time events via SSE for the frontend to display:
- task_progress: Message field updates (title + 3 subtitle lines)
- step_update: Execution panel step list
- browser_screenshot: Live browser viewer
- execution_reasoning: Reasoning tab content
- content: Final response text
"""

import asyncio
import json
import time
import uuid
from typing import Dict, Any, Optional, List, AsyncGenerator, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging

from ..agents.planner_agent import PlannerAgent, ExecutionPlan, ExecutionStep
from ..agents.executor_agent import ExecutorAgent
from ..agents.browser_agent import BrowserAgent

logger = logging.getLogger(__name__)


@dataclass
class ExecutionState:
    """Tracks the state of an execution."""
    execution_id: str
    user_request: str
    plan: Optional[ExecutionPlan] = None
    current_step: int = 0
    total_steps: int = 0
    status: str = "pending"
    results: Dict[int, Any] = field(default_factory=dict)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class ExecutionEngine:
    """
    Main execution engine. Coordinates planning and execution,
    emits events for real-time frontend updates.
    """

    def __init__(
        self,
        planner: PlannerAgent,
        executor: ExecutorAgent,
        browser: Optional[BrowserAgent] = None,
    ):
        self.planner = planner
        self.executor = executor
        self.browser = browser
        self._active_executions: Dict[str, ExecutionState] = {}

    async def execute_stream(
        self,
        user_request: str,
        context: Optional[Dict] = None,
    ) -> AsyncGenerator[Dict, None]:
        """
        Execute a user request and yield events in real-time.
        Each yielded dict is an SSE event: {"event": "type", "data": {...}}
        """
        execution_id = str(uuid.uuid4())[:8]
        state = ExecutionState(
            execution_id=execution_id,
            user_request=user_request,
            started_at=datetime.now().isoformat(),
        )
        self._active_executions[execution_id] = state

        try:
            # ================================================================
            # PHASE 1: PLANNING
            # ================================================================
            state.status = "planning"

            yield self._event("execution_start", {
                "execution_id": execution_id,
                "status": "planning",
            })

            yield self._event("task_progress", {
                "title": "Analyzing your request",
                "detail": "Breaking down the task into executable steps\nDetermining the best tools and approach\nCreating an optimized execution plan",
                "status": "active",
                "phase": "planning",
            })

            # Create the plan
            plan = await self.planner.create_plan(user_request, context)
            state.plan = plan
            state.total_steps = len(plan.steps)

            yield self._event("execution_plan", {
                "execution_id": execution_id,
                "goal": plan.goal,
                "steps": [
                    {"id": s.id, "tool": s.tool, "instruction": s.instruction[:100]}
                    for s in plan.steps
                ],
                "reasoning": plan.reasoning,
            })

            yield self._event("task_progress", {
                "title": f"Execution plan ready — {len(plan.steps)} steps",
                "detail": f"{plan.goal}\nTools: {', '.join(set(s.tool for s in plan.steps))}\nStarting execution now",
                "status": "complete",
                "phase": "planning",
            })

            yield self._event("execution_reasoning", {
                "content": f"## Execution Plan\n\n**Goal:** {plan.goal}\n\n**Reasoning:** {plan.reasoning}\n\n**Steps:**\n" +
                    "\n".join(f"{s.id}. [{s.tool}] {s.instruction}" for s in plan.steps),
            })

            # ================================================================
            # PHASE 2: EXECUTION
            # ================================================================
            state.status = "executing"
            execution_context = {"previous_results": {}}

            for step in plan.steps:
                state.current_step = step.id

                # Emit task_progress for message field
                step_detail = self._get_step_detail(step, plan)
                yield self._event("task_progress", {
                    "title": self._get_step_title(step),
                    "detail": step_detail,
                    "status": "active",
                    "phase": "execution",
                    "step_number": step.id,
                    "total_steps": state.total_steps,
                })

                # Emit step_update for execution panel
                yield self._event("step_update", {
                    "step_id": step.id,
                    "tool": step.tool,
                    "title": self._get_step_title(step),
                    "status": "running",
                    "instruction": step.instruction,
                })

                # Collect events from the executor
                events_queue = asyncio.Queue()

                async def emit_sub_event(event_type: str, data: Dict):
                    await events_queue.put({"event": event_type, "data": data})

                # Run step execution in a task
                step_task = asyncio.create_task(
                    self.executor.execute_step(step, execution_context, emit_sub_event)
                )

                # Yield sub-events in real-time while step executes
                while not step_task.done():
                    try:
                        sub_event = await asyncio.wait_for(events_queue.get(), timeout=0.5)
                        # Forward browser_screenshot and other events
                        yield self._event(sub_event["event"], sub_event["data"])
                    except asyncio.TimeoutError:
                        continue

                # Get step result
                result = await step_task

                # Drain remaining events
                while not events_queue.empty():
                    sub_event = events_queue.get_nowait()
                    yield self._event(sub_event["event"], sub_event["data"])

                # Store result
                state.results[step.id] = result
                execution_context["previous_results"][f"step_{step.id}"] = self._compact_result(result)

                # Emit step completion
                yield self._event("step_update", {
                    "step_id": step.id,
                    "tool": step.tool,
                    "title": self._get_step_title(step),
                    "status": "completed" if result.get("success") else "failed",
                    "result_summary": self.executor._summarize_result(result),
                })

                yield self._event("task_progress", {
                    "title": self._get_step_title(step),
                    "detail": self.executor._summarize_result(result),
                    "status": "complete",
                    "phase": "execution",
                    "step_number": step.id,
                    "total_steps": state.total_steps,
                })

            # ================================================================
            # PHASE 3: DELIVERY
            # ================================================================
            state.status = "delivering"

            yield self._event("task_progress", {
                "title": "Composing response",
                "detail": "Synthesizing all findings into a structured answer\nOrganizing key insights with supporting evidence\nFormatting for maximum readability",
                "status": "active",
                "phase": "delivery",
            })

            # Generate final response
            final_response = await self._generate_response(user_request, state)

            yield self._event("content", {"text": final_response})

            state.status = "completed"
            state.completed_at = datetime.now().isoformat()

            yield self._event("task_progress", {
                "title": "Task complete",
                "detail": f"All {state.total_steps} steps executed successfully",
                "status": "complete",
                "phase": "delivery",
            })

            yield self._event("complete", {
                "execution_id": execution_id,
                "steps_completed": state.total_steps,
                "status": "completed",
            })

        except Exception as e:
            logger.error(f"Execution failed: {e}")
            state.status = "failed"

            yield self._event("error", {
                "message": str(e),
                "execution_id": execution_id,
            })

        finally:
            # Clean up browser if it was used
            if self.browser and self.browser._started:
                try:
                    await self.browser.stop()
                except:
                    pass
            # Remove from active executions
            self._active_executions.pop(execution_id, None)

    async def _generate_response(self, user_request: str, state: ExecutionState) -> str:
        """Generate the final response from all step results."""
        # Collect all results
        results_summary = []
        for step in (state.plan.steps if state.plan else []):
            result = state.results.get(step.id, {})
            if result.get("analysis"):
                results_summary.append(result["analysis"])
            elif result.get("text"):
                results_summary.append(result["text"][:2000])
            elif result.get("summary"):
                results_summary.append(result["summary"])
            elif result.get("output"):
                results_summary.append(str(result["output"])[:2000])

        combined = "\n\n---\n\n".join(results_summary)

        # Use LLM to compose final response
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Compose a clear, well-structured response based on the execution results. Use markdown formatting. Be concise but thorough."},
            {"role": "user", "content": f"Original request: {user_request}\n\nExecution results:\n{combined[:8000]}\n\nCompose a comprehensive response."}
        ]

        try:
            response = await self.executor.call_llm(messages, temperature=0.5, max_tokens=4096)
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return combined or f"Task completed but response generation failed: {e}"

    def _event(self, event_type: str, data: Dict) -> Dict:
        """Create an SSE event dict."""
        return {"event": event_type, "data": data}

    def _get_step_title(self, step: ExecutionStep) -> str:
        """Get a clean title for a step."""
        tool_labels = {
            "browser": "Browsing the web",
            "search": "Searching for information",
            "code": "Running code",
            "github": "Working with GitHub",
            "think": "Analyzing findings",
            "file": "Generating files",
        }
        return tool_labels.get(step.tool, f"Executing: {step.tool}")

    def _get_step_detail(self, step: ExecutionStep, plan: ExecutionPlan) -> str:
        """Get 3-line detail for a step."""
        line1 = f"Step {step.id} of {len(plan.steps)} — {step.instruction[:80]}"
        tool_details = {
            "browser": "Opening live browser with screen capture\nScreenshots streaming to Browser tab",
            "search": "Querying multiple search engines\nGathering and ranking results",
            "code": "Generating code from task description\nExecuting in secure sandbox",
            "github": "Connecting to GitHub API\nPerforming repository operations",
            "think": "Reasoning about collected information\nSynthesizing insights from previous steps",
            "file": "Generating document from data\nFormatting and structuring output",
        }
        detail = tool_details.get(step.tool, "Processing task\nAnalyzing results")
        return f"{line1}\n{detail}"

    def _compact_result(self, result: Dict) -> Dict:
        """Compact a result for context passing (remove large fields)."""
        compact = {}
        for k, v in result.items():
            if k == "screenshot":
                continue  # Skip base64 screenshots
            if isinstance(v, str) and len(v) > 2000:
                compact[k] = v[:2000] + "..."
            else:
                compact[k] = v
        return compact
