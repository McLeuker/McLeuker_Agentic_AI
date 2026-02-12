"""
Execution Engine for Agentic AI Task Processing
Handles task execution with step-by-step iteration and state management.
"""

from typing import Dict, Any, List, Optional
import asyncio
from dataclasses import dataclass, field
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ExecutionStep:
    step_id: str
    action: str
    parameters: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None

class TaskExecutor:
    """
    Core task execution engine with step iteration capabilities.
    """
    
    def __init__(self, state_manager=None, error_handler=None):
        self.state_manager = state_manager
        self.error_handler = error_handler
        self.active_tasks: Dict[str, List[ExecutionStep]] = {}
        
    async def execute_task(self, task_id: str, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute a task by iterating through its steps.
        
        Args:
            task_id: Unique identifier for the task
            steps: List of step definitions to execute
            
        Returns:
            Execution result with status and outputs
        """
        execution_steps = [
            ExecutionStep(
                step_id=step.get("id", f"step_{i}"),
                action=step.get("action"),
                parameters=step.get("parameters", {})
            )
            for i, step in enumerate(steps)
        ]
        
        self.active_tasks[task_id] = execution_steps
        
        results = []
        
        try:
            for step in execution_steps:
                step.status = TaskStatus.RUNNING
                
                # Update state if state manager available
                if self.state_manager:
                    await self.state_manager.set_state(
                        f"task:{task_id}:current_step", 
                        step.step_id
                    )
                
                # Execute step with error handling
                try:
                    result = await self._execute_step(step)
                    step.result = result
                    step.status = TaskStatus.COMPLETED
                    results.append({
                        "step_id": step.step_id,
                        "status": "completed",
                        "result": result
                    })
                    
                except Exception as e:
                    step.error = str(e)
                    step.status = TaskStatus.FAILED
                    
                    if self.error_handler:
                        should_retry = await self.error_handler.handle_error(
                            task_id, step, e
                        )
                        if should_retry:
                            # Retry logic would be implemented here
                            pass
                    else:
                        raise
                
            return {
                "task_id": task_id,
                "status": "completed",
                "steps_completed": len(results),
                "results": results
            }
            
        except Exception as e:
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "completed_steps": results
            }
        finally:
            if self.state_manager:
                await self.state_manager.set_state(
                    f"task:{task_id}:status", 
                    "completed" if not any(s.status == TaskStatus.FAILED for s in execution_steps) else "failed"
                )
    
    async def _execute_step(self, step: ExecutionStep) -> Any:
        """
        Execute a single step action.
        """
        # Placeholder for actual step execution logic
        # This would integrate with browser automation, LLM calls, etc.
        await asyncio.sleep(0.1)  # Simulate work
        return {"action": step.action, "parameters": step.parameters}
    
    def get_task_progress(self, task_id: str) -> Dict[str, Any]:
        """Get current progress of a task."""
        if task_id not in self.active_tasks:
            return {"error": "Task not found"}
            
        steps = self.active_tasks[task_id]
        completed = sum(1 for s in steps if s.status == TaskStatus.COMPLETED)
        
        return {
            "task_id": task_id,
            "total_steps": len(steps),
            "completed_steps": completed,
            "progress_percentage": (completed / len(steps)) * 100 if steps else 0,
            "steps": [
                {
                    "step_id": s.step_id,
                    "status": s.status.value,
                    "action": s.action
                }
                for s in steps
            ]
        }