"""
Browser Agent — Real Playwright Browser Automation
====================================================

Provides actual end-to-end browser control:
- Navigate to URLs
- Click elements (by selector or coordinates)
- Type text into fields
- Read page content
- Scroll pages
- Take screenshots at every action
- Stream screenshots in real-time

Uses Playwright headless Chromium. Screenshots are base64 JPEG
and streamed to the frontend via SSE/WebSocket.
"""

import asyncio
import base64
import json
import os
import re
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Playwright — optional
try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not installed — browser agent disabled")


@dataclass
class BrowserState:
    """Current browser state."""
    url: str = ""
    title: str = ""
    screenshot_b64: Optional[str] = None
    page_text: str = ""
    is_loading: bool = False
    error: Optional[str] = None


class BrowserAgent:
    """
    Real browser automation agent using Playwright.
    Each action captures a screenshot for the live viewer.
    """

    # Tool definitions for LLM function calling
    BROWSER_TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "browser_navigate",
                "description": "Navigate the browser to a URL",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to navigate to"}
                    },
                    "required": ["url"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "browser_click",
                "description": "Click an element on the page by CSS selector or text content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "selector": {"type": "string", "description": "CSS selector or text to click"},
                        "x": {"type": "integer", "description": "X coordinate to click (optional)"},
                        "y": {"type": "integer", "description": "Y coordinate to click (optional)"}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "browser_type",
                "description": "Type text into an input field",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "selector": {"type": "string", "description": "CSS selector of the input field"},
                        "text": {"type": "string", "description": "Text to type"},
                        "press_enter": {"type": "boolean", "description": "Press Enter after typing", "default": False}
                    },
                    "required": ["selector", "text"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "browser_read",
                "description": "Read the text content of the current page or a specific element",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "selector": {"type": "string", "description": "CSS selector to read (optional, reads full page if omitted)"}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "browser_scroll",
                "description": "Scroll the page up or down",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "direction": {"type": "string", "enum": ["up", "down"], "description": "Scroll direction"},
                        "amount": {"type": "integer", "description": "Pixels to scroll", "default": 500}
                    },
                    "required": ["direction"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "browser_screenshot",
                "description": "Take a screenshot of the current page",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "browser_done",
                "description": "Indicate that the browser task is complete and provide a summary",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string", "description": "Summary of what was accomplished"}
                    },
                    "required": ["summary"]
                }
            }
        }
    ]

    def __init__(self, headless: bool = True, viewport_width: int = 1280, viewport_height: int = 800):
        self.headless = headless
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._started = False
        self._screenshot_callbacks: List[Callable] = []
        self.state = BrowserState()

    @property
    def is_available(self) -> bool:
        return PLAYWRIGHT_AVAILABLE

    async def start(self) -> bool:
        """Start the browser. Returns True if successful."""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not installed")
            return False

        if self._started:
            return True

        try:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--single-process",
                ]
            )
            self._context = await self._browser.new_context(
                viewport={"width": self.viewport_width, "height": self.viewport_height},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            self._page = await self._context.new_page()
            self._started = True
            logger.info("Browser agent started (headless Chromium)")
            return True
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            self._started = False
            return False

    async def stop(self):
        """Stop the browser and clean up."""
        try:
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
        except Exception as e:
            logger.error(f"Error stopping browser: {e}")
        finally:
            self._started = False
            self._page = None
            self._context = None
            self._browser = None
            self._playwright = None

    def on_screenshot(self, callback: Callable):
        """Register a callback for screenshot events."""
        self._screenshot_callbacks.append(callback)

    async def _capture_screenshot(self) -> Optional[str]:
        """Capture a screenshot and return base64 JPEG. Also triggers callbacks."""
        if not self._page:
            return None
        try:
            screenshot_bytes = await self._page.screenshot(type="jpeg", quality=70)
            b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
            self.state.screenshot_b64 = b64
            self.state.url = self._page.url
            self.state.title = await self._page.title()

            # Notify all screenshot callbacks
            for cb in self._screenshot_callbacks:
                try:
                    if asyncio.iscoroutinefunction(cb):
                        await cb(b64, self.state.url, self.state.title)
                    else:
                        cb(b64, self.state.url, self.state.title)
                except Exception as e:
                    logger.error(f"Screenshot callback error: {e}")

            return b64
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            return None

    async def _update_state(self):
        """Update the browser state."""
        if self._page:
            self.state.url = self._page.url
            try:
                self.state.title = await self._page.title()
            except:
                pass

    # ========================================================================
    # BROWSER ACTIONS — Each returns a result dict with optional screenshot
    # ========================================================================

    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL."""
        if not self._started:
            started = await self.start()
            if not started:
                return {"success": False, "error": "Browser not available"}

        try:
            self.state.is_loading = True
            await self._page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(1)  # Wait for dynamic content
            self.state.is_loading = False
            await self._update_state()
            screenshot = await self._capture_screenshot()
            return {
                "success": True,
                "url": self.state.url,
                "title": self.state.title,
                "screenshot": screenshot
            }
        except Exception as e:
            self.state.is_loading = False
            self.state.error = str(e)
            logger.error(f"Navigation failed: {e}")
            return {"success": False, "error": str(e)}

    async def click(self, selector: str = None, x: int = None, y: int = None) -> Dict[str, Any]:
        """Click an element by selector or coordinates."""
        if not self._page:
            return {"success": False, "error": "No page open"}

        try:
            if x is not None and y is not None:
                await self._page.mouse.click(x, y)
            elif selector:
                # Try CSS selector first, then text
                try:
                    await self._page.click(selector, timeout=5000)
                except:
                    # Try as text content
                    await self._page.click(f"text={selector}", timeout=5000)
            else:
                return {"success": False, "error": "No selector or coordinates provided"}

            await asyncio.sleep(0.5)
            await self._update_state()
            screenshot = await self._capture_screenshot()
            return {
                "success": True,
                "url": self.state.url,
                "screenshot": screenshot
            }
        except Exception as e:
            logger.error(f"Click failed: {e}")
            screenshot = await self._capture_screenshot()
            return {"success": False, "error": str(e), "screenshot": screenshot}

    async def type_text(self, selector: str, text: str, press_enter: bool = False) -> Dict[str, Any]:
        """Type text into an input field."""
        if not self._page:
            return {"success": False, "error": "No page open"}

        try:
            await self._page.fill(selector, text, timeout=5000)
            if press_enter:
                await self._page.press(selector, "Enter")
                await asyncio.sleep(1)
            await self._update_state()
            screenshot = await self._capture_screenshot()
            return {
                "success": True,
                "url": self.state.url,
                "screenshot": screenshot
            }
        except Exception as e:
            logger.error(f"Type failed: {e}")
            # Try clicking and typing as fallback
            try:
                element = await self._page.query_selector(selector)
                if element:
                    await element.click()
                    await self._page.keyboard.type(text)
                    if press_enter:
                        await self._page.keyboard.press("Enter")
                        await asyncio.sleep(1)
                    screenshot = await self._capture_screenshot()
                    return {"success": True, "url": self.state.url, "screenshot": screenshot}
            except:
                pass
            return {"success": False, "error": str(e)}

    async def read_content(self, selector: str = None) -> Dict[str, Any]:
        """Read text content from the page or a specific element."""
        if not self._page:
            return {"success": False, "error": "No page open"}

        try:
            if selector:
                element = await self._page.query_selector(selector)
                if element:
                    text = await element.inner_text()
                else:
                    text = f"Element not found: {selector}"
            else:
                text = await self._page.inner_text("body")

            # Truncate if too long
            if len(text) > 10000:
                text = text[:10000] + "\n... [truncated]"

            self.state.page_text = text
            screenshot = await self._capture_screenshot()
            return {
                "success": True,
                "text": text,
                "url": self.state.url,
                "screenshot": screenshot
            }
        except Exception as e:
            logger.error(f"Read failed: {e}")
            return {"success": False, "error": str(e)}

    async def scroll(self, direction: str = "down", amount: int = 500) -> Dict[str, Any]:
        """Scroll the page."""
        if not self._page:
            return {"success": False, "error": "No page open"}

        try:
            delta = amount if direction == "down" else -amount
            await self._page.mouse.wheel(0, delta)
            await asyncio.sleep(0.5)
            screenshot = await self._capture_screenshot()
            return {
                "success": True,
                "direction": direction,
                "screenshot": screenshot
            }
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return {"success": False, "error": str(e)}

    async def take_screenshot(self) -> Dict[str, Any]:
        """Take a screenshot."""
        screenshot = await self._capture_screenshot()
        return {
            "success": screenshot is not None,
            "screenshot": screenshot,
            "url": self.state.url,
            "title": self.state.title
        }

    async def get_page_html(self) -> str:
        """Get the full page HTML."""
        if not self._page:
            return ""
        try:
            return await self._page.content()
        except:
            return ""

    # ========================================================================
    # TOOL EXECUTION — Called by ExecutorAgent via tool registry
    # ========================================================================

    async def execute_tool(self, tool_name: str, parameters: Dict) -> Dict[str, Any]:
        """Execute a browser tool by name. Returns result with optional screenshot."""
        handlers = {
            "browser_navigate": lambda p: self.navigate(p.get("url", "")),
            "browser_click": lambda p: self.click(
                selector=p.get("selector"),
                x=p.get("x"),
                y=p.get("y")
            ),
            "browser_type": lambda p: self.type_text(
                selector=p.get("selector", ""),
                text=p.get("text", ""),
                press_enter=p.get("press_enter", False)
            ),
            "browser_read": lambda p: self.read_content(p.get("selector")),
            "browser_scroll": lambda p: self.scroll(
                direction=p.get("direction", "down"),
                amount=p.get("amount", 500)
            ),
            "browser_screenshot": lambda p: self.take_screenshot(),
            "browser_done": lambda p: self._done(p.get("summary", "")),
        }

        handler = handlers.get(tool_name)
        if not handler:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

        return await handler(parameters)

    async def _done(self, summary: str) -> Dict[str, Any]:
        """Mark browser task as done."""
        screenshot = await self._capture_screenshot()
        return {
            "success": True,
            "summary": summary,
            "screenshot": screenshot,
            "done": True
        }

    def get_tool_handlers(self) -> Dict[str, Callable]:
        """Get tool handlers for registration with ExecutorAgent."""
        return {
            "browser_navigate": lambda **p: self.navigate(p.get("url", "")),
            "browser_click": lambda **p: self.click(
                selector=p.get("selector"),
                x=p.get("x"),
                y=p.get("y")
            ),
            "browser_type": lambda **p: self.type_text(
                selector=p.get("selector", ""),
                text=p.get("text", ""),
                press_enter=p.get("press_enter", False)
            ),
            "browser_read": lambda **p: self.read_content(p.get("selector")),
            "browser_scroll": lambda **p: self.scroll(
                direction=p.get("direction", "down"),
                amount=p.get("amount", 500)
            ),
            "browser_screenshot": lambda **p: self.take_screenshot(),
            "browser_done": lambda **p: self._done(p.get("summary", "")),
        }
