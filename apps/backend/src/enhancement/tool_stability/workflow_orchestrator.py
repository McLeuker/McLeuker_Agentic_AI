"""
Workflow Orchestrator - Complex Multi-Step Workflow Management
===============================================================

Orchestrates complex workflows with:
- Step dependencies
- Parallel execution
- Error handling
- State tracking
- Progress reporting
"""

import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """Step execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """A single step in a workflow"""
    id: str
    name: str
    description: str
    tool_name: str
    tool_params: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 3
    retry_delay: float = 1.0
    timeout: float = 60.0
    status: StepStatus = StepStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tool_name": self.tool_name,
            "tool_params": self.tool_params,
            "dependencies": self.dependencies,
            "retry_count": self.retry_count,
            "retry_delay": self.retry_delay,
            "timeout": self.timeout,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "execution_time_ms": self.execution_time_ms,
        }


@dataclass
class Workflow:
    """A complete workflow definition"""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": [s.to_dict() for s in self.steps],
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "metadata": self.metadata,
        }
    
    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Get a step by ID"""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None
    
    def get_ready_steps(self) -> List[WorkflowStep]:
        """Get steps that are ready to execute (dependencies met)"""
        ready = []
        completed_ids = {s.id for s in self.steps if s.status == StepStatus.COMPLETED}
        
        for step in self.steps:
            if step.status == StepStatus.PENDING:
                if all(dep in completed_ids for dep in step.dependencies):
                    ready.append(step)
        
        return ready
    
    def get_execution_order(self) -> List[WorkflowStep]:
        """Get steps in topological order"""
        executed = set()
        order = []
        
        while len(order) < len(self.steps):
            progress = False
            for step in self.steps:
                if step.id in executed:
                    continue
                if all(dep in executed for dep in step.dependencies):
                    order.append(step)
                    executed.add(step.id)
                    progress = True
            
            if not progress:
                # Circular dependency - add remaining
                for step in self.steps:
                    if step.id not in executed:
                        order.append(step)
                break
        
        return order


class WorkflowOrchestrator:
    """
    Orchestrates complex multi-step workflows.
    
    Features:
    - Dependency management
    - Parallel execution
    - Error recovery
    - Progress tracking
    - State persistence
    """
    
    def __init__(
        self,
        tool_registry,
        state_persistence=None,
        max_parallel_steps: int = 5,
    ):
        """
        Initialize workflow orchestrator.
        
        Args:
            tool_registry: Tool registry for executing steps
            state_persistence: Optional state persistence
            max_parallel_steps: Maximum parallel steps
        """
        self.tool_registry = tool_registry
        self.state_persistence = state_persistence
        self.max_parallel_steps = max_parallel_steps
        
        # Track running workflows
        self._active_workflows: Dict[str, Workflow] = {}
        self._cancelled: set = set()
    
    def create_workflow(
        self,
        name: str,
        description: str,
        steps: List[WorkflowStep],
        metadata: Optional[Dict] = None
    ) -> Workflow:
        """
        Create a new workflow.
        
        Args:
            name: Workflow name
            description: Workflow description
            steps: List of workflow steps
            metadata: Optional metadata
            
        Returns:
            Created workflow
        """
        workflow = Workflow(
            id=str(uuid4()),
            name=name,
            description=description,
            steps=steps,
            metadata=metadata or {}
        )
        
        if self.state_persistence:
            self.state_persistence.save_workflow(workflow)
        
        return workflow
    
    async def execute(
        self,
        workflow: Workflow,
        context: Optional[Dict] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute a workflow.
        
        Args:
            workflow: Workflow to execute
            context: Execution context
            
        Yields:
            Execution events
        """
        workflow_id = workflow.id
        self._active_workflows[workflow_id] = workflow
        
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now().isoformat()
        
        yield {
            "type": "workflow_started",
            "workflow_id": workflow_id,
            "name": workflow.name,
            "total_steps": len(workflow.steps)
        }
        
        try:
            execution_order = workflow.get_execution_order()
            
            for step in execution_order:
                if workflow_id in self._cancelled:
                    workflow.status = WorkflowStatus.CANCELLED
                    yield {"type": "workflow_cancelled", "workflow_id": workflow_id}
                    return
                
                # Check dependencies
                completed_ids = {s.id for s in workflow.steps if s.status == StepStatus.COMPLETED}
                if not all(dep in completed_ids for dep in step.dependencies):
                    # Wait for dependencies
                    yield {
                        "type": "step_waiting",
                        "step_id": step.id,
                        "step_name": step.name,
                        "waiting_for": step.dependencies
                    }
                    continue
                
                # Execute step
                async for event in self._execute_step(step, workflow, context):
                    yield event
                
                # Save state after each step
                if self.state_persistence:
                    self.state_persistence.save_workflow(workflow)
            
            # Check if all steps completed
            all_completed = all(s.status == StepStatus.COMPLETED for s in workflow.steps)
            
            if all_completed:
                workflow.status = WorkflowStatus.COMPLETED
                workflow.completed_at = datetime.now().isoformat()
                
                yield {
                    "type": "workflow_completed",
                    "workflow_id": workflow_id,
                    "total_time_ms": sum(s.execution_time_ms for s in workflow.steps),
                    "results": {s.id: s.result for s in workflow.steps}
                }
            else:
                workflow.status = WorkflowStatus.FAILED
                failed_steps = [s for s in workflow.steps if s.status == StepStatus.FAILED]
                
                yield {
                    "type": "workflow_failed",
                    "workflow_id": workflow_id,
                    "failed_steps": [s.id for s in failed_steps],
                    "errors": [s.error for s in failed_steps if s.error]
                }
        
        except Exception as e:
            logger.exception(f"Workflow execution failed: {e}")
            workflow.status = WorkflowStatus.FAILED
            yield {"type": "workflow_error", "workflow_id": workflow_id, "error": str(e)}
        
        finally:
            if workflow_id in self._active_workflows:
                del self._active_workflows[workflow_id]
            if workflow_id in self._cancelled:
                self._cancelled.remove(workflow_id)
    
    async def _execute_step(
        self,
        step: WorkflowStep,
        workflow: Workflow,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute a single workflow step"""
        
        step.status = StepStatus.RUNNING
        step.started_at = datetime.now().isoformat()
        
        yield {
            "type": "step_started",
            "workflow_id": workflow.id,
            "step_id": step.id,
            "step_name": step.name,
            "description": step.description
        }
        
        start_time = datetime.now()
        
        for attempt in range(step.retry_count + 1):
            try:
                # Execute tool
                result = await asyncio.wait_for(
                    self.tool_registry.execute_tool(
                        tool_name=step.tool_name,
                        params=step.tool_params
                    ),
                    timeout=step.timeout
                )
                
                step.execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
                step.result = result
                step.status = StepStatus.COMPLETED
                step.completed_at = datetime.now().isoformat()
                
                yield {
                    "type": "step_completed",
                    "workflow_id": workflow.id,
                    "step_id": step.id,
                    "step_name": step.name,
                    "execution_time_ms": step.execution_time_ms,
                    "result": result
                }
                
                return
                
            except asyncio.TimeoutError:
                step.status = StepStatus.RETRYING
                yield {
                    "type": "step_timeout",
                    "workflow_id": workflow.id,
                    "step_id": step.id,
                    "attempt": attempt + 1,
                    "max_attempts": step.retry_count + 1
                }
                
                if attempt < step.retry_count:
                    await asyncio.sleep(step.retry_delay * (attempt + 1))
                
            except Exception as e:
                logger.warning(f"Step {step.id} failed (attempt {attempt + 1}): {e}")
                
                step.status = StepStatus.RETRYING
                yield {
                    "type": "step_retry",
                    "workflow_id": workflow.id,
                    "step_id": step.id,
                    "attempt": attempt + 1,
                    "max_attempts": step.retry_count + 1,
                    "error": str(e)
                }
                
                if attempt < step.retry_count:
                    await asyncio.sleep(step.retry_delay * (attempt + 1))
                else:
                    step.error = str(e)
                    step.status = StepStatus.FAILED
                    step.execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
                    
                    yield {
                        "type": "step_failed",
                        "workflow_id": workflow.id,
                        "step_id": step.id,
                        "step_name": step.name,
                        "error": str(e),
                        "total_attempts": attempt + 1
                    }
    
    async def execute_parallel(
        self,
        workflow: Workflow,
        context: Optional[Dict] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute workflow with parallel step execution.
        
        Args:
            workflow: Workflow to execute
            context: Execution context
            
        Yields:
            Execution events
        """
        workflow_id = workflow.id
        self._active_workflows[workflow_id] = workflow
        
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now().isoformat()
        
        yield {
            "type": "workflow_started",
            "workflow_id": workflow_id,
            "name": workflow.name,
            "mode": "parallel",
            "total_steps": len(workflow.steps)
        }
        
        try:
            pending_steps = set(s.id for s in workflow.steps)
            completed_steps = set()
            failed_steps = set()
            
            semaphore = asyncio.Semaphore(self.max_parallel_steps)
            
            async def execute_with_limit(step: WorkflowStep):
                async with semaphore:
                    async for event in self._execute_step(step, workflow, context):
                        pass  # Events handled by caller
            
            while pending_steps:
                # Find ready steps
                ready = []
                for step in workflow.steps:
                    if step.id in pending_steps:
                        deps_met = all(dep in completed_steps for dep in step.dependencies)
                        if deps_met:
                            ready.append(step)
                
                if not ready:
                    if failed_steps:
                        break  # Can't proceed
                    await asyncio.sleep(0.1)
                    continue
                
                # Execute ready steps in parallel
                tasks = [execute_with_limit(step) for step in ready]
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Update tracking
                for step in ready:
                    pending_steps.discard(step.id)
                    if step.status == StepStatus.COMPLETED:
                        completed_steps.add(step.id)
                    elif step.status == StepStatus.FAILED:
                        failed_steps.add(step.id)
                
                yield {
                    "type": "progress_update",
                    "workflow_id": workflow_id,
                    "completed": len(completed_steps),
                    "failed": len(failed_steps),
                    "pending": len(pending_steps)
                }
            
            # Final status
            if failed_steps:
                workflow.status = WorkflowStatus.FAILED
                yield {
                    "type": "workflow_failed",
                    "workflow_id": workflow_id,
                    "failed_steps": list(failed_steps)
                }
            else:
                workflow.status = WorkflowStatus.COMPLETED
                workflow.completed_at = datetime.now().isoformat()
                yield {
                    "type": "workflow_completed",
                    "workflow_id": workflow_id
                }
        
        finally:
            if workflow_id in self._active_workflows:
                del self._active_workflows[workflow_id]
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        if workflow_id in self._active_workflows:
            self._cancelled.add(workflow_id)
            return True
        return False
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict]:
        """Get workflow status"""
        workflow = self._active_workflows.get(workflow_id)
        if not workflow:
            return None
        
        return {
            "workflow_id": workflow_id,
            "status": workflow.status.value,
            "progress": {
                "total": len(workflow.steps),
                "completed": sum(1 for s in workflow.steps if s.status == StepStatus.COMPLETED),
                "failed": sum(1 for s in workflow.steps if s.status == StepStatus.FAILED),
                "pending": sum(1 for s in workflow.steps if s.status == StepStatus.PENDING),
                "running": sum(1 for s in workflow.steps if s.status == StepStatus.RUNNING),
            }
        }
