"""
Executor Agent — Executes planned steps using registered tools
================================================================

Takes execution steps from the PlannerAgent and executes them
using the appropriate tools (browser, code, search, github, etc.).
Implements the observation loop: execute → observe → decide next action.
"""

import asyncio
import json
import re
import time
from typing import Dict, List, Any, Optional, Callable, AsyncGenerator
from dataclasses import dataclass, field
from .base_agent import BaseAgent, AgentEvent, ToolCall, ToolResult
from .planner_agent import ExecutionStep, ExecutionPlan
from .browser_agent import BrowserAgent
import logging

logger = logging.getLogger(__name__)


EXECUTOR_SYSTEM_PROMPT = """You are an execution agent. You execute tasks step by step using available tools.

When given a task step, you must:
1. Determine the exact tool calls needed
2. Execute them in order
3. Observe the results
4. Decide if the step is complete or needs more actions

For browser tasks, you have these tools:
- browser_navigate(url): Go to a URL
- browser_click(selector): Click an element
- browser_type(selector, text, press_enter): Type into a field
- browser_read(selector): Read page content
- browser_scroll(direction, amount): Scroll the page
- browser_screenshot(): Take a screenshot
- browser_done(summary): Mark task complete

For each action, observe the screenshot and page state to decide the next action.
When the task is complete, call browser_done with a summary.

Always be specific with selectors. Use CSS selectors like:
- input[name="search"], button[type="submit"], a[href="/login"]
- .class-name, #element-id
- text="Click me" for text-based selection
"""


class ExecutorAgent(BaseAgent):
    """
    Executes steps from the execution plan.
    Manages tool registration and the execute-observe loop.
    """

    def __init__(self, llm_client=None, browser_agent: Optional[BrowserAgent] = None, **kwargs):
        super().__init__(
            name="executor",
            system_prompt=EXECUTOR_SYSTEM_PROMPT,
            llm_client=llm_client,
            **kwargs
        )
        self.browser = browser_agent
        self._tool_handlers: Dict[str, Callable] = {}
        self._search_handler: Optional[Callable] = None
        self._code_handler: Optional[Callable] = None
        self._github_handler: Optional[Callable] = None

        # Register browser tools if available
        if self.browser and self.browser.is_available:
            handlers = self.browser.get_tool_handlers()
            for name, handler in handlers.items():
                self._tool_handlers[name] = handler

    def register_search(self, handler: Callable):
        """Register the search handler."""
        self._search_handler = handler

    def register_code(self, handler: Callable):
        """Register the code execution handler."""
        self._code_handler = handler

    def register_github(self, handler: Callable):
        """Register the GitHub handler."""
        self._github_handler = handler

    async def execute_step(
        self,
        step: ExecutionStep,
        context: Dict[str, Any],
        emit_event: Callable,
    ) -> Dict[str, Any]:
        """
        Execute a single step. Returns the step result.
        emit_event is called with (event_type, data) for real-time streaming.
        """
        tool = step.tool
        instruction = step.instruction
        start_time = time.time()

        await emit_event("step_start", {
            "step_id": step.id,
            "tool": tool,
            "instruction": instruction,
        })

        try:
            if tool == "browser":
                result = await self._execute_browser_step(step, context, emit_event)
            elif tool == "search":
                result = await self._execute_search_step(step, context, emit_event)
            elif tool == "code":
                result = await self._execute_code_step(step, context, emit_event)
            elif tool == "github":
                result = await self._execute_github_step(step, context, emit_event)
            elif tool == "think":
                result = await self._execute_think_step(step, context, emit_event)
            elif tool == "file":
                result = await self._execute_file_step(step, context, emit_event)
            else:
                result = await self._execute_think_step(step, context, emit_event)

            elapsed = int((time.time() - start_time) * 1000)
            step.status = "completed"
            step.result = result

            await emit_event("step_complete", {
                "step_id": step.id,
                "tool": tool,
                "result_summary": self._summarize_result(result),
                "execution_time_ms": elapsed,
            })

            return result

        except Exception as e:
            elapsed = int((time.time() - start_time) * 1000)
            step.status = "failed"
            error_msg = str(e)
            logger.error(f"Step {step.id} failed: {error_msg}")

            await emit_event("step_error", {
                "step_id": step.id,
                "tool": tool,
                "error": error_msg,
                "execution_time_ms": elapsed,
            })

            return {"success": False, "error": error_msg}

    # ========================================================================
    # BROWSER STEP — Multi-turn tool-calling loop with screenshots
    # ========================================================================

    async def _execute_browser_step(
        self,
        step: ExecutionStep,
        context: Dict,
        emit_event: Callable,
    ) -> Dict[str, Any]:
        """Execute a browser step using the LLM tool-calling loop."""
        if not self.browser or not self.browser.is_available:
            return {"success": False, "error": "Browser not available"}

        # Start browser if needed
        started = await self.browser.start()
        if not started:
            return {"success": False, "error": "Failed to start browser"}

        # Build messages for the LLM
        messages = [
            {"role": "system", "content": EXECUTOR_SYSTEM_PROMPT},
            {"role": "user", "content": f"Execute this browser task:\n{step.instruction}\n\nStart by navigating to the appropriate URL."}
        ]

        max_iterations = 15
        all_results = []

        for iteration in range(max_iterations):
            # Call LLM with browser tools
            try:
                response = await self.call_llm(
                    messages,
                    tools=BrowserAgent.BROWSER_TOOLS,
                    temperature=0.3,
                    max_tokens=2048,
                )
            except Exception as e:
                logger.error(f"LLM call failed in browser loop: {e}")
                break

            choice = response["choices"][0]
            message = choice["message"]

            # Check if LLM wants to call tools
            tool_calls = message.get("tool_calls", [])

            if not tool_calls:
                # LLM responded with text — task might be done
                content = message.get("content", "")
                if content:
                    messages.append({"role": "assistant", "content": content})
                    await emit_event("browser_thinking", {"thought": content})
                break

            # Execute each tool call
            messages.append(message)  # Add assistant message with tool calls

            for tc in tool_calls:
                fn_name = tc["function"]["name"]
                try:
                    fn_args = json.loads(tc["function"]["arguments"])
                except:
                    fn_args = {}

                await emit_event("browser_action", {
                    "action": fn_name,
                    "parameters": fn_args,
                    "iteration": iteration + 1,
                })

                # Execute the tool
                result = await self.browser.execute_tool(fn_name, fn_args)
                all_results.append(result)

                # Emit screenshot if available
                if result.get("screenshot"):
                    await emit_event("browser_screenshot", {
                        "image": result["screenshot"],
                        "url": result.get("url", self.browser.state.url),
                        "title": result.get("title", self.browser.state.title),
                        "action": fn_name,
                    })

                # Check if done
                if result.get("done"):
                    return {
                        "success": True,
                        "summary": result.get("summary", "Browser task completed"),
                        "url": self.browser.state.url,
                        "iterations": iteration + 1,
                    }

                # Add tool result to messages
                result_text = json.dumps({
                    k: v for k, v in result.items()
                    if k != "screenshot"  # Don't send base64 back to LLM
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result_text,
                })

        # Reached max iterations or LLM stopped
        return {
            "success": True,
            "summary": f"Browser task completed after {min(iteration + 1, max_iterations)} iterations",
            "url": self.browser.state.url,
            "results_count": len(all_results),
        }

    # ========================================================================
    # SEARCH STEP
    # ========================================================================

    async def _execute_search_step(
        self,
        step: ExecutionStep,
        context: Dict,
        emit_event: Callable,
    ) -> Dict[str, Any]:
        """Execute a search step using the registered search handler."""
        if not self._search_handler:
            return {"success": False, "error": "Search not available"}

        await emit_event("search_start", {"query": step.instruction})

        try:
            result = await self._search_handler(step.instruction)
            await emit_event("search_complete", {
                "results_count": len(result.get("results", [])),
            })
            return {"success": True, **result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ========================================================================
    # CODE STEP
    # ========================================================================

    async def _execute_code_step(
        self,
        step: ExecutionStep,
        context: Dict,
        emit_event: Callable,
    ) -> Dict[str, Any]:
        """Execute a code step — generate code with LLM then run it."""
        # Generate code
        messages = [
            {"role": "system", "content": "You are a Python code generator. Write clean, executable Python code. Output ONLY the code, no markdown fences, no explanations."},
            {"role": "user", "content": f"Write Python code to: {step.instruction}\n\nPrevious context: {json.dumps(context.get('previous_results', {}), default=str)[:2000]}"}
        ]

        try:
            response = await self.call_llm(messages, temperature=0.3, max_tokens=4096)
            code = response["choices"][0]["message"]["content"]

            # Clean markdown fences
            code = code.strip()
            if code.startswith("```"):
                code = re.sub(r"^```(?:python)?\s*\n?", "", code)
                code = re.sub(r"\n?```\s*$", "", code)

            await emit_event("code_generated", {"code": code[:500], "lines": len(code.splitlines())})

            # Execute code
            if self._code_handler:
                result = await self._code_handler(code)
                await emit_event("code_executed", {
                    "output": str(result.get("output", ""))[:500],
                    "success": result.get("success", False),
                })
                return {"success": True, "code": code, **result}
            else:
                return {"success": True, "code": code, "note": "Code generated but no sandbox available"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ========================================================================
    # GITHUB STEP
    # ========================================================================

    async def _execute_github_step(
        self,
        step: ExecutionStep,
        context: Dict,
        emit_event: Callable,
    ) -> Dict[str, Any]:
        """Execute a GitHub step using the registered handler."""
        if not self._github_handler:
            return {"success": False, "error": "GitHub not available"}

        try:
            result = await self._github_handler(step.instruction, context)
            return {"success": True, **result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ========================================================================
    # THINK STEP
    # ========================================================================

    async def _execute_think_step(
        self,
        step: ExecutionStep,
        context: Dict,
        emit_event: Callable,
    ) -> Dict[str, Any]:
        """Execute a think/analysis step."""
        previous = context.get("previous_results", {})
        messages = [
            {"role": "system", "content": "You are an analytical agent. Analyze the given information and provide clear, structured insights."},
            {"role": "user", "content": f"Task: {step.instruction}\n\nContext and previous results:\n{json.dumps(previous, default=str)[:4000]}"}
        ]

        try:
            response = await self.call_llm(messages, temperature=0.5, max_tokens=4096)
            analysis = response["choices"][0]["message"]["content"]

            await emit_event("analysis_complete", {
                "summary": analysis[:200],
                "length": len(analysis),
            })

            return {"success": True, "analysis": analysis}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ========================================================================
    # FILE STEP
    # ========================================================================

    async def _execute_file_step(
        self,
        step: ExecutionStep,
        context: Dict,
        emit_event: Callable,
    ) -> Dict[str, Any]:
        """Execute a file generation step."""
        # Delegate to code handler for file generation
        return await self._execute_code_step(step, context, emit_event)

    # ========================================================================
    # HELPERS
    # ========================================================================

    def _summarize_result(self, result: Dict) -> str:
        """Create a brief summary of a step result."""
        if not result:
            return "No result"
        if result.get("error"):
            return f"Error: {result['error'][:100]}"
        if result.get("summary"):
            return result["summary"][:200]
        if result.get("analysis"):
            return result["analysis"][:200]
        if result.get("text"):
            return f"Extracted {len(result['text'])} chars"
        if result.get("output"):
            return f"Output: {str(result['output'])[:200]}"
        return "Completed"
