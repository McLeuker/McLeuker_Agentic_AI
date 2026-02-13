"""
Browser Engine V3 - Advanced Web Automation with Visual Understanding
======================================================================
Enhanced browser automation featuring:
- Visual element detection and understanding
- Intelligent element selection
- Session persistence
- Multi-page workflow management
- JavaScript execution
- Form understanding and auto-fill
- Screenshot analysis with kimi-2.5 vision

Integrates with existing BrowserEngine (V1) in src/agentic/browser_engine.py
as an enhanced layer. V1 continues to work for existing SSE flows.
"""

import asyncio
import base64
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin, urlparse
from uuid import uuid4

from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    ElementHandle,
    TimeoutError as PlaywrightTimeout,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class BrowserSessionV3:
    """Represents a browser session with state."""
    id: str = field(default_factory=lambda: str(uuid4()))
    context: Optional[BrowserContext] = None
    pages: List[Any] = field(default_factory=list)  # List[Page]
    current_page_index: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def current_page(self) -> Optional[Any]:
        if 0 <= self.current_page_index < len(self.pages):
            return self.pages[self.current_page_index]
        return None


@dataclass
class ElementInfo:
    """Information about a web element."""
    selector: str = ""
    tag_name: str = ""
    text: str = ""
    attributes: Dict[str, str] = field(default_factory=dict)
    bounding_box: Optional[Dict[str, float]] = None
    is_visible: bool = True
    is_interactive: bool = False
    element_type: Optional[str] = None
    confidence: float = 1.0


@dataclass
class PageInfoV3:
    """Information about the current page state."""
    url: str = ""
    title: str = ""
    screenshot: Optional[str] = None
    elements: List[ElementInfo] = field(default_factory=list)
    scroll_position: Dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0})
    viewport: Dict[str, int] = field(default_factory=lambda: {"width": 1280, "height": 720})

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "screenshot": self.screenshot,
            "scroll_position": self.scroll_position,
            "viewport": self.viewport,
            "element_count": len(self.elements),
        }


# ---------------------------------------------------------------------------
# Browser Engine V3
# ---------------------------------------------------------------------------

class BrowserEngineV3:
    """
    Advanced browser engine with visual understanding capabilities.

    Features:
    - Multi-session management
    - Visual element detection via kimi-2.5 vision
    - Intelligent selectors
    - Form understanding
    - JavaScript execution
    - Screenshot analysis
    """

    def __init__(
        self,
        headless: bool = True,
        viewport: Optional[Dict[str, int]] = None,
        user_agent: Optional[str] = None,
        llm_client: Optional[Any] = None,
    ):
        self.headless = headless
        self.viewport = viewport or {"width": 1280, "height": 720}
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.llm_client = llm_client

        self._playwright = None
        self._browser: Optional[Browser] = None
        self._sessions: Dict[str, BrowserSessionV3] = {}
        self._default_session_id: Optional[str] = None
        self._screenshot_callback: Optional[Callable] = None

        logger.info("BrowserEngineV3 initialized")

    # -- Lifecycle -------------------------------------------------------------

    async def initialize(self):
        if self._playwright is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--disable-gpu",
                    "--window-size=1280,720",
                ],
            )
            logger.info("BrowserEngineV3 browser launched")

    async def shutdown(self):
        for session in self._sessions.values():
            if session.context:
                try:
                    await session.context.close()
                except Exception:
                    pass
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._sessions.clear()
        logger.info("BrowserEngineV3 shutdown complete")

    def set_screenshot_callback(self, callback: Callable):
        self._screenshot_callback = callback

    async def _notify_screenshot(self, session_id: str, screenshot_b64: str, metadata: Optional[Dict] = None):
        if self._screenshot_callback:
            try:
                if asyncio.iscoroutinefunction(self._screenshot_callback):
                    await self._screenshot_callback(session_id, {
                        "screenshot": screenshot_b64,
                        "metadata": metadata or {},
                        "timestamp": datetime.utcnow().isoformat(),
                    })
                else:
                    self._screenshot_callback(session_id, {
                        "screenshot": screenshot_b64,
                        "metadata": metadata or {},
                        "timestamp": datetime.utcnow().isoformat(),
                    })
            except Exception as e:
                logger.error(f"Screenshot callback error: {e}")

    # -- Session management ----------------------------------------------------

    async def create_session(self, session_id: Optional[str] = None) -> str:
        await self.initialize()
        session = BrowserSessionV3(id=session_id or str(uuid4()))
        context = await self._browser.new_context(
            viewport=self.viewport,
            user_agent=self.user_agent,
            accept_downloads=True,
        )
        context.set_default_timeout(30000)
        context.set_default_navigation_timeout(30000)
        session.context = context
        page = await context.new_page()
        session.pages.append(page)
        self._sessions[session.id] = session
        if self._default_session_id is None:
            self._default_session_id = session.id
        logger.info(f"Created browser session: {session.id}")
        return session.id

    async def close_session(self, session_id: str):
        session = self._sessions.pop(session_id, None)
        if session and session.context:
            await session.context.close()
            logger.info(f"Closed browser session: {session_id}")

    def get_session(self, session_id: Optional[str] = None) -> Optional[BrowserSessionV3]:
        if session_id:
            return self._sessions.get(session_id)
        return self._sessions.get(self._default_session_id)

    # -- Navigation ------------------------------------------------------------

    async def navigate(
        self,
        url: str,
        session_id: Optional[str] = None,
        wait_until: str = "networkidle",
        timeout: int = 30000,
    ) -> Dict[str, Any]:
        session = self.get_session(session_id)
        if not session:
            session_id = await self.create_session(session_id)
            session = self.get_session(session_id)

        page = session.current_page
        if not page:
            return {"success": False, "error": "No page available in session"}

        try:
            logger.info(f"Navigating to: {url}")
            response = await page.goto(url, wait_until=wait_until, timeout=timeout)
            await page.wait_for_load_state("domcontentloaded")
            screenshot_b64 = await self._take_screenshot(page)
            await self._notify_screenshot(session.id, screenshot_b64, {"action": "navigate", "url": url})
            page_info = await self._get_page_info(page, screenshot_b64)
            session.last_activity = datetime.utcnow()
            return {
                "success": True,
                "url": page.url,
                "title": await page.title(),
                "status": response.status if response else None,
                "screenshot": screenshot_b64,
                "page_info": page_info.to_dict(),
            }
        except PlaywrightTimeout:
            return {"success": False, "error": "Navigation timeout", "url": url}
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return {"success": False, "error": str(e), "url": url}

    # -- Click -----------------------------------------------------------------

    async def click(
        self,
        selector: Optional[str] = None,
        element_description: Optional[str] = None,
        session_id: Optional[str] = None,
        timeout: int = 10000,
    ) -> Dict[str, Any]:
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": "No active session"}
        page = session.current_page
        if not page:
            return {"success": False, "error": "No active page"}
        try:
            element = None
            if selector:
                element = await page.query_selector(selector)
            if not element and element_description and self.llm_client:
                element = await self._find_element_visual(page, element_description)
            if not element:
                return {"success": False, "error": f"Element not found: {selector or element_description}"}
            await element.scroll_into_view_if_needed()
            await element.click(timeout=timeout)
            await asyncio.sleep(0.5)
            screenshot_b64 = await self._take_screenshot(page)
            await self._notify_screenshot(session.id, screenshot_b64, {"action": "click"})
            session.last_activity = datetime.utcnow()
            return {"success": True, "url": page.url, "title": await page.title(), "screenshot": screenshot_b64}
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return {"success": False, "error": str(e)}

    # -- Type ------------------------------------------------------------------

    async def type_text(
        self,
        text: str,
        selector: Optional[str] = None,
        element_description: Optional[str] = None,
        session_id: Optional[str] = None,
        clear_first: bool = True,
        submit: bool = False,
    ) -> Dict[str, Any]:
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": "No active session"}
        page = session.current_page
        if not page:
            return {"success": False, "error": "No active page"}
        try:
            element = None
            if selector:
                element = await page.query_selector(selector)
            if not element and element_description and self.llm_client:
                element = await self._find_element_visual(page, element_description)
            if not element:
                return {"success": False, "error": f"Input not found: {selector or element_description}"}
            await element.focus()
            if clear_first:
                await element.fill("")
            await element.type(text, delay=10)
            if submit:
                await element.press("Enter")
                await asyncio.sleep(0.5)
            screenshot_b64 = await self._take_screenshot(page)
            await self._notify_screenshot(session.id, screenshot_b64, {"action": "type"})
            session.last_activity = datetime.utcnow()
            return {"success": True, "text": text, "url": page.url, "screenshot": screenshot_b64}
        except Exception as e:
            logger.error(f"Type failed: {e}")
            return {"success": False, "error": str(e)}

    # -- Scroll ----------------------------------------------------------------

    async def scroll(
        self,
        direction: str = "down",
        amount: int = 500,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": "No active session"}
        page = session.current_page
        if not page:
            return {"success": False, "error": "No active page"}
        try:
            scroll_map = {
                "down": f"window.scrollBy(0, {amount})",
                "up": f"window.scrollBy(0, -{amount})",
                "right": f"window.scrollBy({amount}, 0)",
                "left": f"window.scrollBy(-{amount}, 0)",
            }
            await page.evaluate(scroll_map.get(direction, scroll_map["down"]))
            screenshot_b64 = await self._take_screenshot(page)
            await self._notify_screenshot(session.id, screenshot_b64, {"action": "scroll", "direction": direction})
            session.last_activity = datetime.utcnow()
            return {"success": True, "direction": direction, "amount": amount, "screenshot": screenshot_b64}
        except Exception as e:
            logger.error(f"Scroll failed: {e}")
            return {"success": False, "error": str(e)}

    # -- Text extraction -------------------------------------------------------

    async def extract_text(self, selector: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": "No active session"}
        page = session.current_page
        if not page:
            return {"success": False, "error": "No active page"}
        try:
            if selector:
                element = await page.query_selector(selector)
                text = await element.text_content() if element else None
                if text is None:
                    return {"success": False, "error": f"Element not found: {selector}"}
            else:
                text = await page.evaluate("() => document.body.innerText")
            return {"success": True, "text": text, "length": len(text) if text else 0}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # -- JavaScript execution --------------------------------------------------

    async def execute_javascript(self, script: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": "No active session"}
        page = session.current_page
        if not page:
            return {"success": False, "error": "No active page"}
        try:
            result = await page.evaluate(script)
            session.last_activity = datetime.utcnow()
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # -- Form fill -------------------------------------------------------------

    async def fill_form(
        self,
        fields: Dict[str, str],
        submit_selector: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": "No active session"}
        page = session.current_page
        if not page:
            return {"success": False, "error": "No active page"}
        results = []
        try:
            for sel, value in fields.items():
                element = await page.query_selector(sel)
                if element:
                    await element.fill(value)
                    results.append({"selector": sel, "success": True})
                else:
                    results.append({"selector": sel, "success": False, "error": "Not found"})
            if submit_selector:
                btn = await page.query_selector(submit_selector)
                if btn:
                    await btn.click()
                    await asyncio.sleep(1)
            screenshot_b64 = await self._take_screenshot(page)
            await self._notify_screenshot(session.id, screenshot_b64, {"action": "fill_form"})
            session.last_activity = datetime.utcnow()
            return {"success": all(r.get("success") for r in results), "fields": results, "screenshot": screenshot_b64}
        except Exception as e:
            return {"success": False, "error": str(e), "fields": results}

    # -- Page elements ---------------------------------------------------------

    async def get_page_elements(self, session_id: Optional[str] = None, interactive_only: bool = True) -> Dict[str, Any]:
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": "No active session"}
        page = session.current_page
        if not page:
            return {"success": False, "error": "No active page"}
        try:
            io_flag = "true" if interactive_only else "false"
            script = f"""
            () => {{
                const elements = [];
                const interactiveTags = ['a', 'button', 'input', 'select', 'textarea', 'form'];
                const allElements = document.querySelectorAll('*');
                allElements.forEach((el, index) => {{
                    const isInteractive = interactiveTags.includes(el.tagName.toLowerCase()) ||
                                         el.onclick ||
                                         el.getAttribute('role') === 'button';
                    if (!{io_flag} || isInteractive) {{
                        const rect = el.getBoundingClientRect();
                        elements.push({{
                            index: index,
                            tag: el.tagName.toLowerCase(),
                            text: el.innerText?.substring(0, 100) || '',
                            boundingBox: {{ x: rect.x, y: rect.y, width: rect.width, height: rect.height }},
                            isVisible: rect.width > 0 && rect.height > 0 && rect.top >= 0 && rect.left >= 0,
                            isInteractive: isInteractive,
                        }});
                    }}
                }});
                return elements;
            }}
            """
            elements = await page.evaluate(script)
            return {"success": True, "elements": elements, "count": len(elements)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # -- Visual page analysis --------------------------------------------------

    async def analyze_page(self, session_id: Optional[str] = None, question: Optional[str] = None) -> Dict[str, Any]:
        session = self.get_session(session_id)
        if not session:
            return {"success": False, "error": "No active session"}
        page = session.current_page
        if not page:
            return {"success": False, "error": "No active page"}
        if not self.llm_client:
            return {"success": False, "error": "LLM client not available"}
        try:
            screenshot_b64 = await self._take_screenshot(page)
            page_text = await page.evaluate("() => document.body.innerText")
            prompt = question or "Analyze this webpage and describe its main content, purpose, and key interactive elements."
            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"{prompt}\n\nPage text:\n{page_text[:2000]}..."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{screenshot_b64}"}},
                    ],
                }],
                temperature=0.5,
            )
            return {
                "success": True,
                "analysis": response.choices[0].message.content,
                "url": page.url,
                "title": await page.title(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # -- Internal helpers ------------------------------------------------------

    async def _take_screenshot(self, page, full_page: bool = False) -> str:
        try:
            screenshot_bytes = await page.screenshot(full_page=full_page, type="jpeg", quality=80)
            return base64.b64encode(screenshot_bytes).decode("utf-8")
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return ""

    async def _get_page_info(self, page, screenshot_b64: Optional[str] = None) -> PageInfoV3:
        return PageInfoV3(
            url=page.url,
            title=await page.title(),
            screenshot=screenshot_b64,
            viewport={"width": self.viewport["width"], "height": self.viewport["height"]},
        )

    async def _find_element_visual(self, page, description: str) -> Optional[ElementHandle]:
        """Find an element using kimi-2.5 vision capabilities."""
        if not self.llm_client:
            return None
        try:
            screenshot_b64 = await self._take_screenshot(page)
            elements_data = await self.get_page_elements()
            elements = elements_data.get("elements", [])[:20]
            prompt = f"""Given the following page elements and a screenshot, find the element that matches the description.

Description: "{description}"

Available elements:
{json.dumps(elements, indent=2)}

Respond with the index of the matching element, or -1 if not found.
Only respond with a number."""

            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{screenshot_b64}"}},
                    ],
                }],
                temperature=0.3,
            )
            result = response.choices[0].message.content.strip()
            match = re.search(r'-?\d+', result)
            if match:
                index = int(match.group())
                if 0 <= index < len(elements):
                    all_elements = await page.query_selector_all("*")
                    if index < len(all_elements):
                        return all_elements[index]
            return None
        except Exception as e:
            logger.error(f"Visual element finding failed: {e}")
            return None
