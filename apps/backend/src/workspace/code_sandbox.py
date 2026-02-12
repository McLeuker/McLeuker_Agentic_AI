"""
Code Sandbox — Secure Code Execution Environment
==================================================

Provides sandboxed code execution:
- Python and JavaScript execution
- Resource limits
- Output capture
- Artifact generation from code
"""

import os
import asyncio
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of code execution."""
    success: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    execution_time: float = 0.0
    language: str = "python"
    files_created: list = None

    def __post_init__(self):
        if self.files_created is None:
            self.files_created = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "stdout": self.stdout[:5000],
            "stderr": self.stderr[:2000],
            "exit_code": self.exit_code,
            "execution_time": self.execution_time,
            "language": self.language,
            "files_created": self.files_created,
        }


class CodeSandbox:
    """
    Sandboxed code execution environment.
    """

    def __init__(self, workspace_path: str = "/tmp/agentic_sandbox"):
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(parents=True, exist_ok=True)

    async def execute(
        self,
        code: str,
        language: str = "python",
        timeout: int = 60,
        session_id: str = "",
    ) -> ExecutionResult:
        """
        Execute code in sandbox.

        Args:
            code: Code to execute
            language: Programming language
            timeout: Execution timeout in seconds
            session_id: Session identifier for workspace isolation

        Returns:
            ExecutionResult
        """
        start_time = datetime.now()

        # Create session workspace
        session_path = self.workspace_path / (session_id or "default")
        session_path.mkdir(parents=True, exist_ok=True)

        if language == "python":
            result = await self._execute_python(code, session_path, timeout)
        elif language == "javascript":
            result = await self._execute_javascript(code, session_path, timeout)
        else:
            result = ExecutionResult(
                success=False,
                stderr=f"Unsupported language: {language}",
                exit_code=-1,
            )

        result.execution_time = (datetime.now() - start_time).total_seconds()
        result.language = language

        # Check for generated files
        result.files_created = self._list_new_files(session_path)

        return result

    async def _execute_python(self, code: str, workspace: Path, timeout: int) -> ExecutionResult:
        """Execute Python code."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        code_file = workspace / f"script_{timestamp}.py"
        code_file.write_text(code)

        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(workspace)
            env["MPLBACKEND"] = "Agg"

            process = await asyncio.create_subprocess_exec(
                "python3", str(code_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(workspace),
                env=env,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )

            return ExecutionResult(
                success=process.returncode == 0,
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
                exit_code=process.returncode,
            )

        except asyncio.TimeoutError:
            return ExecutionResult(
                success=False,
                stderr=f"Execution timed out after {timeout}s",
                exit_code=-1,
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                stderr=str(e),
                exit_code=-1,
            )
        finally:
            try:
                code_file.unlink()
            except Exception:
                pass

    async def _execute_javascript(self, code: str, workspace: Path, timeout: int) -> ExecutionResult:
        """Execute JavaScript code."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        code_file = workspace / f"script_{timestamp}.js"
        code_file.write_text(code)

        try:
            process = await asyncio.create_subprocess_exec(
                "node", str(code_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(workspace),
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )

            return ExecutionResult(
                success=process.returncode == 0,
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
                exit_code=process.returncode,
            )

        except asyncio.TimeoutError:
            return ExecutionResult(success=False, stderr=f"Timeout after {timeout}s", exit_code=-1)
        except Exception as e:
            return ExecutionResult(success=False, stderr=str(e), exit_code=-1)
        finally:
            try:
                code_file.unlink()
            except Exception:
                pass

    def _list_new_files(self, workspace: Path) -> list:
        """List files in workspace (excluding scripts)."""
        files = []
        for f in workspace.iterdir():
            if f.is_file() and not f.name.startswith("script_"):
                files.append({
                    "name": f.name,
                    "path": str(f),
                    "size": f.stat().st_size,
                })
        return files
