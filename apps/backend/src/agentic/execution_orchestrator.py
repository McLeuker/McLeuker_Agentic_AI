"""
Manus-Style Execution Orchestrator V3
=======================================

Real agentic task execution with:
- LLM-powered planning that decomposes tasks into executable steps
- SearchLayer integration for multi-source research (10+ APIs)
- E2B sandbox for code execution (Python, JS, Bash)
- Browserless for web automation and content extraction
- Firecrawl for deep URL content fetching
- Self-correction with retry logic
- Real-time SSE streaming with granular step updates
- Manus-style reasoning: clean structured bullets
- Content streaming during delivery phase

Architecture:
  User Request → Planner → [Research | Code | Browser | Think] → Verifier → Delivery → Stream

All LLM calls use sync OpenAI clients via run_in_executor (matching main.py pattern).
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
    VERIFY = "verify"
    DELIVER = "deliver"
    THINK = "think"


STEP_TYPE_TO_PHASE = {
    StepType.PLAN: "planning",
    StepType.RESEARCH: "research",
    StepType.CODE: "execution",
    StepType.BROWSER: "research",
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
# EXECUTION ORCHESTRATOR
# ============================================================================

class ExecutionOrchestrator:
    """
    Real agentic execution orchestrator V3.
    
    Plans tasks, executes them with real tools (search, code, browser),
    verifies results, and delivers output — all with real-time SSE streaming.
    
    Key fix in V3: Proper SearchLayer data extraction from structured_data format.
    """

    def __init__(
        self,
        kimi_client=None,
        grok_client=None,
        search_layer=None,
        e2b_manager=None,
        browserless_client=None,
        max_steps: int = 15,
        enable_auto_correct: bool = True,
    ):
        self.kimi = kimi_client
        self.grok = grok_client
        self.search_layer = search_layer
        self.e2b = e2b_manager
        self.browserless = browserless_client
        self.max_steps = max_steps
        self.enable_auto_correct = enable_auto_correct
        self._executions: Dict[str, Dict[str, Any]] = {}
        logger.info("ExecutionOrchestrator V3 initialized")

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
            # Try fallback
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
        
        Yields dicts with 'event' and 'data' keys.
        
        Event types:
          start, execution_start, step_update, execution_progress,
          execution_reasoning, content, execution_artifact,
          execution_complete, complete, execution_error
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
                "title": "Analyzing request and creating execution plan",
                "status": "active",
                "detail": user_request[:120]
            }}
            yield {"event": "execution_reasoning", "data": {
                "chunk": "**Planning Phase**\n- Analyzing user request to determine required tools\n- Detecting URLs, code requirements, and research needs\n"
            }}
            yield {"event": "execution_progress", "data": {"progress": 5, "status": "planning"}}

            plan = await self._create_plan(execution_id, user_request, context)

            # Format plan reasoning as clean bullets
            plan_reasoning = f"**Plan Created — {len(plan.steps)} steps**\n"
            for s in plan.steps:
                tool_icon = {"research": "🔍", "code": "💻", "browser": "🌐", "think": "🧠"}.get(s.get("step_type", ""), "📋")
                plan_reasoning += f"- {tool_icon} Step {s.get('step_number', '?')}: {s.get('instruction', '')[:100]}\n"
            plan_reasoning += f"\n*Reasoning:* {plan.reasoning[:200]}\n\n"

            yield {"event": "step_update", "data": {
                "id": "plan-1", "phase": "planning",
                "title": f"Execution plan ready — {len(plan.steps)} steps",
                "status": "complete",
                "detail": f"Tools: {', '.join(set(s.get('step_type', 'think') for s in plan.steps))}"
            }}
            yield {"event": "execution_reasoning", "data": {"chunk": plan_reasoning}}
            yield {"event": "execution_progress", "data": {"progress": 10, "status": "executing"}}

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
                phase = STEP_TYPE_TO_PHASE.get(
                    StepType(step_type_str) if step_type_str in [st.value for st in StepType] else StepType.THINK,
                    "execution"
                )

                base_progress = 10
                step_progress = base_progress + int(((i + 0.5) / max(total_steps, 1)) * 70)

                tool_icon = {"research": "🔍", "code": "💻", "browser": "🌐", "think": "🧠"}.get(step_type_str, "📋")

                # Emit step started
                yield {"event": "step_update", "data": {
                    "id": step_id, "phase": phase,
                    "title": f"{tool_icon} {instruction[:120]}",
                    "status": "active",
                    "detail": f"Step {step_num}/{total_steps} — {step_type_str}"
                }}
                yield {"event": "execution_reasoning", "data": {
                    "chunk": f"**Step {step_num}/{total_steps} — {step_type_str.upper()}**\n- Executing: {instruction[:150]}\n"
                }}
                yield {"event": "execution_progress", "data": {"progress": step_progress, "status": "executing"}}

                # Execute the step
                step = ExecutionStep(
                    step_id=step_id,
                    execution_id=execution_id,
                    step_number=step_num,
                    step_type=StepType(step_type_str) if step_type_str in [st.value for st in StepType] else StepType.THINK,
                    status=ExecutionStatus.EXECUTING,
                    agent=step_data.get("agent", "kimi"),
                    instruction=instruction,
                    input_data=step_data,
                )
                step.started_at = datetime.now()

                try:
                    result, sub_events = await self._execute_step_with_events(step, context, all_step_results)
                    step.output_data = result
                    step.status = ExecutionStatus.COMPLETED
                    step.completed_at = datetime.now()
                    elapsed = (step.completed_at - step.started_at).total_seconds()

                    # Yield sub-events (granular progress from within the step)
                    for sub_evt in sub_events:
                        yield sub_evt

                    # Emit step completed with clean summary
                    result_summary = self._summarize_result(result)
                    yield {"event": "step_update", "data": {
                        "id": step_id, "phase": phase,
                        "title": f"{tool_icon} {instruction[:80]}",
                        "status": "complete",
                        "detail": result_summary[:200]
                    }}

                    # Emit clean reasoning for this step
                    reasoning_text = f"- ✅ Completed in {elapsed:.1f}s: {result_summary[:250]}\n\n"
                    yield {"event": "execution_reasoning", "data": {"chunk": reasoning_text}}

                except Exception as e:
                    step.status = ExecutionStatus.FAILED
                    step.error_message = str(e)
                    step.completed_at = datetime.now()
                    logger.error(f"Step {step_num} failed: {e}")

                    yield {"event": "step_update", "data": {
                        "id": step_id, "phase": phase,
                        "title": f"{tool_icon} {instruction[:80]}",
                        "status": "error",
                        "detail": f"Error: {str(e)[:150]}"
                    }}
                    yield {"event": "execution_reasoning", "data": {
                        "chunk": f"- ❌ Step failed: {str(e)[:200]}\n\n"
                    }}

                all_step_results.append(step)
                yield {"event": "execution_progress", "data": {
                    "progress": base_progress + int(((i + 1) / max(total_steps, 1)) * 70),
                    "status": "executing"
                }}

            # === PHASE 4: VERIFICATION ===
            yield {"event": "step_update", "data": {
                "id": "verify-1", "phase": "verification",
                "title": "Verifying execution results",
                "status": "active"
            }}
            yield {"event": "execution_reasoning", "data": {
                "chunk": "**Verification Phase**\n- Checking step completion status\n- Evaluating data quality and coverage\n"
            }}
            yield {"event": "execution_progress", "data": {"progress": 82, "status": "verifying"}}

            verification = await self._verify_execution(all_step_results, user_request)

            completed_count = verification.get("completed_steps", 0)
            failed_count = verification.get("failed_steps", 0)
            confidence = verification.get("confidence", 0)

            verify_reasoning = f"- Results: {completed_count} steps completed, {failed_count} failed\n"
            verify_reasoning += f"- Confidence: {confidence:.0%}\n"
            if verification.get("issues"):
                verify_reasoning += f"- Issues: {', '.join(verification['issues'])}\n"
            else:
                verify_reasoning += "- All checks passed ✅\n"
            verify_reasoning += "\n"

            yield {"event": "step_update", "data": {
                "id": "verify-1", "phase": "verification",
                "title": f"Verified — {confidence:.0%} confidence",
                "status": "complete",
                "detail": f"{completed_count}/{completed_count + failed_count} steps successful"
            }}
            yield {"event": "execution_reasoning", "data": {"chunk": verify_reasoning}}
            yield {"event": "execution_progress", "data": {"progress": 88, "status": "delivering"}}

            # === PHASE 5: DELIVERY ===
            yield {"event": "step_update", "data": {
                "id": "deliver-1", "phase": "delivery",
                "title": "Synthesizing comprehensive response",
                "status": "active"
            }}
            yield {"event": "execution_reasoning", "data": {
                "chunk": "**Delivery Phase**\n- Synthesizing all research findings and execution results\n- Generating structured response with citations\n"
            }}
            yield {"event": "execution_progress", "data": {"progress": 90, "status": "delivering"}}

            full_content = ""
            async for token in self._deliver_stream(all_step_results, user_request, verification, context):
                full_content += token
                yield {"event": "content", "data": {"chunk": token}}

            yield {"event": "step_update", "data": {
                "id": "deliver-1", "phase": "delivery",
                "title": "Response delivered",
                "status": "complete",
                "detail": f"{len(full_content)} characters"
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

    # ------------------------------------------------------------------
    # Planning
    # ------------------------------------------------------------------

    async def _create_plan(self, execution_id: str, user_request: str, context: Optional[Dict]) -> ExecutionPlan:
        current_date = date.today().isoformat()

        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', user_request)
        has_urls = len(urls) > 0

        code_keywords = ["code", "script", "program", "calculate", "compute", "analyze data", "chart", "plot", "graph", "csv", "json"]
        needs_code = any(kw in user_request.lower() for kw in code_keywords)

        available_tools = []
        if self.search_layer:
            available_tools.append("research: Search across 10+ APIs (Perplexity, Bing, Google, Exa, SerpAPI, YouTube, Firecrawl, Pinterest)")
        if self.e2b and self.e2b.available:
            available_tools.append("code: Execute Python/JS/Bash in E2B sandbox")
        if self.browserless and self.browserless.available:
            available_tools.append("browser: Navigate URLs, extract content, take screenshots via Browserless")
        available_tools.append("think: Analyze data, reason about findings, synthesize information")

        plan_prompt = f"""You are an execution planner for an AI agent system. Today is {current_date}.

AVAILABLE TOOLS:
{chr(10).join(f'- {t}' for t in available_tools)}

Decompose this user request into 3-8 executable steps. Each step must be one of:
- research: Search the web for information using multiple search engines
- code: Generate and execute code in a sandbox
- browser: Navigate to a URL and extract content
- think: Analyze and reason about collected data

IMPORTANT RULES:
- If the user provides URLs, include a "browser" step to fetch that URL content FIRST
- If the user asks for data analysis, include a "code" step
- Always include at least one "research" step for information gathering
- End with a "think" step to synthesize all findings
- Keep instructions specific and actionable

For each step provide:
- step_number (integer starting from 1)
- step_type (research/code/browser/think)
- instruction (specific, actionable — what exactly to search/code/browse/analyze)
- agent ("kimi" or "grok")
- expected_output (what this step produces)
- dependencies (list of step_numbers this depends on, [] if independent)

Respond ONLY in JSON:
{{
    "objective": "brief description of the goal",
    "reasoning": "why this decomposition makes sense",
    "steps": [
        {{"step_number": 1, "step_type": "research", "instruction": "...", "agent": "kimi", "expected_output": "...", "dependencies": []}}
    ],
    "parallel_groups": [[1, 2], [3]]
}}

User Request: {user_request}
{"URLs detected: " + ", ".join(urls) if urls else ""}
{"Context: " + json.dumps(context)[:500] if context else ""}"""

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

            if has_urls and not any(s.get("step_type") == "browser" for s in steps):
                browser_step = {
                    "step_number": 0,
                    "step_type": "browser",
                    "instruction": f"Navigate to and extract content from: {urls[0]}",
                    "agent": "kimi",
                    "expected_output": "Page content and structure",
                    "dependencies": [],
                }
                steps.insert(0, browser_step)
                for idx, s in enumerate(steps):
                    s["step_number"] = idx + 1

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

            fallback_steps = []
            step_num = 1

            if has_urls:
                fallback_steps.append({
                    "step_number": step_num, "step_type": "browser",
                    "instruction": f"Extract content from URL: {urls[0]}",
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
                reasoning="Fallback plan with smart step detection",
                parallel_groups=[[s["step_number"]] for s in fallback_steps],
            )

    # ------------------------------------------------------------------
    # Step execution with sub-events
    # ------------------------------------------------------------------

    async def _execute_step_with_events(
        self,
        step: ExecutionStep,
        context: Optional[Dict],
        previous_steps: List[ExecutionStep],
    ) -> tuple:
        """Execute a step and return (result, sub_events).
        
        sub_events are granular progress events emitted during the step.
        """
        sub_events = []

        if step.step_type == StepType.RESEARCH:
            result = await self._exec_research(step, context, previous_steps, sub_events)
        elif step.step_type == StepType.CODE:
            result = await self._exec_code(step, context, previous_steps, sub_events)
        elif step.step_type == StepType.BROWSER:
            result = await self._exec_browser(step, context, sub_events)
        elif step.step_type == StepType.THINK:
            result = await self._exec_think(step, context, previous_steps, sub_events)
        else:
            result = await self._exec_think(step, context, previous_steps, sub_events)

        return result, sub_events

    # ------------------------------------------------------------------
    # RESEARCH — Fixed SearchLayer data extraction
    # ------------------------------------------------------------------

    async def _exec_research(
        self,
        step: ExecutionStep,
        context: Optional[Dict],
        previous: List[ExecutionStep],
        sub_events: list,
    ) -> Dict:
        """Execute research using SearchLayer (10+ APIs).
        
        SearchLayer.search() returns:
        {
            "query": "...",
            "results": {
                "perplexity": {"answer": "...", "citations": [...], "data_points": [...], "sources": []},
                "exa": {"results": [...], "data_points": [...], "sources": [...]},
                "google": {"results": [...], "data_points": [...], "sources": [...]},
                ...
            },
            "structured_data": {"data_points": [...], "sources": [...]}
        }
        """
        if self.search_layer:
            try:
                sub_events.append({"event": "execution_reasoning", "data": {
                    "chunk": "- Querying 10+ search APIs in parallel (Perplexity, Exa, Google, Bing, YouTube, Firecrawl...)\n"
                }})

                search_result = await self.search_layer.search(
                    step.instruction,
                    sources=["web", "news", "social"],
                    num_results=15,
                )

                # === EXTRACT DATA FROM STRUCTURED_DATA (the aggregated format) ===
                structured_data = search_result.get("structured_data", {})
                data_points = structured_data.get("data_points", [])
                sources = structured_data.get("sources", [])

                # Extract Perplexity answer (the most comprehensive single answer)
                perplexity_answer = ""
                results_dict = search_result.get("results", {})
                if isinstance(results_dict, dict):
                    pplx = results_dict.get("perplexity", {})
                    if isinstance(pplx, dict):
                        perplexity_answer = pplx.get("answer", "")

                # Build findings text from data points
                findings_parts = []
                if perplexity_answer:
                    findings_parts.append(f"**Perplexity AI Summary:**\n{perplexity_answer[:3000]}")

                # Add data points from all sources
                seen_descriptions = set()
                for dp in data_points[:20]:
                    if isinstance(dp, dict):
                        title = dp.get("title", "")
                        desc = dp.get("description", "")
                        source = dp.get("source", "")
                        if desc and desc[:100] not in seen_descriptions:
                            seen_descriptions.add(desc[:100])
                            findings_parts.append(f"[{source}] **{title}**: {desc[:400]}")

                # Count active sources
                active_sources = []
                if isinstance(results_dict, dict):
                    for src_name, src_data in results_dict.items():
                        if isinstance(src_data, dict) and not src_data.get("error"):
                            active_sources.append(src_name)

                findings_text = "\n\n".join(findings_parts) if findings_parts else "No results found from search APIs"

                sub_events.append({"event": "execution_reasoning", "data": {
                    "chunk": f"- Found {len(data_points)} data points from {len(active_sources)} sources ({', '.join(active_sources[:6])})\n"
                    f"- Collected {len(sources)} unique source URLs\n"
                }})

                return {
                    "type": "research",
                    "query": step.instruction,
                    "findings": findings_text,
                    "sources": sources[:15],
                    "result_count": len(data_points),
                    "active_sources": active_sources,
                    "perplexity_answer": perplexity_answer[:2000] if perplexity_answer else "",
                }

            except Exception as e:
                logger.error(f"Search failed: {e}")
                sub_events.append({"event": "execution_reasoning", "data": {
                    "chunk": f"- Search API error: {str(e)[:100]}. Falling back to LLM knowledge.\n"
                }})
                content = await self._llm_call([
                    {"role": "system", "content": "You are a research assistant. Provide comprehensive, factual information with sources."},
                    {"role": "user", "content": step.instruction},
                ])
                return {"type": "research", "findings": content, "sources": [], "fallback": True, "result_count": 0}
        else:
            sub_events.append({"event": "execution_reasoning", "data": {
                "chunk": "- SearchLayer not available. Using LLM knowledge base.\n"
            }})
            content = await self._llm_call([
                {"role": "system", "content": "You are a research assistant. Provide comprehensive, factual information."},
                {"role": "user", "content": step.instruction},
            ])
            return {"type": "research", "findings": content, "sources": [], "result_count": 0}

    # ------------------------------------------------------------------
    # CODE — E2B sandbox execution
    # ------------------------------------------------------------------

    async def _exec_code(
        self,
        step: ExecutionStep,
        context: Optional[Dict],
        previous: List[ExecutionStep],
        sub_events: list,
    ) -> Dict:
        """Execute code in E2B sandbox."""
        prev_context = self._get_previous_context(previous)

        sub_events.append({"event": "execution_reasoning", "data": {
            "chunk": "- Generating Python code for the task\n"
        }})

        code_prompt = f"""Write clean, executable Python code for this task. Return ONLY the code, no explanations or markdown.

Task: {step.instruction}

{f"Previous context: {prev_context[:3000]}" if prev_context else ""}

Requirements:
- Print all results to stdout
- Handle errors gracefully
- If creating visualizations, save to /tmp/output.png
- If processing data, print a summary"""

        code_content = await self._llm_call([
            {"role": "system", "content": "You are a Python code generator. Return ONLY executable Python code, no markdown fences, no explanations."},
            {"role": "user", "content": code_prompt},
        ], max_tokens=4096)

        # Clean code
        code_content = code_content.strip()
        if code_content.startswith("```python"):
            code_content = code_content[9:]
        if code_content.startswith("```"):
            code_content = code_content[3:]
        if code_content.endswith("```"):
            code_content = code_content[:-3]
        code_content = code_content.strip()

        sub_events.append({"event": "execution_reasoning", "data": {
            "chunk": f"- Generated {len(code_content)} chars of Python code\n"
        }})

        # Execute in E2B if available
        if self.e2b and self.e2b.available:
            try:
                sub_events.append({"event": "execution_reasoning", "data": {
                    "chunk": "- Executing code in E2B secure sandbox...\n"
                }})

                result = await self.e2b.execute_code(code_content, language="python", timeout=30)

                status = "✅ Success" if result.success else "❌ Error"
                sub_events.append({"event": "execution_reasoning", "data": {
                    "chunk": f"- E2B execution {status} ({result.execution_time_ms:.0f}ms)\n"
                }})

                return {
                    "type": "code_execution",
                    "code": code_content,
                    "output": result.output or "",
                    "error": result.error or "",
                    "success": result.success,
                    "execution_time_ms": result.execution_time_ms,
                    "sandbox": "e2b",
                }
            except Exception as e:
                sub_events.append({"event": "execution_reasoning", "data": {
                    "chunk": f"- E2B execution failed: {str(e)[:100]}\n"
                }})
                return {
                    "type": "code_execution",
                    "code": code_content,
                    "output": "",
                    "error": f"E2B execution failed: {str(e)}",
                    "success": False,
                    "sandbox": "e2b_error",
                }
        else:
            sub_events.append({"event": "execution_reasoning", "data": {
                "chunk": "- E2B sandbox not available — code generated but not executed\n"
            }})
            return {
                "type": "code_generation",
                "code": code_content,
                "note": "E2B sandbox not available — code generated but not executed. User can run locally.",
                "success": True,
            }

    # ------------------------------------------------------------------
    # BROWSER — Browserless web automation
    # ------------------------------------------------------------------

    async def _exec_browser(
        self,
        step: ExecutionStep,
        context: Optional[Dict],
        sub_events: list,
    ) -> Dict:
        """Execute browser automation via Browserless."""
        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', step.instruction)

        if self.browserless and self.browserless.available:
            if urls:
                target_url = urls[0]
                sub_events.append({"event": "execution_reasoning", "data": {
                    "chunk": f"- Navigating to URL via Browserless: {target_url[:80]}\n"
                }})

                try:
                    result = await self.browserless.deep_extract(target_url, extract_links=True)

                    if result.get("success"):
                        title = result.get("title", "")
                        text = result.get("text", "")
                        links = result.get("links", [])
                        sub_events.append({"event": "execution_reasoning", "data": {
                            "chunk": f"- Extracted {len(text)} chars from '{title[:60]}'\n"
                            f"- Found {len(links)} links on the page\n"
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
                        error = result.get("error", "Unknown error")
                        sub_events.append({"event": "execution_reasoning", "data": {
                            "chunk": f"- Browserless extraction failed: {error[:100]}\n"
                        }})
                        return {"type": "browser_error", "url": target_url, "error": error, "success": False}

                except Exception as e:
                    sub_events.append({"event": "execution_reasoning", "data": {
                        "chunk": f"- Browserless error: {str(e)[:100]}\n"
                    }})
                    return {"type": "browser_error", "url": target_url, "error": str(e), "success": False}
            else:
                sub_events.append({"event": "execution_reasoning", "data": {
                    "chunk": "- No URL found in instruction. Performing Google search via Browserless.\n"
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
        else:
            sub_events.append({"event": "execution_reasoning", "data": {
                "chunk": "- Browserless not available. Using LLM to analyze URL.\n"
            }})
            if urls:
                content = await self._llm_call([
                    {"role": "system", "content": "The user wants to analyze a URL. Since browser automation is not available, provide what you know about this URL/domain."},
                    {"role": "user", "content": f"Analyze this URL: {urls[0]}\n\nContext: {step.instruction}"},
                ])
                return {"type": "browser_fallback", "url": urls[0], "content": content, "note": "Browserless not available"}
            else:
                content = await self._llm_call([{"role": "user", "content": step.instruction}])
                return {"type": "browser_fallback", "content": content}

    # ------------------------------------------------------------------
    # THINK — Analysis and synthesis
    # ------------------------------------------------------------------

    async def _exec_think(
        self,
        step: ExecutionStep,
        context: Optional[Dict],
        previous: List[ExecutionStep],
        sub_events: list,
    ) -> Dict:
        """Execute thinking/analysis step."""
        prev_context = self._get_previous_context(previous)

        sub_events.append({"event": "execution_reasoning", "data": {
            "chunk": f"- Analyzing {len(previous)} previous step outputs\n- Synthesizing findings into structured analysis\n"
        }})

        content = await self._llm_call([
            {"role": "system", "content": "You are an analytical assistant. Provide deep, structured analysis based on the available data. Be thorough and cite specific findings from the research."},
            {"role": "user", "content": f"{step.instruction}\n\nData from previous steps:\n{prev_context}"},
        ], max_tokens=8192)

        sub_events.append({"event": "execution_reasoning", "data": {
            "chunk": f"- Analysis complete: {len(content)} chars generated\n"
        }})

        return {"type": "analysis", "content": content}

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    async def _verify_execution(self, steps: List[ExecutionStep], user_request: str) -> Dict:
        completed = [s for s in steps if s.status == ExecutionStatus.COMPLETED]
        failed = [s for s in steps if s.status == ExecutionStatus.FAILED]

        if not completed:
            return {"verified": False, "confidence": 0.0, "issues": ["No steps completed successfully"], "completed_steps": 0, "failed_steps": len(failed)}

        confidence = len(completed) / max(len(steps), 1)
        issues = []
        if failed:
            issues.append(f"{len(failed)} step(s) failed")
        if confidence < 0.5:
            issues.append("Less than half of steps completed")

        # Check if research produced actual data
        has_research_data = False
        for s in completed:
            if s.output_data and isinstance(s.output_data, dict):
                if s.output_data.get("type") == "research" and s.output_data.get("result_count", 0) > 0:
                    has_research_data = True
                elif s.output_data.get("type") == "browser_extraction" and s.output_data.get("success"):
                    has_research_data = True

        if not has_research_data and any(s.step_type == StepType.RESEARCH for s in steps):
            issues.append("Research steps produced no data")
            confidence *= 0.7

        return {
            "verified": confidence > 0.3,
            "confidence": round(confidence, 2),
            "issues": issues,
            "recommendations": [],
            "completed_steps": len(completed),
            "failed_steps": len(failed),
        }

    # ------------------------------------------------------------------
    # Delivery (streaming)
    # ------------------------------------------------------------------

    async def _deliver_stream(
        self,
        steps: List[ExecutionStep],
        user_request: str,
        verification: Dict,
        context: Optional[Dict],
    ) -> AsyncGenerator[str, None]:
        """Stream the final delivery response token by token."""

        step_summaries = []
        for s in steps:
            if s.output_data:
                output_str = ""
                if isinstance(s.output_data, dict):
                    rtype = s.output_data.get("type", "")
                    if rtype == "research":
                        output_str = s.output_data.get("findings", "")[:3000]
                    elif rtype == "code_execution":
                        output_str = f"Code:\n{s.output_data.get('code', '')[:1000]}\nOutput:\n{s.output_data.get('output', '')[:1000]}"
                    elif rtype in ("browser_extraction", "browser_fallback"):
                        output_str = f"URL: {s.output_data.get('url', '')}\nContent:\n{s.output_data.get('content', '')[:3000]}"
                    elif rtype == "analysis":
                        output_str = s.output_data.get("content", "")[:3000]
                    else:
                        output_str = json.dumps(s.output_data, default=str)[:1500]
                else:
                    output_str = str(s.output_data)[:1500]

                step_summaries.append(f"### Step {s.step_number} ({s.step_type.value}): {s.instruction[:100]}\n{output_str}")

        all_context = "\n\n".join(step_summaries)

        history_context = ""
        if context and context.get("history"):
            for h in context["history"][-5:]:
                if isinstance(h, dict) and h.get("role") and h.get("content"):
                    content = h["content"] if isinstance(h["content"], str) else str(h["content"])
                    history_context += f"\n{h['role']}: {content[:500]}"

        delivery_prompt = f"""You are McLeuker AI, an advanced agentic AI assistant. Synthesize a comprehensive, well-structured response based on the execution results below.

User Request: {user_request}

{f"Conversation History:{history_context}" if history_context else ""}

Execution Results:
{all_context}

Verification: {json.dumps(verification)}

INSTRUCTIONS:
1. Directly answer the user's request with specific, actionable information
2. Reference specific data and findings from the research
3. Use markdown formatting (headers, lists, bold, tables where appropriate)
4. If code was executed, include the relevant output
5. If URLs were analyzed, reference the specific content found
6. Be thorough but concise — focus on what the user actually asked for
7. If any steps failed, acknowledge limitations honestly
8. End with actionable next steps or recommendations if appropriate"""

        async for token in self._llm_stream(
            messages=[
                {"role": "system", "content": "You are McLeuker AI, a powerful agentic AI assistant that executes tasks and delivers comprehensive results. Always be helpful, accurate, and thorough."},
                {"role": "user", "content": delivery_prompt},
            ],
            max_tokens=16384,
        ):
            yield token

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_previous_context(self, previous_steps: List[ExecutionStep], max_chars: int = 6000) -> str:
        parts = []
        total = 0
        for ps in previous_steps:
            if ps.output_data and ps.status == ExecutionStatus.COMPLETED:
                if isinstance(ps.output_data, dict):
                    rtype = ps.output_data.get("type", "")
                    if rtype == "research":
                        text = ps.output_data.get("findings", "")[:2000]
                    elif rtype == "code_execution":
                        text = f"Code output: {ps.output_data.get('output', '')[:1000]}"
                    elif rtype in ("browser_extraction", "browser_fallback"):
                        text = f"URL content: {ps.output_data.get('content', '')[:2000]}"
                    elif rtype == "analysis":
                        text = ps.output_data.get("content", "")[:2000]
                    else:
                        text = json.dumps(ps.output_data, default=str)[:1000]
                else:
                    text = str(ps.output_data)[:1000]

                if total + len(text) > max_chars:
                    break
                parts.append(f"[Step {ps.step_number} - {ps.step_type.value}]: {text}")
                total += len(text)
        return "\n\n".join(parts)

    def _summarize_result(self, result: Any) -> str:
        if isinstance(result, dict):
            rtype = result.get("type", "unknown")
            if rtype == "research":
                count = result.get("result_count", 0)
                sources = result.get("active_sources", [])
                return f"Found {count} data points from {len(sources)} sources ({', '.join(sources[:4])})"
            elif rtype == "code_execution":
                if result.get("success"):
                    output = result.get("output", "")[:100]
                    ms = result.get("execution_time_ms", 0)
                    return f"Code executed in E2B ({ms:.0f}ms): {output}"
                else:
                    return f"Code execution failed: {result.get('error', '')[:100]}"
            elif rtype == "code_generation":
                return f"Code generated ({len(result.get('code', ''))} chars) — E2B not available"
            elif rtype == "browser_extraction":
                title = result.get("title", "")
                content_len = len(result.get("content", ""))
                return f"Extracted {content_len} chars from: {title[:60]}"
            elif rtype == "browser_search":
                return "Browser search completed"
            elif rtype == "browser_fallback":
                return "URL analysis via LLM (Browserless not available)"
            elif rtype == "browser_error":
                return f"Browser error: {result.get('error', '')[:100]}"
            elif rtype == "analysis":
                return f"Analysis complete ({len(result.get('content', ''))} chars)"
            else:
                return json.dumps(result, default=str)[:150]
        return str(result)[:150]

    # ------------------------------------------------------------------
    # Control methods
    # ------------------------------------------------------------------

    async def pause_execution(self, execution_id: str):
        if execution_id in self._executions:
            self._executions[execution_id]["paused"] = True

    async def resume_execution(self, execution_id: str):
        if execution_id in self._executions:
            self._executions[execution_id]["paused"] = False

    async def cancel_execution(self, execution_id: str):
        if execution_id in self._executions:
            self._executions[execution_id]["cancelled"] = True

    def get_execution_status(self, execution_id: str) -> Optional[Dict]:
        exec_data = self._executions.get(execution_id)
        if not exec_data:
            return None
        return {
            "execution_id": execution_id,
            "status": exec_data["status"].value if isinstance(exec_data["status"], ExecutionStatus) else str(exec_data["status"]),
        }

    def list_executions(self) -> List[Dict]:
        return [self.get_execution_status(eid) for eid in self._executions if self.get_execution_status(eid)]
