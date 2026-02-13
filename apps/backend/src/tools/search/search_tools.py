"""
Search Tools — Web Search Integration for Agentic Engine
==========================================================

Wraps the existing SearchLayer to provide search capabilities:
- Multi-provider web search
- URL content fetching
- Result formatting
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class SearchTools:
    """
    Search tool implementations that wrap the existing SearchLayer.
    """

    def __init__(self, search_layer=None):
        """
        Initialize search tools.

        Args:
            search_layer: The existing SearchLayer from main.py
        """
        self.search_layer = search_layer

    def set_search_layer(self, search_layer):
        """Set the search layer (called during startup wiring)."""
        self.search_layer = search_layer

    async def web_search(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform a web search.

        Args:
            params: {"query": str, "num_results": int}
            context: Execution context

        Returns:
            Search results
        """
        query = params.get("query", "")
        num_results = params.get("num_results", 10)

        if not self.search_layer:
            return {"error": "Search layer not available", "results": [], "text": ""}

        try:
            results = await self.search_layer.search(
                query=query,
                sources=["web"],
                num_results=num_results,
            )

            return {
                "results": results.get("results", [])[:num_results],
                "text": results.get("combined_text", ""),
                "sources_count": len(results.get("results", [])),
                "query": query,
                "source": "search_layer",
            }

        except Exception as e:
            logger.exception(f"Web search error: {e}")
            return {"error": str(e), "results": [], "text": ""}

    async def fetch_url(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Fetch content from a URL.

        Args:
            params: {"url": str}
            context: Execution context

        Returns:
            URL content
        """
        url = params.get("url", "")

        try:
            import httpx
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                response = await client.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; McLeukerBot/1.0)"
                })

                content_type = response.headers.get("content-type", "")

                if "text/html" in content_type:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, "html.parser")

                    # Remove scripts and styles
                    for tag in soup(["script", "style", "nav", "footer", "header"]):
                        tag.decompose()

                    text = soup.get_text(separator="\n", strip=True)
                    title = soup.title.string if soup.title else ""

                    return {
                        "url": url,
                        "title": title,
                        "text": text[:10000],
                        "status_code": response.status_code,
                    }
                else:
                    return {
                        "url": url,
                        "text": response.text[:10000],
                        "status_code": response.status_code,
                    }

        except Exception as e:
            logger.exception(f"URL fetch error: {e}")
            return {"error": str(e), "url": url}
