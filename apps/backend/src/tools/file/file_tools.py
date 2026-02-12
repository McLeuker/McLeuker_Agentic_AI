"""
File Tools — File Operations for Agentic Engine
=================================================

Provides file system operations:
- Read/write files
- Directory listing
- File generation (code, documents, data)
- File type detection
"""

import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import mimetypes

logger = logging.getLogger(__name__)


class FileTools:
    """
    File operation tool implementations.

    Provides safe file operations within workspace boundaries.
    """

    def __init__(self, workspace_path: str = "/tmp/agentic_files"):
        """
        Initialize file tools.

        Args:
            workspace_path: Base path for file operations
        """
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(parents=True, exist_ok=True)

    def _safe_path(self, path: str) -> Path:
        """Ensure path is within workspace."""
        resolved = Path(path).resolve()
        workspace_resolved = self.workspace_path.resolve()

        # Allow paths within workspace or /tmp
        if str(resolved).startswith(str(workspace_resolved)) or str(resolved).startswith("/tmp"):
            return resolved

        # Default to workspace
        return self.workspace_path / Path(path).name

    async def read_file(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Read content from a file."""
        path = params.get("path", "")
        if not path:
            return {"error": "No path provided"}

        safe_path = self._safe_path(path)

        try:
            if not safe_path.exists():
                return {"error": f"File not found: {path}"}

            mime_type, _ = mimetypes.guess_type(str(safe_path))
            size = safe_path.stat().st_size

            # Read text files
            if mime_type and mime_type.startswith("text/") or safe_path.suffix in [
                ".py", ".js", ".json", ".md", ".csv", ".txt", ".html", ".css", ".yaml", ".yml", ".xml"
            ]:
                content = safe_path.read_text(errors="replace")
                return {
                    "path": str(safe_path),
                    "content": content[:100000],
                    "size": size,
                    "mime_type": mime_type,
                    "truncated": size > 100000,
                }
            else:
                return {
                    "path": str(safe_path),
                    "content": f"[Binary file: {mime_type or 'unknown'}, {size} bytes]",
                    "size": size,
                    "mime_type": mime_type,
                    "binary": True,
                }

        except Exception as e:
            logger.exception(f"File read error: {e}")
            return {"error": str(e), "path": path}

    async def write_file(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Write content to a file."""
        path = params.get("path", "")
        content = params.get("content", "")

        if not path:
            return {"error": "No path provided"}

        safe_path = self._safe_path(path)

        try:
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            safe_path.write_text(content)

            return {
                "path": str(safe_path),
                "size": safe_path.stat().st_size,
                "success": True,
            }

        except Exception as e:
            logger.exception(f"File write error: {e}")
            return {"error": str(e), "path": path}

    async def list_directory(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """List files in a directory."""
        path = params.get("path", str(self.workspace_path))
        safe_path = self._safe_path(path)

        try:
            if not safe_path.exists():
                return {"error": f"Directory not found: {path}"}

            if not safe_path.is_dir():
                return {"error": f"Not a directory: {path}"}

            entries = []
            for entry in sorted(safe_path.iterdir()):
                stat = entry.stat()
                entries.append({
                    "name": entry.name,
                    "type": "directory" if entry.is_dir() else "file",
                    "size": stat.st_size if entry.is_file() else 0,
                    "path": str(entry),
                })

            return {
                "path": str(safe_path),
                "entries": entries,
                "count": len(entries),
            }

        except Exception as e:
            logger.exception(f"Directory list error: {e}")
            return {"error": str(e), "path": path}

    async def create_file(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a file with generated content."""
        filename = params.get("filename", "output.txt")
        content = params.get("content", "")
        file_type = params.get("file_type", "text")

        safe_path = self.workspace_path / filename

        try:
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            safe_path.write_text(content)

            return {
                "path": str(safe_path),
                "filename": filename,
                "size": safe_path.stat().st_size,
                "file_type": file_type,
                "success": True,
            }

        except Exception as e:
            logger.exception(f"File creation error: {e}")
            return {"error": str(e)}

    async def delete_file(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Delete a file."""
        path = params.get("path", "")
        safe_path = self._safe_path(path)

        try:
            if safe_path.exists():
                safe_path.unlink()
                return {"success": True, "path": str(safe_path)}
            else:
                return {"error": f"File not found: {path}"}

        except Exception as e:
            return {"error": str(e)}
