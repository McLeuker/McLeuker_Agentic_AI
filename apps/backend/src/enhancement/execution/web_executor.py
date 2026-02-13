"""
Web Executor — True end-to-end web automation
================================================
Executes web-based tasks using Playwright browser engine.
Provides real-time screen updates, element interaction,
form filling, login flows, and content extraction.

Capabilities:
- Navigate to any URL
- Click elements by selector, text, or coordinates
- Type text into inputs
- Fill forms with multiple fields
- Read and extract page content
- Take screenshots for real-time display
- Handle login flows
- Download and upload files
- Execute JavaScript
- Wait for elements/conditions
"""

import asyncio
import base64
import json
import logging
import os
import re
from typing import Dict, List, Optional, Any, AsyncGenerator, Callable
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class WebAction:
    """A single web action to execute."""
    action: str  # navigate, click, type, scroll, read, screenshot, wait, fill_form, execute_js
    params: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    timeout: float = 30.0


@dataclass
class WebActionResult:
    """Result of a web action."""
    success: bool
    action: str
    data: Any = None
    screenshot: Optional[str] = None  # base64 encoded
    page_content: Optional[str] = None
    page_url: Optional[str] = None
    page_title: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "success": self.success,
            "action": self.action,
            "page_url": self.page_url,
            "page_title": self.page_title,
            "execution_time_ms": self.execution_time_ms,
        }
        if self.data:
            result["data"] = self.data
        if self.screenshot:
            result["screenshot"] = self.screenshot[:100] + "..."  # Truncate for logging
        if self.page_content:
            result["page_content_length"] = len(self.page_content)
        if self.error:
            result["error"] = self.error
        return result


class WebExecutor:
    """
    Executes web automation tasks using Playwright.

    Provides a high-level interface for web interaction that the
    execution engine uses to carry out user tasks.
    """

    def __init__(self, browser_tools=None):
        """
        Initialize the web executor.

        Args:
            browser_tools: Existing browser tools instance from the main app
        """
        self.browser_tools = browser_tools
        self._browser = None
        self._page = None
        self._context = None
        self._playwright = None
        self._initialized = False
        self._screenshot_callback: Optional[Callable] = None

    def set_screenshot_callback(self, callback: Callable):
        """Set callback for real-time screenshot streaming."""
        self._screenshot_callback = callback

    async def initialize(self):
        """Initialize the Playwright browser if not using existing tools."""
        if self._initialized:
            return

        if self.browser_tools:
            self._initialized = True
            return

        try:
            from playwright.async_api import async_playwright

            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ]
            )
            self._context = await self._browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )
            self._page = await self._context.new_page()
            self._initialized = True
            logger.info("WebExecutor: Playwright browser initialized")
        except ImportError:
            logger.warning("Playwright not installed. Web execution limited to browser_tools.")
        except Exception as e:
            logger.error("Failed to initialize Playwright: %s", e)

    async def cleanup(self):
        """Clean up browser resources."""
        if self._page:
            await self._page.close()
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._initialized = False

    async def execute_action(self, action: WebAction) -> WebActionResult:
        """
        Execute a single web action.

        Args:
            action: The WebAction to execute

        Returns:
            WebActionResult with the outcome
        """
        await self.initialize()

        start_time = datetime.now()

        action_map = {
            "navigate": self._navigate,
            "click": self._click,
            "type": self._type_text,
            "scroll": self._scroll,
            "read": self._read_page,
            "screenshot": self._take_screenshot,
            "wait": self._wait_for,
            "fill_form": self._fill_form,
            "execute_js": self._execute_js,
            "extract": self._extract_data,
            "login": self._login_flow,
            "download": self._download,
            "select": self._select_option,
        }

        handler = action_map.get(action.action)
        if not handler:
            return WebActionResult(
                success=False,
                action=action.action,
                error=f"Unknown action: {action.action}",
            )

        try:
            result = await asyncio.wait_for(
                handler(action.params),
                timeout=action.timeout,
            )
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            result.execution_time_ms = elapsed
            return result
        except asyncio.TimeoutError:
            return WebActionResult(
                success=False,
                action=action.action,
                error=f"Action timed out after {action.timeout}s",
                execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
            )
        except Exception as e:
            logger.exception("Web action failed: %s", e)
            return WebActionResult(
                success=False,
                action=action.action,
                error=str(e),
                execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
            )

    async def execute_sequence(
        self, actions: List[WebAction]
    ) -> AsyncGenerator[WebActionResult, None]:
        """Execute a sequence of web actions, yielding results."""
        for action in actions:
            result = await self.execute_action(action)
            yield result
            if not result.success:
                logger.warning("Action %s failed: %s", action.action, result.error)
                break

    async def _navigate(self, params: Dict[str, Any]) -> WebActionResult:
        """Navigate to a URL."""
        url = params.get("url", "")
        if not url:
            return WebActionResult(success=False, action="navigate", error="No URL provided")

        if self.browser_tools:
            result = await self.browser_tools.navigate({"url": url})
            screenshot = await self._get_screenshot()
            return WebActionResult(
                success=not result.get("error"),
                action="navigate",
                page_url=url,
                page_title=result.get("title", ""),
                page_content=result.get("content", ""),
                screenshot=screenshot,
                error=result.get("error"),
            )

        if self._page:
            await self._page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await self._page.wait_for_load_state("networkidle", timeout=10000)
            title = await self._page.title()
            content = await self._page.content()
            screenshot = await self._get_screenshot()
            return WebActionResult(
                success=True,
                action="navigate",
                page_url=url,
                page_title=title,
                page_content=content[:5000],
                screenshot=screenshot,
            )

        return WebActionResult(
            success=False, action="navigate", error="No browser available"
        )

    async def _click(self, params: Dict[str, Any]) -> WebActionResult:
        """Click an element."""
        selector = params.get("selector", "")
        text = params.get("text", "")
        x = params.get("x")
        y = params.get("y")

        if self.browser_tools:
            result = await self.browser_tools.click(params)
            screenshot = await self._get_screenshot()
            return WebActionResult(
                success=not result.get("error"),
                action="click",
                screenshot=screenshot,
                error=result.get("error"),
            )

        if self._page:
            try:
                if x is not None and y is not None:
                    await self._page.mouse.click(float(x), float(y))
                elif text:
                    await self._page.click(f"text={text}", timeout=10000)
                elif selector:
                    await self._page.click(selector, timeout=10000)
                else:
                    return WebActionResult(
                        success=False, action="click",
                        error="No selector, text, or coordinates provided"
                    )
                await asyncio.sleep(0.5)
                screenshot = await self._get_screenshot()
                return WebActionResult(
                    success=True, action="click", screenshot=screenshot
                )
            except Exception as e:
                return WebActionResult(
                    success=False, action="click", error=str(e)
                )

        return WebActionResult(
            success=False, action="click", error="No browser available"
        )

    async def _type_text(self, params: Dict[str, Any]) -> WebActionResult:
        """Type text into an input field."""
        selector = params.get("selector", "")
        text = params.get("text", "")
        clear_first = params.get("clear_first", True)
        press_enter = params.get("press_enter", False)

        if self.browser_tools:
            result = await self.browser_tools.type_text(params)
            screenshot = await self._get_screenshot()
            return WebActionResult(
                success=not result.get("error"),
                action="type",
                screenshot=screenshot,
                error=result.get("error"),
            )

        if self._page:
            try:
                if clear_first:
                    await self._page.fill(selector, text, timeout=10000)
                else:
                    await self._page.type(selector, text, timeout=10000)
                if press_enter:
                    await self._page.press(selector, "Enter")
                screenshot = await self._get_screenshot()
                return WebActionResult(
                    success=True, action="type", screenshot=screenshot
                )
            except Exception as e:
                return WebActionResult(
                    success=False, action="type", error=str(e)
                )

        return WebActionResult(
            success=False, action="type", error="No browser available"
        )

    async def _scroll(self, params: Dict[str, Any]) -> WebActionResult:
        """Scroll the page."""
        direction = params.get("direction", "down")
        amount = params.get("amount", 500)

        if self._page:
            if direction == "down":
                await self._page.evaluate(f"window.scrollBy(0, {amount})")
            elif direction == "up":
                await self._page.evaluate(f"window.scrollBy(0, -{amount})")
            screenshot = await self._get_screenshot()
            return WebActionResult(
                success=True, action="scroll", screenshot=screenshot
            )

        return WebActionResult(
            success=False, action="scroll", error="No browser available"
        )

    async def _read_page(self, params: Dict[str, Any]) -> WebActionResult:
        """Read page content."""
        selector = params.get("selector", "body")

        if self.browser_tools:
            result = await self.browser_tools.read_page(params)
            return WebActionResult(
                success=not result.get("error"),
                action="read",
                data=result.get("content", ""),
                page_content=result.get("content", ""),
                error=result.get("error"),
            )

        if self._page:
            try:
                content = await self._page.inner_text(selector, timeout=10000)
                url = self._page.url
                title = await self._page.title()
                return WebActionResult(
                    success=True,
                    action="read",
                    data=content[:10000],
                    page_content=content[:10000],
                    page_url=url,
                    page_title=title,
                )
            except Exception as e:
                return WebActionResult(
                    success=False, action="read", error=str(e)
                )

        return WebActionResult(
            success=False, action="read", error="No browser available"
        )

    async def _take_screenshot(self, params: Dict[str, Any]) -> WebActionResult:
        """Take a screenshot of the current page."""
        screenshot = await self._get_screenshot()
        if screenshot:
            return WebActionResult(
                success=True, action="screenshot", screenshot=screenshot
            )
        return WebActionResult(
            success=False, action="screenshot", error="Could not take screenshot"
        )

    async def _wait_for(self, params: Dict[str, Any]) -> WebActionResult:
        """Wait for an element or condition."""
        selector = params.get("selector", "")
        timeout = params.get("timeout", 10)
        state = params.get("state", "visible")

        if self._page and selector:
            try:
                await self._page.wait_for_selector(
                    selector, state=state, timeout=timeout * 1000
                )
                return WebActionResult(success=True, action="wait")
            except Exception as e:
                return WebActionResult(
                    success=False, action="wait", error=str(e)
                )

        await asyncio.sleep(timeout)
        return WebActionResult(success=True, action="wait")

    async def _fill_form(self, params: Dict[str, Any]) -> WebActionResult:
        """Fill a form with multiple fields."""
        fields = params.get("fields", {})
        submit_selector = params.get("submit_selector", "")

        if self._page:
            try:
                for selector, value in fields.items():
                    await self._page.fill(selector, str(value), timeout=5000)
                    await asyncio.sleep(0.2)

                if submit_selector:
                    await self._page.click(submit_selector, timeout=5000)
                    await asyncio.sleep(1)

                screenshot = await self._get_screenshot()
                return WebActionResult(
                    success=True, action="fill_form", screenshot=screenshot
                )
            except Exception as e:
                return WebActionResult(
                    success=False, action="fill_form", error=str(e)
                )

        return WebActionResult(
            success=False, action="fill_form", error="No browser available"
        )

    async def _execute_js(self, params: Dict[str, Any]) -> WebActionResult:
        """Execute JavaScript on the page."""
        script = params.get("script", "")

        if self._page:
            try:
                result = await self._page.evaluate(script)
                return WebActionResult(
                    success=True, action="execute_js", data=result
                )
            except Exception as e:
                return WebActionResult(
                    success=False, action="execute_js", error=str(e)
                )

        return WebActionResult(
            success=False, action="execute_js", error="No browser available"
        )

    async def _extract_data(self, params: Dict[str, Any]) -> WebActionResult:
        """Extract structured data from the page."""
        selectors = params.get("selectors", {})

        if self._page:
            try:
                extracted = {}
                for key, selector in selectors.items():
                    try:
                        element = await self._page.query_selector(selector)
                        if element:
                            extracted[key] = await element.inner_text()
                    except Exception:
                        extracted[key] = None
                return WebActionResult(
                    success=True, action="extract", data=extracted
                )
            except Exception as e:
                return WebActionResult(
                    success=False, action="extract", error=str(e)
                )

        return WebActionResult(
            success=False, action="extract", error="No browser available"
        )

    async def _login_flow(self, params: Dict[str, Any]) -> WebActionResult:
        """Execute a login flow."""
        url = params.get("url", "")
        username_selector = params.get("username_selector", "")
        password_selector = params.get("password_selector", "")
        submit_selector = params.get("submit_selector", "")
        username = params.get("username", "")
        password = params.get("password", "")

        if self._page:
            try:
                if url:
                    await self._page.goto(url, wait_until="domcontentloaded")
                    await asyncio.sleep(1)

                if username_selector and username:
                    await self._page.fill(username_selector, username)
                if password_selector and password:
                    await self._page.fill(password_selector, password)
                if submit_selector:
                    await self._page.click(submit_selector)
                    await asyncio.sleep(2)

                screenshot = await self._get_screenshot()
                current_url = self._page.url
                return WebActionResult(
                    success=True,
                    action="login",
                    page_url=current_url,
                    screenshot=screenshot,
                )
            except Exception as e:
                return WebActionResult(
                    success=False, action="login", error=str(e)
                )

        return WebActionResult(
            success=False, action="login", error="No browser available"
        )

    async def _download(self, params: Dict[str, Any]) -> WebActionResult:
        """Download a file."""
        url = params.get("url", "")
        selector = params.get("selector", "")

        if self._page:
            try:
                async with self._page.expect_download(timeout=30000) as download_info:
                    if selector:
                        await self._page.click(selector)
                    elif url:
                        await self._page.goto(url)
                download = await download_info.value
                path = await download.path()
                filename = download.suggested_filename
                return WebActionResult(
                    success=True,
                    action="download",
                    data={"path": str(path), "filename": filename},
                )
            except Exception as e:
                return WebActionResult(
                    success=False, action="download", error=str(e)
                )

        return WebActionResult(
            success=False, action="download", error="No browser available"
        )

    async def _select_option(self, params: Dict[str, Any]) -> WebActionResult:
        """Select an option from a dropdown."""
        selector = params.get("selector", "")
        value = params.get("value", "")
        label = params.get("label", "")

        if self._page:
            try:
                if label:
                    await self._page.select_option(selector, label=label)
                else:
                    await self._page.select_option(selector, value=value)
                screenshot = await self._get_screenshot()
                return WebActionResult(
                    success=True, action="select", screenshot=screenshot
                )
            except Exception as e:
                return WebActionResult(
                    success=False, action="select", error=str(e)
                )

        return WebActionResult(
            success=False, action="select", error="No browser available"
        )

    async def _get_screenshot(self) -> Optional[str]:
        """Take a screenshot and return as base64."""
        if self._page:
            try:
                screenshot_bytes = await self._page.screenshot(type="jpeg", quality=70)
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
                if self._screenshot_callback:
                    await self._screenshot_callback(screenshot_b64)
                return screenshot_b64
            except Exception:
                pass
        return None
