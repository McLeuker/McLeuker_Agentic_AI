"""
Browser Automation Engine — Playwright + Kimi K2.5 Vision
==========================================================

Provides real end-to-end browser automation with live screenshot streaming:
- Playwright for actual browser control (navigate, click, type, scroll)
- Kimi K2.5 vision model for screen understanding and action planning
- Real-time screenshot streaming to frontend via SSE events
- Computer-Use Agent (CUA) loop: screenshot → vision → action → repeat

This replaces Browserless for interactive tasks while keeping it for
simple content extraction. The engine runs headless Chromium server-side
and streams every screenshot to the frontend so users can watch live.
"""

import asyncio
import base64
import json
import os
import re
import time
import functools
from typing import Dict, Any, Optional, List, Callable, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# Playwright — optional dependency
try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("playwright not installed — browser engine disabled. Install with: pip install playwright && playwright install chromium")

# OpenAI-compatible client for Kimi K2.5 vision
import openai


# ============================================================================
# DATA MODELS
# ============================================================================

class BrowserActionType(Enum):
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    KEYPRESS = "keypress"
    SELECT = "select"
    HOVER = "hover"
    BACK = "back"
    FORWARD = "forward"
    EXTRACT_TEXT = "extract_text"
    DONE = "done"


@dataclass
class BrowserAction:
    """An action to perform in the browser."""
    action_type: BrowserActionType
    x: Optional[int] = None
    y: Optional[int] = None
    text: Optional[str] = None
    url: Optional[str] = None
    selector: Optional[str] = None
    key: Optional[str] = None
    direction: Optional[str] = None  # up/down/left/right
    amount: Optional[int] = None
    description: str = ""


@dataclass
class BrowserState:
    """Current state of the browser."""
    url: str = ""
    title: str = ""
    screenshot_b64: str = ""
    page_text: str = ""
    timestamp: float = 0.0
    viewport_width: int = 1280
    viewport_height: int = 720


@dataclass
class BrowserStepResult:
    """Result of a single browser automation step."""
    step_number: int
    action: BrowserAction
    state_before: Optional[BrowserState] = None
    state_after: Optional[BrowserState] = None
    success: bool = True
    error: Optional[str] = None
    duration_ms: float = 0.0


# ============================================================================
# BROWSER ENGINE
# ============================================================================

class BrowserEngine:
    """
    Playwright-based browser automation engine with vision model integration.

    Runs headless Chromium, takes screenshots at each step, and can use
    Kimi K2.5 vision model to understand the screen and decide next actions.
    Screenshots are streamed to the frontend via a callback function.
    """

    VIEWPORT_WIDTH = 1280
    VIEWPORT_HEIGHT = 720
    MAX_STEPS = 30
    SCREENSHOT_QUALITY = 70  # JPEG quality for streaming (lower = faster)

    def __init__(
        self,
        kimi_client: Optional[openai.OpenAI] = None,
        grok_client: Optional[openai.OpenAI] = None,
        on_screenshot: Optional[Callable] = None,
        on_action: Optional[Callable] = None,
    ):
        """
        Initialize browser engine.

        Args:
            kimi_client: OpenAI-compatible client for Kimi K2.5 vision (base_url=moonshot)
            grok_client: Fallback OpenAI-compatible client for Grok vision
            on_screenshot: Callback(screenshot_b64, url, title) called after each screenshot
            on_action: Callback(action_description) called before each action
        """
        self.kimi_client = kimi_client
        self.grok_client = grok_client
        self.on_screenshot = on_screenshot
        self.on_action = on_action

        self._playwright: Optional[Any] = None
        self._browser: Optional[Any] = None
        self._context: Optional[Any] = None
        self._page: Optional[Any] = None
        self._started = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self):
        """Launch headless Chromium browser."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not installed. Run: pip install playwright && playwright install chromium")

        if self._started:
            return

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )
        self._context = await self._browser.new_context(
            viewport={"width": self.VIEWPORT_WIDTH, "height": self.VIEWPORT_HEIGHT},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        self._page = await self._context.new_page()
        self._started = True
        logger.info("Browser engine started (headless Chromium)")

    async def stop(self):
        """Close browser and clean up."""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._started = False
        logger.info("Browser engine stopped")

    # ------------------------------------------------------------------
    # Screenshot
    # ------------------------------------------------------------------

    async def take_screenshot(self) -> str:
        """Take a screenshot and return as base64 JPEG string."""
        if not self._page:
            return ""

        try:
            screenshot_bytes = await self._page.screenshot(
                type="jpeg",
                quality=self.SCREENSHOT_QUALITY,
                full_page=False,
            )
            b64 = base64.b64encode(screenshot_bytes).decode("utf-8")

            # Notify callback
            if self.on_screenshot:
                url = self._page.url
                title = await self._page.title()
                try:
                    await self.on_screenshot(b64, url, title)
                except Exception:
                    pass  # Don't fail on callback errors

            return b64
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return ""

    async def get_state(self) -> BrowserState:
        """Get current browser state including screenshot."""
        if not self._page:
            return BrowserState()

        screenshot_b64 = await self.take_screenshot()

        # Extract visible text (first 5000 chars for context)
        try:
            page_text = await self._page.evaluate("() => document.body?.innerText?.substring(0, 5000) || ''")
        except Exception:
            page_text = ""

        return BrowserState(
            url=self._page.url,
            title=await self._page.title(),
            screenshot_b64=screenshot_b64,
            page_text=page_text,
            timestamp=time.time(),
            viewport_width=self.VIEWPORT_WIDTH,
            viewport_height=self.VIEWPORT_HEIGHT,
        )

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    async def execute_action(self, action: BrowserAction) -> bool:
        """Execute a single browser action. Returns True on success."""
        if not self._page:
            return False

        # Notify callback
        if self.on_action:
            try:
                await self.on_action(action.description or f"{action.action_type.value}")
            except Exception:
                pass

        try:
            if action.action_type == BrowserActionType.NAVIGATE:
                url = action.url or action.text or ""
                if not url.startswith("http"):
                    url = "https://" + url
                await self._page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(1)  # Let page settle

            elif action.action_type == BrowserActionType.CLICK:
                if action.selector:
                    await self._page.click(action.selector, timeout=5000)
                elif action.x is not None and action.y is not None:
                    await self._page.mouse.click(action.x, action.y)
                else:
                    return False
                await asyncio.sleep(0.5)

            elif action.action_type == BrowserActionType.TYPE:
                text = action.text or ""
                if action.selector:
                    await self._page.fill(action.selector, text)
                elif action.x is not None and action.y is not None:
                    await self._page.mouse.click(action.x, action.y)
                    await asyncio.sleep(0.2)
                    await self._page.keyboard.type(text, delay=30)
                else:
                    await self._page.keyboard.type(text, delay=30)
                await asyncio.sleep(0.3)

            elif action.action_type == BrowserActionType.KEYPRESS:
                key = action.key or "Enter"
                await self._page.keyboard.press(key)
                await asyncio.sleep(0.5)

            elif action.action_type == BrowserActionType.SCROLL:
                direction = action.direction or "down"
                amount = action.amount or 300
                if direction == "down":
                    await self._page.mouse.wheel(0, amount)
                elif direction == "up":
                    await self._page.mouse.wheel(0, -amount)
                elif direction == "right":
                    await self._page.mouse.wheel(amount, 0)
                elif direction == "left":
                    await self._page.mouse.wheel(-amount, 0)
                await asyncio.sleep(0.3)

            elif action.action_type == BrowserActionType.HOVER:
                if action.x is not None and action.y is not None:
                    await self._page.mouse.move(action.x, action.y)
                elif action.selector:
                    await self._page.hover(action.selector, timeout=5000)
                await asyncio.sleep(0.3)

            elif action.action_type == BrowserActionType.SELECT:
                if action.selector and action.text:
                    await self._page.select_option(action.selector, action.text)
                await asyncio.sleep(0.3)

            elif action.action_type == BrowserActionType.BACK:
                await self._page.go_back(wait_until="domcontentloaded", timeout=10000)
                await asyncio.sleep(0.5)

            elif action.action_type == BrowserActionType.FORWARD:
                await self._page.go_forward(wait_until="domcontentloaded", timeout=10000)
                await asyncio.sleep(0.5)

            elif action.action_type == BrowserActionType.WAIT:
                wait_time = action.amount or 2000
                await asyncio.sleep(wait_time / 1000.0)

            elif action.action_type == BrowserActionType.EXTRACT_TEXT:
                pass  # Text extraction happens in get_state()

            elif action.action_type == BrowserActionType.SCREENSHOT:
                pass  # Screenshot happens in get_state()

            elif action.action_type == BrowserActionType.DONE:
                pass  # Terminal action

            return True

        except Exception as e:
            logger.error(f"Browser action error ({action.action_type.value}): {e}")
            return False

    # ------------------------------------------------------------------
    # Vision Model — Screen Understanding
    # ------------------------------------------------------------------

    async def analyze_screen(
        self,
        screenshot_b64: str,
        task: str,
        history: List[Dict[str, Any]] = None,
        page_text: str = "",
        current_url: str = "",
    ) -> BrowserAction:
        """
        Send screenshot to Kimi K2.5 vision model and get the next action.

        Uses the Computer-Use Agent (CUA) pattern:
        1. Send screenshot + task description
        2. Model analyzes the screen
        3. Returns structured action to perform
        """
        if not self.kimi_client and not self.grok_client:
            logger.warning("No vision model available for screen analysis")
            return BrowserAction(action_type=BrowserActionType.DONE, description="No vision model available")

        # Build the tool definitions for structured action output
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "browser_action",
                    "description": "Execute a browser action based on what you see on screen",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action_type": {
                                "type": "string",
                                "enum": ["navigate", "click", "type", "scroll", "wait", "keypress", "hover", "back", "extract_text", "done"],
                                "description": "The type of browser action to perform"
                            },
                            "x": {"type": "integer", "description": "X coordinate for click/type/hover actions (0-1280)"},
                            "y": {"type": "integer", "description": "Y coordinate for click/type/hover actions (0-720)"},
                            "text": {"type": "string", "description": "Text to type, URL to navigate to, or description"},
                            "selector": {"type": "string", "description": "CSS selector if known (optional)"},
                            "key": {"type": "string", "description": "Key to press for keypress action (e.g., Enter, Tab, Escape)"},
                            "direction": {"type": "string", "enum": ["up", "down", "left", "right"], "description": "Scroll direction"},
                            "amount": {"type": "integer", "description": "Scroll amount in pixels or wait time in ms"},
                            "description": {"type": "string", "description": "Human-readable description of what this action does"},
                        },
                        "required": ["action_type", "description"],
                    },
                },
            }
        ]

        # Build messages
        system_prompt = f"""You are a browser automation agent. You can see the current state of a web browser through screenshots.

Your task: {task}

Current URL: {current_url}

Instructions:
- Analyze the screenshot carefully to understand what's on screen
- Decide the next action to take to accomplish the task
- Use click(x, y) for buttons, links, and interactive elements
- Use type(text) to enter text in input fields (click the field first if needed)
- Use navigate(url) to go to a specific URL
- Use scroll(direction) to see more content
- Use keypress(key) for keyboard shortcuts (Enter, Tab, Escape, etc.)
- Use extract_text when you need to read and report content from the page
- Use done when the task is complete or you've gathered enough information
- The viewport is {self.VIEWPORT_WIDTH}x{self.VIEWPORT_HEIGHT} pixels
- Coordinates (0,0) is top-left corner
- Be precise with click coordinates — aim for the center of the target element
- If a page is loading, use wait action
- Always describe what you're doing and why"""

        messages = [{"role": "system", "content": system_prompt}]

        # Add history of previous actions
        if history:
            for h in history[-6:]:  # Last 6 actions for context
                messages.append({"role": "assistant", "content": h.get("action_desc", "")})
                if h.get("screenshot_b64"):
                    messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"Action result. Current URL: {h.get('url', '')}. Page title: {h.get('title', '')}"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{h['screenshot_b64']}"}},
                        ],
                    })

        # Current screenshot
        user_content = [
            {"type": "text", "text": f"Current state — URL: {current_url}. Visible text (first 2000 chars): {page_text[:2000]}. What action should I take next?"},
        ]
        if screenshot_b64:
            user_content.append(
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{screenshot_b64}"}}
            )
        messages.append({"role": "user", "content": user_content})

        # Call vision model
        client = self.kimi_client or self.grok_client
        model = "kimi-k2.5" if self.kimi_client else "grok-4-1-fast-reasoning"

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                functools.partial(
                    client.chat.completions.create,
                    model=model,
                    messages=messages,
                    tools=tools,
                    tool_choice={"type": "function", "function": {"name": "browser_action"}},
                    temperature=1 if self.kimi_client else 0.7,
                    max_tokens=1024,
                ),
            )

            message = response.choices[0].message

            # Parse tool call
            if message.tool_calls:
                tc = message.tool_calls[0]
                args = json.loads(tc.function.arguments)
                action_type_str = args.get("action_type", "done")

                try:
                    action_type = BrowserActionType(action_type_str)
                except ValueError:
                    action_type = BrowserActionType.DONE

                return BrowserAction(
                    action_type=action_type,
                    x=args.get("x"),
                    y=args.get("y"),
                    text=args.get("text"),
                    url=args.get("text") if action_type == BrowserActionType.NAVIGATE else None,
                    selector=args.get("selector"),
                    key=args.get("key"),
                    direction=args.get("direction"),
                    amount=args.get("amount"),
                    description=args.get("description", ""),
                )

            # Fallback: parse from content
            if message.content:
                logger.info(f"Vision model returned text instead of tool call: {message.content[:200]}")
                return BrowserAction(
                    action_type=BrowserActionType.DONE,
                    description=message.content[:500],
                )

            return BrowserAction(action_type=BrowserActionType.DONE, description="No action determined")

        except Exception as e:
            logger.error(f"Vision model error: {e}")
            return BrowserAction(
                action_type=BrowserActionType.DONE,
                description=f"Vision model error: {str(e)[:200]}",
            )

    # ------------------------------------------------------------------
    # High-Level: Execute a browsing task autonomously
    # ------------------------------------------------------------------

    async def execute_task(
        self,
        task: str,
        start_url: Optional[str] = None,
        max_steps: int = None,
        sub_events: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Execute a complete browsing task autonomously using the CUA loop.

        Args:
            task: Natural language description of what to do
            start_url: Optional URL to start from
            max_steps: Maximum number of actions to take
            sub_events: List/queue to append SSE events to (for streaming)

        Returns:
            Dict with task results including extracted content and screenshots
        """
        max_steps = max_steps or self.MAX_STEPS

        def emit(event_name: str, data: Dict):
            if sub_events is not None:
                try:
                    sub_events.append({"event": event_name, "data": data})
                except Exception:
                    pass

        # Start browser if not running
        if not self._started:
            await self.start()

        emit("execution_reasoning", {"chunk": "- Starting browser automation engine...\n"})

        # Navigate to start URL if provided
        if start_url:
            emit("execution_reasoning", {"chunk": f"- Navigating to {start_url}\n"})
            await self.execute_action(BrowserAction(
                action_type=BrowserActionType.NAVIGATE,
                url=start_url,
                description=f"Navigate to {start_url}",
            ))

        # Take initial screenshot
        state = await self.get_state()
        emit("browser_screenshot", {
            "screenshot": state.screenshot_b64,
            "url": state.url,
            "title": state.title,
            "step": 0,
            "action": "Initial page load",
        })

        # CUA Loop
        history: List[Dict[str, Any]] = []
        steps: List[BrowserStepResult] = []
        extracted_content = ""
        final_url = state.url

        for step_num in range(1, max_steps + 1):
            # Analyze screen with vision model
            emit("execution_reasoning", {"chunk": f"- Analyzing screen (step {step_num})...\n"})

            action = await self.analyze_screen(
                screenshot_b64=state.screenshot_b64,
                task=task,
                history=history,
                page_text=state.page_text,
                current_url=state.url,
            )

            # Check if done
            if action.action_type == BrowserActionType.DONE:
                emit("execution_reasoning", {"chunk": f"- Task complete: {action.description}\n"})
                extracted_content = action.description
                break

            # Execute action
            action_desc = action.description or f"{action.action_type.value}"
            emit("execution_reasoning", {"chunk": f"- Action {step_num}: {action_desc}\n"})

            state_before = state
            start_time = time.time()
            success = await self.execute_action(action)
            duration_ms = (time.time() - start_time) * 1000

            # Get new state
            await asyncio.sleep(0.5)  # Let page update
            state = await self.get_state()
            final_url = state.url

            # Stream screenshot to frontend
            emit("browser_screenshot", {
                "screenshot": state.screenshot_b64,
                "url": state.url,
                "title": state.title,
                "step": step_num,
                "action": action_desc,
            })

            # Record step
            step_result = BrowserStepResult(
                step_number=step_num,
                action=action,
                state_before=state_before,
                state_after=state,
                success=success,
                duration_ms=duration_ms,
            )
            steps.append(step_result)

            # Add to history for context
            history.append({
                "action_desc": action_desc,
                "screenshot_b64": state.screenshot_b64,
                "url": state.url,
                "title": state.title,
            })

            # Extract text if that was the action
            if action.action_type == BrowserActionType.EXTRACT_TEXT:
                extracted_content = state.page_text

        # Final extraction
        if not extracted_content:
            extracted_content = state.page_text

        return {
            "type": "browser_automation",
            "success": True,
            "url": final_url,
            "title": state.title if state else "",
            "content": extracted_content[:10000],
            "steps_taken": len(steps),
            "max_steps": max_steps,
            "screenshots_count": len(steps) + 1,  # +1 for initial
            "final_screenshot": state.screenshot_b64 if state else "",
        }

    # ------------------------------------------------------------------
    # Simple operations (non-CUA, direct control)
    # ------------------------------------------------------------------

    async def navigate_and_extract(self, url: str, sub_events=None) -> Dict[str, Any]:
        """Navigate to a URL, take screenshot, extract text. Simple non-CUA operation."""
        def emit(event_name: str, data: Dict):
            if sub_events is not None:
                try:
                    sub_events.append({"event": event_name, "data": data})
                except Exception:
                    pass

        if not self._started:
            await self.start()

        emit("execution_reasoning", {"chunk": f"- Opening {url} in browser...\n"})

        await self.execute_action(BrowserAction(
            action_type=BrowserActionType.NAVIGATE,
            url=url,
            description=f"Navigate to {url}",
        ))

        state = await self.get_state()

        emit("browser_screenshot", {
            "screenshot": state.screenshot_b64,
            "url": state.url,
            "title": state.title,
            "step": 1,
            "action": f"Loaded {url}",
        })

        return {
            "type": "browser_extraction",
            "success": True,
            "url": state.url,
            "title": state.title,
            "content": state.page_text,
            "screenshot": state.screenshot_b64,
        }

    async def navigate_and_screenshot(self, url: str) -> Dict[str, Any]:
        """Navigate to URL and return screenshot. Minimal operation."""
        if not self._started:
            await self.start()

        await self.execute_action(BrowserAction(
            action_type=BrowserActionType.NAVIGATE,
            url=url,
        ))
        state = await self.get_state()

        return {
            "url": state.url,
            "title": state.title,
            "screenshot_b64": state.screenshot_b64,
            "page_text": state.page_text,
        }


# ============================================================================
# GLOBAL INSTANCE MANAGEMENT
# ============================================================================

_browser_engine: Optional[BrowserEngine] = None


async def get_browser_engine(
    kimi_client: Optional[openai.OpenAI] = None,
    grok_client: Optional[openai.OpenAI] = None,
) -> BrowserEngine:
    """Get or create the global browser engine instance."""
    global _browser_engine
    if _browser_engine is None:
        _browser_engine = BrowserEngine(
            kimi_client=kimi_client,
            grok_client=grok_client,
        )
    return _browser_engine


async def shutdown_browser_engine():
    """Shutdown the global browser engine."""
    global _browser_engine
    if _browser_engine:
        await _browser_engine.stop()
        _browser_engine = None
