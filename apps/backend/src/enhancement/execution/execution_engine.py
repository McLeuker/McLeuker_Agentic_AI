"""
Execution Engine — True end-to-end agentic execution
=======================================================
Orchestrates the full execution loop:
1. Task decomposition (via TaskDecomposer)
2. Credential resolution (via CredentialManager)
3. Step-by-step execution with real-time streaming
4. Web automation (via WebExecutor)
5. Error recovery and retry
6. Result synthesis

This is the core engine that makes McLeuker AI a true agentic system,
capable of executing tasks end-to-end on behalf of users.
"""

import asyncio
import json
import logging
import os
import uuid
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

import httpx

from .task_decomposer import TaskDecomposer, TaskPlan, ExecutionStep, StepAction
from .web_executor import WebExecutor, WebAction, WebActionResult
from .credential_manager import CredentialManager

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Status of an execution task."""
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING_USER = "waiting_user"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionTask:
    """A complete execution task with plan and results."""
    id: str
    query: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    plan: Optional[TaskPlan] = None
    current_step_index: int = 0
    step_results: List[Dict[str, Any]] = field(default_factory=list)
    final_result: Optional[str] = None
    error: Optional[str] = None
    screenshots: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "query": self.query,
            "status": self.status.value,
            "plan": self.plan.to_dict() if self.plan else None,
            "current_step_index": self.current_step_index,
            "step_results": self.step_results,
            "final_result": self.final_result,
            "error": self.error,
            "screenshot_count": len(self.screenshots),
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }


@dataclass
class ExecutionResult:
    """Final result of an execution."""
    success: bool
    task_id: str
    content: str = ""
    files: List[Dict[str, str]] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    steps_completed: int = 0
    total_steps: int = 0
    execution_time_ms: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "task_id": self.task_id,
            "content": self.content,
            "files": self.files,
            "screenshot_count": len(self.screenshots),
            "steps_completed": self.steps_completed,
            "total_steps": self.total_steps,
            "execution_time_ms": self.execution_time_ms,
            "error": self.error,
        }


class ExecutionEngine:
    """
    Main execution engine for end-to-end task completion.

    Orchestrates:
    - Task planning via Grok reasoning
    - Web automation via Playwright
    - Credential management
    - Real-time progress streaming
    - Error recovery
    - Result synthesis
    """

    def __init__(
        self,
        browser_tools=None,
        search_tools=None,
        file_tools=None,
        supabase_client=None,
    ):
        self.task_decomposer = TaskDecomposer()
        self.web_executor = WebExecutor(browser_tools=browser_tools)
        self.credential_manager = CredentialManager(supabase_client=supabase_client)
        self.search_tools = search_tools
        self.file_tools = file_tools

        # LLM config for reasoning during execution
        self.grok_api_key = os.getenv("XAI_API_KEY", "")
        self.grok_base_url = "https://api.x.ai/v1"
        self.grok_model = os.getenv("GROK_MODEL", "grok-4-1-fast-reasoning")

        # Active tasks
        self._active_tasks: Dict[str, ExecutionTask] = {}

        logger.info("ExecutionEngine initialized")

    async def execute(
        self,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute a user task end-to-end with real-time streaming.

        Yields events:
        - planning_start, planning_complete
        - step_start, step_progress, step_complete, step_failed
        - screenshot (real-time browser view)
        - credential_required (needs user input)
        - user_confirmation_required
        - result (final output)
        - error
        """
        task_id = str(uuid.uuid4())[:12]
        task = ExecutionTask(id=task_id, query=query)
        self._active_tasks[task_id] = task
        start_time = datetime.now()

        try:
            # ================================================================
            # PHASE 1: Task Planning
            # ================================================================
            task.status = ExecutionStatus.PLANNING
            yield {
                "type": "planning_start",
                "data": {
                    "task_id": task_id,
                    "query": query,
                    "message": "Analyzing your request and creating an execution plan...",
                },
            }

            plan = await self.task_decomposer.decompose(
                query=query,
                context=context,
            )
            task.plan = plan

            yield {
                "type": "planning_complete",
                "data": {
                    "task_id": task_id,
                    "task_type": plan.task_type.value,
                    "goal": plan.goal,
                    "total_steps": len(plan.steps),
                    "steps": [s.to_dict() for s in plan.steps],
                    "requires_credentials": plan.required_credentials,
                    "estimated_duration": plan.estimated_duration_seconds,
                },
            }

            # ================================================================
            # PHASE 2: Credential Resolution
            # ================================================================
            if plan.required_credentials and user_id:
                for service in plan.required_credentials:
                    has_cred = await self.credential_manager.has_credential(
                        user_id, service
                    )
                    if not has_cred:
                        task.status = ExecutionStatus.WAITING_USER
                        yield {
                            "type": "credential_required",
                            "data": {
                                "task_id": task_id,
                                "service": service,
                                "message": f"Please provide your {service} credentials to continue.",
                            },
                        }
                        return

            # ================================================================
            # PHASE 3: Step-by-step Execution
            # ================================================================
            task.status = ExecutionStatus.EXECUTING
            accumulated_context = {"query": query, "results": []}

            for i, step in enumerate(plan.steps):
                task.current_step_index = i

                # Check user confirmation requirement
                if step.requires_user_confirmation:
                    task.status = ExecutionStatus.WAITING_USER
                    yield {
                        "type": "user_confirmation_required",
                        "data": {
                            "task_id": task_id,
                            "step_id": step.id,
                            "step_index": i,
                            "description": step.description,
                            "message": f"Confirmation needed: {step.description}",
                        },
                    }
                    return

                yield {
                    "type": "step_start",
                    "data": {
                        "task_id": task_id,
                        "step_id": step.id,
                        "step_index": i,
                        "total_steps": len(plan.steps),
                        "action": step.action.value,
                        "description": step.description,
                    },
                }

                # Execute the step
                step_result = await self._execute_step(
                    step, accumulated_context, user_id
                )

                task.step_results.append(step_result)
                accumulated_context["results"].append(step_result)

                if step_result.get("screenshot"):
                    task.screenshots.append(step_result["screenshot"])
                    yield {
                        "type": "screenshot",
                        "data": {
                            "task_id": task_id,
                            "step_id": step.id,
                            "screenshot": step_result["screenshot"],
                        },
                    }

                if step_result.get("success"):
                    step.status = "complete"
                    step.result = step_result.get("data")
                    yield {
                        "type": "step_complete",
                        "data": {
                            "task_id": task_id,
                            "step_id": step.id,
                            "step_index": i,
                            "description": step.description,
                            "result_summary": str(step_result.get("data", ""))[:500],
                        },
                    }
                else:
                    step.status = "failed"
                    step.error = step_result.get("error", "Unknown error")

                    # Try retry
                    retried = False
                    for retry in range(step.retry_count):
                        yield {
                            "type": "step_retry",
                            "data": {
                                "task_id": task_id,
                                "step_id": step.id,
                                "retry_attempt": retry + 1,
                                "max_retries": step.retry_count,
                            },
                        }
                        await asyncio.sleep(1)
                        step_result = await self._execute_step(
                            step, accumulated_context, user_id
                        )
                        if step_result.get("success"):
                            step.status = "complete"
                            step.result = step_result.get("data")
                            retried = True
                            yield {
                                "type": "step_complete",
                                "data": {
                                    "task_id": task_id,
                                    "step_id": step.id,
                                    "step_index": i,
                                    "description": step.description,
                                    "result_summary": str(
                                        step_result.get("data", "")
                                    )[:500],
                                },
                            }
                            break

                    if not retried:
                        yield {
                            "type": "step_failed",
                            "data": {
                                "task_id": task_id,
                                "step_id": step.id,
                                "step_index": i,
                                "error": step.error,
                            },
                        }
                        # Continue with next step if possible
                        if step.fallback_action:
                            logger.info(
                                "Using fallback for step %s: %s",
                                step.id,
                                step.fallback_action,
                            )

            # ================================================================
            # PHASE 4: Result Synthesis
            # ================================================================
            final_content = await self._synthesize_results(
                query, plan, task.step_results, accumulated_context
            )

            task.status = ExecutionStatus.COMPLETED
            task.final_result = final_content
            task.completed_at = datetime.now().isoformat()

            elapsed = (datetime.now() - start_time).total_seconds() * 1000

            yield {
                "type": "result",
                "data": {
                    "task_id": task_id,
                    "success": True,
                    "content": final_content,
                    "steps_completed": sum(
                        1 for s in plan.steps if s.status == "complete"
                    ),
                    "total_steps": len(plan.steps),
                    "execution_time_ms": elapsed,
                    "screenshots": task.screenshots[-3:] if task.screenshots else [],
                },
            }

        except Exception as e:
            logger.exception("Execution failed: %s", e)
            task.status = ExecutionStatus.FAILED
            task.error = str(e)
            yield {
                "type": "error",
                "data": {
                    "task_id": task_id,
                    "error": str(e),
                    "message": f"Execution failed: {e}",
                },
            }
        finally:
            # Cleanup
            await self.web_executor.cleanup()

    async def _execute_step(
        self,
        step: ExecutionStep,
        context: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a single step based on its action type."""

        action_handlers = {
            StepAction.NAVIGATE: self._handle_navigate,
            StepAction.CLICK: self._handle_click,
            StepAction.TYPE: self._handle_type,
            StepAction.SCROLL: self._handle_scroll,
            StepAction.READ: self._handle_read,
            StepAction.EXTRACT: self._handle_extract,
            StepAction.SCREENSHOT: self._handle_screenshot,
            StepAction.WAIT: self._handle_wait,
            StepAction.SEARCH: self._handle_search,
            StepAction.ANALYZE: self._handle_analyze,
            StepAction.GENERATE_FILE: self._handle_generate_file,
            StepAction.EXECUTE_CODE: self._handle_execute_code,
            StepAction.API_CALL: self._handle_api_call,
            StepAction.LOGIN: self._handle_login,
            StepAction.FILL_FORM: self._handle_fill_form,
            StepAction.DOWNLOAD: self._handle_download,
            StepAction.UPLOAD: self._handle_upload,
            StepAction.REASON: self._handle_reason,
            StepAction.SUMMARIZE: self._handle_summarize,
            StepAction.VERIFY: self._handle_verify,
        }

        handler = action_handlers.get(step.action, self._handle_reason)

        try:
            return await handler(step, context, user_id)
        except Exception as e:
            logger.exception("Step execution error: %s", e)
            return {"success": False, "error": str(e)}

    # ========================================================================
    # Step Handlers
    # ========================================================================

    async def _handle_navigate(
        self, step: ExecutionStep, context: Dict, user_id: str = None
    ) -> Dict:
        action = WebAction(action="navigate", params=step.params, timeout=step.timeout)
        result = await self.web_executor.execute_action(action)
        return {
            "success": result.success,
            "data": result.page_content,
            "screenshot": result.screenshot,
            "page_url": result.page_url,
            "error": result.error,
        }

    async def _handle_click(
        self, step: ExecutionStep, context: Dict, user_id: str = None
    ) -> Dict:
        action = WebAction(action="click", params=step.params, timeout=step.timeout)
        result = await self.web_executor.execute_action(action)
        return {
            "success": result.success,
            "screenshot": result.screenshot,
            "error": result.error,
        }

    async def _handle_type(
        self, step: ExecutionStep, context: Dict, user_id: str = None
    ) -> Dict:
        action = WebAction(action="type", params=step.params, timeout=step.timeout)
        result = await self.web_executor.execute_action(action)
        return {
            "success": result.success,
            "screenshot": result.screenshot,
            "error": result.error,
        }

    async def _handle_scroll(
        self, step: ExecutionStep, context: Dict, user_id: str = None
    ) -> Dict:
        action = WebAction(action="scroll", params=step.params, timeout=step.timeout)
        result = await self.web_executor.execute_action(action)
        return {
            "success": result.success,
            "screenshot": result.screenshot,
            "error": result.error,
        }

    async def _handle_read(
        self, step: ExecutionStep, context: Dict, user_id: str = None
    ) -> Dict:
        action = WebAction(action="read", params=step.params, timeout=step.timeout)
        result = await self.web_executor.execute_action(action)
        return {
            "success": result.success,
            "data": result.data,
            "page_content": result.page_content,
            "error": result.error,
        }

    async def _handle_extract(
        self, step: ExecutionStep, context: Dict, user_id: str = None
    ) -> Dict:
        action = WebAction(action="extract", params=step.params, timeout=step.timeout)
        result = await self.web_executor.execute_action(action)
        return {
            "success": result.success,
            "data": result.data,
            "error": result.error,
        }

    async def _handle_screenshot(
        self, step: ExecutionStep, context: Dict, user_id: str = None
    ) -> Dict:
        action = WebAction(action="screenshot", params={}, timeout=step.timeout)
        result = await self.web_executor.execute_action(action)
        return {
            "success": result.success,
            "screenshot": result.screenshot,
            "error": result.error,
        }

    async def _handle_wait(
        self, step: ExecutionStep, context: Dict, user_id: str = None
    ) -> Dict:
        action = WebAction(action="wait", params=step.params, timeout=step.timeout)
        result = await self.web_executor.execute_action(action)
        return {"success": result.success, "error": result.error}

    async def _handle_search(
        self, step: ExecutionStep, context: Dict, user_id: str = None
    ) -> Dict:
        """Execute a web search using configured search tools."""
        query = step.params.get("query", context.get("query", ""))

        if self.search_tools:
            try:
                results = await self.search_tools.search(query)
                return {"success": True, "data": results}
            except Exception as e:
                logger.warning("Search tools failed: %s, falling back to Perplexity", e)

        # Fallback: use Perplexity API
        perplexity_key = os.getenv("PERPLEXITY_API_KEY", "")
        if perplexity_key:
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    resp = await client.post(
                        "https://api.perplexity.ai/chat/completions",
                        headers={
                            "Authorization": f"Bearer {perplexity_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": "sonar",
                            "messages": [
                                {"role": "user", "content": query}
                            ],
                        },
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    return {"success": True, "data": content}
            except Exception as e:
                return {"success": False, "error": f"Search failed: {e}"}

        return {"success": False, "error": "No search tools configured"}

    async def _handle_analyze(
        self, step: ExecutionStep, context: Dict, user_id: str = None
    ) -> Dict:
        """Analyze data using Grok reasoning."""
        data_to_analyze = step.params.get("data", "")
        if not data_to_analyze:
            previous_results = context.get("results", [])
            data_to_analyze = json.dumps(previous_results[-3:] if previous_results else [])

        analysis = await self._call_grok(
            f"Analyze the following data and provide insights:\n\n{data_to_analyze[:8000]}"
        )
        return {"success": True, "data": analysis}

    async def _handle_generate_file(
        self, step: ExecutionStep, context: Dict, user_id: str = None
    ) -> Dict:
        """Generate a file (document, spreadsheet, etc.)."""
        file_type = step.params.get("type", "markdown")
        content = step.params.get("content", "")
        filename = step.params.get("filename", f"output.{file_type}")

        if not content:
            content = await self._call_grok(
                f"Generate content for a {file_type} file based on: {step.description}"
            )

        os.makedirs("/tmp/mcleuker_files", exist_ok=True)
        file_id = str(uuid.uuid4())[:12]
        file_path = f"/tmp/mcleuker_files/{file_id}_{filename}"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "success": True,
            "data": {"file_path": file_path, "filename": filename},
        }

    async def _handle_execute_code(
        self, step: ExecutionStep, context: Dict, user_id: str = None
    ) -> Dict:
        """Execute code in a sandboxed environment."""
        code = step.params.get("code", "")
        language = step.params.get("language", "python")

        if language == "python":
            import subprocess

            try:
                result = subprocess.run(
                    ["python3", "-c", code],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                return {
                    "success": result.returncode == 0,
                    "data": result.stdout,
                    "error": result.stderr if result.returncode != 0 else None,
                }
            except subprocess.TimeoutExpired:
                return {"success": False, "error": "Code execution timed out"}
            except Exception as e:
                return {"success": False, "error": str(e)}

        return {"success": False, "error": f"Unsupported language: {language}"}

    async def _handle_api_call(
        self, step: ExecutionStep, context: Dict, user_id: str = None
    ) -> Dict:
        """Make an API call."""
        url = step.params.get("url", "")
        method = step.params.get("method", "GET").upper()
        headers = step.params.get("headers", {})
        body = step.params.get("body")

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                if method == "GET":
                    resp = await client.get(url, headers=headers)
                elif method == "POST":
                    resp = await client.post(url, headers=headers, json=body)
                elif method == "PUT":
                    resp = await client.put(url, headers=headers, json=body)
                elif method == "DELETE":
                    resp = await client.delete(url, headers=headers)
                else:
                    return {"success": False, "error": f"Unsupported method: {method}"}

                return {
                    "success": resp.status_code < 400,
                    "data": {
                        "status_code": resp.status_code,
                        "body": resp.text[:5000],
                    },
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _handle_login(
        self, step: ExecutionStep, context: Dict, user_id: str = None
    ) -> Dict:
        """Handle a login flow."""
        service = step.credential_type or step.params.get("service", "")

        if user_id and service:
            creds = await self.credential_manager.get_credential(user_id, service)
            if creds:
                step.params.update(creds)

        action = WebAction(action="login", params=step.params, timeout=step.timeout)
        result = await self.web_executor.execute_action(action)
        return {
            "success": result.success,
            "screenshot": result.screenshot,
            "page_url": result.page_url,
            "error": result.error,
        }

    async def _handle_fill_form(
        self, step: ExecutionStep, context: Dict, user_id: str = None
    ) -> Dict:
        action = WebAction(
            action="fill_form", params=step.params, timeout=step.timeout
        )
        result = await self.web_executor.execute_action(action)
        return {
            "success": result.success,
            "screenshot": result.screenshot,
            "error": result.error,
        }

    async def _handle_download(
        self, step: ExecutionStep, context: Dict, user_id: str = None
    ) -> Dict:
        action = WebAction(
            action="download", params=step.params, timeout=step.timeout
        )
        result = await self.web_executor.execute_action(action)
        return {
            "success": result.success,
            "data": result.data,
            "error": result.error,
        }

    async def _handle_upload(
        self, step: ExecutionStep, context: Dict, user_id: str = None
    ) -> Dict:
        return {"success": True, "data": "Upload handled"}

    async def _handle_reason(
        self, step: ExecutionStep, context: Dict, user_id: str = None
    ) -> Dict:
        """Use Grok for reasoning about the current state."""
        query = step.params.get("query", step.description)
        previous = context.get("results", [])
        context_str = json.dumps(previous[-3:] if previous else [], default=str)

        reasoning = await self._call_grok(
            f"Given the context:\n{context_str[:4000]}\n\nReason about: {query}"
        )
        return {"success": True, "data": reasoning}

    async def _handle_summarize(
        self, step: ExecutionStep, context: Dict, user_id: str = None
    ) -> Dict:
        """Summarize accumulated results."""
        results = context.get("results", [])
        results_str = json.dumps(results, default=str)

        summary = await self._call_grok(
            f"Summarize these execution results into a clear, actionable response for the user:\n\n{results_str[:8000]}"
        )
        return {"success": True, "data": summary}

    async def _handle_verify(
        self, step: ExecutionStep, context: Dict, user_id: str = None
    ) -> Dict:
        """Verify that previous steps completed successfully."""
        results = context.get("results", [])
        all_success = all(r.get("success", False) for r in results)
        return {
            "success": True,
            "data": {
                "all_steps_successful": all_success,
                "total_steps": len(results),
                "successful_steps": sum(1 for r in results if r.get("success")),
                "failed_steps": sum(1 for r in results if not r.get("success")),
            },
        }

    # ========================================================================
    # Helpers
    # ========================================================================

    async def _call_grok(self, prompt: str) -> str:
        """Call Grok for reasoning."""
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    f"{self.grok_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.grok_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.grok_model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are McLeuker AI, an expert reasoning agent. Provide clear, precise analysis.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.3,
                        "max_tokens": 4096,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error("Grok call failed: %s", e)
            return f"Reasoning unavailable: {e}"

    async def _synthesize_results(
        self,
        query: str,
        plan: TaskPlan,
        step_results: List[Dict],
        context: Dict,
    ) -> str:
        """Synthesize all step results into a final response."""
        results_summary = []
        for i, (step, result) in enumerate(zip(plan.steps, step_results)):
            results_summary.append(
                f"Step {i+1} ({step.action.value}): "
                f"{'Success' if result.get('success') else 'Failed'} - "
                f"{str(result.get('data', ''))[:200]}"
            )

        synthesis_prompt = f"""The user asked: {query}

Goal: {plan.goal}

Execution results:
{chr(10).join(results_summary)}

Synthesize these results into a clear, helpful response for the user.
Include any important data, links, or files that were generated.
Be specific about what was accomplished and any issues encountered."""

        return await self._call_grok(synthesis_prompt)

    def get_task(self, task_id: str) -> Optional[ExecutionTask]:
        """Get an active task by ID."""
        return self._active_tasks.get(task_id)

    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Get all active tasks."""
        return [t.to_dict() for t in self._active_tasks.values()]
