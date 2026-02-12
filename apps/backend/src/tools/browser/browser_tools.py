"""
Browser Tools — Web Automation for Agentic Engine
===================================================

Wraps BrowserEngineV2 to provide browser capabilities:
- Navigation
- Element interaction (click, type, scroll)
- Screenshot capture
- Text extraction
- Form filling
"""

import base64
import logging
from typing import Dict, List, Optional, Any, Callable

logger = logging.getLogger(__name__)


class BrowserTools:
    """
    Browser tool implementations that wrap BrowserEngineV2.

    Provides high-level browser operations for the agentic engine.
    """

    def __init__(self, browser_engine=None):
        """
        Initialize browser tools.

        Args:
            browser_engine: BrowserEngineV2 instance
        """
        self.browser_engine = browser_engine
        self._screenshot_callback: Optional[Callable] = None

    def set_browser_engine(self, browser_engine):
        """Set the browser engine (called during startup)."""
        self.browser_engine = browser_engine

    def set_screenshot_callback(self, callback: Callable):
        """Set callback for screenshot streaming."""
        self._screenshot_callback = callback

    async def navigate(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Navigate to a URL."""
        url = params.get("url", "")

        if not self.browser_engine:
            return {"error": "Browser engine not available", "url": url}

        try:
            result = await self.browser_engine.navigate(url)

            # Stream screenshot if callback is set
            if self._screenshot_callback and result.get("screenshot"):
                await self._screenshot_callback({
                    "type": "browser.navigated",
                    "url": url,
                    "title": result.get("title", ""),
                    "screenshot": result.get("screenshot", ""),
                })

            return result

        except Exception as e:
            logger.exception(f"Browser navigate error: {e}")
            return {"error": str(e), "url": url}

    async def click(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Click an element on the page."""
        if not self.browser_engine:
            return {"error": "Browser engine not available"}

        try:
            selector = params.get("selector", "")
            x = params.get("x")
            y = params.get("y")

            if x is not None and y is not None:
                result = await self.browser_engine.click(x=int(x), y=int(y))
            elif selector:
                result = await self.browser_engine.click(selector=selector)
            else:
                return {"error": "No selector or coordinates provided"}

            if self._screenshot_callback and result.get("screenshot"):
                await self._screenshot_callback({
                    "type": "browser.clicked",
                    "screenshot": result.get("screenshot", ""),
                })

            return result

        except Exception as e:
            logger.exception(f"Browser click error: {e}")
            return {"error": str(e)}

    async def type_text(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Type text into an input field."""
        if not self.browser_engine:
            return {"error": "Browser engine not available"}

        try:
            text = params.get("text", "")
            selector = params.get("selector", "")

            result = await self.browser_engine.type_text(selector=selector, text=text)

            if self._screenshot_callback and result.get("screenshot"):
                await self._screenshot_callback({
                    "type": "browser.typed",
                    "screenshot": result.get("screenshot", ""),
                })

            return result

        except Exception as e:
            logger.exception(f"Browser type error: {e}")
            return {"error": str(e)}

    async def screenshot(self, params: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Take a screenshot of the current page."""
        if not self.browser_engine:
            return {"error": "Browser engine not available"}

        try:
            result = await self.browser_engine.screenshot()

            if self._screenshot_callback and result.get("screenshot"):
                await self._screenshot_callback({
                    "type": "browser.screenshot",
                    "screenshot": result.get("screenshot", ""),
                })

            return result

        except Exception as e:
            logger.exception(f"Browser screenshot error: {e}")
            return {"error": str(e)}

    async def extract_text(self, params: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract text content from the current page."""
        if not self.browser_engine:
            return {"error": "Browser engine not available"}

        try:
            result = await self.browser_engine.extract_text(
                selector=params.get("selector") if params else None
            )
            return result

        except Exception as e:
            logger.exception(f"Browser extract error: {e}")
            return {"error": str(e)}

    async def scroll(self, params: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Scroll the page."""
        if not self.browser_engine:
            return {"error": "Browser engine not available"}

        try:
            direction = params.get("direction", "down") if params else "down"
            amount = params.get("amount", 500) if params else 500

            result = await self.browser_engine.scroll(direction=direction, amount=amount)

            if self._screenshot_callback and result.get("screenshot"):
                await self._screenshot_callback({
                    "type": "browser.scrolled",
                    "screenshot": result.get("screenshot", ""),
                })

            return result

        except Exception as e:
            logger.exception(f"Browser scroll error: {e}")
            return {"error": str(e)}

    def get_tools_list(self) -> List[Dict[str, Any]]:
        """Get list of available browser tools."""
        return [
            {"name": "browser_navigate", "description": "Navigate to a URL"},
            {"name": "browser_click", "description": "Click an element"},
            {"name": "browser_type", "description": "Type text into an input"},
            {"name": "browser_screenshot", "description": "Take a screenshot"},
            {"name": "browser_extract_text", "description": "Extract page text"},
            {"name": "browser_scroll", "description": "Scroll the page"},
        ]
