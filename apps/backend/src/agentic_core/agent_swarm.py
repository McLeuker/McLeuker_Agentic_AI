"""
AI Agent Swarm — Coordinated Multi-Agent Execution
===================================================

Coordinates multiple agents working together on complex tasks:
- Agent spawning and lifecycle management
- Task distribution and load balancing
- Inter-agent communication
- Result aggregation
- Conflict resolution

Enables swarm intelligence for complex problem-solving.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional, Callable
import openai

logger = logging.getLogger(__name__)


class SwarmStatus(Enum):
    """Status of a swarm execution."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"  # Some agents completed, some failed


class AgentRole(Enum):
    """Roles agents can have in a swarm."""
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    ANALYZER = "analyzer"
    GENERATOR = "generator"
    VALIDATOR = "validator"
    EXECUTOR = "executor"


@dataclass
class SwarmAgent:
    """An agent in the swarm."""
    agent_id: str
    name: str
    role: AgentRole
    handler: Callable
    capabilities: List[str]
    status: str = "idle"
    current_task: Optional[str] = None
    results: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role.value,
            "capabilities": self.capabilities,
            "status": self.status,
            "current_task": self.current_task,
            "results_count": len(self.results),
        }


@dataclass
class SwarmTask:
    """A task assigned to the swarm."""
    task_id: str
    description: str
    assigned_agents: List[str]
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"
    result: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "assigned_agents": self.assigned_agents,
            "dependencies": self.dependencies,
            "status": self.status,
            "result": self.result,
        }


@dataclass
class SwarmExecution:
    """Execution state of a swarm."""
    swarm_id: str
    original_request: str
    status: SwarmStatus
    agents: List[SwarmAgent]
    tasks: List[SwarmTask]
    aggregated_result: Optional[Dict] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "swarm_id": self.swarm_id,
            "original_request": self.original_request,
            "status": self.status.value,
            "agents": [a.to_dict() for a in self.agents],
            "tasks": [t.to_dict() for t in self.tasks],
            "aggregated_result": self.aggregated_result,
            "metadata": self.metadata,
        }


class AgentSwarm:
    """
    AI Agent Swarm for coordinated multi-agent execution.
    
    Usage:
        swarm = AgentSwarm(llm_client)
        
        # Register agents
        swarm.register_agent("researcher", research_agent_handler, [AgentRole.RESEARCHER])
        swarm.register_agent("writer", writer_agent_handler, [AgentRole.GENERATOR])
        
        # Execute
        async for event in swarm.execute("Research and write a report on AI"):
            print(event)
    """
    
    def __init__(
        self,
        llm_client: openai.AsyncOpenAI,
        model: str = "kimi-k2.5",
        max_concurrent_agents: int = 10,
    ):
        self.llm_client = llm_client
        self.model = model
        self.max_concurrent_agents = max_concurrent_agents
        
        # Registered agents (templates)
        self._agent_templates: Dict[str, Dict] = {}
        
        # Active swarm executions
        self._executions: Dict[str, SwarmExecution] = {}
    
    def register_agent(
        self,
        name: str,
        handler: Callable,
        roles: List[AgentRole],
        capabilities: List[str],
    ):
        """Register an agent template with the swarm."""
        self._agent_templates[name] = {
            "handler": handler,
            "roles": roles,
            "capabilities": capabilities,
        }
        logger.info(f"Registered agent template: {name} with roles: {[r.value for r in roles]}")
    
    async def execute(
        self,
        request: str,
        swarm_id: Optional[str] = None,
        num_agents: int = 5,
        coordination_strategy: str = "hierarchical",  # "hierarchical", "democratic", "specialized"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute a request using a swarm of agents.
        
        Args:
            request: The task to execute
            swarm_id: Optional swarm ID
            num_agents: Number of agents to spawn
            coordination_strategy: How agents coordinate
            
        Yields:
            Progress events and final results
        """
        import uuid
        swarm_id = swarm_id or str(uuid.uuid4())
        
        yield {"type": "start", "data": {"swarm_id": swarm_id, "request": request, "agents": num_agents}}
        
        try:
            # Step 1: Plan swarm composition
            yield {"type": "phase", "data": {"phase": "planning", "status": "started"}}
            
            swarm_plan = await self._plan_swarm(request, num_agents, coordination_strategy)
            
            yield {
                "type": "phase",
                "data": {
                    "phase": "planning",
                    "status": "completed",
                    "agents": len(swarm_plan.get("agents", [])),
                    "strategy": coordination_strategy,
                }
            }
            
            # Step 2: Spawn agents
            yield {"type": "phase", "data": {"phase": "spawning", "status": "started"}}
            
            agents = await self._spawn_agents(swarm_plan, swarm_id)
            
            yield {
                "type": "phase",
                "data": {
                    "phase": "spawning",
                    "status": "completed",
                    "agents": [a.to_dict() for a in agents],
                }
            }
            
            # Step 3: Create and distribute tasks
            yield {"type": "phase", "data": {"phase": "tasking", "status": "started"}}
            
            tasks = await self._create_tasks(request, agents, swarm_plan)
            
            yield {
                "type": "phase",
                "data": {
                    "phase": "tasking",
                    "status": "completed",
                    "tasks": len(tasks),
                }
            }
            
            # Step 4: Execute swarm
            yield {"type": "phase", "data": {"phase": "execution", "status": "started"}}
            
            execution = SwarmExecution(
                swarm_id=swarm_id,
                original_request=request,
                status=SwarmStatus.RUNNING,
                agents=agents,
                tasks=tasks,
            )
            self._executions[swarm_id] = execution
            
            # Execute tasks
            async for event in self._execute_swarm(execution):
                yield event
            
            yield {"type": "phase", "data": {"phase": "execution", "status": "completed"}}
            
            # Step 5: Aggregate results
            yield {"type": "phase", "data": {"phase": "aggregation", "status": "started"}}
            
            aggregated_result = await self._aggregate_results(execution)
            execution.aggregated_result = aggregated_result
            execution.status = SwarmStatus.COMPLETED
            
            yield {"type": "phase", "data": {"phase": "aggregation", "status": "completed"}}
            
            yield {
                "type": "complete",
                "data": {
                    "swarm_id": swarm_id,
                    "status": execution.status.value,
                    "result": aggregated_result,
                    "execution": execution.to_dict(),
                }
            }
            
        except Exception as e:
            logger.error(f"Error in swarm execution: {e}")
            yield {"type": "error", "data": {"swarm_id": swarm_id, "message": str(e)}}
    
    async def _plan_swarm(
        self,
        request: str,
        num_agents: int,
        coordination_strategy: str,
    ) -> Dict:
        """Plan the swarm composition and strategy."""
        available_agents = list(self._agent_templates.keys())
        
        messages = [
            {
                "role": "system",
                "content": f"""Plan a swarm of {num_agents} agents to execute this request.

Coordination strategy: {coordination_strategy}
Available agent types: {json.dumps(available_agents)}

Determine:
1. Which agent types to use
2. What role each agent should have
3. How tasks should be distributed

Respond with JSON:
{{
    "agents": [
        {{
            "name": "agent_name",
            "role": "coordinator|researcher|analyzer|generator|validator|executor",
            "task_description": "what this agent should do"
        }}
    ],
    "coordination_plan": "how agents will coordinate",
    "task_distribution": "how tasks will be distributed"
}}"""
            },
            {
                "role": "user",
                "content": f"Request: {request}"
            }
        ]
        
        response = await self.llm_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.5,
            max_tokens=2048,
            response_format={"type": "json_object"},
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _spawn_agents(
        self,
        swarm_plan: Dict,
        swarm_id: str,
    ) -> List[SwarmAgent]:
        """Spawn agents based on the swarm plan."""
        agents = []
        agent_configs = swarm_plan.get("agents", [])
        
        for i, config in enumerate(agent_configs):
            agent_id = f"{swarm_id}_agent_{i}"
            agent_name = config.get("name", f"agent_{i}")
            role_str = config.get("role", "executor")
            
            # Find matching template
            template = self._agent_templates.get(agent_name)
            if not template:
                # Use default handler
                template = {
                    "handler": self._default_handler,
                    "roles": [AgentRole.EXECUTOR],
                    "capabilities": [],
                }
            
            agent = SwarmAgent(
                agent_id=agent_id,
                name=agent_name,
                role=AgentRole(role_str),
                handler=template["handler"],
                capabilities=template["capabilities"],
            )
            agents.append(agent)
        
        return agents
    
    async def _create_tasks(
        self,
        request: str,
        agents: List[SwarmAgent],
        swarm_plan: Dict,
    ) -> List[SwarmTask]:
        """Create tasks for the swarm."""
        tasks = []
        
        # Break request into subtasks
        messages = [
            {
                "role": "system",
                "content": f"""Break this request into subtasks for {len(agents)} agents.

Respond with JSON:
{{
    "tasks": [
        {{
            "task_id": "task_1",
            "description": "Task description",
            "assigned_roles": ["researcher"],
            "dependencies": []
        }}
    ]
}}"""
            },
            {
                "role": "user",
                "content": f"Request: {request}"
            }
        ]
        
        response = await self.llm_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.5,
            max_tokens=2048,
            response_format={"type": "json_object"},
        )
        
        result = json.loads(response.choices[0].message.content)
        task_configs = result.get("tasks", [])
        
        for config in task_configs:
            # Find agents with matching roles
            assigned = [
                a.agent_id for a in agents
                if a.role.value in config.get("assigned_roles", [])
            ]
            
            task = SwarmTask(
                task_id=config.get("task_id", str(len(tasks))),
                description=config.get("description", ""),
                assigned_agents=assigned,
                dependencies=config.get("dependencies", []),
            )
            tasks.append(task)
        
        return tasks
    
    async def _execute_swarm(
        self,
        execution: SwarmExecution,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute the swarm tasks."""
        # Group tasks by dependencies
        pending_tasks = {t.task_id: t for t in execution.tasks}
        completed_tasks = set()
        
        while pending_tasks:
            # Find tasks ready to execute
            ready_tasks = [
                t for t in pending_tasks.values()
                if all(dep in completed_tasks for dep in t.dependencies)
            ]
            
            if not ready_tasks:
                # Circular dependency or stuck
                ready_tasks = [list(pending_tasks.values())[0]]
            
            # Execute ready tasks in parallel
            task_futures = []
            for task in ready_tasks:
                agents = [
                    a for a in execution.agents
                    if a.agent_id in task.assigned_agents
                ]
                if agents:
                    task_futures.append(self._execute_task(task, agents))
            
            # Wait for tasks to complete
            for future in asyncio.as_completed(task_futures):
                result = await future
                task_id = result.get("task_id")
                
                if task_id in pending_tasks:
                    pending_tasks[task_id].status = "completed"
                    pending_tasks[task_id].result = result
                    completed_tasks.add(task_id)
                    del pending_tasks[task_id]
                
                yield {"type": "task_complete", "data": result}
    
    async def _execute_task(
        self,
        task: SwarmTask,
        agents: List[SwarmAgent],
    ) -> Dict:
        """Execute a single task with assigned agents."""
        # Use first available agent
        agent = agents[0]
        agent.status = "working"
        agent.current_task = task.task_id
        
        try:
            # Execute agent handler
            result = await agent.handler(task.description)
            
            agent.results.append({
                "task_id": task.task_id,
                "result": result,
            })
            
            return {
                "task_id": task.task_id,
                "agent_id": agent.agent_id,
                "status": "success",
                "result": result,
            }
            
        except Exception as e:
            logger.error(f"Task execution error: {e}")
            return {
                "task_id": task.task_id,
                "agent_id": agent.agent_id,
                "status": "failed",
                "error": str(e),
            }
        
        finally:
            agent.status = "idle"
            agent.current_task = None
    
    async def _aggregate_results(
        self,
        execution: SwarmExecution,
    ) -> Dict:
        """Aggregate results from all agents."""
        all_results = []
        for task in execution.tasks:
            if task.result:
                all_results.append(task.result)
        
        # Use LLM to synthesize results
        messages = [
            {
                "role": "system",
                "content": """Synthesize the results from multiple agents into a coherent response.

Respond with JSON:
{
    "summary": "Overall summary",
    "key_findings": ["finding1", "finding2"],
    "detailed_results": {...},
    "confidence": "high|medium|low"
}"""
            },
            {
                "role": "user",
                "content": f"Original request: {execution.original_request}\n\nAgent results: {json.dumps(all_results)}"
            }
        ]
        
        response = await self.llm_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.5,
            max_tokens=4096,
            response_format={"type": "json_object"},
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _default_handler(self, task_description: str) -> Dict:
        """Default handler for agents without specific handlers."""
        # This would be replaced with actual agent logic
        return {"task": task_description, "status": "completed"}
    
    def get_execution(self, swarm_id: str) -> Optional[SwarmExecution]:
        """Get a swarm execution by ID."""
        return self._executions.get(swarm_id)


# Singleton instance
_agent_swarm: Optional[AgentSwarm] = None


def get_agent_swarm(llm_client: openai.AsyncOpenAI = None) -> AgentSwarm:
    """Get or create the Agent Swarm singleton."""
    global _agent_swarm
    if _agent_swarm is None and llm_client:
        _agent_swarm = AgentSwarm(llm_client)
    return _agent_swarm
