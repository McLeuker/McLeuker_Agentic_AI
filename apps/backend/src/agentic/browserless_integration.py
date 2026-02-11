"""
Browserless Integration for Web Automation
============================================

Provides headless browser capabilities via Browserless.io API:
- Page navigation and content extraction
- Screenshot capture
- PDF generation
- JavaScript evaluation
- Structured data scraping
- Multi-step browser action sequences
"""

import httpx
import os
import json
import base64
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class BrowserResult:
    """Result from browser operation"""
    success: bool
    url: Optional[str] = None
    content: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    screenshot: Optional[bytes] = None
    pdf: Optional[bytes] = None
    error: Optional[str] = None
    execution_time_ms: float = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BrowserAction:
    """Browser action to execute"""
    type: str  # navigate, click, type, screenshot, pdf, evaluate, scrape
    selector: Optional[str] = None
    value: Optional[str] = None
    url: Optional[str] = None
    options: Optional[Dict[str, Any]] = None


class BrowserlessClient:
    """
    Browserless.io client for headless browser automation.

    Provides:
    - Page navigation with content extraction
    - Screenshot and PDF capture
    - JavaScript evaluation
    - Structured data scraping
    - Multi-step action sequences
    """

    BASE_URL = "https://production-sfo.browserless.io"

    def __init__(self, api_key: Optional[str] = None, timeout: int = 30):
        self.api_key = api_key or os.getenv("BROWSERLESS_API_KEY", "")
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        self._available = bool(self.api_key)

        if self._available:
            logger.info("Browserless client initialized")
        else:
            logger.warning("Browserless API key not set")

    @property
    def available(self) -> bool:
        return self._available

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Basic {self.api_key}",
        }

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    async def navigate(
        self,
        url: str,
        wait_for: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> BrowserResult:
        """Navigate to a URL and extract page content."""
        start_time = datetime.now()

        try:
            payload: Dict[str, Any] = {
                "url": url,
                "gotoOptions": {"waitUntil": "networkidle2", "timeout": (timeout or self.timeout) * 1000},
            }
            if wait_for:
                payload["waitForSelector"] = {"selector": wait_for, "timeout": 10000}

            response = await self.client.post(
                f"{self.BASE_URL}/content",
                headers=self._headers(),
                json=payload,
                timeout=timeout or self.timeout,
            )

            exec_time = (datetime.now() - start_time).total_seconds() * 1000

            if response.status_code == 200:
                return BrowserResult(
                    success=True,
                    url=url,
                    content=response.text,
                    execution_time_ms=exec_time,
                )
            else:
                return BrowserResult(
                    success=False,
                    url=url,
                    error=f"HTTP {response.status_code}: {response.text[:200]}",
                    execution_time_ms=exec_time,
                )

        except Exception as e:
            logger.error(f"Browserless navigate error: {e}")
            return BrowserResult(
                success=False,
                url=url,
                error=str(e),
                execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
            )

    # ------------------------------------------------------------------
    # Screenshot
    # ------------------------------------------------------------------

    async def screenshot(
        self,
        url: str,
        full_page: bool = True,
        format: str = "png",
    ) -> BrowserResult:
        """Capture screenshot of a page."""
        start_time = datetime.now()

        try:
            payload = {
                "url": url,
                "gotoOptions": {"waitUntil": "networkidle2"},
                "options": {"fullPage": full_page, "type": format},
            }

            response = await self.client.post(
                f"{self.BASE_URL}/screenshot",
                headers=self._headers(),
                json=payload,
            )

            exec_time = (datetime.now() - start_time).total_seconds() * 1000

            if response.status_code == 200:
                return BrowserResult(
                    success=True,
                    url=url,
                    screenshot=response.content,
                    execution_time_ms=exec_time,
                    metadata={"format": format, "full_page": full_page},
                )
            else:
                return BrowserResult(
                    success=False,
                    url=url,
                    error=f"HTTP {response.status_code}",
                    execution_time_ms=exec_time,
                )

        except Exception as e:
            logger.error(f"Browserless screenshot error: {e}")
            return BrowserResult(success=False, url=url, error=str(e))

    # ------------------------------------------------------------------
    # PDF
    # ------------------------------------------------------------------

    async def pdf(
        self,
        url: str,
        full_page: bool = True,
    ) -> BrowserResult:
        """Generate PDF of a page."""
        start_time = datetime.now()

        try:
            payload = {
                "url": url,
                "gotoOptions": {"waitUntil": "networkidle2"},
                "options": {"printBackground": True, "format": "A4"},
            }

            response = await self.client.post(
                f"{self.BASE_URL}/pdf",
                headers=self._headers(),
                json=payload,
            )

            exec_time = (datetime.now() - start_time).total_seconds() * 1000

            if response.status_code == 200:
                return BrowserResult(
                    success=True,
                    url=url,
                    pdf=response.content,
                    execution_time_ms=exec_time,
                )
            else:
                return BrowserResult(
                    success=False,
                    url=url,
                    error=f"HTTP {response.status_code}",
                    execution_time_ms=exec_time,
                )

        except Exception as e:
            logger.error(f"Browserless PDF error: {e}")
            return BrowserResult(success=False, url=url, error=str(e))

    # ------------------------------------------------------------------
    # JavaScript evaluation
    # ------------------------------------------------------------------

    async def evaluate(
        self,
        url: str,
        javascript: str,
        wait_for: Optional[str] = None,
    ) -> BrowserResult:
        """Evaluate JavaScript on a page."""
        start_time = datetime.now()

        try:
            payload: Dict[str, Any] = {
                "url": url,
                "gotoOptions": {"waitUntil": "networkidle2"},
                "code": f"module.exports = async ({{ page }}) => {{ return await page.evaluate({javascript}); }};",
            }

            response = await self.client.post(
                f"{self.BASE_URL}/function",
                headers=self._headers(),
                json=payload,
            )

            exec_time = (datetime.now() - start_time).total_seconds() * 1000

            if response.status_code == 200:
                try:
                    data = response.json()
                except Exception:
                    data = {"raw": response.text}
                return BrowserResult(
                    success=True,
                    url=url,
                    data=data,
                    execution_time_ms=exec_time,
                )
            else:
                return BrowserResult(
                    success=False,
                    url=url,
                    error=f"HTTP {response.status_code}: {response.text[:200]}",
                    execution_time_ms=exec_time,
                )

        except Exception as e:
            logger.error(f"Browserless evaluate error: {e}")
            return BrowserResult(success=False, url=url, error=str(e))

    # ------------------------------------------------------------------
    # Structured scraping
    # ------------------------------------------------------------------

    async def scrape(
        self,
        url: str,
        selectors: Dict[str, str],
        wait_for: Optional[str] = None,
    ) -> BrowserResult:
        """Scrape structured data from a page using CSS selectors."""
        start_time = datetime.now()

        try:
            # Build JavaScript to extract data
            selector_parts = []
            for key, selector in selectors.items():
                selector_parts.append(
                    f"data['{key}'] = Array.from(document.querySelectorAll('{selector}')).map(el => el.textContent.trim());"
                )
            selector_script = "\n".join(selector_parts)

            script = f"""
            () => {{
                const data = {{}};
                {selector_script}
                return data;
            }}
            """

            result = await self.evaluate(url, script, wait_for)

            if result.success and result.data:
                return BrowserResult(
                    success=True,
                    url=url,
                    data=result.data.get("data", result.data),
                    execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                )
            else:
                return result

        except Exception as e:
            logger.error(f"Browserless scraping error: {e}")
            return BrowserResult(
                success=False,
                url=url,
                error=str(e),
                execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
            )

    # ------------------------------------------------------------------
    # Deep content extraction (for SearchLayer integration)
    # ------------------------------------------------------------------

    async def deep_extract(
        self,
        url: str,
        extract_links: bool = True,
        extract_images: bool = False,
    ) -> Dict[str, Any]:
        """
        Deep content extraction from a URL.
        Used by SearchLayer for enhanced web scraping.
        """
        result = await self.navigate(url)

        if not result.success:
            return {"success": False, "error": result.error, "url": url}

        # Parse HTML content
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(result.content, "html.parser")

            # Remove script/style
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)

            extracted: Dict[str, Any] = {
                "success": True,
                "url": url,
                "title": soup.title.string if soup.title else "",
                "text": text[:10000],
                "text_length": len(text),
            }

            if extract_links:
                links = []
                for a in soup.find_all("a", href=True)[:50]:
                    links.append({"text": a.get_text(strip=True)[:100], "href": a["href"]})
                extracted["links"] = links

            if extract_images:
                images = []
                for img in soup.find_all("img", src=True)[:20]:
                    images.append({"alt": img.get("alt", ""), "src": img["src"]})
                extracted["images"] = images

            return extracted

        except ImportError:
            return {
                "success": True,
                "url": url,
                "text": result.content[:10000] if result.content else "",
                "note": "BeautifulSoup not available for parsing",
            }
        except Exception as e:
            return {"success": False, "url": url, "error": str(e)}

    # ------------------------------------------------------------------
    # Multi-step actions
    # ------------------------------------------------------------------

    async def execute_actions(
        self,
        url: str,
        actions: List[BrowserAction],
    ) -> List[BrowserResult]:
        """Execute a sequence of browser actions."""
        results = []
        current_url = url

        for action in actions:
            try:
                if action.type == "navigate":
                    result = await self.navigate(action.url or current_url)
                    if result.url:
                        current_url = result.url
                elif action.type == "screenshot":
                    full_page = action.options.get("full_page", True) if action.options else True
                    result = await self.screenshot(current_url, full_page=full_page)
                elif action.type == "pdf":
                    result = await self.pdf(current_url)
                elif action.type == "evaluate":
                    result = await self.evaluate(current_url, action.value or "")
                elif action.type == "scrape":
                    selectors = action.options.get("selectors", {}) if action.options else {}
                    result = await self.scrape(current_url, selectors)
                else:
                    result = BrowserResult(success=False, error=f"Unknown action type: {action.type}")

                results.append(result)

                if not result.success:
                    break

            except Exception as e:
                results.append(BrowserResult(success=False, error=str(e)))
                break

        return results

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


# Global instance
_browserless_client: Optional[BrowserlessClient] = None


def get_browserless() -> Optional[BrowserlessClient]:
    """Get global Browserless client."""
    return _browserless_client


def init_browserless(api_key: Optional[str] = None) -> BrowserlessClient:
    """Initialize global Browserless client."""
    global _browserless_client
    _browserless_client = BrowserlessClient(api_key=api_key)
    return _browserless_client
