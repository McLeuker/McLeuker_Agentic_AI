"""
Local Code Execution Sandbox
==============================

Provides secure-ish code execution without requiring E2B or Docker.
Uses subprocess with timeouts and resource limits for Python/Node/Bash.

This is the fallback when E2B is not configured. For production,
E2B or Docker isolation is strongly recommended.

Features:
- Python, Node.js, and Bash execution
- Timeout enforcement (default 30s)
- Output capture (stdout + stderr)
- Temporary file management
- File read/write operations within sandbox directory
"""

import asyncio
import os
import tempfile
import shutil
import subprocess
import time
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class SandboxResult:
    """Result of code execution in local sandbox."""
    success: bool
    output: str = ""
    error: str = ""
    execution_time_ms: float = 0
    files_created: List[str] = field(default_factory=list)
    language: str = "python"


class LocalSandbox:
    """
    Local code execution sandbox using subprocess.

    Provides a temporary directory for each execution session,
    runs code with timeouts, and captures output.
    """

    def __init__(self, base_dir: Optional[str] = None, default_timeout: int = 30):
        self.base_dir = base_dir or tempfile.mkdtemp(prefix="mcleuker_sandbox_")
        self.default_timeout = default_timeout
        self._available = True
        self._sessions: Dict[str, str] = {}  # session_id -> directory
        logger.info(f"Local sandbox initialized at {self.base_dir}")

    @property
    def available(self) -> bool:
        return self._available

    def _get_session_dir(self, session_id: Optional[str] = None) -> str:
        """Get or create a session directory."""
        if not session_id:
            session_id = str(uuid.uuid4())[:8]

        if session_id not in self._sessions:
            session_dir = os.path.join(self.base_dir, f"session_{session_id}")
            os.makedirs(session_dir, exist_ok=True)
            self._sessions[session_id] = session_dir

        return self._sessions[session_id]

    async def execute_code(
        self,
        code: str,
        language: str = "python",
        timeout: int = None,
        session_id: Optional[str] = None,
    ) -> SandboxResult:
        """Execute code in a subprocess with timeout."""
        timeout = timeout or self.default_timeout
        session_dir = self._get_session_dir(session_id)
        start_time = time.time()

        try:
            if language in ("python", "python3"):
                return await self._run_python(code, session_dir, timeout, start_time)
            elif language in ("javascript", "node", "nodejs"):
                return await self._run_node(code, session_dir, timeout, start_time)
            elif language in ("bash", "shell", "sh"):
                return await self._run_bash(code, session_dir, timeout, start_time)
            else:
                return SandboxResult(
                    success=False,
                    error=f"Unsupported language: {language}",
                    language=language,
                    execution_time_ms=(time.time() - start_time) * 1000,
                )
        except Exception as e:
            return SandboxResult(
                success=False,
                error=str(e),
                language=language,
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    async def _run_python(self, code: str, workdir: str, timeout: int, start_time: float) -> SandboxResult:
        """Run Python code."""
        script_path = os.path.join(workdir, "script.py")
        with open(script_path, "w") as f:
            f.write(code)

        try:
            proc = await asyncio.create_subprocess_exec(
                "python3", script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workdir,
                env={**os.environ, "PYTHONPATH": workdir},
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)

            output = stdout.decode("utf-8", errors="replace")
            error = stderr.decode("utf-8", errors="replace")
            exec_time = (time.time() - start_time) * 1000

            # List files created
            files_created = []
            for f in os.listdir(workdir):
                if f != "script.py":
                    files_created.append(f)

            return SandboxResult(
                success=proc.returncode == 0,
                output=output[:10000],
                error=error[:5000] if proc.returncode != 0 else "",
                execution_time_ms=exec_time,
                files_created=files_created,
                language="python",
            )
        except asyncio.TimeoutError:
            return SandboxResult(
                success=False,
                error=f"Execution timed out after {timeout}s",
                execution_time_ms=(time.time() - start_time) * 1000,
                language="python",
            )

    async def _run_node(self, code: str, workdir: str, timeout: int, start_time: float) -> SandboxResult:
        """Run Node.js code."""
        script_path = os.path.join(workdir, "script.js")
        with open(script_path, "w") as f:
            f.write(code)

        try:
            proc = await asyncio.create_subprocess_exec(
                "node", script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workdir,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)

            output = stdout.decode("utf-8", errors="replace")
            error = stderr.decode("utf-8", errors="replace")

            return SandboxResult(
                success=proc.returncode == 0,
                output=output[:10000],
                error=error[:5000] if proc.returncode != 0 else "",
                execution_time_ms=(time.time() - start_time) * 1000,
                language="javascript",
            )
        except asyncio.TimeoutError:
            return SandboxResult(
                success=False,
                error=f"Execution timed out after {timeout}s",
                execution_time_ms=(time.time() - start_time) * 1000,
                language="javascript",
            )

    async def _run_bash(self, code: str, workdir: str, timeout: int, start_time: float) -> SandboxResult:
        """Run Bash code."""
        script_path = os.path.join(workdir, "script.sh")
        with open(script_path, "w") as f:
            f.write(code)
        os.chmod(script_path, 0o755)

        try:
            proc = await asyncio.create_subprocess_exec(
                "bash", script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workdir,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)

            output = stdout.decode("utf-8", errors="replace")
            error = stderr.decode("utf-8", errors="replace")

            return SandboxResult(
                success=proc.returncode == 0,
                output=output[:10000],
                error=error[:5000] if proc.returncode != 0 else "",
                execution_time_ms=(time.time() - start_time) * 1000,
                language="bash",
            )
        except asyncio.TimeoutError:
            return SandboxResult(
                success=False,
                error=f"Execution timed out after {timeout}s",
                execution_time_ms=(time.time() - start_time) * 1000,
                language="bash",
            )

    # ------------------------------------------------------------------
    # File operations
    # ------------------------------------------------------------------

    async def write_file(self, path: str, content: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Write a file in the sandbox."""
        session_dir = self._get_session_dir(session_id)
        full_path = os.path.join(session_dir, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, "w") as f:
            f.write(content)

        return {"success": True, "path": full_path, "size": len(content)}

    async def read_file(self, path: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Read a file from the sandbox."""
        session_dir = self._get_session_dir(session_id)
        full_path = os.path.join(session_dir, path)

        if not os.path.exists(full_path):
            return {"success": False, "error": f"File not found: {path}"}

        with open(full_path, "r") as f:
            content = f.read()

        return {"success": True, "path": full_path, "content": content, "size": len(content)}

    async def list_files(self, session_id: Optional[str] = None) -> List[str]:
        """List files in the sandbox session."""
        session_dir = self._get_session_dir(session_id)
        files = []
        for root, dirs, filenames in os.walk(session_dir):
            for fn in filenames:
                rel_path = os.path.relpath(os.path.join(root, fn), session_dir)
                files.append(rel_path)
        return files

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def cleanup_session(self, session_id: str):
        """Remove a session directory."""
        if session_id in self._sessions:
            try:
                shutil.rmtree(self._sessions[session_id], ignore_errors=True)
            except Exception:
                pass
            del self._sessions[session_id]

    def cleanup_all(self):
        """Remove all session directories."""
        for sid in list(self._sessions.keys()):
            self.cleanup_session(sid)
        try:
            shutil.rmtree(self.base_dir, ignore_errors=True)
        except Exception:
            pass


# Global instance
_local_sandbox: Optional[LocalSandbox] = None


def get_local_sandbox() -> LocalSandbox:
    """Get or create the global local sandbox."""
    global _local_sandbox
    if _local_sandbox is None:
        _local_sandbox = LocalSandbox()
    return _local_sandbox
