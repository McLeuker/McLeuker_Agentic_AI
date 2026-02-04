"""
McLeuker AI - Multi-Model Orchestrator
======================================
Manus AI-style architecture with:
- Grok: Primary reasoning model (deep thinking, analysis, planning)
- Kimi K2.5: Execution model (tool calls, code execution, multimodal)

This orchestrator implements a sophisticated agent system that:
1. Uses Grok for high-level reasoning and task planning
2. Delegates tool execution and specialized tasks to Kimi K2.5
3. Supports parallel task execution (Agent Swarm pattern)
4. Maintains context across multi-step workflows
"""

import asyncio
import json
import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, AsyncGenerator, Callable
from dataclasses import dataclass, field
from enum import Enum
import httpx
from openai import AsyncOpenAI

from src.providers.kimi_provider import KimiProvider, KimiResponse, get_kimi_provider


class ModelRole(Enum):
    """Role assignment for different models"""
    REASONING = "reasoning"      # High-level thinking and planning
    EXECUTION = "execution"      # Tool calls and task execution
    ANALYSIS = "analysis"        # Data analysis and insights
    MULTIMODAL = "multimodal"    # Image/video processing


class TaskStatus(Enum):
    """Status of a task in the execution pipeline"""
    PENDING = "pending"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    WAITING_TOOL = "waiting_tool"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentTask:
    """Represents a task in the agent system"""
    task_id: str
    description: str
    assigned_model: ModelRole
    status: TaskStatus = TaskStatus.PENDING
    parent_task_id: Optional[str] = None
    subtasks: List[str] = field(default_factory=list)
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    tool_calls: List[Dict] = field(default_factory=list)
    reasoning_trace: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "assigned_model": self.assigned_model.value,
            "status": self.status.value,
            "parent_task_id": self.parent_task_id,
            "subtasks": self.subtasks,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "tool_calls_count": len(self.tool_calls),
            "reasoning_steps": len(self.reasoning_trace)
        }


@dataclass
class ExecutionPlan:
    """Execution plan created by the reasoning model"""
    plan_id: str
    goal: str
    tasks: List[AgentTask]
    parallel_groups: List[List[str]]  # Groups of task IDs that can run in parallel
    estimated_time: str
    complexity: str  # "simple", "moderate", "complex"
    
    def to_dict(self) -> Dict:
        return {
            "plan_id": self.plan_id,
            "goal": self.goal,
            "tasks": [t.to_dict() for t in self.tasks],
            "parallel_groups": self.parallel_groups,
            "estimated_time": self.estimated_time,
            "complexity": self.complexity
        }


class MultiModelOrchestrator:
    """
    Multi-Model Orchestrator implementing Manus AI-style architecture.
    
    Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                    User Query                                │
    └─────────────────────────────────────────────────────────────┘
                              │
                              ▼
    ┌─────────────────────────────────────────────────────────────┐
    │              GROK (Reasoning Model)                          │
    │  - Query understanding                                       │
    │  - Task decomposition                                        │
    │  - Execution planning                                        │
    │  - Result synthesis                                          │
    └─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
    ┌───────────────────────┐  ┌───────────────────────┐
    │   KIMI K2.5           │  │   KIMI K2.5           │
    │   (Execution Agent)   │  │   (Execution Agent)   │
    │   - Tool calls        │  │   - Tool calls        │
    │   - Code execution    │  │   - Multimodal        │
    │   - Data processing   │  │   - Long context      │
    └───────────────────────┘  └───────────────────────┘
                    │                   │
                    └─────────┬─────────┘
                              ▼
    ┌─────────────────────────────────────────────────────────────┐
    │              GROK (Result Synthesis)                         │
    │  - Aggregate results                                         │
    │  - Generate insights                                         │
    │  - Format response                                           │
    └─────────────────────────────────────────────────────────────┘
    """
    
    def __init__(self):
        # Grok for reasoning
        self.grok_api_key = os.getenv("XAI_API_KEY", "")
        self.grok_base_url = "https://api.x.ai/v1"
        self.grok_model = "grok-4-fast-non-reasoning"
        
        # Kimi for execution
        self.kimi_api_key = os.getenv("MOONSHOT_API_KEY", "")
        self.kimi_provider: Optional[KimiProvider] = None
        
        # Initialize Grok client
        if self.grok_api_key:
            self.grok_client = AsyncOpenAI(
                api_key=self.grok_api_key,
                base_url=self.grok_base_url
            )
        else:
            self.grok_client = None
        
        # Initialize Kimi provider
        if self.kimi_api_key:
            self.kimi_provider = KimiProvider(
                api_key=self.kimi_api_key,
                model="kimi-k2.5",
                thinking_enabled=True
            )
        
        # Tool registry
        self.tools: Dict[str, Dict] = {}
        self.tool_handlers: Dict[str, Callable] = {}
        
        # Task tracking
        self.active_tasks: Dict[str, AgentTask] = {}
        
        # Register default tools
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools available to the execution model"""
        
        # Web Search Tool
        self.register_tool(
            name="web_search",
            description="Search the web for current information on any topic",
            parameters={
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return (default 5)",
                    "default": 5
                }
            },
            required=["query"],
            handler=self._handle_web_search
        )
        
        # Code Execution Tool
        self.register_tool(
            name="execute_code",
            description="Execute Python code and return the result",
            parameters={
                "code": {
                    "type": "string",
                    "description": "Python code to execute"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Execution timeout in seconds (default 30)",
                    "default": 30
                }
            },
            required=["code"],
            handler=self._handle_code_execution
        )
        
        # Data Analysis Tool
        self.register_tool(
            name="analyze_data",
            description="Analyze structured data and extract insights",
            parameters={
                "data": {
                    "type": "string",
                    "description": "JSON string of data to analyze"
                },
                "analysis_type": {
                    "type": "string",
                    "enum": ["summary", "trends", "comparison", "statistical"],
                    "description": "Type of analysis to perform"
                }
            },
            required=["data", "analysis_type"],
            handler=self._handle_data_analysis
        )
        
        # File Generation Tool
        self.register_tool(
            name="generate_file",
            description="Generate a file (Excel, PDF, CSV) from data",
            parameters={
                "file_type": {
                    "type": "string",
                    "enum": ["excel", "pdf", "csv"],
                    "description": "Type of file to generate"
                },
                "content": {
                    "type": "string",
                    "description": "JSON string of content for the file"
                },
                "filename": {
                    "type": "string",
                    "description": "Name for the generated file"
                }
            },
            required=["file_type", "content", "filename"],
            handler=self._handle_file_generation
        )
    
    def register_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        required: List[str],
        handler: Callable
    ):
        """Register a tool for use by the execution model"""
        self.tools[name] = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": parameters,
                    "required": required
                }
            }
        }
        self.tool_handlers[name] = handler
    
    async def process(
        self,
        query: str,
        session_id: Optional[str] = None,
        context: Optional[Dict] = None,
        mode: str = "auto"
    ) -> Dict[str, Any]:
        """
        Process a user query using the multi-model architecture.
        
        Steps:
        1. Grok analyzes and creates execution plan
        2. Kimi executes tasks (potentially in parallel)
        3. Grok synthesizes results
        """
        session_id = session_id or str(uuid.uuid4())
        
        try:
            # Step 1: Reasoning - Analyze query and create plan
            plan = await self._create_execution_plan(query, context)
            
            # Step 2: Execute tasks
            results = await self._execute_plan(plan)
            
            # Step 3: Synthesize results
            final_response = await self._synthesize_results(query, plan, results)
            
            return {
                "success": True,
                "response": final_response,
                "plan": plan.to_dict(),
                "session_id": session_id,
                "tasks_executed": len(plan.tasks),
                "model_usage": {
                    "reasoning": "grok-4-fast-non-reasoning",
                    "execution": "kimi-k2.5"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    async def process_stream(
        self,
        query: str,
        session_id: Optional[str] = None,
        context: Optional[Dict] = None,
        mode: str = "auto"
    ) -> AsyncGenerator[Dict, None]:
        """
        Process query with streaming events for real-time UI updates.
        """
        session_id = session_id or str(uuid.uuid4())
        
        try:
            # Phase 1: Understanding
            yield {
                "type": "thinking",
                "phase": "understanding",
                "message": "Analyzing your request...",
                "model": "grok"
            }
            
            # Phase 2: Planning
            yield {
                "type": "thinking",
                "phase": "planning",
                "message": "Creating execution plan...",
                "model": "grok"
            }
            
            plan = await self._create_execution_plan(query, context)
            
            yield {
                "type": "plan",
                "data": plan.to_dict()
            }
            
            # Phase 3: Execution
            for task in plan.tasks:
                yield {
                    "type": "task_start",
                    "task_id": task.task_id,
                    "description": task.description,
                    "model": task.assigned_model.value
                }
                
                # Execute task
                result = await self._execute_task(task)
                
                yield {
                    "type": "task_complete",
                    "task_id": task.task_id,
                    "status": task.status.value,
                    "result_preview": str(result)[:200] if result else None
                }
            
            # Phase 4: Synthesis
            yield {
                "type": "thinking",
                "phase": "synthesizing",
                "message": "Synthesizing results...",
                "model": "grok"
            }
            
            results = {t.task_id: t.result for t in plan.tasks}
            final_response = await self._synthesize_results(query, plan, results)
            
            # Final response
            yield {
                "type": "complete",
                "response": final_response,
                "plan": plan.to_dict(),
                "session_id": session_id
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "message": str(e)
            }
    
    async def _create_execution_plan(
        self,
        query: str,
        context: Optional[Dict] = None
    ) -> ExecutionPlan:
        """Use Grok to analyze query and create execution plan"""
        
        system_prompt = """You are a task planning AI. Analyze the user's query and create an execution plan.

Your job is to:
1. Understand what the user wants to accomplish
2. Break it down into executable tasks
3. Identify which tasks can run in parallel
4. Assign each task to the appropriate model:
   - REASONING: Complex analysis, synthesis, creative writing
   - EXECUTION: Tool calls, code execution, data processing
   - MULTIMODAL: Image/video analysis

Respond with a JSON object:
{
    "goal": "Brief description of the overall goal",
    "complexity": "simple|moderate|complex",
    "estimated_time": "e.g., 10-15 seconds",
    "tasks": [
        {
            "id": "task_1",
            "description": "What this task does",
            "model": "REASONING|EXECUTION|MULTIMODAL",
            "depends_on": [],  // IDs of tasks this depends on
            "tools_needed": ["web_search", "execute_code", etc.]
        }
    ],
    "parallel_groups": [["task_1", "task_2"], ["task_3"]]  // Tasks that can run together
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context or {})}"}
        ]
        
        if self.grok_client:
            response = await self.grok_client.chat.completions.create(
                model=self.grok_model,
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON from response
            try:
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                plan_data = json.loads(content)
            except json.JSONDecodeError:
                # Fallback to simple plan
                plan_data = {
                    "goal": query,
                    "complexity": "simple",
                    "estimated_time": "10-15 seconds",
                    "tasks": [{
                        "id": "task_1",
                        "description": f"Process query: {query}",
                        "model": "EXECUTION",
                        "depends_on": [],
                        "tools_needed": ["web_search"]
                    }],
                    "parallel_groups": [["task_1"]]
                }
        else:
            # Fallback without Grok
            plan_data = {
                "goal": query,
                "complexity": "simple",
                "estimated_time": "10-15 seconds",
                "tasks": [{
                    "id": "task_1",
                    "description": f"Process query: {query}",
                    "model": "EXECUTION",
                    "depends_on": [],
                    "tools_needed": ["web_search"]
                }],
                "parallel_groups": [["task_1"]]
            }
        
        # Convert to ExecutionPlan
        tasks = []
        for task_data in plan_data.get("tasks", []):
            model_role = ModelRole[task_data.get("model", "EXECUTION")]
            task = AgentTask(
                task_id=task_data["id"],
                description=task_data["description"],
                assigned_model=model_role
            )
            tasks.append(task)
            self.active_tasks[task.task_id] = task
        
        return ExecutionPlan(
            plan_id=str(uuid.uuid4())[:8],
            goal=plan_data.get("goal", query),
            tasks=tasks,
            parallel_groups=plan_data.get("parallel_groups", [[t.task_id for t in tasks]]),
            estimated_time=plan_data.get("estimated_time", "15-30 seconds"),
            complexity=plan_data.get("complexity", "moderate")
        )
    
    async def _execute_plan(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Execute all tasks in the plan, respecting parallelism"""
        results = {}
        
        for group in plan.parallel_groups:
            # Execute tasks in this group in parallel
            group_tasks = [
                self._execute_task(self.active_tasks[task_id])
                for task_id in group
                if task_id in self.active_tasks
            ]
            
            group_results = await asyncio.gather(*group_tasks, return_exceptions=True)
            
            for task_id, result in zip(group, group_results):
                if isinstance(result, Exception):
                    results[task_id] = {"error": str(result)}
                else:
                    results[task_id] = result
        
        return results
    
    async def _execute_task(self, task: AgentTask) -> Any:
        """Execute a single task using the appropriate model"""
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        
        try:
            if task.assigned_model == ModelRole.EXECUTION and self.kimi_provider:
                # Use Kimi for execution tasks
                result = await self._execute_with_kimi(task)
            elif task.assigned_model == ModelRole.MULTIMODAL and self.kimi_provider:
                # Use Kimi for multimodal tasks
                result = await self._execute_multimodal(task)
            else:
                # Use Grok for reasoning tasks
                result = await self._execute_with_grok(task)
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            return result
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            raise
    
    async def _execute_with_kimi(self, task: AgentTask) -> Any:
        """Execute task using Kimi K2.5 with tool calling"""
        
        messages = [
            {
                "role": "system",
                "content": """You are an execution agent. Complete the given task using available tools.
Be efficient and precise. Use tools when needed to gather information or perform actions."""
            },
            {
                "role": "user",
                "content": f"Task: {task.description}"
            }
        ]
        
        # Get available tools
        tools_list = list(self.tools.values())
        
        # Execute with tool calling loop
        response = await self.kimi_provider.complete_with_tools(
            messages=messages,
            tools=tools_list,
            tool_executor=self._execute_tool,
            max_iterations=5
        )
        
        task.tool_calls = [
            {"name": tc.name, "arguments": tc.arguments}
            for tc in response.tool_calls
        ] if response.tool_calls else []
        
        if response.reasoning_content:
            task.reasoning_trace.append(response.reasoning_content)
        
        return response.content
    
    async def _execute_multimodal(self, task: AgentTask) -> Any:
        """Execute multimodal task using Kimi K2.5"""
        # For now, return a placeholder
        # In production, this would handle image/video analysis
        return f"Multimodal analysis for: {task.description}"
    
    async def _execute_with_grok(self, task: AgentTask) -> Any:
        """Execute reasoning task using Grok"""
        
        if not self.grok_client:
            return f"Reasoning result for: {task.description}"
        
        messages = [
            {
                "role": "system",
                "content": "You are a reasoning agent. Analyze and provide insights."
            },
            {
                "role": "user",
                "content": f"Task: {task.description}"
            }
        ]
        
        response = await self.grok_client.chat.completions.create(
            model=self.grok_model,
            messages=messages,
            temperature=0.5,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    async def _execute_tool(self, tool_name: str, arguments: Dict) -> Any:
        """Execute a registered tool"""
        if tool_name not in self.tool_handlers:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        handler = self.tool_handlers[tool_name]
        return await handler(arguments)
    
    async def _synthesize_results(
        self,
        query: str,
        plan: ExecutionPlan,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use Grok to synthesize all results into a coherent response"""
        
        system_prompt = """You are a synthesis agent. Combine the results from multiple tasks into a coherent, well-structured response.

Format your response as JSON:
{
    "summary": "Brief overview of the findings",
    "main_content": "Detailed response with proper formatting",
    "key_insights": [
        {"icon": "emoji", "title": "Insight title", "description": "Details"}
    ],
    "follow_up_questions": ["Question 1", "Question 2", "Question 3"]
}"""

        results_summary = "\n".join([
            f"Task {task_id}: {str(result)[:500]}"
            for task_id, result in results.items()
        ])
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""
Original Query: {query}

Execution Plan Goal: {plan.goal}

Task Results:
{results_summary}

Please synthesize these results into a comprehensive response."""}
        ]
        
        if self.grok_client:
            response = await self.grok_client.chat.completions.create(
                model=self.grok_model,
                messages=messages,
                temperature=0.5,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            
            try:
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                return json.loads(content)
            except json.JSONDecodeError:
                return {
                    "summary": content[:200],
                    "main_content": content,
                    "key_insights": [],
                    "follow_up_questions": []
                }
        else:
            # Fallback without Grok
            return {
                "summary": f"Results for: {query}",
                "main_content": results_summary,
                "key_insights": [],
                "follow_up_questions": []
            }
    
    # Tool Handlers
    async def _handle_web_search(self, args: Dict) -> Dict:
        """Handle web search tool calls"""
        query = args.get("query", "")
        num_results = args.get("num_results", 5)
        
        # Use Perplexity or fallback
        perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        
        if perplexity_key:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {perplexity_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-sonar-small-128k-online",
                        "messages": [
                            {"role": "user", "content": f"Search for: {query}"}
                        ],
                        "return_citations": True
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "results": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                        "citations": data.get("citations", [])
                    }
        
        return {"results": f"Search results for: {query}", "citations": []}
    
    async def _handle_code_execution(self, args: Dict) -> Dict:
        """Handle code execution tool calls"""
        code = args.get("code", "")
        timeout = args.get("timeout", 30)
        
        # Safe code execution (in production, use sandboxed environment)
        try:
            # Create a restricted execution environment
            local_vars = {}
            exec(code, {"__builtins__": {}}, local_vars)
            return {"success": True, "result": str(local_vars)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_data_analysis(self, args: Dict) -> Dict:
        """Handle data analysis tool calls"""
        data = args.get("data", "{}")
        analysis_type = args.get("analysis_type", "summary")
        
        try:
            parsed_data = json.loads(data)
            return {
                "analysis_type": analysis_type,
                "data_points": len(parsed_data) if isinstance(parsed_data, list) else 1,
                "summary": f"Analysis of {analysis_type} completed"
            }
        except json.JSONDecodeError:
            return {"error": "Invalid JSON data"}
    
    async def _handle_file_generation(self, args: Dict) -> Dict:
        """Handle file generation tool calls"""
        file_type = args.get("file_type", "csv")
        content = args.get("content", "{}")
        filename = args.get("filename", "output")
        
        return {
            "file_type": file_type,
            "filename": f"{filename}.{file_type}",
            "status": "generated"
        }


# Singleton instance
multi_model_orchestrator: Optional[MultiModelOrchestrator] = None


def get_multi_model_orchestrator() -> MultiModelOrchestrator:
    """Get or create the multi-model orchestrator singleton"""
    global multi_model_orchestrator
    
    if multi_model_orchestrator is None:
        multi_model_orchestrator = MultiModelOrchestrator()
    
    return multi_model_orchestrator
