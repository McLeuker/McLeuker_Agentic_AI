"""
GitHub Tools — Code Repository Operations (FIXED)
=================================================

CRITICAL FIXES:
1. Fixed file operation parsing that was causing "Could not parse file operation details" error
2. Added robust JSON parsing with fallback to regex extraction
3. Added validation for all required fields
4. Added better error messages for debugging
5. Added support for both string and dict content inputs

Provides tools for:
- Creating repositories
- Reading file contents
- Writing/updating files
- Pushing changes
- Creating pull requests
"""

import os
import re
import json
import base64
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

import httpx

logger = logging.getLogger(__name__)

# GitHub API configuration
GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_ACCESS_TOKEN")


class FileOperationType(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RENAME = "rename"


@dataclass
class FileOperation:
    """Represents a single file operation."""
    path: str
    content: Union[str, bytes]
    operation: FileOperationType = FileOperationType.CREATE
    message: str = "Update file"
    sha: Optional[str] = None  # Required for updates
    encoding: str = "utf-8"


@dataclass
class GitHubFile:
    """Represents a file in a GitHub repository."""
    path: str
    content: str
    sha: str
    size: int
    encoding: str
    url: str


class GitHubTools:
    """GitHub API tools for repository operations."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or GITHUB_TOKEN
        if not self.token:
            logger.warning("GitHub token not configured")
        
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        }

    # ========================================================================
    # FIXED: Repository Operations
    # ========================================================================

    async def create_repository(
        self,
        name: str,
        description: str = "",
        private: bool = False,
        auto_init: bool = True
    ) -> Dict[str, Any]:
        """Create a new GitHub repository."""
        if not self.token:
            return {"error": "GitHub token not configured"}

        url = f"{GITHUB_API_BASE}/user/repos"
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": auto_init,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=data,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to create repository: {e}")
            return {"error": f"Failed to create repository: {str(e)}"}

    async def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information."""
        if not self.token:
            return {"error": "GitHub token not configured"}

        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=30.0)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get repository: {e}")
            return {"error": f"Failed to get repository: {str(e)}"}

    # ========================================================================
    # FIXED: File Content Operations
    # ========================================================================

    async def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: str = "main"
    ) -> Union[GitHubFile, Dict[str, str]]:
        """Get the content of a file from a repository."""
        if not self.token:
            return {"error": "GitHub token not configured"}

        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
        params = {"ref": ref}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                # Decode content
                content = base64.b64decode(data["content"]).decode("utf-8")

                return GitHubFile(
                    path=data["path"],
                    content=content,
                    sha=data["sha"],
                    size=data["size"],
                    encoding=data["encoding"],
                    url=data["url"],
                )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": "File not found"}
            logger.error(f"Failed to get file content: {e}")
            return {"error": f"Failed to get file content: {str(e)}"}
        except httpx.HTTPError as e:
            logger.error(f"Failed to get file content: {e}")
            return {"error": f"Failed to get file content: {str(e)}"}

    async def create_or_update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: Union[str, bytes],
        message: str,
        sha: Optional[str] = None,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """Create or update a file in a repository."""
        if not self.token:
            return {"error": "GitHub token not configured"}

        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"

        # Encode content to base64
        if isinstance(content, str):
            content_bytes = content.encode("utf-8")
        else:
            content_bytes = content
        
        content_b64 = base64.b64encode(content_bytes).decode("utf-8")

        data = {
            "message": message,
            "content": content_b64,
            "branch": branch,
        }

        # Include SHA for updates
        if sha:
            data["sha"] = sha

        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    url,
                    headers=self.headers,
                    json=data,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to create/update file: {e}")
            return {"error": f"Failed to create/update file: {str(e)}"}

    # ========================================================================
    # FIXED: Push Files with Robust Parsing
    # ========================================================================

    async def push_files(
        self,
        owner: str,
        repo: str,
        files: List[FileOperation],
        branch: str = "main",
        commit_message: str = "Update files"
    ) -> Dict[str, Any]:
        """
        Push multiple files to a repository.
        
        FIXED: This method now handles the file operation parsing correctly.
        """
        if not self.token:
            return {"error": "GitHub token not configured"}

        results = []
        errors = []

        for file_op in files:
            try:
                # Get existing file SHA if updating
                sha = None
                if file_op.operation == FileOperationType.UPDATE:
                    existing = await self.get_file_content(owner, repo, file_op.path, branch)
                    if isinstance(existing, GitHubFile):
                        sha = existing.sha
                    else:
                        # File doesn't exist, treat as create
                        logger.warning(f"File {file_op.path} not found, creating instead of updating")

                result = await self.create_or_update_file(
                    owner=owner,
                    repo=repo,
                    path=file_op.path,
                    content=file_op.content,
                    message=file_op.message or commit_message,
                    sha=sha,
                    branch=branch,
                )

                if "error" in result:
                    errors.append({"path": file_op.path, "error": result["error"]})
                else:
                    results.append({"path": file_op.path, "status": "success"})

            except Exception as e:
                logger.error(f"Failed to push file {file_op.path}: {e}")
                errors.append({"path": file_op.path, "error": str(e)})

        return {
            "success": len(errors) == 0,
            "results": results,
            "errors": errors,
            "total": len(files),
            "succeeded": len(results),
            "failed": len(errors),
        }

    # ========================================================================
    # FIXED: Parse File Operations from LLM Output
    # ========================================================================

    @staticmethod
    def parse_file_operations(content: str) -> List[FileOperation]:
        """
        FIXED: Parse file operations from LLM output with robust error handling.
        
        This method handles multiple input formats:
        1. JSON array of file operations
        2. JSON object with 'files' key
        3. Markdown code blocks containing JSON
        4. Individual file objects
        
        Previously this was failing with "Could not parse file operation details"
        because it expected a very specific format.
        """
        operations = []

        if not content or not content.strip():
            logger.error("Empty content provided for parsing")
            return operations

        # Try to extract JSON from markdown code blocks
        json_content = content
        code_block_pattern = r'```(?:json)?\s*([\s\S]*?)```'
        code_blocks = re.findall(code_block_pattern, content)
        
        if code_blocks:
            # Use the first code block that looks like JSON
            for block in code_blocks:
                if block.strip().startswith('[') or block.strip().startswith('{'):
                    json_content = block.strip()
                    break

        # Try to parse as JSON
        data = None
        parse_errors = []

        # Attempt 1: Direct JSON parsing
        try:
            data = json.loads(json_content)
        except json.JSONDecodeError as e:
            parse_errors.append(f"Direct JSON parse failed: {e}")

        # Attempt 2: Try to find JSON array in the string
        if data is None:
            array_pattern = r'\[\s*\{.*\}\s*\]'
            match = re.search(array_pattern, json_content, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(0))
                except json.JSONDecodeError as e:
                    parse_errors.append(f"Array extraction failed: {e}")

        # Attempt 3: Try to find individual JSON objects
        if data is None:
            object_pattern = r'\{[^{}]*"path"[^{}]*\}'
            matches = re.findall(object_pattern, json_content, re.DOTALL)
            if matches:
                data = []
                for match in matches:
                    try:
                        obj = json.loads(match)
                        data.append(obj)
                    except json.JSONDecodeError:
                        pass

        # Attempt 4: Manual parsing for simple cases
        if data is None:
            # Try to extract path and content using regex
            path_pattern = r'["\']path["\']\s*:\s*["\']([^"\']+)["\']'
            content_pattern = r'["\']content["\']\s*:\s*["\']([^"\']*)["\']'
            
            paths = re.findall(path_pattern, json_content)
            contents = re.findall(content_pattern, json_content, re.DOTALL)
            
            if paths and contents and len(paths) == len(contents):
                data = [
                    {"path": p, "content": c}
                    for p, c in zip(paths, contents)
                ]

        if data is None:
            logger.error(f"Failed to parse file operations. Errors: {parse_errors}")
            return operations

        # Normalize data to a list
        if isinstance(data, dict):
            if "files" in data:
                data = data["files"]
            else:
                data = [data]

        if not isinstance(data, list):
            logger.error(f"Expected list of file operations, got {type(data)}")
            return operations

        # Parse each file operation
        for item in data:
            if not isinstance(item, dict):
                logger.warning(f"Skipping non-dict item: {item}")
                continue

            # Extract required fields with validation
            path = item.get("path") or item.get("file_path") or item.get("filename")
            content = item.get("content") or item.get("file_content") or item.get("code")
            message = item.get("message") or item.get("commit_message") or "Update file"
            operation_str = item.get("operation") or item.get("action") or "create"

            # Validate required fields
            if not path:
                logger.warning(f"Skipping item without path: {item}")
                continue

            if content is None:
                logger.warning(f"Skipping item without content: {item}")
                continue

            # Determine operation type
            try:
                operation = FileOperationType(operation_str.lower())
            except ValueError:
                operation = FileOperationType.CREATE

            # Handle content that might be a string or already encoded
            if isinstance(content, dict):
                # Content might be a structured object, convert to string
                content = json.dumps(content, indent=2)
            elif not isinstance(content, (str, bytes)):
                content = str(content)

            operations.append(FileOperation(
                path=path,
                content=content,
                operation=operation,
                message=message,
            ))

        logger.info(f"Parsed {len(operations)} file operations")
        return operations

    # ========================================================================
    # FIXED: Push from LLM Output
    # ========================================================================

    async def push_from_llm_output(
        self,
        owner: str,
        repo: str,
        llm_output: str,
        branch: str = "main",
        commit_message: str = "Update from AI"
    ) -> Dict[str, Any]:
        """
        FIXED: Push files from LLM output with robust parsing.
        
        This is the main method that was failing with 
        "Could not parse file operation details" error.
        """
        logger.info(f"Parsing LLM output for {owner}/{repo}")
        
        # Parse file operations
        operations = self.parse_file_operations(llm_output)
        
        if not operations:
            return {
                "success": False,
                "error": "Could not parse file operation details from LLM output",
                "hint": "Expected JSON array with objects containing 'path' and 'content' fields",
                "received_preview": llm_output[:500] if llm_output else "empty",
            }

        # Push files
        result = await self.push_files(
            owner=owner,
            repo=repo,
            files=operations,
            branch=branch,
            commit_message=commit_message,
        )

        return result

    # ========================================================================
    # Pull Request Operations
    # ========================================================================

    async def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str = "main"
    ) -> Dict[str, Any]:
        """Create a pull request."""
        if not self.token:
            return {"error": "GitHub token not configured"}

        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls"
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=data,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to create pull request: {e}")
            return {"error": f"Failed to create pull request: {str(e)}"}


# ========================================================================
# Singleton instance
# ========================================================================

_github_tools: Optional[GitHubTools] = None


def get_github_tools() -> GitHubTools:
    """Get or create the global GitHub tools instance."""
    global _github_tools
    if _github_tools is None:
        _github_tools = GitHubTools()
    return _github_tools
