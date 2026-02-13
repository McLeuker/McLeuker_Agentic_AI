"""
E2B Code Execution Integration
================================

Provides secure sandboxed code execution via E2B.
Used by the Execution Orchestrator for code steps.

Features:
- Python/Node.js/Bash execution
- File I/O within sandbox
- Package installation
- Timeout and resource limits
- Session management
"""

import os
import json
import asyncio
import functools
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# E2B SDK import – optional dependency
try:
    from e2b_code_interpreter import Sandbox
    E2B_AVAILABLE = True
except ImportError:
    E2B_AVAILABLE = False
    logger.warning("e2b_code_interpreter not installed – E2B features disabled. Install with: pip install e2b-code-interpreter")


@dataclass
class CodeExecutionResult:
    """Result of code execution in E2B sandbox"""
    success: bool
    output: str = ""
    error: str = ""
    execution_time_ms: float = 0
    files: List[Dict[str, str]] = field(default_factory=list)
    language: str = "python"
    sandbox_id: Optional[str] = None


@dataclass
class SandboxSession:
    """Active E2B sandbox session"""
    session_id: str
    sandbox: Any = None
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)
    language: str = "python"


class E2BManager:
    """
    Manages E2B sandbox sessions for code execution.

    Provides:
    - Session pooling and reuse
    - Multi-language support (Python, Node.js, Bash)
    - File upload/download
    - Automatic cleanup
    """

    def __init__(self, api_key: Optional[str] = None, max_sessions: int = 5):
        self.api_key = api_key or os.getenv("E2B_API_KEY", "")
        self.max_sessions = max_sessions
        self._sessions: Dict[str, SandboxSession] = {}
        self._available = E2B_AVAILABLE and bool(self.api_key)

        if self._available:
            os.environ["E2B_API_KEY"] = self.api_key
            logger.info("E2B Manager initialized")
        else:
            if not E2B_AVAILABLE:
                logger.warning("E2B SDK not installed")
            elif not self.api_key:
                logger.warning("E2B API key not set")

    @property
    def available(self) -> bool:
        return self._available

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    async def get_or_create_session(self, session_id: Optional[str] = None) -> Optional[SandboxSession]:
        """Get existing session or create a new one."""
        if not self._available:
            return None

        if session_id and session_id in self._sessions:
            session = self._sessions[session_id]
            session.last_used = datetime.now()
            return session

        # Clean up old sessions if at limit
        if len(self._sessions) >= self.max_sessions:
            await self._cleanup_oldest_session()

        try:
            loop = asyncio.get_event_loop()
            sandbox = await loop.run_in_executor(None, Sandbox)

            sid = session_id or f"e2b_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            session = SandboxSession(session_id=sid, sandbox=sandbox)
            self._sessions[sid] = session
            logger.info(f"E2B session created: {sid}")
            return session

        except Exception as e:
            logger.error(f"Failed to create E2B session: {e}")
            return None

    async def _cleanup_oldest_session(self):
        """Remove the oldest session."""
        if not self._sessions:
            return
        oldest_id = min(self._sessions, key=lambda k: self._sessions[k].last_used)
        await self.close_session(oldest_id)

    async def close_session(self, session_id: str):
        """Close and cleanup a session."""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            try:
                if session.sandbox:
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, session.sandbox.kill)
            except Exception as e:
                logger.warning(f"Error closing E2B session {session_id}: {e}")
            del self._sessions[session_id]
            logger.info(f"E2B session closed: {session_id}")

    async def close_all(self):
        """Close all sessions."""
        for sid in list(self._sessions.keys()):
            await self.close_session(sid)

    # ------------------------------------------------------------------
    # Code execution
    # ------------------------------------------------------------------

    async def execute_code(
        self,
        code: str,
        language: str = "python",
        session_id: Optional[str] = None,
        timeout: int = 30,
    ) -> CodeExecutionResult:
        """
        Execute code in E2B sandbox.

        Args:
            code: Code to execute
            language: Programming language (python, javascript, bash)
            session_id: Optional session ID for reuse
            timeout: Execution timeout in seconds

        Returns:
            CodeExecutionResult with output and metadata
        """
        if not self._available:
            return CodeExecutionResult(
                success=False,
                error="E2B not available. Install e2b-code-interpreter and set E2B_API_KEY.",
            )

        start_time = datetime.now()
        session = await self.get_or_create_session(session_id)

        if not session or not session.sandbox:
            return CodeExecutionResult(
                success=False,
                error="Failed to create E2B sandbox session",
                execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
            )

        try:
            loop = asyncio.get_event_loop()

            if language == "python":
                execution = await loop.run_in_executor(
                    None,
                    functools.partial(session.sandbox.run_code, code, timeout=timeout),
                )
            elif language in ("javascript", "js", "node"):
                # Write JS file and execute with node
                await loop.run_in_executor(
                    None,
                    functools.partial(session.sandbox.filesystem.write, "/tmp/script.js", code),
                )
                execution = await loop.run_in_executor(
                    None,
                    functools.partial(session.sandbox.run_code, f"import subprocess; result = subprocess.run(['node', '/tmp/script.js'], capture_output=True, text=True, timeout={timeout}); print(result.stdout); print(result.stderr)", timeout=timeout + 5),
                )
            elif language == "bash":
                execution = await loop.run_in_executor(
                    None,
                    functools.partial(session.sandbox.run_code, f"import subprocess; result = subprocess.run({repr(code)}, shell=True, capture_output=True, text=True, timeout={timeout}); print(result.stdout); print(result.stderr)", timeout=timeout + 5),
                )
            else:
                return CodeExecutionResult(
                    success=False,
                    error=f"Unsupported language: {language}",
                    execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                )

            exec_time = (datetime.now() - start_time).total_seconds() * 1000

            # Parse results
            output_text = ""
            error_text = ""

            if hasattr(execution, "logs"):
                if hasattr(execution.logs, "stdout"):
                    output_text = "\n".join(execution.logs.stdout) if isinstance(execution.logs.stdout, list) else str(execution.logs.stdout)
                if hasattr(execution.logs, "stderr"):
                    error_text = "\n".join(execution.logs.stderr) if isinstance(execution.logs.stderr, list) else str(execution.logs.stderr)

            if hasattr(execution, "error") and execution.error:
                error_text = str(execution.error)

            success = not bool(error_text) or (bool(output_text) and "Error" not in error_text)

            return CodeExecutionResult(
                success=success,
                output=output_text,
                error=error_text,
                execution_time_ms=exec_time,
                language=language,
                sandbox_id=session.session_id,
            )

        except Exception as e:
            logger.error(f"E2B execution error: {e}")
            return CodeExecutionResult(
                success=False,
                error=str(e),
                execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                language=language,
            )

    # ------------------------------------------------------------------
    # File operations
    # ------------------------------------------------------------------

    async def upload_file(
        self,
        session_id: str,
        remote_path: str,
        content: str,
    ) -> bool:
        """Upload a file to the sandbox."""
        if not self._available:
            return False

        session = self._sessions.get(session_id)
        if not session or not session.sandbox:
            return False

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                functools.partial(session.sandbox.filesystem.write, remote_path, content),
            )
            return True
        except Exception as e:
            logger.error(f"E2B file upload error: {e}")
            return False

    async def download_file(
        self,
        session_id: str,
        remote_path: str,
    ) -> Optional[str]:
        """Download a file from the sandbox."""
        if not self._available:
            return None

        session = self._sessions.get(session_id)
        if not session or not session.sandbox:
            return None

        try:
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(
                None,
                functools.partial(session.sandbox.filesystem.read, remote_path),
            )
            return content
        except Exception as e:
            logger.error(f"E2B file download error: {e}")
            return None

    async def install_packages(
        self,
        session_id: str,
        packages: List[str],
        language: str = "python",
    ) -> CodeExecutionResult:
        """Install packages in the sandbox."""
        if language == "python":
            cmd = f"pip install {' '.join(packages)}"
            code = f"import subprocess; result = subprocess.run('{cmd}', shell=True, capture_output=True, text=True); print(result.stdout); print(result.stderr)"
        elif language in ("javascript", "js", "node"):
            cmd = f"npm install {' '.join(packages)}"
            code = f"import subprocess; result = subprocess.run('{cmd}', shell=True, capture_output=True, text=True); print(result.stdout); print(result.stderr)"
        else:
            return CodeExecutionResult(success=False, error=f"Unsupported language: {language}")

        return await self.execute_code(code, "python", session_id, timeout=60)


# Global instance
_e2b_manager: Optional[E2BManager] = None


def get_e2b_manager() -> E2BManager:
    """Get or create global E2B manager."""
    global _e2b_manager
    if _e2b_manager is None:
        _e2b_manager = E2BManager()
    return _e2b_manager


def init_e2b(api_key: Optional[str] = None) -> E2BManager:
    """Initialize global E2B manager with API key."""
    global _e2b_manager
    _e2b_manager = E2BManager(api_key=api_key)
    return _e2b_manager
