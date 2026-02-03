"""
V3.1 Action Layer
Web automation using Browserless.io and data extraction using Firecrawl.
"""

import asyncio
import aiohttp
import json
import base64
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from src.config.settings import settings


@dataclass
class ActionResult:
    """Result from a web action."""
    success: bool
    data: Any
    screenshot: Optional[str] = None
    error: Optional[str] = None


class BrowserlessAction:
    """
    Browserless.io integration for web automation.
    Allows the agent to browse, click, and interact with websites.
    """
    
    def __init__(self):
        self.api_key = settings.BROWSERLESS_API_KEY
        self.enabled = bool(self.api_key)
        self.base_url = "https://chrome.browserless.io"
    
    async def navigate_and_extract(self, url: str, wait_for: str = None) -> ActionResult:
        """Navigate to a URL and extract the page content."""
        if not self.enabled:
            return ActionResult(success=False, data=None, error="Browserless not configured")
        
        try:
            endpoint = f"{self.base_url}/content?token={self.api_key}"
            
            payload = {
                "url": url,
                "waitFor": wait_for or 3000,
                "gotoOptions": {
                    "waitUntil": "networkidle2",
                    "timeout": settings.BROWSERLESS_TIMEOUT * 1000
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, json=payload,
                                        timeout=aiohttp.ClientTimeout(total=settings.BROWSERLESS_TIMEOUT)) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        return ActionResult(success=False, data=None, error=f"Browserless error: {error_text}")
                    
                    content = await resp.text()
                    return ActionResult(success=True, data=content)
                    
        except Exception as e:
            return ActionResult(success=False, data=None, error=str(e))
    
    async def take_screenshot(self, url: str) -> ActionResult:
        """Take a screenshot of a webpage."""
        if not self.enabled:
            return ActionResult(success=False, data=None, error="Browserless not configured")
        
        try:
            endpoint = f"{self.base_url}/screenshot?token={self.api_key}"
            
            payload = {
                "url": url,
                "options": {
                    "fullPage": False,
                    "type": "png"
                },
                "gotoOptions": {
                    "waitUntil": "networkidle2",
                    "timeout": settings.BROWSERLESS_TIMEOUT * 1000
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, json=payload,
                                        timeout=aiohttp.ClientTimeout(total=settings.BROWSERLESS_TIMEOUT)) as resp:
                    if resp.status != 200:
                        return ActionResult(success=False, data=None, error="Screenshot failed")
                    
                    image_data = await resp.read()
                    base64_image = base64.b64encode(image_data).decode('utf-8')
                    return ActionResult(success=True, data=None, screenshot=base64_image)
                    
        except Exception as e:
            return ActionResult(success=False, data=None, error=str(e))
    
    async def execute_script(self, url: str, script: str) -> ActionResult:
        """Execute a custom script on a webpage."""
        if not self.enabled:
            return ActionResult(success=False, data=None, error="Browserless not configured")
        
        try:
            endpoint = f"{self.base_url}/function?token={self.api_key}"
            
            function_code = f"""
            module.exports = async ({{ page }}) => {{
                await page.goto('{url}', {{ waitUntil: 'networkidle2' }});
                const result = await page.evaluate(() => {{
                    {script}
                }});
                return result;
            }};
            """
            
            payload = {"code": function_code}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, json=payload,
                                        timeout=aiohttp.ClientTimeout(total=settings.BROWSERLESS_TIMEOUT)) as resp:
                    if resp.status != 200:
                        return ActionResult(success=False, data=None, error="Script execution failed")
                    
                    result = await resp.json()
                    return ActionResult(success=True, data=result)
                    
        except Exception as e:
            return ActionResult(success=False, data=None, error=str(e))


class FirecrawlExtractor:
    """
    Firecrawl integration for clean data extraction from websites.
    Converts any webpage into AI-readable markdown.
    """
    
    def __init__(self):
        self.api_key = settings.FIRECRAWL_API_KEY
        self.enabled = bool(self.api_key)
        self.base_url = "https://api.firecrawl.dev/v0"
    
    async def scrape(self, url: str) -> ActionResult:
        """Scrape a URL and return clean markdown content."""
        if not self.enabled:
            return ActionResult(success=False, data=None, error="Firecrawl not configured")
        
        try:
            endpoint = f"{self.base_url}/scrape"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "url": url,
                "pageOptions": {
                    "onlyMainContent": True,
                    "includeHtml": False
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, headers=headers, json=payload,
                                        timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        return ActionResult(success=False, data=None, error=f"Firecrawl error: {error_text}")
                    
                    data = await resp.json()
                    content = data.get("data", {}).get("markdown", "")
                    metadata = data.get("data", {}).get("metadata", {})
                    
                    return ActionResult(
                        success=True,
                        data={
                            "content": content,
                            "title": metadata.get("title", ""),
                            "description": metadata.get("description", ""),
                            "url": url
                        }
                    )
                    
        except Exception as e:
            return ActionResult(success=False, data=None, error=str(e))
    
    async def crawl_site(self, url: str, max_pages: int = 5) -> ActionResult:
        """Crawl multiple pages from a website."""
        if not self.enabled:
            return ActionResult(success=False, data=None, error="Firecrawl not configured")
        
        try:
            endpoint = f"{self.base_url}/crawl"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "url": url,
                "crawlerOptions": {
                    "limit": max_pages
                },
                "pageOptions": {
                    "onlyMainContent": True
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, headers=headers, json=payload,
                                        timeout=aiohttp.ClientTimeout(total=60)) as resp:
                    if resp.status != 200:
                        return ActionResult(success=False, data=None, error="Crawl failed")
                    
                    data = await resp.json()
                    job_id = data.get("jobId")
                    
                    # Poll for results
                    for _ in range(30):  # Max 30 attempts
                        await asyncio.sleep(2)
                        status_resp = await session.get(
                            f"{self.base_url}/crawl/status/{job_id}",
                            headers=headers
                        )
                        status_data = await status_resp.json()
                        
                        if status_data.get("status") == "completed":
                            return ActionResult(success=True, data=status_data.get("data", []))
                        elif status_data.get("status") == "failed":
                            return ActionResult(success=False, data=None, error="Crawl job failed")
                    
                    return ActionResult(success=False, data=None, error="Crawl timeout")
                    
        except Exception as e:
            return ActionResult(success=False, data=None, error=str(e))


class ActionLayer:
    """
    The V3.1 Action Layer
    Combines Browserless and Firecrawl for comprehensive web interaction.
    """
    
    def __init__(self):
        self.browserless = BrowserlessAction()
        self.firecrawl = FirecrawlExtractor()
    
    async def execute(self, query: str, context: Dict = None) -> Dict:
        """
        Execute a web action based on the query and context.
        Intelligently chooses between Browserless and Firecrawl.
        """
        
        # Determine the best tool for the job
        urls = context.get("urls", []) if context else []
        action_type = context.get("action_type", "extract") if context else "extract"
        
        results = []
        
        if action_type == "screenshot":
            # Take screenshots
            for url in urls[:3]:  # Limit to 3 screenshots
                result = await self.browserless.take_screenshot(url)
                if result.success:
                    results.append({
                        "url": url,
                        "screenshot": result.screenshot
                    })
        
        elif action_type == "interact":
            # Interactive browsing
            for url in urls[:2]:
                result = await self.browserless.navigate_and_extract(url)
                if result.success:
                    results.append({
                        "url": url,
                        "content": result.data
                    })
        
        else:
            # Default: Clean extraction using Firecrawl
            for url in urls[:5]:
                result = await self.firecrawl.scrape(url)
                if result.success:
                    results.append(result.data)
        
        return {
            "action_type": action_type,
            "results": results,
            "success": len(results) > 0
        }
    
    async def extract_from_url(self, url: str) -> Dict:
        """Extract clean content from a single URL."""
        # Try Firecrawl first (cleaner output)
        result = await self.firecrawl.scrape(url)
        if result.success:
            return result.data
        
        # Fallback to Browserless
        result = await self.browserless.navigate_and_extract(url)
        if result.success:
            return {"content": result.data, "url": url}
        
        return {"error": "Failed to extract content", "url": url}


# Global instance
action_layer = ActionLayer()
