"""
Agent Swarm Coordinator - Central Hub for 100+ Agent Ecosystem
===============================================================

The Coordinator manages:
- Agent registration and discovery
- Task routing to appropriate agents
- Agent-to-agent communication
- Resource allocation
- Load balancing
- Fault tolerance
- Performance monitoring

Built on top of kimi-2.5 + grok-4-1-fast-reasoning model capabilities.
"""

import asyncio
import functools
import json
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union
from uuid import uuid4

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Agent lifecycle statuses."""
    IDLE = "idle"
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATING = "terminating"
    TERMINATED = "terminated"


class TaskPriority(int, Enum):
    """Task priority levels."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class AgentCapability:
    """Defines what an agent can do."""
    name: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    examples: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    average_execution_time: float = 30.0
    success_rate: float = 0.95


@dataclass
class AgentMetadata:
    """Metadata for an agent in the swarm."""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    category: str = "general"
    subcategory: str = ""
    capabilities: List[AgentCapability] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    required_tools: List[str] = field(default_factory=list)
    max_concurrent_tasks: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    author: str = ""
    llm_model: str = "kimi-k2.5"
    temperature: float = 0.7


@dataclass
class SwarmTask:
    """A task to be executed by the swarm."""
    id: str = field(default_factory=lambda: str(uuid4()))
    description: str = ""
    input_data: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    status: str = "pending"
    assigned_agent: Optional[str] = None
    parent_task: Optional[str] = None
    subtasks: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
    context: Dict[str, Any] = field(default_factory=dict)
    callback_url: Optional[str] = None


@dataclass
class AgentInstance:
    """Runtime instance of an agent in the swarm."""
    metadata: AgentMetadata
    status: AgentStatus = AgentStatus.IDLE
    current_tasks: List[str] = field(default_factory=list)
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    average_execution_time: float = 0.0
    last_active: datetime = field(default_factory=datetime.utcnow)
    health_score: float = 1.0
    error_count: int = 0
    instance_id: str = field(default_factory=lambda: str(uuid4()))


class AgentSwarmCoordinator:
    """
    Central coordinator for the agent swarm.
    
    Manages 100+ agents with:
    - Intelligent task routing
    - Load balancing
    - Agent health monitoring
    - Dynamic scaling
    - Fault tolerance
    """

    def __init__(
        self,
        llm_client: Any,
        reasoning_client: Any = None,
        tool_registry: Any = None,
        memory_manager: Any = None,
        max_concurrent_tasks: int = 100,
        task_timeout: int = 300,
        enable_load_balancing: bool = True,
    ):
        self.llm_client = llm_client
        self.reasoning_client = reasoning_client or llm_client
        self.tool_registry = tool_registry
        self.memory_manager = memory_manager
        self.max_concurrent_tasks = max_concurrent_tasks
        self.task_timeout = task_timeout
        self.enable_load_balancing = enable_load_balancing
        
        # Agent registry
        self._agents: Dict[str, Type] = {}
        self._agent_metadata: Dict[str, AgentMetadata] = {}
        self._agent_instances: Dict[str, AgentInstance] = {}
        self._agent_categories: Dict[str, Set[str]] = defaultdict(set)
        
        # Task management
        self._task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._active_tasks: Dict[str, SwarmTask] = {}
        self._completed_tasks: Dict[str, SwarmTask] = {}
        self._task_history: List[str] = []
        self._max_history = 10000
        
        # Communication
        self._message_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self._agent_communication_buffer: Dict[str, List[Dict]] = defaultdict(list)
        
        # Monitoring
        self._metrics: Dict[str, Any] = {
            "tasks_submitted": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "agents_registered": 0,
            "agents_active": 0,
        }
        
        # Background tasks
        self._monitoring_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        logger.info("AgentSwarmCoordinator initialized")

    async def start(self):
        """Start the coordinator background tasks."""
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("AgentSwarmCoordinator started")

    async def stop(self):
        """Stop the coordinator and all agents."""
        if self._monitoring_task:
            self._monitoring_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        for instance_id in list(self._agent_instances.keys()):
            await self.terminate_agent(instance_id)
        
        logger.info("AgentSwarmCoordinator stopped")

    # ==================== Agent Registration ====================

    def register_agent(
        self,
        agent_class: Type,
        metadata: AgentMetadata,
    ) -> "AgentSwarmCoordinator":
        """Register an agent class with the swarm."""
        agent_name = metadata.name
        
        if agent_name in self._agents:
            logger.warning(f"Agent '{agent_name}' already registered, updating")
        
        self._agents[agent_name] = agent_class
        self._agent_metadata[agent_name] = metadata
        self._agent_categories[metadata.category].add(agent_name)
        
        self._metrics["agents_registered"] += 1
        
        logger.info(f"Registered agent: {agent_name} (category: {metadata.category})")
        return self

    def register_agents_batch(
        self,
        agents: List[Tuple[Type, AgentMetadata]],
    ) -> "AgentSwarmCoordinator":
        """Register multiple agents at once."""
        for agent_class, metadata in agents:
            self.register_agent(agent_class, metadata)
        return self

    def unregister_agent(self, agent_name: str) -> bool:
        """Unregister an agent from the swarm."""
        if agent_name not in self._agents:
            return False
        
        instances_to_remove = [
            id for id, inst in self._agent_instances.items()
            if inst.metadata.name == agent_name
        ]
        for instance_id in instances_to_remove:
            asyncio.create_task(self.terminate_agent(instance_id))
        
        metadata = self._agent_metadata.pop(agent_name)
        self._agents.pop(agent_name)
        self._agent_categories[metadata.category].discard(agent_name)
        
        self._metrics["agents_registered"] -= 1
        logger.info(f"Unregistered agent: {agent_name}")
        return True

    def get_agent_metadata(self, agent_name: str) -> Optional[AgentMetadata]:
        """Get metadata for a registered agent."""
        return self._agent_metadata.get(agent_name)

    def list_agents(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[AgentMetadata]:
        """List registered agents with optional filtering."""
        agents = []
        
        agent_names = (
            self._agent_categories.get(category, set())
            if category
            else set(self._agents.keys())
        )
        
        for name in agent_names:
            metadata = self._agent_metadata.get(name)
            if metadata:
                if tags:
                    if not all(tag in metadata.tags for tag in tags):
                        continue
                agents.append(metadata)
        
        return agents

    def get_agents_by_capability(
        self,
        capability_name: str,
    ) -> List[AgentMetadata]:
        """Find agents that have a specific capability."""
        matching = []
        for metadata in self._agent_metadata.values():
            for cap in metadata.capabilities:
                if cap.name == capability_name:
                    matching.append(metadata)
                    break
        return matching

    # ==================== Agent Instance Management ====================

    async def spawn_agent(
        self,
        agent_name: str,
        instance_config: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Spawn a new instance of an agent."""
        if agent_name not in self._agents:
            logger.error(f"Cannot spawn unknown agent: {agent_name}")
            return None
        
        metadata = self._agent_metadata[agent_name]
        
        try:
            instance = AgentInstance(
                metadata=metadata,
                status=AgentStatus.INITIALIZING,
            )
            
            self._agent_instances[instance.instance_id] = instance
            instance.status = AgentStatus.READY
            
            self._metrics["agents_active"] += 1
            
            logger.info(f"Spawned agent instance: {instance.instance_id} ({agent_name})")
            return instance.instance_id
            
        except Exception as e:
            logger.error(f"Failed to spawn agent {agent_name}: {e}")
            return None

    async def terminate_agent(self, instance_id: str) -> bool:
        """Terminate an agent instance."""
        instance = self._agent_instances.get(instance_id)
        if not instance:
            return False
        
        instance.status = AgentStatus.TERMINATING
        
        for task_id in instance.current_tasks:
            await self.cancel_task(task_id)
        
        instance.status = AgentStatus.TERMINATED
        del self._agent_instances[instance_id]
        
        self._metrics["agents_active"] -= 1
        logger.info(f"Terminated agent instance: {instance_id}")
        return True

    def get_agent_instance(self, instance_id: str) -> Optional[AgentInstance]:
        """Get an agent instance by ID."""
        return self._agent_instances.get(instance_id)

    def get_agent_instances(
        self,
        agent_name: Optional[str] = None,
        status: Optional[AgentStatus] = None,
    ) -> List[AgentInstance]:
        """Get agent instances with optional filtering."""
        instances = []
        for instance in self._agent_instances.values():
            if agent_name and instance.metadata.name != agent_name:
                continue
            if status and instance.status != status:
                continue
            instances.append(instance)
        return instances

    # ==================== Task Management ====================

    async def submit_task(
        self,
        description: str,
        input_data: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        preferred_agent: Optional[str] = None,
        parent_task: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Submit a task to the swarm."""
        task = SwarmTask(
            description=description,
            input_data=input_data,
            priority=priority,
            parent_task=parent_task,
            context=context or {},
        )
        
        if preferred_agent:
            task.assigned_agent = preferred_agent
        
        await self._task_queue.put((
            priority.value,
            time.time(),
            task.id,
            task,
        ))
        
        self._active_tasks[task.id] = task
        self._metrics["tasks_submitted"] += 1
        
        logger.info(f"Submitted task: {task.id} (priority: {priority.name})")
        
        asyncio.create_task(self._process_tasks())
        
        return task.id

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task."""
        task = self._active_tasks.get(task_id)
        if not task:
            return False
        
        if task.status == "pending":
            task.status = "cancelled"
            return True
        
        if task.status == "running" and task.assigned_agent:
            await self._send_agent_message(
                task.assigned_agent,
                {"type": "cancel_task", "task_id": task_id},
            )
            return True
        
        return False

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task."""
        task = self._active_tasks.get(task_id) or self._completed_tasks.get(task_id)
        if not task:
            return None
        
        return {
            "id": task.id,
            "status": task.status,
            "description": task.description,
            "assigned_agent": task.assigned_agent,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "execution_time_ms": task.execution_time_ms,
            "result": task.result,
            "error": task.error,
        }

    async def wait_for_task(
        self,
        task_id: str,
        timeout: Optional[int] = None,
    ) -> Optional[SwarmTask]:
        """Wait for a task to complete."""
        start = time.time()
        timeout = timeout or self.task_timeout
        
        while time.time() - start < timeout:
            task = self._active_tasks.get(task_id) or self._completed_tasks.get(task_id)
            if task and task.status in ("completed", "failed", "cancelled"):
                return task
            await asyncio.sleep(0.1)
        
        return None

    # ==================== Task Routing & Execution ====================

    async def _process_tasks(self):
        """Process tasks from the queue."""
        while not self._task_queue.empty():
            active_count = sum(
                1 for t in self._active_tasks.values()
                if t.status == "running"
            )
            
            if active_count >= self.max_concurrent_tasks:
                await asyncio.sleep(0.1)
                continue
            
            try:
                priority, timestamp, task_id, task = self._task_queue.get_nowait()
                
                if task.status == "cancelled":
                    continue
                
                await self._route_task(task)
                
            except asyncio.QueueEmpty:
                break
            except Exception as e:
                logger.error(f"Error processing task: {e}")

    async def _route_task(self, task: SwarmTask):
        """Route a task to the best available agent."""
        if not task.assigned_agent:
            agent_name = await self._select_agent_for_task(task)
        else:
            agent_name = task.assigned_agent
        
        if not agent_name:
            task.status = "failed"
            task.error = "No suitable agent found"
            self._move_to_completed(task)
            return
        
        instance_id = await self._get_available_instance(agent_name)
        
        if not instance_id:
            instance_id = await self.spawn_agent(agent_name)
        
        if not instance_id:
            await self._task_queue.put((
                task.priority.value,
                time.time(),
                task.id,
                task,
            ))
            return
        
        task.assigned_agent = instance_id
        task.status = "running"
        task.started_at = datetime.utcnow()
        
        instance = self._agent_instances[instance_id]
        instance.status = AgentStatus.BUSY
        instance.current_tasks.append(task.id)
        
        asyncio.create_task(self._execute_task(task, instance_id))

    async def _select_agent_for_task(self, task: SwarmTask) -> Optional[str]:
        """Use grok-4-1-fast-reasoning to select the best agent for a task."""
        available_agents = list(self._agent_metadata.values())
        
        if not available_agents:
            return None
        
        agent_descriptions = []
        for metadata in available_agents:
            caps = [c.name for c in metadata.capabilities]
            agent_descriptions.append(
                f"- {metadata.name}: {metadata.description}\n"
                f"  Capabilities: {', '.join(caps)}\n"
                f"  Category: {metadata.category}"
            )
        
        prompt = f"""Given the following task and available agents, select the best agent to handle this task.

Task: {task.description}
Task Input: {json.dumps(task.input_data, indent=2)[:500]}

Available Agents:
{chr(10).join(agent_descriptions)}

Respond with ONLY the agent name that is best suited for this task. If no agent is suitable, respond with "NONE".

Best Agent:"""

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                functools.partial(
                    self.reasoning_client.chat.completions.create,
                    model="grok-4-1-fast-reasoning",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=50,
                )
            )
            
            agent_name = response.choices[0].message.content.strip()
            
            if agent_name == "NONE" or agent_name not in self._agents:
                return None
            
            return agent_name
            
        except Exception as e:
            logger.error(f"Failed to select agent: {e}")
            # Fallback: pick the first available agent
            if available_agents:
                return available_agents[0].name
            return None

    async def _get_available_instance(self, agent_name: str) -> Optional[str]:
        """Get an available instance of an agent."""
        instances = self.get_agent_instances(agent_name, AgentStatus.READY)
        
        if not instances:
            return None
        
        best_instance = min(instances, key=lambda i: len(i.current_tasks))
        
        if len(best_instance.current_tasks) < best_instance.metadata.max_concurrent_tasks:
            return best_instance.instance_id
        
        return None

    async def _execute_task(self, task: SwarmTask, instance_id: str):
        """Execute a task on an agent instance."""
        instance = self._agent_instances.get(instance_id)
        if not instance:
            task.status = "failed"
            task.error = "Agent instance not found"
            self._move_to_completed(task)
            return
        
        try:
            agent_class = self._agents[instance.metadata.name]
            
            # Create agent instance with LLM client and tool registry
            agent = agent_class(
                llm_client=self.llm_client,
                tool_registry=self.tool_registry,
                memory_manager=self.memory_manager,
                coordinator=self,
            )
            
            start_time = time.time()
            
            result = await asyncio.wait_for(
                agent.execute(task.description, task.input_data, task.context),
                timeout=self.task_timeout,
            )
            
            execution_time = int((time.time() - start_time) * 1000)
            
            task.status = "completed"
            task.result = result
            task.execution_time_ms = execution_time
            task.completed_at = datetime.utcnow()
            
            instance.total_tasks_completed += 1
            instance.average_execution_time = (
                (instance.average_execution_time * (instance.total_tasks_completed - 1) + execution_time)
                / instance.total_tasks_completed
            )
            
            self._metrics["tasks_completed"] += 1
            logger.info(f"Task completed: {task.id} ({execution_time}ms)")
            
        except asyncio.TimeoutError:
            task.status = "failed"
            task.error = f"Task timed out after {self.task_timeout}s"
            instance.total_tasks_failed += 1
            self._metrics["tasks_failed"] += 1
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            instance.total_tasks_failed += 1
            instance.error_count += 1
            self._metrics["tasks_failed"] += 1
            logger.error(f"Task failed: {task.id} - {e}")
        
        finally:
            if task.id in instance.current_tasks:
                instance.current_tasks.remove(task.id)
            
            if not instance.current_tasks:
                instance.status = AgentStatus.READY
            
            instance.last_active = datetime.utcnow()
            self._move_to_completed(task)
            asyncio.create_task(self._process_tasks())

    def _move_to_completed(self, task: SwarmTask):
        """Move a task from active to completed."""
        if task.id in self._active_tasks:
            del self._active_tasks[task.id]
        
        self._completed_tasks[task.id] = task
        self._task_history.append(task.id)
        
        if len(self._task_history) > self._max_history:
            old_id = self._task_history.pop(0)
            if old_id in self._completed_tasks:
                del self._completed_tasks[old_id]

    # ==================== Agent Communication ====================

    async def _send_agent_message(
        self,
        instance_id: str,
        message: Dict[str, Any],
    ):
        """Send a message to an agent instance."""
        self._agent_communication_buffer[instance_id].append({
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
        })

    def register_message_handler(
        self,
        message_type: str,
        handler: Callable,
    ):
        """Register a handler for agent messages."""
        self._message_handlers[message_type].append(handler)

    # ==================== Background Tasks ====================

    async def _monitoring_loop(self):
        """Background task for monitoring agent health."""
        while True:
            try:
                await asyncio.sleep(30)
                
                for instance in list(self._agent_instances.values()):
                    inactive_time = (datetime.utcnow() - instance.last_active).total_seconds()
                    
                    if inactive_time > 300:
                        instance.health_score *= 0.9
                    
                    if instance.error_count > 10:
                        instance.health_score *= 0.8
                    
                    if instance.health_score < 0.3:
                        logger.warning(f"Agent instance unhealthy: {instance.instance_id}")
                        await self.terminate_agent(instance.instance_id)
                        await self.spawn_agent(instance.metadata.name)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")

    async def _cleanup_loop(self):
        """Background task for cleaning up resources."""
        while True:
            try:
                await asyncio.sleep(300)
                
                cutoff = datetime.utcnow().timestamp() - 3600
                
                to_remove = []
                for task_id, task in self._completed_tasks.items():
                    if task.completed_at and task.completed_at.timestamp() < cutoff:
                        to_remove.append(task_id)
                
                for task_id in to_remove:
                    del self._completed_tasks[task_id]
                
                if to_remove:
                    logger.info(f"Cleaned up {len(to_remove)} old tasks")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")

    # ==================== Metrics & Stats ====================

    def get_metrics(self) -> Dict[str, Any]:
        """Get coordinator metrics."""
        return {
            **self._metrics,
            "active_tasks": len([t for t in self._active_tasks.values() if t.status == "running"]),
            "pending_tasks": self._task_queue.qsize(),
            "completed_tasks": len(self._completed_tasks),
            "agent_instances": len(self._agent_instances),
        }

    def get_agent_stats(self) -> Dict[str, Any]:
        """Get statistics for all agents."""
        stats = {}
        
        for name, metadata in self._agent_metadata.items():
            instances = self.get_agent_instances(name)
            
            stats[name] = {
                "metadata": {
                    "category": metadata.category,
                    "capabilities": [c.name for c in metadata.capabilities],
                },
                "instances": len(instances),
                "ready": len([i for i in instances if i.status == AgentStatus.READY]),
                "busy": len([i for i in instances if i.status == AgentStatus.BUSY]),
                "total_completed": sum(i.total_tasks_completed for i in instances),
                "total_failed": sum(i.total_tasks_failed for i in instances),
            }
        
        return stats
