"""
Browser Engine V2 — Fixed Playwright + Vision Model
=====================================================

Fixes from V1:
1. Removed tool_choice conflict with thinking mode
2. Proper navigation to actual URLs (not about:blank)
3. Better screenshot capture and streaming
4. Working click, type, read, scroll actions
5. Fully async — no run_in_executor hacks
6. Dual-model: Kimi K2.5 for vision, Grok for reasoning

Architecture:
  Screenshot → Vision Model → JSON Action → Execute → Screenshot → Repeat
"""

import asyncio
import base64
import json
import logging
from typing import Dict, List, Optional, Any, Callable, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_V2_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_V2_AVAILABLE = False
    logger.warning("playwright not installed — BrowserEngineV2 disabled")


class BrowserActionType(Enum):
    """Types of browser actions"""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    KEYPRESS = "keypress"
    EXTRACT_TEXT = "extract_text"
    WAIT = "wait"
    DONE = "done"


@dataclass
class BrowserAction:
    """A single browser action"""
    action_type: BrowserActionType
    x: Optional[int] = None
    y: Optional[int] = None
    text: Optional[str] = None
    url: Optional[str] = None
    selector: Optional[str] = None
    key: Optional[str] = None
    direction: Optional[str] = None
    amount: Optional[int] = None
    description: str = ""


@dataclass
class BrowserState:
    """Current browser state"""
    url: str = "about:blank"
    title: str = ""
    screenshot_b64: Optional[str] = None
    page_text: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


class BrowserEngineV2:
    """
    Browser automation engine using Playwright.

    Fixed issues:
    - Removed tool_choice conflict with thinking mode
    - Proper URL navigation
    - Screenshot streaming via event callbacks
    - Fully async
    """

    VIEWPORT_WIDTH = 1280
    VIEWPORT_HEIGHT = 720

    def __init__(
        self,
        kimi_client=None,
        grok_client=None,
        headless: bool = True,
    ):
        """
        Args:
            kimi_client: openai.AsyncOpenAI for Kimi (vision model)
            grok_client: openai.AsyncOpenAI for Grok (reasoning fallback)
            headless: Run browser headless
        """
        self.kimi_client = kimi_client
        self.grok_client = grok_client
        self.headless = headless

        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None

        self.state = BrowserState()
        self.action_history: List[Dict] = []
        self.event_callbacks: List[Callable] = []

        self.is_available = PLAYWRIGHT_V2_AVAILABLE
        logger.info(f"BrowserEngineV2 initialized (headless={headless}, available={self.is_available})")

    async def start(self):
        """Start browser session"""
        if not PLAYWRIGHT_V2_AVAILABLE:
            raise RuntimeError("Playwright not available")
        if self.browser:
            return

        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process",
                ],
            )
            self.context = await self.browser.new_context(
                viewport={"width": self.VIEWPORT_WIDTH, "height": self.VIEWPORT_HEIGHT},
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ),
            )
            self.page = await self.context.new_page()
            await self.page.goto("about:blank")
            logger.info("BrowserEngineV2 started successfully")
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise

    async def stop(self):
        """Stop browser session"""
        try:
            if self.page:
                await self.page.close()
                self.page = None
            if self.context:
                await self.context.close()
                self.context = None
            if self.browser:
                await self.browser.close()
                self.browser = None
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            logger.info("BrowserEngineV2 stopped")
        except Exception as e:
            logger.error(f"Error stopping browser: {e}")

    def add_event_callback(self, callback: Callable):
        """Add event callback for streaming"""
        self.event_callbacks.append(callback)

    async def emit_event(self, event_type: str, data: Dict):
        """Emit event to all callbacks"""
        for callback in self.event_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event_type, data)
                else:
                    callback(event_type, data)
            except Exception as e:
                logger.error(f"Event callback error: {e}")

    # ─── Core Actions ────────────────────────────────────────────────

    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to URL"""
        if not self.page:
            await self.start()

        try:
            # Ensure URL has protocol
            if not url.startswith(("http://", "https://", "about:")):
                url = "https://" + url

            logger.info(f"Navigating to: {url}")
            await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Update state
            self.state.url = self.page.url
            self.state.title = await self.page.title()
            screenshot_b64 = await self._capture_screenshot()
            self.state.screenshot_b64 = screenshot_b64
            self.state.page_text = await self._get_page_text()

            result = {
                "success": True,
                "url": self.state.url,
                "title": self.state.title,
                "screenshot": screenshot_b64,
                "content_preview": self.state.page_text[:500],
            }
            await self.emit_event("browser.navigated", result)
            return result

        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return {"success": False, "error": str(e), "url": url}

    async def click(self, x: int, y: int, description: str = "") -> Dict[str, Any]:
        """Click at coordinates"""
        if not self.page:
            return {"success": False, "error": "Browser not started"}

        try:
            logger.info(f"Clicking at ({x}, {y}): {description}")
            await self.page.mouse.click(x, y)
            await asyncio.sleep(1)

            self.state.url = self.page.url
            self.state.title = await self.page.title()
            screenshot_b64 = await self._capture_screenshot()

            result = {
                "success": True,
                "x": x,
                "y": y,
                "description": description,
                "url": self.state.url,
                "screenshot": screenshot_b64,
            }
            await self.emit_event("browser.clicked", result)
            return result

        except Exception as e:
            logger.error(f"Click failed: {e}")
            return {"success": False, "error": str(e)}

    async def type_text(self, text: str, selector: Optional[str] = None) -> Dict[str, Any]:
        """Type text into focused element or selector"""
        if not self.page:
            return {"success": False, "error": "Browser not started"}

        try:
            logger.info(f"Typing: {text[:50]}...")
            if selector:
                await self.page.fill(selector, text)
            else:
                await self.page.keyboard.type(text, delay=50)

            screenshot_b64 = await self._capture_screenshot()
            result = {
                "success": True,
                "text": text,
                "selector": selector,
                "screenshot": screenshot_b64,
            }
            await self.emit_event("browser.typed", result)
            return result

        except Exception as e:
            logger.error(f"Type failed: {e}")
            return {"success": False, "error": str(e)}

    async def scroll(self, direction: str = "down", amount: int = 500) -> Dict[str, Any]:
        """Scroll page"""
        if not self.page:
            return {"success": False, "error": "Browser not started"}

        try:
            directions = {
                "up": (0, -amount),
                "down": (0, amount),
                "left": (-amount, 0),
                "right": (amount, 0),
            }
            dx, dy = directions.get(direction, (0, amount))
            await self.page.mouse.wheel(dx, dy)
            await asyncio.sleep(0.5)

            screenshot_b64 = await self._capture_screenshot()
            result = {
                "success": True,
                "direction": direction,
                "amount": amount,
                "screenshot": screenshot_b64,
            }
            await self.emit_event("browser.scrolled", result)
            return result

        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return {"success": False, "error": str(e)}

    async def keypress(self, key: str) -> Dict[str, Any]:
        """Press a key"""
        if not self.page:
            return {"success": False, "error": "Browser not started"}

        try:
            await self.page.keyboard.press(key)
            await asyncio.sleep(0.5)
            screenshot_b64 = await self._capture_screenshot()
            result = {"success": True, "key": key, "screenshot": screenshot_b64}
            await self.emit_event("browser.keypress", result)
            return result

        except Exception as e:
            logger.error(f"Keypress failed: {e}")
            return {"success": False, "error": str(e)}

    async def extract_text(self) -> Dict[str, Any]:
        """Extract text from page"""
        if not self.page:
            return {"success": False, "error": "Browser not started"}

        try:
            text = await self._get_page_text()
            return {"success": True, "text": text, "url": self.state.url}
        except Exception as e:
            logger.error(f"Extract text failed: {e}")
            return {"success": False, "error": str(e)}

    async def wait_ms(self, milliseconds: int = 1000) -> Dict[str, Any]:
        """Wait for specified time"""
        await asyncio.sleep(milliseconds / 1000)
        return {"success": True, "waited_ms": milliseconds}

    async def execute_action(self, action: BrowserAction) -> Dict[str, Any]:
        """Execute a browser action"""
        handlers = {
            BrowserActionType.NAVIGATE: lambda: self.navigate(action.url or "about:blank"),
            BrowserActionType.CLICK: lambda: self.click(action.x or 0, action.y or 0, action.description),
            BrowserActionType.TYPE: lambda: self.type_text(action.text or "", action.selector),
            BrowserActionType.SCROLL: lambda: self.scroll(action.direction or "down", action.amount or 500),
            BrowserActionType.KEYPRESS: lambda: self.keypress(action.key or "Enter"),
            BrowserActionType.EXTRACT_TEXT: lambda: self.extract_text(),
            BrowserActionType.WAIT: lambda: self.wait_ms(action.amount or 1000),
            BrowserActionType.DONE: lambda: asyncio.coroutine(lambda: {"success": True, "done": True})(),
        }
        handler = handlers.get(action.action_type)
        if handler:
            return await handler()
        return {"success": False, "error": f"Unknown action: {action.action_type}"}

    # ─── Vision-Driven CUA Loop ──────────────────────────────────────

    async def analyze_screen_and_act(
        self,
        task: str,
        max_steps: int = 10,
    ) -> AsyncGenerator[Dict, None]:
        """
        Computer-Use Agent loop: screenshot → vision → action → repeat.

        FIXED: No tool_choice, uses JSON response parsing.
        Uses Kimi K2.5 for vision (screenshot analysis).
        """
        if not self.page:
            await self.start()

        for step in range(max_steps):
            screenshot_b64 = await self._capture_screenshot()
            page_text = await self._get_page_text()
            current_url = self.page.url
            title = await self.page.title()

            self.state.screenshot_b64 = screenshot_b64
            self.state.page_text = page_text
            self.state.url = current_url
            self.state.title = title

            system_prompt = f"""You are a browser automation assistant.
Your task: {task}

Current URL: {current_url}
Page Title: {title}

Available actions (respond with JSON only):
- {{"action": "navigate", "url": "https://example.com"}} — Go to URL
- {{"action": "click", "x": 100, "y": 200, "description": "Click button"}} — Click at coordinates
- {{"action": "type", "text": "hello", "selector": "#input"}} — Type text
- {{"action": "scroll", "direction": "down", "amount": 500}} — Scroll page
- {{"action": "keypress", "key": "Enter"}} — Press key
- {{"action": "extract_text"}} — Extract page text
- {{"action": "wait", "amount": 1000}} — Wait (milliseconds)
- {{"action": "done"}} — Task complete

Respond with ONLY a JSON object. No markdown, no explanation."""

            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Visible text (first 2000 chars): {page_text[:2000]}\n\nWhat action should I take?",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{screenshot_b64}"},
                        },
                    ],
                },
            ]

            try:
                # Use Kimi for vision (it supports image input)
                client = self.kimi_client or self.grok_client
                if not client:
                    yield {"error": "No LLM client available", "step": step + 1}
                    return

                model = "kimi-k2.5" if self.kimi_client else "grok-4-1-fast-reasoning"
                temp = 1 if model == "kimi-k2.5" else 0.7

                response = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temp,
                    max_tokens=500,
                )

                content = response.choices[0].message.content or ""
                action_data = self._parse_action_json(content)

                # Map to BrowserAction
                action_type_str = action_data.get("action", "done")
                try:
                    action_type = BrowserActionType(action_type_str)
                except ValueError:
                    action_type = BrowserActionType.DONE

                action = BrowserAction(
                    action_type=action_type,
                    url=action_data.get("url"),
                    x=action_data.get("x"),
                    y=action_data.get("y"),
                    text=action_data.get("text"),
                    selector=action_data.get("selector"),
                    key=action_data.get("key"),
                    direction=action_data.get("direction"),
                    amount=action_data.get("amount"),
                    description=action_data.get("description", ""),
                )

                result = await self.execute_action(action)

                yield {
                    "step": step + 1,
                    "action": action_type_str,
                    "description": action.description,
                    "result": result,
                    "screenshot": result.get("screenshot"),
                    "url": self.state.url,
                    "done": action_type == BrowserActionType.DONE,
                }

                if action_type == BrowserActionType.DONE:
                    break

                self.action_history.append(
                    {"step": step + 1, "action": action_type_str, "result": result}
                )

            except Exception as e:
                logger.error(f"CUA loop error at step {step + 1}: {e}")
                yield {"error": str(e), "step": step + 1}
                break

    # ─── Internal Helpers ─────────────────────────────────────────────

    def _parse_action_json(self, content: str) -> Dict:
        """Parse JSON action from LLM response"""
        try:
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()
            return json.loads(json_str)
        except json.JSONDecodeError:
            try:
                start = content.find("{")
                end = content.rfind("}")
                if start != -1 and end != -1:
                    return json.loads(content[start : end + 1])
            except Exception:
                pass
            return {"action": "done"}

    async def _capture_screenshot(self) -> str:
        """Capture screenshot as base64 JPEG"""
        if not self.page:
            return ""
        try:
            screenshot_bytes = await self.page.screenshot(
                type="jpeg", quality=80, full_page=False
            )
            return base64.b64encode(screenshot_bytes).decode("utf-8")
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return ""

    async def _get_page_text(self) -> str:
        """Get visible text from page"""
        if not self.page:
            return ""
        try:
            return await self.page.evaluate("() => document.body ? document.body.innerText : ''")
        except Exception as e:
            logger.error(f"Get page text failed: {e}")
            return ""

    def get_state(self) -> BrowserState:
        """Get current browser state"""
        return self.state
