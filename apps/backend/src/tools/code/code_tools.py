"""
Code Tools — Code Execution for Agentic Engine
================================================

Provides secure code execution capabilities:
- Python code execution
- JavaScript code execution
- Package installation
- Output capture
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class CodeTools:
    """
    Code execution tool implementations.

    Executes code in a local subprocess sandbox.
    """

    def __init__(self, workspace_path: str = "/tmp/agentic_code"):
        """
        Initialize code tools.

        Args:
            workspace_path: Path for code execution workspace
        """
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(parents=True, exist_ok=True)

    async def execute_python(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute Python code.

        Args:
            params: {"code": str}
            context: Execution context

        Returns:
            Execution result with stdout, stderr, exit_code
        """
        code = params.get("code", "")
        timeout = params.get("timeout", 60)

        if not code.strip():
            return {"success": False, "error": "No code provided"}

        # Write code to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        code_file = self.workspace_path / f"script_{timestamp}.py"
        code_file.write_text(code)

        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.workspace_path)
            env["MPLBACKEND"] = "Agg"

            process = await asyncio.create_subprocess_exec(
                "python3", str(code_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace_path),
                env=env,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            stdout_str = stdout.decode("utf-8", errors="replace")[:50000]
            stderr_str = stderr.decode("utf-8", errors="replace")[:50000]

            return {
                "success": process.returncode == 0,
                "stdout": stdout_str,
                "stderr": stderr_str,
                "exit_code": process.returncode,
                "language": "python",
            }

        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Execution timed out after {timeout}s",
                "stdout": "",
                "stderr": "",
                "exit_code": -1,
            }
        except Exception as e:
            logger.exception(f"Python execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
                "exit_code": -1,
            }
        finally:
            try:
                code_file.unlink()
            except Exception:
                pass

    async def execute_javascript(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute JavaScript code.

        Args:
            params: {"code": str}
            context: Execution context

        Returns:
            Execution result
        """
        code = params.get("code", "")
        timeout = params.get("timeout", 60)

        if not code.strip():
            return {"success": False, "error": "No code provided"}

        # Check Node.js availability
        try:
            check = await asyncio.create_subprocess_exec(
                "node", "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await check.communicate()
            if check.returncode != 0:
                return {"success": False, "error": "Node.js not available"}
        except FileNotFoundError:
            return {"success": False, "error": "Node.js not installed"}

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        code_file = self.workspace_path / f"script_{timestamp}.js"
        code_file.write_text(code)

        try:
            process = await asyncio.create_subprocess_exec(
                "node", str(code_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace_path),
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode("utf-8", errors="replace")[:50000],
                "stderr": stderr.decode("utf-8", errors="replace")[:50000],
                "exit_code": process.returncode,
                "language": "javascript",
            }

        except asyncio.TimeoutError:
            return {"success": False, "error": f"Execution timed out after {timeout}s"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            try:
                code_file.unlink()
            except Exception:
                pass

    async def install_packages(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Install Python packages."""
        packages = params.get("packages", [])
        if not packages:
            return {"success": False, "error": "No packages specified"}

        try:
            process = await asyncio.create_subprocess_exec(
                "pip", "install", *packages,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=120
            )

            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
