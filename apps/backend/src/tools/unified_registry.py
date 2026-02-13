"""
Unified Tool Registry — Central Registry for All Agent Tools
==============================================================

Manages tool registration, discovery, and dispatch:
- Tool definitions with schemas
- Category-based organization
- Automatic tool selection
- Usage tracking
"""

import json
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ToolCategory(Enum):
    SEARCH = "search"
    BROWSER = "browser"
    CODE = "code"
    FILE = "file"
    COMMUNICATION = "communication"
    DATA = "data"
    SYSTEM = "system"


@dataclass
class ToolDefinition:
    """Definition of a tool available to agents."""
    name: str
    description: str
    category: ToolCategory
    parameters: Dict[str, Any] = field(default_factory=dict)
    required_params: List[str] = field(default_factory=list)
    handler: Optional[Callable] = None
    enabled: bool = True
    credit_cost: float = 0.0
    requires_confirmation: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_openai_function(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": self.required_params,
                }
            }
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "parameters": self.parameters,
            "required_params": self.required_params,
            "enabled": self.enabled,
            "credit_cost": self.credit_cost,
        }


class UnifiedToolRegistry:
    """
    Central registry for all agent tools.

    Features:
    - Register tools with handlers
    - Discover tools by category
    - Dispatch tool calls
    - Track usage
    """

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._usage_stats: Dict[str, int] = {}
        self._register_builtin_tools()

    def _register_builtin_tools(self):
        """Register built-in tool definitions."""

        # Search tools
        self.register(ToolDefinition(
            name="web_search",
            description="Search the web for information using multiple search providers",
            category=ToolCategory.SEARCH,
            parameters={
                "query": {"type": "string", "description": "Search query"},
                "num_results": {"type": "integer", "description": "Number of results", "default": 10},
            },
            required_params=["query"],
            credit_cost=0.5,
        ))

        self.register(ToolDefinition(
            name="fetch_url",
            description="Fetch and extract content from a URL",
            category=ToolCategory.SEARCH,
            parameters={
                "url": {"type": "string", "description": "URL to fetch"},
            },
            required_params=["url"],
            credit_cost=0.3,
        ))

        # Browser tools
        self.register(ToolDefinition(
            name="browser_navigate",
            description="Navigate to a URL in the browser",
            category=ToolCategory.BROWSER,
            parameters={
                "url": {"type": "string", "description": "URL to navigate to"},
            },
            required_params=["url"],
            credit_cost=1.0,
        ))

        self.register(ToolDefinition(
            name="browser_click",
            description="Click an element on the page",
            category=ToolCategory.BROWSER,
            parameters={
                "selector": {"type": "string", "description": "CSS selector or element description"},
                "x": {"type": "number", "description": "X coordinate"},
                "y": {"type": "number", "description": "Y coordinate"},
            },
            credit_cost=0.5,
        ))

        self.register(ToolDefinition(
            name="browser_type",
            description="Type text into an input field",
            category=ToolCategory.BROWSER,
            parameters={
                "text": {"type": "string", "description": "Text to type"},
                "selector": {"type": "string", "description": "CSS selector of input field"},
            },
            required_params=["text"],
            credit_cost=0.5,
        ))

        self.register(ToolDefinition(
            name="browser_screenshot",
            description="Take a screenshot of the current page",
            category=ToolCategory.BROWSER,
            parameters={},
            credit_cost=0.3,
        ))

        self.register(ToolDefinition(
            name="browser_extract_text",
            description="Extract text content from the current page",
            category=ToolCategory.BROWSER,
            parameters={
                "selector": {"type": "string", "description": "CSS selector to extract from"},
            },
            credit_cost=0.3,
        ))

        # Code tools
        self.register(ToolDefinition(
            name="execute_python",
            description="Execute Python code in a sandbox",
            category=ToolCategory.CODE,
            parameters={
                "code": {"type": "string", "description": "Python code to execute"},
            },
            required_params=["code"],
            credit_cost=2.0,
        ))

        self.register(ToolDefinition(
            name="execute_javascript",
            description="Execute JavaScript code in a sandbox",
            category=ToolCategory.CODE,
            parameters={
                "code": {"type": "string", "description": "JavaScript code to execute"},
            },
            required_params=["code"],
            credit_cost=2.0,
        ))

        # File tools
        self.register(ToolDefinition(
            name="read_file",
            description="Read content from a file",
            category=ToolCategory.FILE,
            parameters={
                "path": {"type": "string", "description": "File path to read"},
            },
            required_params=["path"],
            credit_cost=0.1,
        ))

        self.register(ToolDefinition(
            name="write_file",
            description="Write content to a file",
            category=ToolCategory.FILE,
            parameters={
                "path": {"type": "string", "description": "File path to write"},
                "content": {"type": "string", "description": "Content to write"},
            },
            required_params=["path", "content"],
            credit_cost=0.5,
        ))

        self.register(ToolDefinition(
            name="list_directory",
            description="List files in a directory",
            category=ToolCategory.FILE,
            parameters={
                "path": {"type": "string", "description": "Directory path"},
            },
            required_params=["path"],
            credit_cost=0.1,
        ))

    def register(self, tool: ToolDefinition):
        """Register a tool."""
        self._tools[tool.name] = tool
        self._usage_stats[tool.name] = 0

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool by name."""
        return self._tools.get(name)

    def get_tools_by_category(self, category: ToolCategory) -> List[ToolDefinition]:
        """Get all tools in a category."""
        return [t for t in self._tools.values() if t.category == category and t.enabled]

    def get_all_tools(self) -> List[ToolDefinition]:
        """Get all enabled tools."""
        return [t for t in self._tools.values() if t.enabled]

    def get_openai_tools(self, categories: Optional[List[ToolCategory]] = None) -> List[Dict]:
        """Get tools in OpenAI function calling format."""
        tools = self.get_all_tools()
        if categories:
            tools = [t for t in tools if t.category in categories]
        return [t.to_openai_function() for t in tools]

    async def dispatch(self, tool_name: str, params: Dict[str, Any], context: Dict[str, Any] = None) -> Any:
        """
        Dispatch a tool call.

        Args:
            tool_name: Name of the tool to call
            params: Parameters for the tool
            context: Execution context

        Returns:
            Tool execution result
        """
        tool = self._tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")

        if not tool.enabled:
            raise ValueError(f"Tool is disabled: {tool_name}")

        if not tool.handler:
            raise ValueError(f"Tool has no handler: {tool_name}")

        # Track usage
        self._usage_stats[tool_name] = self._usage_stats.get(tool_name, 0) + 1

        # Execute handler
        try:
            import asyncio
            if asyncio.iscoroutinefunction(tool.handler):
                return await tool.handler(params, context or {})
            else:
                return tool.handler(params, context or {})
        except Exception as e:
            logger.exception(f"Tool dispatch error for {tool_name}: {e}")
            raise

    def set_handler(self, tool_name: str, handler: Callable):
        """Set the handler for a tool."""
        tool = self._tools.get(tool_name)
        if tool:
            tool.handler = handler
        else:
            logger.warning(f"Cannot set handler: tool {tool_name} not found")

    def get_usage_stats(self) -> Dict[str, int]:
        """Get tool usage statistics."""
        return dict(self._usage_stats)

    def get_total_credit_cost(self) -> float:
        """Get total credit cost of all tool usage."""
        total = 0.0
        for tool_name, count in self._usage_stats.items():
            tool = self._tools.get(tool_name)
            if tool:
                total += tool.credit_cost * count
        return total

    def to_dict(self) -> Dict[str, Any]:
        """Export registry state."""
        return {
            "tools": [t.to_dict() for t in self._tools.values()],
            "usage_stats": self._usage_stats,
            "total_credit_cost": self.get_total_credit_cost(),
        }
