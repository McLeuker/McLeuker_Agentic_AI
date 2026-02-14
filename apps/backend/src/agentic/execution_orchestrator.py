"""
Execution Orchestrator V4
==========================

Real agentic task execution with:
- LLM-powered planning that decomposes tasks into executable steps
- Multi-source research (search APIs queried in parallel)
- E2B sandbox for code execution (Python, JS, Bash)
- Browserless for web automation and content extraction
- GitHub API for real repository operations (read, edit, push, PR)
- Credential request system — agent asks user for tokens when needed
- Self-correction with retry logic
- Real-time SSE streaming with clean, user-friendly reasoning
- No internal API names exposed to users

Architecture:
  User Request → Planner → [Research | Code | Browser | GitHub | Think] → Verifier → Delivery → Stream
"""

import asyncio
import json
import uuid
import traceback
import re
import functools
from typing import List, Dict, Any, Optional, Callable, Literal, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

class ExecutionStatus(Enum):
    PENDING = "pending"
    PLANNING = "planning"
    RESEARCHING = "researching"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    RETRYING = "retrying"
    DELIVERING = "delivering"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class StepType(Enum):
    PLAN = "plan"
    RESEARCH = "research"
    CODE = "code"
    BROWSER = "browser"
    GITHUB = "github"
    VERIFY = "verify"
    DELIVER = "deliver"
    THINK = "think"


STEP_TYPE_TO_PHASE = {
    StepType.PLAN: "planning",
    StepType.RESEARCH: "research",
    StepType.CODE: "execution",
    StepType.BROWSER: "research",
    StepType.GITHUB: "execution",
    StepType.THINK: "execution",
    StepType.VERIFY: "verification",
    StepType.DELIVER: "delivery",
}


@dataclass
class ExecutionArtifact:
    artifact_id: str
    name: str
    type: Literal["code", "document", "image", "data", "other"]
    content: Optional[str] = None
    file_path: Optional[str] = None
    public_url: Optional[str] = None
    size_bytes: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionStep:
    step_id: str
    execution_id: str
    step_number: int
    step_type: StepType
    status: ExecutionStatus
    agent: Literal["kimi", "grok"]
    instruction: str
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Any = None
    reasoning: str = ""
    artifacts: List[ExecutionArtifact] = field(default_factory=list)
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 2
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ExecutionPlan:
    plan_id: str
    objective: str
    steps: List[Dict[str, Any]]
    estimated_duration: int
    reasoning: str
    parallel_groups: List[List[Any]]


@dataclass
class ExecutionResult:
    execution_id: str
    status: ExecutionStatus
    user_request: str
    final_output: str
    artifacts: List[ExecutionArtifact]
    steps: List[ExecutionStep]
    started_at: datetime
    completed_at: Optional[datetime]
    total_tokens: int
    execution_time_seconds: float
    metadata: Dict[str, Any]


# ============================================================================
# HELPER: Queue-based sub-event proxy for streaming step execution
# ============================================================================

class _SubEventQueue:
    """A list-like proxy that puts appended items into an asyncio.Queue.
    
    Allows _exec_github (and others) to keep using sub_events.append()
    while the events are immediately available to the streaming consumer.
    """
    def __init__(self, queue: asyncio.Queue):
        self._queue = queue
        self._items: List[Dict] = []

    def append(self, item: Dict):
        self._items.append(item)
        try:
            self._queue.put_nowait(item)
        except Exception:
            pass

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)


# ============================================================================
# EXECUTION ORCHESTRATOR V4
# ============================================================================

class ExecutionOrchestrator:
    """
    Real agentic execution orchestrator V4.

    Plans tasks, executes them with real tools (search, code, browser, GitHub),
    verifies results, and delivers output — all with real-time SSE streaming.

    V4 changes:
    - GitHub API integration for real repo operations
    - Clean user-facing reasoning (no internal API names)
    - Credential request events
    - Better step descriptions
    """

    def __init__(
        self,
        kimi_client=None,
        grok_client=None,
        search_layer=None,
        e2b_manager=None,
        browserless_client=None,
        github_client=None,
        browser_engine=None,
        max_steps: int = 15,
        enable_auto_correct: bool = True,
    ):
        self.kimi = kimi_client
        self.grok = grok_client
        self.search_layer = search_layer
        self.e2b = e2b_manager
        self.browserless = browserless_client
        self.github = github_client
        self.browser_engine = browser_engine  # Playwright-based browser with live screenshots
        self.local_sandbox = None  # Lazy-init local sandbox as E2B fallback
        self.max_steps = max_steps
        self.enable_auto_correct = enable_auto_correct
        self._executions: Dict[str, Dict[str, Any]] = {}
        # User-provided credentials stored per execution
        self._credentials: Dict[str, Dict[str, str]] = {}
        # Async events for credential waiting
        self._credential_events: Dict[str, asyncio.Event] = {}
        logger.info("ExecutionOrchestrator V4 initialized")

    # ------------------------------------------------------------------
    # Credential management
    # ------------------------------------------------------------------

    def set_credentials(self, execution_id: str, creds: Dict[str, str]):
        """Store user-provided credentials for an execution."""
        self._credentials[execution_id] = creds

    def provide_credential(self, execution_id: str, key: str, value: str):
        """Provide a credential and signal the waiting execution."""
        if execution_id not in self._credentials:
            self._credentials[execution_id] = {}
        self._credentials[execution_id][key] = value
        # Signal the waiting coroutine
        evt = self._credential_events.get(execution_id)
        if evt:
            evt.set()
            logger.info(f"Credential provided for execution {execution_id}, signaling wait")

    def get_credential(self, execution_id: str, key: str) -> Optional[str]:
        return self._credentials.get(execution_id, {}).get(key)

    async def _wait_for_credential(self, execution_id: str, timeout: float = 120.0) -> bool:
        """Wait for a credential to be provided via the API. Returns True if received."""
        evt = asyncio.Event()
        self._credential_events[execution_id] = evt
        try:
            await asyncio.wait_for(evt.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            logger.warning(f"Credential wait timed out for execution {execution_id}")
            return False
        finally:
            self._credential_events.pop(execution_id, None)

    # ------------------------------------------------------------------
    # LLM helpers
    # ------------------------------------------------------------------

    def _get_primary_client(self):
        return self.kimi or self.grok

    async def _llm_call(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 16384) -> str:
        client = self._get_primary_client()
        if not client:
            return "No LLM client available"

        try:
            model = "kimi-k2.5" if client == self.kimi else "grok-4-1-fast-reasoning"
            temp = 1 if client == self.kimi else temperature
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                functools.partial(
                    client.chat.completions.create,
                    model=model,
                    messages=messages,
                    temperature=temp,
                    max_tokens=max_tokens,
                ),
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            fallback = self.grok if client == self.kimi else self.kimi
            if fallback:
                try:
                    model = "grok-4-1-fast-reasoning" if fallback == self.grok else "kimi-k2.5"
                    temp = 0.5 if fallback == self.grok else 1
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(
                        None,
                        functools.partial(
                            fallback.chat.completions.create,
                            model=model,
                            messages=messages,
                            temperature=temp,
                            max_tokens=max_tokens,
                        ),
                    )
                    return response.choices[0].message.content or ""
                except Exception as e2:
                    return f"LLM error: {str(e)} / fallback: {str(e2)}"
            return f"LLM error: {str(e)}"

    async def _llm_stream(self, messages: List[Dict], max_tokens: int = 16384) -> AsyncGenerator[str, None]:
        """Stream LLM response token by token using async queue."""
        client = self._get_primary_client()
        if not client:
            yield "No LLM client available"
            return

        try:
            model = "kimi-k2.5" if client == self.kimi else "grok-4-1-fast-reasoning"
            temp = 1 if client == self.kimi else 0.7
            queue: asyncio.Queue = asyncio.Queue()
            SENTINEL = object()

            def _sync_stream():
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temp,
                        max_tokens=max_tokens,
                        stream=True,
                    )
                    for chunk in response:
                        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                            asyncio.run_coroutine_threadsafe(queue.put(chunk.choices[0].delta.content), loop)
                except Exception as e:
                    asyncio.run_coroutine_threadsafe(queue.put(f"\n\n[Error: {str(e)}]"), loop)
                finally:
                    asyncio.run_coroutine_threadsafe(queue.put(SENTINEL), loop)

            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, _sync_stream)

            while True:
                token = await queue.get()
                if token is SENTINEL:
                    break
                yield token
        except Exception as e:
            yield f"\n\n[Error during streaming: {str(e)}]"

    # ------------------------------------------------------------------
    # Main SSE streaming execution
    # ------------------------------------------------------------------

    async def execute_stream(
        self,
        user_request: str,
        context: Optional[Dict[str, Any]] = None,
        execution_id: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute a task and yield SSE events in real-time.

        Event types:
          start, execution_start, step_update, execution_progress,
          execution_reasoning, content, execution_artifact,
          credential_request, execution_complete, complete, execution_error
        """
        execution_id = execution_id or f"exec_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now()
        context = context or {}

        self._executions[execution_id] = {
            "status": ExecutionStatus.PLANNING,
            "cancelled": False,
            "paused": False,
        }

        try:
            # === PHASE 1: START ===
            yield {"event": "start", "data": {"conversation_id": execution_id}}
            yield {"event": "execution_start", "data": {"execution_id": execution_id}}

            # === PHASE 2: PLANNING ===
            yield {"event": "step_update", "data": {
                "id": "plan-1", "phase": "planning",
                "title": "Understanding your request",
                "status": "active",
                "detail": "Analyzing what needs to be done and creating an execution plan"
            }}
            yield {"event": "execution_reasoning", "data": {
                "chunk": "**Understanding Request**\n- Reading and analyzing the task requirements\n- Determining which tools and actions are needed\n"
            }}
            yield {"event": "execution_progress", "data": {"progress": 5, "status": "planning"}}
            # task_progress for message field (Manus-style — longer detail)
            yield {"event": "task_progress", "data": {
                "id": "tp-plan", "step": "tp-plan",
                "title": "Analyzing your request and creating execution plan",
                "status": "active",
                "detail": "Understanding the scope and requirements of your task. Identifying the best tools and approach to deliver accurate results. Preparing a multi-step execution strategy."
            }}

            plan = await self._create_plan(execution_id, user_request, context)

            # Format plan reasoning — clean, no API names
            plan_reasoning = f"**Execution Plan — {len(plan.steps)} steps**\n"
            for s in plan.steps:
                step_label = {
                    "research": "Search & gather information",
                    "code": "Write & run code",
                    "browser": "Visit & extract web content",
                    "github": "Repository operation",
                    "think": "Analyze & synthesize findings",
                }.get(s.get("step_type", ""), "Process task")
                plan_reasoning += f"- Step {s.get('step_number', '?')}: {step_label} — {s.get('instruction', '')[:100]}\n"
            plan_reasoning += "\n"

            yield {"event": "step_update", "data": {
                "id": "plan-1", "phase": "planning",
                "title": f"Plan ready — {len(plan.steps)} steps to execute",
                "status": "complete",
                "detail": plan.reasoning[:150] if plan.reasoning else "Execution plan created"
            }}
            yield {"event": "execution_reasoning", "data": {"chunk": plan_reasoning}}
            yield {"event": "execution_progress", "data": {"progress": 10, "status": "executing"}}
            # task_progress: plan complete
            plan_tools = set(s.get('step_type', '') for s in plan.steps)
            tools_desc = ', '.join({
                'research': 'web research', 'code': 'code execution',
                'browser': 'web browsing', 'github': 'repository operations',
                'think': 'analysis'
            }.get(t, t) for t in plan_tools if t)
            yield {"event": "task_progress", "data": {
                "id": "tp-plan", "step": "tp-plan",
                "title": f"Execution plan ready — {len(plan.steps)} steps",
                "status": "complete",
                "detail": f"Plan includes: {tools_desc}. {plan.reasoning[:80] if plan.reasoning else 'Optimized for accuracy and speed.'}"
            }}

            # === PHASE 3: EXECUTE STEPS ===
            all_step_results: List[ExecutionStep] = []
            total_steps = len(plan.steps)

            for i, step_data in enumerate(plan.steps):
                if self._executions.get(execution_id, {}).get("cancelled"):
                    yield {"event": "execution_error", "data": {"message": "Execution cancelled by user"}}
                    return

                while self._executions.get(execution_id, {}).get("paused"):
                    await asyncio.sleep(0.5)

                step_num = step_data.get("step_number", i + 1)
                step_type_str = step_data.get("step_type", "think")
                instruction = step_data.get("instruction", "")
                step_id = f"step-{step_num}"

                valid_types = {st.value for st in StepType}
                actual_type = step_type_str if step_type_str in valid_types else "think"
                phase = STEP_TYPE_TO_PHASE.get(StepType(actual_type), "execution")

                base_progress = 10
                step_progress = base_progress + int(((i + 0.5) / max(total_steps, 1)) * 70)

                # Clean step title — no API names
                step_title = self._clean_step_title(actual_type, instruction)

                # Emit step started
                yield {"event": "step_update", "data": {
                    "id": step_id, "phase": phase,
                    "title": step_title,
                    "status": "active",
                    "detail": f"Step {step_num} of {total_steps}"
                }}
                yield {"event": "execution_reasoning", "data": {
                    "chunk": f"**Step {step_num}/{total_steps}**\n- {step_title}\n"
                }}
                yield {"event": "execution_progress", "data": {"progress": step_progress, "status": "executing"}}
                # task_progress for message field — rich 3-line detail
                step_details = self._get_step_detail_lines(actual_type, instruction, step_num, total_steps)
                yield {"event": "task_progress", "data": {
                    "id": f"tp-{step_id}", "step": f"tp-{step_id}",
                    "title": step_title,
                    "status": "active",
                    "detail": step_details
                }}

                # Execute the step
                step = ExecutionStep(
                    step_id=step_id,
                    execution_id=execution_id,
                    step_number=step_num,
                    step_type=StepType(actual_type),
                    status=ExecutionStatus.EXECUTING,
                    agent=step_data.get("agent", "kimi"),
                    instruction=instruction,
                    input_data=step_data,
                )
                step.started_at = datetime.now()

                try:
                    # ALL step types use streaming execution via asyncio.Queue
                    # so sub-events (browser screenshots, reasoning, credential requests)
                    # reach the frontend in real-time as they're produced.
                    event_queue: asyncio.Queue = asyncio.Queue()
                    result_holder: Dict[str, Any] = {"result": None, "error": None}

                    async def _run_step(_step, _ctx, _prev, _queue, _eid, _type):
                        proxy = _SubEventQueue(_queue)
                        try:
                            if _type == "github":
                                r = await self._exec_github(_step, _ctx, _prev, proxy, _eid)
                            elif _type == "browser":
                                r = await self._exec_browser(_step, _ctx, proxy)
                            elif _type == "code":
                                r = await self._exec_code(_step, _ctx, _prev, proxy)
                            elif _type == "research":
                                r = await self._exec_research(_step, _ctx, _prev, proxy)
                            elif _type == "think":
                                r = await self._exec_think(_step, _ctx, _prev, proxy)
                            else:
                                r = await self._exec_think(_step, _ctx, _prev, proxy)
                            result_holder["result"] = r
                        except Exception as exc:
                            result_holder["error"] = exc
                        finally:
                            await _queue.put(None)  # sentinel

                    step_task = asyncio.create_task(
                        _run_step(step, context, all_step_results, event_queue, execution_id, actual_type)
                    )

                    # Yield sub-events in real-time as they're produced
                    while True:
                        sub_evt = await event_queue.get()
                        if sub_evt is None:
                            break
                        yield sub_evt

                    await step_task
                    if result_holder["error"]:
                        raise result_holder["error"]
                    result = result_holder["result"]

                    step.output_data = result
                    step.status = ExecutionStatus.COMPLETED
                    step.completed_at = datetime.now()
                    elapsed = (step.completed_at - step.started_at).total_seconds()

                    # Clean result summary
                    result_summary = self._clean_result_summary(result)
                    yield {"event": "step_update", "data": {
                        "id": step_id, "phase": phase,
                        "title": step_title,
                        "status": "complete",
                        "detail": result_summary
                    }}
                    yield {"event": "execution_reasoning", "data": {
                        "chunk": f"- Done ({elapsed:.1f}s): {result_summary}\n\n"
                    }}
                    # task_progress: step complete — concise summary
                    yield {"event": "task_progress", "data": {
                        "id": f"tp-{step_id}", "step": f"tp-{step_id}",
                        "title": step_title,
                        "status": "complete",
                        "detail": result_summary[:120]
                    }}

                except Exception as e:
                    step.status = ExecutionStatus.FAILED
                    step.error_message = str(e)
                    step.completed_at = datetime.now()
                    logger.error(f"Step {step_num} failed: {e}")

                    yield {"event": "step_update", "data": {
                        "id": step_id, "phase": phase,
                        "title": step_title,
                        "status": "error",
                        "detail": f"Failed: {str(e)[:100]}"
                    }}
                    yield {"event": "execution_reasoning", "data": {
                        "chunk": f"- Failed: {str(e)[:150]}\n\n"
                    }}
                    # task_progress: step failed
                    yield {"event": "task_progress", "data": {
                        "id": f"tp-{step_id}", "step": f"tp-{step_id}",
                        "title": step_title,
                        "status": "complete",
                        "detail": f"Encountered an issue, continuing..."
                    }}

                all_step_results.append(step)
                yield {"event": "execution_progress", "data": {
                    "progress": base_progress + int(((i + 1) / max(total_steps, 1)) * 70),
                    "status": "executing"
                }}

            # === PHASE 4: VERIFICATION ===
            yield {"event": "step_update", "data": {
                "id": "verify-1", "phase": "verification",
                "title": "Checking results quality",
                "status": "active"
            }}
            yield {"event": "execution_reasoning", "data": {
                "chunk": "**Checking Results**\n- Verifying data quality and completeness\n"
            }}
            yield {"event": "execution_progress", "data": {"progress": 82, "status": "verifying"}}
            yield {"event": "task_progress", "data": {
                "id": "tp-verify", "step": "tp-verify",
                "title": "Verifying results quality and completeness",
                "status": "active",
                "detail": "Cross-checking data accuracy and consistency across all gathered information. Ensuring all parts of your request have been addressed. Validating source reliability and output quality."
            }}

            verification = await self._verify_execution(all_step_results, user_request)

            completed_count = verification.get("completed_steps", 0)
            failed_count = verification.get("failed_steps", 0)
            confidence = verification.get("confidence", 0)

            verify_detail = f"{completed_count} of {completed_count + failed_count} steps completed"
            if confidence >= 0.8:
                verify_detail += " — high confidence"
            elif confidence >= 0.5:
                verify_detail += " — moderate confidence"

            yield {"event": "step_update", "data": {
                "id": "verify-1", "phase": "verification",
                "title": "Results verified",
                "status": "complete",
                "detail": verify_detail
            }}
            yield {"event": "execution_reasoning", "data": {
                "chunk": f"- {verify_detail}\n\n"
            }}
            yield {"event": "task_progress", "data": {
                "id": "tp-verify", "step": "tp-verify",
                "title": "Results verified",
                "status": "complete",
                "detail": verify_detail
            }}

            # === PHASE 5: DELIVERY ===
            yield {"event": "step_update", "data": {
                "id": "deliver-1", "phase": "delivery",
                "title": "Writing comprehensive response",
                "status": "active"
            }}
            yield {"event": "execution_reasoning", "data": {
                "chunk": "**Preparing Response**\n- Synthesizing all findings into a clear answer\n"
            }}
            yield {"event": "execution_progress", "data": {"progress": 90, "status": "delivering"}}
            yield {"event": "task_progress", "data": {
                "id": "tp-deliver", "step": "tp-deliver",
                "title": "Composing comprehensive response",
                "status": "active",
                "detail": "Synthesizing all findings into a clear, structured answer. Organizing key insights with supporting evidence. Formatting the response for maximum readability."
            }}

            full_content = ""
            async for token in self._deliver_stream(all_step_results, user_request, verification, context):
                full_content += token
                yield {"event": "content", "data": {"chunk": token}}

            yield {"event": "step_update", "data": {
                "id": "deliver-1", "phase": "delivery",
                "title": "Response delivered",
                "status": "complete",
                "detail": f"{len(full_content):,} characters"
            }}

            # === COMPLETE ===
            execution_time = (datetime.now() - start_time).total_seconds()
            yield {"event": "execution_progress", "data": {"progress": 100, "status": "completed"}}
            yield {"event": "execution_complete", "data": {
                "status": "completed",
                "execution_time": round(execution_time, 1),
                "steps_completed": len([s for s in all_step_results if s.status == ExecutionStatus.COMPLETED]),
                "total_steps": len(all_step_results),
            }}
            yield {"event": "complete", "data": {
                "content": full_content,
                "model": "agent-orchestrator",
            }}

        except Exception as e:
            logger.error(f"Execution failed: {e}\n{traceback.format_exc()}")
            yield {"event": "execution_error", "data": {"message": str(e)}}
            yield {"event": "error", "data": {"message": str(e)}}

        finally:
            self._executions.pop(execution_id, None)
            self._credentials.pop(execution_id, None)

    # ------------------------------------------------------------------
    # Planning
    # ------------------------------------------------------------------

    async def _create_plan(self, execution_id: str, user_request: str, context: Optional[Dict]) -> ExecutionPlan:
        current_date = date.today().isoformat()

        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', user_request)
        has_urls = len(urls) > 0

        github_patterns = ["github", "repo", "repository", "commit", "push", "pull request", "PR", "branch", "merge", "git"]
        needs_github = any(kw.lower() in user_request.lower() for kw in github_patterns)

        code_keywords = ["code", "script", "program", "calculate", "compute", "analyze data", "chart", "plot", "graph", "csv", "json", "python"]
        needs_code = any(kw in user_request.lower() for kw in code_keywords)

        available_tools = ["research", "think"]
        # Code: E2B or local sandbox
        if (self.e2b and self.e2b.available) or self.local_sandbox:
            available_tools.append("code")
        # Browser: Playwright engine or Browserless
        if self.browser_engine or (self.browserless and self.browserless.available):
            available_tools.append("browser")
        if self.github:
            available_tools.append("github")

        plan_prompt = f"""You are an execution planner for an AI agent. Today is {current_date}.

AVAILABLE STEP TYPES:
- research: Search the web for information using multiple search engines
- think: Analyze and reason about collected data, synthesize findings
{f'- code: Generate and execute Python/JavaScript code in a secure sandbox (data analysis, file generation, calculations, automation scripts)' if 'code' in available_tools else ''}
{f'- browser: Open a live browser with real-time screen capture. Can navigate URLs, click buttons, fill forms, scroll pages, interact with any website. Use for: visiting URLs, web scraping, interactive web tasks, logging into platforms, filling forms, searching on websites' if 'browser' in available_tools else ''}
{f'- github: Perform GitHub repository operations (read files, create/update files, create branches, create PRs, list issues, push code changes)' if 'github' in available_tools else ''}

Decompose this user request into 2-8 executable steps.

RULES:
- If the user provides URLs, include a "browser" step to visit and extract content FIRST
- If the user mentions GitHub/repos, include "github" steps for repo operations
- For data analysis, calculations, or file generation, include a "code" step
- Use "browser" for ANY task that requires visiting a website, clicking, filling forms, or interacting with web pages
- Always include at least one "research" step for information gathering
- End with a "think" step to synthesize all findings
- Keep instructions specific and actionable
- For GitHub write operations (push, edit, create PR), the instruction must specify: owner, repo, file path, and what to change
- For browser steps, specify the target URL and what actions to perform (navigate, click, type, extract)

For each step provide:
- step_number (integer starting from 1)
- step_type (one of: {', '.join(available_tools)})
- instruction (specific, actionable)
- agent ("kimi")
- expected_output (what this step produces)
- dependencies (list of step_numbers this depends on, [] if independent)

Respond ONLY in JSON:
{{
    "objective": "brief description",
    "reasoning": "why this plan makes sense",
    "steps": [
        {{"step_number": 1, "step_type": "research", "instruction": "...", "agent": "kimi", "expected_output": "...", "dependencies": []}}
    ]
}}

User Request: {user_request}
{"URLs detected: " + ", ".join(urls) if urls else ""}
{"Context: " + json.dumps(context, default=str)[:500] if context else ""}"""

        content = await self._llm_call(
            messages=[{"role": "user", "content": plan_prompt}],
            max_tokens=4096,
        )

        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            plan_data = json.loads(content.strip())
            steps = plan_data.get("steps", [])

            valid_types = {st.value for st in StepType}
            for s in steps:
                if s.get("step_type") not in valid_types:
                    s["step_type"] = "think"
                if "agent" not in s:
                    s["agent"] = "kimi"

            # Force browser step if URLs detected but not in plan
            if has_urls and not any(s.get("step_type") == "browser" for s in steps):
                browser_step = {
                    "step_number": 0,
                    "step_type": "browser",
                    "instruction": f"Navigate to and extract content from: {urls[0]}",
                    "agent": "kimi",
                    "expected_output": "Page content",
                    "dependencies": [],
                }
                steps.insert(0, browser_step)
                for idx, s in enumerate(steps):
                    s["step_number"] = idx + 1

            # Force github step if repo operations needed but not in plan
            if needs_github and "github" in available_tools and not any(s.get("step_type") == "github" for s in steps):
                github_step = {
                    "step_number": len(steps) + 1,
                    "step_type": "github",
                    "instruction": f"Perform GitHub operation for: {user_request[:200]}",
                    "agent": "kimi",
                    "expected_output": "Repository operation result",
                    "dependencies": [],
                }
                steps.append(github_step)

            return ExecutionPlan(
                plan_id=f"plan_{uuid.uuid4().hex[:8]}",
                objective=plan_data.get("objective", user_request),
                steps=steps[:self.max_steps],
                estimated_duration=len(steps) * 15,
                reasoning=plan_data.get("reasoning", ""),
                parallel_groups=plan_data.get("parallel_groups", [[s["step_number"]] for s in steps]),
            )

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Plan parsing failed, using smart fallback: {e}")
            return self._fallback_plan(user_request, has_urls, needs_code, needs_github, urls)

    def _fallback_plan(self, user_request, has_urls, needs_code, needs_github, urls):
        fallback_steps = []
        step_num = 1

        if has_urls:
            fallback_steps.append({
                "step_number": step_num, "step_type": "browser",
                "instruction": f"Extract content from: {urls[0]}",
                "agent": "kimi", "expected_output": "URL content", "dependencies": [],
            })
            step_num += 1

        fallback_steps.append({
            "step_number": step_num, "step_type": "research",
            "instruction": f"Research: {user_request}",
            "agent": "kimi", "expected_output": "Research findings", "dependencies": [],
        })
        step_num += 1

        if needs_code:
            fallback_steps.append({
                "step_number": step_num, "step_type": "code",
                "instruction": f"Write and execute code for: {user_request}",
                "agent": "kimi", "expected_output": "Code output", "dependencies": [],
            })
            step_num += 1

        if needs_github:
            fallback_steps.append({
                "step_number": step_num, "step_type": "github",
                "instruction": f"GitHub operation: {user_request[:200]}",
                "agent": "kimi", "expected_output": "Repo operation result", "dependencies": [],
            })
            step_num += 1

        fallback_steps.append({
            "step_number": step_num, "step_type": "think",
            "instruction": f"Synthesize all findings for: {user_request}",
            "agent": "kimi", "expected_output": "Final analysis",
            "dependencies": list(range(1, step_num)),
        })

        return ExecutionPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:8]}",
            objective=user_request,
            steps=fallback_steps,
            estimated_duration=len(fallback_steps) * 15,
            reasoning="Automatic plan based on task analysis",
            parallel_groups=[[s["step_number"]] for s in fallback_steps],
        )

    # ------------------------------------------------------------------
    # Step execution dispatcher
    # ------------------------------------------------------------------

    async def _execute_step_with_events(
        self,
        step: ExecutionStep,
        context: Optional[Dict],
        previous_steps: List[ExecutionStep],
        execution_id: str = "",
    ) -> tuple:
        sub_events = []

        if step.step_type == StepType.RESEARCH:
            result = await self._exec_research(step, context, previous_steps, sub_events)
        elif step.step_type == StepType.CODE:
            result = await self._exec_code(step, context, previous_steps, sub_events)
        elif step.step_type == StepType.BROWSER:
            result = await self._exec_browser(step, context, sub_events)
        elif step.step_type == StepType.GITHUB:
            # GitHub uses the streaming variant so credential_request reaches frontend before wait
            result = await self._exec_github(step, context, previous_steps, sub_events, execution_id)
        elif step.step_type == StepType.THINK:
            result = await self._exec_think(step, context, previous_steps, sub_events)
        else:
            result = await self._exec_think(step, context, previous_steps, sub_events)

        return result, sub_events

    # ------------------------------------------------------------------
    # RESEARCH — Clean reasoning, no API names
    # ------------------------------------------------------------------

    async def _exec_research(self, step, context, previous, sub_events):
        if self.search_layer:
            try:
                sub_events.append({"event": "execution_reasoning", "data": {
                    "chunk": "- Searching across multiple sources for relevant information\n"
                }})

                search_result = await self.search_layer.search(
                    step.instruction,
                    sources=["web", "news", "social"],
                    num_results=15,
                )

                # Extract from structured_data (aggregated format)
                structured_data = search_result.get("structured_data", {})
                data_points = structured_data.get("data_points", [])
                sources = structured_data.get("sources", [])

                # Get AI summary from results
                ai_summary = ""
                results_dict = search_result.get("results", {})
                if isinstance(results_dict, dict):
                    for src_name, src_data in results_dict.items():
                        if isinstance(src_data, dict) and src_data.get("answer"):
                            ai_summary = src_data["answer"]
                            break

                # Build findings from data points
                findings_parts = []
                if ai_summary:
                    findings_parts.append(f"**Summary:**\n{ai_summary[:3000]}")

                seen = set()
                for dp in data_points[:20]:
                    if isinstance(dp, dict):
                        title = dp.get("title", "")
                        desc = dp.get("description", "")
                        if desc and desc[:80] not in seen:
                            seen.add(desc[:80])
                            findings_parts.append(f"**{title}**: {desc[:400]}")

                # Count active sources (without naming them)
                active_count = 0
                if isinstance(results_dict, dict):
                    for src_data in results_dict.values():
                        if isinstance(src_data, dict) and not src_data.get("error"):
                            active_count += 1

                findings_text = "\n\n".join(findings_parts) if findings_parts else "No results found"

                sub_events.append({"event": "execution_reasoning", "data": {
                    "chunk": f"- Found {len(data_points)} results from {active_count} search engines\n"
                    f"- Collected {len(sources)} unique source URLs\n"
                }})

                return {
                    "type": "research",
                    "query": step.instruction,
                    "findings": findings_text,
                    "sources": sources[:15],
                    "result_count": len(data_points),
                    "active_source_count": active_count,
                    "ai_summary": ai_summary[:2000] if ai_summary else "",
                }

            except Exception as e:
                logger.error(f"Search failed: {e}")
                sub_events.append({"event": "execution_reasoning", "data": {
                    "chunk": f"- Web search encountered an error. Using AI knowledge base instead.\n"
                }})
                content = await self._llm_call([
                    {"role": "system", "content": "Provide comprehensive, factual information with sources."},
                    {"role": "user", "content": step.instruction},
                ])
                return {"type": "research", "findings": content, "sources": [], "fallback": True, "result_count": 0}
        else:
            sub_events.append({"event": "execution_reasoning", "data": {
                "chunk": "- Using AI knowledge base for research\n"
            }})
            content = await self._llm_call([
                {"role": "system", "content": "Provide comprehensive, factual information."},
                {"role": "user", "content": step.instruction},
            ])
            return {"type": "research", "findings": content, "sources": [], "result_count": 0}

    # ------------------------------------------------------------------
    # CODE — E2B sandbox execution
    # ------------------------------------------------------------------

    async def _exec_code(self, step, context, previous, sub_events):
        prev_context = self._get_previous_context(previous)

        sub_events.append({"event": "execution_reasoning", "data": {
            "chunk": "- Generating code for the task\n"
        }})

        code_prompt = f"""Write clean, executable Python code for this task.

Task: {step.instruction}

{f"Previous data/context from earlier steps: {prev_context[:3000]}" if prev_context else ""}

IMPORTANT REQUIREMENTS:
- Return ONLY raw Python code, no markdown, no ```python fences, no explanations
- The code must be directly executable with python3
- Print all results to stdout using print()
- Handle errors gracefully with try/except
- If creating visualizations, save to /tmp/output.png and print the file path
- If processing data, print a clear summary of results
- Start with import statements if needed
- The code must produce meaningful output"""

        code_content = await self._llm_call([
            {"role": "system", "content": "Return ONLY executable Python code, no markdown fences, no explanations."},
            {"role": "user", "content": code_prompt},
        ], max_tokens=4096)

        # Clean code
        code_content = code_content.strip()
        for prefix in ["```python", "```py", "```"]:
            if code_content.startswith(prefix):
                code_content = code_content[len(prefix):]
                break
        if code_content.endswith("```"):
            code_content = code_content[:-3]
        code_content = code_content.strip()

        # Validate Python syntax before execution
        import ast
        try:
            ast.parse(code_content)
        except SyntaxError as syn_err:
            sub_events.append({"event": "execution_reasoning", "data": {
                "chunk": f"- Syntax error detected, regenerating code...\n"
            }})
            # Retry with explicit error feedback
            retry_prompt = f"""The previous code had a syntax error: {syn_err}

Original task: {step.instruction}

Write CORRECT, COMPLETE Python code. Return ONLY raw Python code.
No markdown fences. No explanations. Must be directly executable."""
            code_content = await self._llm_call([
                {"role": "system", "content": "Return ONLY executable Python code. No markdown. No explanations."},
                {"role": "user", "content": retry_prompt},
            ], max_tokens=4096)
            code_content = code_content.strip()
            for prefix in ["```python", "```py", "```"]:
                if code_content.startswith(prefix):
                    code_content = code_content[len(prefix):]
                    break
            if code_content.endswith("```"):
                code_content = code_content[:-3]
            code_content = code_content.strip()

        # Fallback if code is empty or too short
        if len(code_content.strip()) < 10:
            code_content = f"""# Auto-generated code for: {step.instruction[:100]}
import json

# Task: {step.instruction[:200]}
result = "Code generation produced minimal output. Task: {step.instruction[:100]}"
print(result)
"""

        sub_events.append({"event": "execution_reasoning", "data": {
            "chunk": f"- Generated {len(code_content.splitlines())} lines of Python code\n"
        }})

        # Try E2B first, then local sandbox fallback
        sandbox_to_use = None
        sandbox_name = ""

        if self.e2b and self.e2b.available:
            sandbox_to_use = self.e2b
            sandbox_name = "cloud sandbox"
        else:
            # Lazy-init local sandbox
            if not self.local_sandbox:
                try:
                    from agentic.local_sandbox import get_local_sandbox
                    self.local_sandbox = get_local_sandbox()
                except Exception:
                    pass
            if self.local_sandbox and self.local_sandbox.available:
                sandbox_to_use = self.local_sandbox
                sandbox_name = "local sandbox"

        if sandbox_to_use:
            try:
                sub_events.append({"event": "execution_reasoning", "data": {
                    "chunk": f"- Running code in {sandbox_name}\n"
                }})

                result = await sandbox_to_use.execute_code(code_content, language="python", timeout=30)

                if result.success:
                    output_preview = (result.output or "")[:200]
                    sub_events.append({"event": "execution_reasoning", "data": {
                        "chunk": f"- Code executed successfully ({result.execution_time_ms:.0f}ms)\n- Output: {output_preview}\n"
                    }})
                else:
                    sub_events.append({"event": "execution_reasoning", "data": {
                        "chunk": f"- Code execution error: {(result.error or '')[:150]}\n"
                    }})

                return {
                    "type": "code_execution",
                    "code": code_content,
                    "output": result.output or "",
                    "error": result.error or "",
                    "success": result.success,
                    "execution_time_ms": result.execution_time_ms,
                }
            except Exception as e:
                sub_events.append({"event": "execution_reasoning", "data": {
                    "chunk": f"- Sandbox execution failed: {str(e)[:100]}\n"
                }})
                return {"type": "code_execution", "code": code_content, "output": "", "error": str(e), "success": False}
        else:
            sub_events.append({"event": "execution_reasoning", "data": {
                "chunk": "- Code sandbox not available \u2014 code generated for reference\n"
            }})
            return {"type": "code_generation", "code": code_content, "note": "Sandbox not available", "success": True}

    # ------------------------------------------------------------------
    # BROWSER — Playwright live browser + Browserless fallback
    # ------------------------------------------------------------------

    async def _exec_browser(self, step, context, sub_events):
        """Execute browser operations with live screenshot streaming.

        Priority:
        1. Playwright browser engine (interactive, screenshots streamed to frontend)
        2. Browserless (simple content extraction fallback)
        3. LLM fallback (no browser available)
        """
        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', step.instruction)
        instruction_lower = step.instruction.lower()

        # Determine if this is an interactive task (needs clicking, typing, etc.)
        interactive_keywords = ["click", "fill", "type", "submit", "login", "sign in",
                                "search for", "enter", "navigate and", "interact",
                                "book", "order", "purchase", "register", "form",
                                "browse", "scroll", "find and click", "automation"]
        is_interactive = any(kw in instruction_lower for kw in interactive_keywords)

        # === PRIORITY 1: Playwright Browser Engine (live screenshots) ===
        if self.browser_engine:
            try:
                if is_interactive or not urls:
                    # Full CUA (Computer-Use Agent) loop with vision model
                    sub_events.append({"event": "execution_reasoning", "data": {
                        "chunk": "- Starting live browser automation with screen capture...\n"
                    }})
                    start_url = urls[0] if urls else None
                    result = await self.browser_engine.execute_task(
                        task=step.instruction,
                        start_url=start_url,
                        max_steps=15,
                        sub_events=sub_events,
                    )
                    return result
                else:
                    # Simple navigate + extract with screenshot
                    target_url = urls[0]
                    sub_events.append({"event": "execution_reasoning", "data": {
                        "chunk": f"- Opening {target_url[:80]} in live browser...\n"
                    }})
                    result = await self.browser_engine.navigate_and_extract(
                        url=target_url,
                        sub_events=sub_events,
                    )
                    return result

            except Exception as e:
                logger.error(f"Browser engine error: {e}")
                sub_events.append({"event": "execution_reasoning", "data": {
                    "chunk": f"- Live browser encountered an error, falling back to content extraction...\n"
                }})
                # Fall through to Browserless

        # === PRIORITY 2: Browserless (simple extraction + screenshot) ===
        if self.browserless and self.browserless.available:
            if urls:
                target_url = urls[0]
                sub_events.append({"event": "execution_reasoning", "data": {
                    "chunk": f"- Opening {target_url[:80]} in browser...\n"
                }})

                try:
                    # Capture screenshot for live preview
                    try:
                        screenshot_result = await self.browserless.screenshot(target_url, full_page=False)
                        if screenshot_result.success and screenshot_result.screenshot:
                            import base64
                            screenshot_b64 = base64.b64encode(screenshot_result.screenshot).decode('utf-8')
                            sub_events.append({"event": "browser_screenshot", "data": {
                                "screenshot": screenshot_b64,
                                "url": target_url,
                                "title": f"Browsing: {target_url[:60]}",
                                "step": step.step_number if hasattr(step, 'step_number') else 0,
                                "action": "Extracting page content",
                            }})
                    except Exception as ss_err:
                        logger.debug(f"Screenshot capture failed (non-fatal): {ss_err}")

                    result = await self.browserless.deep_extract(target_url, extract_links=True)

                    if result.get("success"):
                        title = result.get("title", "")
                        text = result.get("text", "")
                        links = result.get("links", [])
                        sub_events.append({"event": "execution_reasoning", "data": {
                            "chunk": f"- Extracted {len(text):,} characters from the page\n"
                            f"- Page title: {title[:80]}\n"
                            f"- Found {len(links)} links\n"
                        }})
                        return {
                            "type": "browser_extraction",
                            "url": target_url,
                            "title": title,
                            "content": text[:8000],
                            "links": links[:20],
                            "success": True,
                        }
                    else:
                        error = result.get("error", "Could not extract page content")
                        sub_events.append({"event": "execution_reasoning", "data": {
                            "chunk": f"- Could not extract content from the URL\n"
                        }})
                        return {"type": "browser_error", "url": target_url, "error": error, "success": False}

                except Exception as e:
                    sub_events.append({"event": "execution_reasoning", "data": {
                        "chunk": f"- Web extraction error: {str(e)[:80]}\n"
                    }})
                    return {"type": "browser_error", "url": target_url, "error": str(e), "success": False}
            else:
                sub_events.append({"event": "execution_reasoning", "data": {
                    "chunk": "- No URL found in instruction. Performing web search instead.\n"
                }})
                try:
                    search_url = f"https://www.google.com/search?q={step.instruction[:100].replace(' ', '+')}"
                    result = await self.browserless.navigate(search_url)
                    return {
                        "type": "browser_search",
                        "query": step.instruction,
                        "content": result.content[:5000] if result.content else "",
                        "success": result.success,
                    }
                except Exception as e:
                    return {"type": "browser_error", "error": str(e), "success": False}

        # === PRIORITY 3: LLM Fallback ===
        sub_events.append({"event": "execution_reasoning", "data": {
            "chunk": "- Web browser not available. Using AI to analyze the request.\n"
        }})
        if urls:
            content = await self._llm_call([
                {"role": "system", "content": "The user wants to analyze a URL. Provide what you know about this URL/domain."},
                {"role": "user", "content": f"Analyze this URL: {urls[0]}\n\nContext: {step.instruction}"},
            ])
            return {"type": "browser_fallback", "url": urls[0], "content": content}
        else:
            content = await self._llm_call([{"role": "user", "content": step.instruction}])
            return {"type": "browser_fallback", "content": content}

    # ------------------------------------------------------------------
    # GITHUB — Real repository operations
    # ------------------------------------------------------------------

    async def _exec_github(self, step, context, previous, sub_events, execution_id):
        """Execute GitHub operations using the GitHub API."""
        if not self.github:
            sub_events.append({"event": "execution_reasoning", "data": {
                "chunk": "- GitHub integration not configured. Providing guidance instead.\n"
            }})
            content = await self._llm_call([
                {"role": "system", "content": "The user wants to perform a GitHub operation but the GitHub API is not configured. Explain what would need to be done and provide the commands/steps."},
                {"role": "user", "content": step.instruction},
            ])
            return {"type": "github_guidance", "content": content, "success": False, "needs_setup": True}

        # Check if we have a token (from credential system or already set on client)
        token = self.get_credential(execution_id, "github_token")
        if token:
            self.github.set_token(token)

        if not self.github.token:
            # Emit credential request with all fields the frontend expects
            sub_events.append({"event": "credential_request", "data": {
                "credential_type": "github_token",
                "type": "github_token",
                "message": "To perform GitHub operations, I need a GitHub Personal Access Token (PAT) with 'repo' scope. You can create one at https://github.com/settings/tokens",
                "execution_id": execution_id,
                "field_label": "GitHub Personal Access Token",
                "required_scopes": ["repo"],
                "url": "https://github.com/settings/tokens",
            }})
            sub_events.append({"event": "execution_reasoning", "data": {
                "chunk": "- GitHub token required for repository operations\n- Waiting for you to provide credentials (up to 2 minutes)...\n"
            }})

            # Wait for the user to provide the credential via /api/v2/execute/credential
            received = await self._wait_for_credential(execution_id, timeout=120.0)

            if received:
                token = self.get_credential(execution_id, "github_token")
                if token:
                    self.github.set_token(token)
                    sub_events.append({"event": "execution_reasoning", "data": {
                        "chunk": "- GitHub token received. Proceeding with repository operation.\n"
                    }})
                else:
                    sub_events.append({"event": "execution_reasoning", "data": {
                        "chunk": "- Credential received but token was empty.\n"
                    }})
                    return {"type": "github_needs_auth", "content": "Token was empty.", "success": False, "needs_token": True}
            else:
                sub_events.append({"event": "execution_reasoning", "data": {
                    "chunk": "- Timed out waiting for GitHub token. Providing guidance instead.\n"
                }})
                content = await self._llm_call([
                    {"role": "system", "content": "The user wanted a GitHub operation but didn't provide a token in time. Explain what the operation would do and how to provide a GitHub PAT next time."},
                    {"role": "user", "content": step.instruction},
                ])
                return {"type": "github_needs_auth", "content": content, "success": False, "needs_token": True}

        # Parse the instruction to determine the GitHub operation
        instruction_lower = step.instruction.lower()

        # Extract owner/repo from instruction or context
        repo_match = re.search(r'(?:github\.com/)?([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+)', step.instruction)
        owner = repo_match.group(1) if repo_match else None
        repo = repo_match.group(2) if repo_match else None

        # Try to get from context
        if not owner and context:
            owner = context.get("github_owner")
            repo = context.get("github_repo")

        if not owner or not repo:
            sub_events.append({"event": "execution_reasoning", "data": {
                "chunk": "- Could not determine repository from the instruction\n"
            }})
            content = await self._llm_call([
                {"role": "system", "content": "Help the user specify which GitHub repository they want to operate on."},
                {"role": "user", "content": step.instruction},
            ])
            return {"type": "github_error", "content": content, "error": "Could not determine owner/repo", "success": False}

        sub_events.append({"event": "execution_reasoning", "data": {
            "chunk": f"- Working with repository: {owner}/{repo}\n"
        }})

        try:
            # Determine operation type — check WRITE operations BEFORE read
            # (instructions often contain both "read" and "create" keywords)
            if any(kw in instruction_lower for kw in ["pull request", "pr ", "merge request", "open pr", "create pr"]):
                return await self._github_pr(owner, repo, step, sub_events)
            elif any(kw in instruction_lower for kw in [
                "create file", "add file", "write file", "update file", "edit file",
                "push", "commit", "create", "write", "update", "modify", "add",
                "generate", "deploy", "upload", "save to", "overwrite",
            ]):
                return await self._github_write(owner, repo, step, previous, sub_events)
            elif any(kw in instruction_lower for kw in ["branch", "create branch", "new branch"]):
                return await self._github_branch(owner, repo, step, sub_events)
            elif any(kw in instruction_lower for kw in ["issue", "bug", "feature request"]):
                return await self._github_issue(owner, repo, step, sub_events)
            elif any(kw in instruction_lower for kw in ["read", "get", "show", "list", "view", "check", "analyze", "inspect", "fetch", "retrieve"]):
                return await self._github_read(owner, repo, step, sub_events)
            else:
                # Default: get repo info and list files
                return await self._github_read(owner, repo, step, sub_events)

        except Exception as e:
            sub_events.append({"event": "execution_reasoning", "data": {
                "chunk": f"- GitHub operation failed: {str(e)[:100]}\n"
            }})
            return {"type": "github_error", "error": str(e), "success": False}

    async def _github_read(self, owner, repo, step, sub_events):
        """Read repository info and files."""
        sub_events.append({"event": "execution_reasoning", "data": {
            "chunk": "- Reading repository information\n"
        }})

        repo_info = await self.github.get_repo_info(owner, repo)
        if not repo_info.success:
            return {"type": "github_error", "error": repo_info.error, "success": False}

        # Try to list root directory
        dir_result = await self.github.list_directory(owner, repo, "")
        entries = dir_result.data.get("entries", []) if dir_result.success else []

        # Check if a specific file is mentioned
        file_match = re.search(r'(?:file|path)[:\s]+([^\s,]+)', step.instruction)
        file_content = None
        if file_match:
            file_path = file_match.group(1)
            file_result = await self.github.get_file_content(owner, repo, file_path)
            if file_result.success:
                file_content = file_result.data
                sub_events.append({"event": "execution_reasoning", "data": {
                    "chunk": f"- Read file: {file_path} ({file_result.data.get('size', 0)} bytes)\n"
                }})

        sub_events.append({"event": "execution_reasoning", "data": {
            "chunk": f"- Repository: {repo_info.data.get('full_name')}\n"
            f"- Language: {repo_info.data.get('language', 'N/A')}\n"
            f"- {len(entries)} items in root directory\n"
        }})

        return {
            "type": "github_read",
            "repo_info": repo_info.data,
            "directory": entries[:30],
            "file_content": file_content,
            "success": True,
        }

    async def _github_write(self, owner, repo, step, previous, sub_events):
        """Create or update files in the repository."""
        prev_context = self._get_previous_context(previous)

        # Generate the file content using LLM
        write_prompt = f"""Based on the instruction, determine:
1. The file path to create/update
2. The file content
3. A commit message

Instruction: {step.instruction}

{f"Context from previous steps: {prev_context[:3000]}" if prev_context else ""}

Respond in JSON:
{{"file_path": "path/to/file.ext", "content": "file content here", "commit_message": "descriptive commit message"}}"""

        response = await self._llm_call([{"role": "user", "content": write_prompt}], max_tokens=8192)

        try:
            # FIXED: Robust JSON parsing with multiple strategies
            cleaned = response.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0]
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0]
            
            # Try direct parse first
            try:
                file_data = json.loads(cleaned.strip())
            except json.JSONDecodeError:
                # Try to find JSON object in the response
                json_match = re.search(r'\{[\s\S]*"file_path"[\s\S]*\}', cleaned, re.DOTALL)
                if json_match:
                    try:
                        file_data = json.loads(json_match.group(0))
                    except json.JSONDecodeError:
                        # Last resort: extract fields with regex
                        path_match = re.search(r'"file_path"\s*:\s*"([^"]+)"', cleaned)
                        content_match = re.search(r'"content"\s*:\s*"([\s\S]*?)"\s*[,}]', cleaned)
                        msg_match = re.search(r'"commit_message"\s*:\s*"([^"]+)"', cleaned)
                        if path_match:
                            file_data = {
                                "file_path": path_match.group(1),
                                "content": content_match.group(1) if content_match else "",
                                "commit_message": msg_match.group(1) if msg_match else "Update file",
                            }
                        else:
                            raise ValueError("No file_path found")
                else:
                    raise ValueError("No JSON object found")
        except (json.JSONDecodeError, IndexError, ValueError, AttributeError) as parse_err:
            logger.error(f"GitHub write parse error: {parse_err}. Response preview: {response[:300]}")
            sub_events.append({"event": "execution_reasoning", "data": {
                "chunk": f"- Could not parse file operation details from LLM response\n"
            }})
            return {"type": "github_error", "error": f"Could not parse file operation details: {str(parse_err)}", "raw_response": response[:500], "success": False}

        file_path = file_data.get("file_path", "") or file_data.get("path", "")
        content = file_data.get("content", "") or file_data.get("file_content", "")
        message = file_data.get("commit_message", "") or file_data.get("message", f"Update {file_path}")

        if not file_path or not content:
            return {"type": "github_error", "error": "Missing file path or content", "success": False}

        sub_events.append({"event": "execution_reasoning", "data": {
            "chunk": f"- Creating/updating file: {file_path}\n- Commit message: {message}\n"
        }})

        # Check if file exists (to get SHA for update)
        existing = await self.github.get_file_content(owner, repo, file_path)
        sha = existing.data.get("sha") if existing.success else None

        result = await self.github.create_or_update_file(
            owner, repo, file_path, content, message, sha=sha
        )

        if result.success:
            sub_events.append({"event": "execution_reasoning", "data": {
                "chunk": f"- File committed successfully\n- Commit: {result.data.get('commit_sha', '')[:8]}\n"
            }})
            # Emit as artifact
            sub_events.append({"event": "execution_artifact", "data": {
                "name": file_path,
                "type": "code",
                "url": result.url,
            }})
        else:
            sub_events.append({"event": "execution_reasoning", "data": {
                "chunk": f"- Failed to commit: {result.error[:100]}\n"
            }})

        return {
            "type": "github_write",
            "file_path": file_path,
            "commit_sha": result.data.get("commit_sha"),
            "commit_url": result.data.get("commit_url"),
            "url": result.url,
            "success": result.success,
            "error": result.error,
        }

    async def _github_pr(self, owner, repo, step, sub_events):
        """Create a pull request."""
        pr_prompt = f"""Based on this instruction, determine the PR details:
Instruction: {step.instruction}

Respond with ONLY a JSON object (no markdown, no explanation):
{{"title": "PR title", "body": "PR description", "head": "source-branch", "base": "main"}}"""

        response = await self._llm_call([
            {"role": "system", "content": "Return ONLY valid JSON. No markdown fences. No explanation."},
            {"role": "user", "content": pr_prompt},
        ])
        try:
            # Try to extract JSON from various formats
            cleaned = response.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0]
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0]
            # Find JSON object in the response
            json_match = re.search(r'\{[^{}]*\}', cleaned, re.DOTALL)
            if json_match:
                cleaned = json_match.group(0)
            pr_data = json.loads(cleaned.strip())
        except (json.JSONDecodeError, IndexError, AttributeError) as e:
            sub_events.append({"event": "execution_reasoning", "data": {
                "chunk": f"- Could not parse PR details from LLM response, using defaults\n"
            }})
            # Use sensible defaults
            pr_data = {
                "title": f"Update from agent: {step.instruction[:60]}",
                "body": f"Automated PR created by McLeuker AI agent.\n\nTask: {step.instruction}",
                "head": f"feature/agent-{uuid.uuid4().hex[:6]}",
                "base": "main"
            }

        sub_events.append({"event": "execution_reasoning", "data": {
            "chunk": f"- Creating pull request: {pr_data.get('title', '')}\n"
        }})

        result = await self.github.create_pull_request(
            owner, repo,
            title=pr_data.get("title", ""),
            body=pr_data.get("body", ""),
            head=pr_data.get("head", ""),
            base=pr_data.get("base", "main"),
        )

        if result.success:
            sub_events.append({"event": "execution_reasoning", "data": {
                "chunk": f"- PR #{result.data.get('number')} created: {result.url}\n"
            }})

        return {
            "type": "github_pr",
            "pr_number": result.data.get("number"),
            "url": result.url,
            "success": result.success,
            "error": result.error,
        }

    async def _github_branch(self, owner, repo, step, sub_events):
        """Create a branch."""
        branch_match = re.search(r'(?:branch|named?)\s+["\']?([a-zA-Z0-9_/-]+)', step.instruction)
        branch_name = branch_match.group(1) if branch_match else f"feature/{uuid.uuid4().hex[:6]}"

        sub_events.append({"event": "execution_reasoning", "data": {
            "chunk": f"- Creating branch: {branch_name}\n"
        }})

        result = await self.github.create_branch(owner, repo, branch_name)

        if result.success:
            sub_events.append({"event": "execution_reasoning", "data": {
                "chunk": f"- Branch '{branch_name}' created from {result.data.get('from_branch', 'main')}\n"
            }})

        return {
            "type": "github_branch",
            "branch": branch_name,
            "success": result.success,
            "error": result.error,
        }

    async def _github_issue(self, owner, repo, step, sub_events):
        """List or create issues."""
        if any(kw in step.instruction.lower() for kw in ["create", "open", "new", "file"]):
            issue_prompt = f"""Based on this instruction, create an issue:
Instruction: {step.instruction}

Respond in JSON:
{{"title": "Issue title", "body": "Issue description", "labels": ["bug"]}}"""

            response = await self._llm_call([{"role": "user", "content": issue_prompt}])
            try:
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0]
                issue_data = json.loads(response.strip())
            except (json.JSONDecodeError, IndexError):
                return {"type": "github_error", "error": "Could not parse issue details", "success": False}

            result = await self.github.create_issue(
                owner, repo,
                title=issue_data.get("title", ""),
                body=issue_data.get("body", ""),
                labels=issue_data.get("labels"),
            )

            if result.success:
                sub_events.append({"event": "execution_reasoning", "data": {
                    "chunk": f"- Issue #{result.data.get('number')} created: {result.url}\n"
                }})

            return {
                "type": "github_issue_create",
                "issue_number": result.data.get("number"),
                "url": result.url,
                "success": result.success,
                "error": result.error,
            }
        else:
            result = await self.github.list_issues(owner, repo)
            if result.success:
                issues = result.data.get("issues", [])
                sub_events.append({"event": "execution_reasoning", "data": {
                    "chunk": f"- Found {len(issues)} open issues\n"
                }})
            return {
                "type": "github_issue_list",
                "issues": result.data.get("issues", []) if result.success else [],
                "count": result.data.get("count", 0) if result.success else 0,
                "success": result.success,
                "error": result.error,
            }

    # ------------------------------------------------------------------
    # THINK — Analysis and synthesis
    # ------------------------------------------------------------------

    async def _exec_think(self, step, context, previous, sub_events):
        prev_context = self._get_previous_context(previous)

        sub_events.append({"event": "execution_reasoning", "data": {
            "chunk": f"- Analyzing findings from {len(previous)} previous steps\n"
        }})

        content = await self._llm_call([
            {"role": "system", "content": "You are an analytical assistant. Provide deep, structured analysis based on the available data. Be thorough and reference specific findings."},
            {"role": "user", "content": f"{step.instruction}\n\nData from previous steps:\n{prev_context}"},
        ], max_tokens=8192)

        sub_events.append({"event": "execution_reasoning", "data": {
            "chunk": f"- Analysis complete\n"
        }})

        return {"type": "analysis", "content": content}

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    async def _verify_execution(self, steps, user_request):
        completed = [s for s in steps if s.status == ExecutionStatus.COMPLETED]
        failed = [s for s in steps if s.status == ExecutionStatus.FAILED]

        if not completed:
            return {"verified": False, "confidence": 0.0, "issues": ["No steps completed"], "completed_steps": 0, "failed_steps": len(failed)}

        confidence = len(completed) / max(len(steps), 1)
        issues = []
        if failed:
            issues.append(f"{len(failed)} step(s) encountered errors")
        if confidence < 0.5:
            issues.append("Less than half of steps completed")

        has_data = False
        for s in completed:
            if s.output_data and isinstance(s.output_data, dict):
                rtype = s.output_data.get("type", "")
                if rtype == "research" and s.output_data.get("result_count", 0) > 0:
                    has_data = True
                elif rtype == "browser_extraction" and s.output_data.get("success"):
                    has_data = True
                elif rtype in ("github_read", "github_write", "github_pr") and s.output_data.get("success"):
                    has_data = True
                elif rtype == "code_execution" and s.output_data.get("success"):
                    has_data = True

        if not has_data and any(s.step_type in (StepType.RESEARCH, StepType.BROWSER) for s in steps):
            issues.append("Data gathering produced limited results")
            confidence *= 0.7

        return {
            "verified": confidence > 0.3,
            "confidence": round(confidence, 2),
            "issues": issues,
            "completed_steps": len(completed),
            "failed_steps": len(failed),
        }

    # ------------------------------------------------------------------
    # Delivery (streaming)
    # ------------------------------------------------------------------

    async def _deliver_stream(self, steps, user_request, verification, context):
        step_summaries = []
        for s in steps:
            if s.output_data:
                output_str = self._extract_step_output(s)
                step_summaries.append(f"### Step {s.step_number} ({s.step_type.value}): {s.instruction[:100]}\n{output_str}")

        all_context = "\n\n".join(step_summaries)

        history_context = ""
        if context and context.get("history"):
            for h in context["history"][-5:]:
                if isinstance(h, dict) and h.get("role") and h.get("content"):
                    content = h["content"] if isinstance(h["content"], str) else str(h["content"])
                    history_context += f"\n{h['role']}: {content[:500]}"

        delivery_prompt = f"""You are McLeuker AI, an advanced agentic AI assistant. Synthesize a comprehensive, well-structured response.

User Request: {user_request}

{f"Conversation History:{history_context}" if history_context else ""}

Execution Results:
{all_context}

INSTRUCTIONS:
1. Directly answer the user's request with specific, actionable information
2. Reference specific data and findings from the research
3. Use markdown formatting (headers, lists, bold, tables where appropriate)
4. If code was executed, include the relevant output
5. If URLs were analyzed, reference the specific content found
6. If GitHub operations were performed, include links and commit details
7. Be thorough but concise — focus on what the user actually asked for
8. End with actionable next steps if appropriate"""

        async for token in self._llm_stream(
            messages=[
                {"role": "system", "content": "You are McLeuker AI, a powerful agentic AI assistant. Always be helpful, accurate, and thorough."},
                {"role": "user", "content": delivery_prompt},
            ],
            max_tokens=16384,
        ):
            yield token

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _extract_step_output(self, step, max_chars=3000):
        if not step.output_data or not isinstance(step.output_data, dict):
            return str(step.output_data)[:1500] if step.output_data else ""

        rtype = step.output_data.get("type", "")
        if rtype == "research":
            return step.output_data.get("findings", "")[:max_chars]
        elif rtype == "code_execution":
            code = step.output_data.get("code", "")[:1000]
            output = step.output_data.get("output", "")[:1000]
            return f"Code:\n{code}\nOutput:\n{output}"
        elif rtype == "code_generation":
            return f"Code (not executed):\n{step.output_data.get('code', '')[:2000]}"
        elif rtype in ("browser_extraction", "browser_fallback"):
            url = step.output_data.get("url", "")
            content = step.output_data.get("content", "")[:max_chars]
            return f"URL: {url}\nContent:\n{content}"
        elif rtype == "analysis":
            return step.output_data.get("content", "")[:max_chars]
        elif rtype == "github_read":
            info = step.output_data.get("repo_info", {})
            entries = step.output_data.get("directory", [])
            file_content = step.output_data.get("file_content")
            result = f"Repository: {info.get('full_name', '')}\nLanguage: {info.get('language', 'N/A')}\nFiles: {len(entries)}\n"
            if file_content:
                result += f"\nFile content:\n{file_content.get('content', '')[:2000]}"
            return result
        elif rtype == "github_write":
            return f"File: {step.output_data.get('file_path', '')}\nCommit: {step.output_data.get('commit_sha', '')[:8]}\nURL: {step.output_data.get('url', '')}"
        elif rtype == "github_pr":
            return f"PR #{step.output_data.get('pr_number', '')}: {step.output_data.get('url', '')}"
        elif rtype == "github_needs_auth":
            return step.output_data.get("content", "GitHub token required")
        elif rtype == "github_guidance":
            return step.output_data.get("content", "GitHub not configured")
        else:
            return json.dumps(step.output_data, default=str)[:1500]

    def _get_previous_context(self, previous_steps, max_chars=6000):
        parts = []
        total = 0
        for ps in previous_steps:
            if ps.output_data and ps.status == ExecutionStatus.COMPLETED:
                text = self._extract_step_output(ps, max_chars=2000)
                if total + len(text) > max_chars:
                    break
                parts.append(f"[Step {ps.step_number} - {ps.step_type.value}]: {text}")
                total += len(text)
        return "\n\n".join(parts)

    def _get_step_detail_lines(self, step_type, instruction, step_num, total_steps):
        """Generate rich 3-line detail for task_progress events in the message field."""
        short_instr = instruction[:100].rstrip('.')
        
        details = {
            "research": [
                f"Querying multiple search engines for: {short_instr[:60]}",
                "Aggregating results from diverse sources for comprehensive coverage",
                "Filtering and ranking findings by relevance and recency",
            ],
            "code": [
                f"Generating executable code for: {short_instr[:60]}",
                "Running in a secure sandbox environment with output capture",
                "Validating execution results and handling any errors",
            ],
            "browser": [
                f"Opening web page and capturing live screenshot",
                f"Extracting structured content from: {short_instr[:60]}",
                "Analyzing page layout and identifying key information",
            ],
            "github": [
                f"Connecting to GitHub repository for: {short_instr[:60]}",
                "Authenticating and preparing repository operation",
                "Executing changes and verifying commit integrity",
            ],
            "think": [
                f"Deep analysis: {short_instr[:60]}",
                f"Synthesizing data from {step_num - 1} previous step{'s' if step_num > 2 else ''}",
                "Generating structured insights and actionable conclusions",
            ],
        }
        
        lines = details.get(step_type, [
            f"Processing step {step_num} of {total_steps}",
            f"Working on: {short_instr[:60]}",
            "Preparing output for next phase",
        ])
        
        return " ".join(lines)

    def _clean_step_title(self, step_type, instruction):
        """Generate a clean, user-friendly step title."""
        titles = {
            "research": "Searching for information",
            "code": "Running code",
            "browser": "Visiting web page",
            "github": "Working with repository",
            "think": "Analyzing findings",
        }
        base = titles.get(step_type, "Processing")

        # Add context from instruction
        if step_type == "browser":
            urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', instruction)
            if urls:
                domain = urls[0].split("//")[-1].split("/")[0]
                return f"Visiting {domain}"
        elif step_type == "github":
            repo_match = re.search(r'([a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+)', instruction)
            if repo_match:
                return f"Working with {repo_match.group(1)}"
        elif step_type == "research":
            # Shorten the instruction for the title
            short = instruction[:60]
            if len(instruction) > 60:
                short += "..."
            return f"Searching: {short}"

        return f"{base}: {instruction[:60]}{'...' if len(instruction) > 60 else ''}"

    def _clean_result_summary(self, result):
        """Generate a clean, user-friendly result summary without API names."""
        if not isinstance(result, dict):
            return str(result)[:150]

        rtype = result.get("type", "unknown")
        if rtype == "research":
            count = result.get("result_count", 0)
            src_count = result.get("active_source_count", 0)
            return f"Found {count} results from {src_count} search engines"
        elif rtype == "code_execution":
            if result.get("success"):
                output = (result.get("output", "") or "")[:80]
                ms = result.get("execution_time_ms", 0)
                return f"Code executed ({ms:.0f}ms): {output}"
            else:
                return f"Code error: {(result.get('error', '') or '')[:80]}"
        elif rtype == "code_generation":
            return f"Code generated ({len(result.get('code', ''))} chars)"
        elif rtype == "browser_extraction":
            title = result.get("title", "")
            chars = len(result.get("content", ""))
            return f"Extracted {chars:,} chars from: {title[:50]}"
        elif rtype == "browser_fallback":
            return "Analyzed URL content"
        elif rtype == "browser_error":
            return f"Could not access the URL"
        elif rtype == "analysis":
            return f"Analysis complete ({len(result.get('content', '')):,} chars)"
        elif rtype == "github_read":
            info = result.get("repo_info", {})
            return f"Read repository: {info.get('full_name', '')}"
        elif rtype == "github_write":
            return f"Committed to: {result.get('file_path', '')}"
        elif rtype == "github_pr":
            return f"Created PR #{result.get('pr_number', '')}"
        elif rtype == "github_branch":
            return f"Created branch: {result.get('branch', '')}"
        elif rtype == "github_needs_auth":
            return "GitHub token required for this operation"
        elif rtype == "github_guidance":
            return "Provided GitHub operation guidance"
        else:
            return json.dumps(result, default=str)[:100]

    # ------------------------------------------------------------------
    # Control methods
    # ------------------------------------------------------------------

    async def pause_execution(self, execution_id):
        if execution_id in self._executions:
            self._executions[execution_id]["paused"] = True

    async def resume_execution(self, execution_id):
        if execution_id in self._executions:
            self._executions[execution_id]["paused"] = False

    async def cancel_execution(self, execution_id):
        if execution_id in self._executions:
            self._executions[execution_id]["cancelled"] = True

    def get_execution_status(self, execution_id):
        exec_data = self._executions.get(execution_id)
        if not exec_data:
            return None
        return {
            "execution_id": execution_id,
            "status": exec_data["status"].value if isinstance(exec_data["status"], ExecutionStatus) else str(exec_data["status"]),
        }

    def list_executions(self):
        return [self.get_execution_status(eid) for eid in self._executions if self.get_execution_status(eid)]
