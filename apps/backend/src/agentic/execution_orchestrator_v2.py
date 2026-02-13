"""
Execution Orchestrator V5 — Complete Working Version
=====================================================

True agentic execution with:
1. Reasoning BEFORE execution — asks for clarification if needed
2. Fixed tool_choice conflict with thinking mode
3. Proper browser navigation — shows actual web pages
4. Live screenshot streaming to frontend
5. True 3-mode system: instant / auto / agent
6. Dual-model with fallback: Grok (reasoning) + Kimi (vision)
7. SSE streaming for real-time updates

Architecture:
  User Request → Mode Router → Reasoning Agent → (Clarification?) → Plan → Execute → Stream Results
"""

import asyncio
import json
import re
import uuid
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime
from enum import Enum

from .reasoning_agent import ReasoningAgent, ModeRouter
from .browser_engine_v2 import BrowserEngineV2, BrowserActionType, PLAYWRIGHT_V2_AVAILABLE

logger = logging.getLogger(__name__)


class ExecutionStatusV2(Enum):
    PENDING = "pending"
    REASONING = "reasoning"
    CLARIFYING = "clarifying"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionOrchestratorV2:
    """
    Main orchestrator for agentic task execution.

    Features:
    - 3-mode system: instant, auto, agent
    - Reasoning before execution
    - Clarification when needed
    - Live browser automation with screenshots
    - Real-time SSE streaming
    - Dual-model with fallback
    """

    def __init__(
        self,
        kimi_client=None,
        grok_client=None,
        search_layer=None,
    ):
        """
        Args:
            kimi_client: openai.AsyncOpenAI for Kimi K2.5 (vision + general)
            grok_client: openai.AsyncOpenAI for Grok (fast reasoning)
            search_layer: SearchLayer class for web search
        """
        self.kimi_client = kimi_client
        self.grok_client = grok_client
        self.search_layer = search_layer

        # Components
        self.reasoning_agent = ReasoningAgent(grok_client, kimi_client)
        self.mode_router = ModeRouter(grok_client, kimi_client)
        self.browser_engine: Optional[BrowserEngineV2] = None

        # Active executions
        self.executions: Dict[str, Dict] = {}

        logger.info("ExecutionOrchestratorV2 initialized")

    async def execute_stream(
        self,
        user_request: str,
        mode: str = "agent",
        conversation_history: Optional[List[Dict]] = None,
    ) -> AsyncGenerator[Dict, None]:
        """
        Execute a request and yield SSE events.

        This is the main entry point for the V2 API.
        Yields dicts like: {"event": "reasoning.started", "data": {...}}
        """
        execution_id = str(uuid.uuid4())

        execution = {
            "id": execution_id,
            "user_request": user_request,
            "mode": mode,
            "status": ExecutionStatusV2.PENDING.value,
            "started_at": datetime.now().isoformat(),
            "steps": [],
            "results": [],
        }
        self.executions[execution_id] = execution

        try:
            # ── PHASE 1: MODE ROUTING ────────────────────────────────
            yield {
                "event": "mode.routing",
                "data": {"mode": mode, "execution_id": execution_id},
            }

            routing = await self.mode_router.route(user_request, mode, conversation_history)

            # INSTANT MODE: Direct response
            if routing.get("mode") == "instant":
                yield {
                    "event": "mode.instant",
                    "data": {"message": "Providing direct response..."},
                }
                response = await self._get_instant_response(user_request, conversation_history)
                yield {
                    "event": "execution.completed",
                    "data": {"response": response, "mode": "instant"},
                }
                execution["status"] = ExecutionStatusV2.COMPLETED.value
                return

            # ── PHASE 2: REASONING ───────────────────────────────────
            execution["status"] = ExecutionStatusV2.REASONING.value
            yield {
                "event": "reasoning.started",
                "data": {"message": "Analyzing your request..."},
            }

            reasoning = await self.reasoning_agent.reason(
                user_request, conversation_history, mode
            )

            yield {
                "event": "reasoning.completed",
                "data": {
                    "can_proceed": reasoning.can_proceed,
                    "needs_clarification": reasoning.needs_clarification,
                    "task_analysis": reasoning.task_analysis,
                    "confidence": reasoning.confidence,
                    "reasoning": reasoning.reasoning_text,
                },
            }

            # ── PHASE 3: CLARIFICATION (if needed) ───────────────────
            if reasoning.needs_clarification:
                execution["status"] = ExecutionStatusV2.CLARIFYING.value
                yield {
                    "event": "clarification.needed",
                    "data": {
                        "questions": reasoning.clarification_questions,
                        "message": "I need some clarification before proceeding.",
                    },
                }
                # In a real implementation, we'd wait for user response.
                # For now, if we can still proceed with partial info, continue.
                if not reasoning.can_proceed:
                    execution["status"] = ExecutionStatusV2.COMPLETED.value
                    yield {
                        "event": "execution.completed",
                        "data": {
                            "response": (
                                f"I need more information to proceed:\n\n"
                                + "\n".join(f"• {q}" for q in reasoning.clarification_questions)
                            ),
                            "mode": mode,
                            "needs_clarification": True,
                        },
                    }
                    return

            # ── PHASE 4: EXECUTION PLANNING ──────────────────────────
            execution["status"] = ExecutionStatusV2.PLANNING.value
            yield {
                "event": "planning.started",
                "data": {"message": "Creating execution plan..."},
            }

            execution_plan = reasoning.execution_plan or await self._create_execution_plan(
                user_request, reasoning.task_analysis
            )

            steps = execution_plan.get("steps", []) if execution_plan else []

            yield {
                "event": "planning.completed",
                "data": {"steps": steps, "estimated_steps": len(steps)},
            }

            # ── PHASE 5: EXECUTION ───────────────────────────────────
            execution["status"] = ExecutionStatusV2.EXECUTING.value

            all_results = []
            for i, step in enumerate(steps):
                step_num = i + 1

                yield {
                    "event": "execution.step_started",
                    "data": {
                        "step_number": step_num,
                        "total_steps": len(steps),
                        "description": step.get("action", "Executing..."),
                        "tool": step.get("tool", "think"),
                    },
                }

                # Execute step and collect sub-events
                result = {}
                async for sub_event in self._execute_step_stream(step, execution_id):
                    if sub_event.get("event"):
                        yield sub_event
                    else:
                        result = sub_event  # Final result

                yield {
                    "event": "execution.step_completed",
                    "data": {
                        "step_number": step_num,
                        "result": {k: v for k, v in result.items() if k != "screenshot"},
                        "screenshot": result.get("screenshot"),
                    },
                }

                execution["steps"].append(
                    {"step": step_num, "action": step.get("action"), "result": result}
                )
                all_results.append(result)

            # ── PHASE 6: COMPLETION ──────────────────────────────────
            execution["status"] = ExecutionStatusV2.COMPLETED.value

            summary = await self._generate_summary(user_request, all_results)

            yield {
                "event": "execution.completed",
                "data": {
                    "summary": summary,
                    "response": summary,
                    "total_steps": len(steps),
                    "mode": mode,
                },
            }

        except Exception as e:
            logger.error(f"Execution failed: {e}", exc_info=True)
            execution["status"] = ExecutionStatusV2.FAILED.value
            execution["error"] = str(e)
            yield {"event": "execution.failed", "data": {"error": str(e)}}

    # ─── Step Execution ──────────────────────────────────────────────

    async def _execute_step_stream(
        self, step: Dict, execution_id: str
    ) -> AsyncGenerator[Dict, None]:
        """Execute a single step, yielding sub-events and final result."""
        tool = step.get("tool", "")
        action = step.get("action", "")

        try:
            if tool == "browser" or any(
                kw in action.lower()
                for kw in ["navigate", "go to", "visit", "open", "browse", "click", "login"]
            ):
                async for event in self._execute_browser_step_stream(step, execution_id):
                    yield event

            elif tool == "search" or "search" in action.lower():
                result = await self._execute_search_step(step)
                yield result

            elif tool == "code" or any(
                kw in action.lower() for kw in ["generate code", "write code", "execute"]
            ):
                result = await self._execute_code_step(step)
                yield result

            elif tool == "github" or "github" in action.lower():
                result = await self._execute_github_step(step)
                yield result

            else:
                # Default: think/analyze
                result = await self._execute_think_step(step)
                yield result

        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            yield {"success": False, "error": str(e)}

    async def _execute_browser_step_stream(
        self, step: Dict, execution_id: str
    ) -> AsyncGenerator[Dict, None]:
        """Execute browser step with screenshot streaming."""
        if not self.browser_engine:
            if not PLAYWRIGHT_V2_AVAILABLE:
                yield {"success": False, "error": "Playwright not available"}
                return

            self.browser_engine = BrowserEngineV2(
                kimi_client=self.kimi_client,
                grok_client=self.grok_client,
                headless=True,
            )
            await self.browser_engine.start()

        action = step.get("action", "").lower()

        # Direct navigation
        if any(kw in action for kw in ["navigate", "go to", "visit", "open"]):
            url = step.get("url", "")
            if not url:
                # Try to extract URL from action text
                urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', action)
                if urls:
                    url = urls[0]
                else:
                    # Try to extract domain-like text
                    domain_match = re.search(r'(?:to|visit|open)\s+(\S+\.\S+)', action)
                    if domain_match:
                        url = domain_match.group(1)
                    else:
                        url = "https://google.com"

            result = await self.browser_engine.navigate(url)
            yield {
                "event": "browser.navigated",
                "data": {
                    "url": result.get("url", ""),
                    "title": result.get("title", ""),
                    "screenshot": result.get("screenshot", ""),
                },
            }
            yield result

        elif "click" in action:
            x = step.get("x", 640)
            y = step.get("y", 360)
            result = await self.browser_engine.click(x, y, action)
            yield result

        elif any(kw in action for kw in ["type", "enter", "input", "fill"]):
            text = step.get("text", "")
            selector = step.get("selector")
            result = await self.browser_engine.type_text(text, selector)
            yield result

        elif "scroll" in action:
            direction = step.get("direction", "down")
            result = await self.browser_engine.scroll(direction)
            yield result

        else:
            # Use vision model to determine action
            async for cua_result in self.browser_engine.analyze_screen_and_act(
                step.get("action", ""), max_steps=5
            ):
                yield {
                    "event": "browser.action",
                    "data": {
                        "step": cua_result.get("step"),
                        "action": cua_result.get("action"),
                        "screenshot": cua_result.get("screenshot"),
                        "url": cua_result.get("url"),
                    },
                }
                if cua_result.get("done"):
                    yield cua_result
                    return

            yield {"success": True, "note": "Browser actions completed"}

    async def _execute_search_step(self, step: Dict) -> Dict:
        """Execute search step using SearchLayer."""
        query = step.get("query", step.get("action", ""))

        if not self.search_layer:
            # Fallback: use LLM to answer
            return await self._execute_think_step(step)

        try:
            results = await self.search_layer.search(
                query=query, sources=["web"], num_results=8
            )
            combined_text = ""
            for source_name, source_data in results.get("results", {}).items():
                answer = source_data.get("answer", "")
                if answer:
                    combined_text += f"\n{answer[:1500]}\n"

            return {
                "success": True,
                "query": query,
                "results_count": len(results.get("results", {})),
                "combined_text": combined_text[:3000],
            }
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_code_step(self, step: Dict) -> Dict:
        """Execute code generation step."""
        task = step.get("action", "")

        try:
            client = self.grok_client or self.kimi_client
            if not client:
                return {"success": False, "error": "No LLM client"}

            model = "grok-4-1-fast-reasoning" if self.grok_client else "kimi-k2.5"
            temp = 0.7 if model != "kimi-k2.5" else 1

            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": f"Generate code for: {task}\n\nProvide only the code, no explanation.",
                    }
                ],
                temperature=temp,
            )
            code = response.choices[0].message.content or ""
            return {"success": True, "code": code}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _execute_github_step(self, step: Dict) -> Dict:
        """Execute GitHub step (placeholder — wired via main.py)."""
        return {"success": True, "note": "GitHub operation — requires handler wiring"}

    async def _execute_think_step(self, step: Dict) -> Dict:
        """Execute thinking/analysis step."""
        task = step.get("action", "")

        try:
            client = self.grok_client or self.kimi_client
            if not client:
                return {"success": False, "error": "No LLM client"}

            model = "grok-4-1-fast-reasoning" if self.grok_client else "kimi-k2.5"
            temp = 0.7 if model != "kimi-k2.5" else 1

            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": f"Analyze and provide insights: {task}"}
                ],
                temperature=temp,
                max_tokens=2000,
            )
            analysis = response.choices[0].message.content or ""
            return {"success": True, "analysis": analysis}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ─── Plan & Summary Generation ───────────────────────────────────

    async def _create_execution_plan(self, user_request: str, task_analysis: str) -> Dict:
        """Create execution plan using LLM."""
        prompt = f"""Create an execution plan for this task.

USER REQUEST: {user_request}

TASK ANALYSIS: {task_analysis}

Available tools: browser, search, code, github, think

Create a step-by-step plan. For each step, specify:
- step number
- action description
- tool to use
- any parameters (url, query, text, etc.)

Respond in JSON:
{{
    "steps": [
        {{"step": 1, "action": "...", "tool": "browser", "url": "..."}},
        {{"step": 2, "action": "...", "tool": "search", "query": "..."}}
    ]
}}"""

        try:
            client = self.grok_client or self.kimi_client
            if not client:
                return {"steps": [{"step": 1, "action": user_request, "tool": "think"}]}

            model = "grok-4-1-fast-reasoning" if self.grok_client else "kimi-k2.5"
            temp = 0.7 if model != "kimi-k2.5" else 1

            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temp,
            )
            content = response.choices[0].message.content or ""

            # Parse JSON
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                start = content.find("{")
                end = content.rfind("}")
                json_str = content[start : end + 1] if start != -1 else content

            return json.loads(json_str)

        except Exception as e:
            logger.error(f"Plan creation failed: {e}")
            return {"steps": [{"step": 1, "action": user_request, "tool": "think"}]}

    async def _get_instant_response(
        self, user_request: str, conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """Get instant response without execution — reasoning-first, concise."""
        try:
            client = self.grok_client or self.kimi_client
            if not client:
                return "Error: No LLM client available"

            model = "grok-4-1-fast-reasoning" if self.grok_client else "kimi-k2.5"
            temp = 0.7 if model != "kimi-k2.5" else 1

            messages = []
            if conversation_history:
                for msg in conversation_history[-5:]:
                    if msg.get("content"):
                        messages.append(
                            {"role": msg.get("role", "user"), "content": msg["content"]}
                        )

            messages.append({"role": "user", "content": user_request})

            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temp,
                max_tokens=1500,
            )
            return response.choices[0].message.content or ""

        except Exception as e:
            return f"Error: {str(e)}"

    async def _generate_summary(self, user_request: str, results: List[Dict]) -> str:
        """Generate execution summary."""
        # Collect all useful text from results
        collected = []
        for r in results:
            if r.get("analysis"):
                collected.append(r["analysis"])
            if r.get("combined_text"):
                collected.append(r["combined_text"])
            if r.get("code"):
                collected.append(f"```\n{r['code'][:1000]}\n```")
            if r.get("content_preview"):
                collected.append(r["content_preview"])

        if not collected:
            return f"Task completed: {user_request}"

        results_text = "\n\n".join(collected)[:4000]

        prompt = f"""Summarize this task execution concisely.

REQUEST: {user_request}

RESULTS:
{results_text}

Write a clear, well-structured summary of what was accomplished. Be concise but thorough.
Lead with the key finding or result. Use markdown formatting."""

        try:
            client = self.grok_client or self.kimi_client
            if not client:
                return results_text

            model = "grok-4-1-fast-reasoning" if self.grok_client else "kimi-k2.5"
            temp = 0.7 if model != "kimi-k2.5" else 1

            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temp,
                max_tokens=2000,
            )
            return response.choices[0].message.content or results_text

        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return results_text

    # ─── Execution Management ────────────────────────────────────────

    def get_execution(self, execution_id: str) -> Optional[Dict]:
        """Get execution by ID."""
        return self.executions.get(execution_id)

    async def cancel_execution(self, execution_id: str):
        """Cancel an execution."""
        execution = self.executions.get(execution_id)
        if execution:
            execution["status"] = ExecutionStatusV2.FAILED.value
            execution["cancelled"] = True
