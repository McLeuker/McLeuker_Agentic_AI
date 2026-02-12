"""
Task Planner — Structured Plan Generation for Agentic Execution
================================================================

Uses kimi-2.5 to decompose user requests into executable plans:
- Task analysis and decomposition
- Step dependency management
- Tool selection per step
- Fallback plan generation
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class StepType(Enum):
    RESEARCH = "research"
    ANALYSIS = "analysis"
    CODE_EXECUTION = "code_execution"
    CODE_GENERATION = "code_generation"
    WEB_BROWSING = "web_browsing"
    FILE_OPERATION = "file_operation"
    COMMUNICATION = "communication"
    VERIFICATION = "verification"
    SYNTHESIS = "synthesis"


class StepStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TaskStep:
    id: str
    description: str
    step_type: StepType
    tool_name: Optional[str] = None
    tool_params: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    expected_output: str = ""
    validation_criteria: List[str] = field(default_factory=list)
    error_handling: str = "retry"
    max_retries: int = 3
    requires_reflection: bool = True
    checkpoint: bool = False
    status: StepStatus = StepStatus.PENDING
    result: Optional[Any] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "step_type": self.step_type.value,
            "tool_name": self.tool_name,
            "tool_params": self.tool_params,
            "dependencies": self.dependencies,
            "expected_output": self.expected_output,
            "validation_criteria": self.validation_criteria,
            "error_handling": self.error_handling,
            "max_retries": self.max_retries,
            "status": self.status.value,
        }


@dataclass
class ExecutionPlan:
    id: str
    objective: str
    steps: List[TaskStep]
    parallel_groups: List[List[str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "objective": self.objective,
            "steps": [s.to_dict() for s in self.steps],
            "parallel_groups": self.parallel_groups,
            "metadata": self.metadata,
        }


class TaskPlanner:
    """
    Creates structured execution plans from user requests.

    Uses kimi-2.5 to:
    1. Analyze the task
    2. Decompose into steps
    3. Assign tools and dependencies
    4. Generate fallback plans
    """

    PLANNING_SYSTEM_PROMPT = """You are an expert task planner for an AI agent system.

Given a user request, create a detailed execution plan.

Available step types:
- research: Search the web for information
- analysis: Analyze data or information
- code_execution: Execute Python or JavaScript code
- code_generation: Generate code files
- web_browsing: Navigate and interact with websites
- file_operation: Read, write, or manipulate files
- communication: Generate text responses
- verification: Verify results and quality
- synthesis: Combine results into final output

Available tools:
- web_search: Search the web (params: query, num_results)
- browser_navigate: Navigate to URL (params: url)
- browser_click: Click element (params: selector or x,y)
- browser_type: Type text (params: text, selector)
- browser_extract_text: Extract page text (params: selector)
- browser_screenshot: Take screenshot
- execute_python: Run Python code (params: code)
- execute_javascript: Run JavaScript (params: code)
- read_file: Read file (params: path)
- write_file: Write file (params: path, content)
- list_directory: List directory (params: path)
- fetch_url: Fetch URL content (params: url)

Respond in JSON format:
{
    "objective": "clear objective statement",
    "steps": [
        {
            "id": "step_1",
            "description": "what this step does",
            "step_type": "research|analysis|code_execution|web_browsing|file_operation|communication|verification|synthesis",
            "tool_name": "tool to use or null",
            "tool_params": {},
            "dependencies": [],
            "expected_output": "what we expect",
            "validation_criteria": ["criterion 1"],
            "requires_reflection": true,
            "checkpoint": false
        }
    ],
    "parallel_groups": [["step_1", "step_2"]],
    "metadata": {"estimated_time_minutes": 5}
}"""

    def __init__(self, kimi_client, config):
        self.kimi_client = kimi_client
        self.config = config

    async def create_plan(
        self,
        user_request: str,
        context: Optional[Dict[str, Any]] = None,
        available_tools: Optional[List[str]] = None,
    ) -> ExecutionPlan:
        """Create an execution plan from a user request."""

        # Analyze the task first
        task_analysis = await self._analyze_task(user_request, context)

        messages = [
            {"role": "system", "content": self.PLANNING_SYSTEM_PROMPT},
            {"role": "user", "content": f"""Create an execution plan for:

REQUEST: {user_request}

ANALYSIS:
- Complexity: {task_analysis.get('complexity', 'medium')}
- Type: {task_analysis.get('task_type', 'general')}
- Requirements: {', '.join(task_analysis.get('requirements', []))}
- Constraints: {', '.join(task_analysis.get('constraints', []))}
- Challenges: {', '.join(task_analysis.get('challenges', []))}

Provide a detailed plan with all steps, dependencies, and tool usage."""}
        ]

        try:
            response = await self.kimi_client.chat.completions.create(
                model=self.config.primary_model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=8000,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            plan_data = json.loads(content)

            steps = []
            for step_data in plan_data.get("steps", []):
                step_type_str = step_data.get("step_type", "research")
                try:
                    step_type = StepType(step_type_str)
                except ValueError:
                    step_type = StepType.RESEARCH

                steps.append(TaskStep(
                    id=step_data.get("id", f"step_{len(steps)+1}"),
                    description=step_data.get("description", ""),
                    step_type=step_type,
                    tool_name=step_data.get("tool_name"),
                    tool_params=step_data.get("tool_params", {}),
                    dependencies=step_data.get("dependencies", []),
                    expected_output=step_data.get("expected_output", ""),
                    validation_criteria=step_data.get("validation_criteria", []),
                    error_handling=step_data.get("error_handling", "retry"),
                    max_retries=step_data.get("max_retries", 3),
                    requires_reflection=step_data.get("requires_reflection", True),
                    checkpoint=step_data.get("checkpoint", False),
                ))

            plan = ExecutionPlan(
                id=f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(user_request) % 10000}",
                objective=plan_data.get("objective", user_request),
                steps=steps,
                parallel_groups=plan_data.get("parallel_groups", []),
                metadata=plan_data.get("metadata", {})
            )

            logger.info(f"Created plan with {len(steps)} steps")
            return plan

        except Exception as e:
            logger.exception(f"Plan creation failed: {e}")
            return self._create_fallback_plan(user_request)

    async def revise_plan(
        self,
        current_plan: ExecutionPlan,
        reflection: Any,
        context: Any
    ) -> ExecutionPlan:
        """Revise the plan based on reflection."""

        system_prompt = """You are an expert plan reviser. Given a plan that encountered issues,
revise it to address the problems while preserving completed work.

Respond in JSON format with the same structure as the original plan.
Only modify steps that need changes - keep successful steps as-is."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""Revise this plan:

ORIGINAL PLAN:
{json.dumps(current_plan.to_dict(), indent=2)}

REFLECTION:
- Issue: {reflection.reflection}
- Suggested action: {reflection.suggested_action}
- Restart from step: {reflection.restart_from_step}

Create a revised plan that addresses the issue."""}
        ]

        try:
            response = await self.kimi_client.chat.completions.create(
                model=self.config.primary_model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=8000,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            plan_data = json.loads(content)

            steps = []
            for step_data in plan_data.get("steps", []):
                step_type_str = step_data.get("step_type", "research")
                try:
                    step_type = StepType(step_type_str)
                except ValueError:
                    step_type = StepType.RESEARCH

                steps.append(TaskStep(
                    id=step_data.get("id", f"step_{len(steps)+1}"),
                    description=step_data.get("description", ""),
                    step_type=step_type,
                    tool_name=step_data.get("tool_name"),
                    tool_params=step_data.get("tool_params", {}),
                    dependencies=step_data.get("dependencies", []),
                    expected_output=step_data.get("expected_output", ""),
                    validation_criteria=step_data.get("validation_criteria", []),
                    max_retries=step_data.get("max_retries", 3),
                    requires_reflection=step_data.get("requires_reflection", True),
                ))

            return ExecutionPlan(
                id=f"{current_plan.id}_rev",
                objective=plan_data.get("objective", current_plan.objective),
                steps=steps,
                parallel_groups=plan_data.get("parallel_groups", []),
                metadata={**current_plan.metadata, "revised": True}
            )

        except Exception as e:
            logger.exception(f"Plan revision failed: {e}")
            return current_plan

    async def _analyze_task(
        self,
        user_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze the task to determine complexity and requirements."""

        messages = [
            {"role": "system", "content": """Analyze this task and provide:
1. Complexity (simple/medium/complex)
2. Task type (research/coding/browsing/analysis/creative/mixed)
3. Requirements (what's needed)
4. Constraints (limitations)
5. Challenges (potential issues)

Respond in JSON format:
{
    "complexity": "simple|medium|complex",
    "task_type": "research|coding|browsing|analysis|creative|mixed",
    "requirements": ["req1", "req2"],
    "constraints": ["constraint1"],
    "challenges": ["challenge1"]
}"""},
            {"role": "user", "content": user_request}
        ]

        try:
            response = await self.kimi_client.chat.completions.create(
                model=self.config.primary_model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            logger.warning(f"Task analysis failed: {e}")
            return {
                "complexity": "medium",
                "task_type": "mixed",
                "requirements": [],
                "constraints": [],
                "challenges": []
            }

    def _create_fallback_plan(self, user_request: str) -> ExecutionPlan:
        """Create a simple fallback plan when LLM planning fails."""
        return ExecutionPlan(
            id=f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            objective=user_request,
            steps=[
                TaskStep(
                    id="step_1",
                    description=f"Research: {user_request}",
                    step_type=StepType.RESEARCH,
                    tool_name="web_search",
                    tool_params={"query": user_request, "num_results": 10},
                    expected_output="Search results",
                ),
                TaskStep(
                    id="step_2",
                    description="Synthesize findings into a response",
                    step_type=StepType.SYNTHESIS,
                    dependencies=["step_1"],
                    expected_output="Final response",
                ),
            ],
            metadata={"fallback": True}
        )
