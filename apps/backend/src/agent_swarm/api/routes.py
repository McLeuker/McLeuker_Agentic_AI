"""
Agent Swarm API Routes - FastAPI Endpoints
==========================================

REST API endpoints for the agent swarm system:
- Agent management (list, search, filter)
- Task submission and monitoring
- Instance management
- Metrics retrieval
- WebSocket for real-time updates
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from agent_swarm.agents.definitions import (
    AgentDefinition,
    get_agent_definition,
    search_agents,
    get_agents_by_capability,
    get_agents_by_category,
    AGENT_REGISTRY,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/swarm", tags=["agent-swarm"])


# ==================== Pydantic Models ====================

class SubmitTaskRequest(BaseModel):
    description: str = Field(..., description="Task description")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Task input data")
    priority: int = Field(default=3, ge=1, le=5, description="Task priority (1=critical, 5=background)")
    preferred_agent: Optional[str] = Field(None, description="Preferred agent name")
    required_capabilities: Optional[List[str]] = Field(None, description="Required capabilities")


class SubmitTaskResponse(BaseModel):
    task_id: str
    status: str
    assigned_agent: Optional[str] = None
    estimated_time: Optional[int] = None
    message: str


class TaskStatusResponse(BaseModel):
    id: str
    status: str
    description: str
    assigned_agent: Optional[str]
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    execution_time_ms: Optional[int]
    result: Optional[Any]
    error: Optional[str]


class AgentInfoResponse(BaseModel):
    name: str
    description: str
    category: str
    subcategory: str
    capabilities: List[str]
    required_tools: List[str]
    temperature: float
    tags: List[str]
    examples: List[str]


class SwarmMetricsResponse(BaseModel):
    total_agents: int
    active_agents: int
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    pending_tasks: int
    success_rate: float


class AgentInstanceResponse(BaseModel):
    instance_id: str
    agent_name: str
    status: str
    current_tasks: List[str]
    total_tasks_completed: int
    health_score: float


# ==================== Helper ====================

def _get_coordinator(request: Request):
    """Get coordinator from app state."""
    coordinator = getattr(request.app.state, "swarm_coordinator", None)
    if not coordinator:
        raise HTTPException(status_code=503, detail="Agent Swarm not initialized")
    return coordinator


def _get_router_instance(request: Request):
    """Get agent router from app state."""
    agent_router = getattr(request.app.state, "swarm_router", None)
    if not agent_router:
        raise HTTPException(status_code=503, detail="Agent Router not initialized")
    return agent_router


# ==================== Agent Listing ====================

@router.get("/agents", response_model=List[AgentInfoResponse])
async def list_all_agents(
    category: Optional[str] = None,
    capability: Optional[str] = None,
    search_query: Optional[str] = None,
):
    """List all available agents with optional filtering."""
    if search_query:
        agent_list = search_agents(search_query)
    elif capability:
        agent_list = get_agents_by_capability(capability)
    elif category:
        agent_list = get_agents_by_category(category)
    else:
        agent_list = list(AGENT_REGISTRY.values())
    
    return [
        AgentInfoResponse(
            name=a.name,
            description=a.description,
            category=a.category,
            subcategory=a.subcategory,
            capabilities=a.capabilities,
            required_tools=a.required_tools,
            temperature=a.temperature,
            tags=a.tags,
            examples=a.examples,
        )
        for a in agent_list
    ]


@router.get("/agents/{agent_name}", response_model=AgentInfoResponse)
async def get_agent(agent_name: str):
    """Get detailed information about a specific agent."""
    agent = get_agent_definition(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    return AgentInfoResponse(
        name=agent.name,
        description=agent.description,
        category=agent.category,
        subcategory=agent.subcategory,
        capabilities=agent.capabilities,
        required_tools=agent.required_tools,
        temperature=agent.temperature,
        tags=agent.tags,
        examples=agent.examples,
    )


@router.get("/categories")
async def list_categories():
    """List all agent categories with counts."""
    from collections import Counter
    counts = Counter(a.category for a in AGENT_REGISTRY.values())
    return {
        "categories": [
            {"name": cat, "count": count}
            for cat, count in sorted(counts.items())
        ],
        "total_agents": len(AGENT_REGISTRY),
    }


# ==================== Task Management ====================

@router.post("/tasks", response_model=SubmitTaskResponse)
async def submit_task(request_body: SubmitTaskRequest, request: Request):
    """Submit a new task to the agent swarm."""
    coordinator = _get_coordinator(request)
    
    try:
        from agent_swarm.core.coordinator import TaskPriority
        priority = TaskPriority(request_body.priority)
        
        assigned_agent = request_body.preferred_agent
        estimated_time = 60
        
        if not assigned_agent:
            try:
                agent_router = _get_router_instance(request)
                decision = await agent_router.route_task(
                    task_description=request_body.description,
                    input_data=request_body.input_data,
                    required_capabilities=request_body.required_capabilities,
                )
                if decision:
                    assigned_agent = decision.agent_name
                    estimated_time = decision.estimated_time
            except Exception as e:
                logger.warning(f"Router failed, using fallback: {e}")
        
        task_id = await coordinator.submit_task(
            description=request_body.description,
            input_data=request_body.input_data,
            priority=priority,
            preferred_agent=assigned_agent,
        )
        
        return SubmitTaskResponse(
            task_id=task_id,
            status="submitted",
            assigned_agent=assigned_agent,
            estimated_time=estimated_time,
            message="Task submitted successfully",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str, request: Request):
    """Get the status of a specific task."""
    coordinator = _get_coordinator(request)
    status = await coordinator.get_task_status(task_id)
    
    if not status:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    
    return TaskStatusResponse(**status)


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str, request: Request):
    """Cancel a pending or running task."""
    coordinator = _get_coordinator(request)
    success = await coordinator.cancel_task(task_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Task cannot be cancelled")
    
    return {"message": "Task cancelled successfully"}


# ==================== Instance Management ====================

@router.get("/instances", response_model=List[AgentInstanceResponse])
async def list_instances(
    agent_name: Optional[str] = None,
    status: Optional[str] = None,
    request: Request = None,
):
    """List active agent instances."""
    coordinator = _get_coordinator(request)
    from agent_swarm.core.coordinator import AgentStatus
    
    instances = coordinator.get_agent_instances(
        agent_name=agent_name,
        status=AgentStatus(status) if status else None,
    )
    
    return [
        AgentInstanceResponse(
            instance_id=inst.instance_id,
            agent_name=inst.metadata.name,
            status=inst.status.value,
            current_tasks=inst.current_tasks,
            total_tasks_completed=inst.total_tasks_completed,
            health_score=inst.health_score,
        )
        for inst in instances
    ]


@router.post("/agents/{agent_name}/spawn")
async def spawn_agent(agent_name: str, request: Request):
    """Spawn a new instance of an agent."""
    coordinator = _get_coordinator(request)
    instance_id = await coordinator.spawn_agent(agent_name)
    
    if not instance_id:
        raise HTTPException(status_code=400, detail=f"Failed to spawn agent '{agent_name}'")
    
    return {"instance_id": instance_id, "message": "Agent spawned successfully"}


@router.delete("/instances/{instance_id}")
async def terminate_instance(instance_id: str, request: Request):
    """Terminate an agent instance."""
    coordinator = _get_coordinator(request)
    success = await coordinator.terminate_agent(instance_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Instance '{instance_id}' not found")
    
    return {"message": "Instance terminated successfully"}


# ==================== Metrics ====================

@router.get("/metrics", response_model=SwarmMetricsResponse)
async def get_metrics(request: Request):
    """Get swarm-wide metrics."""
    coordinator = _get_coordinator(request)
    metrics = coordinator.get_metrics()
    
    submitted = metrics.get("tasks_submitted", 0)
    completed = metrics.get("tasks_completed", 0)
    
    return SwarmMetricsResponse(
        total_agents=metrics.get("agents_registered", 0),
        active_agents=metrics.get("agents_active", 0),
        total_tasks=submitted,
        completed_tasks=completed,
        failed_tasks=metrics.get("tasks_failed", 0),
        pending_tasks=metrics.get("pending_tasks", 0),
        success_rate=completed / submitted if submitted > 0 else 0,
    )


@router.get("/metrics/agents")
async def get_agent_metrics(request: Request):
    """Get per-agent metrics."""
    coordinator = _get_coordinator(request)
    return coordinator.get_agent_stats()


# ==================== Health ====================

@router.get("/health")
async def swarm_health():
    """Health check for the agent swarm."""
    return {
        "status": "healthy",
        "agents_registered": len(AGENT_REGISTRY),
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


# ==================== WebSocket ====================

@router.websocket("/ws")
async def swarm_websocket(websocket: WebSocket):
    """WebSocket for real-time swarm updates."""
    await websocket.accept()
    
    try:
        while True:
            message = await websocket.receive_json()
            msg_type = message.get("type")
            
            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
            elif msg_type == "subscribe_tasks":
                await websocket.send_json({
                    "type": "subscribed",
                    "channel": "tasks",
                })
            elif msg_type == "subscribe_metrics":
                await websocket.send_json({
                    "type": "subscribed",
                    "channel": "metrics",
                })
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}",
                })
    
    except WebSocketDisconnect:
        logger.info("Swarm WebSocket disconnected")
    except Exception as e:
        logger.error(f"Swarm WebSocket error: {e}")
