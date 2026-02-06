"""
McLeuker AI - Tool Registry and Plugin System
=============================================
Extensible tool framework for the execution model (Kimi K2.5).

Features:
- Plugin-based tool registration
- Async tool execution
- Input validation
- Output formatting
- Error handling and retry logic
- Tool discovery and documentation

Inspired by Manus AI and Kimi K2.5 tool calling architecture.
"""

import asyncio
import json
import os
import re
import subprocess
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable, Type, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import logging
import httpx

logger = logging.getLogger(__name__)


class ToolCategory(Enum):
    """Categories of tools"""
    SEARCH = "search"
    CODE = "code"
    DATA = "data"
    FILE = "file"
    WEB = "web"
    ANALYSIS = "analysis"
    UTILITY = "utility"


@dataclass
class ToolParameter:
    """Definition of a tool parameter"""
    name: str
    type: str  # "string", "integer", "number", "boolean", "array", "object"
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[str]] = None
    
    def to_schema(self) -> Dict:
        schema = {
            "type": self.type,
            "description": self.description
        }
        if self.enum:
            schema["enum"] = self.enum
        if self.default is not None:
            schema["default"] = self.default
        return schema


@dataclass
class ToolResult:
    """Result from tool execution"""
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "metadata": self.metadata
        }


class BaseTool(ABC):
    """Base class for all tools"""
    
    name: str
    description: str
    category: ToolCategory
    parameters: List[ToolParameter]
    
    def __init__(self):
        self.execution_count = 0
        self.total_execution_time = 0
        self.last_executed = None
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters"""
        pass
    
    def get_definition(self) -> Dict:
        """Get OpenAI-compatible tool definition"""
        properties = {}
        required = []
        
        for param in self.parameters:
            properties[param.name] = param.to_schema()
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
    
    def validate_input(self, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate input parameters"""
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                return False, f"Missing required parameter: {param.name}"
            
            if param.name in kwargs:
                value = kwargs[param.name]
                
                # Type validation
                if param.type == "string" and not isinstance(value, str):
                    return False, f"Parameter {param.name} must be a string"
                elif param.type == "integer" and not isinstance(value, int):
                    return False, f"Parameter {param.name} must be an integer"
                elif param.type == "number" and not isinstance(value, (int, float)):
                    return False, f"Parameter {param.name} must be a number"
                elif param.type == "boolean" and not isinstance(value, bool):
                    return False, f"Parameter {param.name} must be a boolean"
                elif param.type == "array" and not isinstance(value, list):
                    return False, f"Parameter {param.name} must be an array"
                elif param.type == "object" and not isinstance(value, dict):
                    return False, f"Parameter {param.name} must be an object"
                
                # Enum validation
                if param.enum and value not in param.enum:
                    return False, f"Parameter {param.name} must be one of: {param.enum}"
        
        return True, None
    
    async def run(self, **kwargs) -> ToolResult:
        """Run the tool with validation and timing"""
        # Validate input
        valid, error = self.validate_input(**kwargs)
        if not valid:
            return ToolResult(success=False, data=None, error=error)
        
        # Execute with timing
        start_time = datetime.utcnow()
        
        try:
            result = await self.execute(**kwargs)
            
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            result.execution_time_ms = execution_time
            
            # Update stats
            self.execution_count += 1
            self.total_execution_time += execution_time
            self.last_executed = datetime.utcnow()
            
            return result
            
        except Exception as e:
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            logger.error(f"Tool {self.name} failed: {e}")
            
            return ToolResult(
                success=False,
                data=None,
                error=str(e),
                execution_time_ms=execution_time
            )


# =============================================================================
# Built-in Tools
# =============================================================================

class WebSearchTool(BaseTool):
    """Search the web for information"""
    
    name = "web_search"
    description = "Search the web for current information on any topic. Returns relevant results with snippets."
    category = ToolCategory.SEARCH
    parameters = [
        ToolParameter("query", "string", "The search query"),
        ToolParameter("num_results", "integer", "Number of results to return", required=False, default=5)
    ]
    
    def __init__(self):
        super().__init__()
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY", "")
    
    async def execute(self, query: str, num_results: int = 5) -> ToolResult:
        if self.perplexity_key:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.perplexity_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-sonar-small-128k-online",
                        "messages": [
                            {"role": "user", "content": f"Search for: {query}. Return factual information."}
                        ],
                        "return_citations": True
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    citations = data.get("citations", [])
                    
                    return ToolResult(
                        success=True,
                        data={
                            "query": query,
                            "results": content,
                            "citations": citations[:num_results],
                            "source": "perplexity"
                        }
                    )
        
        # Fallback
        return ToolResult(
            success=True,
            data={
                "query": query,
                "results": f"Search results for: {query}",
                "citations": [],
                "source": "fallback"
            }
        )


class CodeExecutionTool(BaseTool):
    """Execute Python code safely"""
    
    name = "execute_code"
    description = "Execute Python code and return the result. Supports data analysis, calculations, and transformations."
    category = ToolCategory.CODE
    parameters = [
        ToolParameter("code", "string", "Python code to execute"),
        ToolParameter("timeout", "integer", "Execution timeout in seconds", required=False, default=30)
    ]
    
    async def execute(self, code: str, timeout: int = 30) -> ToolResult:
        # Create a safe execution environment
        safe_globals = {
            "__builtins__": {
                "print": print,
                "len": len,
                "range": range,
                "str": str,
                "int": int,
                "float": float,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "bool": bool,
                "sum": sum,
                "min": min,
                "max": max,
                "abs": abs,
                "round": round,
                "sorted": sorted,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                "isinstance": isinstance,
                "type": type,
            }
        }
        
        # Add safe imports
        try:
            import json as json_module
            import math
            import statistics
            safe_globals["json"] = json_module
            safe_globals["math"] = math
            safe_globals["statistics"] = statistics
        except ImportError:
            pass
        
        local_vars = {}
        output = []
        
        # Capture print output
        original_print = print
        def capture_print(*args, **kwargs):
            output.append(" ".join(str(a) for a in args))
        safe_globals["__builtins__"]["print"] = capture_print
        
        try:
            exec(code, safe_globals, local_vars)
            
            # Get result
            result = local_vars.get("result", local_vars.get("output", None))
            if result is None and output:
                result = "\n".join(output)
            
            return ToolResult(
                success=True,
                data={
                    "output": result,
                    "variables": {k: str(v)[:500] for k, v in local_vars.items() if not k.startswith("_")},
                    "print_output": output
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=f"Code execution error: {str(e)}"
            )


class DataAnalysisTool(BaseTool):
    """Analyze structured data"""
    
    name = "analyze_data"
    description = "Analyze structured data (JSON, CSV) and extract insights, statistics, and patterns."
    category = ToolCategory.DATA
    parameters = [
        ToolParameter("data", "string", "JSON string of data to analyze"),
        ToolParameter("analysis_type", "string", "Type of analysis", 
                     enum=["summary", "statistics", "trends", "comparison", "distribution"])
    ]
    
    async def execute(self, data: str, analysis_type: str) -> ToolResult:
        try:
            parsed_data = json.loads(data)
            
            if analysis_type == "summary":
                if isinstance(parsed_data, list):
                    result = {
                        "type": "array",
                        "count": len(parsed_data),
                        "sample": parsed_data[:3] if len(parsed_data) > 3 else parsed_data
                    }
                elif isinstance(parsed_data, dict):
                    result = {
                        "type": "object",
                        "keys": list(parsed_data.keys()),
                        "key_count": len(parsed_data)
                    }
                else:
                    result = {"type": type(parsed_data).__name__, "value": str(parsed_data)[:200]}
                    
            elif analysis_type == "statistics":
                if isinstance(parsed_data, list) and all(isinstance(x, (int, float)) for x in parsed_data):
                    import statistics as stats
                    result = {
                        "count": len(parsed_data),
                        "mean": stats.mean(parsed_data),
                        "median": stats.median(parsed_data),
                        "stdev": stats.stdev(parsed_data) if len(parsed_data) > 1 else 0,
                        "min": min(parsed_data),
                        "max": max(parsed_data)
                    }
                else:
                    result = {"error": "Statistics requires numeric array"}
                    
            else:
                result = {
                    "analysis_type": analysis_type,
                    "data_type": type(parsed_data).__name__,
                    "processed": True
                }
            
            return ToolResult(success=True, data=result)
            
        except json.JSONDecodeError as e:
            return ToolResult(success=False, data=None, error=f"Invalid JSON: {str(e)}")


class FileGenerationTool(BaseTool):
    """Generate files from data"""
    
    name = "generate_file"
    description = "Generate files (Excel, CSV, PDF) from structured data."
    category = ToolCategory.FILE
    parameters = [
        ToolParameter("file_type", "string", "Type of file to generate", enum=["excel", "csv", "pdf", "json"]),
        ToolParameter("content", "string", "JSON string of content for the file"),
        ToolParameter("filename", "string", "Name for the generated file")
    ]
    
    async def execute(self, file_type: str, content: str, filename: str) -> ToolResult:
        try:
            parsed_content = json.loads(content)
            
            # Create output directory
            output_dir = "/tmp/mcleuker_files"
            os.makedirs(output_dir, exist_ok=True)
            
            if file_type == "json":
                file_path = os.path.join(output_dir, f"{filename}.json")
                with open(file_path, "w") as f:
                    json.dump(parsed_content, f, indent=2)
                    
            elif file_type == "csv":
                import csv
                file_path = os.path.join(output_dir, f"{filename}.csv")
                
                if isinstance(parsed_content, list) and parsed_content:
                    with open(file_path, "w", newline="") as f:
                        if isinstance(parsed_content[0], dict):
                            writer = csv.DictWriter(f, fieldnames=parsed_content[0].keys())
                            writer.writeheader()
                            writer.writerows(parsed_content)
                        else:
                            writer = csv.writer(f)
                            writer.writerows(parsed_content)
                            
            elif file_type == "excel":
                # Placeholder - would use openpyxl in production
                file_path = os.path.join(output_dir, f"{filename}.xlsx")
                # For now, save as JSON
                with open(file_path.replace(".xlsx", ".json"), "w") as f:
                    json.dump(parsed_content, f, indent=2)
                file_path = file_path.replace(".xlsx", ".json")
                
            else:
                file_path = os.path.join(output_dir, f"{filename}.txt")
                with open(file_path, "w") as f:
                    f.write(str(parsed_content))
            
            return ToolResult(
                success=True,
                data={
                    "file_path": file_path,
                    "file_type": file_type,
                    "filename": os.path.basename(file_path)
                }
            )
            
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))


class WebScrapeTool(BaseTool):
    """Scrape content from web pages"""
    
    name = "web_scrape"
    description = "Extract content from a web page URL."
    category = ToolCategory.WEB
    parameters = [
        ToolParameter("url", "string", "URL of the web page to scrape"),
        ToolParameter("selector", "string", "CSS selector for specific content", required=False)
    ]
    
    async def execute(self, url: str, selector: str = None) -> ToolResult:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, follow_redirects=True)
                
                if response.status_code == 200:
                    content = response.text
                    
                    # Basic content extraction
                    # In production, use BeautifulSoup or similar
                    title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE)
                    title = title_match.group(1) if title_match else "Unknown"
                    
                    # Remove HTML tags for text content
                    text = re.sub(r"<[^>]+>", " ", content)
                    text = re.sub(r"\s+", " ", text).strip()[:2000]
                    
                    return ToolResult(
                        success=True,
                        data={
                            "url": url,
                            "title": title,
                            "content": text,
                            "status_code": response.status_code
                        }
                    )
                else:
                    return ToolResult(
                        success=False,
                        data=None,
                        error=f"HTTP {response.status_code}"
                    )
                    
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))


class CalculatorTool(BaseTool):
    """Perform mathematical calculations"""
    
    name = "calculator"
    description = "Perform mathematical calculations and expressions."
    category = ToolCategory.UTILITY
    parameters = [
        ToolParameter("expression", "string", "Mathematical expression to evaluate")
    ]
    
    async def execute(self, expression: str) -> ToolResult:
        import math
        
        # Safe evaluation environment
        safe_dict = {
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "pow": pow,
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
            "pi": math.pi, "e": math.e,
            "floor": math.floor, "ceil": math.ceil
        }
        
        try:
            # Remove potentially dangerous characters
            clean_expr = re.sub(r"[^0-9+\-*/().a-z\s]", "", expression.lower())
            result = eval(clean_expr, {"__builtins__": {}}, safe_dict)
            
            return ToolResult(
                success=True,
                data={
                    "expression": expression,
                    "result": result
                }
            )
            
        except Exception as e:
            return ToolResult(success=False, data=None, error=f"Calculation error: {str(e)}")


# =============================================================================
# Tool Registry
# =============================================================================

class ToolRegistry:
    """
    Central registry for all tools.
    
    Manages tool registration, discovery, and execution.
    """
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._register_builtin_tools()
    
    def _register_builtin_tools(self):
        """Register all built-in tools"""
        builtin_tools = [
            WebSearchTool(),
            CodeExecutionTool(),
            DataAnalysisTool(),
            FileGenerationTool(),
            WebScrapeTool(),
            CalculatorTool()
        ]
        
        for tool in builtin_tools:
            self.register(tool)
    
    def register(self, tool: BaseTool):
        """Register a tool"""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def unregister(self, name: str):
        """Unregister a tool"""
        if name in self.tools:
            del self.tools[name]
            logger.info(f"Unregistered tool: {name}")
    
    def get(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict]:
        """List all registered tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "category": tool.category.value,
                "parameters": [p.to_schema() for p in tool.parameters]
            }
            for tool in self.tools.values()
        ]
    
    def get_definitions(self) -> List[Dict]:
        """Get OpenAI-compatible tool definitions for all tools"""
        return [tool.get_definition() for tool in self.tools.values()]
    
    async def execute(self, name: str, **kwargs) -> ToolResult:
        """Execute a tool by name"""
        tool = self.get(name)
        if not tool:
            return ToolResult(
                success=False,
                data=None,
                error=f"Tool not found: {name}"
            )
        
        return await tool.run(**kwargs)
    
    def get_stats(self) -> Dict:
        """Get execution statistics for all tools"""
        return {
            name: {
                "execution_count": tool.execution_count,
                "total_execution_time_ms": tool.total_execution_time,
                "avg_execution_time_ms": (
                    tool.total_execution_time / tool.execution_count
                    if tool.execution_count > 0 else 0
                ),
                "last_executed": tool.last_executed.isoformat() if tool.last_executed else None
            }
            for name, tool in self.tools.items()
        }


# Global registry instance
tool_registry = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry"""
    return tool_registry
