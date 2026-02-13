"""
McLeuker Workspace Layer — File Management, Artifacts, and Code Sandbox
========================================================================

Provides workspace capabilities:
- WorkspaceManager: Per-session file workspace
- ArtifactStore: Generated artifact management
- CodeSandbox: Secure code execution environment
"""

from .workspace_manager import WorkspaceManager
from .artifact_store import ArtifactStore, Artifact
from .code_sandbox import CodeSandbox

__all__ = [
    "WorkspaceManager",
    "ArtifactStore", "Artifact",
    "CodeSandbox",
]
