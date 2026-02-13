"""
GitHub API Integration for McLeuker Agentic AI
================================================

Real GitHub operations via REST API:
- Read repository contents (files, directories, branches)
- Create/update files with commit messages
- Create branches
- Create pull requests
- Search code and repositories
- Get repository info and stats

Uses user-provided GitHub tokens for authentication.
All operations are async-compatible via httpx.
"""

import asyncio
import base64
import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    logger.warning("httpx not installed — GitHub API integration disabled")


@dataclass
class GitHubResult:
    success: bool
    action: str
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    url: Optional[str] = None


class GitHubClient:
    """
    GitHub REST API client for real repository operations.
    
    Requires a user-provided Personal Access Token (PAT) with repo scope.
    """

    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.available = HTTPX_AVAILABLE
        if token:
            logger.info("GitHubClient initialized with token")
        else:
            logger.info("GitHubClient initialized without token (read-only public repos)")

    def set_token(self, token: str):
        """Set or update the GitHub token."""
        self.token = token
        logger.info("GitHubClient token updated")

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    # ------------------------------------------------------------------
    # Repository info
    # ------------------------------------------------------------------

    async def get_repo_info(self, owner: str, repo: str) -> GitHubResult:
        """Get repository information."""
        if not self.available:
            return GitHubResult(success=False, action="get_repo_info", error="httpx not installed")

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{self.BASE_URL}/repos/{owner}/{repo}",
                    headers=self._headers(),
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return GitHubResult(
                        success=True,
                        action="get_repo_info",
                        data={
                            "name": data.get("name"),
                            "full_name": data.get("full_name"),
                            "description": data.get("description"),
                            "default_branch": data.get("default_branch"),
                            "language": data.get("language"),
                            "private": data.get("private"),
                            "html_url": data.get("html_url"),
                            "size": data.get("size"),
                            "open_issues_count": data.get("open_issues_count"),
                            "updated_at": data.get("updated_at"),
                        },
                        url=data.get("html_url"),
                    )
                else:
                    return GitHubResult(
                        success=False, action="get_repo_info",
                        error=f"HTTP {resp.status_code}: {resp.text[:200]}",
                    )
        except Exception as e:
            return GitHubResult(success=False, action="get_repo_info", error=str(e))

    # ------------------------------------------------------------------
    # Read files and directories
    # ------------------------------------------------------------------

    async def get_file_content(self, owner: str, repo: str, path: str, ref: Optional[str] = None) -> GitHubResult:
        """Get the content of a file from a repository."""
        if not self.available:
            return GitHubResult(success=False, action="get_file", error="httpx not installed")

        try:
            params = {}
            if ref:
                params["ref"] = ref

            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}",
                    headers=self._headers(),
                    params=params,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list):
                        # It's a directory listing
                        entries = [{"name": f["name"], "type": f["type"], "path": f["path"], "size": f.get("size", 0)} for f in data]
                        return GitHubResult(
                            success=True, action="list_directory",
                            data={"path": path, "entries": entries, "count": len(entries)},
                        )
                    elif data.get("type") == "file":
                        content = ""
                        if data.get("encoding") == "base64" and data.get("content"):
                            try:
                                content = base64.b64decode(data["content"]).decode("utf-8")
                            except Exception:
                                content = "[Binary file — cannot decode as text]"
                        return GitHubResult(
                            success=True, action="get_file",
                            data={
                                "path": path,
                                "content": content,
                                "sha": data.get("sha"),
                                "size": data.get("size"),
                                "name": data.get("name"),
                                "html_url": data.get("html_url"),
                            },
                        )
                    else:
                        return GitHubResult(
                            success=True, action="get_file",
                            data={"path": path, "type": data.get("type"), "raw": data},
                        )
                else:
                    return GitHubResult(
                        success=False, action="get_file",
                        error=f"HTTP {resp.status_code}: {resp.text[:200]}",
                    )
        except Exception as e:
            return GitHubResult(success=False, action="get_file", error=str(e))

    async def list_directory(self, owner: str, repo: str, path: str = "", ref: Optional[str] = None) -> GitHubResult:
        """List files in a directory."""
        return await self.get_file_content(owner, repo, path, ref)

    # ------------------------------------------------------------------
    # Create/Update files
    # ------------------------------------------------------------------

    async def create_or_update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: Optional[str] = None,
        sha: Optional[str] = None,
    ) -> GitHubResult:
        """Create or update a file in the repository."""
        if not self.available:
            return GitHubResult(success=False, action="create_file", error="httpx not installed")
        if not self.token:
            return GitHubResult(success=False, action="create_file", error="GitHub token required for write operations")

        try:
            encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
            body: Dict[str, Any] = {
                "message": message,
                "content": encoded_content,
            }
            if branch:
                body["branch"] = branch
            if sha:
                body["sha"] = sha

            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.put(
                    f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}",
                    headers=self._headers(),
                    json=body,
                )
                if resp.status_code in (200, 201):
                    data = resp.json()
                    return GitHubResult(
                        success=True,
                        action="create_file" if resp.status_code == 201 else "update_file",
                        data={
                            "path": path,
                            "sha": data.get("content", {}).get("sha"),
                            "commit_sha": data.get("commit", {}).get("sha"),
                            "commit_url": data.get("commit", {}).get("html_url"),
                        },
                        url=data.get("content", {}).get("html_url"),
                    )
                else:
                    return GitHubResult(
                        success=False, action="create_file",
                        error=f"HTTP {resp.status_code}: {resp.text[:200]}",
                    )
        except Exception as e:
            return GitHubResult(success=False, action="create_file", error=str(e))

    # ------------------------------------------------------------------
    # Branches
    # ------------------------------------------------------------------

    async def create_branch(self, owner: str, repo: str, branch_name: str, from_branch: Optional[str] = None) -> GitHubResult:
        """Create a new branch from an existing branch."""
        if not self.available:
            return GitHubResult(success=False, action="create_branch", error="httpx not installed")
        if not self.token:
            return GitHubResult(success=False, action="create_branch", error="GitHub token required")

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                # Get the SHA of the source branch
                source = from_branch or "main"
                ref_resp = await client.get(
                    f"{self.BASE_URL}/repos/{owner}/{repo}/git/ref/heads/{source}",
                    headers=self._headers(),
                )
                if ref_resp.status_code != 200:
                    return GitHubResult(
                        success=False, action="create_branch",
                        error=f"Source branch '{source}' not found: {ref_resp.text[:200]}",
                    )

                sha = ref_resp.json()["object"]["sha"]

                # Create the new branch
                create_resp = await client.post(
                    f"{self.BASE_URL}/repos/{owner}/{repo}/git/refs",
                    headers=self._headers(),
                    json={"ref": f"refs/heads/{branch_name}", "sha": sha},
                )
                if create_resp.status_code == 201:
                    return GitHubResult(
                        success=True, action="create_branch",
                        data={"branch": branch_name, "sha": sha, "from_branch": source},
                    )
                else:
                    return GitHubResult(
                        success=False, action="create_branch",
                        error=f"HTTP {create_resp.status_code}: {create_resp.text[:200]}",
                    )
        except Exception as e:
            return GitHubResult(success=False, action="create_branch", error=str(e))

    async def list_branches(self, owner: str, repo: str) -> GitHubResult:
        """List all branches in a repository."""
        if not self.available:
            return GitHubResult(success=False, action="list_branches", error="httpx not installed")

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{self.BASE_URL}/repos/{owner}/{repo}/branches",
                    headers=self._headers(),
                )
                if resp.status_code == 200:
                    branches = [{"name": b["name"], "protected": b.get("protected", False)} for b in resp.json()]
                    return GitHubResult(
                        success=True, action="list_branches",
                        data={"branches": branches, "count": len(branches)},
                    )
                else:
                    return GitHubResult(
                        success=False, action="list_branches",
                        error=f"HTTP {resp.status_code}: {resp.text[:200]}",
                    )
        except Exception as e:
            return GitHubResult(success=False, action="list_branches", error=str(e))

    # ------------------------------------------------------------------
    # Pull Requests
    # ------------------------------------------------------------------

    async def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str = "main",
    ) -> GitHubResult:
        """Create a pull request."""
        if not self.available:
            return GitHubResult(success=False, action="create_pr", error="httpx not installed")
        if not self.token:
            return GitHubResult(success=False, action="create_pr", error="GitHub token required")

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self.BASE_URL}/repos/{owner}/{repo}/pulls",
                    headers=self._headers(),
                    json={"title": title, "body": body, "head": head, "base": base},
                )
                if resp.status_code == 201:
                    data = resp.json()
                    return GitHubResult(
                        success=True, action="create_pr",
                        data={
                            "number": data.get("number"),
                            "title": data.get("title"),
                            "html_url": data.get("html_url"),
                            "state": data.get("state"),
                        },
                        url=data.get("html_url"),
                    )
                else:
                    return GitHubResult(
                        success=False, action="create_pr",
                        error=f"HTTP {resp.status_code}: {resp.text[:200]}",
                    )
        except Exception as e:
            return GitHubResult(success=False, action="create_pr", error=str(e))

    # ------------------------------------------------------------------
    # Issues
    # ------------------------------------------------------------------

    async def list_issues(self, owner: str, repo: str, state: str = "open", per_page: int = 10) -> GitHubResult:
        """List issues in a repository."""
        if not self.available:
            return GitHubResult(success=False, action="list_issues", error="httpx not installed")

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{self.BASE_URL}/repos/{owner}/{repo}/issues",
                    headers=self._headers(),
                    params={"state": state, "per_page": per_page},
                )
                if resp.status_code == 200:
                    issues = [
                        {
                            "number": i["number"],
                            "title": i["title"],
                            "state": i["state"],
                            "labels": [l["name"] for l in i.get("labels", [])],
                            "created_at": i.get("created_at"),
                            "html_url": i.get("html_url"),
                        }
                        for i in resp.json()
                    ]
                    return GitHubResult(
                        success=True, action="list_issues",
                        data={"issues": issues, "count": len(issues)},
                    )
                else:
                    return GitHubResult(
                        success=False, action="list_issues",
                        error=f"HTTP {resp.status_code}: {resp.text[:200]}",
                    )
        except Exception as e:
            return GitHubResult(success=False, action="list_issues", error=str(e))

    async def create_issue(self, owner: str, repo: str, title: str, body: str, labels: Optional[List[str]] = None) -> GitHubResult:
        """Create an issue."""
        if not self.available:
            return GitHubResult(success=False, action="create_issue", error="httpx not installed")
        if not self.token:
            return GitHubResult(success=False, action="create_issue", error="GitHub token required")

        try:
            payload: Dict[str, Any] = {"title": title, "body": body}
            if labels:
                payload["labels"] = labels

            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self.BASE_URL}/repos/{owner}/{repo}/issues",
                    headers=self._headers(),
                    json=payload,
                )
                if resp.status_code == 201:
                    data = resp.json()
                    return GitHubResult(
                        success=True, action="create_issue",
                        data={
                            "number": data.get("number"),
                            "title": data.get("title"),
                            "html_url": data.get("html_url"),
                        },
                        url=data.get("html_url"),
                    )
                else:
                    return GitHubResult(
                        success=False, action="create_issue",
                        error=f"HTTP {resp.status_code}: {resp.text[:200]}",
                    )
        except Exception as e:
            return GitHubResult(success=False, action="create_issue", error=str(e))

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    async def search_code(self, query: str, owner: Optional[str] = None, repo: Optional[str] = None) -> GitHubResult:
        """Search for code across GitHub."""
        if not self.available:
            return GitHubResult(success=False, action="search_code", error="httpx not installed")

        try:
            q = query
            if owner and repo:
                q = f"{query} repo:{owner}/{repo}"
            elif owner:
                q = f"{query} user:{owner}"

            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"{self.BASE_URL}/search/code",
                    headers=self._headers(),
                    params={"q": q, "per_page": 10},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    items = [
                        {
                            "name": i["name"],
                            "path": i["path"],
                            "repository": i["repository"]["full_name"],
                            "html_url": i["html_url"],
                        }
                        for i in data.get("items", [])
                    ]
                    return GitHubResult(
                        success=True, action="search_code",
                        data={"results": items, "total_count": data.get("total_count", 0)},
                    )
                else:
                    return GitHubResult(
                        success=False, action="search_code",
                        error=f"HTTP {resp.status_code}: {resp.text[:200]}",
                    )
        except Exception as e:
            return GitHubResult(success=False, action="search_code", error=str(e))

    # ------------------------------------------------------------------
    # Multi-file commit (tree API)
    # ------------------------------------------------------------------

    async def commit_multiple_files(
        self,
        owner: str,
        repo: str,
        files: List[Dict[str, str]],
        message: str,
        branch: str = "main",
    ) -> GitHubResult:
        """
        Commit multiple files in a single commit using the Git Tree API.
        
        files: [{"path": "src/file.py", "content": "..."}, ...]
        """
        if not self.available:
            return GitHubResult(success=False, action="multi_commit", error="httpx not installed")
        if not self.token:
            return GitHubResult(success=False, action="multi_commit", error="GitHub token required")

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                # 1. Get the latest commit SHA on the branch
                ref_resp = await client.get(
                    f"{self.BASE_URL}/repos/{owner}/{repo}/git/ref/heads/{branch}",
                    headers=self._headers(),
                )
                if ref_resp.status_code != 200:
                    return GitHubResult(
                        success=False, action="multi_commit",
                        error=f"Branch '{branch}' not found: {ref_resp.text[:200]}",
                    )
                latest_sha = ref_resp.json()["object"]["sha"]

                # 2. Get the tree SHA
                commit_resp = await client.get(
                    f"{self.BASE_URL}/repos/{owner}/{repo}/git/commits/{latest_sha}",
                    headers=self._headers(),
                )
                tree_sha = commit_resp.json()["tree"]["sha"]

                # 3. Create blobs for each file
                tree_items = []
                for f in files:
                    blob_resp = await client.post(
                        f"{self.BASE_URL}/repos/{owner}/{repo}/git/blobs",
                        headers=self._headers(),
                        json={"content": f["content"], "encoding": "utf-8"},
                    )
                    if blob_resp.status_code != 201:
                        return GitHubResult(
                            success=False, action="multi_commit",
                            error=f"Failed to create blob for {f['path']}: {blob_resp.text[:200]}",
                        )
                    tree_items.append({
                        "path": f["path"],
                        "mode": "100644",
                        "type": "blob",
                        "sha": blob_resp.json()["sha"],
                    })

                # 4. Create new tree
                new_tree_resp = await client.post(
                    f"{self.BASE_URL}/repos/{owner}/{repo}/git/trees",
                    headers=self._headers(),
                    json={"base_tree": tree_sha, "tree": tree_items},
                )
                if new_tree_resp.status_code != 201:
                    return GitHubResult(
                        success=False, action="multi_commit",
                        error=f"Failed to create tree: {new_tree_resp.text[:200]}",
                    )
                new_tree_sha = new_tree_resp.json()["sha"]

                # 5. Create commit
                new_commit_resp = await client.post(
                    f"{self.BASE_URL}/repos/{owner}/{repo}/git/commits",
                    headers=self._headers(),
                    json={
                        "message": message,
                        "tree": new_tree_sha,
                        "parents": [latest_sha],
                    },
                )
                if new_commit_resp.status_code != 201:
                    return GitHubResult(
                        success=False, action="multi_commit",
                        error=f"Failed to create commit: {new_commit_resp.text[:200]}",
                    )
                new_commit_sha = new_commit_resp.json()["sha"]

                # 6. Update branch reference
                update_resp = await client.patch(
                    f"{self.BASE_URL}/repos/{owner}/{repo}/git/refs/heads/{branch}",
                    headers=self._headers(),
                    json={"sha": new_commit_sha},
                )
                if update_resp.status_code != 200:
                    return GitHubResult(
                        success=False, action="multi_commit",
                        error=f"Failed to update ref: {update_resp.text[:200]}",
                    )

                return GitHubResult(
                    success=True, action="multi_commit",
                    data={
                        "commit_sha": new_commit_sha,
                        "files_committed": len(files),
                        "branch": branch,
                        "file_paths": [f["path"] for f in files],
                    },
                    url=f"https://github.com/{owner}/{repo}/commit/{new_commit_sha}",
                )

        except Exception as e:
            return GitHubResult(success=False, action="multi_commit", error=str(e))
