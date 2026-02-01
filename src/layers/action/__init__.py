"""
V3.1 Action Layer
Web automation with Browserless.io and data extraction with Firecrawl.
"""

from src.layers.action.web_action import (
    ActionLayer,
    BrowserlessAction,
    FirecrawlExtractor,
    ActionResult,
    action_layer
)

__all__ = [
    "ActionLayer",
    "BrowserlessAction",
    "FirecrawlExtractor",
    "ActionResult",
    "action_layer"
]
