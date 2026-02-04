"""
McLeuker AI - Agent Swarm Orchestration
=======================================
Implements the Agent Swarm pattern inspired by Kimi K2.5 architecture.

Features:
- Dynamic task decomposition
- Parallel agent execution
- Coordination and result aggregation
- Fault tolerance and retry logic
- Progress tracking and streaming

Architecture:
┌─────────────────────────────────────────────────────────────────┐
│                     COORDINATOR AGENT                            │
│  - Receives user query                                           │
│  - Decomposes into subtasks                                      │
│  - Assigns to worker agents                                      │
│  - Aggregates results                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  WORKER AGENT   │  │  WORKER AGENT   │  │  WORKER AGENT   │
│  (Search)       │  │  (Analysis)     │  │  (Execution)    │
└─────────────────┘  └─────────────────┘  └─────────────────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SYNTHESIS AGENT                              │
│  - Combines all results                                          │
│  - Generates coherent response                                   │
│  - Formats output                                                │
└─────────────────────────────────────────────────────────────────┘
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, AsyncGenerator, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Types of agents in the swarm"""
    COORDINATOR = "coordinator"
    SEARCH = "search"
    ANALYSIS = "analysis"
    EXECUTION = "execution"
    SYNTHESIS = "synthesis"
    MULTIMODAL = "multimodal"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskState(Enum):
    """State of a task in the swarm"""
    QUEUED = "queued"
    ASSIGNED = "assigned"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SwarmTask:
    """A task in the agent swarm"""
    task_id: str
    description: str
    agent_type: AgentType
    priority: TaskPriority = TaskPriority.MEDIUM
    state: TaskState = TaskState.QUEUED
    
    # Dependencies
    depends_on: Set[str] = field(default_factory=set)
    blocks: Set[str] = field(default_factory=set)
    
    # Execution details
    assigned_agent: Optional[str] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Optional[Any] = None
    error: Optional[str] = None
    
    # Timing
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Retry logic
    retry_count: int = 0
    max_retries: int = 3
    
    def can_start(self, completed_tasks: Set[str]) -> bool:
        """Check if all dependencies are satisfied"""
        return self.depends_on.issubset(completed_tasks)
    
    def duration_ms(self) -> Optional[int]:
        """Get task duration in milliseconds"""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds() * 1000)
        return None
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "agent_type": self.agent_type.value,
            "priority": self.priority.value,
            "state": self.state.value,
            "depends_on": list(self.depends_on),
            "blocks": list(self.blocks),
            "assigned_agent": self.assigned_agent,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms(),
            "retry_count": self.retry_count
        }


@dataclass
class SwarmResult:
    """Result from the agent swarm execution"""
    success: bool
    output: Any
    tasks_completed: int
    tasks_failed: int
    total_duration_ms: int
    task_details: List[Dict]
    errors: List[str] = field(default_factory=list)


class BaseAgent(ABC):
    """Base class for all agents in the swarm"""
    
    def __init__(self, agent_id: str, agent_type: AgentType):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.is_busy = False
        self.current_task: Optional[SwarmTask] = None
        self.tasks_completed = 0
        self.tasks_failed = 0
    
    @abstractmethod
    async def execute(self, task: SwarmTask) -> Any:
        """Execute a task and return the result"""
        pass
    
    async def run_task(self, task: SwarmTask) -> SwarmTask:
        """Run a task with error handling"""
        self.is_busy = True
        self.current_task = task
        task.state = TaskState.RUNNING
        task.started_at = datetime.utcnow()
        task.assigned_agent = self.agent_id
        
        try:
            result = await self.execute(task)
            task.output_data = result
            task.state = TaskState.COMPLETED
            task.completed_at = datetime.utcnow()
            self.tasks_completed += 1
            
        except Exception as e:
            task.error = str(e)
            task.retry_count += 1
            
            if task.retry_count < task.max_retries:
                task.state = TaskState.QUEUED
                logger.warning(f"Task {task.task_id} failed, retry {task.retry_count}/{task.max_retries}")
            else:
                task.state = TaskState.FAILED
                task.completed_at = datetime.utcnow()
                self.tasks_failed += 1
                logger.error(f"Task {task.task_id} failed permanently: {e}")
        
        finally:
            self.is_busy = False
            self.current_task = None
        
        return task


class SearchAgent(BaseAgent):
    """Agent specialized in web search and information retrieval"""
    
    def __init__(self, agent_id: str, search_handler: Callable):
        super().__init__(agent_id, AgentType.SEARCH)
        self.search_handler = search_handler
    
    async def execute(self, task: SwarmTask) -> Any:
        query = task.input_data.get("query", task.description)
        num_results = task.input_data.get("num_results", 5)
        
        result = await self.search_handler({
            "query": query,
            "num_results": num_results
        })
        
        return result


class AnalysisAgent(BaseAgent):
    """Agent specialized in data analysis and insight extraction"""
    
    def __init__(self, agent_id: str, llm_handler: Callable):
        super().__init__(agent_id, AgentType.ANALYSIS)
        self.llm_handler = llm_handler
    
    async def execute(self, task: SwarmTask) -> Any:
        data = task.input_data.get("data", {})
        analysis_type = task.input_data.get("analysis_type", "summary")
        
        prompt = f"""Analyze the following data and provide a {analysis_type}:

Data: {json.dumps(data, indent=2)}

Task: {task.description}

Provide a structured analysis with key findings."""

        result = await self.llm_handler(prompt)
        return result


class ExecutionAgent(BaseAgent):
    """Agent specialized in tool execution and code running"""
    
    def __init__(self, agent_id: str, tool_executor: Callable):
        super().__init__(agent_id, AgentType.EXECUTION)
        self.tool_executor = tool_executor
    
    async def execute(self, task: SwarmTask) -> Any:
        tool_name = task.input_data.get("tool")
        tool_args = task.input_data.get("arguments", {})
        
        if tool_name:
            result = await self.tool_executor(tool_name, tool_args)
        else:
            # Generic execution
            result = {"status": "executed", "task": task.description}
        
        return result


class SynthesisAgent(BaseAgent):
    """Agent specialized in combining results and generating final output"""
    
    def __init__(self, agent_id: str, llm_handler: Callable):
        super().__init__(agent_id, AgentType.SYNTHESIS)
        self.llm_handler = llm_handler
    
    async def execute(self, task: SwarmTask) -> Any:
        results = task.input_data.get("results", [])
        original_query = task.input_data.get("query", "")
        
        prompt = f"""Synthesize the following results into a coherent response:

Original Query: {original_query}

Results from subtasks:
{json.dumps(results, indent=2)}

Create a comprehensive, well-structured response that:
1. Addresses the original query
2. Incorporates all relevant findings
3. Provides clear insights and recommendations
4. Is formatted for easy reading"""

        result = await self.llm_handler(prompt)
        return result


class AgentSwarm:
    """
    Agent Swarm Orchestrator
    
    Manages a pool of specialized agents and coordinates task execution
    following the Agent Swarm pattern.
    """
    
    def __init__(
        self,
        max_concurrent_tasks: int = 5,
        search_handler: Optional[Callable] = None,
        llm_handler: Optional[Callable] = None,
        tool_executor: Optional[Callable] = None
    ):
        self.max_concurrent_tasks = max_concurrent_tasks
        
        # Task management
        self.task_queue: List[SwarmTask] = []
        self.active_tasks: Dict[str, SwarmTask] = {}
        self.completed_tasks: Dict[str, SwarmTask] = {}
        self.failed_tasks: Dict[str, SwarmTask] = {}
        
        # Agent pool
        self.agents: Dict[str, BaseAgent] = {}
        
        # Initialize agents with handlers
        self._init_agents(search_handler, llm_handler, tool_executor)
        
        # Execution state
        self.is_running = False
        self.start_time: Optional[datetime] = None
    
    def _init_agents(
        self,
        search_handler: Optional[Callable],
        llm_handler: Optional[Callable],
        tool_executor: Optional[Callable]
    ):
        """Initialize the agent pool"""
        
        # Default handlers if not provided
        async def default_search(args):
            return {"results": f"Search results for: {args.get('query', '')}"}
        
        async def default_llm(prompt):
            return f"LLM response for: {prompt[:100]}..."
        
        async def default_executor(tool, args):
            return {"status": "executed", "tool": tool}
        
        search_handler = search_handler or default_search
        llm_handler = llm_handler or default_llm
        tool_executor = tool_executor or default_executor
        
        # Create agent pool
        for i in range(2):
            agent_id = f"search_{i}"
            self.agents[agent_id] = SearchAgent(agent_id, search_handler)
        
        for i in range(2):
            agent_id = f"analysis_{i}"
            self.agents[agent_id] = AnalysisAgent(agent_id, llm_handler)
        
        for i in range(2):
            agent_id = f"execution_{i}"
            self.agents[agent_id] = ExecutionAgent(agent_id, tool_executor)
        
        agent_id = "synthesis_0"
        self.agents[agent_id] = SynthesisAgent(agent_id, llm_handler)
    
    def add_task(
        self,
        description: str,
        agent_type: AgentType,
        input_data: Dict[str, Any] = None,
        depends_on: Set[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM
    ) -> SwarmTask:
        """Add a task to the swarm"""
        task = SwarmTask(
            task_id=str(uuid.uuid4())[:8],
            description=description,
            agent_type=agent_type,
            priority=priority,
            input_data=input_data or {},
            depends_on=depends_on or set()
        )
        
        # Update blocking relationships
        for dep_id in task.depends_on:
            for t in self.task_queue + list(self.active_tasks.values()):
                if t.task_id == dep_id:
                    t.blocks.add(task.task_id)
        
        self.task_queue.append(task)
        self._sort_queue()
        
        return task
    
    def _sort_queue(self):
        """Sort task queue by priority and dependencies"""
        self.task_queue.sort(
            key=lambda t: (-t.priority.value, len(t.depends_on), t.created_at)
        )
    
    def _get_available_agent(self, agent_type: AgentType) -> Optional[BaseAgent]:
        """Get an available agent of the specified type"""
        for agent in self.agents.values():
            if agent.agent_type == agent_type and not agent.is_busy:
                return agent
        return None
    
    def _get_completed_task_ids(self) -> Set[str]:
        """Get IDs of all completed tasks"""
        return set(self.completed_tasks.keys())
    
    async def execute(
        self,
        timeout: float = 120.0
    ) -> SwarmResult:
        """
        Execute all tasks in the swarm.
        
        Returns when all tasks are complete or timeout is reached.
        """
        self.is_running = True
        self.start_time = datetime.utcnow()
        
        try:
            await asyncio.wait_for(
                self._run_swarm(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning("Swarm execution timed out")
            # Cancel remaining tasks
            for task in self.task_queue:
                task.state = TaskState.CANCELLED
        
        self.is_running = False
        
        # Calculate results
        total_duration = int((datetime.utcnow() - self.start_time).total_seconds() * 1000)
        
        return SwarmResult(
            success=len(self.failed_tasks) == 0,
            output=self._aggregate_results(),
            tasks_completed=len(self.completed_tasks),
            tasks_failed=len(self.failed_tasks),
            total_duration_ms=total_duration,
            task_details=[t.to_dict() for t in self.completed_tasks.values()],
            errors=[t.error for t in self.failed_tasks.values() if t.error]
        )
    
    async def execute_stream(
        self,
        timeout: float = 120.0
    ) -> AsyncGenerator[Dict, None]:
        """
        Execute tasks with streaming progress updates.
        """
        self.is_running = True
        self.start_time = datetime.utcnow()
        
        yield {
            "type": "swarm_start",
            "total_tasks": len(self.task_queue),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        completed_ids = set()
        
        try:
            while self.task_queue or self.active_tasks:
                # Check for completed tasks
                newly_completed = set(self.completed_tasks.keys()) - completed_ids
                for task_id in newly_completed:
                    task = self.completed_tasks[task_id]
                    yield {
                        "type": "task_complete",
                        "task": task.to_dict(),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    completed_ids.add(task_id)
                
                # Start new tasks
                await self._schedule_tasks()
                
                # Small delay to prevent busy loop
                await asyncio.sleep(0.1)
                
                # Check timeout
                elapsed = (datetime.utcnow() - self.start_time).total_seconds()
                if elapsed > timeout:
                    break
        
        except Exception as e:
            yield {
                "type": "swarm_error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        self.is_running = False
        
        yield {
            "type": "swarm_complete",
            "tasks_completed": len(self.completed_tasks),
            "tasks_failed": len(self.failed_tasks),
            "result": self._aggregate_results(),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _run_swarm(self):
        """Main swarm execution loop"""
        while self.task_queue or self.active_tasks:
            await self._schedule_tasks()
            await asyncio.sleep(0.05)
    
    async def _schedule_tasks(self):
        """Schedule ready tasks to available agents"""
        completed_ids = self._get_completed_task_ids()
        
        # Find tasks that can start
        ready_tasks = [
            task for task in self.task_queue
            if task.can_start(completed_ids) and task.state == TaskState.QUEUED
        ]
        
        for task in ready_tasks:
            if len(self.active_tasks) >= self.max_concurrent_tasks:
                break
            
            agent = self._get_available_agent(task.agent_type)
            if agent:
                self.task_queue.remove(task)
                self.active_tasks[task.task_id] = task
                
                # Start task execution
                asyncio.create_task(self._execute_task(agent, task))
    
    async def _execute_task(self, agent: BaseAgent, task: SwarmTask):
        """Execute a single task with an agent"""
        try:
            completed_task = await agent.run_task(task)
            
            # Move to appropriate collection
            del self.active_tasks[task.task_id]
            
            if completed_task.state == TaskState.COMPLETED:
                self.completed_tasks[task.task_id] = completed_task
            elif completed_task.state == TaskState.FAILED:
                self.failed_tasks[task.task_id] = completed_task
            elif completed_task.state == TaskState.QUEUED:
                # Retry - add back to queue
                self.task_queue.append(completed_task)
                self._sort_queue()
                
        except Exception as e:
            logger.error(f"Error executing task {task.task_id}: {e}")
            task.state = TaskState.FAILED
            task.error = str(e)
            del self.active_tasks[task.task_id]
            self.failed_tasks[task.task_id] = task
    
    def _aggregate_results(self) -> Dict[str, Any]:
        """Aggregate results from all completed tasks"""
        results = {}
        
        for task_id, task in self.completed_tasks.items():
            results[task_id] = {
                "description": task.description,
                "agent_type": task.agent_type.value,
                "output": task.output_data,
                "duration_ms": task.duration_ms()
            }
        
        return results
    
    def get_status(self) -> Dict:
        """Get current swarm status"""
        return {
            "is_running": self.is_running,
            "queued_tasks": len(self.task_queue),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "agents": {
                agent_id: {
                    "type": agent.agent_type.value,
                    "is_busy": agent.is_busy,
                    "tasks_completed": agent.tasks_completed
                }
                for agent_id, agent in self.agents.items()
            }
        }


class TaskDecomposer:
    """
    Decomposes complex queries into subtasks for the agent swarm.
    """
    
    def __init__(self, llm_handler: Callable):
        self.llm_handler = llm_handler
    
    async def decompose(
        self,
        query: str,
        context: Optional[Dict] = None
    ) -> List[SwarmTask]:
        """
        Decompose a query into subtasks.
        
        Returns a list of SwarmTask objects with proper dependencies.
        """
        prompt = f"""Analyze this query and break it down into subtasks:

Query: {query}

Context: {json.dumps(context or {})}

For each subtask, specify:
1. Description of what needs to be done
2. Type: SEARCH, ANALYSIS, EXECUTION, or SYNTHESIS
3. Dependencies (which other tasks must complete first)

Respond with JSON:
{{
    "tasks": [
        {{
            "id": "task_1",
            "description": "...",
            "type": "SEARCH|ANALYSIS|EXECUTION|SYNTHESIS",
            "depends_on": [],
            "input": {{}}
        }}
    ]
}}

Always end with a SYNTHESIS task that combines all results."""

        try:
            response = await self.llm_handler(prompt)
            
            # Parse response
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            data = json.loads(response)
            
            tasks = []
            for task_data in data.get("tasks", []):
                agent_type = AgentType[task_data.get("type", "EXECUTION")]
                
                task = SwarmTask(
                    task_id=task_data.get("id", str(uuid.uuid4())[:8]),
                    description=task_data.get("description", ""),
                    agent_type=agent_type,
                    depends_on=set(task_data.get("depends_on", [])),
                    input_data=task_data.get("input", {})
                )
                tasks.append(task)
            
            return tasks
            
        except Exception as e:
            logger.error(f"Error decomposing query: {e}")
            
            # Fallback: simple decomposition
            return [
                SwarmTask(
                    task_id="search_1",
                    description=f"Search for information about: {query}",
                    agent_type=AgentType.SEARCH,
                    input_data={"query": query}
                ),
                SwarmTask(
                    task_id="synthesis_1",
                    description="Synthesize search results",
                    agent_type=AgentType.SYNTHESIS,
                    depends_on={"search_1"},
                    input_data={"query": query}
                )
            ]
