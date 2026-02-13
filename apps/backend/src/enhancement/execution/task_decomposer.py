"""
Task Decomposer — Breaks user requests into executable steps
==============================================================
Uses Grok for reasoning to decompose complex user tasks into
a sequence of atomic, executable actions.

Key capabilities:
- Intent classification (web_automation, research, file_generation, etc.)
- Step dependency resolution
- Resource requirement detection
- Credential requirement detection
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

import httpx

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of tasks the system can handle."""
    WEB_AUTOMATION = "web_automation"
    RESEARCH = "research"
    FILE_GENERATION = "file_generation"
    DATA_ANALYSIS = "data_analysis"
    CODE_EXECUTION = "code_execution"
    COMMUNICATION = "communication"
    ACCOUNT_MANAGEMENT = "account_management"
    CREATIVE = "creative"
    GENERAL = "general"


class StepAction(Enum):
    """Atomic actions a step can perform."""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    READ = "read"
    EXTRACT = "extract"
    SCREENSHOT = "screenshot"
    WAIT = "wait"
    SEARCH = "search"
    ANALYZE = "analyze"
    GENERATE_FILE = "generate_file"
    EXECUTE_CODE = "execute_code"
    API_CALL = "api_call"
    LOGIN = "login"
    FILL_FORM = "fill_form"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    REASON = "reason"
    SUMMARIZE = "summarize"
    VERIFY = "verify"


@dataclass
class ExecutionStep:
    """A single executable step in a task plan."""
    id: str
    action: StepAction
    description: str
    params: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    requires_credential: bool = False
    credential_type: Optional[str] = None
    requires_user_confirmation: bool = False
    timeout: float = 60.0
    retry_count: int = 2
    fallback_action: Optional[str] = None
    status: str = "pending"
    result: Optional[Any] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action": self.action.value,
            "description": self.description,
            "params": self.params,
            "dependencies": self.dependencies,
            "requires_credential": self.requires_credential,
            "credential_type": self.credential_type,
            "requires_user_confirmation": self.requires_user_confirmation,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "fallback_action": self.fallback_action,
            "status": self.status,
        }


@dataclass
class TaskPlan:
    """A complete task plan with all steps."""
    id: str
    task_type: TaskType
    original_query: str
    goal: str
    steps: List[ExecutionStep] = field(default_factory=list)
    required_credentials: List[str] = field(default_factory=list)
    estimated_duration_seconds: float = 0.0
    requires_user_input: bool = False
    user_input_prompts: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "task_type": self.task_type.value,
            "original_query": self.original_query,
            "goal": self.goal,
            "steps": [s.to_dict() for s in self.steps],
            "required_credentials": self.required_credentials,
            "estimated_duration_seconds": self.estimated_duration_seconds,
            "requires_user_input": self.requires_user_input,
            "user_input_prompts": self.user_input_prompts,
            "created_at": self.created_at,
        }


class TaskDecomposer:
    """
    Decomposes complex user tasks into executable step sequences.

    Uses Grok for reasoning to understand intent, identify required
    resources, and create an optimal execution plan.
    """

    def __init__(self):
        self.grok_api_key = os.getenv("XAI_API_KEY", "")
        self.grok_base_url = "https://api.x.ai/v1"
        self.grok_model = os.getenv("GROK_MODEL", "grok-4-1-fast-reasoning")

    async def decompose(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        available_tools: Optional[List[str]] = None,
    ) -> TaskPlan:
        """
        Decompose a user query into an executable task plan.

        Args:
            query: The user's natural language request
            context: Additional context (session history, user preferences)
            available_tools: List of available tool names

        Returns:
            A TaskPlan with ordered execution steps
        """
        import uuid

        plan_id = str(uuid.uuid4())[:12]

        system_prompt = self._build_decomposition_prompt(available_tools or [])

        user_message = f"""Decompose this user request into executable steps:

USER REQUEST: {query}

CONTEXT: {json.dumps(context or {}, indent=2)}

Return a JSON object with:
{{
    "task_type": "web_automation|research|file_generation|data_analysis|code_execution|communication|account_management|creative|general",
    "goal": "Clear goal statement",
    "steps": [
        {{
            "id": "step_1",
            "action": "navigate|click|type|scroll|read|extract|screenshot|wait|search|analyze|generate_file|execute_code|api_call|login|fill_form|download|upload|reason|summarize|verify",
            "description": "What this step does",
            "params": {{}},
            "dependencies": [],
            "requires_credential": false,
            "credential_type": null,
            "requires_user_confirmation": false,
            "timeout": 60,
            "retry_count": 2,
            "fallback_action": null
        }}
    ],
    "required_credentials": [],
    "estimated_duration_seconds": 30,
    "requires_user_input": false,
    "user_input_prompts": []
}}"""

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{self.grok_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.grok_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.grok_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message},
                        ],
                        "temperature": 0.3,
                        "max_tokens": 4096,
                    },
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]

                plan_data = self._parse_plan_json(content)
                return self._build_task_plan(plan_id, query, plan_data)

        except Exception as e:
            logger.error("Task decomposition failed: %s", e)
            return self._build_fallback_plan(plan_id, query)

    def _build_decomposition_prompt(self, available_tools: List[str]) -> str:
        """Build the system prompt for task decomposition."""
        tools_str = ", ".join(available_tools) if available_tools else "web_search, browser_navigate, browser_click, browser_type, browser_read, browser_screenshot, file_read, file_write, code_execute, api_call"

        return f"""You are an expert task decomposer for an agentic AI system.
Your job is to break down user requests into precise, atomic, executable steps.

AVAILABLE TOOLS: {tools_str}

RULES:
1. Each step must be a single atomic action
2. Steps must have clear dependencies
3. Identify when credentials are needed (login, API keys)
4. Flag steps that need user confirmation (payments, posting, deleting)
5. Include verification steps to confirm success
6. Add fallback actions for critical steps
7. Estimate realistic timeouts
8. For web automation: always start with navigate, then read/extract, then act
9. For research: search first, then analyze, then synthesize
10. For file generation: analyze requirements, generate content, then create file
11. Always include a final verification step

CREDENTIAL TYPES: github, google, twitter, linkedin, canva, slack, email, custom

Return ONLY valid JSON. No markdown, no explanation."""

    def _parse_plan_json(self, content: str) -> Dict[str, Any]:
        """Parse JSON from LLM response, handling markdown code blocks."""
        content = content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1])
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            import re
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise

    def _build_task_plan(
        self, plan_id: str, query: str, data: Dict[str, Any]
    ) -> TaskPlan:
        """Build a TaskPlan from parsed JSON data."""
        task_type = TaskType(data.get("task_type", "general"))

        steps = []
        for step_data in data.get("steps", []):
            try:
                action = StepAction(step_data.get("action", "reason"))
            except ValueError:
                action = StepAction.REASON

            steps.append(ExecutionStep(
                id=step_data.get("id", f"step_{len(steps)+1}"),
                action=action,
                description=step_data.get("description", ""),
                params=step_data.get("params", {}),
                dependencies=step_data.get("dependencies", []),
                requires_credential=step_data.get("requires_credential", False),
                credential_type=step_data.get("credential_type"),
                requires_user_confirmation=step_data.get("requires_user_confirmation", False),
                timeout=step_data.get("timeout", 60.0),
                retry_count=step_data.get("retry_count", 2),
                fallback_action=step_data.get("fallback_action"),
            ))

        return TaskPlan(
            id=plan_id,
            task_type=task_type,
            original_query=query,
            goal=data.get("goal", query),
            steps=steps,
            required_credentials=data.get("required_credentials", []),
            estimated_duration_seconds=data.get("estimated_duration_seconds", 30.0),
            requires_user_input=data.get("requires_user_input", False),
            user_input_prompts=data.get("user_input_prompts", []),
        )

    def _build_fallback_plan(self, plan_id: str, query: str) -> TaskPlan:
        """Build a simple fallback plan when decomposition fails."""
        return TaskPlan(
            id=plan_id,
            task_type=TaskType.GENERAL,
            original_query=query,
            goal=query,
            steps=[
                ExecutionStep(
                    id="step_1",
                    action=StepAction.REASON,
                    description="Analyze the user's request",
                    params={"query": query},
                ),
                ExecutionStep(
                    id="step_2",
                    action=StepAction.SEARCH,
                    description="Search for relevant information",
                    params={"query": query},
                    dependencies=["step_1"],
                ),
                ExecutionStep(
                    id="step_3",
                    action=StepAction.SUMMARIZE,
                    description="Synthesize findings into a response",
                    dependencies=["step_2"],
                ),
            ],
            estimated_duration_seconds=30.0,
        )
