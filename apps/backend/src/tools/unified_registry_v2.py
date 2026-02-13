"""
Unified Tool Registry V2 - Enhanced Tool Management for Agentic AI
===================================================================
Extends the existing tool_registry with:
- BaseTool class for structured tool definitions
- Execution tracking with history
- OpenAI function-calling schema generation
- Retry with exponential backoff
- Category-based organization
- Decorator for easy tool creation

Backward-compatible: the existing set_handler / get_handler pattern
is preserved alongside the new BaseTool pattern.
"""

import asyncio
import inspect
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Type, Union, get_type_hints
from uuid import uuid4

from pydantic import BaseModel, Field, create_model

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ToolMetadata:
    """Metadata for a registered tool."""
    name: str
    description: str
    category: str = "general"
    version: str = "1.0.0"
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    requires_confirmation: bool = False
    max_execution_time: int = 60
    retryable: bool = True
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ToolExecution:
    """Record of a tool execution."""
    id: str = field(default_factory=lambda: str(uuid4()))
    tool_name: str = ""
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Any = None
    status: str = "pending"
    error_message: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_ms: Optional[int] = None
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "tool_name": self.tool_name,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "status": self.status,
            "error_message": self.error_message,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "retry_count": self.retry_count,
        }


class ToolDefinition(BaseModel):
    """Definition of a tool for LLM function calling."""
    name: str
    description: str
    parameters: Dict[str, Any]

    def to_openai_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


# ---------------------------------------------------------------------------
# Base Tool
# ---------------------------------------------------------------------------

class BaseToolV2:
    """Base class for all V2 tools."""
    name: str = ""
    description: str = ""
    parameters: Optional[Type[BaseModel]] = None
    metadata: Optional[ToolMetadata] = None

    def __init__(self):
        if not self.metadata:
            self.metadata = ToolMetadata(
                name=self.name,
                description=self.description,
                category="general",
            )

    async def execute(self, **kwargs) -> Any:
        raise NotImplementedError

    def get_definition(self) -> ToolDefinition:
        if self.parameters:
            schema = self.parameters.model_json_schema()
            parameters = {
                "type": "object",
                "properties": schema.get("properties", {}),
                "required": schema.get("required", []),
            }
        else:
            parameters = {"type": "object", "properties": {}, "required": []}
        return ToolDefinition(name=self.name, description=self.description, parameters=parameters)


# ---------------------------------------------------------------------------
# Enhanced Registry
# ---------------------------------------------------------------------------

class UnifiedToolRegistryV2:
    """
    Enhanced tool registry that supports both:
    - Legacy handler-based tools (set_handler / get_handler)
    - New BaseTool-based tools (register / get_tool / execute)
    """

    def __init__(self):
        # New-style tools
        self._tools: Dict[str, BaseToolV2] = {}
        self._categories: Dict[str, List[str]] = {}
        # Legacy handler-based tools
        self._handlers: Dict[str, Callable] = {}
        self._handler_schemas: Dict[str, Dict] = {}
        # Execution tracking
        self._execution_history: List[ToolExecution] = []
        self._max_history_size = 1000
        logger.info("UnifiedToolRegistryV2 initialized")

    # -- Legacy handler interface (backward compat) ---------------------------

    def set_handler(self, name: str, handler: Callable, schema: Optional[Dict] = None):
        """Register a legacy handler function."""
        self._handlers[name] = handler
        if schema:
            self._handler_schemas[name] = schema
        logger.info(f"Handler registered: {name}")

    def get_handler(self, name: str) -> Optional[Callable]:
        return self._handlers.get(name)

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all tools (both new and legacy) as dicts."""
        tools = []
        for name, tool in self._tools.items():
            tools.append({"name": name, "description": tool.description, "type": "v2"})
        for name in self._handlers:
            if name not in self._tools:
                tools.append({"name": name, "description": "", "type": "handler"})
        return tools

    # -- New-style tool interface ----------------------------------------------

    def register(self, tool: BaseToolV2, category: Optional[str] = None) -> "UnifiedToolRegistryV2":
        if not tool.name:
            raise ValueError("Tool must have a name")
        if tool.name in self._tools:
            logger.warning(f"Tool '{tool.name}' already registered, overwriting")
        self._tools[tool.name] = tool
        cat = category or (tool.metadata.category if tool.metadata else "general")
        if cat not in self._categories:
            self._categories[cat] = []
        if tool.name not in self._categories[cat]:
            self._categories[cat].append(tool.name)
        logger.info(f"Registered tool: {tool.name} (category: {cat})")
        return self

    def register_batch(self, tools: List[BaseToolV2]) -> "UnifiedToolRegistryV2":
        for tool in tools:
            self.register(tool)
        return self

    def get_tool(self, name: str) -> Optional[BaseToolV2]:
        return self._tools.get(name)

    def has_tool(self, name: str) -> bool:
        return name in self._tools or name in self._handlers

    def get_tool_names(self) -> List[str]:
        names = list(self._tools.keys())
        for n in self._handlers:
            if n not in names:
                names.append(n)
        return names

    def get_tools_by_category(self, category: str) -> List[BaseToolV2]:
        names = self._categories.get(category, [])
        return [self._tools[n] for n in names if n in self._tools]

    def get_categories(self) -> List[str]:
        return list(self._categories.keys())

    def get_definitions(self) -> List[ToolDefinition]:
        return [tool.get_definition() for tool in self._tools.values()]

    def get_openai_schemas(self) -> List[Dict[str, Any]]:
        schemas = [tool.get_definition().to_openai_schema() for tool in self._tools.values()]
        # Also include handler schemas
        for name, schema in self._handler_schemas.items():
            if name not in self._tools:
                schemas.append(schema)
        return schemas

    # -- Execution with tracking -----------------------------------------------

    async def execute(
        self,
        tool_name: str,
        input_data: Dict[str, Any],
        track_execution: bool = True,
        timeout: Optional[int] = None,
    ) -> Any:
        """Execute a tool (new-style or legacy handler) with tracking."""
        execution = ToolExecution(tool_name=tool_name, input_data=input_data, status="running")
        if track_execution:
            execution.start_time = datetime.utcnow()

        try:
            # Try new-style tool first
            tool = self._tools.get(tool_name)
            if tool:
                exec_timeout = timeout or (tool.metadata.max_execution_time if tool.metadata else 60)
                result = await asyncio.wait_for(tool.execute(**input_data), timeout=exec_timeout)
            else:
                # Fallback to legacy handler
                handler = self._handlers.get(tool_name)
                if not handler:
                    raise ValueError(f"Tool '{tool_name}' not found")
                exec_timeout = timeout or 60
                if asyncio.iscoroutinefunction(handler):
                    result = await asyncio.wait_for(handler(**input_data), timeout=exec_timeout)
                else:
                    result = handler(**input_data)

            if track_execution:
                execution.end_time = datetime.utcnow()
                execution.duration_ms = int((execution.end_time - execution.start_time).total_seconds() * 1000)
                execution.output_data = result
                execution.status = "completed"

            return result

        except asyncio.TimeoutError:
            msg = f"Tool '{tool_name}' timed out"
            logger.error(msg)
            if track_execution:
                execution.end_time = datetime.utcnow()
                execution.error_message = msg
                execution.status = "failed"
            raise TimeoutError(msg)

        except Exception as e:
            logger.error(f"Tool '{tool_name}' failed: {e}")
            if track_execution:
                execution.end_time = datetime.utcnow()
                execution.error_message = str(e)
                execution.status = "failed"
            raise

        finally:
            if track_execution:
                self._execution_history.append(execution)
                if len(self._execution_history) > self._max_history_size:
                    self._execution_history = self._execution_history[-self._max_history_size:]

    async def execute_with_retry(
        self, tool_name: str, input_data: Dict[str, Any],
        max_retries: int = 3, retry_delay: float = 1.0,
    ) -> Any:
        tool = self._tools.get(tool_name)
        if tool and tool.metadata and not tool.metadata.retryable:
            return await self.execute(tool_name, input_data)

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                return await self.execute(tool_name, input_data)
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    delay = retry_delay * (2 ** attempt)
                    logger.warning(f"Tool '{tool_name}' failed (attempt {attempt + 1}), retrying in {delay}s...")
                    await asyncio.sleep(delay)
        raise last_error

    def get_execution_history(self, tool_name: Optional[str] = None, limit: int = 100) -> List[ToolExecution]:
        history = self._execution_history
        if tool_name:
            history = [e for e in history if e.tool_name == tool_name]
        return history[-limit:]

    def clear_history(self):
        self._execution_history.clear()

    def get_stats(self) -> Dict[str, Any]:
        total = len(self._execution_history)
        successful = sum(1 for e in self._execution_history if e.status == "completed")
        failed = sum(1 for e in self._execution_history if e.status == "failed")
        tool_stats = {}
        for ex in self._execution_history:
            n = ex.tool_name
            if n not in tool_stats:
                tool_stats[n] = {"total": 0, "success": 0, "failed": 0}
            tool_stats[n]["total"] += 1
            if ex.status == "completed":
                tool_stats[n]["success"] += 1
            else:
                tool_stats[n]["failed"] += 1
        return {
            "total_tools": len(self._tools) + len(self._handlers),
            "v2_tools": len(self._tools),
            "legacy_handlers": len(self._handlers),
            "categories": len(self._categories),
            "total_executions": total,
            "successful_executions": successful,
            "failed_executions": failed,
            "success_rate": successful / total if total > 0 else 0,
            "tool_stats": tool_stats,
        }


# ---------------------------------------------------------------------------
# Decorator for creating tools from functions
# ---------------------------------------------------------------------------

def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    category: str = "general",
    requires_confirmation: bool = False,
):
    """Decorator to create a BaseToolV2 from a function."""
    def decorator(func: Callable) -> BaseToolV2:
        tool_name = name or func.__name__
        tool_desc = description or func.__doc__ or ""

        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        fields = {}
        for pname, param in sig.parameters.items():
            ptype = type_hints.get(pname, str)
            default = param.default if param.default != inspect.Parameter.empty else ...
            fields[pname] = (ptype, default)

        ParametersModel = create_model(f"{tool_name}_params", **fields)

        class FunctionTool(BaseToolV2):
            pass

        ft = FunctionTool()
        ft.name = tool_name
        ft.description = tool_desc
        ft.parameters = ParametersModel
        ft.metadata = ToolMetadata(
            name=tool_name, description=tool_desc, category=category,
            requires_confirmation=requires_confirmation,
        )

        async def _execute(**kwargs):
            if asyncio.iscoroutinefunction(func):
                return await func(**kwargs)
            return func(**kwargs)

        ft.execute = _execute
        return ft

    return decorator


# ---------------------------------------------------------------------------
# Global singleton
# ---------------------------------------------------------------------------

_global_registry_v2: Optional[UnifiedToolRegistryV2] = None


def get_global_registry_v2() -> UnifiedToolRegistryV2:
    global _global_registry_v2
    if _global_registry_v2 is None:
        _global_registry_v2 = UnifiedToolRegistryV2()
    return _global_registry_v2
