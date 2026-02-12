"""
Workspace Manager — Per-Session File Workspace
================================================

Manages isolated file workspaces for each execution session:
- Session workspace creation and cleanup
- File operations within workspace
- Workspace listing and stats
"""

import logging
import shutil
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class WorkspaceManager:
    """
    Manages per-session file workspaces.
    """

    def __init__(self, base_path: str = "/tmp/agentic_workspaces"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._workspaces: Dict[str, Path] = {}

    def create_workspace(self, session_id: str) -> Path:
        """Create a workspace for a session."""
        workspace_path = self.base_path / session_id
        workspace_path.mkdir(parents=True, exist_ok=True)
        self._workspaces[session_id] = workspace_path
        logger.info(f"Created workspace: {workspace_path}")
        return workspace_path

    def get_workspace(self, session_id: str) -> Optional[Path]:
        """Get workspace path for a session."""
        if session_id in self._workspaces:
            return self._workspaces[session_id]
        # Check if exists on disk
        workspace_path = self.base_path / session_id
        if workspace_path.exists():
            self._workspaces[session_id] = workspace_path
            return workspace_path
        return None

    def list_files(self, session_id: str) -> List[Dict[str, Any]]:
        """List files in a session workspace."""
        workspace = self.get_workspace(session_id)
        if not workspace:
            return []

        files = []
        for path in sorted(workspace.rglob("*")):
            if path.is_file():
                files.append({
                    "name": path.name,
                    "path": str(path.relative_to(workspace)),
                    "size": path.stat().st_size,
                    "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
                })
        return files

    def cleanup_workspace(self, session_id: str) -> bool:
        """Clean up a session workspace."""
        workspace = self.get_workspace(session_id)
        if not workspace:
            return False

        try:
            shutil.rmtree(workspace)
            if session_id in self._workspaces:
                del self._workspaces[session_id]
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup workspace {session_id}: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get workspace statistics."""
        total_size = 0
        for workspace in self._workspaces.values():
            if workspace.exists():
                for f in workspace.rglob("*"):
                    if f.is_file():
                        total_size += f.stat().st_size

        return {
            "active_workspaces": len(self._workspaces),
            "total_size_bytes": total_size,
        }
