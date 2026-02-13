"""
State Persistence - Workflow State Management
==============================================

Persists workflow state for:
- Recovery from failures
- Long-running workflows
- Progress tracking
- Audit trails
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import aiofiles

logger = logging.getLogger(__name__)


@dataclass
class WorkflowState:
    """Persisted workflow state"""
    workflow_id: str
    workflow_data: Dict[str, Any]
    created_at: str
    updated_at: str
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "workflow_data": self.workflow_data,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version,
        }


class StatePersistence:
    """
    Persists workflow state to storage.
    
    Supports:
    - File-based persistence
    - In-memory caching
    - State versioning
    - Cleanup
    """
    
    def __init__(
        self,
        storage_path: Optional[str] = None,
        max_age_hours: int = 24,
        enable_compression: bool = False
    ):
        """
        Initialize state persistence.
        
        Args:
            storage_path: Path for file storage (None for memory-only)
            max_age_hours: Maximum age before cleanup
            enable_compression: Enable compression for storage
        """
        self.storage_path = Path(storage_path) if storage_path else None
        self.max_age_hours = max_age_hours
        self.enable_compression = enable_compression
        
        # In-memory cache
        self._cache: Dict[str, WorkflowState] = {}
        
        # Create storage directory
        if self.storage_path:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            self._load_existing()
    
    def _load_existing(self):
        """Load existing workflows from storage"""
        if not self.storage_path:
            return
        
        try:
            for file_path in self.storage_path.glob("*.json"):
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                    
                    state = WorkflowState(
                        workflow_id=data["workflow_id"],
                        workflow_data=data["workflow_data"],
                        created_at=data["created_at"],
                        updated_at=data["updated_at"],
                        version=data.get("version", 1)
                    )
                    
                    self._cache[state.workflow_id] = state
                    
                except Exception as e:
                    logger.warning(f"Failed to load workflow from {file_path}: {e}")
            
            logger.info(f"Loaded {len(self._cache)} workflows from storage")
            
        except Exception as e:
            logger.error(f"Failed to load existing workflows: {e}")
    
    async def save_workflow(self, workflow) -> bool:
        """
        Save workflow state.
        
        Args:
            workflow: Workflow to save
            
        Returns:
            True if saved successfully
        """
        try:
            workflow_id = workflow.id if hasattr(workflow, 'id') else workflow.get('id')
            workflow_data = workflow.to_dict() if hasattr(workflow, 'to_dict') else workflow
            
            now = datetime.now().isoformat()
            
            # Update or create state
            if workflow_id in self._cache:
                state = self._cache[workflow_id]
                state.workflow_data = workflow_data
                state.updated_at = now
                state.version += 1
            else:
                state = WorkflowState(
                    workflow_id=workflow_id,
                    workflow_data=workflow_data,
                    created_at=now,
                    updated_at=now,
                    version=1
                )
                self._cache[workflow_id] = state
            
            # Persist to file if configured
            if self.storage_path:
                await self._persist_to_file(state)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save workflow: {e}")
            return False
    
    async def _persist_to_file(self, state: WorkflowState):
        """Persist state to file"""
        file_path = self.storage_path / f"{state.workflow_id}.json"
        
        async with aiofiles.open(file_path, "w") as f:
            await f.write(json.dumps(state.to_dict(), indent=2))
    
    def load_workflow(self, workflow_id: str) -> Optional[Dict]:
        """
        Load workflow state.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Workflow data or None if not found
        """
        state = self._cache.get(workflow_id)
        if state:
            return state.workflow_data
        return None
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete workflow state.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            True if deleted
        """
        if workflow_id in self._cache:
            del self._cache[workflow_id]
            
            # Delete file if exists
            if self.storage_path:
                file_path = self.storage_path / f"{workflow_id}.json"
                if file_path.exists():
                    file_path.unlink()
            
            return True
        
        return False
    
    def list_workflows(self) -> List[Dict]:
        """
        List all persisted workflows.
        
        Returns:
            List of workflow summaries
        """
        return [
            {
                "workflow_id": state.workflow_id,
                "created_at": state.created_at,
                "updated_at": state.updated_at,
                "version": state.version,
                "status": state.workflow_data.get("status", "unknown")
            }
            for state in self._cache.values()
        ]
    
    async def cleanup_old(self) -> int:
        """
        Clean up old workflow states.
        
        Returns:
            Number of workflows cleaned up
        """
        now = datetime.now()
        to_delete = []
        
        for workflow_id, state in self._cache.items():
            try:
                updated = datetime.fromisoformat(state.updated_at)
                age_hours = (now - updated).total_seconds() / 3600
                
                if age_hours > self.max_age_hours:
                    to_delete.append(workflow_id)
                    
            except Exception as e:
                logger.warning(f"Error checking age for {workflow_id}: {e}")
        
        for workflow_id in to_delete:
            self.delete_workflow(workflow_id)
        
        logger.info(f"Cleaned up {len(to_delete)} old workflows")
        return len(to_delete)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get persistence statistics"""
        return {
            "total_workflows": len(self._cache),
            "storage_path": str(self.storage_path) if self.storage_path else None,
            "max_age_hours": self.max_age_hours,
        }
